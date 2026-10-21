# P123 — Kronos's expansion read vs longer volatility windows

Same P122 check events (live unbroken consolidation at 03/04/07/08/09 ET), n = 5170 of 5170 with every baseline available. Pairs: EURUSD, GBPUSD.
Kronos survives only if column (c) stays clearly positive in BOTH periods and the out-of-sample gain is > 0 both ways. noise/mimic must read ~0 (they are the calibration).

## Rank corr with the realised 4h range (± day-block bootstrap SE)

| period | n | Kronos | atr16 | atr256 | rv256 | adr20 | pdr | seas20 | width |
|---|---|---|---|---|---|---|---|---|---|
| 2024-07..2025-12 | 3930 | +0.159 | +0.793 | +0.223 | +0.221 | +0.050 | +0.036 | +0.015 | +0.012 |
| 2026 | 1240 | +0.190 | +0.753 | +0.208 | +0.200 | -0.065 | -0.019 | -0.131 | +0.006 |
| ALL | 5170 | +0.166 | +0.785 | +0.221 | +0.217 | +0.031 | +0.026 | -0.012 | +0.011 |

## Kronos's corr with what the baselines LEAVE (the test)

| period | (a) P122: atr16 + hour | (b) + atr256 | (c) everything | noise, after (c) | mimic, after (c) |
|---|---|---|---|---|---|
| 2024-07..2025-12 | +0.002±0.019 | -0.003±0.019 | -0.004±0.019 | +0.035±0.015 | +0.021±0.019 |
| 2026 | +0.072±0.034 | +0.038±0.035 | +0.037±0.035 | +0.002±0.027 | -0.052±0.032 |
| ALL | +0.019±0.018 | +0.006±0.018 | +0.005±0.018 | +0.028±0.014 | +0.005±0.017 |

## Out-of-sample R² of log realised range (fit one period, score the other)

| fit -> score | full baseline | + log Kronos | gain |
|---|---|---|---|
| 2024-07..2025-12 -> 2026 | 0.608 | 0.608 | -0.001 |
| 2026 -> 2024-07..2025-12 | 0.657 | 0.654 | -0.004 |

## Kronos's OWN opinion (log k_range residualised on the full baseline), by tercile

What an engine filter would act on. Cells: price closes outside the range within 4h % / median realised 4h range pips / median baseline-predicted pips. Terciles cut on the first period and applied to both.

| period | low third | mid | top third | top - low leave-rate ± SE |
|---|---|---|---|---|
| 2024-07..2025-12 | 61% / 9.8 / 9.9 (n 1310) | 59% / 9.8 / 10.1 (n 1310) | 58% / 10.0 / 9.9 (n 1310) | -3.7±1.9pp |
| 2026 | 59% / 9.5 / 9.6 (n 391) | 59% / 9.7 / 10.1 (n 422) | 58% / 10.0 / 10.0 (n 427) | -1.0±3.4pp |

