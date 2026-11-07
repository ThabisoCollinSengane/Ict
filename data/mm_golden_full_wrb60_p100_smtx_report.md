# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 919, unique setups 469, simulated 469. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 46% / 1.69 / +20.1 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & smt | OOS | 37 | 57% / 2.51 / +24.1 | 14% / 0.31 / -22.0 | reversal |
| shift>=2 & cont | IS | 68 | 47% / 1.74 / +26.8 | 16% / 0.39 / -35.0 | reversal |
| shift>=2 & cont | OOS | 59 | 51% / 2.08 / +30.2 | 14% / 0.31 / -35.0 | reversal |
| shift>=2 & none | IS | 10 | 40% / 1.33 / +2.0 | 50% / 2.00 / +5.0 | continuation |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 102 | 51% / 2.03 / +51.7 | 13% / 0.29 / -63.0 | reversal |
| shift<2 | OOS | 93 | 52% / 2.06 / +46.4 | 20% / 0.51 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
