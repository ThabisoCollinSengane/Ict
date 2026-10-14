# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 389, unique setups 203, simulated 203. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 37 | 54% / 2.24 / +21.1 | 16% / 0.39 / -19.0 | reversal |
| shift>=2 & cont | OOS | 52 | 52% / 2.14 / +27.9 | 15% / 0.36 / -28.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & noref | OOS | 18 | 61% / 3.23 / +14.2 | 11% / 0.25 / -12.0 | reversal |
| shift<2 | OOS | 86 | 49% / 1.84 / +36.5 | 21% / 0.53 / -32.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
