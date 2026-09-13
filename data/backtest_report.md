# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     355
win_rate_pct               43.1
profit_factor              3.37
starting_equity_ZAR        1000
ending_equity_ZAR          48420.98
pnl_ZAR                    47420.98
pnl_pct                    4742.1
max_drawdown_pct           -13.24
avg_win_ZAR                440.81
avg_loss_ZAR               -99.12
withdrawn_total_ZAR        41433.25
withdrawal_count           16
working_balance_ZAR        6987.73
working_max_drawdown_pct   21.89
```

## Gate funnel

```
checks                         59299
in_killzone                    59299
news_clear                     56523
nfp_fomc_ok                    48468
intermarket_signal             2934
pair_matches                   2934
mss_h1_m15_m5_ok               1003
daily_bias_ok                  1003
h1_bias_ok                     1003
h4_bias_ok                     1003
dealing_range_ok               33
consolidation_found            482
manipulation_correct_dir       434
m5_fvg_correct_dir             482
target_found                   482
rr_ok                          482
units_nonzero                  482
limit_placed                   0
entry_opened                   346
pyramid_added                  9
pyramid_blocked_min_target     309
drawdown_halt                  1510
daily_loss_halt                556
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      218
daily_pair_cap                 1950
weekly_amd_confirmed           166
session_handover_closed        2
htf_draw_full_cascade          130
htf_draw_partial               298
htf_draw_counter               194
htf_fvg_5050_hit               8
ote_zone                       2
choch_confirmed                12
low_conviction                 0
judas_divergence               2
ny_continuation                201
pm_gate_pair_news              0
dxy_flat                       35603
dxy_directional                10697
eurgbp_flat                    1952
eurgbp_flat_gbp_blocked        1400
breakout_confirmed             583
sr_attempted                   42
sr_prev_session_ok             42
sr_enough_bars                 42
sr_consol_found                41
sr_breakout_found              21
session_range_found            30
soj_retest                     238
soj_sweep                      434
golden_rule_no                 230
mstruct_align                  467
phase_ny_judas                 252
gt_pool_sweep                  388
structure_stop_used            451
stop_capped_10pip              392
target_rung_far                126
risk_cap_ok                    346
pyramid_blocked_low_im         994
eurgbp_directional             6299
soj_judas                      196
crt_turtle_soup                224
golden_rule_yes                242
gt_disp_wick                   354
m1_stop_used                   31
pyramid_blocked_favour         1810
dxy_fvg_room                   57
phase_london_judas             242
gt_macro_window                63
im_score_low                   4099
smt_pair_opposing              59
gt_mp_discount                 92
smt_pair_confirmed             153
mstruct_minor_sweep            71
gt_judas_reversal              51
gt_mp_extreme                  18
ny_continuation_gated          6
london_judas_ny_echo           7
sr_consol_no_sweep             12
sr_fail_no_sweep               4
sr_pdliq_attempted             13
sr_fail_low_swept_no_close_back 5
target_score_sized             130
crt_sweep_sized                77
risk_cap_skip                  136
golden_rule_sized              203
pdliq_sweep_sized              66
htf_fvg_breakout_sized         2
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
sr_fail_high_swept_no_close_back 2
sr_fail_both_swept             1
```

_income: R41,433 across 16 withdrawals · working balance R6,988_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            262   110  42.0%     35110.04   3.30
OB              83    37  44.6%     11334.84   3.72
BREAKER         10     6  60.0%       976.09   2.69

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            2     1  50.0%   1.80
BREAKER M5             7     4  57.1%  14.19
FVG H1                39    15  38.5%   3.41
FVG M15               38    15  39.5%   5.36
FVG M5               185    80  43.2%   3.02
OB M15                12     6  50.0%  11.51
OB M5                 71    31  43.7%   3.54

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             8     4  50.0%   0.89
BREAKER GBPUSD             2     2 100.0%    inf
FVG EURUSD               117    48  41.0%   3.74
FVG GBPUSD               133    59  44.4%   3.15
FVG NZDUSD                12     3  25.0%   1.45
OB EURUSD                 50    16  32.0%   1.41
OB GBPUSD                 25    15  60.0%  15.42
OB NZDUSD                  8     6  75.0%  43.57
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     0   0.0%    -541.12   0.00
amd_breaker_m5               4     3  75.0%      95.89  24.04
amd_fvg_h1                  33    14  42.4%     176.13   4.00
amd_fvg_m15                 29    10  34.5%     110.72   3.35
amd_fvg_m5                 164    74  45.1%     139.18   3.28
amd_ob_m15                   9     6  66.7%     118.64  58.58
amd_ob_m5                   55    23  41.8%     103.60   2.63
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              1     1 100.0%     974.25    inf
mss_breaker_m5               3     1  33.3%      31.73   5.84
mss_fvg_h1                   5     1  20.0%     -43.60   0.42
mss_fvg_m15                  7     4  57.1%     337.16  61.75
mss_fvg_m5                  12     5  41.7%      61.10   1.59
mss_ob_m15                   3     0   0.0%     -25.28   0.00
mss_ob_m5                   16     8  50.0%     290.30   9.18
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  2     0   0.0%     -43.94   0.00
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         2     1  50.0%      -4.63   0.90
pyramid_im1.0_fvg_m5         2     0   0.0%     -23.59   0.00
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -18.38   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              315   136  43.2%     43959.16   3.54
session_range           29    12  41.4%      2264.89   2.08
(no AMD)                11     5  45.5%      1196.92   2.91
```

