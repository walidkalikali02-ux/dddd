"""Command line: python -m sales_agent <command>"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import webbrowser

from .config import settings


def _agent():
    from .server import build_agent

    return build_agent(settings)


def cmd_serve(args):
    import threading

    import uvicorn

    from .server import create_app

    os.environ["PORT"] = str(args.port)
    url = f"http://127.0.0.1:{args.port}"
    print(f"\n✅ لوحة التحكم: {url}\n")
    if not args.no_browser:
        threading.Timer(2.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="info")


def cmd_import(args):
    from .db import Database
    from .leads import import_leads

    result = import_leads(args.file, Database(settings.db_path), settings.default_country_code)
    print(f"تمت إضافة {result['added']} عميل، وتحديث {result['updated']}، من أصل {result['total']} صف.")
    if result["skipped"]:
        print(f"⚠️ صفوف أرقامها غير صحيحة وتم تخطيها: {result['skipped']}")


def cmd_report(args):
    print(_agent().report_text())


def cmd_simulate(args):
    """Chat with the agent in the terminal as if you were a lead. Nothing is sent on WhatsApp."""
    from .transport import InboundMessage

    settings.reply_debounce_seconds = 0
    settings.owner_phone = ""
    settings.db_path = settings.db_path.with_name("simulation.db")
    agent = _agent()
    agent.db.set_flag("dry_run", True)
    phone = args.phone
    agent.db.upsert_lead(phone, name=args.name, business_name=args.business, business_type=args.type, source="simulation")

    def show(before: int):
        for item in agent.wa.sent[before:]:
            print(f"🤖 الايجنت: {item['text']}\n")
        if len(agent.wa.sent) == before:
            print("🤖 (الايجنت اختار ميردش)\n")
        lead = dict(agent.db.get_lead_by_phone(phone))
        print(f"   ↳ الحالة: {lead['status']} | الاهتمام: {lead['interest_level']} | متابعة: {lead['next_followup_at']}")
        print(f"   ↳ ملخص: {lead['agent_summary']}\n")

    async def run():
        lead = dict(agent.db.get_lead_by_phone(phone))
        if lead["status"] == "new":
            before = len(agent.wa.sent)
            decision = await agent.brain.decide(lead, [], "first_contact")
            await agent.apply_decision(lead, decision, "first_contact")
            print("\n[أول رسالة للعميل]")
            show(before)
        print("اكتب كأنك العميل ('خروج' للإنهاء، 'متابعة' لتجربة رسالة متابعة لو العميل مردش):\n")
        counter = 0
        while True:
            try:
                text = input("👤 العميل: ").strip()
            except EOFError:
                break
            if text in {"خروج", "exit", "quit"}:
                break
            before = len(agent.wa.sent)
            if text in {"متابعة", "followup"}:
                lead = dict(agent.db.get_lead_by_phone(phone))
                decision = await agent.brain.decide(lead, agent._history(lead["id"]), "followup")
                await agent.apply_decision(lead, decision, "followup")
            elif text:
                counter += 1
                agent.db.update_lead(lead["id"], paused=0)
                await agent.handle_inbound(InboundMessage(phone, f"sim-{os.getpid()}-{counter}", args.name, "text", text))
            show(before)

    asyncio.run(run())


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="python -m sales_agent", description="WhatsApp sales agent")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("serve", help="start the dashboard, the WhatsApp Web bridge and the scheduler")
    p.add_argument("--host", default="127.0.0.1", help="use 0.0.0.0 to open the dashboard from other devices")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("import", help="import leads from CSV / Excel")
    p.add_argument("file")
    p.set_defaults(func=cmd_import)

    sub.add_parser("report", help="summary of all leads").set_defaults(func=cmd_report)

    p = sub.add_parser("simulate", help="chat with the agent in the terminal as a fake lead (uses Claude, sends nothing)")
    p.add_argument("--phone", default="999000000001")
    p.add_argument("--name", default="أحمد")
    p.add_argument("--business", default="مطعم السعادة")
    p.add_argument("--type", default="مطعم")
    p.set_defaults(func=cmd_simulate)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
