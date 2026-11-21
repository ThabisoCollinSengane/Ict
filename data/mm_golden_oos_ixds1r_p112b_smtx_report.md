# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 351, unique setups 182, simulated 182. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 31 | 52% / 2.01 / +15.1 | 16% / 0.38 / -16.0 | reversal |
| shift>=2 & cont | OOS | 49 | 55% / 2.40 / +30.5 | 14% / 0.33 / -28.0 | reversal |
| shift>=2 & none | OOS | 9 | 44% / 1.60 / +3.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 16 | 56% / 2.60 / +10.2 | 12% / 0.29 / -10.0 | reversal |
| shift<2 | OOS | 77 | 52% / 2.03 / +37.7 | 16% / 0.37 / -41.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
