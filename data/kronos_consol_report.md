# P122 — Kronos on the consolidation -> breakout cycle (CLEAN window only)

Kronos (KRONOS_MODEL=NeoQuasar/Kronos-mini), context 256 completed M15 bars, 12 sampled paths, horizon 16 M15 bars (4h). EURUSD/GBPUSD/NZDUSD from 2024-07.
Files: 12; events: 6050 (3823 checks, 2227 breaks).

## Q1 — does Kronos see the EXPANSION coming? (rank corr with the realised 4h range)

Kronos must beat ATR (recent bar size) and HOUR (time of day). `Kronos | left over` = its correlation with what ATR + hour do NOT explain — the only number that says it adds anything. ± = day-block bootstrap SE.

| period | n | Kronos | ATR | HOUR (mean range of that hour) | Kronos | left over | left-range rate: Kronos top vs bottom third |
|---|---|---|---|---|---|---|
| 2024-07..2025-12 | 2396 | +0.510±0.023 | +0.522±0.021 | +0.267±0.023 | +0.145±0.027 | 83% vs 61% |
| 2026 | 1427 | +0.500±0.027 | +0.523±0.025 | +0.254±0.036 | +0.136±0.033 | 84% vs 64% |
| ALL | 3823 | +0.513±0.019 | +0.526±0.017 | +0.267±0.020 | +0.144±0.022 | 84% vs 61% |

## Q2 — Judas (fakeout) or real breakout?

Accuracy on resolved breaks (fakeout = close half a range back inside the edge, breakout = close half a range beyond it, whichever first). BASE = always guess the period's more common outcome; RULE = the engine's 'break bar closed back inside' read; NEAR = whichever level the break bar's close is nearer to (pure geometry — what a random walk would do); KRONOS = majority of its sampled paths. Kronos must beat NEAR, not just 50%. ± = day-clustered SE.

| period | resolved | fakeout share | BASE | RULE | NEAR | KRONOS | KRONOS - NEAR |
|---|---|---|---|---|---|---|---|
| 2024-07..2025-12 | 1084 | 47% | 53.0±1.7 | 63.3±1.5 | 63.3±1.5 | 59.1±1.6 | -4.2±1.8 |
| 2026 | 543 | 49% | 50.6±2.3 | 62.2±2.1 | 62.2±2.1 | 59.1±2.1 | -3.1±2.5 |
| ALL | 1627 | 48% | 52.2±1.4 | 62.9±1.2 | 62.9±1.2 | 59.1±1.3 | -3.8±1.4 |

Realised fakeout rate by Kronos p_fake tercile (resolved breaks):

| period | low p_fake | mid | high |
|---|---|---|---|
| 2024-07..2025-12 | 31% (n 363) | 52% (n 351) | 58% (n 370) |
| 2026 | 38% (n 201) | 55% (n 161) | 56% (n 181) |
| ALL | 36% (n 639) | 53% (n 415) | 58% (n 573) |

## Q2 trade sim — fade vs follow, 2R, 1 pip cost (avg R ± day-clustered SE, n)

| period | always FADE | always FOLLOW | RULE picks | KRONOS picks | COIN picks |
|---|---|---|---|---|---|
| 2024-07..2025-12 | -0.248±0.037 (n 1272) | -0.300±0.047 (n 909) | -0.269±0.043 (n 1001) | -0.254±0.040 (n 1106) | -0.283±0.039 (n 1101) |
| 2026 | -0.228±0.055 (n 661) | -0.302±0.067 (n 447) | -0.222±0.060 (n 509) | -0.227±0.059 (n 578) | -0.276±0.057 (n 568) |
| ALL | -0.241±0.031 (n 1933) | -0.301±0.039 (n 1356) | -0.253±0.035 (n 1510) | -0.245±0.033 (n 1684) | -0.294±0.032 (n 1635) |

