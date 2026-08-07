"""Two-way Telegram control for the live engine.

Polls Telegram getUpdates and dispatches a WHITELIST of commands. Three access
tiers (so the bot can be shared safely):

  * owner   — TELEGRAM_CHAT_ID          — full control
  * admins  — TELEGRAM_ADMIN_IDS (csv)  — full control
  * viewers — TELEGRAM_VIEWER_IDS (csv) — READ-ONLY (/read /positions /account …)

Anyone not listed is ignored. Replies go to whoever sent the command; alerts
(trade open/close, session brief) are broadcast to everyone authorised.

Parsing is pure/offline-testable (parse_command); the network poll wraps it.
"""
from __future__ import annotations

import json
import os
import ssl
import urllib.parse
import urllib.request

import config

try:
    from scripts.notify import _SSL_CTX      # reuse certifi CA bundle if present
except Exception:  # pragma: no cover
    _SSL_CTX = ssl.create_default_context()

_OFFSET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "telegram_offset.txt",
)

# Commands a read-only viewer may use. Everything else is full-control only.
READ_CMDS = {"read", "structure", "markets", "positions", "open", "trades",
             "account", "equity", "dxy", "session", "brief", "news",
             "status", "help", "start", "whoami"}
# Ops-bot commands — if sent here, point the user at the ops bot.
OPS_CMDS = {"setaccount", "setpassword", "setpath", "smoketest", "installtask",
            "startbot", "stopbot", "backtest", "validate", "logs", "pull"}

HELP = (
    "TRADING BOT — commands\n"
    "\n"
    "READ (ask the bot):\n"
    "/brief  full session brief (structure + positions + account)\n"
    "/read [EURUSD]  market-structure template\n"
    "/markets  all pairs at a glance\n"
    "/positions  open trades + live P&L\n"
    "/account  equity / day P&L / drawdown\n"
    "/dxy  dollar index   ·   /session  killzone\n"
    "/news  upcoming high-impact events\n"
    "\n"
    "PLAN (steer the bot):\n"
    "/lot 0.02  ·  /lot GBPUSD 0.03\n"
    "/bias EURUSD long | short | both\n"
    "/levels EURUSD buy 1.0950 1.0975 sell 1.0900\n"
    "/hold EURUSD (run across sessions) · /release EURUSD\n"
    "\n"
    "CONTROL (act now):\n"
    "/test EURUSD long|short [lot]  (e.g. /test EURUSD long 0.05)\n"
    "/pyramid EURUSD [1.1600]  (add to a WINNER; same TP or a set level)\n"
    "/sl EURUSD 1.15550 [leg#]  (move stop)  ·  /be EURUSD (breakeven)\n"
    "/close EURUSD [leg#] | all  ·  /flat  ·  /halt  ·  /resume\n"
    "/lot 0.01..0.05  (size all trades)  ·  /auto  ·  /clear  ·  /whoami\n"
    "\n"
    "(Setup/backtest/logs live on the Ops Bot.)"
)

HELP_VIEW = (
    "TRADING BOT — read-only access\n"
    "/brief  ·  /read [EURUSD]  ·  /markets\n"
    "/positions  ·  /account  ·  /dxy  ·  /session  ·  /news\n"
    "/status  ·  /whoami"
)


# ── access control ────────────────────────────────────────────────────────────

def _ids(s) -> set:
    return {x.strip() for x in str(s or "").replace(";", ",").split(",") if x.strip()}


def _access():
    owner = str(getattr(config, "TELEGRAM_CHAT_ID", "") or os.getenv("TELEGRAM_CHAT_ID", ""))
    admins = _ids(getattr(config, "TELEGRAM_ADMIN_IDS", "") or os.getenv("TELEGRAM_ADMIN_IDS", ""))
    viewers = _ids(getattr(config, "TELEGRAM_VIEWER_IDS", "") or os.getenv("TELEGRAM_VIEWER_IDS", ""))
    return owner, admins, viewers


def _open_view() -> bool:
    v = getattr(config, "TELEGRAM_OPEN_VIEW", 0) or os.getenv("TELEGRAM_OPEN_VIEW", "0")
    return str(v).strip().lower() not in ("", "0", "false", "no")


def _role(cid):
    """'full' | 'view' | None for a chat id."""
    cid = str(cid)
    owner, admins, viewers = _access()
    if cid and (cid == owner or cid in admins):
        return "full"
    if cid in viewers:
        return "view"
    if _open_view():          # open read-only: anyone who messages can read
        return "view"
    return None


# ── telegram send ─────────────────────────────────────────────────────────────

