# P126 — An honest forecast of the current hour's dollar move

Status: DRAFT (2026-11-07) — awaiting trader approval
Author: spec-writer · Approved by: —

## 1. The idea
- **Trader's choice (2026-11-07, after P125 Phase A):** look for an HONEST way to forecast where the
  dollar's current H1 candle will close. If one exists, it replaces the leaky DXY H1 read in the engine.
- **Mechanical rule (one sentence):** at a decision time t inside the killzones, using only candles that
  have closed by t, predict whether DXY will be higher or lower at the end of the current H1 candle than
  it is now.
- **What we already know:**

| P | What was tested | Result |
|---|---|---|
| P115b / P125 A | Make only the DXY H1 read honest | WR 42-44% -> 28.5% / 29.9%, PF 1.97 / 4.83 -> 1.17 / 1.46. The leak WAS the dollar hour. |
| P118 `cfp93` | Leaky read, side flipped | flipped trades reach 1R only 13-16% — the leaky read knew the next hour almost perfectly |
| P120 | 10 DXY reads on completed bars (H1/H4/D BOS, latch, momentum, EMA, prior day, d2s) vs the PAIRS' next 1-4h | none beat a coin |
| P124 | ICT session position vs close-vs-now | 0 of 12 cells pass |
| P121-P123 | Kronos direction / Judas / expansion | coin; expansion = a longer volatility window |

  **What is new here:** P120 asked "does the dollar's past predict the pairs' next 1-4 hours?". This asks
  a narrower thing: "does what has happened SO FAR inside this hour — on DXY, the pairs, the crosses,
  gold and the US indices — predict the REST of this hour on DXY?". Different target, different inputs
  (intra-hour, cross-market). It is still very likely to fail.

## 2. Stage 0 — how good would a forecast have to be? (measure first, no pass rule)
Before testing any predictor, measure the accuracy bar on the engine itself, so a "pass" is judged
against what it would actually buy:
1. On the leaky engine (`leaky`, IS + OOS, measurement mode), record at every first-leg entry BOTH DXY H1
   reads: `dxy_h1_leaky` (forming candle, what the engine used) and `dxy_h1_honest` (closed candles).
   Report: how often they differ; win rate / PF on trades where they agree vs differ.
2. On the 5-minute grid of §3, report how often the leaky read's sign equals the sign of
   (hour close − price now). That is the leak's accuracy on THIS project's target.
3. Rough mapping to engine WR: honest DXY read ≈ 50% accurate -> 28.5-30% WR; leaky ≈ near-perfect ->
   42-44%. If WR rises roughly in a straight line with accuracy, **a 55% forecast buys about +1.5 WR
   points, and reaching 42% needs ~95-100% accuracy.** No honest predictor of the next ≤ 60 minutes of a
   currency index is plausibly anywhere near that. Stage 0 replaces this guess with measured numbers.

**Say it plainly:** even a clean pass in Stage 1 is very unlikely to bring the engine back to 42%. It
would still be the first honest direction edge in the rework, and worth knowing.

## 3. What is known at decision time
Decision grid: every 5 minutes in the killzones the gate actually serves — London 03:00-04:55 ET,
NY 07:00-09:55 ET (60 decisions per day). Each decision belongs to the H1 candle that contains it
(UTC hours = whole ET hours, so the boundaries match the engine).

| Read | Timeframe | How the forming bar is excluded |
|---|---|---|
| Every predictor below | M1 / M5 / M15 | only bars whose close time is <= t; the bar containing t is never read |
| "Price now" for the target | M1 | the OPEN of the first M1 bar starting at t (see the bounce trap, §5) |
| Hour close (outcome) | M1 | close of the last M1 bar of the current H1 candle — future, used only as the answer |

## 4. Outcome and baseline
- **Main outcome:** sign of (DXY at the end of the current H1 candle − DXY now). Ties (zero move) dropped.
  **Baseline = 50%** on a random walk. NOT "close vs the hour's open": that scores 70-76% on a random walk
  (P124) and is not a test.
