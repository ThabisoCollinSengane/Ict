"""Dealing Range + Premium / Discount logic.

ICT Case Studies — "Dealing Ranges" & "Premium / Discount":

DEALING RANGE DEFINITION
------------------------
A dealing range (DR) is formed when the market takes out one side of liquidity
(Buyside Liquidity / BSL) and then reverses to take out the other side (Sellside
Liquidity / SSL), OR vice versa.  The resulting range is bounded by those two
swept extremes:
    DR high  = the BSL extreme that was swept
    DR low   = the SSL extreme that was swept

Once both sides have been taken we have a *confirmed* dealing range.

The key behavioural rule:
  - If we have NOT yet taken BSL we will likely go for SSL next.
  - If we came from BSL (i.e. BSL was swept most recently) we will likely take SSL next.
  → The market always wants to trade back into the PD arrays of the dealing range and
    eventually take out the opposite side of liquidity.

PREMIUM / DISCOUNT
------------------
Within ANY range (a dealing range, a market-structure swing, a 1m MSS range) the
50% midpoint is the "equilibrium" level.

    equilibrium = (range_high + range_low) / 2

    PREMIUM zone:  current_price > equilibrium   (upper half of the range)
    DISCOUNT zone: current_price < equilibrium   (lower half of the range)
    AT EQUILIBRIUM: current_price == equilibrium (exactly 50%)

Trading bias:
    Buys  → look for entries in DISCOUNT (price below 50%).
    Sells → look for entries in PREMIUM  (price above 50%).

Smart money buys in discount and sells in premium; retail does the opposite.

When looking for targets:
    If selling in premium → target a FVG / Liquidity / OB in DISCOUNT.
    If buying  in discount → target a FVG / Liquidity / OB in PREMIUM.

SUPER BULLISH / HEAVY DISCOUNT
-------------------------------
Applied relative to the Midnight Open (MNO) and the 8:30 AM open:

    Super Bullish: expecting bullish day; price barely trades below MNO or 8:30.
        → Use the 8:30 opening as the reference since we're already above MNO.

    Heavy Discount: expecting bullish day but at 8:30 price is still below BOTH
        MNO and the 8:30 opening.
        → This is "heavy discount" — strongest buy condition.

LOW PROBABILITY CONDITIONS (from "Low Probability Conditions.pdf")
------------------------------------------------------------------
Avoid new trades under any of the following:
    1. NFP week: Wednesday, Thursday, Friday in New York are low probability.
    2. FOMC caused a major whipsaw: London AND the AM session are low probability
       for the rest of that day.
    3. Trading against the daily trend.
"""

from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class DealingRange:
    """A confirmed dealing range bounded by two swept liquidity extremes."""
    high: float        # BSL extreme that was swept (upper bound)
    low: float         # SSL extreme that was swept (lower bound)

    # Which side was swept *most recently* (+1 = BSL swept last, -1 = SSL swept last).
    # This tells us which side is the *next likely target*.
    last_swept: int    # +1 if BSL was swept last; -1 if SSL was swept last

    @property
    def equilibrium(self) -> float:
        """50% level — the boundary between premium and discount."""
        return (self.high + self.low) / 2.0

    @property
    def width(self) -> float:
        return self.high - self.low

    def premium_discount(self, price: float) -> str:
        """Return 'PREMIUM', 'DISCOUNT', or 'EQUILIBRIUM' for the given price."""
        eq = self.equilibrium
        if price > eq:
            return "PREMIUM"
        if price < eq:
            return "DISCOUNT"
        return "EQUILIBRIUM"

    def is_premium(self, price: float) -> bool:
        return price > self.equilibrium

    def is_discount(self, price: float) -> bool:
        return price < self.equilibrium

    def next_likely_target(self) -> str:
        """Based on which side was swept last, return the next likely target side."""
        if self.last_swept == +1:
            # BSL swept last → SSL is next likely target
            return "SSL"
        # SSL swept last → BSL is next likely target
        return "BSL"


