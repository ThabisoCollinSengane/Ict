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
/read            market-structure template for all pairs
/read EURUSD     just that pair
/markets         all pairs at a glance
/positions       open trades + live P&L (also /open, /trades)
/account         equity, day P&L, drawdown, halt state (also /equity)
/dxy             synthetic dollar index right now
/session         which killzone, and whether new entries are allowed
```
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
/close EURUSD          → close EURUSD's open position(s) at market, now
/close all             → flatten everything
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

## Safety

- **Only your Telegram chat can steer the bot** — anyone else messaging it is ignored.
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
| `/read [EURUSD]` · `/markets` | market-structure read (template) |
| `/positions` · `/account` · `/dxy` · `/session` | live read-outs |
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
