# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 390, unique setups 211, simulated 211. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 48 | 40% / 1.25 / +7.2 | 23% / 0.59 / -15.0 | reversal |
| shift>=2 & cont | OOS | 54 | 46% / 1.71 / +20.0 | 17% / 0.40 / -27.0 | reversal |
| shift>=2 & none | OOS | 14 | 29% / 0.80 / -2.0 | 29% / 0.80 / -2.0 | continuation |
| shift>=2 & noref | OOS | 24 | 50% / 2.21 / +13.1 | 8% / 0.18 / -18.0 | reversal |
| shift<2 | OOS | 71 | 45% / 1.52 / +19.7 | 17% / 0.41 / -35.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
