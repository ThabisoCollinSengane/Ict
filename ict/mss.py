"""Market Structure Shift (MSS) detection.

A bullish MSS occurs when price closes above the most recent short-term high
that capped a lower-low sequence — i.e., the trend was making lower highs and
a candle's close finally exceeded one of them. Mirrors for bearish MSS.

This distinguishes a true CHoCH from a mere BOS in a trend (BOS continues the
trend; MSS is the first close *against* the prevailing direction).
"""

from dataclasses import dataclass
from typing import Optional

from ict.swings import find_swings


@dataclass
class MSSEvent:
    bar_index: int
    direction: int         # +1 bullish shift, -1 bearish shift
    broken_level: float


def latest_mss(candles) -> Optional[MSSEvent]:
    swings = find_swings(candles)
    if len(swings) < 4:
        return None

    # Identify recent trend by the last 4 swings.
    highs = [s for s in swings if s.kind == +1]
    lows = [s for s in swings if s.kind == -1]

    # Bearish-trend → bullish MSS: last 2 highs are descending AND a later
    # candle closes above the most recent of those descending highs.
    if len(highs) >= 2 and highs[-1].price < highs[-2].price:
        ref = highs[-1]
        for j in range(ref.index + 1, len(candles)):
            if candles[j].Close > ref.price:
                return MSSEvent(j, +1, ref.price)

    # Bullish-trend → bearish MSS: last 2 lows ascending AND a later close
    # breaks the most recent of them.
    if len(lows) >= 2 and lows[-1].price > lows[-2].price:
        ref = lows[-1]
        for j in range(ref.index + 1, len(candles)):
            if candles[j].Close < ref.price:
                return MSSEvent(j, -1, ref.price)

    return None


def mss_direction(candles) -> int:
    ev = latest_mss(candles)
    return ev.direction if ev else 0
