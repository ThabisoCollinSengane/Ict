# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 383, unique setups 197, simulated 197. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 34 | 56% / 2.41 / +21.1 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & cont | OOS | 50 | 54% / 2.29 / +29.5 | 16% / 0.38 / -26.0 | reversal |
| shift>=2 & none | OOS | 11 | 45% / 1.67 / +4.0 | 27% / 0.75 / -2.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | OOS | 86 | 49% / 1.80 / +34.7 | 21% / 0.53 / -32.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
