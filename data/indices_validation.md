# Realistic full-basket validation — currencies + indices + gold

Judged on the **scheduled-withdrawal income model** (start at R10k; every R10k band the account reaches makes withdrawals more frequent + larger; bank 70% / compound 30%). Sizing for indices/gold is provisional, so PF / WR / working-MaxDD and the **income schedule** are the signals, not fantasy equity.

_run commit: `dc6890e`_

## Metrics — currencies-only vs full basket

| split | book | trades | WR% | PF | MaxDD% | working-DD% | total value R | income R | withdrawals |
|---|---|---|---|---|---|---|---|---|---|
| Full 4yr | FX only | 804.00 | 44.90 | 4.91 | -12.76 | 12.76 | 1,222,169 | 838,314 | 92 |
| Full 4yr | FX+idx+gold | 926.00 | 42.40 | 4.25 | -12.76 | 18.46 | 1,375,521 | 940,875 | 95 |
| IS 2022-23 | FX only | 389.00 | 44.70 | 3.39 | -12.76 | 12.76 | 82,391 | 50,425 | 24 |
| IS 2022-23 | FX+idx+gold | 415.00 | 43.90 | 2.98 | -12.76 | 18.46 | 84,807 | 50,164 | 22 |
| OOS 2024-25 | FX only | 409.00 | 45.00 | 4.87 | -12.41 | 13.30 | 186,569 | 121,349 | 31 |
| OOS 2024-25 | FX+idx+gold | 430.00 | 44.40 | 4.82 | -12.41 | 13.37 | 239,045 | 160,338 | 33 |

## Income schedule — FULL basket (currencies + indices + gold), 4yr

```
Withdrawals (income) per year — amount, frequency, avg ===
  2022: R       9,318  (  4 withdrawals, ~1 / 91d, avg R2,329)
  2023: R      40,846  ( 18 withdrawals, ~1 / 20d, avg R2,269)
  2024: R     151,753  ( 32 withdrawals, ~1 / 11d, avg R4,742)
  2025: R     738,959  ( 41 withdrawals, ~1 / 9d, avg R18,023)
  TOTAL income: R940,875 across 95 withdrawals (avg R9,904 each)
  final working balance: R434,645  (keep-level R413,232)
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

- Full basket banked **R940,875** income across **95** withdrawals over 4yr; currencies-only banked R838,314 across 92. Indices+gold added **R102,561** of income (+12%).
- **Full-basket working-DD: 18.46% — TOO HIGH (>15% — trim via INDEX_SIZE_MULT<1 or INDEX_AMD_MAX_RANGE_PCT=0.6)**
- Indices run with the SMT quality gate (INDEX_SMT_REQUIRED=1). Compare income vs FX-only AND working-DD vs the ~15% line: ship if income is clearly up and working-DD is back under ~15%. If DD is still high, dial INDEX_SIZE_MULT / INDEX_AMD_MAX_RANGE_PCT and re-run.
- Working-account MaxDD is the realistic per-cycle drawdown; the total-value MaxDD is withdrawal-neutral (a cash-out is never a drawdown).
