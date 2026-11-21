# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 336, unique setups 178, simulated 178. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 29 | 55% / 2.32 / +17.1 | 17% / 0.42 / -14.0 | reversal |
| shift>=2 & cont | OOS | 48 | 56% / 2.51 / +31.5 | 12% / 0.29 / -30.0 | reversal |
| shift>=2 & none | OOS | 9 | 44% / 1.60 / +3.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | OOS | 76 | 51% / 2.03 / +37.5 | 20% / 0.49 / -31.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
