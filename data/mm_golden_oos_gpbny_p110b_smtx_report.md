# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 341, unique setups 179, simulated 179. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 30 | 53% / 2.15 / +16.1 | 17% / 0.40 / -15.0 | reversal |
| shift>=2 & cont | OOS | 43 | 53% / 2.21 / +24.3 | 16% / 0.39 / -22.0 | reversal |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 16 | 56% / 2.83 / +11.6 | 12% / 0.29 / -10.0 | reversal |
| shift<2 | OOS | 82 | 49% / 1.85 / +35.8 | 20% / 0.48 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
