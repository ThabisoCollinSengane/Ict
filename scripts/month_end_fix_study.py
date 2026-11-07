#!/usr/bin/env python3
"""P80 — the MONTH-END London (WMR) fix: is the hedging flow predictable?

    python scripts/month_end_fix_study.py                    # real: HistData M1 + Yahoo equity
    python scripts/month_end_fix_study.py --null             # random walk: must read nothing
    python scripts/month_end_fix_study.py --null --plant 8   # planted effect: must be found
    python scripts/month_end_fix_study.py --selftest

THE CLAIM (Melvin & Prins, J. Financial Markets 2015): international equity
managers re-hedge their currency exposure at the LAST WMR fix of the month
(16:00 London). If a foreign market OUTPERFORMED US stocks over the month, US
holders now own more of that currency than they are hedged for and SELL it into
the fix; if US stocks outperformed, foreign holders sell DOLLARS. So the
direction is knowable before the fix from one number per month:

    s = foreign index return - S&P 500 return, month-to-date (local currency)
    predicted pair move into the fix = OPPOSITE sign of s

Pairs / indices: EURUSD <- Euro Stoxx 50, GBPUSD <- FTSE 100, NZDUSD <- NZX 50.

NO LOOKAHEAD: s uses index closes from the previous month-end to the day BEFORE
the last weekday (both known at the start of the fix day). Price "at" T is the
last 5-min close at or before T (same convention as fx_clock_study).

MEASURED
  pre  = pair move in the 4h before 16:00 London on the last weekday (the hedge)
  post = pair move in the 2h after (does it give it back?)
  FOLLOW = pre x predicted sign, in bp. > 0 = the prediction was right.
CONTROL: the identical calculation on a PLACEBO day two weeks earlier (same
signal method, same clock time). Month-end must beat its own placebo, or the
"effect" is just how equities and FX co-move at any 16:00.
GATE (same as P79): FOLLOW > 0 in BOTH halves (2010-17, 2018-25), pooled
t >= 2.5, AND month-end beats placebo in both halves.
"""
from __future__ import annotations

import argparse
import calendar
import math
import os
import subprocess
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import fx_clock_study as F                       # noqa: E402  (loader, px_at, mean_se)

REPORT = os.path.join(ROOT, "data", "month_end_fix_report.md")
PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
INDEX = {"US": "^GSPC", "EURUSD": "^STOXX50E", "GBPUSD": "^FTSE", "NZDUSD": "^NZ50"}
HALVES = {"2010-17": tuple(range(2010, 2018)), "2018-25": tuple(range(2018, 2026))}
PRE_H, POST_H = 4, 2
T_BAR = 2.5


# ───────────────────────────── pure logic ──────────────────────────────────────
def last_weekday(y: int, m: int) -> date:
    d = date(y, m, calendar.monthrange(y, m)[1])
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def placebo_day(month_end: date) -> date:
    """Two weeks before the month-end fix day, rolled back to a weekday."""
    d = month_end - timedelta(days=14)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def predicted_sign(s: float) -> int:
    """Foreign stocks outperformed (s > 0) -> foreign currency SOLD -> pair DOWN."""
    if s is None or s == 0 or math.isnan(s):
        return 0
    return -1 if s > 0 else 1


def follow_bp(pre_bp: float, sign: int):
    if sign == 0 or pre_bp is None or math.isnan(pre_bp):
        return None
    return sign * pre_bp


def close_on_or_before(series_dates, series_vals, d):
    import bisect
    i = bisect.bisect_right(series_dates, d) - 1
    return series_vals[i] if i >= 0 else None


def mtd_return(dates, vals, month_start_prev_end: date, cutoff: date):
    """ln(P(cutoff)/P(previous month-end)), using the last close on or before each."""
    a = close_on_or_before(dates, vals, month_start_prev_end)
    b = close_on_or_before(dates, vals, cutoff)
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return math.log(b / a)


