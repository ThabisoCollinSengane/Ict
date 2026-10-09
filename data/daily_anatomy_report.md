# What the DAILY timeframe does

Measured on raw UTC daily candles built the way the engine builds them (HistData EST +5h). Session labels are New York time, as the killzones are.

## 1. Shape — how far does a day travel?

```
pair     split  days    p25  median    p75  body/rng  close pos  closed >=80% or <=20%
--------------------------------------------------------------------------------------
EURUSD   IS      519   60.5    81.0  109.2      0.48       0.48                  48.2%
EURUSD   OOS     521   46.2    61.9   85.6      0.45       0.48                  41.8%
GBPUSD   IS      519   76.1    99.9  135.2      0.46       0.49                  44.5%
GBPUSD   OOS     521   58.4    77.3  101.6      0.45       0.52                  45.9%
NZDUSD   IS      519   50.1    64.1   85.3      0.46       0.46                  44.5%
NZDUSD   OOS     521   36.7    46.6   60.9      0.48       0.47                  47.2%
```

`body/rng` is how much of the day's travel the candle keeps. A low number means the average day round-trips — it goes somewhere and comes back — which is the single most important fact for target selection.

## 2. Timing — when do the daily HIGH and LOW print?

Share of days whose extreme printed in each session (New York time). A flat profile would put ~33% in asia (9h), ~17% london (4h), ~21% ny_am (5h), ~17% ny_pm (4h) purely on clock time, so compare against the HOURS column, not against each other.

```
pair     split     n    asia(9h)  london(4h)   ny_am(5h)    noon(1h)   ny_pm(4h)
------------------------------------------------------------------------------
EURUSD   IS      519       30.8%       20.4%       27.4%        6.0%       15.4%   <- high
EURUSD   IS      519       31.2%       18.3%       27.4%        5.8%       17.3%   <- low
EURUSD   OOS     521       34.7%       16.7%       31.9%        5.4%       11.3%   <- high
EURUSD   OOS     521       30.5%       15.9%       33.4%        5.6%       14.6%   <- low
GBPUSD   IS      519       32.2%       20.0%       27.7%        3.9%       16.2%   <- high
GBPUSD   IS      519       27.7%       19.7%       31.8%        4.6%       16.2%   <- low
GBPUSD   OOS     521       33.4%       16.1%       30.9%        6.3%       13.2%   <- high
GBPUSD   OOS     521       32.6%       18.8%       31.1%        5.4%       12.1%   <- low
NZDUSD   IS      519       41.6%       13.9%       23.9%        3.7%       17.0%   <- high
NZDUSD   IS      519       43.9%       10.8%       27.7%        3.7%       13.9%   <- low
NZDUSD   OOS     521       48.6%       10.4%       25.7%        3.3%       12.1%   <- high
NZDUSD   OOS     521       51.2%       10.7%       22.1%        3.8%       12.1%   <- low
```

## 3. The daily Judas — running the 00:00 UTC open

