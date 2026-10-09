# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 531, unique setups 262, simulated 262. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 53% / 2.19 / +29.7 | 11% / 0.26 / -35.0 | reversal |
| shift>=2 & cont | IS | 64 | 50% / 1.96 / +30.8 | 16% / 0.37 / -34.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 57% / 2.67 / +5.0 | continuation |
| shift>=2 & noref | IS | 15 | 67% / 3.61 / +13.1 | 7% / 0.14 / -12.0 | reversal |
| shift<2 | IS | 123 | 53% / 2.22 / +69.8 | 14% / 0.32 / -72.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
