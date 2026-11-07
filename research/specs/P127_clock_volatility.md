# P127 — Volatility by clock time (seas20): a bracket and a fade that do not pick a side

Status: DRAFT (2026-11-07) — awaiting trader approval
Author: spec-writer · Approved by: <trader>

**Three words used throughout:**
- **Bracket:** two pending orders at once, a buy-stop above the recent range and a sell-stop below it,
  so whichever side price breaks gets filled. No direction is predicted.
- **OCO ("one cancels the other"):** when one of the two orders fills, the other is cancelled at once.
- **Tercile:** one third. The "top tercile" is the highest third of values, the "bottom tercile" the lowest third.

## 0. The problem, stated first
- On spot FX we have no options, so we cannot buy a straddle. **Knowing that a big move is coming does
  not, by itself, pay anything.** A spot trade pays only if the price moves our way after we enter.
- The only direction-free spot trade is the bracket. It makes money only if, after price breaks out of
  the range, it KEEPS GOING (follow-through) more than a random walk would. **On a random walk a bracket
  loses exactly its costs, however large the volatility.** Bigger moves make the wins bigger AND the
  losses bigger in the same proportion; R stays the same.
- The mirror trade is fading the range edges when volatility is predicted to be LOW. It makes money only
  if price turns back from the edges MORE than a random walk would.
- **So the claim tested here is not "seas20 predicts the size of the move".** P123 already showed that,
  and it is true but not tradeable on its own. The claim is: **in clock slots where seas20 predicts a
  big move, price follows through after a break (or, in quiet slots, turns back from the edges) more
  than a random walk, by enough to beat the costs.**

## 1. The idea
- **In the trader's words (2026-11-07):** "Start the volatility strategy using the same-clock-time pattern."
- **Mechanical rule (one sentence):** every hour, read seas20 for that clock time; in the busiest third of
  slots place an OCO bracket just outside the last 2 hours' range (Strategy A), and in the quietest third
  fade the first touch of the range edges (Strategy B); score both in R after costs against a random walk
  that has the same clock-time volatility pattern.
- **Already tested (CLAUDE.md):**

| P | What was tested | What it found |
|---|---|---|
| P123 | Predictors of the realised 4h range, EU/GU/NZ M15 | **seas20 is the best single predictor** (rank corr +0.61 / +0.51), beating ATR16 +0.52, ATR256 +0.49 / +0.46 and Kronos +0.51. Size, not direction. |
| P122 Q2 + trade sim | First killzone M15 bar through a live range edge; follow vs fade, 2R target, 1 pip | **Every chooser loses**: always FOLLOW −0.30 / −0.30R, always FADE −0.25 / −0.23R, coin −0.28. This is Strategies A and B without the seas20 filter, and it is the strongest prior against this idea. |
| P112c | Does an H1 sweep candle reach 1R / 2R more than any candle? | No. Any candle reaches 1R ~45%, 2R ~26% — close to random-walk odds. |
| P114 / P114b | Timeframe ladders, FVG touch + M1 break, 1-pip cost | Every combo negative in two of three periods; a 1-pip cost on small stops is ~0.13-0.25R by itself. |
| P106 | Which market moves today | Own recent move ranks future move SIZE (volatility clustering), not which side. |
| P118 / P120 / P124 / P126 | Direction reads on completed bars | All coin flips. This is why P127 does not pick a side. |
| P100 / P101 | Unger wide-range-bar skip, compression size-up (leaky engine) | RED — but those were filters on a leaky engine, not a test of follow-through. |

  **What is new:** P122 tested breaks of ranges in the killzones with no volatility conditioning. P127 asks
  whether conditioning on seas20 — busy slots vs quiet slots — separates breaks that follow through from
  breaks that turn back. **Honest note:** seas20 is mostly a clock-time map (London and NY opens are the
  busy slots, Asia the quiet ones), so this is largely the question "do breakouts follow through at the
  session opens, and do edges hold in the quiet hours, more than chance?".

