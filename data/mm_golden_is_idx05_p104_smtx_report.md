# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 467, unique setups 232, simulated 232. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 52 | 54% / 2.30 / +30.1 | 12% / 0.26 / -34.0 | reversal |
| shift>=2 & cont | IS | 57 | 44% / 1.53 / +16.8 | 16% / 0.38 / -30.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 15% / 0.35 / -11.0 | reversal |
| shift<2 | IS | 94 | 50% / 1.95 / +44.7 | 14% / 0.32 / -55.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
