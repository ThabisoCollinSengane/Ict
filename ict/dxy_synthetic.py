"""Synthetic DXY (US Dollar Index).

OANDA doesn't carry DXY directly. We replicate it with the ICE formula:

    DXY = 50.14348112
        * EURUSD^(-0.576)
        * USDJPY^( 0.136)
        * GBPUSD^(-0.119)
        * USDCAD^( 0.091)
        * USDSEK^( 0.042)
        * USDCHF^( 0.036)

`compute_dxy(prices)` takes a dict of constituent prices (any consistent point in
time — closes, mids, highs, etc.) and returns the synthetic index value.

`compute_dxy_range(highs, lows)` builds DXY's *high* and *low* for a bar in a
sign-aware way: for positively-weighted constituents (USD/X pairs) DXY rises when
they rise, so we plug their HIGH into the DXY-high calc; for negatively-weighted
constituents (X/USD pairs) DXY rises when they FALL, so we plug their LOW into
the DXY-high calc.
"""

DXY_CONSTANT = 50.14348112
WEIGHTS = {
    "EURUSD": -0.576,
    "USDJPY":  0.136,
    "GBPUSD": -0.119,
    "USDCAD":  0.091,
    "USDSEK":  0.042,
    "USDCHF":  0.036,
}


def compute_dxy(prices):
    """Return synthetic DXY at a single point in time, or None if any input missing."""
    value = DXY_CONSTANT
    for sym, w in WEIGHTS.items():
        p = prices.get(sym)
        if p is None or p <= 0:
            return None
        value *= p ** w
    return value


def compute_dxy_range(highs, lows):
    """Return (dxy_high, dxy_low) using sign-aware constituent extremes.

    `highs` / `lows` are dicts of constituent prices for a single bar.
    Returns (None, None) if any constituent is missing.
    """
    high_inputs = {}
    low_inputs = {}
    for sym, w in WEIGHTS.items():
        h = highs.get(sym)
        l = lows.get(sym)
        if h is None or l is None or h <= 0 or l <= 0:
            return None, None
        # DXY-high: maximise positively-weighted, minimise negatively-weighted.
        high_inputs[sym] = h if w > 0 else l
        low_inputs[sym] = l if w > 0 else h
    return compute_dxy(high_inputs), compute_dxy(low_inputs)
