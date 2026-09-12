# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     523
win_rate_pct               53.2
profit_factor              7.64
starting_equity_ZAR        1000
ending_equity_ZAR          164492.45
pnl_ZAR                    163492.45
pnl_pct                    16349.25
max_drawdown_pct           -6.83
avg_win_ZAR                676.61
avg_loss_ZAR               -100.43
withdrawn_total_ZAR        154992.34
withdrawal_count           41
working_balance_ZAR        9500.11
working_max_drawdown_pct   14.72
```

## Gate funnel

```
checks                         123510
in_killzone                    123510
news_clear                     121634
nfp_fomc_ok                    104318
intermarket_signal             7601
pair_matches                   7601
mss_h1_m15_m5_ok               2938
daily_bias_ok                  2938
h1_bias_ok                     2938
h4_bias_ok                     2938
dealing_range_ok               138
consolidation_found            1983
manipulation_correct_dir       1789
m5_fvg_correct_dir             1994
target_found                   1994
rr_ok                          1994
units_nonzero                  682
limit_placed                   0
entry_opened                   514
pyramid_added                  9
pyramid_blocked_min_target     905
drawdown_halt                  0
daily_loss_halt                389
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      262
daily_pair_cap                 2606
weekly_amd_confirmed           497
session_handover_closed        3
htf_draw_full_cascade          396
htf_draw_partial               1444
htf_draw_counter               358
htf_fvg_5050_hit               55
ote_zone                       12
choch_confirmed                82
low_conviction                 0
judas_divergence               2
ny_continuation                844
pm_gate_pair_news              0
dxy_flat                       78112
dxy_directional                23338
eurgbp_flat                    5652
eurgbp_flat_gbp_blocked        3499
breakout_confirmed             1845
sr_attempted                   188
sr_prev_session_ok             188
sr_enough_bars                 188
sr_consol_found                187
sr_breakout_found              132
session_range_found            152
soj_retest                     1221
soj_sweep                      1819
golden_rule_no                 1085
mstruct_align                  1886
phase_ny_judas                 1069
gt_pool_sweep                  1560
structure_stop_used            1898
stop_capped_10pip              1453
target_rung_far                1312
target_rung_skipped            1312
risk_cap_ok                    514
eurgbp_directional             12794
soj_judas                      598
crt_turtle_soup                834
golden_rule_yes                763
gt_disp_wick                   1403
m1_stop_used                   96
smt_pair_confirmed             524
dxy_fvg_room                   370
phase_london_judas             950
gt_macro_window                205
im_score_low                   7972
pyramid_blocked_favour         3223
pyramid_blocked_low_im         1708
smt_pair_opposing              201
gt_mp_discount                 202
mstruct_minor_sweep            224
gt_judas_reversal              225
gt_mp_extreme                  40
london_judas_ny_echo           7
sr_consol_no_sweep             39
sr_fail_no_sweep               10
sr_pdliq_attempted             40
target_score_sized             281
crt_sweep_sized                122
golden_rule_sized              273
sr_fail_low_swept_no_close_back 19
risk_cap_skip                  168
pdliq_sweep_sized              129
ny_continuation_gated          6
htf_fvg_breakout_sized         12
sr_pdliq_width_ok              4
sr_pdliq_sweep                 4
sr_fail_high_swept_no_close_back 8
sr_fail_both_swept             2
pyramid_blocked_no_pattern     6
```

_income: R154,992 across 41 withdrawals · working balance R9,500_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            344   174  50.6%     99463.60   6.70
OB             159    90  56.6%     58934.70   9.79
BREAKER         20    14  70.0%      5094.15  12.05

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            3     3 100.0%    inf
BREAKER M5            16    10  62.5%   7.08
FVG H1                61    32  52.5%   9.13
FVG M15               49    27  55.1%   8.60
FVG M5               234   115  49.1%   5.55
OB M15                22    17  77.3% 122.17
OB M5                137    73  53.3%   8.36

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            12     8  66.7%  49.63
BREAKER GBPUSD             4     4 100.0%    inf
BREAKER NZDUSD             4     2  50.0%   3.36
FVG EURUSD               166    82  49.4%   8.65
FVG GBPUSD               166    88  53.0%   5.98
FVG NZDUSD                12     4  33.3%   1.51
OB EURUSD                101    52  51.5%   6.87
OB GBPUSD                 44    29  65.9%  14.03
OB NZDUSD                 14     9  64.3%  36.55
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     1 100.0%     990.67    inf
amd_breaker_m5              12     9  75.0%     226.80   7.39
amd_fvg_h1                  49    26  53.1%     332.97   6.37
amd_fvg_m15                 39    20  51.3%     362.96   6.08
amd_fvg_m5                 209   103  49.3%     226.30   5.45
amd_ob_m15                  14    11  78.6%     421.79 133.98
amd_ob_m5                  116    60  51.7%     328.20   7.67
mss_breaker_h1               1     1 100.0%     128.40    inf
mss_breaker_m15              2     2 100.0%     587.03    inf
mss_breaker_m5               4     1  25.0%      19.87   3.25
mss_fvg_h1                  11     6  54.5%     889.01  61.55
mss_fvg_m15                  9     6  66.7%     743.47 189.50
mss_fvg_m5                  17    10  58.8%     234.26   8.25
mss_ob_m15                   7     5  71.4%     593.97 105.05
mss_ob_m5                   20    12  60.0%     524.06  12.46
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
m15_range              475   254  53.5%    150760.96   7.67
session_range           38    20  52.6%     11309.74   7.97
(no AMD)                10     4  40.0%      1421.74   4.71
```

