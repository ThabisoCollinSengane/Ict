"""Telegram notification wrapper for live trading alerts.

Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py or as
environment variables. All sends are fire-and-forget — failures are
swallowed silently so they never interrupt the trading engine.

Usage:
    from scripts.notify import send_message
    send_message("EURUSD LONG opened at 1.08500")
"""
import json
import os
import urllib.request
import urllib.error

try:
    import sys as _sys
    import os as _os
    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    import config as _cfg
    _TOKEN   = getattr(_cfg, "TELEGRAM_BOT_TOKEN", "")
    _CHAT_ID = getattr(_cfg, "TELEGRAM_CHAT_ID", "")
except Exception:
    _TOKEN   = ""
    _CHAT_ID = ""


def send_message(text: str) -> bool:
    """Post `text` to the configured Telegram chat.

    Returns True on success, False on any failure. Never raises.
    """
    token   = _TOKEN   or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = _CHAT_ID or os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return False

    url     = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode()
    req     = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False
