"""P120 — rework step 1: does the DOLLAR READ predict direction on COMPLETED bars?

Every 15 minutes inside the killzones (London 03:00-05:00 ET, NY 07:00-10:00 ET) each
reader looks at UDXUSD bars that are COMPLETE at that moment and calls the dollar up / down /
flat. A dollar-up call means EURUSD / GBPUSD / NZDUSD down. Scored on what the pair does next:

  race   which comes first from the decision price: +10 pips or -10 pips (M1 path, 8h cap).
         A coin scores 50% whatever the market drifts (it is symmetric), so lift = hit - 50.
  fwd1 / fwd4   signed pips over the next 1h / 4h in the called direction (coin = 0).

Readers (all on completed bars only — the forming bar is never seen):
  bos_h1     the engine's htf_bias: last H1 close beyond the prior 20 bars' high/low
             (fires only on the breakout bar)
  latch_h1   the direction of the most recent such breakout within the last 24 H1 bars
  bos_h4 / latch_h4 / bos_d / latch_d   the same rule on H4 / D
  mom_h1     sign of the DXY change over the last 6 completed H1 bars
  ema_h1     last H1 close vs EMA(50) of H1 closes
  prev_d     colour of the last completed daily candle
  d2s        yesterday vs the day before: HH+HL up, LH+LL down, else flat

Pair selection (the DXY x EURGBP quadrant): when the dollar read and the EURGBP read (same
rule on EURGBP) are both live, the quadrant names ONE of EURUSD/GBPUSD (dollar up: sell the
weaker; dollar down: buy the stronger). `sel` = chosen pair's 4h move in the called direction
minus the other pair's move in the same direction. Selection works only if sel > 0.

--null replaces every series with an independent random walk: every lift must read ~0.
"""
import argparse
import glob
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "histdata")
PAIRS = ["EURUSD", "GBPUSD", "NZDUSD"]
NY = "America/New_York"
PIP = 0.0001
RACE_PIPS = 10.0
RACE_CAP_MIN = 480
STEP_MIN = 15
KZ = ((3 * 60, 5 * 60, "london"), (7 * 60, 10 * 60, "ny"))
LB = 20
LATCH = 24
READERS = ["bos_h1", "latch_h1", "bos_h4", "latch_h4", "bos_d", "latch_d",
           "mom_h1", "ema_h1", "prev_d", "d2s"]


def split_of(year):
    return "IS" if year <= 2023 else ("OOS" if year <= 2025 else "2026")


# ───────────────────────── readers on a completed-bar array ─────────────────────────

def bos_series(h, l, c, lb=LB):
    """+1 / -1 on the bar whose close breaks the prior lb bars' high / low (htf_bias rule)."""
    import numpy as np
    n = len(c)
    out = np.zeros(n, dtype=int)
    for i in range(lb + 1, n):
        hh = h[i - lb:i].max()
        ll = l[i - lb:i].min()
        if c[i] > hh:
            out[i] = 1
        elif c[i] < ll:
            out[i] = -1
    return out


def latch_series(bos, span=LATCH):
    """Direction of the most recent breakout within the last `span` bars (0 if none)."""
    import numpy as np
    out = np.zeros(len(bos), dtype=int)
    last, age = 0, 10 ** 9
    for i, b in enumerate(bos):
        if b != 0:
            last, age = b, 0
        else:
            age += 1
        out[i] = last if age < span else 0
    return out


def ema(x, n):
    import numpy as np
    a = 2.0 / (n + 1)
    out = np.empty(len(x))
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def d2s_series(h, l):
    """Bar i vs bar i-1: HH+HL = +1, LH+LL = -1, else 0."""
    import numpy as np
    out = np.zeros(len(h), dtype=int)
    for i in range(1, len(h)):
        if h[i] > h[i - 1] and l[i] > l[i - 1]:
            out[i] = 1
        elif h[i] < h[i - 1] and l[i] < l[i - 1]:
            out[i] = -1
    return out


def quadrant(dollar, cross):
    """(pair, pair_dir) from the DXY x EURGBP table, or (None, 0)."""
    if dollar == 0 or cross == 0:
        return None, 0
    if dollar > 0:      # dollar up -> sell the weaker
        return ("GBPUSD", -1) if cross > 0 else ("EURUSD", -1)
    return ("EURUSD", 1) if cross > 0 else ("GBPUSD", 1)


# ─────────────────────────────── data ───────────────────────────────

