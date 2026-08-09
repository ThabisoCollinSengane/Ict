# NWOG (New Week Opening Gap) — full-backtest validation

Baseline (`NWOG_ENABLED=0`, byte-identical to pre-NWOG) vs NWOG (`NWOG_ENABLED=1`) on the full 4yr and the IS/OOS splits. `hit` = trades where price sat at the NWOG CE aligned with the trade. **Ships only if full-4yr equity is up and MaxDD is not worse, and both splits stay positive with MaxDD not materially worse.**

_run commit: `e3b24ed`_
_**TRUE 4yr run** — 2025 M1 data present._

## Full 4yr

| metric | baseline | NWOG | Δ |
|---|---|---|---|
| trades | 804.00 | 804.00 | +0.00 |
| win rate | 44.90% | 44.90% | +0.00 |
| profit factor | 4.95 | 4.95 | +0.00 |
| max drawdown | -12.76% | -12.76% | +0.00 |
| ending equity ZAR | 567,575,614 | 559,725,110 | -7,850,504 |

_NWOG CE hits: 26_

## IS 2022-23

| metric | baseline | NWOG | Δ |
|---|---|---|---|
| trades | 389.00 | 389.00 | +0.00 |
| win rate | 44.70% | 44.70% | +0.00 |
| profit factor | 2.88 | 2.86 | -0.02 |
| max drawdown | -12.76% | -12.76% | +0.00 |
| ending equity ZAR | 273,481 | 271,929 | -1,551 |

_NWOG CE hits: 13_

## OOS 2024-25

| metric | baseline | NWOG | Δ |
|---|---|---|---|
| trades | 409.00 | 409.00 | +0.00 |
| win rate | 45.00% | 45.00% | +0.00 |
| profit factor | 4.95 | 4.95 | +0.00 |
| max drawdown | -12.55% | -12.55% | +0.00 |
| ending equity ZAR | 2,241,887 | 2,229,736 | -12,151 |

_NWOG CE hits: 13_

## Verdict

**🔴 RED — do NOT ship. Default NWOG_ENABLED=0.**

- **Full 4yr: 🔴 fail** — equity 559,725,110≤567,575,614
- **IS 2022-23: 🔴 fail** — equity down 271,929<273,481
- **OOS 2024-25: 🔴 fail** — equity down 2,229,736<2,241,887

_Provisional — review split magnitudes (IS/OOS same ballpark?) before final ship, per the 'what not curve-fit means' rule._
