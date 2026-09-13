# HistData backtest — 2024–2025 (2 yr)

## Results

```
trades                     384
win_rate_pct               44.3
profit_factor              4.33
starting_equity_ZAR        1000
ending_equity_ZAR          76631.46
pnl_ZAR                    75631.46
pnl_pct                    7563.15
max_drawdown_pct           -9.59
avg_win_ZAR                578.31
avg_loss_ZAR               -105.99
withdrawn_total_ZAR        68141.8
withdrawal_count           16
working_balance_ZAR        8489.65
working_max_drawdown_pct   17.12
```

## Gate funnel

```
checks                         60936
in_killzone                    60936
news_clear                     58702
nfp_fomc_ok                    50597
intermarket_signal             2592
pair_matches                   2592
mss_h1_m15_m5_ok               922
daily_bias_ok                  922
h1_bias_ok                     922
h4_bias_ok                     922
dealing_range_ok               74
consolidation_found            534
manipulation_correct_dir       456
m5_fvg_correct_dir             530
target_found                   530
rr_ok                          530
units_nonzero                  530
limit_placed                   0
entry_opened                   381
pyramid_added                  3
pyramid_blocked_min_target     682
drawdown_halt                  1032
daily_loss_halt                458
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      316
daily_pair_cap                 1180
weekly_amd_confirmed           154
session_handover_closed        0
htf_draw_full_cascade          157
htf_draw_partial               343
htf_draw_counter               157
htf_fvg_5050_hit               29
ote_zone                       3
choch_confirmed                30
low_conviction                 0
judas_divergence               0
ny_continuation                226
pm_gate_pair_news              0
dxy_flat                       39206
dxy_directional                9895
eurgbp_directional             5103
im_score_low                   3474
breakout_confirmed             509
soj_retest                     329
soj_sweep                      486
crt_turtle_soup                259
golden_rule_no                 262
mstruct_align                  501
phase_ny_judas                 283
gt_pool_sweep                  397
gt_disp_wick                   388
structure_stop_used            491
stop_capped_10pip              345
risk_cap_ok                    381
pyramid_blocked_favour         3123
eurgbp_flat                    2683
eurgbp_flat_gbp_blocked        1938
golden_rule_yes                229
phase_london_judas             258
gt_mp_discount                 85
gt_mp_extreme                  21
soj_judas                      157
mstruct_minor_sweep            63
london_judas_ny_echo           15
pyramid_blocked_low_im         1640
smt_pair_opposing              41
target_rung_far                197
sr_attempted                   43
sr_prev_session_ok             43
sr_enough_bars                 43
sr_consol_found                43
sr_breakout_found              30
session_range_found            36
gt_macro_window                69
smt_pair_confirmed             139
m1_stop_used                   39
dxy_fvg_room                   91
gt_judas_reversal              57
sr_consol_no_sweep             8
sr_fail_high_swept_no_close_back 2
sr_pdliq_attempted             8
target_score_sized             225
golden_rule_sized              201
crt_sweep_sized                96
sr_fail_low_swept_no_close_back 4
pdliq_sweep_sized              110
risk_cap_skip                  149
htf_fvg_breakout_sized         15
pyramid_blocked_no_pattern     6
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
ny_continuation_gated          3
sr_fail_no_sweep               2
```

