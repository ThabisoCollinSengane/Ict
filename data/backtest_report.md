# HistData backtest — 2022–2025 (2 yr)

## Results

```
Trades                     300
```

## Gate funnel

```
entry_opened                   300
```

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
other          300   150  50.0%     22500.00   2.50

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
other ?              300   150  50.0%   2.50

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
other EURUSD             300   150  50.0%   2.50
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
fvg_m5                     300   150  50.0%      75.00   2.50
```

## Entry vs the DAILY FVG / PD array (P74)

Every entry measured against the day's draw: how far the fill sat from the nearest unmitigated DAILY FVG, and whether that gap points the way we are trading (`with`) or the other way (`against`). Completed daily candles only — the forming bar carries hours that have not happened yet.

**Alignment with the daily FVG: 143 of 223 (64.1%) entries traded WITH the gap, 80 (35.9%) against it; 77 entries had no daily gap on the chart.

```
Align         Trades  Wins    WR%      P&L ZAR     PF  medDist
----------------------------------------------------------------
with             143    76  53.1%     12300.00   2.84      5.8
against           80    38  47.5%      5300.00   2.26     15.5
```

**Distance from the daily FVG**

```
Dist pips     Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside            76    41  53.9%      6750.00   2.93
0-10              33    15  45.5%      1950.00   2.08
10-25             31    17  54.8%      2850.00   3.04
25-50             36    21  58.3%      3750.00   3.50
50-100            16     6  37.5%       500.00   1.50
>100              31    14  45.2%      1800.00   2.06
```

**Alignment x where the gap sits** (`ahead` = we travel toward it)

```
Align     Pos        Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
with      inside         55    33  60.0%      6050.00   3.75
with      ahead          39    21  53.8%      3450.00   2.92
with      behind         49    22  44.9%      2800.00   2.04
against   inside         21     8  38.1%       700.00   1.54
against   ahead          34    14  41.2%      1500.00   1.75
against   behind         25    16  64.0%      3100.00   4.44
```

**Nearest daily PD array of any kind** (fvg / ifvg / ob)

```
Type     Align      Trades  Wins    WR%      P&L ZAR     PF  medDist
--------------------------------------------------------------------
fvg      with           39    18  46.2%      2400.00   2.14      5.4
fvg      against        27    13  48.1%      1850.00   2.32     15.8
ifvg     with           51    27  52.9%      4350.00   2.81     15.2
ifvg     against        26    13  50.0%      1950.00   2.50     10.6
ob       with           53    31  58.5%      5550.00   3.52     15.0
ob       against        27    12  44.4%      1500.00   2.00     15.5
```