def load_utc(sym):
    import pandas as pd
    files = sorted(glob.glob(os.path.join(DATA, f"{sym}_20??.csv")) +
                   glob.glob(os.path.join(DATA, f"{sym}_20??_??.csv")))
    if not files:
        return None
    df = pd.concat([pd.read_csv(f, sep=";", header=None, names=["dt", "o", "h", "l", "c", "v"])
                    for f in files], ignore_index=True)
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    df = df.drop_duplicates("dt").sort_values("dt").set_index("dt")
    df.index = (df.index + pd.Timedelta(hours=5)).tz_localize("UTC")   # HistData = fixed EST
    return df[["o", "h", "l", "c"]]


def null_frame(seed, base, scale, days=1460):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-03", periods=days * 1440, freq="1min", tz="UTC")
    idx = idx[idx.dayofweek < 5]
    c = base + np.cumsum(rng.normal(0, scale, len(idx)))
    o = np.r_[c[0], c[:-1]]
    w = np.abs(rng.normal(0, scale / 2, len(idx)))
    return pd.DataFrame({"o": o, "h": np.maximum(o, c) + w, "l": np.minimum(o, c) - w, "c": c},
                        index=idx)


def resample(df, rule):
    agg = {"o": "first", "h": "max", "l": "min", "c": "last"}
    import pandas as pd
    b = df.resample(rule).agg(agg).dropna()
    b["done"] = b.index + pd.Timedelta(rule)
    return b


def reader_frame(df):
    """Per completed bar: the reader values, indexed by the time the bar is COMPLETE."""
    import numpy as np
    import pandas as pd
    out = {}
    for tf, rule in (("h1", "60min"), ("h4", "240min"), ("d", "1D")):
        b = resample(df, rule)
        h, l, c, o = (b[k].values for k in ("h", "l", "c", "o"))
        bos = bos_series(h, l, c)
        cols = {f"bos_{tf}": bos, f"latch_{tf}": latch_series(bos)}
        if tf == "h1":
            cols["mom_h1"] = np.sign(c - np.r_[[np.nan] * 6, c[:-6]]).astype(float)
            cols["ema_h1"] = np.sign(c - ema(c, 50))
        if tf == "d":
            cols["prev_d"] = np.sign(c - o)
            cols["d2s"] = d2s_series(h, l)
        out[tf] = pd.DataFrame(cols, index=pd.DatetimeIndex(b["done"]))
    return out


def asof(frame, times):
    """Value of each column as of `times` (last bar COMPLETE at or before t)."""
    import numpy as np
    pos = frame.index.searchsorted(times, side="right") - 1
    vals = frame.values
    res = np.zeros((len(times), vals.shape[1]))
    ok = pos >= 0
    res[ok] = vals[pos[ok]]
    return np.nan_to_num(res).astype(int), list(frame.columns)


def decision_times(idx):
    import numpy as np
    import pandas as pd
    et = idx.tz_convert(NY)
    mins = et.hour * 60 + et.minute
    keep = np.zeros(len(idx), dtype=bool)
    for a, b, _ in KZ:
        keep |= (mins >= a) & (mins < b)
    keep &= (mins % STEP_MIN == 0) & (et.dayofweek < 5)
    return idx[keep]


def outcomes(df, times, pip=PIP):
    """race (+1 up first / -1 down first / 0 none), fwd1, fwd4 pips (long sense), price at t."""
    import numpy as np
    c = df["c"].values
    h = df["h"].values
    l = df["l"].values
    idx = df.index
    pos = idx.searchsorted(times, side="right") - 1          # M1 bar closing at/just before t+1min
    n = len(c)
    race = np.zeros(len(times), dtype=int)
    f1 = np.full(len(times), np.nan)
    f4 = np.full(len(times), np.nan)
    tv = idx.values
    for k, p in enumerate(pos):
        if p < 0 or p + 1 >= n:
            continue
        px = c[p]
        end = min(n, p + 1 + RACE_CAP_MIN)
        up = np.nonzero(h[p + 1:end] >= px + RACE_PIPS * pip)[0]
        dn = np.nonzero(l[p + 1:end] <= px - RACE_PIPS * pip)[0]
        u = up[0] if len(up) else 10 ** 9
        d = dn[0] if len(dn) else 10 ** 9
        if u < d:
            race[k] = 1
        elif d < u:
            race[k] = -1
        for mins, arr in ((60, f1), (240, f4)):
            j = idx.searchsorted(times[k] + np.timedelta64(mins, "m"), side="right") - 1
            if j > p and (tv[j] - tv[p]) <= np.timedelta64(mins + 30, "m"):
                arr[k] = (c[j] - px) / pip
    return race, f1, f4


# ─────────────────────────────── report ───────────────────────────────

