# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 449, unique setups 238, simulated 238. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 44 | 55% / 2.34 / +26.7 | 11% / 0.26 / -29.0 | reversal |
| shift>=2 & cont | IS | 60 | 53% / 2.24 / +34.8 | 17% / 0.40 / -30.0 | reversal |
| shift>=2 & none | IS | 5 | 40% / 1.33 / +1.0 | 60% / 3.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 14 | 71% / 4.52 / +14.1 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 115 | 54% / 2.32 / +68.8 | 15% / 0.35 / -64.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
