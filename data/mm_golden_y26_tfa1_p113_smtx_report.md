# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 153, unique setups 82, simulated 82. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 12 | 42% / 1.43 / +3.0 | 8% / 0.18 / -9.0 | reversal |
| shift>=2 & cont | OOS | 13 | 23% / 0.60 / -4.0 | 15% / 0.36 / -7.0 | reversal |
| shift>=2 & none | OOS | 8 | 38% / 1.04 / +0.2 | 0% / 0.00 / -8.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 35 | 51% / 1.97 / +16.5 | 14% / 0.33 / -20.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
