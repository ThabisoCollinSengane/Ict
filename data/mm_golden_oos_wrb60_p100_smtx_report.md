# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 374, unique setups 196, simulated 196. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 35 | 57% / 2.54 / +23.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | OOS | 51 | 51% / 2.06 / +25.9 | 14% / 0.32 / -30.0 | reversal |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.83 / +15.2 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 84 | 50% / 1.93 / +38.5 | 21% / 0.55 / -30.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
