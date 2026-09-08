# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     505
win_rate_pct               42.2
profit_factor              3.22
starting_equity_ZAR        1000
ending_equity_ZAR          73109.52
pnl_ZAR                    72109.52
pnl_pct                    7210.95
max_drawdown_pct           -15.75
avg_win_ZAR                491.08
avg_loss_ZAR               -111.27
withdrawn_total_ZAR        66929.77
withdrawal_count           17
working_balance_ZAR        6179.76
working_max_drawdown_pct   14.96
```

## Gate funnel

```
checks                         57893
in_killzone                    57893
news_clear                     56250
nfp_fomc_ok                    47833
intermarket_signal             2401
pair_matches                   2401
mss_h1_m15_m5_ok               1658
daily_bias_ok                  1658
h1_bias_ok                     1658
h4_bias_ok                     1658
dealing_range_ok               144
consolidation_found            629
manipulation_correct_dir       522
m5_fvg_correct_dir             595
target_found                   595
rr_ok                          595
units_nonzero                  595
limit_placed                   0
entry_opened                   463
pyramid_added                  13
pyramid_blocked_min_target     495
drawdown_halt                  0
daily_loss_halt                952
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      1228
daily_pair_cap                 2495
weekly_amd_confirmed           257
session_handover_closed        7
htf_draw_full_cascade          152
htf_draw_partial               423
htf_draw_counter               439
htf_fvg_5050_hit               20
ote_zone                       19
choch_confirmed                13
low_conviction                 0
judas_divergence               3
ny_continuation                251
pm_gate_pair_news              0
mm_golden_checked              5408
mm_golden_amd_ok               2595
mm_golden_ob_failed            2061
breakout_confirmed             519
sr_attempted                   350
sr_prev_session_ok             350
sr_enough_bars                 350
sr_consol_found                333
sr_breakout_found              207
session_range_found            28
soj_retest                     323
soj_sweep                      525
golden_rule_no                 242
mstruct_align                  624
phase_ny_judas                 304
gt_pool_sweep                  492
structure_stop_used            544
stop_capped_10pip              409
risk_cap_ok                    463
mm_golden_other_pair_open      1456
pyramid_blocked_low_im         1073
soj_judas                      202
crt_turtle_soup                345
golden_rule_yes                298
gt_disp_wick                   395
m1_stop_used                   51
pyramid_blocked_favour         2907
dxy_fvg_room                   94
phase_london_judas             349
gt_macro_window                107
mm_golden_wrong_sweep          668
mm_golden_via_own_ob           120
mm_golden_smt_yes              96
mm_golden_opened               29
mm_golden_no_draw              62
mm_golden_no_smt               29
mm_golden_ob_untested          361
mm_golden_corr_block           451
smt_pair_opposing              65
gt_mp_discount                 145
smt_pair_confirmed             153
mstruct_minor_sweep            107
gt_mp_extreme                  48
mm_golden_via_cascade          5
mm_golden_daily_cap            150
gt_judas_reversal              54
sr_consol_no_sweep             98
sr_fail_no_sweep               34
sr_pdliq_attempted             115
mm_golden_no_amd               88
ny_continuation_gated          33
london_judas_ny_echo           8
phase_ny_extend                1
sr_fail_high_swept_no_close_back 17
mm_golden_no_retrace           45
crt_sweep_sized                116
risk_cap_skip                  132
pdliq_sweep_sized              88
golden_rule_sized              222
target_score_sized             179
mm_golden_risk_cap             5
mm_golden_ob_none              3
sr_fail_both_swept             22
sr_fail_low_swept_no_close_back 25
phase_london_watch             1
htf_fvg_breakout_sized         5
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
```

_income: R66,930 across 17 withdrawals · working balance R6,180_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            317   133  42.0%     39785.55   2.86
OB             163    69  42.3%     26657.04   3.75
BREAKER         25    11  44.0%      5666.93   4.98

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             2     1  50.0%   0.46
BREAKER M15            3     2  66.7%   6.00
BREAKER M5            20     8  40.0%   5.40
FVG H1                42    20  47.6%   6.21
FVG M15               50    24  48.0%   3.12
FVG M5               225    89  39.6%   2.42
OB M15                37    15  40.5%   2.52
OB M5                126    54  42.9%   4.10

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            11     8  72.7% 137.63
BREAKER GBPUSD             9     3  33.3%   8.13
BREAKER NZDUSD             5     0   0.0%   0.00
FVG EURUSD               111    46  41.4%   2.78
FVG GBPUSD               165    71  43.0%   2.93
FVG NZDUSD                41    16  39.0%   2.72
OB EURUSD                 59    19  32.2%   2.25
OB GBPUSD                 60    34  56.7%   8.94
OB NZDUSD                 44    16  36.4%   2.22
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_h1               1     0   0.0%    -140.48   0.00
amd_breaker_m15              1     0   0.0%    -168.17   0.00
amd_breaker_m5              13     4  30.8%     361.68  11.46
amd_fvg_h1                  31    19  61.3%     320.66   9.51
amd_fvg_m15                 35    16  45.7%     119.29   2.69
amd_fvg_m5                 194    83  42.8%     114.44   2.60
amd_ob_m15                  21    11  52.4%     158.95   4.32
amd_ob_m5                   91    39  42.9%     178.87   3.96
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     2 100.0%     504.70    inf
mss_breaker_m5               7     4  57.1%      28.60   1.30
mss_fvg_h1                   9     1  11.1%      -2.02   0.97
mss_fvg_m15                 12     7  58.3%     195.10   4.58
mss_fvg_m5                  21     4  19.0%      65.71   1.71
mss_ob_m15                  16     4  25.0%      -5.32   0.92
mss_ob_m5                   33    13  39.4%     185.10   3.96
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  1     0   0.0%    -325.18   0.00
news_ob_m5                   2     2 100.0%     509.46    inf
pyramid_im1.0_fvg_m15        1     1 100.0%     158.17    inf
pyramid_im1.0_fvg_m5         4     2  50.0%      49.72   5.22
pyramid_wamd1.0_fvg_h1       2     0   0.0%     -43.71   0.00
pyramid_wamd1.0_fvg_m15       1     0   0.0%     -12.49   0.00
pyramid_wamd1.0_fvg_m5       5     0   0.0%     -31.38   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              465   199  42.8%     68790.20   3.28
session_range           27     9  33.3%      1880.85   2.50
(no AMD)                13     5  38.5%      1438.47   2.33
```

