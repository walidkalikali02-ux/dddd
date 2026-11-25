"""Talks to the local WhatsApp Web bridge (bridge/index.js)."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

import httpx

log = logging.getLogger("transport")


class SendError(RuntimeError):
    pass


class NotOnWhatsApp(SendError):
    pass


@dataclass
class InboundMessage:
    phone: str            # international digits, no '+'
    wa_message_id: str
    profile_name: str
    type: str             # text, ptt, image, ...
    text: str             # text, or a description like "[sent a voice note]"
    from_me: bool = False  # True = you typed it yourself on your phone / WhatsApp Desktop


class BridgeClient:
    """Sends messages through WhatsApp Web. With dry_run=True nothing leaves your computer."""

    def __init__(self, base_url: str, secret: str = "", dry_run_getter=lambda: True):
        self.base_url = base_url.rstrip("/")
        self.secret = secret
        self._dry_run = dry_run_getter
        self.sent: list[dict] = []  # every send attempt (useful for the simulator and tests)

    @property
    def dry_run(self) -> bool:
        return self._dry_run()

    def _headers(self) -> dict:
        return {"X-Bridge-Secret": self.secret} if self.secret else {}

    async def send_text(self, phone: str, text: str) -> str:
        self.sent.append({"phone": phone, "text": text})
        if self.dry_run:
            log.info("[DRY RUN] to %s: %s", phone, text)
            return f"dryrun-{uuid.uuid4().hex[:12]}"
        try:
            async with httpx.AsyncClient(timeout=60) as http:
                resp = await http.post(f"{self.base_url}/send", json={"phone": phone, "text": text}, headers=self._headers())
        except httpx.HTTPError as exc:
            raise SendError(f"WhatsApp bridge is not reachable at {self.base_url} ({exc})") from exc
        if resp.status_code == 404 and "not_on_whatsapp" in resp.text:
            raise NotOnWhatsApp(f"{phone} is not on WhatsApp")
        if resp.status_code >= 400:
            raise SendError(f"bridge error {resp.status_code}: {resp.text}")
        return resp.json().get("id") or f"wa-{uuid.uuid4().hex[:12]}"

    async def status(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=5) as http:
                resp = await http.get(f"{self.base_url}/status", headers=self._headers())
            return resp.json()
        except (httpx.HTTPError, ValueError):
            return {"status": "bridge_offline", "qr": None, "me": None}

    async def logout(self) -> dict:
        async with httpx.AsyncClient(timeout=30) as http:
            resp = await http.post(f"{self.base_url}/logout", headers=self._headers())
        return resp.json()
