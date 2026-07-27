# P40 conditional-volume modulator — tick-volume validation

**EURUSD + GBPUSD only; 2022 and 2024 as two separate tests** (the tick-covered set). Baseline (modulator OFF) vs modulator ON. `vmod` = trades the modulator actually sized. **Ships only if PF + equity improve while MaxDD holds in BOTH years.**

## 2022

| metric | baseline | modulator | Δ |
|---|---|---|---|
| trades | 190.00 | — | — |
| win rate | 48.90% | — | — |
| profit factor | 5.26 | — | — |
| max drawdown | -11.55% | — | — |
| ending equity ZAR | 30,016 | — | — |

_trades sized by modulator: 0_

## 2024

| metric | baseline | modulator | Δ |
|---|---|---|---|
| trades | 196.00 | — | — |
| win rate | 44.90% | — | — |
| profit factor | 3.32 | — | — |
| max drawdown | -11.60% | — | — |
| ending equity ZAR | 26,778 | — | — |

_trades sized by modulator: 0_

## Verdict

GREEN (ship) = PF and equity up, MaxDD not worse, in **both** 2022 and 2024. Otherwise it stays OFF (USE_CONDITIONAL_VOLUME=0).
