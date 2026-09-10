#!/usr/bin/env python3
"""Triple liquidity raid — EURUSD + GBPUSD take highs while DXY takes lows.

The setup, in ICT terms: buy-side liquidity above BOTH pairs is raided at the
same time the dollar raids the sell-side below itself. Because the pairs are
inverse to DXY these are the SAME event expressed twice, so agreement across all
three is a genuine triple confirmation rather than three independent signals.
Structure then shifts and price reverses — pairs down, dollar up. The mirror case
(pairs take LOWS, DXY takes HIGHS) is the long side.

This measures the pattern on RAW price, independent of the strategy's entries, so
the answer is not contaminated by whatever the engine happened to trade. It asks
four things:

  1. How often does the synchronised triple raid actually occur?
  2. When it does, does price reverse — and by how much?
  3. Does the TRIPLE beat a SINGLE-pair raid? (control-1 — the whole point. If a
     lone EURUSD sweep reverses just as often, the confirmation is worthless.)
  4. Does requiring a market-structure shift AFTER the raid improve it?

Measurement only. Nothing here ships to the engine; a positive result earns an
IS/OOS validation of an actual lever, exactly as P41 did.

Run:  python scripts/triple_sweep_study.py [--tf 60T] [--window 4] [--horizon 24]
      python scripts/triple_sweep_study.py --selftest      # no data needed
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "histdata")
REPORT = os.path.join(ROOT, "data", "triple_sweep_report.md")

PAIRS = ("EURUSD", "GBPUSD")
DXY = "UDXUSD"
NO_PUSH = False
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)


# ─────────────────────────── pure logic (unit-testable) ────────────────────────

def sweep_events(highs, lows, direction):
    """Bars where price took out the most recent INTACT 3-bar fractal swing.

    direction +1 → sweeps of swing HIGHS (buy-side raided)
    direction -1 → sweeps of swing LOWS  (sell-side raided)

    A fractal high at i needs h[i] > h[i-1] and h[i] > h[i+1], so it is only
    CONFIRMED at i+1 — the level cannot be swept before it exists. After a level
    is taken we wait for the next confirmed fractal before arming again, so one
    structural high yields one event, not one per bar above it.

    Returns a list of (bar_index, level_price). O(n).
    """
    n = len(highs)
    out = []
    pending = None                     # the armed level, or None
    for i in range(1, n):
        # Sweep check first: a level armed before this bar can be taken by it.
        if pending is not None:
            if direction > 0 and highs[i] > pending:
                out.append((i, pending))
                pending = None
            elif direction < 0 and lows[i] < pending:
                out.append((i, pending))
                pending = None
        # Arm the fractal confirmed by bar i (its centre is i-1). ALWAYS take the
        # most recent one — that is the live structural reference, whether or not
        # it sits beyond the previously armed level.
        #
        # ⚠️ An earlier version only re-armed at a MORE EXTREME level
        # ("pending is None or lows[c] < pending"). In a trending market every new
        # fractal low is higher than the stale armed one, so the detector latched
        # onto a far level that price never returned to and went permanently dead:
        # 101 low-sweeps in 2022-23 and exactly ZERO in 2024-25 on equal bar
        # counts, which is what exposed it.
        c = i - 1
        if c >= 1:
            if direction > 0:
                if highs[c] > highs[c - 1] and highs[c] > highs[i]:
                    pending = highs[c]
            else:
                if lows[c] < lows[c - 1] and lows[c] < lows[i]:
                    pending = lows[c]
    return out


def align_triple(ev_a, ev_b, ev_dxy, window):
    """Indices where all three raids land within `window` bars of each other.

    ev_* are lists of (bar_index, level). Returns a list of the LAST bar index in
    each aligned trio — the moment the setup is complete and tradeable. One
    result per cluster: once a trio is formed its members are consumed, so a
    noisy run of sweeps cannot inflate the count.
    """
    ia = {i for i, _ in ev_a}
    ib = {i for i, _ in ev_b}
    id_ = {i for i, _ in ev_dxy}
    out = []
    used = set()
    for i in sorted(ia):
        if i in used:
            continue
        nb = [j for j in ib if abs(j - i) <= window and j not in used]
        nd = [j for j in id_ if abs(j - i) <= window and j not in used]
        if not nb or not nd:
            continue
        j, k = min(nb, key=lambda x: abs(x - i)), min(nd, key=lambda x: abs(x - i))
        last = max(i, j, k)
        out.append(last)
        used.update({i, j, k})
    return sorted(out)


def forward_excursion(highs, lows, start, horizon, direction, ref):
    """(favourable, adverse) pip-less excursions from `ref` over the horizon.

    direction -1 (expecting a move DOWN): favourable = ref - min(low),
    adverse = max(high) - ref. Mirrored for +1. Returns (0,0) with no room left.
    """
    lo = lows[start + 1: start + 1 + horizon]
    hi = highs[start + 1: start + 1 + horizon]
    if len(lo) == 0:
        return 0.0, 0.0
    if direction < 0:
        return ref - float(min(lo)), float(max(hi)) - ref
    return float(max(hi)) - ref, ref - float(min(lo))


def mss_bar(highs, lows, start, window, direction):
    """Index of the bar where structure SHIFTED after the raid, or None.

    After a buy-side raid (direction -1 = expecting down) the shift is price
    breaking BELOW the lowest low of the bars leading into the raid — the
    opposing short-term swing being taken, the confirmation the trader waits for.

    ⚠️ `window` MUST be short and MUST NOT be the same horizon the reversal is
    later measured over. The first version of this study used the full 24-bar
    horizon for both, which made "structure shifted our way" and "price moved our
    way" the same statement — a 100-pip favourable move has necessarily broken the
    prior swing — so the trip+MSS bucket scored ~100% by construction. The MSS
    must confirm quickly; the excursion is then measured from the MSS bar FORWARD,
    so the two windows never overlap.
    """
    look = 3
    a = max(0, start - look)
    if direction < 0:
        ref = float(min(lows[a:start + 1]))
        for j in range(start + 1, min(start + 1 + window, len(lows))):
            if lows[j] < ref:
                return j
        return None
    ref = float(max(highs[a:start + 1]))
    for j in range(start + 1, min(start + 1 + window, len(highs))):
        if highs[j] > ref:
            return j
    return None


def summarise(rows, pip):
    """rows = list of (fav, adv, mss). Returns dict of headline stats."""
    if not rows:
        return {"n": 0}
    n = len(rows)
    fav = [r[0] / pip for r in rows]
    adv = [r[1] / pip for r in rows]
    return {
        "n": n,
        "med_fav": sorted(fav)[n // 2],
        "med_adv": sorted(adv)[n // 2],
        # "reversed" = travelled further our way than against, i.e. the raid was
        # the turn rather than the start of a run through.
        "rev_rate": 100.0 * sum(1 for f, a in zip(fav, adv) if f > a) / n,
        "rev20": 100.0 * sum(1 for f in fav if f >= 20) / n,
        "mss_rate": 100.0 * sum(1 for r in rows if r[2]) / n,
    }


def verdict(is_stats, oos_stats, ctrl_is, ctrl_oos, min_lift=5.0):
    """GREEN only when the triple beats the single-pair control in BOTH splits by
    at least `min_lift` points, on a sample big enough to mean anything."""
    if not is_stats.get("n") or not oos_stats.get("n"):
        return "RED", "no events in one or both splits"
    if is_stats["n"] < 15 or oos_stats["n"] < 15:
        return "YELLOW", f"small sample (IS n={is_stats['n']}, OOS n={oos_stats['n']})"
    li = is_stats["rev_rate"] - ctrl_is.get("rev_rate", 0)
    lo = oos_stats["rev_rate"] - ctrl_oos.get("rev_rate", 0)
    if li >= min_lift and lo >= min_lift:
        return "GREEN", f"triple beats single by {li:+.1f}pp IS / {lo:+.1f}pp OOS"
    if li > 0 and lo > 0:
        return "YELLOW", f"positive but weak ({li:+.1f}pp IS / {lo:+.1f}pp OOS)"
    return "RED", f"no consistent lift ({li:+.1f}pp IS / {lo:+.1f}pp OOS)"


# ─────────────────────────────── data plumbing ────────────────────────────────

def _load(sym):
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
    return df.drop_duplicates("dt").sort_values("dt").set_index("dt")


def _freq(tf):
    """Project timeframe label → a pandas alias this pandas accepts.

    The codebase names timeframes "60T"/"15T" (config, bars_up_to). pandas 2.2
    removed the "T" minute alias in favour of "min", so a bare "60T" raises on a
    current pandas while still working on the older one the VM runs. Translate
    rather than renaming the convention.
    """
    return tf[:-1] + "min" if tf and tf[-1] in ("T", "t") else tf


def _resample(m1, tf):
    return m1.resample(_freq(tf)).agg(
        {"h": "max", "l": "min", "c": "last"}).dropna()


def run(tf, window, horizon, mss_win):
    import pandas as pd

    series = {}
    for sym in PAIRS + (DXY,):
        m1 = _load(sym)
        if m1 is None:
            print(f"  MISSING {sym} — put {sym}_YYYY.csv in data/histdata/")
            return 1
        series[sym] = _resample(m1, tf)

    idx = series[PAIRS[0]].index
    for sym in PAIRS[1:] + (DXY,):
        idx = idx.intersection(series[sym].index)
    for sym in series:
        series[sym] = series[sym].reindex(idx)
    print(f"  aligned {len(idx)} {tf} bars across EURUSD/GBPUSD/{DXY}")

    arr = {s: (series[s]["h"].to_numpy(), series[s]["l"].to_numpy(),
               series[s]["c"].to_numpy()) for s in series}
    years = idx.year.to_numpy()
    cover = {}
    for y in IS_YEARS + OOS_YEARS:
        cover[y] = int((years == y).sum())
    cover["IS"] = sum(cover[y] for y in IS_YEARS)
    cover["OOS"] = sum(cover[y] for y in OOS_YEARS)

    out = {}
    for label, pdir in (("short (pairs take HIGHS, DXY takes LOWS)", -1),
                        ("long  (pairs take LOWS,  DXY takes HIGHS)", +1)):
        # pairs raid the side opposite to the expected reversal; DXY the mirror
        praid = -pdir          # short → pairs sweep highs (+1)
        ev = {s: sweep_events(arr[s][0], arr[s][1], praid) for s in PAIRS}
        ev[DXY] = sweep_events(arr[DXY][0], arr[DXY][1], -praid)
        trio = align_triple(ev[PAIRS[0]], ev[PAIRS[1]], ev[DXY], window)

        buckets = {"IS": [], "OOS": [], "ctrlIS": [], "ctrlOOS": [],
                   "mssIS": [], "mssOOS": []}
        for sym in PAIRS:
            h, l, c = arr[sym]
            pip = 0.0001
            trio_set = set(trio)
            def _measure(i):
                """(fav, adv, mss_idx) measured from the RAID bar; mss_idx is the
                separate short-window confirmation, never the same window."""
                fav, adv = forward_excursion(h, l, i, horizon, pdir, float(c[i]))
                return fav, adv, mss_bar(h, l, i, mss_win, pdir)

            for i in trio:
                if i >= len(c) - 1:
                    continue
                fav, adv, mi = _measure(i)
                key = "IS" if years[i] in IS_YEARS else "OOS"
                buckets[key].append((fav, adv, mi is not None))
                # trip+MSS: entered AT the shift, so the excursion is measured
                # from the MSS bar forward — no overlap with the MSS window.
                if mi is not None and mi < len(c) - 1:
                    f2, a2 = forward_excursion(h, l, mi, horizon, pdir,
                                               float(c[mi]))
                    buckets["mss" + key].append((f2, a2, True))
            # control-1: this pair raided but the trio did NOT align
            for i, _lvl in ev[sym]:
                if i in trio_set or i >= len(c) - 1:
                    continue
                fav, adv, mi = _measure(i)
                buckets["ctrlIS" if years[i] in IS_YEARS else "ctrlOOS"].append(
                    (fav, adv, mi is not None))
        out[label] = {k: summarise(v, 0.0001) for k, v in buckets.items()}
        out[label]["_trio"] = len(trio)

    _write(out, tf, window, horizon, mss_win, cover)
    if not NO_PUSH:
        _publish(REPORT)
    return 0


def _write(out, tf, window, horizon, mss_win, cover):
    cov = " / ".join(f"{y}: {cover.get(y, 0)}" for y in IS_YEARS + OOS_YEARS)
    L = ["# Triple liquidity raid — EURUSD + GBPUSD vs DXY", "",
         f"Timeframe **{tf}**, sync window **{window}** bars, "
         f"forward horizon **{horizon}** bars, MSS confirms within "
         f"**{mss_win}** bars.", "",
         f"**Bar coverage** (bars present in ALL THREE symbols): {cov}  \n"
         f"IS **{cover.get('IS', 0)}** / OOS **{cover.get('OOS', 0)}**. "
         f"An empty OOS bucket below usually means missing UDXUSD data for those "
         f"years, not an absence of setups — check this line first.", "",
         "`rev_rate` = share of events where price travelled FURTHER in the "
         "reversal direction than against it. `rev20` = share reaching 20+ pips "
         "our way. `single` = the same pair raided its own level while the trio "
         "did NOT align — the control that decides whether triple confirmation "
         "is worth anything. `trip+MSS` additionally requires structure to shift "
         "after the raid.", "",
         "`n` counts PER-PAIR observations: one aligned trio contributes two "
         "rows (the EURUSD read and the GBPUSD read), so n = 2 x trios.", ""]
    for label, st in out.items():
        L += [f"## {label}", "", f"Aligned trios: **{st['_trio']}**", "",
              "```",
              f"{'bucket':<10} {'n':>6} {'rev%':>7} {'rev20%':>8} "
              f"{'medFav':>8} {'medAdv':>8} {'MSS%':>7}",
              "-" * 60]
        for key, name in (("IS", "triple IS"), ("OOS", "triple OOS"),
                          ("ctrlIS", "single IS"), ("ctrlOOS", "single OOS"),
                          ("mssIS", "trip+MSS IS"), ("mssOOS", "trip+MSS OOS")):
            s = st.get(key, {})
            if not s.get("n"):
                L.append(f"{name:<10} {0:>6}   —")
                continue
            L.append(f"{name:<10} {s['n']:>6} {s['rev_rate']:>6.1f}% "
                     f"{s['rev20']:>7.1f}% {s['med_fav']:>8.1f} "
                     f"{s['med_adv']:>8.1f} {s['mss_rate']:>6.1f}%")
        L.append("```")
        v, why = verdict(st.get("IS", {}), st.get("OOS", {}),
                         st.get("ctrlIS", {}), st.get("ctrlOOS", {}))
        L += ["", f"**Verdict: {v}** — {why}", ""]
    L += ["---", "", "Measurement only. A GREEN earns an IS/OOS validation of a "
          "real lever; YELLOW/RED stands as the record of why nothing shipped."]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n  wrote {REPORT}")


def _publish(path):
    """Force-add (data/ is gitignored), commit and push the report.

    Verifies rather than assuming: mm_analysis's version prints "RESULTS PUSHED"
    even when the commit was empty, which cost several exchanges of confusion when
    an unchanged report looked like a successful publish. Here an empty stage is
    reported as such.
    """
    import subprocess

    def _git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True)

    _git("add", "-f", path)
    staged = _git("diff", "--cached", "--quiet", "--", path)
    if staged.returncode == 0:
        print(f"\n  report unchanged since the last push — nothing to commit."
              f"\n  If Claude has not seen it, paste {os.path.basename(path)} "
              f"directly.")
        return
    sha = (_git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown")
    c = _git("commit", "-q", "-m", f"triple-sweep report (auto, on {sha})")
    if c.returncode != 0:
        print("\n  (commit failed — paste the report above)\n" + c.stderr[-300:])
        return
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    p = _git("push", "origin", "HEAD")
    if p.returncode == 0:
        print(f"\n  RESULTS PUSHED — Claude can read data/"
              f"{os.path.basename(path)}")
    else:
        print("\n  (auto-push failed — paste the report above)\n"
              + p.stderr[-300:])


# ──────────────────────────────── selftest ────────────────────────────────────

def selftest():
    # sweep_events: one fractal high at index 2 (1.10), taken at index 4
    h = [1.00, 1.05, 1.10, 1.04, 1.12, 1.06]
    l = [0.99, 1.01, 1.03, 1.00, 1.05, 1.02]
    ev = sweep_events(h, l, +1)
    assert ev and ev[0][0] == 4 and abs(ev[0][1] - 1.10) < 1e-9, ev
    # one structural high yields ONE event, not one per bar above it: price runs
    # up monotonically after the raid, so no NEW fractal high ever forms
    h2 = [1.00, 1.05, 1.10, 1.04, 1.12, 1.13, 1.14, 1.15]
    l2 = [0.99, 1.01, 1.03, 1.00, 1.05, 1.06, 1.07, 1.08]
    assert len(sweep_events(h2, l2, +1)) == 1, sweep_events(h2, l2, +1)
    # but a genuinely NEW structural high that is later taken IS a second event
    h3 = [1.00, 1.05, 1.10, 1.04, 1.12, 1.06, 1.15, 1.16]
    l3 = [0.99, 1.01, 1.03, 1.00, 1.05, 1.02, 1.10, 1.11]
    assert len(sweep_events(h3, l3, +1)) == 2, sweep_events(h3, l3, +1)
    # low side mirrors
    lo = [1.00, 0.95, 0.90, 0.96, 0.88, 0.94]
    hi = [1.01, 1.00, 0.99, 1.00, 0.97, 0.99]
    evl = sweep_events(hi, lo, -1)
    assert evl and evl[0][0] == 4 and abs(evl[0][1] - 0.90) < 1e-9, evl

    # DEAD-LATCH regression. Two fractal lows, the second HIGHER than the first;
    # price then dips below the SECOND but stays above the first. The live
    # structural level is the second, so this IS a sweep. The old "only re-arm at
    # a lower low" guard kept the stale first level armed and found nothing —
    # which in a trending market silenced the detector for years at a time.
    dl_l = [0.995, 0.990, 0.996, 0.998, 0.995, 0.999, 0.993]
    dl_h = [1.01] * 7
    ev_dl = sweep_events(dl_h, dl_l, -1)
    assert len(ev_dl) == 1 and ev_dl[0][0] == 6, ev_dl
    assert abs(ev_dl[0][1] - 0.995) < 1e-9, ev_dl      # the SECOND low, not 0.990
    # mirrored on the high side
    dh_h = [1.005, 1.010, 1.004, 1.002, 1.005, 1.001, 1.007]
    ev_dh = sweep_events(dh_h, [0.99] * 7, +1)
    assert len(ev_dh) == 1 and ev_dh[0][0] == 6, ev_dh
    assert abs(ev_dh[0][1] - 1.005) < 1e-9, ev_dh

    # align_triple: within window → one trio at the LAST index
    assert align_triple([(10, 0)], [(12, 0)], [(11, 0)], 4) == [12]
    # outside window → nothing
    assert align_triple([(10, 0)], [(30, 0)], [(11, 0)], 4) == []
    # members are consumed — a second trio needs its own events
    assert align_triple([(10, 0), (11, 0)], [(12, 0)], [(11, 0)], 4) == [12]

    # forward_excursion, expecting DOWN
    hh = [1.0, 1.0, 1.0, 1.02, 1.01]
    ll = [1.0, 1.0, 1.0, 0.97, 0.95]
    fav, adv = forward_excursion(hh, ll, 2, 2, -1, 1.0)
    assert abs(fav - 0.05) < 1e-9 and abs(adv - 0.02) < 1e-9, (fav, adv)

    # mss_bar: returns WHERE structure shifted, so the excursion can start there
    assert mss_bar([1.0]*6, [0.99, 0.99, 0.99, 0.98, 0.97, 0.96], 2, 3, -1) == 3
    assert mss_bar([1.0]*6, [0.99]*4 + [0.995, 0.996], 2, 3, -1) is None
    # the short window must not reach a late break
    assert mss_bar([1.0]*8, [0.99]*6 + [0.90, 0.90], 2, 2, -1) is None
    assert mss_bar([1.0]*8, [0.99]*6 + [0.90, 0.90], 2, 5, -1) == 6
    # long side mirrors
    assert mss_bar([1.0, 1.0, 1.0, 1.01, 1.02], [0.9]*5, 2, 3, +1) == 3

    # summarise + verdict gating
    s = summarise([(0.0030, 0.0010, True), (0.0005, 0.0020, False)], 0.0001)
    assert s["n"] == 2 and s["rev_rate"] == 50.0 and s["mss_rate"] == 50.0, s
    big = {"n": 40, "rev_rate": 60.0}
    ctrl = {"n": 40, "rev_rate": 50.0}
    assert verdict(big, big, ctrl, ctrl)[0] == "GREEN"
    assert verdict(big, big, big, big)[0] == "RED"
    assert verdict({"n": 5, "rev_rate": 90.0}, big, ctrl, ctrl)[0] == "YELLOW"
    print("selftest OK — sweep detection, trio alignment, excursion, MSS, verdict")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", default="60T", help="bar timeframe (default 60T = H1)")
    ap.add_argument("--window", type=int, default=4,
                    help="max bars between the three raids")
    ap.add_argument("--horizon", type=int, default=24,
                    help="forward bars to measure the reversal over")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mss-window", type=int, default=6,
                    help="bars after the raid in which the shift must confirm")
    ap.add_argument("--no-push", action="store_true",
                    help="write the report but do not commit/push it")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    global NO_PUSH
    NO_PUSH = a.no_push
    return run(a.tf, a.window, a.horizon, a.mss_window)


if __name__ == "__main__":
    sys.exit(main())
