#!/usr/bin/env python3
"""What does the DAILY timeframe actually do?

Eight studies on the analysis axis have measured null here (P39/P40/P47/P48/
P65/P66/P68b/P69) while every result that validated sits on the TARGET axis —
P67's rung (near PF 5.31/9.15, every far rung under 1.0 in both splits) and the
pure-price cascade (3-day pool 58%/61%). So this stays on the target axis and
asks the daily candle four questions:

  1. SHAPE   — how far does a day travel, and how directional is it?
  2. TIMING  — at what hour do the daily HIGH and LOW actually form?
  3. JUDAS   — does the day run one side of the 00:00 UTC open and close the
               other way, and does knowing which side was run predict the close?
  4. WHAT IS LEFT — from any hour, how much further does price still travel?

(4) is the one that matters, because it is a MECHANISM for P67. A far target
is not merely "far"; it may be asking for more than a day delivers. If true, the
fix is choosing targets against what is left rather than removing trades — and
no removal has ever survived the full run in this project.

  5. (if data/trades_dump.csv exists) TARGET DEMAND — every real target expressed
     as a fraction of what was typically left at that entry hour, scored against
     the outcome, and compared with the rung it was classified as.

⚠️ Timestamps. HistData is fixed EST (UTC-5). run_backtest_histdata.py adds 5h to
get UTC and the engine's daily bars are UTC days; killzones then read
America/New_York. This study mirrors that exactly. Note that
triple_sweep_study._load does NOT convert, so the "D" bars in P68b/P69 are
EST-days, not the engine's UTC-days — harmless there (gap and control share the
same bars, so the lift is internally valid) but wrong for a time-of-day study,
which is why this file does not reuse that loader.

Measurement only. Nothing here ships to the engine.

Run:  python scripts/daily_anatomy_study.py
      python scripts/daily_anatomy_study.py --selftest      # no data needed
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
REPORT = os.path.join(ROOT, "data", "daily_anatomy_report.md")
DUMP = os.path.join(ROOT, "data", "trades_dump.csv")
PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)
PIP = 0.0001
NO_PUSH = False


# ─────────────────────────── pure logic (unit-testable) ────────────────────────

def session_of(et_hour):
    """The project's own session map, in New York time."""
    if 3 <= et_hour < 7:
        return "london"
    if 7 <= et_hour < 12:
        return "ny_am"
    if et_hour == 12:
        return "noon"
    if 13 <= et_hour < 17:
        return "ny_pm"
    return "asia"


def close_position(o, h, l, c):
    """Where the close sits in the day's range: 0.0 at the low, 1.0 at the high.

    A day closing at 0.9 has held its gains; one closing at 0.5 gave them back.
    """
    if h <= l:
        return None
    return (c - l) / (h - l)


def judas_side(o, early_h, early_l, c, min_pips, pip=PIP):
    """Which side of the OPEN was run EARLY, and which way the day then closed.

    ⚠️ The window is the whole test. Measured across the FULL day, "ran the low"
    simply selects days that ended down — the condition contains its outcome, and
    the first version of this read **−43pp on a random walk** for exactly that
    reason. The run must be observable BEFORE the close it is meant to predict,
    so `early_h`/`early_l` come from the opening hours only and the close is the
    full day's. Fourth time this failure mode has appeared here (P65c, P66,
    P68b, now this) — it is the default way a study goes wrong.

    Returns (ran, closed): ran is -1 when price traded at least `min_pips` BELOW
    the open in that window, +1 when at least that far above, 0 when neither, and
    2 when BOTH sides were run (the ambiguous day — reported separately rather
    than silently assigned, because assigning it is how a rate gets inflated).
    """
    below = (o - early_l) / pip >= min_pips
    above = (early_h - o) / pip >= min_pips
    ran = 2 if (below and above) else (-1 if below else (+1 if above else 0))
    closed = +1 if c > o else (-1 if c < o else 0)
    return ran, closed


def placebo_level(o, prev_range, day_ordinal):
    """A meaningless level to ask the same Judas question of.

    The unconditional close rate is NOT a control for "swept the open then closed
    back". On a driftless random walk a day that ran the low early tends to stay
    there, so the lift is about −30pp with no institution involved — verified on
    the fixture. The only way to learn whether the OPEN is special is to run the
    identical test against a level that is not special.

    Deterministic by design (no RNG): a quarter of the previous day's range from
    the open, alternating side by date so neither direction is favoured.
    """
    off = 0.25 * prev_range * (1 if day_ordinal % 2 else -1)
    return o + off