_Session-range widths (n=350): median=57.3 p75=72.0 p90=90.9 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           205    90  43.9%     35843.21   3.54
against          210    91  43.3%     28849.00   3.58

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                67  38.8%   2.28
EURUSD SHORT against             114  41.2%   3.87
GBPUSD LONG against               96  45.8%   3.29
GBPUSD SHORT golden              138  46.4%   4.22
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          102    50  49.0%     18897.99   4.97
opposing            55    25  45.5%      8379.76   4.01
no divergence      258   106  41.1%     37414.46   3.11
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              4     1  25.0%        77.92   1.82
1             37    12  32.4%       357.61   1.16
2            121    47  38.8%     12201.55   2.44
3            224    97  43.3%     35362.45   3.35
4            107    49  45.8%     19097.60   4.24
5             12     7  58.3%      5012.39   8.47

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           332  43.7%   3.62      173  39.3%   2.43
NFP week Mon/Tue          42  52.4%   4.38      463  41.3%   3.14
Rate decision             40  52.5%   7.02      465  41.3%   3.00
PD prov (sweep)          413  43.6%   3.36       92  35.9%   2.60
Seasonal lean              0   0.0%   0.00      505  42.2%   3.22
HTF OB Context           172  41.3%   3.45      333  42.6%   3.08
D1 Draw                  440  43.0%   3.41       65  36.9%   2.21
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 9     3  33.3%      2373.97   7.59
continuation         163    68  41.7%     27185.65   3.32
(none)               333   142  42.6%     42549.90   3.08

Liq type          Trades    WR%     PF
----------------------------------------
breaker               39  48.7%   2.82
d1_fvg               103  39.8%   3.44
ob                     8  25.0%   3.17
pdhl                  15  40.0%   3.14
w_fvg                  7  42.9%   9.55
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 2     1  50.0%       -41.62   0.83
equal_hl             438   188  42.9%     66032.61   3.43
(none)                65    24  36.9%      6118.53   2.21
```
