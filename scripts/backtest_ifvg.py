#!/usr/bin/env python3
"""Inversion Fair Value Gap (IFVG) backtest.

Core insight under test: a FVG whose imbalance is later violated by a **full-body
close outside it** inverts into a supply/demand zone; the retest of that zone
(with a rejection wick) is the trade.

Pipeline per detection timeframe (D1 / H4 / H1 / M15):
  1. Detect 3-candle FVGs.
  2. Mark the INVERSION: after the gap is mitigated (price entered it), the first
     candle whose OPEN and CLOSE are both beyond one edge marks the IFVG —
        close+open above the FVG high  -> bullish IFVG (demand, buy on retest)
        close+open below the FVG low   -> bearish IFVG (supply, sell on retest)
  3. Drop ONE timeframe (D1->H4, H4->H1, H1->M15, M15->M5) and hunt the entry:
     - M15/H1/H4: first LTF candle that retests the zone with a rejection wick
       > 40% of its range in the zone direction; enter on its close, stop beyond
       the wick.
     - D1: limit at the zone's near edge on first retest, stop at the far edge —
       price does the same consolidation and the IFVG high/low is the entry.
  4. Target = 2R (fixed). The zone dies if price closes full-body back through it.

Output: WR% / PF / MaxDD(R) / count / mean-R / median-R, split IS (2022) vs
OOS (2024), broken down by detection timeframe (incl. D1).

Run:  RUN_IFVG_BACKTEST=1 python scripts/backtest_ifvg.py
      python scripts/backtest_ifvg.py --selftest      # no data needed
"""
from __future__ import annotations

import argparse
import bisect
import os
import statistics
import sys
from collections import namedtuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "histdata")
REPORT = os.path.join(ROOT, "data", "ifvg_report.md")

C = namedtuple("C", "t o h l c")
# detection TF -> (label, entry TF one lower, entry mode)
#   "wick" = LTF retest rejection candle (>40% wick in the zone direction)
#   "edge" = limit at the zone's near edge on retest, stop at the far edge (D1)
TF_MAP = [("15T", "M15", "5T", "wick"),
          ("60T", "H1", "15T", "wick"),
          ("240T", "H4", "60T", "wick"),
          ("D", "D1", "240T", "edge")]
WICK_FRAC = 0.40
RR = 2.0
INV_SCAN = 300        # bars after FVG to find the inversion
RETEST_BARS = 600     # LTF bars after inversion to find the entry
SIM_BARS = 1500       # LTF bars to resolve the trade


# ── FVG / IFVG / entry logic (pure, unit-tested) ──────────────────────────────

def detect_fvgs(cs):
    """3-candle FVGs. Returns (form_idx, lo, hi) boxes (gap direction irrelevant —
    the inversion decides the tradable direction)."""
    out = []
    for i in range(2, len(cs)):
        c0, c2 = cs[i - 2], cs[i]
        if c0.h < c2.l:            # gap up
            out.append((i, c0.h, c2.l))
        elif c0.l > c2.h:          # gap down
            out.append((i, c2.h, c0.l))
    return out


def mark_inversion(cs, form_idx, lo, hi):
    """First full-body close outside the box (after the box is mitigated).
    Returns (inv_idx, idir, lo, hi): idir +1 = bullish IFVG (demand),
    -1 = bearish IFVG (supply). None if it never inverts in the scan window."""
    touched = False
    for j in range(form_idx + 1, min(len(cs), form_idx + 1 + INV_SCAN)):
        c = cs[j]
        if c.l <= hi and c.h >= lo:
            touched = True
        if not touched:
            continue
        if c.o > hi and c.c > hi:      # full body above -> demand
            return (j, +1, lo, hi)
        if c.o < lo and c.c < lo:      # full body below -> supply
            return (j, -1, lo, hi)
    return None


