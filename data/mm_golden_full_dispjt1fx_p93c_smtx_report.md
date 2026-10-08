# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 905, unique setups 459, simulated 459. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 48% / 1.82 / +23.1 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & smt | OOS | 35 | 54% / 2.26 / +20.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | IS | 67 | 46% / 1.69 / +24.8 | 15% / 0.35 / -37.0 | reversal |
| shift>=2 & cont | OOS | 57 | 53% / 2.20 / +31.8 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 9 | 44% / 1.60 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.33 / +14.0 | 12% / 0.29 / -10.0 | reversal |
| shift<2 | IS | 98 | 51% / 2.04 / +49.7 | 13% / 0.31 / -59.0 | reversal |
| shift<2 | OOS | 91 | 52% / 2.06 / +45.4 | 21% / 0.53 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
