# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 974, unique setups 475, simulated 475. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 49 | 55% / 2.40 / +30.7 | 10% / 0.23 / -34.0 | reversal |
| shift>=2 & smt | OOS | 30 | 60% / 2.84 / +22.1 | 13% / 0.31 / -18.0 | reversal |
| shift>=2 & cont | IS | 66 | 48% / 1.85 / +28.8 | 17% / 0.40 / -33.0 | reversal |
| shift>=2 & cont | OOS | 58 | 53% / 2.25 / +33.5 | 16% / 0.37 / -31.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 57% / 2.67 / +5.0 | continuation |
| shift>=2 & none | OOS | 4 | 50% / 2.00 / +2.0 | 0% / 0.00 / -4.0 | reversal |
| shift>=2 & noref | IS | 16 | 69% / 4.01 / +15.1 | 6% / 0.13 / -13.0 | reversal |
| shift>=2 & noref | OOS | 12 | 50% / 2.00 / +6.0 | 8% / 0.18 / -9.0 | reversal |
| shift<2 | IS | 119 | 54% / 2.31 / +70.8 | 14% / 0.33 / -68.0 | reversal |
| shift<2 | OOS | 114 | 58% / 2.70 / +78.8 | 18% / 0.43 / -54.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
