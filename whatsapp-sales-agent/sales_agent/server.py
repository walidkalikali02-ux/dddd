"""Dashboard + API server. Also starts the WhatsApp Web bridge and the automatic scheduler."""

from __future__ import annotations

import asyncio
import csv
import io
import logging
import os
import secrets
import shutil
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from .brain import Brain
from .config import PROJECT_DIR, Settings, settings
from .db import LEAD_STATUSES, Database, rows_to_dicts, utcnow
from .engine import STATUS_LABELS, SalesAgent
from .leads import import_leads, normalize_phone
from .transport import BridgeClient, InboundMessage

log = logging.getLogger("server")
STATIC_DIR = Path(__file__).parent / "static"
BRIDGE_DIR = PROJECT_DIR / "bridge"


def build_agent(s: Settings) -> SalesAgent:
    db = Database(s.db_path)
    wa = BridgeClient(s.bridge_url, s.bridge_secret, dry_run_getter=lambda: db.get_flag("dry_run", True))
    brain = Brain(s.business_profile(), model=s.model, effort=s.effort, timezone=s.timezone,
                  max_followups=s.max_followups)
    return SalesAgent(db, wa, brain, s)


async def scheduler_loop(agent: SalesAgent, interval_minutes: int) -> None:
    while True:
        try:
            await agent.run_outreach()
            await agent.run_followups()
        except Exception:  # keep the loop alive no matter what
            log.exception("scheduled run failed")
        await asyncio.sleep(interval_minutes * 60)


async def start_bridge(s: Settings) -> asyncio.subprocess.Process | None:
    node = shutil.which("node")
    if not node:
        log.error("Node.js is not installed - the WhatsApp Web bridge can't start. Install it from nodejs.org")
        return None
    if not (BRIDGE_DIR / "node_modules").exists():
        log.error("Run 'npm install' inside the bridge folder first (or use the setup script).")
        return None
    port = s.bridge_url.rsplit(":", 1)[-1].strip("/") or "3100"
    env = {**os.environ, "BRIDGE_PORT": port, "BRIDGE_SECRET": s.bridge_secret,
           "AGENT_URL": f"http://127.0.0.1:{os.getenv('PORT', '8000')}"}
    proc = await asyncio.create_subprocess_exec(node, "index.js", cwd=str(BRIDGE_DIR), env=env)
    log.info("started WhatsApp Web bridge (pid %s)", proc.pid)
    return proc


class FlagsIn(BaseModel):
    automation_on: bool | None = None
    replies_on: bool | None = None
    dry_run: bool | None = None


class LeadIn(BaseModel):
    phone: str
    name: str = ""
    business_name: str = ""
    business_type: str = ""
    city: str = ""
    notes: str = ""


class LeadPatch(BaseModel):
    name: str | None = None
    business_name: str | None = None
    business_type: str | None = None
    city: str | None = None
    notes: str | None = None
    status: str | None = None
    paused: bool | None = None
    next_followup_at: str | None = None


class SendIn(BaseModel):
    text: str
    pause_agent: bool = True


class ProfileIn(BaseModel):
    text: str


class InboundIn(BaseModel):
    phone: str
    wa_message_id: str = ""
    profile_name: str = ""
    type: str = "text"
    text: str = ""
    from_me: bool = False


