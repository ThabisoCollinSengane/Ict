# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 891, unique setups 448, simulated 448. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 50% / 1.96 / +26.1 | 11% / 0.24 / -38.0 | reversal |
| shift>=2 & smt | OOS | 36 | 56% / 2.38 / +22.1 | 14% / 0.32 / -21.0 | reversal |
| shift>=2 & cont | IS | 64 | 45% / 1.62 / +21.8 | 17% / 0.42 / -31.0 | reversal |
| shift>=2 & cont | OOS | 56 | 54% / 2.29 / +32.8 | 14% / 0.33 / -32.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 13 | 62% / 3.20 / +11.0 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | IS | 91 | 51% / 1.99 / +44.7 | 10% / 0.22 / -64.0 | reversal |
| shift<2 | OOS | 92 | 50% / 1.92 / +41.4 | 21% / 0.52 / -35.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
