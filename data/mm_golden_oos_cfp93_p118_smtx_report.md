# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 115, unique setups 60, simulated 60. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 9 | 33% / 1.16 / +0.8 | 11% / 0.25 / -6.0 | reversal |
| shift>=2 & cont | OOS | 18 | 28% / 0.77 / -3.0 | 22% / 0.57 / -6.0 | reversal |
| shift>=2 & none | OOS | 3 | 33% / 1.00 / +0.0 | 33% / 1.00 / +0.0 | continuation |
| shift>=2 & noref | OOS | 6 | 50% / 2.53 / +3.6 | 17% / 0.40 / -3.0 | reversal |
| shift<2 | OOS | 24 | 62% / 3.02 / +18.2 | 8% / 0.18 / -18.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
