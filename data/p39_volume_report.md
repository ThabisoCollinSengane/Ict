# P39 — Volume-as-Confidence Analysis

**Generated:** 2026-07-26 14:42 UTC  
**Type:** measurement only — no engine changes, nothing shipped  
**Verdict:** **RED (insufficient data)**

---

## 1. Data coverage

_(aggregate phase not run in this invocation — using cached aggregates in `data/p39_agg/`)_

Aggregated M5 bins available per pair:

| pair | M5 bins |
|---|---|
| EURUSD | 131,209 |
| GBPUSD | 118,269 |

| split | years | measured trades |
|---|---|---|
| IS | 2022 | 133 |
| OOS | 2024 | 182 |

## 2. H1 — friction ratio (sweep-bar tick volume)

Friction ratio = ticks on the bar ÷ mean ticks of the previous 20 M5 bars. Buckets: low <0.65×, normal 0.65–1.20×, high 1.20–1.80×, spike >1.80×.

### Sweep bar (proxy: densest bar within 6 bars up to entry)

| bucket | IS n | IS WR | IS meanR | IS medR | OOS n | OOS WR | OOS meanR | OOS medR |
|---|---|---|---|---|---|---|---|---|
| low | 0 | — | — | — | 0 | — | — | — |
| normal | 19 | 57.9% | +0.64 | +0.95 | 28 | 42.9% | +0.93 | +1.98 |
| high | 71 | 47.9% | +0.91 | +0.96 | 82 | 43.9% | +0.84 | +0.96 |
| spike | 43 | 55.8% | +0.74 | +0.96 | 72 | 50.0% | +0.83 | +0.96 |

### Entry bar (unproxied — the M5 bin containing the fill)

| bucket | IS n | IS WR | IS meanR | IS medR | OOS n | OOS WR | OOS meanR | OOS medR |
|---|---|---|---|---|---|---|---|---|
| low | 2 | 0.0% | -1.04 | -1.04 | 7 | 57.1% | +0.51 | +0.95 |
| normal | 41 | 56.1% | +0.93 | +0.96 | 70 | 38.6% | +0.72 | +0.99 |
| high | 55 | 50.9% | +0.94 | +0.96 | 60 | 48.3% | +0.88 | +0.96 |
| spike | 35 | 51.4% | +0.57 | +0.95 | 45 | 53.3% | +1.00 | +2.04 |

### By entry model — the two opposite volume priors

The handover notes sweeps-that-reverse and breakouts-that-continue have opposite expected volume signatures, so these are reported separately rather than pooled.

**entry_model = `breakout`** (n=165)

| bucket | IS n | IS WR | IS meanR | IS medR | OOS n | OOS WR | OOS meanR | OOS medR |
|---|---|---|---|---|---|---|---|---|
| low | 0 | — | — | — | 0 | — | — | — |
| normal | 11 | 72.7% | +0.95 | +0.96 | 8 | 87.5% | +2.16 | +2.21 |
| high | 42 | 47.6% | +1.12 | +0.97 | 36 | 44.4% | +0.86 | +0.95 |
| spike | 27 | 51.9% | +0.89 | +0.95 | 41 | 53.7% | +1.08 | +0.99 |

**entry_model = `judas`** (n=150)

| bucket | IS n | IS WR | IS meanR | IS medR | OOS n | OOS WR | OOS meanR | OOS medR |
|---|---|---|---|---|---|---|---|---|
| low | 0 | — | — | — | 0 | — | — | — |
| normal | 8 | 37.5% | -0.05 | -0.05 | 20 | 25.0% | +0.17 | -1.04 |
| high | 29 | 48.3% | +0.67 | +0.95 | 46 | 43.5% | +0.83 | +0.99 |
| spike | 16 | 62.5% | +0.51 | +0.96 | 31 | 45.2% | +0.58 | +0.96 |

### Per pair

**EURUSD** (n=194)

| bucket | IS n | IS WR | IS meanR | IS medR | OOS n | OOS WR | OOS meanR | OOS medR |
|---|---|---|---|---|---|---|---|---|
| low | 0 | — | — | — | 0 | — | — | — |
| normal | 8 | 62.5% | +0.30 | +0.96 | 19 | 31.6% | +0.15 | -1.04 |
| high | 31 | 45.2% | +0.92 | +0.96 | 55 | 40.0% | +0.59 | +0.96 |
| spike | 29 | 55.2% | +0.72 | +0.96 | 52 | 51.9% | +0.92 | +0.96 |

**GBPUSD** (n=121)

| bucket | IS n | IS WR | IS meanR | IS medR | OOS n | OOS WR | OOS meanR | OOS medR |
|---|---|---|---|---|---|---|---|---|
| low | 0 | — | — | — | 0 | — | — | — |
| normal | 11 | 54.5% | +0.94 | +0.95 | 9 | 66.7% | +1.84 | +2.26 |
| high | 40 | 50.0% | +0.91 | +0.95 | 27 | 51.9% | +1.28 | +2.06 |
| spike | 14 | 57.1% | +0.78 | +0.95 | 20 | 45.0% | +0.60 | +0.99 |

## 3. H2 — directional delta alignment

Ticks classified by bid movement (up = buy-initiated, down = sell-initiated, unchanged = neutral and left unclassified). `aligned` = net delta on the sweep bar agrees with the trade direction.

| delta | IS n | IS WR | IS meanR | IS medR | OOS n | OOS WR | OOS meanR | OOS medR |
|---|---|---|---|---|---|---|---|---|
| aligned | 93 | 46.2% | +0.64 | +0.95 | 133 | 44.4% | +0.80 | +0.96 |
| against | 39 | 66.7% | +1.30 | +0.96 | 48 | 50.0% | +0.94 | +1.48 |
| flat (net 0) | 1 | 0.0% | -1.04 | -1.04 | 1 | 100.0% | +2.18 | +2.18 |

