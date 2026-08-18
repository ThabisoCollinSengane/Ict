#!/usr/bin/env python3
"""AMD range & sweep analysis: what are the typical consolidation ranges,
Judas sweep depths, and breakout distances — per pair, per session, winners
vs losers. Reads the trade dump from the last backtest run.

Usage:
    python scripts/amd_range_analysis.py            # writes data/amd_range_report.md
    python scripts/amd_range_analysis.py --selftest  # no data needed
"""
from __future__ import annotations
import argparse, os, subprocess, sys
from collections import defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DUMP_CANDIDATES = [
    os.environ.get("TRADE_CSV"),
    os.path.join(_ROOT, "data", "histdata", "trades_dump.csv"),
    os.path.join(_ROOT, "data", "trades_dump.csv"),
]
DUMP = next((p for p in _DUMP_CANDIDATES if p and os.path.exists(p)),
            _DUMP_CANDIDATES[1])
REPORT = os.path.join(_ROOT, "data", "amd_range_report.md")


def _median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def _pct(xs, p):
    if not xs:
        return None
    s = sorted(xs)
    idx = int(len(s) * p / 100)
    return s[min(idx, len(s) - 1)]


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _fmt(v):
    return f"{v:.1f}" if v is not None else "—"


def _bucket_stats(values):
    if not values:
        return {"n": 0, "median": None, "mean": None, "p25": None, "p75": None,
                "p10": None, "p90": None, "min": None, "max": None}
    return {
        "n": len(values),
        "median": _median(values),
        "mean": _mean(values),
        "p25": _pct(values, 25),
        "p75": _pct(values, 75),
        "p10": _pct(values, 10),
        "p90": _pct(values, 90),
        "min": min(values),
        "max": max(values),
    }


def _is_base_row(row):
    et = str(row.get("entry_type", ""))
    em = str(row.get("entry_model", ""))
    return em != "mm_standalone" and not et.startswith(("mm_", "mmstd_"))


def _table_header():
    return ("| Bucket | n | Median | Mean | P25 | P75 | P10 | P90 | Min | Max |\n"
            "|---|---|---|---|---|---|---|---|---|---|")


def _table_row(label, s):
    return (f"| {label} | {s['n']} | {_fmt(s['median'])} | {_fmt(s['mean'])} | "
            f"{_fmt(s['p25'])} | {_fmt(s['p75'])} | {_fmt(s['p10'])} | "
            f"{_fmt(s['p90'])} | {_fmt(s['min'])} | {_fmt(s['max'])} |")


