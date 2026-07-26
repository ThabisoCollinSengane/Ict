# AMD × tick-volume — signature + winners-vs-losers deep dive

Every number is a **ratio to the trade's own pre-accumulation baseline** (20 M5 bins before the coil). 1.00× = normal. Split **IS (2022)** vs **OOS (2024)**; winner-vs-loser deltas (`W−L`) only count if they hold in both.
Coverage: 275 AMD trades with tick data (EURUSD/GBPUSD, 2022 + 2024).

## 1. The fingerprint — all AMD trades

| phase | mean | median | n |
|---|---|---|---|
| Accumulation | 0.82× | 0.66× | 275 |
| Run-into-entry | 1.35× | 1.02× | 274 |
| Sweep (M5) | 1.56× | 1.05× | 275 |
| Distribution | 1.81× | 1.22× | 274 |
| PD array | 1.90× | 1.28× | 274 |

## 2. Winners vs losers — the whole path (IS then OOS)

The core question: what do losers do differently? A phase where **WIN beats LOSE in the same direction in BOTH years** is a real filter.

### IS (2022) — n=116 (58 win / 58 lose)

| phase | WIN | LOSE | Δ win−lose |
|---|---|---|---|
| Accumulation | 0.90× | 0.91× | -0.00× |
| Run-into-entry | 1.74× | 1.59× | +0.15× |
| Sweep (M5) | 1.76× | 1.87× | -0.12× |
| Distribution | 2.23× | 2.15× | +0.08× |
| PD array | 2.40× | 2.30× | +0.10× |

### OOS (2024) — n=159 (71 win / 88 lose)

| phase | WIN | LOSE | Δ win−lose |
|---|---|---|---|
| Accumulation | 0.77× | 0.76× | +0.01× |
| Run-into-entry | 1.01× | 1.20× | -0.19× |
| Sweep (M5) | 1.30× | 1.45× | -0.14× |
| Distribution | 1.42× | 1.63× | -0.21× |
| PD array | 1.47× | 1.66× | -0.20× |

## 3. By PD-array type (OB vs FVG)
`sweep W−L` / `PD-array W−L` = winners' minus losers' volume ratio there.

| segment | n | IS WR | OOS WR | sweep W−L | PD-array W−L |
|---|---|---|---|---|---|
| FVG | 180 | 49% | 47% | -0.11× | -0.18× |
| OB | 86 | 45% | 41% | +0.05× | +0.50× |
| breaker | 9 | 100% | 60% | -4.48× | -6.29× |

## 4. By side (buying vs selling)

| segment | n | IS WR | OOS WR | sweep W−L | PD-array W−L |
|---|---|---|---|---|---|
| buy | 100 | 56% | 49% | +0.16× | +0.46× |
| sell | 175 | 47% | 42% | -0.28× | -0.33× |

## 5. By session

| segment | n | IS WR | OOS WR | sweep W−L | PD-array W−L |
|---|---|---|---|---|---|
| london | 121 | 58% | 44% | -0.26× | -0.14× |
| ny | 154 | 42% | 45% | +0.04× | +0.06× |

## 6. Did the sweep run PDH/PDL (previous-day liquidity)?

| segment | n | IS WR | OOS WR | sweep W−L | PD-array W−L |
|---|---|---|---|---|---|
| swept PDH/PDL | 47 | 55% | 53% | -0.08× | -0.38× |
| no prev-day liq | 170 | 46% | 43% | -0.11× | +0.01× |

## 7. Entry in premium vs discount (vs prior-day mid)

| segment | n | IS WR | OOS WR | sweep W−L | PD-array W−L |
|---|---|---|---|---|---|
| premium | 93 | 45% | 44% | +0.24× | +0.41× |
| discount | 124 | 49% | 48% | -0.43× | -0.54× |

## 8. Absorption at the sweep (flow against the raid)

| split | WIN absorb% | LOSE absorb% | n win / n lose |
|---|---|---|---|
| IS | 41% | 50% | 58 / 58 |
| OOS | 48% | 53% | 71 / 88 |

## 9. Read

§2 is the headline — scan for a phase where winners' volume beats losers' in the **same direction in both IS and OOS**. §3–§7 answer *where* it lives (which array / side / session / whether it ran PDH-PDL / premium vs discount): look for a `W−L` that is clearly positive in a high-n segment, consistent across years. Anything that only shows in one year, or only in a small-n (<20) cell, is noise — same discipline as P39.

