"""ICT Accumulation -> Manipulation -> Distribution (AMD / Power-of-Three) detection.

Premise
-------
Markets cycle through three phases:

    ACCUMULATION   tight range, low conviction, equal H/L forming.
    MANIPULATION   stop-run above/below the range ("Judas swing"); rejects back inside.
    DISTRIBUTION   real expansion in the opposite direction with displacement + FVG.

We trade ONLY at the manipulation -> distribution handoff. Concretely:

    1. Identify the most recent valid accumulation range on the setup TF (M15).
    2. Confirm the next bar(s) swept one extreme of that range and closed back inside.
       The swept side defines the trade direction (low swept -> long; high swept -> short).
    3. Hand off to the M5 layer for the distribution trigger (FVG, handled in main.py).

A range may persist across many bars (whole Asian session, multi-day coil, etc.). We
scan for the *longest* range ending just before the current bars whose total span fits
inside `MAX_RANGE_PIPS` and whose body count is at least `MIN_RANGE_BARS`. We then
allow the last `MAX_SWEEP_LOOKBACK` bars to contain the manipulation.
"""

from dataclasses import dataclass
from typing import Optional

import config


def _pip(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


@dataclass
class Range:
    """Detected consolidation range. Bar indices are into the candles slice passed in."""
    high: float
    low: float
    start_idx: int     # inclusive
    end_idx: int       # exclusive
    touches_high: int
    touches_low: int

    @property
    def width(self) -> float:
        return self.high - self.low

    @property
    def length_bars(self) -> int:
        return self.end_idx - self.start_idx


def detect_consolidation(
    candles,
    symbol: str,
    min_bars: int = None,
    max_bars: int = None,
    max_range_pips: float = None,
    min_touches: int = None,
    sweep_lookback: int = None,
) -> Optional[Range]:
    """Return the longest valid accumulation range ending within `sweep_lookback`
    bars of the most recent close, or None if no qualifying range exists.

    A range qualifies when:
      - it spans at least `min_bars` consecutive M15 candles,
      - its (max High - min Low) fits inside `max_range_pips`,
      - the high and the low were each touched at least `min_touches` times
        (a "touch" is any bar whose High/Low comes within 1 pip of the extreme).
    """
    min_bars = min_bars or config.AMD_MIN_RANGE_BARS
    max_bars = max_bars or config.AMD_MAX_RANGE_BARS
    max_range_pips = max_range_pips or config.AMD_MAX_RANGE_PIPS
    min_touches = min_touches or config.AMD_MIN_TOUCHES
    sweep_lookback = sweep_lookback or config.AMD_SWEEP_LOOKBACK

    n = len(candles)
    if n < min_bars + 1:
        return None

    pip = _pip(symbol)
    max_width = max_range_pips * pip
    touch_tol = 1.0 * pip  # within 1 pip = "touch"

    best: Optional[Range] = None

    # Range must end somewhere in the last `sweep_lookback` bars so that the
    # manipulation candle(s) are in the most recent window.
    earliest_end = max(min_bars, n - sweep_lookback)
    for end in range(n, earliest_end, -1):
        # Slide the range start back as far as max_bars permits.
        lo_start = max(0, end - max_bars)
        for start in range(lo_start, end - min_bars + 1):
            window = candles[start:end]
            hi = max(c.High for c in window)
            lo = min(c.Low for c in window)
            if (hi - lo) > max_width:
                continue
            th = sum(1 for c in window if abs(c.High - hi) <= touch_tol)
            tl = sum(1 for c in window if abs(c.Low - lo) <= touch_tol)
            if th < min_touches or tl < min_touches:
                continue
            length = end - start
            if best is None or length > best.length_bars:
                best = Range(high=hi, low=lo, start_idx=start, end_idx=end,
                             touches_high=th, touches_low=tl)
        if best is not None:
            # We prefer the longest range ending closest to "now". As soon as we
            # find any qualifying range at this end, keep scanning earlier `end`s
            # only if they could yield a longer range - they can't, so break.
            break
    return best


def detect_manipulation(
    candles,
    rng: Range,
    sweep_lookback: int = None,
) -> Optional[int]:
    """Did price sweep `rng` in the last `sweep_lookback` bars and reject back inside?

    Returns +1 if the LOW was swept (bullish manipulation - look long),
            -1 if the HIGH was swept (bearish manipulation - look short),
            None if no clean sweep happened.
    """
    sweep_lookback = sweep_lookback or config.AMD_SWEEP_LOOKBACK
    # Bars after the range that we'll check for a sweep.
    tail = candles[rng.end_idx:]
    if not tail:
        # No bars after the range - the "now" bar IS still inside the range.
        return None
    tail = tail[-sweep_lookback:]
    last = candles[-1]

    low_swept = any(c.Low < rng.low for c in tail) and last.Close > rng.low
    high_swept = any(c.High > rng.high for c in tail) and last.Close < rng.high

    if low_swept and not high_swept:
        return +1
    if high_swept and not low_swept:
        return -1
    return None


def classify_phase(
    candles,
    symbol: str,
) -> tuple:
    """Return (phase_name, range_or_None, sweep_direction_or_None).

    phase_name in {"NONE", "ACCUMULATION", "MANIPULATION", "DISTRIBUTION"}.
    Useful for logging / debugging; the trade trigger uses detect_consolidation +
    detect_manipulation directly.
    """
    rng = detect_consolidation(candles, symbol)
    if rng is None:
        return ("NONE", None, None)
    # If the range ends at the very last bar, we're still in accumulation.
    if rng.end_idx >= len(candles):
        return ("ACCUMULATION", rng, None)
    sweep = detect_manipulation(candles, rng)
    if sweep is None:
        # Range ended; no clean sweep yet. Could be distribution already starting.
        return ("DISTRIBUTION", rng, None)
    return ("MANIPULATION", rng, sweep)
