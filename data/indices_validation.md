# Realistic full-basket validation — currencies + indices + gold

> ⚠️ Some runs produced no Results — diagnostics at the bottom.


Judged on the **scheduled-withdrawal income model** (start at R10k; every R10k band the account reaches makes withdrawals more frequent + larger; bank 70% / compound 30%). Sizing for indices/gold is provisional, so PF / WR / working-MaxDD and the **income schedule** are the signals, not fantasy equity.

_run commit: `5d4ae8b`_

## Metrics — currencies-only vs full basket

| split | book | trades | WR% | PF | MaxDD% | working-DD% | total value R | income R | withdrawals |
|---|---|---|---|---|---|---|---|---|---|
| Full 4yr | FX only | 804.00 | 44.90 | 4.91 | -12.76 | 12.76 | 1,222,169 | 838,314 | 92 |
| Full 4yr | FX+idx+gold | 1070.00 | 41.60 | 3.96 | -12.76 | 16.24 | 1,996,162 | 1,372,473 | 101 |
| IS 2022-23 | FX only | 389.00 | 44.70 | 3.39 | -12.76 | 12.76 | 82,391 | 50,425 | 24 |
| IS 2022-23 | FX+idx+gold | — | — | — | — | — | — | — | None |
| OOS 2024-25 | FX only | 409.00 | 45.00 | 4.87 | -12.41 | 13.30 | 186,569 | 121,349 | 31 |
| OOS 2024-25 | FX+idx+gold | 448.00 | 44.00 | 4.80 | -12.41 | 13.41 | 248,918 | 167,703 | 35 |

## Income schedule — FULL basket (currencies + indices + gold), 4yr

```
Withdrawals (income) per year — amount, frequency, avg ===
  2022: R       9,318  (  4 withdrawals, ~1 / 91d, avg R2,329)
  2023: R      92,242  ( 26 withdrawals, ~1 / 14d, avg R3,548)
  2024: R     205,430  ( 32 withdrawals, ~1 / 11d, avg R6,420)
  2025: R   1,065,483  ( 39 withdrawals, ~1 / 9d, avg R27,320)
  TOTAL income: R1,372,473 across 101 withdrawals (avg R13,589 each)
  final working balance: R623,689  (keep-level R598,203)
```

## Income schedule — currencies only, 4yr (for comparison)

```
Withdrawals (income) per year — amount, frequency, avg ===
  2022: R       9,834  (  4 withdrawals, ~1 / 91d, avg R2,459)
  2023: R      40,591  ( 20 withdrawals, ~1 / 18d, avg R2,030)
  2024: R     143,205  ( 31 withdrawals, ~1 / 12d, avg R4,620)
  2025: R     644,685  ( 37 withdrawals, ~1 / 10d, avg R17,424)
  TOTAL income: R838,314 across 92 withdrawals (avg R9,112 each)
  final working balance: R383,855  (keep-level R369,278)
```

## Bottom line

- Full basket banked **R1,372,473** income across **101** withdrawals over 4yr; currencies-only banked R838,314 across 92. Indices+gold added **R534,158** of income (+64%).
- Working-account MaxDD is the realistic per-cycle drawdown; the total-value MaxDD is withdrawal-neutral. Ship the basket if working-DD stays tolerable and the income schedule is worth it — equity size is capped by design.

## Diagnostics (why some runs had no Results)

### all_is — NO RESULTS (crash/early-exit)

```
    bar 64000/139494 (2022-11-09 07:00:00+00:00) - active=0 trades=171 equity=12717
    bar 65000/139494 (2022-11-14 18:20:00+00:00) - active=0 trades=179 equity=17070
    bar 66000/139494 (2022-11-18 05:40:00+00:00) - active=0 trades=182 equity=17127
    bar 67000/139494 (2022-11-23 17:05:00+00:00) - active=0 trades=184 equity=16391
    bar 68000/139494 (2022-11-29 04:25:00+00:00) - active=0 trades=186 equity=16555
    bar 69000/139494 (2022-12-02 15:45:00+00:00) - active=0 trades=187 equity=16994
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 728, in <module>
    main()
  File "/workspaces/Ict/run_backtest_histdata.py", line 216, in main
    backtester.run()
  File "/workspaces/Ict/backtest.py", line 246, in run
    self._update_orders(pair, t)
  File "/workspaces/Ict/backtest.py", line 369, in _update_orders
    self._exit_leg(pair, leg, sl, t, "stop")
  File "/workspaces/Ict/backtest.py", line 480, in _exit_leg
    self.log.write_trade(record, equity_after=self.equity)
  File "/workspaces/Ict/trade_log.py", line 71, in write_trade
    with _connect(self.db_path) as conn:
         ^^^^^^^^^^^^^^^^^^^^^^
  File "/workspaces/Ict/trade_log.py", line 22, in _connect
    _ensure_schema(conn)
  File "/workspaces/Ict/trade_log.py", line 27, in _ensure_schema
    conn.executescript("""
sqlite3.OperationalError: database is locked
```

