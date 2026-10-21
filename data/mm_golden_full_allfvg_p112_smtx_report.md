# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 751, unique setups 387, simulated 387. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 46 | 57% / 2.57 / +30.1 | 9% / 0.19 / -34.0 | reversal |
| shift>=2 & smt | OOS | 33 | 58% / 2.58 / +22.1 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | IS | 55 | 42% / 1.40 / +12.8 | 15% / 0.34 / -31.0 | reversal |
| shift>=2 & cont | OOS | 48 | 56% / 2.56 / +31.8 | 12% / 0.29 / -30.0 | reversal |
| shift>=2 & none | IS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & none | OOS | 7 | 57% / 2.67 / +5.0 | 29% / 0.80 / -1.0 | reversal |
| shift>=2 & noref | IS | 18 | 67% / 3.71 / +16.3 | 11% / 0.25 / -12.0 | reversal |
| shift>=2 & noref | OOS | 12 | 58% / 2.80 / +9.0 | 8% / 0.18 / -9.0 | reversal |
| shift<2 | IS | 79 | 48% / 1.80 / +32.7 | 13% / 0.29 / -49.0 | reversal |
| shift<2 | OOS | 83 | 52% / 2.09 / +42.4 | 18% / 0.44 / -38.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
