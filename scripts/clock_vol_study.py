"""P127 — volatility by clock time (seas20): a bracket and a fade that do not pick a side.

Spec: research/specs/P127_clock_volatility.md (APPROVED 2026-11-07: 16 cells, hourly 00:00-12:00 ET,
EURUSD / GBPUSD / NZDUSD only). Pure price, HistData M1 (bid), completed bars only.

Every weekday, every hour on the hour t = 00:00..12:00 ET, per pair:
  seas20  mean realised range (high - low) of [c, c+4h) at the same ET clock c on the 20 previous
          weekdays that have data (day d itself never read: rolling mean shifted by one day)
  ATR16   mean true range of the last 16 COMPLETED M15 bars (bar containing t never read)
  ratio   seas20 / ATR16
  range   high / low of the last 8 completed M15 bars = the M1 bars in [t-2h, t)
Terciles of seas20, ratio and ATR16 are cut per pair on IS 2022-23 only, applied unchanged later.

Strategy A (top tercile): OCO buy-stop at range high + k*seas20 / sell-stop at range low - k*seas20,
  live 60 min; stop = range midpoint; E1 = 2R target + time exit t+4h, E2 = time exit only.
Strategy B (bottom tercile): OCO limit sell at range high / limit buy at range low, live 60 min,
  filled only when price trades THROUGH the limit by 0.5 pip; stop = k*seas20 beyond the edge;
  E1 = target range midpoint, E2 = target opposite edge; time exit t+4h.
Costs (fixed): 1.0 pip spread per round trip (1.5 reported), 0.5 pip slip on every STOP-order fill
  (A entry, every protective stop). Inside one M1 bar the stop is checked before the target; a stop
  on the fill bar counts; a target is not taken on the fill bar; both OCO orders in one bar = filled
  long and stopped (worst case).
k in (0.10, 0.25). Cells: {seas20, ratio} tercile x {A, B} x k x {E1, E2} = 16.

Controls: all-slots (tercile minus the other two terciles), opposite tercile, ATR-only (terciles
on ATR16, offset/stop k' x ATR16 with k' set on IS so the median offset in pips matches), and two
random-walk nulls with the real clock-time volatility shape (--null; B adds bid-quote noise).
Standard errors clustered by ET day, pooled across the three pairs.

  python scripts/clock_vol_study.py --selftest
  python scripts/clock_vol_study.py --null           # writes data/clock_vol_null.md + .json
  python scripts/clock_vol_study.py --power          # planted follow-through / reversion
  python scripts/clock_vol_study.py                  # real run (runs the nulls first if missing)
"""
import argparse
import json
import math
import os
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dollar_read_study as drs   # noqa: E402  (load_utc: +5h EST->UTC, cl_mean: day-clustered SE)

NY = "America/New_York"
PIP = 0.0001
PAIRS = ["EURUSD", "GBPUSD", "NZDUSD"]
HOURS = list(range(0, 13))          # decisions 00:00 .. 12:00 ET
PRE = 120                           # range = last 2h (8 completed M15 bars)
HOLD = 240                          # time exit t + 4h
LIVE = 60                           # pending orders live 60 min
SEAS_N = 20
KS = (0.10, 0.25)
SPREAD = 1.0
SPREAD_SENS = 1.5
SLIP = 0.5
TT = 0.5                            # limit trade-through
MIN_PRE, MIN_WIN, MIN_LIVE = 90, 180, 40
BIG = 10 ** 6
NULL_DAYS = 1741                    # 2022-01-03 .. 2026-10-09
NULL_BASE = {"EURUSD": 1.08, "GBPUSD": 1.25, "NZDUSD": 0.60}
OUT = os.path.join(ROOT, "data", "clock_vol_report.md")
NULL_OUT = os.path.join(ROOT, "data", "clock_vol_null.md")
NULL_JSON = os.path.join(ROOT, "data", "clock_vol_null.json")
SPLITS = ("IS", "OOS", "2026")
EXITS = {"A": ("E1 2R", "E2 time"), "B": ("E1 mid", "E2 edge")}


def split_of(y):
    return "IS" if y <= 2023 else ("OOS" if y <= 2025 else "2026")


# ─────────────────────────────── simulation (pure, vectorised) ───────────────────────────────

def first(mask):
    """Index of the first True per row, BIG if none."""
    import numpy as np
    a = mask.argmax(1)
    a[~mask.any(1)] = BIG
    return a


def last_close(Wc):
    import numpy as np
    ok = ~np.isnan(Wc)
    li = Wc.shape[1] - 1 - ok[:, ::-1].argmax(1)
    return Wc[np.arange(len(Wc)), li]


def simulate(Wh, Wl, Wc, ent_long, ent_short, stop_l, stop_s, tgt_l, tgt_s):
    """Wh/Wl/Wc: (n, HOLD) M1 bid bars from the first bar opening at/after t.
    ent_long/ent_short: (n, LIVE) bool, the bar the pending order fills on.
    stop_* / tgt_* : price per row (tgt NaN = no target). Returns raw outcome arrays."""
    import numpy as np
    n, W = Wh.shape
    jl, js = first(ent_long), first(ent_short)
    filled = np.minimum(jl, js) < BIG
    both = filled & (jl == js)
    side = np.where(jl < js, 1, np.where(js < jl, -1, 0))
    side[both] = 1                                     # worst case booked on the long side
    jf = np.minimum(jl, js)
    J = np.arange(W)[None, :]
    after = J >= jf[:, None]                           # stop can hit on the fill bar
    later = J > jf[:, None]                            # target only after the fill bar
    with np.errstate(invalid="ignore"):
        st_l = first((Wl <= stop_l[:, None]) & after)
        st_s = first((Wh >= stop_s[:, None]) & after)
        tg_l = first((Wh >= tgt_l[:, None]) & later)
        tg_s = first((Wl <= tgt_s[:, None]) & later)
    st = np.where(side == 1, st_l, st_s)
    tg = np.where(side == 1, tg_l, tg_s)
    stopped = filled & ((st < BIG) & (st <= tg) | both)
    targ = filled & ~stopped & (tg < BIG)
    cl = last_close(Wc)
    ex = np.where(stopped, np.where(side == 1, stop_l, stop_s),
                  np.where(targ, np.where(side == 1, tgt_l, tgt_s), cl))
    return dict(filled=filled, both=both, side=side, stopped=stopped, targ=targ, exit=ex)


