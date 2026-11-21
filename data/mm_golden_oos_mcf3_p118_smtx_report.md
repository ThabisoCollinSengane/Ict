# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 439, unique setups 273, simulated 273. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 54 | 44% / 1.44 / +13.2 | 20% / 0.51 / -21.0 | reversal |
| shift>=2 & cont | OOS | 75 | 40% / 1.38 / +16.6 | 16% / 0.38 / -39.0 | reversal |
| shift>=2 & none | OOS | 16 | 38% / 1.20 / +2.0 | 31% / 0.91 / -1.0 | reversal |
| shift>=2 & noref | OOS | 28 | 43% / 1.49 / +7.5 | 11% / 0.24 / -19.0 | reversal |
| shift<2 | OOS | 100 | 40% / 1.23 / +13.3 | 14% / 0.30 / -60.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
