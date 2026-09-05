# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     587
win_rate_pct               41.7
profit_factor              3.42
starting_equity_ZAR        1000
ending_equity_ZAR          103585.05
pnl_ZAR                    102585.05
pnl_pct                    10258.51
max_drawdown_pct           -21.96
avg_win_ZAR                591.87
avg_loss_ZAR               -124.04
withdrawn_total_ZAR        97857.41
withdrawal_count           16
working_balance_ZAR        5727.64
working_max_drawdown_pct   28.77
```

## Gate funnel

```
checks                         57622
in_killzone                    57622
news_clear                     49888
nfp_fomc_ok                    42313
intermarket_signal             2239
pair_matches                   2239
mss_h1_m15_m5_ok               744
daily_bias_ok                  744
h1_bias_ok                     744
h4_bias_ok                     744
dealing_range_ok               28
consolidation_found            378
manipulation_correct_dir       336
m5_fvg_correct_dir             377
target_found                   377
rr_ok                          377
units_nonzero                  377
limit_placed                   0
entry_opened                   303
pyramid_added                  9
pyramid_blocked_min_target     540
drawdown_halt                  6148
daily_loss_halt                929
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      223
daily_pair_cap                 1485
weekly_amd_confirmed           124
session_handover_closed        4
htf_draw_full_cascade          94
htf_draw_partial               229
htf_draw_counter               175
htf_fvg_5050_hit               6
ote_zone                       2
choch_confirmed                7
low_conviction                 0
judas_divergence               1
ny_continuation                162
pm_gate_pair_news              0
mm_golden_checked              3645
mm_golden_amd_ok               1156
mm_golden_opened               275
pyramid_blocked_favour         2615
breakout_confirmed             430
sr_attempted                   197
sr_prev_session_ok             197
sr_enough_bars                 197
sr_consol_found                185
sr_breakout_found              71
session_range_found            24
soj_retest                     199
soj_sweep                      344
golden_rule_no                 197
mstruct_align                  363
phase_ny_judas                 202
gt_pool_sweep                  311
structure_stop_used            351
stop_capped_10pip              304
risk_cap_ok                    303
pyramid_blocked_low_im         1615
dxy_fvg_room                   41
phase_london_judas             183
gt_macro_window                54
mm_golden_wrong_sweep          876
soj_judas                      145
gt_disp_wick                   275
mm_golden_no_draw              783
crt_turtle_soup                178
golden_rule_yes                168
smt_pair_opposing              48
gt_mp_discount                 71
smt_pair_confirmed             110
mm_golden_daily_cap            1533
mstruct_minor_sweep            53
m1_stop_used                   26
gt_judas_reversal              40
gt_mp_extreme                  12
sr_consol_no_sweep             76
sr_fail_no_sweep               42
sr_pdliq_attempted             88
mm_golden_no_amd               80
ny_continuation_gated          6
london_judas_ny_echo           5
target_score_sized             111
golden_rule_sized              147
risk_cap_skip                  74
htf_fvg_breakout_sized         3
pdliq_sweep_sized              52
sr_fail_high_swept_no_close_back 12
crt_sweep_sized                50
sr_fail_low_swept_no_close_back 16
mm_golden_risk_cap             98
pyramid_blocked_no_pattern     1
sr_fail_both_swept             6
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
```

_income: R97,857 across 16 withdrawals · working balance R5,728_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            392   156  39.8%     64089.94   3.27
OB             157    73  46.5%     31969.33   3.74
BREAKER         25     9  36.0%      3939.18   2.72
other           13     7  53.8%      2586.60  15.84

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            5     1  20.0%   0.70
BREAKER M5            19     7  36.8%   5.76
FVG H1                53    23  43.4%   5.40
FVG M15               70    21  30.0%   2.11
FVG M5               269   112  41.6%   3.25
OB M15                29    14  48.3%   3.43
OB M5                128    59  46.1%   3.80
other ?               13     7  53.8%  15.84

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            13     4  30.8%   0.35
BREAKER GBPUSD            12     5  41.7%   7.83
FVG EURUSD               173    65  37.6%   3.65
FVG GBPUSD               207    88  42.5%   3.11
FVG NZDUSD                12     3  25.0%   1.73
OB EURUSD                 92    38  41.3%   2.99
OB GBPUSD                 58    30  51.7%   5.20
OB NZDUSD                  7     5  71.4%  17.52
other EURUSD               6     4  66.7%  34.70
other GBPUSD               7     3  42.9%  10.73
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                    13     7  53.8%     198.97  15.84
amd_breaker_m15              3     0   0.0%    -394.57   0.00
amd_breaker_m5              15     5  33.3%     258.09   5.48
amd_fvg_h1                  49    22  44.9%     275.46   5.43
amd_fvg_m15                 61    16  26.2%      39.48   1.45
amd_fvg_m5                 251   107  42.6%     165.52   3.24
amd_ob_m15                  27    14  51.9%     174.21   3.50
amd_ob_m5                  113    52  46.0%     206.85   3.55
mss_breaker_h1               1     1 100.0%     128.40    inf
mss_breaker_m15              2     1  50.0%     378.90   4.50
mss_breaker_m5               4     2  50.0%      91.32  14.50
mss_fvg_h1                   3     1  33.3%      41.90   4.68
mss_fvg_m15                  7     4  57.1%     420.95  52.80
mss_fvg_m5                  10     4  40.0%     312.70   4.17
mss_ob_m15                   2     0   0.0%     -19.98   0.00
mss_ob_m5                   15     7  46.7%     262.12   7.93
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  1     0   0.0%     -46.25   0.00
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         1     0   0.0%     -97.12   0.00
pyramid_im1.0_fvg_m5         3     1  33.3%      17.57   1.50
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -18.38   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              540   225  41.7%     97269.65   3.56
session_range           41    17  41.5%      4968.71   2.21
(no AMD)                 6     3  50.0%       346.70   2.40
```

_Session-range widths (n=197): median=49.2 p75=60.3 p90=88.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           393   167  42.5%     80531.42   3.61
against          175    70  40.0%     20682.91   2.95

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               173  41.0%   3.44
EURUSD SHORT against             111  36.0%   2.74
GBPUSD LONG against               64  46.9%   3.41
GBPUSD SHORT golden              220  43.6%   3.73
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           88    40  45.5%     16914.20   4.66
opposing            34    14  41.2%      3971.53   5.33
no divergence      446   183  41.0%     80328.60   3.24
```
