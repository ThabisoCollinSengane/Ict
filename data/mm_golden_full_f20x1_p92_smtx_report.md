# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 800, unique setups 440, simulated 440. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 44 | 55% / 2.34 / +26.7 | 11% / 0.26 / -29.0 | reversal |
| shift>=2 & smt | OOS | 29 | 59% / 2.68 / +20.1 | 14% / 0.32 / -17.0 | reversal |
| shift>=2 & cont | IS | 60 | 53% / 2.24 / +34.8 | 17% / 0.40 / -30.0 | reversal |
| shift>=2 & cont | OOS | 51 | 49% / 1.94 / +24.2 | 18% / 0.43 / -24.0 | reversal |
| shift>=2 & none | IS | 5 | 40% / 1.33 / +1.0 | 60% / 3.00 / +4.0 | continuation |
| shift>=2 & none | OOS | 4 | 50% / 2.00 / +2.0 | 0% / 0.00 / -4.0 | reversal |
| shift>=2 & noref | IS | 14 | 71% / 4.52 / +14.1 | 7% / 0.15 / -11.0 | reversal |
| shift>=2 & noref | OOS | 11 | 45% / 1.67 / +4.0 | 9% / 0.20 / -8.0 | reversal |
| shift<2 | IS | 115 | 54% / 2.32 / +68.8 | 15% / 0.35 / -64.0 | reversal |
| shift<2 | OOS | 107 | 54% / 2.30 / +62.7 | 20% / 0.49 / -44.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
