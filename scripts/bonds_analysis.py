#!/usr/bin/env python3
"""Bonds/yields × dollar — does the rates market improve the daily dollar bias?

The intermarket thesis: US Treasury yields LEAD the dollar. Higher US yields pull
capital in -> USD bid, so yields (DGS2/5/10) are POSITIVELY correlated with the
dollar. Every pair we trade is X/USD (EURUSD, GBPUSD, NZDUSD), which is INVERSELY
correlated with the dollar -> therefore pair vs yields are INVERSELY correlated.

Two measurements, both split IS (2022-23) / OOS (2024-25), per pair and per tenor.
Measurement only — nothing here touches the engine. It writes a GREEN/YELLOW/RED
verdict; the lever (a sizing bump on bond-confirmed trades, default OFF in config)
is only worth flipping on if this passes both splits.

  FOUNDATION — yield<->dollar correlation
      Daily dollar-proxy return (= -pair return) vs daily yield change. Must be
      POSITIVE in both splits or the whole thesis is void — reported first.

  TEST A — SMT divergence (reversal signal, the headline)
      Reusing ict.smt with yields as the INVERSE reference to the pair: the pair
      sweeps a new extreme (a dollar move) that yields FAIL to confirm -> the move
      isn't backed by rates -> reversal. We measure whether the pair actually
      reverses over the next H days, vs the unconditional baseline reversal rate.

  TEST B — structure agreement (continuation quality)
      When the yield intermediate structure AGREES with the dollar direction the
      pair's structure implies, is the next-H-day dollar continuation more reliable
      than when they disagree?

Run:
    python scripts/bonds_analysis.py [--horizon-days 3] [--lookback 20]
    python scripts/bonds_analysis.py --emit-bias      # also write data/bond_bias.json
    python scripts/bonds_analysis.py --selftest        # no data / no network
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import namedtuple

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

HISTDATA = os.path.join(_ROOT, "data", "histdata")
BONDS_SRC = os.path.join(_ROOT, "data", "bonds_src")
REPORT = os.path.join(_ROOT, "data", "bonds_report.md")
BIAS_OUT = os.path.join(_ROOT, "data", "bond_bias.json")

PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
TENORS = ("DGS2", "DGS5", "DGS10")
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)

Bar = namedtuple("Bar", "Open High Low Close")


# ------------------------------------------------------------------ pure logic

def pearson(xs, ys):
    """Pearson correlation of two equal-length lists; None if degenerate."""
    n = len(xs)
    if n < 3 or len(ys) != n:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sx = sum((x - mx) ** 2 for x in xs)
    sy = sum((y - my) ** 2 for y in ys)
    if sx <= 0 or sy <= 0:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(sx * sy)


def reversal_hit(closes, i, horizon, rev_dir):
    """Did price reverse in `rev_dir` over the next `horizon` bars?

    rev_dir +1: expect price higher H bars later; -1: lower. Returns True/False,
    or None when there aren't enough forward bars. Pure — the forward evaluator
    both TEST A and the baseline share, so they are always measured identically.
    """
    j = i + horizon
    if j >= len(closes):
        return None
    delta = closes[j] - closes[i]
    return (delta > 0) if rev_dir > 0 else (delta < 0)


def _pct(a, b):
    return (100.0 * a / b) if b else None


def _fmt_pct(v):
    return "—" if v is None else f"{v:.0f}%"


def _fmt_corr(v):
    return "—" if v is None else f"{v:+.2f}"


def _wilson_lift(hit, n, base):
    """Simple edge readout: conditional hit-rate minus baseline, in pp."""
    if not n or base is None:
        return None
    return _pct(hit, n) - base


# ------------------------------------------------------------------ data (pandas)

def _load_pair_daily(pair):
    """Daily OHLC list of (year, Bar) from the M1 histdata, or None if absent."""
    import pandas as pd
    frames = []
    for y in (2022, 2023, 2024, 2025):
        p = os.path.join(HISTDATA, f"{pair}_{y}.csv")
        if os.path.exists(p):
            df = pd.read_csv(p, sep=";", header=None,
                             names=["dt", "o", "h", "l", "c", "v"])
            frames.append(df)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    df = df.drop_duplicates("dt").sort_values("dt").set_index("dt")
    d = df.resample("1D").agg({"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()
    return d


def _load_yields():
    """Return {tenor: pandas.Series indexed by date} forward-filled, or {}.

    Rows with "." (FRED non-trading marker) are dropped then the series is
    reindexed/ffilled onto whatever daily index we join against later.
    """
    import pandas as pd
    out = {}
    for t in TENORS:
        p = os.path.join(BONDS_SRC, f"{t}.csv")
        if not os.path.exists(p):
            continue
        df = pd.read_csv(p)
        col = t if t in df.columns else df.columns[-1]
        df.columns = ["DATE", "VAL"] if len(df.columns) == 2 else df.columns
        s = pd.to_numeric(df["VAL"] if "VAL" in df.columns else df[col], errors="coerce")
        s.index = pd.to_datetime(df["DATE"] if "DATE" in df.columns else df.iloc[:, 0])
        s = s.dropna()
        if len(s):
            out[t] = s
    return out


def _yield_bars(yield_series, index):
    """Align a yield series onto `index` (ffill) and wrap as flat OHLC bars.

    A yield level has no intraday range, so High=Low=Close=Open=level. That is
    enough for the fractal/SMT logic, which only compares extremes across bars.
    Returns (bars, values) aligned 1:1 with `index`.
    """
    import pandas as pd  # noqa: F401
    aligned = yield_series.reindex(index, method="ffill")
    vals = aligned.to_numpy()
    bars = [Bar(v, v, v, v) for v in vals]
    return bars, vals


# ------------------------------------------------------------------ measurement

def _build_frame(pair, yields):
    """Join one pair's daily bars with the aligned yields.

    Returns dict with: years[], closes[], pair_bars[], and per-tenor
    (bars, vals). Days before the first yield observation are dropped so every
    tenor has a real (ffilled) value. None if data is missing.
    """
    import numpy as np  # noqa: F401
    d = _load_pair_daily(pair)
    if d is None or len(d) < 100 or not yields:
        return None
    idx = d.index
    closes = d["c"].to_numpy().tolist()
    pair_bars = [Bar(o, h, l, c) for o, h, l, c
                 in zip(d["o"], d["h"], d["l"], d["c"])]
    years = [int(x) for x in idx.year.to_numpy()]
    per_tenor = {}
    first_valid = idx[0]
    for t, s in yields.items():
        # only score days on/after the tenor's first observation
        first_valid = max(first_valid, s.index.min())
        per_tenor[t] = _yield_bars(s, idx)
    # mask of days with a real yield value (>= first observation across tenors)
    valid_from = None
    for i, ts in enumerate(idx):
        if ts >= first_valid:
            valid_from = i
            break
    return {"years": years, "closes": closes, "pair_bars": pair_bars,
            "index": idx, "per_tenor": per_tenor, "valid_from": valid_from or 0}


def _foundation_corr(frame, tenor, years):
    """Correlation of daily dollar-proxy return (= -pair return) vs daily yield
    change, over the given years. Positive = the thesis holds."""
    closes = frame["closes"]
    _, yvals = frame["per_tenor"][tenor]
    yy = frame["years"]
    dollar_ret, yield_chg = [], []
    for i in range(1, len(closes)):
        if yy[i] not in years:
            continue
        if closes[i - 1] <= 0 or yvals[i - 1] is None:
            continue
        pr = (closes[i] - closes[i - 1]) / closes[i - 1]
        dy = yvals[i] - yvals[i - 1]
        if pr != pr or dy != dy:      # NaN guard
            continue
        dollar_ret.append(-pr)        # dollar proxy = inverse of the pair
        yield_chg.append(dy)
    return pearson(dollar_ret, yield_chg), len(dollar_ret)


def _test_a_smt(frame, tenor, years, horizon, lookback):
    """SMT-divergence reversal test for one pair/tenor over `years`.

    At each day we look for a divergence in each direction using ict.smt with the
    yield series as the INVERSE reference (pair is inverse to the dollar; yields
    are positive to the dollar -> pair vs yields inverse). A fired divergence
    predicts the pair REVERSES; we score that against the shared baseline.
    """
    from ict import smt
    closes = frame["closes"]
    pair_bars = frame["pair_bars"]
    ybars, _ = frame["per_tenor"][tenor]
    yy = frame["years"]
    hit = n = 0
    base_hit = base_n = 0
    start = max(frame["valid_from"], lookback)
    for i in range(start, len(closes) - horizon):
        if yy[i] not in years:
            continue
        p_slice = pair_bars[:i + 1]
        y_slice = ybars[:i + 1]
        for direction in (1, -1):
            # direction +1: pair swept a LOWER low (dollar-strength spike) ->
            #   yields should make a HIGHER high; divergence if they didn't ->
            #   predict pair reverses UP (rev_dir +1).
            # direction -1: pair swept a HIGHER high -> yields should make a lower
            #   low; divergence if not -> predict pair reverses DOWN (rev_dir -1).
            if smt.smt_divergence(p_slice, y_slice, direction, inverse=True,
                                  lookback=lookback):
                rev_dir = direction    # +1 low-sweep->up ; -1 high-sweep->down
                r = reversal_hit(closes, i, horizon, rev_dir)
                if r is not None:
                    n += 1
                    hit += 1 if r else 0
        # baseline: unconditional reversal-up rate at this bar (both dirs pooled)
        for rev_dir in (1, -1):
            r = reversal_hit(closes, i, horizon, rev_dir)
            if r is not None:
                base_n += 1
                base_hit += 1 if r else 0
    return {"hit": hit, "n": n, "base_hit": base_hit, "base_n": base_n}


def _test_b_structure(frame, tenor, years, horizon):
    """Structure-agreement continuation test for one pair/tenor over `years`.

    Yield intermediate structure direction vs the dollar direction the pair's own
    structure implies (dollar_dir = -pair_struct_dir). On AGREE days, is the
    next-H-day dollar continuation more reliable than on DISAGREE days?
    """
    from ict import market_structure as ms
    closes = frame["closes"]
    pair_bars = frame["pair_bars"]
    ybars, _ = frame["per_tenor"][tenor]
    yy = frame["years"]
    win = 60
    agree_hit = agree_n = dis_hit = dis_n = 0
    start = max(frame["valid_from"], win)
    for i in range(start, len(closes) - horizon):
        if yy[i] not in years:
            continue
        pdir = ms.structure_direction(ms.classify(pair_bars[i - win:i + 1]))
        ydir = ms.structure_direction(ms.classify(ybars[i - win:i + 1]))
        if pdir == 0 or ydir == 0:
            continue
        dollar_dir = -pdir            # pair up => dollar down
        # dollar continuation = pair continues in -dollar_dir = pdir direction
        cont = reversal_hit(closes, i, horizon, pdir)
        if cont is None:
            continue
        if ydir == dollar_dir:        # yields agree with the dollar read
            agree_n += 1
            agree_hit += 1 if cont else 0
        else:
            dis_n += 1
            dis_hit += 1 if cont else 0
    return {"agree_hit": agree_hit, "agree_n": agree_n,
            "dis_hit": dis_hit, "dis_n": dis_n}


# ------------------------------------------------------------------ reporting

def _verdict(rows_a, corr_ok):
    """GREEN/YELLOW/RED from TEST A lift consistency across IS/OOS + foundation.

    rows_a: list of dicts with keys is_lift, oos_lift, is_n, oos_n (per pair/tenor).
    GREEN needs a positive lift in BOTH splits (same sign) with real n, on a
    majority of pair/tenor cells, AND a positive foundation correlation.
    """
    strong = 0
    total = 0
    for r in rows_a:
        if r["is_n"] < 15 or r["oos_n"] < 15:
            continue
        total += 1
        if (r["is_lift"] or 0) > 3 and (r["oos_lift"] or 0) > 3:
            strong += 1
    if not corr_ok:
        return "RED", ("foundation correlation is not positive in both splits — "
                       "the yield<->dollar link the whole thesis rests on is absent")
    if total == 0:
        return "YELLOW", "too few divergence events to judge (need more history)"
    frac = strong / total
    if frac >= 0.5:
        return "GREEN", f"{strong}/{total} pair-tenor cells show a >3pp reversal lift in BOTH splits"
    if strong >= 1:
        return "YELLOW", f"only {strong}/{total} cells lift in both splits — mixed, not shippable"
    return "RED", "no pair-tenor cell shows a consistent both-split reversal lift"


def analyse(horizon, lookback):
    yields = _load_yields()
    L = ["# Bonds / yields × dollar — daily-bias measurement", "",
         "US Treasury yields lead the dollar (higher yields -> USD bid). Every pair "
         "is X/USD so pair vs yields is INVERSELY correlated. Split IS 2022-23 / "
         "OOS 2024-25. Measurement only — nothing ships from here.",
         "", f"_horizon = {horizon} trading days · SMT lookback = {lookback} daily bars_", ""]

    if not yields:
        return L + ["**ERROR: no yield data in data/bonds_src/.** Run "
                    "`python scripts/fetch_fred.py` first (or drop DGS2/DGS5/DGS10 "
                    "CSVs there manually if the proxy blocks FRED)."]
    L += [f"_yields loaded: {', '.join(sorted(yields))}_", ""]

    frames = {}
    missing = []
    for pair in PAIRS:
        fr = _build_frame(pair, yields)
        if fr is None:
            missing.append(pair)
        else:
            frames[pair] = fr
    if missing:
        L += [f"_⚠️ no price data for: {', '.join(missing)} — skipped "
              "(run fetch_histdata / prepare_histdata)._", ""]
    if not frames:
        return L + ["**ERROR: no pair price data found in data/histdata.**"]

    # ---- FOUNDATION ------------------------------------------------------
    L += ["## Foundation — yield ↔ dollar correlation", "",
          "Daily dollar-proxy return (−pair return) vs daily yield change. Must be "
          "**positive** in both splits or the thesis is void.", "",
          "| pair | tenor | corr IS | corr OOS | n IS/OOS |", "|---|---|---|---|---|"]
    corr_pos_is = corr_pos_oos = corr_cells = 0
    for pair, fr in frames.items():
        for t in sorted(fr["per_tenor"]):
            ci, ni = _foundation_corr(fr, t, IS_YEARS)
            co, no = _foundation_corr(fr, t, OOS_YEARS)
            L.append(f"| {pair} | {t} | {_fmt_corr(ci)} | {_fmt_corr(co)} | {ni}/{no} |")
            corr_cells += 1
            if ci is not None and ci > 0:
                corr_pos_is += 1
            if co is not None and co > 0:
                corr_pos_oos += 1
    corr_ok = corr_cells and corr_pos_is >= corr_cells * 0.5 and corr_pos_oos >= corr_cells * 0.5
    L += ["", f"_positive-correlation cells: {corr_pos_is}/{corr_cells} IS, "
          f"{corr_pos_oos}/{corr_cells} OOS_", ""]

    # ---- TEST A ----------------------------------------------------------
    L += ["## Test A — SMT divergence reversal rate (headline)", "",
          "When the pair sweeps an extreme (a dollar move) that yields FAIL to "
          "confirm, does the pair reverse over the next horizon? `lift` = "
          "divergence reversal-rate − unconditional baseline (percentage points).",
          "", "| pair | tenor | IS rev% | IS base | IS lift | IS n | OOS rev% | OOS base | OOS lift | OOS n |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    rows_a = []
    for pair, fr in frames.items():
        for t in sorted(fr["per_tenor"]):
            ia = _test_a_smt(fr, t, IS_YEARS, horizon, lookback)
            oa = _test_a_smt(fr, t, OOS_YEARS, horizon, lookback)
            ib = _pct(ia["base_hit"], ia["base_n"])
            ob = _pct(oa["base_hit"], oa["base_n"])
            il = _wilson_lift(ia["hit"], ia["n"], ib)
            ol = _wilson_lift(oa["hit"], oa["n"], ob)
            rows_a.append({"is_lift": il, "oos_lift": ol,
                           "is_n": ia["n"], "oos_n": oa["n"]})
            L.append(f"| {pair} | {t} | {_fmt_pct(_pct(ia['hit'], ia['n']))} | "
                     f"{_fmt_pct(ib)} | {_fmt_pct(il)} | {ia['n']} | "
                     f"{_fmt_pct(_pct(oa['hit'], oa['n']))} | {_fmt_pct(ob)} | "
                     f"{_fmt_pct(ol)} | {oa['n']} |")
    L.append("")

    # ---- TEST B ----------------------------------------------------------
    L += ["## Test B — structure-agreement continuation", "",
          "When yield structure agrees with the pair's dollar read, is the "
          "next-horizon continuation more reliable than when they disagree?", "",
          "| pair | tenor | IS agree% (n) | IS disagree% (n) | OOS agree% (n) | OOS disagree% (n) |",
          "|---|---|---|---|---|---|"]
    for pair, fr in frames.items():
        for t in sorted(fr["per_tenor"]):
            ib = _test_b_structure(fr, t, IS_YEARS, horizon)
            ob = _test_b_structure(fr, t, OOS_YEARS, horizon)
            L.append(
                f"| {pair} | {t} | {_fmt_pct(_pct(ib['agree_hit'], ib['agree_n']))} "
                f"({ib['agree_n']}) | {_fmt_pct(_pct(ib['dis_hit'], ib['dis_n']))} "
                f"({ib['dis_n']}) | {_fmt_pct(_pct(ob['agree_hit'], ob['agree_n']))} "
                f"({ob['agree_n']}) | {_fmt_pct(_pct(ob['dis_hit'], ob['dis_n']))} "
                f"({ob['dis_n']}) |")
    L.append("")

    # ---- VERDICT ---------------------------------------------------------
    verdict, why = _verdict(rows_a, corr_ok)
    L += ["## Verdict", "", f"**{verdict}** — {why}.", "",
          "Ship rule (same as every lever here): the reversal lift must hold in "
          "BOTH splits at a comparable magnitude, on top of a positive foundation "
          "correlation. GREEN -> flip `BONDS_BIAS_ENABLED=1` and run "
          "`bash run_bonds_validation.sh` to A/B the sizing lever on the full "
          "backtest before shipping. YELLOW/RED -> nothing ships; the study stands "
          "as the record of why."]
    return L, verdict


def write_bond_bias(horizon, lookback):
    """Byproduct for the (default-OFF) engine hook: per-date dollar-direction read
    from DGS10 intermediate structure -> data/bond_bias.json.

    { "DGS10": { "YYYY-MM-DD": +1/-1/0, ... }, "_meta": {...} }
    +1 = yields structure UP = dollar-bullish; -1 = dollar-bearish; 0 = flat.
    The engine reads the date's value and confirms it against the trade's dollar
    direction. Uses EURUSD's calendar as the reference daily index.
    """
    from ict import market_structure as ms
    yields = _load_yields()
    if not yields or "DGS10" not in yields:
        print("  (no DGS10 — bond_bias.json not written)")
        return
    fr = _build_frame("EURUSD", yields)
    if fr is None:
        print("  (no EURUSD calendar — bond_bias.json not written)")
        return
    ybars, _ = fr["per_tenor"]["DGS10"]
    idx = fr["index"]
    win = 60
    out = {}
    for i in range(win, len(idx)):
        d = ms.structure_direction(ms.classify(ybars[i - win:i + 1]))
        out[str(idx[i].date())] = int(d)
    payload = {"DGS10": out,
               "_meta": {"source": "FRED DGS10", "structure_window": win,
                         "note": "yields-up=+1=dollar-bullish; read at daily close"}}
    with open(BIAS_OUT, "w") as f:
        json.dump(payload, f)
    print(f"  wrote {os.path.relpath(BIAS_OUT, _ROOT)} ({len(out)} dates)")


def _selftest():
    # pearson: perfectly correlated / anti-correlated / flat
    assert abs(pearson([1, 2, 3, 4], [2, 4, 6, 8]) - 1.0) < 1e-9
    assert abs(pearson([1, 2, 3, 4], [8, 6, 4, 2]) + 1.0) < 1e-9
    assert pearson([1, 1, 1], [1, 2, 3]) is None       # degenerate
    # reversal_hit: up move detected, down move not, forward-bounds respected
    closes = [100, 101, 102, 99, 98]
    assert reversal_hit(closes, 0, 2, 1) is True        # 100 -> 102 up
    assert reversal_hit(closes, 0, 2, -1) is False
    assert reversal_hit(closes, 2, 2, -1) is True       # 102 -> 98 down
    assert reversal_hit(closes, 3, 5, 1) is None        # not enough forward bars
    # lift math
    assert _wilson_lift(6, 10, 50.0) == 10.0            # 60% - 50% = +10pp
    assert _wilson_lift(0, 0, 50.0) is None
    # verdict gating: no foundation -> RED regardless of lifts
    v, _ = _verdict([{"is_lift": 20, "oos_lift": 20, "is_n": 50, "oos_n": 50}], False)
    assert v == "RED", v
    v, _ = _verdict([{"is_lift": 8, "oos_lift": 6, "is_n": 50, "oos_n": 50}], True)
    assert v == "GREEN", v
    v, _ = _verdict([{"is_lift": 8, "oos_lift": -4, "is_n": 50, "oos_n": 50}], True)
    assert v == "RED", v
    # SMT wiring: build a divergence and confirm the smt module fires inverse
    from ict import smt
    # pair sweeps a lower low late; yield ref makes a LOWER high (fails to confirm)
    pair = [Bar(10, 10, 9, 9)] * 10 + [Bar(9, 9, 7, 8)] * 10
    yref = [Bar(2, 3, 2, 2)] * 10 + [Bar(2, 2, 1, 1)] * 10   # ref high fell
    assert smt.smt_divergence(pair, yref, 1, inverse=True, lookback=20) is True
    print("selftest OK — pearson, reversal_hit, lift, verdict gating, SMT inverse wiring")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon-days", type=int, default=3)
    ap.add_argument("--lookback", type=int, default=20)
    ap.add_argument("--emit-bias", action="store_true",
                    help="also write data/bond_bias.json for the (default-off) engine hook")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    result = analyse(a.horizon_days, a.lookback)
    if isinstance(result, tuple):
        lines, verdict = result
    else:
        lines, verdict = result, "?"
    text = "\n".join(lines) + "\n"
    with open(REPORT, "w") as f:
        f.write(text)
    print(text)
    if a.emit_bias:
        write_bond_bias(a.horizon_days, a.lookback)
    print(f"[report → {REPORT}]  verdict={verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