def half_of(d: date):
    for k, yrs in HALVES.items():
        if d.year in yrs:
            return k
    return None


def verdict(a, b, t, beat_a, beat_b):
    if any(x is None or (isinstance(x, float) and math.isnan(x)) for x in (a, b, t)):
        return "no data"
    if a > 0 and b > 0 and t >= T_BAR and beat_a and beat_b:
        return "WORKS"
    if a < 0 and b < 0 and t <= -T_BAR:
        return "OPPOSITE WORKS"
    return "nothing"


# ───────────────────────────── data ────────────────────────────────────────────
def load_equity():
    import pandas as pd
    import yfinance as yf
    out = {}
    for k, t in INDEX.items():
        df = yf.download(t, start="2009-11-01", interval="1d", progress=False, auto_adjust=False)
        if df is None or df.empty:
            print(f"  WARN: no data for {t}")
            continue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        c = df["Close"].dropna()
        out[k] = ([x.date() for x in c.index], [float(v) for v in c.to_numpy()])
    return out


def load_fx():
    F.IS_YEARS = HALVES["2010-17"]
    F.OOS_YEARS = HALVES["2018-25"]
    out = {}
    for p in PAIRS:
        c = F._load_closes(p)
        if c is not None and len(c):
            out[p] = c
    return out


# ───────────────────────────── study ───────────────────────────────────────────
def observations(fx, eq, placebo=False):
    import pandas as pd
    rows = []
    if "US" not in eq:
        return rows
    us_d, us_v = eq["US"]
    for y in range(2010, 2026):
        for m in range(1, 13):
            me = last_weekday(y, m)
            day = placebo_day(me) if placebo else me
            prev_end = date(y, m, 1) - timedelta(days=1)
            cutoff = day - timedelta(days=1)
            r_us = mtd_return(us_d, us_v, prev_end, cutoff)
            fix = F.fix_utc(day, "Europe/London", 16, 0)
            for pair in PAIRS:
                if pair not in fx or pair not in eq:
                    continue
                fd, fv = eq[pair]
                r_f = mtd_return(fd, fv, prev_end, cutoff)
                if r_f is None or r_us is None:
                    continue
                s = r_f - r_us
                sign = predicted_sign(s)
                px = F._px_at(fx[pair], [fix - pd.Timedelta(hours=PRE_H), fix,
                                         fix + pd.Timedelta(hours=POST_H)])
                a, b, c = (float(v) for v in px)
                if any(math.isnan(v) for v in (a, b, c)):
                    continue
                pre = math.log(b / a) * 1e4
                post = math.log(c / b) * 1e4
                rows.append({"day": day, "half": half_of(day), "pair": pair, "s": s,
                             "sign": sign, "pre": pre, "post": post,
                             "follow": follow_bp(pre, sign),
                             "post_follow": follow_bp(post, sign)})
    return rows


def _stats(xs):
    xs = [x for x in xs if x is not None]
    m, se, n = F.mean_se(xs)
    t = m / se if se and se == se and se > 0 else float("nan")
    hit = 100.0 * sum(1 for x in xs if x > 0) / n if n else float("nan")
    return m, t, n, hit


def _f(x, nd=2):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.{nd}f}"


