# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 89, unique setups 55, simulated 55. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 10 | 40% / 1.33 / +2.0 | 20% / 0.50 / -4.0 | reversal |
| shift>=2 & cont | OOS | 8 | 0% / 0.00 / -8.0 | 12% / 0.29 / -5.0 | continuation |
| shift>=2 & none | OOS | 6 | 17% / 0.45 / -2.4 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | OOS | 5 | 40% / 1.33 / +1.0 | 0% / 0.00 / -5.0 | reversal |
| shift<2 | OOS | 26 | 31% / 0.78 / -4.0 | 27% / 0.74 / -5.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
