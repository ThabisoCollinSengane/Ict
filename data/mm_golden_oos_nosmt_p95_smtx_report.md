# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 471, unique setups 234, simulated 234. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 38 | 47% / 1.71 / +14.1 | 13% / 0.30 / -23.0 | reversal |
| shift>=2 & cont | OOS | 60 | 50% / 1.96 / +28.5 | 17% / 0.40 / -30.0 | reversal |
| shift>=2 & none | OOS | 12 | 33% / 1.00 / +0.0 | 25% / 0.67 / -3.0 | reversal |
| shift>=2 & noref | OOS | 23 | 52% / 2.25 / +12.5 | 9% / 0.19 / -17.0 | reversal |
| shift<2 | OOS | 101 | 54% / 2.29 / +58.7 | 21% / 0.53 / -38.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
