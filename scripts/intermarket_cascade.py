"""Intermarket cascade — top-down analysis from bonds through DXY to pair selection.

Reusable module for the MM scanner and weekly replay tools.  Implements the
four-layer ICT intermarket model:

  Layer 0: Yield Curve Structure (T5 vs T10 vs T30)
    Compare 5Y (^FVX), 10Y (^TNX), 30Y (^TYX) yields against each other.
    All three trending same direction = strong signal.  SMT divergence
    between maturities = yield curve stress / reversal tell.
    Yields are POSITIVELY correlated with each other (all rise/fall together
    in normal conditions).

  Layer 1: Combined Yields vs DXY
    The combined yield bias from Layer 0 compared to the dollar.
    Yields POSITIVELY correlate with USD (higher yields = capital inflow = USD bid).
    Agreement = continuation; divergence (SMT) = reversal signal.

  Layer 2: DXY vs EURGBP
    Dollar direction from Layer 1 + EURGBP relative strength selects the
    preferred pair (EURUSD or GBPUSD) and trade direction.

  Layer 3: EURUSD vs GBPUSD SMT
    Entry timing confirmation between the two traded pairs.

All bar data uses the shared Bar = namedtuple("Bar", ["Open", "High", "Low", "Close"]).
DataFrames are 5-min OHLC with a UTC DatetimeIndex.
"""
from __future__ import annotations

import os, sys
from collections import namedtuple

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ict.bias import htf_bias
from ict.smt import smt_divergence
from intermarket import resolve_pair_direction

Bar = namedtuple("Bar", ["Open", "High", "Low", "Close"])

# Yahoo Finance tickers for the three maturities
YIELD_TICKERS = {
    "T5":  "^FVX",   # 5-Year Treasury Yield
    "T10": "^TNX",   # 10-Year Treasury Yield
    "T30": "^TYX",   # 30-Year Treasury Yield
}


def _resample(df_5m, tf_str):
    import pandas as pd
    return df_5m.resample(tf_str).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last",
    }).dropna()


def _df_to_bars(df):
    return [Bar(r.Open, r.High, r.Low, r.Close) for _, r in df.iterrows()]


_H1_TF = "1h"
_D1_TF = "1D"
_BIAS_LOOKBACK = 10
_YIELD_BIAS_LOOKBACK = 10   # 10 daily bars = 2 weeks of yield trend
_SMT_LOOKBACK = 20
_YIELD_SMT_LOOKBACK = 10    # 10 daily bars for yield-vs-yield and yield-vs-DXY SMT
_MIN_BARS = 36              # ~3 trading days of US-hours H1 bars
_MIN_YIELD_5M_BARS = 200    # ~1.5 trading days of 5m bars → enough for daily resample


# ---------------------------------------------------------------------------
# Layer 0 — Yield Curve Structure (T5 vs T10 vs T30)
# ---------------------------------------------------------------------------

