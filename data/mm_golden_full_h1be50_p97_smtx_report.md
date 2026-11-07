# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 907, unique setups 457, simulated 457. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 55 | 49% / 1.89 / +24.1 | 11% / 0.24 / -37.0 | reversal |
| shift>=2 & smt | OOS | 35 | 54% / 2.26 / +20.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | IS | 68 | 46% / 1.64 / +23.8 | 16% / 0.39 / -35.0 | reversal |
| shift>=2 & cont | OOS | 57 | 53% / 2.20 / +31.8 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 9 | 44% / 1.60 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.33 / +14.0 | 12% / 0.29 / -10.0 | reversal |
| shift<2 | IS | 96 | 50% / 1.95 / +45.7 | 14% / 0.31 / -57.0 | reversal |
| shift<2 | OOS | 91 | 52% / 2.06 / +45.4 | 21% / 0.53 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
