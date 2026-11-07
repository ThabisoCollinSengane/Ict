# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 384, unique setups 197, simulated 197. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.71 / +31.1 | 9% / 0.20 / -33.0 | reversal |
| shift>=2 & cont | IS | 55 | 42% / 1.40 / +12.8 | 15% / 0.34 / -31.0 | reversal |
| shift>=2 & none | IS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 17 | 65% / 3.38 / +14.3 | 12% / 0.27 / -11.0 | reversal |
| shift<2 | IS | 74 | 47% / 1.74 / +28.7 | 12% / 0.28 / -47.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
