# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     533
win_rate_pct               53.1
profit_factor              7.5
starting_equity_ZAR        1000
ending_equity_ZAR          166052.65
pnl_ZAR                    165052.65
pnl_pct                    16505.27
max_drawdown_pct           -6.83
avg_win_ZAR                673.0
avg_loss_ZAR               -101.63
withdrawn_total_ZAR        156552.54
withdrawal_count           41
working_balance_ZAR        9500.11
working_max_drawdown_pct   14.77
```

## Gate funnel

```
checks                         123410
in_killzone                    123410
news_clear                     121438
nfp_fomc_ok                    104122
intermarket_signal             7457
pair_matches                   7457
mss_h1_m15_m5_ok               2863
daily_bias_ok                  2863
h1_bias_ok                     2863
h4_bias_ok                     2863
dealing_range_ok               138
consolidation_found            1910
manipulation_correct_dir       1716
m5_fvg_correct_dir             1919
target_found                   1919
rr_ok                          1919
units_nonzero                  697
limit_placed                   0
entry_opened                   524
pyramid_added                  9
pyramid_blocked_min_target     907
drawdown_halt                  0
daily_loss_halt                491
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      262
daily_pair_cap                 2664
weekly_amd_confirmed           483
session_handover_closed        3
htf_draw_full_cascade          388
htf_draw_partial               1377
htf_draw_counter               358
htf_fvg_5050_hit               52
ote_zone                       12
choch_confirmed                70
low_conviction                 0
judas_divergence               2
ny_continuation                814
pm_gate_pair_news              0
dxy_flat                       78024
dxy_directional                23172
eurgbp_flat                    5603
eurgbp_flat_gbp_blocked        3499
breakout_confirmed             1782
sr_attempted                   178
sr_prev_session_ok             178
sr_enough_bars                 178
sr_consol_found                177
sr_breakout_found              124
session_range_found            144
soj_retest                     1153
soj_sweep                      1746
golden_rule_no                 1031
mstruct_align                  1811
phase_ny_judas                 1037
gt_pool_sweep                  1491
structure_stop_used            1826
stop_capped_10pip              1399
target_rung_far                1222
target_rung_skipped            1222
risk_cap_ok                    524
eurgbp_directional             12697
soj_judas                      593
crt_turtle_soup                789
golden_rule_yes                743
gt_disp_wick                   1351
m1_stop_used                   93
target_deescalated             858
smt_pair_confirmed             494
dxy_fvg_room                   363
phase_london_judas             907
gt_macro_window                199
im_score_low                   7950
pyramid_blocked_favour         3311
pyramid_blocked_low_im         1718
smt_pair_opposing              188
gt_mp_discount                 200
mstruct_minor_sweep            221
gt_judas_reversal              223
gt_mp_extreme                  40
london_judas_ny_echo           7
sr_consol_no_sweep             37
sr_fail_no_sweep               10
sr_pdliq_attempted             38
target_score_sized             284
crt_sweep_sized                124
golden_rule_sized              278
sr_fail_low_swept_no_close_back 17
risk_cap_skip                  173
pdliq_sweep_sized              132
ny_continuation_gated          6
htf_fvg_breakout_sized         12
sr_pdliq_width_ok              4
sr_pdliq_sweep                 4
sr_fail_high_swept_no_close_back 8
sr_fail_both_swept             2
pyramid_blocked_no_pattern     6
```

_income: R156,553 across 41 withdrawals · working balance R9,500_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            350   178  50.9%    101381.27   6.57
OB             163    91  55.8%     58577.23   9.68
BREAKER         20    14  70.0%      5094.15  12.05

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            3     3 100.0%    inf
BREAKER M5            16    10  62.5%   7.08
FVG H1                64    35  54.7%   9.80
FVG M15               50    27  54.0%   8.55
FVG M5               236   116  49.2%   5.26
OB M15                23    17  73.9% 113.23
OB M5                140    74  52.9%   8.26

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            12     8  66.7%  49.63
BREAKER GBPUSD             4     4 100.0%    inf
BREAKER NZDUSD             4     2  50.0%   3.36
FVG EURUSD               168    84  50.0%   8.41
FVG GBPUSD               169    90  53.3%   6.15
FVG NZDUSD                13     4  30.8%   1.14
OB EURUSD                106    54  50.9%   6.98
OB GBPUSD                 43    28  65.1%  13.28
OB NZDUSD                 14     9  64.3%  36.55
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     1 100.0%     990.67    inf
amd_breaker_m5              12     9  75.0%     226.80   7.39
amd_fvg_h1                  52    29  55.8%     355.12   7.08
amd_fvg_m15                 40    20  50.0%     353.46   6.04
amd_fvg_m5                 209   104  49.8%     228.70   5.49
amd_ob_m15                  15    11  73.3%     393.22 116.51
amd_ob_m5                  118    61  51.7%     319.80   7.59
mss_breaker_h1               1     1 100.0%     128.40    inf
mss_breaker_m15              2     2 100.0%     587.03    inf
mss_breaker_m5               4     1  25.0%      19.87   3.25
mss_fvg_h1                  11     6  54.5%     889.01  61.55
mss_fvg_m15                  9     6  66.7%     743.47 189.50
mss_fvg_m5                  19    10  52.6%     171.92   3.58
mss_ob_m15                   7     5  71.4%     593.97 105.05
mss_ob_m5                   21    12  57.1%     498.31  12.24
news_fvg_m5                  3     1  33.3%     236.93   9.09
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         1     0   0.0%     -97.12   0.00
pyramid_im0.8_ob_m15         1     1 100.0%     159.84    inf
pyramid_im1.0_fvg_m5         2     1  50.0%      40.24  10.67
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       2     0   0.0%     -23.40   0.00
pyramid_wamd1.0_ob_m5        1     1 100.0%     159.84    inf
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              482   258  53.5%    152662.63   7.60
session_range           40    21  52.5%     10984.93   6.88
(no AMD)                11     4  36.4%      1405.09   4.51
```

