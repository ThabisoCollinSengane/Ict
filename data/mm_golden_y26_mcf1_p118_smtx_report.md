# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 138, unique setups 83, simulated 83. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 14 | 43% / 1.50 / +4.0 | 21% / 0.55 / -5.0 | reversal |
| shift>=2 & cont | OOS | 15 | 7% / 0.14 / -12.0 | 27% / 0.73 / -3.0 | continuation |
| shift>=2 & none | OOS | 9 | 67% / 3.64 / +6.4 | 0% / 0.00 / -9.0 | reversal |
| shift>=2 & noref | OOS | 7 | 43% / 1.50 / +2.0 | 0% / 0.00 / -7.0 | reversal |
| shift<2 | OOS | 38 | 37% / 1.09 / +2.3 | 24% / 0.62 / -11.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
