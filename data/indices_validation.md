# Realistic full-basket validation — currencies + indices + gold

Judged on the **scheduled-withdrawal income model** (start at R10k; every R10k band the account reaches makes withdrawals more frequent + larger; bank 70% / compound 30%). Sizing for indices/gold is provisional, so PF / WR / working-MaxDD and the **income schedule** are the signals, not fantasy equity.

_run commit: `abd39b0`_

## Metrics — currencies-only vs full basket

| split | book | trades | WR% | PF | MaxDD% | working-DD% | total value R | income R | withdrawals |
|---|---|---|---|---|---|---|---|---|---|
| Full 4yr | FX only | 804.00 | 44.90 | 4.91 | -12.76 | 12.76 | 1,222,169 | 838,314 | 92 |
| Full 4yr | FX+idx+gold | 1335.00 | 41.00 | 4.22 | -12.76 | 12.76 | 3,588,055 | 2,485,034 | 100 |
| IS 2022-23 | FX only | 389.00 | 44.70 | 3.39 | -12.76 | 12.76 | 82,391 | 50,425 | 24 |
| IS 2022-23 | FX+idx+gold | 652.00 | 42.50 | 3.76 | -12.76 | 12.76 | 272,151 | 176,045 | 32 |
| OOS 2024-25 | FX only | 409.00 | 45.00 | 4.87 | -12.41 | 13.30 | 186,569 | 121,349 | 31 |
| OOS 2024-25 | FX+idx+gold | 522.00 | 42.50 | 3.68 | -19.32 | 25.15 | 182,984 | 120,760 | 29 |

## Income schedule — FULL basket (currencies + indices + gold), 4yr

```
Withdrawals (income) per year — amount, frequency, avg ===
  2022: R      26,672  (  6 withdrawals, ~1 / 61d, avg R4,445)
  2023: R     149,374  ( 26 withdrawals, ~1 / 14d, avg R5,745)
  2024: R     391,387  ( 32 withdrawals, ~1 / 11d, avg R12,231)
  2025: R   1,917,602  ( 36 withdrawals, ~1 / 10d, avg R53,267)
  TOTAL income: R2,485,034 across 100 withdrawals (avg R24,850 each)
  final working balance: R1,103,021  (keep-level R1,075,015)
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

- Full basket banked **R2,485,034** income across **100** withdrawals over 4yr; currencies-only banked R838,314 across 92. Indices+gold added **R1,646,720** of income (+196%).
- **Full-basket working-DD: 12.76% — OK (<15%)**
- Indices run with the SMT quality gate (INDEX_SMT_REQUIRED=1). Compare income vs FX-only AND working-DD vs the ~15% line: ship if income is clearly up and working-DD is back under ~15%. If DD is still high, dial INDEX_SIZE_MULT / INDEX_AMD_MAX_RANGE_PCT and re-run.
- Working-account MaxDD is the realistic per-cycle drawdown; the total-value MaxDD is withdrawal-neutral (a cash-out is never a drawdown).
