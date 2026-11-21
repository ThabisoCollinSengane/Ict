# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 121, unique setups 69, simulated 69. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 11 | 55% / 2.04 / +5.2 | 27% / 0.75 / -2.0 | reversal |
| shift>=2 & cont | OOS | 17 | 29% / 0.83 / -2.0 | 29% / 0.83 / -2.0 | continuation |
| shift>=2 & none | OOS | 7 | 57% / 2.67 / +5.0 | 43% / 1.50 / +2.0 | reversal |
| shift>=2 & noref | OOS | 8 | 38% / 1.55 / +2.1 | 0% / 0.00 / -8.0 | reversal |
| shift<2 | OOS | 26 | 46% / 1.60 / +7.9 | 12% / 0.26 / -17.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
