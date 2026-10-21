# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 557, unique setups 257, simulated 257. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 60 | 52% / 2.10 / +31.1 | 13% / 0.31 / -36.0 | reversal |
| shift>=2 & cont | IS | 63 | 49% / 1.90 / +28.8 | 14% / 0.33 / -36.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 25 | 64% / 3.36 / +21.3 | 12% / 0.27 / -16.0 | reversal |
| shift<2 | IS | 100 | 51% / 2.04 / +50.7 | 12% / 0.27 / -64.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