_Session-range widths (n=178): median=34.8 p75=54.1 p90=83.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           213   129  60.6%     83953.05   9.39
against          289   139  48.1%     69669.84   6.40

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                98  57.1%  11.62
EURUSD SHORT against             188  47.9%   6.61
GBPUSD LONG against              101  48.5%   5.95
GBPUSD SHORT golden              115  63.5%   8.20
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          143    74  51.7%     43226.07   7.48
opposing            62    37  59.7%     20057.58  10.81
no divergence      297   157  52.9%     90339.24   7.37
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         533   283  53.1%    165052.65   7.50
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     348   183  52.6%   8.09
near             no     185   100  54.1%   6.08
```

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            333   174  52.3%     99937.38   7.50
OB              72    38  52.8%     30115.48   7.01
none (projection)     128    71  55.5%     34999.79   7.96
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             55    32  58.2%   8.84
near    fib_extension       278   154  55.4%   8.67
near    ith_liquidity         3     1  33.3%  22.77
near    pdh_pdl              71    31  43.7%   5.36
near    pwh_pwl               5     1  20.0%   0.75
near    round_number         41    21  51.2%   4.49
near    swing                78    42  53.8%   6.31
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          207   102  49.3%     50292.40   5.70
  on 240T        168    80  47.6%     36938.46   4.79
  on D            39    22  56.4%     13353.94  14.85
clear            326   181  55.5%    114760.25   8.81
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        175    99  56.6%     65560.65   8.71
             60T        150    82  54.7%     51809.50   8.03
             D           25    17  68.0%     13751.15  13.05
down (-1)    all        122    55  45.1%     28563.05   5.91
             60T        105    45  42.9%     21016.22   4.88
             D           17    10  58.8%      7546.82  19.89
none         all        236   129  54.7%     70928.96   7.40

with rev                228   119  52.2%     78097.34   9.11
against                  69    35  50.7%     16026.36   4.42
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             29    11  37.9%      3675.92   3.59
2            128    66  51.6%     32576.07   7.62
3            249   132  53.0%     82039.30   7.31
4            107    58  54.2%     35850.61   7.50
5             19    15  78.9%     10794.13  20.76

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           350  56.3%   8.30      183  47.0%   5.84
NFP week Mon/Tue          58  62.1%  12.95      475  52.0%   7.04
Rate decision             45  53.3%  10.79      488  53.1%   7.31
PD prov (sweep)          469  51.8%   6.57       64  62.5%  17.98
Seasonal lean              0   0.0%   0.00      533  53.1%   7.50
HTF OB Context           152  59.9%  10.61      381  50.4%   6.16
D1 Draw                  481  53.0%   7.23       52  53.8%  11.13
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 5     1  20.0%        73.77   1.36
continuation         147    90  61.2%     73330.68  10.87
(none)               381   192  50.4%     91648.20   6.16

Liq type          Trades    WR%     PF
----------------------------------------
breaker               24  62.5%   3.77
d1_fvg                81  58.0%   9.81
ob                     8  62.5%  47.07
pdhl                  12  50.0%   8.37
w_fvg                 27  66.7%  22.29
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     1  33.3%         5.83   1.03
equal_hl             478   254  53.1%    147650.11   7.28
(none)                52    28  53.8%     17396.71  11.13
```
