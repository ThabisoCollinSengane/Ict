# Going live on Exness MT5 — VPS setup guide

This is the path for running the ICT algo **headless** on your Windows VPS/RDP,
talking to the **MetaTrader 5** terminal via the `MetaTrader5` Python package
(the chosen broker link — lighter and simpler than QuantConnect LEAN for an 8GB
Exness box).

> ⚠️ **Status: NOT yet ready for real money.** The broker layer + connectivity
> test are built and testable now. The strategy wiring (`live/run_live.py`) and
> the live sizing levers are the next phase. **Run everything on an Exness DEMO
> account until that phase is done and paper-traded.** See "Build phases" below.

---

## What runs where

- **Your VPS (8GB Windows):** MT5 terminal (logged into Exness) + this Python bot.
  No assistant app on the VPS — it runs headless. RAM budget: Windows ~2.5GB +
  MT5 ~0.4GB + bot ~0.4GB ≈ 3.5GB used, comfortable on 8GB.
- **This repo:** all the code. You `git clone` it onto the VPS and run it.

---

## One-time install (manual, ~15 min)

1. **Python 3.11+** — https://www.python.org/downloads/windows/
   During install **tick "Add python.exe to PATH"**.
2. **MetaTrader 5 terminal** — install from Exness's download link (or metaquotes).
   Launch it and **log into your Exness DEMO account** (Exness shows the server
   name, e.g. `Exness-MT5Trial14`, in the account panel).
3. **Git** (to pull the repo) — https://git-scm.com/download/win
   Then: `git clone <your repo url>` and `cd Ict`.

## Project setup (scripted)

From the repo root in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_vps.ps1
```

This creates `.venv` and installs `requirements_live.txt` (MetaTrader5, pandas, numpy).

## Connectivity smoke test (DEMO — places NO trades)

```powershell
$env:MT5_LOGIN="12345678"
$env:MT5_PASSWORD="yourpassword"
$env:MT5_SERVER="Exness-MT5Trial14"
.\.venv\Scripts\python.exe -m live.smoke_test
```

A healthy run prints: your account, every symbol resolved (incl. any Exness
suffix like `EURUSDm`), bars on every timeframe, a live tick, and a synthetic
DXY value in the ~90–115 range. If a symbol shows `*** MISSING ***`, that
instrument isn't offered on your account type — tell me and I'll adjust.

> Tip: if you've already logged into MT5 in the GUI, you can run the smoke test
> with no env vars — it attaches to the signed-in account.

---

## Build phases (where we are)

| Phase | What | Status |
|---|---|---|
| 1 | Broker layer (`live/mt5_connector.py`) — connect, bars, orders | ✅ built |
| 1 | Connectivity smoke test (`live/smoke_test.py`) | ✅ built |
| 1 | VPS setup script + this guide | ✅ built |
| 2 | Live strategy loop (`live/run_live.py`) — drive backtest logic on live bars | ✅ built |
| 2 | Telegram notifications (trade open/close/circuit breaker/daily equity) | ✅ built |
| 2 | P23 milestone trailing stop in live engine | ✅ built |
| 3 | Demo paper-trade ≥2 weeks; reconcile fills vs backtest expectations | 🔄 active |
| 4 | Switch to real account + funding | ⬜ |

**Do not skip Phase 3.** The backtest assumes fills at bar prices with modelled
spread/slippage; live fills will differ. Paper trading on demo is how we confirm
the live engine matches the validated R400.7M behavior before risking the R500.

---

## Telegram notifications setup (one-time, ~5 min)

Notifications fire on: trade opened, trade closed (with P&L), circuit breaker,
daily equity snapshot at midnight UTC.

1. Open Telegram → search `@BotFather` → send `/newbot` → follow prompts → copy the token
   (looks like `7123456789:AABBccDD...`)
2. Search `@userinfobot` → send `/start` → copy your numeric chat ID (e.g. `987654321`)
3. Set as env vars on the VPS **before** running the bot:

```powershell
$env:TELEGRAM_BOT_TOKEN="7123456789:AABBccDD..."
$env:TELEGRAM_CHAT_ID="987654321"
```

Or add them to a `.env` file in the repo root (already in `.gitignore`):

```
TELEGRAM_BOT_TOKEN=7123456789:AABBccDD...
TELEGRAM_CHAT_ID=987654321
```

Test it without starting the bot:
```powershell
.\.venv\Scripts\python.exe -m scripts.notify
```

A message saying "ICT Bot — test OK" should arrive on your phone within seconds.

### What actually arrives on your phone

Once `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set, these fire automatically:

