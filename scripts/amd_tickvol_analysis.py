#!/usr/bin/env python3
"""AMD × tick-volume signature + winners-vs-losers deep dive (measurement only).

Joins the P39 tick aggregation to per-trade AMD phase timestamps and profiles
tick volume across the cycle, then digs into what LOSERS do differently from
WINNERS — across PD-array type, side, session, and PDH/PDL liquidity.

Phases (ratio to each trade's own pre-accumulation baseline):
  Accumulation  coil bars              (expect quiet <1x)
  Run-into-entry the 6 M5 bars before entry — the MSS→mitigation run-up
  Manipulation  the M5 sweep bar        (option-B: exact M5 bar, not the M15 proxy)
  Distribution  entry → exit
  PD array      the entry bar (OB/FVG mitigation)

Every table splits IS (2022) vs OOS (2024) and, where relevant, winners vs
losers — an effect only counts if it holds in both years.

stdlib-only. Needs data/p39_agg/ + a dump from the option-B instrumented
backtest. Writes data/amd_tickvol_report.md.
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
MIN_BASELINE = 8
RUNUP_BARS = 6            # M5 bins before entry = the MSS→mitigation run-in (30 min)
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


def _array_type(entry_type):
    et = (entry_type or "").lower()
    if "fvg" in et:
        return "FVG"
    if "breaker" in et:
        return "breaker"
    if "ob" in et:
        return "OB"
    return "other"


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
        if opened is None or accum_s is None:
            continue
        try:
            pnl = float(r.get("pnl"))
            direction = int(float(r.get("direction")))
        except (TypeError, ValueError):
            continue
        yr = datetime.fromtimestamp(opened, timezone.utc).year
        out.append({
            "pair": (r.get("pair") or "").upper(),
            "year": yr, "split": _split(yr), "win": pnl > 0,
            "opened": opened, "closed": _parse_dt(r.get("closed_at")),
            "accum_s": accum_s, "accum_e": _parse_dt(r.get("amd_accum_end")),
            "sweep_t": _parse_dt(r.get("amd_sweep_time_m5")) or _parse_dt(r.get("amd_sweep_time")),
            "sweep_side": (r.get("amd_sweep_side") or "").strip(),
            "array": _array_type(r.get("entry_type")),
            "side": "buy" if direction > 0 else "sell",
            "session": (r.get("profile") or r.get("session_side") or "?").strip(),
            "pdliq": {"True": True, "False": False}.get((r.get("amd_swept_pdliq") or "").strip()),
            "zone": (r.get("amd_entry_zone") or "").strip(),
        })
    return out


def _mean_ticks(s, lo, hi):
    vals = [s[b][0] for b in range(lo - lo % M5, hi, M5) if b in s]
    return statistics.fmean(vals) if vals else None


def measure(trades, series):
    out = []
    for t in trades:
        s = series.get(t["pair"])
        if not s or t["accum_e"] is None:
            continue
        a0 = t["accum_s"] - t["accum_s"] % M5
        base_vals = [s[a0 - i * M5][0] for i in range(1, BASELINE_BARS + 1)
                     if (a0 - i * M5) in s]
        if len(base_vals) < MIN_BASELINE:
            continue
        base = statistics.fmean(base_vals)
        if base <= 0:
            continue
        rec = {k: t[k] for k in ("split", "win", "pair", "array", "side",
                                 "session", "pdliq", "zone")}
        am = _mean_ticks(s, t["accum_s"], t["accum_e"] + 900)
        rec["accum"] = am / base if am is not None else None
        eb = t["opened"] - t["opened"] % M5
        # run-into-entry: the RUNUP_BARS M5 bins immediately before the entry bin
        ru = [s[eb - i * M5][0] for i in range(1, RUNUP_BARS + 1) if (eb - i * M5) in s]
        rec["runup"] = (statistics.fmean(ru) / base) if ru else None
        rec["entry"] = (s[eb][0] / base) if eb in s else None
        # sweep (M5-exact bin), plus absorption from its delta
        rec["sweep"] = rec["absorb"] = None
        if t["sweep_t"] is not None:
            sb = t["sweep_t"] - t["sweep_t"] % M5
            if sb in s:
                tk, bu, se, _n = s[sb]
                rec["sweep"] = tk / base
                net = bu - se
                rec["absorb"] = ((t["sweep_side"] == "low" and net > 0) or
                                 (t["sweep_side"] == "high" and net < 0))
        if t["closed"] and t["closed"] > t["opened"]:
            dm = _mean_ticks(s, t["opened"], t["closed"])
            rec["dist"] = dm / base if dm is not None else None
        else:
            rec["dist"] = None
        out.append(rec)
    return out


def _mean(rows, key):
    v = [r[key] for r in rows if r.get(key) is not None]
    return statistics.fmean(v) if v else None


def _med(rows, key):
    v = [r[key] for r in rows if r.get(key) is not None]
    return statistics.median(v) if v else None


def _wr(rows):
    return (100.0 * sum(1 for r in rows if r["win"]) / len(rows)) if rows else None


def _tbl(header, rows):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


PHASES = [("accum", "Accumulation"), ("runup", "Run-into-entry"),
          ("sweep", "Sweep (M5)"), ("dist", "Distribution"), ("entry", "PD array")]


def _fingerprint(rows):
    body = []
    for key, label in PHASES:
        m, md = _mean(rows, key), _med(rows, key)
        n = sum(1 for r in rows if r.get(key) is not None)
        body.append([label, f"{m:.2f}×" if m is not None else "—",
                     f"{md:.2f}×" if md is not None else "—", str(n)])
    return _tbl(["phase", "mean", "median", "n"], body)


def _win_lose_phase(rows):
    """Winner vs loser mean ratio per phase, with the win−lose delta."""
    body = []
    for key, label in PHASES:
        w = _mean([r for r in rows if r["win"]], key)
        l = _mean([r for r in rows if not r["win"]], key)
        d = f"{w-l:+.2f}×" if (w is not None and l is not None) else "—"
        body.append([label, f"{w:.2f}×" if w is not None else "—",
                     f"{l:.2f}×" if l is not None else "—", d])
    return _tbl(["phase", "WIN", "LOSE", "Δ win−lose"], body)


def _wr_by(rows, keyfn, values, labelfn=str):
    """WR + n by a category, split IS/OOS, plus win−lose Δ at sweep & PD array."""
    body = []
    for v in values:
        sub = [r for r in rows if keyfn(r) == v]
        s_is = [r for r in sub if r["split"] == "IS"]
        s_oos = [r for r in sub if r["split"] == "OOS"]
        wl_sweep = None
        w, l = _mean([r for r in sub if r["win"]], "sweep"), _mean([r for r in sub if not r["win"]], "sweep")
        if w is not None and l is not None:
            wl_sweep = w - l
        w2, l2 = _mean([r for r in sub if r["win"]], "entry"), _mean([r for r in sub if not r["win"]], "entry")
        wl_entry = (w2 - l2) if (w2 is not None and l2 is not None) else None
        body.append([
            labelfn(v), str(len(sub)),
            f"{_wr(s_is):.0f}%" if s_is else "—",
            f"{_wr(s_oos):.0f}%" if s_oos else "—",
            f"{wl_sweep:+.2f}×" if wl_sweep is not None else "—",
            f"{wl_entry:+.2f}×" if wl_entry is not None else "—",
        ])
    return _tbl(["segment", "n", "IS WR", "OOS WR", "sweep W−L", "PD-array W−L"], body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades")
    args = ap.parse_args()
    series = load_aggregates()
    if not series:
        sys.exit(f"ERROR: no aggregates in {AGG_DIR} — run the P39 aggregate step first.")
    m = measure(load_trades(args.trades), series)
    print(f"AMD trades with tick coverage: {len(m)} (pairs: {', '.join(sorted(series))})")
    if not m:
        sys.exit("No AMD trades overlapped the tick data.")

    L = []
    def a(x=""):
        L.append(x)

    a("# AMD × tick-volume — signature + winners-vs-losers deep dive")
    a("")
    a("Every number is a **ratio to the trade's own pre-accumulation baseline** "
      "(20 M5 bins before the coil). 1.00× = normal. Split **IS (2022)** vs "
      "**OOS (2024)**; winner-vs-loser deltas (`W−L`) only count if they hold in both.")
    a(f"Coverage: {len(m)} AMD trades with tick data (EURUSD/GBPUSD, 2022 + 2024).")
    a("")

    a("## 1. The fingerprint — all AMD trades")
    a("")
    a(_fingerprint(m))
    a("")

    a("## 2. Winners vs losers — the whole path (IS then OOS)")
    a("")
    a("The core question: what do losers do differently? A phase where **WIN "
      "beats LOSE in the same direction in BOTH years** is a real filter.")
    a("")
    for split in ("IS", "OOS"):
        sub = [r for r in m if r["split"] == split]
        a(f"### {split} ({'2022' if split == 'IS' else '2024'}) — n={len(sub)} "
          f"({sum(1 for r in sub if r['win'])} win / {sum(1 for r in sub if not r['win'])} lose)")
        a("")
        a(_win_lose_phase(sub))
        a("")

    a("## 3. By PD-array type (OB vs FVG)")
    a("`sweep W−L` / `PD-array W−L` = winners' minus losers' volume ratio there.")
    a("")
    a(_wr_by(m, lambda r: r["array"], ["FVG", "OB", "breaker"]))
    a("")

    a("## 4. By side (buying vs selling)")
    a("")
    a(_wr_by(m, lambda r: r["side"], ["buy", "sell"]))
    a("")

    a("## 5. By session")
    a("")
    sessions = sorted({r["session"] for r in m if r["session"] not in ("", "?")})
    a(_wr_by(m, lambda r: r["session"], sessions) if sessions else "_no session labels_")
    a("")

    a("## 6. Did the sweep run PDH/PDL (previous-day liquidity)?")
    a("")
    a(_wr_by(m, lambda r: r["pdliq"], [True, False],
             labelfn=lambda v: "swept PDH/PDL" if v else "no prev-day liq"))
    a("")

    a("## 7. Entry in premium vs discount (vs prior-day mid)")
    a("")
    a(_wr_by(m, lambda r: r["zone"], ["premium", "discount"]))
    a("")

    a("## 8. Absorption at the sweep (flow against the raid)")
    a("")
    hdr = ["split", "WIN absorb%", "LOSE absorb%", "n win / n lose"]
    body = []
    for split in ("IS", "OOS"):
        sub = [r for r in m if r["split"] == split and r["absorb"] is not None]
        win = [r for r in sub if r["win"]]
        los = [r for r in sub if not r["win"]]
        pw = 100 * sum(1 for r in win if r["absorb"]) / len(win) if win else None
        pl = 100 * sum(1 for r in los if r["absorb"]) / len(los) if los else None
        body.append([split, f"{pw:.0f}%" if pw is not None else "—",
                     f"{pl:.0f}%" if pl is not None else "—",
                     f"{len(win)} / {len(los)}"])
    a(_tbl(hdr, body))
    a("")

    a("## 9. Read")
    a("")
    a("§2 is the headline — scan for a phase where winners' volume beats losers' "
      "in the **same direction in both IS and OOS**. §3–§7 answer *where* it "
      "lives (which array / side / session / whether it ran PDH-PDL / premium vs "
      "discount): look for a `W−L` that is clearly positive in a high-n segment, "
      "consistent across years. Anything that only shows in one year, or only in "
      "a small-n (<20) cell, is noise — same discipline as P39.")
    a("")

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"Report → {REPORT}")


if __name__ == "__main__":
    main()
