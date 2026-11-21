# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 614, unique setups 275, simulated 275. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 52 | 56% / 2.47 / +33.7 | 12% / 0.26 / -34.0 | reversal |
| shift>=2 & cont | IS | 64 | 50% / 1.96 / +30.8 | 16% / 0.37 / -34.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 57% / 2.67 / +5.0 | continuation |
| shift>=2 & noref | IS | 20 | 70% / 4.35 / +20.1 | 15% / 0.35 / -11.0 | reversal |
| shift<2 | IS | 132 | 55% / 2.39 / +81.8 | 13% / 0.30 / -81.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
