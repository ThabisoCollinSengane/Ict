# Gold (XAUUSD) gate — validation

Baseline (`GOLD_ENABLED=0`) vs gold (`GOLD_ENABLED=1`, DXY+silver+AUDUSD gate). **XAUUSD sizing is provisional (GOLD_PIP=1.0) — absolute equity is NOT calibrated; PF/WR/MaxDD are scale-invariant and ARE the edge signal.** Ship gold ON only if the book's MaxDD is not worse and gold trades are PF-positive in both splits.

_run commit: `0c8275f`_

## Full 4yr

| metric | baseline | +gold | Δ |
|---|---|---|---|
| trades | 804.00 | 971.00 | +167.00 |
| win rate | 44.90% | 40.60% | -4.30 |
| profit factor | 4.95 | 3.71 | -1.24 |
| max drawdown | -12.76% | -15.67% | -2.91 |
| ending equity ZAR | 567,575,614 | 904,689,958 | +337,114,344 |

_gold trades taken: 167_

## IS 2022-23

| metric | baseline | +gold | Δ |
|---|---|---|---|
| trades | 389.00 | 446.00 | +57.00 |
| win rate | 44.70% | 42.60% | -2.10 |
| profit factor | 2.88 | 2.95 | +0.07 |
| max drawdown | -12.76% | -15.67% | -2.91 |
| ending equity ZAR | 273,481 | 753,834 | +480,353 |

_gold trades taken: 57_

## OOS 2024-25

| metric | baseline | +gold | Δ |
|---|---|---|---|
| trades | 409.00 | 453.00 | +44.00 |
| win rate | 45.00% | 40.80% | -4.20 |
| profit factor | 4.95 | 3.49 | -1.46 |
| max drawdown | -12.55% | -20.00% | -7.45 |
| ending equity ZAR | 2,241,887 | 1,028,161 | -1,213,726 |

_gold trades taken: 44_

## Verdict

**🔴 RED — do NOT ship gold ON (GOLD_ENABLED stays 0).**

- **Full 4yr: 🔴 fail** — MaxDD -15.67 worse than -12.76
- **IS 2022-23: 🔴 fail** — MaxDD -15.67 worse than -12.76
- **OOS 2024-25: 🔴 fail** — MaxDD -20.00 worse than -12.55

_Reminder: calibrate GOLD_PIP / gold contract before trusting absolute equity; then re-run. Also inspect gold-only WR/PF (report scenario table G-long/G-short) for the not-curve-fit IS/OOS ballpark check._
