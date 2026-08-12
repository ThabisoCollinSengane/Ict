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
            "liq_run": (r.get("amd_liq_run") or "").strip() or "none",
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
                                 "session", "pdliq", "zone", "liq_run")}
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
        # Distribution trajectory: does the entry→target move run on DECLINING
        # (express/quiet) or BUILDING volume? slope = 2nd-half − 1st-half mean.
        rec["dist_slope"] = None
        if t["closed"] and t["closed"] > t["opened"]:
            dbins = [s[b][0] for b in range(eb, t["closed"] + M5, M5) if b in s]
            if len(dbins) >= 4:
                h = len(dbins) // 2
                rec["dist_slope"] = (statistics.fmean(dbins[h:])
                                     - statistics.fmean(dbins[:h])) / base
        # Approach-to-entry MINIMUM: the quietest of the entry bar + 3 bars before
        # it. The entry-hypothesis metric — did volume "die" going into the array?
        appr = [s[eb - i * M5][0] for i in range(0, 4) if (eb - i * M5) in s]
        rec["approach_min"] = (min(appr) / base) if appr else None
        # Approaching the target (higher-TF draw): volume in the last 3 bins into
        # the exit, and the peak ('huge activity') as price delivers to the draw.
        rec["tp_approach"] = rec["tp_spike"] = None
        if t["closed"]:
            xb = t["closed"] - t["closed"] % M5
            tap = [s[xb - i * M5][0] for i in range(0, 3) if (xb - i * M5) in s]
            if tap:
                rec["tp_approach"] = statistics.fmean(tap) / base
                rec["tp_spike"] = max(tap) / base
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


MAJOR = {"pwh", "pwl", "pdh", "pdl", "eqh", "eql"}


def _is_major(r):
    return r["liq_run"] in MAJOR


def _vol_bucket(r):
    v = r.get("entry")
    if v is None:
        return None
    return "low <0.9" if v < 0.9 else ("normal 0.9-1.3" if v < 1.3 else "high >1.3")


def _approach_bucket(r):
    v = r.get("approach_min")
    if v is None:
        return None
    return ("died <0.5×" if v < 0.5 else "0.5-0.8×" if v < 0.8
            else "0.8-1.2×" if v < 1.2 else ">1.2×")


def _slope_sign(r):
    v = r.get("dist_slope")
    if v is None:
        return None
    return "declining (express)" if v < 0 else "building"


def _wr_simple(rows, keyfn, values, labelfn=str):
    """WR + n split IS/OOS for a category (the liquidity/quality thread)."""
    body = []
    for v in values:
        sub = [r for r in rows if keyfn(r) == v]
        s_is = [r for r in sub if r["split"] == "IS"]
        s_oos = [r for r in sub if r["split"] == "OOS"]
        body.append([labelfn(v), f"{len(s_is)}/{len(s_oos)}",
                     f"{_wr(s_is):.0f}%" if s_is else "—",
                     f"{_wr(s_oos):.0f}%" if s_oos else "—"])
    return _tbl(["segment", "n IS/OOS", "IS WR", "OOS WR"], body)


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


def _entry_wl(rows):
    """Winners' minus losers' mean entry-bar (PD-array) volume ratio."""
    w = _mean([r for r in rows if r["win"]], "entry")
    l = _mean([r for r in rows if not r["win"]], "entry")
    return (w - l) if (w is not None and l is not None) else None


