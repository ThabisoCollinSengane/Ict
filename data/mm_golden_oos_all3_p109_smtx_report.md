# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 358, unique setups 189, simulated 189. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 33 | 58% / 2.58 / +22.1 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | OOS | 49 | 55% / 2.40 / +30.5 | 14% / 0.33 / -28.0 | reversal |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.83 / +15.2 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 81 | 51% / 1.93 / +36.7 | 19% / 0.45 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
