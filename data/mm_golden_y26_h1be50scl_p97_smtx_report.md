# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 164, unique setups 87, simulated 87. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 15 | 40% / 1.16 / +1.5 | 13% / 0.31 / -9.0 | reversal |
| shift>=2 & cont | OOS | 14 | 29% / 0.80 / -2.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & none | OOS | 7 | 29% / 0.90 / -0.4 | 0% / 0.00 / -7.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 37 | 54% / 2.20 / +20.5 | 14% / 0.31 / -22.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
