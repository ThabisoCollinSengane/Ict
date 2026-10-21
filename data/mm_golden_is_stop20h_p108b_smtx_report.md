# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 467, unique setups 244, simulated 244. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 52 | 52% / 2.12 / +27.1 | 10% / 0.21 / -37.0 | reversal |
| shift>=2 & cont | IS | 64 | 47% / 1.73 / +24.8 | 14% / 0.33 / -37.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift<2 | IS | 98 | 50% / 1.95 / +46.7 | 13% / 0.31 / -59.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
