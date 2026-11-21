# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 442, unique setups 238, simulated 238. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 40 | 55% / 2.44 / +26.0 | 18% / 0.42 / -19.0 | reversal |
| shift>=2 & cont | OOS | 64 | 38% / 1.25 / +9.4 | 19% / 0.46 / -28.0 | reversal |
| shift>=2 & none | OOS | 14 | 50% / 2.22 / +7.7 | 21% / 0.55 / -5.0 | reversal |
| shift>=2 & noref | OOS | 17 | 53% / 2.25 / +9.2 | 18% / 0.43 / -8.0 | reversal |
| shift<2 | OOS | 103 | 49% / 1.78 / +41.0 | 17% / 0.42 / -49.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
