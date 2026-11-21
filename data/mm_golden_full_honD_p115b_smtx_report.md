# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 944, unique setups 476, simulated 476. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 49% / 1.88 / +23.1 | 8% / 0.16 / -41.0 | reversal |
| shift>=2 & smt | OOS | 37 | 54% / 2.24 / +21.1 | 14% / 0.31 / -22.0 | reversal |
| shift>=2 & cont | IS | 68 | 51% / 2.09 / +35.8 | 15% / 0.34 / -38.0 | reversal |
| shift>=2 & cont | OOS | 60 | 52% / 2.09 / +31.5 | 18% / 0.45 / -27.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 44% / 1.60 / +3.0 | continuation |
| shift>=2 & none | OOS | 11 | 45% / 1.98 / +5.0 | 27% / 0.75 / -2.0 | reversal |
| shift>=2 & noref | IS | 26 | 62% / 3.01 / +20.1 | 15% / 0.36 / -14.0 | reversal |
| shift>=2 & noref | OOS | 16 | 56% / 2.83 / +11.6 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | IS | 101 | 53% / 2.25 / +58.7 | 14% / 0.32 / -59.0 | reversal |
| shift<2 | OOS | 95 | 51% / 1.97 / +44.4 | 23% / 0.60 / -29.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
