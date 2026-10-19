"""P114 — which TIMEFRAME COMBO gives the best intraday entries and risk? (pure price, M1 exec)

Trader (2026-10-19): use time + candlestick theory (price action), loop over 5 timeframe
combos from W1 down to M1, and find which alignment produces the best entry signals and risk
management for intraday trading. M1 is ALWAYS the last layer (trigger + stop).

Every combo = (bias TF, draw TF, setup TF) -> M1 execution:
  C1  W   -> D   -> H1  -> M1      (swing read, intraday execution)
  C2  D   -> H4  -> M15 -> M1
  C3  D   -> H1  -> M5  -> M1      (JadeCap "short-term": daily bias, 1H)
  C4  H4  -> H1  -> M15 -> M1      (JadeCap "day trading": 4H/1H -> 15M/5M)
  C5  H1  -> M15 -> M5  -> M1      (scalping)

One identical recipe per combo, COMPLETED bars only at every layer:
  bias   (candlestick theory) — last completed bias-TF candle vs the one before: HH+HL = up,
         LH+LL = down, outside bar = its body direction, inside bar = no bias.
  setup  (price action)       — the FIRST touch of an unfilled setup-TF FVG (an imbalance left by a
         displacement candle), during a killzone (time theory: London 03:00-05:00 ET, NY
         07:00-10:00 ET). Direction = the gap's direction (bullish gap -> long).
  exec   (M1)                 — after the touch, the first M1 close through the last M1 3-bar swing
         that formed after the touch (structure shift), within 60 M1 bars and before the
         killzone ends; invalid if a close goes through the gap's far side first.
         Stop = the pullback extreme since the touch -/+ 1 pip. Entry = that close + 1 pip cost.
  draw   (target)             — the nearest unfilled draw-TF FVG AHEAD of price (positional, P75),
         known before the entry; its near edge is the target; must be >= 1R away.
  time   — trades close by 16:00 ET the same day (intraday); open trades are marked there.
  candle theory flag `manip`  — the entry sits on the DISCOUNT side of the forming bias-TF candle's
         open (long below the open, short above it): in a bullish candle the low forms first, below the
         open (open-low-high-close), so buying below the open buys the candle's manipulation leg.

Groups: WITH = setup direction agrees with the bias; AGAINST = opposite (the control: identical
machinery, opposite alignment). If alignment carries information, WITH beats AGAINST, in BOTH
halves. Read the gap, not the raw rates.

Metrics per combo / group / split: trades and trades/week, win rate to the draw, average R net of
cost, PF in R, hit 1R / 2R before the stop, the same entries with a fixed 2R target, median stop
in pips, % stopped inside 15 minutes (noise stops), median minutes in trade.

  python scripts/tf_combo_study.py            # data/histdata -> data/tf_combo_report.md
  python scripts/tf_combo_study.py --null     # random walk through the same code
  python scripts/tf_combo_study.py --selftest
"""
import argparse
import glob
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "data", "histdata")
PAIRS = ["EURUSD", "GBPUSD", "NZDUSD"]
COMBOS = [("C1", "W", "D", "60min"), ("C2", "D", "240min", "15min"), ("C3", "D", "60min", "5min"),
          ("C4", "240min", "60min", "15min"), ("C5", "60min", "15min", "5min")]
LABEL = {"W": "W1", "D": "D1", "240min": "H4", "60min": "H1", "15min": "M15", "5min": "M5"}
PIP = 0.0001
COST_PIPS = 1.0
BUF_PIPS = 1.0
MIN_STOP_PIPS = 2.0
EXEC_BARS = 60
KZ = ((3 * 60, 5 * 60, "london"), (7 * 60, 10 * 60, "ny"))
NY = "America/New_York"


def split_of(year):
    return "IS" if year <= 2023 else ("OOS" if year <= 2025 else "2026")


# ─────────────────────────────── pure pieces ───────────────────────────────

def bias_of(ph, pl, po, pc, qh, ql):
    """Candlestick read: candle p (newer) vs q (older)."""
    if ph > qh and pl > ql:
        return 1
    if ph < qh and pl < ql:
        return -1
    if ph > qh and pl < ql:
        return 1 if pc > po else (-1 if pc < po else 0)
    return 0


def fvgs(h, l, c, min_size):
    """3-candle gaps on arrays. Returns list of (i, dir, bottom, top); i = the 3rd candle."""
    out = []
    for i in range(2, len(h)):
        if l[i] > h[i - 2] and l[i] - h[i - 2] >= min_size:
            out.append((i, 1, h[i - 2], l[i]))
        elif h[i] < l[i - 2] and l[i - 2] - h[i] >= min_size:
            out.append((i, -1, h[i], l[i - 2]))
    return out