## 2. What is known at decision time
Decision grid: every hour on the hour, 00:00-12:00 ET (13 decisions per pair per weekday). Each trade is
closed by t + 4h, so everything is flat by 16:00 ET and no trade crosses the 17:00 ET rollover (P78: the
bid quotes spike there, which would fake stop hits).

| Read | Timeframe | How the forming bar is excluded |
|---|---|---|
| seas20 (the signal) | M15 | for decision clock c on day d: mean of (high − low) of the M15 bars in [c, c+4h) on each of the **20 previous weekdays**, all of which ended before day d began. Day d itself is never read. |
| ATR16 | M15 | mean true range of the last 16 M15 bars whose close time is <= t. The bar containing t is never read. |
| Ratio | — | seas20 / ATR16, both as above. High ratio = a big move is expected but has not happened yet. |
| Range (both strategies) | M15 | high and low of the last 8 completed M15 bars (2 hours) ending at t. |
| Tercile cut points | — | fixed on IS 2022-23 only, per pair; applied unchanged to OOS and 2026. |
| Fills, stops, targets | M1 | simulation starts with the first M1 bar that OPENS at or after t. |

Clock is New York time (as the engine). Missing M1 / M15 data on a day -> that day is skipped and counted
in the coverage line.

## 3. The two strategies
**Strategy A — expansion bracket (top-tercile seas20 slots).**
- At t: buy-stop at range high + k × seas20, sell-stop at range low − k × seas20, OCO. Orders live 60 min,
  then cancelled if neither filled. Skip the slot if price at t is already beyond either level.
- Stop: the range midpoint. R = distance from the fill price to the midpoint.
- Exit A-E1: target 2R, otherwise time exit at t + 4h. Exit A-E2: no target, time exit at t + 4h (stop live).

**Strategy B — quiet-slot fade (bottom-tercile seas20 slots).**
- At t: limit sell at the range high, limit buy at the range low, OCO, live 60 min. A limit counts as
  filled only if price trades THROUGH it by at least 0.5 pip (a bare touch does not fill — queue risk).
- Stop: k × seas20 beyond the edge that was faded.
- Exit B-E1: target the range midpoint. Exit B-E2: target the opposite edge. Both with a time exit at t + 4h.

**Costs and fill rules (both strategies, fixed now):**
- HistData prices are bid. Buys are charged the spread: 1.0 pip for EURUSD, GBPUSD and NZDUSD (the
  project convention, P114/P122); a 1.5-pip sensitivity is reported, not gated.
- Every STOP order fill — entry stops in A and protective stops in A and B — slips 0.5 pip against us.
- Inside one M1 bar: stop is checked before target. If the bar that fills the entry also reaches the
  stop, the trade is stopped. If one M1 bar triggers BOTH bracket orders, it is booked as the worst case
  (filled and stopped, −1R plus costs); how often this happens is reported.

## 4. Outcome and baseline
- **Outcome:** average R per filled trade after costs (R = the initial risk from fill to stop), plus PF.
- **Correct baseline:** on a random walk, ANY entry-and-exit rule has zero expected profit before costs
  (a driftless price has no follow-through and no reversion). So the baseline is **average R = −(cost per
  trade in R), not 0**, and a bit lower still from the conservative "stop first in a shared bar" rule.
  The null measures this number directly; it is the floor a real result must clear.
- **Win rate is reported, not gated.** Win rate is set by where the target sits, not by any edge: a 2R
  target wins about one time in three on a random walk, a midpoint target in Strategy B wins well over
  half, and both lose money there. A high-WR fade can lose and a 30%-WR bracket can win. Average R and PF
  are what pay.

## 5. Controls
The bracket has no side, so the P118 coin-flip control **does not apply** — there is no side to flip.
Strategy B's side is set by which edge is touched, which is not a prediction either. The right test is
whether price behaves differently from a random walk after the break, so:
1. **All slots:** the same rules in every slot regardless of tercile. Does the seas20 filter add anything?
   (Compared as tercile vs the other two terciles, which are disjoint, so the SE is clean.)