def _send(chat_id, text: str) -> bool:
    token = getattr(config, "TELEGRAM_BOT_TOKEN", "") or os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token or not chat_id:
        return False
    if len(text) > 4000:
        text = text[:3980] + "\n...(truncated)"
    data = json.dumps({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12, context=_SSL_CTX) as r:
            return r.status == 200
    except Exception as exc:  # noqa: BLE001
        print(f"[telegram_control] send failed: {exc}", flush=True)
        return False


def broadcast(text: str) -> bool:
    """Send `text` to everyone authorised (owner + admins + viewers). Used for
    alerts and the session brief so shared users see them too."""
    owner, admins, viewers = _access()
    ok = False
    for cid in ({owner} | admins | viewers):
        if cid:
            ok = _send(cid, text) or ok
    return ok


def _pairs() -> list[str]:
    return list(getattr(config, "PAIRS", []))


def _match_pair(tok: str):
    t = tok.upper()
    for p in _pairs():
        if p.upper() == t:
            return p
    return None


# ── command dispatch ──────────────────────────────────────────────────────────

def parse_command(text: str, inputs, trader=None, role="full", sender=None) -> str | None:
    """Apply one command; return an ack (or None to ignore).

    role: 'full' (owner/admin) or 'view' (read-only). sender: the chat id (for
    /whoami). Pure — works with trader=None for offline tests.
    """
    text = (text or "").strip()
    if not text.startswith("/"):
        return None
    toks = text.split()
    cmd = toks[0][1:].lower().split("@", 1)[0]
    args = toks[1:]

    if cmd == "whoami":
        r = {"full": "full control", "view": "read-only"}.get(role, str(role))
        return f"chat id: {sender}\naccess: {r}"
    if cmd in ("help", "start"):
        return HELP if role == "full" else HELP_VIEW
    if cmd == "status":
        return inputs.status_text()

    # Sent to the wrong bot? Point them at the ops bot.
    if cmd in OPS_CMDS:
        return "that's an Ops Bot command — send it to the Ops Bot, not here."

    # Read/query — available to viewers too.
    if cmd in ("read", "structure", "markets", "positions", "open", "trades",
               "account", "equity", "dxy", "session", "brief", "news"):
        if trader is None:
            return "read commands need the live bot running."
        try:
            if cmd in ("read", "structure", "markets"):
                return trader.read_structure(_match_pair(args[0]) if args else None)
            if cmd in ("positions", "open", "trades"):
                return trader.read_positions()
            if cmd in ("account", "equity"):
                return trader.read_account()
            if cmd == "dxy":
                d = trader.read_dxy_value()
                return f"DXY ~ {d:.3f}" if d else "DXY unavailable"
            if cmd == "session":
                return trader.read_session()
            if cmd == "brief":
                return trader.read_brief()
            if cmd == "news":
                return trader.read_news()
        except Exception as exc:  # noqa: BLE001
            return f"read failed: {exc}"

    # Everything below changes state or trades — full control only.
    if role != "full":
        return ("read-only access — you can use /brief /read /markets /positions "
                "/account /dxy /session /news")

    if cmd in ("test", "testtrade", "buy", "sell"):
        if trader is None:
            return "test needs the live bot running."
        lot = None
        if cmd == "buy":
            pair, d = (_match_pair(args[0]) if args else None), 1
            lot = args[1] if len(args) >= 2 else None
        elif cmd == "sell":
            pair, d = (_match_pair(args[0]) if args else None), -1
            lot = args[1] if len(args) >= 2 else None
        else:
            if len(args) < 2:
                return "usage: /test EURUSD long|short [lot]   (e.g. /test EURUSD long 0.05)"
            pair = _match_pair(args[0])
            d = 1 if args[1].lower().startswith("l") else -1
            lot = args[2] if len(args) >= 3 else None
        if not pair:
            return "usage: /test EURUSD long|short [lot]   (or /buy EURUSD 0.05, /sell EURUSD)"
        return trader.manual_test_trade(pair, d, lot)

    if cmd in ("sl", "stop"):
        if len(args) < 2:
            return "usage: /sl EURUSD 1.15550   (or /sl EURUSD 2 1.15550 for one leg)"
        p = _match_pair(args[0])
        if not p:
            return f"unknown pair '{args[0]}' (have: {', '.join(_pairs())})"
        if len(args) >= 3:            # /sl PAIR LEG LEVEL
            return trader.manual_move_stop(p, args[2], args[1])
        return trader.manual_move_stop(p, args[1])   # /sl PAIR LEVEL (all legs)

    if cmd in ("be", "breakeven"):
        if not args:
            return "usage: /be EURUSD   (or /be EURUSD 2 for one leg)"
        p = _match_pair(args[0])
        if not p:
            return f"unknown pair '{args[0]}' (have: {', '.join(_pairs())})"
        return trader.manual_breakeven(p, args[1] if len(args) >= 2 else None)

    if cmd in ("pyramid", "add"):
        if trader is None:
            return "pyramid needs the live bot running."
        if not args:
            return "usage: /pyramid EURUSD   (or /pyramid EURUSD 1.1600 for a set exit)"
        p = _match_pair(args[0])
        if not p:
            return f"unknown pair '{args[0]}' (have: {', '.join(_pairs())})"
        level = args[1] if len(args) >= 2 else None
        return trader.manual_pyramid(p, level)

    if cmd == "flat":
        if trader is None:
            return "flat — (no live engine attached)"
        n = trader.manual_close_all()
        return f"closing ALL open positions ({n})" if n else "nothing open to close"

    if cmd == "close":
        if not args:
            return "usage: /close EURUSD   ·   /close EURUSD 2 (one leg)   ·   /close all"
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
        leg = args[1] if len(args) >= 2 else None      # optional leg number
        return trader.manual_close(p, leg)

    if cmd in ("halt", "stop", "pause"):
        if trader is not None:
            trader.manual_halt()
        return ("TRADING HALTED — no new entries or pyramid adds. Open trades keep "
                "running on their stops. /resume to re-enable, /flat to close all.")

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


# ── network layer ─────────────────────────────────────────────────────────────

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
    """Fetch new messages, dispatch, reply to the sender. Never raises."""
    token = getattr(config, "TELEGRAM_BOT_TOKEN", "") or os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
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
        max_uid = max(max_uid, upd.get("update_id", 0) + 1)
        msg = upd.get("message") or {}
        cid = msg.get("chat", {}).get("id")
        role = _role(cid)
        if role is None:
            continue                       # not owner/admin/viewer — ignore
        try:
            ack = parse_command(msg.get("text", ""), inputs, trader=trader,
                                role=role, sender=cid)
        except Exception as exc:  # noqa: BLE001
            ack = f"command error: {exc}"   # never let one bad command re-queue forever
        if ack is not None:
            _send(cid, ack)                # reply to whoever asked
            applied += 1

    if max_uid != offset:
        _write_offset(max_uid)
    return applied