# ---------------------------------------------------------------------------
# Equilibrium helpers (used on any range, not just a full dealing range)
# ---------------------------------------------------------------------------

def equilibrium(range_high: float, range_low: float) -> float:
    """50% midpoint of any range. This is THE level that separates premium from discount."""
    return (range_high + range_low) / 2.0


def premium_discount(price: float, range_high: float, range_low: float) -> str:
    """Classify `price` as 'PREMIUM', 'DISCOUNT', or 'EQUILIBRIUM' within the range."""
    eq = equilibrium(range_high, range_low)
    if price > eq:
        return "PREMIUM"
    if price < eq:
        return "DISCOUNT"
    return "EQUILIBRIUM"


def is_valid_entry_zone(
    price: float,
    range_high: float,
    range_low: float,
    direction: int,
) -> bool:
    """Return True if `price` is in the correct half of the range for a trade entry.

    Buys  (+1) require price to be at or below equilibrium (DISCOUNT zone).
    Sells (-1) require price to be at or above equilibrium (PREMIUM zone).
    """
    eq = equilibrium(range_high, range_low)
    if direction > 0:
        return price <= eq      # buy in discount
    return price >= eq          # sell in premium


def is_valid_target_zone(
    target_price: float,
    range_high: float,
    range_low: float,
    direction: int,
) -> bool:
    """Return True if `target_price` is in the correct half of the range for a target.

    When buying in discount → target must be in PREMIUM (above equilibrium).
    When selling in premium → target must be in DISCOUNT (below equilibrium).
    """
    eq = equilibrium(range_high, range_low)
    if direction > 0:
        return target_price >= eq   # target in premium
    return target_price <= eq       # target in discount


# ---------------------------------------------------------------------------
# Dealing range detection from a candle series
# ---------------------------------------------------------------------------

def _find_swing_highs(candles) -> list[tuple[int, float]]:
    """Return (bar_index, price) for all local swing highs (higher than neighbours)."""
    n = len(candles)
    out = []
    for i in range(1, n - 1):
        if candles[i].High > candles[i - 1].High and candles[i].High > candles[i + 1].High:
            out.append((i, candles[i].High))
    return out


def _find_swing_lows(candles) -> list[tuple[int, float]]:
    """Return (bar_index, price) for all local swing lows (lower than neighbours)."""
    n = len(candles)
    out = []
    for i in range(1, n - 1):
        if candles[i].Low < candles[i - 1].Low and candles[i].Low < candles[i + 1].Low:
            out.append((i, candles[i].Low))
    return out


def detect_dealing_range(candles, lookback: int = 100) -> Optional[DealingRange]:
    """Scan the last `lookback` candles for a confirmed dealing range.

    A confirmed DR requires:
      1. A swing high that was swept by a subsequent candle's wick/close (BSL taken).
      2. A swing low that was swept by a subsequent candle's wick/close (SSL taken).
      3. Both sweeps happened within the `lookback` window.

    The most recent confirmed DR is returned. Returns None if no DR is found.

    The `last_swept` field records which side was swept most recently so callers
    know which side of the DR is the next probable target.
    """
    n = len(candles)
    if n < 10:
        return None
    start = max(0, n - lookback)
    window = candles[start:]
    m = len(window)

    swing_highs = _find_swing_highs(window)
    swing_lows = _find_swing_lows(window)

    # For each swing high find the first candle AFTER it that swept (traded above) it.
    bsl_sweeps: list[tuple[int, float, int]] = []  # (swing_idx, swing_price, sweep_idx)
    for sh_idx, sh_price in swing_highs:
        for k in range(sh_idx + 1, m):
            if window[k].High > sh_price:
                bsl_sweeps.append((sh_idx, sh_price, k))
                break

    # For each swing low find the first candle AFTER it that swept (traded below) it.
    ssl_sweeps: list[tuple[int, float, int]] = []  # (swing_idx, swing_price, sweep_idx)
    for sl_idx, sl_price in swing_lows:
        for k in range(sl_idx + 1, m):
            if window[k].Low < sl_price:
                ssl_sweeps.append((sl_idx, sl_price, k))
                break

    if not bsl_sweeps or not ssl_sweeps:
        return None

    # Find the most recent *pair* of (BSL sweep, SSL sweep) that together form a DR.
    # We want the pair where both sweeps have occurred and they are in different
    # temporal order (one comes before the other), giving us both extremes.
    best: Optional[DealingRange] = None
    best_last_sweep = -1

    for bsl_si, bsl_price, bsl_sw in bsl_sweeps:
        for ssl_si, ssl_price, ssl_sw in ssl_sweeps:
            if bsl_sw == ssl_sw:
                continue  # same sweep candle took both sides — ambiguous, skip
            dr_high = bsl_price
            dr_low = ssl_price
            if dr_high <= dr_low:
                continue  # degenerate range
            # The more recent of the two sweeps determines the last_swept field.
            last_swept_idx = max(bsl_sw, ssl_sw)
            last_swept = +1 if bsl_sw > ssl_sw else -1
            if last_swept_idx > best_last_sweep:
                best_last_sweep = last_swept_idx
                best = DealingRange(high=dr_high, low=dr_low, last_swept=last_swept)

    return best


