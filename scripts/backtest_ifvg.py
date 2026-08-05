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
     a CONFIRMATION CLOSE — a candle that wicks into the IFVG zone AND closes back
     OUT in the trade direction (demand: dips in, closes above the high; supply:
     pokes in, closes below the low). The rejection is proven and price is already
     moving away, so entry is at that close.
  4. Stop = market structure, capped at 10 pips (beyond the confirmation candle's
     wick / nearest swing). Target = 2R. Spread + slippage on both fills. The zone
     dies if a full body closes through it against the IFVG direction first.

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
# Stop = market structure, capped at 10 pips — on EVERY entry, every TF (per the
# live strategy: beyond the nearest LTF swing, never wider than 10 pips). R is
# defined off THIS stop, so the 2R target is ~20 pips regardless of detection TF.
STOP_CAP_PIPS = 10
STOP_LOOKBACK = 12    # LTF bars back to locate the structural swing
try:
    import config as _cfg
    _SPREAD = dict(_cfg.PAIR_SPREAD_PIPS)
    _SLIP = float(getattr(_cfg, "SLIPPAGE_PIPS", 0.5))
except Exception:      # noqa: BLE001 - standalone use without config
    _SPREAD = {"default": 1.5}
    _SLIP = 0.5


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


def find_entry(ltf, start_k, idir, lo, hi):
    """Confirmation-close entry (all TFs). The candle must WICK into the IFVG zone
    AND CLOSE back OUT in the trade direction — the rejection is proven and price is
    already moving away, so the tight 10-pip stop sits behind a confirmed move, not
    inside the retest noise. Returns (k, entry=close) or None.
      demand (idir>0): low ≤ hi (dipped in) AND close > hi (closed back above) AND bullish
      supply (idir<0): high ≥ lo (poked in) AND close < lo (closed back below) AND bearish
    Zone dies if a full body closes through it against the IFVG direction first."""
    for k in range(start_k, min(len(ltf), start_k + RETEST_BARS)):
        c = ltf[k]
        if idir > 0:                                        # demand
            if c.l <= hi and c.c > hi and c.c > c.o:
                return (k, c.c)
            if c.o < lo and c.c < lo:                       # closed below zone → dead
                return None
        else:                                               # supply
            if c.h >= lo and c.c < lo and c.c < c.o:
                return (k, c.c)
            if c.o > hi and c.c > hi:                        # closed above zone → dead
                return None
    return None


def structure_stop(ltf, k, idir, entry, pip):
    """Market-structure stop, capped at 10 pips — beyond the nearest LTF swing in
    the last STOP_LOOKBACK bars, but never wider than STOP_CAP_PIPS. Mirrors the
    live strategy: the stop always sits on structure, tight, regardless of the
    detection timeframe."""
    seg = ltf[max(0, k - STOP_LOOKBACK):k + 1]
    if idir > 0:
        stop = min(c.l for c in seg) - pip
    else:
        stop = max(c.h for c in seg) + pip
    cap = STOP_CAP_PIPS * pip
    if abs(entry - stop) > cap or (idir > 0 and stop >= entry) or (idir < 0 and stop <= entry):
        stop = entry - idir * cap        # fall back to the flat 10-pip cap
    return stop


def htf_target(entry, idir, d_cs, w_cs, min_dist):
    """Nearest unswept HTF liquidity beyond entry in the trade direction — the
    closest prior-day (last 3 completed daily) or prior-week high/low, at least
    min_dist away. None if no draw exists that far out. Uses only COMPLETED HTF
    bars (drops the current forming day/week) → no lookahead."""
    levels = []
    for b in d_cs[-4:-1]:                # prior 3 completed daily candles (PDH/PDL)
        levels += [b.h, b.l]
    if len(w_cs) >= 2:
        levels += [w_cs[-2].h, w_cs[-2].l]   # prior completed week (PWH/PWL)
    if idir > 0:
        cand = [lv for lv in levels if lv > entry + min_dist]
        return min(cand) if cand else None
    cand = [lv for lv in levels if lv < entry - min_dist]
    return max(cand) if cand else None


def simulate(ltf, k0, idir, entry, stop, friction, tp_price=None):
    """Walk to the stop or the target with spread+slippage on BOTH fills. Returns
    realised R (off the structural stop). tp_price given → use it (HTF-liquidity
    target); else fixed 2R. Stop checked before target within a bar (conservative)."""
    eff_entry = entry + idir * friction          # worse entry fill
    risk = abs(eff_entry - stop)
    if risk <= 0:
        return None
    tp = tp_price if tp_price is not None else eff_entry + idir * RR * risk
    for k in range(k0 + 1, min(len(ltf), k0 + 1 + SIM_BARS)):
        c = ltf[k]
        if idir > 0:
            if c.l <= stop:
                return (stop - friction - eff_entry) / risk
            if c.h >= tp:
                return (tp - friction - eff_entry) / risk
        else:
            if c.h >= stop:
                return (eff_entry - (stop + friction)) / risk
            if c.l <= tp:
                return (eff_entry - (tp + friction)) / risk
    last = ltf[min(len(ltf) - 1, k0 + SIM_BARS)].c
    exit_fill = last - idir * friction
    return (exit_fill - eff_entry) * idir / risk


