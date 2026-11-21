# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 359, unique setups 186, simulated 186. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 34 | 59% / 2.72 / +24.1 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & cont | OOS | 48 | 54% / 2.31 / +28.5 | 17% / 0.40 / -24.0 | reversal |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.72 / +14.6 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | OOS | 79 | 51% / 1.93 / +35.7 | 19% / 0.47 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
