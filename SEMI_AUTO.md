# Talking to the algorithm — the Telegram manual

Everything you can tell the live bot from your phone, and exactly how to say it.
You steer it; it still runs its full validated ICT logic underneath. Your inputs
**filter, aim, and hold** it — they never replace the strategy.

Everything is **opt-in, per pair, per day.** Say nothing → that pair trades fully
automatic, exactly as backtested. All inputs auto-expire at **00:00 UTC**, so
nothing you set today leaks into tomorrow.

---

## Session templates — you get one at the start of every session

At the top of **each** session the bot messages you a template. You reply with
that session's plan (or ignore it and it runs on full auto):

- **LONDON SESSION START** — ~02:00 ET
- **NEW YORK AM SESSION START** — ~07:00 ET (also lists what's already open, so
  you can decide to `/hold` it into NY)
- **NEW YORK PM SESSION START** — ~13:00 ET (only if PM trading is enabled)

You don't have to wait for the template — any command works any time.

---

## The commands

### 0 · Ask the bot (read anytime — no effect on trading)
```
/brief           FULL session brief: account + structure + open trades + commands
/read            market-structure template for all pairs
/read EURUSD     just that pair
/markets         all pairs at a glance
/positions       open trades: live P&L + % to target, the Model (Judas reversal /
                 Breakout), the TP idea (H1 FVG / ITH draw / fib ext) and the SL
                 basis (structural ITL/ITH). Reasoning is saved and survives restarts.
/account         equity, day P&L, drawdown, halt state (also /equity)
/dxy             synthetic dollar index right now
/session         which killzone, and whether new entries are allowed
/news            next high-impact news events (UTC)
/whoami          your chat id + access level
```
`/brief` is the same rich summary the bot sends you at the start of every
session — call it any time to get the current picture in one message.
The `/read` template shows, per pair: current price, H4/H1/M15 structure
(bullish / bearish / flat), the intact **ITH** (buy-side draw) and **ITL**
(sell-side draw), and your current plan for that pair. Example:
```
MARKET READ - 08:20 UTC
Session: NY AM
DXY: 99.97

EURUSD  1.15206
  H4 bullish | H1 bearish | M15 bullish
  buy-side draw (ITH): 1.15800
  sell-side draw (ITL): 1.14900
  your plan: EURUSD long only, levels set
```

### 1 · Lot for the day
```
/lot 0.02              → all pairs
/lot GBPUSD 0.03       → one pair
```
Becomes the **base** lot. The draw 2×/3× and the 1.25× confluence/CRT/PDL bumps
still stack on top (they only fire at R3k+ equity anyway).

### 2 · Direction to hunt
```
/bias EURUSD long      → longs only on EURUSD today
/bias EURUSD short     → shorts only
/bias EURUSD both      → clear the filter (back to auto)
```
A **filter**: the bot still needs its own ICT setup to fire — it just won't take
the other side.

### 3 · Your liquidity levels (full manual AMD)
```
/levels EURUSD buy 1.0950 1.0975 sell 1.0900 1.0880
```
- **buy** = buy-side liquidity **above** price · **sell** = sell-side **below**.
- The bot waits for **manipulation** — price sweeps one side and reclaims — then
  trades the **distribution** toward the other side:
  - sell-side swept & reclaimed → hunt **LONG**, target the **buy-side**
  - buy-side swept & dropped back → hunt **SHORT**, target the **sell-side**
  - neither side swept yet → **waits** (no trade)
- So your levels set **which way** (direction gate) and **where to** (the opposite
  side becomes the TP). Your engine still decides **whether the setup is there.**
- If both `/bias` and `/levels` are set, **both must agree.**

### 4 · Let a trade run across sessions
```
/hold EURUSD           → don't close it at the session handover; let it run
/hold all              → every pair
/release EURUSD        → back to normal handover management
```
Normally, at the London→NY (and NY→PM) boundary the bot closes a trade **only if
it's losing AND fighting the weekly bias**. `/hold` exempts that pair from that
close, so a London trade **runs into New York** — and a NY-AM trade **runs into
the afternoon** — managed purely by its **stop, target, and milestone trail**.
(Winning trades already carry across by default; `/hold` also keeps the
losing-but-you-believe-in-it ones alive.)

