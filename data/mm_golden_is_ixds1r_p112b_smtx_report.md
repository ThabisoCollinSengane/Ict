# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 452, unique setups 223, simulated 223. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.59 / +30.2 | 9% / 0.20 / -33.0 | reversal |
| shift>=2 & cont | IS | 59 | 42% / 1.44 / +14.8 | 15% / 0.36 / -32.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 19 | 58% / 2.51 / +12.1 | 16% / 0.38 / -10.0 | reversal |
| shift<2 | IS | 91 | 52% / 2.08 / +47.7 | 12% / 0.28 / -58.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
