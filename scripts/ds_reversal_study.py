"""P112c — how good is the Daily Sweep SFP at PICKING THE REVERSAL? (pure price)

The trader's question (2026-10-19): forget the exit and the win rate; when the 1H candle
sweeps a marked level and closes back inside (the Swing Failure Pattern / Judas swing),
does price actually turn there more often than it would anyway?

Every event is measured the same way, independent of any target:
  entry  = the candle's close, stop = beyond its wick (+1 pip / point buffer), R = the distance.
  From the next M1 bar to 16:00 ET the same day:
    fav    = best move our way BEFORE price reclaims the wick (the premise fails), in R
    held   = the wick was never reclaimed by 16:00 ET
    hit1/2/3 = fav reached 1R / 2R / 3R before the wick was reclaimed

The CONTROL is what makes it a test (P65/P68b/P77 lesson). Every other completed 1H candle
in the same window (07:00-11:00 ET opens, so it closes 08:00-12:00 ET) that is NOT an SFP,
entered at its close with the stop beyond its own extreme — the same construction with no
sweep. Because a small R inflates every R-rate, SFP and control are compared WITHIN
buckets of R / daily ATR (edges = the SFP quintiles), and the lift is the SFP-weighted
average of the per-bucket differences ("matched lift").

Groups (the bias is the engine's d2s: yesterday vs the day before, daily Ep-12 structure
not opposed):
  with    — SFP in the bias direction (what the model trades)   vs control in the bias direction
  against — SFP against the bias                                  vs control against the bias
  nobias  — SFP on a day with no bias (both directions)            vs control, both directions
  all     — every SFP                                              vs every control candle/direction

Levels mirror backtest._ds_levels: PDH/PDL (previous completed UTC day), prior-day H1 fractal
swings, today's Asia (20:00-03:00 ET) and London (03:00-07:00 ET) high/low; fresh = nothing
traded through it between when it formed and the SFP candle; deepest swept level wins; first
SFP per instrument / day / direction. COMPLETED bars only for bias, levels and ATR.

  python scripts/ds_reversal_study.py                    # real data in data/histdata
  python scripts/ds_reversal_study.py --null             # random walk through the same code
  python scripts/ds_reversal_study.py --selftest
"""
import argparse
import math
import os
import sys
from collections import namedtuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "data", "histdata")
SYMS = ["SPXUSD", "NSXUSD", "XAUUSD", "EURUSD", "GBPUSD"]
YEARS = [2022, 2023, 2024, 2025, 2026]
SPLIT = {2022: "IS", 2023: "IS", 2024: "OOS", 2025: "OOS", 2026: "2026"}
HITS = ("hit1", "hit2", "hit3", "held")
Bar = namedtuple("Bar", "Open High Low Close")


# ─────────────────────────────── pure logic ───────────────────────────────

def d2(y, p):
    """Mirror of Backtester._ds_d2."""
    if y.High > p.High and y.Low > p.Low:
        return 1
    if y.High < p.High and y.Low < p.Low:
        return -1
    if y.High > p.High and y.Low < p.Low:
        return 1 if y.Close > y.Open else (-1 if y.Close < y.Open else 0)
    return 0


def sfp_side(bar, levels, side, min_pierce=0.0):
    """levels: [(price, kind)] already filtered for freshness. Returns (level, kind) of the
    deepest level the candle swept and closed back inside, or None. side 'low' -> long."""
    best = None
    for lvl, kind in levels:
        if side == "low":
            ok = (lvl - bar.Low) > min_pierce and bar.Close > lvl
            if ok and (best is None or lvl < best[0]):
                best = (lvl, kind)
        else:
            ok = (bar.High - lvl) > min_pierce and bar.Close < lvl
            if ok and (best is None or lvl > best[0]):
                best = (lvl, kind)
    return best


