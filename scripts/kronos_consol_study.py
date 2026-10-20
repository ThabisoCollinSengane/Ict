"""P122 — can KRONOS read the consolidation -> breakout cycle the strategy trades?

Pure price, COMPLETED M15 bars only, EURUSD / GBPUSD / NZDUSD, CLEAN window only (Kronos's
pretraining reportedly ends 2024-06, so this study starts 2024-07). Two questions:

Q1  EXPANSION TIMING. At 03/04/07/08/09:00 ET, when a consolidation (the engine's own
    `_find_best_range`: 8-96 M15 bars, <= 35 pips, both extremes touched >= 2x) is live and
    unbroken, how big are the next 16 M15 bars (4h) and does price leave the range?
    Kronos predictor = median over sampled paths of the path's high-low range.
    BASELINES it must beat: ATR = mean high-low of the last 16 bars, and HOUR = the ET hour.
    Score: Spearman rank correlation of each predictor with the realised range, and Kronos's
    correlation with what is LEFT after the baselines (residual of log realised range on
    log ATR + hour dummies). Day-block bootstrap SE.

Q2  JUDAS OR BREAKOUT. At the first completed killzone M15 bar that trades through a range
    extreme (one side only; 16-bar cooldown per pair), what happens next within 16 bars:
    FAKEOUT = a close back inside the range before price extends a full range-width beyond the
    broken edge; BREAKOUT = the extension comes first; neither / same bar = unresolved.
    Kronos p_fake = share of its sampled paths that resolve as a fakeout.
    BASELINE = the engine's rule: break bar CLOSED back inside -> fakeout, else breakout.
    Scores: accuracy vs the base rate and vs the rule (day-clustered SE), realised fakeout rate
    by Kronos tercile, and a trade sim from the break bar close (1 pip cost, M15 path, stop
    first on a shared bar): FADE (stop beyond the break bar's extreme + 1 pip, 2R) or FOLLOW
    (stop at the range middle, 2R), chosen by Kronos / by the rule / always fade / always
    follow / coin.

  --events --pair P --start S --end E   detect events, run Kronos, write data/kronos_consol/*.csv
  --report                              score all event files -> data/kronos_consol_report.md
"""
import argparse
import glob
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dollar_read_study as drs   # noqa: E402

NY = drs.NY
PIP = 0.0001
H = 16                        # bars ahead (M15 -> 4h)
CTX = int(os.environ.get("KRONOS_CTX", "256"))
SAMPLES = int(os.environ.get("KRONOS_SAMPLES", "12"))
BATCH = int(os.environ.get("KRONOS_BATCH", "4"))
OUT_DIR = os.path.join(ROOT, "data", "kronos_consol")
KZ = ((3 * 60, 5 * 60), (7 * 60, 10 * 60))
CHECK_HOURS = (3, 4, 7, 8, 9)
COST = 1.0


# ─────────────────────────────── pure logic ───────────────────────────────

def levels(side, hi, lo, width):
    """Equidistant outcome levels around the broken edge: FAKEOUT = a close back half a range
    inside the edge, BREAKOUT = a close half a range beyond it. (v1 used 'any close back inside'
    vs 'a full range beyond' — so lopsided that a random walk read 93% fakeouts.)"""
    edge = hi if side > 0 else lo
    return edge - side * width / 2, edge + side * width / 2


def classify(side, hi, lo, width, highs, lows, closes):
    """Fakeout (+1) / breakout (-1) / unresolved (0) for a break of `side` (+1 = above hi),
    judged on CLOSES against the two equidistant levels."""
    fake, brk = levels(side, hi, lo, width)
    for c in closes:
        if (c - fake) * side <= 0:
            return 1
        if (c - brk) * side >= 0:
            return -1
    return 0


