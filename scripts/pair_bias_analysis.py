#!/usr/bin/env python3
"""Discretionary-sync playbook: from the EXISTING trade dump (data/trades_dump.csv,
already written as a byproduct of any run_backtest_histdata.py run — no new backtest
needed), cross-tab the shipped autonomous algo's own history by:

  - pair x direction (which pair is reliable on which bias)
  - entry pattern / PD array family (fvg / ob / breaker, and by TF) — which entries
    are actually good
  - session profile (london / ny / ny_pm) x pair and x direction — which session
    performs best at what
  - im_scenario (the intermarket cheat-sheet classification) x pair — ties the above
    back to the documented scenario table in CLAUDE.md

Excludes MM continuation/standalone rows (entry_model == "mm_standalone" or
entry_type starting with mm_/mmstd_) — those are profiled separately by
scripts/mm_analysis.py (data/mm_winners_report.md). This script is base-algo only:
the trades the autonomous engine actually takes on its own.

Usage:
    python scripts/pair_bias_analysis.py            # writes data/pair_bias_report.md
    python scripts/pair_bias_analysis.py --selftest  # no data needed
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DUMP_CANDIDATES = [
    os.environ.get("TRADE_CSV"),
    os.path.join(_ROOT, "data", "histdata", "trades_dump.csv"),
    os.path.join(_ROOT, "data", "trades_dump.csv"),
]
DUMP = next((p for p in _DUMP_CANDIDATES if p and os.path.exists(p)),
            _DUMP_CANDIDATES[1])
REPORT = os.path.join(_ROOT, "data", "pair_bias_report.md")

_PATTERN_FAMILY = {"fvg": "fvg", "ob": "ob", "breaker": "breaker"}


def parse_pattern(entry_type):
    """('fvg'|'ob'|'breaker'|None, tf|None) from tags like fvg_m5 / ob_m15 / breaker_h1."""
    s = str(entry_type)
    for fam in ("fvg", "ob", "breaker"):
        if s.startswith(fam + "_"):
            return fam, s[len(fam) + 1:]
    return None, None


def is_base_row(row):
    et = str(row.get("entry_type", ""))
    em = str(row.get("entry_model", ""))
    return em != "mm_standalone" and not et.startswith(("mm_", "mmstd_"))


def stats(rows, pnl_key="pnl"):
    n = len(rows)
    if n == 0:
        return {"n": 0, "wr": None, "pf": None, "pnl": 0.0, "avg": None}
    wins = [r for r in rows if r[pnl_key] > 0]
    losses = [r for r in rows if r[pnl_key] <= 0]
    gp = sum(r[pnl_key] for r in wins)
    gl = -sum(r[pnl_key] for r in losses)
    pf = (gp / gl) if gl > 0 else (float("inf") if gp > 0 else None)
    total = sum(r[pnl_key] for r in rows)
    return {"n": n, "wr": len(wins) / n * 100, "pf": pf, "pnl": total, "avg": total / n}


def _fmt_pf(pf):
    if pf is None:
        return "—"
    return "inf" if pf == float("inf") else f"{pf:.2f}"


def _table(rows, key_fn, order=None, title=""):
    groups = {}
    for r in rows:
        k = key_fn(r)
        groups.setdefault(k, []).append(r)
    keys = order if order else sorted(groups, key=lambda k: -len(groups.get(k, [])))
    L = [f"### {title}", "", "| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |",
         "|---|---|---|---|---|---|"]
    for k in keys:
        rs = groups.get(k, [])
        if not rs:
            continue
        s = stats(rs)
        L.append(f"| {k} | {s['n']} | {s['wr']:.1f} | {_fmt_pf(s['pf'])} | "
                 f"{s['pnl']:,.0f} | {s['avg']:,.0f} |")
    L.append("")
    return L


def build_report(rows):
    base = [r for r in rows if is_base_row(r)]
    mm = [r for r in rows if not is_base_row(r)]
    L = ["# Discretionary-sync playbook — pair x bias x entry x session", "",
         f"_{len(base)} base-algo trades analysed ({len(mm)} MM rows excluded — see "
         "data/mm_winners_report.md for those). Source: the trade dump from your "
         "last backtest run — no new backtest run for this report._", ""]

    overall = stats(base)
    L += ["## Overall", "",
          f"- {overall['n']} trades, WR {overall['wr']:.1f}%, PF {_fmt_pf(overall['pf'])}, "
          f"total P&L {overall['pnl']:,.0f} ZAR", ""]

    # 1) pair x direction — which pair is reliable on which bias
    L += ["## 1. Pair x direction — which pair is reliable on which bias", ""]
    L += _table(base, lambda r: f"{r['pair']} {'LONG' if int(r['direction']) > 0 else 'SHORT'}",
                title="Pair x direction")

    # 2) entry pattern family (PD array) — which entries are good
    pat_rows = []
    for r in base:
        fam, tf = parse_pattern(r.get("entry_type"))
        if fam:
            pat_rows.append({**r, "_fam": fam, "_famtf": f"{fam}_{tf}"})
    L += ["## 2. PD-array family — which entries are good", ""]
    L += _table(pat_rows, lambda r: r["_fam"], order=["fvg", "ob", "breaker"],
                title="By family (fvg / ob / breaker)")
    L += _table(pat_rows, lambda r: r["_famtf"], title="By family + timeframe")

    # entry_model: judas vs breakout
    L += ["## 3. Entry model — Judas reversal vs intermarket breakout", ""]
    L += _table(base, lambda r: r.get("entry_model", "judas"), title="By entry_model")

    # 4) session profile — which session performs best at what
    L += ["## 4. Session profile — which session performs best at what", ""]
    L += _table(base, lambda r: r.get("profile", "other"),
                order=["london", "ny", "ny_pm", "other"], title="By session profile")
    L += _table(base, lambda r: f"{r.get('profile', 'other')} / {r['pair']}",
                title="Session x pair")
    L += _table(base, lambda r: f"{r.get('profile', 'other')} / "
                                 f"{'LONG' if int(r['direction']) > 0 else 'SHORT'}",
                title="Session x direction")

    # 5) the 3-way ask: pair x direction x session
    L += ["## 5. Pair x direction x session (the full cross-tab)", ""]
    L += _table(base, lambda r: f"{r['pair']} {'LONG' if int(r['direction']) > 0 else 'SHORT'} "
                                 f"/ {r.get('profile', 'other')}",
                title="Pair x direction x session")

    # 6) im_scenario x pair — ties back to the documented cheat-sheet table
    L += ["## 6. Intermarket scenario x pair", ""]
    L += _table(base, lambda r: f"{r.get('im_scenario', '?')} / {r['pair']}",
                title="Scenario x pair")

    return "\n".join(L) + "\n"


def _publish():
    def _git(*a):
        return subprocess.run(["git", *a], cwd=_ROOT, capture_output=True, text=True)
    _git("add", "-f", REPORT)
    _git("commit", "-q", "-m", "Pair x bias x entry x session playbook (auto)")
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    if _git("push", "origin", "HEAD").returncode == 0:
        print("\nRESULTS PUSHED — Claude can read data/pair_bias_report.md")
    else:
        print("\n(auto-push failed — paste the report above to Claude)")


def _selftest():
    rows = [
        {"pair": "EURUSD", "direction": -1, "entry_type": "fvg_m5", "entry_model": "judas",
         "profile": "london", "im_scenario": "1b", "pnl": 100.0},
        {"pair": "EURUSD", "direction": -1, "entry_type": "ob_m15", "entry_model": "judas",
         "profile": "london", "im_scenario": "1b", "pnl": -20.0},
        {"pair": "GBPUSD", "direction": -1, "entry_type": "breaker_h1", "entry_model": "breakout",
         "profile": "ny", "im_scenario": "1a", "pnl": 50.0},
        {"pair": "GBPUSD", "direction": 1, "entry_type": "mm_fvg_m5_ifvg60T",
         "entry_model": "mm_standalone", "profile": "ny", "im_scenario": "?", "pnl": -5.0},
    ]
    assert not is_base_row(rows[3]) and all(is_base_row(r) for r in rows[:3])
    assert parse_pattern("fvg_m5") == ("fvg", "m5")
    assert parse_pattern("mm_fvg_m5_ifvg60T") == (None, None)
    s = stats(rows[:2])
    assert s["n"] == 2 and abs(s["pnl"] - 80.0) < 1e-9
    out = build_report(rows)
    assert "Pair x direction x session" in out and "1b / EURUSD" in out
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return 0
    if not os.path.exists(DUMP):
        print(f"**ERROR: no trade dump at {DUMP}.** Run a backtest first, e.g.:\n\n"
              "```\npython run_backtest_histdata.py --years 2022 2023 2024 2025\n```")
        return 1
    import pandas as pd
    df = pd.read_csv(DUMP)
    rows = df.to_dict("records")
    text = build_report(rows)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write(text)
    print(text)
    _publish()
    return 0


if __name__ == "__main__":
    sys.exit(main())
