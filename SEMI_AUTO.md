# Semi-auto mode — daily inputs via Telegram

Steer the live bot each day from your phone: set the **lot**, tell it which
**direction** to hunt per pair, and hand it the **buy-side / sell-side levels**
you're watching. The bot still runs its full validated ICT logic — your inputs
**filter and aim** it, they don't replace it.

It's **opt-in per pair per day.** Set nothing → that pair trades fully automatic,
exactly as before. Inputs auto-expire at 00:00 UTC, so yesterday's levels never
leak into today.

---

## The three inputs

| You send | Effect |
|---|---|
| **`/lot 0.02`** | Day lot (all pairs). `/lot GBPUSD 0.03` sets one pair. This becomes the **base** lot — the draw 2×/3× and 1.25× confluence/CRT/PDL bumps still stack on top (they only fire at R3k+ anyway). |
| **`/bias EURUSD long`** | Hunt **longs only** on EURUSD today (`short` / `both`). A **filter**: the bot still needs its own ICT setup to fire — it just won't take the other direction. |
| **`/levels EURUSD buy 1.0950 1.0975 sell 1.0900 1.0880`** | Your **buy-side** (above) and **sell-side** (below) liquidity. Runs **full manual AMD** — see below. |

Plus: **`/status`** (echo today's plan), **`/auto EURUSD`** (revert one pair),
**`/clear`** (revert all), **`/help`**.

Every command gets an acknowledgement back so you always see what registered.

---

## How the levels work — full manual AMD

Your two sides define the day's range. The bot waits for **manipulation** (a
sweep of one side) then trades the **distribution** toward the other:

- Price **sweeps the sell-side** (dips below it) and **reclaims** → the bot hunts
  **LONGS**, targeting the **buy-side**.
- Price **sweeps the buy-side** (pokes above) and drops back → the bot hunts
  **SHORTS**, targeting the **sell-side**.
- **Neither side swept yet** → the bot **waits** (no trade — manipulation hasn't
  happened).

So the levels do two things at once: they **gate the direction** (only trade the
post-sweep way) and they **set the target** (the opposite side becomes the TP,
when it's a valid ≥1R / ≥ min-target draw). The bot's own MSS + FVG entry still
has to trigger — the levels decide *which way* and *where to*, your engine decides
*whether the setup is there*.

If both `/bias` and `/levels` are set, **both must agree** — they're both filters.

---

## A typical morning

At the first killzone bar the bot sends you a **SESSION START** template. Reply:

```
/lot 0.02
/bias EURUSD long
/levels EURUSD buy 1.0975 sell 1.0900 1.0880
/status
```

The bot acks each line, then trades EURUSD **long-only**, but only **after**
price sweeps 1.0900/1.0880 and reclaims — aiming at 1.0975 — and only if its own
setup fires. GBPUSD / NZDUSD (untouched) keep trading fully automatic.

Change your mind mid-session? Send another `/bias` or `/levels`; `/auto EURUSD`
drops EURUSD back to automatic.

---

## Setup

Nothing extra to install — it reuses your existing Telegram bot token + chat id
(the same ones already sending trade alerts). The bot only obeys **your** chat
id; no one else can steer it.

- Config lives in `live/session_inputs.py` (state) + `live/telegram_control.py`
  (command parsing/polling). The engine reads it in `live/run_live.py`.
- Offline self-test (no MT5/network): `python -m live.test_semi_auto`.

> **DEMO first**, same as the rest of the go-live checklist in
> `AZURE_WINDOWS_SETUP.md`. Prove the semi-auto flow on a demo account before it
> touches the funded one.
