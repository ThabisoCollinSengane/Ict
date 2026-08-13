# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `7ce68eb`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 | 0 | 0 |
| MM adds | 816.00 | 44.90 | 4.95 | -12.76 | 550,802,112 | 14 | 0 |
| MM adds + opp-tgt | 948.00 | 41.60 | 4.67 | -12.89 | 301,225,127 | 42 | 174 |

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 389.00 | 44.70 | 2.88 | -12.76 | 273,481 | 0 | 0 |
| MM adds | 392.00 | 44.90 | 2.88 | -12.76 | 270,534 | 5 | 0 |
| MM adds + opp-tgt | 440.00 | 42.30 | 2.77 | -12.89 | 218,049 | 15 | 67 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 409.00 | 45.00 | 4.95 | -12.55 | 2,241,887 | 0 | 0 |
| MM adds | 419.00 | 44.90 | 4.95 | -12.81 | 2,410,754 | 8 | 0 |
| MM adds + opp-tgt | 506.00 | 40.70 | 4.63 | -13.00 | 1,696,863 | 25 | 101 |

## Verdict

- **MM adds: 🔴 RED** — full equity 550,802,112≤567,575,614
- **MM adds + opp-tgt: 🔴 RED** — full equity 301,225,127≤567,575,614; full MaxDD -12.89 worse than -12.76

_No arm passed the full gate. Same measure-first discipline: nothing ships._
