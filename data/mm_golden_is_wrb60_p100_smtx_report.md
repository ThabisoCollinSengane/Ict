# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 506, unique setups 257, simulated 257. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 46% / 1.69 / +20.1 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & cont | IS | 68 | 47% / 1.74 / +26.8 | 16% / 0.39 / -35.0 | reversal |
| shift>=2 & none | IS | 10 | 40% / 1.33 / +2.0 | 50% / 2.00 / +5.0 | continuation |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift<2 | IS | 102 | 51% / 2.03 / +51.7 | 13% / 0.29 / -63.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
