# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 871, unique setups 441, simulated 441. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 49 | 53% / 2.14 / +26.2 | 14% / 0.33 / -28.0 | reversal |
| shift>=2 & smt | OOS | 36 | 56% / 2.38 / +22.1 | 14% / 0.32 / -21.0 | reversal |
| shift>=2 & cont | IS | 64 | 45% / 1.62 / +21.8 | 16% / 0.37 / -34.0 | reversal |
| shift>=2 & cont | OOS | 56 | 54% / 2.29 / +32.8 | 14% / 0.33 / -32.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 18 | 61% / 2.87 / +13.1 | 11% / 0.25 / -12.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 97 | 52% / 2.08 / +50.7 | 13% / 0.31 / -58.0 | reversal |
| shift<2 | OOS | 90 | 51% / 2.01 / +43.4 | 21% / 0.54 / -33.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