def outcome(direction, entry, stop, hi, lo):
    """Walk M1 highs/lows (numpy arrays from the bar after the candle to the horizon).
    Returns (favR, held). fav is measured on bars BEFORE the one that reclaims the wick."""
    import numpy as np
    R = abs(entry - stop)
    if R <= 0 or len(hi) == 0:
        return None
    if direction > 0:
        fail = np.nonzero(lo <= stop)[0]
        k = fail[0] if len(fail) else len(lo)
        fav = (hi[:k].max() - entry) if k > 0 else 0.0
    else:
        fail = np.nonzero(hi >= stop)[0]
        k = fail[0] if len(fail) else len(hi)
        fav = (entry - lo[:k].min()) if k > 0 else 0.0
    return max(fav, 0.0) / R, len(fail) == 0


def rates(rows):
    n = len(rows)
    if not n:
        return None
    out = {"n": n}
    for h in HITS:
        out[h] = 100.0 * sum(1 for r in rows if r[h]) / n
    fs = sorted(r["favR"] for r in rows)
    out["medfav"] = fs[n // 2]
    return out


def matched_lift(sfp, ctl, key, edges):
    """SFP-weighted average of (SFP rate - control rate) within R/ATR buckets, + its SE."""
    num = var = tot = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        s = [r for r in sfp if lo <= r["ratr"] < hi]
        c = [r for r in ctl if lo <= r["ratr"] < hi]
        if len(s) < 3 or len(c) < 10:
            continue
        ps = sum(1 for r in s if r[key]) / len(s)
        pc = sum(1 for r in c if r[key]) / len(c)
        w = len(s)
        num += w * (ps - pc)
        var += w * w * (ps * (1 - ps) / len(s) + pc * (1 - pc) / len(c))
        tot += w
    if not tot:
        return None, None
    return 100.0 * num / tot, 100.0 * math.sqrt(var) / tot


def quantile_edges(vals, q=5):
    v = sorted(vals)
    if len(v) < q * 3:
        return [0.0, float("inf")]
    e = [0.0] + [v[int(len(v) * i / q)] for i in range(1, q)] + [float("inf")]
    return sorted(set(e))


# ─────────────────────────────── data ───────────────────────────────

def _pip(sym):
    import config
    if sym == "XAUUSD":
        return config.GOLD_PIP
    if sym in ("SPXUSD", "NSXUSD"):
        return config.INDEX_PIP
    return 0.0001


def _load_utc(sym):
    import pandas as pd
    frames = []
    for y in YEARS:
        p = os.path.join(DATA, f"{sym}_{y}.csv")
        if os.path.exists(p):
            frames.append(pd.read_csv(p, sep=";", header=None,
                                      names=["dt", "o", "h", "l", "c", "v"]))
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    df = df.drop_duplicates("dt").sort_values("dt").set_index("dt")
    df.index = (df.index + pd.Timedelta(hours=5)).tz_localize("UTC")   # HistData = fixed EST
    return df[["o", "h", "l", "c"]]


def _null_frame(seed, days=520, start="2022-01-03"):
    """Random-walk M1, weekdays only, ~1.10 price, so the whole pipeline runs on no-edge data."""
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=days * 1440, freq="1min", tz="UTC")
    idx = idx[idx.dayofweek < 5]
    steps = rng.normal(0, 0.00006, len(idx))
    c = 1.10 + np.cumsum(steps)
    o = np.r_[c[0], c[:-1]]
    wig = np.abs(rng.normal(0, 0.00003, len(idx)))
    h = np.maximum(o, c) + wig
    l = np.minimum(o, c) - wig
    return pd.DataFrame({"o": o, "h": h, "l": l, "c": c}, index=idx)


# ─────────────────────────────── study ───────────────────────────────

