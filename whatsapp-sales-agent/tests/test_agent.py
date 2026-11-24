import asyncio
import dataclasses
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from sales_agent.brain import DECISION_SCHEMA, Decision, build_user_prompt
from sales_agent.config import Settings
from sales_agent.db import Database, iso, utcnow
from sales_agent.engine import SalesAgent
from sales_agent.leads import import_leads, normalize_phone
from sales_agent.server import create_app
from sales_agent.transport import BridgeClient, InboundMessage


def decision(**overrides) -> Decision:
    base = dict(action="send_message", message="أهلا! تحب أبعتلك أمثلة من شغلنا؟", lead_status="engaged",
                interest_level="warm", services_of_interest=["website"], followup_in_hours=24,
                lead_summary="مطعم مهتم بموقع", owner_alert="")
    base.update(overrides)
    return Decision(**base)


class FakeBrain:
    def __init__(self, *decisions):
        self.queue = list(decisions)
        self.calls = []

    async def decide(self, lead, history, event="inbound"):
        self.calls.append((event, lead, history))
        return self.queue.pop(0) if self.queue else decision()

    def set_business_profile(self, text):
        self.profile = text


async def no_sleep(_):
    return None


@pytest.fixture
def make_agent(tmp_path):
    def _make(*decisions, **setting_overrides):
        s = dataclasses.replace(Settings(), db_path=tmp_path / "t.db", default_country_code="20", owner_phone="",
                                reply_debounce_seconds=0, send_hour_start=0, send_hour_end=24, **setting_overrides)
        db = Database(s.db_path)
        wa = BridgeClient("http://127.0.0.1:9", dry_run_getter=lambda: db.get_flag("dry_run", True))
        return SalesAgent(db, wa, FakeBrain(*decisions), s, sleep=no_sleep)
    return _make


def run(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------- leads import
@pytest.mark.parametrize("raw,expected", [
    ("01001234567", "201001234567"),
    ("+20 100 123 4567", "201001234567"),
    ("00201001234567", "201001234567"),
    ("٠١٠٠١٢٣٤٥٦٧", "201001234567"),
    ("201001234567.0", "201001234567"),
    ("123", None),
])
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw, "20") == expected


def test_import_csv_with_arabic_headers(tmp_path):
    f = tmp_path / "leads.csv"
    f.write_text("الاسم,رقم الهاتف,اسم النشاط,نوع النشاط\nأحمد,01001234567,مطعم السعادة,مطعم\nسارة,12,x,y\n", encoding="utf-8")
    db = Database(tmp_path / "db.sqlite")
    result = import_leads(f, db, "20")
    assert result["added"] == 1 and result["skipped"] == [3]
    lead = db.get_lead_by_phone("201001234567")
    assert lead["name"] == "أحمد" and lead["business_type"] == "مطعم" and lead["status"] == "new"


# ---------------------------------------------------------------- inbound
def test_unknown_numbers_are_ignored(make_agent):
    agent = make_agent()
    run(agent.handle_inbound(InboundMessage("201112223334", "m1", "صاحبي", "text", "ازيك")))
    assert agent.db.get_lead_by_phone("201112223334") is None
    assert agent.brain.calls == [] and agent.wa.sent == []


def test_reply_to_lead_updates_record(make_agent):
    agent = make_agent(decision(lead_status="interested", interest_level="hot"))
    lead_id, _ = agent.db.upsert_lead("201001234567", name="أحمد", status="contacted")
    run(agent.handle_inbound(InboundMessage("201001234567", "m1", "Ahmed", "text", "عاوز أعرف الأسعار")))
    lead = agent.db.get_lead(lead_id)
    assert agent.wa.sent[-1]["text"].startswith("أهلا")
    assert lead["status"] == "interested" and lead["interest_level"] == "hot"
    assert lead["next_followup_at"] is not None
    assert [m["direction"] for m in agent.db.history(lead_id)] == ["in", "out"]


def test_duplicate_delivery_is_processed_once(make_agent):
    agent = make_agent()
    agent.db.upsert_lead("201001234567", status="contacted")
    msg = InboundMessage("201001234567", "same-id", "", "text", "مرحبا")
    run(agent.handle_inbound(msg))
    run(agent.handle_inbound(msg))
    assert len(agent.brain.calls) == 1


def test_stop_word_opts_out_without_claude(make_agent):
    agent = make_agent()
    lead_id, _ = agent.db.upsert_lead("201001234567", status="contacted", next_followup_at=iso(utcnow()))
    run(agent.handle_inbound(InboundMessage("201001234567", "m1", "", "text", "توقف")))
    lead = agent.db.get_lead(lead_id)
    assert lead["status"] == "opted_out" and lead["next_followup_at"] is None
    assert agent.brain.calls == [] and "مش هنبعت" in agent.wa.sent[-1]["text"]


def test_manual_reply_from_phone_pauses_agent(make_agent):
    agent = make_agent()
    lead_id, _ = agent.db.upsert_lead("201001234567", status="engaged")
    run(agent.handle_inbound(InboundMessage("201001234567", "m1", "", "text", "أهلا يا أحمد، أنا صاحب الشركة", from_me=True)))
    assert agent.db.get_lead(lead_id)["paused"] == 1
    assert agent.db.alerts()[0]["lead_id"] == lead_id
    run(agent.handle_inbound(InboundMessage("201001234567", "m2", "", "text", "تمام")))
    assert agent.brain.calls == []  # paused: the agent stays quiet