def cl_mean(x, g):
    """Mean and DAY-CLUSTERED standard error. Checks 15 min apart share the same dollar call
    and the same 4h outcome, so they are not independent; the naive SE was 3-5x too small
    (the random-walk null read +5..+14pp 'significant' lifts with it)."""
    import numpy as np
    ok = ~np.isnan(x)
    x, g = x[ok], g[ok]
    n = len(x)
    if n == 0:
        return float("nan"), float("nan")
    m = x.mean()
    e = x - m
    _, inv = np.unique(g, return_inverse=True)
    sg = np.bincount(inv, weights=e)
    return m, math.sqrt((sg ** 2).sum()) / n


def cell(dirs, race, f1, f4, days):
    import numpy as np
    m = dirs != 0
    n = int(m.sum())
    if n < 20:
        return None
    r = race[m]
    hitv = np.where(r == 0, np.nan, (r == dirs[m]).astype(float) * 100)
    hit, se_h = cl_mean(hitv, days[m])
    a1, s1 = cl_mean(dirs[m] * f1[m], days[m])
    a4, s4 = cl_mean(dirs[m] * f4[m], days[m])
    return dict(n=n, days=len(np.unique(days[m])), hit=hit, se=se_h, f1=a1, f1se=s1, f4=a4, f4se=s4)


def fmt(c):
    if c is None:
        return "—"
    return (f"{c['n']}/{c['days']}d / {c['hit']:.1f}% ({c['hit']-50:+.1f}±{c['se']:.1f}) / "
            f"{c['f1']:+.2f}±{c['f1se']:.2f} / {c['f4']:+.2f}±{c['f4se']:.2f}")


def run(frames, title):
    import numpy as np
    import pandas as pd
    dxy = reader_frame(frames["UDXUSD"])
    cross = reader_frame(frames["EURGBP"]) if "EURGBP" in frames else None
    lines = [f"# {title}", "",
             "Cell = n checks/days / race hit% (lift vs coin ± SE) / fwd 1h pips ± SE / fwd 4h pips ± SE, "
             "in the called PAIR direction (dollar up = pair down). Coin = 50% / 0 / 0. "
             "Costs NOT deducted (~1.3 pips spread + slippage per trade). "
             "± = DAY-CLUSTERED SE (pooled across pairs: the three pairs on one day are one dollar bet). "
             "A reader is real only if its lift clears 2 SE in IS, OOS AND 2026 with the same sign.", ""]
    per_pair = {}
    for pair in PAIRS:
        if pair not in frames:
            continue
        df = frames[pair]
        times = decision_times(df.index)
        race, f1, f4 = outcomes(df, times)
        vals = {}
        for tf in ("h1", "h4", "d"):
            v, cols = asof(dxy[tf], times)
            for j, col in enumerate(cols):
                vals[col] = -v[:, j]                      # dollar up -> pair down
        years = times.tz_convert(NY).year
        split = np.array([split_of(y) for y in years])
        sess = np.where(times.tz_convert(NY).hour < 6, "london", "ny")
        days = np.asarray(times.tz_convert(NY).date, dtype="datetime64[D]").astype("int64")
        per_pair[pair] = dict(times=times, race=race, f1=f1, f4=f4, vals=vals, split=split,
                              sess=sess, years=years, days=days)

    for split in ("IS", "OOS", "2026"):
        lines += [f"## {split}", "", "| reader | " + " | ".join(per_pair) + " | ALL |",
                  "|---|" + "---|" * (len(per_pair) + 1)]
        for rd in READERS:
            row = [rd]
            all_d, all_r, all_1, all_4, all_g = [], [], [], [], []
            for pair, P in per_pair.items():
                m = P["split"] == split
                d = P["vals"][rd][m]
                row.append(fmt(cell(d, P["race"][m], P["f1"][m], P["f4"][m], P["days"][m])))
                all_d.append(d); all_r.append(P["race"][m]); all_1.append(P["f1"][m]); all_4.append(P["f4"][m])
                all_g.append(P["days"][m])
            row.append(fmt(cell(np.concatenate(all_d), np.concatenate(all_r),
                                np.concatenate(all_1), np.concatenate(all_4), np.concatenate(all_g))))
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # by year, ALL pairs, for the three main readers (drift check: a trend year can flatter a reader)
    lines += ["## By year (all pairs pooled)", "", "| reader | " +
              " | ".join(str(y) for y in range(2022, 2027)) + " |", "|---|" + "---|" * 5]
    for rd in READERS:
        row = [rd]
        for y in range(2022, 2027):
            ds, rs, a1, a4, gs = [], [], [], [], []
            for P in per_pair.values():
                m = P["years"] == y
                ds.append(P["vals"][rd][m]); rs.append(P["race"][m]); a1.append(P["f1"][m]); a4.append(P["f4"][m])
                gs.append(P["days"][m])
            c = cell(np.concatenate(ds), np.concatenate(rs), np.concatenate(a1), np.concatenate(a4),
                     np.concatenate(gs))
            row.append("—" if c is None else f"{c['hit']-50:+.1f}±{c['se']:.1f} / {c['f4']:+.1f}±{c['f4se']:.1f}")
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "(cell = race lift pp ± SE / fwd 4h pips ± SE)", ""]

    # pair selection
    if cross is not None and "EURUSD" in per_pair and "GBPUSD" in per_pair:
        E, G = per_pair["EURUSD"], per_pair["GBPUSD"]
        common = E["times"].intersection(G["times"])
        ie = E["times"].get_indexer(common)
        ig = G["times"].get_indexer(common)
        lines += ["## Pair selection — DXY x EURGBP quadrant", "",
                  "sel = chosen pair's 4h pips in the called direction minus the other pair's "
                  "4h pips in the same direction (> 0 = the quadrant picked the better pair). "
                  "n / sel ± SE / chosen-pair fwd4 / other-pair fwd4.", "",
                  "| reader | IS | OOS | 2026 |", "|---|---|---|---|"]
        for rd in ("bos_h1", "latch_h1", "bos_h4", "latch_h4", "mom_h1", "ema_h1", "prev_d", "d2s"):
            tf = rd.split("_")[-1] if rd not in ("prev_d", "d2s") else "d"
            tf = {"h1": "h1", "h4": "h4", "d": "d"}[tf]
            dv, cols = asof(dxy[tf], common)
            cv, _ = asof(cross[tf], common)
            j = cols.index(rd)
            dol = dv[:, j]
            cr = cv[:, j]
            row = [rd]
            for split in ("IS", "OOS", "2026"):
                sel, ch, ot, gd = [], [], [], []
                for k in range(len(common)):
                    if E["split"][ie[k]] != split:
                        continue
                    pair, pdir = quadrant(dol[k], cr[k])
                    if pair is None:
                        continue
                    fe, fg = E["f4"][ie[k]], G["f4"][ig[k]]
                    if np.isnan(fe) or np.isnan(fg):
                        continue
                    a, b = (fe, fg) if pair == "EURUSD" else (fg, fe)
                    sel.append(pdir * (a - b)); ch.append(pdir * a); ot.append(pdir * b)
                    gd.append(E["days"][ie[k]])
                if len(sel) < 20:
                    row.append("—")
                else:
                    s = np.array(sel)
                    sm, sse = cl_mean(s, np.array(gd))
                    row.append(f"{len(s)} / {sm:+.2f}±{sse:.2f} / "
                               f"{np.mean(ch):+.2f} / {np.mean(ot):+.2f}")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    return "\n".join(lines)