def _layer0_yield_curve(t5_bars, t10_bars, t30_bars):
    """Analyze yield curve structure across three maturities.

    Returns dict with:
        yield_bias : int (+1 rising, -1 falling, 0 mixed/flat)
        t5_bias, t10_bias, t30_bias : int (individual readings)
        agreement : int (count of maturities agreeing with majority)
        curve_smt : bool (SMT divergence between any two maturities)
        curve_stress : str (description of yield curve state)
        detail : str
    """
    t5b = htf_bias(t5_bars, lookback=_YIELD_BIAS_LOOKBACK) if len(t5_bars) >= _YIELD_BIAS_LOOKBACK else 0
    t10b = htf_bias(t10_bars, lookback=_YIELD_BIAS_LOOKBACK) if len(t10_bars) >= _YIELD_BIAS_LOOKBACK else 0
    t30b = htf_bias(t30_bars, lookback=_YIELD_BIAS_LOOKBACK) if len(t30_bars) >= _YIELD_BIAS_LOOKBACK else 0

    biases = [t5b, t10b, t30b]
    labels = ["T5", "T10", "T30"]
    non_zero = [b for b in biases if b != 0]

    # SMT between maturity pairs (positively correlated → inverse=False)
    # Uses daily bars → daily SMT lookback
    pairs_to_check = [
        (t5_bars, t10_bars, "T5/T10"),
        (t10_bars, t30_bars, "T10/T30"),
        (t5_bars, t30_bars, "T5/T30"),
    ]
    smt_pairs = []
    for a_bars, b_bars, label in pairs_to_check:
        if len(a_bars) < _YIELD_SMT_LOOKBACK or len(b_bars) < _YIELD_SMT_LOOKBACK:
            continue
        for d in (+1, -1):
            if smt_divergence(a_bars, b_bars, direction=d, inverse=False, lookback=_YIELD_SMT_LOOKBACK):
                smt_pairs.append(label)
                break

    curve_smt = len(smt_pairs) > 0

    # Determine majority bias
    bull_count = sum(1 for b in biases if b > 0)
    bear_count = sum(1 for b in biases if b < 0)
    flat_count = sum(1 for b in biases if b == 0)

    if bull_count >= 2:
        yield_bias = +1
        agreement = bull_count
    elif bear_count >= 2:
        yield_bias = -1
        agreement = bear_count
    elif len(non_zero) == 1:
        yield_bias = non_zero[0]
        agreement = 1
    else:
        yield_bias = 0
        agreement = 0

    # Curve stress description
    if bull_count == 3:
        curve_stress = "all yields rising"
    elif bear_count == 3:
        curve_stress = "all yields falling"
    elif bull_count == 2 and bear_count == 1:
        odd = labels[biases.index(-1)]
        curve_stress = f"2 rising, {odd} falling (divergence)"
    elif bear_count == 2 and bull_count == 1:
        odd = labels[biases.index(+1)]
        curve_stress = f"2 falling, {odd} rising (divergence)"
    elif flat_count == 3:
        curve_stress = "all flat"
    else:
        parts = [f"{labels[i]}={_dir(biases[i])}" for i in range(3)]
        curve_stress = " / ".join(parts)

    detail_parts = [f"T5={_dir(t5b)}", f"T10={_dir(t10b)}", f"T30={_dir(t30b)}"]
    if smt_pairs:
        detail_parts.append(f"SMT: {', '.join(smt_pairs)}")
    detail = " | ".join(detail_parts)

    return {
        "yield_bias": yield_bias,
        "t5_bias": t5b,
        "t10_bias": t10b,
        "t30_bias": t30b,
        "agreement": agreement,
        "curve_smt": curve_smt,
        "smt_pairs": smt_pairs,
        "curve_stress": curve_stress,
        "detail": detail,
    }


# ---------------------------------------------------------------------------
# Layer 1 — Combined Yields vs DXY
# ---------------------------------------------------------------------------

def _layer1_yields_vs_dxy(yield_curve, dxy_h1_bars, t10_daily_bars,
                          dxy_daily_bars=None):
    """Compare the combined yield signal to the dollar.

    DXY is ALWAYS the primary dollar signal (it moves the forex pairs).
    Yields add conviction but NEVER override DXY direction — yields lead
    the dollar on weekly/monthly scale, not intraday where we trade.

    DXY bias uses H1 bars (intraday structure).
    SMT between T10 and DXY uses daily bars (both must be on the same TF).

    Returns (dollar_bias, source_str, agreement, smt_detected).
    """
    yb = yield_curve["yield_bias"]
    dxy_bias = htf_bias(dxy_h1_bars, lookback=_BIAS_LOOKBACK)

    # SMT: DXY vs 10Y on DAILY bars (positively correlated → inverse=False)
    smt_detected = False
    dxy_smt_bars = dxy_daily_bars if dxy_daily_bars is not None else dxy_h1_bars
    smt_lb = _YIELD_SMT_LOOKBACK if dxy_daily_bars is not None else _SMT_LOOKBACK
    if len(t10_daily_bars) >= smt_lb and len(dxy_smt_bars) >= smt_lb:
        for d in (+1, -1):
            if smt_divergence(dxy_smt_bars, t10_daily_bars, direction=d,
                              inverse=False, lookback=smt_lb):
                smt_detected = True
                break

    ya = yield_curve["agreement"]
    curve_desc = yield_curve["curve_stress"]

    # Decision tree — DXY is ALWAYS primary
    if dxy_bias != 0 and yb == dxy_bias:
        # Best case: DXY and yields agree
        strength = "strong" if ya == 3 else "moderate"
        return (dxy_bias,
                f"DXY {_dir(dxy_bias)} + yields {_dir(yb)} ({ya}/3 agree, {curve_desc}) = {strength} confirmation",
                True, smt_detected)

    if dxy_bias != 0 and yb == 0:
        # DXY has direction, yields are flat — use DXY
        return (dxy_bias,
                f"DXY {_dir(dxy_bias)} (yields mixed: {curve_desc})",
                False, smt_detected)

    if dxy_bias != 0 and yb != 0 and yb != dxy_bias:
        # DXY and yields DISAGREE — DXY is the actionable signal for forex,
        # but flag SMT (yields diverging = warning, not a reversal signal)
        return (dxy_bias,
                f"DXY {_dir(dxy_bias)} vs yields {_dir(yb)} ({ya}/3, {curve_desc}) — DXY leads, yields diverge (caution)",
                False, True)

    if dxy_bias == 0 and yb != 0:
        # DXY flat, yields have direction — yields HINT but not confirmed
        # Return 0 (flat) because the dollar hasn't moved yet
        return (0,
                f"DXY flat, yields {_dir(yb)} ({ya}/3, {curve_desc}) — waiting for DXY confirmation",
                False, smt_detected)

    return (0, f"both flat (yields: {curve_desc}, DXY flat)", False, smt_detected)


