# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 378, unique setups 212, simulated 212. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 32 | 47% / 1.62 / +10.5 | 19% / 0.46 / -14.0 | reversal |
| shift>=2 & cont | OOS | 59 | 46% / 1.66 / +20.9 | 15% / 0.36 / -32.0 | reversal |
| shift>=2 & none | OOS | 9 | 44% / 1.60 / +3.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 25 | 52% / 2.29 / +14.6 | 16% / 0.38 / -13.0 | reversal |
| shift<2 | OOS | 87 | 52% / 2.05 / +43.4 | 17% / 0.42 / -42.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
