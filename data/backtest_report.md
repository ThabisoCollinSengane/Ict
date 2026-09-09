# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     132
win_rate_pct               15.2
profit_factor              0.64
starting_equity_ZAR        1000
ending_equity_ZAR          495.53
pnl_ZAR                    -504.47
pnl_pct                    -50.45
max_drawdown_pct           -51.99
avg_win_ZAR                44.27
avg_loss_ZAR               -12.41
```

## Gate funnel

```
checks                         61225
in_killzone                    61225
news_clear                     6577
nfp_fomc_ok                    5495
intermarket_signal             934
pair_matches                   934
mss_h1_m15_m5_ok               549
daily_bias_ok                  549
h1_bias_ok                     549
h4_bias_ok                     549
dealing_range_ok               104
consolidation_found            127
manipulation_correct_dir       89
m5_fvg_correct_dir             120
target_found                   120
rr_ok                          120
units_nonzero                  120
limit_placed                   0
entry_opened                   120
pyramid_added                  0
pyramid_blocked_min_target     74
drawdown_halt                  54256
daily_loss_halt                301
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      773
daily_pair_cap                 821
weekly_amd_confirmed           126
session_handover_closed        6
htf_draw_full_cascade          0
htf_draw_partial               118
htf_draw_counter               237
htf_fvg_5050_hit               13
ote_zone                       15
choch_confirmed                1
low_conviction                 0
judas_divergence               1
ny_continuation                52
pm_gate_pair_news              0
dxy_real_used                  12901
dxy_directional                3118
eurgbp_directional             2527
im_score_low                   1741
mss_no_dxy                     346
mm_golden_checked              2452
mm_golden_amd_ok               904
mm_golden_via_own_ob           73
mm_golden_smt_yes              60
mm_golden_opened               12
mm_golden_daily_cap            225
mm_golden_ob_failed            573
mss_no_pair                    39
dxy_fvg_room                   49
crt_turtle_soup                76
golden_rule_yes                49
mstruct_align                  130
mstruct_minor_sweep            40
phase_london_judas             74
gt_pool_sweep                  100
gt_disp_wick                   80
m1_stop_used                   14
stop_capped_10pip              78
risk_cap_ok                    120
pyramid_blocked_favour         979
soj_retest                     71
soj_sweep                      103
phase_ny_judas                 68
gt_judas_reversal              16
structure_stop_used            106
soj_judas                      32
breakout_confirmed             160
mm_golden_wrong_sweep          537
gt_macro_window                29
mm_golden_corr_block           228
golden_rule_no                 61
mm_golden_other_pair_open      540
mm_golden_no_draw              48
mm_golden_no_smt               15
eurgbp_flat                    35
eurgbp_flat_gbp_blocked        20
pyramid_blocked_low_im         120
mm_golden_ob_untested          246
sr_attempted                   129
sr_prev_session_ok             129
sr_enough_bars                 129
sr_consol_found                129
sr_breakout_found              82
session_range_found            5
dxy_flat                       783
smt_pair_opposing              23
gt_mp_discount                 39
smt_pair_confirmed             16
london_judas_ny_echo           4
gt_mp_extreme                  22
mm_golden_via_cascade          2
sr_consol_no_sweep             34
sr_fail_high_swept_no_close_back 3
sr_pdliq_attempted             34
mm_golden_no_amd               18
sr_fail_no_sweep               27
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
sr_fail_low_swept_no_close_back 4
ny_continuation_gated          44
mm_golden_no_retrace           10
```

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG             65    11  16.9%      -265.42   0.66
OB              51     6  11.8%      -254.86   0.49
BREAKER         13     2  15.4%        15.44   1.15
other            3     1  33.3%         0.37   1.02

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             2     1  50.0%   3.51
BREAKER M15            2     0   0.0%   0.00
BREAKER M5             9     1  11.1%   0.85
FVG H1                 9     0   0.0%   0.00
FVG M15               10     0   0.0%   0.00
FVG M5                46    11  23.9%   0.98
OB M15                13     0   0.0%   0.00
OB M5                 38     6  15.8%   0.70
other ?                3     1  33.3%   1.02

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             4     0   0.0%   0.00
BREAKER GBPUSD             5     1  20.0%   3.04
BREAKER NZDUSD             4     1  25.0%   1.86
FVG EURUSD                27     3  11.1%   0.29
FVG GBPUSD                32     7  21.9%   1.17
FVG NZDUSD                 6     1  16.7%   0.21
OB EURUSD                 16     2  12.5%   0.57
OB GBPUSD                 18     2  11.1%   0.42
OB NZDUSD                 17     2  11.8%   0.50
other EURUSD               1     0   0.0%   0.00
other GBPUSD               2     1  50.0%  19.00
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                     3     1  33.3%       0.12   1.02
amd_breaker_m5               6     0   0.0%      -7.68   0.00
amd_fvg_h1                   6     0   0.0%     -10.11   0.00
amd_fvg_m15                  8     0   0.0%     -12.89   0.00
amd_fvg_m5                  40    11  27.5%       2.39   1.23
amd_ob_m15                   5     0   0.0%     -13.82   0.00
amd_ob_m5                   24     5  20.8%       0.94   1.11
mss_breaker_h1               2     1  50.0%      22.94   3.51
mss_breaker_m15              2     0   0.0%     -10.08   0.00
mss_breaker_m5               3     1  33.3%      11.93   2.74
mss_fvg_h1                   3     0   0.0%     -15.66   0.00
mss_fvg_m15                  2     0   0.0%     -22.39   0.00
mss_fvg_m5                   6     0   0.0%     -17.61   0.00
mss_ob_m15                   8     0   0.0%     -10.46   0.00
mss_ob_m5                   14     1   7.1%      -8.90   0.12
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              124    20  16.1%      -376.31   0.70
session_range            5     0   0.0%       -78.21   0.00
(no AMD)                 3     0   0.0%       -49.95   0.00
```