2. **Opposite tercile:** Strategy A in the bottom tercile, Strategy B in the top tercile.
3. **ATR-only:** the same rules with terciles cut on ATR16 instead of seas20, and the offset/stop set to
   k' × ATR16, with k' chosen on IS so the median offset in pips matches the seas20 version (same
   geometry). Does the clock pattern beat plain recent volatility? Compared as a paired, per-day difference.
4. **Null A — random walk with the real volatility shape:** M1 random walks whose volatility follows the
   real median M1 range for each clock minute, times a slow day-level random multiplier. On this null
   seas20 and ATR both predict SIZE (as in the market) but there is no follow-through and no reversion.
   This separates "predicts size" from "pays" exactly.
5. **Null B — Null A plus bid-quote noise:** independent ±0.2-0.5 pip noise on each M1 bar. This is the
   P124 bounce trap: fading the edges can win a few tenths of a pip from quote noise alone. Strategy B
   must read cost-only here too, or the fill rule is broken.
- Standard errors clustered by DAY, pooled across the three pairs (they are one dollar bet on the same day).
- Null numbers sit in the same tables as the real ones (P77 lesson), not just a verdict label.

## 6. Pass rule (fixed before any result is seen)
A cell passes only if ALL of these hold:
1. Average R after costs > 0, beyond 2 day-clustered SE, in IS 2022-23, OOS 2024-25 AND 2026 (Jan - 9 Oct).
2. PF >= 1.3 after costs in each of the three periods.
3. It beats the all-slots version (tercile minus the other two terciles, average R) AND the ATR-only
   version (paired per-day difference): positive in all three periods and beyond 2 SE pooled.
4. Null A and Null B, run through the same cell, each read within 2 SE of their own cost-only
   expectation (and within 2 SE of 0 with costs switched off).

Win rate: reported, not gated (§4). 2026 is read once, after the IS/OOS cells are fixed.

## 7. Cells read and chance passes
- Pre-registered grid: 2 strategies × 2 offsets (k = 0.10, 0.25) × 2 exits = **8 cells on the seas20
  tercile**, plus the same 8 on the **seas20 / ATR16 ratio tercile** (top ratio for A, bottom ratio for B)
  = **16 cells**. Q1 asks whether to drop the ratio family and keep it at 8.
- Chance: for one cell on noise, average R > 0 beyond 2 SE (one-sided, ~2.5%) in all three periods is
  about 0.025³ ≈ 0.00002; over 16 cells ≈ 0.0003, before PF >= 1.3 and the control comparisons.
  **Expected chance passes ≈ 0.** Chance is not the danger here; costs, the bounce trap and fill
  optimism are, which is what Null B and the conservative fill rules are for.
- Reported but not pass cells: London vs NY vs Asia slots, per pair, 1.5-pip spread sensitivity,
  both-orders-in-one-bar rate, fill rate, and win rate. Read only for a cell that passes.
- Gold and indices: not pass cells (see Q3).

## 8. Sample size
- Decisions: ~520 weekdays × 13 slots × 3 pairs ≈ 20,000 per IS / OOS half; ≈ 7,800 in 2026.
- One tercile ≈ 6,700 decisions per half (2,600 in 2026). Fill rate assumed 60-80% -> roughly
  4,000-5,000 trades per half, 1,600-2,000 in 2026.
- But trades on one day are correlated (overlapping 4h windows, three dollar pairs). With ~9 trades per
  day and within-day correlation ~0.3, per-trade SD ~1.3R: **day-clustered SE ≈ 0.035R per half,
  ≈ 0.06R in 2026.** So criterion 1 needs about +0.07R (IS/OOS) and +0.12R (2026) after costs — reachable.
