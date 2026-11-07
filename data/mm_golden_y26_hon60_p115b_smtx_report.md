# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 127, unique setups 68, simulated 68. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 15 | 53% / 2.29 / +9.0 | 7% / 0.14 / -12.0 | reversal |
| shift>=2 & cont | OOS | 15 | 20% / 0.50 / -6.0 | 27% / 0.73 / -3.0 | continuation |
| shift>=2 & none | OOS | 5 | 20% / 0.58 / -1.4 | 0% / 0.00 / -5.0 | reversal |
| shift>=2 & noref | OOS | 7 | 71% / 5.00 / +8.0 | 0% / 0.00 / -7.0 | reversal |
| shift<2 | OOS | 26 | 50% / 1.81 / +10.5 | 19% / 0.48 / -11.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
