# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 552, unique setups 259, simulated 259. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 58 | 50% / 1.96 / +27.1 | 12% / 0.27 / -37.0 | reversal |
| shift>=2 & cont | IS | 65 | 48% / 1.79 / +26.8 | 14% / 0.32 / -38.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 26 | 62% / 3.03 / +20.3 | 15% / 0.36 / -14.0 | reversal |
| shift<2 | IS | 101 | 49% / 1.84 / +43.7 | 13% / 0.30 / -62.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
