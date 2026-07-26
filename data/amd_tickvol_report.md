# AMD × tick-volume signature

**Type:** measurement only.  Each number is a **ratio to the trade's own pre-accumulation baseline** (mean ticks/M5-bin over the 20 bins before the coil). 1.00× = normal; <1 = quieter; >1 = busier.
Coverage: 275 AMD trades with tick data (EURUSD/GBPUSD, 2022 + 2024).

## 1. The fingerprint — all AMD trades

| phase | mean ratio | median | n |
|---|---|---|---|
| Accumulation (coil) | 0.82× | 0.66× | 275 |
| Manipulation (Judas sweep) | 1.74× | 1.26× | 275 |
| Distribution (entry→exit) | 1.81× | 1.22× | 274 |
| PD array (OB/FVG entry) | 1.90× | 1.28× | 274 |

ICT expectation: accumulation **quiet (<1×)**, the Judas sweep **spikes (>1×)**, distribution **elevated**, PD-array mitigation shows a **reaction**.

## 2. Winners vs losers — does the fingerprint differ?

This is the edge: if winning trades spike harder on the sweep, or fill the PD array on higher volume, that's a tradeable filter.

### IS (2022) — n=116

| phase | WIN mean | LOSE mean | Δ (win−lose) |
|---|---|---|---|
| Accumulation | 0.90× | 0.91× | -0.00× |
| Sweep | 1.97× | 2.03× | -0.07× |
| Distribution | 2.23× | 2.15× | +0.08× |
| PD array | 2.40× | 2.30× | +0.10× |

### OOS (2024) — n=159

| phase | WIN mean | LOSE mean | Δ (win−lose) |
|---|---|---|---|
| Accumulation | 0.77× | 0.76× | +0.01× |
| Sweep | 1.48× | 1.60× | -0.12× |
| Distribution | 1.42× | 1.63× | -0.21× |
| PD array | 1.47× | 1.66× | -0.20× |

## 3. Directional delta at the sweep — absorption

`absorption` = net tick flow on the sweep ran **against** the sweep direction (buyers soaking up a sell-sweep). ICT says that's the real reversal. Shown as % of trades with absorption, winners vs losers.

| split | WIN absorb% | LOSE absorb% | n win / n lose |
|---|---|---|---|
| IS | 50% | 50% | 58 / 58 |
| OOS | 48% | 48% | 71 / 88 |

## 4. Per pair

**EURUSD** (n=175)

| phase | mean ratio | median | n |
|---|---|---|---|
| Accumulation (coil) | 0.75× | 0.62× | 175 |
| Manipulation (Judas sweep) | 1.63× | 1.18× | 175 |
| Distribution (entry→exit) | 1.64× | 1.16× | 175 |
| PD array (OB/FVG entry) | 1.75× | 1.14× | 175 |

**GBPUSD** (n=100)

| phase | mean ratio | median | n |
|---|---|---|---|
| Accumulation (coil) | 0.95× | 0.75× | 100 |
| Manipulation (Judas sweep) | 1.93× | 1.36× | 100 |
| Distribution (entry→exit) | 2.11× | 1.50× | 99 |
| PD array (OB/FVG entry) | 2.17× | 1.65× | 99 |

## 5. Read

First confirm the shape matches ICT theory (quiet coil → sweep spike → elevated distribution). Then look at §2: a phase where **winners' ratio beats losers' in BOTH IS and OOS** is a real volume filter — e.g. if real sweeps spike higher, gate/size on sweep volume; if winners fill the PD array on higher volume, that's an entry-quality signal. Same discipline as P39: consistent across both years, or it's noise. Small-n cells (n<20) are indicative only.

