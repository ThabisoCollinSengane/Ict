#!/usr/bin/env python3
"""AMD × tick-volume signature (measurement only).

Joins the P39 tick aggregation (per-M5-bin tick + buy/sell counts) to the AMD
phase timestamps the backtest now logs, and profiles how tick volume behaves
across the AMD cycle and at PD arrays:

  Accumulation   — mean tick volume across the coil bars     (expect LOW)
  Manipulation   — tick volume on the Judas sweep bar        (expect SPIKE)
  Distribution   — mean tick volume entry → exit             (expect ELEVATED)
  PD array       — tick volume on the entry bar = OB / FVG   (expect a reaction)
                   mitigation

Each phase is expressed as a RATIO to the trade's own pre-accumulation baseline
(mean ticks/M5-bin over the 20 bins before the coil), so trades are comparable.
Also reports directional delta (buy vs sell ticks) at the sweep and the PD array
— absorption (flow against the sweep) is the reversal tell.

Every table splits IS (2022) vs OOS (2024) and winners vs losers — the edge is
whether winners carry a different volume fingerprint than losers.

stdlib-only. Needs data/p39_agg/ (from the P39 aggregate step) + a trade dump
produced by the AMD-instrumented backtest. Writes data/amd_tickvol_report.md.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_REPO, "data")
AGG_DIR = os.path.join(DATA_DIR, "p39_agg")
REPORT = os.path.join(DATA_DIR, "amd_tickvol_report.md")

M5 = 300
BASELINE_BARS = 20
MIN_BASELINE = 8          # need at least this many bins for a trustworthy baseline
IS_YEARS = {2022, 2023}
OOS_YEARS = {2024, 2025}


def _split(y):
    return "IS" if y in IS_YEARS else ("OOS" if y in OOS_YEARS else "other")


def _parse_dt(s):
    s = (s or "").strip()
    if not s:
        return None
    s = s.replace("T", " ")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    m = re.search(r"([+-]\d{2}:?\d{2})$", s)
    if m:
        s = s[:m.start()].strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return int(datetime.strptime(s, fmt).replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    return None


def load_aggregates():
    series = defaultdict(dict)
    for path in sorted(glob.glob(os.path.join(AGG_DIR, "*_m5.csv"))):
        pair = os.path.basename(path).split("_")[0]
        with open(path) as f:
            for r in csv.DictReader(f):
                series[pair][int(r["bin_utc"])] = (
                    int(r["ticks"]), int(r["buy"]), int(r["sell"]), int(r["neutral"]))
    return series


def load_trades(path):
    cands = [path] if path else [
        os.path.join(DATA_DIR, "histdata", "trades_dump.csv"),
        os.path.join(DATA_DIR, "trades_dump.csv")]
    src = next((c for c in cands if c and os.path.exists(c)), None)
    if src is None:
        sys.exit("ERROR: no trades_dump.csv — run the backtest first.")
    with open(src, newline="") as f:
        rows = list(csv.DictReader(f))
    if rows and "amd_accum_start" not in rows[0]:
        sys.exit("ERROR: dump lacks amd_accum_start — re-run the AMD-instrumented backtest.")
    out = []
    for r in rows:
        if str(r.get("leg_idx", "1")).strip() not in ("1", "1.0"):
            continue
        opened = _parse_dt(r.get("opened_at"))
        accum_s = _parse_dt(r.get("amd_accum_start"))
        if opened is None or accum_s is None:      # AMD trades only
            continue
        try:
            pnl = float(r.get("pnl"))
        except (TypeError, ValueError):
            continue
        out.append({
            "pair": (r.get("pair") or "").upper(),
            "year": datetime.fromtimestamp(opened, timezone.utc).year,
            "split": _split(datetime.fromtimestamp(opened, timezone.utc).year),
            "win": pnl > 0,
            "opened": opened,
            "closed": _parse_dt(r.get("closed_at")),
            "accum_s": accum_s,
            "accum_e": _parse_dt(r.get("amd_accum_end")),
            "sweep_t": _parse_dt(r.get("amd_sweep_time")),
            "sweep_side": (r.get("amd_sweep_side") or "").strip(),
        })
    return out


def _mean_ticks(s, lo, hi):
    """Mean ticks/bin over bins in [lo, hi). None if none present."""
    vals = [s[b][0] for b in range(lo - lo % M5, hi, M5) if b in s]
    return statistics.fmean(vals) if vals else None


def measure(trades, series):
    out = []
    for t in trades:
        s = series.get(t["pair"])
        if not s or t["accum_e"] is None:
            continue
        a0 = t["accum_s"] - t["accum_s"] % M5
        # baseline: 20 bins before accumulation
        base_vals = [s[a0 - i * M5][0] for i in range(1, BASELINE_BARS + 1)
                     if (a0 - i * M5) in s]
        if len(base_vals) < MIN_BASELINE:
            continue
        base = statistics.fmean(base_vals)
        if base <= 0:
            continue

        rec = {"split": t["split"], "win": t["win"], "pair": t["pair"]}
        # accumulation
        am = _mean_ticks(s, t["accum_s"], t["accum_e"] + 900)
        rec["accum"] = am / base if am is not None else None
        # sweep — the densest of the sweep M15 bar's 3 M5 bins (the spike)
        rec["sweep"] = rec["absorb"] = None
        if t["sweep_t"] is not None:
            sbins = [(s[b], b) for b in (t["sweep_t"] - t["sweep_t"] % M5 + k * M5
                                         for k in range(3)) if b in s]
            if sbins:
                (tk, bu, se, _n), _ = max(sbins, key=lambda kv: kv[0][0])
                rec["sweep"] = tk / base
                net = bu - se
                rec["absorb"] = ((t["sweep_side"] == "low" and net > 0) or
                                 (t["sweep_side"] == "high" and net < 0))
        # distribution
        if t["closed"] and t["closed"] > t["opened"]:
            dm = _mean_ticks(s, t["opened"], t["closed"])
            rec["dist"] = dm / base if dm is not None else None
        else:
            rec["dist"] = None
        # PD array = entry bin
        eb = t["opened"] - t["opened"] % M5
        rec["entry"] = (s[eb][0] / base) if eb in s else None
        out.append(rec)
    return out


def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return statistics.fmean(vals) if vals else None


def _med(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return statistics.median(vals) if vals else None


def _cell(rows, key):
    m, md = _mean(rows, key), _med(rows, key)
    n = sum(1 for r in rows if r.get(key) is not None)
    return f"{m:.2f}×" if m is not None else "—", \
           f"{md:.2f}×" if md is not None else "—", str(n)


def _tbl(header, rows):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _phase_table(rows):
    hdr = ["phase", "mean ratio", "median", "n"]
    body = []
    for key, label in (("accum", "Accumulation (coil)"),
                       ("sweep", "Manipulation (Judas sweep)"),
                       ("dist", "Distribution (entry→exit)"),
                       ("entry", "PD array (OB/FVG entry)")):
        mean, med, n = _cell(rows, key)
        body.append([label, mean, med, n])
    return _tbl(hdr, body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades")
    args = ap.parse_args()

    series = load_aggregates()
    if not series:
        sys.exit(f"ERROR: no aggregates in {AGG_DIR} — run the P39 aggregate step first.")
    trades = load_trades(args.trades)
    m = measure(trades, series)
    print(f"AMD trades with tick coverage: {len(m)} "
          f"(pairs: {', '.join(sorted(series))})")
    if not m:
        sys.exit("No AMD trades overlapped the tick data (check pairs/years).")

    L, a = [], None
    L = []
    def a(x=""):
        L.append(x)

    a("# AMD × tick-volume signature")
    a("")
    a("**Type:** measurement only.  Each number is a **ratio to the trade's own "
      "pre-accumulation baseline** (mean ticks/M5-bin over the 20 bins before the "
      "coil). 1.00× = normal; <1 = quieter; >1 = busier.")
    a(f"Coverage: {len(m)} AMD trades with tick data "
      f"(EURUSD/GBPUSD, 2022 + 2024).")
    a("")

    a("## 1. The fingerprint — all AMD trades")
    a("")
    a(_phase_table(m))
    a("")
    a("ICT expectation: accumulation **quiet (<1×)**, the Judas sweep **spikes "
      "(>1×)**, distribution **elevated**, PD-array mitigation shows a **reaction**.")
    a("")

    a("## 2. Winners vs losers — does the fingerprint differ?")
    a("")
    a("This is the edge: if winning trades spike harder on the sweep, or fill the "
      "PD array on higher volume, that's a tradeable filter.")
    a("")
    for split in ("IS", "OOS"):
        sub = [r for r in m if r["split"] == split]
        a(f"### {split} ({'2022' if split=='IS' else '2024'}) — n={len(sub)}")
        a("")
        hdr = ["phase", "WIN mean", "LOSE mean", "Δ (win−lose)"]
        body = []
        for key, label in (("accum", "Accumulation"), ("sweep", "Sweep"),
                           ("dist", "Distribution"), ("entry", "PD array")):
            w = _mean([r for r in sub if r["win"]], key)
            l = _mean([r for r in sub if not r["win"]], key)
            d = (f"{w-l:+.2f}×" if (w is not None and l is not None) else "—")
            body.append([label,
                         f"{w:.2f}×" if w is not None else "—",
                         f"{l:.2f}×" if l is not None else "—", d])
        a(_tbl(hdr, body))
        a("")

    a("## 3. Directional delta at the sweep — absorption")
    a("")
    a("`absorption` = net tick flow on the sweep ran **against** the sweep "
      "direction (buyers soaking up a sell-sweep). ICT says that's the real "
      "reversal. Shown as % of trades with absorption, winners vs losers.")
    a("")
    hdr = ["split", "WIN absorb%", "LOSE absorb%", "n win / n lose"]
    body = []
    for split in ("IS", "OOS"):
        sub = [r for r in m if r["split"] == split and r["absorb"] is not None]
        win = [r for r in sub if r["win"]]
        los = [r for r in sub if not r["win"]]
        pw = 100 * sum(1 for r in win if r["absorb"]) / len(win) if win else None
        pl = 100 * sum(1 for r in los if r["absorb"]) / len(los) if los else None
        body.append([split,
                     f"{pw:.0f}%" if pw is not None else "—",
                     f"{pl:.0f}%" if pl is not None else "—",
                     f"{len(win)} / {len(los)}"])
    a(_tbl(hdr, body))
    a("")

    a("## 4. Per pair")
    a("")
    for pair in sorted({r["pair"] for r in m}):
        sub = [r for r in m if r["pair"] == pair]
        a(f"**{pair}** (n={len(sub)})")
        a("")
        a(_phase_table(sub))
        a("")

    a("## 5. Read")
    a("")
    a("First confirm the shape matches ICT theory (quiet coil → sweep spike → "
      "elevated distribution). Then look at §2: a phase where **winners' ratio "
      "beats losers' in BOTH IS and OOS** is a real volume filter — e.g. if real "
      "sweeps spike higher, gate/size on sweep volume; if winners fill the PD "
      "array on higher volume, that's an entry-quality signal. Same discipline as "
      "P39: consistent across both years, or it's noise. Small-n cells (n<20) "
      "are indicative only.")
    a("")

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"Report → {REPORT}")


if __name__ == "__main__":
    main()
