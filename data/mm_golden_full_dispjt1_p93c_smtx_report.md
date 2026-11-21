# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 914, unique setups 460, simulated 460. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 48% / 1.82 / +23.1 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & smt | OOS | 36 | 56% / 2.38 / +22.1 | 14% / 0.32 / -21.0 | reversal |
| shift>=2 & cont | IS | 68 | 46% / 1.64 / +23.8 | 16% / 0.39 / -35.0 | reversal |
| shift>=2 & cont | OOS | 57 | 53% / 2.20 / +31.8 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 97 | 51% / 1.99 / +47.7 | 13% / 0.31 / -58.0 | reversal |
| shift<2 | OOS | 93 | 51% / 1.97 / +43.4 | 20% / 0.51 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
