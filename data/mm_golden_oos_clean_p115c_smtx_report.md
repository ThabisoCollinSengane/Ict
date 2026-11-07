# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 186, unique setups 104, simulated 104. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 17 | 35% / 0.93 / -0.8 | 18% / 0.43 / -8.0 | reversal |
| shift>=2 & cont | OOS | 29 | 31% / 0.94 / -1.2 | 10% / 0.23 / -20.0 | reversal |
| shift>=2 & none | OOS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | OOS | 10 | 30% / 0.94 / -0.4 | 0% / 0.00 / -10.0 | reversal |
| shift<2 | OOS | 42 | 43% / 1.33 / +8.0 | 19% / 0.41 / -20.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
