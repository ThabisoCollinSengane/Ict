# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 882, unique setups 443, simulated 443. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 55 | 51% / 2.04 / +27.1 | 9% / 0.20 / -40.0 | reversal |
| shift>=2 & smt | OOS | 35 | 54% / 2.26 / +20.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | IS | 64 | 45% / 1.62 / +21.8 | 17% / 0.42 / -31.0 | reversal |
| shift>=2 & cont | OOS | 57 | 53% / 2.20 / +31.8 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.47 / +13.3 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 90 | 51% / 2.04 / +45.7 | 10% / 0.22 / -63.0 | reversal |
| shift<2 | OOS | 89 | 53% / 2.16 / +47.4 | 19% / 0.47 / -38.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
