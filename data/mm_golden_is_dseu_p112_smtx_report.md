# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 431, unique setups 215, simulated 215. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 44 | 55% / 2.26 / +25.2 | 16% / 0.38 / -23.0 | reversal |
| shift>=2 & cont | IS | 56 | 50% / 1.96 / +26.8 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 19 | 63% / 3.15 / +15.1 | 16% / 0.38 / -10.0 | reversal |
| shift<2 | IS | 88 | 51% / 2.04 / +44.7 | 14% / 0.32 / -52.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