def demand_bucket(ratio):
    """Target distance as a fraction of what is typically still available."""
    if ratio is None:
        return ""
    if ratio <= 0.5:
        return "<=0.5x"
    if ratio <= 1.0:
        return "0.5-1.0x"
    if ratio <= 1.5:
        return "1.0-1.5x"
    return ">1.5x"


def pct(part, whole):
    return None if not whole else 100.0 * part / whole


def med(vals):
    s = sorted(v for v in vals if v is not None)
    return s[len(s) // 2] if s else None


def quantiles(vals):
    s = sorted(v for v in vals if v is not None)
    if not s:
        return (None, None, None)
    def q(f):
        return s[min(len(s) - 1, int(f * len(s)))]
    return (q(0.25), q(0.50), q(0.75))


def lift_table(cond_hits, cond_n, base_hits, base_n):
    """Conditional rate, the unconditional base rate, and the lift in pp."""
    a, b = pct(cond_hits, cond_n), pct(base_hits, base_n)
    return a, b, (None if a is None or b is None else a - b)


# ─────────────────────────────── data plumbing ────────────────────────────────

def _load_utc(sym):
    """HistData M1 -> UTC-indexed frame. Mirrors run_backtest_histdata exactly."""
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


def run(min_judas_pips, early_hours):
    import numpy as np
    import pandas as pd

    out = {"pairs": {}, "hours": {}, "judas": {}, "left": {}, "cover": {}}
    left_lookup = {}          # (pair, split, et_hour) -> median pips still to come
    for pair in PAIRS:
        m1 = _load_utc(pair)
        if m1 is None:
            print(f"  MISSING {pair} — put {pair}_YYYY.csv in {DATA}")
            continue
        h1 = m1.resample("1h").agg({"o": "first", "h": "max",
                                    "l": "min", "c": "last"}).dropna()
        day = h1.index.floor("D")
        et_hour = h1.index.tz_convert("America/New_York").hour
        h1 = h1.assign(_day=day, _eth=et_hour, _yr=h1.index.year)

        # ── day-level aggregates ──────────────────────────────────────────────
        gb = h1.groupby("_day")
        d = gb.agg(o=("o", "first"), h=("h", "max"),
                   l=("l", "min"), c=("c", "last"))
        # the EARLY window: the first `early_hours` UTC hours of the day. 00:00
        # UTC is 19:00 ET, so the default 12 covers Asia plus the London session
        # — the manipulation window — and leaves the whole US session to close in.
        _e = h1[h1.index.hour < early_hours].groupby("_day")
        _ew = _e.agg(eh=("h", "max"), el=("l", "min"))
        d = d.join(_ew, how="inner")
        _prev_rng = (d.h - d.l).shift(1)
        d = d.assign(pl=[placebo_level(o_, pr_, i)
                         for i, (o_, pr_) in enumerate(zip(d.o, _prev_rng))])
        d = d[d.pl.notna()]
        d["_yr"] = d.index.year
        d = d[d.h > d.l]
        # The ET hour at which the day's extreme printed. Index-aligned, NOT
        # positional: `d` gets filtered (zero-range days, the first day which has
        # no previous range for the placebo) while `gb` still spans every day, so
        # a positional assign silently misaligns — it raised a length error here
        # only because the counts happened to differ by one.
        _hi_i, _lo_i = gb["h"].idxmax(), gb["l"].idxmin()
        _hi_s = pd.Series(h1.loc[_hi_i, "_eth"].to_numpy(), index=_hi_i.index)
        _lo_s = pd.Series(h1.loc[_lo_i, "_eth"].to_numpy(), index=_lo_i.index)
        d = d.assign(hi_eth=_hi_s.reindex(d.index),
                     lo_eth=_lo_s.reindex(d.index))

        for split, yrs in (("IS", IS_YEARS), ("OOS", OOS_YEARS)):
            dd = d[d._yr.isin(yrs)]
            if not len(dd):
                continue
            rng = (dd.h - dd.l) / PIP
            body = (dd.c - dd.o).abs() / PIP
            cp = [close_position(o_, h_, l_, c_)
                  for o_, h_, l_, c_ in zip(dd.o, dd.h, dd.l, dd.c)]
            out["pairs"][(pair, split)] = {
                "days": len(dd), "rng": quantiles(list(rng)),
                "body_ratio": med([b / r for b, r in zip(body, rng) if r]),
                "close_pos": med(cp),
                "close_strong": pct(sum(1 for x in cp
                                        if x is not None and (x >= .8 or x <= .2)),
                                    len(cp)),
            }
            # ── when the extremes print ───────────────────────────────────────
            hh, ll = {}, {}
            for x in dd.hi_eth:
                hh[session_of(x)] = hh.get(session_of(x), 0) + 1
            for x in dd.lo_eth:
                ll[session_of(x)] = ll.get(session_of(x), 0) + 1
            out["hours"][(pair, split)] = {"n": len(dd), "high": hh, "low": ll}

            # ── the daily Judas against the 00:00 UTC open ────────────────────
            # the OPEN, and the same question asked of a meaningless level
            rows = [judas_side(o_, eh_, el_, c_, min_judas_pips)
                    for o_, eh_, el_, c_ in zip(dd.o, dd.eh, dd.el, dd.c)]
            ctl_rows = [judas_side(pl_, eh_, el_, c_, min_judas_pips)
                        for pl_, eh_, el_, c_ in zip(dd.pl, dd.eh, dd.el, dd.c)]
            j = {}
            for ran_v, label in ((-1, "ran_low"), (+1, "ran_high"), (2, "ran_both")):
                def _rate(rs, ref):
                    # "closed back through the reference" -- for the placebo the
                    # reference is the placebo level, not the open
                    sel = [(cl, c_, r_) for (rn, cl), c_, r_
                           in zip(rs, dd.c, ref) if rn == ran_v]
                    if not sel:
                        return None, 0
                    back = sum(1 for _, c_, r_ in sel
                               if (c_ > r_ if ran_v in (-1, 2) else c_ < r_))
                    return pct(back, len(sel)), len(sel)
                a, n = _rate(rows, dd.o)
                b, cn = _rate(ctl_rows, dd.pl)
                if n == 0:
                    continue
                j[label] = (n, a, b, (None if a is None or b is None else a - b), cn)
            out["judas"][(pair, split)] = j

        # ── what is LEFT, by ET hour (reverse cummax within the UTC day) ───────
        fwd_hi = h1.iloc[::-1].groupby("_day")["h"].cummax().iloc[::-1]
        fwd_lo = h1.iloc[::-1].groupby("_day")["l"].cummin().iloc[::-1]
        up_left = (fwd_hi - h1["c"]) / PIP
        dn_left = (h1["c"] - fwd_lo) / PIP
        fav = np.maximum(up_left, dn_left)
        tmp = pd.DataFrame({"eth": h1["_eth"], "yr": h1["_yr"],
                            "up": up_left, "dn": dn_left, "fav": fav})
        for split, yrs in (("IS", IS_YEARS), ("OOS", OOS_YEARS)):
            t2 = tmp[tmp.yr.isin(yrs)]
            if not len(t2):
                continue
            g = t2.groupby("eth")[["up", "dn", "fav"]].median()
            out["left"][(pair, split)] = g
            for hr, row in g.iterrows():
                left_lookup[(pair, split, int(hr))] = float(row["fav"])
        out["cover"][pair] = {s: int((d._yr.isin(y)).sum())
                              for s, y in (("IS", IS_YEARS), ("OOS", OOS_YEARS))}

    demand = _target_demand(left_lookup)
    _write(out, demand, min_judas_pips, early_hours)
    return 0


def _target_demand(left_lookup):
    """§5 — every real target as a fraction of what was typically left."""
    import pandas as pd
    if not os.path.exists(DUMP) or not left_lookup:
        return None
    df = pd.read_csv(DUMP)
    need = {"opened_at", "entry", "target", "pair", "pnl"}
    if not need.issubset(df.columns):
        return {"error": f"trades_dump.csv lacks {sorted(need - set(df.columns))}"}
    df = df.dropna(subset=["opened_at", "entry", "target", "pair", "pnl"])
    ts = pd.to_datetime(df["opened_at"], utc=True, errors="coerce")
    df = df[ts.notna()]
    ts = ts[ts.notna()]
    # NB no leading underscores: itertuples renames those to positional fields,
    # so r._eth silently becomes an AttributeError at the first row.
    df = df.assign(et_hour=ts.dt.tz_convert("America/New_York").dt.hour,
                   trade_year=ts.dt.year)
    rows = []
    for r in df.itertuples(index=False):
        split = "IS" if r.trade_year in IS_YEARS else "OOS"
        left = left_lookup.get((r.pair, split, int(r.et_hour)))
        if not left:
            continue
        dist = abs(float(r.target) - float(r.entry)) / PIP
        rows.append((split, demand_bucket(dist / left), float(r.pnl),
                     getattr(r, "target_rung", "")))
    if not rows:
        return {"error": "no trades matched a pair/split/hour with data"}
    agg = {}
    for split, bucket, pnl, rung in rows:
        for key in ((split, bucket), (split, bucket, str(rung))):
            a = agg.setdefault(key, {"n": 0, "w": 0, "gain": 0.0, "loss": 0.0})
            a["n"] += 1
            a["w"] += pnl > 0
            a["gain" if pnl > 0 else "loss"] += abs(pnl)
    return agg


def _pf(a):
    return float("inf") if a["loss"] == 0 else a["gain"] / a["loss"]


def _write(out, demand, min_judas_pips, early_hours):
    L = ["# What the DAILY timeframe does", "",
         "Measured on raw UTC daily candles built the way the engine builds them "
         "(HistData EST +5h). Session labels are New York time, as the killzones "
         "are.", ""]

    L += ["## 1. Shape — how far does a day travel?", "", "```",
          f"{'pair':<8} {'split':<5} {'days':>5} {'p25':>6} {'median':>7} "
          f"{'p75':>6} {'body/rng':>9} {'close pos':>10} {'closed >=80% or <=20%':>22}",
          "-" * 86]
    for (pair, split), s in sorted(out["pairs"].items()):
        q = s["rng"]
        f = lambda x, d=1: "—" if x is None else f"{x:.{d}f}"
        L.append(f"{pair:<8} {split:<5} {s['days']:>5} {f(q[0]):>6} "
                 f"{f(q[1]):>7} {f(q[2]):>6} {f(s['body_ratio'],2):>9} "
                 f"{f(s['close_pos'],2):>10} {f(s['close_strong']):>21}%")
    L += ["```", "",
          "`body/rng` is how much of the day's travel the candle keeps. A low "
          "number means the average day round-trips — it goes somewhere and comes "
          "back — which is the single most important fact for target selection.", ""]

    L += ["## 2. Timing — when do the daily HIGH and LOW print?", "",
          "Share of days whose extreme printed in each session (New York time). "
          "A flat profile would put ~33% in asia (9h), ~17% london (4h), "
          "~21% ny_am (5h), ~17% ny_pm (4h) purely on clock time, so compare "
          "against the HOURS column, not against each other.", "", "```",
          f"{'pair':<8} {'split':<5} {'n':>5}  " +
          "  ".join(f"{s:>10}" for s in ("asia(9h)", "london(4h)", "ny_am(5h)",
                                         "noon(1h)", "ny_pm(4h)")),
          "-" * 78]
    for (pair, split), s in sorted(out["hours"].items()):
        for which in ("high", "low"):
            d = s[which]
            cells = "  ".join(
                f"{pct(d.get(k, 0), s['n']) or 0:>9.1f}%"
                for k in ("asia", "london", "ny_am", "noon", "ny_pm"))
            L.append(f"{pair:<8} {split:<5} {s['n']:>5}  {cells}   <- {which}")
    L += ["```", ""]

    L += [f"## 3. The daily Judas — running the 00:00 UTC open", "",
          f"Did price trade at least **{min_judas_pips} pips** through the daily "
          f"open **within the first {early_hours} UTC hours** (00:00 UTC is 19:00 "
          f"ET, so that is Asia plus London), and then close the other way? `base` "
          f"and then close back through it? **`placebo` is the control** — the "
          f"identical question asked of a meaningless level (a quarter of the "
          f"previous day's range from the open, side alternating by date). The "
          f"unconditional close rate is NOT a valid control here: on a driftless "
          f"walk a day that ran the low early tends to STAY there, which reads "
          f"about −30pp with no institution involved. Only the lift over the "
          f"placebo says the OPEN is special. The early window is load-bearing "
          f"too — measured across the whole day, running a side merely selects "
          f"days that ENDED that way (−43pp on the same fixture).",
          "", "```",
          f"{'pair':<8} {'split':<5} {'case':<9} {'days':>6} {'back':>7} "
          f"{'placebo':>9} {'n':>6} {'lift':>8}",
          "-" * 68]
    for (pair, split), j in sorted(out["judas"].items()):
        for label in ("ran_low", "ran_high", "ran_both"):
            if label not in j:
                continue
            n, a, b, li, cn = j[label]
            f = lambda x: "—" if x is None else f"{x:.1f}"
            L.append(f"{pair:<8} {split:<5} {label:<9} {n:>6} {f(a):>6}% "
                     f"{f(b):>8}% {cn:>6} "
                     f"{('—' if li is None else f'{li:+.1f}pp'):>8}")
    L += ["```", "",
          "`ran_both` is the day that ran BOTH sides of its open — reported "
          "separately rather than folded into one side, because folding it is how "
          "a Judas rate gets inflated.", ""]

    L += ["## 4. What is LEFT — the mechanism P67 needs", "",
          "From the close of each hour, the median pips price still travels before "
          "the UTC day ends: `up`/`dn` in each direction and `fav` the better of "
          "the two. **A target further away than `fav` is asking for more than a "
          "typical day gives from that hour** — which would make the far rung's "
          "PF<1 a reachability problem, not a quality one.", ""]
    for (pair, split), g in sorted(out["left"].items()):
        L += [f"### {pair} {split}", "", "```", f"{'ET hr':>5} {'up':>7} {'dn':>7} "
              f"{'fav':>7}  session", "-" * 42]
        for hr, row in g.iterrows():
            L.append(f"{int(hr):>5} {row['up']:>7.1f} {row['dn']:>7.1f} "
                     f"{row['fav']:>7.1f}  {session_of(int(hr))}")
        L += ["```", ""]

    L += ["## 5. Target demand — every real target against what was left", ""]
    if demand is None:
        L += ["*`data/trades_dump.csv` not found — run "
              "`python run_backtest_histdata.py` first and re-run this study to "
              "get the section that connects the daily range to P67.*", ""]
    elif "error" in demand:
        L += [f"*skipped: {demand['error']}*", ""]
    else:
        L += ["Each trade's target distance divided by the median `fav` for its "
              "pair, split and entry hour. If demand explains outcomes better "
              "than the rung does, the lever is choosing targets against what is "
              "left — not removing trades, which has never survived the full run "
              "here (P8 −R31M, P10, P9's −20.15%).", "", "```",
              f"{'split':<5} {'demand':<10} {'trades':>7} {'wins':>5} {'WR%':>6} "
              f"{'PF':>7}", "-" * 44]
        for split in ("IS", "OOS"):
            for b in ("<=0.5x", "0.5-1.0x", "1.0-1.5x", ">1.5x"):
                a = demand.get((split, b))
                if not a:
                    continue
                L.append(f"{split:<5} {b:<10} {a['n']:>7} {a['w']:>5} "
                         f"{100*a['w']/a['n']:>5.1f}% {_pf(a):>7.2f}")
        L += ["```", "", "Demand x rung (does demand say anything the rung does "
              "not?):", "", "```",
              f"{'split':<5} {'demand':<10} {'rung':<6} {'trades':>7} {'WR%':>6} "
              f"{'PF':>7}", "-" * 46]
        for split in ("IS", "OOS"):
            for b in ("<=0.5x", "0.5-1.0x", "1.0-1.5x", ">1.5x"):
                for rung in ("near", "d3", "d30", "d60"):
                    a = demand.get((split, b, rung))
                    if not a:
                        continue
                    L.append(f"{split:<5} {b:<10} {rung:<6} {a['n']:>7} "
                             f"{100*a['w']/a['n']:>5.1f}% {_pf(a):>7.2f}")
        L += ["```", ""]

    L += ["---", "",
          "Measurement only; nothing ships. The result to act on, if there is "
          "one, is §4/§5: a target the day cannot reach is a target-SELECTION "
          "problem, and target selection is the one axis that has validated here."]

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
        print(f"\n  report unchanged — nothing to commit. Paste "
              f"{os.path.basename(path)} if Claude has not seen it.")
        return
    sha = (_git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown")
    if _git("commit", "-q", "-m", f"daily anatomy report (auto, on {sha})").returncode:
        print("\n  (commit failed — paste the report above)")
        return
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    p = _git("push", "origin", "HEAD")
    print(f"\n  RESULTS PUSHED — Claude can read data/{os.path.basename(path)}"
          if p.returncode == 0 else
          "\n  (auto-push failed — paste the report above)\n" + p.stderr[-300:])


# ──────────────────────────────── selftest ────────────────────────────────────

def selftest():
    assert session_of(4) == "london" and session_of(8) == "ny_am"
    assert session_of(12) == "noon" and session_of(14) == "ny_pm"
    assert session_of(20) == "asia" and session_of(1) == "asia"
    assert session_of(2) == "asia" and session_of(3) == "london"
    assert session_of(16) == "ny_pm" and session_of(17) == "asia"

    assert close_position(1.0, 1.1, 0.9, 1.1) == 1.0
    assert close_position(1.0, 1.1, 0.9, 0.9) == 0.0
    assert abs(close_position(1.0, 1.1, 0.9, 1.0) - 0.5) < 1e-9
    assert close_position(1.0, 1.0, 1.0, 1.0) is None      # zero-range day

    # ran 30 pips below the open and closed above it -> the Judas day.
    # NB the high must stay within the threshold of the open or this is a
    # both-sides day, which is exactly what the first version of this fixture got
    # wrong: a 50-pip upper wick made it ran_both, and the code was right.
    assert judas_side(1.1000, 1.1010, 1.0970, 1.1005, 20) == (-1, +1)
    # the early window is what the sweep is judged on, NOT the full day: a day
    # whose low came late must not register as having run the low early
    assert judas_side(1.1000, 1.1010, 1.0999, 1.0900, 20)[0] == 0
    # ran above only
    assert judas_side(1.1000, 1.1050, 1.0995, 1.1040, 20) == (+1, +1)
    # both sides run by more than the threshold -> ambiguous, never folded in
    assert judas_side(1.1000, 1.1050, 1.0950, 1.1040, 20)[0] == 2
    # neither side run far enough
    assert judas_side(1.1000, 1.1005, 1.0995, 1.1002, 20)[0] == 0
    # a doji closes flat
    assert judas_side(1.1000, 1.1050, 1.0950, 1.1000, 20)[1] == 0

    assert demand_bucket(0.4) == "<=0.5x" and demand_bucket(0.5) == "<=0.5x"
    assert demand_bucket(0.9) == "0.5-1.0x" and demand_bucket(1.4) == "1.0-1.5x"
    assert demand_bucket(3.0) == ">1.5x" and demand_bucket(None) == ""

    assert quantiles([]) == (None, None, None)
    assert quantiles([1, 2, 3, 4])[1] == 3
    assert med([5, 1, 3]) == 3 and med([None]) is None
    assert pct(1, 4) == 25.0 and pct(1, 0) is None

    # the placebo level is deterministic and alternates side
    assert abs(placebo_level(1.1000, 0.0080, 1) - 1.1020) < 1e-9
    assert abs(placebo_level(1.1000, 0.0080, 2) - 1.0980) < 1e-9

    a, b, li = lift_table(60, 100, 50, 100)
    assert (a, b, li) == (60.0, 50.0, 10.0), (a, b, li)
    assert lift_table(0, 0, 50, 100)[2] is None       # empty conditional
    print("selftest OK — session map, close position, judas sides incl. the "
          "both-sides day, demand buckets, quantiles, lift")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judas-pips", type=float, default=20.0,
                    help="how far through the open counts as running that side")
    ap.add_argument("--early-hours", type=int, default=12,
                    help="UTC hours from the daily open in which the sweep must "
                         "happen; the close it predicts comes after")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    global NO_PUSH
    NO_PUSH = a.no_push
    return run(a.judas_pips, a.early_hours)


if __name__ == "__main__":
    sys.exit(main())
