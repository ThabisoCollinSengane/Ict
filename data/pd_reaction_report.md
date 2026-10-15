# How does price act at intraday HTF PD arrays (FVG / IFVG / OB)?

Data: **real HistData M1**. Pairs EURUSD, GBPUSD, NZDUSD. IS = 2022-23, OOS = 2024-25.

`respect` = full body closes back out the side price came from; `break` = full body closes through the far side; whichever first within **3** bars of the touch. Excursion over **12** bars FROM the confirmation bar. `ctl` = mirror band (same width, same distance, opposite side of price, inverted orientation). **Read the lift, never the rate.** SE = standard error of the lift; verdict GREEN needs >= 5pp lift in BOTH splits AND medFav > medAdv on respect in both; otherwise RED.

## Coverage (completed bars per split; last bin dropped)

```
  240T  EURUSD IS    3198 OOS    3217  GBPUSD IS    3195 OOS    3217  NZDUSD IS    3198 OOS    3215
   60T  EURUSD IS   11648 OOS   12467  GBPUSD IS   11631 OOS   12467  NZDUSD IS   11639 OOS   12457
   15T  EURUSD IS   46588 OOS   49865  GBPUSD IS   46519 OOS   49863  NZDUSD IS   46526 OOS   49811
```

## 240T

```
zone  row            n  resp%   brk% unres%  resFav  resAdv  brkFav  brkAdv
------------------------------------------------------------------------------
fvg   zone IS     2062   64.2   26.2    9.6    47.2    52.0    54.3    46.4
fvg   zone OOS    1968   66.4   25.1    8.5    38.8    36.5    38.7    36.3
fvg   ctl IS      2058   63.7   26.4   10.0    50.6    47.2    42.2    55.8
fvg   ctl OOS     1968   64.3   26.3    9.3    38.1    38.8    38.5    37.5

ifvg  zone IS      568   61.3   31.9    6.9    61.4    46.5    46.0    57.8
ifvg  zone OOS     526   65.8   26.2    8.0    37.2    37.7    37.3    41.8
ifvg  ctl IS       588   58.5   32.3    9.2    48.0    52.0    41.5    59.6
ifvg  ctl OOS      535   59.1   32.3    8.6    42.1    38.8    40.0    39.0

ob    zone IS      792   62.8   29.4    7.8    51.9    49.2    41.9    53.9
ob    zone OOS     834   64.6   27.5    7.9    38.1    37.8    37.2    39.2
ob    ctl IS       797   63.2   27.5    9.3    50.7    48.0    39.3    51.7
ob    ctl OOS      834   64.5   27.3    8.2    39.3    38.9    38.4    41.5

```

Lifts over control (pp, ± SE):

```
zone        respect IS      respect OOS         break IS        break OOS         retest-hold IS        retest-hold OOS  verdict
fvg         +0.6 ± 1.5       +2.1 ± 1.5       -0.2 ± 1.4       -1.3 ± 1.4    +2.6 ± 3.2 n445/471    +1.5 ± 3.3 n400/409  RED
ifvg        +2.8 ± 2.9       +6.7 ± 3.0       -0.4 ± 2.7       -6.1 ± 2.8    -3.1 ± 5.3 n159/168    -5.2 ± 6.2 n111/136  RED
ob          -0.5 ± 2.4       +0.1 ± 2.3       +1.9 ± 2.3       +0.1 ± 2.2    +1.8 ± 5.0 n189/183    +1.4 ± 4.9 n185/183  RED
```

*retest-hold = after a BREAK, does the broken zone reject price on its first return within 30 bars (breakaway -> IFVG claim)? n = zone/control retests.*

## 60T

```
zone  row            n  resp%   brk% unres%  resFav  resAdv  brkFav  brkAdv
------------------------------------------------------------------------------
fvg   zone IS     7067   65.4   24.7    9.9    24.0    25.6    24.6    24.9
fvg   zone OOS    7432   65.2   25.2    9.7    17.9    17.9    18.4    18.1
fvg   ctl IS      7070   63.7   26.7    9.6    26.0    24.7    24.1    24.8
fvg   ctl OOS     7444   64.9   25.3    9.8    18.5    17.4    17.4    18.4

ifvg  zone IS     1994   65.4   26.4    8.2    24.7    25.3    24.4    25.2
ifvg  zone OOS    2161   65.8   26.1    8.1    18.2    18.1    19.0    17.7
ifvg  ctl IS      1987   61.0   30.3    8.7    24.5    24.7    24.5    24.4
ifvg  ctl OOS     2161   65.8   26.8    7.4    19.0    17.6    19.2    17.4

ob    zone IS     3113   65.2   26.6    8.2    25.2    26.3    23.5    24.1
ob    zone OOS    3383   64.3   26.0    9.7    18.5    17.5    19.1    17.8
ob    ctl IS      3125   63.5   27.0    9.5    26.8    23.4    21.6    27.1
ob    ctl OOS     3404   66.5   24.6    8.9    18.5    17.0    19.2    19.1

```

