r"""Ops bot - drive the VM from Telegram via a SECOND bot (whitelist, owner-only).

Runs the operational commands so you can set up and control everything from your
phone, without typing in PowerShell:

  /status                     what's configured + whether the live bot is running
  /setaccount <login> <srv>   save MT5 login + server to live.env
  /setpassword <pwd>          save MT5 password to live.env  (see warning)
  /setpath <terminal64.exe>   save MT5_TERMINAL_PATH
  /smoketest                  run the MT5 connectivity test (places NO trades)
  /installtask                register the live bot to auto-start (Windows)
  /startbot   /stopbot        start / stop the live trading bot
  /backtest [years...]        run the backtest, send the summary back
  /validate <name>            run a validation runner (structure_entry, pdliq, ...)
  /logs [n]                   tail data/live.log
  /pull                       git pull --ff-only
  /help

SECURITY: this executes a FIXED WHITELIST of actions, never arbitrary shell. It
obeys ONLY your chat id, and uses its OWN token (OPS_BOT_TOKEN) so it does not
clash with the live alert bot's poller. Add to live.env:
    OPS_BOT_TOKEN=<token from BotFather for the 2nd bot>
    (chat id is reused from TELEGRAM_CHAT_ID; set OPS_CHAT_ID to override)

Run it (on the VM, in the repo, inside the venv):
    .\.venv\Scripts\python.exe -m scripts.ops_bot
    (or: powershell -ExecutionPolicy Bypass -File scripts\ops_bot.ps1)
"""
from __future__ import annotations

import json
import os
import re
import ssl
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

try:
    import certifi as _certifi
    _SSL = ssl.create_default_context(cafile=_certifi.where())
except Exception:
    _SSL = ssl.create_default_context()

OFFSET_PATH = os.path.join(REPO, "data", "ops_offset.txt")
LIVE_ENV = os.path.join(REPO, "live.env")
PY = sys.executable
IS_WIN = os.name == "nt"

VALIDATORS = {   # /validate NAME -> runner script (bash)
    "structure_entry": "run_structure_entry_validation.sh",
    "pdliq": "run_pdliq_validation.sh",
    "mintarget": "run_mintarget_validation.sh",
    "scaledtarget": "run_scaledtarget_validation.sh",
}

HELP = (
    "OPS commands (owner + admins):\n"
    "/status  ·  /whoami\n"
    "/setaccount <login> <server>\n"
    "/setpassword <pwd>   /setpath <terminal64.exe>\n"
    "/smoketest\n"
    "/installtask  /startbot  /stopbot\n"
    "/backtest [years]   /validate <name>\n"
    "/logs [n]   /pull"
)


# ── env + telegram plumbing ───────────────────────────────────────────────────

