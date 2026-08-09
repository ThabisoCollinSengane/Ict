# US index gate — validation

Baseline (`INDICES_ENABLED=0`) vs indices (`INDICES_ENABLED=1`, US500+US100 via DXY+sibling+US30 SMT-breadth gate). **Sizing is provisional — absolute equity is NOT calibrated; PF/WR/MaxDD are scale-invariant and ARE the edge signal.** Ship indices ON only if the book's MaxDD is not worse and index trades are PF-positive in both splits.

_run commit: `9f639ae`_

## Full 4yr

| metric | baseline | +indices | Δ |
|---|---|---|---|
| trades | 804.00 | 1053.00 | +249.00 |
| win rate | 44.90% | 43.10% | -1.80 |
| profit factor | 4.95 | 4.72 | -0.23 |
| max drawdown | -12.76% | -15.53% | -2.77 |
| ending equity ZAR | 567,575,614 | 1,674,637,110 | +1,107,061,496 |

_index trades taken: 249_

## IS 2022-23

| metric | baseline | +indices | Δ |
|---|---|---|---|
| trades | 389.00 | 496.00 | +107.00 |
| win rate | 44.70% | 43.50% | -1.20 |
| profit factor | 2.88 | 2.97 | +0.09 |
| max drawdown | -12.76% | -12.76% | +0.00 |
| ending equity ZAR | 273,481 | 745,239 | +471,758 |

_index trades taken: 107_

## OOS 2024-25

| metric | baseline | +indices | Δ |
|---|---|---|---|
| trades | 409.00 | 459.00 | +50.00 |
| win rate | 45.00% | 44.40% | -0.60 |
| profit factor | 4.95 | 4.73 | -0.22 |
| max drawdown | -12.55% | -12.55% | +0.00 |
| ending equity ZAR | 2,241,887 | 2,782,243 | +540,355 |

_index trades taken: 50_

## Verdict

**🔴 RED — do NOT ship indices ON (INDICES_ENABLED stays 0).**

- **Full 4yr: 🔴 fail** — MaxDD -15.53 worse than -12.76
- **IS 2022-23: 🟢 pass** — ok
- **OOS 2024-25: 🟢 pass** — ok

_Reminder: calibrate INDEX_PIP / INDEX_LOT_UNITS before trusting absolute equity. If MaxDD breaches, tighten INDEX_MIN_IMSCORE=1.0 (all 3 agree) or set INDEX_SIZE_MULT<1 and re-run — same risk-fit path as gold._