def build_report(fx, eq, label):
    me = observations(fx, eq, placebo=False)
    pl = observations(fx, eq, placebo=True)
    cov = ", ".join(f"{p} {s.index.min():%Y-%m-%d}→{s.index.max():%Y-%m-%d}"
                    for p, s in fx.items())
    L = [f"# P80 — month-end London (WMR) fix hedging flow ({label})", "",
         f"_FX: {cov}. Equity indices: {', '.join(k + '=' + INDEX[k] for k in INDEX if k in eq)}. "
         f"Month-end observations {len(me)}, placebo {len(pl)}._", "",
         "Prediction made BEFORE the fix: foreign stocks beat the S&P 500 this month → "
         "that currency is sold into the 16:00 London fix (pair DOWN); S&P won → dollar "
         "sold (pair UP). FOLLOW = pair move in the 4h before the fix in the predicted "
         "direction (bp). Placebo = same method two weeks earlier.", "",
         "## The verdict — all three pairs pooled", "",
         "| half | month-ends | FOLLOW bp (t) | hit % | placebo FOLLOW bp (t) | beats placebo | 2h after the fix bp |",
         "|---|---|---|---|---|---|---|"]
    per = {}
    for h in HALVES:
        a = [r["follow"] for r in me if r["half"] == h]
        b = [r["follow"] for r in pl if r["half"] == h]
        post = [r["post_follow"] for r in me if r["half"] == h]
        ma, ta, na, ha = _stats(a)
        mb, tb, nb, hb = _stats(b)
        mp, tp, _, _ = _stats(post)
        per[h] = (ma, (ma == ma and mb == mb and ma > mb))
        L.append(f"| {h} | {na} | {_f(ma)} ({_f(ta,1)}) | {ha:.0f}% | {_f(mb)} ({_f(tb,1)}) | "
                 f"{'yes' if per[h][1] else 'no'} | {_f(mp)} ({_f(tp,1)}) |")
    ma, ta, na, ha = _stats([r["follow"] for r in me])
    v = verdict(per["2010-17"][0], per["2018-25"][0], ta, per["2010-17"][1], per["2018-25"][1])
    L += ["", f"**VERDICT: {v}** — pooled FOLLOW {_f(ma)} bp, t {_f(ta,1)}, n {na}, "
              f"hit {ha:.0f}%. Gate: both halves > 0, pooled t ≥ {T_BAR}, beats placebo both halves.", "",
          "_Note: pair-months share the dollar side, so the three pairs are not fully "
          "independent — the pooled t is somewhat optimistic. Read the per-pair table._", "",
          "## Per pair", "",
          "| pair | half | n | FOLLOW bp (t) | hit % | corr(signal, move) |", "|---|---|---|---|---|---|"]
    for pair in PAIRS:
        for h in HALVES:
            rows = [r for r in me if r["pair"] == pair and r["half"] == h]
            m, t, n, hit = _stats([r["follow"] for r in rows])
            from fundamentals_scorecard import corr_t
            c, _, _ = corr_t([r["s"] for r in rows], [r["pre"] for r in rows])
            L.append(f"| {pair} | {h} | {n} | {_f(m)} ({_f(t,1)}) | {hit:.0f}% | {_f(c,2)} |")
    L += ["", "_corr(signal, move) should be NEGATIVE if the hedging story holds (foreign "
          "outperformance → that currency sold)._", "",
          "## Big months only (|signal| in the top third)", "",
          "Hedging needs scale: a month where stocks barely diverged leaves little to "
          "re-hedge. If the mechanism is real, the big months should carry it.", "",
          "| half | n | FOLLOW bp (t) | hit % |", "|---|---|---|---|"]
    allabs = sorted(abs(r["s"]) for r in me)
    cut = allabs[int(len(allabs) * 2 / 3)] if allabs else 0
    for h in HALVES:
        m, t, n, hit = _stats([r["follow"] for r in me if r["half"] == h and abs(r["s"]) >= cut])
        L.append(f"| {h} | {n} | {_f(m)} ({_f(t,1)}) | {hit:.0f}% |")
    L += ["", "_Context: the WMR window widened from 1 to 5 minutes in Feb 2015, inside the "
          "2010-17 half; the daily fix reversal (P78) faded after 2018._", ""]
    return "\n".join(L) + "\n", v


