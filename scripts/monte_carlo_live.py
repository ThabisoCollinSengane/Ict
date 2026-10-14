"""P102 — Monte Carlo for the first year of the LIVE account (R1,000 start).

    python scripts/monte_carlo_live.py [--sims 10000]

Draws trades at random (bootstrap) from the engine's own trade lists, re-sized to the
simulated account's equity tier exactly as scripts/monte_carlo.py does, ~18 trades a
month, monthly withdrawals above R6k. Four scenarios:

  hist     2022-25 trade pool (876 trades, the default p93 engine)
  y2026    2026 Jan-Sep pool only (131 trades — the harder regime, WR 37%)
  missed   hist, but 20% of trades never happen (missed fills, VPS down, overrides)
  costs    hist, every trade 1 extra pip worse (slippage / wider live spread)

Reports, per scenario: balance at 3 / 6 / 12 months, chance of being below the R1,000
start, months to reach R6k, deepest drop of the account from its high, longest stretch
without a new high, losing streak, income in months 7-12, and alarm thresholds for live.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402
from monte_carlo import infer_base, tier_units  # noqa: E402

PIP_ZAR_PER_UNIT = 0.0001 * 18.5        # R per pip per unit (EUR/GBP USD-quoted, USDZAR ~18.5)


def load(path):
    d = pd.read_csv(path)
    return (d.pnl / d.units.map(infer_base)).to_numpy()


def sim_year(pool, rng, months=12, per_month=18, miss=0.0, cost_pips=0.0,
             start=1000.0, keep=6000.0):
    eq, peak, maxdd = start, start, 0.0
    streak = worst = 0
    under = longest = 0
    withdrawn = 0.0
    snap, first6k, ruin = {}, None, False
    income_late = 0.0
    for m in range(1, months + 1):
        for _ in range(per_month):
            if miss and rng.random() < miss:
                continue
            p = rng.choice(pool) - cost_pips * PIP_ZAR_PER_UNIT
            eq += p * tier_units(eq)
            streak = streak + 1 if p < 0 else 0
            worst = max(worst, streak)
            if eq > peak:
                peak, under = eq, 0
            else:
                under += 1
                longest = max(longest, under)
            maxdd = max(maxdd, (peak - eq) / peak)
            ruin |= eq < 500
        if first6k is None and eq >= keep:
            first6k = m
        if eq > keep:                                   # month-end withdrawal
            withdrawn += eq - keep
            if m > 6:
                income_late += eq - keep
            eq = peak = keep
        if m in (3, 6, 12):
            snap[m] = eq + withdrawn
    return snap, first6k, maxdd * 100, worst, longest / per_month, ruin, income_late, withdrawn


def run(name, pool, rng, sims, **kw):
    R = [sim_year(pool, rng, **kw) for _ in range(sims)]
    q = lambda v, p: np.percentile(v, p)
    tv = {m: np.array([r[0][m] for r in R]) for m in (3, 6, 12)}
    f6 = np.array([r[1] if r[1] else 99 for r in R])
    dd = np.array([r[2] for r in R]); st = np.array([r[3] for r in R])
    uw = np.array([r[4] for r in R]); ruin = np.mean([r[5] for r in R])
    inc = np.array([r[6] for r in R])
    L = [f"### {name}", "",
         "| | bad (10th pct) | typical (median) | good (90th pct) |", "|---|---|---|---|"]
    for m in (3, 6, 12):
        L.append(f"| Total value after {m} months (balance + withdrawn) | R{q(tv[m],10):,.0f} | "
                 f"R{q(tv[m],50):,.0f} | R{q(tv[m],90):,.0f} |")
    L += [f"| Months to reach R6,000 | {q(f6,90):.0f} | {q(f6,50):.0f} | {q(f6,10):.0f} |",
          f"| Income withdrawn in months 7-12 | R{q(inc,10):,.0f} | R{q(inc,50):,.0f} | R{q(inc,90):,.0f} |",
          f"| Deepest drop from the high | {q(dd,90):.0f}% | {q(dd,50):.0f}% | {q(dd,10):.0f}% |",
          f"| Longest losing streak | {q(st,90):.0f} | {q(st,50):.0f} | {q(st,10):.0f} |",
          f"| Longest time without a new high (months) | {q(uw,90):.1f} | {q(uw,50):.1f} | {q(uw,10):.1f} |",
          "",
          f"Chance of being below the R1,000 start after 3 months: **{np.mean(tv[3]<1000)*100:.0f}%**, "
          f"6 months: **{np.mean(tv[6]<1000)*100:.0f}%**, 12 months: **{np.mean(tv[12]<1000)*100:.0f}%**. "
          f"Chance the balance ever falls below R500: **{ruin*100:.1f}%**. "
          f"Not at R6,000 within 12 months: **{np.mean(f6==99)*100:.0f}%**.", "",
          f"Alarm levels (worse than 95% of runs): drop from the high **{q(dd,95):.0f}%**, losing streak "
          f"**{q(st,95):.0f}**, time without a new high **{q(uw,95):.1f} months**.", ""]
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--out", default="data/monte_carlo_live_report.md")
    a = ap.parse_args()
    hist = load("data/mm_golden_full_p93_p99_trades.csv")
    y26 = load("data/mm_golden_y26_p93_p99_trades.csv")
    rng = np.random.default_rng(a.seed)
    L = ["# Monte Carlo — first year of the live account (P102)", "",
         f"{a.sims:,} simulated years per scenario, R1,000 start, ~18 trades/month, "
         "withdraw everything above R6,000 at month end, lot tiers as config.EQUITY_TIERS.", ""]
    L += run("1. History 2022-25 (876 trades)", hist, rng, a.sims)
    L += run("2. 2026 only (131 trades, the harder year)", y26, rng, a.sims, per_month=15)
    L += run("3. History, 20% of trades missed", hist, rng, a.sims, miss=0.2)
    L += run("4. History, every trade 1 pip worse (live costs)", hist, rng, a.sims, cost_pips=1.0)
    txt = "\n".join(L) + "\n"
    open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
