# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 113, unique setups 71, simulated 71. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 12 | 50% / 1.70 / +4.2 | 25% / 0.67 / -3.0 | reversal |
| shift>=2 & cont | OOS | 20 | 30% / 0.80 / -2.9 | 30% / 0.86 / -2.0 | continuation |
| shift>=2 & none | OOS | 4 | 25% / 0.67 / -1.0 | 75% / 6.00 / +5.0 | continuation |
| shift>=2 & noref | OOS | 10 | 30% / 1.02 / +0.1 | 0% / 0.00 / -10.0 | reversal |
| shift<2 | OOS | 25 | 44% / 1.36 / +4.8 | 8% / 0.17 / -19.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
