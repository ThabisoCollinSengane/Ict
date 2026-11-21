# Minimum-target floor — 20 vs 25 vs 30 pips

Raising the floor forces further targets: higher reward:risk per trade but a lower hit-rate. **Ship a new floor only if full-4yr equity is up and MaxDD is not worse, both IS/OOS splits still positive.**

_run commit: `79d0228`_

## Full 4yr

| floor | trades | WR | PF | MaxDD | equity ZAR |
|---|---|---|---|---|---|
| 20 pips | 810.00 | 45.90% | 4.46 | -12.95% | 675,623,325 |
| 25 pips | 805.00 | 44.80% | 4.71 | -12.66% | 475,019,140 |
| 30 pips | 804.00 | 44.90% | 4.95 | -12.76% | 567,575,614 |

## IS 2022-23

| floor | trades | WR | PF | MaxDD | equity ZAR |
|---|---|---|---|---|---|
| 20 pips | 389.00 | 45.80% | 3.04 | -12.95% | 343,444 |
| 25 pips | 386.00 | 45.10% | 2.98 | -12.66% | 292,775 |
| 30 pips | 389.00 | 44.70% | 2.88 | -12.76% | 273,481 |

## OOS 2024-25

| floor | trades | WR | PF | MaxDD | equity ZAR |
|---|---|---|---|---|---|
| 20 pips | 417.00 | 45.80% | 4.46 | -15.41% | 2,012,439 |
| 25 pips | 412.00 | 44.90% | 4.71 | -15.86% | 1,753,199 |
| 30 pips | 409.00 | 45.00% | 4.95 | -12.55% | 2,241,887 |

## Verdict (full-4yr vs 20-pip baseline)

- **25 pips: 🔴 no** — equity 475,019,140 vs 675,623,325, MaxDD -12.66 vs -12.95, PF 4.71
- **30 pips: 🔴 no** — equity 567,575,614 vs 675,623,325, MaxDD -12.76 vs -12.95, PF 4.95

_Claude reviews IS/OOS magnitudes before shipping — a full-run gain that regresses either split is not shipped (the not-curve-fit rule)._
