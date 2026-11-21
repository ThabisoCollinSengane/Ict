# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 433, unique setups 269, simulated 269. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 51 | 47% / 1.60 / +16.2 | 18% / 0.43 / -24.0 | reversal |
| shift>=2 & cont | OOS | 72 | 39% / 1.32 / +13.6 | 17% / 0.40 / -36.0 | reversal |
| shift>=2 & none | OOS | 16 | 38% / 1.20 / +2.0 | 31% / 0.91 / -1.0 | reversal |
| shift>=2 & noref | OOS | 29 | 41% / 1.47 / +7.6 | 14% / 0.32 / -17.0 | reversal |
| shift<2 | OOS | 101 | 40% / 1.21 / +12.3 | 14% / 0.30 / -61.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
