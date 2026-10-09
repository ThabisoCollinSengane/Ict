#!/usr/bin/env python3
"""Does price gravitate to an unfilled HTF FVG — even if it takes days?

The trader's claim, and the most load-bearing one in the model: "the FVG always
calls price to it." If true, an unmitigated W1/D1/H4 gap is a standing draw and
the bias should be held toward it until reached, however long that takes.

This measures it on RAW price, independent of the strategy. For every FVG that
forms on W/D/H4 it asks: was the gap ever traded into, and how many days did it
take? Then it conditions on the two things the trader says decide whether price
will actually go there:

  * a SHIFT IN MARKET STRUCTURE toward the gap, and
  * INTERMARKET support — the prior daily dollar close favouring the move.

The unconditional reach rate tests "price always gravitates." The conditional
rates test whether the confirmations add anything, or whether the gap pulls price
regardless. `median days` matters as much as the rate: a gap reached 85% of the
time but typically 14 days later is a real magnet and a useless intraday target.

Measurement only. Nothing here ships to the engine.

Run:  python scripts/fvg_draw_study.py [--tfs W,D,240T] [--max-days 30]
      python scripts/fvg_draw_study.py --selftest      # no data needed
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

REPORT = os.path.join(ROOT, "data", "fvg_draw_report.md")
PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
DXY = "UDXUSD"
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)
NO_PUSH = False


# ─────────────────────────── pure logic (unit-testable) ────────────────────────

def find_fvgs(highs, lows):
    """Every 3-bar fair value gap. Returns (bar_index, bottom, top, direction).

    Bullish: bar i's LOW sits above bar i-2's HIGH — an unfilled void below price.
    Bearish: bar i's HIGH sits below bar i-2's LOW. The gap is CONFIRMED at bar i,
    so it cannot be reached before then.
    """
    out = []
    for i in range(2, len(highs)):
        if lows[i] > highs[i - 2]:
            out.append((i, highs[i - 2], lows[i], +1))
        elif highs[i] < lows[i - 2]:
            out.append((i, highs[i], lows[i - 2], -1))
    return out


def first_touch(highs, lows, start, bottom, top, limit):
    """Bars until price first trades INTO [bottom, top], or None inside `limit`.

    A gap is reached the moment price trades into the void — the wick counts,
    because the draw is the gap itself, not a close through it.
    """
    end = min(start + 1 + limit, len(highs))
    for j in range(start + 1, end):
        if lows[j] <= top and highs[j] >= bottom:
            return j - start
    return None


def mss_toward_gap(highs, lows, start, bottom, top, gap_dir, window):
    """Bar where structure broke TOWARD the gap, or None. NOT circular.

    ⚠️ The obvious reading — "did price break the recent low" — is circular. For
    a bullish gap the recent lows include bar start-2, whose low sits at or below
    the gap's BOTTOM edge, so ref <= bottom always and breaking it REQUIRES
    trading through the gap. Verified on 62,797 synthetic gaps: zero exceptions.
    That is why the first run reported MSS reach = 100.0% on every timeframe and
    split — by construction, not by prediction. Same defect as P65c and P66.

    A genuine precursor is the break of a swing price can take out WITHOUT
    entering the gap. For a gap BELOW price that is a swing LOW sitting strictly
    ABOVE the gap's top edge. No such swing exists when the gap forms (price has
    just displaced away from it), so the reference is armed FORWARD, re-arming on
    the most recent qualifying fractal — the P65d dead-latch lesson.
    """
    end = min(start + 1 + window, len(highs))
    pending = None
    for i in range(start + 2, end):
        c = i - 1                          # fractal confirmed by bar i
        if gap_dir > 0:
            if (lows[c] < lows[c - 1] and lows[c] < lows[i] and lows[c] > top):
                pending = lows[c]
            if pending is not None and lows[i] < pending:
                return i
        else:
            if (highs[c] > highs[c - 1] and highs[c] > highs[i]
                    and highs[c] < bottom):
                pending = highs[c]
            if pending is not None and highs[i] > pending:
                return i
    return None


def mirror_band(close, bottom, top):
    """The CONTROL: same width, same distance, opposite side of price.

    A reach rate means nothing on its own — a band a few pips from price gets
    traded into whether or not a gap is there. This is the placebo that decides
    the question, the counterpart of P65's single-pair control. Pooled over
    bullish and bearish gaps, directional drift cancels.
    """
    return (2.0 * close - top, 2.0 * close - bottom)


def summarise(rows, max_days):
    """rows = list of (days_to_reach or None). Reach rate + median days."""
    if not rows:
        return {"n": 0}
    hit = [d for d in rows if d is not None]
    med = sorted(hit)[len(hit) // 2] if hit else None
    return {
        "n": len(rows),
        "reach": 100.0 * len(hit) / len(rows),
        "med_days": med,
        # reached quickly enough to be a tradeable intraday/next-day draw
        "fast": 100.0 * sum(1 for d in hit if d <= 2) / len(rows),
    }


def verdict(uncond_is, uncond_oos, ctrl_is, ctrl_oos,
            min_reach=70.0, min_lift=5.0):
    """GREEN needs the gap to be reached often AND to beat its own control.

    The raw reach rate cannot answer the question: an identical band on the
    other side of price is reached too. What the trader's claim requires is that
    the GAP is reached more than that placebo — in both splits.
    """
    if not uncond_is.get("n") or not uncond_oos.get("n"):
        return "RED", "no gaps in one or both splits"
    a, b = uncond_is["reach"], uncond_oos["reach"]
    ca, cb = ctrl_is.get("reach"), ctrl_oos.get("reach")
    if ca is None or cb is None:
        return "RED", "control missing — result uninterpretable"
    la, lb = a - ca, b - cb
    tag = (f"reached {a:.0f}%/{b:.0f}% vs control {ca:.0f}%/{cb:.0f}% "
           f"(lift {la:+.1f}pp IS / {lb:+.1f}pp OOS)")
    if a >= min_reach and b >= min_reach and la >= min_lift and lb >= min_lift:
        return "GREEN", f"{tag} — the gap pulls price harder than a plain band"
    if la >= min_lift and lb >= min_lift:
        return "YELLOW", f"{tag} — beats its control, but not reached often enough"
    return "RED", (f"{tag} — no edge over an identical band on the other side; "
                   f"the reach rate is what any nearby level scores")


# ─────────────────────────────── data plumbing ────────────────────────────────

def run(tfs, max_days, mss_win):
    import pandas as pd
    from triple_sweep_study import _load, _resample, daily_direction

    dxy_m1 = _load(DXY)
    if dxy_m1 is None:
        print("  MISSING UDXUSD — put UDXUSD_YYYY.csv in data/histdata/")
        return 1
    dxy_d = _resample(dxy_m1, "1D")
    dxy_dir = dxy_d.apply(
        lambda r: daily_direction(r["o"], r["h"], r["l"], r["c"], 0.15),
        axis=1).shift(1)                      # prior completed day — no lookahead

    out = {}
    for tf in tfs:
        buckets = {k: [] for k in ("IS", "OOS", "ctrlIS", "ctrlOOS",
                                   "mssIS", "mssOOS", "msscIS", "msscOOS",
                                   "imIS", "imOOS", "bothIS", "bothOOS")}
        for pair in PAIRS:
            m1 = _load(pair)
            if m1 is None:
                continue
            bars = _resample(m1, tf)
            h = bars["h"].to_numpy()
            l = bars["l"].to_numpy()
            c_ = bars["c"].to_numpy()
            years = bars.index.year.to_numpy()
            # how many BARS of this timeframe make up `max_days` of calendar time
            per_day = {"W": 1 / 5.0, "D": 1.0, "240T": 6.0, "60T": 24.0}.get(tf, 6.0)
            limit = int(max_days * per_day)
            dd = dxy_dir.reindex(bars.index, method="ffill").fillna(0).to_numpy()

            for (i, bot, top, gdir) in find_fvgs(h, l):
                if i >= len(h) - 2:
                    continue
                raw = first_touch(h, l, i, bot, top, limit)
                days = None if raw is None else raw / per_day
                key = "IS" if years[i] in IS_YEARS else "OOS"
                buckets[key].append(days)

                # CONTROL: identical band, same distance, other side of price
                cb, ct = mirror_band(c_[i], bot, top)
                craw = first_touch(h, l, i, cb, ct, limit)
                buckets["ctrl" + key].append(
                    None if craw is None else craw / per_day)

                # dollar support: a gap BELOW a X/USD pair is reached by the pair
                # falling, which is the dollar RISING (+1).
                im = (dd[i] == -gdir) and dd[i] != 0
                if im:
                    buckets["im" + key].append(days)

                # The confirmation must PRECEDE the outcome, never share its
                # window (P65c). Measure the reach strictly AFTER the shift bar,
                # and drop gaps price had already reached at or before it — a
                # shift bar that lands in the gap did not predict the arrival,
                # it WAS the arrival (37% of shifts on a random-walk fixture).
                mb = mss_toward_gap(h, l, i, bot, top, gdir, mss_win)
                if mb is None or (raw is not None and i + raw <= mb):
                    continue
                mraw = first_touch(h, l, mb, bot, top, limit)
                mdays = None if mraw is None else mraw / per_day
                buckets["mss" + key].append(mdays)
                # the shift needs its own control too — a number without a
                # baseline is what put the first run wrong
                mcb, mct = mirror_band(c_[mb], bot, top)
                mcraw = first_touch(h, l, mb, mcb, mct, limit)
                buckets["mssc" + key].append(
                    None if mcraw is None else mcraw / per_day)
                if im:
                    buckets["both" + key].append(mdays)
        out[tf] = {k: summarise(v, max_days) for k, v in buckets.items()}
    _write(out, tfs, max_days, mss_win)
    return 0


def _write(out, tfs, max_days, mss_win):
    L = ["# Does the FVG call price to it?", "",
         f"Every 3-bar gap on {', '.join(tfs)}, all pairs, followed forward up to "
         f"**{max_days} days**. `reach` = ever traded into. `fast` = reached "
         f"within 2 days (a tradeable draw rather than a distant magnet). "
         f"`MSS` = structure broke toward the gap; `IM` = the prior daily dollar "
         f"close favours the move; `both` = the trader's full condition. "
         f"Structure must shift within **{mss_win}** bars of the gap forming — if "
         f"an MSS bucket reads 0 on a timeframe, that window is too tight for it, "
         f"not an absence of shifts.", "",
         "**`control` is the row that decides the question.** It is a band of the "
         "SAME width at the SAME distance on the OPPOSITE side of price. Price "
         "trades into a nearby band whether or not a gap is there, so only the "
         "gap's LIFT over its control is evidence that the gap itself calls "
         "price. A high reach rate with a flat lift means the level was near, "
         "not special.", "",
         "MSS rows measure the reach FROM the shift bar forward, off a swing that "
         "sits clear of the gap, and skip gaps already filled before the shift — "
         "so the confirmation cannot contain its own outcome.", ""]
    for tf in tfs:
        st = out.get(tf, {})
        L += [f"## {tf}", "", "```",
              f"{'bucket':<14} {'n':>6} {'reach%':>8} {'fast%':>7} {'med days':>9}",
              "-" * 48]
        for key, name in (("IS", "all IS"), ("OOS", "all OOS"),
                          ("ctrlIS", "control IS"), ("ctrlOOS", "control OOS"),
                          ("mssIS", "MSS IS"), ("mssOOS", "MSS OOS"),
                          ("msscIS", "MSS ctrl IS"), ("msscOOS", "MSS ctrl OOS"),
                          ("imIS", "IM IS"), ("imOOS", "IM OOS"),
                          ("bothIS", "both IS"), ("bothOOS", "both OOS")):
            s = st.get(key, {})
            if not s.get("n"):
                L.append(f"{name:<14} {0:>6}   —")
                continue
            md = "—" if s["med_days"] is None else f"{s['med_days']:.1f}"
            # one W bar spans 5 days, so "reached within 2 days" can never fire
            fa = "   n/a" if tf == "W" else f"{s['fast']:>6.1f}%"
            L.append(f"{name:<14} {s['n']:>6} {s['reach']:>7.1f}% "
                     f"{fa} {md:>9}")
        L.append("```")
        v, why = verdict(st.get("IS", {}), st.get("OOS", {}),
                         st.get("ctrlIS", {}), st.get("ctrlOOS", {}))
        L += ["", f"**Verdict: {v}** — {why}", ""]
    L += ["---", "",
          "A high reach rate with a long median is a real magnet and a poor "
          "intraday target — which would argue for the gap as a BIAS held across "
          "days, not as a take-profit. But read the LIFT over the control first: "
          "without it, a high reach rate only says the band was close. "
          "Measurement only; nothing ships."]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    if not NO_PUSH:
        _publish(REPORT)


def _publish(path):
    import subprocess

    def _git(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)

    _git("add", "-f", path)
    if _git("diff", "--cached", "--quiet", "--", path).returncode == 0:
        print(f"\n  report unchanged — nothing to commit. Paste "
              f"{os.path.basename(path)} if Claude has not seen it.")
        return
    sha = (_git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown")
    if _git("commit", "-q", "-m", f"FVG draw report (auto, on {sha})").returncode:
        print("\n  (commit failed — paste the report above)")
        return
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    p = _git("push", "origin", "HEAD")
    print(f"\n  RESULTS PUSHED — Claude can read data/{os.path.basename(path)}"
          if p.returncode == 0 else
          "\n  (auto-push failed — paste the report above)\n" + p.stderr[-300:])


# ──────────────────────────────── selftest ────────────────────────────────────

def selftest():
    # find_fvgs: a clean bullish gap — bar 2's low above bar 0's high
    h = [1.00, 1.05, 1.12, 1.13]
    l = [0.98, 1.01, 1.06, 1.07]
    ev = find_fvgs(h, l)
    assert ev and ev[0][0] == 2 and ev[0][3] == +1, ev
    assert abs(ev[0][1] - 1.00) < 1e-9 and abs(ev[0][2] - 1.06) < 1e-9, ev
    # bearish mirror
    hb = [1.10, 1.05, 0.98, 0.97]
    lb = [1.06, 1.01, 0.94, 0.93]
    eb = find_fvgs(hb, lb)
    assert eb and eb[0][3] == -1, eb
    # no gap when the bars overlap
    assert find_fvgs([1.0, 1.0, 1.0], [0.9, 0.9, 0.9]) == []

    # first_touch: reached on the 3rd bar after formation, and censored when not
    th = [1.10] * 3 + [1.09, 1.08, 1.05]
    tl = [1.08] * 3 + [1.07, 1.06, 1.00]
    assert first_touch(th, tl, 2, 1.00, 1.02, 10) == 3, first_touch(th, tl, 2, 1.00, 1.02, 10)
    assert first_touch(th, tl, 2, 0.50, 0.60, 10) is None
    assert first_touch(th, tl, 2, 1.00, 1.02, 2) is None      # inside the limit only

    # mss_toward_gap: gap below price at [0.90, 0.95]. Price must first build a
    # swing low ABOVE 0.95, then break it — a shift price can make without ever
    # entering the gap.
    #        idx  0     1     2     3     4     5     6     7
    mh = [1.20, 1.20, 1.20, 1.20, 1.20, 1.20, 1.20, 1.20]
    ml = [1.10, 1.10, 1.10, 1.00, 1.05, 1.05, 0.99, 0.99]
    #   bar 3 is a fractal low (1.00 < 1.10 and < 1.05), confirmed by bar 4,
    #   and 1.00 > top 0.95 -> a legal reference. Bar 6 breaks it.
    assert mss_toward_gap(mh, ml, 2, 0.90, 0.95, +1, 8) == 6, \
        mss_toward_gap(mh, ml, 2, 0.90, 0.95, +1, 8)
    # no break -> None
    assert mss_toward_gap(mh, [1.10, 1.10, 1.10, 1.00, 1.05, 1.05, 1.05, 1.05],
                          2, 0.90, 0.95, +1, 8) is None
    # a reference INSIDE the gap is illegal — that is the circular case, and the
    # break of it must NOT be reported as a shift
    assert mss_toward_gap(mh, [1.10, 1.10, 1.10, 0.93, 0.96, 0.96, 0.90, 0.90],
                          2, 0.90, 0.95, +1, 8) is None
    # mirror control: same width, same distance, other side of price
    cb, ct = mirror_band(1.00, 0.90, 0.95)
    assert abs(cb - 1.05) < 1e-9 and abs(ct - 1.10) < 1e-9, (cb, ct)

    s = summarise([1.0, 2.0, None, 8.0], 30)
    assert s["n"] == 4 and s["reach"] == 75.0 and s["fast"] == 50.0, s
    G = ({"n": 50, "reach": 85.0}, {"n": 50, "reach": 80.0})
    assert verdict(*G, {"reach": 60.0}, {"reach": 55.0})[0] == "GREEN"
    # high reach but the control matches it -> no edge, however big the number
    assert verdict(*G, {"reach": 84.0}, {"reach": 79.0})[0] == "RED"
    # beats its control but is not reached often enough
    assert verdict({"n": 50, "reach": 40.0}, {"n": 50, "reach": 38.0},
                   {"reach": 20.0}, {"reach": 18.0})[0] == "YELLOW"
    # lift in one split only is not a result
    assert verdict(*G, {"reach": 60.0}, {"reach": 79.0})[0] == "RED"
    print("selftest OK — gap detection, first touch, non-circular shift, "
          "mirror control, verdict")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tfs", default="W,D,240T")
    ap.add_argument("--max-days", type=int, default=30)
    ap.add_argument("--mss-window", type=int, default=6,
                    help="bars after the gap forms in which structure must shift "
                         "toward it; an all-zero MSS bucket usually means this is "
                         "too tight for the timeframe")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    global NO_PUSH
    NO_PUSH = a.no_push
    return run(tuple(a.tfs.split(",")), a.max_days, a.mss_window)


if __name__ == "__main__":
    sys.exit(main())
