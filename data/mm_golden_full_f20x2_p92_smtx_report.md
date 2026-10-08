# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 1150, unique setups 510, simulated 510. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 52 | 56% / 2.47 / +33.7 | 12% / 0.26 / -34.0 | reversal |
| shift>=2 & smt | OOS | 30 | 60% / 3.00 / +24.0 | 13% / 0.31 / -18.0 | reversal |
| shift>=2 & cont | IS | 64 | 50% / 1.96 / +30.8 | 16% / 0.37 / -34.0 | reversal |
| shift>=2 & cont | OOS | 64 | 50% / 1.96 / +30.5 | 17% / 0.42 / -31.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 57% / 2.67 / +5.0 | continuation |
| shift>=2 & none | OOS | 7 | 57% / 2.67 / +5.0 | 14% / 0.33 / -4.0 | reversal |
| shift>=2 & noref | IS | 20 | 70% / 4.35 / +20.1 | 15% / 0.35 / -11.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.38 / +11.9 | 0% / 0.00 / -14.0 | reversal |
| shift<2 | IS | 132 | 55% / 2.39 / +81.8 | 13% / 0.30 / -81.0 | reversal |
| shift<2 | OOS | 120 | 57% / 2.57 / +78.9 | 17% / 0.40 / -60.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
