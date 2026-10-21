# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 847, unique setups 426, simulated 426. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 47 | 57% / 2.56 / +31.2 | 11% / 0.24 / -32.0 | reversal |
| shift>=2 & smt | OOS | 35 | 54% / 2.26 / +20.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | IS | 59 | 42% / 1.44 / +14.8 | 15% / 0.36 / -32.0 | reversal |
| shift>=2 & cont | OOS | 57 | 53% / 2.20 / +31.8 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 7 | 57% / 2.67 / +5.0 | 29% / 0.80 / -1.0 | reversal |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 15% / 0.35 / -11.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 94 | 51% / 2.04 / +47.7 | 13% / 0.29 / -58.0 | reversal |
| shift<2 | OOS | 84 | 55% / 2.34 / +49.4 | 15% / 0.37 / -45.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
