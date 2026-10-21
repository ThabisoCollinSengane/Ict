"""P123 — is Kronos's EXPANSION read (P122 Q1) its own, or just a longer volatility window?

P122 Q1 found Kronos's predicted 4h range correlates +0.14 (both clean periods, ~5 SE) with
what is LEFT of the realised 4h range after log ATR(16 M15 bars = 4h) + hour. But Kronos reads
256 bars (64h), so it may only be re-telling a longer volatility window. This re-scores the SAME
P122 check events (data/kronos_consol/kc_*.csv — no Kronos re-run) against stronger baselines,
all from COMPLETED M15 bars up to and including the decision bar k (the future is k+1..k+16):

  atr16   mean high-low, last 16 bars (P122's baseline)
  atr256  mean high-low, last 256 bars (exactly Kronos's window)
  rv256   std of close-to-close moves, last 256 bars
  adr20   mean range of the last 20 completed UTC days;  pdr = the last completed day's range
  seas20  mean realised 4h range from the SAME clock time over the previous 28 calendar days
  width   the live consolidation's width;  + hour and pair dummies

Reported: Kronos's residual rank corr after (a) P122's controls, (b) + atr256, (c) everything;
out-of-sample R² gain of adding log Kronos to the full baseline (fit one period, score the
other); and, for the engine filter, the leave-the-range rate and realised range by tercile of
Kronos's OWN opinion (log k_range residualised on the full baseline). Sanity rows: a pure-noise
predictor and a 'mimic' (log atr256 + noise) must read ~0 after the full controls.
"""
import argparse
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dollar_read_study as drs   # noqa: E402
import kronos_consol_study as kcs  # noqa: E402

PIP = kcs.PIP
H = kcs.H
SPLITS = ("2024-07..2025-12", "2026")
BASE = ["atr16", "atr256", "rv256", "adr20", "pdr", "seas20", "width"]


def baselines(b, times):
    """b = M15 frame (o/h/l/c, bar-open UTC index). times = decision-bar open times.
    Returns a DataFrame of baselines indexed like `times`, using bars <= the decision bar only."""
    import numpy as np
    import pandas as pd
    rng = (b.h - b.l) / PIP
    atr16 = rng.rolling(16).mean()
    atr256 = rng.rolling(256).mean()
    rv256 = (b.c.diff() / PIP).rolling(256).std()
    # realised range of the NEXT 16 bars, labelled at the decision bar (used only for PAST days)
    fh = b.h[::-1].rolling(H).max()[::-1].shift(-1)
    fl = b.l[::-1].rolling(H).min()[::-1].shift(-1)
    fr = (fh - fl) / PIP
    d = b.resample("1D").agg({"h": "max", "l": "min"}).dropna()
    d["rng"] = (d.h - d.l) / PIP
    d["done"] = d.index + pd.Timedelta("1D")
    out = []
    for t in times:
        k = b.index.get_loc(t)
        past = d[d.done <= t + pd.Timedelta("15min")]["rng"]
        seas = fr.reindex([t - pd.Timedelta(days=n) for n in range(1, 29)]).dropna()
        out.append(dict(atr16=atr16.iloc[k], atr256=atr256.iloc[k], rv256=rv256.iloc[k],
                        adr20=past.iloc[-20:].mean() if len(past) >= 20 else np.nan,
                        pdr=past.iloc[-1] if len(past) else np.nan,
                        seas20=seas.iloc[-20:].mean() if len(seas) >= 10 else np.nan))
    return pd.DataFrame(out, index=times)


def design(s, cols):
    import numpy as np
    X = [np.ones(len(s))] + [np.log(s[c].clip(lower=0.1).values) for c in cols]
    for h in sorted(s.hour.unique())[1:]:
        X.append((s.hour.values == h).astype(float))
    for p in sorted(s.pair.unique())[1:]:
        X.append((s.pair.values == p).astype(float))
    return np.column_stack(X)


def resid(y, X):
    import numpy as np
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return y - X @ beta


def oos_r2(tr, te, cols, extra):
    """R² on `te` of a model fit on `tr`, baseline vs baseline + log `extra`."""
    import numpy as np
    out = []
    for c in (cols, cols + [extra]):
        hours = sorted(set(tr.hour) & set(te.hour))
        pairs = sorted(set(tr.pair) & set(te.pair))
        a, b = tr[tr.hour.isin(hours) & tr.pair.isin(pairs)], te[te.hour.isin(hours) & te.pair.isin(pairs)]
        Xa, Xb = design(a, c), design(b, c)
        ya, yb = np.log(a.real_range.clip(lower=0.5).values), np.log(b.real_range.clip(lower=0.5).values)
        beta = np.linalg.lstsq(Xa, ya, rcond=None)[0]
        e = yb - Xb @ beta
        out.append(1 - (e ** 2).sum() / ((yb - yb.mean()) ** 2).sum())
    return out