- **Secondary outcome (descriptive, not a pass cell):** what the leaky gate actually needed — will the
  current H1 candle close produce an `htf_bias` break up / down / none? Its random-walk score is not 50%;
  report it next to the null's score only.
- Report every rule by minutes left in the hour (0-15 / 15-30 / 30-45 / 45-60) and London vs NY —
  as splits, not as extra pass cells.

## 5. Traps (the Builder and Auditor must check these)
1. **DXY is ~58% EURUSD.** "EURUSD moved down this hour" is almost the same statement as "DXY moved up
   this hour". Pair moves are not independent evidence; they are mostly DXY's own move again.
2. **Momentum on a random walk is a coin.** On a vs-now target, any "move so far" rule reads 50% on a
   random walk. Anything above that must come from the market, not the geometry — the null proves it.
3. **The bounce trap (P124).** HistData quotes are bid prices with tick noise. If "price now" is the
   same M1 close the predictors just read, a "fade the last minute" rule wins a little from the noise
   alone (P124 discount: +0.2-0.3 pip, not tradeable). Fix: "price now" = the open of the NEXT minute;
   the null includes quote noise to confirm the fix works.
4. **Decisions in one hour share one answer.** Twelve decisions inside the same hour all score against
   the same close. Standard errors are clustered by DAY (which also covers the hour).

## 6. Control and null
- **Coin:** 50% on the main outcome.
- **Null A:** independent random walks for every symbol — every rule must read ~50%.
- **Null B:** correlated by construction — pairs = −k × DXY + noise, gold and indices partly tied to DXY,
  plus bid-quote noise — every rule must STILL read ~50% on the vs-now target. (If a rule beats 50% here,
  it is the bounce or the geometry, and the study is broken.)
- Null tables go in the same table as the real results (P77 lesson), not just a verdict label.
- Stage 2 control: `COIN_FLIP=1` seeds 1-3 in the same run (P118).

## 7. Candidate predictors (pre-registered — no others are scored)
All "this hour" moves = last completed M1 close − the H1 candle's open. The sign tested is both ways:
a rule passes as FOLLOW (hit > 50%) or FADE (hit < 50%), but the sign must be the same in all three periods.

| # | Rule | Reads |
|---|---|---|
| R1 | `dxy_hour` | DXY move so far this hour |
| R2 | `dxy_m5_bos` | engine `htf_bias` on completed DXY M5 bars |
| R3 | `dxy_m15_bos` | engine `htf_bias` on completed DXY M15 bars |
| R4 | `cross_hour` | EURGBP and AUDNZD move so far this hour (vote; flat if they disagree) |
| R5 | `gold_hour` | XAUUSD move so far this hour (gold up -> dollar down) |
| R6 | `index_hour` | SPXUSD + NSXUSD move so far this hour (risk-on -> dollar down) |
| R7 | `vote` | majority of R1-R6, abstain on a tie |

Reported but not a pass cell (trap 1): `pairs_hour` = −(EURUSD + GBPUSD + NZDUSD move this hour).
USDJPY is NOT in the project's data (`fetch_histdata.py` list); it is free on HistData — see Q2.

## 8. Pass rule (fixed now, before any result)
**Stage 1** — a rule passes only if, in IS 2022-23, OOS 2024-25 AND 2026 (Jan - 9 Oct):
1. hit rate differs from 50% by more than 2 day-clustered SE, same sign in all three periods; AND
2. the economic bar: hit rate >= 55% (or <= 45% for a fade) in every period; AND
3. Null A and Null B both read within 2 SE of 50% for that rule.

Costs do not apply in Stage 1 (pure direction; no trade).

**Stage 2** (only if a rule passes Stage 1): the P125 pass rule, unchanged — in IS, OOS AND 2026:
WR >= 42%, PF >= 1.3 after spread + 0.5-pip stop slippage (stop before target on a shared bar), and kept
side beats the coin-flipped side on average R, same sign every period and beyond 2 SE pooled.

