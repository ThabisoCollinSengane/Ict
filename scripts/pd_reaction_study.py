#!/usr/bin/env python3
"""How does price ACT when it enters an intraday HTF PD array — FVG, IFVG, OB?

P69 (`fvg_reaction_study.py`) measured the reaction at W/D/H4 FVGs and read RED:
price bounces at a gap 64-70% of the time, and at a mirror band the same distance
away just as often. This extends the same measurement to the three PD arrays the
trader actually works with, on the intraday ladder H4 / H1 / M15:

  fvg   unmitigated 3-candle FVG, first touch after it formed (P69's detection)
  ifvg  an FVG traded into and then CLOSED THROUGH by a full body (open AND close
        beyond the far side) — the role flips (bullish gap closed through down ->
        supply). Inversion is judged only on bars AFTER the third candle (P81: the
        formation candles must not count as the touch). The reaction is measured
        on the FIRST return into the box after the inversion bar.
  ob    order block from `ict/order_block.detect_order_blocks` (last opposite
        candle before an up/down close that clears its range with an FVG between;
        zone = the OB candle's BODY, per Ep. 35 in that module). Known only at the
        displacement bar; the reaction is the first return after that bar.

Every row is reported against the mirror CONTROL (same width, same distance,
opposite side of price, INVERTED orientation — the P69 control bug). Only the
LIFT is evidence. All classification/excursion/retest logic is imported from
`fvg_reaction_study` unchanged, so P69's calibrated wiring is what runs here.

Lookahead discipline: zones are known only on completed bars (the zone's own
confirmation bar), the last — possibly forming — resampled bar is dropped, and
the excursion starts at the reaction's confirmation bar, never at the touch.

Measurement only. Nothing here ships to the engine.

Run:  python scripts/pd_reaction_study.py [--tfs 240T,60T,15T] [--zones fvg,ifvg,ob]
      python scripts/pd_reaction_study.py --selftest     # no data needed
      python scripts/pd_reaction_study.py --null         # random-walk calibration
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

from fvg_reaction_study import (classify_reaction, excursion, retest_holds,  # noqa: E402
                                reaction_direction, control_zone, summarise,
                                _safe_print, _publish)
from fvg_draw_study import find_fvgs, first_touch                    # noqa: E402

REPORT = os.path.join(ROOT, "data", "pd_reaction_report.md")
PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)
ZONES = ("fvg", "ifvg", "ob")
# NO_PUSH env (the workflow sets it) is honoured as well as --no-push
NO_PUSH = os.environ.get("NO_PUSH", "") not in ("", "0")

Bar = namedtuple("Bar", "Open High Low Close")


# ─────────────────────────── pure logic (unit-testable) ────────────────────────

class _BarSeq:
    """Read-only Open/High/Low/Close candle view over numpy arrays.

    `detect_order_blocks` and `ict.ifvg._inversion` take a list of candles. A
    real list of namedtuples works, but detect_order_blocks marks mitigation with
    `candles[ob.bar_index + 2:]` per block — on M15 that is ~10k full copies of a
    100k list. A slice here is a lazy iterator, so the module runs unchanged.
    """

    def __init__(self, o, h, l, c):
        self.o, self.h, self.l, self.c = o, h, l, c

    def __len__(self):
        return len(self.c)

    def __getitem__(self, k):
        if isinstance(k, slice):
            return (self[j] for j in range(*k.indices(len(self))))
        if k < 0:
            k += len(self)
        return Bar(float(self.o[k]), float(self.h[k]), float(self.l[k]),
                   float(self.c[k]))


def first_touch_fast(h, l, start, bottom, top, limit):
    """`fvg_draw_study.first_touch`, vectorised. Pinned equal in the selftest."""
    import numpy as np
    end = min(start + 1 + limit, len(h))
    if end <= start + 1:
        return None
    hit = np.flatnonzero((l[start + 1:end] <= top) & (h[start + 1:end] >= bottom))
    return int(hit[0]) + 1 if hit.size else None


def ifvg_events(bars, fvgs, scan):
    """FVG -> IFVG. Returns [(inv_bar, bottom, top, idir)].

    `fvgs` are find_fvgs rows (i = THIRD candle). The inversion is judged by
    `ict.ifvg._inversion(bars, form_idx=i, ...)`, which scans from i + 1: the
    first bar AFTER the gap formed. Passing an earlier index lets the formation
    candles supply the touch and the displacement candle's own body close read
    as the decisive close — the P81 bug that made a real IFVG read "none".

    _inversion returns the FIRST full-body close beyond either edge after the
    touch. Only a close through the FAR side is a flip (bullish gap -> supply
    idir -1); a body close back out the near side means the gap was respected
    first, and is not an IFVG.
    """
    from ict.ifvg import _inversion
    out = []
    for (i, bot, top, gdir) in fvgs:
        r = _inversion(bars, i, bot, top, scan)
        if r is None:
            continue
        j, idir, _, _ = r
        if idir == -gdir:
            out.append((j, bot, top, idir))
    return out


def ob_confirm_bar(bars, j, direction, max_back=50):
    """The displacement bar at which `detect_order_blocks` first emits the OB at j.

    OrderBlock only carries the OB candle's index, but the block is not KNOWN
    until the displacement candle closes — using j as the known bar would let
    the study "see" a block before it existed. Mirrors the module's loop: the
    first i > j (within its 50-bar look-back) whose close is in the OB's
    direction, with no other opposite candle between j and i (the module breaks
    on the first one), that clears the OB candle's far wick, with an FVG
    between j and i.
    """
    from ict.order_block import _has_fvg_between
    ob = bars[j]
    for i in range(j + 1, min(len(bars), j + max_back + 1)):
        cur = bars[i]
        if direction > 0:
            if cur.Close > cur.Open:
                if cur.Close > ob.High and _has_fvg_between(bars, j, i, +1):
                    return i
            elif cur.Close < cur.Open:
                return None            # j is no longer the last bearish candle
        else:
            if cur.Close < cur.Open:
                if cur.Close < ob.Low and _has_fvg_between(bars, j, i, -1):
                    return i
            elif cur.Close > cur.Open:
                return None
    return None


def ob_events(bars):
    """Order blocks -> [(confirm_bar, body_bottom, body_top, direction)]."""
    from ict.order_block import detect_order_blocks
    out = []
    for ob in detect_order_blocks(bars, lookback=len(bars)):
        k = ob_confirm_bar(bars, ob.bar_index, ob.direction)
        if k is None:          # cannot happen if the mirror is right (selftest)
            continue
        out.append((k, ob.body_bottom, ob.body_top, ob.direction))
    return out


def lift_se(p1, n1, p2, n2):
    """Standard error (pp) of the difference of two proportions given in %."""
    if not n1 or not n2 or p1 is None or p2 is None:
        return None
    a, b = p1 / 100.0, p2 / 100.0
    return 100.0 * math.sqrt(a * (1 - a) / n1 + b * (1 - b) / n2)


def cell_verdict(z_is, z_oos, c_is, c_oos, min_lift=5.0):
    """GREEN only if respect lifts >= min_lift over control in BOTH splits (same
    sign by construction) AND the respect branch pays (medFav > medAdv) in both.
    Anything else is RED."""
    for s in (z_is, z_oos, c_is, c_oos):
        if not s.get("n"):
            return "RED", "empty zone or control bucket in a split"
    la = z_is["respect"] - c_is["respect"]
    lb = z_oos["respect"] - c_oos["respect"]
    if la < min_lift or lb < min_lift:
        return "RED", f"lift {la:+.1f}/{lb:+.1f}pp (< {min_lift:.0f}pp in a split)"
    pays = all(s["res_fav"] is not None and s["res_adv"] is not None
               and s["res_fav"] > s["res_adv"] for s in (z_is, z_oos))
    if not pays:
        return "RED", f"lift {la:+.1f}/{lb:+.1f}pp but respect does not pay"
    return "GREEN", f"lift {la:+.1f}/{lb:+.1f}pp and respect pays both splits"


# ─────────────────────────────── data plumbing ────────────────────────────────

def _minutes(tf):
    from triple_sweep_study import _freq
    import pandas as pd
    return pd.Timedelta(_freq(tf)).total_seconds() / 60.0


def _split(year):
    if year in IS_YEARS:
        return "IS"
    if year in OOS_YEARS:
        return "OOS"
    return None


def null_loader(seed=7):
    """Random-walk M1 for the --null calibration (weekday minutes, 2022-2025).
    A random walk has no PD arrays, so every lift must sit near zero."""
    import numpy as np
    import pandas as pd
    idx = pd.date_range("2022-01-03", "2025-12-31 23:59", freq="1min")
    idx = idx[idx.dayofweek < 5]
    cache = {}

    def _load(pair):
        if pair in cache:
            return cache[pair]
        # (seed, pair) -> its own stream; seed+index would make consecutive
        # seeds share pair series and fake a consistent bias across "seeds"
        rng = np.random.default_rng([seed, PAIRS.index(pair) if pair in PAIRS
                                     else 99])
        n = len(idx)
        step = rng.normal(0.0, 0.5e-4, n)               # ~0.5 pip / minute
        c = 1.10 + np.cumsum(step)
        o = np.concatenate(([1.10], c[:-1]))
        wick = np.abs(rng.normal(0.0, 0.25e-4, (2, n)))
        h = np.maximum(o, c) + wick[0]
        l = np.minimum(o, c) - wick[1]
        df = pd.DataFrame({"o": o, "h": h, "l": l, "c": c,
                           "v": np.zeros(n)}, index=idx)
        df.index.name = "dt"
        cache[pair] = df
        return df
    return _load


def run(tfs, zones, react_win, horizon, retest_h, loader=None, report=REPORT,
        label="real HistData M1", push=True):
    from triple_sweep_study import _load, _resample
    loader = loader or _load

    out, cover = {}, {}
    for tf in tfs:
        lim = max(3, int(30 * 1440.0 / _minutes(tf)))       # 30 days, any TF
        B = {(z, t, k): [] for z in zones for t in ("zone", "ctl")
             for k in ("IS", "OOS")}
        H = {(z, t, k): [] for z in zones for t in ("zone", "ctl")
             for k in ("IS", "OOS")}
        cov = {}
        for pair in PAIRS:
            m1 = loader(pair)
            if m1 is None:
                print(f"  MISSING {pair} — put {pair}_YYYY.csv in data/histdata/")
                continue
            bars = _resample(m1, tf)
            bars = bars.iloc[:-1]          # last bin may be forming: never use it
            o = bars["o"].to_numpy(); h = bars["h"].to_numpy()
            l = bars["l"].to_numpy(); c = bars["c"].to_numpy()
            years = bars.index.year.to_numpy()
            for k in ("IS", "OOS"):
                ys = IS_YEARS if k == "IS" else OOS_YEARS
                cov[(pair, k)] = int(sum((years == y).sum() for y in ys))
            seq = _BarSeq(o, h, l, c)
            fvgs = find_fvgs(h, l)
            ev = {}
            if "fvg" in zones:
                ev["fvg"] = [(i, b, t, d) for (i, b, t, d) in fvgs]
            if "ifvg" in zones:
                ev["ifvg"] = ifvg_events(seq, fvgs, lim)
            if "ob" in zones:
                ev["ob"] = ob_events(seq)

            for z, events in ev.items():
                for (kb, bot, top, zdir) in events:
                    if kb >= len(c) - 2:
                        continue
                    key = _split(int(years[kb]))
                    if key is None:
                        continue
                    for tag, (bb, tt, gd) in (
                            ("zone", (bot, top, zdir)),
                            ("ctl", control_zone(c[kb], bot, top, zdir))):
                        d = first_touch_fast(h, l, kb, bb, tt, lim)
                        if d is None:
                            continue
                        tb = kb + d
                        v, cb = classify_reaction(o, h, l, c, tb, bb, tt, gd,
                                                  react_win)
                        if v == "unresolved":
                            B[(z, tag, key)].append((v, None, None))
                            continue
                        ex = excursion(h, l, cb, c[cb],
                                       reaction_direction(v, gd), horizon)
                        B[(z, tag, key)].append((v, None, None) if ex is None
                                                else (v, ex[0], ex[1]))
                        if v == "break":
                            hd = retest_holds(o, h, l, c, cb, bb, tt, gd,
                                              retest_h, react_win)
                            if hd is not None:
                                H[(z, tag, key)].append(hd)
        out[tf] = {"S": {k: summarise(v) for k, v in B.items()},
                   "H": {k: (len(v), 100.0 * sum(v) / len(v) if v else None)
                         for k, v in H.items()}}
        cover[tf] = cov
    text = _render(out, cover, tfs, zones, react_win, horizon, retest_h, label)
    os.makedirs(os.path.dirname(report), exist_ok=True)
    with open(report, "w", encoding="utf-8") as f:
        f.write(text)
    _safe_print(text)
    if push and not NO_PUSH:
        _publish(report)
    else:
        print(f"\n  (no push) report written to {report}")
    return out


def _f(x, fmt="{:.1f}"):
    return "—" if x is None else fmt.format(x)


def _render(out, cover, tfs, zones, react_win, horizon, retest_h, label):
    L = ["# How does price act at intraday HTF PD arrays (FVG / IFVG / OB)?", "",
         f"Data: **{label}**. Pairs {', '.join(PAIRS)}. IS = "
         f"{IS_YEARS[0]}-{str(IS_YEARS[-1])[-2:]}, OOS = "
         f"{OOS_YEARS[0]}-{str(OOS_YEARS[-1])[-2:]}.", "",
         f"`respect` = full body closes back out the side price came from; "
         f"`break` = full body closes through the far side; whichever first "
         f"within **{react_win}** bars of the touch. Excursion over **{horizon}** "
         f"bars FROM the confirmation bar. `ctl` = mirror band (same width, same "
         f"distance, opposite side of price, inverted orientation). "
         f"**Read the lift, never the rate.** SE = standard error of the lift; "
         f"verdict GREEN needs >= 5pp lift in BOTH splits AND medFav > medAdv on "
         f"respect in both; otherwise RED.", "",
         "## Coverage (completed bars per split; last bin dropped)", "", "```"]
    for tf in tfs:
        cv = cover.get(tf, {})
        L.append(f"{tf:>6}  " + "  ".join(
            f"{p} IS {cv.get((p, 'IS'), 0):>7} OOS {cv.get((p, 'OOS'), 0):>7}"
            for p in PAIRS))
    L += ["```", ""]
    summary = []
    for tf in tfs:
        S, Hd = out[tf]["S"], out[tf]["H"]
        L += [f"## {tf}", "", "```",
              f"{'zone':<5} {'row':<9} {'n':>6} {'resp%':>6} {'brk%':>6} "
              f"{'unres%':>6} {'resFav':>7} {'resAdv':>7} {'brkFav':>7} "
              f"{'brkAdv':>7}", "-" * 78]
        for z in zones:
            for t in ("zone", "ctl"):
                for k in ("IS", "OOS"):
                    s = S[(z, t, k)]
                    nm = f"{t} {k}"
                    if not s.get("n"):
                        L.append(f"{z:<5} {nm:<9} {0:>6}   —")
                        continue
                    L.append(f"{z:<5} {nm:<9} {s['n']:>6} {s['respect']:>6.1f} "
                             f"{s['break']:>6.1f} {s['unres']:>6.1f} "
                             f"{_f(s['res_fav']):>7} {_f(s['res_adv']):>7} "
                             f"{_f(s['brk_fav']):>7} {_f(s['brk_adv']):>7}")
            L.append("")
        L += ["```", "", "Lifts over control (pp, ± SE):", "", "```",
              f"{'zone':<5} {'respect IS':>16} {'respect OOS':>16} "
              f"{'break IS':>16} {'break OOS':>16} {'retest-hold IS':>22} "
              f"{'retest-hold OOS':>22}  verdict"]
        for z in zones:
            cells = []
            for metric in ("respect", "break"):
                for k in ("IS", "OOS"):
                    a, b = S[(z, "zone", k)], S[(z, "ctl", k)]
                    if a.get("n") and b.get("n"):
                        lf = a[metric] - b[metric]
                        se = lift_se(a[metric], a["n"], b[metric], b["n"])
                        cells.append(f"{lf:+6.1f} ±{se:4.1f}")
                    else:
                        cells.append("—")
            for k in ("IS", "OOS"):
                gn, gp = Hd[(z, "zone", k)]
                cn, cp = Hd[(z, "ctl", k)]
                if gp is None or cp is None:
                    cells.append(f"n {gn}/{cn} —")
                else:
                    se = lift_se(gp, gn, cp, cn)
                    cells.append(f"{gp - cp:+6.1f} ±{se:4.1f} n{gn}/{cn}")
            v, why = cell_verdict(S[(z, "zone", "IS")], S[(z, "zone", "OOS")],
                                  S[(z, "ctl", "IS")], S[(z, "ctl", "OOS")])
            summary.append((tf, z, v, why))
            L.append(f"{z:<5} {cells[0]:>16} {cells[1]:>16} {cells[2]:>16} "
                     f"{cells[3]:>16} {cells[4]:>22} {cells[5]:>22}  {v}")
        L += ["```", "",
              f"*retest-hold = after a BREAK, does the broken zone reject price "
              f"on its first return within {retest_h} bars (breakaway -> "
              f"IFVG claim)? n = zone/control retests.*", ""]
    L += ["## Verdicts", "", "| TF | zone | verdict | why |", "|---|---|---|---|"]
    L += [f"| {tf} | {z} | **{v}** | {why} |" for tf, z, v, why in summary]
    L += ["", "Measurement only; nothing ships."]
    return "\n".join(L) + "\n"


# ──────────────────────────────── selftest ────────────────────────────────────

def selftest():
    import numpy as np
    from ict.ifvg import _inversion

    # ── IFVG: the P81 slice. Bullish gap formed by bars 0-2, box [1.00, 1.02].
    # bar 0 high = 1.00 (box bottom) and bar 2 low = 1.02 (box top) — both
    # formation candles TOUCH the box edge, and bar 2's body is fully ABOVE it.
    # bar 3 trades back in, bar 4 closes a full body BELOW -> bearish IFVG at 4.
    O = [0.995, 1.00, 1.03, 1.03, 0.99, 0.985, 0.99, 1.01, 0.98]
    H = [1.00, 1.04, 1.05, 1.035, 1.00, 0.99, 1.005, 1.012, 0.99]
    L_ = [0.98, 0.995, 1.02, 1.01, 0.98, 0.97, 0.98, 1.001, 0.975]
    C = [1.000, 1.03, 1.04, 1.015, 0.985, 0.98, 1.004, 0.99, 0.976]
    h, l = np.array(H), np.array(L_)
    o, c = np.array(O), np.array(C)
    seq = _BarSeq(o, h, l, c)
    fv = [g for g in find_fvgs(h, l) if g[0] == 2]
    assert fv == [(2, 1.00, 1.02, +1)], fv
    ev = ifvg_events(seq, fv, 20)
    assert ev == [(4, 1.00, 1.02, -1)], ev                 # supply IFVG at bar 4
    # the P81 bug: let the formation candles in (scan from bar 0) and the
    # displacement candle's body above the box is read as the decisive close
    bug = _inversion(seq, -1, 1.00, 1.02, 20)
    assert bug is not None and bug[0] == 2 and bug[1] == +1, bug
    # a gap that is touched and RESPECTED first is not an IFVG
    O2 = [0.99, 1.00, 1.03, 1.03, 1.03, 0.99]
    H2 = [1.00, 1.04, 1.05, 1.035, 1.05, 1.00]
    L2 = [0.98, 0.995, 1.02, 1.01, 1.025, 0.98]
    C2 = [0.995, 1.03, 1.04, 1.025, 1.04, 0.985]           # bar 3 body > 1.02
    s2 = _BarSeq(*(np.array(x) for x in (O2, H2, L2, C2)))
    assert ifvg_events(s2, [(2, 1.00, 1.02, +1)], 20) == []
    # reaction is measured on the first return AFTER the inversion bar: bar 6
    d = first_touch_fast(h, l, 4, 1.00, 1.02, 20)
    assert d == 2, d
    # supply IFVG (idir -1) approached from below, near side = bottom 1.00:
    # bar 7 body 0.99-1.01 straddles -> no verdict; bar 8 body < 1.00 -> respect
    v = classify_reaction(o, h, l, c, 6, 1.00, 1.02, -1, 3)
    assert v == ("respect", 8), v
    # its control sits BELOW price with bullish orientation
    assert control_zone(c[4], 1.00, 1.02, -1)[2] == +1

    # ── first_touch_fast == first_touch on random data
    rng = np.random.default_rng(1)
    rh = 1 + np.cumsum(rng.normal(0, 1e-3, 500)); rl = rh - 2e-3
    for st in range(0, 480, 7):
        for (bb, tt) in ((rh[st] + 1e-3, rh[st] + 3e-3), (rl[st] - 4e-3, rl[st] - 1e-3)):
            assert first_touch(rh, rl, st, bb, tt, 40) == \
                first_touch_fast(rh, rl, st, bb, tt, 40)

    # ── OB: bearish candle 1 (body 1.010-1.000), then up-closes; bar 4 closes
    # above bar 1's high with an FVG between (bar 4 low > bar 2 high).
    Ob = [1.000, 1.010, 1.001, 1.006, 1.016, 1.022, 1.020, 1.012]
    Hb = [1.005, 1.012, 1.008, 1.010, 1.024, 1.026, 1.022, 1.014]
    Lb = [0.998, 0.997, 0.999, 1.004, 1.012, 1.018, 1.009, 1.008]
    Cb = [1.004, 1.000, 1.006, 1.009, 1.022, 1.024, 1.012, 1.013]
    sb = _BarSeq(*(np.array(x) for x in (Ob, Hb, Lb, Cb)))
    from ict.order_block import detect_order_blocks
    obs = [x for x in detect_order_blocks(sb, lookback=len(sb)) if x.bar_index == 1]
    assert obs and obs[0].direction == +1, obs
    assert (obs[0].body_bottom, obs[0].body_top) == (1.000, 1.010), obs[0]
    # known at the displacement bar (4), NOT at the OB candle (1) — bar 3 closes
    # 1.009 < high 1.012 so it does not yet confirm the block
    assert ob_confirm_bar(sb, 1, +1) == 4, ob_confirm_bar(sb, 1, +1)
    ev = [e for e in ob_events(sb) if e[1] == 1.000]
    assert ev == [(4, 1.000, 1.010, +1)], ev
    # first return into the body after bar 4: bar 6 (low 1.009)
    assert first_touch_fast(np.array(Hb), np.array(Lb), 4, 1.000, 1.010, 10) == 2
    # every block the module emits must have a confirm bar (mirror is faithful)
    rr = np.random.default_rng(3)
    cc = 1 + np.cumsum(rr.normal(0, 1e-3, 3000))
    oo = np.concatenate(([1.0], cc[:-1]))
    hh = np.maximum(oo, cc) + np.abs(rr.normal(0, 5e-4, 3000))
    ll = np.minimum(oo, cc) - np.abs(rr.normal(0, 5e-4, 3000))
    sr = _BarSeq(oo, hh, ll, cc)
    allobs = detect_order_blocks(sr, lookback=len(sr))
    assert len(allobs) > 20
    for x in allobs:
        k = ob_confirm_bar(sr, x.bar_index, x.direction)
        assert k is not None and k > x.bar_index, x
        # at the confirm bar price is beyond the body, on the right side
        assert (cc[k] > x.body_top) if x.direction > 0 else (cc[k] < x.body_bottom)
    assert len(ob_events(sr)) == len(allobs)

    # ── lift SE and verdict
    assert abs(lift_se(50.0, 100, 50.0, 100) - 100 * math.sqrt(0.005)) < 1e-9
    G = {"n": 100, "respect": 60.0, "res_fav": 20.0, "res_adv": 8.0}
    Cc = {"n": 100, "respect": 50.0}
    assert cell_verdict(G, G, Cc, Cc)[0] == "GREEN"
    assert cell_verdict(G, G, Cc, {"n": 100, "respect": 58.0})[0] == "RED"
    NP = {"n": 100, "respect": 60.0, "res_fav": 8.0, "res_adv": 20.0}
    assert cell_verdict(NP, NP, Cc, Cc)[0] == "RED"
    assert cell_verdict(G, {"n": 0}, Cc, Cc)[0] == "RED"
    print("selftest OK — IFVG inversion slice (P81 fixture: correct=supply@4, "
          "bug=demand@2), respected gap not an IFVG, IFVG first-return + "
          "orientation, OB body zone + confirm bar (mirror of module on 3000 "
          "bars), first_touch parity, lift SE, verdict")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tfs", default="240T,60T,15T")
    ap.add_argument("--zones", default="fvg,ifvg,ob")
    ap.add_argument("--react-window", type=int, default=3)
    ap.add_argument("--horizon", type=int, default=12)
    ap.add_argument("--retest-horizon", type=int, default=30)
    ap.add_argument("--out", default=None, help="report path")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--null", action="store_true",
                    help="random-walk M1 through the real run() path; must read RED")
    ap.add_argument("--seed", type=int, default=7, help="--null RNG seed")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    global NO_PUSH
    NO_PUSH = NO_PUSH or a.no_push or a.null
    zones = tuple(z for z in a.zones.split(",") if z)
    bad = [z for z in zones if z not in ZONES]
    if bad:
        ap.error(f"unknown zone(s) {bad}; choose from {ZONES}")
    if a.null:
        run(tuple(a.tfs.split(",")), zones, a.react_window, a.horizon,
            a.retest_horizon, loader=null_loader(a.seed),
            report=a.out or os.path.join(ROOT, "data", "pd_reaction_null.md"),
            label="NULL random walk (calibration — must read RED)", push=False)
        return 0
    run(tuple(a.tfs.split(",")), zones, a.react_window, a.horizon,
        a.retest_horizon, report=a.out or REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
