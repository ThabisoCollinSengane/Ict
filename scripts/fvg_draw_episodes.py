#!/usr/bin/env python3
"""P76 — the DAILY FVG as a standing DRAW: how many entries aim at it before it fills.

The measurement that was missing, and the trader had to ask for twice.

WHAT I MEASURED BEFORE AND WHY IT WAS THE WRONG UNIT
----------------------------------------------------
P75 reported the per-trade outcome of trades whose TARGET was an FVG — WR 35.5%,
"the weakest family". That is arithmetic, not evidence: a daily gap sits tens to
hundreds of pips away, and a single intraday trade carrying a ~10-pip structural
stop cannot be expected to reach it. Judging a multi-day objective by one
intraday trade's hit rate answers a question nobody asked.

WHAT THIS MEASURES
------------------
The gap as a DRAW ON LIQUIDITY that persists until it is filled. The unit is the
EPISODE — from the daily FVG forming to the bar that fills it — and the headline
is: **how many entries did the algo make AIMING AT the gap over that window?**

Per episode:
  - duration in days, and whether it was ever filled at all
  - `toward`  entries: the trade direction points at the gap POSITIONALLY
                       (gap above price -> a long aims at it; gap below -> a short)
  - `away`    entries: the opposite
  - `inside`  entries: price was within the gap, so no direction aims at it

`toward` vs `away` is the internal control and needs no mirror band: both
populations are the algo's own entries during the same episode, on the same pair,
under the same gates. If aiming at the day's gap is worth anything, the toward
bucket separates from the away bucket.

⚠️ COMPLETED daily candles only. A forming daily bar carries the whole day's High
and Low including hours that have not happened, so a gap read off it — or a FILL
judged by it — would be a function of the outcome. Seven bugs of that exact shape
in this project (P67/P70/P72, P73 §1, and the `_draw_ladder` retraction).

⚠️ RETROSPECTIVE BY CONSTRUCTION, and that is the question asked. "Until it was
eventually reached" uses the fill date, which is not knowable at entry. So the
episode framing DESCRIBES how entries distributed around a draw; it is NOT a
tradeable signal on its own. What IS knowable live is the toward/away split at
entry — the gap's existence and position are known then. Build a lever only on
that half.

Mitigation is ICT Ep 9 — a full body CLOSE through the FAR side — matching
`_scan_htf_fvgs` in the engine, NOT the near-edge wick rule that P75 found in
`_targets_in_series`.

Run (needs the trade dump, so the backtest first):
    python run_backtest_histdata.py
    python scripts/fvg_draw_episodes.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

DATA = os.path.join(ROOT, "data", "histdata")
OUT = os.path.join(ROOT, "data", "fvg_draw_episodes.md")
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)
NO_PUSH = False


def _find_dump():
    """Same candidate list as the six existing scripts (P73 lesson)."""
    for p in (os.path.join(ROOT, "data", "histdata", "trades_dump.csv"),
              os.path.join(ROOT, "data", "trades_dump.csv")):
        if os.path.exists(p):
            return p
    return None


# ─────────────────────────── pure logic (unit-testable) ────────────────────────

def daily_fvgs(highs, lows, min_size):
    """Every 3-bar FVG in the series. Returns (i, gdir, bottom, top); `i` is the
    index of the THIRD bar — the gap is only knowable once that bar completes."""
    out = []
    for i in range(2, len(highs)):
        h0, l0 = highs[i - 2], lows[i - 2]
        h2, l2 = highs[i], lows[i]
        if l2 > h0 and (l2 - h0) >= min_size:
            out.append((i, +1, h0, l2))
        elif h2 < l0 and (l0 - h2) >= min_size:
            out.append((i, -1, h2, l0))
    return out


def fill_index(closes, start, gdir, bottom, top):
    """First bar CLOSING a full body through the FAR side (ICT Ep 9), or None.

    Bullish gap sits below price and is spent by a close BELOW its bottom;
    bearish gap sits above and is spent by a close ABOVE its top. This is the
    engine's `_scan_htf_fvgs` rule, not the near-edge wick rule.
    """
    for j in range(start + 1, len(closes)):
        if gdir > 0 and closes[j] <= bottom:
            return j
        if gdir < 0 and closes[j] >= top:
            return j
    return None


def aim(bottom, top, price, direction):
    """Does this trade AIM at the gap? Purely positional — how the gap formed is
    irrelevant to which way price must travel to reach it (the P73 `zone_ahead`
    reasoning, and the same correction P75 applied to target selection)."""
    if bottom <= price <= top:
        return "inside"
    if bottom > price:                       # gap is ABOVE -> a long aims at it
        return "toward" if direction > 0 else "away"
    return "toward" if direction < 0 else "away"   # gap BELOW -> a short aims


def _pf(gross_win, gross_loss):
    return (gross_win / gross_loss) if gross_loss else float("inf")


def _selftest():
    # daily_fvgs — bullish, bearish, and one below the size floor
    hi = [10, 10, 10, 20, 20]
    lo = [9, 9, 15, 15, 15]          # bar2 low 15 > bar0 high 10 -> bullish 10..15
    g = daily_fvgs(hi, lo, 1.0)
    assert g and g[0][1] == +1 and g[0][2] == 10 and g[0][3] == 15, g
    assert daily_fvgs(hi, lo, 99.0) == [], "size floor must reject"
    hi2 = [20, 20, 10]; lo2 = [15, 15, 9]   # bar2 high 10 < bar0 low 15 -> bearish
    g2 = daily_fvgs(hi2, lo2, 1.0)
    assert g2 and g2[0][1] == -1 and g2[0][2] == 10 and g2[0][3] == 15, g2

    # fill_index — far-side close only; a close INSIDE the gap must NOT fill it
    assert fill_index([0, 0, 0, 12, 9], 2, +1, 10, 15) == 4, "close below bottom fills"
    assert fill_index([0, 0, 0, 12, 11], 2, +1, 10, 15) is None, "inside is not a fill"
    assert fill_index([0, 0, 0, 14, 16], 2, -1, 10, 15) == 4, "close above top fills"

    # aim — positional, both gap directions, both trade directions
    assert aim(10, 15, 5, +1) == "toward"   # gap above, long
    assert aim(10, 15, 5, -1) == "away"
    assert aim(10, 15, 20, -1) == "toward"  # gap below, short
    assert aim(10, 15, 20, +1) == "away"
    assert aim(10, 15, 12, +1) == "inside"
    assert aim(10, 15, 10, -1) == "inside", "edge counts as inside"
    print("selftest OK")


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


def _pip(pair):
    return 0.01 if pair.endswith("JPY") else 0.0001


def run(min_gap_pips=3.0):
    import pandas as pd

    dump = _find_dump()
    if dump is None:
        print("  trades_dump.csv MISSING — looked in data/histdata/ and data/.")
        print("  Run `python run_backtest_histdata.py` first.")
        return 1
    print(f"  trade dump: {dump}")
    td = pd.read_csv(dump)
    need = {"opened_at", "pair", "direction", "entry", "pnl"}
    miss = need - set(td.columns)
    if miss:
        print(f"  trades_dump.csv lacks {sorted(miss)}")
        return 1
    td = td.dropna(subset=sorted(need))
    # No leading underscores: itertuples renames those to positional fields.
    td["t_open"] = pd.to_datetime(td["opened_at"], utc=True, errors="coerce")
    td = td[td.t_open.notna()]

    episodes, trades = [], []
    for pair in sorted(td["pair"].unique()):
        m1 = _load_utc(pair)
        if m1 is None:
            print(f"  {pair}: no M1 data, skipped")
            continue
        d = m1.resample("1D").agg({"o": "first", "h": "max",
                                   "l": "min", "c": "last"}).dropna()
        hi, lo, cl = d["h"].tolist(), d["l"].tolist(), d["c"].tolist()
        idx = list(d.index)
        gaps = daily_fvgs(hi, lo, min_gap_pips * _pip(pair))
        pair_eps = []
        for (i, gdir, bot, top) in gaps:
            j = fill_index(cl, i, gdir, bot, top)
            pair_eps.append({
                "pair": pair, "gdir": gdir, "bottom": bot, "top": top,
                # The gap is knowable only once bar i has CLOSED, so it becomes
                # active at the start of the next day.
                "t_form": idx[i] + pd.Timedelta(days=1),
                "t_fill": idx[j] if j is not None else None,
                "filled": j is not None,
                "days": (j - i) if j is not None else None,
                "toward": 0, "away": 0, "inside": 0,
                "pnl_toward": 0.0, "pnl_away": 0.0,
                "win_toward": 0, "win_away": 0,
            })
        sub = td[td["pair"] == pair]
        for r in sub.itertuples(index=False):
            t, px, dirn, pnl = r.t_open, float(r.entry), int(r.direction), float(r.pnl)
            live = [e for e in pair_eps
                    if e["t_form"] <= t and (e["t_fill"] is None or e["t_fill"] > t)]
            if not live:
                trades.append({"t": t, "pair": pair, "cls": "no_gap", "pnl": pnl})
                continue
            above = [e for e in live if e["bottom"] > px]
            below = [e for e in live if e["top"] < px]
            nearest = min(live, key=lambda e: 0.0 if e["bottom"] <= px <= e["top"]
                          else min(abs(e["bottom"] - px), abs(e["top"] - px)))
            cls = aim(nearest["bottom"], nearest["top"], px, dirn)
            nearest[cls] += 1
            if cls in ("toward", "away"):
                nearest[f"pnl_{cls}"] += pnl
                if pnl > 0:
                    nearest[f"win_{cls}"] += 1
            trades.append({"t": t, "pair": pair, "cls": cls, "pnl": pnl,
                           # Straddled = unfilled gaps on BOTH sides, so "toward"
                           # is ambiguous. Reported, never folded into a side
                           # (the `ran_both` lesson).
                           "straddled": bool(above and below)})
        episodes += pair_eps

    ep = pd.DataFrame(episodes)
    tr = pd.DataFrame(trades)
    if ep.empty or tr.empty:
        print("  no episodes or no trades — nothing to report")
        return 1

    def split_of(ts):
        return "IS" if ts.year in IS_YEARS else "OOS"

    tr["split"] = tr["t"].map(split_of)
    ep["split"] = ep["t_form"].map(split_of)

    L = ["# Daily FVG as a standing DRAW — entries per episode (P76)", "",
         "The unit is the gap EPISODE (formation -> fill), not the trade. "
         "`toward` = the entry direction aims at the gap positionally; `away` = "
         "the opposite. Completed daily candles only; fill = full body close "
         "through the far side (ICT Ep 9).", ""]

    L += ["## 1. Episode census", "", "```",
          f"{'split':<6} {'gaps':>6} {'filled':>7} {'fill%':>7} {'medDays':>8} {'p90Days':>8}",
          "-" * 48]
    for s in ("IS", "OOS"):
        e = ep[ep.split == s]
        if not len(e):
            continue
        f = e[e.filled]
        L.append(f"{s:<6} {len(e):>6} {len(f):>7} {100*len(f)/len(e):>6.1f}% "
                 f"{(f['days'].median() if len(f) else float('nan')):>8.1f} "
                 f"{(f['days'].quantile(0.9) if len(f) else float('nan')):>8.1f}")
    L.append("```")

    L += ["", "## 2. THE HEADLINE — entries aimed at the gap per episode", "",
          "How many entries the algo made AIMING at each daily gap before it "
          "filled. This is the question P75 never asked.", "", "```",
          f"{'split':<6} {'episodes':>9} {'with>=1':>8} {'toward':>7} {'away':>6} "
          f"{'inside':>7} {'med/ep':>7} {'max/ep':>7}",
          "-" * 64]
    for s in ("IS", "OOS"):
        e = ep[ep.split == s]
        if not len(e):
            continue
        act = e[e.toward > 0]
        L.append(f"{s:<6} {len(e):>9} {len(act):>8} {int(e.toward.sum()):>7} "
                 f"{int(e.away.sum()):>6} {int(e.inside.sum()):>7} "
                 f"{(act.toward.median() if len(act) else 0):>7.1f} "
                 f"{int(e.toward.max()):>7}")
    L.append("```")

    L += ["", "## 3. toward vs away — the internal control", "",
          "Both buckets are the algo's own entries, same pair, same episode, "
          "same gates. No mirror band needed.", "", "```",
          f"{'split':<6} {'bucket':<9} {'trades':>7} {'wins':>5} {'WR%':>6} "
          f"{'P&L ZAR':>12} {'PF':>7}",
          "-" * 56]
    for s in ("IS", "OOS"):
        t = tr[tr.split == s]
        for b in ("toward", "away", "inside", "no_gap"):
            g = t[t.cls == b]
            if not len(g):
                continue
            w = int((g.pnl > 0).sum())
            gw = g[g.pnl > 0].pnl.sum()
            gl = abs(g[g.pnl < 0].pnl.sum())
            L.append(f"{s:<6} {b:<9} {len(g):>7} {w:>5} {100*w/len(g):>5.1f}% "
                     f"{g.pnl.sum():>12.2f} {_pf(gw, gl):>7.2f}")
    L.append("```")

    if "straddled" in tr.columns:
        st = tr[tr.straddled.fillna(False)]
        L += ["", f"**Straddled:** {len(st)} entries had unfilled daily gaps on "
              f"BOTH sides, so 'toward' is ambiguous for them. Counted in the "
              f"nearest-gap classification above but flagged here rather than "
              f"folded silently into one side.", ""]

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nwrote {OUT}")

    if not NO_PUSH:
        import subprocess
        def _git(*a):
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
        br = _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "HEAD"
        _git("add", "-f", OUT)
        _git("commit", "-q", "-m", "fvg draw-episode report (auto)")
        _git("pull", "-q", "--rebase", "--no-edit", "origin", br)
        if _git("push", "origin", br).returncode == 0:
            print("REPORT PUSHED")
        else:
            print("(auto-push failed — paste the report to Claude)")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
        sys.exit(0)
    NO_PUSH = os.environ.get("NO_PUSH") == "1"
    sys.exit(run())
