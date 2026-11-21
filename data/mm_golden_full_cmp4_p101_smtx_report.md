# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 869, unique setups 443, simulated 443. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 53% / 2.20 / +29.1 | 9% / 0.21 / -38.0 | reversal |
| shift>=2 & smt | OOS | 36 | 56% / 2.38 / +22.1 | 14% / 0.32 / -21.0 | reversal |
| shift>=2 & cont | IS | 64 | 45% / 1.62 / +21.8 | 17% / 0.42 / -31.0 | reversal |
| shift>=2 & cont | OOS | 56 | 54% / 2.29 / +32.8 | 14% / 0.33 / -32.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 9 | 67% / 4.00 / +9.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 10% / 0.22 / -14.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 89 | 49% / 1.91 / +40.7 | 10% / 0.23 / -62.0 | reversal |
| shift<2 | OOS | 93 | 51% / 1.97 / +43.4 | 20% / 0.51 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