| Alert | When |
|---|---|
| **MM semi-auto read** | a SELL GBPUSD / BUY EURUSD setup reaches 2+ confirmations |
| MM zone reached / broken | price hits or breaks an IFVG zone you armed with `/mm` |
| Fast read | a pair sweeps its recent M15 high/low (advisory) |
| Session brief | at each killzone open, with that session's plan |
| Trade opened / closed | with P&L |
| Circuit breaker | daily cap, consecutive losses, session kill, drawdown halt |
| Restart notice | positions re-adopted after a restart |

### The MM read — ENABLED 2026-09-14

`MM_SEMI_AUTO_ENABLED=1`. Permanently watching **SELL GBPUSD** and **BUY EURUSD**
— your golden rule, no `/mm` arming needed.

It scores four confirmations and alerts at 2 or more:

| | |
|---|---|
| **IFVG** | price retraced into an inverted fair value gap (H4→H1→M30→M15→M5 cascade) |
| **MSS** | market structure shift on M5/M15 — the opposing swing was swept |
| **SMT** | EURUSD↔GBPUSD divergence on H1/H4 — one sweeps, the other fails to confirm |
| **FBC** | full body close through the IFVG — the inversion confirmation |

3+ = **STRONG** · 2 = **MODERATE** · 1 = **WATCH** (not alerted)

Throttles: **max 3 alerts per pair per day**, **30-minute cooldown** between
alerts on the same pair, and only inside a killzone.

What lands on your phone:

```
MM STRONG — SELL GBPUSD
✅IFVG  ✅MSS  ✅SMT  ⬜FBC

Entry:  1.33240
Stop:   1.33340  (10.0 pips)
Target: 1.32910  (33.0 pips, 3.3R)
  <- pdh_pdl

H1 IFVG 1.33210-1.33280 (inverted 2 bars ago)
M15 MSS: prior swing high 1.33301 swept + reclaimed
SMT: EU failed to confirm GU's high on H1

/go gbpusd to EXECUTE  |  ignore to PASS
```

**⚠️ It never trades by itself.** Verified by AST that `_mm_semi_auto_scan`
contains no order-placing call of any kind — it reads bars and sends a message,
nothing else. A trade happens only when you reply `/go PAIR`. The three
autonomous MM channels (`MM_GOLDEN`, `MM_STANDALONE`, `MM_CONTINUATION`) remain
**off**, so the engine never opens an MM trade on its own.

**Ignoring an alert is a valid answer** — and given the measured 21% win rate on
MM setups when a machine picks them, ignoring most of them is the expected
behaviour. The alert exists so you get to apply the judgement the classifier
could not.

### If no messages arrive

`broadcast()` returns False and logs, but does **not** raise — a missing or wrong
token silently disables alerts without touching the trading loop. So silence means
check the credentials, not that the bot has stopped trading:

```powershell
.\.venv\Scripts\python.exe -m scripts.notify     # should land within seconds
```

---

## Keeping the bot alive on the VPS

- Run inside the RDP session; if you disconnect RDP, use **"disconnect"** (not log
  off) so the session — and the bot + MT5 — keep running.
- For auto-restart on crash/reboot we can add a Task Scheduler entry in Phase 2.

## Security

- Never commit credentials. Use the `MT5_*` environment variables (or a local
  `.env` that's git-ignored). The repo contains no passwords.
