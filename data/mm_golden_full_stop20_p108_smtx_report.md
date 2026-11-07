# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 989, unique setups 468, simulated 468. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 60 | 52% / 2.10 / +31.1 | 13% / 0.31 / -36.0 | reversal |
| shift>=2 & smt | OOS | 34 | 53% / 2.25 / +20.0 | 12% / 0.27 / -22.0 | reversal |
| shift>=2 & cont | IS | 63 | 49% / 1.90 / +28.8 | 14% / 0.33 / -36.0 | reversal |
| shift>=2 & cont | OOS | 58 | 52% / 2.16 / +31.2 | 14% / 0.32 / -34.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 11 | 45% / 1.67 / +4.0 | 27% / 0.75 / -2.0 | reversal |
| shift>=2 & noref | IS | 25 | 64% / 3.36 / +21.3 | 12% / 0.27 / -16.0 | reversal |
| shift>=2 & noref | OOS | 15 | 67% / 3.78 / +13.9 | 7% / 0.14 / -12.0 | reversal |
| shift<2 | IS | 100 | 51% / 2.04 / +50.7 | 12% / 0.27 / -64.0 | reversal |
| shift<2 | OOS | 93 | 48% / 1.80 / +37.5 | 22% / 0.55 / -33.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
