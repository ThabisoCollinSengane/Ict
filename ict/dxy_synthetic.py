"""Synthetic DXY (US Dollar Index).

OANDA doesn't carry DXY directly. We replicate it with the ICE formula:

    DXY = 50.14348112
        * EURUSD^(-0.576)
        * USDJPY^( 0.136)
        * GBPUSD^(-0.119)
        * USDCAD^( 0.091)
        * USDSEK^( 0.042)
        * USDCHF^( 0.036)

Caller supplies a dict of latest prices for each constituent.
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


def compute_dxy(prices: dict[str, float]) -> float | None:
    """Return synthetic DXY, or None if any constituent is missing."""
    value = DXY_CONSTANT
    for sym, w in WEIGHTS.items():
        p = prices.get(sym)
        if p is None or p <= 0:
            return None
        value *= p ** w
    return value