_Session-range widths (n=188): median=34.8 p75=52.6 p90=83.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           209   126  60.3%     83351.29   9.57
against          284   137  48.2%     68266.01   6.33

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                96  56.2%  12.63
EURUSD SHORT against             183  48.1%   6.50
GBPUSD LONG against              101  48.5%   5.95
GBPUSD SHORT golden              113  63.7%   8.12
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          138    71  51.4%     41463.34   7.17
opposing            60    36  60.0%     19758.71  10.76
no divergence      295   156  52.9%     90395.25   7.55
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         523   278  53.2%    163492.45   7.64
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     355   187  52.7%   7.92
near             no     168    91  54.2%   6.80
```

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            328   170  51.8%     98117.75   7.40
OB              71    38  53.5%     30441.75   7.18
none (projection)     124    70  56.5%     34932.95   9.03
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             55    32  58.2%   8.84
near    fib_extension       285   158  55.4%   8.37
near    ith_liquidity         3     1  33.3%  22.77
near    pdh_pdl              71    31  43.7%   5.34
near    pwh_pwl               5     1  20.0%   0.75
near    round_number         33    17  51.5%   8.50
near    swing                69    37  53.6%   6.10
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          204    99  48.5%     49456.97   5.57
  on 240T        166    78  47.0%     36529.23   4.75
  on D            38    21  55.3%     12927.75  13.03
clear            319   179  56.1%    114035.48   9.27
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        174    98  56.3%     64472.31   8.52
             60T        149    81  54.4%     50721.16   7.82
             D           25    17  68.0%     13751.15  13.05
down (-1)    all        120    55  45.8%     29350.26   6.49
             60T        103    45  43.7%     21403.37   5.32
             D           17    10  58.8%      7946.89  20.89
none         all        229   125  54.6%     69669.88   7.52

with rev                226   118  52.2%     77775.40   9.40
against                  68    35  51.5%     16047.17   4.43
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             28    11  39.3%      4322.95   6.60
2            126    64  50.8%     31985.12   7.50
3            244   131  53.7%     81602.54   7.45
4            107    58  54.2%     36128.66   7.33
5             17    13  76.5%      9336.56  18.09

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           340  56.5%   8.43      183  47.0%   6.00
NFP week Mon/Tue          56  62.5%  12.79      467  52.0%   7.20
Rate decision             44  52.3%   9.97      479  53.2%   7.51
PD prov (sweep)          461  51.6%   6.49       62  64.5%  27.49
Seasonal lean              0   0.0%   0.00      523  53.2%   7.64
HTF OB Context           149  59.7%  10.74      374  50.5%   6.30
D1 Draw                  475  53.1%   7.18       48  54.2%  17.96
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 5     1  20.0%        73.77   1.36
continuation         144    88  61.1%     72523.28  11.01
(none)               374   189  50.5%     90895.40   6.30

Liq type          Trades    WR%     PF
----------------------------------------
breaker               23  60.9%   3.69
d1_fvg                80  58.8%   9.85
ob                     8  62.5%  47.07
pdhl                  12  50.0%   9.39
w_fvg                 26  65.4%  23.41
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     1  33.3%         5.83   1.03
equal_hl             472   251  53.2%    145676.32   7.24
(none)                48    26  54.2%     17810.30  17.96
```
