# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 883, unique setups 447, simulated 447. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 54 | 52% / 2.12 / +28.1 | 9% / 0.20 / -39.0 | reversal |
| shift>=2 & smt | OOS | 37 | 57% / 2.51 / +24.1 | 14% / 0.31 / -22.0 | reversal |
| shift>=2 & cont | IS | 64 | 45% / 1.62 / +21.8 | 16% / 0.37 / -34.0 | reversal |
| shift>=2 & cont | OOS | 57 | 54% / 2.37 / +34.8 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 15% / 0.35 / -11.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 94 | 52% / 2.13 / +50.7 | 13% / 0.29 / -58.0 | reversal |
| shift<2 | OOS | 90 | 51% / 2.01 / +43.4 | 19% / 0.47 / -39.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
