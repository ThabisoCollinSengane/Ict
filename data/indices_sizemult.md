# US index gate — INDEX_SIZE_MULT sweep (full 4yr)

_run commit: `7931aca`_. Baseline = indices off. Goal: smallest downsize whose full-4yr MaxDD is back under the -15% breaker (ideally ~baseline) with equity still up and PF held. IS/OOS already pass (see indices_validation.md).

| config | trades | WR% | PF | MaxDD% | equity ZAR |
|---|---|---|---|---|---|
| baseline (off) | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 |
| indices x1.0 | 1053.00 | 43.10 | 4.72 | -15.53 | 1,674,637,110 |
| indices x0.75 | 1114.00 | 42.70 | 4.83 | -15.04 | 1,459,306,792 |
| indices x0.5 | 1115.00 | 42.50 | 4.95 | -15.77 | 985,466,557 |
| indices x0.35 | 1115.00 | 42.50 | 5.02 | -15.40 | 795,320,565 |

**No multiplier held full-4yr MaxDD at baseline** — try smaller (0.25) or keep indices off. The edge is real (IS/OOS pass) but the compounding path adds drawdown even downsized.
