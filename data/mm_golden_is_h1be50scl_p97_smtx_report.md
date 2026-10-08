# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 501, unique setups 249, simulated 249. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 55 | 49% / 1.89 / +24.1 | 13% / 0.29 / -34.0 | reversal |
| shift>=2 & cont | IS | 67 | 46% / 1.69 / +24.8 | 16% / 0.39 / -34.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 19 | 53% / 2.01 / +9.1 | 16% / 0.38 / -10.0 | reversal |
| shift<2 | IS | 99 | 52% / 2.08 / +51.7 | 13% / 0.30 / -60.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
