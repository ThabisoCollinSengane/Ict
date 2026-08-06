"""Two-way Telegram control for the live engine (semi-auto inputs).

Polls Telegram getUpdates for the trader's replies and applies them to a
SessionInputs store. Reply to the session-start template with:

  /lot 0.02                    day lot for ALL pairs
  /lot GBPUSD 0.03             day lot for one pair
  /bias EURUSD long            long | short | both(=auto)
  /levels EURUSD buy 1.0950 1.0975 sell 1.0900 1.0880
  /auto EURUSD                 revert one pair to full auto
  /clear                       revert ALL pairs to full auto
  /status                      echo today's inputs
  /help                        command list

Only messages from the configured TELEGRAM_CHAT_ID are honoured — no one else
can steer the bot. Parsing is pure/offline-testable; the network poll is a thin
wrapper around it (see parse_command).
"""
from __future__ import annotations

import json
import os
import ssl
import urllib.parse
import urllib.request

import config

try:
    from scripts.notify import send_message as _notify, _SSL_CTX  # reuse CA bundle
except Exception:  # pragma: no cover
    _SSL_CTX = ssl.create_default_context()

    def _notify(msg):  # noqa: E731
        return False

_OFFSET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "telegram_offset.txt",
)

HELP = (
    "Semi-auto commands:\n"
    "/lot 0.02  ·  /lot GBPUSD 0.03\n"
    "/bias EURUSD long | short | both\n"
    "/levels EURUSD buy 1.0950 1.0975 sell 1.0900\n"
    "/hold EURUSD  (run across sessions)  ·  /release EURUSD\n"
    "/close EURUSD | all   ·   /halt   ·   /resume\n"
    "/auto EURUSD  ·  /clear  ·  /status"
)


def _pairs() -> list[str]:
    return list(getattr(config, "PAIRS", []))


def _match_pair(tok: str):
    """Resolve a user token to a configured pair (case-insensitive), else None."""
    t = tok.upper()
    for p in _pairs():
        if p.upper() == t:
            return p
    return None


