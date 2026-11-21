# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 365, unique setups 186, simulated 186. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 43 | 58% / 2.62 / +29.2 | 9% / 0.21 / -31.0 | reversal |
| shift>=2 & cont | IS | 43 | 51% / 2.04 / +21.8 | 14% / 0.32 / -25.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 18 | 56% / 2.35 / +10.8 | 11% / 0.25 / -12.0 | reversal |
| shift<2 | IS | 73 | 51% / 1.99 / +35.7 | 15% / 0.35 / -40.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
