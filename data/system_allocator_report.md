# Three systems — pick the most probable per session? (P109)

1207 trades from 4 dump(s). R = profit / initial risk (proxy: per-unit move / 80th-pct losing move per pair-year (~ a full stop)).

## Each system by session (n / WR / avg R / PF in R)

| system | session | IS | OOS | 2026 |
|---|---|---|---|---|
| FX | London | 212 / 45% / +0.61 / 3.08 | 211 / 44% / +0.67 / 3.69 | 55 / 33% / +0.46 / 2.47 |
| FX | NY | 212 / 40% / +0.55 / 2.85 | 220 / 41% / +0.63 / 3.32 | 76 / 39% / +0.50 / 2.67 |
| Gold | London | 20 / 10% / -0.28 / 0.55 | 5 / 20% / +1.13 / 2.59 | 1 / 100% / +2.18 / nan |
| Gold | NY | 11 / 18% / -0.10 / 0.73 | 7 / 14% / +0.20 / 1.55 | 2 / 0% / -0.67 / 0.00 |
| Indices | London | 63 / 41% / +5.78 / 7.64 | 25 / 40% / +1.22 / 5.17 | 1 / 0% / -0.04 / 0.00 |
| Indices | NY | 44 / 43% / +3.88 / 11.98 | 40 / 40% / +0.74 / 2.66 | 2 / 50% / -0.24 / 0.62 |

IS-best system per session: London -> Indices, NY -> Indices
Slots with more than one system trading: 152 of 888.

## Rules (total R / trades / PF / max drawdown in R)

| rule | IS | OOS | 2026 |
|---|---|---|---|
| all | +773.3R / 562 / 4.65 / 42.6 | +345.5R / 508 / 3.42 / 6.4 | +63.7R / 137 / 2.49 / 6.2 |
| fixed | +534.8R / 107 / 8.60 / 41.5 | +60.0R / 65 / 3.39 / 5.1 | -0.5R / 3 / 0.60 / 1.2 |
| pick | +706.6R / 442 / 4.97 / 41.6 | +278.4R / 437 / 3.24 / 5.4 | +61.1R / 132 / 2.48 / 5.0 |
| quality | +433.0R / 449 / 3.48 / 40.8 | +284.9R / 443 / 3.38 / 5.1 | +61.4R / 132 / 2.46 / 6.1 |
| sizeup | +907.1R / 562 / 4.95 / 53.0 | +360.5R / 508 / 3.42 / 7.6 | +63.6R / 137 / 2.48 / 6.5 |
| random (control) | median +469.9R (5-95%: +331.8..+617.4) | median +278.5R (5-95%: +260.0..+296.2) | median +60.7R (5-95%: +58.9..+62.2) |

## Daily R correlation between systems (days both traded)

```
sys        FX  Gold  Indices
sys                         
FX       1.00  0.09     0.06
Gold     0.09  1.00      NaN
Indices  0.06   NaN     1.00
```