_Session-range widths (n=129): median=53.6 p75=72.0 p90=86.7 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden            47     5  10.6%      -252.19   0.51
against           58    11  19.0%      -132.45   0.78

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                14   7.1%   0.35
EURUSD SHORT against              34  11.8%   0.31
GBPUSD LONG against               24  29.2%   1.70
GBPUSD SHORT golden               33  12.1%   0.60
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           15     3  20.0%       -61.09   0.69
opposing            20     3  15.0%       -76.48   0.67
no divergence       70    10  14.3%      -247.08   0.64
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
1             10     0   0.0%      -143.84   0.00
2             45     5  11.1%      -156.51   0.67
3             44     9  20.5%      -167.39   0.59
4             29     6  20.7%        20.34   1.07
5              4     0   0.0%       -57.07   0.00

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile            83  19.3%   0.82       49   8.2%   0.37
NFP week Mon/Tue          11  18.2%   0.56      121  14.9%   0.65
Rate decision             13   0.0%   0.00      119  16.8%   0.71
PD prov (sweep)           95  17.9%   0.78       37   8.1%   0.32
Seasonal lean              0   0.0%   0.00      132  15.2%   0.64
HTF OB Context            54  13.0%   0.52       78  16.7%   0.74
D1 Draw                  112  17.0%   0.74       20   5.0%   0.23
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 5     0   0.0%       -50.23   0.00
continuation          49     7  14.3%      -264.26   0.56
(none)                78    13  16.7%      -189.99   0.74

Liq type          Trades    WR%     PF
----------------------------------------
breaker               15  13.3%   0.75
d1_fvg                33  15.2%   0.53
ob                     1   0.0%   0.00
pdhl                   3   0.0%   0.00
w_fvg                  2   0.0%   0.00
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     0   0.0%       -28.12   0.00
equal_hl             109    19  17.4%      -263.04   0.76
(none)                20     1   5.0%      -213.30   0.23
```
