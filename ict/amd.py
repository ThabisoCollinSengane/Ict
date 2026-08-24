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

Performance
-----------
The inner consolidation search uses a right-to-left sweep with incremental hi/lo
tracking, reducing the per-end complexity from O(max_bars * window) to O(max_bars).
This matters because detect_amd_setup and detect_breakout are called per pair per
5-min bar (~3 pairs * ~4000 bars = 12,000 calls per 10-day backtest).
"""

from dataclasses import dataclass
from typing import Optional, List

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


def _find_best_range(candles, end: int, min_bars: int, max_bars: int,
                     max_width: float, touch_tol: float, min_touches: int) -> Optional[Range]:
    """Find the longest qualifying consolidation range ending at `end`.

    Scans start positions from (end - min_bars) backward to (end - max_bars),
    incrementally tracking hi/lo AND touch counts as each bar is added.
    Touch counts are only recomputed from scratch when an extreme changes
    (which redefines what counts as a "touch"); otherwise only the new bar
    is checked -- O(1) per step instead of O(window_len).
    """
    best: Optional[Range] = None
    lo_start = max(0, end - max_bars)

    init_start = end - min_bars
    if init_start < lo_start:
        return None

    # Initialize hi/lo and touch counts from the minimum window
    window_hi = -1e30
    window_lo = 1e30
    for i in range(init_start, end):
        c = candles[i]
        if c.High > window_hi:
            window_hi = c.High
        if c.Low < window_lo:
            window_lo = c.Low

    # Count touches for the initial window
    _abs = abs  # local ref for speed
    th = 0
    tl = 0
    for i in range(init_start, end):
        if _abs(candles[i].High - window_hi) <= touch_tol:
            th += 1
        if _abs(candles[i].Low - window_lo) <= touch_tol:
            tl += 1

    if (window_hi - window_lo) <= max_width and th >= min_touches and tl >= min_touches:
        best = Range(high=window_hi, low=window_lo, start_idx=init_start, end_idx=end,
                     touches_high=th, touches_low=tl)

    # Grow the window leftward one bar at a time
    for start in range(init_start - 1, lo_start - 1, -1):
        c = candles[start]
        new_hi = window_hi if c.High <= window_hi else c.High
        new_lo = window_lo if c.Low >= window_lo else c.Low

        if (new_hi - new_lo) > max_width:
            break

        if new_hi != window_hi or new_lo != window_lo:
            # Extreme changed -- must recount touches from scratch
            window_hi = new_hi
            window_lo = new_lo
            th = 0
            tl = 0
            for i in range(start, end):
                if _abs(candles[i].High - window_hi) <= touch_tol:
                    th += 1
                if _abs(candles[i].Low - window_lo) <= touch_tol:
                    tl += 1
        else:
            # Extremes unchanged -- just check the new bar
            if _abs(c.High - window_hi) <= touch_tol:
                th += 1
            if _abs(c.Low - window_lo) <= touch_tol:
                tl += 1

        if th < min_touches or tl < min_touches:
            continue
        length = end - start
        if best is None or length > best.length_bars:
            best = Range(high=window_hi, low=window_lo, start_idx=start, end_idx=end,
                         touches_high=th, touches_low=tl)

    return best


def detect_consolidation(
    candles,
    symbol: str,
    min_bars: int = None,
    max_bars: int = None,
    max_range_pips: float = None,
    min_touches: int = None,
    range_end_lookback: int = None,
) -> Optional[Range]:
    """Return the longest valid accumulation range ending within `range_end_lookback`
    bars of the most recent close, or None if no qualifying range exists.

    `range_end_lookback` controls how far back the RANGE END can be.  This is
    intentionally separate from `AMD_SWEEP_LOOKBACK` (used by detect_manipulation)
    because ICT setups have the accumulation range end hours before the manipulation
    sweep (e.g. Asia range -> London/NY manipulation).

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
    range_end_lookback = range_end_lookback or config.AMD_RANGE_END_LOOKBACK

    n = len(candles)
    if n < min_bars + 1:
        return None

    pip = _pip(symbol)
    max_width = max_range_pips * pip
    touch_tol = 1.0 * pip

    earliest_end = max(min_bars, n - range_end_lookback)
    for end in range(n - 1, earliest_end - 1, -1):
        best = _find_best_range(candles, end, min_bars, max_bars, max_width, touch_tol, min_touches)
        if best is not None:
            return best
    return None


def detect_manipulation(
    candles,
    rng: Range,
    sweep_lookback: int = None,
) -> Optional[int]:
    """Did price sweep `rng` in the last `sweep_lookback` bars from NOW and reject back inside?

    Returns +1 if the LOW was swept (bullish manipulation - look long),
            -1 if the HIGH was swept (bearish manipulation - look short),
            None if no clean sweep happened.

    The sweep window is the last `sweep_lookback` bars from the END of `candles`
    (not from the range end), so this remains tight regardless of how long ago
    the accumulation range ended.
    """
    sweep_lookback = sweep_lookback or config.AMD_SWEEP_LOOKBACK
    n = len(candles)
    recent_start = max(rng.end_idx, n - sweep_lookback)
    recent = candles[recent_start:]
    if not recent:
        return None
    last = candles[-1]

    low_swept = any(c.Low < rng.low for c in recent) and last.Close > rng.low
    high_swept = any(c.High > rng.high for c in recent) and last.Close < rng.high

    if low_swept and not high_swept:
        return +1
    if high_swept and not low_swept:
        return -1
    return None


