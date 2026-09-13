# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     730
win_rate_pct               43.7
profit_factor              4.01
starting_equity_ZAR        1000
ending_equity_ZAR          142283.1
pnl_ZAR                    141283.1
pnl_pct                    14128.31
max_drawdown_pct           -13.24
avg_win_ZAR                590.18
avg_loss_ZAR               -114.32
withdrawn_total_ZAR        133793.45
withdrawal_count           37
working_balance_ZAR        8489.65
working_max_drawdown_pct   21.58
```

## Gate funnel

```
checks                         120839
in_killzone                    120839
news_clear                     115327
nfp_fomc_ok                    98773
intermarket_signal             5526
pair_matches                   5526
mss_h1_m15_m5_ok               1918
daily_bias_ok                  1918
h1_bias_ok                     1918
h4_bias_ok                     1918
dealing_range_ok               110
consolidation_found            1033
manipulation_correct_dir       908
m5_fvg_correct_dir             1028
target_found                   1028
rr_ok                          1028
units_nonzero                  1028
limit_placed                   0
entry_opened                   718
pyramid_added                  12
pyramid_blocked_min_target     984
drawdown_halt                  2790
daily_loss_halt                1254
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      531
daily_pair_cap                 3145
weekly_amd_confirmed           325
session_handover_closed        2
htf_draw_full_cascade          309
htf_draw_partial               635
htf_draw_counter               343
htf_fvg_5050_hit               34
ote_zone                       5
choch_confirmed                41
low_conviction                 0
judas_divergence               1
ny_continuation                424
pm_gate_pair_news              0
dxy_flat                       74509
dxy_directional                20588
eurgbp_flat                    4585
eurgbp_flat_gbp_blocked        3284
breakout_confirmed             1079
sr_attempted                   82
sr_prev_session_ok             82
sr_enough_bars                 82
sr_consol_found                81
sr_breakout_found              50
session_range_found            64
soj_retest                     575
soj_sweep                      940
golden_rule_no                 504
mstruct_align                  984
phase_ny_judas                 537
gt_pool_sweep                  792
structure_stop_used            959
stop_capped_10pip              755
target_rung_far                330
risk_cap_ok                    718
pyramid_blocked_low_im         2582
eurgbp_directional             11440
soj_judas                      365
crt_turtle_soup                491
golden_rule_yes                469
gt_disp_wick                   755
m1_stop_used                   69
pyramid_blocked_favour         4904
dxy_fvg_room                   155
phase_london_judas             514
gt_macro_window                132
im_score_low                   7614
smt_pair_opposing              112
gt_mp_discount                 179
smt_pair_confirmed             283
mstruct_minor_sweep            133
gt_judas_reversal              113
gt_mp_extreme                  40
ny_continuation_gated          9
london_judas_ny_echo           21
sr_consol_no_sweep             19
sr_fail_no_sweep               6
sr_pdliq_attempted             20
sr_fail_low_swept_no_close_back 9
target_score_sized             452
crt_sweep_sized                181
risk_cap_skip                  310
golden_rule_sized              422
pdliq_sweep_sized              206
htf_fvg_breakout_sized         15
sr_pdliq_width_ok              2
sr_pdliq_sweep                 2
sr_fail_high_swept_no_close_back 3
sr_fail_both_swept             1
pyramid_blocked_no_pattern     6
```

_income: R133,793 across 37 withdrawals · working balance R8,490_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            482   203  42.1%     86410.20   3.62
OB             225   102  45.3%     50626.14   4.97
BREAKER         23    14  60.9%      4246.77   4.47

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            4     3  75.0%   4.46
BREAKER M5            18    10  55.6%   4.38
FVG H1                87    39  44.8%   6.27
FVG M15               78    30  38.5%   3.49
FVG M5               317   134  42.3%   3.04
OB M15                31    18  58.1%   7.60
OB M5                194    84  43.3%   4.66

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            14     8  57.1%   3.88
BREAKER GBPUSD             5     4  80.0%   7.01
BREAKER NZDUSD             4     2  50.0%   3.97
FVG EURUSD               237    98  41.4%   4.06
FVG GBPUSD               218    99  45.4%   3.71
FVG NZDUSD                27     6  22.2%   0.81
OB EURUSD                147    56  38.1%   3.24
OB GBPUSD                 55    35  63.6%  10.80
OB NZDUSD                 23    11  47.8%   8.71
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              2     1  50.0%     348.61   2.29
amd_breaker_m5              12     8  66.7%     190.70   6.30
amd_fvg_h1                  69    32  46.4%     243.25   5.34
amd_fvg_m15                 61    21  34.4%     157.81   2.60
amd_fvg_m5                 281   120  42.7%     144.05   3.12
amd_ob_m15                  21    12  57.1%     201.33   4.33
amd_ob_m5                  157    67  42.7%     200.24   4.27
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     2 100.0%     587.03    inf
mss_breaker_m5               6     2  33.3%       3.81   1.09
mss_fvg_h1                  17     7  41.2%     552.49   9.62
mss_fvg_m15                 14     8  57.1%     459.91  16.57
mss_fvg_m5                  24    11  45.8%     122.87   2.43
mss_ob_m15                  10     6  60.0%     468.55  58.40
mss_ob_m5                   37    17  45.9%     277.69   6.76
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  3     1  33.3%     118.60   5.05
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         3     1  33.3%      -4.32   0.87
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         3     1  33.3%      13.87   1.88
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -18.38   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              660   290  43.9%    131622.91   4.12
session_range           53    24  45.3%     10157.42   3.86
(no AMD)                17     5  29.4%      -497.22   0.59
```

