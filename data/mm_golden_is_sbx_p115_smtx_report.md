# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 487, unique setups 244, simulated 244. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 54 | 50% / 1.96 / +25.1 | 9% / 0.20 / -39.0 | reversal |
| shift>=2 & cont | IS | 65 | 45% / 1.58 / +20.8 | 15% / 0.36 / -35.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift<2 | IS | 95 | 51% / 1.99 / +46.7 | 14% / 0.32 / -56.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
