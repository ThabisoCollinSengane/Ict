# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 259, unique setups 144, simulated 144. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 32 | 47% / 1.70 / +11.9 | 25% / 0.67 / -8.0 | reversal |
| shift>=2 & cont | OOS | 42 | 55% / 2.42 / +27.0 | 12% / 0.27 / -27.0 | reversal |
| shift>=2 & none | OOS | 7 | 43% / 1.50 / +2.0 | 43% / 1.50 / +2.0 | continuation |
| shift>=2 & noref | OOS | 16 | 56% / 2.57 / +11.0 | 25% / 0.67 / -4.0 | reversal |
| shift<2 | OOS | 47 | 38% / 1.10 / +2.7 | 15% / 0.35 / -26.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
