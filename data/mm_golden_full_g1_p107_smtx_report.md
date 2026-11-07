# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 791, unique setups 406, simulated 406. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.59 / +30.2 | 11% / 0.25 / -30.0 | reversal |
| shift>=2 & smt | OOS | 36 | 58% / 2.67 / +25.1 | 14% / 0.32 / -21.0 | reversal |
| shift>=2 & cont | IS | 56 | 45% / 1.57 / +17.8 | 14% / 0.33 / -32.0 | reversal |
| shift>=2 & cont | OOS | 54 | 54% / 2.30 / +31.8 | 13% / 0.30 / -33.0 | reversal |
| shift>=2 & none | IS | 7 | 43% / 1.50 / +2.0 | 43% / 1.50 / +2.0 | continuation |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 18 | 61% / 2.90 / +13.3 | 11% / 0.25 / -12.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 81 | 48% / 1.80 / +33.7 | 14% / 0.31 / -48.0 | reversal |
| shift<2 | OOS | 87 | 51% / 1.97 / +40.4 | 21% / 0.52 / -33.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
