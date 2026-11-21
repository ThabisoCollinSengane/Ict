# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 596, unique setups 377, simulated 377. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 29 | 59% / 2.83 / +22.0 | 14% / 0.32 / -17.0 | reversal |
| shift>=2 & smt | OOS | 16 | 50% / 2.00 / +8.0 | 12% / 0.29 / -10.0 | reversal |
| shift>=2 & cont | IS | 45 | 49% / 1.86 / +19.8 | 11% / 0.25 / -30.0 | reversal |
| shift>=2 & cont | OOS | 42 | 57% / 2.57 / +28.3 | 17% / 0.40 / -21.0 | reversal |
| shift>=2 & none | IS | 4 | 50% / 2.00 / +2.0 | 50% / 2.00 / +2.0 | continuation |
| shift>=2 & none | OOS | 1 | 0% / 0.00 / -1.0 | 100% / inf / +2.0 | continuation |
| shift>=2 & noref | IS | 6 | 50% / 2.00 / +3.0 | 17% / 0.40 / -3.0 | reversal |
| shift>=2 & noref | OOS | 10 | 60% / 2.73 / +6.9 | 10% / 0.22 / -7.0 | reversal |
| shift<2 | IS | 120 | 50% / 1.98 / +57.8 | 17% / 0.40 / -60.0 | reversal |
| shift<2 | OOS | 104 | 56% / 2.54 / +68.1 | 12% / 0.29 / -65.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
