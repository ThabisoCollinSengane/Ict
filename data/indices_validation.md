# US index gate — validation

Baseline (`INDICES_ENABLED=0`) vs indices (`INDICES_ENABLED=1`, US500+US100 via DXY+sibling+US30 SMT-breadth gate). **Sizing is provisional — absolute equity is NOT calibrated; PF/WR/MaxDD are scale-invariant and ARE the edge signal.** Ship indices ON only if the book's MaxDD is not worse and index trades are PF-positive in both splits.

_run commit: `b17aa2c`_

## Full 4yr

| metric | baseline | +indices | Δ |
|---|---|---|---|
| trades | 804.00 | 928.00 | +124.00 |
| win rate | 44.90% | 44.40% | -0.50 |
| profit factor | 4.95 | 4.87 | -0.08 |
| max drawdown | -12.76% | -12.88% | -0.12 |
| ending equity ZAR | 567,575,614 | 1,441,021,881 | +873,446,267 |

_index trades taken: 124_

## IS 2022-23

| metric | baseline | +indices | Δ |
|---|---|---|---|
| trades | 389.00 | 442.00 | +53.00 |
| win rate | 44.70% | 44.80% | +0.10 |
| profit factor | 2.88 | 3.36 | +0.48 |
| max drawdown | -12.76% | -12.76% | +0.00 |
| ending equity ZAR | 273,481 | 623,657 | +350,176 |

_index trades taken: 53_

## OOS 2024-25

| metric | baseline | +indices | Δ |
|---|---|---|---|
| trades | 409.00 | 431.00 | +22.00 |
| win rate | 45.00% | 45.00% | +0.00 |
| profit factor | 4.95 | 4.88 | -0.07 |
| max drawdown | -12.55% | -12.55% | +0.00 |
| ending equity ZAR | 2,241,887 | 2,669,080 | +427,193 |

_index trades taken: 22_

## Verdict

**🔴 RED — do NOT ship indices ON (INDICES_ENABLED stays 0).**

- **Full 4yr: 🔴 fail** — MaxDD -12.88 worse than -12.76
- **IS 2022-23: 🟢 pass** — ok
- **OOS 2024-25: 🟢 pass** — ok

_Reminder: calibrate INDEX_PIP / INDEX_LOT_UNITS before trusting absolute equity. If MaxDD breaches, tighten INDEX_MIN_IMSCORE=1.0 (all 3 agree) or set INDEX_SIZE_MULT<1 and re-run — same risk-fit path as gold._