_income: R68,142 across 16 withdrawals · working balance R8,490_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            222    92  41.4%     36201.16   3.43
OB             148    69  46.6%     36061.19   5.92
BREAKER         14     9  64.3%      3369.11   8.29

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER M15            2     2 100.0%    inf
BREAKER M5            12     7  58.3%   5.18
FVG H1                52    25  48.1%   6.59
FVG M15               40    16  40.0%   2.75
FVG M5               130    51  39.2%   2.67
OB M15                20    12  60.0%   6.70
OB M5                128    57  44.5%   5.75

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             7     5  71.4% 136.49
BREAKER GBPUSD             3     2  66.7%   7.27
BREAKER NZDUSD             4     2  50.0%   3.97
FVG EURUSD               120    50  41.7%   3.83
FVG GBPUSD                87    38  43.7%   3.40
FVG NZDUSD                15     4  26.7%   1.03
OB EURUSD                101    42  41.6%   4.89
OB GBPUSD                 31    21  67.7%   6.72
OB NZDUSD                 16     6  37.5%   9.73
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     1 100.0%    1238.34    inf
amd_breaker_m5               9     6  66.7%     215.85   5.68
amd_fvg_h1                  38    19  50.0%     255.42   6.58
amd_fvg_m15                 31    11  35.5%     154.37   2.43
amd_fvg_m5                 115    43  37.4%      94.42   2.48
amd_ob_m15                  13     6  46.2%     237.23   3.44
amd_ob_m5                  107    47  43.9%     202.50   5.20
mss_breaker_m15              1     1 100.0%     199.80    inf
mss_breaker_m5               3     1  33.3%      -3.89   0.75
mss_fvg_h1                  14     6  42.9%     435.01   6.59
mss_fvg_m15                  8     5  62.5%     273.48   6.84
mss_fvg_m5                  12     6  50.0%     184.63   3.71
mss_ob_m15                   7     6  85.7%     593.14 719.22
mss_ob_m5                   21    10  47.6%     340.86   8.83
news_fvg_m5                  1     1 100.0%     443.68    inf
pyramid_im0.8_fvg_m5         1     0   0.0%      -1.48   0.00
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         1     1 100.0%      88.80    inf
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              352   157  44.6%     73801.00   4.53
session_range           25    12  48.0%      1953.99   2.34
(no AMD)                 7     1  14.3%      -123.53   0.62
```

_Session-range widths (n=43): median=28.6 p75=48.2 p90=52.7 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           145    73  50.3%     33749.30   4.53
against          204    85  41.7%     31941.30   4.03

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                85  47.1%   4.58
EURUSD SHORT against             143  39.9%   4.23
GBPUSD LONG against               61  45.9%   3.66
GBPUSD SHORT golden               60  55.0%   4.47
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           88    36  40.9%     16163.86   3.97
opposing            40    24  60.0%     13113.27   8.27
no divergence      221    98  44.3%     36413.47   3.84
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         261   117  44.8%     44767.45   4.21
3-day         91    42  46.2%     27921.01   5.94
30-day        15     5  33.3%      -437.32   0.71
60-day        17     6  35.3%      3380.32   3.13
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     181    75  41.4%   3.68
near             no      80    42  52.5%   6.64
3-day           yes      61    30  49.2%   6.74
3-day            no      30    12  40.0%   1.97
30-day          yes      11     4  36.4%   0.69
30-day           no       4     1  25.0%   0.88
60-day          yes      14     5  35.7%   3.59
60-day           no       3     1  33.3%   1.41
```

**86 of 123 far-rung trades (70%) were escalated.** High means P20 pushed them out there and de-escalation is the fix; low means the far target was simply the nearest one available, and only skipping or resizing can touch it.

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            238   107  45.0%     46920.42   4.45
OB              64    26  40.6%     14402.97   4.38
none (projection)      82    37  45.1%     14308.06   3.97
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             20     7  35.0%   3.27
near    fib_extension       118    58  49.2%   4.67
near    fvg                  17     6  35.3%   4.48
near    pdh_pdl              47    19  40.4%   4.40
near    pwh_pwl               5     0   0.0%   0.00
near    round_number         13     7  53.8%  14.87
near    swing                37    17  45.9%   3.57
d3      equal_hl             13     7  53.8%   9.35
d3      fib_extension        41    23  56.1%   7.39
d3      fvg                  10     4  40.0%   1.43
d3      itl_liquidity         7     2  28.6%   4.47
d3      round_number          7     4  57.1%   5.29
d3      swing                12     2  16.7%   0.45
d30     fib_extension        10     4  40.0%   0.61
d30     itl_liquidity         3     1  33.3%  14.21
d60     equal_hl              3     1  33.3%   0.51
d60     fib_extension        12     4  33.3%   4.35
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          184    78  42.4%     25996.78   3.28
  on 240T        143    57  39.9%     18694.92   3.19
  on D            41    21  51.2%      7301.86   3.53