_Session-range widths (n=82): median=44.8 p75=61.5 p90=85.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           283   141  49.8%     72010.34   4.70
against          393   159  40.5%     59508.30   3.58

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               139  45.3%   4.31
EURUSD SHORT against             259  38.2%   3.42
GBPUSD LONG against              134  44.8%   3.97
GBPUSD SHORT golden              144  54.2%   5.04
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          194    85  43.8%     40096.53   4.15
opposing            83    43  51.8%     16681.88   4.98
no divergence      399   172  43.1%     74740.23   3.92
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         511   223  43.6%     87055.28   3.74
3-day        153    69  45.1%     39678.20   5.14
30-day        26    11  42.3%      7555.81   5.14
60-day        40    16  40.0%      6993.81   2.83
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     343   144  42.0%   3.52
near             no     168    79  47.0%   4.60
3-day           yes      98    44  44.9%   5.47
3-day            no      55    25  45.5%   3.97
30-day          yes      20     9  45.0%   4.90
30-day           no       6     2  33.3%   7.82
60-day          yes      33    14  42.4%   2.74
60-day           no       7     2  28.6%   3.72
```

**151 of 219 far-rung trades (69%) were escalated.** High means P20 pushed them out there and de-escalation is the fix; low means the far target was simply the nearest one available, and only skipping or resizing can touch it.

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            471   211  44.8%     94732.13   4.44
OB             111    47  42.3%     29599.01   4.37
none (projection)     148    61  41.2%     16951.96   2.59
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             40    17  42.5%   4.30
near    fib_extension       237   110  46.4%   3.80
near    fvg                  47    16  34.0%   3.61
near    ith_liquidity         4     1  25.0%   1.28
near    itl_liquidity         3     2  66.7% 190.70
near    pdh_pdl              70    30  42.9%   4.04
near    pwh_pwl               9     0   0.0%   0.00
near    round_number         33    15  45.5%   6.88
near    swing                68    32  47.1%   3.74
d3      equal_hl             25    13  52.0%   7.61
d3      fib_extension        73    37  50.7%   5.99
d3      fvg                  13     5  38.5%   2.84
d3      itl_liquidity         4     1  25.0%   0.83
d3      round_number          8     3  37.5%   2.22
d3      swing                27     9  33.3%   2.72
d30     equal_hl              3     2  66.7%   6.15
d30     fib_extension        13     6  46.2%   5.41
d30     itl_liquidity         4     0   0.0%   0.00
d30     swing                 3     1  33.3%   7.50
d60     equal_hl              5     2  40.0%   1.25
d60     fib_extension        26    10  38.5%   3.21
d60     itl_liquidity         3     1  33.3%   0.46
d60     round_number          3     1  33.3%  50.30
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          293   122  41.6%     41348.02   2.93
  on 240T        220    94  42.7%     32027.10   3.16
  on D            73    28  38.4%      9320.92   2.42
clear            437   197  45.1%     99935.08   4.91
```

