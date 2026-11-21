# PDH/PDL-sweep sizing lever — full-backtest validation

Baseline (`PDLIQ_SWEEP_MULT=1.0`) vs lever (`1.25`) on the full 4yr and the IS/OOS splits. `sized` = trades the lever bumped. **Ships only if full-4yr equity is up and MaxDD is not worse, and both splits stay positive with MaxDD not materially worse.**

_run commit: `2abe5be`_
_**TRUE 4yr run** — 2025 M1 data present._

## Full 4yr

| metric | baseline | lever 1.25× | Δ |
|---|---|---|---|
| trades | 810.00 | 810.00 | +0.00 |
| win rate | 45.90% | 45.90% | +0.00 |
| profit factor | 4.47 | 4.46 | -0.01 |
| max drawdown | -12.95% | -12.95% | +0.00 |
| ending equity ZAR | 429,300,486 | 675,623,325 | +246,322,839 |

_trades sized by lever: 122_

## IS 2022-23

| metric | baseline | lever 1.25× | Δ |
|---|---|---|---|
| trades | 389.00 | 389.00 | +0.00 |
| win rate | 45.80% | 45.80% | +0.00 |
| profit factor | 3.09 | 3.04 | -0.05 |
| max drawdown | -12.95% | -12.95% | +0.00 |
| ending equity ZAR | 313,759 | 343,444 | +29,685 |

_trades sized by lever: 48_

## OOS 2024-25

| metric | baseline | lever 1.25× | Δ |
|---|---|---|---|
| trades | 418.00 | 417.00 | -1.00 |
| win rate | 45.90% | 45.80% | -0.10 |
| profit factor | 4.47 | 4.46 | -0.01 |
| max drawdown | -15.41% | -15.41% | +0.00 |
| ending equity ZAR | 1,593,594 | 2,012,439 | +418,844 |

_trades sized by lever: 62_

## Verdict

**🟢 GREEN — provisional ship. Full-4yr equity up + MaxDD held; both splits positive.**

- **Full 4yr: 🟢 pass** — ok
- **IS 2022-23: 🟢 pass** — ok
- **OOS 2024-25: 🟢 pass** — ok

_Provisional — Claude reviews the split magnitudes (IS/OOS same ballpark?) before final ship, per the 'what not curve-fit means' rule._