def test_handoff_pauses_and_alerts(make_agent):
    agent = make_agent(decision(action="handoff_to_human", lead_status="meeting_requested",
                                owner_alert="عاوز مكالمة بكرة الساعة ٥", message="تمام، الفريق هيكلمك قريب"))
    lead_id, _ = agent.db.upsert_lead("201001234567", name="أحمد", status="engaged")
    run(agent.handle_inbound(InboundMessage("201001234567", "m1", "", "text", "كلموني بكرة")))
    lead = agent.db.get_lead(lead_id)
    assert lead["paused"] == 1 and lead["status"] == "meeting_requested" and lead["next_followup_at"] is None
    assert "مكالمة" in agent.db.alerts()[0]["text"]


# ---------------------------------------------------------------- outbound jobs
def test_outreach_needs_automation_switch_and_respects_cap(make_agent):
    agent = make_agent(max_new_contacts_per_day=2)
    for i in range(4):
        agent.db.upsert_lead(f"20100123456{i}", name=f"lead{i}")
    assert run(agent.run_outreach()) == 0  # automation is off by default
    agent.db.set_flag("automation_on", True)
    assert run(agent.run_outreach()) == 2
    assert run(agent.run_outreach()) == 0  # daily cap reached
    assert {c[0] for c in agent.brain.calls} == {"first_contact"}
    assert agent.db.status_counts().get("new") == 2


def test_followups_stop_at_max(make_agent):
    agent = make_agent(max_followups=2, followup_gap_days=[1, 1])
    agent.db.set_flag("automation_on", True)
    lead_id, _ = agent.db.upsert_lead("201001234567", status="contacted")
    agent.db.update_lead(lead_id, next_followup_at=utcnow())
    for _ in range(4):
        if agent.db.get_lead(lead_id)["next_followup_at"]:
            agent.db.update_lead(lead_id, next_followup_at=utcnow() - timedelta(minutes=1))
        run(agent.run_followups())
    lead = agent.db.get_lead(lead_id)
    assert lead["followups_sent"] == 2 and lead["next_followup_at"] is None


def test_prompt_renders_for_all_events():
    lead = {"name": "أحمد", "business_type": "مطعم", "followups_sent": 1, "status": "contacted"}
    history = [{"created_at": iso(utcnow()), "direction": "out", "kind": "text", "body": "أهلا"}]
    for event in ("first_contact", "inbound", "followup"):
        prompt = build_user_prompt(lead, history, event, "Africa/Cairo", 3)
        assert "أحمد" in prompt and "<task>" in prompt
    assert set(DECISION_SCHEMA["required"]) == set(Decision.model_fields)


# ---------------------------------------------------------------- dashboard API
def test_dashboard_api(make_agent, tmp_path):
    agent = make_agent()
    profile = tmp_path / "profile.md"
    profile.write_text("خدماتنا: مواقع", encoding="utf-8")
    agent.s.business_profile_path = profile
    agent.s.bridge_secret = "s3cret"
    client = TestClient(create_app(agent, agent.s, background_services=False))

    assert client.get("/").status_code == 200
    ov = client.get("/api/overview").json()
    assert ov["flags"] == {"automation_on": False, "replies_on": True, "dry_run": True}
    assert ov["whatsapp"]["status"] == "bridge_offline"

    r = client.post("/api/leads/import", files={"file": ("l.csv", "phone,name\n01001234567,أحمد\n".encode(), "text/csv")})
    assert r.json()["added"] == 1
    lead = client.get("/api/leads?q=أحمد").json()[0]

    assert client.post(f"/api/leads/{lead['id']}/send", json={"text": "أهلا"}).status_code == 200
    detail = client.get(f"/api/leads/{lead['id']}").json()
    assert detail["lead"]["paused"] == 1 and detail["messages"][0]["kind"] == "manual"

    assert client.patch(f"/api/leads/{lead['id']}", json={"paused": False, "status": "won"}).status_code == 200
    assert client.get(f"/api/leads/{lead['id']}").json()["lead"]["status"] == "won"

    assert client.post("/api/flags", json={"automation_on": True}).status_code == 200
    assert client.get("/api/overview").json()["flags"]["automation_on"] is True

    assert client.put("/api/profile", json={"text": "جديد"}).status_code == 200
    assert profile.read_text(encoding="utf-8") == "جديد"

    assert client.post("/bridge/inbound", json={"phone": "201001234567", "text": "x"}).status_code == 401
    ok = client.post("/bridge/inbound", json={"phone": "201001234567", "text": "x", "wa_message_id": "w1"},
                     headers={"X-Bridge-Secret": "s3cret"})
    assert ok.status_code == 200
    assert "201001234567" in client.get("/api/export.csv").text


def test_dashboard_password(make_agent):
    agent = make_agent(admin_password="pw")
    client = TestClient(create_app(agent, agent.s, background_services=False))
    assert client.get("/api/overview").status_code == 401
    assert client.get("/api/overview", auth=("admin", "pw")).status_code == 200
