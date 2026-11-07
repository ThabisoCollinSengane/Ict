# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 410, unique setups 207, simulated 207. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.59 / +30.2 | 11% / 0.25 / -30.0 | reversal |
| shift>=2 & cont | IS | 56 | 45% / 1.57 / +17.8 | 14% / 0.33 / -32.0 | reversal |
| shift>=2 & none | IS | 7 | 43% / 1.50 / +2.0 | 43% / 1.50 / +2.0 | continuation |
| shift>=2 & noref | IS | 18 | 61% / 2.90 / +13.3 | 11% / 0.25 / -12.0 | reversal |
| shift<2 | IS | 81 | 48% / 1.80 / +33.7 | 14% / 0.31 / -48.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
