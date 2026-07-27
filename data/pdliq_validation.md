# PDH/PDL-sweep sizing lever — full-backtest validation

Baseline (`PDLIQ_SWEEP_MULT=1.0`) vs lever (`1.25`) on the full 4yr and the IS/OOS splits. `sized` = trades the lever bumped. **Ships only if full-4yr equity is up and MaxDD is not worse, and both splits stay positive with MaxDD not materially worse.**

_run commit: `a453405`_

## Full 4yr

| metric | baseline | lever 1.25× | Δ |
|---|---|---|---|
| trades | 602.00 | 602.00 | +0.00 |
| win rate | 45.30% | 45.30% | +0.00 |
| profit factor | 3.45 | 3.49 | +0.04 |
| max drawdown | -12.95% | -12.95% | +0.00 |
| ending equity ZAR | 8,743,319 | 11,702,904 | +2,959,585 |

_trades sized by lever: 91_

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
| trades | 210.00 | 209.00 | -1.00 |
| win rate | 44.30% | 44.00% | -0.30 |
| profit factor | 3.47 | 3.50 | +0.03 |
| max drawdown | -15.41% | -15.41% | +0.00 |
| ending equity ZAR | 32,293 | 34,690 | +2,398 |

_trades sized by lever: 31_

## Verdict

**🟢 GREEN — provisional ship. Full-4yr equity up + MaxDD held; both splits positive.**

- **Full 4yr: 🟢 pass** — ok
- **IS 2022-23: 🟢 pass** — ok
- **OOS 2024-25: 🟢 pass** — ok

_Provisional — Claude reviews the split magnitudes (IS/OOS same ballpark?) before final ship, per the 'what not curve-fit means' rule._
