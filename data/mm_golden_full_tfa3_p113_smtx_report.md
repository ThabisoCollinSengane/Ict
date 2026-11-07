# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 962, unique setups 463, simulated 463. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 59 | 49% / 1.89 / +26.1 | 10% / 0.23 / -41.0 | reversal |
| shift>=2 & smt | OOS | 34 | 56% / 2.41 / +21.1 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & cont | IS | 70 | 49% / 1.86 / +30.8 | 16% / 0.37 / -37.0 | reversal |
| shift>=2 & cont | OOS | 57 | 49% / 1.94 / +26.2 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 9 | 44% / 1.60 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 14 | 57% / 2.67 / +10.0 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | IS | 98 | 50% / 1.95 / +46.7 | 13% / 0.31 / -59.0 | reversal |
| shift<2 | OOS | 92 | 53% / 2.21 / +50.4 | 18% / 0.45 / -41.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
