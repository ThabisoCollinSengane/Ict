# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 164, unique setups 88, simulated 88. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 18 | 44% / 1.45 / +4.5 | 17% / 0.40 / -9.0 | reversal |
| shift>=2 & cont | OOS | 14 | 29% / 0.80 / -2.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & none | OOS | 7 | 29% / 0.90 / -0.4 | 0% / 0.00 / -7.0 | reversal |
| shift>=2 & noref | OOS | 11 | 55% / 2.95 / +7.9 | 18% / 0.44 / -5.0 | reversal |
| shift<2 | OOS | 38 | 47% / 1.67 / +13.5 | 16% / 0.38 / -20.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
