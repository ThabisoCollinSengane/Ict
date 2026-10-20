# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 911, unique setups 547, simulated 547. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 48 | 44% / 1.48 / +13.1 | 12% / 0.29 / -30.0 | reversal |
| shift>=2 & smt | OOS | 55 | 42% / 1.34 / +11.0 | 20% / 0.50 / -22.0 | reversal |
| shift>=2 & cont | IS | 70 | 44% / 1.56 / +21.8 | 21% / 0.55 / -25.0 | reversal |
| shift>=2 & cont | OOS | 77 | 43% / 1.54 / +23.2 | 14% / 0.33 / -44.0 | reversal |
| shift>=2 & none | IS | 5 | 80% / 8.00 / +7.0 | 20% / 0.50 / -2.0 | reversal |
| shift>=2 & none | OOS | 15 | 40% / 1.33 / +3.0 | 40% / 1.33 / +3.0 | continuation |
| shift>=2 & noref | IS | 31 | 55% / 2.43 / +20.0 | 16% / 0.38 / -16.0 | reversal |
| shift>=2 & noref | OOS | 29 | 38% / 1.27 / +4.6 | 14% / 0.32 / -17.0 | reversal |
| shift<2 | IS | 106 | 43% / 1.51 / +30.4 | 15% / 0.36 / -58.0 | reversal |
| shift<2 | OOS | 111 | 41% / 1.32 / +20.3 | 16% / 0.39 / -57.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
