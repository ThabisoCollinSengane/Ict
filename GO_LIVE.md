# Go-live — pre-flight, and what to actually expect

Written 2026-09-14, the night before funding. R1,000 · Exness ZAR · MT5.

---

## PART A — Pre-flight: what I verified tonight

### ✅ The live path loads clean

`live/run_live.py`, `live/mt5_connector.py`, `live/session_inputs.py`,
`live/telegram_control.py`, `live/smoke_test.py`, `backtest.py`, `config.py`,
`risk.py` — all compile without error.

**`LiveTrader` subclasses `Backtester`**, so the live runner inherits the full
validated strategy — the scenario cascade, conviction scoring, target selection,
structural stops, every sizing lever. It is *not* the cut-down QuantConnect port
in `main.py` (that one is missing the EURGBP cascade and the 2a gates). You are
running the thing that was tested.

### ✅ Nothing experimental is live

Every one of these is off or a no-op, checked against the actual config object,
not from memory:

`MM_GOLDEN` · `MM_STANDALONE` · `MM_CONTINUATION` · `DRAW_CONT` · `NY_PM` ·
`BONDS_BIAS` · `USE_CONDITIONAL_VOLUME` · `RANGE_BIAS` · `STRUCT_BIAS` ·
`MSS_REQUIRE_DXY` · `STRICT_BAR_CLOSE` · `TRAIL_AT_TP` · `TP_RUNNER` ·
`HTF_TARGET_PREF` · `MIN_TARGET_SCALED` · `FVG_TARGET_FIX` · `TARGET_RUNG_*` ·
`DXY_PREFER_REAL`

### ⚠️ One live find — a disarmed landmine

`RANGE_BIAS_USE_LEAN` was defaulting to **True**. That is the flag whose last
recorded run produced **win rate 15.2%, profit factor 0.64, drawdown −51.99%**,
and the record is explicit that its polarity *"was guessed, never specified, and
is probably inverted."*

**It is not firing.** I traced the whole call graph: every path to it sits behind
`RANGE_BIAS_ENABLED` (off) or the MM golden channel (off). So it is inert for
your live run and nothing about tomorrow changes.

**But it was a loaded gun.** Anyone flipping `RANGE_BIAS_ENABLED=1` to experiment
would have silently inherited the untested lean along with it. **Default now
flipped to 0**, with the reason pinned in a comment beside it.

> Because I cannot run the backtest here (no price data in this session), the
> proof of inertness is *static* — the call-graph trace. The next time you run
> the backtest it must still reproduce **736 / 43.9% / 4.01 / −13.24%** exactly.
> If it doesn't, this change is the first thing to look at.

### ☐ What you must do — in this order

1. **Demo first.** `python -m live.smoke_test` on a DEMO account. It places no
   trades. It proves the connection, resolves every symbol (this is where broker
   suffixes like `EURUSD.m` bite), pulls bars on each timeframe, and sanity-checks
   the synthetic dollar index lands in the 90–115 range.
2. **One demo session** with the runner actually live, start to finish. Watch one
   trade open and close. You are checking plumbing, not performance.
3. **Then fund**, and run the same command against the live credentials.
4. **Credentials via environment variables only.** Never in a file, never in git.

---

## PART B — What to expect

Everything here comes from the measured 736-trade record, or from simulating
20,000 paths at your actual starting size.

### The single most important number

> ### More than half your trades will lose.
> **Win rate 43.9%.** That is the measured, validated, profitable number.

This is a strategy with a small stop and a target three times bigger. It is
*supposed* to lose more often than it wins. If you catch yourself thinking
"it's not working" after three losses, that is the strategy working exactly as
designed.

### How often it trades

**About 15 trades a month** across all three pairs — roughly 3–4 a week. Some
weeks will have one. The cap is 1 per pair, 3 per day, and most days will be
zero or one.

### Losing streaks — the part that hurts

| streak | chance of starting on any trade | expect roughly |
|---|---|---|
| 3 in a row | 17.7% | **32× a year** |
| 4 in a row | 9.9% | 18× a year |
| **5 in a row** | 5.6% | **10× a year** |
| 6 in a row | 3.1% | 6× a year |
| 8 in a row | 1.0% | ~2× a year |

**Expect a run of about 8 losses in a row at some point in your first year.**
Not as a worst case — as the *expected* longest run. When it happens it is not a
malfunction.

The 5-loss breaker will fire roughly **10 times a year**. That is the design
working, not the strategy failing.

### ⚠️ The drawdown you'll feel is NOT the −13.24% headline

At R1,000 on 0.02 lots, **one stop is R37 — that's 3.7% of the account.**

