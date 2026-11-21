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


# Direction anchor + minimum coverage. Robust to a broker missing a minor
# constituent (e.g. Exness without USDSEK, 4.2% weight): a FLAT DXY halts ALL
# trading, which is far worse than a tiny-weight approximation — the gate only reads
# DXY *direction* (BOS), not its absolute value. EURUSD (57.6%) must be present.
_REQUIRED = ("EURUSD",)
_MIN_CONSTITUENTS = 4


def compute_dxy(prices):
    """Synthetic DXY, robust to a missing constituent. Computes over whatever IS
    present as long as EURUSD and ≥ _MIN_CONSTITUENTS are available; else None.
    With all 6 present (backtest) this is byte-identical to the strict formula."""
    value = DXY_CONSTANT
    used = 0
    for sym, w in WEIGHTS.items():
        p = prices.get(sym)
        if p is None or p <= 0:
            continue                       # skip an unavailable constituent
        value *= p ** w
        used += 1
    if used < _MIN_CONSTITUENTS:
        return None
    for r in _REQUIRED:
        p = prices.get(r)
        if p is None or p <= 0:
            return None
    return value


def compute_dxy_range(highs, lows):
    """(dxy_high, dxy_low) from sign-aware constituent extremes; skips any missing
    constituent (compute_dxy enforces the EURUSD + min-coverage requirement)."""
    high_inputs = {}
    low_inputs = {}
    for sym, w in WEIGHTS.items():
        h = highs.get(sym)
        l = lows.get(sym)
        if h is None or l is None or h <= 0 or l <= 0:
            continue                       # skip an unavailable constituent
        # DXY-high: maximise positively-weighted, minimise negatively-weighted.
        high_inputs[sym] = h if w > 0 else l
        low_inputs[sym] = l if w > 0 else h
    return compute_dxy(high_inputs), compute_dxy(low_inputs)
