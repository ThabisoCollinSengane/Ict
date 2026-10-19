# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 164, unique setups 88, simulated 88. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 14 | 43% / 1.31 / +2.5 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & cont | OOS | 14 | 29% / 0.80 / -2.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & none | OOS | 7 | 29% / 0.90 / -0.4 | 0% / 0.00 / -7.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 39 | 54% / 2.19 / +21.5 | 15% / 0.36 / -21.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
