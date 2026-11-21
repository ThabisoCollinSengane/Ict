# P40 conditional-volume modulator — tick-volume validation

**EURUSD + GBPUSD only; 2022 and 2024 as two separate tests** (the tick-covered set). Baseline (modulator OFF) vs modulator ON. `vmod` = trades the modulator actually sized. **Ships only if PF + equity improve while MaxDD holds in BOTH years.**

_run commit: `089f3b8`_

## 2022

| metric | baseline | modulator | Δ |
|---|---|---|---|
| trades | 190.00 | 190.00 | +0.00 |
| win rate | 48.90% | 48.90% | +0.00 |
| profit factor | 5.26 | 5.35 | +0.09 |
| max drawdown | -11.55% | -11.89% | -0.34 |
| ending equity ZAR | 30,016 | 29,473 | -543 |

_trades sized by modulator: 90_

## 2024

| metric | baseline | modulator | Δ |
|---|---|---|---|
| trades | 196.00 | 195.00 | -1.00 |
| win rate | 44.90% | 44.60% | -0.30 |
| profit factor | 3.32 | 3.11 | -0.21 |
| max drawdown | -11.60% | -11.95% | -0.35 |
| ending equity ZAR | 26,778 | 24,388 | -2,390 |

_trades sized by modulator: 108_

## Verdict

GREEN (ship) = PF and equity up, MaxDD not worse, in **both** 2022 and 2024. Otherwise it stays OFF (USE_CONDITIONAL_VOLUME=0).