_Session-range widths (n=42): median=57.3 p75=80.8 p90=95.8 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           141    67  47.5%     25471.15   4.07
against          194    77  39.7%     19757.55   2.82

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                56  42.9%   2.71
EURUSD SHORT against             119  37.0%   2.82
GBPUSD LONG against               75  44.0%   2.83
GBPUSD SHORT golden               85  50.6%   4.98
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          108    48  44.4%     18348.38   3.85
opposing            44    20  45.5%      3345.88   3.37
no divergence      183    76  41.5%     23534.43   3.09
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         260   110  42.3%     30308.60   3.03
3-day         61    27  44.3%      9149.54   4.25
30-day        11     6  54.5%      4435.66  17.39
60-day        23    10  43.5%      3527.17   2.74
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     168    69  41.1%   2.97
near             no      92    41  44.6%   3.22
3-day           yes      33    13  39.4%   3.70
3-day            no      28    14  50.0%   5.30
30-day          yes       8     5  62.5%  17.90
30-day           no       3     1  33.3%   9.50
60-day          yes      19     9  47.4%   2.50
60-day           no       4     1  25.0%  34.78
```

**60 of 95 far-rung trades (63%) were escalated.** High means P20 pushed them out there and de-escalation is the fix; low means the far target was simply the nearest one available, and only skipping or resizing can touch it.

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            212    95  44.8%     34181.85   4.41
OB              47    20  42.6%      7405.81   2.80
none (projection)      96    38  39.6%      5833.32   1.99
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             17     9  52.9%   2.35
near    fib_extension       157    65  41.4%   3.24
near    ith_liquidity         3     0   0.0%   0.00
near    pdh_pdl              28    12  42.9%   3.81
near    pwh_pwl               4     1  25.0%   0.83
near    round_number         22    10  45.5%   4.93
near    swing                29    13  44.8%   2.97
d3      equal_hl              7     5  71.4%  23.89
d3      fib_extension        37    15  40.5%   2.80
d3      round_number          4     1  25.0%   2.36
d3      swing                11     5  45.5%   5.04
d30     fib_extension         8     5  62.5%  19.24
d60     fib_extension        18     7  38.9%   1.98
d60     round_number          3     1  33.3%  50.30
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          130    54  41.5%     16108.84   2.84
  on 240T         96    43  44.8%     13492.39   3.31
  on D            34    11  32.4%      2616.45   1.89
clear            225    99  44.0%     31312.14   3.78
```

