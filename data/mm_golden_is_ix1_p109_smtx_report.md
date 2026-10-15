# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 389, unique setups 212, simulated 212. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 41 | 59% / 2.66 / +28.2 | 10% / 0.22 / -29.0 | reversal |
| shift>=2 & cont | IS | 54 | 44% / 1.56 / +16.8 | 17% / 0.40 / -27.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 10% / 0.22 / -14.0 | reversal |
| shift<2 | IS | 89 | 52% / 2.09 / +46.7 | 11% / 0.25 / -59.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