## Entry vs the DAILY FVG / PD array (P74)

Every entry measured against the day's draw: how far the fill sat from the nearest unmitigated DAILY FVG, and whether that gap points the way we are trading (`with`) or the other way (`against`). Completed daily candles only — the forming bar carries hours that have not happened yet.

**Alignment with the daily FVG:** 284 of 725 (39.2%) entries traded WITH the gap, 441 (60.8%) against it; 5 entries had no daily gap on the chart.

```
Align         Trades  Wins    WR%      P&L ZAR     PF  medDist
----------------------------------------------------------------
with             284   119  41.9%     60993.92   4.16     44.5
against          441   199  45.1%     80658.67   3.98     11.3
```

**Distance from the daily FVG**

```
Dist pips     Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside           189    85  45.0%     37519.95   4.15
0-10              76    30  39.5%      9868.34   2.44
10-25            110    55  50.0%     24234.91   5.09
25-50            135    62  45.9%     32281.43   6.62
50-100           127    56  44.1%     25449.31   3.91
>100              88    30  34.1%     12298.64   2.70
```

**Alignment x where the gap sits** (`ahead` = we travel toward it)

```
Align     Pos        Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
with      inside         35    20  57.1%     15610.43  14.42
with      ahead           1     0   0.0%       -10.41   0.00
with      behind        248    99  39.9%     45393.89   3.51
against   inside        154    65  42.2%     21909.52   3.04
against   ahead         236   113  47.9%     53417.72   5.04
against   behind         51    21  41.2%      5331.43   2.70
```

**Nearest daily PD array of any kind** (fvg / ifvg / ob)

```
Type     Align      Trades  Wins    WR%      P&L ZAR     PF  medDist
--------------------------------------------------------------------
fvg      with          223    90  40.4%     43711.43   3.61     38.9
fvg      against       358   156  43.6%     59334.06   3.61      5.3
ob       with           46    22  47.8%      6297.92   3.39     11.8
ob       against       103    51  49.5%     31939.69   7.58      0.0
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        231   111  48.1%     59426.83   5.58
             60T        194    93  47.9%     46919.96   5.54
             D           37    18  48.6%     12506.86   5.75
down (-1)    all        163    62  38.0%     26430.95   3.44
             60T        144    52  36.1%     20684.11   3.09
             D           19    10  52.6%      5746.83   7.18
none         all        336   146  43.5%     55425.33   3.39

with rev                304   135  44.4%     71834.29   5.41
against                  90    38  42.2%     14023.49   2.86
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             38    13  34.2%      1128.57   1.58
2            173    72  41.6%     26832.81   3.58
3            335   146  43.6%     71125.34   4.21
4            162    73  45.1%     33081.91   4.00
5             21    14  66.7%      8997.84   7.26

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           504  45.2%   4.35      226  40.3%   3.20
NFP week Mon/Tue          77  57.1%   7.98      653  42.1%   3.68
Rate decision             57  43.9%   3.76      673  43.7%   4.03
PD prov (sweep)          634  42.4%   3.49       96  52.1%   8.69
Seasonal lean              0   0.0%   0.00      730  43.7%   4.01
HTF OB Context           212  47.2%   4.85      518  42.3%   3.57
D1 Draw                  658  44.2%   4.16       72  38.9%   2.72
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 5     1  20.0%        29.02   1.12
continuation         207    99  47.8%     62191.07   4.91
(none)               518   219  42.3%     79063.00   3.57

Liq type          Trades    WR%     PF
----------------------------------------
breaker               35  45.7%   3.52
d1_fvg               120  45.0%   4.17
ob                     9  66.7%  48.48
pdhl                  16  37.5%   1.77
w_fvg                 32  56.2%  11.57
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     1  33.3%         5.83   1.03
equal_hl             655   290  44.3%    132576.49   4.18
(none)                72    28  38.9%      8700.78   2.72
```
