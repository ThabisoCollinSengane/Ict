# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 162, unique setups 83, simulated 83. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 21 | 29% / 0.72 / -3.9 | 29% / 0.80 / -3.0 | continuation |
| shift>=2 & cont | OOS | 21 | 19% / 0.49 / -8.2 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & none | OOS | 5 | 20% / 0.50 / -2.0 | 40% / 1.33 / +1.0 | continuation |
| shift>=2 & noref | OOS | 9 | 44% / 1.83 / +3.6 | 11% / 0.25 / -6.0 | reversal |
| shift<2 | OOS | 27 | 44% / 1.41 / +6.2 | 30% / 0.74 / -5.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
