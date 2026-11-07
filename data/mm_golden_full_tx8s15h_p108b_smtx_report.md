# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 842, unique setups 436, simulated 436. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 49% / 1.88 / +23.1 | 9% / 0.21 / -38.0 | reversal |
| shift>=2 & smt | OOS | 33 | 55% / 2.27 / +19.1 | 12% / 0.28 / -21.0 | reversal |
| shift>=2 & cont | IS | 60 | 47% / 1.71 / +22.8 | 13% / 0.31 / -36.0 | reversal |
| shift>=2 & cont | OOS | 54 | 50% / 1.98 / +25.8 | 15% / 0.35 / -30.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & none | OOS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 13 | 62% / 3.20 / +11.0 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | IS | 98 | 51% / 2.04 / +49.7 | 13% / 0.31 / -59.0 | reversal |
| shift<2 | OOS | 90 | 52% / 2.11 / +46.4 | 18% / 0.43 / -42.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
