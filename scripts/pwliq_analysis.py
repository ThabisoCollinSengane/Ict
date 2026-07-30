#!/usr/bin/env python3
"""Previous-week high/low (PWH/PWL) reaction study — the P41 question one TF up.

P41 shipped because sweeping PRIOR-DAY liquidity (PDH/PDL) predicted a better
reversal in both years. This asks the same of PRIOR-WEEK liquidity (PWH/PWL):
when the AMD manipulation sweep ran a weekly pool, does the fade pay more?

Reads the full trade dump (data/histdata/trades_dump.csv — all pairs, 2022-2025),
buckets every trade by `amd_liq_run` (the pool the sweep ran, weekly-priority:
pwh/pwl > pdh/pdl > eqh/eql > vah/val > none), and reports count / win-rate /
profit-factor / mean-R, split IS (2022-23) vs OOS (2024-25). Weekly levels are
rarer than daily, so watch the n column — a bucket under ~15 per split is noise.

Verdict rule (same as P41): a weekly-sweep edge is real only if WR (and PF) beat
the no-sweep baseline in BOTH years, same ballpark. Then it's a candidate for a
PWH/PWL sizing lever; otherwise it stays a measurement.

Run:  python scripts/pwliq_analysis.py            # reads data/histdata/trades_dump.csv
      python scripts/pwliq_analysis.py --selftest  # no data needed
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DUMP = os.path.join(DATA_DIR, "histdata", "trades_dump.csv")
REPORT = os.path.join(DATA_DIR, "pwliq_report.md")

BUCKETS = ["pwh", "pwl", "pdh", "pdl", "eqh", "eql", "vah", "val", "none"]
GROUPS = [("weekly (PWH/PWL)", {"pwh", "pwl"}),
          ("daily (PDH/PDL)", {"pdh", "pdl"}),
          ("equal H/L", {"eqh", "eql"}),
          ("value area", {"vah", "val"}),
          ("no major pool", {"none", ""})]


def _year(s):
    s = (s or "").strip()
    return s[:4] if len(s) >= 4 and s[:4].isdigit() else ""


def _r(row):
    """Signed R multiple from entry/stop/exit/direction; None if unusable."""
    try:
        e, sl, x = float(row["entry"]), float(row["stop"]), float(row["exit"])
        d = float(row.get("direction", 0) or 0)
        risk = abs(e - sl)
        if risk <= 0 or d == 0:
            return None
        return ((x - e) * d) / risk
    except (KeyError, ValueError, TypeError):
        return None


def _stats(rows):
    """(n, win_rate_pct, profit_factor, mean_R) for a list of trade rows."""
    n = len(rows)
    if not n:
        return 0, None, None, None
    pnls = [float(r["pnl"]) for r in rows if r.get("pnl") not in (None, "")]
    wins = sum(1 for p in pnls if p > 0)
    gp = sum(p for p in pnls if p > 0)
    gl = -sum(p for p in pnls if p <= 0)
    pf = (gp / gl) if gl > 0 else float("inf")
    wr = 100.0 * wins / len(pnls) if pnls else None
    rs = [v for v in (_r(r) for r in rows) if v is not None]
    mr = sum(rs) / len(rs) if rs else None
    return n, wr, pf, mr


def _fmt(v, kind):
    if v is None:
        return "—"
    if kind == "wr":
        return f"{v:.1f}%"
    if kind == "pf":
        return "inf" if v == float("inf") else f"{v:.2f}"
    if kind == "r":
        return f"{v:+.2f}R"
    return str(v)


def _split(rows):
    is_rows = [r for r in rows if _year(r.get("opened_at")) in ("2022", "2023")]
    oos_rows = [r for r in rows if _year(r.get("opened_at")) in ("2024", "2025")]
    return is_rows, oos_rows


def _line(label, rows):
    (isn, iswr, ispf, isr) = _stats(_split(rows)[0])
    (on, owr, opf, orr) = _stats(_split(rows)[1])
    return (f"| {label} | {isn}/{on} | {_fmt(iswr,'wr')} | {_fmt(owr,'wr')} | "
            f"{_fmt(ispf,'pf')} | {_fmt(opf,'pf')} | {_fmt(isr,'r')} | {_fmt(orr,'r')} |")


def analyse(path):
    if not os.path.exists(path):
        return [f"# PWH/PWL reaction study", "",
                f"ERROR: no trade dump at `{path}`. Run the backtest first "
                f"(run_backtest_histdata.py writes it)."]
    with open(path) as f:
        rows = list(csv.DictReader(f))
    if not rows or "amd_liq_run" not in rows[0]:
        return ["# PWH/PWL reaction study", "",
                "ERROR: trade dump missing the `amd_liq_run` column — re-run the "
                "backtest on the current branch (the classifier logs it)."]

    total = len(rows)
    have = sum(1 for r in rows if (r.get("amd_liq_run") or "") in BUCKETS
               and r.get("amd_liq_run"))
    baseline = [r for r in rows if (r.get("amd_liq_run") or "none") in ("none", "")]

    L = ["# Previous-week high/low (PWH/PWL) reaction study", "",
         "The P41 question one timeframe up: does sweeping a **weekly** pool "
         "(PWH/PWL) predict a better reversal, the way sweeping a **daily** pool "
         "(PDH/PDL) did? Measured on the full trade set (all pairs, 2022-2025). "
         "`amd_liq_run` classifies the pool the AMD sweep ran, weekly-priority.", "",
         f"_trades: {total} · with a classified sweep pool: {have} · "
         f"IS = 2022-23, OOS = 2024-25_", "",
         "**Watch n:** weekly sweeps are rarer than daily. A bucket under ~15 per "
         "split is noise, not signal — the P41 discipline (consistent in BOTH years, "
         "adequate n) applies.", "",
         "## By pool the sweep ran", "",
         "| pool | n IS/OOS | WR IS | WR OOS | PF IS | PF OOS | meanR IS | meanR OOS |",
         "|---|---|---|---|---|---|---|---|"]
    for b in BUCKETS:
        sub = [r for r in rows if (r.get("amd_liq_run") or "") == b]
        if sub:
            L.append(_line(f"`{b}`", sub))

    L += ["", "## Rolled up — weekly vs daily vs none (the money table)", "",
          "| group | n IS/OOS | WR IS | WR OOS | PF IS | PF OOS | meanR IS | meanR OOS |",
          "|---|---|---|---|---|---|---|---|"]
    for name, keys in GROUPS:
        # "none" and "" both mean no pool → the no-major-pool group.
        sub = [r for r in rows if (r.get("amd_liq_run") or "none") in keys]
        if sub:
            L.append(_line(name, sub))

    # Verdict on the weekly bucket vs baseline.
    weekly = [r for r in rows if (r.get("amd_liq_run") or "") in ("pwh", "pwl")]
    wi, wo = _split(weekly)
    bi, bo = _split(baseline)
    (wisn, wiswr, _, _) = _stats(wi)
    (won, wowr, _, _) = _stats(wo)
    (_, biswr, _, _) = _stats(bi)
    (_, bowr, _, _) = _stats(bo)
    L += ["", "## Verdict — is a PWH/PWL sizing lever justified?", ""]
    if wisn < 10 or won < 10:
        L += [f"⚠️ **INCONCLUSIVE — sample too small.** Weekly sweeps: {wisn} IS / "
              f"{won} OOS. Below ~10-15 per split, WR/PF are noise. Weekly pools are "
              "swept far less often than daily ones, so even 4yr may not give a "
              "tradeable sample. Report the numbers; do NOT ship a lever on this n.",
              "", "PWH/PWL remain valuable where they already are: as **target** "
              "levels (P17) and confluence sources (P18) — that use doesn't need a "
              "large sweep sample."]
    else:
        beats = (wiswr is not None and biswr is not None and wiswr > biswr
                 and wowr is not None and bowr is not None and wowr > bowr)
        if beats:
            L += [f"🟢 **Candidate lever.** Weekly-sweep WR beats the no-pool baseline "
                  f"in BOTH years ({_fmt(wiswr,'wr')} vs {_fmt(biswr,'wr')} IS, "
                  f"{_fmt(wowr,'wr')} vs {_fmt(bowr,'wr')} OOS), n {wisn}/{won}. "
                  "Worth building a PWH/PWL 1.25× sizing lever (like P41) and running "
                  "the full baseline-vs-lever + MaxDD validation before shipping."]
        else:
            L += [f"🔴 **No edge.** Weekly-sweep WR does NOT beat baseline in both years "
                  f"({_fmt(wiswr,'wr')}/{_fmt(wowr,'wr')} vs {_fmt(biswr,'wr')}/"
                  f"{_fmt(bowr,'wr')}), n {wisn}/{won}. PWH/PWL stay as targets/confluence "
                  "only — no entry-side sizing lever."]
    return L


def _selftest():
    rows = [
        {"amd_liq_run": "pwh", "pnl": "100", "opened_at": "2022-03-01 08:00:00",
         "entry": "1.1000", "stop": "1.0990", "exit": "1.1030", "direction": "1"},
        {"amd_liq_run": "pwl", "pnl": "-50", "opened_at": "2024-06-01 08:00:00",
         "entry": "1.2000", "stop": "1.2010", "exit": "1.1990", "direction": "-1"},
        {"amd_liq_run": "none", "pnl": "20", "opened_at": "2023-01-01 08:00:00",
         "entry": "1", "stop": "0.999", "exit": "1.001", "direction": "1"},
    ]
    n, wr, pf, mr = _stats(rows)
    assert n == 3, n
    assert abs(wr - 66.7) < 0.2, wr
    assert _year("2022-03-01 08:00:00") == "2022"
    r = _r(rows[0]); assert r is not None and r > 0, r
    print("selftest OK — stats, year split, R computation pass")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default=DUMP)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    lines = analyse(a.dump)
    text = "\n".join(lines) + "\n"
    with open(REPORT, "w") as f:
        f.write(text)
    print(text)
    print(f"[report → {REPORT}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