def find_entry(ltf, start_k, idir, lo, hi, pip):
    """First LTF retest with a rejection wick > WICK_FRAC in the zone direction.
    Returns (k, entry, stop) or None. Zone invalidated if a full body closes
    back through it against the IFVG direction before a valid retest."""
    for k in range(start_k, min(len(ltf), start_k + RETEST_BARS)):
        c = ltf[k]
        rng = c.h - c.l
        if rng <= 0:
            continue
        in_zone = (c.l <= hi and c.h >= lo)
        if not in_zone:
            if idir > 0 and c.o < lo and c.c < lo:      # demand broken
                return None
            if idir < 0 and c.o > hi and c.c > hi:      # supply broken
                return None
            continue
        lower_wick = min(c.o, c.c) - c.l
        upper_wick = c.h - max(c.o, c.c)
        if idir > 0 and lower_wick / rng > WICK_FRAC:   # bullish rejection
            return (k, c.c, c.l - pip)
        if idir < 0 and upper_wick / rng > WICK_FRAC:   # bearish rejection
            return (k, c.c, c.h + pip)
    return None


def find_entry_edge(ltf, start_k, idir, lo, hi, pip):
    """D1-style entry: a limit at the IFVG's NEAR edge on first retest, stop at the
    FAR edge (± 1 pip) → risk = zone height. Bullish IFVG (demand) broke UP so price
    sits above the zone and retests DOWN to the high edge (buy at hi, stop below lo);
    bearish IFVG (supply) sits below and retests UP to the low edge (sell at lo, stop
    above hi). Zone dies if a full body closes through it against the IFVG direction."""
    for k in range(start_k, min(len(ltf), start_k + RETEST_BARS)):
        c = ltf[k]
        if idir > 0:                              # demand — buy at the high edge
            if c.l <= hi:
                return (k, hi, lo - pip)
            if c.o < lo and c.c < lo:             # closed below the zone → dead
                return None
        else:                                     # supply — sell at the low edge
            if c.h >= lo:
                return (k, lo, hi + pip)
            if c.o > hi and c.c > hi:
                return None
    return None


def simulate(ltf, k0, idir, entry, stop):
    """Walk forward to 1R stop or 2R target; stop checked first (conservative)."""
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    tp = entry + idir * RR * risk
    for k in range(k0 + 1, min(len(ltf), k0 + 1 + SIM_BARS)):
        c = ltf[k]
        if idir > 0:
            if c.l <= stop:
                return -1.0
            if c.h >= tp:
                return RR
        else:
            if c.h >= stop:
                return -1.0
            if c.l <= tp:
                return RR
    last = ltf[min(len(ltf) - 1, k0 + SIM_BARS)].c
    return (last - entry) * idir / risk


def run_tf(det_cs, ltf, ltf_times, pip, mode="wick"):
    """All IFVG trades for one detection-TF / entry-TF pair. Returns list of R.
    mode: 'wick' (LTF rejection candle) or 'edge' (limit at the zone edge, D1)."""
    entry_fn = find_entry_edge if mode == "edge" else find_entry
    rs = []
    used_until = -1   # avoid overlapping trades from clustered gaps
    for form_idx, lo, hi in detect_fvgs(det_cs):
        inv = mark_inversion(det_cs, form_idx, lo, hi)
        if inv is None:
            continue
        inv_idx, idir, zlo, zhi = inv
        start_k = bisect.bisect_right(ltf_times, det_cs[inv_idx].t)
        if start_k <= used_until:
            continue
        ent = entry_fn(ltf, start_k, idir, zlo, zhi, pip)
        if ent is None:
            continue
        k, entry, stop = ent
        r = simulate(ltf, k, idir, entry, stop)
        if r is not None:
            rs.append(r)
            used_until = k
    return rs


# ── metrics ───────────────────────────────────────────────────────────────────

def metrics(rs):
    n = len(rs)
    if not n:
        return {"n": 0}
    wins = [r for r in rs if r > 0]
    gl = -sum(r for r in rs if r <= 0)
    gp = sum(wins)
    eq = peak = mdd = 0.0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        mdd = min(mdd, eq - peak)
    return {"n": n, "wr": 100 * len(wins) / n,
            "pf": (gp / gl) if gl > 0 else float("inf"),
            "mdd": mdd, "mean": statistics.fmean(rs), "median": statistics.median(rs),
            "total": sum(rs)}


