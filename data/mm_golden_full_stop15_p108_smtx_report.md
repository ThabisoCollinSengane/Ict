# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 974, unique setups 468, simulated 468. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 58 | 50% / 1.96 / +27.1 | 12% / 0.27 / -37.0 | reversal |
| shift>=2 & smt | OOS | 35 | 54% / 2.38 / +22.0 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | IS | 65 | 48% / 1.79 / +26.8 | 14% / 0.32 / -38.0 | reversal |
| shift>=2 & cont | OOS | 55 | 53% / 2.25 / +31.2 | 15% / 0.34 / -31.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 13 | 54% / 2.33 / +8.0 | 23% / 0.60 / -4.0 | reversal |
| shift>=2 & noref | IS | 26 | 62% / 3.03 / +20.3 | 15% / 0.36 / -14.0 | reversal |
| shift>=2 & noref | OOS | 13 | 62% / 2.98 / +9.9 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | IS | 101 | 49% / 1.84 / +43.7 | 13% / 0.30 / -62.0 | reversal |
| shift<2 | OOS | 93 | 51% / 1.92 / +42.0 | 20% / 0.51 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
