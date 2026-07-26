#!/usr/bin/env python3
"""AMD setup-quality analysis (measurement only).

Reads the enriched trade dump (backtest.py now logs the accumulation range +
stop-run details on every trade) and measures which AMD conditions produce
winners:

  Accumulation:  range width (pips), duration (M15 bars), touches per extreme.
  Manipulation:  how deep the stop-run swept, which side, and whether the swept
                 side aligned with the trade direction.

Every table is split IS (2022-23) vs OOS (2024-25) — an effect only counts if it
holds in both. stdlib-only (no pandas) so it runs anywhere. Writes
data/amd_report.md.

    python scripts/amd_analysis.py            # after run_backtest_histdata.py
    python scripts/amd_analysis.py --trades <path>
"""
from __future__ import annotations

import argparse
import csv
import os
import statistics
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_REPO, "data")
REPORT = os.path.join(DATA_DIR, "amd_report.md")
MIN_RISK = 1e-5
IS_YEARS = {2022, 2023}
OOS_YEARS = {2024, 2025}

# Buckets (edges are lower-inclusive, upper-exclusive)
WIDTH_BUCKETS = [("tight <12", 0, 12), ("mid 12-20", 12, 20),
                 ("wide 20-28", 20, 28), ("v.wide 28+", 28, 1e9)]
DUR_BUCKETS = [("short <8", 0, 8), ("mid 8-16", 8, 16),
               ("long 16-28", 16, 28), ("v.long 28+", 28, 1e9)]
DEPTH_BUCKETS = [("shallow <3", 0, 3), ("mid 3-8", 3, 8),
                 ("deep 8-15", 8, 15), ("v.deep 15+", 15, 1e9)]