def _fmt(m):
    if m.get("n", 0) == 0:
        return "| — | 0 | — | — | — | — | — |"
    pf = "inf" if m["pf"] == float("inf") else f"{m['pf']:.2f}"
    return (f"{m['n']} | {m['wr']:.0f}% | {pf} | {m['mdd']:.1f}R | "
            f"{m['mean']:+.2f}R | {m['median']:+.2f}R | {m['total']:+.1f}R")


# ── data ──────────────────────────────────────────────────────────────────────

def _load_m1(pair, year):
    import pandas as pd
    p = os.path.join(DATA, f"{pair}_{year}.csv")
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p, sep=";", header=None, names=["dt", "o", "h", "l", "c", "v"])
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    return df.drop_duplicates("dt").sort_values("dt").set_index("dt")[["o", "h", "l", "c"]]


def _candles(m1, rule):
    import pandas as pd  # noqa: F401
    d = m1.resample(rule).agg({"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()
    return [C(t, r.o, r.h, r.l, r.c) for t, r in zip(d.index, d.itertuples(index=False))]


def analyse(pairs, years):
    # results[tf_label][year] = list of R
    results = {lab: {y: [] for y in years} for _, lab, _, _ in TF_MAP}
    covered = []
    for pair in pairs:
        pip = 0.01 if pair.endswith("JPY") else 0.0001
        for y in years:
            m1 = _load_m1(pair, y)
            if m1 is None or len(m1) < 5000:
                continue
            covered.append(f"{pair} {y}")
            cache = {}
            for det_tf, lab, ent_tf, mode in TF_MAP:
                det = cache.setdefault(det_tf, _candles(m1, det_tf))
                ltf = cache.setdefault(ent_tf, _candles(m1, ent_tf))
                ltf_times = [c.t for c in ltf]
                results[lab][y] += run_tf(det, ltf, ltf_times, pip, mode)
    return results, covered


def report(results, years, covered, pairs):
    is_y = [y for y in years if y <= 2023]
    oos_y = [y for y in years if y >= 2024]
    L = ["# Inversion FVG (IFVG) backtest", "",
         "Core condition tested: a FVG violated by a **full-body close outside it** "
         "inverts to a supply/demand zone; entry on the LTF retest rejection (wick "
         f">{WICK_FRAC:.0%} of range), stop beyond the wick, target {RR:.0f}R. "
         "Detection TF → entry TF: H4→H1, H1→M15, M15→M5.", "",
         f"_pairs: {', '.join(pairs)} · coverage: {', '.join(covered) or 'NONE'}_", "",
         "MaxDD is peak-to-trough of the cumulative-R curve. `total` = summed R.", ""]

    def split(y_list):
        L2 = ["| TF | n | WR | PF | MaxDD | mean R | median R | total |",
              "|---|---|---|---|---|---|---|---|"]
        for _, lab, _, _ in TF_MAP:
            rs = [r for y in y_list for r in results[lab].get(y, [])]
            L2.append(f"| {lab} | {_fmt(metrics(rs))}")
        return L2

    if is_y:
        L += [f"## In-sample ({'/'.join(map(str, is_y))})", ""] + split(is_y) + [""]
    if oos_y:
        L += [f"## Out-of-sample ({'/'.join(map(str, oos_y))})", ""] + split(oos_y) + [""]

    # verdict
    all_is = [r for y in is_y for lab in results for r in results[lab].get(y, [])]
    all_oos = [r for y in oos_y for lab in results for r in results[lab].get(y, [])]
    mi, mo = metrics(all_is), metrics(all_oos)
    L += ["## Read", ""]
    if mi.get("n", 0) < 15 or mo.get("n", 0) < 15:
        L += [f"⚠️ small sample (IS {mi.get('n',0)} / OOS {mo.get('n',0)}). The IFVG "
              "condition is strict; thin counts = noisy. Treat as directional, not shippable."]
    else:
        pis = mi["pf"]; poo = mo["pf"]
        good = pis > 1.0 and poo > 1.0
        L += [f"IS PF {pis:.2f} (n={mi['n']}, WR {mi['wr']:.0f}%) · OOS PF {poo:.2f} "
              f"(n={mo['n']}, WR {mo['wr']:.0f}%). "
              + ("Both splits positive — the full-body-close inversion carries an edge worth "
                 "a proper (spread/slippage-aware) follow-up." if good else
                 "Not positive in both splits — the raw inversion edge doesn't hold; nothing to ship.")]
    return L


# ── self-test (no data) ────────────────────────────────────────────────────────

def _selftest():
    def c(t, o, h, l, cl):
        return C(t, o, h, l, cl)
    # bullish gap: c0.h=10 < c2.l=12 -> box [10,12]
    cs = [c(0, 9, 10, 8, 9.5), c(1, 10, 11, 9, 10.5), c(2, 12, 13, 12, 12.5)]
    fv = detect_fvgs(cs)
    assert fv and fv[0][1] == 10 and fv[0][2] == 12, fv
    # mitigate (dip into box) then full body below -> bearish IFVG (supply)
    cs += [c(3, 11.5, 11.6, 10.5, 11.0),   # touches box
           c(4, 9.8, 9.9, 9.0, 9.2)]        # full body below 10 -> supply
    inv = mark_inversion(cs, fv[0][0], 10, 12)
    assert inv and inv[1] == -1, inv        # bearish IFVG
    # LTF retest: candle pushes up into zone with big upper wick (rejection)
    ltf = [c(5, 9.5, 9.6, 9.4, 9.55),
           c(6, 10.2, 11.9, 10.1, 10.4)]    # high 11.9 in zone, upper wick huge
    e = find_entry(ltf, 0, -1, 10, 12, 0.0001)
    assert e is not None, "should find a bearish rejection entry"
    k, entry, stop = e
    assert stop > entry, (entry, stop)      # sell: stop above entry
    # simulate a drop to 2R target
    risk = stop - entry
    tp = entry - RR * risk
    sim = [c(7, entry, entry + 0.01, tp - 0.5, tp - 0.4)]  # low pierces tp
    r = simulate(ltf[:1] + [ltf[1]] + sim, 1, -1, entry, stop)
    assert r == RR, r
    # D1 edge entry: bearish IFVG (supply) zone [10,12]; price retests UP to lo=10
    edge = find_entry_edge([c(8, 9.0, 9.5, 8.8, 9.2), c(9, 9.6, 10.3, 9.5, 9.9)],
                           0, -1, 10, 12, 0.0001)
    assert edge is not None, "edge entry should trigger when high reaches the low edge"
    _, e_entry, e_stop = edge
    assert e_entry == 10 and e_stop > 12, edge   # sell at low edge, stop above high edge
    # demand edge: zone [10,12], price retests DOWN to hi=12
    edge2 = find_entry_edge([c(8, 13, 13.2, 11.9, 12.8)], 0, +1, 10, 12, 0.0001)
    assert edge2 and edge2[1] == 12 and edge2[2] < 10, edge2  # buy at high edge, stop below low
    print("selftest OK — FVG detect, full-body inversion, wick-rejection entry, D1 edge entry, 2R sim")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", default=["EURUSD", "GBPUSD", "NZDUSD"])
    ap.add_argument("--years", type=int, nargs="+", default=[2022, 2024])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if os.getenv("RUN_IFVG_BACKTEST", "0") != "1":
        print("Guarded: set RUN_IFVG_BACKTEST=1 to run the IFVG backtest.")
        return 0
    print(f"IFVG backtest — pairs {a.pairs}, years {a.years}…")
    results, covered = analyse(a.pairs, a.years)
    lines = report(results, a.years, covered, a.pairs)
    text = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        f.write(text)
    print(text)
    print(f"[report → {REPORT}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
