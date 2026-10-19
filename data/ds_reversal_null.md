# P112c NULL (random walk) — every lift should read ~0

Every number: entry at the candle close, stop beyond its wick. `hitX` = price went X R our way BEFORE reclaiming the wick; `held` = the wick was never reclaimed by 16:00 ET. **lift** = SFP minus an ordinary candle with the same stop size (matched on R/ATR), in percentage points, ± one standard error. Read the lift, not the raw rate.

## All instruments pooled

| group | split | SFP n | SFP hit1 / hit2 / held | ctrl n | ctrl hit1 / hit2 / held | **lift hit1** | **lift hit2** | lift held | SFP med fav R |
|---|---|---|---|---|---|---|---|---|---|
| with | IS | 248 | 50 / 28 / 30% | 2981 | 47 / 27 / 31% | +2.8 ± 3.3 | +1.7 ± 2.9 | -3.2 ± 2.8 | 0.99 |
| against | IS | 224 | 48 / 25 / 27% | 2981 | 47 / 27 / 34% | +1.3 ± 3.4 | -1.5 ± 2.9 | -7.9 ± 3.0 | 0.94 |
| nobias | IS | 244 | 47 / 27 / 33% | 2944 | 48 / 27 / 31% | -0.8 ± 3.3 | +0.5 ± 2.9 | -0.2 ± 3.0 | 0.94 |
| all | IS | 716 | 48 / 27 / 30% | 8906 | 47 / 27 / 32% | +1.1 ± 1.9 | +0.3 ± 1.7 | -3.7 ± 1.7 | 0.94 |

## NULL1

| group | split | SFP n | SFP hit1 / hit2 / held | ctrl n | ctrl hit1 / hit2 / held | **lift hit1** | **lift hit2** | lift held | SFP med fav R |
|---|---|---|---|---|---|---|---|---|---|
| with | IS | 81 | 54 / 33 / 33% | 926 | 47 / 27 / 32% | +8.5 ± 5.8 | +7.2 ± 5.4 | -0.4 ± 5.1 | 1.14 |
| against | IS | 73 | 42 / 25 / 29% | 926 | 49 / 28 / 35% | -5.3 ± 6.1 | -1.4 ± 5.1 | -12.0 ± 5.4 | 0.74 |
| nobias | IS | 87 | 40 / 20 / 32% | 1122 | 47 / 24 / 29% | -5.4 ± 5.4 | -3.3 ± 4.3 | -0.1 ± 5.1 | 0.83 |
| all | IS | 241 | 46 / 26 / 32% | 2974 | 47 / 26 / 32% | -0.9 ± 3.3 | +0.8 ± 2.9 | -3.8 ± 3.0 | 0.91 |

## NULL2

| group | split | SFP n | SFP hit1 / hit2 / held | ctrl n | ctrl hit1 / hit2 / held | **lift hit1** | **lift hit2** | lift held | SFP med fav R |
|---|---|---|---|---|---|---|---|---|---|
| with | IS | 76 | 43 / 28 / 29% | 1008 | 48 / 27 / 32% | -4.4 ± 5.5 | +0.5 ± 5.1 | -6.2 ± 5.1 | 0.75 |
| against | IS | 69 | 51 / 25 / 28% | 1008 | 46 / 27 / 34% | +4.6 ± 6.1 | -1.6 ± 5.2 | -7.6 ± 4.9 | 1.02 |
| nobias | IS | 87 | 47 / 31 / 31% | 952 | 48 / 28 / 31% | -1.0 ± 5.6 | +2.9 ± 5.1 | -0.6 ± 4.9 | 0.96 |
| all | IS | 232 | 47 / 28 / 29% | 2968 | 48 / 27 / 32% | -0.3 ± 3.3 | +0.9 ± 3.0 | -4.6 ± 2.9 | 0.93 |

## NULL3

| group | split | SFP n | SFP hit1 / hit2 / held | ctrl n | ctrl hit1 / hit2 / held | **lift hit1** | **lift hit2** | lift held | SFP med fav R |
|---|---|---|---|---|---|---|---|---|---|
| with | IS | 91 | 51 / 23 / 27% | 1047 | 46 / 25 / 30% | +4.6 ± 5.2 | -1.6 ± 4.5 | -2.7 ± 4.3 | 1.01 |
| against | IS | 82 | 51 / 26 / 26% | 1047 | 47 / 27 / 32% | +4.7 ± 5.5 | -1.3 ± 4.7 | -4.6 ± 4.9 | 1.12 |
| nobias | IS | 70 | 54 / 30 / 36% | 870 | 48 / 27 / 32% | +5.4 ± 6.1 | +2.6 ± 5.3 | +0.7 ± 5.7 | 1.17 |
| all | IS | 243 | 52 / 26 / 29% | 2964 | 47 / 26 / 31% | +4.8 ± 3.3 | -0.5 ± 2.8 | -2.4 ± 2.9 | 1.11 |

## SFP in the bias direction, by swept level (lift vs control in the bias direction)

| level | split | n | hit1 | hit2 | held | lift hit1 | lift hit2 |
|---|---|---|---|---|---|---|---|
| pd | IS | 8 | 50% | 38% | 25% | -15.0 ± 27.3 | +7.1 ± 27.3 |
| pdsw | IS | 26 | 38% | 19% | 19% | -8.7 ± 9.4 | -7.2 ± 7.5 |
| asia | IS | 41 | 54% | 29% | 39% | +6.5 ± 7.5 | +2.7 ± 6.9 |
| london | IS | 173 | 50% | 28% | 29% | +3.6 ± 3.9 | +2.4 ± 3.5 |

## SFP in the bias direction, by SFP close hour (ET), all splits pooled

| close hour | n | hit1 | hit2 | held | lift hit1 |
|---|---|---|---|---|---|
| 8:00 | 120 | 57% | 32% | 32% | +8.1 ± 5.0 |
| 9:00 | 45 | 42% | 24% | 31% | -5.9 ± 7.3 |
| 10:00 | 42 | 43% | 29% | 21% | -5.4 ± 7.6 |
| 11:00 | 20 | 40% | 20% | 25% | -5.2 ± 8.8 |
| 12:00 | 21 | 48% | 14% | 38% | +5.4 ± 10.2 |

R/ATR bucket edges (SFP quintiles): 0.079, 0.108, 0.143, 0.189
