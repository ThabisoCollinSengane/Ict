# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 486, unique setups 261, simulated 261. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 51 | 45% / 1.47 / +13.2 | 18% / 0.43 / -24.0 | reversal |
| shift>=2 & cont | OOS | 69 | 38% / 1.26 / +10.6 | 14% / 0.34 / -39.0 | reversal |
| shift>=2 & none | OOS | 15 | 27% / 0.73 / -3.0 | 33% / 1.00 / +0.0 | continuation |
| shift>=2 & noref | OOS | 30 | 43% / 1.64 / +10.1 | 10% / 0.22 / -21.0 | reversal |
| shift<2 | OOS | 96 | 35% / 1.04 / +2.5 | 17% / 0.38 / -50.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