def create_app(agent: SalesAgent | None = None, s: Settings = settings, background_services: bool = True) -> FastAPI:
    agent = agent or build_agent(s)
    security = HTTPBasic(auto_error=False)

    def require_admin(creds: HTTPBasicCredentials | None = Depends(security)):
        if not s.admin_password:
            return
        if creds is None or not secrets.compare_digest(creds.password.encode(), s.admin_password.encode()):
            raise HTTPException(status_code=401, detail="login required", headers={"WWW-Authenticate": "Basic"})

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        bridge = await start_bridge(s) if background_services and s.bridge_autostart else None
        loop = asyncio.create_task(scheduler_loop(agent, s.scheduler_interval_minutes)) if background_services else None
        yield
        if loop:
            loop.cancel()
        if bridge and bridge.returncode is None:
            bridge.terminate()

    app = FastAPI(title="WhatsApp Sales Agent", lifespan=lifespan)
    app.state.agent = agent
    admin = [Depends(require_admin)]

    # ---------------- bridge -> agent ----------------
    @app.post("/bridge/inbound")
    async def bridge_inbound(payload: InboundIn, request: Request, background: BackgroundTasks):
        if s.bridge_secret and request.headers.get("X-Bridge-Secret") != s.bridge_secret:
            raise HTTPException(status_code=401, detail="bad secret")
        background.add_task(agent.handle_inbound, InboundMessage(**payload.model_dump()))
        return {"ok": True}

    # ---------------- dashboard ----------------
    @app.get("/", dependencies=admin)
    async def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/overview", dependencies=admin)
    async def overview():
        midnight = agent._local_midnight()
        return {
            "whatsapp": await agent.wa.status(),
            "flags": {"automation_on": agent.automation_on, "replies_on": agent.replies_on, "dry_run": agent.dry_run},
            "counts": agent.db.status_counts(),
            "labels": STATUS_LABELS,
            "statuses": LEAD_STATUSES,
            "today": {"new_contacts": agent.db.new_contacts_since(midnight), "messages_sent": agent.db.sent_today(midnight)},
            "limits": {
                "max_new_contacts_per_day": s.max_new_contacts_per_day,
                "max_followups": s.max_followups,
                "send_hours": f"{s.send_hour_start}:00 - {s.send_hour_end}:00 ({s.timezone})",
                "in_send_window": agent.in_send_window(),
            },
            "unseen_alerts": sum(1 for a in agent.db.alerts(200) if not a["seen"]),
            "job_running": agent._job_lock.locked(),
            "model": s.model,
        }

    @app.post("/api/flags", dependencies=admin)
    async def set_flags(flags: FlagsIn):
        for key, value in flags.model_dump(exclude_none=True).items():
            agent.db.set_flag(key, value)
        return {"ok": True}

    @app.get("/api/leads", dependencies=admin)
    async def list_leads(q: str = "", status: str = ""):
        return rows_to_dicts(agent.db.search_leads(q, status))

    @app.post("/api/leads", dependencies=admin)
    async def add_lead(lead: LeadIn):
        phone = normalize_phone(lead.phone, s.default_country_code)
        if not phone:
            raise HTTPException(status_code=400, detail="رقم غير صحيح")
        lead_id, created = agent.db.upsert_lead(phone, **lead.model_dump(exclude={"phone"}), source="dashboard")
        return {"id": lead_id, "created": created}

    @app.post("/api/leads/import", dependencies=admin)
    async def import_file(file: UploadFile = File(...)):
        suffix = Path(file.filename or "leads.csv").suffix or ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
        try:
            result = import_leads(tmp.name, agent.db, s.default_country_code)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        finally:
            os.unlink(tmp.name)
        return result

    def _lead_or_404(lead_id: int) -> dict:
        row = agent.db.get_lead(lead_id)
        if row is None:
            raise HTTPException(status_code=404, detail="lead not found")
        return dict(row)

    @app.get("/api/leads/{lead_id}", dependencies=admin)
    async def get_lead(lead_id: int):
        lead = _lead_or_404(lead_id)
        return {"lead": lead, "messages": rows_to_dicts(agent.db.history(lead_id, limit=500))}

    @app.patch("/api/leads/{lead_id}", dependencies=admin)
    async def patch_lead(lead_id: int, patch: LeadPatch):
        _lead_or_404(lead_id)
        fields = patch.model_dump(exclude_unset=True)
        if "status" in fields and fields["status"] not in LEAD_STATUSES:
            raise HTTPException(status_code=400, detail="bad status")
        if "paused" in fields:
            fields["paused"] = 1 if fields["paused"] else 0
        agent.db.update_lead(lead_id, **fields)
        return {"ok": True}

    @app.delete("/api/leads/{lead_id}", dependencies=admin)
    async def delete_lead(lead_id: int):
        _lead_or_404(lead_id)
        agent.db.delete_lead(lead_id)
        return {"ok": True}

    @app.post("/api/leads/{lead_id}/send", dependencies=admin)
    async def send(lead_id: int, body: SendIn):
        _lead_or_404(lead_id)
        if not body.text.strip():
            raise HTTPException(status_code=400, detail="empty message")
        if not await agent.send_manual(lead_id, body.text.strip(), body.pause_agent):
            raise HTTPException(status_code=502, detail="فشل الإرسال - اتأكد إن واتساب متصل")
        return {"ok": True}

    @app.post("/api/leads/{lead_id}/suggest", dependencies=admin)
    async def suggest(lead_id: int):
        _lead_or_404(lead_id)
        return (await agent.suggest_reply(lead_id)).model_dump()

    @app.post("/api/leads/{lead_id}/agent-reply", dependencies=admin)
    async def agent_reply(lead_id: int):
        lead = _lead_or_404(lead_id)
        decision = await agent.suggest_reply(lead_id)
        event = "inbound" if lead["last_inbound_at"] else "first_contact"
        sent = await agent.apply_decision(lead, decision, event)
        return {"sent": sent, "decision": decision.model_dump()}

    @app.post("/api/run/{job}", dependencies=admin)
    async def run_job(job: str, background: BackgroundTasks, limit: int | None = None):
        if agent._job_lock.locked():
            raise HTTPException(status_code=409, detail="فيه عملية إرسال شغالة بالفعل")
        if job == "outreach":
            background.add_task(agent.run_outreach, True, limit)
        elif job == "followups":
            background.add_task(agent.run_followups, True)
        else:
            raise HTTPException(status_code=404, detail="unknown job")
        return {"started": job}

    @app.get("/api/alerts", dependencies=admin)
    async def alerts():
        return rows_to_dicts(agent.db.alerts(100))

    @app.post("/api/alerts/seen", dependencies=admin)
    async def alerts_seen():
        agent.db.mark_alerts_seen()
        return {"ok": True}

    @app.get("/api/profile", dependencies=admin)
    async def get_profile():
        return {"text": s.business_profile()}

    @app.put("/api/profile", dependencies=admin)
    async def put_profile(body: ProfileIn):
        s.business_profile_path.write_text(body.text, encoding="utf-8")
        agent.brain.set_business_profile(body.text)
        return {"ok": True}

    @app.get("/api/export.csv", dependencies=admin)
    async def export_csv():
        rows = rows_to_dicts(agent.db.all_leads())
        buf = io.StringIO()
        if rows:
            writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        data = "﻿" + buf.getvalue()  # BOM so Excel shows Arabic correctly
        name = f"leads-{utcnow():%Y%m%d}.csv"
        return StreamingResponse(iter([data]), media_type="text/csv",
                                 headers={"Content-Disposition": f"attachment; filename={name}"})

    @app.post("/api/whatsapp/logout", dependencies=admin)
    async def whatsapp_logout():
        try:
            return await agent.wa.logout()
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc))

    return app