def pnl_R(res, fill_l, fill_s, stop_l, stop_s, slip_e, spread, slip_s):
    """Net R per row (NaN if not filled). fill_* = raw order level; slip_e = entry slip (stop
    orders); spread charged once per round trip; slip_s on protective-stop exits."""
    import numpy as np
    L = res["side"] == 1
    fl = np.where(L, fill_l + slip_e, fill_s - slip_e)
    stp = np.where(L, stop_l, stop_s)
    ex = np.where(res["stopped"], np.where(L, stp - slip_s, stp + slip_s), res["exit"])
    pnl = np.where(L, ex - fl, fl - ex) - spread
    R = np.where(L, fl - stp, stp - fl)
    out = np.where(res["filled"], pnl / R, np.nan)
    return out, np.where(res["filled"], R, np.nan)


def run_A(Wh, Wl, Wc, rh, rl, off, pip):
    """Expansion bracket. off = offset in price per row."""
    import numpy as np
    up, dn = rh + off, rl - off
    mid = (rh + rl) / 2
    with np.errstate(invalid="ignore"):
        el = Wh[:, :LIVE] >= up[:, None]
        es = Wl[:, :LIVE] <= dn[:, None]
    fl_s, fs_s = up + SLIP * pip, dn - SLIP * pip      # slipped fills fix the 2R target
    tl = fl_s + 2 * (fl_s - mid)
    ts = fs_s - 2 * (mid - fs_s)
    nan = np.full(len(up), np.nan)
    out = {}
    for e, (a, b) in zip(EXITS["A"], ((tl, ts), (nan, nan))):
        r = simulate(Wh, Wl, Wc, el, es, mid, mid, a, b)
        net, R = pnl_R(r, up, dn, mid, mid, SLIP * pip, SPREAD * pip, SLIP * pip)
        n15, _ = pnl_R(r, up, dn, mid, mid, SLIP * pip, SPREAD_SENS * pip, SLIP * pip)
        gr, R0 = pnl_R(r, up, dn, mid, mid, 0.0, 0.0, 0.0)
        cost = (SPREAD + SLIP + SLIP * r["stopped"]) * pip / R
        out[e] = dict(net=net, net15=n15, gross=gr, cost=np.where(r["filled"], cost, np.nan),
                      tt=np.where(r["filled"], 0.0, np.nan), both=r["both"], filled=r["filled"],
                      Rp=R / pip, win=net > 0)
    return out


def run_B(Wh, Wl, Wc, rh, rl, sd, pip):
    """Quiet-slot fade. sd = stop distance beyond the faded edge, price per row."""
    import numpy as np
    mid = (rh + rl) / 2
    with np.errstate(invalid="ignore"):
        es = Wh[:, :LIVE] >= (rh + TT * pip)[:, None]   # limit sell at rh, trade-through required
        el = Wl[:, :LIVE] <= (rl - TT * pip)[:, None]   # limit buy at rl
    sl, ss = rl - sd, rh + sd
    out = {}
    for e, (a, b) in zip(EXITS["B"], ((mid, mid), (rh, rl))):
        r = simulate(Wh, Wl, Wc, el, es, sl, ss, a, b)
        net, R = pnl_R(r, rl, rh, sl, ss, 0.0, SPREAD * pip, SLIP * pip)
        n15, _ = pnl_R(r, rl, rh, sl, ss, 0.0, SPREAD_SENS * pip, SLIP * pip)
        gr, _ = pnl_R(r, rl, rh, sl, ss, 0.0, 0.0, 0.0)
        cost = (SPREAD + SLIP * r["stopped"]) * pip / R
        out[e] = dict(net=net, net15=n15, gross=gr, cost=np.where(r["filled"], cost, np.nan),
                      tt=np.where(r["filled"], TT * pip / R, np.nan), both=r["both"],
                      filled=r["filled"], Rp=R / pip, win=net > 0)
    return out


# ─────────────────────────────── features ───────────────────────────────

