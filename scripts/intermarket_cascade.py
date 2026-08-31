"""Intermarket cascade — top-down analysis from bonds through DXY to pair selection.

Reusable module for the MM scanner and weekly replay tools.  Implements the
three-layer ICT intermarket model:

  Layer 1: Bonds/Yields (^TNX) vs DXY
    Yields are POSITIVELY correlated with the dollar.  Agreement = continuation;
    divergence (SMT) = reversal signal.  Yields lead the dollar.

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

# ---------------------------------------------------------------------------
# Path setup — allow import from the repo root
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ict.bias import htf_bias
from ict.smt import smt_divergence
from intermarket import resolve_pair_direction

# ---------------------------------------------------------------------------
# Bar type — same namedtuple used by mm_scanner / mm_weekly_replay
# ---------------------------------------------------------------------------
Bar = namedtuple("Bar", ["Open", "High", "Low", "Close"])


# ---------------------------------------------------------------------------
# Helpers (local — no import from scanner)
# ---------------------------------------------------------------------------

def _resample(df_5m, tf_str):
    """Resample a 5-min OHLC DataFrame to a higher timeframe."""
    import pandas as pd  # noqa: F811 — deferred so the module loads without pandas
    return df_5m.resample(tf_str).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last",
    }).dropna()


def _df_to_bars(df):
    """Convert DataFrame rows to a list of Bar namedtuples."""
    return [Bar(r.Open, r.High, r.Low, r.Close) for _, r in df.iterrows()]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_H1_TF = "1h"
_BIAS_LOOKBACK = 10      # bars for htf_bias (H1)
_SMT_LOOKBACK = 20       # bars for smt_divergence


# ---------------------------------------------------------------------------
# Layer 1 — Bonds/Yields vs DXY
# ---------------------------------------------------------------------------

def _layer1_bonds_dxy(tnx_h1_bars, dxy_h1_bars):
    """Determine dollar bias from the yields-vs-DXY relationship.

    Returns (dollar_bias, source_str, agreement, smt_detected).
    """
    yields_bias = htf_bias(tnx_h1_bars, lookback=_BIAS_LOOKBACK)
    dxy_bias = htf_bias(dxy_h1_bars, lookback=_BIAS_LOOKBACK)

    # SMT check: test both long and short directions.
    # Yields are POSITIVELY correlated with DXY → inverse=False.
    # SMT fires when DXY sweeps an extreme that yields fail to confirm.
    smt_bull = smt_divergence(dxy_h1_bars, tnx_h1_bars,
                              direction=+1, inverse=False,
                              lookback=_SMT_LOOKBACK)
    smt_bear = smt_divergence(dxy_h1_bars, tnx_h1_bars,
                              direction=-1, inverse=False,
                              lookback=_SMT_LOOKBACK)
    smt_detected = smt_bull or smt_bear

    # Decision tree
    if yields_bias == dxy_bias and dxy_bias != 0:
        # Agreement — continuation
        return dxy_bias, f"yields {_dir(yields_bias)} + DXY {_dir(dxy_bias)} agree", True, smt_detected

    if yields_bias != 0 and dxy_bias == 0:
        # Yields lead, DXY flat
        return yields_bias, f"yields LEAD {_dir(yields_bias)}, DXY flat", False, smt_detected

    if yields_bias != 0 and dxy_bias != 0 and yields_bias != dxy_bias:
        # SMT divergence — yields lead, DXY should follow
        return yields_bias, f"SMT divergence: yields {_dir(yields_bias)} vs DXY {_dir(dxy_bias)}", False, True

    if yields_bias == 0 and dxy_bias != 0:
        # Yields flat, DXY has direction — use DXY alone
        return dxy_bias, f"DXY {_dir(dxy_bias)} alone (yields flat)", False, smt_detected

    # Both flat
    return 0, "both yields and DXY flat", False, smt_detected


# ---------------------------------------------------------------------------
# Layer 2 — DXY vs EURGBP → pair selection
# ---------------------------------------------------------------------------

def _layer2_pair_selection(dollar_bias, eurgbp_h1_bars):
    """Select preferred pair and direction from dollar bias + EURGBP.

    Returns (preferred_pair, preferred_direction, pair_source, eurgbp_bias,
             eu_score, gu_score).
    """
    eurgbp_bias = htf_bias(eurgbp_h1_bars, lookback=_BIAS_LOOKBACK)

    eu_dir, eu_score = resolve_pair_direction(dollar_bias, eurgbp_bias,
                                              "EURUSD", primary_pair="EURUSD")
    gu_dir, gu_score = resolve_pair_direction(dollar_bias, eurgbp_bias,
                                              "GBPUSD", primary_pair="EURUSD")

    if dollar_bias == 0:
        return None, None, "no dollar bias — no pair selection", eurgbp_bias, 0.0, 0.0

    # Pick the pair with the higher im_score
    if eu_score >= gu_score:
        pair = "EURUSD"
        direction = eu_dir
    else:
        pair = "GBPUSD"
        direction = gu_dir

    # Build source description
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
    """Check EURUSD vs GBPUSD SMT divergence in the preferred direction.

    EURUSD and GBPUSD are positively correlated (both X/USD), so
    inverse=False.

    Returns bool.
    """
    if preferred_direction is None or preferred_direction == 0:
        return False
    return smt_divergence(eu_h1_bars, gu_h1_bars,
                          direction=preferred_direction,
                          inverse=False,
                          lookback=_SMT_LOOKBACK)


# ---------------------------------------------------------------------------
# Direction label helper
# ---------------------------------------------------------------------------

def _dir(bias):
    """Human-readable direction label."""
    if bias > 0:
        return "bullish"
    if bias < 0:
        return "bearish"
    return "flat"


def _dir_action(direction):
    """Trade action label."""
    if direction is None:
        return "—"
    return "BUY" if direction > 0 else "SELL"


# ---------------------------------------------------------------------------
# Main cascade function
# ---------------------------------------------------------------------------

def intermarket_cascade(all_data, check_time=None):
    """Run the full three-layer intermarket cascade.

    Parameters
    ----------
    all_data : dict[str, DataFrame]
        Mapping of pair/ticker name to a DataFrame with OHLC 5-min bars
        (UTC DatetimeIndex).  Must include keys:
        ``"TNX"`` (10Y yield), ``"DXY"``, ``"EURGBP"``, ``"EURUSD"``,
        ``"GBPUSD"``.
    check_time : datetime or Timestamp, optional
        UTC timestamp to slice data up to (for replay mode).  If *None*,
        all available data is used.

    Returns
    -------
    dict
        dollar_bias : int (+1 bullish, -1 bearish, 0 unclear)
        dollar_source : str
        bonds_dxy_agreement : bool
        bonds_dxy_smt : bool
        preferred_pair : str or None
        preferred_direction : int or None (+1 BUY, -1 SELL)
        pair_source : str
        eurgbp_bias : int
        eu_score : float
        gu_score : float
        entry_smt : bool
        summary : str
    """
    required = ("TNX", "DXY", "EURGBP", "EURUSD", "GBPUSD")
    missing = [k for k in required if k not in all_data]
    if missing:
        return _empty_result(f"missing data: {', '.join(missing)}")

    # Slice to check_time if provided (replay mode)
    sliced = {}
    for key in required:
        df = all_data[key]
        if check_time is not None:
            df = df.loc[:check_time]
        sliced[key] = df

    # Verify we have enough data after slicing
    for key in required:
        if len(sliced[key]) < (_BIAS_LOOKBACK + 2) * 12:
            # Need at least ~12 5-min bars per H1 bar, times lookback+2
            return _empty_result(f"insufficient data for {key} ({len(sliced[key])} bars)")

    # Resample to H1
    tnx_h1 = _df_to_bars(_resample(sliced["TNX"], _H1_TF))
    dxy_h1 = _df_to_bars(_resample(sliced["DXY"], _H1_TF))
    eurgbp_h1 = _df_to_bars(_resample(sliced["EURGBP"], _H1_TF))
    eu_h1 = _df_to_bars(_resample(sliced["EURUSD"], _H1_TF))
    gu_h1 = _df_to_bars(_resample(sliced["GBPUSD"], _H1_TF))

    # Layer 1 — Bonds/Yields vs DXY
    dollar_bias, dollar_source, agreement, smt = _layer1_bonds_dxy(tnx_h1, dxy_h1)

    # Layer 2 — DXY vs EURGBP → pair selection
    pair, direction, pair_source, eurgbp_bias, eu_score, gu_score = \
        _layer2_pair_selection(dollar_bias, eurgbp_h1)

    # Layer 3 — EURUSD vs GBPUSD SMT entry confirmation
    entry_smt = _layer3_entry_smt(eu_h1, gu_h1, direction)

    # Build one-line summary
    summary = _build_summary(dollar_bias, dollar_source, pair, direction,
                             entry_smt, agreement, smt)

    return {
        "dollar_bias": dollar_bias,
        "dollar_source": dollar_source,
        "bonds_dxy_agreement": agreement,
        "bonds_dxy_smt": smt,
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
    """Return a result dict indicating no analysis was possible."""
    return {
        "dollar_bias": 0,
        "dollar_source": reason,
        "bonds_dxy_agreement": False,
        "bonds_dxy_smt": False,
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
                   entry_smt, agreement, smt):
    """Compose a one-line summary of the cascade result."""
    if dollar_bias == 0:
        return "Dollar unclear — no trade signal"

    parts = [f"USD {_dir(dollar_bias)}"]

    if agreement:
        parts.append("(yields+DXY agree)")
    elif smt:
        parts.append("(yields/DXY SMT)")

    if pair and direction is not None:
        parts.append(f"-> {_dir_action(direction)} {pair}")
    else:
        parts.append("-> no preferred pair")

    if entry_smt:
        parts.append("[EU/GU SMT confirms]")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def selftest():
    """Verify that all imports resolve and the cascade function is callable."""
    print("intermarket_cascade: imports OK")

    # Verify the three ICT module functions are callable
    assert callable(htf_bias), "htf_bias not callable"
    assert callable(smt_divergence), "smt_divergence not callable"
    assert callable(resolve_pair_direction), "resolve_pair_direction not callable"

    # Verify intermarket_cascade itself
    assert callable(intermarket_cascade), "intermarket_cascade not callable"

    # Verify _layer helpers
    assert callable(_layer1_bonds_dxy), "_layer1_bonds_dxy not callable"
    assert callable(_layer2_pair_selection), "_layer2_pair_selection not callable"
    assert callable(_layer3_entry_smt), "_layer3_entry_smt not callable"

    # Quick smoke test with synthetic bars to confirm no crashes
    bars = [Bar(1.0, 1.1, 0.9, 1.05)] * 30
    b = htf_bias(bars, lookback=10)
    assert b in (+1, -1, 0), f"htf_bias returned unexpected value: {b}"

    d = smt_divergence(bars, bars, direction=+1, inverse=False, lookback=20)
    assert isinstance(d, bool), f"smt_divergence returned non-bool: {d}"

    dir_, score = resolve_pair_direction(+1, -1, "EURUSD", "EURUSD")
    assert dir_ is not None, "resolve_pair_direction returned None direction"
    assert isinstance(score, float), "resolve_pair_direction returned non-float score"

    print("intermarket_cascade: selftest PASSED")
    return True


if __name__ == "__main__":
    selftest()
