# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     804
win_rate_pct               44.9
profit_factor              4.95
starting_equity_ZAR        500
ending_equity_ZAR          567575614.25
pnl_ZAR                    567575114.25
pnl_pct                    113515022.85
max_drawdown_pct           -12.76
avg_win_ZAR                1970068.69
avg_loss_ZAR               -324197.93
```

## Gate funnel

```
checks                         119943
in_killzone                    119943
news_clear                     118405
nfp_fomc_ok                    101089
intermarket_signal             5107
pair_matches                   5107
mss_h1_m15_m5_ok               1712
daily_bias_ok                  1712
h1_bias_ok                     1712
h4_bias_ok                     1712
dealing_range_ok               105
consolidation_found            756
manipulation_correct_dir       653
m5_fvg_correct_dir             811
target_found                   811
rr_ok                          811
units_nonzero                  811
limit_placed                   0
entry_opened                   786
pyramid_added                  18
pyramid_blocked_min_target     1124
drawdown_halt                  0
daily_loss_halt                52
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      673
daily_pair_cap                 3571
weekly_amd_confirmed           283
session_handover_closed        3
htf_draw_full_cascade          125
htf_draw_partial               598
htf_draw_counter               348
htf_fvg_5050_hit               34
ote_zone                       5
choch_confirmed                27
low_conviction                 0
judas_divergence               2
ny_continuation                315
pm_gate_pair_news              0
breakout_confirmed             913
soj_retest                     478
soj_sweep                      737
golden_rule_no                 423
mstruct_align                  782
phase_ny_judas                 420
gt_pool_sweep                  624
structure_stop_used            751
stop_capped_10pip              552
risk_cap_ok                    786
pyramid_blocked_low_im         2847
soj_judas                      259
crt_turtle_soup                386
golden_rule_yes                347
gt_disp_wick                   619
m1_stop_used                   60
pyramid_blocked_favour         5388
dxy_fvg_room                   131
phase_london_judas             405
gt_macro_window                121
smt_pair_opposing              91
gt_mp_discount                 162
smt_pair_confirmed             216
mstruct_minor_sweep            115
gt_judas_reversal              107
gt_mp_extreme                  36
ny_continuation_gated          9
london_judas_ny_echo           18
pdliq_sweep_sized              121
risk_cap_skip                  25
target_score_sized             285
crt_sweep_sized                120
phase_london_watch             3
pyramid_blocked_no_pattern     7
htf_fvg_breakout_sized         15
phase_ny_extend                2
phase_london_breakout          1
```

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            529   230  43.5% 226063332.83   3.14
OB             246   114  46.3% 331112672.44  11.10
BREAKER         29    17  58.6%  10399108.98   3.07

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            6     3  50.0%   1.19
BREAKER M5            22    13  59.1%  12.62
FVG H1                94    41  43.6%   4.45
FVG M15               86    35  40.7%   1.37
FVG M5               349   154  44.1%   3.91
OB M15                36    21  58.3% 270.22
OB M5                210    93  44.3%   7.67

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            20    11  55.0%   0.67
BREAKER GBPUSD             5     4  80.0% 1257.16
BREAKER NZDUSD             4     2  50.0%   6.43
FVG EURUSD               256   109  42.6%   4.16
FVG GBPUSD               243   113  46.5%   2.58
FVG NZDUSD                30     8  26.7%   4.37
OB EURUSD                164    64  39.0%   6.64
OB GBPUSD                 58    37  63.8% 107.11
OB NZDUSD                 24    13  54.2%  25.68
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              3     1  33.3%  241041.15   1.17
amd_breaker_m5              14     9  64.3%  684736.36  12.81
amd_fvg_h1                  72    33  45.8%  253782.51   2.10
amd_fvg_m15                 64    24  37.5%  279622.94   1.57
amd_fvg_m5                 274   118  43.1%  260751.58   2.97
amd_ob_m15                  24    14  58.3% 1791413.57 101.88
amd_ob_m5                  158    70  44.3% 1082155.94   6.63
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              3     2  66.7%   28442.17  74.75
mss_breaker_m5               8     4  50.0%     535.72   1.31
mss_fvg_h1                  21     8  38.1% 3689830.48   7.98
mss_fvg_m15                 19    10  52.6% -204445.51   0.41
mss_fvg_m5                  59    31  52.5%  756914.11  12.88
mss_ob_m15                  10     6  60.0% 7230693.53 34591.08
mss_ob_m5                   52    23  44.2%  862134.67  23.59
news_fvg_m15                 1     0   0.0%      -4.63   0.00
news_fvg_m5                  3     1  33.3%   62712.87 2034.93
pyramid_im0.8_fvg_m15        1     1 100.0%     670.06    inf
pyramid_im0.8_fvg_m5         6     3  50.0%      99.59   2.51
pyramid_im0.8_ob_m15         2     1  50.0%      85.10  24.00
pyramid_im1.0_fvg_m15        1     0   0.0%    -192.40   0.00
pyramid_im1.0_fvg_m5         4     1  25.0%      30.52   3.20
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -9.25   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -12.58   0.00
```

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           321   165  51.4% 318368164.85   6.61
against          425   173  40.7% 142455686.40   2.81

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               158  48.1%   5.70
EURUSD SHORT against             282  38.3%   4.22
GBPUSD LONG against              143  45.5%   1.90
GBPUSD SHORT golden              163  54.6%   8.06
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          215    96  44.7% 105456539.10   4.65
opposing            92    49  53.3%  61996038.18  12.82
no divergence      439   193  44.0% 293371273.96   3.89
```