def dense(df):
    import numpy as np
    import pandas as pd
    g0 = df.index[0].floor("min")
    p = ((df.index - g0) // pd.Timedelta("1min")).astype(np.int64)
    n = int(p.max()) + 1
    arr = {}
    for k in ("h", "l", "c"):
        a = np.full(n, np.nan)
        a[p] = df[k].values
        arr[k] = a
    return g0, arr


def decisions(df):
    """(ET date, hour, UTC time) for every weekday x hour inside the data span."""
    import numpy as np
    import pandas as pd
    et0 = df.index[0].tz_convert(NY).normalize().tz_localize(None)
    et1 = df.index[-1].tz_convert(NY).normalize().tz_localize(None)
    days = pd.date_range(et0, et1, freq="D")
    days = days[days.day_of_week < 5]
    d = np.repeat(days.values, len(HOURS))
    hr = np.tile(HOURS, len(days))
    loc = pd.DatetimeIndex(d) + pd.to_timedelta(hr, unit="h")
    t = loc.tz_localize(NY, ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")
    ok = ~t.isna()
    return pd.DatetimeIndex(d)[ok], hr[ok], t[ok]


def features(df, pip=PIP):
    """One row per decision, plus the (n, HOLD) bar matrices. Uses only bars that OPENED before t
    for every read (range, ATR16, price at t) and only PRIOR days for seas20."""
    import numpy as np
    import pandas as pd
    g0, A = dense(df)
    day, hr, t = decisions(df)
    pos = ((t - g0) // pd.Timedelta("1min")).values.astype(np.int64)
    n = len(A["c"])
    ok = (pos >= PRE) & (pos + HOLD <= n)
    day, hr, t, pos = day[ok], hr[ok], t[ok], pos[ok]
    idx = pos[:, None] + np.arange(-PRE, HOLD)[None, :]
    Mh, Ml, Mc = A["h"][idx], A["l"][idx], A["c"][idx]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        npre = (~np.isnan(Mc[:, :PRE])).sum(1)
        nwin = (~np.isnan(Mc[:, PRE:])).sum(1)
        nlive = (~np.isnan(Mc[:, PRE:PRE + LIVE])).sum(1)
        rh = np.nanmax(Mh[:, :PRE], 1)
        rl = np.nanmin(Ml[:, :PRE], 1)
        px = last_close(Mc[:, :PRE])
        wr = (np.nanmax(Mh[:, PRE:], 1) - np.nanmin(Ml[:, PRE:], 1)) / pip
    win_ok = (nwin >= MIN_WIN) & (nlive >= MIN_LIVE)
    # seas20: same clock, previous 20 weekdays with a valid window, strictly before this day
    W = pd.DataFrame({"day": day, "hr": hr, "wr": np.where(win_ok, wr, np.nan)})
    seas = np.full(len(W), np.nan)
    for h in HOURS:
        m = (W.hr == h).values
        s = pd.Series(W.wr.values[m], index=W.day.values[m])
        sv = s.dropna().rolling(SEAS_N).mean().shift(1)
        seas[np.nonzero(m)[0]] = sv.reindex(s.index).values
    # ATR16 on COMPLETED M15 bars
    agg = {"o": "first", "h": "max", "l": "min", "c": "last"}
    b = df.resample("15min").agg(agg).dropna()
    pc = b.c.shift(1)
    tr = np.maximum(b.h - b.l, np.maximum((b.h - pc).abs(), (b.l - pc).abs()))
    atr = (tr.rolling(16).mean() / pip).values
    done = (b.index + pd.Timedelta("15min")).values
    k = np.searchsorted(done, t.values, side="right") - 1
    atr16 = np.where(k >= 0, atr[np.clip(k, 0, None)], np.nan)
    valid = (npre >= MIN_PRE) & win_ok & ~np.isnan(seas) & ~np.isnan(atr16) & (atr16 > 0)
    rows = pd.DataFrame({"day": day, "hr": hr, "t": t, "year": day.year, "rh": rh, "rl": rl, "px": px,
                         "seas20": seas, "atr16": atr16, "ratio": seas / atr16, "valid": valid,
                         "why": np.where(npre < MIN_PRE, "range", np.where(~win_ok, "window",
                                np.where(np.isnan(seas), "seas20", np.where(valid, "", "atr"))))})
    return rows, Mh[:, PRE:], Ml[:, PRE:], Mc[:, PRE:]


def terc(x, cuts):
    import numpy as np
    return np.where(np.isnan(x), -1, np.where(x < cuts[0], 0, np.where(x > cuts[1], 2, 1)))


def pair_results(df, pair, pip=PIP):
    """Features, IS-fixed terciles, and every geometry x exit simulated on every valid slot."""
    import numpy as np
    import pandas as pd
    rows, Wh, Wl, Wc = features(df, pip)
    rows["pair"] = pair
    rows["split"] = rows.year.map(split_of)
    v = rows.valid.values
    # Spec: skip a slot if price at t is already beyond a bracket level (cannot happen with a
    # range that ends at t, but kept explicit)
    isv = v & (rows.split.values == "IS")
    cuts = {}
    for f in ("seas20", "ratio", "atr16"):
        q = np.nanpercentile(rows[f].values[isv], [100 / 3, 200 / 3])
        cuts[f] = q
        rows["t_" + f] = np.where(v, terc(rows[f].values, q), -1)
    rows = rows[v].reset_index(drop=True)
    Wh, Wl, Wc = Wh[v], Wl[v], Wc[v]
    rh, rl = rows.rh.values, rows.rl.values
    seas, atr = rows.seas20.values * pip, rows.atr16.values * pip
    isr = rows.split.values == "IS"
    kp = {}
    for strat, sel in (("A", 2), ("B", 0)):
        for k in KS:
            ms = isr & (rows.t_seas20.values == sel)
            ma = isr & (rows.t_atr16.values == sel)
            kp[(strat, k)] = k * np.median(rows.seas20.values[ms]) / np.median(rows.atr16.values[ma])
    cols = {}
    for strat in "AB":
        for k in KS:
            for geo, off in (("s", k * seas), ("a", kp[(strat, k)] * atr)):
                if strat == "A":
                    beyond = (rows.px.values > rh + off) | (rows.px.values < rl - off)
                    res = run_A(Wh, Wl, Wc, rh, rl, off, pip)
                else:
                    beyond = np.zeros(len(rows), bool)
                    res = run_B(Wh, Wl, Wc, rh, rl, off, pip)
                for e, d in res.items():
                    key = f"{strat}{geo}{k:.2f}|{e}"
                    for fld, arr in d.items():
                        a = np.array(arr, dtype=float)
                        if fld in ("net", "net15", "gross", "cost", "tt", "Rp"):
                            a[beyond] = np.nan
                        cols[f"{key}|{fld}"] = a
    out = pd.concat([rows.drop(columns=["valid", "why"]), pd.DataFrame(cols)], axis=1)
    cov = dict(decisions=int(len(v)), valid=int(v.sum()))
    return out, cuts, kp, cov


def coverage_rows(df, pair, pip=PIP):
    rows, *_ = features(df, pip)
    rows["split"] = rows.year.map(split_of)
    return rows[["split", "day", "valid", "why"]].assign(pair=pair)


# ─────────────────────────────── scoring ───────────────────────────────

def dayid(T):
    import numpy as np
    return T.day.values.astype("datetime64[D]").astype(np.int64)


def stats(x, days):
    import numpy as np
    ok = ~np.isnan(x)
    x, g = x[ok], days[ok]
    if len(x) < 20:
        return None
    m, se = drs.cl_mean(x, g)
    pos, neg = x[x > 0].sum(), -x[x < 0].sum()
    return dict(n=int(len(x)), mean=float(m), se=float(se), pf=float(pos / neg) if neg > 0 else float("inf"),
                wr=float((x > 0).mean() * 100), ndays=int(len(np.unique(g))))


def diff_stats(x, days, g1):
    """mean(x | g1) - mean(x | ~g1), SE clustered by day (influence functions summed per day)."""
    import numpy as np
    ok = ~np.isnan(x)
    x, d, g = x[ok], days[ok], g1[ok]
    n1, n2 = g.sum(), (~g).sum()
    if n1 < 20 or n2 < 20:
        return None
    m1, m2 = x[g].mean(), x[~g].mean()
    inf = np.where(g, (x - m1) / n1, -(x - m2) / n2)
    _, inv = np.unique(d, return_inverse=True)
    s = np.bincount(inv, weights=inf)
    return dict(mean=float(m1 - m2), se=float(math.sqrt((s ** 2).sum())))


def paired_day(x1, d1, x2, d2):
    """Per-day mean of cell 1 minus per-day mean of cell 2 over days with trades in both."""
    import numpy as np
    import pandas as pd
    a = pd.Series(x1).groupby(d1).mean().dropna()
    b = pd.Series(x2).groupby(d2).mean().dropna()
    j = a.index.intersection(b.index)
    if len(j) < 20:
        return None
    dd = (a[j] - b[j]).values
    return dict(mean=float(dd.mean()), se=float(dd.std(ddof=1) / math.sqrt(len(dd))), n=int(len(dd)))


def cell_list():
    out = []
    for fam in ("seas20", "ratio"):
        for strat in "AB":
            for k in KS:
                for e in EXITS[strat]:
                    out.append((fam, strat, k, e))
    return out


def cname(c):
    fam, strat, k, e = c
    return f"{fam} {strat} k{k:.2f} {e}"


def evaluate(T):
    """All cell statistics on the stacked result table T (all pairs)."""
    import numpy as np
    D = dayid(T)
    per = {s: (T.split.values == s) for s in SPLITS}
    per["ALL"] = np.ones(len(T), bool)
    C = {}
    for c in cell_list():
        fam, strat, k, e = c
        sel = 2 if strat == "A" else 0
        opp = 2 - sel
        geo = f"{strat}s{k:.2f}|{e}"
        ageo = f"{strat}a{k:.2f}|{e}"
        tf = T["t_" + fam].values
        ta = T.t_atr16.values
        net = T[geo + "|net"].values
        R = {}
        for p, m in per.items():
            ms = m & (tf == sel)
            st = stats(net[ms], D[ms])
            if st:
                st["fill"] = float(T[geo + "|filled"].values[ms].mean() * 100)
                st["both"] = float(np.nansum(T[geo + "|both"].values[ms]) / max(1, (~np.isnan(net[ms])).sum()) * 100)
                st["net15"] = float(np.nanmean(T[geo + "|net15"].values[ms]))
                st["gross"] = float(np.nanmean(T[geo + "|gross"].values[ms]))
                g = stats(T[geo + "|gross"].values[ms], D[ms])
                st["gross_se"] = g["se"] if g else float("nan")
                st["exp"] = -float(np.nanmean(T[geo + "|cost"].values[ms]) + np.nanmean(T[geo + "|tt"].values[ms]))
                st["tt_exp"] = -float(np.nanmean(T[geo + "|tt"].values[ms]))
                st["Rp"] = float(np.nanmedian(T[geo + "|Rp"].values[ms]))
            mt = m & (tf >= 0)
            al = diff_stats(net[mt], D[mt], tf[mt] == sel)
            mo = m & (tf == opp)
            op = stats(net[mo], D[mo])
            aa = T[ageo + "|net"].values
            mA = m & (ta == sel)
            at = stats(aa[mA], D[mA])
            ok1 = ms & ~np.isnan(net)
            ok2 = mA & ~np.isnan(aa)
            pr = paired_day(net[ok1], D[ok1], aa[ok2], D[ok2])
            R[p] = dict(cell=st, allslots=al, opp=op, atr=at, paired=pr)
        C[cname(c)] = R
    return C


def verdict(name, Rc, NA, NB):
    """Pre-registered pass rule (spec §6). Returns (pass, list of failed criteria)."""
    fails = []
    for p in SPLITS:
        c = Rc[p]["cell"]
        if not c or not (c["mean"] > 0 and c["mean"] > 2 * c["se"]):
            fails.append(f"1:{p}")
        if not c or c["pf"] < 1.3:
            fails.append(f"2:{p}")
        a, pr = Rc[p]["allslots"], Rc[p]["paired"]
        if not a or a["mean"] <= 0:
            fails.append(f"3all:{p}")
        if not pr or pr["mean"] <= 0:
            fails.append(f"3atr:{p}")
    a, pr = Rc["ALL"]["allslots"], Rc["ALL"]["paired"]
    if not a or a["mean"] <= 2 * a["se"]:
        fails.append("3all:pooled")
    if not pr or pr["mean"] <= 2 * pr["se"]:
        fails.append("3atr:pooled")
    for lab, N in (("A", NA), ("B", NB)):
        ok, _ = null_ok(N.get(name, {}).get("ALL") if N else None)
        if not ok:
            fails.append(f"4:null{lab}")
    return (not fails), fails


def null_ok(nc):
    """Criterion 4 on one null cell (pooled all periods): net within 2 SE of its cost-only
    expectation, and the costs-off R within 2 SE of its mechanical expectation (0 for A; minus the
    0.5-pip limit trade-through in R for B, which a martingale charges by construction)."""
    if not nc or not nc.get("cell"):
        return False, "missing"
    c = nc["cell"]
    z1 = (c["mean"] - c["exp"]) / c["se"]
    z2 = (c["gross"] - c["tt_exp"]) / c["gross_se"]
    z3 = c["gross"] / c["gross_se"]
    return (abs(z1) <= 2 and abs(z2) <= 2), f"z_net {z1:+.1f}, z_gross {z2:+.1f} (vs 0: {z3:+.1f})"


# ─────────────────────────────── report ───────────────────────────────

def f_cell(c):
    if not c:
        return "—"
    return f"{c['mean']:+.3f}±{c['se']:.3f}"


def coverage_lines(cov):
    import pandas as pd
    L = ["## Coverage", "", "| period | days | decisions | valid | skipped (range / window / seas20 / atr) |",
         "|---|---|---|---|---|"]
    for s in SPLITS:
        c = cov[cov.split == s]
        if not len(c):
            continue
        w = c.why.value_counts()
        L.append(f"| {s} | {c.day.nunique()} | {len(c)} | {int(c.valid.sum())} | "
                 f"{w.get('range', 0)} / {w.get('window', 0)} / {w.get('seas20', 0)} / {w.get('atr', 0)} |")
    L += ["", "seas20 needs 20 prior valid days per clock, so the first ~4 weeks of each series are skipped.", ""]
    return L


def report(T, cov, title, NA=None, NB=None, extra=None, is_null=False):
    C = evaluate(T)
    L = [f"# {title}", "", "Spec: research/specs/P127_clock_volatility.md (approved 2026-11-07). "
         "Avg R per filled trade after costs (1.0 pip spread, 0.5 pip slip on every stop-order fill) "
         "± day-clustered SE (three pairs pooled). PF in R. WR reported, not gated. "
         "`exp` = cost-only expectation on a random walk = −(mean cost in R) − (B only: mean 0.5-pip "
         "limit trade-through in R).", ""]
    L += coverage_lines(cov)
    if extra:
        L += extra
    names = [cname(c) for c in cell_list()]
    for p in SPLITS + ("ALL",):
        L += [f"## {p}" + (" (pooled, used for criterion 3 'beyond 2 SE pooled' and criterion 4)" if p == "ALL" else ""), "",
              "| cell | n | fill% | WR% | avg R ± SE | PF | exp | R pips (med) | 1.5-pip spread | both-in-1-bar % "
              "| tercile − other two | opposite tercile | ATR-only cell | seas − ATR (paired day) | Null A | Null B |",
              "|---|" + "---|" * 15]
        for nm in names:
            r = C[nm][p]
            c = r["cell"]
            na = (NA or {}).get(nm, {}).get(p) if NA else None
            nb = (NB or {}).get(nm, {}).get(p) if NB else None
            fna = f_cell(na["cell"]) + f" (exp {na['cell']['exp']:+.3f})" if na and na.get("cell") else "—"
            fnb = f_cell(nb["cell"]) + f" (exp {nb['cell']['exp']:+.3f})" if nb and nb.get("cell") else "—"
            if c:
                L.append(f"| {nm} | {c['n']} | {c['fill']:.0f} | {c['wr']:.1f} | {f_cell(c)} | {c['pf']:.2f} | "
                         f"{c['exp']:+.3f} | {c['Rp']:.1f} | {c['net15']:+.3f} | {c['both']:.2f} | "
                         f"{f_cell(r['allslots'])} | {f_cell(r['opp'])} | {f_cell(r['atr'])} | "
                         f"{f_cell(r['paired'])} | {fna} | {fnb} |")
            else:
                L.append(f"| {nm} | — |" + " — |" * 14)
        L.append("")
    # null calibration
    if is_null:
        L += ["## Null calibration (pooled): criterion 4", "",
              "| cell | net − exp (z) | costs-off R | costs-off vs mechanical expectation (z) | costs-off vs 0 (z) |",
              "|---|---|---|---|---|"]
        for nm in names:
            c = C[nm]["ALL"]["cell"]
            if not c:
                continue
            L.append(f"| {nm} | {c['mean']-c['exp']:+.3f} ({(c['mean']-c['exp'])/c['se']:+.1f}) | "
                     f"{c['gross']:+.3f}±{c['gross_se']:.3f} | {(c['gross']-c['tt_exp'])/c['gross_se']:+.1f} | "
                     f"{c['gross']/c['gross_se']:+.1f} |")
        L.append("")
    else:
        L += ["## Verdict (spec §6 — all four criteria)", "", "| cell | verdict | failed criteria |", "|---|---|---|"]
        npass = 0
        for nm in names:
            ok, fails = verdict(nm, C[nm], NA, NB)
            npass += ok
            L.append(f"| {nm} | {'PASS' if ok else 'FAIL'} | {', '.join(fails[:12])}{' …' if len(fails) > 12 else ''} |")
        L += ["", f"**VERDICT: {npass} of {len(names)} cells pass.** "
              + ("Session / pair breakdowns below for the passing cells." if npass else
                 "No cell passes; session / pair breakdowns are not read (spec §7)."), ""]
        if npass:
            L += breakdown(T, C, NA, NB)
        if NA:
            L += ["## Null calibration used by criterion 4 (pooled)", "", "| cell | Null A | Null B |", "|---|---|---|"]
            for nm in names:
                L.append(f"| {nm} | {null_ok(NA.get(nm, {}).get('ALL'))[1]} | {null_ok(NB.get(nm, {}).get('ALL'))[1]} |")
            L.append("")
    return "\n".join(L), C


def breakdown(T, C, NA, NB):
    import numpy as np
    L = ["## Breakdowns for passing cells (reported, not gated)", ""]
    D = dayid(T)
    sess = np.where(T.hr.values < 3, "asia", np.where(T.hr.values < 7, "london", "ny"))
    for c in cell_list():
        nm = cname(c)
        if not verdict(nm, C[nm], NA, NB)[0]:
            continue
        fam, strat, k, e = c
        sel = 2 if strat == "A" else 0
        net = T[f"{strat}s{k:.2f}|{e}|net"].values
        m0 = T["t_" + fam].values == sel
        L += [f"### {nm}", "", "| slice | IS | OOS | 2026 |", "|---|---|---|---|"]
        for lab, mm in [(s, sess == s) for s in ("asia", "london", "ny")] + [(p, T.pair.values == p) for p in PAIRS]:
            L.append(f"| {lab} | " + " | ".join(f_cell(stats(net[m0 & mm & (T.split.values == s)],
                                                              D[m0 & mm & (T.split.values == s)])) for s in SPLITS) + " |")
        L.append("")
    return L


def to_json(C):
    return {nm: {p: {"cell": r["cell"]} for p, r in d.items()} for nm, d in C.items()}


# ─────────────────────────────── nulls ───────────────────────────────

def stylized_profile():
    """Median M1 range (pips) by ET minute of day, used when no real data is available."""
    import numpy as np
    m = np.arange(1440)
    prof = np.full(1440, 0.6)
    prof[(m >= 2 * 60) & (m < 3 * 60)] = 0.9
    prof[(m >= 3 * 60) & (m < 6 * 60)] = 1.6
    prof[(m >= 6 * 60) & (m < 7 * 60)] = 1.1
    prof[(m >= 7 * 60) & (m < 11 * 60)] = 1.9
    prof[(m >= 11 * 60) & (m < 13 * 60)] = 1.2
    prof[(m >= 13 * 60) & (m < 17 * 60)] = 0.8
    return prof


def real_profile(pair):
    """Real median M1 high-low (pips) for each ET clock minute, weekdays, from the HistData file."""
    import numpy as np
    df = drs.load_utc(pair)
    if df is None:
        return None
    et = df.index.tz_convert(NY)
    keep = et.day_of_week < 5
    mod = (et.hour * 60 + et.minute)[keep]
    rng = ((df.h - df.l).values / PIP)[keep]
    import pandas as pd
    prof = pd.Series(rng).groupby(np.asarray(mod)).median().reindex(range(1440))
    return prof.interpolate().bfill().ffill().values


def null_frames(kind, seed=0, phi=0.0, days=NULL_DAYS, profiles=None):
    """Random walks with the clock-time volatility shape: per-minute sd from the median M1 range
    for that ET minute, times a slow AR(1) day multiplier shared by the pairs (one dollar day).
    Bar high/low = exact Brownian-bridge extremes (continuous path). phi != 0 plants autocorrelation in the
    1-min increments (power check). kind 'B' adds independent +-0.2-0.5 pip bid-quote shifts per bar."""
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(1000 + seed)
    idx = pd.date_range("2022-01-03", periods=days * 1440, freq="1min", tz="UTC")
    et = idx.tz_convert(NY)
    keep = ~((et.day_of_week == 5) | ((et.day_of_week == 4) & (et.hour >= 17)) |
             ((et.day_of_week == 6) & (et.hour < 17)))
    idx, et = idx[keep], et[keep]
    mod = np.asarray(et.hour * 60 + et.minute)
    dnum = np.asarray(et.normalize().tz_localize(None).values.astype("datetime64[D]").astype(np.int64))
    ud, inv = np.unique(dnum, return_inverse=True)
    lm = np.zeros(len(ud))
    e = rng.normal(0, 0.1, len(ud))
    for i in range(1, len(ud)):
        lm[i] = 0.95 * lm[i - 1] + e[i]
    mult = np.exp(lm - lm.mean())[inv]
    out = {}
    for j, s in enumerate(PAIRS):
        prof = (profiles or {}).get(s)
        if prof is None:
            prof = stylized_profile()
        sig = prof[mod] * mult * PIP / 1.6           # median range of a Brownian minute ~ 1.6 sd
        r = np.random.default_rng(2000 + 37 * seed + j)
        n = len(idx)
        z = r.normal(0, 1, n) * sig
        if phi:
            m = np.empty(n)
            m[0] = z[0]
            sc = math.sqrt(1 - phi * phi)
            for i in range(1, n):
                m[i] = phi * m[i - 1] + sc * z[i]
            z = m
        # CONTINUOUS path inside each bar: high / low drawn from the exact Brownian-bridge
        # maximum / minimum given the bar's open-to-close move. A discrete sub-step walk overshoots
        # a level before it is "seen", and booking fills / stops at the level then pays stop
        # entries ~+0.05R and charges trade-through limits on pure noise (found in v1 of this null).
        x2 = z * z
        hi_rel = (z + np.sqrt(x2 - 2 * sig * sig * np.log(r.uniform(1e-12, 1, n)))) / 2
        lo_rel = (z - np.sqrt(x2 - 2 * sig * sig * np.log(r.uniform(1e-12, 1, n)))) / 2
        o = NULL_BASE[s] + np.r_[0.0, np.cumsum(z)[:-1]]
        c = o + z
        h = o + hi_rel
        lo = o + lo_rel
        if kind == "B":
            q = r.uniform(0.2, 0.5, n) * r.choice([-1.0, 1.0], n) * PIP
            o, h, lo, c = o + q, h + q, lo + q, c + q
        out[s] = pd.DataFrame({"o": o, "h": h, "l": lo, "c": c}, index=idx)
        del z, x2, hi_rel, lo_rel
    return out


def stack(frames):
    import pandas as pd
    parts, covs, meta = [], [], {}
    for s, df in frames.items():
        T, cuts, kp, cv = pair_results(df, s)
        parts.append(T)
        covs.append(coverage_rows(df, s))
        meta[s] = (cuts, kp)
        print(f"  {s}: {len(T)} valid slots", flush=True)
    return pd.concat(parts, ignore_index=True), pd.concat(covs, ignore_index=True), meta


def meta_lines(meta, prof_src):
    L = ["## Tercile cut points (IS, per pair) and ATR-only k'", "", f"Volatility profile: {prof_src}", "",
         "| pair | seas20 q33 / q67 (pips) | ratio q33 / q67 | ATR16 q33 / q67 (pips) | k' A 0.10 / 0.25 | k' B 0.10 / 0.25 |",
         "|---|---|---|---|---|---|"]
    for s, (cuts, kp) in meta.items():
        L.append(f"| {s} | {cuts['seas20'][0]:.1f} / {cuts['seas20'][1]:.1f} | {cuts['ratio'][0]:.2f} / {cuts['ratio'][1]:.2f} | "
                 f"{cuts['atr16'][0]:.2f} / {cuts['atr16'][1]:.2f} | {kp[('A', 0.1)]:.2f} / {kp[('A', 0.25)]:.2f} | "
                 f"{kp[('B', 0.1)]:.2f} / {kp[('B', 0.25)]:.2f} |")
    return L + [""]


def profiles():
    P, src = {}, []
    for s in PAIRS:
        p = real_profile(s)
        if p is not None:
            P[s] = p
            src.append(f"{s} real (median M1 range by ET minute, Asia {p[60:120].mean():.2f} / London "
                       f"{p[200:300].mean():.2f} / NY {p[480:600].mean():.2f} pips)")
        else:
            src.append(f"{s} stylized (no HistData file found)")
    return P, "; ".join(src)


def run_null(kinds=("A", "B"), seeds=(1, 2, 3)):
    """Seed 0 is the pre-registered null that criterion 4 reads. Extra seeds only feed a
    robustness table, so one unlucky seed shows as luck instead of being re-rolled away."""
    P, src = profiles()
    res, texts = {}, []
    names = [cname(c) for c in cell_list()]
    for k in kinds:
        fr = null_frames(k, seed=0, profiles=P)
        T, cov, meta = stack(fr)
        del fr
        title = f"P127 NULL {k} — random walks with the real clock-volatility shape" + \
                (" + bid-quote noise (±0.2-0.5 pip per M1 bar)" if k == "B" else "")
        txt, C = report(T, cov, title, extra=meta_lines(meta, src), is_null=True)
        res[k] = to_json(C)
        zs = {0: C}
        for sd in seeds:
            fr = null_frames(k, seed=sd, profiles=P)
            zs[sd] = evaluate(stack(fr)[0])
            del fr
        rob = [f"## Null {k} seed robustness — z of (avg R − cost-only expectation), pooled; "
               "criterion 4 reads seed 0 only", "", "| cell | " + " | ".join(f"seed {sd}" for sd in zs) + " |",
               "|---|" + "---|" * len(zs)]
        for nm in names:
            rob.append(f"| {nm} | " + " | ".join(
                f"{(zs[sd][nm]['ALL']['cell']['mean'] - zs[sd][nm]['ALL']['cell']['exp']) / zs[sd][nm]['ALL']['cell']['se']:+.1f}"
                for sd in zs) + " |")
        rob += ["", "A calibrated null gives z ~ N(0,1) per seed; a cell that sits beyond ±2 in most seeds "
                "is a property of that null (e.g. the bid-noise bounce), not luck.", ""]
        texts.append(txt + "\n" + "\n".join(rob))
        print(f"null {k} done", flush=True)
    return res, texts


def run_power(phis=(0.0, 0.1, 0.25, 0.4, -0.1, -0.25, -0.4)):
    """Planted effects on the Null A generator (same seed for every phi, so phi = 0 is a paired
    baseline): AR(1) autocorrelation phi in the 1-min increments. phi > 0 = follow-through (should
    lift the A cells), phi < 0 = reversion (should lift the B cells)."""
    P, src = profiles()
    L = ["# P127 power check — planted follow-through / reversion", "",
         "Null A generator (seed 5) with AR(1) autocorrelation phi in the 1-min increments "
         "(1-min variance kept; 4h variance ratio ~ (1+phi)/(1-phi)). Seas20 cells, pooled over all "
         "periods. `Δ vs phi 0` = avg R minus the same-seed phi = 0 run (SE = root sum of squares, "
         "conservative for a paired design). `z vs exp` = avg R against the cost-only "
         "expectation (= the costs-off R in SE units) — **this is the power column**: planted "
         "follow-through must push the A cells up, planted reversion the B cells. `Δ vs phi 0` mixes in "
         "a geometry change (phi alters the 4h variance, hence seas20, hence R and cost-in-R), so it "
         "moves A and B the same way and is not the test. The bar on real data is far higher than "
         "detection (avg R > 0 after costs, PF >= 1.3).", "",
         "| phi | 4h var ratio | cell | avg R ± SE | PF | Δ vs phi 0 (z) | z vs exp |", "|---|---|---|---|---|---|---|"]
    base = {}
    for phi in phis:
        fr = null_frames("A", seed=5, phi=phi, profiles=P)
        C = evaluate(stack(fr)[0])
        del fr
        for c in cell_list():
            if c[0] != "seas20":
                continue
            nm = cname(c)
            st = C[nm]["ALL"]["cell"]
            if phi == 0.0:
                base[nm] = st
            b = base[nm]
            dlt = st["mean"] - b["mean"]
            dse = math.sqrt(st["se"] ** 2 + b["se"] ** 2)
            L.append(f"| {phi:+.2f} | {(1 + phi) / (1 - phi):.2f} | {nm} | {f_cell(st)} | {st['pf']:.2f} | "
                     f"{dlt:+.3f} ({dlt / dse:+.1f}) | {(st['mean'] - st['exp']) / st['se']:+.1f} |")
        print(f"power phi {phi} done", flush=True)
    L.append("")
    return "\n".join(L)


# ─────────────────────────────── selftest ───────────────────────────────

def selftest():
    import numpy as np
    import pandas as pd
    pip = PIP
    nan = np.nan
    W = HOLD

    def mats(n=1):
        base = np.full((n, W), 1.1005)        # inside the 1.0990-1.1010 range, above the midpoint
        return base + 0.00002, base - 0.00002, base.copy()

    rh, rl = np.array([1.1010]), np.array([1.0990])
    # A: buy-stop fills at bar 5, sell level touched at bar 20 -> OCO: one long trade only
    Wh, Wl, Wc = mats()
    Wh[0, 5] = 1.1013; Wc[0, 5:] = 1.1012; Wl[0, 6:] = 1.1011; Wh[0, 6:] = 1.1013
    Wl[0, 20] = 1.0980
    off = np.array([0.0002])
    r = run_A(Wh, Wl, Wc, rh, rl, off, pip)["E2 time"]
    up = 1.1012 + SLIP * pip
    assert r["filled"][0] and not r["both"][0]
    # bar 20 low 1.0980 <= mid 1.1000 -> stopped at mid - slip
    exp = ((1.1000 - SLIP * pip) - up - SPREAD * pip) / (up - 1.1000)
    assert abs(r["net"][0] - exp) < 1e-9, (r["net"][0], exp)
    # costs-off version: exit at mid, fill at level
    assert abs(r["gross"][0] - (1.1000 - 1.1012) / (1.1012 - 1.1000)) < 1e-9
    # stop before target in the same bar
    Wh, Wl, Wc = mats()
    Wh[0, 5] = 1.1013; Wc[0, 5] = 1.1012
    tgt = up + 2 * (up - 1.1000)
    Wh[0, 9] = tgt + 0.0001; Wl[0, 9] = 1.0999
    rr = run_A(Wh, Wl, Wc, rh, rl, off, pip)
    assert rr["E1 2R"]["net"][0] < -1, rr["E1 2R"]["net"]
    # target alone -> +2R minus costs, exactly
    Wl[0, 9] = 1.1005
    rr = run_A(Wh, Wl, Wc, rh, rl, off, pip)
    exp = (tgt - up - SPREAD * pip) / (up - 1.1000)
    assert abs(rr["E1 2R"]["net"][0] - exp) < 1e-9 and abs(exp - (2 - SPREAD * pip / (up - 1.1000))) < 1e-9
    # target is not taken on the fill bar
    Wh, Wl, Wc = mats()
    Wh[0, 5] = tgt + 0.0001; Wc[0, 5:] = 1.1012
    rr = run_A(Wh, Wl, Wc, rh, rl, off, pip)
    assert abs(rr["E1 2R"]["net"][0] - (1.1012 - up - SPREAD * pip) / (up - 1.1000)) < 1e-9
    # stop on the fill bar counts
    Wh, Wl, Wc = mats()
    Wh[0, 5] = 1.1013; Wl[0, 5] = 1.0995
    rr = run_A(Wh, Wl, Wc, rh, rl, off, pip)
    assert rr["E2 time"]["net"][0] < -1
    # both bracket sides in one bar -> worst case -1R - costs
    Wh, Wl, Wc = mats()
    Wh[0, 7] = 1.1013; Wl[0, 7] = 1.0987
    rr = run_A(Wh, Wl, Wc, rh, rl, off, pip)["E1 2R"]
    R = up - 1.1000
    assert rr["both"][0] and abs(rr["net"][0] - (-R - SLIP * pip - SPREAD * pip) / R) < 1e-9
    # pending orders expire after LIVE bars
    Wh, Wl, Wc = mats()
    Wh[0, LIVE] = 1.1013
    assert not run_A(Wh, Wl, Wc, rh, rl, off, pip)["E1 2R"]["filled"][0]
    # B: limit sell at rh needs a 0.5-pip trade-through
    sd = np.array([0.0005])
    Wh, Wl, Wc = mats()
    Wh[0, 3] = 1.1010 + 0.4 * pip
    assert not run_B(Wh, Wl, Wc, rh, rl, sd, pip)["E1 mid"]["filled"][0]
    Wh[0, 3] = 1.1010 + 0.5 * pip
    rb = run_B(Wh, Wl, Wc, rh, rl, sd, pip)
    assert rb["E1 mid"]["filled"][0]
    # filled short at 1.1010; lows never reach the 1.1000 midpoint -> time exit at the 1.1005 close
    exp = (1.1010 - 1.1005 - SPREAD * pip) / 0.0005
    assert abs(rb["E1 mid"]["net"][0] - exp) < 1e-9, (rb["E1 mid"]["net"][0], exp)
    assert abs(rb["E1 mid"]["tt"][0] - TT * pip / 0.0005) < 1e-12
    # B stop: short stopped at rh + sd + slip
    Wh, Wl, Wc = mats()
    Wh[0, 3] = 1.1011; Wl[0, 3:] = 1.1006; Wc[0, 3:] = 1.1008; Wh[0, 4:] = 1.1009
    Wh[0, 10] = 1.1016
    rb = run_B(Wh, Wl, Wc, rh, rl, sd, pip)["E2 edge"]
    assert abs(rb["net"][0] - (1.1010 - (1.1015 + SLIP * pip) - SPREAD * pip) / 0.0005) < 1e-9
    # B both edges in one bar -> worst case
    Wh, Wl, Wc = mats()
    Wh[0, 2] = 1.1011; Wl[0, 2] = 1.0989
    rb = run_B(Wh, Wl, Wc, rh, rl, sd, pip)["E1 mid"]
    assert rb["both"][0] and abs(rb["net"][0] - (-0.0005 - SLIP * pip - SPREAD * pip) / 0.0005) < 1e-9

    # features: seas20 prior days only; range / ATR / price on bars that opened before t only
    fr = null_frames("A", seed=3, days=70)["EURUSD"]
    rows0, *_ = features(fr)
    X = pd.Timestamp("2022-02-23 13:00", tz=NY).tz_convert("UTC")
    fr2 = fr.copy()
    fr2.loc[X, ["h", "c"]] = [fr2.loc[X, "h"] + 0.05, fr2.loc[X, "c"] + 0.04]   # 500-pip junk bar
    rows1, *_ = features(fr2)
    cols = ["rh", "rl", "px", "seas20", "atr16", "ratio"]
    before = rows0.t <= X
    a = rows0.loc[before, cols].values
    b = rows1.loc[before, cols].values
    assert np.allclose(np.nan_to_num(a, nan=-9), np.nan_to_num(b, nan=-9)), "a bar at/after t leaked into a read"
    assert rows0.loc[before & (rows0.t == X), "valid"].all()
    # the same day's later slots: seas20 unchanged (day d never read), and the next day DOES see it
    sameday = rows0.day == pd.Timestamp("2022-02-23")
    assert np.allclose(rows0.loc[sameday, "seas20"].values, rows1.loc[sameday, "seas20"].values)
    nxt = (rows0.day == pd.Timestamp("2022-02-24")) & (rows0.hr == 10)
    assert not np.allclose(rows0.loc[nxt, "seas20"].values, rows1.loc[nxt, "seas20"].values)
    # decisions: 13 per weekday, 00:00..12:00 ET
    hrs = rows0.groupby("day").hr.apply(list)
    assert all(h == HOURS for h in hrs.values)
    # day-clustered SE / diff helper sanity
    x = np.array([1.0, 1.0, -1.0, -1.0] * 10)
    d = np.repeat(np.arange(20), 2)
    st = stats(x, d)
    assert abs(st["mean"]) < 1e-12 and st["pf"] == 1.0
    ds = diff_stats(np.r_[np.ones(30), np.zeros(30)], np.arange(60), np.r_[np.ones(30, bool), np.zeros(30, bool)])
    assert abs(ds["mean"] - 1) < 1e-12 and ds["se"] < 1e-9
    # zero-cost Null A: the bracket's costs-off R must be ~0, the fade's ~ minus its trade-through
    T, _, _ = stack(null_frames("A", seed=11, days=420))
    Dd = dayid(T)
    for geo, ttx in (("As0.10|E2 time", False), ("As0.25|E1 2R", False), ("Bs0.25|E1 mid", True)):
        g = T[geo + "|gross"].values
        st = stats(g, Dd)
        z = (st["mean"] + (np.nanmean(T[geo + "|tt"].values) if ttx else 0)) / st["se"]
        assert abs(z) < 3, (geo, st, z)
        print(f"  zero-cost null {geo}: {st['mean']:+.3f}±{st['se']:.3f} (z vs expectation {z:+.1f})")
    print("selftest ok")


# ─────────────────────────────── main ───────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--null", nargs="?", const="both", choices=["A", "B", "both"])
    ap.add_argument("--power", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    if a.power:
        txt = run_power()
        with open(a.out or os.path.join(ROOT, "data", "clock_vol_power.md"), "w") as f:
            f.write(txt + "\n")
        print(txt)
        return
    if a.null:
        kinds = ["A", "B"] if a.null == "both" else [a.null]
        res, texts = run_null(kinds)
        with open(a.out or NULL_OUT, "w") as f:
            f.write("\n\n".join(texts) + "\n")
        prev = {}
        if os.path.exists(NULL_JSON):
            with open(NULL_JSON) as f:
                prev = json.load(f)
        prev.update(res)
        with open(NULL_JSON, "w") as f:
            json.dump(prev, f)
        print("\n\n".join(texts))
        return
    frames = {}
    for s in PAIRS:
        df = drs.load_utc(s)
        if df is None:
            sys.exit(f"missing {s}")
        frames[s] = df
        print(s, len(df), df.index[0], df.index[-1], flush=True)
    if not os.path.exists(NULL_JSON):
        print("null JSON missing -> running both nulls first", flush=True)
        res, texts = run_null(["A", "B"])
        with open(NULL_JSON, "w") as f:
            json.dump(res, f)
        with open(NULL_OUT, "w") as f:
            f.write("\n\n".join(texts) + "\n")
    with open(NULL_JSON) as f:
        nj = json.load(f)
    T, cov, meta = stack(frames)
    _, src = profiles()
    extra = meta_lines(meta, "real data (nulls use: " + src + ")")
    pw = os.path.join(ROOT, "data", "clock_vol_power.md")
    if os.path.exists(pw):
        extra += ["## Power check (planted effects on Null A)", "", open(pw).read().split("\n", 2)[-1], ""]
    txt, _ = report(T, cov, "P127 — clock-time volatility: bracket in busy slots, fade in quiet slots",
                    nj.get("A"), nj.get("B"), extra=extra)
    with open(a.out or OUT, "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
