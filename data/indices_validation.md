# Realistic full-basket validation — currencies + indices + gold

> ⚠️ Some runs produced no Results — diagnostics at the bottom.


Judged on the **scheduled-withdrawal income model** (start at R10k; every R10k band the account reaches makes withdrawals more frequent + larger; bank 70% / compound 30%). Sizing for indices/gold is provisional, so PF / WR / working-MaxDD and the **income schedule** are the signals, not fantasy equity.

_run commit: `e028093`_

## Metrics — currencies-only vs full basket

| split | book | trades | WR% | PF | MaxDD% | working-DD% | total value R | income R | withdrawals |
|---|---|---|---|---|---|---|---|---|---|
| Full 4yr | FX only | — | — | — | — | — | — | — | None |
| Full 4yr | FX+idx+gold | — | — | — | — | — | — | — | None |
| IS 2022-23 | FX only | — | — | — | — | — | — | — | None |
| IS 2022-23 | FX+idx+gold | — | — | — | — | — | — | — | None |
| OOS 2024-25 | FX only | — | — | — | — | — | — | — | None |
| OOS 2024-25 | FX+idx+gold | — | — | — | — | — | — | — | None |

## Income schedule — FULL basket (currencies + indices + gold), 4yr

```
(no withdrawals — account never reached R10k)
```

## Income schedule — currencies only, 4yr (for comparison)

```
(no withdrawals — account never reached R10k)
```

## Bottom line

- Working-account MaxDD is the realistic per-cycle drawdown; the total-value MaxDD is withdrawal-neutral. Ship the basket if working-DD stays tolerable and the income schedule is worth it — equity size is capped by design.

## Diagnostics (why some runs had no Results)

### fx_full — NO RESULTS (crash/early-exit)

```
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 20, in <module>
    import config
  File "/workspaces/Ict/config.py", line 24, in <module>
    WITHDRAW_FRACTION = float(_os.environ.get("WITHDRAW_FRACTION", 1.0))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: '0.7#'
```

### all_full — NO RESULTS (crash/early-exit)

```
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 20, in <module>
    import config
  File "/workspaces/Ict/config.py", line 24, in <module>
    WITHDRAW_FRACTION = float(_os.environ.get("WITHDRAW_FRACTION", 1.0))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: '0.7#'
```

### fx_is — NO RESULTS (crash/early-exit)

```
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 20, in <module>
    import config
  File "/workspaces/Ict/config.py", line 24, in <module>
    WITHDRAW_FRACTION = float(_os.environ.get("WITHDRAW_FRACTION", 1.0))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: '0.7#'
```

### all_is — NO RESULTS (crash/early-exit)

```
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 20, in <module>
    import config
  File "/workspaces/Ict/config.py", line 24, in <module>
    WITHDRAW_FRACTION = float(_os.environ.get("WITHDRAW_FRACTION", 1.0))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: '0.7#'
```

### fx_oos — NO RESULTS (crash/early-exit)

```
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 20, in <module>
    import config
  File "/workspaces/Ict/config.py", line 24, in <module>
    WITHDRAW_FRACTION = float(_os.environ.get("WITHDRAW_FRACTION", 1.0))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: '0.7#'
```

### all_oos — NO RESULTS (crash/early-exit)

```
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 20, in <module>
    import config
  File "/workspaces/Ict/config.py", line 24, in <module>
    WITHDRAW_FRACTION = float(_os.environ.get("WITHDRAW_FRACTION", 1.0))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: '0.7#'
```

