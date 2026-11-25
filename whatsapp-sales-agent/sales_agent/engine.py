"""Orchestration: first contact, replies, follow-ups, opt-outs, alerts for the owner."""

from __future__ import annotations

import asyncio
import json
import logging
import random
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .brain import Brain, Decision
from .config import Settings
from .db import CLOSED_STATUSES, Database, utcnow
from .leads import normalize_phone
from .transport import BridgeClient, InboundMessage, NotOnWhatsApp, SendError

log = logging.getLogger("engine")

# Messages that mean "stop" no matter what - handled instantly, without asking Claude.
STOP_WORDS = {
    "stop", "unsubscribe", "توقف", "قف", "ايقاف", "إيقاف", "الغاء", "إلغاء", "الغاء الاشتراك",
    "إلغاء الاشتراك", "لا ترسل", "لا ترسل لي", "ما ترسل", "ماترسل", "متبعتش", "بطل رسايل", "بطلوا رسايل",
}
STOP_CONFIRMATION = "تمام، مش هنبعت لحضرتك رسايل تاني. آسفين على الإزعاج 🙏"

STATUS_LABELS = {
    "new": "لسه متبعتلهمش", "contacted": "اتبعتلهم ومردوش", "engaged": "في محادثة",
    "interested": "مهتمين", "meeting_requested": "عاوزين مكالمة/عرض سعر", "won": "اتفقنا",
    "not_interested": "مش مهتمين", "opted_out": "طلبوا التوقف",
}


def _clean(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text).strip().lower()