def m1_shift(d, hi, lo, cl, bottom, top, max_bars):
    """From the touch bar (index 0), the first close through the last M1 3-bar swing formed after
    the touch. Returns (k, stop_extreme) or None. Invalid if a close goes through the far side."""
    n = min(len(hi), max_bars)
    swing = None
    ext = lo[0] if d > 0 else hi[0]
    for k in range(1, n):
        ext = min(ext, lo[k]) if d > 0 else max(ext, hi[k])
        if (d > 0 and cl[k] < bottom) or (d < 0 and cl[k] > top):
            return None
        j = k - 1
        if j >= 1:
            if d > 0 and hi[j] > hi[j - 1] and hi[j] > hi[k]:
                swing = hi[j]
            if d < 0 and lo[j] < lo[j - 1] and lo[j] < lo[k]:
                swing = lo[j]
        if swing is not None and ((d > 0 and cl[k] > swing) or (d < 0 and cl[k] < swing)):
            return k, ext
    return None


def walk(d, entry, stop, target, hi, lo, cl):
    """First passage to stop or target (stop wins a shared bar). Returns
    (R_result, hit_target, mfe_R, bars_to_exit, stopped)."""
    import numpy as np
    R = abs(entry - stop)
    if len(hi) == 0:
        return 0.0, False, 0.0, 0, False
    if d > 0:
        s_hit = np.nonzero(lo <= stop)[0]
        t_hit = np.nonzero(hi >= target)[0]
    else:
        s_hit = np.nonzero(hi >= stop)[0]
        t_hit = np.nonzero(lo <= target)[0]
    ks = s_hit[0] if len(s_hit) else 10 ** 9
    kt = t_hit[0] if len(t_hit) else 10 ** 9
    upto = min(ks, len(hi))
    fav = ((hi[:upto].max() - entry) if d > 0 else (entry - lo[:upto].min())) if upto > 0 else 0.0
    mfe = max(fav, 0.0) / R
    if kt < ks:
        return abs(target - entry) / R, True, mfe, kt + 1, False
    if ks < 10 ** 9:
        return -1.0, False, mfe, ks + 1, True
    return d * (cl[-1] - entry) / R, False, mfe, len(hi), False


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


def null_frame(seed, days=1460):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-03", periods=days * 1440, freq="1min", tz="UTC")
    idx = idx[idx.dayofweek < 5]
    c = 1.10 + np.cumsum(rng.normal(0, 0.00006, len(idx)))
    o = np.r_[c[0], c[:-1]]
    w = np.abs(rng.normal(0, 0.00003, len(idx)))
    return pd.DataFrame({"o": o, "h": np.maximum(o, c) + w, "l": np.minimum(o, c) - w, "c": c},
                        index=idx)


def bars(df, rule):
    """Resampled bars + the time each bar is COMPLETE (= next bar's open, or open + span)."""
    import pandas as pd
    agg = {"o": "first", "h": "max", "l": "min", "c": "last"}
    if rule == "W":
        b = df.resample("W-SUN", label="left", closed="left").agg(agg).dropna()
        span = pd.Timedelta(days=7)
    elif rule == "D":
        b = df.resample("1D").agg(agg).dropna()
        cnt = df["c"].resample("1D").count()
        b = b[cnt.reindex(b.index).fillna(0) >= 120]
        span = pd.Timedelta(days=1)
    else:
        b = df.resample(rule, label="left", closed="left").agg(agg).dropna()
        span = pd.Timedelta(rule)
    b["done"] = b.index + span
    return b


class TFData:
    def __init__(self, b, min_size):
        import numpy as np
        self.t = b.index
        self.done = b["done"].values
        self.o, self.h, self.l, self.c = (b[k].values for k in ("o", "h", "l", "c"))
        g = fvgs(self.h, self.l, self.c, min_size)
        self.g_i = np.array([x[0] for x in g], dtype=int)
        self.g_dir = np.array([x[1] for x in g], dtype=int)
        self.g_bot = np.array([x[2] for x in g])
        self.g_top = np.array([x[3] for x in g])
        self.g_known = self.done[self.g_i] if len(g) else np.array([], dtype="datetime64[ns]")
        mit = []
        far_inf = np.datetime64("2100-01-01")
        for i, d, bo, tp in g:
            cc = self.c[i + 1:]
            k = np.nonzero(cc <= bo)[0] if d > 0 else np.nonzero(cc >= tp)[0]
            mit.append(self.done[i + 1 + k[0]] if len(k) else far_inf)
        self.g_mit = np.array(mit, dtype="datetime64[ns]") if mit else np.array([], dtype="datetime64[ns]")