# ───────────────────────────── null / plant ────────────────────────────────────
def _synthetic(plant_bp: float, seed: int = 5):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-04", "2025-12-31", freq="15min", tz="UTC")
    idx = idx[idx.dayofweek < 5]
    days = pd.bdate_range("2009-11-02", "2025-12-31")
    eq = {k: ([d.date() for d in days],
              list(np.exp(np.cumsum(rng.normal(0, 0.01, len(days)))) * 100)) for k in INDEX}
    fx = {}
    for p in PAIRS:
        steps = rng.normal(0, 3.0, len(idx))
        if plant_bp:
            us_d, us_v = eq["US"]
            fd, fv = eq[p]
            pos = pd.Series(np.arange(len(idx)), index=idx)
            for y in range(2010, 2026):
                for m in range(1, 13):
                    me = last_weekday(y, m)
                    prev_end = date(y, m, 1) - timedelta(days=1)
                    r_us = mtd_return(us_d, us_v, prev_end, me - timedelta(days=1))
                    r_f = mtd_return(fd, fv, prev_end, me - timedelta(days=1))
                    if r_us is None or r_f is None:
                        continue
                    sg = predicted_sign(r_f - r_us)
                    fix = F.fix_utc(me, "Europe/London", 16, 0)
                    w = pos[(pos.index > fix - pd.Timedelta(hours=PRE_H)) & (pos.index <= fix)].values
                    if len(w):
                        steps[w] += sg * plant_bp / len(w)
        fx[p] = pd.Series(np.exp(np.cumsum(steps) / 1e4), index=idx)
    return fx, eq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--plant", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.null:
        fx, eq = _synthetic(a.plant, a.seed)
        text, _ = build_report(fx, eq, f"RANDOM-WALK NULL, planted {a.plant:g}bp" if a.plant else "RANDOM-WALK NULL")
        print(text)
        return 0
    fx = load_fx()
    eq = load_equity()
    if not fx or "US" not in eq:
        print("missing data: fx pairs", list(fx), "equity", list(eq))
        return 1
    text, _ = build_report(fx, eq, "real data, 2010-2025")
    print(text)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w", encoding="utf-8").write(text)
    return 0


def selftest():
    assert last_weekday(2026, 10) == date(2026, 10, 30)          # Fri
    assert last_weekday(2026, 5) == date(2026, 5, 29)            # 30/31 weekend
    assert last_weekday(2025, 8) == date(2025, 8, 29)
    assert placebo_day(date(2026, 10, 30)) == date(2026, 10, 16)
    assert placebo_day(date(2026, 11, 30)).weekday() < 5
    assert predicted_sign(0.02) == -1 and predicted_sign(-0.01) == 1 and predicted_sign(0.0) == 0
    assert follow_bp(-5.0, -1) == 5.0 and follow_bp(5.0, -1) == -5.0 and follow_bp(3.0, 0) is None
    ds = [date(2026, 1, 2), date(2026, 1, 5), date(2026, 1, 30)]
    vs = [100.0, 110.0, 121.0]
    assert close_on_or_before(ds, vs, date(2026, 1, 3)) == 100.0
    assert close_on_or_before(ds, vs, date(2025, 12, 31)) is None
    r = mtd_return(ds, vs, date(2026, 1, 2), date(2026, 1, 29))
    assert abs(r - math.log(110 / 100)) < 1e-12                  # uses 1/5, not 1/30
    assert half_of(date(2015, 3, 31)) == "2010-17" and half_of(date(2020, 1, 31)) == "2018-25"
    assert verdict(1, 1, 3, True, True) == "WORKS"
    assert verdict(1, 1, 3, True, False) == "nothing"           # must beat placebo
    assert verdict(1, 1, 2.0, True, True) == "nothing"           # t bar 2.5
    assert verdict(-1, -1, -3, False, False) == "OPPOSITE WORKS"
    import pandas as pd
    t = F.fix_utc(date(2026, 7, 31), "Europe/London", 16, 0)
    assert t.tz_convert("UTC").strftime("%H:%M") == "15:00"     # BST
    t = F.fix_utc(date(2026, 1, 30), "Europe/London", 16, 0)
    assert t.tz_convert("UTC").strftime("%H:%M") == "16:00"     # GMT
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