def selftest():
    import numpy as np
    h = np.array([1.0] * 22 + [1.0]); l = np.array([0.9] * 22 + [0.9]); c = np.array([0.95] * 22 + [1.05])
    b = bos_series(h, l, c)
    assert b[-1] == 1 and b[:-1].sum() == 0, b
    c2 = c.copy(); c2[-1] = 0.85
    assert bos_series(h, l, c2)[-1] == -1
    lat = latch_series(np.array([0, 1, 0, 0, -1, 0]), span=2)
    assert list(lat) == [0, 1, 1, 0, -1, -1], lat
    assert list(d2s_series(np.array([1, 2, 1.5]), np.array([0, 1, 0.5]))) == [0, 1, -1]
    assert quadrant(1, 1) == ("GBPUSD", -1) and quadrant(1, -1) == ("EURUSD", -1)
    assert quadrant(-1, 1) == ("EURUSD", 1) and quadrant(-1, -1) == ("GBPUSD", 1)
    assert quadrant(0, 1) == (None, 0)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "dollar_read_report.md"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    syms = PAIRS + ["UDXUSD", "EURGBP"]
    if a.null:
        base = {"EURUSD": 1.10, "GBPUSD": 1.27, "NZDUSD": 0.62, "UDXUSD": 100.0, "EURGBP": 0.86}
        scale = {"UDXUSD": 0.006}
        frames = {s: null_frame(11 + i, base[s], scale.get(s, 0.00006), days=1700)
                  for i, s in enumerate(syms)}
        title = "P120 dollar-read study — NULL (independent random walks)"
    else:
        frames = {}
        for s in syms:
            df = load_utc(s)
            if df is None:
                print("missing", s)
                continue
            frames[s] = df
            print(s, len(df), df.index[0], df.index[-1])
        if "UDXUSD" not in frames:
            sys.exit("UDXUSD required")
        title = "P120 dollar-read study — does the DXY read predict the pairs on COMPLETED bars?"
    txt = run(frames, title)
    with open(a.out, "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
