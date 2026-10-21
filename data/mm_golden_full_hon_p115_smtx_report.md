# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 41, unique setups 30, simulated 30. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 6 | 17% / 0.40 / -3.0 | 17% / 0.40 / -3.0 | continuation |
| shift>=2 & cont | IS | 5 | 60% / 3.00 / +4.0 | 0% / 0.00 / -5.0 | reversal |
| shift>=2 & noref | IS | 5 | 60% / 3.00 / +4.0 | 0% / 0.00 / -5.0 | reversal |
| shift<2 | IS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.
