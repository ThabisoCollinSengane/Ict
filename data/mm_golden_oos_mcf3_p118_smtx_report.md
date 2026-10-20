# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 439, unique setups 275, simulated 275. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 54 | 44% / 1.44 / +13.2 | 19% / 0.45 / -24.0 | reversal |
| shift>=2 & cont | OOS | 73 | 40% / 1.37 / +15.6 | 16% / 0.39 / -37.0 | reversal |
| shift>=2 & none | OOS | 16 | 38% / 1.20 / +2.0 | 31% / 0.91 / -1.0 | reversal |
| shift>=2 & noref | OOS | 29 | 45% / 1.62 / +9.5 | 10% / 0.23 / -20.0 | reversal |
| shift<2 | OOS | 103 | 39% / 1.17 / +10.3 | 15% / 0.32 / -60.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
