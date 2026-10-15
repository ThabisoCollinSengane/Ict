# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 459, unique setups 240, simulated 240. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 49% / 1.88 / +23.1 | 9% / 0.21 / -38.0 | reversal |
| shift>=2 & cont | IS | 64 | 47% / 1.73 / +24.8 | 14% / 0.33 / -37.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 20 | 55% / 2.31 / +11.8 | 15% / 0.35 / -11.0 | reversal |
| shift<2 | IS | 95 | 49% / 1.91 / +43.7 | 14% / 0.32 / -56.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
