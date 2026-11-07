# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 494, unique setups 261, simulated 261. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 53% / 2.20 / +29.1 | 11% / 0.26 / -35.0 | reversal |
| shift>=2 & cont | IS | 71 | 49% / 1.91 / +32.8 | 20% / 0.49 / -29.0 | reversal |
| shift>=2 & none | IS | 11 | 45% / 1.67 / +4.0 | 45% / 1.67 / +4.0 | continuation |
| shift>=2 & noref | IS | 21 | 57% / 2.47 / +13.3 | 14% / 0.33 / -12.0 | reversal |
| shift<2 | IS | 105 | 46% / 1.66 / +37.6 | 16% / 0.39 / -54.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
