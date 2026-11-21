# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 167, unique setups 90, simulated 90. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 16 | 44% / 1.21 / +1.9 | 12% / 0.29 / -10.0 | reversal |
| shift>=2 & cont | OOS | 14 | 21% / 0.55 / -5.0 | 21% / 0.55 / -5.0 | continuation |
| shift>=2 & none | OOS | 6 | 33% / 1.17 / +0.6 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 40 | 52% / 2.08 / +20.5 | 12% / 0.29 / -25.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