# ---------------------------------------------------------------------------
# Layer 2 — DXY vs EURGBP → pair selection
# ---------------------------------------------------------------------------

def _layer2_pair_selection(dollar_bias, eurgbp_h1_bars):
    eurgbp_bias = htf_bias(eurgbp_h1_bars, lookback=_BIAS_LOOKBACK)

    eu_dir, eu_score = resolve_pair_direction(dollar_bias, eurgbp_bias,
                                              "EURUSD", primary_pair="EURUSD")
    gu_dir, gu_score = resolve_pair_direction(dollar_bias, eurgbp_bias,
                                              "GBPUSD", primary_pair="EURUSD")

    if dollar_bias == 0:
        return None, None, "no dollar bias — no pair selection", eurgbp_bias, 0.0, 0.0

    if eu_score >= gu_score:
        pair, direction = "EURUSD", eu_dir
    else:
        pair, direction = "GBPUSD", gu_dir

    if eurgbp_bias > 0:
        cross_desc = "EURGBP bullish (EUR > GBP)"
    elif eurgbp_bias < 0:
        cross_desc = "EURGBP bearish (GBP > EUR)"
    else:
        cross_desc = "EURGBP flat (both viable)"

    src = f"dollar {_dir(dollar_bias)} + {cross_desc} -> {pair} {_dir(direction)} (EU {eu_score:.2f} / GU {gu_score:.2f})"
    return pair, direction, src, eurgbp_bias, eu_score, gu_score


# ---------------------------------------------------------------------------
# Layer 3 — EURUSD vs GBPUSD SMT for entry timing
# ---------------------------------------------------------------------------

def _layer3_entry_smt(eu_h1_bars, gu_h1_bars, preferred_direction):
    if preferred_direction is None or preferred_direction == 0:
        return False
    if len(eu_h1_bars) < _SMT_LOOKBACK or len(gu_h1_bars) < _SMT_LOOKBACK:
        return False
    return smt_divergence(eu_h1_bars, gu_h1_bars,
                          direction=preferred_direction,
                          inverse=False,
                          lookback=_SMT_LOOKBACK)


def _dir(bias):
    if bias > 0:
        return "bullish"
    if bias < 0:
        return "bearish"
    return "flat"


def _dir_action(direction):
    if direction is None:
        return "—"
    return "BUY" if direction > 0 else "SELL"


# ---------------------------------------------------------------------------
# Main cascade function
# ---------------------------------------------------------------------------

