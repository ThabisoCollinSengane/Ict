"""ICT Fibonacci Extension targets — Episode 12 / Standard Deviation projections.

After an OTE entry (62-79% retracement), ICT projects profit targets using
Fibonacci extensions of the initiating swing leg. The standard deviation model
treats each extension level as a probabilistic price magnet:

  100%  (1.0)  — swing midpoint target / equal legs
  127.2% (1.272) — first premium/discount extension (common first TP)
  161.8% (1.618) — golden ratio extension (primary TP zone)
  200%  (2.0)  — full-range extension (runner target)
  261.8% (2.618) — deep extension for high-conviction runs

For a bullish swing (swing_low → swing_high):
  extension = swing_low + rng × ratio

For a bearish swing (swing_high → swing_low):
  extension = swing_high - rng × ratio

This means 100% = the original swing_high (for long) — price returns to where it was.
161.8% = swing_low + rng × 1.618 — the standard "ICT runner" target.
"""

from __future__ import annotations

EXTENSION_RATIOS = (1.272, 1.618, 2.0, 2.618)


def fib_extension_targets(
    swing_low: float,
    swing_high: float,
    direction: int,
) -> list[float]:
    """Compute Fibonacci extension levels from a swing.

    For direction > 0 (bullish): projects above swing_high.
    For direction < 0 (bearish): projects below swing_low.
    Returns levels in ascending order for long, descending for short.
    """
    rng = swing_high - swing_low
    if direction > 0:
        return [swing_low + rng * r for r in EXTENSION_RATIOS]
    else:
        return [swing_high - rng * r for r in EXTENSION_RATIOS]


def nearest_fib_target(
    swing_low: float,
    swing_high: float,
    direction: int,
    entry_price: float,
    min_distance: float,
) -> float | None:
    """Return the nearest Fib extension target at least min_distance beyond entry.

    min_distance should be in price units (e.g. 20 pips × pip_value).
    Returns None if no extension clears the minimum distance.
    """
    targets = fib_extension_targets(swing_low, swing_high, direction)
    for t in targets:
        if direction > 0 and t >= entry_price + min_distance:
            return t
        if direction < 0 and t <= entry_price - min_distance:
            return t
    return None
