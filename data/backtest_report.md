# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     696
win_rate_pct               42.8
profit_factor              3.58
starting_equity_ZAR        1000
ending_equity_ZAR          137471.84
pnl_ZAR                    136471.84
pnl_pct                    13647.18
max_drawdown_pct           -13.24
avg_win_ZAR                635.25
avg_loss_ZAR               -132.74
withdrawn_total_ZAR        128173.46
withdrawal_count           35
working_balance_ZAR        9298.38
working_max_drawdown_pct   22.11
```

## Gate funnel

```
checks                         121155
in_killzone                    121155
news_clear                     111053
nfp_fomc_ok                    95655
intermarket_signal             5489
pair_matches                   5489
mss_h1_m15_m5_ok               1965
daily_bias_ok                  1965
h1_bias_ok                     1965
h4_bias_ok                     1965
dealing_range_ok               99
consolidation_found            1093
manipulation_correct_dir       960
m5_fvg_correct_dir             1093
target_found                   1093
rr_ok                          1093
units_nonzero                  1093
limit_placed                   0
entry_opened                   679
pyramid_added                  17
pyramid_blocked_min_target     958
drawdown_halt                  7099
daily_loss_halt                1564
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      465
daily_pair_cap                 2822
weekly_amd_confirmed           358
session_handover_closed        3
htf_draw_full_cascade          309
htf_draw_partial               704
htf_draw_counter               329
htf_fvg_5050_hit               33
ote_zone                       5
choch_confirmed                46
low_conviction                 0
judas_divergence               2
ny_continuation                448
pm_gate_pair_news              0
dxy_flat                       72234
dxy_directional                20134
eurgbp_flat                    4518
eurgbp_flat_gbp_blocked        3210
breakout_confirmed             1124
sr_attempted                   109
sr_prev_session_ok             109
sr_enough_bars                 109
sr_consol_found                108
sr_breakout_found              69
session_range_found            87
soj_retest                     631
soj_sweep                      998
golden_rule_no                 515
mstruct_align                  1034
phase_ny_judas                 564
gt_pool_sweep                  854
structure_stop_used            1030
stop_capped_10pip              811
target_rung_far                329
risk_cap_ok                    679
pyramid_blocked_low_im         2513
eurgbp_directional             11161
soj_judas                      367
crt_turtle_soup                532
golden_rule_yes                533
gt_disp_wick                   793
m1_stop_used                   63
pyramid_blocked_favour         4687
dxy_fvg_room                   155
phase_london_judas             551
gt_macro_window                127
im_score_low                   7334
smt_pair_opposing              117
gt_mp_discount                 178
smt_pair_confirmed             306
mstruct_minor_sweep            131
gt_judas_reversal              116
gt_mp_extreme                  44
ny_continuation_gated          9
london_judas_ny_echo           14
sr_consol_no_sweep             23
sr_fail_no_sweep               6
sr_pdliq_attempted             24
sr_fail_low_swept_no_close_back 9
target_score_sized             415
crt_sweep_sized                188
target_rung_near_sized         695
risk_cap_skip                  414
golden_rule_sized              486
pdliq_sweep_sized              198
htf_fvg_breakout_sized         15
sr_pdliq_width_ok              2
sr_pdliq_sweep                 2
sr_fail_high_swept_no_close_back 6
sr_fail_both_swept             2
pyramid_blocked_no_pattern     6
```

_income: R128,173 across 35 withdrawals · working balance R9,298_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            466   193  41.4%     83011.30   3.22
OB             209    91  43.5%     48361.56   4.41
BREAKER         21    14  66.7%      5098.98   4.92

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            5     4  80.0%   6.07
BREAKER M5            15     9  60.0%   4.02
FVG H1                82    36  43.9%   5.16
FVG M15               74    29  39.2%   4.70
FVG M5               310   128  41.3%   2.50
OB M15                26    15  57.7%   4.93
OB M5                183    76  41.5%   4.35

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            13     9  69.2%   5.96
BREAKER GBPUSD             5     4  80.0%   8.07
BREAKER NZDUSD             3     1  33.3%   2.42
FVG EURUSD               228    93  40.8%   3.27
FVG GBPUSD               212    93  43.9%   3.27
FVG NZDUSD                26     7  26.9%   2.27
OB EURUSD                143    54  37.8%   3.45
OB GBPUSD                 44    26  59.1%   6.20
OB NZDUSD                 22    11  50.0%   9.56
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              2     1  50.0%     348.61   2.29
amd_breaker_m5              10     7  70.0%     226.12   5.37
amd_fvg_h1                  64    29  45.3%     198.99   3.92
amd_fvg_m15                 60    21  35.0%     209.29   3.50
amd_fvg_m5                 272   113  41.5%     129.75   2.50
amd_ob_m15                  17    10  58.8%     210.79   3.61
amd_ob_m5                  147    60  40.8%     220.37   4.03
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     2 100.0%     733.76    inf
mss_breaker_m5               5     2  40.0%       6.55   1.14
mss_fvg_h1                  18     7  38.9%     622.14   9.07
mss_fvg_m15                 11     7  63.6%     589.85 130.21
mss_fvg_m5                  22    11  50.0%     194.67   3.37
mss_ob_m15                   8     4  50.0%     248.29  25.33
mss_ob_m5                   36    16  44.4%     284.39   6.02
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  3     1  33.3%     152.11   5.64
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         7     2  28.6%     -34.50   0.61
pyramid_im0.8_ob_m15         1     1 100.0%     159.84    inf
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         3     1  33.3%      13.87   1.88
pyramid_wamd1.0_breaker_m15       1     1 100.0%     576.09    inf
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -73.32   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              627   268  42.7%    123231.40   3.60
session_range           53    24  45.3%     11750.97   3.56
(no AMD)                16     6  37.5%      1489.47   2.63
```

