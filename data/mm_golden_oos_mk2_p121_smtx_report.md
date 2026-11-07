# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 558, unique setups 301, simulated 301. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 56 | 46% / 1.57 / +17.2 | 18% / 0.43 / -26.0 | reversal |
| shift>=2 & cont | OOS | 81 | 40% / 1.35 / +16.6 | 15% / 0.35 / -45.0 | reversal |
| shift>=2 & none | OOS | 18 | 33% / 1.00 / +0.0 | 33% / 1.00 / +0.0 | continuation |
| shift>=2 & noref | OOS | 32 | 44% / 1.66 / +11.1 | 12% / 0.29 / -20.0 | reversal |
| shift<2 | OOS | 114 | 37% / 1.09 / +6.1 | 16% / 0.35 / -62.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
