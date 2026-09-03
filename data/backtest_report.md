# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     355
win_rate_pct               43.1
profit_factor              3.38
starting_equity_ZAR        1000
ending_equity_ZAR          48472.73
pnl_ZAR                    47472.73
pnl_pct                    4747.27
max_drawdown_pct           -13.24
avg_win_ZAR                440.81
avg_loss_ZAR               -98.86
withdrawn_total_ZAR        41485.0
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
consolidation_found            452
manipulation_correct_dir       409
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
breakout_confirmed             583
soj_retest                     238
soj_sweep                      434
golden_rule_no                 230
mstruct_align                  467
phase_ny_judas                 251
gt_pool_sweep                  388
structure_stop_used            451
stop_capped_10pip              392
risk_cap_ok                    346
pyramid_blocked_low_im         994
soj_judas                      196
crt_turtle_soup                224
golden_rule_yes                242
gt_disp_wick                   354
m1_stop_used                   31
pyramid_blocked_favour         1810
dxy_fvg_room                   57
phase_london_judas             241
gt_macro_window                63
smt_pair_opposing              59
gt_mp_discount                 92
smt_pair_confirmed             153
mstruct_minor_sweep            71
gt_judas_reversal              51
gt_mp_extreme                  18
ny_continuation_gated          6
london_judas_ny_echo           7
target_score_sized             130
crt_sweep_sized                77
risk_cap_skip                  136
golden_rule_sized              203
pdliq_sweep_sized              62
phase_london_watch             1
htf_fvg_breakout_sized         2
phase_ny_extend                1
```

_income: R41,485 across 16 withdrawals · working balance R6,988_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            262   110  42.0%     35161.80   3.31
OB              83    37  44.6%     11334.84   3.72
BREAKER         10     6  60.0%       976.09   2.69

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            2     1  50.0%   1.80
BREAKER M5             7     4  57.1%  14.19
FVG H1                39    15  38.5%   3.41
FVG M15               38    15  39.5%   5.36
FVG M5               185    80  43.2%   3.04
OB M15                12     6  50.0%  11.51
OB M5                 71    31  43.7%   3.54

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             8     4  50.0%   0.89
BREAKER GBPUSD             2     2 100.0%    inf
FVG EURUSD               117    48  41.0%   3.77
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
amd_fvg_h1                  32    14  43.8%     181.81   4.01
amd_fvg_m15                 27    10  37.0%     121.12   3.50
amd_fvg_m5                 147    64  43.5%     139.27   3.40
amd_ob_m15                   9     6  66.7%     118.64  58.58
amd_ob_m5                   52    23  44.2%     112.14   2.73
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              1     1 100.0%     974.25    inf
mss_breaker_m5               3     1  33.3%      31.73   5.84
mss_fvg_h1                   6     1  16.7%     -37.11   0.42
mss_fvg_m15                  9     4  44.4%     255.65  24.44
mss_fvg_m5                  29    15  51.7%     108.16   2.16
mss_ob_m15                   3     0   0.0%     -25.28   0.00
mss_ob_m5                   19     8  42.1%     237.44   7.44
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  2     0   0.0%     -43.94   0.00
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         2     1  50.0%      -4.63   0.90
pyramid_im1.0_fvg_m5         2     0   0.0%     -23.59   0.00
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -18.38   0.00
```

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           141    67  47.5%     25471.15   4.07
against          194    77  39.7%     19809.30   2.84

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                56  42.9%   2.71
EURUSD SHORT against             119  37.0%   2.84
GBPUSD LONG against               75  44.0%   2.83
GBPUSD SHORT golden               85  50.6%   4.98
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          108    48  44.4%     18353.37   3.85
opposing            44    20  45.5%      3345.88   3.37
no divergence      183    76  41.5%     23581.19   3.10
```
