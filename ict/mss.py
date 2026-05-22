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
    """Latest MSS-CHoCH event (reversal): last 2 highs descending then a
    close breaks the most recent, or last 2 lows ascending then a close
    breaks the most recent. Detects ONLY reversal events; use
    structural_direction() for either reversal or continuation BOS.
    """
    swings = find_swings(candles)
    if len(swings) < 4:
        return None

    highs = [s for s in swings if s.kind == +1]
    lows = [s for s in swings if s.kind == -1]

    if len(highs) >= 2 and highs[-1].price < highs[-2].price:
        ref = highs[-1]
        for j in range(ref.index + 1, len(candles)):
            if candles[j].Close > ref.price:
                return MSSEvent(j, +1, ref.price)

    if len(lows) >= 2 and lows[-1].price > lows[-2].price:
        ref = lows[-1]
        for j in range(ref.index + 1, len(candles)):
            if candles[j].Close < ref.price:
                return MSSEvent(j, -1, ref.price)

    return None


def mss_direction(candles) -> int:
    ev = latest_mss(candles)
    return ev.direction if ev else 0


def structural_direction(candles) -> int:
    """LTF structural direction: returns +1 / -1 / 0 based on the most
    recent break of structure (whether reversal CHoCH or continuation BOS).

    A bullish read is any of:
      - latest_mss returns +1 (reversal CHoCH)
      - last close is above the most recent unbroken swing high (continuation BOS)
    Mirror for bearish.

    This is the LTF "is structure with us?" check the user-spec asks for
    on H1/M15/M5 — works in trending AND reversing markets, where pure
    MSS-reversal detection silently returns 0.
    """
    mss = mss_direction(candles)
    if mss != 0:
        return mss
    swings = find_swings(candles)
    if not swings or not candles:
        return 0
    highs = [s for s in swings if s.kind == +1]
    lows = [s for s in swings if s.kind == -1]
    last_close = candles[-1].Close
    if highs and last_close > highs[-1].price:
        return +1
    if lows and last_close < lows[-1].price:
        return -1
    return 0