Lifts over control (pp, ± SE):

```
zone        respect IS      respect OOS         break IS        break OOS         retest-hold IS        retest-hold OOS  verdict
fvg         +1.7 ± 0.8       +0.3 ± 0.8       -2.0 ± 0.7       -0.1 ± 0.7   -1.4 ± 1.8 n1426/1553   +0.4 ± 1.7 n1531/1597  RED
ifvg        +4.3 ± 1.5       +0.0 ± 1.4       -3.9 ± 1.4       -0.8 ± 1.3    -2.6 ± 3.2 n430/496    -2.0 ± 3.1 n463/484  RED
ob          +1.7 ± 1.2       -2.2 ± 1.2       -0.4 ± 1.1       +1.4 ± 1.1    -1.7 ± 2.7 n660/666    -1.2 ± 2.6 n692/674  RED
```

*retest-hold = after a BREAK, does the broken zone reject price on its first return within 30 bars (breakaway -> IFVG claim)? n = zone/control retests.*

## 15T

```
zone  row            n  resp%   brk% unres%  resFav  resAdv  brkFav  brkAdv
------------------------------------------------------------------------------
fvg   zone IS    30547   62.9   26.7   10.4    11.1    11.2    11.2    11.8
fvg   zone OOS   32083   63.7   26.3   10.0     8.1     8.3     8.2     8.9
fvg   ctl IS     30540   63.3   26.6   10.0    11.3    11.2    11.4    12.2
fvg   ctl OOS    32061   64.0   26.7    9.3     8.5     8.2     8.5     9.1

ifvg  zone IS     9463   62.9   28.4    8.7    11.4    11.7    11.5    12.5
ifvg  zone OOS    9813   63.1   28.5    8.3     8.4     8.6     9.0     9.1
ifvg  ctl IS      9445   63.0   28.8    8.2    11.6    11.6    12.3    13.1
ifvg  ctl OOS     9782   64.6   27.0    8.5     8.5     8.6     9.1     9.5

ob    zone IS    13709   65.9   24.3    9.8    11.9    11.6    12.5    12.5
ob    zone OOS   14625   65.9   24.2   10.0     8.7     8.7     9.0     9.7
ob    ctl IS     13697   64.2   26.1    9.7    12.1    11.7    12.6    13.0
ob    ctl OOS    14639   65.1   25.0    9.8     8.9     8.5     9.4    10.1

```

Lifts over control (pp, ± SE):

```
zone        respect IS      respect OOS         break IS        break OOS         retest-hold IS        retest-hold OOS  verdict
fvg         -0.4 ± 0.4       -0.3 ± 0.4       +0.0 ± 0.4       -0.4 ± 0.3   -0.8 ± 0.8 n6818/6657   -0.4 ± 0.8 n7043/7096  RED
ifvg        -0.1 ± 0.7       -1.4 ± 0.7       -0.4 ± 0.7       +1.6 ± 0.6   +2.8 ± 1.5 n2219/2210   +1.2 ± 1.4 n2291/2138  RED
ob          +1.7 ± 0.6       +0.7 ± 0.6       -1.8 ± 0.5       -0.8 ± 0.5   -1.1 ± 1.3 n2700/2826   -1.1 ± 1.3 n2859/2986  RED
```

*retest-hold = after a BREAK, does the broken zone reject price on its first return within 30 bars (breakaway -> IFVG claim)? n = zone/control retests.*

## Verdicts

| TF | zone | verdict | why |
|---|---|---|---|
| 240T | fvg | **RED** | lift +0.6/+2.1pp (< 5pp in a split) |
| 240T | ifvg | **RED** | lift +2.8/+6.7pp (< 5pp in a split) |
| 240T | ob | **RED** | lift -0.5/+0.1pp (< 5pp in a split) |
| 60T | fvg | **RED** | lift +1.7/+0.3pp (< 5pp in a split) |
| 60T | ifvg | **RED** | lift +4.3/+0.0pp (< 5pp in a split) |
| 60T | ob | **RED** | lift +1.7/-2.2pp (< 5pp in a split) |
| 15T | fvg | **RED** | lift -0.4/-0.3pp (< 5pp in a split) |
| 15T | ifvg | **RED** | lift -0.1/-1.4pp (< 5pp in a split) |
| 15T | ob | **RED** | lift +1.7/+0.7pp (< 5pp in a split) |

Measurement only; nothing ships.