def events_for(sym, df, pip=PIP):
    import numpy as np
    import pandas as pd
    min_size = 3 * pip
    m_t = df.index
    m_t64 = m_t.values
    mh, ml, mc, mo = (df[k].values for k in ("h", "l", "c", "o"))
    et = m_t.tz_convert(NY)
    et_min = (et.hour * 60 + et.minute).values
    et_day = et.normalize()
    out = []
    cache = {}

    def tfd(rule):
        if rule not in cache:
            cache[rule] = TFData(bars(df, rule), min_size)
        return cache[rule]

    for name, b_rule, d_rule, s_rule in COMBOS:
        B, Dw, S = tfd(b_rule), tfd(d_rule), tfd(s_rule)
        seen = set()
        for gi in range(len(S.g_i)):
            d, bo, tp = S.g_dir[gi], S.g_bot[gi], S.g_top[gi]
            s0 = m_t64.searchsorted(S.g_known[gi])
            s1 = min(len(mh), s0 + 1440)
            if s0 >= s1:
                continue
            touch = np.nonzero((ml[s0:s1] <= tp) if d > 0 else (mh[s0:s1] >= bo))[0]
            if not len(touch):
                continue
            k0 = s0 + touch[0]
            if m_t64[k0] >= S.g_mit[gi]:
                continue
            mins = et_min[k0]
            kz = [z for z in KZ if z[0] <= mins < z[1]]
            if not kz:
                continue
            kz_end = kz[0][1]
            # bias from the last two COMPLETED bias-TF candles at the touch
            bi = B.t.values.searchsorted(m_t64[k0], side="right") - 1      # forming candle
            if bi < 2:
                continue
            p, q = bi - 1, bi - 2
            if B.done[p] > m_t64[k0]:
                continue
            bias = bias_of(B.h[p], B.l[p], B.o[p], B.c[p], B.h[q], B.l[q])
            if bias == 0:
                continue
            group = "with" if bias == d else "against"
            # M1 execution
            n_left = int(np.searchsorted(et_min[k0:k0 + EXEC_BARS], kz_end))
            sh = m1_shift(d, mh[k0:k0 + EXEC_BARS], ml[k0:k0 + EXEC_BARS], mc[k0:k0 + EXEC_BARS],
                          bo, tp, max(2, n_left))
            if sh is None:
                continue
            kk, ext = sh
            ke = k0 + kk
            entry = mc[ke] + d * COST_PIPS * pip
            stop = ext - d * BUF_PIPS * pip
            R = abs(entry - stop)
            if R < MIN_STOP_PIPS * pip or (d > 0 and stop >= entry) or (d < 0 and stop <= entry):
                continue
            day = et_day[ke]
            key = (name, group, str(day.date()), kz[0][2])
            if key in seen:
                continue
            # draw: nearest unfilled draw-TF gap AHEAD, known before entry
            tnow = m_t64[ke]
            ok = (Dw.g_known <= tnow) & (Dw.g_mit > tnow)
            if d > 0:
                ok &= Dw.g_bot > entry
                near = Dw.g_bot
            else:
                ok &= Dw.g_top < entry
                near = Dw.g_top
            if not ok.any():
                continue
            cand = near[ok]
            target = cand.min() if d > 0 else cand.max()
            if abs(target - entry) < R:
                continue
            seen.add(key)
            # candle theory: is the entry on the DISCOUNT side of the forming bias candle's open
            # (long below the open / short above it) — ICT "buy below the open on a bullish day"
            manip = bool((entry < B.o[bi]) if d > 0 else (entry > B.o[bi]))
            end = int(np.searchsorted(m_t64, (day + pd.Timedelta(hours=16)).tz_convert("UTC").to_datetime64()))
            if end <= ke + 1:
                continue
            fh, fl, fc = mh[ke + 1:end], ml[ke + 1:end], mc[ke + 1:end]
            r_draw, hit, mfe, nbar, stopped = walk(d, entry, stop, target, fh, fl, fc)
            r_2r, hit2, _, _, _ = walk(d, entry, stop, entry + d * 2 * R, fh, fl, fc)
            out.append(dict(sym=sym, combo=name, group=group, split=split_of(day.year),
                            kz=kz[0][2], manip=manip, r=r_draw, win=hit, r2=r_2r,
                            mfe=mfe, stop_pips=R / pip, early=stopped and nbar <= 15,
                            mins=nbar, tgt_R=abs(target - entry) / R, date=day))
    return out