class SalesAgent:
    def __init__(self, db: Database, wa: BridgeClient, brain: Brain, settings: Settings, sleep=asyncio.sleep):
        self.db = db
        self.wa = wa
        self.brain = brain
        self.s = settings
        self.tz = ZoneInfo(settings.timezone)
        self._sleep = sleep
        self._locks: dict[int, asyncio.Lock] = {}
        self._job_lock = asyncio.Lock()

    # ------------------------------------------------------------------ switches
    @property
    def automation_on(self) -> bool:
        """Automatic first contact + follow-ups. Off by default; turn it on from the dashboard."""
        return self.db.get_flag("automation_on", False)

    @property
    def replies_on(self) -> bool:
        """Automatic replies to leads who message us."""
        return self.db.get_flag("replies_on", True)

    @property
    def dry_run(self) -> bool:
        return self.db.get_flag("dry_run", True)

    @property
    def owner_number(self) -> str | None:
        return normalize_phone(self.s.owner_phone, self.s.default_country_code) if self.s.owner_phone else None

    # ------------------------------------------------------------------ helpers
    def _lock(self, lead_id: int) -> asyncio.Lock:
        return self._locks.setdefault(lead_id, asyncio.Lock())

    def in_send_window(self, now: datetime | None = None) -> bool:
        local = (now or utcnow()).astimezone(self.tz)
        return self.s.send_hour_start <= local.hour < self.s.send_hour_end

    def _history(self, lead_id: int) -> list[dict]:
        return [dict(r) for r in self.db.history(lead_id)]

    def _local_midnight(self) -> datetime:
        return utcnow().astimezone(self.tz).replace(hour=0, minute=0, second=0, microsecond=0)

    async def _pause_between_sends(self) -> None:
        low, high = self.s.min_seconds_between_sends, max(self.s.min_seconds_between_sends, self.s.max_seconds_between_sends)
        await self._sleep(random.uniform(low, high))

    async def send_text(self, lead: dict, text: str, kind: str = "text") -> bool:
        try:
            wa_id = await self.wa.send_text(lead["phone"], text)
        except NotOnWhatsApp:
            self.db.update_lead(lead["id"], paused=1, next_followup_at=None,
                                agent_summary="الرقم ده مش عليه واتساب - اتوقف التواصل.")
            return False
        except SendError as exc:
            log.error("send to %s failed: %s", lead["phone"], exc)
            self.db.add_alert(f"فشل إرسال رسالة لـ {lead.get('name') or lead['phone']}: {exc}", lead["id"])
            return False
        self.db.add_message(lead["id"], "out", text, kind=kind, wa_message_id=wa_id)
        return True

    async def transport_ready(self) -> bool:
        if self.dry_run:
            return True
        status = (await self.wa.status()).get("status")
        if status != "ready":
            log.warning("WhatsApp is not connected (status: %s) - skipping scheduled sends", status)
            return False
        return True

    async def notify_owner(self, text: str, lead_id: int | None = None) -> None:
        log.warning("ALERT: %s", text)
        self.db.add_alert(text, lead_id)
        if self.owner_number and not self.dry_run:
            try:
                await self.wa.send_text(self.owner_number, text)
            except SendError as exc:
                log.error("could not alert owner on WhatsApp: %s", exc)

    # ------------------------------------------------------------------ inbound
    async def handle_inbound(self, msg: InboundMessage) -> None:
        if self.owner_number and msg.phone == self.owner_number:
            return  # never treat the owner as a lead

        lead_row = self.db.get_lead_by_phone(msg.phone)
        if lead_row is None:
            if msg.from_me or not self.s.reply_to_unknown:
                return  # not a lead (friend, family, existing client...) - leave it alone
            lead_id, _ = self.db.upsert_lead(msg.phone, name=msg.profile_name, source="whatsapp_inbound", status="engaged")
        else:
            lead_id = lead_row["id"]
            if not lead_row["name"] and msg.profile_name:
                self.db.update_lead(lead_id, name=msg.profile_name)

        if msg.from_me:
            # You replied yourself from your phone / WhatsApp Desktop: the agent steps back for this lead.
            if self.db.add_message(lead_id, "out", msg.text, kind="manual", wa_message_id=msg.wa_message_id or None):
                lead = dict(self.db.get_lead(lead_id))
                if not lead["paused"]:
                    self.db.update_lead(lead_id, paused=1, next_followup_at=None)
                    self.db.add_alert(f"انت رديت بنفسك على {lead['name'] or lead['phone']} فالايجنت وقف معاه. "
                                      "تقدر ترجّعه من الداشبورد.", lead_id)
            return

        stored_id = self.db.add_message(lead_id, "in", msg.text, kind=msg.type, wa_message_id=msg.wa_message_id or None)
        if stored_id is None:
            return  # duplicate delivery
        lead = dict(self.db.get_lead(lead_id))

        if _clean(msg.text) in STOP_WORDS:
            await self._opt_out(lead)
            return
        if lead["paused"] or not self.replies_on:
            return

        # People often send several short messages in a row: wait, then answer them together.
        await self._sleep(self.s.reply_debounce_seconds)
        if self.db.last_message_id(lead_id, "in") != stored_id:
            return

        async with self._lock(lead_id):
            lead = dict(self.db.get_lead(lead_id))
            if lead["paused"]:
                return
            decision = await self.brain.decide(lead, self._history(lead_id), "inbound")
            await self.apply_decision(lead, decision, "inbound")

    async def _opt_out(self, lead: dict) -> None:
        await self.send_text(lead, STOP_CONFIRMATION)
        self.db.update_lead(lead["id"], status="opted_out", next_followup_at=None)
        log.info("lead %s opted out", lead["phone"])

    async def apply_decision(self, lead: dict, d: Decision, event: str) -> bool:
        sent = False
        if d.action != "stay_silent" and d.message.strip():
            sent = await self.send_text(lead, d.message.strip())
            if not sent and event != "inbound":
                return False  # keep the lead as it was so the job can retry later

        status = "opted_out" if d.action == "opt_out" else d.lead_status
        if event == "first_contact" and sent:
            followups_sent = 0
        elif event == "followup":
            followups_sent = lead["followups_sent"] + (1 if sent else 0)
        else:
            followups_sent = 0  # the lead replied, so the follow-up counter starts over

        next_at = None
        if (
            d.followup_in_hours > 0
            and status not in CLOSED_STATUSES
            and d.action != "handoff_to_human"
            and followups_sent < self.s.max_followups
        ):
            hours = d.followup_in_hours
            if event == "followup" and self.s.followup_gap_days:
                # don't follow up faster than the configured gap
                gap = self.s.followup_gap_days[min(followups_sent, len(self.s.followup_gap_days) - 1)]
                hours = max(hours, gap * 24)
            next_at = utcnow() + timedelta(hours=hours)

        services = sorted(set(json.loads(lead.get("services") or "[]")) | set(d.services_of_interest))
        self.db.update_lead(
            lead["id"],
            status=status,
            interest_level=d.interest_level,
            services=services,
            agent_summary=d.lead_summary or lead.get("agent_summary") or "",
            next_followup_at=next_at,
            followups_sent=followups_sent,
            paused=1 if d.action == "handoff_to_human" else lead["paused"],
        )

        if d.action == "handoff_to_human" or d.owner_alert:
            who = lead.get("name") or lead.get("business_name") or lead["phone"]
            note = d.owner_alert or "العميل محتاج متابعة منك."
            if d.action == "handoff_to_human":
                note += " (الايجنت وقف الرد عليه لحد ما ترجّعه من الداشبورد)"
            await self.notify_owner(f"🔔 {who}: {note}", lead["id"])
        return sent

    # ------------------------------------------------------------------ outbound jobs
    async def run_outreach(self, force: bool = False, limit: int | None = None) -> int:
        """Send a personal first message to new leads, within the daily cap and sending hours."""
        if not force and not (self.automation_on and self.in_send_window()):
            return 0
        if not await self.transport_ready():
            return 0
        async with self._job_lock:
            remaining = self.s.max_new_contacts_per_day - self.db.new_contacts_since(self._local_midnight())
            if limit is not None:
                remaining = min(remaining, limit)
            sent = 0
            for row in self.db.leads_to_contact(max(remaining, 0)):
                lead = dict(row)
                async with self._lock(lead["id"]):
                    decision = await self.brain.decide(lead, [], "first_contact")
                    if decision.action != "send_message" or not decision.message.strip():
                        self.db.update_lead(lead["id"], paused=1)
                        await self.notify_owner(
                            f"الايجنت مقدرش يكتب أول رسالة لـ {lead['name'] or lead['phone']}. "
                            f"{decision.owner_alert}".strip(), lead["id"])
                    elif await self.apply_decision(lead, decision, "first_contact"):
                        sent += 1
                await self._pause_between_sends()
            log.info("outreach: contacted %d new leads", sent)
            return sent

    async def run_followups(self, force: bool = False) -> int:
        """Follow up with leads who went quiet."""
        if not force and not (self.automation_on and self.in_send_window()):
            return 0
        if not await self.transport_ready():
            return 0
        async with self._job_lock:
            sent = 0
            for row in self.db.leads_due_for_followup(utcnow()):
                lead = dict(row)
                async with self._lock(lead["id"]):
                    lead = dict(self.db.get_lead(lead["id"]))
                    if lead["paused"] or lead["followups_sent"] >= self.s.max_followups:
                        self.db.update_lead(lead["id"], next_followup_at=None)
                        continue
                    decision = await self.brain.decide(lead, self._history(lead["id"]), "followup")
                    if await self.apply_decision(lead, decision, "followup"):
                        sent += 1
                await self._pause_between_sends()
            log.info("followups: sent %d", sent)
            return sent

    # ------------------------------------------------------------------ manual actions (dashboard)
    async def send_manual(self, lead_id: int, text: str, pause_agent: bool = True) -> bool:
        lead = dict(self.db.get_lead(lead_id))
        ok = await self.send_text(lead, text, kind="manual")
        if ok and pause_agent:
            self.db.update_lead(lead_id, paused=1, next_followup_at=None)
        return ok

    async def suggest_reply(self, lead_id: int) -> Decision:
        lead = dict(self.db.get_lead(lead_id))
        event = "inbound" if lead["last_inbound_at"] else "first_contact"
        return await self.brain.decide(lead, self._history(lead_id), event)

    def report_text(self) -> str:
        counts = self.db.status_counts()
        lines = ["📊 تقرير العملاء"] + [f"{STATUS_LABELS.get(k, k)}: {v}" for k, v in counts.items()]
        hot = [dict(r) for r in self.db.all_leads() if r["interest_level"] == "hot" and r["status"] not in CLOSED_STATUSES]
        if hot:
            lines.append("\n🔥 عملاء سخنين:")
            lines += [f"- {h['name'] or h['business_name'] or h['phone']} ({h['phone']}): {h['agent_summary'][:120]}" for h in hot[:10]]
        return "\n".join(lines)
