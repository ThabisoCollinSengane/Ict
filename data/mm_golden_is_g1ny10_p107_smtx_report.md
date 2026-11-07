# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 445, unique setups 226, simulated 226. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 48 | 54% / 2.24 / +27.2 | 10% / 0.23 / -33.0 | reversal |
| shift>=2 & cont | IS | 60 | 43% / 1.49 / +16.8 | 17% / 0.40 / -30.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift<2 | IS | 88 | 52% / 2.14 / +47.7 | 11% / 0.26 / -58.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
