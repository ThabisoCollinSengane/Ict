# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 504, unique setups 223, simulated 223. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 30 | 63% / 3.28 / +25.1 | 13% / 0.31 / -18.0 | reversal |
| shift>=2 & cont | OOS | 57 | 51% / 2.02 / +28.5 | 16% / 0.38 / -30.0 | reversal |
| shift>=2 & none | OOS | 8 | 50% / 2.00 / +4.0 | 12% / 0.29 / -5.0 | reversal |
| shift>=2 & noref | OOS | 15 | 60% / 3.15 / +11.5 | 0% / 0.00 / -15.0 | reversal |
| shift<2 | OOS | 113 | 56% / 2.42 / +71.0 | 17% / 0.40 / -56.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
