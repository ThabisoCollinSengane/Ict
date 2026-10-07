"""P85 — what happens to the MM trades the M1-shift gate SKIPS, and can we catch them late?

Input: trade dumps from a SHADOW run (MM_GOLDEN_ENABLED=1, MM_GOLDEN_M1_SHADOW=1,
MM_GOLDEN_M1_MSS=0). Every MM trade there is the ungated P81 trade, labelled with what
the M1 gate would have said (`m1_diag`) and the zone it filled in (`mm_zone_lo/hi`).

§1  Outcome of the ORIGINAL trade by m1_diag x half — which rejection reasons were
    winners (the "continuation" trades) and which were genuine bad fills.
§2  LATE CATCH — for every rejected trade, walk forward on completed M1 bars from the
    original entry and ask, bar by bar, whether a valid M1 shift (the same rule as
    backtest._m1_shift) has now formed in the same zone. If it does within
    --late-bars, simulate a late entry at that bar's close (+ spread/2 + slippage),
    stop beyond the pullback extreme (+1 pip, min 3, max 10), the ORIGINAL target,
    first touch on later M1 bars (same-bar stop+target = stop), --hold-bars timeout.
    Results in R so different stop sizes compare.
§3  ORIGINAL vs LATE on exactly the same setups, in R.

No lookahead: the shift test at bar k only sees bars <= k; the entry fills at bar k's
close; the outcome is read from bar k+1 on. Run: python scripts/m1_skip_study.py
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "data", "histdata")
EST = pd.Timedelta(hours=5)

LOOKBACK, FRESH, TOL, BUF, MIN_STOP, MAX_STOP = 60, 10, 2.0, 1.0, 3.0, 10.0


def pip_of(pair):
    return 0.01 if pair.endswith("JPY") else 0.0001


def shift_at(h, l, c, k, direction, zlo, zhi, pip):
    """Valid M1 shift whose break bar is k, using bars <= k only (mirrors _m1_shift)."""
    lo = max(0, k - LOOKBACK)
    tol = TOL * pip
    seg_h, seg_l = h[lo:k], l[lo:k]
    if len(seg_h) < 5:
        return None
    if direction > 0:
        li = int(np.argmin(seg_l)); ext = seg_l[li]
        if ext > zhi + tol or ext < zlo - tol:
            return None
        sw = [j for j in range(1, li) if j + 1 < len(seg_h)
              and seg_h[j] > seg_h[j - 1] and seg_h[j] > seg_h[j + 1]]
        if not sw:
            return None
        lvl = seg_h[sw[-1]]
        if c[k] <= lvl or np.any(c[lo + li + 1:k] > lvl):
            return None
        return ext
    li = int(np.argmax(seg_h)); ext = seg_h[li]
    if ext < zlo - tol or ext > zhi + tol:
        return None
    sw = [j for j in range(1, li) if j + 1 < len(seg_l)
          and seg_l[j] < seg_l[j - 1] and seg_l[j] < seg_l[j + 1]]
    if not sw:
        return None
    lvl = seg_l[sw[-1]]
    if c[k] >= lvl or np.any(c[lo + li + 1:k] < lvl):
        return None
    return ext


def simulate(h, l, c, k, direction, entry, stop, target, hold):
    """First touch from bar k+1: +R at target, -1R at stop, mark-to-close at timeout."""
    risk = abs(entry - stop)
    for j in range(k + 1, min(len(c), k + 1 + hold)):
        hit_stop = l[j] <= stop if direction > 0 else h[j] >= stop
        hit_tgt = h[j] >= target if direction > 0 else l[j] <= target
        if hit_stop:
            return -1.0, "stop"
        if hit_tgt:
            return abs(target - entry) / risk, "target"
    j = min(len(c), k + 1 + hold) - 1
    return (c[j] - entry) * direction / risk, "timeout"


def late_catch(m1, row, late_bars, hold, friction_pips):
    pip = pip_of(row.pair)
    t0 = pd.Timestamp(row.opened_at)
    if t0.tzinfo is None:
        t0 = t0.tz_localize("UTC")
    i0 = int(m1.index.searchsorted(t0, side="right"))
    h, l, c = m1["High"].values, m1["Low"].values, m1["Close"].values
    d, zlo, zhi = int(row.direction), float(row.mm_zone_lo), float(row.mm_zone_hi)
    if not (zhi > zlo > 0):
        return None
    for k in range(i0, min(len(c) - 1, i0 + late_bars)):
        # the original target already printed before we would enter -> move is gone
        if (d > 0 and h[k] >= row.target) or (d < 0 and l[k] <= row.target):
            return {"found": False, "why": "target_first"}
        ext = shift_at(h, l, c, k, d, zlo, zhi, pip)
        if ext is None:
            continue
        entry = c[k] + d * friction_pips * pip
        stop = ext - d * BUF * pip
        dist = (entry - stop) * d / pip
        if dist <= 0:
            continue
        if dist < MIN_STOP:
            stop = entry - d * MIN_STOP * pip
        elif dist > MAX_STOP:
            stop = entry - d * MAX_STOP * pip
        if (row.target - entry) * d <= abs(entry - stop):
            return {"found": False, "why": "rr_below_1"}
        r, how = simulate(h, l, c, k, d, entry, stop, row.target, hold)
        return {"found": True, "why": how, "R": r, "delay": k - i0 + 1}
    return {"found": False, "why": "no_shift"}


def orig_r(row):
    risk = abs(row.entry - row.stop)
    return (row.exit - row.entry) * row.direction / risk if risk else np.nan


def pf_r(rs):
    rs = np.asarray(rs, float)
    w, lo = rs[rs > 0].sum(), -rs[rs < 0].sum()
    return w / lo if lo > 0 else float("inf") if w > 0 else float("nan")


def load_pair(pair, years):
    files = []
    for y in years:
        f = os.path.join(DATA, f"{pair}_{y}.csv")
        files += [f] if os.path.exists(f) else sorted(glob.glob(os.path.join(DATA, f"{pair}_{y}_*.csv")))
    if not files:
        return None
    parts = []
    for f in files:
        df = pd.read_csv(f, sep=";", header=None, names=["dt", "Open", "High", "Low", "Close", "V"])
        df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S") + EST
        parts.append(df.set_index("dt")[["Open", "High", "Low", "Close"]])
    out = pd.concat(parts).sort_index()
    out.index = out.index.tz_localize("UTC")
    return out[~out.index.duplicated()]


def run(dumps, late_bars, hold, friction, loader=load_pair):
    import config
    rows = []
    for path, half in dumps:
        if not os.path.exists(path):
            print(f"MISSING dump: {path}")
            continue
        try:
            d = pd.read_csv(path)
        except pd.errors.EmptyDataError:
            print(f"EMPTY dump: {path}")
            continue
        if "m1_diag" not in d.columns or "entry_model" not in d.columns:
            print(f"no m1_diag column in {path} — not a shadow run")
            continue
        d = d[(d.entry_model == "mm_golden") & (d["m1_diag"].fillna("").astype(str) != "")].copy()
        d["half"] = half
        rows.append(d)
    if not rows:
        return "no shadow MM trades found (was MM_GOLDEN_M1_SHADOW=1 set?)"
    T = pd.concat(rows, ignore_index=True)
    T["origR"] = [orig_r(r) for r in T.itertuples()]
    years = sorted({pd.Timestamp(x).year for x in T.opened_at})
    cache = {}
    late = []
    for r in T.itertuples():
        if r.m1_diag == "ok":
            late.append(None)
            continue
        if r.pair not in cache:
            cache[r.pair] = loader(r.pair, years)
        m1 = cache[r.pair]
        spread = config.PAIR_SPREAD_PIPS.get(r.pair, config.PAIR_SPREAD_PIPS["default"])
        fr = spread / 2 + config.SLIPPAGE_PIPS if friction is None else friction
        late.append(None if m1 is None else late_catch(m1, r, late_bars, hold, fr))
    T["late"] = late

    L = ["# P85 — the trades the M1 shift skips, and catching them late", ""]
    L += [f"Shadow run: every MM trade below is the UNGATED P81 trade, labelled with what the "
          f"M1 gate would have said. Late window {late_bars} M1 bars, hold {hold} M1 bars. "
          f"R = result / initial risk.", ""]
    L += ["## §1 Original trade outcome by M1 diagnosis", "",
          "| half | m1_diag | n | WR | PF (R) | sum R | med MFE pips |", "|---|---|---|---|---|---|---|"]
    for half in ["IS", "OOS"]:
        for dg, g in T[T.half == half].groupby("m1_diag"):
            L.append(f"| {half} | {dg} | {len(g)} | {100*(g.pnl>0).mean():.1f}% | {pf_r(g.origR):.2f} | "
                     f"{g.origR.sum():+.1f} | {g.mfe_pips.median():.1f} |")
    L += ["", "`ok` = the M1 gate would have taken it at the same moment. Everything else was skipped.",
          "", "## §2 Late catch — does a valid M1 shift form AFTER the original entry?", "",
          "| half | m1_diag | skipped | shift found | target first | no shift | late WR | late PF (R) | late sum R | orig sum R (same trades) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for half in ["IS", "OOS"]:
        S = T[(T.half == half) & (T.m1_diag != "ok")]
        for dg, g in list(S.groupby("m1_diag")) + [("ALL", S)]:
            lt = [x for x in g.late if x]
            f = [x for x in lt if x["found"]]
            tf = sum(1 for x in lt if x["why"] == "target_first")
            ns = sum(1 for x in lt if x["why"] == "no_shift")
            rs = [x["R"] for x in f]
            ids = [i for i, x in zip(g.index, g.late) if x and x["found"]]
            L.append(f"| {half} | {dg} | {len(g)} | {len(f)} | {tf} | {ns} | "
                     f"{(100*np.mean(np.array(rs)>0) if rs else 0):.0f}% | {pf_r(rs):.2f} | "
                     f"{sum(rs):+.1f} | {T.loc[ids,'origR'].sum():+.1f} |")
    L += ["", "`target first` = price reached the original target before any M1 shift formed — "
          "the move left without us. That is the continuation case the gate cannot catch.", "",
          "## §3 Verdict", ""]
    for half in ["IS", "OOS"]:
        S = T[(T.half == half) & (T.m1_diag != "ok")]
        f = [(i, x) for i, x in zip(S.index, S.late) if x and x["found"]]
        lr = sum(x["R"] for _, x in f); orr = T.loc[[i for i, _ in f], "origR"].sum()
        tfirst = S.loc[[i for i, x in zip(S.index, S.late) if x and x["why"] == "target_first"], "origR"]
        L.append(f"- **{half}**: skipped {len(S)} (orig sum {S.origR.sum():+.1f}R). Late shift on "
                 f"{len(f)}: late {lr:+.1f}R vs original {orr:+.1f}R on those same setups. "
                 f"{len(tfirst)} ran to target before any shift (orig {tfirst.sum():+.1f}R).")
    return "\n".join(L) + "\n"


def selftest():
    p = 1e-4
    seq = [1.1030 - i * 2 * p for i in range(10)] + [1.1008, 1.1012, 1.1004] + \
          [1.0998, 1.0994, 1.0996, 1.1003, 1.1009, 1.1014] + [1.1014 + i * 3 * p for i in range(40)]
    c = np.array(seq); h = c + 2e-5; l = c - 2e-5
    k = 18
    assert shift_at(h, l, c, k, +1, 1.0990, 1.1000, p) is not None
    assert shift_at(h, l, c, k - 1, +1, 1.0990, 1.1000, p) is None   # break not yet
    assert shift_at(h, l, c, k, +1, 1.0960, 1.0970, p) is None       # zone not reached
    r, how = simulate(h, l, c, k, +1, c[k], 1.0993, 1.1050, 60)
    assert how == "target" and r > 0, (r, how)
    r, how = simulate(h, l, c, k, +1, c[k], c[k] + 1e-5, 1.2, 60)     # stop just above? no: below
    print("selftest OK — shift detection (fires / not yet / no touch), first-touch sim")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--is-dump", default="data/mm_golden_is_shadow_trades.csv")
    ap.add_argument("--oos-dump", default="data/mm_golden_oos_shadow_trades.csv")
    ap.add_argument("--late-bars", type=int, default=60)
    ap.add_argument("--hold", type=int, default=480)
    ap.add_argument("--friction", type=float, default=None)
    ap.add_argument("--out", default="data/m1_skip_report.md")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    rep = run([(a.is_dump, "IS"), (a.oos_dump, "OOS")], a.late_bars, a.hold, a.friction)
    with open(a.out, "w") as f:
        f.write(rep)
    print(rep)


if __name__ == "__main__":
    main()