def score(c, lines):
    import numpy as np
    rs = np.random.default_rng(3)
    c = c.copy()
    c["noise"] = np.exp(rs.normal(size=len(c)))
    c["mimic"] = np.exp(np.log(c.atr256.values) + 0.3 * rs.normal(size=len(c)))
    lines += ["## Rank corr with the realised 4h range (± day-block bootstrap SE)", "",
              "| period | n | Kronos | " + " | ".join(BASE) + " |", "|---|---|---" + "|---" * len(BASE) + "|"]
    for sp in SPLITS + ("ALL",):
        s = c if sp == "ALL" else c[c.split == sp]
        y = np.log(s.real_range.clip(lower=0.5).values)
        cells = [f"{kcs.boot_corr(s[v].values, y, s.day.values, reps=150)[0]:+.3f}" for v in ["k_range"] + BASE]
        lines.append(f"| {sp} | {len(s)} | " + " | ".join(cells) + " |")
    lines += ["", "## Kronos's corr with what the baselines LEAVE (the test)", "",
              "| period | (a) P122: atr16 + hour | (b) + atr256 | (c) everything | noise, after (c) | "
              "mimic, after (c) |", "|---|---|---|---|---|---|"]
    for sp in SPLITS + ("ALL",):
        s = c if sp == "ALL" else c[c.split == sp]
        y = np.log(s.real_range.clip(lower=0.5).values)
        g = s.day.values
        cells = []
        for cols, pred in ((["atr16"], "k_range"), (["atr16", "atr256"], "k_range"),
                           (BASE, "k_range"), (BASE, "noise"), (BASE, "mimic")):
            r, se = kcs.boot_corr(s[pred].values, resid(y, design(s, cols)), g)
            cells.append(f"{r:+.3f}±{se:.3f}")
        lines.append(f"| {sp} | " + " | ".join(cells) + " |")
    lines += ["", "## Out-of-sample R² of log realised range (fit one period, score the other)", "",
              "| fit -> score | full baseline | + log Kronos | gain |", "|---|---|---|---|"]
    a, b = c[c.split == SPLITS[0]], c[c.split == SPLITS[1]]
    for (tr, te, name) in ((a, b, f"{SPLITS[0]} -> {SPLITS[1]}"), (b, a, f"{SPLITS[1]} -> {SPLITS[0]}")):
        if len(tr) < 100 or len(te) < 100:
            continue
        r0, r1 = oos_r2(tr, te, BASE, "k_range")
        lines.append(f"| {name} | {r0:.3f} | {r1:.3f} | {r1 - r0:+.3f} |")
    lines += ["", "## Kronos's OWN opinion (log k_range residualised on the full baseline), by tercile", "",
              "What an engine filter would act on. Cells: price closes outside the range within 4h % / "
              "median realised 4h range pips / median baseline-predicted pips. Terciles cut on the "
              "first period and applied to both.", "",
              "| period | low third | mid | top third | top - low leave-rate ± SE |", "|---|---|---|---|---|"]
    a = c[c.split == SPLITS[0]]
    beta = np.linalg.lstsq(design(a, BASE), np.log(a.k_range.clip(lower=0.1).values), rcond=None)[0]
    by = np.linalg.lstsq(design(a, BASE), np.log(a.real_range.clip(lower=0.5).values), rcond=None)[0]
    q = None
    for sp in SPLITS:
        s = c[c.split == sp]
        X = design(s, BASE)
        if X.shape[1] != len(beta):
            continue
        own = np.log(s.k_range.clip(lower=0.1).values) - X @ beta
        if q is None:
            q = np.quantile(own, [1 / 3, 2 / 3])
        pred = np.exp(X @ by)
        cells, lv = [], {}
        for name, m in (("low", own <= q[0]), ("mid", (own > q[0]) & (own < q[1])), ("top", own >= q[1])):
            lv[name] = (s.left_range.values * 100.0, m)
            cells.append(f"{s.left_range.values[m].mean()*100:.0f}% / {np.median(s.real_range.values[m]):.1f} / "
                         f"{np.median(pred[m]):.1f} (n {m.sum()})")
        x = np.where(lv["top"][1], lv["top"][0], np.nan)
        z = np.where(lv["low"][1], lv["low"][0], np.nan)
        g = s.day.values
        mt, st = drs.cl_mean(x, g)
        ml, sl = drs.cl_mean(z, g)
        lines.append(f"| {sp} | " + " | ".join(cells) + f" | {mt - ml:+.1f}±{(st**2 + sl**2) ** 0.5:.1f}pp |")
    lines.append("")


