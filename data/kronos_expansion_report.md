# P123 — Kronos's expansion read vs longer volatility windows

Same P122 check events (live unbroken consolidation at 03/04/07/08/09 ET), n = 3823 of 3823 with every baseline available. Pairs: EURUSD, GBPUSD, NZDUSD.
Kronos survives only if column (c) stays clearly positive in BOTH periods and the out-of-sample gain is > 0 both ways. noise/mimic must read ~0 (they are the calibration).

## Rank corr with the realised 4h range (± day-block bootstrap SE)

| period | n | Kronos | atr16 | atr256 | rv256 | adr20 | pdr | seas20 | width |
|---|---|---|---|---|---|---|---|---|---|
| 2024-07..2025-12 | 2396 | +0.510 | +0.522 | +0.494 | +0.457 | +0.492 | +0.278 | +0.605 | +0.097 |
| 2026 | 1427 | +0.500 | +0.523 | +0.457 | +0.377 | +0.405 | +0.240 | +0.512 | +0.137 |
| ALL | 3823 | +0.513 | +0.526 | +0.486 | +0.435 | +0.469 | +0.268 | +0.579 | +0.116 |

## Kronos's corr with what the baselines LEAVE (the test)

| period | (a) P122: atr16 + hour | (b) + atr256 | (c) everything | noise, after (c) | mimic, after (c) |
|---|---|---|---|---|---|
| 2024-07..2025-12 | +0.091±0.027 | +0.050±0.027 | +0.037±0.027 | +0.033±0.020 | +0.037±0.025 |
| 2026 | +0.096±0.033 | +0.063±0.033 | +0.050±0.032 | +0.031±0.029 | -0.010±0.026 |
| ALL | +0.102±0.022 | +0.061±0.022 | +0.050±0.022 | +0.032±0.018 | +0.018±0.020 |

## Out-of-sample R² of log realised range (fit one period, score the other)

| fit -> score | full baseline | + log Kronos | gain |
|---|---|---|---|
| 2024-07..2025-12 -> 2026 | 0.328 | 0.333 | +0.004 |
| 2026 -> 2024-07..2025-12 | 0.371 | 0.374 | +0.003 |

## Kronos's OWN opinion (log k_range residualised on the full baseline), by tercile

What an engine filter would act on. Cells: price closes outside the range within 4h % / median realised 4h range pips / median baseline-predicted pips. Terciles cut on the first period and applied to both.

| period | low third | mid | top third | top - low leave-rate ± SE |
|---|---|---|---|---|
| 2024-07..2025-12 | 73% / 26.1 / 26.8 (n 799) | 71% / 27.4 / 26.2 (n 798) | 70% / 27.7 / 25.9 (n 799) | -3.3±2.8pp |
| 2026 | 72% / 23.4 / 25.0 (n 512) | 70% / 24.0 / 25.2 (n 504) | 75% / 25.8 / 24.9 (n 411) | +2.2±4.0pp |