## 9. Cells read and chance passes
- Stage 1: 7 rules × 3 periods = 21 cells; a rule needs 3 of 3. For a coin, the chance one rule clears
  same-sign-beyond-2-SE in all three periods is about 2 × 0.025³ ≈ 0.00003; over 7 rules ≈ 0.0002, before
  even the 55% bar. **Chance is not the danger here; the bounce and the geometry are** — that is what the
  two nulls are for. The splits in §4 (minutes left, London/NY) are read only for a rule that passes.
- Stage 2: at most 1-2 arms × 3 periods.

## 10. Sample size
- Decisions: ~520 days × 60 ≈ 31k per IS / OOS half, ~200 days × 60 ≈ 12k in 2026.
- But decisions in one hour share one answer, so the real sample is about day-hours: ~2,600 (IS), ~2,600
  (OOS), ~1,000 (2026). Day-clustered SE ≈ 1.0-1.5 pp (IS/OOS), ≈ 2 pp (2026).
- A 55% rule is ~3-5 SE per half and ~2.5 SE in 2026 — reachable. A 52% rule is ~1-2 SE: invisible in 2026,
  and economically useless anyway (§2).
- Stage 2: ~300 / 340 / 100 first legs per period (P125); a kept-vs-flipped gap needs ~0.25R for 2 SE in 2026.

## 11. Out of scope
- No change to config.py defaults; no edit of the shared gate's default behaviour (new read behind a
  default-OFF flag only, Stage 2).
- No live trading, no funding, no paid data.
- 2026 is the holdout: read once per stage, after IS/OOS are fixed; no rule, threshold or split tuned on it.
- No new predictors after the first results are seen (that would be a new spec).
- Kronos and other models: closed (P121-P123).

## 12. Build plan (for the Builder, after approval)
- **Stage 0:** record-only engine columns `dxy_h1_leaky` / `dxy_h1_honest` at entry (both close whitelists +
  MM block), default OFF -> `leaky` arm byte-identical (876 / R176,034; IS 424 / 42.2% / 3.13). Arms
  `p126s0` × is/oos in `mm-golden-isoos.yml`. The grid accuracy of the leaky read lives in the study script.
- **Stage 1:** `scripts/dollar_hour_forecast.py` (`--null A|B`, `--selftest`), loader reads `SYM_YYYY.csv`
  AND `SYM_YYYY_MM.csv` (P114 fix). Workflow `.github/workflows/dollar-hour-forecast.yml` (fetch UDXUSD,
  EURUSD, GBPUSD, NZDUSD, EURGBP, AUDNZD, XAUUSD, SPXUSD, NSXUSD 2022-2026). Reports
  `data/dollar_hour_forecast_report.md` and `data/dollar_hour_forecast_null.md` (null numbers in the
  same tables as real ones). Print per-period coverage (days, decisions, missing symbols) at the top.
  Run the nulls first.
- **Stage 2 (only on a pass):** flag `DXY_H1_FORECAST` (default "" = off) in the engine's DXY H1 read —
  check the `_dxy_bias` / `_dxy_bias_1h` overrides in `run_backtest_histdata.py` first (the P63 trap) —
  measurement mode, `COIN_FLIP=1` seeds 1-3, IS/OOS, then 2026 once.

## 13. Open questions for the trader
1. **Stage 2 when Stage 1 passes but Stage 0 says it cannot reach 42%:** run the engine test anyway (one
   cheap run, recommended) or stop at Stage 1?
2. **USDJPY:** add it (free on HistData, ~14% of DXY, the second-biggest piece) as an R8, or keep the list
   as is (recommended: as is — one variable at a time)?
3. **Grid:** every 5 minutes in the killzones only (recommended), or every 15 minutes 03:00-11:45 ET like P124?

Ready for approval.
