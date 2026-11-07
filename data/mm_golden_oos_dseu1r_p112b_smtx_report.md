# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 369, unique setups 190, simulated 190. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 31 | 61% / 3.01 / +24.1 | 13% / 0.30 / -19.0 | reversal |
| shift>=2 & cont | OOS | 51 | 55% / 2.38 / +31.5 | 14% / 0.32 / -30.0 | reversal |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 0% / 0.00 / -16.0 | reversal |
| shift<2 | OOS | 83 | 48% / 1.75 / +31.7 | 22% / 0.55 / -29.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