def _load_env_file():
    """Load live.env into the process env. OVERRIDES existing vars so live.env is
    always the source of truth (a stale value inherited from the launching shell
    must not win)."""
    if not os.path.exists(LIVE_ENV):
        return
    for line in open(LIVE_ENV, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


def _token_chat():
    tok = os.getenv("OPS_BOT_TOKEN", "")
    chat = os.getenv("OPS_CHAT_ID", "") or os.getenv("TELEGRAM_CHAT_ID", "")
    return tok, str(chat)


def _ids(s):
    return {x.strip() for x in str(s or "").replace(";", ",").split(",") if x.strip()}


def _allowed_ids():
    """Ops bot is owner + admins only (viewers can't run VM ops)."""
    _, owner = _token_chat()
    return ({owner} if owner else set()) | _ids(os.getenv("TELEGRAM_ADMIN_IDS", ""))


# Trading-bot commands — if sent here, point the user at the GameTheory bot.
TRADING_CMDS = {"read", "structure", "markets", "positions", "open", "trades",
                "account", "equity", "dxy", "session", "brief", "news",
                "lot", "bias", "levels", "hold", "release", "close", "flat",
                "halt", "resume", "auto", "clear", "test", "testtrade", "buy", "sell",
                "pyramid", "add", "sl", "stop", "be", "breakeven", "mm"}


def send(text: str, chat_id: str = None) -> bool:
    tok, owner = _token_chat()
    chat = str(chat_id) if chat_id else owner
    if not tok or not chat:
        return False
    if len(text) > 4000:
        text = text[:3980] + "\n...(truncated)"
    data = json.dumps({"chat_id": chat, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{tok}/sendMessage",
        data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=_SSL) as r:
            return r.status == 200
    except Exception as exc:  # noqa: BLE001
        print(f"[ops_bot] send failed: {exc}", flush=True)
        return False


def _read_offset() -> int:
    try:
        return int(open(OFFSET_PATH).read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def _write_offset(o: int) -> None:
    os.makedirs(os.path.dirname(OFFSET_PATH), exist_ok=True)
    open(OFFSET_PATH, "w").write(str(o))


# ── shell helpers (fixed arg lists only — never a user-built string) ──────────

def run(cmd: list, timeout: int = 120):
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
        return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()
    except subprocess.TimeoutExpired:
        return 124, f"(timed out after {timeout}s)"
    except FileNotFoundError as exc:
        return 127, f"(not found: {exc})"
    except Exception as exc:  # noqa: BLE001
        return 1, f"(error: {exc})"


def _ps(command: str, timeout: int = 60):
    return run(["powershell", "-NoProfile", "-Command", command], timeout=timeout)


def tail(text: str, n: int = 40) -> str:
    return "\n".join(text.splitlines()[-n:])


def run_async(header: str, cmd: list, timeout: int, extract=None) -> None:
    """Run a long command off the poll thread; message start + result."""
    def work():
        send(f"{header} - started...")
        rc, out = run(cmd, timeout=timeout)
        body = extract(out) if extract else tail(out, 40)
        send(f"{header} - done (rc {rc})\n\n{body or '(no output)'}")
    threading.Thread(target=work, daemon=True).start()


def _bt_summary(out: str) -> str:
    keys = ["trades", "win_rate_pct", "profit_factor", "max_drawdown_pct", "ending_equity_ZAR"]
    lines = []
    for k in keys:
        m = re.search(rf"{k}\s+(-?[\d.,]+)", out)
        if m:
            lines.append(f"{k}: {m.group(1)}")
    return "\n".join(lines) if lines else tail(out, 25)


def set_env_var(key: str, value: str) -> None:
    lines, found = [], False
    if os.path.exists(LIVE_ENV):
        for line in open(LIVE_ENV, encoding="utf-8"):
            if re.match(rf"\s*{re.escape(key)}\s*=", line):
                lines.append(f"{key}={value}\n"); found = True
            else:
                lines.append(line if line.endswith("\n") else line + "\n")
    if not found:
        lines.append(f"{key}={value}\n")
    open(LIVE_ENV, "w", encoding="utf-8").write("".join(lines))
    os.environ[key] = str(value)


def status_text() -> str:
    _load_env_file()   # re-read live.env so /status always reflects the file, not startup
    def present(k):
        return "set" if os.getenv(k) else "-"
    _, sha = run(["git", "rev-parse", "--short", "HEAD"], 10)
    _, br = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 10)
    task = "-"
    if IS_WIN:
        _, out = _ps("(Get-ScheduledTask -TaskName ICTLiveBot -ErrorAction SilentlyContinue).State")
        task = out.strip() or "not installed"
    return ("OPS STATUS\n"
            f"repo: {br.strip()} @ {sha.strip()}\n"
            f"MT5_LOGIN: {os.getenv('MT5_LOGIN', '-')} | SERVER: {os.getenv('MT5_SERVER', '-')}\n"
            f"MT5_PASSWORD: {present('MT5_PASSWORD')} | PATH: {present('MT5_TERMINAL_PATH')}\n"
            f"live bot task: {task}")


# ── command dispatch (the whitelist) ──────────────────────────────────────────

def handle(text: str, sender=None) -> str | None:
    text = (text or "").strip()
    if not text.startswith("/"):
        return None
    toks = text.split()
    cmd = toks[0][1:].lower().split("@", 1)[0]
    args = toks[1:]

    if cmd == "whoami":
        return f"chat id: {sender}\naccess: ops (full)"
    if cmd in ("help", "start"):
        return HELP
    if cmd == "status":
        return status_text()

    # Sent to the wrong bot? Point them at the trading bot.
    if cmd in TRADING_CMDS:
        return "that's a trading command — send it to the GameTheory bot, not here."

    if cmd == "setaccount":
        if len(args) < 2 or not args[0].isdigit():
            return "usage: /setaccount <login> <server>   e.g. /setaccount 591937412 FxPro-MT5 Demo"
        server = " ".join(args[1:])   # server names can contain spaces (e.g. 'FxPro-MT5 Demo')
        set_env_var("MT5_LOGIN", args[0])
        set_env_var("MT5_SERVER", server)
        return f"saved MT5_LOGIN={args[0]}, MT5_SERVER={server} to live.env"

    if cmd == "setpassword":
        if not args:
            return "usage: /setpassword <password>"
        set_env_var("MT5_PASSWORD", " ".join(args))
        return ("MT5_PASSWORD saved to live.env.\n"
                "WARNING: delete your message above - it contains the password. For the "
                "FUNDED account, prefer typing it in notepad on the VM, not over Telegram.")

    if cmd == "setpath":
        if not args:
            return r"usage: /setpath C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe"
        set_env_var("MT5_TERMINAL_PATH", " ".join(args))
        return "saved MT5_TERMINAL_PATH to live.env"

    if cmd == "smoketest":
        run_async("Smoke test", [PY, "-m", "live.smoke_test"], 150)
        return None

    if cmd == "installtask":
        if not IS_WIN:
            return "installtask is Windows-only (run on the VM)."
        run_async("Install startup task",
                  ["powershell", "-ExecutionPolicy", "Bypass", "-File",
                   os.path.join("scripts", "install_startup_task.ps1")], 90)
        return None

    if cmd == "startbot":
        if not IS_WIN:
            return "startbot is Windows-only (run on the VM)."
        rc, out = _ps("Start-ScheduledTask -TaskName ICTLiveBot")
        return ("Live bot started (task ICTLiveBot)." if rc == 0 else
                "Couldn't start it - is the task installed? Try /installtask.\n" + tail(out, 8))

    if cmd == "stopbot":
        if not IS_WIN:
            return "stopbot is Windows-only (run on the VM)."
        rc, out = _ps("Stop-ScheduledTask -TaskName ICTLiveBot")
        return "Live bot stopped." if rc == 0 else "stop failed:\n" + tail(out, 8)

    if cmd == "backtest":
        yrs = [a for a in args if re.fullmatch(r"\d{4}", a)] or ["2022", "2023", "2024", "2025"]
        run_async(f"Backtest {' '.join(yrs)}",
                  [PY, "run_backtest_histdata.py", "--years", *yrs], 1800, extract=_bt_summary)
        return None

    if cmd == "validate":
        name = args[0] if args else ""
        if name not in VALIDATORS:
            return "usage: /validate <" + " | ".join(VALIDATORS) + ">"
        run_async(f"Validate {name}", ["bash", VALIDATORS[name]], 3600,
                  extract=lambda o: tail(o, 30))
        return None

    if cmd == "logs":
        n = int(args[0]) if (args and args[0].isdigit()) else 40
        p = os.path.join(REPO, "data", "live.log")
        if not os.path.exists(p):
            return "no data/live.log yet (the live bot hasn't run)."
        return "live.log (tail):\n" + tail(open(p, encoding="utf-8", errors="replace").read(), n)

    if cmd == "pull":
        run_async("git pull", ["git", "pull", "--ff-only"], 60)
        return None

    return f"unknown command '{cmd}' - send /help"


# ── main loop ─────────────────────────────────────────────────────────────────

def poll_loop() -> int:
    tok, chat = _token_chat()
    if not tok or not chat:
        print("Missing OPS_BOT_TOKEN and/or chat id. Add OPS_BOT_TOKEN to live.env "
              "(chat id is reused from TELEGRAM_CHAT_ID).")
        return 1
    off = _read_offset()
    print(f"Ops bot: token {tok[:10]}... chat {chat}. Listening (Ctrl-C to stop).")
    send("OPS BOT ONLINE\nOwner + admins, whitelist-only. Send /help for commands.")
    while True:
        params = {"timeout": 25}
        if off:
            params["offset"] = off
        url = f"https://api.telegram.org/bot{tok}/getUpdates?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=40, context=_SSL) as r:
                data = json.loads(r.read().decode())
        except KeyboardInterrupt:
            print("\nStopped."); return 0
        except Exception as exc:  # noqa: BLE001
            print(f"[ops_bot] poll error: {exc}", flush=True)
            time.sleep(3); continue
        if not data.get("ok"):
            time.sleep(2); continue
        for upd in data.get("result", []):
            off = max(off, upd.get("update_id", 0) + 1)
            msg = upd.get("message") or {}
            cid = str(msg.get("chat", {}).get("id"))
            if cid not in _allowed_ids():
                continue                 # owner + admins only
            try:
                ack = handle(msg.get("text", ""), sender=cid)
            except Exception as exc:  # noqa: BLE001
                ack = f"error handling command: {exc}"
            if ack is not None:
                send(ack, chat_id=cid)   # reply to whoever asked
        _write_offset(off)


def _selftest() -> int:
    """Offline parse checks (no network, no side effects on real live.env)."""
    assert handle("/help").startswith("OPS commands")
    assert handle("/setaccount 12").startswith("usage:")          # bad args -> usage, no write
    assert handle("/validate bogus").startswith("usage:")
    assert handle("/nope") .startswith("unknown command")
    assert handle("hello") is None
    assert set(VALIDATORS) >= {"structure_entry", "pdliq"}
    print("ops_bot selftest OK")
    return 0


def main() -> int:
    _load_env_file()
    if "--selftest" in sys.argv:
        return _selftest()
    return poll_loop()


if __name__ == "__main__":
    sys.exit(main())
