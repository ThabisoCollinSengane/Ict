# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 156, unique setups 89, simulated 89. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 15 | 40% / 1.33 / +3.0 | 27% / 0.73 / -3.0 | reversal |
| shift>=2 & cont | OOS | 16 | 6% / 0.13 / -13.0 | 25% / 0.67 / -4.0 | continuation |
| shift>=2 & none | OOS | 11 | 55% / 2.00 / +4.4 | 0% / 0.00 / -11.0 | reversal |
| shift>=2 & noref | OOS | 7 | 43% / 1.50 / +2.0 | 0% / 0.00 / -7.0 | reversal |
| shift<2 | OOS | 40 | 40% / 1.20 / +4.7 | 22% / 0.58 / -13.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