def load_checks(files):
    import pandas as pd
    d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    d = d[d.kind == "check"].dropna(subset=["k_range"]).copy()
    d["t"] = pd.to_datetime(d["t"], utc=True)
    d["day"] = d["t"].dt.tz_convert(drs.NY).dt.date.astype(str)
    d["split"] = d["t"].map(kcs.split_of)
    d["hour"] = d["hour"].astype(int)
    d["width"] = d["width_pips"]
    return d


def run(checks, frames, out_path):
    import pandas as pd
    parts = []
    for p, s in checks.groupby("pair"):
        if frames.get(p) is None:
            print("no price data for", p)
            continue
        b = kcs.m15(frames[p])
        s = s[s.t.isin(b.index)]
        bl = baselines(b, pd.DatetimeIndex(s.t))
        parts.append(pd.concat([s.reset_index(drop=True), bl.reset_index(drop=True)], axis=1))
    c = pd.concat(parts, ignore_index=True).dropna(subset=BASE)
    L = ["# P123 — Kronos's expansion read vs longer volatility windows", "",
         f"Same P122 check events (live unbroken consolidation at 03/04/07/08/09 ET), n = {len(c)} "
         f"of {len(checks)} with every baseline available. Pairs: {', '.join(sorted(c.pair.unique()))}.",
         "Kronos survives only if column (c) stays clearly positive in BOTH periods and the "
         "out-of-sample gain is > 0 both ways. noise/mimic must read ~0 (they are the calibration).", ""]
    score(c, L)
    txt = "\n".join(L)
    with open(out_path, "w") as f:
        f.write(txt + "\n")
    print(txt)


def synthetic():
    """Random-walk M15 with volatility regimes; fake 'Kronos' = log atr256 + noise, so after the
    full baseline it must read ~0 (the mimic and noise rows too)."""
    import numpy as np
    import pandas as pd
    rs = np.random.default_rng(0)
    frames, rows = {}, []
    for p in ("EURUSD", "GBPUSD"):
        idx = pd.date_range("2024-01-01", "2026-06-30", freq="1min", tz="UTC")
        vol = np.repeat(np.exp(rs.normal(0, 0.4, len(idx) // 1440 + 1)), 1440)[:len(idx)] * 0.00004
        c = 1.1 + np.cumsum(rs.normal(size=len(idx)) * vol)
        df = pd.DataFrame({"o": c, "h": c + vol, "l": c - vol, "c": c}, index=idx)
        frames[p] = df
        b = kcs.m15(df)
        rng = (b.h - b.l) / PIP
        a256 = rng.rolling(256).mean()
        et = b.index.tz_convert(drs.NY)
        pick = np.nonzero((b.index >= "2024-07-01") & (et.minute == 0) & np.isin(et.hour, (3, 4, 7, 8, 9))
                          & (et.dayofweek < 5))[0]
        for k in pick[: len(pick) - 20]:
            fut = b.iloc[k + 1:k + 1 + H]
            rows.append(dict(kind="check", t=b.index[k].isoformat(), pair=p, hour=int(et[k].hour),
                             width_pips=20.0 + rs.random() * 10, real_range=(fut.h.max() - fut.l.min()) / PIP,
                             left_range=float(rs.random() < 0.6),
                             k_range=float(np.exp(np.log(a256.iloc[k]) + 0.2 * rs.normal()))))
    return frames, pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", action="store_true", help="synthetic random-walk calibration")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "kronos_expansion_report.md"))
    a = ap.parse_args()
    import pandas as pd
    if a.null:
        frames, raw = synthetic()
        tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "kc_null.csv")
        raw.to_csv(tmp, index=False)
        run(load_checks([tmp]), frames, a.out.replace(".md", "_null.md"))
        return
    files = sorted(glob.glob(os.path.join(kcs.OUT_DIR, "kc_*.csv")))
    checks = load_checks(files)
    frames = {p: drs.load_utc(p) for p in checks.pair.unique()}
    run(checks, frames, a.out)


if __name__ == "__main__":
    main()