def intermarket_cascade(all_data, check_time=None):
    """Run the full four-layer intermarket cascade.

    Parameters
    ----------
    all_data : dict[str, DataFrame]
        Mapping of ticker name to 5-min OHLC DataFrame (UTC DatetimeIndex).
        Yield keys: ``"T5"`` (5Y), ``"T10"`` (10Y), ``"T30"`` (30Y).
        Also accepts legacy ``"TNX"`` as fallback for ``"T10"``.
        Other keys: ``"DXY"``, ``"EURGBP"``, ``"EURUSD"``, ``"GBPUSD"``.

    check_time : datetime or Timestamp, optional
        UTC timestamp to slice data up to (for replay mode).

    Returns
    -------
    dict  (see code for full key set)
    """
    # Accept legacy "TNX" key as T10 fallback
    data = dict(all_data)
    if "TNX" in data and "T10" not in data:
        data["T10"] = data["TNX"]

    # Determine which yield maturities are available
    yield_keys = [k for k in ("T5", "T10", "T30") if k in data]
    other_required = [k for k in ("DXY", "EURGBP", "EURUSD", "GBPUSD") if k in data]

    if len(yield_keys) == 0:
        return _empty_result("no yield data (need T5/T10/T30)")
    if "DXY" not in data:
        return _empty_result("missing DXY data")

    # Slice to check_time
    sliced = {}
    all_keys = yield_keys + ["DXY", "EURGBP", "EURUSD", "GBPUSD"]
    for key in all_keys:
        if key not in data:
            continue
        df = data[key]
        if check_time is not None:
            df = df.loc[:check_time]
        sliced[key] = df

    # Resample yields to DAILY bars (macro timeframe — yields show clear
    # daily trends, not intraday BOS on H1 which reads flat 97% of the time)
    daily_yields = {}
    for key in yield_keys:
        if key not in sliced or len(sliced[key]) < _MIN_YIELD_5M_BARS:
            continue
        resampled = _resample(sliced[key], _D1_TF)
        if len(resampled) >= _YIELD_BIAS_LOOKBACK:
            daily_yields[key] = _df_to_bars(resampled)

    # Resample DXY/EURGBP/EURUSD/GBPUSD to H1 (intraday structure)
    h1 = {}
    for key in ("DXY", "EURGBP", "EURUSD", "GBPUSD"):
        if key not in sliced or len(sliced[key]) < _MIN_BARS:
            continue
        resampled = _resample(sliced[key], _H1_TF)
        if len(resampled) >= _BIAS_LOOKBACK:
            h1[key] = _df_to_bars(resampled)

    # DXY daily bars for SMT comparison with yields (must be same TF)
    dxy_daily_bars = None
    if "DXY" in sliced and len(sliced["DXY"]) >= _MIN_YIELD_5M_BARS:
        dxy_d = _resample(sliced["DXY"], _D1_TF)
        if len(dxy_d) >= _YIELD_SMT_LOOKBACK:
            dxy_daily_bars = _df_to_bars(dxy_d)

    # Layer 0 — Yield Curve Structure (daily bars)
    avail_yields = [k for k in ("T5", "T10", "T30") if k in daily_yields]
    if len(avail_yields) >= 2:
        t5_bars = daily_yields.get("T5", daily_yields.get(avail_yields[0]))
        t10_bars = daily_yields.get("T10", daily_yields.get(avail_yields[min(1, len(avail_yields)-1)]))
        t30_bars = daily_yields.get("T30", daily_yields.get(avail_yields[-1]))
        yield_curve = _layer0_yield_curve(t5_bars, t10_bars, t30_bars)
    elif len(avail_yields) == 1:
        solo = daily_yields[avail_yields[0]]
        b = htf_bias(solo, lookback=_YIELD_BIAS_LOOKBACK)
        yield_curve = {
            "yield_bias": b, "t5_bias": 0, "t10_bias": 0, "t30_bias": 0,
            "agreement": 1 if b != 0 else 0,
            "curve_smt": False, "smt_pairs": [],
            "curve_stress": f"{avail_yields[0]} only: {_dir(b)}",
            "detail": f"{avail_yields[0]}={_dir(b)} (only maturity available)",
        }
        if avail_yields[0] == "T5":
            yield_curve["t5_bias"] = b
        elif avail_yields[0] == "T10":
            yield_curve["t10_bias"] = b
        elif avail_yields[0] == "T30":
            yield_curve["t30_bias"] = b
    else:
        return _empty_result(f"insufficient yield data after resample (have: {list(daily_yields.keys())})")

    # Layer 1 — Yields (daily) vs DXY (H1 for bias, daily for SMT)
    if "DXY" not in h1:
        return _empty_result("insufficient DXY data after resample")

    ref_yield_bars = daily_yields.get("T10", daily_yields.get(avail_yields[0]))
    dollar_bias, dollar_source, agreement, yields_dxy_smt = \
        _layer1_yields_vs_dxy(yield_curve, h1["DXY"], ref_yield_bars,
                              dxy_daily_bars=dxy_daily_bars)

    # Layer 2 — DXY vs EURGBP → pair selection
    if "EURGBP" in h1:
        pair, direction, pair_source, eurgbp_bias, eu_score, gu_score = \
            _layer2_pair_selection(dollar_bias, h1["EURGBP"])
    else:
        pair, direction, pair_source = None, None, "EURGBP data unavailable"
        eurgbp_bias, eu_score, gu_score = 0, 0.0, 0.0
        if dollar_bias > 0:
            pair, direction = "GBPUSD", -1
            pair_source = "dollar bullish, no EURGBP → default SELL GBPUSD"
        elif dollar_bias < 0:
            pair, direction = "EURUSD", +1
            pair_source = "dollar bearish, no EURGBP → default BUY EURUSD"

    # Layer 3 — EURUSD vs GBPUSD SMT entry confirmation
    entry_smt = False
    if "EURUSD" in h1 and "GBPUSD" in h1:
        entry_smt = _layer3_entry_smt(h1["EURUSD"], h1["GBPUSD"], direction)

    summary = _build_summary(dollar_bias, dollar_source, pair, direction,
                             entry_smt, agreement, yields_dxy_smt, yield_curve)

    return {
        "dollar_bias": dollar_bias,
        "dollar_source": dollar_source,
        "bonds_dxy_agreement": agreement,
        "bonds_dxy_smt": yields_dxy_smt,
        "yield_curve": yield_curve,
        "preferred_pair": pair,
        "preferred_direction": direction,
        "pair_source": pair_source,
        "eurgbp_bias": eurgbp_bias,
        "eu_score": eu_score,
        "gu_score": gu_score,
        "entry_smt": entry_smt,
        "summary": summary,
    }