Did price trade at least **20.0 pips** through the daily open **within the first 12 UTC hours** (00:00 UTC is 19:00 ET, so that is Asia plus London), and then close the other way? `base` and then close back through it? **`placebo` is the control** — the identical question asked of a meaningless level (a quarter of the previous day's range from the open, side alternating by date). The unconditional close rate is NOT a valid control here: on a driftless walk a day that ran the low early tends to STAY there, which reads about −30pp with no institution involved. Only the lift over the placebo says the OPEN is special. The early window is load-bearing too — measured across the whole day, running a side merely selects days that ENDED that way (−43pp on the same fixture).

```
pair     split case        days    back   placebo      n     lift
--------------------------------------------------------------------
EURUSD   IS    ran_low      188   28.7%     26.6%    222   +2.1pp
EURUSD   IS    ran_high     194   28.9%     26.3%    217   +2.6pp
EURUSD   IS    ran_both      89   49.4%     48.4%     62   +1.1pp
EURUSD   OOS   ran_low      172   18.0%     22.4%    205   -4.4pp
EURUSD   OOS   ran_high     168   22.0%     21.7%    207   +0.3pp
EURUSD   OOS   ran_both      36   52.8%     50.0%     54   +2.8pp
GBPUSD   IS    ran_low      170   24.7%     22.8%    206   +1.9pp
GBPUSD   IS    ran_high     156   21.2%     24.3%    185   -3.2pp
GBPUSD   IS    ran_both     174   46.6%     50.8%    122   -4.3pp
GBPUSD   OOS   ran_low      196   28.1%     24.3%    222   +3.7pp
GBPUSD   OOS   ran_high     203   23.6%     19.9%    211   +3.7pp
GBPUSD   OOS   ran_both      73   47.9%     50.7%     73   -2.7pp
NZDUSD   IS    ran_low      179   19.0%     24.9%    217   -5.9pp
NZDUSD   IS    ran_high     207   24.2%     26.2%    210   -2.0pp
NZDUSD   IS    ran_both      65   49.2%     40.0%     65   +9.2pp
NZDUSD   OOS   ran_low      168   20.2%     20.0%    210   +0.2pp
NZDUSD   OOS   ran_high     155   19.4%     15.6%    192   +3.7pp
NZDUSD   OOS   ran_both      13   61.5%     60.0%     15   +1.5pp
```

`ran_both` is the day that ran BOTH sides of its open — reported separately rather than folded into one side, because folding it is how a Judas rate gets inflated.

## 4. What is LEFT — the mechanism P67 needs

From the close of each hour, the median pips price still travels before the UTC day ends: `up`/`dn` in each direction and `fav` the better of the two. **A target further away than `fav` is asking for more than a typical day gives from that hour** — which would make the far rung's PF<1 a reachability problem, not a quality one.

### EURUSD IS

```
ET hr      up      dn     fav  session
------------------------------------------
    0    30.3    33.8    59.5  asia
    1    30.8    32.7    59.8  asia
    2    30.9    33.3    59.2  asia
    3    31.0    32.6    56.3  london
    4    29.0    32.3    52.4  london
    5    25.4    30.9    51.9  london
    6    25.2    30.2    47.6  london
    7    26.8    27.8    46.3  ny_am
    8    27.3    27.5    42.7  ny_am
    9    25.6    26.5    41.1  ny_am
   10    22.9    23.7    33.7  ny_am
   11    18.9    20.2    29.4  ny_am
   12    15.6    15.2    21.6  noon
   13    12.8    12.4    17.7  ny_pm
   14     9.9    10.1    14.1  ny_pm
   15     8.4     7.4    11.1  ny_pm
   16     5.9     5.4     8.2  ny_pm
   17     5.4     3.7     6.6  asia
   18     3.9     4.0     5.9  asia
   19     5.9     5.9     9.2  asia
   20    33.1    34.5    63.5  asia
   21    32.5    34.5    60.8  asia
   22    32.0    33.4    61.6  asia
   23    31.0    32.9    60.1  asia
```

### EURUSD OOS

```
ET hr      up      dn     fav  session
------------------------------------------
    0    27.3    25.5    45.3  asia
    1    24.8    25.2    46.9  asia
    2    25.2    24.3    44.0  asia
    3    25.3    24.1    41.9  london
    4    25.3    24.9    39.5  london
    5    23.2    22.2    38.2  london
    6    21.2    22.3    37.2  london
    7    21.2    20.6    35.0  ny_am
    8    21.5    19.2    34.0  ny_am
    9    20.0    19.4    30.6  ny_am
   10    17.0    17.9    25.9  ny_am
   11    15.2    15.0    21.8  ny_am
   12    12.1    12.0    17.9  noon
   13    10.0     9.3    14.0  ny_pm
   14     7.8     8.1    11.0  ny_pm
   15     6.3     6.5     8.8  ny_pm
   16     5.2     4.8     6.9  ny_pm
   17     4.5     4.1     5.9  asia
   18     3.6     3.7     5.4  asia
   19     4.4     5.8     7.3  asia
   20    25.7    26.0    49.2  asia
   21    24.9    28.0    47.7  asia
   22    25.8    25.6    46.9  asia
   23    25.5    25.9    46.3  asia
```

### GBPUSD IS

```
ET hr      up      dn     fav  session
------------------------------------------
    0    40.7    44.4    72.9  asia
    1    39.3    44.8    71.9  asia
    2    40.1    44.7    70.0  asia
    3    40.9    40.0    67.9  london
    4    38.2    42.1    63.2  london
    5    34.6    38.1    61.5  london
    6    34.3    35.0    57.7  london
    7    34.1    33.4    56.3  ny_am
    8    34.0    33.4    53.2  ny_am
    9    30.7    31.6    48.8  ny_am
   10    28.0    28.3    42.7  ny_am
   11    24.9    23.6    34.9  ny_am
   12    19.2    20.1    29.0  noon
   13    15.4    16.4    22.3  ny_pm
   14    12.8    13.3    18.6  ny_pm
   15    10.2     9.9    15.0  ny_pm
   16     7.8     7.6    11.0  ny_pm
   17     7.3     5.5     9.3  asia
   18     5.1     6.0     8.3  asia
   19     7.0     7.6    11.8  asia
   20    40.9    47.4    77.6  asia
   21    41.2    45.7    74.9  asia
   22    40.1    46.2    73.6  asia
   23    38.9    46.0    73.4  asia
```

### GBPUSD OOS

```
ET hr      up      dn     fav  session
------------------------------------------
    0    33.0    30.2    56.5  asia
    1    33.0    28.8    56.2  asia
    2    32.4    29.9    55.0  asia
    3    31.9    29.2    51.9  london
    4    31.2    27.9    49.4  london
    5    28.6    27.2    48.0  london
    6    25.5    25.1    45.3  london
    7    26.6    25.9    42.2  ny_am
    8    26.0    23.5    41.6  ny_am
    9    23.8    23.9    38.1  ny_am
   10    21.8    22.5    33.7  ny_am
   11    19.7    18.2    26.7  ny_am
   12    14.8    14.8    21.7  noon
   13    12.4    12.3    17.1  ny_pm
   14     9.7    10.5    14.4  ny_pm
   15     7.4     9.4    12.0  ny_pm
   16     6.6     7.1     9.6  ny_pm
   17     6.0     5.8     8.2  asia
   18     5.2     5.0     7.7  asia
   19     4.9     6.8     8.8  asia
   20    32.2    31.0    60.6  asia
   21    33.3    30.8    59.6  asia
   22    34.0    29.6    57.9  asia
   23    32.0    29.3    56.7  asia
```

### NZDUSD IS

```
ET hr      up      dn     fav  session
------------------------------------------
    0    25.3    26.2    43.2  asia
    1    24.3    25.7    42.7  asia
    2    23.9    26.3    40.0  asia
    3    24.0    26.0    40.2  london
    4    21.1    24.4    38.7  london
    5    20.3    23.1    37.9  london
    6    20.3    22.6    34.4  london
    7    21.1    22.2    35.6  ny_am
    8    20.3    22.2    33.3  ny_am
    9    19.4    20.9    30.5  ny_am
   10    17.5    19.1    26.6  ny_am
   11    15.3    16.5    23.0  ny_am
   12    12.8    13.5    20.0  noon
   13    10.6    12.1    16.6  ny_pm
   14     8.9    11.2    14.4  ny_pm
   15     7.4     9.4    12.3  ny_pm
   16     6.5     7.6     9.7  ny_pm
   17     7.1     5.3     9.1  asia
   18     4.5     6.9     8.5  asia
   19     6.3     7.3     9.6  asia
   20    28.7    30.2    47.5  asia
   21    27.2    28.5    47.0  asia
   22    26.7    26.2    44.5  asia
   23    26.3    26.5    44.5  asia
```

### NZDUSD OOS

```
ET hr      up      dn     fav  session
------------------------------------------
    0    16.6    19.1    31.0  asia
    1    16.8    18.0    30.0  asia
    2    16.0    17.9    29.1  asia
    3    16.0    18.3    27.5  london
    4    16.2    16.7    27.2  london
    5    15.1    15.7    26.4  london
    6    14.2    15.2    25.9  london
    7    14.5    14.4    24.6  ny_am
    8    13.8    14.3    23.7  ny_am
    9    13.2    14.1    22.1  ny_am
   10    12.3    13.5    19.2  ny_am
   11    10.5    11.5    16.5  ny_am
   12     8.5    10.2    13.6  noon
   13     7.6     8.8    12.2  ny_pm
   14     6.1     8.0    10.5  ny_pm
   15     5.1     7.4     9.1  ny_pm
   16     4.4     7.1     8.0  ny_pm
   17     4.5     5.9     7.5  asia
   18     4.0     5.3     6.9  asia
   19     4.3     5.2     7.0  asia
   20    19.2    21.3    36.0  asia
   21    19.2    20.2    34.3  asia
   22    18.0    19.0    32.4  asia
   23    18.0    18.7    31.3  asia
```

## 5. Target demand — every real target against what was left

Each trade's target distance divided by the median `fav` for its pair, split and entry hour. If demand explains outcomes better than the rung does, the lever is choosing targets against what is left — not removing trades, which has never survived the full run here (P8 −R31M, P10, P9's −20.15%).