def build_report(rows):
    base = [r for r in rows if _is_base_row(r)]

    range_vals = [float(r["amd_range_pips"]) for r in base
                  if r.get("amd_range_pips") and str(r["amd_range_pips"]) not in ("", "nan", "None")]
    sweep_vals = [float(r["amd_sweep_depth"]) for r in base
                  if r.get("amd_sweep_depth") and str(r["amd_sweep_depth"]) not in ("", "nan", "None")]
    range_bars = [int(float(r["amd_range_bars"])) for r in base
                  if r.get("amd_range_bars") and str(r["amd_range_bars"]) not in ("", "nan", "None")]

    L = ["# AMD Range & Sweep Analysis — your live price action reference",
         "",
         f"_{len(base)} base-algo trades analysed. All values in pips._",
         ""]

    # ── 1. Overall consolidation range ──
    L += ["## 1. Consolidation range (accumulation) — how wide is the coil?", "",
          "This is the M15 range the algo detected before the Judas sweep.", "",
          _table_header()]
    L.append(_table_row("ALL trades", _bucket_stats(range_vals)))
    L.append("")

    # by pair
    L += ["### By pair", "", _table_header()]
    for pair in sorted(set(r.get("pair", "?") for r in base)):
        vals = [float(r["amd_range_pips"]) for r in base
                if r.get("pair") == pair and r.get("amd_range_pips")
                and str(r["amd_range_pips"]) not in ("", "nan", "None")]
        L.append(_table_row(pair, _bucket_stats(vals)))
    L.append("")

    # by session
    L += ["### By session", "", _table_header()]
    for sess in ("london", "ny"):
        vals = [float(r["amd_range_pips"]) for r in base
                if r.get("profile") == sess and r.get("amd_range_pips")
                and str(r["amd_range_pips"]) not in ("", "nan", "None")]
        L.append(_table_row(sess.title(), _bucket_stats(vals)))
    L.append("")

    # winners vs losers
    L += ["### Winners vs Losers", "", _table_header()]
    for label, filt in [("Winners", lambda r: float(r.get("pnl", 0)) > 0),
                        ("Losers", lambda r: float(r.get("pnl", 0)) <= 0)]:
        vals = [float(r["amd_range_pips"]) for r in base
                if filt(r) and r.get("amd_range_pips")
                and str(r["amd_range_pips"]) not in ("", "nan", "None")]
        L.append(_table_row(label, _bucket_stats(vals)))
    L.append("")

    # ── 2. Judas sweep depth ──
    L += ["## 2. Judas sweep depth — how far does the stop-hunt go?", "",
          "Pips beyond the range extreme that the manipulation wick reaches.", "",
          _table_header()]
    L.append(_table_row("ALL trades", _bucket_stats(sweep_vals)))
    L.append("")

    L += ["### By pair", "", _table_header()]
    for pair in sorted(set(r.get("pair", "?") for r in base)):
        vals = [float(r["amd_sweep_depth"]) for r in base
                if r.get("pair") == pair and r.get("amd_sweep_depth")
                and str(r["amd_sweep_depth"]) not in ("", "nan", "None")]
        L.append(_table_row(pair, _bucket_stats(vals)))
    L.append("")

    L += ["### By session", "", _table_header()]
    for sess in ("london", "ny"):
        vals = [float(r["amd_sweep_depth"]) for r in base
                if r.get("profile") == sess and r.get("amd_sweep_depth")
                and str(r["amd_sweep_depth"]) not in ("", "nan", "None")]
        L.append(_table_row(sess.title(), _bucket_stats(vals)))
    L.append("")

    L += ["### Winners vs Losers", "", _table_header()]
    for label, filt in [("Winners", lambda r: float(r.get("pnl", 0)) > 0),
                        ("Losers", lambda r: float(r.get("pnl", 0)) <= 0)]:
        vals = [float(r["amd_sweep_depth"]) for r in base
                if filt(r) and r.get("amd_sweep_depth")
                and str(r["amd_sweep_depth"]) not in ("", "nan", "None")]
        L.append(_table_row(label, _bucket_stats(vals)))
    L.append("")

    # ── 3. Range duration ──
    L += ["## 3. Range duration (M15 bars) — how long does accumulation last?", "",
          _table_header()]
    L.append(_table_row("ALL trades", _bucket_stats(range_bars)))
    L.append("")

    L += ["### By session", "", _table_header()]
    for sess in ("london", "ny"):
        vals = [int(float(r["amd_range_bars"])) for r in base
                if r.get("profile") == sess and r.get("amd_range_bars")
                and str(r["amd_range_bars"]) not in ("", "nan", "None")]
        L.append(_table_row(sess.title(), _bucket_stats(vals)))
    L.append("")

    # ── 4. Judas vs Breakout comparison ──
    L += ["## 4. Judas reversal vs Breakout — range & sweep comparison", "",
          "The Judas sweep closes BACK inside (fake). The breakout closes BEYOND and holds (real).",
          ""]

    for model in ("judas", "breakout"):
        model_rows = [r for r in base if r.get("entry_model") == model]
        mr = [float(r["amd_range_pips"]) for r in model_rows
              if r.get("amd_range_pips") and str(r["amd_range_pips"]) not in ("", "nan", "None")]
        ms = [float(r["amd_sweep_depth"]) for r in model_rows
              if r.get("amd_sweep_depth") and str(r["amd_sweep_depth"]) not in ("", "nan", "None")]
        L += [f"### {model.title()} model", "", _table_header()]
        L.append(_table_row(f"{model} — range", _bucket_stats(mr)))
        L.append(_table_row(f"{model} — sweep", _bucket_stats(ms)))
        L.append("")

    # ── 5. Pair x Session x Model cross-tab ──
    L += ["## 5. Pair x Session detail — your quick-reference card", ""]
    for pair in sorted(set(r.get("pair", "?") for r in base)):
        L += [f"### {pair}", "", _table_header()]
        for sess in ("london", "ny"):
            sub = [r for r in base if r.get("pair") == pair and r.get("profile") == sess]
            rr = [float(r["amd_range_pips"]) for r in sub
                  if r.get("amd_range_pips") and str(r["amd_range_pips"]) not in ("", "nan", "None")]
            ss = [float(r["amd_sweep_depth"]) for r in sub
                  if r.get("amd_sweep_depth") and str(r["amd_sweep_depth"]) not in ("", "nan", "None")]
            L.append(_table_row(f"{sess.title()} range", _bucket_stats(rr)))
            L.append(_table_row(f"{sess.title()} sweep", _bucket_stats(ss)))
        L.append("")

    # ── 6. Practical thresholds ──
    L += ["## 6. Your live trading thresholds (from the data)", ""]

    range_med = _median(range_vals)
    sweep_med = _median(sweep_vals)
    range_p75 = _pct(range_vals, 75)
    sweep_p75 = _pct(sweep_vals, 75)
    range_p90 = _pct(range_vals, 90)

    if range_med is not None:
        L.append(f"- **Typical consolidation**: {_fmt(range_med)} pips (median), "
                 f"most are {_fmt(_pct(range_vals, 25))}–{_fmt(range_p75)} pips")
        L.append(f"- If range > {_fmt(range_p90)} pips → unusually wide, "
                 f"expect a bigger move or skip (extended)")
    if sweep_med is not None:
        L.append(f"- **Typical Judas sweep**: {_fmt(sweep_med)} pips beyond the range")
        L.append(f"- Most sweeps are {_fmt(_pct(sweep_vals, 25))}–{_fmt(sweep_p75)} pips deep")
        L.append(f"- If price goes > {_fmt(_pct(sweep_vals, 90))} pips beyond the range → "
                 f"likely a BREAKOUT, not a Judas fake")

    breakout_rows = [r for r in base if r.get("entry_model") == "breakout"]
    bo_sweeps = [float(r["amd_sweep_depth"]) for r in breakout_rows
                 if r.get("amd_sweep_depth") and str(r["amd_sweep_depth"]) not in ("", "nan", "None")]
    judas_rows = [r for r in base if r.get("entry_model") == "judas"]
    ju_sweeps = [float(r["amd_sweep_depth"]) for r in judas_rows
                 if r.get("amd_sweep_depth") and str(r["amd_sweep_depth"]) not in ("", "nan", "None")]

    if bo_sweeps and ju_sweeps:
        L.append("")
        L.append(f"- **Judas sweeps** (fakes) median: {_fmt(_median(ju_sweeps))} pips beyond range")
        L.append(f"- **Breakouts** (real) median: {_fmt(_median(bo_sweeps))} pips beyond range")
        diff = (_median(bo_sweeps) or 0) - (_median(ju_sweeps) or 0)
        if diff > 0:
            L.append(f"- **The gap**: breakouts travel ~{_fmt(diff)} pips MORE than Judas fakes")
            L.append(f"- Rule of thumb: if price holds > {_fmt(_pct(ju_sweeps, 90))} pips "
                     f"beyond the range → it's probably a breakout, not a sweep")

    L.append("")
    L += ["## 7. How to use this live", "",
          "1. **Mark the M15 consolidation range** — expect it to be ~" +
          _fmt(range_med) + " pips wide",
          "2. **Wait for the sweep** — price pokes " + _fmt(sweep_med) +
          " pips beyond one side",
          "3. **If it closes back inside** → Judas fake, fade it (your best setup)",
          "4. **If it holds beyond " + _fmt(_pct(ju_sweeps, 90) if ju_sweeps else None) +
          " pips** → breakout, follow it (need triple confirmation: EU+GU+DXY)",
          "5. **Stop goes beyond the sweep extreme** — the M1 ITH/ITL one tier up",
          ""]

    return "\n".join(L) + "\n"


