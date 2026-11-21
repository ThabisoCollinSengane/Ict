# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 416, unique setups 206, simulated 206. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 35 | 54% / 2.26 / +20.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | OOS | 52 | 54% / 2.28 / +30.5 | 15% / 0.36 / -28.0 | reversal |
| shift>=2 & none | OOS | 13 | 46% / 1.71 / +5.0 | 23% / 0.60 / -4.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.63 / +14.1 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 89 | 51% / 1.94 / +40.7 | 18% / 0.44 / -41.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
