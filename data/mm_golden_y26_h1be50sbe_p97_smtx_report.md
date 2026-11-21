# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 148, unique setups 79, simulated 79. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 12 | 42% / 1.43 / +3.0 | 8% / 0.18 / -9.0 | reversal |
| shift>=2 & cont | OOS | 13 | 23% / 0.60 / -4.0 | 15% / 0.36 / -7.0 | reversal |
| shift>=2 & none | OOS | 7 | 29% / 0.90 / -0.4 | 0% / 0.00 / -7.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 33 | 55% / 2.23 / +18.5 | 12% / 0.28 / -21.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