def _publish():
    def _git(*a):
        return subprocess.run(["git", *a], cwd=_ROOT, capture_output=True, text=True)
    _git("add", "-f", REPORT)
    _git("commit", "-q", "-m", "AMD range & sweep analysis (auto)")
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    if _git("push", "origin", "HEAD").returncode == 0:
        print("\nRESULTS PUSHED — read data/amd_range_report.md")
    else:
        print("\n(auto-push failed — read the report above)")


def _selftest():
    rows = [
        {"pair": "EURUSD", "direction": -1, "entry_type": "fvg_m5", "entry_model": "judas",
         "profile": "london", "amd_range_pips": 15.2, "amd_range_bars": 12,
         "amd_sweep_depth": 4.3, "pnl": 100.0},
        {"pair": "EURUSD", "direction": -1, "entry_type": "ob_m15", "entry_model": "judas",
         "profile": "london", "amd_range_pips": 22.1, "amd_range_bars": 18,
         "amd_sweep_depth": 6.1, "pnl": -20.0},
        {"pair": "GBPUSD", "direction": -1, "entry_type": "fvg_m5", "entry_model": "breakout",
         "profile": "ny", "amd_range_pips": 18.5, "amd_range_bars": 10,
         "amd_sweep_depth": 9.8, "pnl": 50.0},
        {"pair": "GBPUSD", "direction": 1, "entry_type": "mm_fvg_m5",
         "entry_model": "mm_standalone", "profile": "ny", "amd_range_pips": 10.0,
         "amd_range_bars": 8, "amd_sweep_depth": 3.0, "pnl": -5.0},
    ]
    out = build_report(rows)
    assert "Consolidation range" in out
    assert "Judas sweep depth" in out
    assert "Judas reversal vs Breakout" in out
    assert "live trading thresholds" in out
    assert _median([4.3, 6.1, 9.8]) == 6.1
    assert _bucket_stats([10, 20, 30])["median"] == 20
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return 0
    if not os.path.exists(DUMP):
        print(f"**ERROR: no trade dump at {DUMP}.** Run a backtest first:\n\n"
              "  python run_backtest_histdata.py --years 2022 2023 2024 2025\n")
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
