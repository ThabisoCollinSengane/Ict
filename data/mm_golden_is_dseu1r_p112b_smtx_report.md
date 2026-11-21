# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 457, unique setups 227, simulated 227. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 50 | 48% / 1.80 / +20.1 | 12% / 0.27 / -32.0 | reversal |
| shift>=2 & cont | IS | 63 | 44% / 1.57 / +19.8 | 16% / 0.38 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 19 | 58% / 2.53 / +12.3 | 16% / 0.38 / -10.0 | reversal |
| shift<2 | IS | 86 | 51% / 2.04 / +43.7 | 13% / 0.29 / -53.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
