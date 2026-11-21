# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 460, unique setups 235, simulated 235. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 53% / 2.20 / +29.1 | 9% / 0.21 / -38.0 | reversal |
| shift>=2 & cont | IS | 64 | 45% / 1.62 / +21.8 | 17% / 0.42 / -31.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 10% / 0.22 / -14.0 | reversal |
| shift<2 | IS | 89 | 49% / 1.91 / +40.7 | 10% / 0.23 / -62.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
