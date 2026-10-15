# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 377, unique setups 194, simulated 194. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 33 | 55% / 2.27 / +19.1 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | OOS | 51 | 53% / 2.20 / +28.5 | 16% / 0.37 / -27.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 0% / 0.00 / -16.0 | reversal |
| shift<2 | OOS | 84 | 52% / 2.08 / +42.7 | 19% / 0.47 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
