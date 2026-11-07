# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 364, unique setups 189, simulated 189. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 31 | 55% / 2.29 / +18.1 | 13% / 0.30 / -19.0 | reversal |
| shift>=2 & cont | OOS | 49 | 51% / 2.03 / +24.5 | 16% / 0.39 / -25.0 | reversal |
| shift>=2 & none | OOS | 8 | 50% / 2.00 / +4.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | OOS | 85 | 52% / 2.03 / +41.7 | 18% / 0.43 / -40.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
