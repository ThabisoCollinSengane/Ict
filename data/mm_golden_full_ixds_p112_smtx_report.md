# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 834, unique setups 415, simulated 415. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.59 / +30.2 | 9% / 0.20 / -33.0 | reversal |
| shift>=2 & smt | OOS | 32 | 50% / 1.88 / +14.1 | 16% / 0.37 / -17.0 | reversal |
| shift>=2 & cont | IS | 58 | 41% / 1.38 / +12.8 | 16% / 0.37 / -31.0 | reversal |
| shift>=2 & cont | OOS | 57 | 53% / 2.20 / +31.8 | 12% / 0.28 / -36.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 7 | 57% / 2.67 / +5.0 | 29% / 0.80 / -1.0 | reversal |
| shift>=2 & noref | IS | 18 | 61% / 2.87 / +13.1 | 17% / 0.40 / -9.0 | reversal |
| shift>=2 & noref | OOS | 12 | 58% / 2.80 / +9.0 | 8% / 0.18 / -9.0 | reversal |
| shift<2 | IS | 92 | 51% / 2.04 / +46.7 | 13% / 0.30 / -56.0 | reversal |
| shift<2 | OOS | 85 | 55% / 2.40 / +51.4 | 15% / 0.36 / -46.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
