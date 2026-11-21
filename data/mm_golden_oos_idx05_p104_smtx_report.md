# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 365, unique setups 191, simulated 191. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 34 | 56% / 2.41 / +21.1 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & cont | OOS | 50 | 52% / 2.11 / +26.5 | 16% / 0.38 / -26.0 | reversal |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 0% / 0.00 / -16.0 | reversal |
| shift<2 | OOS | 82 | 52% / 2.08 / +41.7 | 18% / 0.45 / -37.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
