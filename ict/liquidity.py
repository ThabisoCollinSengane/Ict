"""Liquidity helpers: equal highs/lows + sweep detection + round numbers.

Ep 17: Heavy liquidity clusters at round-number levels ending in 00, 20, 50, 80
pips.  For EURUSD/GBPUSD these are x.x000, x.x200, x.x500, x.x800.
"""

import config


def _pip(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


def find_equal_highs(candles, symbol: str, lookback: int = 100) -> list[float]:
    """Return price levels where ≥2 swing highs cluster within tolerance."""
    tol = config.EQ_HIGH_LOW_TOLERANCE_PIPS * _pip(symbol)
    n = len(candles)
    highs = []
    for i in range(max(2, n - lookback), n - 2):
        h = candles[i].High
        if h > candles[i - 1].High and h > candles[i + 1].High:
            highs.append(h)
    clusters = []
    used = [False] * len(highs)
    for i, h in enumerate(highs):
        if used[i]:
            continue
        group = [h]
        used[i] = True
        for j in range(i + 1, len(highs)):
            if not used[j] and abs(highs[j] - h) <= tol:
                group.append(highs[j])
                used[j] = True
        if len(group) >= 2:
            clusters.append(sum(group) / len(group))
    return clusters


def find_equal_lows(candles, symbol: str, lookback: int = 100) -> list[float]:
    tol = config.EQ_HIGH_LOW_TOLERANCE_PIPS * _pip(symbol)
    n = len(candles)
    lows = []
    for i in range(max(2, n - lookback), n - 2):
        l = candles[i].Low
        if l < candles[i - 1].Low and l < candles[i + 1].Low:
            lows.append(l)
    clusters = []
    used = [False] * len(lows)
    for i, l in enumerate(lows):
        if used[i]:
            continue
        group = [l]
        used[i] = True
        for j in range(i + 1, len(lows)):
            if not used[j] and abs(lows[j] - l) <= tol:
                group.append(lows[j])
                used[j] = True
        if len(group) >= 2:
            clusters.append(sum(group) / len(group))
    return clusters


def is_near_round_number(price: float, symbol: str, tol_pips: int = 3) -> bool:
    """Ep 17: True when `price` is within `tol_pips` of a round-number liquidity level.

    Significant levels end in 00, 20, 50, 80 pips (x.x000, x.x200, x.x500, x.x800
    for 4-decimal pairs).  These attract institutional liquidity and are both
    targets and stop-hunt magnets.
    """
    pip = _pip(symbol)
    pips_from_zero = round(price / pip) % 100
    return pips_from_zero in (0, 20, 50, 80) or any(
        abs(pips_from_zero - ref) <= tol_pips for ref in (0, 20, 50, 80, 100)
    )


def detect_sweep(candles, direction: int, lookback: int = 20) -> float | None:
    """Detect a liquidity sweep on the LAST bar.

    direction +1: bullish sweep = price took out a recent low and closed back above it
                  (we expect upside after a sell-side sweep).
    direction -1: bearish sweep = price took out a recent high and closed back below it.
    Returns the swept extreme price, or None.
    """
    if len(candles) < lookback + 1:
        return None
    last = candles[-1]
    window = candles[-(lookback + 1):-1]

    if direction > 0:
        prior_low = min(c.Low for c in window)
        if last.Low < prior_low and last.Close > prior_low:
            return prior_low
    else:
        prior_high = max(c.High for c in window)
        if last.High > prior_high and last.Close < prior_high:
            return prior_high
    return None
