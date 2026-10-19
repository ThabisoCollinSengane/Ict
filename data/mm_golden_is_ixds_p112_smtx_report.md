# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 456, unique setups 222, simulated 222. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.59 / +30.2 | 9% / 0.20 / -33.0 | reversal |
| shift>=2 & cont | IS | 58 | 41% / 1.38 / +12.8 | 16% / 0.37 / -31.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 18 | 61% / 2.87 / +13.1 | 17% / 0.40 / -9.0 | reversal |
| shift<2 | IS | 92 | 51% / 2.04 / +46.7 | 13% / 0.30 / -56.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
