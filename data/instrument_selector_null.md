# Which market will deliver? Instrument selector study (P106) — RANDOM-WALK NULL (no instrument should be predictable)

12,020 instrument-sessions. `move` = 5h directional travel in units of the 20-day average daily range; `amd` = ran one side of the pre-session range, then the other.

## 1. Average outcome by instrument and session

| instrument | session | IS move / amd% | OOS move / amd% | 2026 move / amd% | n IS/OOS/26 |
|---|---|---|---|---|---|
| EURUSD | london | 0.25 / 7% | 0.23 / 6% | 0.22 / 7% | 485/523/194 |
| EURUSD | ny | 0.22 / 15% | 0.22 / 13% | 0.22 / 11% | 485/523/194 |
| GBPUSD | london | 0.22 / 6% | 0.23 / 4% | 0.24 / 6% | 485/523/194 |
| GBPUSD | ny | 0.23 / 14% | 0.24 / 17% | 0.22 / 12% | 485/523/194 |
| NSXUSD | london | 0.25 / 8% | 0.25 / 7% | 0.25 / 8% | 485/523/194 |
| NSXUSD | ny | 0.25 / 14% | 0.24 / 17% | 0.23 / 15% | 485/523/194 |
| SPXUSD | london | 0.24 / 6% | 0.24 / 7% | 0.23 / 5% | 485/523/194 |
| SPXUSD | ny | 0.24 / 12% | 0.25 / 14% | 0.23 / 16% | 485/523/194 |
| XAUUSD | london | 0.26 / 6% | 0.23 / 5% | 0.22 / 6% | 485/523/194 |
| XAUUSD | ny | 0.25 / 12% | 0.24 / 15% | 0.25 / 12% | 485/523/194 |

## 2. Does each predictor rank the outcome? (Spearman, IS / OOS)

| instrument | predictor | vs move IS / OOS | vs amd IS / OOS |
|---|---|---|---|
| EURUSD | coil | +0.06 / +0.04 | -0.28 / -0.27 |
| EURUSD | er5 | -0.04 / +0.01 | +0.04 / +0.08 |
| EURUSD | edge | -0.01 / -0.01 | +0.03 / +0.02 |
| EURUSD | past | -0.00 / -0.03 | -0.02 / -0.00 |
| GBPUSD | coil | +0.00 / +0.03 | -0.26 / -0.30 |
| GBPUSD | er5 | -0.02 / -0.03 | -0.01 / -0.01 |
| GBPUSD | edge | -0.06 / -0.03 | -0.03 / -0.04 |
| GBPUSD | past | -0.01 / +0.02 | +0.04 / -0.00 |
| NSXUSD | coil | +0.05 / +0.02 | -0.29 / -0.26 |
| NSXUSD | er5 | -0.01 / -0.00 | +0.05 / -0.09 |
| NSXUSD | edge | +0.04 / +0.03 | +0.03 / +0.02 |
| NSXUSD | past | +0.01 / -0.02 | -0.00 / -0.06 |
| SPXUSD | coil | -0.04 / +0.04 | -0.24 / -0.30 |
| SPXUSD | er5 | +0.03 / +0.01 | +0.02 / +0.07 |
| SPXUSD | edge | +0.02 / +0.02 | +0.03 / +0.04 |
| SPXUSD | past | +0.01 / -0.01 | -0.02 / +0.02 |
| XAUUSD | coil | +0.05 / +0.04 | -0.25 / -0.24 |
| XAUUSD | er5 | -0.05 / +0.02 | +0.03 / +0.02 |
| XAUUSD | edge | -0.03 / -0.02 | -0.01 / -0.03 |
| XAUUSD | past | -0.04 / -0.02 | +0.01 / +0.01 |

## 3. Selector: pick one instrument per session

Model fitted on IS. Best FIXED choice from IS: london -> XAUUSD, ny -> XAUUSD.

| half | selector move / amd% | fixed best move / amd% | average of all | random pick | sessions |
|---|---|---|---|---|---|
| IS | 0.263 / 6% | 0.252 / 9% | 0.239 / 10% | 0.237 / 10% | 970 |
| OOS | 0.241 / 7% | 0.233 / 10% | 0.235 / 10% | 0.236 / 10% | 1046 |
| 2026 | 0.236 / 7% | 0.235 / 9% | 0.231 / 10% | 0.231 / 11% | 388 |

Model coefficients (const, coil, er5, edge, past, instrument-session baseline): -0.016, +0.016, -0.025, +0.002, -0.014, +1.031

