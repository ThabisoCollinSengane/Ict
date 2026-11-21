# Which market will deliver? Instrument selector study (P106) — HistData M1, EURUSD, GBPUSD, NSXUSD, SPXUSD, XAUUSD

11,906 instrument-sessions. `move` = 5h directional travel in units of the 20-day average daily range; `amd` = ran one side of the pre-session range, then the other.

## 1. Average outcome by instrument and session

| instrument | session | IS move / amd% | OOS move / amd% | 2026 move / amd% | n IS/OOS/26 |
|---|---|---|---|---|---|
| EURUSD | london | 0.27 / 25% | 0.25 / 17% | 0.23 / 18% | 483/519/193 |
| EURUSD | ny | 0.33 / 20% | 0.32 / 23% | 0.30 / 22% | 483/519/193 |
| GBPUSD | london | 0.28 / 25% | 0.26 / 18% | 0.24 / 19% | 483/519/193 |
| GBPUSD | ny | 0.33 / 19% | 0.32 / 21% | 0.31 / 21% | 483/519/193 |
| NSXUSD | london | 0.15 / 13% | 0.15 / 11% | 0.17 / 5% | 479/516/192 |
| NSXUSD | ny | 0.32 / 40% | 0.33 / 43% | 0.35 / 45% | 479/516/192 |
| SPXUSD | london | 0.17 / 15% | 0.16 / 11% | 0.16 / 5% | 479/516/192 |
| SPXUSD | ny | 0.30 / 34% | 0.32 / 41% | 0.33 / 41% | 479/516/192 |
| XAUUSD | london | 0.20 / 10% | 0.21 / 5% | 0.18 / 1% | 480/517/192 |
| XAUUSD | ny | 0.35 / 31% | 0.34 / 28% | 0.30 / 29% | 480/517/192 |

## 2. Does each predictor rank the outcome? (Spearman, IS / OOS)

| instrument | predictor | vs move IS / OOS | vs amd IS / OOS |
|---|---|---|---|
| EURUSD | coil | +0.05 / +0.13 | -0.23 / -0.25 |
| EURUSD | er5 | +0.04 / -0.03 | +0.00 / +0.03 |
| EURUSD | edge | +0.05 / +0.08 | -0.01 / -0.00 |
| EURUSD | past | +0.03 / +0.06 | +0.03 / -0.01 |
| GBPUSD | coil | +0.05 / +0.10 | -0.22 / -0.22 |
| GBPUSD | er5 | +0.00 / -0.05 | +0.01 / +0.00 |
| GBPUSD | edge | +0.03 / +0.02 | -0.04 / -0.00 |
| GBPUSD | past | +0.01 / +0.04 | +0.06 / +0.02 |
| NSXUSD | coil | +0.04 / +0.20 | -0.21 / -0.21 |
| NSXUSD | er5 | -0.07 / -0.09 | +0.01 / +0.03 |
| NSXUSD | edge | -0.06 / -0.09 | -0.00 / -0.01 |
| NSXUSD | past | +0.30 / +0.31 | +0.26 / +0.26 |
| SPXUSD | coil | +0.08 / +0.22 | -0.24 / -0.24 |
| SPXUSD | er5 | -0.07 / -0.08 | -0.04 / +0.03 |
| SPXUSD | edge | -0.01 / -0.11 | -0.06 / +0.02 |
| SPXUSD | past | +0.24 / +0.28 | +0.18 / +0.24 |
| XAUUSD | coil | +0.09 / +0.08 | -0.26 / -0.20 |
| XAUUSD | er5 | +0.01 / +0.08 | +0.04 / -0.05 |
| XAUUSD | edge | +0.05 / +0.08 | +0.03 / -0.04 |
| XAUUSD | past | +0.21 / +0.14 | +0.17 / +0.19 |

## 3. Selector: pick one instrument per session

Model fitted on IS. Best FIXED choice from IS: london -> GBPUSD, ny -> XAUUSD.

| half | selector move / amd% | fixed best move / amd% | average of all | random pick | sessions |
|---|---|---|---|---|---|
| IS | 0.311 / 24% | 0.315 / 28% | 0.268 / 23% | 0.251 / 22% | 966 |
| OOS | 0.309 / 19% | 0.302 / 23% | 0.268 / 22% | 0.266 / 24% | 1038 |
| 2026 | 0.283 / 19% | 0.273 / 24% | 0.258 / 20% | 0.251 / 22% | 386 |

Model coefficients (const, coil, er5, edge, past, instrument-session baseline): -0.046, +0.036, -0.029, +0.036, -0.004, +1.014

