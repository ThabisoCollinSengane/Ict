#!/usr/bin/env python3
"""Which gap fills FIRST — does market structure pick it, or is distance all there is?

WHY THIS EXISTS — the trader's correction, and it is right
-----------------------------------------------------------
P76 asked whether the algo's trades do better when aimed at an unfilled daily
gap. 82% of entries had a gap ABOVE and BELOW, and I broke that tie by raw
DISTANCE — nearest gap wins — then reported the toward/away label as
"ambiguous" and closed the line.

That was never the trader's model. Their rule:

    "the algo should look at the closest gap not the furthest. The closest
     depending on past price action where we saw a shift in market structure
     and the overall direction — look at the intermarket analysis. We only
     consider the furthest after the closest is reached and we see a shift in
     market structure."

So "closest" does NOT mean geometrically nearest. It means the one market
STRUCTURE says is next, confirmed by the dollar. Two gaps is not ambiguity —
it is a question structure answers. I tested a strawman and called the model
unresolvable.

⚠️ **WHICH TIMEFRAME — the second correction, 2026-09-14.** The first build read
structure on DAILY candles. The trader:

    "The shift in market structure matters more on the H1 for the daily
     sentiment. The previous days price action always tells the story."

So the daily SENTIMENT is read from H1 structure as of the previous day's close,
not from the daily candle sequence. This is consistent with what the brief
already records twice — P64 uses H1 first as "the trader's timeframe for DAILY
dollar structure", and P66's bias is the PREVIOUS completed day. The study now
carries BOTH reads as separate rules (`struct_h1`, `struct_d`) so the claim is
measured rather than assumed, and the dollar overlay is read on H1 too.

WHY THE SAMPLE-SIZE OBJECTION DIES HERE
---------------------------------------
P76b's closing argument was arithmetic: a 5pp effect needs ~1,580 trades and we
have 736. Two things kill that objection:

1. A BETTER label means a BIGGER effect, and required n falls with the SQUARE
   of the effect. 5pp needs ~790 per bucket; 15pp needs ~88. If structure
   really picks the gap, the effect should be large enough to see.
2. **This question does not need our trades at all.** "Which of two gaps fills
   first" is a pure PRICE question. Every day price straddles two unfilled gaps
   is an observation — thousands, not 736.

THE DESIGN, AND THE ONE CELL THAT DECIDES IT
--------------------------------------------
At every bar where an unfilled daily gap sits above AND below price:
  - `struct_h1` predicts the side the Ep-12 intermediate trend points to, read on
    H1 bars as of the PREVIOUS day's close (higher intermediate lows -> the gap
    ABOVE; lower intermediate highs -> BELOW).  <- the trader's timeframe
  - `struct_d`  the same read on DAILY candles — kept to measure whether H1
    really is the right rung, rather than taking it on faith
  - `dollar_h1` UDXUSD H1 structure, INVERSE (dollar up -> pairs down -> lower gap)
  - `distance`  predicts the nearer gap  — the naive rule, and the one P76 used
  - outcome     is which gap actually fills first (full body close through the
                far side, ICT Ep 9), within `--horizon` days

**The decisive cell is where the two DISAGREE.** Structure that merely tracks
"price moved up so the upper gap is nearer" would add nothing over distance —
and it would score well on the agree cases for free. Only the disagree subset
separates real structural information from that confound.

⚠️ **50% is NOT the bar, and assuming it was would have misread the first null.**
The nearer level is reached first for pure geometric reasons — on a random walk
distance alone scores ~62%. So on the disagree subset, where structure by
construction names the FARTHER gap, a no-information structure reads ~38%, not
50%. Measured against 50% that looks like a strong negative finding; it is just
geometry.

The self-calibrating test avoids needing any external baseline: compare
**distance's own accuracy on the AGREE cases against its accuracy on the
DISAGREE cases.** The two subsets are disjoint, so it is a clean two-proportion
comparison. If structure carries information it is flagging precisely the cases
where distance fails, so distance must score WORSE when structure contradicts
it. On the random-walk null that drop is 10.2pp (1.1 SE) with the two halves
contradicting each other (-2.2 / +29.6) — i.e. RED, as it must be.

INDEPENDENCE — why the headline uses EPISODES, not days
-------------------------------------------------------
Consecutive days usually straddle the SAME pair of gaps, so counting every day
inflates the sample with near-duplicates. The verdict is read off `unique`: the
first day each distinct (above-gap, below-gap) combination straddles price. The
per-day numbers are printed alongside, never used for the verdict.

⚠️ COMPLETED daily candles only, everywhere. Structure at bar i is classified on
candles[:i+1]; the outcome is measured strictly AFTER i. The two windows never
overlap — the failure that voided P65c, P66, P68b, P69 and P71 §3.

⚠️ Read against BOTH controls: `distance` (the naive rule) and the random-walk
null, where the agree-vs-disagree drop must vanish. A study that cannot produce
"no edge" on data with no edge is not measuring anything.

Run (no trade dump needed — this is pure price):
    python scripts/gap_race_study.py
    python scripts/gap_race_study.py --null      # random-walk sanity check
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

DATA = os.path.join(ROOT, "data", "histdata")
OUT = os.path.join(ROOT, "data", "gap_race_report.md")
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)
PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
DOLLAR = "UDXUSD"

Bar = namedtuple("Bar", "Open High Low Close")

# ⚠️ "60min", NOT "60T". pandas 3.x REMOVED the "T" minute alias — a bare "60T"
# raises ValueError("Invalid frequency: T ... Did you mean min?"). The project
# already knew this: `triple_sweep_study._freq` documents it, and backtest.py /
# run_backtest_histdata.py both carry ("60T", "60min") mappings. I wrote "60T"
# anyway. When the repo already has a convention, use it (the P73 `_find_dump`
# lesson, second occurrence).
H1_RULE = "60min"
DAY_RULE = "1D"


# ─────────────────────────── pure logic (unit-testable) ────────────────────────

def daily_fvgs(highs, lows, min_size):
    """Every 3-bar gap. Returns (knowable_at, gdir, bottom, top).

    `knowable_at` is the index of the THIRD bar — the gap does not exist until
    that bar has closed, so it may only be used from the NEXT bar onward.
    """
    out = []
    for i in range(2, len(highs)):
        h0, l0 = highs[i - 2], lows[i - 2]
        h2, l2 = highs[i], lows[i]
        if l2 > h0 and (l2 - h0) >= min_size:
            out.append((i, +1, h0, l2))
        elif h2 < l0 and (l0 - h2) >= min_size:
            out.append((i, -1, h2, l0))
    return out


def fill_index(closes, start, bottom, top, side):
    """First bar CLOSING a full body through the FAR side (ICT Ep 9), or None.

    `side` is where the gap sits RELATIVE TO PRICE, not how it formed — a gap
    ABOVE price is filled by closing above its top, one BELOW by closing below
    its bottom. Formation direction is irrelevant to the race (the P75/P73
    correction: what matters is that it is unfilled and which way price must
    travel to reach it).
    """
    for j in range(start + 1, len(closes)):
        if side == "above" and closes[j] >= top:
            return j
        if side == "below" and closes[j] <= bottom:
            return j
    return None


def structure_side(struct_dir):
    """Which gap the Ep-12 intermediate trend points at.

    Higher intermediate lows (+1) -> price is working UP -> the gap ABOVE is the
    draw. Lower intermediate highs (-1) -> the gap BELOW. 0 -> no read, and the
    observation is DROPPED rather than guessed (a forced coin flip on a flat
    read would dilute the very effect being measured).
    """
    if struct_dir > 0:
        return "above"
    if struct_dir < 0:
        return "below"
    return None


def distance_side(dist_above, dist_below):
    """The naive rule, and the one P76 used: the nearer gap wins."""
    if dist_above < dist_below:
        return "above"
    if dist_below < dist_above:
        return "below"
    return None                      # exact tie — no prediction, dropped


def dollar_side(dxy_dir):
    """Intermarket overlay. Every pair is X/USD, so it is INVERSE to the dollar:
    a dollar working UP pushes the pairs DOWN, toward the gap BELOW."""
    if dxy_dir > 0:
        return "below"
    if dxy_dir < 0:
        return "above"
    return None


def _rate(hits, n):
    return (100.0 * hits / n) if n else float("nan")


def _se_pp(hits, n):
    """Standard error of a proportion, in percentage points."""
    if not n:
        return float("nan")
    p = hits / n
    return 100.0 * (p * (1 - p) / n) ** 0.5


def _selftest():
    # daily_fvgs — both directions plus the size floor
    hi = [10, 10, 10]; lo = [9, 9, 15]          # bar2 low 15 > bar0 high 10
    g = daily_fvgs(hi, lo, 1.0)
    assert g == [(2, +1, 10, 15)], g
    assert daily_fvgs(hi, lo, 99.0) == [], "size floor must reject"
    hi2 = [20, 20, 10]; lo2 = [15, 15, 9]
    assert daily_fvgs(hi2, lo2, 1.0) == [(2, -1, 10, 15)], daily_fvgs(hi2, lo2, 1.0)

    # fill_index — FAR side relative to price, and a close INSIDE must not fill
    assert fill_index([0, 0, 0, 14, 16], 2, 10, 15, "above") == 4
    assert fill_index([0, 0, 0, 14, 14.5], 2, 10, 15, "above") is None, "inside is not a fill"
    assert fill_index([0, 0, 0, 12, 9], 2, 10, 15, "below") == 4
    assert fill_index([0, 0, 0, 12, 11], 2, 10, 15, "below") is None

    # the three predictors
    assert structure_side(+1) == "above" and structure_side(-1) == "below"
    assert structure_side(0) is None, "a flat read predicts nothing"
    assert distance_side(10.0, 50.0) == "above"
    assert distance_side(50.0, 10.0) == "below"
    assert distance_side(20.0, 20.0) is None, "exact tie predicts nothing"
    # dollar is INVERSE — this mapping is the one that is easy to get backwards
    assert dollar_side(+1) == "below", "dollar up -> pairs down -> lower gap"
    assert dollar_side(-1) == "above"
    assert dollar_side(0) is None

    # The resample aliases must parse on the pandas actually installed. This is
    # a plumbing assertion in a pure-logic selftest on purpose: "60T" passed
    # every logic test here and still crashed the real run on pandas 3.x.
    import pandas as _pd
    _f = _pd.DataFrame({"o": [1.0], "h": [1.0], "l": [1.0], "c": [1.0]},
                       index=_pd.date_range("2022-01-03", periods=1, tz="UTC"))
    for _rule in (H1_RULE, DAY_RULE):
        _f.resample(_rule).agg({"o": "first", "h": "max", "l": "min", "c": "last"})

    assert abs(_rate(1, 2) - 50.0) < 1e-9
    assert _se_pp(50, 100) > 4.9 and _se_pp(50, 100) < 5.1
    print("selftest OK")


# ─────────────────────────────── data plumbing ────────────────────────────────

def _load_daily(sym, pandas):
    """HistData M1 -> completed UTC daily bars, matching the engine (EST +5h)."""
    pd = pandas
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
    d = df.resample(DAY_RULE).agg({"o": "first", "h": "max",
                               "l": "min", "c": "last"}).dropna()
    return d


def _load_h1(sym, pandas):
    """HistData M1 -> completed UTC H1 bars, same EST +5h convention."""
    pd = pandas
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
    return df.resample(H1_RULE).agg({"o": "first", "h": "max",
                                   "l": "min", "c": "last"}).dropna()


def _h1_dir_per_day(h1, daily_index, window, mstruct, pandas):
    """Ep-12 intermediate direction from H1 bars, one read per DAILY bar.

    The read for daily bar i uses H1 bars up to the CLOSE of day i — i.e. the
    previous day's price action, which is what the trader says tells the story.
    The outcome is measured from day i+1 onward, so the two windows never touch.
    """
    pd = pandas
    bars = [Bar(o, h, l, c) for o, h, l, c
            in zip(h1["o"], h1["h"], h1["l"], h1["c"])]
    hidx = h1.index
    out = []
    for ts in daily_index:
        end = hidx.searchsorted(ts + pd.Timedelta(days=1), side="left")
        seg = bars[max(0, end - window):end]
        out.append(mstruct.structure_direction(mstruct.classify(seg))
                   if len(seg) >= 12 else 0)
    return out


def _random_walk_h1(pandas, n_days=1040, seed=7):
    """The null: no structure, no draws, nothing to find. Deterministic.

    Built at H1 so the null exercises the SAME code path as a real run —
    `_h1_dir_per_day` and the daily aggregation. The first version generated
    daily bars directly, which meant `--null` never touched the H1 loader at
    all, and a crash there ("60T" on pandas 3.x) sailed straight past it into
    the real run. A null that skips a code path cannot vouch for it.
    """
    import random
    pd = pandas
    rnd = random.Random(seed)
    px, rows, idx = 1.1000, [], []
    ts = pd.Timestamp("2022-01-03 00:00", tz="UTC")
    for _ in range(n_days * 24):
        o = px
        hi = lo = o
        for _ in range(12):
            px += rnd.gauss(0, 0.00038)
            hi, lo = max(hi, px), min(lo, px)
        rows.append((o, hi, lo, px))
        idx.append(ts)
        ts += pd.Timedelta(hours=1)
    return pd.DataFrame(rows, columns=["o", "h", "l", "c"],
                        index=pd.DatetimeIndex(idx))


def _daily_from_h1(h1):
    return h1.resample(DAY_RULE).agg({"o": "first", "h": "max",
                                      "l": "min", "c": "last"}).dropna()


def _pip(pair):
    return 0.01 if pair.endswith("JPY") else 0.0001


def _split_of(ts):
    return "IS" if ts.year in IS_YEARS else "OOS"


# ───────────────────────────────── the study ──────────────────────────────────

def _struct_dir_series(d, window, mstruct):
    """structure_direction at EVERY bar, using completed bars only.

    candles[:i+1] are all closed by definition, and the outcome is read strictly
    after i, so the prediction window and the outcome window never overlap.
    """
    bars = [Bar(o, h, l, c) for o, h, l, c
            in zip(d["o"], d["h"], d["l"], d["c"])]
    out = []
    for i in range(len(bars)):
        lo = max(0, i + 1 - window)
        seg = bars[lo:i + 1]
        out.append(mstruct.structure_direction(mstruct.classify(seg))
                   if len(seg) >= 8 else 0)
    return out


def _observations(d, pip, min_gap_pips, horizon, dirs):
    """Every bar where an unfilled gap sits ABOVE and BELOW price.

    `dirs` maps rule name -> per-daily-bar direction series (+1/-1/0). Each is
    converted to a side by its own mapping: the dollar is INVERSE, everything
    else reads straight.
    """
    hi, lo, cl = d["h"].tolist(), d["l"].tolist(), d["c"].tolist()
    idx = list(d.index)

    # Each gap's SIDE is fixed for its whole life: a gap above price can only
    # stop being above by price closing through its top -- which is its fill.
    # So the side and the fill bar are properties of the gap, computed ONCE.
    gaps = daily_fvgs(hi, lo, min_gap_pips * pip)
    live = []                       # (born, side, bottom, top, fill_idx)
    for (k, _gdir, bot, top) in gaps:
        born = k + 1                # usable only once the third candle closed
        if born >= len(cl):
            continue
        side = "above" if bot > cl[born - 1] else ("below" if top < cl[born - 1] else None)
        if side is None:            # price already inside it -- no race
            continue
        live.append((born, side, bot, top, fill_index(cl, k, bot, top, side)))

    obs, seen = [], set()
    for i in range(len(cl) - 1):
        px = cl[i]
        live_ab = [(b, t) for (born, sd, b, t, f) in live
                   if born <= i and sd == "above" and (f is None or f > i)]
        live_be = [(b, t) for (born, sd, b, t, f) in live
                   if born <= i and sd == "below" and (f is None or f > i)]
        if not live_ab or not live_be:
            continue
        ab = min(live_ab, key=lambda g: g[0] - px)          # nearest above
        be = max(live_be, key=lambda g: g[1])               # nearest below
        d_ab, d_be = (ab[0] - px) / pip, (px - be[1]) / pip

        f_ab = fill_index(cl, i, ab[0], ab[1], "above")
        f_be = fill_index(cl, i, be[0], be[1], "below")
        if f_ab is not None and f_ab - i > horizon:
            f_ab = None
        if f_be is not None and f_be - i > horizon:
            f_be = None
        if f_ab is None and f_be is None:
            actual = None                                    # unresolved
        elif f_be is None:
            actual = "above"
        elif f_ab is None:
            actual = "below"
        elif f_ab == f_be:
            actual = None                                    # same bar — never assigned
        else:
            actual = "above" if f_ab < f_be else "below"

        key = (round(ab[0], 6), round(ab[1], 6), round(be[0], 6), round(be[1], 6))
        row = {"t": idx[i], "split": _split_of(idx[i]),
               "first": key not in seen,
               "dist": distance_side(d_ab, d_be),
               "actual": actual}
        for name, series in dirs.items():
            row[name] = (dollar_side(series[i]) if name.startswith("dollar")
                         else structure_side(series[i]))
        obs.append(row)
        seen.add(key)
    return obs


def _acc(rows, pred_key):
    """(hits, n) for a predictor over resolved observations."""
    hits = n = 0
    for r in rows:
        # .get, not [] — a rule is absent when its series could not be built
        # for that pair (no H1 file, no UDXUSD). Indexing raised KeyError on the
        # null run, where only struct_d exists.
        p, a = r.get(pred_key), r["actual"]
        if p is None or a is None:
            continue
        n += 1
        hits += (p == a)
    return hits, n


def run(min_gap_pips=3.0, horizon=60, window=120, h1_window=120,
        primary="struct_h1", null=False):
    import pandas as pd
    from ict import market_structure as mstruct

    # A second, INDEPENDENT walk stands in for the dollar under --null, so the
    # overlay is exercised without being correlated to the pair by construction.
    dxy_h1 = _random_walk_h1(pd, seed=99) if null else _load_h1(DOLLAR, pd)
    if not null and dxy_h1 is None:
        print(f"  {DOLLAR}: no data — dollar overlay unavailable")

    per_pair, universe = {}, (["NULL"] if null else list(PAIRS))
    for pair in universe:
        h1 = _random_walk_h1(pd) if null else _load_h1(pair, pd)
        d = _daily_from_h1(h1) if null else _load_daily(pair, pd)
        if d is None or len(d) < 40:
            print(f"  {pair}: no daily data, skipped")
            continue
        dirs = {"struct_d": _struct_dir_series(d, window, mstruct)}
        if h1 is not None:
            dirs["struct_h1"] = _h1_dir_per_day(h1, d.index, h1_window,
                                                mstruct, pd)
        if dxy_h1 is not None:
            dirs["dollar_h1"] = _h1_dir_per_day(dxy_h1, d.index, h1_window,
                                                mstruct, pd)
        per_pair[pair] = _observations(d, _pip(pair) if not null else 0.0001,
                                       min_gap_pips, horizon, dirs)
        print(f"  {pair}: {len(per_pair[pair])} straddle bars "
              f"[{', '.join(sorted(dirs))}]")

    rows = [r for v in per_pair.values() for r in v]
    if not rows:
        print("  no observations — nothing to report")
        return 1
    uniq = [r for r in rows if r["first"]]

    L = ["# Which gap fills FIRST — structure vs distance (gap race)", "",
         "At every bar where an unfilled daily gap sits ABOVE *and* BELOW price, "
         "two rules each predict which one fills first: **structure** (the Ep-12 "
         "intermediate trend) and **distance** (the nearer gap — the naive rule, "
         "and the one P76 used to break the tie). The outcome is which gap "
         "actually fills first within the horizon.", "",
         "**Read the DISAGREE table.** Where the two rules agree, structure "
         "scores well for free simply because price that has moved up is both "
         "trending up and nearer the upper gap. Only the disagree cases separate "
         "real structural information from that confound.", "",
         f"Horizon {horizon} days · structure window {window} bars · "
         f"min gap {min_gap_pips} pips" + ("  ·  **RANDOM-WALK NULL**" if null else ""),
         ""]

    L += ["## 1. Coverage", "", "```",
          f"{'set':<10} {'straddle bars':>14} {'unique pairs':>13} {'resolved':>9}",
          "-" * 52]
    for nm, rs in (("all days", rows), ("unique", uniq)):
        res = sum(1 for r in rs if r["actual"] is not None)
        L.append(f"{nm:<10} {len(rs):>14} "
                 f"{sum(1 for r in rs if r['first']):>13} {res:>9}")
    L.append("```")
    L += ["", "Consecutive days usually straddle the SAME two gaps, so the "
          "per-day count is full of near-duplicates. **`unique` — the first day "
          "each distinct gap pair straddles price — is what the verdict is read "
          "off.**", ""]

    def block(title, rs, note=""):
        out = ["", f"## {title}", ""]
        if note:
            out += [note, ""]
        out += ["```",
                f"{'split':<6} {'rule':<10} {'n':>6} {'correct':>8} {'rate':>8} {'SE':>7} {'vs 50%':>8}",
                "-" * 58]
        for sp in ("IS", "OOS", "both"):
            sub = rs if sp == "both" else [r for r in rs if r["split"] == sp]
            for rule in ("struct_h1", "struct_d", "dollar_h1", "dist"):
                h, n = _acc(sub, rule)
                if not n:
                    continue
                se = _se_pp(h, n)
                sig = (_rate(h, n) - 50.0) / se if se else float("nan")
                out.append(f"{sp:<6} {rule:<10} {n:>6} {h:>8} "
                           f"{_rate(h, n):>7.1f}% {se:>6.1f} {sig:>+7.2f}")
        out.append("```")
        return out

    L += block("2. All straddle cases (unique gap pairs)", uniq)
    key = primary if any(primary in r for r in uniq) else "struct_d"
    if key != primary:
        print(f"  NOTE: '{primary}' unavailable — decider falls back to '{key}'")
    dis = [r for r in uniq if r.get(key) and r["dist"] and r[key] != r["dist"]]
    agr = [r for r in uniq if r.get(key) and r["dist"] and r[key] == r["dist"]]
    L += block(f"3. ⭐ THE DECIDER — `{key}` and distance DISAGREE", dis,
               "Structure is pointing at the FARTHER gap. **Do not read this "
               "against 50%** -- the nearer level wins on geometry alone (~62% "
               "even on a random walk), so a useless structure reads ~38% here. "
               "Section 5 makes the comparison that is actually calibrated.")
    L += block("4. Control — the two rules AGREE", agr,
               "Both rules name the same gap, so this cannot separate them. "
               "Shown to confirm the setup detects a real effect at all: if this "
               "is also ~50%, neither rule works and section 3 is moot.")

    L += ["", "## 5. ⭐ VERDICT — does distance FAIL where structure contradicts it?", "",
          "The calibrated test. `agree` and `disagree` are disjoint, so this is a "
          "clean two-proportion comparison and needs no external baseline. If "
          "structure carries information it is flagging exactly the cases where "
          "the nearer gap does NOT fill first, so **distance must score worse on "
          "`disagree` than on `agree`**. A drop near zero means structure is only "
          "restating distance — which is what the random-walk null shows (3.3pp, "
          "0.5 SE).", "", "```",
          f"{'split':<6} {'distance on agree':>18} {'on disagree':>13} {'drop':>8} {'SE':>7} {'in SE':>7}",
          "-" * 64]

    def _drop(sp):
        ga = agr if sp == "both" else [r for r in agr if r["split"] == sp]
        gd = dis if sp == "both" else [r for r in dis if r["split"] == sp]
        ha, na = _acc(ga, "dist")
        hd, nd = _acc(gd, "dist")
        if not na or not nd:
            return None
        pa, pd_ = ha / na, hd / nd
        pool = (ha + hd) / (na + nd)
        se = 100.0 * (pool * (1 - pool) * (1 / na + 1 / nd)) ** 0.5
        drop = 100.0 * (pa - pd_)
        return na, nd, 100 * pa, 100 * pd_, drop, se, (drop / se if se else 0.0)

    for sp in ("IS", "OOS", "both"):
        r = _drop(sp)
        if r is None:
            continue
        na, nd, pa, pd_, drop, se, sig = r
        L.append(f"{sp:<6} {pa:>16.1f}% {pd_:>12.1f}% {drop:>+7.1f} "
                 f"{se:>6.1f} {sig:>+6.2f}")
    L.append("```")

    tot = _drop("both")
    isr, oosr = _drop("IS"), _drop("OOS")
    L += ["", "### Verdict", ""]
    if tot is None or min(tot[0], tot[1]) < 30:
        L.append("**INCONCLUSIVE** — too few disagree cases to read.")
    else:
        drop, sig = tot[4], tot[6]
        both_pos = (isr and oosr and isr[4] > 0 and oosr[4] > 0)
        if sig >= 2.0 and drop >= 8.0 and both_pos:
            L.append(f"🟢 **GREEN** — when structure contradicts the nearer gap, "
                     f"distance's hit rate falls {drop:.1f}pp ({sig:+.1f} SE), and "
                     f"the drop is present in BOTH halves "
                     f"({isr[4]:+.1f} / {oosr[4]:+.1f}). Market structure is "
                     f"picking the gap, and it is a target-selection rule — the "
                     f"one class of change that has ever worked in this project.")
        elif sig >= 2.0:
            L.append(f"🟡 **MIXED** — a {drop:.1f}pp drop ({sig:+.1f} SE) overall, "
                     f"but the halves disagree ({isr[4]:+.1f} / {oosr[4]:+.1f}). "
                     f"Not validated; criterion #2 fails.")
        else:
            L.append(f"🔴 **RED** — the drop is {drop:.1f}pp ({sig:+.1f} SE) on "
                     f"n={tot[0]}/{tot[1]}. Distance does no worse when structure "
                     f"contradicts it, so structure is not identifying which gap "
                     f"fills first — on this data the tie-break really is "
                     f"geometric.")
    L += ["", "Ship gate: the drop must reach 2 SE overall AND be positive in both "
          "halves AND be large enough to matter (>=8pp). Anything less is the "
          "random-walk pattern.", ""]

    txt = "\n".join(L) + "\n"
    print(txt)
    if null:
        print("NULL RUN — not written to the report file.")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print(f"wrote {OUT}")

    if os.environ.get("NO_PUSH") != "1":
        import subprocess
        def _git(*a):
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
        br = _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "HEAD"
        _git("add", "-f", OUT)
        _git("commit", "-q", "-m", "gap race report (auto)")
        _git("pull", "-q", "--rebase", "--no-edit", "origin", br)
        if _git("push", "origin", br).returncode == 0:
            print("REPORT PUSHED")
        else:
            print("auto-push failed - paste the report to Claude")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--null", action="store_true",
                    help="random-walk sanity check; must read ~50%%")
    ap.add_argument("--horizon", type=int, default=60)
    ap.add_argument("--window", type=int, default=120,
                    help="daily bars used for the struct_d read")
    ap.add_argument("--h1-window", type=int, default=120,
                    help="H1 bars (~5 days) used for the struct_h1 read")
    ap.add_argument("--primary", default="struct_h1",
                    choices=("struct_h1", "struct_d", "dollar_h1"),
                    help="which rule the agree/disagree decider is built on")
    ap.add_argument("--min-gap", type=float, default=3.0)
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        sys.exit(0)
    sys.exit(run(min_gap_pips=a.min_gap, horizon=a.horizon, window=a.window,
                 h1_window=a.h1_window, primary=a.primary, null=a.null))
