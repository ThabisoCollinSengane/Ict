# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 352, unique setups 185, simulated 185. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 27 | 52% / 2.01 / +13.1 | 19% / 0.45 / -12.0 | reversal |
| shift>=2 & cont | OOS | 48 | 54% / 2.31 / +28.5 | 15% / 0.34 / -27.0 | reversal |
| shift>=2 & none | OOS | 10 | 60% / 3.00 / +8.0 | 20% / 0.50 / -4.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | OOS | 84 | 51% / 1.98 / +39.7 | 17% / 0.40 / -42.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
