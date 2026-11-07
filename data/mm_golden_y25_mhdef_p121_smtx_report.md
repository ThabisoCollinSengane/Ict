# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 206, unique setups 133, simulated 133. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 30 | 43% / 1.47 / +7.9 | 27% / 0.73 / -6.0 | reversal |
| shift>=2 & cont | OOS | 38 | 55% / 2.47 / +25.0 | 13% / 0.30 / -23.0 | reversal |
| shift>=2 & none | OOS | 7 | 43% / 1.50 / +2.0 | 43% / 1.50 / +2.0 | continuation |
| shift>=2 & noref | OOS | 15 | 53% / 2.29 / +9.0 | 27% / 0.73 / -3.0 | reversal |
| shift<2 | OOS | 43 | 42% / 1.29 / +6.7 | 12% / 0.26 / -28.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
