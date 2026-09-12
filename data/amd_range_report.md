# AMD Range & Sweep Analysis -your live price action reference

_804 base-algo trades analysed. All values in pips._

## 1. Consolidation range (accumulation) -how wide is the coil?

This is the M15 range the algo detected before the Judas sweep.

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| ALL trades | 732 | 24.6 | 23.8 | 17.8 | 30.8 | 11.9 | 33.5 | 3.7 | 35.0 |

### By pair

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 408 | 24.6 | 23.8 | 17.6 | 30.8 | 12.8 | 33.5 | 3.7 | 35.0 |
| GBPUSD | 270 | 24.7 | 23.9 | 18.6 | 30.8 | 11.2 | 33.6 | 5.6 | 34.9 |
| NZDUSD | 54 | 25.6 | 23.4 | 15.1 | 31.3 | 11.5 | 33.8 | 6.6 | 35.0 |

### By session

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| London | 366 | 24.5 | 23.4 | 16.4 | 30.8 | 11.5 | 33.5 | 3.7 | 35.0 |
| Ny | 366 | 24.8 | 24.3 | 19.2 | 30.8 | 12.8 | 33.6 | 3.7 | 35.0 |

### Winners vs Losers

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| Winners | 331 | 24.7 | 24.6 | 19.7 | 31.4 | 13.6 | 33.7 | 3.7 | 35.0 |
| Losers | 401 | 24.6 | 23.1 | 15.6 | 30.5 | 11.1 | 33.5 | 3.7 | 35.0 |

## 2. Judas sweep depth -how far does the stop-hunt go?

Pips beyond the range extreme that the manipulation wick reaches.

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| ALL trades | 732 | 4.1 | 8.3 | 1.6 | 10.5 | 0.6 | 21.4 | 0.1 | 117.5 |

### By pair

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 408 | 3.2 | 6.8 | 1.2 | 7.7 | 0.5 | 17.5 | 0.1 | 93.1 |
| GBPUSD | 270 | 6.5 | 11.1 | 2.5 | 14.3 | 1.1 | 25.6 | 0.1 | 117.5 |
| NZDUSD | 54 | 3.0 | 5.9 | 0.9 | 6.5 | 0.4 | 13.2 | 0.1 | 62.7 |

### By session

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| London | 366 | 3.7 | 7.2 | 1.3 | 9.2 | 0.5 | 19.2 | 0.1 | 67.4 |
| Ny | 366 | 4.5 | 9.4 | 1.9 | 13.3 | 0.7 | 23.4 | 0.1 | 117.5 |

### Winners vs Losers

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| Winners | 331 | 4.2 | 8.4 | 1.7 | 10.5 | 0.5 | 21.3 | 0.1 | 117.5 |
| Losers | 401 | 3.9 | 8.2 | 1.4 | 10.5 | 0.6 | 21.4 | 0.1 | 93.1 |

## 3. Range duration (M15 bars) -how long does accumulation last?

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| ALL trades | 732 | 25.0 | 32.0 | 13.0 | 45.0 | 10.0 | 65.0 | 8.0 | 96.0 |

### By session

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| London | 366 | 24.0 | 30.8 | 13.0 | 43.0 | 10.0 | 63.0 | 8.0 | 96.0 |
| Ny | 366 | 26.0 | 33.3 | 14.0 | 48.0 | 10.0 | 66.0 | 8.0 | 96.0 |

## 4. Judas reversal vs Breakout -range & sweep comparison

The Judas sweep closes BACK inside (fake). The breakout closes BEYOND and holds (real).

### Judas model

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| judas -range | 345 | 26.0 | 24.7 | 19.1 | 31.4 | 12.9 | 33.7 | 6.4 | 35.0 |
| judas -sweep | 345 | 3.6 | 7.2 | 1.3 | 9.0 | 0.5 | 17.5 | 0.1 | 62.7 |

### Breakout model

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| breakout -range | 387 | 23.9 | 23.0 | 16.4 | 30.4 | 11.1 | 33.5 | 3.7 | 34.9 |
| breakout -sweep | 387 | 4.5 | 9.3 | 1.9 | 12.3 | 0.7 | 23.5 | 0.1 | 117.5 |

## 5. Pair x Session detail -your quick-reference card

### EURUSD

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| London range | 194 | 24.2 | 23.3 | 16.4 | 30.8 | 11.9 | 33.5 | 3.7 | 34.9 |
| London sweep | 194 | 3.5 | 6.4 | 1.1 | 8.0 | 0.4 | 15.6 | 0.1 | 67.4 |
| Ny range | 214 | 24.6 | 24.3 | 19.2 | 30.8 | 13.7 | 33.5 | 3.7 | 35.0 |
| Ny sweep | 214 | 2.9 | 7.1 | 1.2 | 7.6 | 0.6 | 18.2 | 0.1 | 93.1 |

### GBPUSD

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| London range | 118 | 24.6 | 23.4 | 17.8 | 30.8 | 11.2 | 33.5 | 5.6 | 34.9 |
| London sweep | 118 | 4.8 | 8.9 | 1.8 | 13.0 | 0.6 | 22.7 | 0.2 | 61.2 |
| Ny range | 152 | 24.8 | 24.3 | 19.6 | 30.9 | 11.2 | 33.7 | 6.8 | 34.9 |
| Ny sweep | 152 | 8.3 | 12.7 | 3.6 | 16.5 | 1.9 | 27.3 | 0.1 | 117.5 |

### NZDUSD

| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| London range | 54 | 25.6 | 23.4 | 15.1 | 31.3 | 11.5 | 33.8 | 6.6 | 35.0 |
| London sweep | 54 | 3.0 | 5.9 | 0.9 | 6.5 | 0.4 | 13.2 | 0.1 | 62.7 |
| Ny range | 0 | - | - | - | - | - | - | - | - |
| Ny sweep | 0 | - | - | - | - | - | - | - | - |

## 6. Your live trading thresholds (from the data)

- **Typical consolidation**: 24.6 pips (median), most are 17.8-30.8 pips
- If range > 33.5 pips -> unusually wide, expect a bigger move or skip (extended)
- **Typical Judas sweep**: 4.1 pips beyond the range
- Most sweeps are 1.6-10.5 pips deep
- If price goes > 21.4 pips beyond the range -> likely a BREAKOUT, not a Judas fake

- **Judas sweeps** (fakes) median: 3.6 pips beyond range
- **Breakouts** (real) median: 4.5 pips beyond range
- **The gap**: breakouts travel ~0.9 pips MORE than Judas fakes
- Rule of thumb: if price holds > 17.5 pips beyond the range -> it's probably a breakout, not a sweep

## 7. How to use this live

1. **Mark the M15 consolidation range** -expect it to be ~24.6 pips wide
2. **Wait for the sweep** -price pokes 4.1 pips beyond one side
3. **If it closes back inside** -> Judas fake, fade it (your best setup)
4. **If it holds beyond 17.5 pips** -> breakout, follow it (need triple confirmation: EU+GU+DXY)
5. **Stop goes beyond the sweep extreme** -the M1 ITH/ITL one tier up

