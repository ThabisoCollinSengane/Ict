# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 415, unique setups 206, simulated 206. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 29 | 62% / 3.10 / +23.1 | 14% / 0.32 / -17.0 | reversal |
| shift>=2 & cont | OOS | 52 | 54% / 2.28 / +30.5 | 17% / 0.42 / -25.0 | reversal |
| shift>=2 & none | OOS | 4 | 25% / 0.67 / -1.0 | 25% / 0.67 / -1.0 | continuation |
| shift>=2 & noref | OOS | 13 | 46% / 1.88 / +5.6 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | OOS | 108 | 57% / 2.55 / +71.1 | 17% / 0.40 / -54.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
