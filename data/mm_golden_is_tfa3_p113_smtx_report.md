# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 489, unique setups 243, simulated 243. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 46% / 1.69 / +20.1 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & cont | IS | 66 | 48% / 1.85 / +28.8 | 15% / 0.36 / -36.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 18 | 56% / 2.26 / +10.1 | 17% / 0.40 / -9.0 | reversal |
| shift<2 | IS | 94 | 50% / 1.95 / +44.7 | 14% / 0.32 / -55.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