def parse_command(text: str, inputs, trader=None) -> str | None:
    """Apply one command line; return an ack string (or None to ignore).

    `inputs` holds per-day state (lot/bias/levels/hold). `trader`, when supplied,
    is the live engine — needed for the ACTION commands (/close /halt /resume)
    that do something now rather than set state. Parsing is pure and works with
    trader=None (offline-testable); the action just isn't executed.
    """
    text = (text or "").strip()
    if not text.startswith("/"):
        return None
    toks = text.split()
    cmd = toks[0][1:].lower().split("@", 1)[0]   # strip leading / and any @botname
    args = toks[1:]

    if cmd in ("help", "start"):
        return HELP
    if cmd == "status":
        return inputs.status_text()

    # ── action commands (need the live engine) ───────────────────────────────
    if cmd == "close":
        if not args:
            return "usage: /close EURUSD   (or /close all)"
        if args[0].lower() == "all":
            if trader is None:
                return "close all — (no live engine attached)"
            n = trader.manual_close_all()
            return f"closing ALL open positions ({n})" if n else "nothing open to close"
        p = _match_pair(args[0])
        if not p:
            return f"unknown pair '{args[0]}' (have: {', '.join(_pairs())})"
        if trader is None:
            return f"close {p} — (no live engine attached)"
        return trader.manual_close(p)

    if cmd in ("halt", "stop", "pause"):
        if trader is not None:
            trader.manual_halt()
        return ("TRADING HALTED — no new entries or pyramid adds. Open trades keep "
                "running on their stops. Send /resume to re-enable, /close all to flatten.")

    if cmd in ("resume", "unhalt"):
        if trader is not None:
            trader.manual_resume()
        return "Resumed — new entries re-enabled."
    if cmd == "clear":
        return inputs.clear()
    if cmd == "auto":
        p = _match_pair(args[0]) if args else None
        return inputs.clear(p) if p else "usage: /auto EURUSD"

    if cmd == "hold":
        if not args:
            return "usage: /hold EURUSD   (also /hold all, /hold EURUSD off)"
        if args[0].lower() == "all":
            return "\n".join(inputs.set_hold(pp, True) for pp in _pairs())
        p = _match_pair(args[0])
        if not p:
            return f"unknown pair '{args[0]}' (have: {', '.join(_pairs())})"
        on = not (len(args) >= 2 and args[1].lower() in ("off", "0", "no", "release"))
        return inputs.set_hold(p, on)

    if cmd == "release":
        if not args:
            return "usage: /release EURUSD   (also /release all)"
        if args[0].lower() == "all":
            return "\n".join(inputs.set_hold(pp, False) for pp in _pairs())
        p = _match_pair(args[0])
        return inputs.set_hold(p, False) if p else f"unknown pair '{args[0]}'"

    if cmd == "lot":
        if not args:
            return "usage: /lot 0.02   or   /lot GBPUSD 0.03"
        p = _match_pair(args[0])
        try:
            if p and len(args) >= 2:
                return inputs.set_lot(p, float(args[1]))
            lot = float(args[-1])
        except ValueError:
            return f"bad lot value in: {text}"
        # No pair given → apply to every configured pair.
        return "\n".join(inputs.set_lot(pp, lot) for pp in _pairs())

    if cmd == "bias":
        if len(args) < 2:
            return "usage: /bias EURUSD long|short|both"
        p = _match_pair(args[0])
        if not p:
            return f"unknown pair '{args[0]}' (have: {', '.join(_pairs())})"
        return inputs.set_bias(p, args[1])

    if cmd == "levels":
        if len(args) < 2:
            return "usage: /levels EURUSD buy 1.0950 1.0975 sell 1.0900"
        p = _match_pair(args[0])
        if not p:
            return f"unknown pair '{args[0]}' (have: {', '.join(_pairs())})"
        buy, sell, bucket = [], [], None
        for a in args[1:]:
            al = a.lower()
            if al in ("buy", "buyside", "buy-side", "bsl"):
                bucket = buy
            elif al in ("sell", "sellside", "sell-side", "ssl"):
                bucket = sell
            else:
                try:
                    (bucket if bucket is not None else buy).append(float(a))
                except ValueError:
                    return f"bad level '{a}' in: {text}"
        return inputs.set_levels(p, buy or None, sell or None)

    return f"unknown command '{cmd}' — try /help"


# ── network layer ────────────────────────────────────────────────────────────

def _read_offset() -> int:
    try:
        with open(_OFFSET_PATH) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def _write_offset(o: int) -> None:
    os.makedirs(os.path.dirname(_OFFSET_PATH), exist_ok=True)
    with open(_OFFSET_PATH, "w") as f:
        f.write(str(o))


def poll(inputs, trader=None) -> int:
    """Fetch new Telegram messages and apply any commands. Returns count applied.

    `trader` (the live engine) enables the action commands /close /halt /resume.
    Never raises — a Telegram hiccup must never interrupt the trading loop.
    """
    token = getattr(config, "TELEGRAM_BOT_TOKEN", "") or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = str(getattr(config, "TELEGRAM_CHAT_ID", "") or os.getenv("TELEGRAM_CHAT_ID", ""))
    if not token or not chat_id:
        return 0

    offset = _read_offset()
    params = {"timeout": 0, "allowed_updates": json.dumps(["message"])}
    if offset:
        params["offset"] = offset
    url = f"https://api.telegram.org/bot{token}/getUpdates?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url, timeout=10, context=_SSL_CTX) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:  # noqa: BLE001
        print(f"[telegram_control] poll failed: {exc}", flush=True)
        return 0

    if not data.get("ok"):
        return 0

    applied = 0
    max_uid = offset
    for upd in data.get("result", []):
        uid = upd.get("update_id", 0)
        max_uid = max(max_uid, uid + 1)   # ack this update so it's not re-served
        msg = upd.get("message") or {}
        if str(msg.get("chat", {}).get("id")) != chat_id:
            continue                       # ignore anyone but the owner
        text = msg.get("text", "")
        ack = parse_command(text, inputs, trader=trader)
        if ack is not None:
            _notify(f"SEMI-AUTO\n{ack}")
            applied += 1

    if max_uid != offset:
        _write_offset(max_uid)
    return applied
