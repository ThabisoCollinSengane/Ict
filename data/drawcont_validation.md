# Draw-to-liquidity continuation entry — full-backtest validation

Baseline (`DRAW_CONT_ENABLED=0`) vs entry ON (`1`). This ADDS continuation trades toward unswept near PDH/PDL. `added` = draw-cont entries opened. **Ships only if full-4yr equity up and MaxDD NOT worse, and both splits stay positive with MaxDD not materially worse** (gate bypasses have blown MaxDD before — this must prove otherwise).

_run commit: `9dbfa39`_
_⚠️ 2025 DXY (UDXUSD_2025) ABSENT — 'Full' is effectively 2022-2024; re-confirm once loaded._

## Full 4yr

| metric | baseline | draw-cont ON | Δ |
|---|---|---|---|
| trades | 602.00 | 625.00 | +23.00 |
| win rate | 45.30% | 44.60% | -0.70 |
| profit factor | 3.49 | 3.30 | -0.19 |
| max drawdown | -12.95% | -16.73% | -3.78 |
| ending equity ZAR | 11,702,904 | 12,267,006 | +564,102 |

_draw-cont entries added: 72_

## IS 2022-23

| metric | baseline | draw-cont ON | Δ |
|---|---|---|---|
| trades | 389.00 | 404.00 | +15.00 |
| win rate | 45.80% | 45.00% | -0.80 |
| profit factor | 3.04 | 2.90 | -0.14 |
| max drawdown | -12.95% | -16.73% | -3.78 |
| ending equity ZAR | 343,444 | 347,740 | +4,297 |

_draw-cont entries added: 47_

## OOS 2024-25

| metric | baseline | draw-cont ON | Δ |
|---|---|---|---|
| trades | 209.00 | 219.00 | +10.00 |
| win rate | 44.00% | 43.40% | -0.60 |
| profit factor | 3.50 | 3.27 | -0.23 |
| max drawdown | -15.41% | -11.86% | +3.55 |
| ending equity ZAR | 34,690 | 33,958 | -733 |

_draw-cont entries added: 28_

## Verdict

**🔴 RED — do NOT ship. Stays OFF (DRAW_CONT_ENABLED=0).**

- **Full 4yr: 🔴 fail** — MaxDD -16.73 worse than -12.95 by >0.1pp
- **IS 2022-23: 🔴 fail** — MaxDD -16.73 worse than -12.95 by >1.0pp
- **OOS 2024-25: 🔴 fail** — equity down 33,958<34,690

_Provisional — Claude reviews split magnitudes + whether the added trades are net-positive (not just MaxDD-neutral) before final ship._
