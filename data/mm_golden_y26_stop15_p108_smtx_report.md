# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 151, unique setups 79, simulated 79. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 11 | 45% / 1.41 / +2.5 | 9% / 0.20 / -8.0 | reversal |
| shift>=2 & cont | OOS | 13 | 23% / 0.60 / -4.0 | 15% / 0.36 / -7.0 | reversal |
| shift>=2 & none | OOS | 8 | 38% / 1.04 / +0.2 | 0% / 0.00 / -8.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 33 | 48% / 1.73 / +12.5 | 18% / 0.44 / -15.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