- **The binding bar is PF >= 1.3.** For a 2R-target bracket winning ~35%, PF 1.3 needs about +0.2R per
  trade after costs. Costs are roughly 1 pip spread + 0.5 entry slip + 0.5 stop slip ≈ 1.5-2 pips on an R
  of ~12-15 pips ≈ 0.13-0.15R. **So a pass needs follow-through worth about +0.35R per trade before costs**
  — far more than any honest read in this project has shown. Detectable if it exists; not expected.
- Control comparisons (difference of two cells): SE ≈ 0.05R per half, smaller pooled.

## 9. Honest expectation
- P112c: any candle reaches 1R ~45% and 2R ~26% of the time, close to what a random walk gives. P122:
  range breaks in the killzones lost −0.30R when followed and −0.25R when faded, i.e. about the costs.
  P114: every entry recipe lost about the cost. **All of this predicts the bracket and the fade will lose
  roughly their cost, in every tercile, with seas20 telling us only how big the wins and losses are.**
- **What a FAIL means:** the clock-time pattern is useful for sizing, risk and choosing when to be at the
  screen, not as a profit source on spot FX. The volatility line closes as an entry edge (it could still
  feed a stop-size or position-size rule in a later, separate spec).
- **What a PASS would mean:** the first honest edge in the rework, and it would not need a direction
  read. It would say that breaks in busy clock slots follow through (or edges in quiet slots hold) more
  than chance, after realistic costs, in three separate periods. It would still be a pure-price study:
  the next step is an engine channel behind a default-OFF flag, measurement mode, with Exness costs —
  not live trading.

## 10. Out of scope
- No change to config.py defaults; no edit to backtest.py in this stage.
- No live trading, no funding, no paid data (HistData M1 only).
- 2026 is the holdout: read once at the end; no tercile cut, k, exit or slot list tuned on it.
- No new strategies, offsets, exits or signals after the first results are seen (that is a new spec).
- No direction reads (closed: P118-P126). No Kronos (closed: P121-P123).

## 11. Build plan (for the Builder, after approval)
- `scripts/clock_vol_study.py` (`--null A|B`, `--selftest`), pure price. Loader reads `SYM_YYYY.csv` AND
  `SYM_YYYY_MM.csv` (P114 fix). Clock = America/New_York; pandas `"15min"` / `"60min"`, never `"T"` (P77).
- Selftest must pin: seas20 never reads day d; the range uses completed M15 bars only (append a junk
  forming bar -> no change); OCO cancel; stop-before-target in a shared bar; both-orders-in-one-bar ->
  worst case; limit needs a 0.5-pip trade-through; zero-cost Null A average R ≈ 0.
- Workflow `.github/workflows/clock-vol-study.yml`: fetch EURUSD, GBPUSD, NZDUSD 2022-2026 (M1); run the
  nulls first, then the real study.
- Reports: `data/clock_vol_report.md` and `data/clock_vol_null.md`, plus a console transcript. Top of each:
  per-period coverage (days, decisions, fills, skipped days). Tables: every cell × period with n, fill
  rate, WR, average R ± day-clustered SE, PF, and the matching all-slots / opposite-tercile / ATR-only /
  Null A / Null B numbers on the same row.
- Engine channel: only after a pass, in a new spec.

## 12. Open questions for the trader
1. **Ratio family:** keep the seas20 / ATR16 ratio as a second set of 8 cells (16 in total, recommended:
   keep — it is the "expansion expected but not yet happened" idea and chance passes stay ≈ 0), or drop it
   and test seas20 alone (8 cells)?
2. **Slots:** every hour 00:00-12:00 ET (recommended — Asia supplies most of the quiet slots Strategy B
   needs, and nothing crosses the 17:00 rollover), or only the killzones (London 03-05, NY 07-10 ET)?
3. **Gold and indices:** skip (recommended — they need their own spreads and sizes, P107), or add them as
   reported-only rows (not pass cells), using data the P126 workflow already fetches?

Ready for approval.