def _empty_result(reason):
    return {
        "dollar_bias": 0,
        "dollar_source": reason,
        "bonds_dxy_agreement": False,
        "bonds_dxy_smt": False,
        "yield_curve": None,
        "preferred_pair": None,
        "preferred_direction": None,
        "pair_source": reason,
        "eurgbp_bias": 0,
        "eu_score": 0.0,
        "gu_score": 0.0,
        "entry_smt": False,
        "summary": f"No analysis: {reason}",
    }


def _build_summary(dollar_bias, dollar_source, pair, direction,
                   entry_smt, agreement, smt, yield_curve):
    if dollar_bias == 0:
        return "Dollar unclear — no trade signal"

    parts = [f"USD {_dir(dollar_bias)}"]

    if yield_curve:
        ya = yield_curve["agreement"]
        parts.append(f"({ya}/3 yields agree)")
        if yield_curve["curve_smt"]:
            parts.append(f"[curve SMT: {', '.join(yield_curve['smt_pairs'])}]")

    if agreement:
        parts.append("(yields+DXY confirm)")
    elif smt:
        parts.append("(yields/DXY SMT)")

    if pair and direction is not None:
        parts.append(f"-> {_dir_action(direction)} {pair}")
    else:
        parts.append("-> no preferred pair")

    if entry_smt:
        parts.append("[EU/GU SMT]")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def selftest():
    print("intermarket_cascade: imports OK")

    assert callable(htf_bias)
    assert callable(smt_divergence)
    assert callable(resolve_pair_direction)
    assert callable(intermarket_cascade)
    assert callable(_layer0_yield_curve)
    assert callable(_layer1_yields_vs_dxy)
    assert callable(_layer2_pair_selection)
    assert callable(_layer3_entry_smt)

    # Smoke test with synthetic bars
    bars = [Bar(1.0, 1.1, 0.9, 1.05)] * 30
    b = htf_bias(bars, lookback=10)
    assert b in (+1, -1, 0)

    d = smt_divergence(bars, bars, direction=+1, inverse=False, lookback=20)
    assert isinstance(d, bool)

    dir_, score = resolve_pair_direction(+1, -1, "EURUSD", "EURUSD")
    assert dir_ is not None
    assert isinstance(score, float)

    # Test layer0 with synthetic bars
    yc = _layer0_yield_curve(bars, bars, bars)
    assert "yield_bias" in yc
    assert "agreement" in yc
    assert "curve_smt" in yc
    assert "curve_stress" in yc

    print("intermarket_cascade: selftest PASSED")
    return True


if __name__ == "__main__":
    selftest()
