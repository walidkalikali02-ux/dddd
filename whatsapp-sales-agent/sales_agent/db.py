"""Small SQLite store for leads and the full message history."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    phone            TEXT NOT NULL UNIQUE,          -- digits only, international format, no '+'
    name             TEXT DEFAULT '',
    business_name    TEXT DEFAULT '',
    business_type    TEXT DEFAULT '',
    city             TEXT DEFAULT '',
    source           TEXT DEFAULT '',
    notes            TEXT DEFAULT '',               -- anything you know about the lead
    status           TEXT NOT NULL DEFAULT 'new',   -- see LEAD_STATUSES
    interest_level   TEXT DEFAULT '',               -- cold / warm / hot
    services         TEXT DEFAULT '[]',             -- JSON list of services they care about
    agent_summary    TEXT DEFAULT '',               -- the agent's running notes about the lead
    followups_sent   INTEGER NOT NULL DEFAULT 0,
    next_followup_at TEXT,                          -- UTC ISO time, NULL = none scheduled
    last_outbound_at TEXT,
    last_inbound_at  TEXT,
    paused           INTEGER NOT NULL DEFAULT 0,    -- 1 = a human took over, agent stays quiet
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id       INTEGER NOT NULL REFERENCES leads(id),
    direction     TEXT NOT NULL,                    -- 'in' (from lead) or 'out' (from us)
    kind          TEXT NOT NULL DEFAULT 'text',     -- text / manual (typed by you) / ptt / image / ...
    body          TEXT NOT NULL,
    wa_message_id TEXT UNIQUE,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id    INTEGER REFERENCES leads(id),
    text       TEXT NOT NULL,
    seen       INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kv (            -- runtime switches set from the dashboard
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_lead ON messages(lead_id, id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
"""

LEAD_STATUSES = (
    "new",                # imported, never contacted
    "contacted",          # first message sent, no reply yet
    "engaged",            # replied, conversation in progress
    "interested",         # showed clear interest / asked for prices or details
    "meeting_requested",  # wants a call / meeting / quote -> owner must act
    "won",                # agreed to buy
    "not_interested",     # politely declined
    "opted_out",          # asked not to be contacted -> never message again
)

