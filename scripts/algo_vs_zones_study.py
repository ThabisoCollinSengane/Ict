#!/usr/bin/env python3
"""The ALGO measured against the levels price demonstrably reaches.

⚠️ READ THIS FIRST — the premise, corrected. P68b found unfilled W/D/H4 gaps are
reached 90-95% of the time. It ALSO found an identical band, same width and same
distance, on the OPPOSITE side of price is reached 90-95% of the time (six lift
cells, none above +0.8pp). So the honest statement is "price reaches nearby bands
at that rate", NOT "price is drawn to gaps." This study therefore treats a zone as
a REACHABLE LEVEL, never as a magnet, and every rate it reports carries a control.

What it asks, which nothing here has asked before: if price reaches a nearby level
~95% of the time and the algo wins 43.9% of the time, **where are our trades
sitting relative to levels price actually gets to?**

  §1 GEOMETRY — at entry, how far is the nearest unfilled zone ahead, and does our
     TARGET sit short of it, on it, or beyond it? WR/PF per bucket.

  §2 EARLY vs WRONG — the headline, and the trader's standing claim ("if our SL is
     hit then we entered early before the real move"). On trades we LOST, from the
     exit forward, does price reach the zone we were aiming at BEFORE it reaches an
     equidistant level on the OTHER side?

     First passage against a mirror level is the whole test. "Price eventually got
     there" is worthless — price eventually gets everywhere. Against the mirror:
       ~50%  -> we were WRONG about direction, full stop.
       >>50% -> we were RIGHT and EARLY, and the problem is timing, not thesis.
     Bars that touch BOTH levels are reported separately, never assigned (the
     `ran_both` lesson — folding ambiguity into one side is how a rate inflates).

  §3 the same test on WINNERS, as the comparison §2 needs.

Measurement only. Nothing here ships to the engine.

Run:  python scripts/algo_vs_zones_study.py            (needs data/trades_dump.csv)
      python scripts/algo_vs_zones_study.py --selftest
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

DATA = os.path.join(ROOT, "data", "histdata")
DUMP = None          # resolved at run time by _find_dump()
REPORT = os.path.join(ROOT, "data", "algo_vs_zones_report.md")
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)
PIP = 0.0001
NO_PUSH = False


def _find_dump():
    """Locate the backtest trade dump.

    ⚠️ `run_backtest_histdata.py` writes it to `data/histdata/` (DATA_DIR is the
    histdata folder), NOT `data/`. Six existing scripts — mm_analysis,
    amd_analysis, amd_range_analysis, amd_tickvol_analysis, p39_volume_analysis,
    pair_bias_analysis — already resolve it with exactly this candidate list.
    Hardcoding `data/trades_dump.csv` made this study report MISSING after a
    backtest that had written the dump perfectly well.
    """
    for p in (os.path.join(ROOT, "data", "histdata", "trades_dump.csv"),
              os.path.join(ROOT, "data", "trades_dump.csv")):
        if os.path.exists(p):
            return p
    return None


# ─────────────────────────── pure logic (unit-testable) ────────────────────────

def zone_ahead(gaps, price, direction):
    """Nearest unfilled zone in the trade's direction: (bottom, top, dist_pips).

    "Ahead" is purely positional — a zone entirely above price for a long, below
    for a short. Whether the gap itself formed bullish or bearish is irrelevant to
    whether price has to travel to it.
    """
    best = None
    for (bot, top) in gaps:
        if direction > 0 and bot > price:
            d = (bot - price) / PIP
        elif direction < 0 and top < price:
            d = (price - top) / PIP
        else:
            continue
        if best is None or d < best[2]:
            best = (bot, top, d)
    return best


def target_vs_zone(target_pips, zone_pips, tol=5.0):
    """Where our TARGET sits relative to the reachable zone."""
    if target_pips is None or zone_pips is None:
        return ""
    if abs(target_pips - zone_pips) <= tol:
        return "at zone"
    return "short of zone" if target_pips < zone_pips else "beyond zone"


def first_passage(highs, lows, start, up_level, dn_level, horizon):
    """Which level price touches FIRST after `start`: "up", "dn", "both", None.

    "both" is a bar that touched each level — reported, never assigned. Folding it
    into one side is exactly how a rate gets inflated (the `ran_both` lesson).
    """
    end = min(start + 1 + horizon, len(highs))
    for j in range(start + 1, end):
        hit_up = highs[j] >= up_level
        hit_dn = lows[j] <= dn_level
        if hit_up and hit_dn:
            return "both"
        if hit_up:
            return "up"
        if hit_dn:
            return "dn"
    return None


def passage_verdict(reached, total, min_edge=10.0):
    """>>50% of resolved races won by the trade's own side = right but early."""
    if not total:
        return "", None
    pct = 100.0 * reached / total
    if pct >= 50 + min_edge:
        return "EARLY — right direction, wrong timing", pct
    if pct <= 50 - min_edge:
        return "WRONG — price went the other way first", pct
    return "COIN FLIP — no directional information", pct