def _split(year: int) -> str:
    return "IS" if year in IS_YEARS else ("OOS" if year in OOS_YEARS else "other")


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _i(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def load_trades(path):
    candidates = [path] if path else [
        os.path.join(DATA_DIR, "histdata", "trades_dump.csv"),
        os.path.join(DATA_DIR, "trades_dump.csv"),
    ]
    src = next((c for c in candidates if c and os.path.exists(c)), None)
    if src is None:
        print("ERROR: no trades_dump.csv found. Run the backtest first:")
        print("  python run_backtest_histdata.py --years 2022 2023 2024 2025")
        sys.exit(1)
    with open(src, newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"Trade log: {src}  ({len(rows)} rows)")
    if rows and "amd_range_pips" not in rows[0]:
        print("ERROR: this dump has no amd_* columns — it was produced before the\n"
              "       AMD instrumentation. Re-run the backtest on this branch.")
        sys.exit(1)

    out = []
    for r in rows:
        if str(r.get("leg_idx", "1")).strip() not in ("1", "1.0"):
            continue
        opened = (r.get("opened_at") or "")[:10]
        try:
            year = int(opened[:4])
        except ValueError:
            continue
        pnl = _f(r.get("pnl"))
        entry, stop, exit_ = _f(r.get("entry")), _f(r.get("stop")), _f(r.get("exit"))
        direction = _i(r.get("direction"))
        if pnl is None or direction is None:
            continue
        r_mult = None
        if entry is not None and stop is not None and exit_ is not None:
            risk = abs(entry - stop)
            if risk > MIN_RISK:
                r_mult = (exit_ - entry) * direction / risk
        out.append({
            "year": year, "split": _split(year), "win": pnl > 0, "r": r_mult,
            "pair": (r.get("pair") or "").upper(),
            "entry_model": (r.get("entry_model") or "").strip() or "?",
            "range_pips": _f(r.get("amd_range_pips")),
            "range_bars": _i(r.get("amd_range_bars")),
            "touch_hi": _i(r.get("amd_touches_hi")),
            "touch_lo": _i(r.get("amd_touches_lo")),
            "sweep_side": (r.get("amd_sweep_side") or "").strip(),
            "sweep_depth": _f(r.get("amd_sweep_depth")),
            "sweep_aligned": {"True": True, "False": False}.get(
                (r.get("amd_sweep_aligned") or "").strip()),
        })
    return out


def _stats(rows):
    n = len(rows)
    if n == 0:
        return {"n": 0}
    wins = sum(1 for r in rows if r["win"])
    rs = [r["r"] for r in rows if r.get("r") is not None]
    return {"n": n, "wr": 100.0 * wins / n,
            "mean_r": statistics.fmean(rs) if rs else None}


def _fmt(s):
    if s["n"] == 0:
        return ["0", "—", "—"]
    mr = f"{s['mean_r']:+.2f}" if s["mean_r"] is not None else "n/a"
    return [str(s["n"]), f"{s['wr']:.1f}%", mr]


HDR = ["bucket", "IS n", "IS WR", "IS mR", "OOS n", "OOS WR", "OOS mR"]


def _tbl(header, rows):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _bucketed(trades, keyfn, buckets):
    rows = []
    for name, lo, hi in buckets:
        sub = [t for t in trades if (v := keyfn(t)) is not None and lo <= v < hi]
        rows.append([name]
                    + _fmt(_stats([t for t in sub if t["split"] == "IS"]))
                    + _fmt(_stats([t for t in sub if t["split"] == "OOS"])))
    return _tbl(HDR, rows)


def _by_value(trades, keyfn, values, labelfn=str):
    rows = []
    for v in values:
        sub = [t for t in trades if keyfn(t) == v]
        rows.append([labelfn(v)]
                    + _fmt(_stats([t for t in sub if t["split"] == "IS"]))
                    + _fmt(_stats([t for t in sub if t["split"] == "OOS"])))
    return _tbl(HDR, rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades")
    args = ap.parse_args()

    trades = load_trades(args.trades)
    amd = [t for t in trades if t["range_pips"] is not None]
    non = [t for t in trades if t["range_pips"] is None]
    print(f"Usable initial entries: {len(trades)}  "
          f"(with AMD setup: {len(amd)}, without: {len(non)})")
    if not amd:
        print("No AMD-tagged trades found.")
        sys.exit(1)

    L = []
    a = L.append
    a("# AMD — setup-quality analysis")
    a("")
    a("**Type:** measurement only — no engine changes.  ")
    a("Every table splits **IS (2022–23)** vs **OOS (2024–25)**; an effect only "
      "counts if it holds in both. `mR` = mean R multiple.")
    a("")
    # coverage
    def cov(rows):
        return _stats([t for t in rows])
    a("## 0. Coverage")
    a("")
    a(_tbl(["group", "IS n", "IS WR", "IS mR", "OOS n", "OOS WR", "OOS mR"],
           [["AMD setup (range+sweep)"]
            + _fmt(_stats([t for t in amd if t["split"] == "IS"]))
            + _fmt(_stats([t for t in amd if t["split"] == "OOS"])),
            ["no AMD range (breakout/other)"]
            + _fmt(_stats([t for t in non if t["split"] == "IS"]))
            + _fmt(_stats([t for t in non if t["split"] == "OOS"]))]))
    a("")

    a("## 1. Accumulation — range width")
    a("How tight was the consolidation before the sweep? (pips high−low)")
    a("")
    a(_bucketed(amd, lambda t: t["range_pips"], WIDTH_BUCKETS))
    a("")

    a("## 2. Accumulation — range duration (M15 bars)")
    a("How long did price coil? (each bar = 15 min; 8 bars = 2h, 28 = 7h)")
    a("")
    a(_bucketed(amd, lambda t: t["range_bars"], DUR_BUCKETS))
    a("")

    a("## 3. Accumulation — touches of the extremes")
    a("Fewest touches of either extreme (a cleaner double/triple-tap = more "
      "engineered liquidity).")
    a("")
    def touch_label(t):
        if t["touch_hi"] is None or t["touch_lo"] is None:
            return None
        m = min(t["touch_hi"], t["touch_lo"])
        return "2 touches" if m <= 2 else ("3 touches" if m == 3 else "4+ touches")
    a(_by_value(amd, touch_label, ["2 touches", "3 touches", "4+ touches"]))
    a("")

    a("## 4. Manipulation — stop-run depth")
    a("How far past the swept extreme price wicked before rejecting (pips). "
      "Deeper = a bigger stop-raid.")
    a("")
    a(_bucketed(amd, lambda t: t["sweep_depth"], DEPTH_BUCKETS))
    a("")

    a("## 5. Manipulation — which side was run, and did it align")
    a("`aligned` = the swept side matched the eventual trade direction "
      "(swept lows → we went long). This is the core AMD read.")
    a("")
    a(_by_value(amd, lambda t: t["sweep_aligned"], [True, False],
                labelfn=lambda v: "aligned" if v else "against"))
    a("")
    a("### Swept side (raw)")
    a("")
    a(_by_value(amd, lambda t: t["sweep_side"], ["low", "high"]))
    a("")

    a("## 6. By entry model (judas reversals are the AMD home)")
    a("")
    for m in sorted({t["entry_model"] for t in amd}):
        sub = [t for t in amd if t["entry_model"] == m]
        s_is, s_oos = _stats([t for t in sub if t["split"] == "IS"]), \
            _stats([t for t in sub if t["split"] == "OOS"])
        a(f"- **{m}** (n={len(sub)}): IS {_fmt(s_is)[1]} WR / OOS {_fmt(s_oos)[1]} WR")
    a("")

    a("## 7. Read")
    a("")
    a("Look down each table for a bucket whose **WR (and mean R) is clearly "
      "higher in BOTH the IS and OOS columns** — that's a real AMD quality "
      "signal we could turn into a conviction/size lever. A bucket that only "
      "wins in one split is noise. Small-n cells (n<20) are indicative only. "
      "Next step depends on what stands out — a sizing lever on the best "
      "bucket, or a gate on the worst, both validated on the full run.")
    a("")

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"\nReport → {REPORT}")


if __name__ == "__main__":
    main()
