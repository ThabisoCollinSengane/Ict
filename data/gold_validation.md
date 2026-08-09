# Gold (XAUUSD) gate — validation

Baseline (`GOLD_ENABLED=0`) vs gold (`GOLD_ENABLED=1`, DXY+silver+AUDUSD gate). **XAUUSD sizing is provisional (GOLD_PIP=1.0) — absolute equity is NOT calibrated; PF/WR/MaxDD are scale-invariant and ARE the edge signal.** Ship gold ON only if the book's MaxDD is not worse and gold trades are PF-positive in both splits.

_run commit: `fdcdbc3`_

## Full 4yr

| metric | baseline | +gold | Δ |
|---|---|---|---|
| trades | 804.00 | 812.00 | +8.00 |
| win rate | 44.90% | 43.20% | -1.70 |
| profit factor | 4.95 | 2.95 | -2.00 |
| max drawdown | -12.76% | -21.12% | -8.36 |
| ending equity ZAR | 559,725,110 | 172,982,107 | -386,743,002 |

_gold trades taken: 0_

## IS 2022-23

| metric | baseline | +gold | Δ |
|---|---|---|---|
| trades | 389.00 | 389.00 | +0.00 |
| win rate | 44.70% | 44.70% | +0.00 |
| profit factor | 2.86 | 2.86 | +0.00 |
| max drawdown | -12.76% | -12.76% | +0.00 |
| ending equity ZAR | 271,929 | 271,929 | +0 |

_gold trades taken: 0_

## OOS 2024-25

| metric | baseline | +gold | Δ |
|---|---|---|---|
| trades | 409.00 | 409.00 | +0.00 |
| win rate | 45.00% | 45.00% | +0.00 |
| profit factor | 4.95 | 4.95 | +0.00 |
| max drawdown | -12.55% | -12.55% | +0.00 |
| ending equity ZAR | 2,229,736 | 2,229,736 | +0 |

_gold trades taken: 0_

## Verdict

**🔴 RED — do NOT ship gold ON (GOLD_ENABLED stays 0).**

- **Full 4yr: 🔴 fail** — MaxDD -21.12 worse than -12.76; gold took 0 trades (data/gate issue)
- **IS 2022-23: 🔴 fail** — gold took 0 trades (data/gate issue)
- **OOS 2024-25: 🔴 fail** — gold took 0 trades (data/gate issue)

_Reminder: calibrate GOLD_PIP / gold contract before trusting absolute equity; then re-run. Also inspect gold-only WR/PF (report scenario table G-long/G-short) for the not-curve-fit IS/OOS ballpark check._
