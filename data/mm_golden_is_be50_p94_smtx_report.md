# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 487, unique setups 242, simulated 242. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 55 | 49% / 1.89 / +24.1 | 11% / 0.24 / -37.0 | reversal |
| shift>=2 & cont | IS | 66 | 47% / 1.74 / +25.8 | 17% / 0.40 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 17 | 53% / 2.01 / +8.1 | 18% / 0.43 / -8.0 | reversal |
| shift<2 | IS | 95 | 51% / 1.99 / +46.7 | 14% / 0.32 / -56.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
