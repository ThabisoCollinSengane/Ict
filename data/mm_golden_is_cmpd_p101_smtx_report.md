# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 470, unique setups 237, simulated 237. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 49 | 53% / 2.14 / +26.2 | 14% / 0.33 / -28.0 | reversal |
| shift>=2 & cont | IS | 64 | 45% / 1.62 / +21.8 | 16% / 0.37 / -34.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 18 | 61% / 2.87 / +13.1 | 11% / 0.25 / -12.0 | reversal |
| shift<2 | IS | 97 | 52% / 2.08 / +50.7 | 13% / 0.31 / -58.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
