# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 148, unique setups 81, simulated 81. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 14 | 36% / 1.11 / +1.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & cont | OOS | 14 | 29% / 0.80 / -2.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & none | OOS | 6 | 33% / 1.17 / +0.6 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | OOS | 13 | 46% / 1.98 / +5.9 | 15% / 0.36 / -7.0 | reversal |
| shift<2 | OOS | 34 | 56% / 2.37 / +20.5 | 12% / 0.27 / -22.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
