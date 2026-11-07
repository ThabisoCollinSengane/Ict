# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 482, unique setups 241, simulated 241. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 50% / 1.96 / +26.1 | 11% / 0.24 / -38.0 | reversal |
| shift>=2 & cont | IS | 65 | 45% / 1.58 / +20.8 | 17% / 0.41 / -32.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 21 | 57% / 2.47 / +13.3 | 14% / 0.33 / -12.0 | reversal |
| shift<2 | IS | 90 | 51% / 2.04 / +45.7 | 10% / 0.22 / -63.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
