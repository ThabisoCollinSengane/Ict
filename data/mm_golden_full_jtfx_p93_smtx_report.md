# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 974, unique setups 478, simulated 478. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 53% / 2.19 / +29.7 | 11% / 0.26 / -35.0 | reversal |
| shift>=2 & smt | OOS | 30 | 60% / 2.84 / +22.1 | 13% / 0.31 / -18.0 | reversal |
| shift>=2 & cont | IS | 64 | 50% / 1.96 / +30.8 | 16% / 0.37 / -34.0 | reversal |
| shift>=2 & cont | OOS | 56 | 54% / 2.26 / +32.5 | 16% / 0.38 / -29.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 57% / 2.67 / +5.0 | continuation |
| shift>=2 & none | OOS | 3 | 33% / 1.00 / +0.0 | 33% / 1.00 / +0.0 | continuation |
| shift>=2 & noref | IS | 15 | 67% / 3.61 / +13.1 | 7% / 0.14 / -12.0 | reversal |
| shift>=2 & noref | OOS | 12 | 50% / 2.00 / +6.0 | 8% / 0.18 / -9.0 | reversal |
| shift<2 | IS | 123 | 53% / 2.22 / +69.8 | 14% / 0.32 / -72.0 | reversal |
| shift<2 | OOS | 115 | 57% / 2.55 / +74.8 | 17% / 0.42 / -55.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