clear            200    92  46.0%     49634.68   5.41
```

## Entry vs the DAILY FVG / PD array (P74)

Every entry measured against the day's draw: how far the fill sat from the nearest unmitigated DAILY FVG, and whether that gap points the way we are trading (`with`) or the other way (`against`). Completed daily candles only — the forming bar carries hours that have not happened yet.

**Alignment with the daily FVG:** 153 of 368 (41.6%) entries traded WITH the gap, 215 (58.4%) against it; 16 entries had no daily gap on the chart.

```
Align         Trades  Wins    WR%      P&L ZAR     PF  medDist
----------------------------------------------------------------
with             153    61  39.9%     28831.90   4.10     47.2
against          215   102  47.4%     46891.02   4.70      8.3
```

**Distance from the daily FVG**

```
Dist pips     Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside            99    42  42.4%     15016.82   3.56
0-10              46    21  45.7%      6973.19   2.54
10-25             54    27  50.0%     14227.68   5.69
25-50             60    30  50.0%     19533.19   7.30
50-100            69    30  43.5%     13197.53   5.15
>100              40    13  32.5%      6774.51   3.95
```

**Alignment x where the gap sits** (`ahead` = we travel toward it)

```
Align     Pos        Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
with      inside         21    11  52.4%      6202.40   8.51
with      behind        132    50  37.9%     22629.49   3.67
against   inside         78    31  39.7%      8814.41   2.75
against   ahead         111    57  51.4%     34114.17   7.50
against   behind         26    14  53.8%      3962.44   2.65
```

**Nearest daily PD array of any kind** (fvg / ifvg / ob)

```
Type     Align      Trades  Wins    WR%      P&L ZAR     PF  medDist
--------------------------------------------------------------------
fvg      with          133    48  36.1%     19535.73   3.21     42.6
fvg      against       176    74  42.0%     29573.78   3.52      5.0
ifvg     with            2     0   0.0%        -2.96   0.00      6.0
ifvg     against         1     0   0.0%        -4.27   0.00      0.0
ob       with           22    13  59.1%      4452.16   5.47     23.6
ob       against        45    32  71.1%     21934.57  22.08      0.0
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        112    57  50.9%     27584.62   5.09
             60T         95    49  51.6%     21256.52   5.00
             D           17     8  47.1%      6328.11   5.41
down (-1)    all         86    39  45.3%     19314.59   5.00
             60T         76    34  44.7%     17578.15   5.08
             D           10     5  50.0%      1736.44   4.29
none         all        186    74  39.8%     28732.25   3.59

with rev                151    74  49.0%     36197.07   5.40
against                  47    22  46.8%     10702.14   4.19
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
1             14     7  50.0%      2194.61   3.35
2             85    34  40.0%     13779.77   4.48
3            182    83  45.6%     36916.63   4.65
4             91    40  44.0%     17381.66   3.69
5             12     6  50.0%      5358.79   5.40

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           278  45.3%   4.18      106  41.5%   4.93
NFP week Mon/Tue          47  53.2%   6.56      337  43.0%   4.04
Rate decision             28  53.6%  10.15      356  43.5%   4.16
PD prov (sweep)          323  41.8%   3.72       61  57.4%   8.22
Seasonal lean              0   0.0%   0.00      384  44.3%   4.33
HTF OB Context           129  45.0%   4.86      255  43.9%   3.96
D1 Draw                  349  44.4%   4.33       35  42.9%   4.34
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
continuation         129    58  45.0%     36292.15   4.86
(none)               255   112  43.9%     39339.31   3.96

Liq type          Trades    WR%     PF
----------------------------------------
breaker               17  41.2%   5.56
d1_fvg                73  41.1%   4.88
ob                     3 100.0%    inf
pdhl                  16  56.2%   1.46
w_fvg                 20  45.0%   6.73
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 2     0   0.0%      -191.89   0.00
equal_hl             347   155  44.7%     70028.49   4.37
(none)                35    15  42.9%      5794.86   4.34
```
