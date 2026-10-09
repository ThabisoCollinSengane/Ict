# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 529, unique setups 255, simulated 255. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 50% / 1.96 / +26.1 | 11% / 0.24 / -38.0 | reversal |
| shift>=2 & cont | IS | 69 | 45% / 1.60 / +22.8 | 17% / 0.42 / -33.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 22 | 64% / 3.26 / +18.1 | 14% / 0.32 / -13.0 | reversal |
| shift<2 | IS | 99 | 52% / 2.08 / +51.7 | 14% / 0.33 / -57.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