## 4. Cross-tabulation — friction bucket × delta alignment

| bucket | delta | IS n | IS WR | IS meanR | IS medR | OOS n | OOS WR | OOS meanR | OOS medR |
|---|---|---|---|---|---|---|---|---|---|
| normal | aligned | 12 | 50.0% | +0.50 | +0.95 | 22 | 36.4% | +0.88 | +1.49 |
| normal | against | 7 | 71.4% | +0.96 | +0.95 | 6 | 66.7% | +1.11 | +2.10 |
| high | aligned | 49 | 40.8% | +0.76 | +0.95 | 57 | 45.6% | +0.91 | +0.96 |
| high | against | 21 | 66.7% | +1.32 | +0.98 | 24 | 37.5% | +0.59 | +0.97 |
| spike | aligned | 32 | 53.1% | +0.53 | +0.95 | 54 | 46.3% | +0.68 | +0.96 |
| spike | against | 11 | 63.6% | +1.43 | +0.96 | 18 | 61.1% | +1.34 | +2.09 |

## 5. Controls

### Control 1 — friction on non-signal bars

For each measured trade, a same-day M5 bar at least 2h from any signal on that pair. If sweep friction matches this distribution, the signal is noise.

| series | n | p25 | median | p75 | mean |
|---|---|---|---|---|---|
| sweep bars | 315 | 1.29 | 1.55 | 2.08 | 1.92 |
| control bars | 315 | 0.72 | 0.97 | 1.40 | 1.19 |

### Control 2 — effect without the entry-type filter

Pooled across all entry types (above) and broken out per type (below). A real effect should hold across sub-populations; if it appears in only one type, treat it as over-fit.

| entry_type | n | low n | high+spike n | WR low | WR high+spike | Δ |
|---|---|---|---|---|---|---|
| amd_breaker_m5 | 3 | 0 | 3 | — | 66.7% | — |
| amd_fvg_h1 | 25 | 0 | 22 | — | 54.5% | — |
| amd_fvg_m15 | 20 | 0 | 17 | — | 35.3% | — |
| amd_fvg_m5 | 114 | 0 | 97 | — | 45.4% | — |
| amd_ob_m15 | 8 | 0 | 8 | — | 25.0% | — |
| amd_ob_m5 | 64 | 0 | 52 | — | 48.1% | — |
| mss_breaker_h1 | 1 | 0 | 1 | — | 100.0% | — |
| mss_breaker_m15 | 2 | 0 | 2 | — | 100.0% | — |
| mss_breaker_m5 | 4 | 0 | 4 | — | 75.0% | — |
| mss_fvg_h1 | 10 | 0 | 9 | — | 44.4% | — |
| mss_fvg_m15 | 8 | 0 | 7 | — | 71.4% | — |
| mss_fvg_m5 | 25 | 0 | 20 | — | 80.0% | — |
| mss_ob_m15 | 5 | 0 | 5 | — | 20.0% | — |
| mss_ob_m5 | 23 | 0 | 18 | — | 33.3% | — |
| news_fvg_m15 | 1 | 0 | 1 | — | 0.0% | — |
| news_fvg_m5 | 2 | 0 | 2 | — | 50.0% | — |

### Control 3 — hour-of-day confound

Tick volume varies systematically by session. If a bucket is really just "trades in the first hour of London", the effect is a session artefact.

| hour (UTC) | n | median friction | low/normal/high/spike |
|---|---|---|---|
| 07:00 | 51 | 2.05 | 0/2/14/35 |
| 08:00 | 64 | 1.95 | 0/1/28/35 |
| 09:00 | 18 | 1.30 | 0/3/13/2 |
| 11:00 | 48 | 1.24 | 0/21/24/3 |
| 12:00 | 60 | 1.35 | 0/12/39/9 |
| 13:00 | 59 | 1.73 | 0/5/25/29 |
| 14:00 | 15 | 1.51 | 0/3/10/2 |

## 6. Verdict

**RED (insufficient data)**

- IS: insufficient sample (low n=0, high+spike n=114)
- OOS: insufficient sample (low n=0, high+spike n=154)

Decision rules (from the P39 handover): GREEN = ≥5pp WR gap between low and high friction, same sign in IS and OOS, survives control-3, with H2 also stratifying. YELLOW = one split only, or <5pp with consistent sign. RED = <3pp everywhere, sign disagreement, or controls indistinguishable.

## 7. Recommended next action

Close the volume question. Document the null and move on — a well-documented null is a shipped result.

## 8. Honest caveats

- **Sweep-bar identification is a proxy.** The engine does not log which M5 bar was the manipulation sweep, so this uses the densest bar within 6 bars up to the entry bar. That is a *tick-volume-selected* bar, which biases the sweep-bucket distribution upward relative to a structurally-identified sweep. The entry-bar table is the unbiased comparator. Exact attribution requires logging the sweep timestamp in the engine — the clean fix if this goes further.
- **Baseline is local.** The friction denominator is the previous 20 bars, so it partly absorbs the session-volume profile — which is why control 3 matters.
- **Bid-only tick test.** HistData's volume column is zeros, so delta comes from bid movement. The ~34% unchanged-bid ticks are counted neutral, not forced to a side (Lee & Ready 1991).
- **Weekend/holiday gaps** produce sparse baselines; trades whose lookback has fewer than 10 populated bars are skipped rather than measured against a thin denominator.
- **R availability.** True R needs the stop price; rows without it are counted in WR but excluded from mean/median R (see `IS n` vs the R columns).
- **Sample sizes are reported per cell.** Small-n cells (n<20) are shown rather than pooled away — read them as indicative only.

