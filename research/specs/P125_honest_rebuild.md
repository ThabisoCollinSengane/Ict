# P125 — Honest rebuild of the original strategy (base + MM, ~42% win rate)

Status: DRAFT — awaiting trader approval
Author: spec-writer · Approved by: —

## 1. The idea
- **Trader's words (2026-11-07):** "Revisit the original algo with the previous 42% win rate and the MM
  model included, the one that turned out to be a disaster because of how we backtested the data.
  Correct this and go back to the same or higher win rate."
- **Mechanical goal:** find a version of the original strategy (base Judas + breakout + MM channel,
  preset p93) that, reading ONLY candles that have closed, wins >= 42% of trades AND makes money
  after costs, in every test period.
- **What we already know (do not re-test blindly):**

| Version | Win rate | Profit factor | Source |
|---|---|---|---|
| Original (`leaky`, reads the unfinished H1/M15/H4/D candle) | 43.3% | 3.64 | P115/P119 |
| Only H1 made honest (`hon60`) | 17-24% | 0.62-0.81 | P115b |
| H1 on closed candles, the rest still leaky (`d60`) | 21-29% | 0.76-1.27 | P115c |
| Fully honest default (`mhdef`, measurement mode) | 18-23% | 0.69-0.81 | P119 |
| Fully honest, side picked by a coin | same as the real side | — | P118 |
| Ten honest dollar (DXY) reads vs a coin | none beat it | — | P120 |

  So the 42% came almost entirely from the H1 reads seeing up to ~55 minutes ahead (mostly the dollar
  gate). On honest data the strategy's direction call is a coin flip, and the ~20% win rate is what its
  trade management (10-pip stop, break-even at +10, lock at +20) does to random entries.

## 2. Honest expectation (read before approving)
Getting back to 42% **and** profit is unlikely: nothing tested so far gives an honest direction edge.
Win rate **alone** is easy to raise and meaningless. Example: a 1:1 target with no early break-even
lifts win rate toward 45-50% even on a coin, and still loses money after costs. So this project
measures win rate **together with** profit and the coin control. The likely outcome is a clear map of
what can and cannot be recovered. A pass would be the first real edge since the leak was found.

## 3. Plan in three phases (each ends at a trader check-in)

**Phase A — Where exactly did the 42% come from? (diagnostic, no pass rule)**
P115b localised the leak to the H1 timeframe. H1 is read by three different things, and we don't yet
know which one carried it. Make ONE group honest at a time, everything else as in the leaky original:
- A1 `dxyH1`: only the DXY H1 read uses closed candles (the dollar gate).
- A2 `crossH1`: only EURGBP / AUDNZD H1 (the pair-selection cross).
- A3 `pairH1`: only the traded pairs' own H1 (H1 FVG entries, MM 60-minute IFVG rung, the EU/GU H1
  structure check).

The arm whose honest version collapses the result is the one that was reading the future. This tells
us WHICH information made the 43%: next-hour dollar direction, the cross, or the pair itself.

**Phase B — Is any of it recoverable honestly? (each arm vs the coin-flip control)**
B1 — **Wait for the candle to close.** Same gate, but read on the H1 candle that just CLOSED, and enter
only within the next 15 minutes (the honest version of what the leak saw). Expected to fail, because P120's
`bos_h1` showed no edge, but it is the direct test of "correct the backtest, keep the strategy".

B2 — **Engine with the leaking read removed.** Drop the gate group from Phase A entirely, so it neither
gates nor sizes, and let the rest of the stack choose direction. The question: does the AMD / Judas /
MM stack carry any direction information without the dollar read?

B3 — **Exit redesign on the honest engine.** Only if B1 or B2 shows a direction edge (kept beats
flipped). Test three management sets:
- the current set;
- no break-even before +1R;
- a fixed 1:1 target.

This is where win rate is won or lost. Without a direction edge, it only moves losses around, and the
coin control will show that.

**Phase C — Holdout.** Run the single best arm from B, unchanged, on 2026 once.

## 4. What is known at decision time
| Read | Timeframe | How the forming bar is excluded |
|---|---|---|
| DXY / EURGBP / AUDNZD gate | H1 | closed candles (`DROP_TFS`, new per-symbol scope) |
| AMD range + Judas sweep | M15 | truncated to open..now (`HONEST_HTF`) |
| Draw cascade, CRT, HTF FVG, structure | H4 / D / W | truncated (H4, D); W is already completed-only |
| MM IFVG ladder / M1 trigger | H1 / M15 / M5 / M1 | H1 closed, M15 truncated; M5/M1 are execution bars |

## 5. Outcome, baseline, control
- Outcome per trade: win rate, average R after costs, profit factor; first legs only for direction tests.
- Baseline: the honest `mhdef` anchor (IS 316 / 21.2% / PF 0.69; OOS 338 / 23.4% / 0.73; 2026 103 / 18.4% / 0.81).
- Control: `COIN_FLIP=1` in the SAME run (P118), on 3 seeds: kept side vs flipped side, same entries,
  stops and targets.

## 6. Pass rule (fixed now, before any result)
A Phase B arm passes only if ALL of these hold, in IS 2022-23, OOS 2024-25 AND 2026:
1. Win rate >= 42%.
2. Profit factor >= 1.3 after spread and 0.5-pip stop slippage.
3. Kept side beats the coin-flipped side on average R, same sign every period, and beyond 2 SE pooled.

Phase A has no pass rule (it is diagnostic).

## 7. Cells read and chance passes
Phase B has 2 arms in B1/B2, plus at most 3 exit sets in B3, each judged in 3 periods with a 3-part rule.
For a coin to clear the bar, it would have to pass a same-sign, beyond-2-SE test in three periods and
also a 42% win rate with PF 1.3. The chance of that is well under 1 in 100 per arm.

## 8. Sample size
~300 / 340 / 100 first legs per period. A win-rate difference of 42% vs 21% is ~7 SE per period, so it is
easy to see. A kept-vs-flipped gap needs roughly 0.25R to reach 2 SE in 2026 alone; smaller gaps can
only be read pooled.

## 9. Out of scope
- No change to config.py defaults. The honest engine stays the default and new reads go behind flags.
- No live trading or funding, no paid data.
- 2026 is touched only in Phase C.
- Gold and indices are excluded (FX core only) unless the trader asks.

## 10. Build plan (for the Builder, after approval)
- `config.py`: `DROP_SYMS` (default "" = all symbols, byte-identical). When set, `DROP_TFS` applies only
  to the listed symbols. Phase A arms (leaky engine + one honest group): `dxyH1` (UDXUSD),
  `crossH1` (EURGBP, AUDNZD), `pairH1` (EURUSD, GBPUSD, NZDUSD).
- `mm-golden-isoos.yml`: new modes `p125a_dxy`, `p125a_cross`, `p125a_pair` × is/oos (2026 withheld);
  then B arms in measurement mode with `COIN_FLIP=1` seeds 1-3.
- Regression: the `leaky` arm must still give 876 / R176,034, and `mhdef` must reproduce its anchor.
- Report: `data/p125_report.md` with the tables above, plus the kept-vs-flipped table per arm.

## 11. Open questions for the trader
1. **Goal:** is it "win rate >= 42% AND profitable" (recommended), or win rate alone?
2. **Scope:** FX base + MM only (recommended), or include gold and indices?
3. **Holdout:** OK to touch 2026 only once, at the very end?

Ready for approval.
