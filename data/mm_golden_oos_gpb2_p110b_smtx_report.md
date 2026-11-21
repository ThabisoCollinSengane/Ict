# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 310, unique setups 165, simulated 165. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 29 | 55% / 2.32 / +17.1 | 17% / 0.42 / -14.0 | reversal |
| shift>=2 & cont | OOS | 42 | 57% / 2.57 / +28.3 | 17% / 0.40 / -21.0 | reversal |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 13 | 46% / 1.88 / +5.6 | 15% / 0.36 / -7.0 | reversal |
| shift<2 | OOS | 73 | 53% / 2.23 / +41.8 | 16% / 0.39 / -37.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