## Entry vs the DAILY FVG / PD array (P74)

Every entry measured against the day's draw: how far the fill sat from the nearest unmitigated DAILY FVG, and whether that gap points the way we are trading (`with`) or the other way (`against`). Completed daily candles only — the forming bar carries hours that have not happened yet.

**Alignment with the daily FVG:** 142 of 355 (40.0%) entries traded WITH the gap, 213 (60.0%) against it.

```
Align         Trades  Wins    WR%      P&L ZAR     PF  medDist
----------------------------------------------------------------
with             142    61  43.0%     23968.65   3.72     47.4
against          213    92  43.2%     23452.33   3.09     14.8
```

**Distance from the daily FVG**

```
Dist pips     Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside            81    39  48.1%     14680.78   4.25
0-10              29     9  31.0%      1687.15   2.15
10-25             56    28  50.0%      7569.61   4.41
25-50             75    33  44.0%     12364.86   6.62
50-100            65    30  46.2%     11388.60   3.22
>100              49    14  28.6%      -270.03   0.94
```

**Alignment x where the gap sits** (`ahead` = we travel toward it)

```
Align     Pos        Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
with      inside         13     7  53.8%      5517.46  17.56
with      ahead           1     0   0.0%       -10.41   0.00
with      behind        128    54  42.2%     18461.60   3.18
against   inside         68    32  47.1%      9163.32   3.19
against   ahead         120    53  44.2%     12918.57   3.06
against   behind         25     7  28.0%      1370.44   2.88
```

**Nearest daily PD array of any kind** (fvg / ifvg / ob)

```
Type     Align      Trades  Wins    WR%      P&L ZAR     PF  medDist
--------------------------------------------------------------------
fvg      with          111    51  45.9%     22155.49   4.12     44.5
fvg      against       174    80  46.0%     22221.80   3.56     11.1
ob       with           24     8  33.3%        64.14   1.05     10.9
ob       against        46    14  30.4%      2979.55   2.04      0.0
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        122    53  43.4%     22639.71   5.63
             60T        103    43  41.7%     17098.31   5.62
             D           19    10  52.6%      5541.40   5.65
down (-1)    all         77    23  29.9%      3848.41   1.69
             60T         73    21  28.8%      2659.64   1.48
             D            4     2  50.0%      1188.76  28.34
none         all        156    77  49.4%     20932.86   3.19

with rev                159    61  38.4%     24897.38   4.44
against                  40    15  37.5%      1590.74   1.50
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             26     7  26.9%      -100.39   0.93
2             91    41  45.1%     13073.66   4.18
3            156    63  40.4%     20116.20   2.94
4             72    33  45.8%     11153.34   3.82
5              9     8  88.9%      3061.53  15.01

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           232  44.8%   4.04      123  39.8%   2.19
NFP week Mon/Tue          32  62.5%   4.66      323  41.2%   3.25
Rate decision             30  36.7%   1.20      325  43.7%   3.73
PD prov (sweep)          318  43.1%   3.19       37  43.2%   5.35
Seasonal lean              0   0.0%   0.00      355  43.1%   3.37
HTF OB Context            85  50.6%   5.13      270  40.7%   2.84
D1 Draw                  312  43.3%   3.40       43  41.9%   3.18
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 5     1  20.0%        73.77   1.36
continuation          80    42  52.5%     19051.62   5.30
(none)               270   110  40.7%     28295.58   2.84

Liq type          Trades    WR%     PF
----------------------------------------
breaker               20  50.0%   2.80
d1_fvg                48  50.0%   5.05
ob                     5  60.0%  24.57
pdhl                   6  33.3%   0.56
w_fvg                  6  66.7%  64.86
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 1     1 100.0%       197.72    inf
equal_hl             311   134  43.1%     41504.06   3.38
(none)                43    18  41.9%      5719.20   3.18
```
