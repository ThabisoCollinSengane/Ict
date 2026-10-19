"""P116 — Patrick Nill's "P / b" model: IMPULSE -> RANGE, strongest at the WEEKLY VALUE AREA.

Mechanised from third-party summaries of his videos (see CLAUDE.md P116). Pure price, M15 setups,
M5 execution, COMPLETED bars only for every decision.

  value area  — prior week's Market Profile by TIME (TPO): M5 closes binned, POC, then grow the band
                to 70% of the week's bars -> VAH / VAL. Built only from the finished prior week.
  impulse     — an M15 move of >= IMP_K (0.4) x daily ATR(14) within IMP_BARS (16 = 4h) completed bars.
  range       — the bars right after the impulse stay inside a box no wider than RNG_W x the impulse
                for >= RNG_MIN bars; the box edges are fixed once it qualifies. It ends when a bar
                closes beyond an edge by > BRK_FRAC x the box width (the breakout).
  trades      — `fade`: the first touch of a box edge after it qualifies, faded back to the opposite
                edge (his range "ping-pong"); stop beyond the edge by STOP_FRAC x width.
                `bopb`: after the breakout in the IMPULSE direction, the first pullback that touches
                the broken edge; target one box width beyond it, stop at the box midpoint.
                Max hold 3 days, spread charged on every trade, stop wins a shared bar.
  at_va       — the box overlaps VAH or VAL (± VA_TOL x ATR). `else` (the control) = all other boxes.

Read AT-VA vs ELSE in every period (2022-23 / 2024-25 / 2026) — the value area must add something
over the same pattern anywhere else, or it is not his edge.

  python scripts/nill_study.py            # -> data/nill_report.md
  python scripts/nill_study.py --null     # random walk through the same code
  python scripts/nill_study.py --selftest
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tf_combo_study as base   # loader + null frame (reads SYM_YYYY.csv and SYM_YYYY_MM.csv)

ROOT = base.ROOT
SYMS = ["EURUSD", "GBPUSD", "NZDUSD", "XAUUSD", "SPXUSD", "NSXUSD"]
SPREAD = {"EURUSD": 0.00010, "GBPUSD": 0.00012, "NZDUSD": 0.00018, "XAUUSD": 0.35,
          "SPXUSD": 0.6, "NSXUSD": 2.0}
IMP_K = float(os.environ.get("NILL_IMP_K", "0.4"))     # impulse: >= 0.4 x daily ATR ...
IMP_BARS = int(os.environ.get("NILL_IMP_BARS", "16"))   # ... within 4 hours of M15
RNG_W, RNG_MIN = 0.5, 8           # range: <= half the impulse, >= 2 hours
BRK_FRAC, STOP_FRAC = 0.25, 0.25
VA_TOL, VA_PCT = 0.10, 0.70
HOLD_M5 = 3 * 288


def value_area(closes, bin_size, pct=VA_PCT):
    """TPO value area from a list of closes (one per M5 bar = equal time)."""
    import numpy as np
    if len(closes) < 50 or bin_size <= 0:
        return None
    b = np.floor(np.asarray(closes) / bin_size).astype(np.int64)
    lo_b = b.min()
    counts = np.bincount(b - lo_b)
    poc = int(counts.argmax())
    total, need = counts.sum(), pct * counts.sum()
    lo = hi = poc
    acc = counts[poc]
    while acc < need and (lo > 0 or hi < len(counts) - 1):
        up = counts[hi + 1] if hi + 1 < len(counts) else -1
        dn = counts[lo - 1] if lo > 0 else -1
        if up >= dn:
            hi += 1
            acc += up
        else:
            lo -= 1
            acc += dn
    return (lo + lo_b) * bin_size, (hi + lo_b + 1) * bin_size


def walk(d, entry, stop, target, hi, lo, cl):
    import numpy as np
    R = abs(entry - stop)
    if R <= 0 or len(hi) == 0:
        return None
    s = np.nonzero(lo <= stop)[0] if d > 0 else np.nonzero(hi >= stop)[0]
    t = np.nonzero(hi >= target)[0] if d > 0 else np.nonzero(lo <= target)[0]
    ks = s[0] if len(s) else 10 ** 9
    kt = t[0] if len(t) else 10 ** 9
    if kt < ks:
        return abs(target - entry) / R, True
    if ks < 10 ** 9:
        return -1.0, False
    return d * (cl[-1] - entry) / R, False


def events_for(sym, df):
    import numpy as np
    import pandas as pd
    agg = {"o": "first", "h": "max", "l": "min", "c": "last"}
    m5 = df.resample("5min").agg(agg).dropna()
    m15 = df.resample("15min").agg(agg).dropna()
    d1 = df.resample("1D").agg(agg).dropna()
    cnt = df["c"].resample("1D").count()
    d1 = d1[cnt.reindex(d1.index).fillna(0) >= 120]
    tr = pd.concat([d1.h - d1.l, (d1.h - d1.c.shift()).abs(), (d1.l - d1.c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    atr_t = d1.index
    # weekly value areas from the finished prior week
    wk = m5.c.groupby(m5.index.tz_convert(None).to_period("W-SUN"))
    va = {}
    for per, closes in wk:
        a = atr.asof(per.start_time.tz_localize("UTC")) if len(atr.dropna()) else np.nan
        if not a or np.isnan(a):
            continue
        va[per + 1] = value_area(closes.values, a / 40.0)
    t5 = m5.index.values
    h5, l5, c5 = m5.h.values, m5.l.values, m5.c.values
    T, H, L, C = m15.index, m15.h.values, m15.l.values, m15.c.values
    cost = SPREAD.get(sym, 0.0001)
    out = []
    i = IMP_BARS
    n = len(C)
    while i < n - RNG_MIN - 2:
        di = atr_t.searchsorted(T[i].normalize()) - 1          # last COMPLETED day
        a = atr.iloc[di] if di >= 14 else np.nan
        mv = C[i] - C[i - IMP_BARS]
        if not (a > 0) or abs(mv) < IMP_K * a:
            i += 1
            continue
        d_imp = 1 if mv > 0 else -1
        origin = C[i - IMP_BARS]
        imp = abs(mv)
        # range right after the impulse
        j, bh, bl = i + 1, H[i + 1], L[i + 1]
        while j + 1 < n and max(bh, H[j + 1]) - min(bl, L[j + 1]) <= RNG_W * imp:
            j += 1
            bh, bl = max(bh, H[j]), min(bl, L[j])
        if j - i < RNG_MIN:
            i += 1
            continue
        box_hi, box_lo = bh, bl
        width = box_hi - box_lo
        q_time = T[j] + pd.Timedelta(minutes=15)                # box known after bar j completes
        per = T[i].tz_convert(None).to_period("W-SUN")
        vab = va.get(per)
        at_va = False
        if vab:
            tol = VA_TOL * a
            for lvl in vab:
                if box_lo - tol <= lvl <= box_hi + tol:
                    at_va = True
        yr = T[i].year
        base_rec = dict(sym=sym, split=base.split_of(yr), at_va=at_va, imp_dir=d_imp, date=T[i])
        k0 = int(np.searchsorted(t5, q_time.to_datetime64()))
        kend = min(len(c5), k0 + HOLD_M5)
        done_fade = done_bo = False
        broke = 0
        for k in range(k0, kend):
            # breakout (completed M5 close beyond an edge)
            if not broke:
                if c5[k] > box_hi + BRK_FRAC * width:
                    broke = 1
                    continue
                if c5[k] < box_lo - BRK_FRAC * width:
                    broke = -1
                    continue
                if not done_fade and (h5[k] >= box_hi or l5[k] <= box_lo):
                    side = -1 if h5[k] >= box_hi else 1                  # fade the touched edge
                    entry = (box_hi if side < 0 else box_lo) + side * cost
                    stop = (box_hi + STOP_FRAC * width) if side < 0 else (box_lo - STOP_FRAC * width)
                    target = box_lo if side < 0 else box_hi
                    r = walk(side, entry, stop, target, h5[k + 1:kend], l5[k + 1:kend], c5[k + 1:kend])
                    if r:
                        out.append(dict(base_rec, kind="fade", with_imp=(side == d_imp), r=r[0], win=r[1]))
                    done_fade = True
            elif broke == d_imp and not done_bo:
                edge = box_hi if d_imp > 0 else box_lo
                if (d_imp > 0 and l5[k] <= edge) or (d_imp < 0 and h5[k] >= edge):
                    entry = edge + d_imp * cost
                    stop = (box_hi + box_lo) / 2
                    target = edge + d_imp * width
                    r = walk(d_imp, entry, stop, target, h5[k + 1:kend], l5[k + 1:kend], c5[k + 1:kend])
                    if r:
                        out.append(dict(base_rec, kind="bopb", with_imp=True, r=r[0], win=r[1]))
                    done_bo = True
            if done_fade and (done_bo or broke == -d_imp):
                break
        i = j + 1
    return out


def stats(rows):
    if not rows:
        return None
    rs = [x["r"] for x in rows]
    w = sum(r for r in rs if r > 0)
    l = -sum(r for r in rs if r < 0)
    return len(rs), 100.0 * sum(x["win"] for x in rows) / len(rs), sum(rs) / len(rs), (w / l if l else float("inf"))


def report(ev, title):
    L = [f"# {title}", "",
         "n / win rate / average R per trade (spread included) / PF in R. **AT VA** = the range sits on "
         "last week's value area high or low; **ELSE** = the same pattern anywhere else (control). "
         "`fade` = range edge faded to the opposite edge (with_imp = the fade runs in the impulse "
         "direction, i.e. bought the bottom of a P / sold the top of a b); `bopb` = breakout in the "
         "impulse direction, entered on the pullback to the broken edge.", ""]
    splits = [s for s in ("IS", "OOS", "2026") if any(x["split"] == s for x in ev)]
    L += ["| setup | split | AT VA | ELSE | gap avg R |", "|---|---|---|---|---|"]
    groups = [("fade, all", lambda x: x["kind"] == "fade"),
              ("fade, toward impulse", lambda x: x["kind"] == "fade" and x["with_imp"]),
              ("fade, against impulse", lambda x: x["kind"] == "fade" and not x["with_imp"]),
              ("breakout-pullback", lambda x: x["kind"] == "bopb")]
    f = lambda s: "—" if not s else f"{s[0]} / {s[1]:.0f}% / {s[2]:+.2f} / {s[3]:.2f}"
    for name, fn in groups:
        for sp in splits:
            a = stats([x for x in ev if fn(x) and x["split"] == sp and x["at_va"]])
            e = stats([x for x in ev if fn(x) and x["split"] == sp and not x["at_va"]])
            gap = "—" if not a or not e else f"{a[2] - e[2]:+.2f}"
            L.append(f"| {name} | {sp} | {f(a)} | {f(e)} | {gap} |")
    L += ["", "## By instrument (all setups, AT VA | ELSE)", "", "| symbol | split | AT VA | ELSE |", "|---|---|---|---|"]
    for sym in sorted({x["sym"] for x in ev}):
        for sp in splits:
            rows = [x for x in ev if x["sym"] == sym and x["split"] == sp]
            L.append(f"| {sym} | {sp} | {f(stats([x for x in rows if x['at_va']]))} | "
                     f"{f(stats([x for x in rows if not x['at_va']]))} |")
    return "\n".join(L)


def selftest():
    import numpy as np
    vah_val = value_area([1.0] * 70 + [2.0] * 20 + [3.0] * 10, 1.0)
    assert vah_val == (1.0, 2.0), vah_val
    r = walk(1, 1.0, 0.9, 1.2, np.array([1.05, 1.21]), np.array([0.95, 1.0]), np.array([1.0, 1.2]))
    assert r == (2.0000000000000004, True) or abs(r[0] - 2.0) < 1e-9
    r = walk(1, 1.0, 0.9, 1.2, np.array([1.25]), np.array([0.85]), np.array([1.0]))
    assert r == (-1.0, False)                      # stop wins a shared bar
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--syms", nargs="+", default=SYMS)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "nill_report.md"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    ev = []
    if a.null:
        for seed in (1, 2, 3):
            ev += events_for("EURUSD", base.null_frame(seed))
        title = "P116 NULL (random walk) — AT VA and ELSE should match"
    else:
        for sym in a.syms:
            df = base.load_utc(sym)
            if df is None:
                print(f"{sym}: no data")
                continue
            e = events_for(sym, df)
            print(f"{sym}: M1 {len(df):,}  setups {len(e)}", flush=True)
            ev += e
        title = "P116 — Patrick Nill P/b impulse->range at the weekly value area (pure price)"
    if not ev:
        print("no events")
        return
    txt = report(ev, title)
    print(txt)
    with open(a.out, "w") as fh:
        fh.write(txt + "\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
