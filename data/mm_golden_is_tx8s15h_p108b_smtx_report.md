# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 462, unique setups 240, simulated 240. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 49% / 1.88 / +23.1 | 9% / 0.21 / -38.0 | reversal |
| shift>=2 & cont | IS | 60 | 47% / 1.71 / +22.8 | 13% / 0.31 / -36.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift<2 | IS | 98 | 51% / 2.04 / +49.7 | 13% / 0.31 / -59.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
