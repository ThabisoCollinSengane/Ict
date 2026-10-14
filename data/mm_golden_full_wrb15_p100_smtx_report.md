# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 907, unique setups 462, simulated 462. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 55 | 47% / 1.75 / +21.1 | 13% / 0.29 / -34.0 | reversal |
| shift>=2 & smt | OOS | 38 | 53% / 2.12 / +20.1 | 16% / 0.38 / -20.0 | reversal |
| shift>=2 & cont | IS | 69 | 48% / 1.80 / +28.8 | 16% / 0.38 / -36.0 | reversal |
| shift>=2 & cont | OOS | 58 | 52% / 2.16 / +31.2 | 14% / 0.32 / -34.0 | reversal |
| shift>=2 & none | IS | 10 | 30% / 0.86 / -1.0 | 60% / 3.00 / +8.0 | continuation |
| shift>=2 & none | OOS | 8 | 50% / 2.00 / +4.0 | 38% / 1.20 / +1.0 | reversal |
| shift>=2 & noref | IS | 19 | 63% / 3.15 / +15.1 | 11% / 0.24 / -13.0 | reversal |
| shift>=2 & noref | OOS | 15 | 60% / 3.00 / +12.0 | 13% / 0.31 / -9.0 | reversal |
| shift<2 | IS | 100 | 51% / 2.04 / +50.7 | 13% / 0.30 / -61.0 | reversal |
| shift<2 | OOS | 90 | 52% / 2.15 / +48.2 | 18% / 0.43 / -42.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