| losses in a row | equity | drawdown | what fires |
|---|---|---|---|
| 1 | R963 | −3.7% | — |
| **2** | R926 | −7.4% | **daily −6% cap → day over** |
| 3 | R889 | −11.1% | daily cap |
| 4 | R852 | −14.8% | daily cap |
| **5** | R815 | **−18.5%** | **10-DAY HALT** + 5-loss rule |

**Two losses ends most of your days.** Five consecutive losses triggers the
10-day halt — and 5-in-a-row happens about ten times a year.

The backtest's −13.24% was measured across a four-year curve that spent most of
its life far above R1,000, where a single stop is a rounding error. **At R1,000
the percentage swings are brutal in a way the headline number does not convey.**
This is arithmetic, not a defect — but it is the thing most likely to make you
abandon a working system in week three.

### Where R1,000 actually lands

20,000 simulated paths, 0.02 lots, using the measured win rate:

| after | worst 10% | poor 25% | **typical** | good 75% | best 10% | chance you're below R1,000 |
|---|---|---|---|---|---|---|
| 1 month | R889 | R1,037 | **R1,185** | R1,333 | R1,518 | **20%** |
| 2 months | R963 | R1,148 | **R1,370** | R1,592 | R1,814 | 12% |
| 3 months | R1,037 | R1,296 | **R1,555** | R1,851 | R2,110 | 7% |
| 6 months | R1,407 | R1,740 | **R2,147** | R2,554 | R2,924 | 2% |
| 12 months | R2,221 | R2,739 | **R3,294** | R3,849 | R4,404 | <1% |

**One month in five, you will be down after the first month.** That is a normal
outcome of a 44%-win-rate system, not evidence of anything.

In the unluckiest tenth of paths, the drawdown along the way reaches about −33%
in the first three months. The system survives it. The question is whether you do.

### The milestones that change things

| | |
|---|---|
| **R3,000** | Lot rises to 0.05. **The sizing multipliers switch on** — draw cascade 2×/3× and the five 1.25× levers. This is where the compounding actually starts. |
| **R6,000** | Lot rises to 0.09. Monthly withdrawals begin, banking everything above R6,000 as income. |

Typical path reaches R3,000 somewhere around **months 9–12**. Faster if you run
hot early. **The first R2,000 is the slowest and least rewarding part of this
whole thing** — that is the phase to survive, not to optimise.

Once at R6,000 the backtest's steady state is roughly **R33,000 a year** of
withdrawals.

---

## PART C — Is it working, or is it broken?

### Normal. Do nothing.

- Three, five, even eight losses in a row
- A month that ends down
- The daily cap firing twice in a week
- The 10-day halt firing once in the first few months
- Two weeks with barely any trades at all

### Watch, but don't act yet

- **Win rate under 35% after 50+ trades.** Below the measured 43.9% but within
  the range of luck. Note it, keep going.
- **Trades firing outside the killzones**, or more than 3 in a day → plumbing bug,
  not strategy. Tell me.
- **Stops not being placed at all** → connection issue. Stop and tell me.

### Stop and call me

- **Any trade placed with no stop loss.** Halt immediately.
- **Win rate under 30% after 100 trades.** That is outside what the measured
  distribution produces; something is wrong with the live wiring.
- **A single loss bigger than about 12 pips** on the base position — the stop is
  capped at 10, so a bigger one means it isn't being respected.
- **Drawdown past −30%.** The breakers should make this near-impossible. If it
  happens they aren't firing.

---

## PART D — The one honest risk

The backtest is optimistic relative to live in one specific, documented way.

**The higher-timeframe bar reads use the bar that is still forming.** At 09:00, a
four-hour candle covering 08:00–12:00 already carries its 11:00 high in the
backtest. Live, it does not — you only have what has happened. This is recorded
in the project notes, it is real, and it has never been fixed (the obvious fix —
dropping the forming bar — was tested and was far worse, because it made signals
*staler* than live rather than more honest).

**What this means practically:** live results should be expected to land *below*
the backtest, not on it. I cannot tell you by how much. That is the main reason
to start at R1,000 and let real trades answer the question rather than argue
about it.

It is also why the monthly review compares your live win rate and profit factor
against 43.9% and 4.01 — if live comes in materially under, the forming-bar
optimism is the first suspect, and it is measurable once you have 50+ real trades.

---

## The one-line version

**More than half your trades lose. Two losses ends your day. You'll have an
eight-loss streak this year. One month in five ends down. The first R2,000 is
the hardest part. None of that is the system breaking — all of it is in the
measured record. The only thing that can actually end this is you overriding it
during a normal losing streak.**

That is what the five rules are for.