def events_for(sym, df, pip):
    import numpy as np
    import pandas as pd
    from ict import market_structure as ms
    ny = "America/New_York"
    agg = {"o": "first", "h": "max", "l": "min", "c": "last"}
    h1 = df.resample("60min", label="left", closed="left").agg(agg).dropna()
    cnt = df["c"].resample("1D").count()
    d1 = df.resample("1D").agg(agg).dropna()
    d1 = d1[cnt.reindex(d1.index).fillna(0) >= 120]           # drop Sunday stubs
    tr = pd.concat([d1.h - d1.l, (d1.h - d1.c.shift()).abs(), (d1.l - d1.c.shift()).abs()],
                   axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    dbars = [Bar(r.o, r.h, r.l, r.c) for r in d1.itertuples()]
    dpos = {ts: i for i, ts in enumerate(d1.index)}
    h1_t = h1.index
    h1_h, h1_l = h1.h.values, h1.l.values
    m1_t = df.index
    m1_h, m1_l = df.h.values, df.l.values
    buf = pip * 1.0
    et_open = h1_t.tz_convert(ny)
    mins = et_open.hour * 60 + et_open.minute
    cand = np.nonzero((mins >= 7 * 60) & (mins <= 11 * 60) & (et_open.dayofweek < 5))[0]
    out_sfp, out_ctl = [], []
    seen = set()
    bias_cache = {}
    for i in cand:
        s_open = h1_t[i]
        s_close = s_open + pd.Timedelta(hours=1)
        if i + 1 < len(h1_t) and h1_t[i + 1] < s_close:
            continue
        today0 = s_open.normalize()                            # UTC day (the forming daily bar)
        di = dpos.get(today0)
        if di is None or di < 21:
            continue
        a_ = atr.iloc[di - 1]
        if not a_ > 0:
            continue
        if di not in bias_cache:
            db = dbars[di - 80 if di >= 80 else 0: di]          # completed days only
            b = d2(db[-1], db[-2])
            if b != 0:
                big = ms.structure_direction(ms.classify(db)) if len(db) >= 20 else 0
                b = 0 if big == -b else b
            bias_cache[di] = b
        bias = bias_cache[di]
        prev0 = d1.index[di - 1]
        pdb = dbars[di - 1]
        etday = s_open.tz_convert(ny).normalize()
        lv = {"low": [(pdb.Low, today0, "pd")], "high": [(pdb.High, today0, "pd")]}
        a, b_ = h1_t.searchsorted(prev0), h1_t.searchsorted(today0)
        for j in range(a + 1, b_ - 1):
            if h1_l[j] < h1_l[j - 1] and h1_l[j] < h1_l[j + 1]:
                lv["low"].append((h1_l[j], today0, "pdsw"))
            if h1_h[j] > h1_h[j - 1] and h1_h[j] > h1_h[j + 1]:
                lv["high"].append((h1_h[j], today0, "pdsw"))
        for name, s, e in (("asia", etday - pd.Timedelta(hours=4), etday + pd.Timedelta(hours=3)),
                           ("london", etday + pd.Timedelta(hours=3), etday + pd.Timedelta(hours=7))):
            su, eu = s.tz_convert("UTC"), e.tz_convert("UTC")
            if eu > s_close:
                continue
            i0, i1 = h1_t.searchsorted(su), h1_t.searchsorted(eu)
            if i1 > i0:
                lv["low"].append((h1_l[i0:i1].min(), eu, name))
                lv["high"].append((h1_h[i0:i1].max(), eu, name))
        bar = Bar(h1.o.iat[i], h1_h[i], h1_l[i], h1.c.iat[i])
        fresh = {}
        for side in ("low", "high"):
            keep = []
            for lvl, vfrom, kind in lv[side]:
                x0, x1 = h1_t.searchsorted(vfrom), i
                if x1 > x0 and ((side == "low" and h1_l[x0:x1].min() < lvl)
                                or (side == "high" and h1_h[x0:x1].max() > lvl)):
                    continue
                keep.append((lvl, kind))
            fresh[side] = keep
        m0 = m1_t.searchsorted(s_close)
        m1 = m1_t.searchsorted((etday + pd.Timedelta(hours=16)).tz_convert("UTC"))
        if m1 <= m0:
            continue
        hi, lo = m1_h[m0:m1], m1_l[m0:m1]
        yr = s_open.year
        base = {"sym": sym, "split": SPLIT.get(yr, str(yr)), "bias": bias,
                "hour": int(s_close.tz_convert(ny).hour)}
        is_sfp = False
        for side, d in (("low", 1), ("high", -1)):
            hit = sfp_side(bar, fresh[side], side)
            if hit is None:
                continue
            is_sfp = True
            key = (sym, today0, d)
            if key in seen:
                continue
            seen.add(key)
            stop = (bar.Low - buf) if d > 0 else (bar.High + buf)
            res = outcome(d, bar.Close, stop, hi, lo)
            if res is None:
                continue
            fav, held = res
            out_sfp.append(dict(base, dir=d, kind=hit[1], favR=fav, held=held,
                                hit1=fav >= 1, hit2=fav >= 2, hit3=fav >= 3,
                                ratr=abs(bar.Close - stop) / a_))
        if is_sfp:
            continue
        for d in (1, -1):
            stop = (bar.Low - buf) if d > 0 else (bar.High + buf)
            res = outcome(d, bar.Close, stop, hi, lo)
            if res is None:
                continue
            fav, held = res
            out_ctl.append(dict(base, dir=d, kind="ctl", favR=fav, held=held,
                                hit1=fav >= 1, hit2=fav >= 2, hit3=fav >= 3,
                                ratr=abs(bar.Close - stop) / a_))
    return out_sfp, out_ctl


def group(rows, g):
    if g == "with":
        return [r for r in rows if r["bias"] != 0 and r["dir"] == r["bias"]]
    if g == "against":
        return [r for r in rows if r["bias"] != 0 and r["dir"] == -r["bias"]]
    if g == "nobias":
        return [r for r in rows if r["bias"] == 0]
    return list(rows)


def report(sfp, ctl, title):
    L = [f"# {title}", ""]
    L.append("Every number: entry at the candle close, stop beyond its wick. `hitX` = price went X R "
             "our way BEFORE reclaiming the wick; `held` = the wick was never reclaimed by 16:00 ET. "
             "**lift** = SFP minus an ordinary candle with the same stop size (matched on R/ATR), "
             "in percentage points, ± one standard error. Read the lift, not the raw rate.")
    L.append("")
    splits = [s for s in ("IS", "OOS", "2026") if any(r["split"] == s for r in sfp)]
    edges = quantile_edges([r["ratr"] for r in sfp])
    syms = sorted({r["sym"] for r in sfp})

    def block(name, S, C):
        L.append(f"## {name}")
        L.append("")
        L.append("| group | split | SFP n | SFP hit1 / hit2 / held | ctrl n | ctrl hit1 / hit2 / held "
                 "| **lift hit1** | **lift hit2** | lift held | SFP med fav R |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for g in ("with", "against", "nobias", "all"):
            for sp in splits:
                s = group([r for r in S if r["split"] == sp], g)
                c = group([r for r in C if r["split"] == sp], g)
                rs, rc = rates(s), rates(c)
                if not rs or not rc:
                    continue
                cells = []
                for k in ("hit1", "hit2", "held"):
                    m, se = matched_lift(s, c, k, edges)
                    cells.append("—" if m is None else f"{m:+.1f} ± {se:.1f}")
                L.append(f"| {g} | {sp} | {rs['n']} | {rs['hit1']:.0f} / {rs['hit2']:.0f} / "
                         f"{rs['held']:.0f}% | {rc['n']} | {rc['hit1']:.0f} / {rc['hit2']:.0f} / "
                         f"{rc['held']:.0f}% | {cells[0]} | {cells[1]} | {cells[2]} | "
                         f"{rs['medfav']:.2f} |")
        L.append("")

    block("All instruments pooled", sfp, ctl)
    for sym in syms:
        block(sym, [r for r in sfp if r["sym"] == sym], [r for r in ctl if r["sym"] == sym])

    L.append("## SFP in the bias direction, by swept level (lift vs control in the bias direction)")
    L.append("")
    L.append("| level | split | n | hit1 | hit2 | held | lift hit1 | lift hit2 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for kind in ("pd", "pdsw", "asia", "london"):
        for sp in splits:
            s = [r for r in group(sfp, "with") if r["kind"] == kind and r["split"] == sp]
            c = group([r for r in ctl if r["split"] == sp], "with")
            rs = rates(s)
            if not rs:
                continue
            m1, e1 = matched_lift(s, c, "hit1", edges)
            m2, e2 = matched_lift(s, c, "hit2", edges)
            f = lambda m, e: "—" if m is None else f"{m:+.1f} ± {e:.1f}"
            L.append(f"| {kind} | {sp} | {rs['n']} | {rs['hit1']:.0f}% | {rs['hit2']:.0f}% | "
                     f"{rs['held']:.0f}% | {f(m1, e1)} | {f(m2, e2)} |")
    L.append("")
    L.append("## SFP in the bias direction, by SFP close hour (ET), all splits pooled")
    L.append("")
    L.append("| close hour | n | hit1 | hit2 | held | lift hit1 |")
    L.append("|---|---|---|---|---|---|")
    for hr in range(8, 13):
        s = [r for r in group(sfp, "with") if r["hour"] == hr]
        c = [r for r in group(ctl, "with") if r["hour"] == hr]
        rs = rates(s)
        if not rs:
            continue
        m, e = matched_lift(s, c, "hit1", edges)
        L.append(f"| {hr}:00 | {rs['n']} | {rs['hit1']:.0f}% | {rs['hit2']:.0f}% | {rs['held']:.0f}% | "
                 + ("—" if m is None else f"{m:+.1f} ± {e:.1f}") + " |")
    L.append("")
    L.append(f"R/ATR bucket edges (SFP quintiles): {', '.join(f'{x:.3f}' for x in edges[1:-1])}")
    return "\n".join(L)


def selftest():
    import numpy as np
    y, p = Bar(1, 3, 1.5, 2), Bar(1, 2, 1, 1.5)
    assert d2(y, p) == 1 and d2(Bar(0, 1, 0, 0.5), p) == -1
    assert d2(Bar(1, 3, 0.5, 2), p) == 1 and d2(Bar(2, 3, 0.5, 1), p) == -1
    assert d2(Bar(1, 1.8, 1.2, 1.5), p) == 0
    b = Bar(10, 11, 8, 10.5)
    assert sfp_side(b, [(9, "a"), (8.5, "b"), (7, "c")], "low") == (8.5, "b")
    assert sfp_side(b, [(10.8, "a")], "low") is None                  # close not back above
    assert sfp_side(b, [(10.6, "h")], "high") == (10.6, "h")
    assert sfp_side(Bar(10, 11, 8, 10.9), [(10.6, "h")], "high") is None
    hi = np.array([11, 12, 13, 12.0]); lo = np.array([10, 10.5, 9, 8.0])
    f, held = outcome(1, 10.0, 9.5, hi, lo)                             # fails on bar 2
    assert abs(f - 4.0) < 1e-9 and not held                             # fav (12-10)/0.5 before bar 2
    rows_s = [dict(ratr=0.1, hit1=True)] * 10 + [dict(ratr=0.3, hit1=False)] * 10
    rows_c = [dict(ratr=0.1, hit1=False)] * 20 + [dict(ratr=0.3, hit1=False)] * 20
    m, se = matched_lift(rows_s, rows_c, "hit1", [0, 0.2, 1])
    assert abs(m - 50.0) < 1e-9, m
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--syms", nargs="+", default=SYMS)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "ds_reversal_report.md"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    sfp, ctl = [], []
    if a.null:
        for seed in (1, 2, 3):
            s, c = events_for(f"NULL{seed}", _null_frame(seed), 0.0001)
            sfp += s
            ctl += c
        title = "P112c NULL (random walk) — every lift should read ~0"
    else:
        for sym in a.syms:
            df = _load_utc(sym)
            if df is None:
                print(f"{sym}: no data, skipped")
                continue
            s, c = events_for(sym, df, _pip(sym))
            print(f"{sym}: M1 {len(df):,}  SFP {len(s)}  control {len(c)}")
            sfp += s
            ctl += c
        title = "P112c — does the Daily Sweep SFP pick the reversal? (pure price, H1 SFP, 08:00-12:00 ET)"
    if not sfp:
        print("no SFP events")
        return
    txt = report(sfp, ctl, title)
    print(txt)
    with open(a.out, "w") as f:
        f.write(txt + "\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