def sim_trade(d, entry, stop, highs, lows, rr=2.0, cost=COST, pip=PIP):
    """R of a trade from entry (cost paid at entry) with a fixed stop and rr x target, walking
    bars; stop first when both are inside one bar; exit at the last close if neither."""
    entry = entry + d * cost * pip
    r = abs(entry - stop)
    if r <= 0 or (stop - entry) * d >= 0:
        return None
    tgt = entry + d * rr * r
    for h, l in zip(highs, lows):
        hit_s = (l <= stop) if d > 0 else (h >= stop)
        hit_t = (h >= tgt) if d > 0 else (l <= tgt)
        if hit_s:
            return -1.0
        if hit_t:
            return rr
    return None


def spearman(a, b):
    import numpy as np
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a))
    rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def boot_corr(x, y, days, reps=300, seed=1):
    import numpy as np
    rng = np.random.default_rng(seed)
    ud, inv = np.unique(days, return_inverse=True)
    groups = [np.nonzero(inv == i)[0] for i in range(len(ud))]
    vals = []
    for _ in range(reps):
        pick = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        vals.append(spearman(x[pick], y[pick]))
    return spearman(x, y), float(np.std(vals))


# ─────────────────────────────── events ───────────────────────────────

def m15(df):
    import pandas as pd
    b = df.resample("15min").agg({"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()
    return b


def build_events(pair, start, end):
    import numpy as np
    import pandas as pd
    from ict.amd import _find_best_range
    df = drs.load_utc(pair)
    b = m15(df)
    Bar = __import__("collections").namedtuple("Bar", "Open High Low Close")
    bars = [Bar(*r) for r in b[["o", "h", "l", "c"]].itertuples(index=False, name=None)]
    t = b.index
    et = t.tz_convert(NY)
    mins = et.hour * 60 + et.minute
    in_kz = np.zeros(len(t), bool)
    for a, z in KZ:
        in_kz |= (mins >= a) & (mins < z)
    lo_t, hi_t = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
    pip = PIP
    ev, last_break = [], -10 ** 9
    for k in range(CTX + 100, len(bars) - H - 1):
        if not (lo_t <= t[k] < hi_t) or et[k].dayofweek >= 5:
            continue
        check = in_kz[k] and et[k].minute == 0 and et[k].hour in CHECK_HOURS
        brk = in_kz[k] and k - last_break >= H
        if not (check or brk):
            continue
        rng = _find_best_range(bars, k, 8, 96, 35 * pip, 1.0 * pip, 2)
        if rng is None:
            continue
        hi, lo, w = rng.high, rng.low, rng.high - rng.low
        fut = b.iloc[k + 1:k + 1 + H]
        bk = bars[k]
        up, dn = bk.High > hi, bk.Low < lo
        if brk and (up != dn):
            side = 1 if up else -1
            outcome = classify(side, hi, lo, w, fut.h.values, fut.l.values, fut.c.values)
            back_inside = (bk.Close < hi) if side > 0 else (bk.Close > lo)
            fk, bl = levels(side, hi, lo, w)
            near_fake = int(abs(bk.Close - fk) < abs(bk.Close - bl))
            ext = bk.High if side > 0 else bk.Low
            mid = (hi + lo) / 2
            fade = sim_trade(-side, bk.Close, ext + side * pip, fut.h.values, fut.l.values)
            follow = sim_trade(side, bk.Close, mid, fut.h.values, fut.l.values)
            ev.append(dict(kind="break", k=k, t=t[k].isoformat(), side=side, hi=hi, lo=lo,
                           width_pips=w / pip, outcome=outcome, rule_fake=int(back_inside),
                           near_fake=near_fake,
                           r_fade=fade, r_follow=follow))
            last_break = k
        elif check and not (up or dn):
            real = (fut.h.max() - fut.l.min()) / pip
            left = int(((fut.c > hi) | (fut.c < lo)).any())
            atr = float((b.h.iloc[k - 15:k + 1] - b.l.iloc[k - 15:k + 1]).mean() / pip)
            ev.append(dict(kind="check", k=k, t=t[k].isoformat(), hi=hi, lo=lo, width_pips=w / pip,
                           real_range=real, left_range=left, atr=atr, hour=int(et[k].hour)))
    return b, ev


def run_events(pair, start, end, max_minutes):
    import numpy as np
    import pandas as pd
    import kronos_bridge
    os.makedirs(OUT_DIR, exist_ok=True)
    b, ev = build_events(pair, start, end)
    print(pair, start, end, "events", len(ev), {k: sum(e["kind"] == k for e in ev) for k in ("break", "check")})
    t0 = time.time()
    done = []
    for i in range(0, len(ev), BATCH):
        chunk = ev[i:i + BATCH]
        frames = [b.iloc[e["k"] + 1 - CTX:e["k"] + 1][["o", "h", "l", "c"]] for e in chunk]
        try:
            P = kronos_bridge.paths(frames, pred_len=H, samples=SAMPLES, seed=i)
        except Exception as ex:
            print("kronos failed", ex)
            continue
        for e, pp in zip(chunk, P):
            hs, ls, cs = pp[:, :, 1], pp[:, :, 2], pp[:, :, 3]
            if e["kind"] == "break":
                res = [classify(e["side"], e["hi"], e["lo"], e["hi"] - e["lo"], hs[s], ls[s], cs[s])
                       for s in range(len(pp))]
                nf, nb = sum(r == 1 for r in res), sum(r == -1 for r in res)
                e["k_pfake"] = nf / (nf + nb) if nf + nb else np.nan
                e["k_resolved"] = (nf + nb) / len(res)
            else:
                rngs = (hs.max(axis=1) - ls.min(axis=1)) / PIP
                e["k_range"] = float(np.median(rngs))
                e["k_leave"] = float(np.mean([((cs[s] > e["hi"]) | (cs[s] < e["lo"])).any()
                                             for s in range(len(pp))]))
            e["pair"] = pair
            done.append(e)
        el = (time.time() - t0) / 60
        if (i // BATCH) % 20 == 0:
            print(f"{pair} {i + len(chunk)}/{len(ev)} {el:.1f} min", flush=True)
        if el > max_minutes:
            print("time budget reached")
            break
    out = os.path.join(OUT_DIR, f"kc_{pair}_{start[:7]}_{end[:7]}.csv")
    pd.DataFrame(done).to_csv(out, index=False)
    print("wrote", out, len(done))


# ─────────────────────────────── report ───────────────────────────────

def split_of(ts):
    return "2024-07..2025-12" if ts.year <= 2025 else "2026"


def report(out_path):
    import numpy as np
    import pandas as pd
    files = sorted(glob.glob(os.path.join(OUT_DIR, "kc_*.csv")))
    if not files:
        sys.exit("no event files")
    d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    d["t"] = pd.to_datetime(d["t"], utc=True)
    d["day"] = d["t"].dt.tz_convert(NY).dt.date.astype(str)
    d["split"] = d["t"].map(split_of)
    L = ["# P122 — Kronos on the consolidation -> breakout cycle (CLEAN window only)", "",
         f"Kronos (KRONOS_MODEL={os.environ.get('KRONOS_MODEL', 'Kronos-small')}), context {CTX} completed M15 "
         f"bars, {SAMPLES} sampled paths, horizon {H} M15 bars (4h). EURUSD/GBPUSD/NZDUSD from 2024-07.",
         f"Files: {len(files)}; events: {len(d)} ({(d.kind == 'check').sum()} checks, "
         f"{(d.kind == 'break').sum()} breaks).", ""]
    # Q1
    c = d[d.kind == "check"].dropna(subset=["k_range"])
    L += ["## Q1 — does Kronos see the EXPANSION coming? (rank corr with the realised 4h range)", "",
          "Kronos must beat ATR (recent bar size) and HOUR (time of day). `Kronos | left over` = its "
          "correlation with what ATR + hour do NOT explain — the only number that says it adds "
          "anything. ± = day-block bootstrap SE.", "",
          "| period | n | Kronos | ATR | HOUR (mean range of that hour) | Kronos | left over | "
          "left-range rate: Kronos top vs bottom third |", "|---|---|---|---|---|---|---|"]
    for sp in ("2024-07..2025-12", "2026", "ALL"):
        s = c if sp == "ALL" else c[c.split == sp]
        if len(s) < 30:
            L.append(f"| {sp} | {len(s)} | — | — | — | — | — |")
            continue
        days = s["day"].values
        y = np.log(s["real_range"].clip(lower=0.5).values)
        kr, kse = boot_corr(s["k_range"].values, y, days)
        ar, ase = boot_corr(s["atr"].values, y, days)
        hm = s.groupby("hour")["real_range"].transform("mean").values
        hr, hse = boot_corr(hm, y, days)
        X = np.column_stack([np.ones(len(s)), np.log(s["atr"].clip(lower=0.5).values)] +
                            [(s["hour"].values == h).astype(float) for h in sorted(s.hour.unique())[1:]])
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        resid = y - X @ beta
        rr, rse = boot_corr(s["k_range"].values, resid, days)
        q = s["k_range"].quantile([1 / 3, 2 / 3]).values
        top = s[s.k_range >= q[1]]["left_range"].mean() * 100
        bot = s[s.k_range <= q[0]]["left_range"].mean() * 100
        L.append(f"| {sp} | {len(s)} | {kr:+.3f}±{kse:.3f} | {ar:+.3f}±{ase:.3f} | {hr:+.3f}±{hse:.3f} | "
                 f"{rr:+.3f}±{rse:.3f} | {top:.0f}% vs {bot:.0f}% |")
    # Q2
    k = d[d.kind == "break"].copy()
    L += ["", "## Q2 — Judas (fakeout) or real breakout?", "",
          "Accuracy on resolved breaks (fakeout = close half a range back inside the edge, breakout = "
          "close half a range beyond it, whichever first). BASE = always guess the period's more common "
          "outcome; RULE = the engine's 'break bar closed back inside' read; NEAR = whichever level the "
          "break bar's close is nearer to (pure geometry — what a random walk would do); KRONOS = "
          "majority of its sampled paths. Kronos must beat NEAR, not just 50%. ± = day-clustered SE.", "",
          "| period | resolved | fakeout share | BASE | RULE | NEAR | KRONOS | KRONOS - NEAR |",
          "|---|---|---|---|---|---|---|---|"]
    for sp in ("2024-07..2025-12", "2026", "ALL"):
        s = k if sp == "ALL" else k[k.split == sp]
        s = s[(s.outcome != 0) & s.k_pfake.notna()]
        if len(s) < 30:
            L.append(f"| {sp} | {len(s)} | — | — | — | — | — | — |")
            continue
        g = s["day"].values
        truth = (s.outcome == 1).astype(int).values
        fs = truth.mean()
        base = (truth == int(fs >= 0.5)).astype(float) * 100
        rule = (s.rule_fake.values == truth).astype(float) * 100
        kron = ((s.k_pfake.values >= 0.5).astype(int) == truth).astype(float) * 100
        bm, bse = drs.cl_mean(base, g)
        rm, rse = drs.cl_mean(rule, g)
        km_, kse = drs.cl_mean(kron, g)
        near = (s.near_fake.values == truth).astype(float) * 100
        nm, nse = drs.cl_mean(near, g)
        dm, dse = drs.cl_mean(kron - near, g)
        L.append(f"| {sp} | {len(s)} | {fs*100:.0f}% | {bm:.1f}±{bse:.1f} | {rm:.1f}±{rse:.1f} | "
                 f"{nm:.1f}±{nse:.1f} | {km_:.1f}±{kse:.1f} | {dm:+.1f}±{dse:.1f} |")
    L += ["", "Realised fakeout rate by Kronos p_fake tercile (resolved breaks):", "",
          "| period | low p_fake | mid | high |", "|---|---|---|---|"]
    for sp in ("2024-07..2025-12", "2026", "ALL"):
        s = k if sp == "ALL" else k[k.split == sp]
        s = s[(s.outcome != 0) & s.k_pfake.notna()]
        if len(s) < 30:
            continue
        q = s.k_pfake.quantile([1 / 3, 2 / 3]).values
        cells = []
        for m in (s.k_pfake <= q[0], (s.k_pfake > q[0]) & (s.k_pfake < q[1]), s.k_pfake >= q[1]):
            cells.append(f"{(s[m].outcome == 1).mean()*100:.0f}% (n {m.sum()})")
        L.append(f"| {sp} | " + " | ".join(cells) + " |")
    L += ["", "## Q2 trade sim — fade vs follow, 2R, 1 pip cost (avg R ± day-clustered SE, n)", "",
          "| period | always FADE | always FOLLOW | RULE picks | KRONOS picks | COIN picks |",
          "|---|---|---|---|---|---|"]
    rng = np.random.default_rng(7)
    for sp in ("2024-07..2025-12", "2026", "ALL"):
        s = k if sp == "ALL" else k[k.split == sp]
        s = s[s.k_pfake.notna()]
        if len(s) < 30:
            continue
        g = s["day"].values
        fade, foll = s.r_fade.values.astype(float), s.r_follow.values.astype(float)
        coin = rng.integers(0, 2, len(s)).astype(bool)
        picks = {"always FADE": fade, "always FOLLOW": foll,
                 "RULE picks": np.where(s.rule_fake.values == 1, fade, foll),
                 "KRONOS picks": np.where(s.k_pfake.values >= 0.5, fade, foll),
                 "COIN picks": np.where(coin, fade, foll)}
        cells = []
        for name, v in picks.items():
            ok = ~np.isnan(v)
            m, se = drs.cl_mean(v[ok], g[ok])
            cells.append(f"{m:+.3f}±{se:.3f} (n {ok.sum()})")
        L.append(f"| {sp} | " + " | ".join(cells) + " |")
    L.append("")
    txt = "\n".join(L)
    with open(out_path, "w") as f:
        f.write(txt + "\n")
    print(txt)


def selftest():
    # break above 1.1010, width 10 pips: fake level 1.1005, breakout level 1.1015 (closes)
    assert classify(1, 1.1010, 1.1000, 0.0010, [0, 0], [0, 0], [1.1008, 1.1004]) == 1
    assert classify(1, 1.1010, 1.1000, 0.0010, [0, 0], [0, 0], [1.1012, 1.1016]) == -1
    assert classify(1, 1.1010, 1.1000, 0.0010, [0, 0], [0, 0], [1.1012, 1.1008]) == 0
    # short-side mirror: break below 1.1000 -> fake 1.1005, breakout 1.0995
    assert classify(-1, 1.1010, 1.1000, 0.0010, [0], [0], [1.0994]) == -1
    assert classify(-1, 1.1010, 1.1000, 0.0010, [0], [0], [1.1006]) == 1
    assert levels(1, 1.1010, 1.1000, 0.0010) == (1.1005, 1.1015)
    # trade sim: long from 1.1000, stop 1.0990 -> R 11 pips with cost, target 1.1023
    assert sim_trade(1, 1.1000, 1.0990, [1.1024], [1.0995]) == 2.0
    assert sim_trade(1, 1.1000, 1.0990, [1.1030], [1.0989]) == -1.0      # stop first on shared bar
    assert sim_trade(1, 1.1000, 1.1005, [1.1030], [1.0989]) is None      # wrong-side stop
    assert abs(spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1) < 1e-9
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--events", action="store_true")
    ap.add_argument("--pair")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--max-minutes", type=float, default=280)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "kronos_consol_report.md"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    if a.events:
        run_events(a.pair, a.start, a.end, a.max_minutes)
    if a.report:
        report(a.out)


if __name__ == "__main__":
    main()
