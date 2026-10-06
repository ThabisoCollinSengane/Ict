# P79 — fundamentals scorecard (real data)

_Measurement only. Every effect must hold in BOTH halves with pooled |t| ≥ 2.5 to count. 'OPPOSITE' = what fading the signal would have done._

_coverage: daily EURUSD 2021-01-01→2026-10-06, GBPUSD 2021-01-01→2026-10-06, NZDUSD 2021-01-01→2026-10-06; yields 3m, 5y, 10y; COT rows 900; hourly pairs 3; news events 354_

## §A COT — do speculators' positions predict next week?

_2021: 156 rows · 2022: 156 rows · 2023: 156 rows · 2024: 159 rows · 2025: 156 rows · 2026: 117 rows_

Signal = specs' net position (% of open interest), z-scored against the prior 52 weeks. Return = Monday after release → following Monday, bp. IS 2022-23 / OOS 2024-26.

| pair | split | weeks | corr z→return (t) | extreme weeks |z|≥1.5 | FOLLOW bp/wk (hit%) | OPPOSITE bp/wk (hit%) |
|---|---|---|---|---|---|---|
| EURUSD | IS | 104 | +0.17 (+1.7) | 30 | +14.3 (60%) | -14.3 (40%) |
| EURUSD | OOS | 143 | +0.05 (+0.6) | 59 | +6.4 (44%) | -6.4 (56%) |
| GBPUSD | IS | 104 | +0.09 (+0.9) | 33 | +17.6 (58%) | -17.6 (42%) |
| GBPUSD | OOS | 143 | -0.10 (-1.1) | 30 | -24.6 (33%) | +24.6 (67%) |
| NZDUSD | IS | 104 | -0.06 (-0.6) | 30 | -31.8 (40%) | +31.8 (60%) |
| NZDUSD | OOS | 143 | -0.20 (-2.4) | 27 | -33.6 (33%) | +33.6 (67%) |

**Verdict (extreme weeks, FOLLOW the specs):** EURUSD nothing (pooled t +1.3) · GBPUSD nothing (pooled t -0.5) · NZDUSD nothing (pooled t -1.9). `OPPOSITE WORKS` means fading the crowd paid in both halves.

## §B Interest rates — do US yields move or predict the pairs?

Daily yield change in bp vs daily pair return in bp. The rate story says yields UP → dollar UP → pairs DOWN, i.e. a NEGATIVE same-day correlation. Halves: 2022-23 / 2024-26.

| pair | yield | same-day corr IS / OOS | next-day corr IS / OOS (t) |
|---|---|---|---|
| EURUSD | 3m | -0.09 / +0.01 | -0.09 (-2.1) / -0.18 (-4.8) |
| EURUSD | 5y | -0.09 / -0.01 | -0.33 (-7.7) / -0.33 (-9.3) |
| EURUSD | 10y | -0.07 / -0.01 | -0.29 (-6.7) / -0.30 (-8.1) |
| GBPUSD | 3m | -0.10 / +0.03 | -0.11 (-2.6) / -0.15 (-4.1) |
| GBPUSD | 5y | -0.05 / -0.06 | -0.36 (-8.6) / -0.30 (-8.2) |
| GBPUSD | 10y | -0.06 / -0.07 | -0.32 (-7.7) / -0.27 (-7.4) |
| NZDUSD | 3m | -0.08 / +0.02 | -0.15 (-3.3) / -0.10 (-2.7) |
| NZDUSD | 5y | -0.02 / -0.05 | -0.41 (-10.2) / -0.24 (-6.5) |
| NZDUSD | 10y | -0.03 / -0.06 | -0.36 (-8.7) / -0.22 (-5.9) |

**The brief's own rule** (5-day US yield change beyond ±5bp → lean the pairs the OTHER way), scored on the next day and the next 5 days:

| pair | horizon | split | signals | FOLLOW bp (hit%) | OPPOSITE bp (hit%) |
|---|---|---|---|---|---|
| EURUSD | +1d | IS | 403 | +4.7 (53%) | -4.7 (47%) |
| EURUSD | +1d | OOS | 456 | +6.6 (57%) | -6.6 (43%) |
| EURUSD | +5d | IS | 79 | -16.5 (48%) | +16.5 (52%) |
| EURUSD | +5d | OOS | 94 | +12.1 (54%) | -12.1 (46%) |
| GBPUSD | +1d | IS | 403 | +8.8 (54%) | -8.8 (46%) |
| GBPUSD | +1d | OOS | 456 | +5.1 (57%) | -5.1 (43%) |
| GBPUSD | +5d | IS | 79 | -2.5 (47%) | +2.5 (53%) |
| GBPUSD | +5d | OOS | 94 | +14.2 (57%) | -14.2 (43%) |
| NZDUSD | +1d | IS | 403 | +12.9 (57%) | -12.9 (43%) |
| NZDUSD | +1d | OOS | 456 | +7.8 (57%) | -7.8 (43%) |
| NZDUSD | +5d | IS | 79 | +22.6 (54%) | -22.6 (46%) |
| NZDUSD | +5d | OOS | 94 | +19.2 (59%) | -19.2 (41%) |

**Verdict (brief's yield lean):** EURUSD +1d WORKS · EURUSD +5d nothing · GBPUSD +1d WORKS · GBPUSD +5d nothing · NZDUSD +1d WORKS · NZDUSD +5d nothing. +5d uses non-overlapping 5-day blocks.

## §C High / Medium news — how big is the move, and does it follow through?

_hourly data 2023-12-21 → 2026-10-06; halves split at 2025-05-14. IMPACT = |move| in the 2h from the event's hour, as a multiple of the same clock hour on no-news days. FOLLOW = next 3h in the direction of that first move (bp); FADE = the opposite. CONTROL = the same measures at the same clock hours on no-news days._

| class | half | events | avg 2h move bp | × normal hour | FOLLOW next 3h bp (t) | vs no-news (t) | FADE bp |
|---|---|---|---|---|---|---|---|
| Critical | A | 135 | 25.0 | 2.2× | -1.7 (-0.7) | -2.1 (-0.9) | +1.7 |
| Critical | B | 132 | 17.3 | 1.8× | -0.2 (-0.1) | -0.9 (-0.7) | +0.2 |
| High | A | 22 | 21.8 | 1.8× | -6.1 (-0.9) | -4.5 (-0.6) | +6.1 |
| High | B | 21 | 23.5 | 2.2× | +0.6 (+0.1) | +0.5 (+0.1) | -0.6 |
| Medium | A | 32 | 11.3 | 1.1× | +3.1 (+1.0) | +3.0 (+1.0) | -3.1 |
| Medium | B | 30 | 9.2 | 1.0× | -2.4 (-0.7) | -1.8 (-0.5) | +2.4 |

**Verdict (follow-through beyond a normal hour):** Critical nothing (pooled t -1.1) · High nothing (pooled t -0.5) · Medium nothing (pooled t +0.3). `OPPOSITE WORKS` here means fading the first news move paid.

_No NZD events exist in the calendar, so NZDUSD only appears via USD news. USD events are High only (NFP/CPI/FOMC are 'Critical')._