# ─────────────────────────────── report ───────────────────────────────

def stats(rows):
    if not rows:
        return None
    n = len(rows)
    rs = [x["r"] for x in rows]
    gw = sum(r for r in rs if r > 0)
    gl = -sum(r for r in rs if r < 0)
    r2 = [x["r2"] for x in rows]
    w2 = sum(r for r in r2 if r > 0)
    l2 = -sum(r for r in r2 if r < 0)
    srt = lambda k: sorted(x[k] for x in rows)[n // 2]
    return dict(n=n, wr=100.0 * sum(x["win"] for x in rows) / n, avgR=sum(rs) / n,
                pf=(gw / gl) if gl else float("inf"),
                h1=100.0 * sum(x["mfe"] >= 1 for x in rows) / n,
                h2=100.0 * sum(x["mfe"] >= 2 for x in rows) / n,
                avg2=sum(r2) / n, pf2=(w2 / l2) if l2 else float("inf"),
                stop=srt("stop_pips"), early=100.0 * sum(x["early"] for x in rows) / n,
                mins=srt("mins"), tgt=srt("tgt_R"))


def weeks(rows):
    if not rows:
        return 1.0
    ds = sorted(x["date"] for x in rows)
    return max(1.0, (ds[-1] - ds[0]).days / 7.0)


def report(ev, title):
    L = [f"# {title}", "",
         "Each row: trades / per week / win rate to the draw / average R per trade net of 1 pip cost "
         "/ PF in R / % that reached 1R and 2R before the stop / the same entries with a FIXED 2R "
         "target (avg R, PF) / median stop pips / % stopped within 15 min / median minutes in trade "
         "/ median target distance in R. **WITH** = setup agrees with the bias candle; **AGAINST** = "
         "the control (same machinery, opposite alignment). Read the WITH-minus-AGAINST gap in BOTH "
         "halves.", ""]
    splits = [s for s in ("IS", "OOS", "2026") if any(x["split"] == s for x in ev)]
    hdr = ("| combo | group | split | n | /wk | WR | avg R | PF | 1R% | 2R% | 2R avg | 2R PF | "
           "stop pips | early% | mins | tgt R |")
    sep = "|" + "---|" * 16
    L += ["## 1. Every combo", "", hdr, sep]
    for name, b, d, s in COMBOS:
        lab = f"{name} {LABEL[b]}>{LABEL[d]}>{LABEL[s]}>M1"
        for g in ("with", "against"):
            for sp in splits:
                rows = [x for x in ev if x["combo"] == name and x["group"] == g and x["split"] == sp]
                st = stats(rows)
                if not st:
                    continue
                L.append(f"| {lab} | {g} | {sp} | {st['n']} | {st['n'] / weeks(rows):.1f} | "
                         f"{st['wr']:.0f}% | {st['avgR']:+.2f} | {st['pf']:.2f} | {st['h1']:.0f} | "
                         f"{st['h2']:.0f} | {st['avg2']:+.2f} | {st['pf2']:.2f} | {st['stop']:.1f} | "
                         f"{st['early']:.0f} | {st['mins']} | {st['tgt']:.1f} |")
    L += ["", "## 2. The alignment gap (WITH minus AGAINST), avg R per trade and 1R-reach",
          "", "| combo | split | WITH avg R | AGAINST avg R | gap R (± SE) | 1R% gap |", "|---|---|---|---|---|---|"]
    for name, b, d, s in COMBOS:
        for sp in splits:
            a = [x for x in ev if x["combo"] == name and x["group"] == "with" and x["split"] == sp]
            c = [x for x in ev if x["combo"] == name and x["group"] == "against" and x["split"] == sp]
            if len(a) < 5 or len(c) < 5:
                continue
            ra, rc = [x["r"] for x in a], [x["r"] for x in c]
            ma, mc_ = sum(ra) / len(ra), sum(rc) / len(rc)
            va = sum((x - ma) ** 2 for x in ra) / max(1, len(ra) - 1)
            vc = sum((x - mc_) ** 2 for x in rc) / max(1, len(rc) - 1)
            se = math.sqrt(va / len(ra) + vc / len(rc))
            h = (100.0 * sum(x["mfe"] >= 1 for x in a) / len(a)
                 - 100.0 * sum(x["mfe"] >= 1 for x in c) / len(c))
            L.append(f"| {name} | {sp} | {ma:+.2f} | {mc_:+.2f} | {ma - mc_:+.2f} ± {se:.2f} | {h:+.1f} |")
    L += ["", "## 3. Candle theory: WITH trades split by entry vs the forming bias candle's OPEN "
          "(discount = long below the open / short above it)", "", "| combo | split | discount n / WR / avg R | premium n / WR / avg R |",
          "|---|---|---|---|"]
    for name, b, d, s in COMBOS:
        for sp in splits:
            w = [x for x in ev if x["combo"] == name and x["group"] == "with" and x["split"] == sp]
            if not w:
                continue
            cells = []
            for flag in (True, False):
                st = stats([x for x in w if x["manip"] == flag])
                cells.append("—" if not st else f"{st['n']} / {st['wr']:.0f}% / {st['avgR']:+.2f}")
            L.append(f"| {name} | {sp} | {cells[0]} | {cells[1]} |")
    L += ["", "## 4. Time: WITH trades by killzone", "", "| combo | split | London n / WR / avg R | NY n / WR / avg R |",
          "|---|---|---|---|"]
    for name, b, d, s in COMBOS:
        for sp in splits:
            w = [x for x in ev if x["combo"] == name and x["group"] == "with" and x["split"] == sp]
            if not w:
                continue
            cells = []
            for z in ("london", "ny"):
                st = stats([x for x in w if x["kz"] == z])
                cells.append("—" if not st else f"{st['n']} / {st['wr']:.0f}% / {st['avgR']:+.2f}")
            L.append(f"| {name} | {sp} | {cells[0]} | {cells[1]} |")
    return "\n".join(L)


def selftest():
    import numpy as np
    assert bias_of(3, 1.5, 1, 2, 2, 1) == 1 and bias_of(1.9, 0.5, 1, 0.8, 2, 1) == -1
    assert bias_of(3, 0.5, 1, 2, 2, 1) == 1 and bias_of(3, 0.5, 2, 1, 2, 1) == -1
    assert bias_of(1.8, 1.2, 1, 1.5, 2, 1) == 0
    h = np.array([1.0, 1.1, 1.3]); l = np.array([0.9, 1.0, 1.2]); c = h
    g = fvgs(h, l, c, 0.05)
    assert g == [(2, 1, 1.0, 1.2)], g
    # M1 shift (long): touch, dip, swing high at index 2, break at index 4
    hi = np.array([1.00, 1.01, 1.03, 1.02, 1.05]); lo = np.array([0.99, 0.98, 1.00, 1.00, 1.02])
    cl = np.array([0.995, 1.00, 1.02, 1.01, 1.04])
    assert m1_shift(1, hi, lo, cl, 0.95, 1.00, 10) == (4, 0.98)
    assert m1_shift(1, hi, lo, np.array([0.995, 0.94, 1.02, 1.01, 1.04]), 0.95, 1.00, 10) is None
    r, hit, mfe, n, st = walk(1, 1.0, 0.99, 1.02, np.array([1.005, 1.021]), np.array([0.995, 1.0]),
                              np.array([1.0, 1.02]))
    assert hit and abs(r - 2.0) < 1e-9 and n == 2
    r, hit, mfe, n, st = walk(1, 1.0, 0.99, 1.02, np.array([1.005, 1.0]), np.array([0.985, 1.0]),
                              np.array([1.0, 1.0]))
    assert st and r == -1.0
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--pairs", nargs="+", default=PAIRS)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "tf_combo_report.md"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    ev = []
    if a.null:
        for seed in (1, 2, 3):
            ev += events_for(f"NULL{seed}", null_frame(seed))
        title = "P114 NULL (random walk) — WITH and AGAINST should match"
    else:
        for sym in a.pairs:
            df = load_utc(sym)
            if df is None:
                print(f"{sym}: no data")
                continue
            print(f"{sym}: M1 {len(df):,} {df.index[0]} -> {df.index[-1]}", flush=True)
            e = events_for(sym, df)
            print(f"  events {len(e)}", flush=True)
            ev += e
        title = "P114 — timeframe combos W1 -> M1: which alignment gives the best intraday entries?"
    if not ev:
        print("no events")
        return
    txt = report(ev, title)
    print(txt)
    with open(a.out, "w") as f:
        f.write(txt + "\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
