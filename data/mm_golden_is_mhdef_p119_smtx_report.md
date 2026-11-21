# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 448, unique setups 260, simulated 260. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 48 | 44% / 1.48 / +13.1 | 12% / 0.29 / -30.0 | reversal |
| shift>=2 & cont | IS | 70 | 44% / 1.56 / +21.8 | 21% / 0.55 / -25.0 | reversal |
| shift>=2 & none | IS | 5 | 80% / 8.00 / +7.0 | 20% / 0.50 / -2.0 | reversal |
| shift>=2 & noref | IS | 31 | 55% / 2.43 / +20.0 | 16% / 0.38 / -16.0 | reversal |
| shift<2 | IS | 106 | 43% / 1.51 / +30.4 | 15% / 0.36 / -58.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