CLOSED_STATUSES = {"won", "not_interested", "opted_out"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds") if dt else None


def parse_iso(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


class Database:
    def __init__(self, path: Path | str):
        path = Path(path)
        if str(path) != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ---------- leads ----------
    def upsert_lead(self, phone: str, **fields: Any) -> tuple[int, bool]:
        """Insert a lead or fill in empty fields of an existing one. Returns (id, created)."""
        now = iso(utcnow())
        row = self.conn.execute("SELECT * FROM leads WHERE phone = ?", (phone,)).fetchone()
        if row is None:
            cols = ["phone", "created_at", "updated_at", *fields.keys()]
            vals = [phone, now, now, *fields.values()]
            cur = self.conn.execute(
                f"INSERT INTO leads ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", vals
            )
            self.conn.commit()
            return cur.lastrowid, True
        updates = {k: v for k, v in fields.items() if v and not row[k]}
        if updates:
            self.update_lead(row["id"], **updates)
        return row["id"], False

    def update_lead(self, lead_id: int, **fields: Any) -> None:
        if not fields:
            return
        fields["updated_at"] = iso(utcnow())
        for key, value in list(fields.items()):
            if isinstance(value, (list, dict)):
                fields[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, datetime):
                fields[key] = iso(value)
        assignments = ", ".join(f"{k} = ?" for k in fields)
        self.conn.execute(f"UPDATE leads SET {assignments} WHERE id = ?", [*fields.values(), lead_id])
        self.conn.commit()

    def get_lead(self, lead_id: int) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()

    def get_lead_by_phone(self, phone: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM leads WHERE phone = ?", (phone,)).fetchone()

    def leads_to_contact(self, limit: int) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM leads WHERE status = 'new' AND paused = 0 ORDER BY id LIMIT ?", (limit,)
        ).fetchall()

    def leads_due_for_followup(self, now: datetime) -> list[sqlite3.Row]:
        placeholders = ", ".join("?" for _ in CLOSED_STATUSES)
        return self.conn.execute(
            f"""SELECT * FROM leads
                WHERE next_followup_at IS NOT NULL AND next_followup_at <= ?
                  AND paused = 0 AND status NOT IN ({placeholders})
                ORDER BY next_followup_at""",
            (iso(now), *CLOSED_STATUSES),
        ).fetchall()

    def new_contacts_since(self, since: datetime) -> int:
        row = self.conn.execute(
            """SELECT COUNT(*) FROM messages m
               WHERE m.direction = 'out' AND m.created_at >= ?
                 AND m.id = (SELECT MIN(id) FROM messages WHERE lead_id = m.lead_id)""",
            (iso(since),),
        ).fetchone()
        return row[0]

    def all_leads(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM leads ORDER BY updated_at DESC").fetchall()

    def search_leads(self, query: str = "", status: str = "", limit: int = 500) -> list[sqlite3.Row]:
        sql = "SELECT * FROM leads WHERE 1=1"
        params: list[Any] = []
        if status:
            sql += " AND status = ?"
            params.append(status)
        if query:
            sql += " AND (phone LIKE ? OR name LIKE ? OR business_name LIKE ? OR business_type LIKE ? OR city LIKE ?)"
            params += [f"%{query}%"] * 5
        sql += " ORDER BY COALESCE(last_inbound_at, last_outbound_at, updated_at) DESC LIMIT ?"
        params.append(limit)
        return self.conn.execute(sql, params).fetchall()

    def delete_lead(self, lead_id: int) -> None:
        self.conn.execute("DELETE FROM messages WHERE lead_id = ?", (lead_id,))
        self.conn.execute("DELETE FROM alerts WHERE lead_id = ?", (lead_id,))
        self.conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        self.conn.commit()

    # ---------- alerts ----------
    def add_alert(self, text: str, lead_id: int | None = None) -> None:
        self.conn.execute(
            "INSERT INTO alerts (lead_id, text, created_at) VALUES (?, ?, ?)", (lead_id, text, iso(utcnow()))
        )
        self.conn.commit()

    def alerts(self, limit: int = 50) -> list[sqlite3.Row]:
        return self.conn.execute(
            """SELECT a.*, l.name AS lead_name, l.phone AS lead_phone FROM alerts a
               LEFT JOIN leads l ON l.id = a.lead_id ORDER BY a.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()

    def mark_alerts_seen(self) -> None:
        self.conn.execute("UPDATE alerts SET seen = 1 WHERE seen = 0")
        self.conn.commit()

    # ---------- switches ----------
    def get_flag(self, key: str, default: bool) -> bool:
        row = self.conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return default if row is None else row[0] == "1"

    def set_flag(self, key: str, value: bool) -> None:
        self.conn.execute(
            "INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, "1" if value else "0"),
        )
        self.conn.commit()

    def sent_today(self, since: datetime) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) FROM messages WHERE direction = 'out' AND created_at >= ?", (iso(since),)
        ).fetchone()
        return row[0]

    def status_counts(self) -> dict[str, int]:
        rows = self.conn.execute("SELECT status, COUNT(*) FROM leads GROUP BY status").fetchall()
        return {r[0]: r[1] for r in rows}

    # ---------- messages ----------
    def add_message(
        self, lead_id: int, direction: str, body: str, kind: str = "text", wa_message_id: str | None = None
    ) -> int | None:
        """Store a message. Returns None if this WhatsApp message id was already stored (duplicate webhook)."""
        try:
            cur = self.conn.execute(
                "INSERT INTO messages (lead_id, direction, kind, body, wa_message_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (lead_id, direction, kind, body, wa_message_id, iso(utcnow())),
            )
        except sqlite3.IntegrityError:
            return None
        now = iso(utcnow())
        column = "last_inbound_at" if direction == "in" else "last_outbound_at"
        self.conn.execute(f"UPDATE leads SET {column} = ?, updated_at = ? WHERE id = ?", (now, now, lead_id))
        self.conn.commit()
        return cur.lastrowid

    def history(self, lead_id: int, limit: int = 60) -> list[sqlite3.Row]:
        rows = self.conn.execute(
            "SELECT * FROM messages WHERE lead_id = ? ORDER BY id DESC LIMIT ?", (lead_id, limit)
        ).fetchall()
        return list(reversed(rows))

    def last_message_id(self, lead_id: int, direction: str = "in") -> int | None:
        row = self.conn.execute(
            "SELECT MAX(id) FROM messages WHERE lead_id = ? AND direction = ?", (lead_id, direction)
        ).fetchone()
        return row[0]


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]
