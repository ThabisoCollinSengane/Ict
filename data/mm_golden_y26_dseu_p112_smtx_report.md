# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 162, unique setups 86, simulated 86. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 13 | 38% / 1.06 / +0.5 | 15% / 0.36 / -7.0 | reversal |
| shift>=2 & cont | OOS | 14 | 29% / 0.80 / -2.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & none | OOS | 6 | 17% / 0.45 / -2.4 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 39 | 51% / 1.97 / +18.5 | 15% / 0.36 / -21.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