def pf(gain, loss):
    return float("inf") if loss == 0 else gain / loss


# ─────────────────────────────── data plumbing ────────────────────────────────

def _load_utc(sym):
    """HistData M1 -> UTC. Mirrors run_backtest_histdata (EST +5h)."""
    import pandas as pd
    frames = []
    for y in IS_YEARS + OOS_YEARS:
        p = os.path.join(DATA, f"{sym}_{y}.csv")
        if os.path.exists(p):
            frames.append(pd.read_csv(p, sep=";", header=None,
                                      names=["dt", "o", "h", "l", "c", "v"]))
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    df = df.drop_duplicates("dt").sort_values("dt").set_index("dt")
    df.index = (df.index + pd.Timedelta(hours=5)).tz_localize("UTC")
    return df[["o", "h", "l", "c"]]


def _unfilled_gaps_at(bars, upto_pos, lookback=400):
    """Every gap confirmed before `upto_pos` and NOT yet traded into by then.

    ⚠️ COMPLETED bars only — `upto_pos - 1`. `searchsorted(t, "right")` lands
    PAST the bar that CONTAINS t, so a plain `[:upto_pos]` slice ends on the
    still-forming bar, which carries the whole period's High and Low including
    the hours after t. That is precisely the `_draw_ladder` lookahead that
    manufactured P67 and a +3.6 PF in P70: a big-range day fills nearby gaps and
    pushes the nearest zone further away, so "our target is short of the zone"
    becomes partly a label for "today moved a lot" — the outcome.
    """
    from fvg_draw_study import find_fvgs
    end = max(0, upto_pos - 1)
    lo = max(0, end - lookback)
    h = bars["h"].to_numpy()[lo:end]
    l = bars["l"].to_numpy()[lo:end]
    out = []
    for (i, bot, top, _d) in find_fvgs(h, l):
        # untouched between confirmation and now
        if any(l[j] <= top and h[j] >= bot for j in range(i + 1, len(h))):
            continue
        out.append((bot, top))
    return out


