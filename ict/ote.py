"""ICT Optimal Trade Entry (OTE) — 62%/70.5%/79% Fibonacci retracement zone.

After a Break of Structure (BOS), the market typically retraces into the
62–79% zone of the prior swing before continuing in the BOS direction.
Entering within this zone gives a "premium discount" or "premium" entry:

  Bullish OTE: after a bullish BOS, buy when price retraces to the 62–79%
               zone of the (swing_low → swing_high) that caused the BOS.
               ote_bottom = swing_high − rng × 0.79
               ote_top    = swing_high − rng × 0.62

  Bearish OTE: after a bearish BOS, sell when price rallies to the 62–79%
               zone of the (swing_high → swing_low) that caused the BOS.
               ote_bottom = swing_low + rng × 0.62
               ote_top    = swing_low + rng × 0.79

The 70.5% midpoint is the strongest single level within the zone.
"""

from typing import Optional


def ote_zone(swing_low: float, swing_high: float, direction: int) -> tuple[float, float]:
    """Return (ote_low, ote_high) for the OTE zone.

    For a bullish entry (+1) after a swing_low → swing_high move:
      price should retrace to the 62–79% area below the swing_high.
    For a bearish entry (-1) after a swing_high → swing_low move:
      price should rally to the 62–79% area above the swing_low.
    """
    rng = swing_high - swing_low
    if direction > 0:
        return (swing_high - rng * 0.79, swing_high - rng * 0.62)
    else:
        return (swing_low + rng * 0.62, swing_low + rng * 0.79)


def find_swing(candles, direction: int, lookback: int = 20) -> Optional[tuple[float, float]]:
    """Identify the most recent significant swing to define the OTE zone.

    For a bullish BOS (+1): the swing_low is the lowest Low in the first half
    of `lookback` bars; the swing_high is the highest High in the second half
    (the impulsive leg that caused the BOS).

    For a bearish BOS (-1): inverse — highest High then lowest Low.

    Returns (swing_low, swing_high) or None if insufficient data.
    """
    n = len(candles)
    if n < lookback * 2:
        return None

    half = lookback
    first_half = candles[-(half * 2):-half]
    second_half = candles[-half:]

    if direction > 0:
        swing_low  = min(c.Low  for c in first_half)
        swing_high = max(c.High for c in second_half)
    else:
        swing_high = max(c.High for c in first_half)
        swing_low  = min(c.Low  for c in second_half)

    return swing_low, swing_high


def in_ote(
    price: float,
    candles,
    direction: int,
    lookback: int = 20,
    pip_tol: float = 0.0002,
) -> bool:
    """Return True if `price` is inside (or within `pip_tol` of) the OTE zone.

    `pip_tol` defaults to 2 pips — allows a small margin for bar-close timing.
    """
    result = find_swing(candles, direction, lookback)
    if result is None:
        return False
    swing_low, swing_high = result
    rng = swing_high - swing_low
    if rng < pip_tol * 5:       # degenerate swing — too small to be meaningful
        return False
    lo, hi = ote_zone(swing_low, swing_high, direction)
    return (lo - pip_tol) <= price <= (hi + pip_tol)