def run_tf(det_cs, ltf, ltf_times, pip, spread=1.5, target="2r",
           d_cs=None, d_times=None, w_cs=None, w_times=None):
    """All IFVG trades for one detection-TF / entry-TF pair. Returns list of R.
    Entry = confirmation close (all TFs); stop = market-structure 10-pip capped;
    target = '2r' (fixed) or 'htf' (nearest HTF liquidity). friction on both fills."""
    friction = (spread / 2 + _SLIP) * pip
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
        ent = find_entry(ltf, start_k, idir, zlo, zhi)
        if ent is None:
            continue
        k, entry = ent
        stop = structure_stop(ltf, k, idir, entry, pip)
        tp_price = None
        if target == "htf":
            et = ltf[k].t
            di = bisect.bisect_right(d_times, et)
            wi = bisect.bisect_right(w_times, et)
            tp_price = htf_target(entry, idir, d_cs[:di], w_cs[:wi], abs(entry - stop))
            if tp_price is None:
                continue   # this variant needs a liquidity draw to aim at
        r = simulate(ltf, k, idir, entry, stop, friction, tp_price)
        if r is not None:
            tp = tp_price if tp_price is not None else entry + idir * RR * abs(entry - stop)
            rs.append({"t": ltf[k].t, "dir": idir, "entry": entry, "stop": stop,
                       "target": tp, "r": r, "stop_pips": abs(entry - stop) / pip})
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


# pandas 2.2+ removed the "T" frequency aliases (15T/60T/…) → use min/h/D.
_RULE = {"5T": "5min", "15T": "15min", "60T": "60min", "240T": "240min", "D": "1D"}


