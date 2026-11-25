"""All settings come from environment variables (or a .env file in the project folder)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


def _list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass
class Settings:
    # --- WhatsApp Web bridge (bridge/index.js) ---
    bridge_url: str = field(default_factory=lambda: os.getenv("BRIDGE_URL", "http://127.0.0.1:3100"))
    bridge_secret: str = field(default_factory=lambda: os.getenv("BRIDGE_SECRET", ""))
    bridge_autostart: bool = field(default_factory=lambda: _bool("BRIDGE_AUTOSTART", True))
    # Reply to people who are NOT in your leads list? Keep false if this is also your personal number,
    # otherwise friends and family would get sales replies.
    reply_to_unknown: bool = field(default_factory=lambda: _bool("REPLY_TO_UNKNOWN", False))

    # --- Claude ---
    model: str = field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-opus-5-5"))
    effort: str = field(default_factory=lambda: os.getenv("CLAUDE_EFFORT", "medium"))

    # --- Business / owner ---
    business_profile_path: Path = field(
        default_factory=lambda: PROJECT_DIR / os.getenv("BUSINESS_PROFILE", "business_profile.md")
    )
    owner_phone: str = field(default_factory=lambda: os.getenv("OWNER_PHONE", ""))
    default_country_code: str = field(default_factory=lambda: os.getenv("DEFAULT_COUNTRY_CODE", ""))

    # --- Sending policy ---
    timezone: str = field(default_factory=lambda: os.getenv("TIMEZONE", "Africa/Cairo"))
    send_hour_start: int = field(default_factory=lambda: _int("SEND_HOUR_START", 10))
    send_hour_end: int = field(default_factory=lambda: _int("SEND_HOUR_END", 20))
    max_new_contacts_per_day: int = field(default_factory=lambda: _int("MAX_NEW_CONTACTS_PER_DAY", 20))
    max_followups: int = field(default_factory=lambda: _int("MAX_FOLLOWUPS", 3))
    followup_gap_days: list[int] = field(default_factory=lambda: [int(x) for x in _list("FOLLOWUP_GAP_DAYS", "2,4,7")])
    min_seconds_between_sends: int = field(default_factory=lambda: _int("MIN_SECONDS_BETWEEN_SENDS", 45))
    max_seconds_between_sends: int = field(default_factory=lambda: _int("MAX_SECONDS_BETWEEN_SENDS", 120))
    reply_debounce_seconds: int = field(default_factory=lambda: _int("REPLY_DEBOUNCE_SECONDS", 8))
    scheduler_interval_minutes: int = field(default_factory=lambda: _int("SCHEDULER_INTERVAL_MINUTES", 10))

    # --- Dashboard ---
    admin_password: str = field(default_factory=lambda: os.getenv("ADMIN_PASSWORD", ""))
    db_path: Path = field(default_factory=lambda: PROJECT_DIR / os.getenv("DB_PATH", "data/agent.db"))

    def business_profile(self) -> str:
        return self.business_profile_path.read_text(encoding="utf-8")


settings = Settings()
