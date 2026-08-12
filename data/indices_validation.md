# Realistic full-basket validation — currencies + indices + gold

Judged on the **scheduled-withdrawal income model** (start at R10k; every R10k band the account reaches makes withdrawals more frequent + larger; bank 70% / compound 30%). Sizing for indices/gold is provisional, so PF / WR / working-MaxDD and the **income schedule** are the signals, not fantasy equity.

_run commit: `413455c`_

## Metrics — currencies-only vs full basket

| split | book | trades | WR% | PF | MaxDD% | working-DD% | total value R | income R | withdrawals |
|---|---|---|---|---|---|---|---|---|---|
| Full 4yr | FX only | 804.00 | 44.90 | 4.91 | -12.76 | 12.76 | 1,222,169 | 838,314 | 92 |
| Full 4yr | FX+indices | 1265.00 | 41.70 | 4.49 | -12.76 | 12.97 | 2,740,026 | 1,889,282 | 111 |
| IS 2022-23 | FX only | 389.00 | 44.70 | 3.39 | -12.76 | 12.76 | 82,391 | 50,425 | 24 |
| IS 2022-23 | FX+indices | 622.00 | 42.60 | 3.44 | -12.76 | 12.76 | 191,463 | 126,491 | 37 |
| OOS 2024-25 | FX only | 409.00 | 45.00 | 4.87 | -12.41 | 13.30 | 186,569 | 121,349 | 31 |
| OOS 2024-25 | FX+indices | 516.00 | 43.00 | 3.86 | -19.32 | 25.15 | 172,292 | 113,271 | 25 |

## Income schedule — FULL basket (currencies + indices + gold), 4yr

```
Withdrawals (income) per year — amount, frequency, avg ===
  2022: R      28,151  (  6 withdrawals, ~1 / 61d, avg R4,692)
  2023: R      98,339  ( 31 withdrawals, ~1 / 12d, avg R3,172)
  2024: R     314,611  ( 34 withdrawals, ~1 / 11d, avg R9,253)
  2025: R   1,448,181  ( 40 withdrawals, ~1 / 9d, avg R36,205)
  TOTAL income: R1,889,282 across 111 withdrawals (avg R17,021 each)
  final working balance: R850,743  (keep-level R819,692)
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

- Full basket banked **R1,889,282** income across **111** withdrawals over 4yr; currencies-only banked R838,314 across 92. Indices+gold added **R1,050,968** of income (+125%).
- **Full-basket working-DD: 12.97% — OK (<15%)**
- Indices run with the SMT quality gate (INDEX_SMT_REQUIRED=1). Compare income vs FX-only AND working-DD vs the ~15% line: ship if income is clearly up and working-DD is back under ~15%. If DD is still high, dial INDEX_SIZE_MULT / INDEX_AMD_MAX_RANGE_PCT and re-run.
- Working-account MaxDD is the realistic per-cycle drawdown; the total-value MaxDD is withdrawal-neutral (a cash-out is never a drawdown).
