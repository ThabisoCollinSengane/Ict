"""P106 — can we tell in advance WHICH market (FX / gold / indices) will deliver today?

    python scripts/instrument_selector_study.py            # needs data/histdata/{SYM}_{Y}.csv
    python scripts/instrument_selector_study.py --null     # random walk through the same code
    python scripts/instrument_selector_study.py --selftest

Pure price, independent of the bot. Instruments: EURUSD, GBPUSD (FX), XAUUSD (gold),
SPXUSD, NSXUSD (S&P 500 / Nasdaq). Sessions (New York time, as the bot): London from
03:00, NY from 07:00. For every instrument x day x session:

OUTCOMES (measured from the session start forward, 5 hours)
  move   |close(+5h) - open(start)| / 20-day average daily range   (directional travel)
  amd    1 if price ran ONE side of the pre-session range and then reached the OTHER side
         (the bot's model: sweep, then deliver to opposing liquidity)

PREDICTORS (known at the session start; only bars strictly before it)
  coil   pre-session range / its own 20-session median    (Asia for London, London for NY)
  er5    5-day efficiency ratio |close - close 5d ago| / sum of daily ranges (trend vs range)
  pos    where the open sits in the prior 5-day dealing range (0 = low, 1 = high);
         reported as |pos - 0.5| (near an edge vs mid-range)
  past   this instrument's average `move` over its previous 10 sessions of the same kind
  session  London vs NY (each instrument's best session)

TESTS
  1. Per instrument and session: average outcome, IS 2022-23 vs OOS 2024-25 (+2026).
  2. Each predictor's rank correlation with `move` and `amd`, per instrument, IS vs OOS.
  3. SELECTOR: fit a small linear model on IS (predictors + instrument x session baseline),
     then in OOS / 2026 pick, every session, the instrument with the highest predicted
     move. Compare the picked instrument's realised move/amd with: the average of all
     instruments, the best FIXED choice learned in IS (e.g. "gold in NY"), and a random pick.
A selector only has value if it beats the FIXED rule out of sample. The --null run must show
no lift (it does: see the selftest).
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "histdata")
SYMS = ["EURUSD", "GBPUSD", "XAUUSD", "SPXUSD", "NSXUSD"]
YEARS = [2022, 2023, 2024, 2025, 2026]
SESS = {"london": (3, (-7, 3)), "ny": (7, (3, 7))}      # start hour ET, pre-range (from, to) hours
WIN_H = 5
PRED = ["coil", "er5", "edge", "past"]


def load(sym):
    fr = []
    import glob
    for y in YEARS:                                  # annual files + 2026 monthly (SYM_2026_01.csv)
        for p in sorted(glob.glob(os.path.join(DATA, f"{sym}_{y}.csv"))
                        + glob.glob(os.path.join(DATA, f"{sym}_{y}_*.csv"))):
            fr.append(pd.read_csv(p, sep=";", header=None, names=["dt", "o", "h", "l", "c", "v"]))
    if not fr:
        return None
    df = pd.concat(fr, ignore_index=True)
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    df = df.drop_duplicates("dt").sort_values("dt").set_index("dt")
    df.index = (df.index + pd.Timedelta(hours=5)).tz_localize("UTC").tz_convert("America/New_York")
    return df[["o", "h", "l", "c"]].resample("5min").agg(
        {"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()


def rows_for(sym, df):
    day = df.resample("1D").agg({"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()
    day = day[day.index.dayofweek < 5]
    rng = (day.h - day.l)
    out = []
    dates = day.index
    for i in range(25, len(dates)):
        d0 = dates[i].normalize()
        prev = day.iloc[i - 20:i]
        adr = (prev.h - prev.l).mean()
        last5 = day.iloc[i - 5:i]
        er5 = abs(last5.c.iloc[-1] - day.c.iloc[i - 6]) / max((last5.h - last5.l).sum(), 1e-12)
        dr_hi, dr_lo = last5.h.max(), last5.l.min()
        for s, (h0, (pf, pt)) in SESS.items():
            t0 = d0 + pd.Timedelta(hours=h0)
            pre = df[(df.index >= d0 + pd.Timedelta(hours=pf)) & (df.index < d0 + pd.Timedelta(hours=pt))]
            win = df[(df.index >= t0) & (df.index < t0 + pd.Timedelta(hours=WIN_H))]
            if len(pre) < 6 or len(win) < 12 or adr <= 0:
                continue
            ph, pl = pre.h.max(), pre.l.min()
            o = win.o.iloc[0]
            # amd: first side swept, then the opposite pre-range extreme reached afterwards
            hi_hit = np.flatnonzero(win.h.to_numpy() > ph)
            lo_hit = np.flatnonzero(win.l.to_numpy() < pl)
            amd = 0
            if len(hi_hit) and len(lo_hit):
                amd = 1
            pos = (o - dr_lo) / max(dr_hi - dr_lo, 1e-12)
            out.append(dict(sym=sym, date=d0, session=s, pre_rng=(ph - pl) / adr,
                            er5=er5, edge=abs(min(max(pos, 0), 1) - 0.5),
                            move=abs(win.c.iloc[-1] - o) / adr, amd=amd))
    r = pd.DataFrame(out)
    if r.empty:
        return r
    r = r.sort_values("date")
    for s in SESS:
        m = r.session == s
        r.loc[m, "coil"] = r.loc[m, "pre_rng"] / r.loc[m, "pre_rng"].rolling(20, min_periods=10).median().shift(1)
        r.loc[m, "past"] = r.loc[m, "move"].rolling(10, min_periods=5).mean().shift(1)
    return r.dropna(subset=["coil", "past"])


def half(d):
    y = d.date.dt.year
    return np.select([y <= 2023, y <= 2025], ["IS", "OOS"], "2026")


def spearman(a, b):
    return pd.Series(a).rank().corr(pd.Series(b).rank())


def report(r):
    r = r.copy()
    r["half"] = half(r)
    L = ["## 1. Average outcome by instrument and session", "",
         "| instrument | session | IS move / amd% | OOS move / amd% | 2026 move / amd% | n IS/OOS/26 |",
         "|---|---|---|---|---|---|"]
    for (sym, s), g in r.groupby(["sym", "session"]):
        cells, ns = [], []
        for h in ("IS", "OOS", "2026"):
            x = g[g.half == h]
            cells.append(f"{x.move.mean():.2f} / {x.amd.mean()*100:.0f}%" if len(x) else "—")
            ns.append(str(len(x)))
        L.append(f"| {sym} | {s} | " + " | ".join(cells) + f" | {'/'.join(ns)} |")
    L += ["", "## 2. Does each predictor rank the outcome? (Spearman, IS / OOS)", "",
          "| instrument | predictor | vs move IS / OOS | vs amd IS / OOS |", "|---|---|---|---|"]
    for sym, g in r.groupby("sym"):
        for p in PRED:
            a = [spearman(g[g.half == h][p], g[g.half == h]["move"]) for h in ("IS", "OOS")]
            b = [spearman(g[g.half == h][p], g[g.half == h]["amd"]) for h in ("IS", "OOS")]
            L.append(f"| {sym} | {p} | {a[0]:+.2f} / {a[1]:+.2f} | {b[0]:+.2f} / {b[1]:+.2f} |")
    # 3. selector
    is_ = r[r.half == "IS"]
    base = is_.groupby(["sym", "session"]).move.mean()
    X = lambda d: np.column_stack([np.ones(len(d))] + [d[p].to_numpy() for p in PRED]
                                  + [d.set_index(["sym", "session"]).index.map(base).to_numpy()])
    coef, *_ = np.linalg.lstsq(X(is_), is_.move.to_numpy(), rcond=None)
    best_fixed = {s: base.xs(s, level="session").idxmax() for s in SESS}
    rng = np.random.default_rng(3)
    L += ["", "## 3. Selector: pick one instrument per session", "",
          f"Model fitted on IS. Best FIXED choice from IS: " +
          ", ".join(f"{s} -> {v}" for s, v in best_fixed.items()) + ".", "",
          "| half | selector move / amd% | fixed best move / amd% | average of all | random pick | sessions |",
          "|---|---|---|---|---|---|"]
    for h in ("IS", "OOS", "2026"):
        d = r[r.half == h].copy()
        if d.empty:
            continue
        d["pred"] = X(d) @ coef
        g = d.groupby(["date", "session"])
        sel = d.loc[g.pred.idxmax()]
        fix = d[d.apply(lambda x: x.sym == best_fixed[x.session], axis=1)]
        rnd = d.groupby(["date", "session"]).sample(1, random_state=rng.integers(1e9))
        L.append(f"| {h} | {sel.move.mean():.3f} / {sel.amd.mean()*100:.0f}% | "
                 f"{fix.move.mean():.3f} / {fix.amd.mean()*100:.0f}% | "
                 f"{d.move.mean():.3f} / {d.amd.mean()*100:.0f}% | "
                 f"{rnd.move.mean():.3f} / {rnd.amd.mean()*100:.0f}% | {g.ngroups} |")
    L += ["", "Model coefficients (const, " + ", ".join(PRED) + ", instrument-session baseline): "
          + ", ".join(f"{c:+.3f}" for c in coef), ""]
    return L


def null_rows():
    rng = np.random.default_rng(1)
    idx = pd.date_range("2022-01-03", "2026-09-30", freq="5min", tz="America/New_York")
    idx = idx[idx.dayofweek < 5]
    rows = []
    for k, sym in enumerate(SYMS):
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.0004 * (1 + k * 0.3), len(idx))))
        df = pd.DataFrame({"o": np.r_[c[0], c[:-1]], "c": c}, index=idx)
        w = np.abs(rng.normal(0, 0.0002, len(idx))) * c
        df["h"] = df[["o", "c"]].max(axis=1) + w
        df["l"] = df[["o", "c"]].min(axis=1) - w
        rows.append(rows_for(sym, df))
    return pd.concat(rows, ignore_index=True)


def selftest():
    r = null_rows()
    assert set(r.session) == {"london", "ny"} and len(r) > 1000
    assert r[PRED + ["move", "amd"]].notna().all().all()
    print(f"selftest ok: {len(r)} null rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default="data/instrument_selector_report.md")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.null:
        r = null_rows()
        title = "RANDOM-WALK NULL (no instrument should be predictable)"
    else:
        parts = []
        for s in SYMS:
            df = load(s)
            print(f"{s}: {0 if df is None else len(df):,} M5 bars")
            if df is not None:
                parts.append(rows_for(s, df))
        r = pd.concat(parts, ignore_index=True)
        title = "HistData M1, " + ", ".join(sorted(r.sym.unique()))
    L = [f"# Which market will deliver? Instrument selector study (P106) — {title}", "",
         f"{len(r):,} instrument-sessions. `move` = 5h directional travel in units of the 20-day "
         "average daily range; `amd` = ran one side of the pre-session range, then the other.", ""]
    L += report(r)
    txt = "\n".join(L) + "\n"
    open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
