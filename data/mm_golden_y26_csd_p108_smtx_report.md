# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 165, unique setups 85, simulated 85. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 13 | 46% / 1.50 / +3.5 | 8% / 0.17 / -10.0 | reversal |
| shift>=2 & cont | OOS | 14 | 29% / 0.80 / -2.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & none | OOS | 7 | 29% / 0.90 / -0.4 | 0% / 0.00 / -7.0 | reversal |
| shift>=2 & noref | OOS | 12 | 50% / 2.37 / +6.9 | 17% / 0.40 / -6.0 | reversal |
| shift<2 | OOS | 39 | 51% / 1.97 / +18.5 | 15% / 0.36 / -21.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