# ---------------------------------------------------------------------------
# Super Bullish / Heavy Discount classification
# ---------------------------------------------------------------------------

def classify_session_condition(
    current_price: float,
    midnight_open: float,
    open_830: float,
    bias: int,                # +1 bullish day expected, -1 bearish
) -> str:
    """Classify intraday condition relative to Midnight Open and 8:30 open.

    Returns one of:
        'SUPER_BULLISH'   — bullish day; price barely traded below MNO / 8:30
                           (price is above both reference levels)
        'HEAVY_DISCOUNT'  — bullish day; at 8:30 price is still below BOTH MNO and 8:30
        'SUPER_BEARISH'   — bearish day; price barely traded above MNO / 8:30
        'HEAVY_PREMIUM'   — bearish day; at 8:30 price is still above BOTH MNO and 8:30
        'NORMAL'          — none of the above extreme conditions

    For SUPER_BULLISH, use the 8:30 opening as the reference level since we're
    already above MNO.  For HEAVY_DISCOUNT, the 8:30 opening and MNO are both
    reference points (price is below both).
    """
    if bias > 0:
        # Bullish day
        if current_price > midnight_open and current_price > open_830:
            return "SUPER_BULLISH"
        if current_price < midnight_open and current_price < open_830:
            return "HEAVY_DISCOUNT"
    elif bias < 0:
        # Bearish day
        if current_price < midnight_open and current_price < open_830:
            return "SUPER_BEARISH"
        if current_price > midnight_open and current_price > open_830:
            return "HEAVY_PREMIUM"
    return "NORMAL"


# ---------------------------------------------------------------------------
# Low-probability condition helpers
# ---------------------------------------------------------------------------

def is_nfp_week_low_probability(utc_dt, is_nfp_week: bool) -> bool:
    """Return True if it's NFP week and we're in one of the low-probability days.

    NFP week: Wednesday New York, Thursday, and Friday are low probability.
    `is_nfp_week` must be supplied by the caller (e.g. from the news calendar).
    """
    if not is_nfp_week:
        return False
    # weekday(): Monday=0 ... Sunday=6
    day = utc_dt.weekday()
    # Wednesday=2, Thursday=3, Friday=4
    return day in (2, 3, 4)


def is_post_fomc_low_probability(
    utc_dt,
    fomc_whipsaw_date,        # date of the FOMC whipsaw day (or None)
) -> bool:
    """Return True if a FOMC whipsaw occurred today, making London+AM low probability.

    After an FOMC whipsaw both London and the AM session on the SAME day are
    low probability.  The caller supplies `fomc_whipsaw_date` (a date object or
    None) so this function stays pure and testable.
    """
    if fomc_whipsaw_date is None:
        return False
    target = (fomc_whipsaw_date.date()
              if hasattr(fomc_whipsaw_date, "date") else fomc_whipsaw_date)
    return utc_dt.date() == target
