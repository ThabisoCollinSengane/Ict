# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 145, unique setups 72, simulated 72. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 11 | 36% / 1.14 / +1.0 | 9% / 0.20 / -8.0 | reversal |
| shift>=2 & cont | OOS | 17 | 18% / 0.30 / -9.8 | 41% / 1.40 / +4.0 | continuation |
| shift>=2 & none | OOS | 8 | 38% / 0.70 / -1.2 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 3 | 67% / 4.00 / +3.0 | 0% / 0.00 / -3.0 | reversal |
| shift<2 | OOS | 33 | 27% / 0.75 / -6.0 | 33% / 1.00 / +0.0 | continuation |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
