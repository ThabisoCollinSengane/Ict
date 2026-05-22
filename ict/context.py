"""Context features: time spent at a level, dwell counts, compression ratios.

Pure helpers that operate on bar lists. Used by FVG scoring (was there
consolidation before the gap?), sweep scoring (had price been building up
against the swept level?), and any other "context before event" check.

All windows are causal — we only look at bars strictly before the event
being scored. No look-ahead.
"""

from typing import Sequence


def time_in_zone_pre_event(bars: Sequence,
                           zone_top: float,
                           zone_bottom: float,
                           lookback: int) -> float:
    """Fraction of the last `lookback` bars whose [Low, High] overlapped
    [zone_bottom, zone_top]. Returns a value in [0, 1].

    Higher = price was consolidating in/around the zone before the event
    (institutional accumulation). 0 = the event came from out-of-zone with
    no prior dwell (e.g. quick sweep-and-go).
    """
    if lookback <= 0 or not bars:
        return 0.0
    window = bars[-lookback:]
    if not window:
        return 0.0
    overlaps = 0
    for b in window:
        if b.High >= zone_bottom and b.Low <= zone_top:
            overlaps += 1
    return overlaps / len(window)


def dwell_at_level(bars: Sequence,
                   level: float,
                   tol: float,
                   lookback: int) -> int:
    """Count of bars in the last `lookback` whose range touched
    [level - tol, level + tol]. Used to detect equal-highs/lows that built up
    before a sweep — institutional stops accumulated.
    """
    if lookback <= 0 or not bars:
        return 0
    window = bars[-lookback:]
    upper, lower = level + tol, level - tol
    return sum(1 for b in window if b.High >= lower and b.Low <= upper)


def compression_ratio(bars: Sequence,
                      short_window: int,
                      long_window: int) -> float:
    """range(last short_window) / range(last long_window). Pure causal.

    <0.5 -> coiled (compression)
    ~1.0 -> normal
    >1.5 -> expanding
    Returns 1.0 if either window is too short / has zero long-range.
    """
    if len(bars) < long_window or short_window <= 0 or long_window <= 0:
        return 1.0
    short = bars[-short_window:]
    long = bars[-long_window:]
    short_range = max(b.High for b in short) - min(b.Low for b in short)
    long_range = max(b.High for b in long) - min(b.Low for b in long)
    if long_range <= 0:
        return 1.0
    return short_range / long_range
