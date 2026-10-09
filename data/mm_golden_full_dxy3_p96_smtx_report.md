# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 958, unique setups 475, simulated 475. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 50% / 1.96 / +26.1 | 11% / 0.24 / -38.0 | reversal |
| shift>=2 & smt | OOS | 39 | 56% / 2.48 / +25.1 | 13% / 0.29 / -24.0 | reversal |
| shift>=2 & cont | IS | 69 | 45% / 1.60 / +22.8 | 17% / 0.42 / -33.0 | reversal |
| shift>=2 & cont | OOS | 58 | 50% / 1.98 / +27.8 | 12% / 0.27 / -37.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 8 | 50% / 2.00 / +4.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 22 | 64% / 3.26 / +18.1 | 14% / 0.32 / -13.0 | reversal |
| shift>=2 & noref | OOS | 16 | 56% / 2.57 / +11.0 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | IS | 99 | 52% / 2.08 / +51.7 | 14% / 0.33 / -57.0 | reversal |
| shift<2 | OOS | 99 | 49% / 1.89 / +43.4 | 20% / 0.51 / -39.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