def _candles(m1, tf):
    d = m1.resample(_RULE.get(tf, tf)).agg(
        {"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()
    return [C(t, r.o, r.h, r.l, r.c) for t, r in zip(d.index, d.itertuples(index=False))]


def analyse(pairs, years, target="2r"):
    # results[tf_label][year] = list of R ; trades = full per-entry log
    results = {lab: {y: [] for y in years} for _, lab, _, _ in TF_MAP}
    covered = []
    trades = []
    for pair in pairs:
        pip = 0.01 if pair.endswith("JPY") else 0.0001
        spread = _SPREAD.get(pair, _SPREAD.get("default", 1.5))
        for y in years:
            m1 = _load_m1(pair, y)
            if m1 is None or len(m1) < 5000:
                continue
            covered.append(f"{pair} {y}")
            cache = {}
            d_cs = _candles(m1, "D"); d_times = [c.t for c in d_cs]
            w_cs = _candles(m1, "1W"); w_times = [c.t for c in w_cs]
            for det_tf, lab, ent_tf, mode in TF_MAP:
                det = cache.setdefault(det_tf, _candles(m1, det_tf))
                ltf = cache.setdefault(ent_tf, _candles(m1, ent_tf))
                ltf_times = [c.t for c in ltf]
                for d in run_tf(det, ltf, ltf_times, pip, spread, target,
                                d_cs, d_times, w_cs, w_times):
                    results[lab][y].append(d["r"])
                    trades.append({**d, "pair": pair, "tf": lab})
    return results, covered, trades


def report(results, years, covered, pairs, target="2r"):
    is_y = [y for y in years if y <= 2023]
    oos_y = [y for y in years if y >= 2024]
    tgt_txt = ("nearest HTF liquidity (prior-day / prior-week high-low, ≥1R away)"
               if target == "htf" else f"fixed {RR:.0f}R")
    L = ["# Inversion FVG (IFVG) backtest — market-structure stop + costs", "",
         "Core condition: a FVG violated by a **full-body close outside it** inverts "
         "to a supply/demand zone. Entry one TF lower (D1→H4, H4→H1, H1→M15, M15→M5) "
         "on a **confirmation close** — a candle that wicks into the zone AND closes "
         "back OUT in the trade direction (rejection proven, price moving away). "
         f"**Stop = market structure, capped at {STOP_CAP_PIPS} pips on every entry** "
         f"(R defined off that stop); **target = {tgt_txt}**. Spread + slippage on "
         "both fills.", "",
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


def entries_section(trades):
    """A readable sample of the ACTUAL entries taken (full log → data/ifvg_trades.csv).
    Shows the first 30 chronologically; every column is a real backtest entry."""
    import pandas as pd
    L = ["## Actual entries taken (sample of the first 30 — full log in data/ifvg_trades.csv)", ""]
    if not trades:
        return L + ["_No entries._", ""]
    L += [f"_{len(trades)} entries total._", "",
          "| time (UTC) | pair | TF | dir | entry | stop | target | stop pips | R |",
          "|---|---|---|---|---|---|---|---|---|"]
    for t in sorted(trades, key=lambda x: pd.Timestamp(x["t"]))[:30]:
        d = "buy" if t["dir"] > 0 else "sell"
        L.append(f"| {pd.Timestamp(t['t']):%Y-%m-%d %H:%M} | {t['pair']} | {t['tf']} | {d} | "
                 f"{t['entry']:.5f} | {t['stop']:.5f} | {t['target']:.5f} | "
                 f"{t['stop_pips']:.1f} | {t['r']:+.2f} |")
    return L + [""]


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
    # supply confirmation-close entry: candle pokes UP into zone [10,12], closes
    # back BELOW lo=10, bearish → confirmed rejection, enter at close.
    ltf = [c(5, 9.5, 9.6, 9.4, 9.55),
           c(6, 9.7, 10.8, 9.6, 9.65)]          # high 10.8 into zone, close 9.65<10, bearish
    e = find_entry(ltf, 0, -1, 10, 12)
    assert e is not None and e[1] == 9.65, e     # entry = close, back below the zone
    # a mere poke that does NOT close back out must NOT trigger
    notrig = find_entry([c(6, 9.7, 10.8, 9.6, 10.5)], 0, -1, 10, 12)  # closes inside zone
    assert notrig is None, "shallow poke closing inside the zone must not enter"
    pip = 0.0001
    st = structure_stop(ltf, 1, -1, 9.65, pip)
    assert abs(9.65 - st) <= STOP_CAP_PIPS * pip + 1e-9 and st > 9.65, st   # ≤10 pips, above
    # 2R sim with friction: price drops to target, high stays under the stop
    friction = (1.5 / 2 + _SLIP) * pip
    r = simulate([ltf[1], c(7, 9.65, 9.6499, 9.6450, 9.6460)], 0, -1, 9.65, st, friction)
    assert 1.3 < r <= RR, r                      # ~2R, minus round-trip friction
    # demand confirmation: candle dips into zone [10,12], closes back ABOVE hi, bullish
    dem = find_entry([c(8, 12.5, 12.7, 11.5, 12.55)], 0, +1, 10, 12)
    assert dem and dem[1] == 12.55, dem
    # HTF target: buy at 100.00, daily highs 100.20 & 100.50 above → nearest = 100.20
    d = [c(0, 99, 99.3, 98.8, 99.1), c(1, 100, 100.2, 99.5, 100.1),
         c(2, 100.1, 100.5, 99.9, 100.3), c(3, 100.3, 100.4, 100.0, 100.35)]
    tp = htf_target(100.00, +1, d, [], 0.001)   # last 3 completed = d[-4:-1]=d[0:3]
    assert tp == 100.20, tp                       # nearest daily high above entry+min_dist
    tp2 = htf_target(100.00, -1, d, [], 0.001)    # sell: nearest low below
    assert tp2 is not None and tp2 < 100.00, tp2
    print("selftest OK — FVG detect, inversion, confirmation-close entry (+no-trigger "
          "on shallow poke), 10-pip structure stop, friction sim, HTF-liquidity target")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", default=["EURUSD", "GBPUSD", "NZDUSD"])
    ap.add_argument("--years", type=int, nargs="+", default=[2022, 2024])
    ap.add_argument("--target", choices=["2r", "htf"], default="2r",
                    help="'2r' fixed, or 'htf' = nearest prior-day/week liquidity")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if os.getenv("RUN_IFVG_BACKTEST", "0") != "1":
        print("Guarded: set RUN_IFVG_BACKTEST=1 to run the IFVG backtest.")
        return 0
    print(f"IFVG backtest — pairs {a.pairs}, years {a.years}, target {a.target}…")
    results, covered, trades = analyse(a.pairs, a.years, a.target)
    lines = report(results, a.years, covered, a.pairs, a.target) + entries_section(trades)
    text = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        f.write(text)
    # full per-entry log to CSV
    import csv
    csv_path = os.path.join(os.path.dirname(REPORT), "ifvg_trades.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "pair", "tf", "dir", "entry", "stop", "target", "stop_pips", "R"])
        for t in sorted(trades, key=lambda x: (x["pair"], x["tf"], str(x["t"]))):
            w.writerow([t["t"], t["pair"], t["tf"], "buy" if t["dir"] > 0 else "sell",
                        f"{t['entry']:.5f}", f"{t['stop']:.5f}", f"{t['target']:.5f}",
                        f"{t['stop_pips']:.1f}", f"{t['r']:.3f}"])
    print(text)
    print(f"[report → {REPORT}] [{len(trades)} entries → {csv_path}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
