"""Telegram notification wrapper for the live trading engine.

Configuration — pick one approach:
  A) Edit config.py:   TELEGRAM_BOT_TOKEN = "..."  TELEGRAM_CHAT_ID = "..."
  B) Environment vars: export TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...

The first line of every message is auto-bolded so it reads clearly on a phone
(e.g. "TRADE OPENED" stands out from the price detail below it).

Quick setup test:
    cd /path/to/Ict
    python -m scripts.notify

How to get your credentials (one-time setup):
  1. Open Telegram, search for @BotFather, send /newbot
  2. Follow prompts — copy the token it gives you (looks like 123456:ABC-...)
  3. Search for @userinfobot, send /start — it replies with your numeric ID
  4. Paste both into config.py or set as env vars
"""
import json
import os
import urllib.error
import urllib.request

# Read from config at import time; env vars are re-read on every send (allows
# runtime injection without restarting the process).
try:
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config as _cfg
    _TOKEN_CFG   = getattr(_cfg, "TELEGRAM_BOT_TOKEN", "")
    _CHAT_ID_CFG = getattr(_cfg, "TELEGRAM_CHAT_ID", "")
except Exception:
    _TOKEN_CFG = _CHAT_ID_CFG = ""


def _esc(text: str) -> str:
    """Escape HTML special chars so Telegram's HTML parse_mode doesn't choke."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt(text: str) -> str:
    """Bold the first line (message type header), plain-text the rest."""
    parts = text.split("\n", 1)
    if len(parts) == 2:
        return f"<b>{_esc(parts[0])}</b>\n{_esc(parts[1])}"
    return f"<b>{_esc(parts[0])}</b>"


def send_message(text: str) -> bool:
    """Post `text` to the configured Telegram chat.

    Returns True on success, False on any failure. Never raises — the trading
    engine must not halt because a notification failed.
    """
    token   = _TOKEN_CFG   or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = _CHAT_ID_CFG or os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return False

    url     = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id":    chat_id,
        "text":       _fmt(text),
        "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        # Log the Telegram error body so misconfiguration is diagnosable
        try:
            body = exc.read().decode(errors="replace")
        except Exception:
            body = str(exc)
        print(f"[notify] Telegram HTTP {exc.code}: {body}", flush=True)
        return False
    except Exception as exc:
        print(f"[notify] send failed: {exc}", flush=True)
        return False


def test() -> bool:
    """Send a test message. Call this after setting credentials to confirm setup."""
    return send_message("ICT Bot — test OK\nNotifications are working.")


if __name__ == "__main__":
    token   = _TOKEN_CFG   or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = _CHAT_ID_CFG or os.getenv("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        print("No credentials found.")
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py or as env vars.")
    else:
        print(f"Token:   {token[:10]}... (truncated)")
        print(f"Chat ID: {chat_id}")
        print("Sending test message...")
        ok = test()
        if ok:
            print("Delivered — check your Telegram.")
        else:
            print("FAILED — check the error above.")
