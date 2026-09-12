r"""Standalone TWO-WAY Telegram test - no MT5, no broker required.

    .\.venv\Scripts\python.exe -m live.telegram_test
    (or: powershell -ExecutionPolicy Bypass -File scripts\telegram_test.ps1)

Loads live.env, sends a welcome message to your phone, then listens for your
commands (/status, /lot, /bias, /levels, /hold, /help, ...) and acks each one -
exactly as the live bot will, but with no MetaTrader connection. Ctrl-C to stop.

Run this FIRST to prove your Telegram bot token + chat id work in both
directions, before installing MetaTrader 5.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_env_file() -> str | None:
    """Load KEY=VALUE lines from live.env into os.environ (no external deps)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for path in ("live.env", os.path.join(root, "live.env")):
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k:
                    os.environ[k] = v
        return path
    return None


def main() -> int:
    src = _load_env_file()
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat = os.getenv("TELEGRAM_CHAT_ID", "")

    print(f"live.env: {src or 'not found'}")
    if not token or not chat:
        print("\nNo Telegram credentials found.")
        print("Put TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in live.env, then re-run.")
        print("  token  <- @BotFather  (/newbot)")
        print("  chatid <- @userinfobot (/start)")
        return 1

    # Import only after env is loaded, so notify/telegram_control read the values.
    from scripts.notify import send_message
    from live.session_inputs import SessionInputs
    from live import telegram_control as tc

    print(f"Token:   {token[:10]}... | Chat: {chat}")
    print("Sending welcome message...")
    ok = send_message(
        "TELEGRAM CONNECTED\n"
        "Two-way test is live (no MT5 yet). Reply to try the controls:\n"
        "/status\n"
        "/lot 0.02\n"
        "/bias EURUSD long\n"
        "/levels EURUSD buy 1.0975 sell 1.0900\n"
        "/help\n"
        "(Ctrl-C in PowerShell when you're done.)"
    )
    if not ok:
        print("\nFAILED to send. Common causes:")
        print("  - wrong token or chat id")
        print("  - you haven't messaged your bot yet: open it in Telegram and send /start once,")
        print("    so Telegram allows the bot to message you back.")
        return 1

    print("Welcome message sent - check your phone.")
    print("Listening for your commands (Ctrl-C to stop)...\n")

    inputs = SessionInputs()
    try:
        while True:
            n = tc.poll(inputs)   # trader=None: state cmds apply; /close /halt ack only
            if n:
                print(f"applied {n} command(s). Current plan:")
                print("   " + inputs.status_text().replace("\n", "\n   ") + "\n")
            time.sleep(2)
    except KeyboardInterrupt:
        send_message("Telegram test stopped.")
        print("\nStopped. Two-way Telegram confirmed - you can set up MT5 next.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
