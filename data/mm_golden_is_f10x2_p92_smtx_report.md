# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 320, unique setups 204, simulated 204. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 29 | 59% / 2.83 / +22.0 | 14% / 0.32 / -17.0 | reversal |
| shift>=2 & cont | IS | 45 | 49% / 1.86 / +19.8 | 11% / 0.25 / -30.0 | reversal |
| shift>=2 & none | IS | 4 | 50% / 2.00 / +2.0 | 50% / 2.00 / +2.0 | continuation |
| shift>=2 & noref | IS | 6 | 50% / 2.00 / +3.0 | 17% / 0.40 / -3.0 | reversal |
| shift<2 | IS | 120 | 50% / 1.98 / +57.8 | 17% / 0.40 / -60.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