def run(zone_tfs, horizon_h, lookback):
    import pandas as pd

    dump = DUMP or _find_dump()
    if dump is None:
        print("  MISSING trades_dump.csv — looked in:")
        print(f"    {os.path.join(ROOT, 'data', 'histdata', 'trades_dump.csv')}")
        print(f"    {os.path.join(ROOT, 'data', 'trades_dump.csv')}")
        print("  Run `python run_backtest_histdata.py` first.")
        return 1
    print(f"  trade dump: {dump}")
    td = pd.read_csv(dump)
    need = {"opened_at", "closed_at", "pair", "direction", "entry", "exit",
            "target", "pnl"}
    miss = need - set(td.columns)
    if miss:
        print(f"  trades_dump.csv lacks {sorted(miss)}")
        return 1
    td = td.dropna(subset=sorted(need))
    # NB no leading underscores: itertuples renames those to positional fields,
    # so r.t_open is an AttributeError on the first row. Documented in P71 and
    # reintroduced here anyway — which is why the end-to-end drive exists.
    td["t_open"] = pd.to_datetime(td["opened_at"], utc=True, errors="coerce")
    td["t_close"] = pd.to_datetime(td["closed_at"], utc=True, errors="coerce")
    td = td[td.t_open.notna() & td.t_close.notna()]

    series, h1s = {}, {}
    for pair in sorted(td["pair"].unique()):
        m1 = _load_utc(pair)
        if m1 is None:
            continue
        h1s[pair] = m1.resample("1h").agg({"o": "first", "h": "max",
                                           "l": "min", "c": "last"}).dropna()
        for tf, rule in zone_tfs.items():
            series[(pair, tf)] = m1.resample(rule).agg(
                {"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()

    geo = {}        # (split, bucket) -> stats
    race = {}       # (split, won/lost) -> counts
    dist = {"lost": [], "won": []}
    for r in td.itertuples(index=False):
        pair = r.pair
        if pair not in h1s:
            continue
        split = "IS" if r.t_open.year in IS_YEARS else "OOS"
        direction = int(r.direction)
        entry, target = float(r.entry), float(r.target)
        won = float(r.pnl) > 0

        # ── nearest unfilled zone ahead, across the requested timeframes ───────
        best = None
        for tf in zone_tfs:
            bars = series.get((pair, tf))
            if bars is None or not len(bars):
                continue
            pos = bars.index.searchsorted(r.t_open, side="right")
            if pos < 5:
                continue
            z = zone_ahead(_unfilled_gaps_at(bars, pos, lookback), entry, direction)
            if z and (best is None or z[2] < best[2]):
                best = z
        if best is None:
            continue
        zbot, ztop, zdist = best
        tdist = abs(target - entry) / PIP
        bucket = target_vs_zone(tdist, zdist)
        a = geo.setdefault((split, bucket), {"n": 0, "w": 0, "g": 0.0, "l": 0.0})
        a["n"] += 1
        a["w"] += won
        a["g" if won else "l"] += abs(float(r.pnl))
        (dist["won"] if won else dist["lost"]).append(zdist)

        # ── §2/§3 first passage AFTER the trade closed ────────────────────────
        hb = h1s[pair]
        xpos = hb.index.searchsorted(r.t_close, side="right") - 1
        if xpos < 0 or xpos >= len(hb) - 2:
            continue
        px = float(r.exit)
        # our zone's near edge, and a MIRROR level the same distance the other way
        near = zbot if direction > 0 else ztop
        gap_pips = abs(near - px) / PIP
        if gap_pips <= 0:
            continue
        mirror = px - direction * gap_pips * PIP
        up_lvl, dn_lvl = (near, mirror) if direction > 0 else (mirror, near)
        res = first_passage(hb["h"].to_numpy(), hb["l"].to_numpy(), xpos,
                            up_lvl, dn_lvl, horizon_h)
        key = (split, "won" if won else "lost")
        c = race.setdefault(key, {"ours": 0, "mirror": 0, "both": 0, "none": 0})
        if res is None:
            c["none"] += 1
        elif res == "both":
            c["both"] += 1
        elif (res == "up") == (direction > 0):
            c["ours"] += 1
        else:
            c["mirror"] += 1

    _write(geo, race, dist, zone_tfs, horizon_h)
    return 0


def _med(v):
    s = sorted(v)
    return s[len(s) // 2] if s else None


def _write(geo, race, dist, zone_tfs, horizon_h):
    L = ["# The algo measured against reachable zones", "",
         "**Premise, corrected.** P68b found unfilled W/D/H4 gaps are reached "
         "90-95% of the time — and that an identical band the same distance away "
         "on the OPPOSITE side of price is reached 90-95% too. So a zone here is "
         "a REACHABLE LEVEL, never a magnet, and every rate below carries a "
         "control. The question is not whether gaps pull price; it is **where our "
         "trades sit relative to levels price demonstrably gets to.**", ""]

    L += ["## 1. Geometry — where our TARGET sits vs the nearest zone ahead", "",
          "```", f"{'split':<5} {'target vs zone':<15} {'trades':>7} {'wins':>5} "
          f"{'WR%':>6} {'PF':>7}", "-" * 50]
    for split in ("IS", "OOS"):
        for b in ("short of zone", "at zone", "beyond zone"):
            a = geo.get((split, b))
            if not a:
                continue
            L.append(f"{split:<5} {b:<15} {a['n']:>7} {a['w']:>5} "
                     f"{100*a['w']/a['n']:>5.1f}% {pf(a['g'], a['l']):>7.2f}")
    L += ["```", "",
          f"*Median distance to the nearest zone ahead at entry — "
          f"winners {_med(dist['won']) or 0:.0f} pips, losers "
          f"{_med(dist['lost']) or 0:.0f} pips.*", ""]

    L += ["## 2 & 3. EARLY or WRONG — the first-passage race after our exit", "",
          f"From the bar after each trade closed, which came first within "
          f"**{horizon_h} hours**: the zone we were aiming at, or a MIRROR level "
          f"the same distance on the other side of our exit?", "",
          "**This is the whole test.** \"Price eventually got there\" is worthless "
          "— price eventually gets everywhere. Against an equidistant mirror, "
          "**~50% means we were simply WRONG about direction**; well above 50% "
          "means we were **RIGHT and EARLY**, and the problem is timing. Bars that "
          "touched both levels are reported, never assigned.", "", "```",
          f"{'split':<5} {'outcome':<7} {'ours':>6} {'mirror':>7} {'both':>6} "
          f"{'neither':>8} {'ours%':>7}  verdict", "-" * 78]
    for split in ("IS", "OOS"):
        for res in ("lost", "won"):
            c = race.get((split, res))
            if not c:
                continue
            resolved = c["ours"] + c["mirror"]
            verdict, p = passage_verdict(c["ours"], resolved)
            L.append(f"{split:<5} {res:<7} {c['ours']:>6} {c['mirror']:>7} "
                     f"{c['both']:>6} {c['none']:>8} "
                     f"{('—' if p is None else f'{p:.1f}%'):>7}  {verdict}")
    L += ["```", "",
          "The **lost** rows are the ones that matter. If they read EARLY, the "
          "thesis was right and the stop was in the wrong place or the entry too "
          "soon — a timing problem, and the first thing in this project that would "
          "point at a fix rather than a null. If they read COIN FLIP, the losses "
          "were simply wrong-way trades and no amount of stop or entry tuning "
          "recovers them.", ""]

    L += ["---", "",
          "Measurement only; nothing ships. Zones scanned on "
          f"{', '.join(zone_tfs)}; a zone counts only if it was confirmed before "
          "entry and still unfilled at entry."]

    text = "\n".join(L) + "\n"
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(text)
    _safe_print(text)
    if not NO_PUSH:
        _publish(REPORT)


def _safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(enc, "replace").decode(enc, "replace"))


def _publish(path):
    import subprocess

    def _git(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)

    _git("add", "-f", path)
    if _git("diff", "--cached", "--quiet", "--", path).returncode == 0:
        print(f"\n  report unchanged — paste {os.path.basename(path)} if needed.")
        return
    sha = (_git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown")
    if _git("commit", "-q", "-m", f"algo-vs-zones report (auto, on {sha})").returncode:
        print("\n  (commit failed — paste the report above)")
        return
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    p = _git("push", "origin", "HEAD")
    print(f"\n  RESULTS PUSHED — Claude can read data/{os.path.basename(path)}"
          if p.returncode == 0 else
          "\n  (auto-push failed — paste the report above)\n" + p.stderr[-300:])


# ──────────────────────────────── selftest ────────────────────────────────────

def selftest():
    gaps = [(1.1050, 1.1060), (1.1100, 1.1110), (1.0900, 1.0910)]
    z = zone_ahead(gaps, 1.1000, +1)
    assert z[0] == 1.1050 and abs(z[2] - 50) < 1e-6, z      # nearest ABOVE
    z = zone_ahead(gaps, 1.1000, -1)
    assert z[1] == 1.0910 and abs(z[2] - 90) < 1e-6, z      # nearest BELOW
    assert zone_ahead([(1.09, 1.11)], 1.10, +1) is None     # straddles price
    assert zone_ahead([], 1.10, +1) is None

    assert target_vs_zone(30, 50) == "short of zone"
    assert target_vs_zone(48, 50) == "at zone"
    assert target_vs_zone(70, 50) == "beyond zone"
    assert target_vs_zone(None, 50) == "" and target_vs_zone(30, None) == ""

    #                 0     1     2     3
    h = [1.1000, 1.1020, 1.1060, 1.1000]
    l = [1.0990, 1.0985, 1.1010, 1.0900]
    # up 1.1050 / dn 1.0950 -> bar 2 takes the upside first
    assert first_passage(h, l, 0, 1.1050, 1.0950, 5) == "up"
    # a bar that touches BOTH is never assigned
    hb = [1.1000, 1.1060]
    lb = [1.0990, 1.0940]
    assert first_passage(hb, lb, 0, 1.1050, 1.0950, 5) == "both"
    # neither reached inside the horizon
    assert first_passage(h, l, 0, 1.2000, 0.9000, 5) is None
    # the horizon is respected: the move is there, just too late
    assert first_passage(h, l, 0, 1.1050, 1.0950, 1) is None

    assert passage_verdict(70, 100)[0].startswith("EARLY")
    assert passage_verdict(30, 100)[0].startswith("WRONG")
    assert passage_verdict(52, 100)[0].startswith("COIN FLIP")
    assert passage_verdict(0, 0)[1] is None
    assert pf(10, 0) == float("inf") and pf(10, 5) == 2.0
    print("selftest OK — zone_ahead (both sides, straddle, empty), target bucket, "
          "first passage incl. the both-touched bar and the horizon, verdict")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tfs", default="W,D,240T")
    ap.add_argument("--horizon-hours", type=int, default=120,
                    help="hours after our exit in which the race is run (5 days)")
    ap.add_argument("--lookback", type=int, default=400,
                    help="bars of history scanned for unfilled zones")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    global NO_PUSH
    NO_PUSH = a.no_push
    rules = {"W": "7D", "D": "1D", "240T": "240min", "60T": "60min"}
    tfs = {t: rules[t] for t in a.tfs.split(",") if t in rules}
    return run(tfs, a.horizon_hours, a.lookback)


if __name__ == "__main__":
    sys.exit(main())