def detect_amd_setup(
    candles,
    symbol: str,
    min_bars: int = None,
    max_bars: int = None,
    max_range_pips: float = None,
    min_touches: int = None,
    range_end_lookback: int = None,
    sweep_lookback: int = None,
) -> Optional[tuple]:
    """Find the most recent consolidation range that has already been swept
    and rejected, returning (Range, direction) or None.

    Unlike calling detect_consolidation then detect_manipulation separately,
    this function does NOT stop at the first consolidation it finds.  It keeps
    scanning earlier range-end positions until it locates a range whose
    manipulation sweep already occurred within AMD_SWEEP_LOOKBACK bars *after
    that range end*.  This correctly handles the ICT Asia-range -> London-sweep
    -> NY-entry pattern where the sweep can be 20-40 M15 bars after the range.
    """
    min_bars = min_bars or config.AMD_MIN_RANGE_BARS
    max_bars = max_bars or config.AMD_MAX_RANGE_BARS
    max_range_pips = max_range_pips or config.AMD_MAX_RANGE_PIPS
    min_touches = min_touches or config.AMD_MIN_TOUCHES
    range_end_lookback = range_end_lookback or config.AMD_RANGE_END_LOOKBACK
    sweep_lookback = sweep_lookback or config.AMD_SWEEP_LOOKBACK

    n = len(candles)
    if n < min_bars + 1:
        return None

    pip = _pip(symbol)
    max_width = max_range_pips * pip
    touch_tol = 1.0 * pip
    last = candles[-1]

    earliest_end = max(min_bars, n - range_end_lookback)

    for end in range(n - 1, earliest_end - 1, -1):
        best = _find_best_range(candles, end, min_bars, max_bars, max_width, touch_tol, min_touches)

        if best is None:
            continue

        # Check sweep in the window AFTER the range (not a sliding window from now).
        tail_end = min(end + sweep_lookback, n)
        tail = candles[end:tail_end]
        if not tail:
            continue

        low_swept = any(c.Low < best.low for c in tail) and last.Close > best.low
        high_swept = any(c.High > best.high for c in tail) and last.Close < best.high

        if low_swept and not high_swept:
            return (best, +1)
        if high_swept and not low_swept:
            return (best, -1)

    return None


def detect_breakout(
    candles,
    symbol: str,
    min_bars: int = None,
    max_bars: int = None,
    max_range_pips: float = None,
    min_touches: int = None,
    range_end_lookback: int = None,
    sweep_lookback: int = None,
    hold_pips: float = None,
) -> Optional[tuple]:
    """Find a consolidation range that price has CLEARED and is HOLDING beyond.

    This is the inverse of detect_amd_setup. Where the Judas model wants a sweep
    that closes BACK inside the range (manipulation -> fade), the breakout model
    wants price to clear an extreme and HOLD outside it (expansion -> follow):

        ACCUMULATION   tight range forms (same as Judas detection).
        EXPANSION      price closes beyond an extreme by at least `hold_pips`
                       and the last close is still holding on that side
                       (no rejection back into the range).

    Returns (Range, direction) where:
        +1  the HIGH was cleared and held  -> bullish continuation (look long)
        -1  the LOW was cleared and held   -> bearish continuation (look short)
        None if no clean held breakout exists.

    A pullback into the old range is allowed AFTER the hold is confirmed -- that
    retest is where breakers/FVGs form for the entry. The hold is judged from the
    breakout extreme of the tail, not the very last bar, so a retest still
    qualifies as long as price cleared and held earlier in the window.
    """
    min_bars = min_bars or config.AMD_MIN_RANGE_BARS
    max_bars = max_bars or config.AMD_MAX_RANGE_BARS
    max_range_pips = max_range_pips or config.AMD_MAX_RANGE_PIPS
    min_touches = min_touches or config.AMD_MIN_TOUCHES
    range_end_lookback = range_end_lookback or config.AMD_RANGE_END_LOOKBACK
    sweep_lookback = sweep_lookback or config.AMD_SWEEP_LOOKBACK
    hold_pips = hold_pips if hold_pips is not None else config.BREAKOUT_HOLD_PIPS

    n = len(candles)
    if n < min_bars + 1:
        return None

    pip = _pip(symbol)
    max_width = max_range_pips * pip
    touch_tol = 1.0 * pip
    hold_dist = hold_pips * pip
    last = candles[-1]

    earliest_end = max(min_bars, n - range_end_lookback)

    for end in range(n - 1, earliest_end - 1, -1):
        best = _find_best_range(candles, end, min_bars, max_bars, max_width, touch_tol, min_touches)

        if best is None:
            continue

        tail_end = min(end + sweep_lookback, n)
        tail = candles[end:tail_end]
        if not tail:
            continue

        high_break = (
            any(c.Close > best.high + hold_dist for c in tail)
            and last.Close > best.low
        )
        low_break = (
            any(c.Close < best.low - hold_dist for c in tail)
            and last.Close < best.high
        )

        if high_break and not low_break:
            return (best, +1)
        if low_break and not high_break:
            return (best, -1)

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
    if rng.end_idx >= len(candles):
        return ("ACCUMULATION", rng, None)
    sweep = detect_manipulation(candles, rng)
    if sweep is None:
        return ("DISTRIBUTION", rng, None)
    return ("MANIPULATION", rng, sweep)
