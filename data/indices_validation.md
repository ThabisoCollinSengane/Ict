# Realistic full-basket validation — currencies + indices + gold

> ⚠️ Some runs produced no Results — diagnostics at the bottom.


Judged on the **scheduled-withdrawal income model** (start at R10k; every R10k band the account reaches makes withdrawals more frequent + larger; bank 70% / compound 30%). Sizing for indices/gold is provisional, so PF / WR / working-MaxDD and the **income schedule** are the signals, not fantasy equity.

_run commit: `9dd3869`_

## Metrics — currencies-only vs full basket

| split | book | trades | WR% | PF | MaxDD% | working-DD% | total value R | income R | withdrawals |
|---|---|---|---|---|---|---|---|---|---|
| Full 4yr | FX only | 804.00 | 44.90 | 4.91 | -12.76 | 12.76 | 1,222,169 | 838,314 | 92 |
| Full 4yr | FX+idx+gold | — | — | — | — | — | — | — | None |
| IS 2022-23 | FX only | 389.00 | 44.70 | 3.39 | -12.76 | 12.76 | 82,391 | 50,425 | 24 |
| IS 2022-23 | FX+idx+gold | 466.00 | 43.10 | 3.47 | -12.76 | 14.44 | 156,632 | 101,560 | 30 |
| OOS 2024-25 | FX only | 409.00 | 45.00 | 4.87 | -12.41 | 13.30 | 186,569 | 121,349 | 31 |
| OOS 2024-25 | FX+idx+gold | 448.00 | 44.00 | 4.80 | -12.41 | 13.41 | 248,918 | 167,703 | 35 |

## Income schedule — FULL basket (currencies + indices + gold), 4yr

```
(no withdrawals — account never reached R10k)
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

- Working-account MaxDD is the realistic per-cycle drawdown; the total-value MaxDD is withdrawal-neutral. Ship the basket if working-DD stays tolerable and the income schedule is worth it — equity size is capped by design.

## Diagnostics (why some runs had no Results)

### all_full — NO RESULTS (crash/early-exit)

```

```

