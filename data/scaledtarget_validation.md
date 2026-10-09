# Equity-scaled target floor — flat-20 vs flat-30 vs scaled(20/30)

Scaled = 20-pip floor below R3k (small-account compounding), 30-pip above (large-account quality). **Ship scaled only if it beats flat-30 on full-4yr equity with MaxDD not worse, both splits holding.**

_run commit: `6158c1c`_

## Full 4yr

| floor | trades | WR | PF | MaxDD | equity ZAR |
|---|---|---|---|---|---|
| flat 20 | 810.00 | 45.90% | 4.46 | -12.95% | 675,623,325 |
| flat 30 (shipped) | 804.00 | 44.90% | 4.95 | -12.76% | 567,575,614 |
| SCALED 20/30 | 804.00 | 44.90% | 4.95 | -12.95% | 563,610,971 |

## IS 2022-23

| floor | trades | WR | PF | MaxDD | equity ZAR |
|---|---|---|---|---|---|
| flat 20 | 389.00 | 45.80% | 3.04 | -12.95% | 343,444 |
| flat 30 (shipped) | 389.00 | 44.70% | 2.88 | -12.76% | 273,481 |
| SCALED 20/30 | 389.00 | 44.70% | 2.88 | -12.95% | 271,571 |

## OOS 2024-25

| floor | trades | WR | PF | MaxDD | equity ZAR |
|---|---|---|---|---|---|
| flat 20 | 417.00 | 45.80% | 4.46 | -15.41% | 2,012,439 |
| flat 30 (shipped) | 409.00 | 45.00% | 4.95 | -12.55% | 2,241,887 |
| SCALED 20/30 | 410.00 | 45.10% | 4.94 | -16.12% | 1,825,825 |

## Pyramiding — did the 30-pip floor starve adds?

`pyramids added` = legs that fired; `blocked by target-room gate` = adds rejected because <floor pips remained to TP. If flat-30 adds ≪ flat-20, the floor is starving pyramids and a separate PYRAMID_MIN_TARGET is worth it.

### Full 4yr — pyramiding

| floor | pyramids added | blocked by target-room gate |
|---|---|---|
| flat 20 | 17 | 514 |
| flat 30 (shipped) | 18 | 1124 |
| SCALED 20/30 | 19 | 1107 |

### IS 2022-23 — pyramiding

| floor | pyramids added | blocked by target-room gate |
|---|---|---|
| flat 20 | 13 | 207 |
| flat 30 (shipped) | 13 | 372 |
| SCALED 20/30 | 14 | 355 |

### OOS 2024-25 — pyramiding

| floor | pyramids added | blocked by target-room gate |
|---|---|---|
| flat 20 | 4 | 311 |
| flat 30 (shipped) | 5 | 750 |
| SCALED 20/30 | 4 | 656 |

## Verdict

🔴 **Keep flat-30.** Scaled full-4yr equity 563,610,971 vs flat-30 567,575,614 (MaxDD -12.95 vs -12.76, PF 4.95) — doesn't beat the shipped flat-30. Claude reviews IS/OOS before final call (scaled may still win the small-account IS phase — relevant to a live R1k start).
