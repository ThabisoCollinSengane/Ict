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

## 3–7. Conditional volume — does high volume mean different things by context?

**This is the P40 test.** `IS entryΔ` / `OOS entryΔ` = winners minus losers mean entry-bar volume, computed **separately per year**. If a context's Δ has the **same sign in both years** (`✅`), high entry volume genuinely means something there (P40 has a basis). If IS and OOS disagree (`✗`), it's a year-flip artifact — the P39 failure mode — and a fixed modifier would be curve-fit. Read the `same sign?` column and the n split first.

### By PD-array type (OB vs FVG)

| segment | n IS/OOS | IS WR | OOS WR | IS entryΔ | OOS entryΔ | same sign? |
|---|---|---|---|---|---|---|
| FVG | 90/90 | 49% | 47% | -0.13× | -0.27× | ✅ |
| OB | 22/64 | 45% | 41% | +1.10× | +0.26× | ✅ |
| breaker | 4/5 | 100% | 60% | — | -6.90× | ✗ |

### By side (buying vs selling)

| segment | n IS/OOS | IS WR | OOS WR | IS entryΔ | OOS entryΔ | same sign? |
|---|---|---|---|---|---|---|
| buy | 43/57 | 56% | 49% | +0.37× | +0.34× | ✅ |
| sell | 73/102 | 47% | 42% | -0.18× | -0.47× | ✅ |

### By session

| segment | n IS/OOS | IS WR | OOS WR | IS entryΔ | OOS entryΔ | same sign? |
|---|---|---|---|---|---|---|
| london | 57/64 | 58% | 44% | +0.01× | -0.49× | ✗ |
| ny | 59/95 | 42% | 45% | +0.22× | -0.01× | ✗ |

### Did the sweep run PDH/PDL (previous-day liquidity)?

| segment | n IS/OOS | IS WR | OOS WR | IS entryΔ | OOS entryΔ | same sign? |
|---|---|---|---|---|---|---|
| swept PDH/PDL | 11/36 | 55% | 53% | -0.40× | -0.38× | ✅ |
| no prev-day liq | 84/86 | 46% | 43% | -0.05× | +0.03× | ✗ |

### Entry in premium vs discount (vs prior-day mid)

| segment | n IS/OOS | IS WR | OOS WR | IS entryΔ | OOS entryΔ | same sign? |
|---|---|---|---|---|---|---|
| premium | 38/55 | 45% | 44% | +0.13× | +0.59× | ✅ |
| discount | 57/67 | 49% | 48% | -0.25× | -0.81× | ✅ |

## 8. Absorption at the sweep (flow against the raid)

| split | WIN absorb% | LOSE absorb% | n win / n lose |
|---|---|---|---|
| IS | 41% | 50% | 58 / 58 |
| OOS | 48% | 53% | 71 / 88 |

## 9. Major-liquidity runs — which pay? (the validated PDH/PDL thread)

What the manipulation swept, ranked. `pwh/pwl` = prior-week high/low, `pdh/pdl` = prior-day, `eqh/eql` = equal highs/lows (engineered), `vah/val` = value area, `none` = a local range edge. **WR above baseline in BOTH years = a real setup-quality signal we can build on.**

| segment | n IS/OOS | IS WR | OOS WR |
|---|---|---|---|
| pwh | 0/1 | — | 0% |
| pwl | 2/1 | 50% | 100% |
| pdh | 5/19 | 80% | 47% |
| pdl | 4/15 | 50% | 53% |
| eqh | 40/44 | 45% | 43% |
| eql | 31/36 | 48% | 42% |
| vah | 4/2 | 50% | 0% |
| val | 0/0 | — | — |
| none | 30/41 | 53% | 46% |

### Major liquidity (weekly / daily / equal H-L) vs none

| segment | n IS/OOS | IS WR | OOS WR |
|---|---|---|---|
| ran MAJOR liq | 82/116 | 49% | 45% |
| no major liq | 34/43 | 53% | 44% |

## 10. Does HIGH volume help WHEN we run major liquidity?

Your point — high volume isn't always a reason to run. Tested only where it should matter: on trades that swept major liquidity. Entry-bar volume bucketed. If high-volume major-liq runs win MORE in both years, volume is conviction here, not a warning — a size-UP case, not a size-down.

| segment | n IS/OOS | IS WR | OOS WR |
|---|---|---|---|
| low <0.9 | 12/49 | 50% | 47% |
| normal 0.9-1.3 | 15/24 | 53% | 33% |
| high >1.3 | 55/42 | 47% | 50% |

## 11. Beneficial-entry recipe — major liquidity × context

Where the major-liquidity edge concentrates (major-liq trades only).

**× session**

| segment | n IS/OOS | IS WR | OOS WR |
|---|---|---|---|
| london | 38/46 | 61% | 41% |
| ny | 44/70 | 39% | 47% |

**× premium/discount**

| segment | n IS/OOS | IS WR | OOS WR |
|---|---|---|---|
| premium | 32/52 | 47% | 40% |
| discount | 50/64 | 50% | 48% |

**× PD-array type**

| segment | n IS/OOS | IS WR | OOS WR |
|---|---|---|---|
| FVG | 62/68 | 45% | 47% |
| OB | 16/45 | 50% | 42% |
| breaker | 4/3 | 100% | 33% |

## 12. Read

**Two questions in this report:**

1. **P40 (conditional volume) — §3–§7.** Read the `same sign?` column. A context (OB/FVG/session/zone) with `✅` in a high-n row means high entry volume genuinely means something different there in both years → P40 has a basis. Mostly `✗` → the 'conditional edge' was a 2022/2024 flip and a fixed modifier would be curve-fit (drop it).

2. **The liquidity edge — §9–§11 (the real thread).** §9: which liquidity the sweep ran, WR per type. A type (esp. PWH/PWL, PDH/PDL) with WR above the ~45% baseline in BOTH years is a genuine setup-quality signal → build a conviction/size lever, validate on the full backtest (IS/OOS, MaxDD-neutral). §10 answers your 'high volume isn't always bad' point directly — if high-volume major-liq runs win more both years, that's a size-UP case. §11 shows where the edge concentrates (session/zone/array) for the recipe.

Discipline throughout: consistent across both years, n≥~20 per cell, or it's noise — same bar as P39.