def _wr_by(rows, keyfn, values, labelfn=str):
    """WR + n by a category, split IS/OOS, with the entry-volume winner−loser Δ
    reported SEPARATELY for IS and OOS. A context whose Δ has the same sign in
    BOTH years is a real conditional-volume signal; if IS and OOS disagree, it's
    a year-flip artifact (the P39 failure mode). n split shown so small cells are
    visible."""
    body = []
    for v in values:
        sub = [r for r in rows if keyfn(r) == v]
        s_is = [r for r in sub if r["split"] == "IS"]
        s_oos = [r for r in sub if r["split"] == "OOS"]
        wl_is, wl_oos = _entry_wl(s_is), _entry_wl(s_oos)
        consistent = (wl_is is not None and wl_oos is not None
                      and (wl_is > 0) == (wl_oos > 0))
        body.append([
            labelfn(v), f"{len(s_is)}/{len(s_oos)}",
            f"{_wr(s_is):.0f}%" if s_is else "—",
            f"{_wr(s_oos):.0f}%" if s_oos else "—",
            f"{wl_is:+.2f}×" if wl_is is not None else "—",
            f"{wl_oos:+.2f}×" if wl_oos is not None else "—",
            "✅" if consistent else "✗",
        ])
    return _tbl(["segment", "n IS/OOS", "IS WR", "OOS WR",
                 "IS entryΔ", "OOS entryΔ", "same sign?"], body)


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

    a("## 3–7. Conditional volume — does high volume mean different things by context?")
    a("")
    a("**This is the P40 test.** `IS entryΔ` / `OOS entryΔ` = winners minus losers "
      "mean entry-bar volume, computed **separately per year**. If a context's Δ "
      "has the **same sign in both years** (`✅`), high entry volume genuinely "
      "means something there (P40 has a basis). If IS and OOS disagree (`✗`), it's "
      "a year-flip artifact — the P39 failure mode — and a fixed modifier would be "
      "curve-fit. Read the `same sign?` column and the n split first.")
    a("")
    a("### By PD-array type (OB vs FVG)")
    a("")
    a(_wr_by(m, lambda r: r["array"], ["FVG", "OB", "breaker"]))
    a("")

    a("### By side (buying vs selling)")
    a("")
    a(_wr_by(m, lambda r: r["side"], ["buy", "sell"]))
    a("")

    a("### By session")
    a("")
    sessions = sorted({r["session"] for r in m if r["session"] not in ("", "?")})
    a(_wr_by(m, lambda r: r["session"], sessions) if sessions else "_no session labels_")
    a("")

    a("### Did the sweep run PDH/PDL (previous-day liquidity)?")
    a("")
    a(_wr_by(m, lambda r: r["pdliq"], [True, False],
             labelfn=lambda v: "swept PDH/PDL" if v else "no prev-day liq"))
    a("")

    a("### Entry in premium vs discount (vs prior-day mid)")
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

    a("## 9. Major-liquidity runs — which pay? (the validated PDH/PDL thread)")
    a("")
    a("What the manipulation swept, ranked. `pwh/pwl` = prior-week high/low, "
      "`pdh/pdl` = prior-day, `eqh/eql` = equal highs/lows (engineered), "
      "`vah/val` = value area, `none` = a local range edge. **WR above baseline "
      "in BOTH years = a real setup-quality signal we can build on.**")
    a("")
    a(_wr_simple(m, lambda r: r["liq_run"],
                 ["pwh", "pwl", "pdh", "pdl", "eqh", "eql", "vah", "val", "none"]))
    a("")
    a("### Major liquidity (weekly / daily / equal H-L) vs none")
    a("")
    a(_wr_simple(m, _is_major, [True, False],
                 labelfn=lambda v: "ran MAJOR liq" if v else "no major liq"))
    a("")

    a("## 10. Does HIGH volume help WHEN we run major liquidity?")
    a("")
    a("Your point — high volume isn't always a reason to run. Tested only where "
      "it should matter: on trades that swept major liquidity. Entry-bar volume "
      "bucketed. If high-volume major-liq runs win MORE in both years, volume is "
      "conviction here, not a warning — a size-UP case, not a size-down.")
    a("")
    maj = [r for r in m if _is_major(r)]
    a(_wr_simple(maj, _vol_bucket, ["low <0.9", "normal 0.9-1.3", "high >1.3"])
      if maj else "_no major-liq trades in the tick window_")
    a("")

    a("## 11. Beneficial-entry recipe — major liquidity × context")
    a("")
    a("Where the major-liquidity edge concentrates (major-liq trades only).")
    a("")
    a("**× session**")
    a("")
    _sess = sorted({r["session"] for r in maj if r["session"] not in ("", "?")})
    a(_wr_simple(maj, lambda r: r["session"], _sess) if _sess else "_n/a_")
    a("")
    a("**× premium/discount**")
    a("")
    a(_wr_simple(maj, lambda r: r["zone"], ["premium", "discount"]))
    a("")
    a("**× PD-array type**")
    a("")
    a(_wr_simple(maj, lambda r: r["array"], ["FVG", "OB", "breaker"]))
    a("")

    a("## 12. ENTRY hypothesis — did tick volume DIE (<0.5×) approaching the PD array?")
    a("")
    a("Your idea: the best entry is when volume **collapses** in the PD array "
      "(coil ending → move imminent), not when it's still busy (still coiling). "
      "`approach` = the quietest volume ratio in the entry bar + 3 bars before it. "
      "If the **died <0.5×** bucket wins more in **both** years, entering on "
      "volume-death is worth building — and note it's a *new* trigger, since the "
      "current entries mostly fire on elevated volume (the tension in §1's 1.28×).")
    a("")
    a(_wr_simple(m, _approach_bucket, ["died <0.5×", "0.5-0.8×", "0.8-1.2×", ">1.2×"]))
    a("")

    a("## 13. DISTRIBUTION shape — express (quiet) move or building volume?")
    a("")
    a("Entry→target: does the move run on **declining** volume (express route — "
      "retail already chased the sweep) or **building** volume? `dist-slope` = "
      "2nd-half minus 1st-half mean volume of the hold; negative = quieter into "
      "the target.")
    a("")
    a(_wr_simple(m, _slope_sign, ["declining (express)", "building"]))
    a("")
    _w = _mean([r for r in m if r["win"]], "dist_slope")
    _l = _mean([r for r in m if not r["win"]], "dist_slope")
    if _w is not None and _l is not None:
        a(f"Mean dist-slope — **winners {_w:+.2f}× vs losers {_l:+.2f}×** "
          "(more negative = the move ran quieter into target).")
        a("")

    a("## 14. Volume approaching the target (the higher-TF draw)")
    a("")
    a("How tick volume behaves as price delivers to the draw. `tp-approach` = mean "
      "volume ratio in the last 3 bars into the exit; `tp-spike` = the peak of "
      "those (the 'huge activity' at the draw). Winners (reached the draw) vs "
      "losers (stopped) — does delivery to the draw come with a volume burst?")
    a("")
    _rows = []
    for label, sub in (("winners", [r for r in m if r["win"]]),
                       ("losers", [r for r in m if not r["win"]])):
        _rows.append([label,
                      f"{_mean(sub, 'tp_approach'):.2f}×" if _mean(sub, 'tp_approach') else "—",
                      f"{_mean(sub, 'tp_spike'):.2f}×" if _mean(sub, 'tp_spike') else "—",
                      str(sum(1 for r in sub if r.get('tp_spike') is not None))])
    a(_tbl(["group", "mean tp-approach", "mean tp-spike", "n"], _rows))
    a("")
    a("Split by year:")
    a("")
    _rows = []
    for split in ("IS", "OOS"):
        for label, pred in (("win", lambda r: r["win"]), ("lose", lambda r: not r["win"])):
            sub = [r for r in m if r["split"] == split and pred(r)]
            _rows.append([f"{split} {label}",
                          f"{_mean(sub, 'tp_approach'):.2f}×" if _mean(sub, 'tp_approach') else "—",
                          f"{_mean(sub, 'tp_spike'):.2f}×" if _mean(sub, 'tp_spike') else "—",
                          str(len(sub))])
    a(_tbl(["group", "tp-approach", "tp-spike", "n"], _rows))
    a("")

    a("## 15. Read")
    a("")
    a("**Two questions in this report:**")
    a("")
    a("1. **P40 (conditional volume) — §3–§7.** Read the `same sign?` column. A "
      "context (OB/FVG/session/zone) with `✅` in a high-n row means high entry "
      "volume genuinely means something different there in both years → P40 has a "
      "basis. Mostly `✗` → the 'conditional edge' was a 2022/2024 flip and a fixed "
      "modifier would be curve-fit (drop it).")
    a("")
    a("2. **The liquidity edge — §9–§11 (the real thread).** §9: which liquidity "
      "the sweep ran, WR per type. A type (esp. PWH/PWL, PDH/PDL) with WR above "
      "the ~45% baseline in BOTH years is a genuine setup-quality signal → build a "
      "conviction/size lever, validate on the full backtest (IS/OOS, MaxDD-neutral). "
      "§10 answers your 'high volume isn't always bad' point directly — if "
      "high-volume major-liq runs win more both years, that's a size-UP case. §11 "
      "shows where the edge concentrates (session/zone/array) for the recipe.")
    a("")
    a("3. **Entry timing & distribution — §12–§13 (your volume-death idea).** §12: "
      "if the `died <0.5×` approach bucket wins clearly more in both years, "
      "entering on volume collapse in the PD array is worth building as a new "
      "trigger (and pyramid gate). §13: if winners' `dist-slope` is consistently "
      "more negative than losers', the real move runs on quiet/express volume — "
      "which also argues for holding through low-volume drift rather than exiting "
      "on it.")
    a("")
    a("Discipline throughout: consistent across both years, n≥~20 per cell, or "
      "it's noise — same bar as P39.")
    a("")

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"Report → {REPORT}")


if __name__ == "__main__":
    main()