_Session-range widths (n=109): median=42.5 p75=57.1 p90=80.8 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           261   124  47.5%     62669.18   3.90
against          384   155  40.4%     60927.53   3.19

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               131  45.0%   3.94
EURUSD SHORT against             253  38.3%   3.09
GBPUSD LONG against              131  44.3%   3.42
GBPUSD SHORT golden              130  50.0%   3.86
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          183    81  44.3%     37461.16   4.04
opposing            80    39  48.8%     14690.97   3.43
no divergence      382   159  41.6%     71444.57   3.30
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         460   236  51.3%    140569.88   5.89
3-day        166    49  29.5%      1189.05   1.08
30-day        32     6  18.8%     -2912.36   0.42
60-day        38     7  18.4%     -2374.73   0.53
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     303   152  50.2%   5.78
near             no     157    84  53.5%   6.26
3-day           yes     104    28  26.9%   1.04
3-day            no      62    21  33.9%   1.28
30-day          yes      27     6  22.2%   0.42
30-day           no       5     0   0.0%   0.00
60-day          yes      31     6  19.4%   0.54
60-day           no       7     1  14.3%   0.43
```

**162 of 236 far-rung trades (69%) were escalated.** High means P20 pushed them out there and de-escalation is the fix; low means the far target was simply the nearest one available, and only skipping or resizing can touch it.

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            438   193  44.1%     89464.63   3.94
OB             108    42  38.9%     26616.29   3.57
none (projection)     150    63  42.0%     20390.92   2.69
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             46    27  58.7%  12.21
near    fib_extension       250   135  54.0%   6.67
near    ith_liquidity         3     1  33.3%   2.30
near    pdh_pdl              62    23  37.1%   2.17
near    pwh_pwl               4     1  25.0%   0.76
near    round_number         31    15  48.4%   6.84
near    swing                62    33  53.2%   5.38
d3      equal_hl             27     9  33.3%   1.66
d3      fib_extension        73    21  28.8%   0.76
d3      ith_liquidity         4     0   0.0%   0.00
d3      itl_liquidity         6     2  33.3%   1.40
d3      pdh_pdl               9     4  44.4%  14.84
d3      pwh_pwl               6     1  16.7%   0.14
d3      round_number         11     4  36.4%   1.81
d3      swing                30     8  26.7%   0.98
d30     fib_extension        23     6  26.1%   0.49
d30     itl_liquidity         4     0   0.0%   0.00
d60     fib_extension        26     4  15.4%   0.41
d60     itl_liquidity         4     2  50.0%   4.43
d60     swing                 4     0   0.0%   0.00
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          308   123  39.9%     40592.70   2.60
  on 240T        231    95  41.1%     34008.10   2.95
  on D            77    28  36.4%      6584.60   1.84
clear            388   175  45.1%     95879.14   4.48
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        208    96  46.2%     49597.33   4.44
             60T        176    81  46.0%     40901.52   4.54
             D           32    15  46.9%      8695.81   4.06
down (-1)    all        160    60  37.5%     25457.17   2.99
             60T        141    50  35.5%     18118.52   2.53
             D           19    10  52.6%      7338.65   8.35
none         all        328   142  43.3%     61417.35   3.40

with rev                280   119  42.5%     62729.39   4.33
against                  88    37  42.0%     12325.11   2.47
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             37    13  35.1%      1032.33   1.44
2            168    73  43.5%     31683.92   4.02
3            319   134  42.0%     62354.99   3.40
4            151    65  43.0%     31854.45   3.67
5             20    12  60.0%      9429.52   5.71

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           479  44.1%   4.06      217  40.1%   2.50
NFP week Mon/Tue          74  52.7%   5.94      622  41.6%   3.33
Rate decision             53  39.6%   2.96      643  43.1%   3.63
PD prov (sweep)          607  41.7%   3.12       89  50.6%   8.12
Seasonal lean              0   0.0%   0.00      696  42.8%   3.58
HTF OB Context           198  44.9%   4.23      498  42.0%   3.26
D1 Draw                  623  43.0%   3.54       73  41.1%   3.99
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 4     0   0.0%      -253.97   0.00
continuation         194    89  45.9%     57026.97   4.29
(none)               498   209  42.0%     79698.84   3.26

Liq type          Trades    WR%     PF
----------------------------------------
breaker               36  44.4%   1.84
d1_fvg               108  40.7%   3.70
ob                     9  66.7%  38.73
pdhl                  15  40.0%   1.22
w_fvg                 30  56.7%  12.12
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     1  33.3%         7.28   1.03
equal_hl             620   267  43.1%    122474.90   3.56
(none)                73    30  41.1%     13989.66   3.99
```
