# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 837, unique setups 434, simulated 434. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 49% / 1.88 / +23.1 | 9% / 0.21 / -38.0 | reversal |
| shift>=2 & smt | OOS | 33 | 55% / 2.27 / +19.1 | 12% / 0.28 / -21.0 | reversal |
| shift>=2 & cont | IS | 64 | 47% / 1.73 / +24.8 | 14% / 0.33 / -37.0 | reversal |
| shift>=2 & cont | OOS | 53 | 51% / 2.05 / +26.8 | 15% / 0.36 / -29.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & none | OOS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 20 | 55% / 2.31 / +11.8 | 15% / 0.35 / -11.0 | reversal |
| shift>=2 & noref | OOS | 13 | 62% / 3.20 / +11.0 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | IS | 95 | 49% / 1.91 / +43.7 | 14% / 0.32 / -56.0 | reversal |
| shift<2 | OOS | 89 | 52% / 2.06 / +44.4 | 18% / 0.44 / -41.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