```
split demand      trades  wins    WR%      PF
--------------------------------------------
IS    <=0.5x          19    13  68.4%   25.99
IS    0.5-1.0x       305   124  40.7%    2.83
IS    1.0-1.5x        26    13  50.0%    4.72
IS    >1.5x            5     3  60.0%   12.03
OOS   0.5-1.0x       223   114  51.1%    5.37
OOS   1.0-1.5x       139    52  37.4%    4.13
OOS   >1.5x           19     4  21.1%    0.53
```

Demand x rung (does demand say anything the rung does not?):

```
split demand     rung    trades    WR%      PF
----------------------------------------------
IS    <=0.5x     near        16  62.5%   17.98
IS    <=0.5x     d3           2 100.0%     inf
IS    <=0.5x     d30          1 100.0%     inf
IS    0.5-1.0x   near       221  39.8%    2.46
IS    0.5-1.0x   d3          56  42.9%    3.31
IS    0.5-1.0x   d30          8  50.0%   59.62
IS    0.5-1.0x   d60         20  40.0%    3.28
IS    1.0-1.5x   near        19  52.6%    6.83
IS    1.0-1.5x   d3           2   0.0%    0.00
IS    1.0-1.5x   d30          2  50.0%    6.08
IS    1.0-1.5x   d60          3  66.7%    0.21
IS    >1.5x      near         4  50.0%    6.33
IS    >1.5x      d3           1 100.0%     inf
OOS   0.5-1.0x   near       156  51.9%    5.32
OOS   0.5-1.0x   d3          52  51.9%    6.76
OOS   0.5-1.0x   d30          7  42.9%    4.42
OOS   0.5-1.0x   d60          8  37.5%    2.22
OOS   1.0-1.5x   near        93  36.6%    2.94
OOS   1.0-1.5x   d3          31  41.9%   11.21
OOS   1.0-1.5x   d30          8  37.5%    2.82
OOS   1.0-1.5x   d60          7  28.6%    2.82
OOS   >1.5x      near         8  12.5%    0.20
OOS   >1.5x      d3           7  28.6%    0.52
OOS   >1.5x      d30          1   0.0%    0.00
OOS   >1.5x      d60          3  33.3%    1.61
```

---

Measurement only; nothing ships. The result to act on, if there is one, is §4/§5: a target the day cannot reach is a target-SELECTION problem, and target selection is the one axis that has validated here.