### 5 · Manual control — close & halt (act now)
```
/test EURUSD long      → open a TEST trade NOW on the demo (also short; /buy /sell)
                          uses the bot's own structural stop + a 2R target,
                          then trails and /close works like any trade
/pyramid EURUSD        → add a leg to a WINNING position, exiting at the SAME TP
/pyramid EURUSD 1.1600 → same, but the whole position exits at 1.1600 instead
                          (only adds if the position is in profit; structural stop)
/close EURUSD          → close EURUSD's open position(s) at market, now
/close all             → flatten everything
/flat                  → flatten everything (shortcut for /close all)
/halt                  → stop all new entries AND pyramid adds; open trades
                          keep running on their stops
/resume                → re-enable new entries
```
To go fully flat and stay out: `/close all` then `/halt`. To stop taking new
trades but let winners keep running: just `/halt`.

### 6 · Review & reset
```
/status                → echo this session's plan for every pair
/auto EURUSD           → revert one pair to full auto
/clear                 → revert ALL pairs to full auto
/help                  → the command list
```

Every command gets an acknowledgement back, so you always see exactly what the
bot registered.

---

## A full day, worked

**London template arrives.** You reply:
```
/lot 0.02
/bias EURUSD long
/levels EURUSD buy 1.0975 sell 1.0900 1.0880
/hold EURUSD
```
→ Bot acks each line. It trades EURUSD **long-only**, but only **after** price
sweeps 1.0900/1.0880 and reclaims, aiming at **1.0975**, and only if its own
MSS+FVG setup fires. GBPUSD / NZDUSD (untouched) trade fully automatic.

**NY-AM template arrives** — "Open now: EURUSD · holding: EURUSD." Your London
long is running into New York (because you `/hold`-ed it) instead of being closed
at the handover. You could add `/bias GBPUSD short` for the NY session, or
`/release EURUSD` if you've changed your mind.

**NY-PM template** (if enabled) — same idea for the afternoon.

---

## Sharing the bot with your partner

**You do NOT create a second bot.** Your partner opens the **same GameTheory bot**
(share the link — `t.me/GameTheory2026bot`) and texts it like any normal chat.
The only question is what they're allowed to do. Three ways, easiest first:

**Option 1 — Open read-only (zero setup, "just text it"):**
Set one flag and anyone you share the link with can read the bot — no ids, no
restarts per person:
```
TELEGRAM_OPEN_VIEW=1
```
They can `/brief`, `/read`, `/positions`, `/account`, `/dxy`, `/session`, `/news`.
They **cannot** touch trades. This is the "share it like WhatsApp" mode you wanted.
(Push alerts still go only to listed people; open-view users read on demand.)

**Option 2 — Named viewer (read-only, also gets alerts):** add their chat id:
```
TELEGRAM_VIEWER_IDS=5111111111,5222222222
```

**Option 3 — Admin (full control, trades like you):** add their chat id:
```
TELEGRAM_ADMIN_IDS=5333333333
```
Trading control **can't** be open (it moves real money) — an admin must be a
listed id.

**Getting a chat id:** the person sends `/start` to @userinfobot (it replies with
their `Id`), or — once they can already read the bot — `/whoami`. Add the id in
`live.env`, restart the bot, done. Anyone not covered by the above is ignored.
The **Ops Bot** honours owner + admins only — never viewers/open-view — since it
changes settings and runs the VM.

## Safety

- **Only listed Telegram chats can use the bot** — anyone else is ignored; viewers
  are limited to read-only.
- **The backtest is byte-identical.** The two engine hooks (`_direction_allowed`,
  `_handover_exempt`) are pure no-ops in the backtester; only the live engine
  overrides them. Your 810-trade / PF 4.47 / MaxDD −12.95% numbers are untouched.
- **Offline self-test** (no MT5, no network): `python -m live.test_semi_auto`.
- **DEMO first**, same as the go-live checklist in `AZURE_WINDOWS_SETUP.md`.
  Prove the whole flow — including a `/hold` across a real handover — on a demo
  account before it touches the funded one.

---

## Quick reference card

| Command | Meaning |
|---|---|
| `/brief` | full session brief (structure + positions + account) |
| `/read [EURUSD]` · `/markets` | market-structure read (template) |
| `/positions` · `/account` · `/dxy` · `/session` · `/news` | live read-outs |
| `/flat` | flatten everything · `/whoami` your id + access |
| `/lot 0.02` / `/lot GBPUSD 0.03` | day lot (base; multipliers stack) |
| `/bias EURUSD long\|short\|both` | direction filter |
| `/levels EURUSD buy … sell …` | manual-AMD liquidity (sweep→target) |
| `/hold EURUSD` / `/hold all` | run across the session handover |
| `/release EURUSD` | normal handover management |
| `/close EURUSD` / `/close all` | close position(s) at market now |
| `/halt` / `/resume` | pause / re-enable all new entries + adds |
| `/status` | echo today's plan |
| `/auto EURUSD` / `/clear` | revert one / all to auto |
| `/help` | command list |
