"""ICT Market Profile: key reference opens and weekly AMD (Power-of-Three).

Three open levels act as intra-day and intra-week strength references:

  Daily Open   — UTC midnight (00:00 UTC) price. Price above = bullish day,
                 below = bearish day. The daily AMD distribution target is always
                 on the opposite side of the manipulation from this level.

  Weekly Open  — Monday 00:00 UTC price. Same concept at the weekly level.
                 Once the weekly Judas swing fires, distribution aims at
                 PWWH (if bullish) or PWWL (if bearish) — often 60-150 pips.

  Session Open — First bar of each kill zone (London 02:00 ET, NY AM 07:00 ET).
                 Used to determine intra-session direction for pyramid sizing.

Weekly AMD
----------
  Monday 00:00 UTC – Friday   = weekly accumulation begins
  Monday candle H/L            = the weekly consolidation box
  Tuesday or Wednesday candle  = Judas swing (sweeps Monday H or L, rejects back)
  Wednesday – Friday           = distribution toward PWWH or PWWL

When the weekly AMD is confirmed, pyramid legs use FULL lots regardless of
intermarket score — the weekly distribution run is the "huge pyramid" setup.
"""

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import pytz

_NY = pytz.timezone("America/New_York")
_UTC = pytz.UTC

_KILL_ZONE_ET = {
    "London Open": (2, 0),
    "New York AM": (7, 0),
}


# ---------------------------------------------------------------------------
# Reference open prices
# ---------------------------------------------------------------------------

def daily_open(bars_h1: list, ts_h1, t) -> Optional[float]:
    """Open price of the H1 bar closest to UTC midnight (00:00 UTC) today.

    Returns None if no bar within ±30 min of midnight is found.
    """
    t_pd = pd.Timestamp(t)
    midnight = t_pd.normalize()          # floor to 00:00 UTC today

    idx = ts_h1.searchsorted(midnight, side="left")
    # Try both the bar at idx and the one before; pick whichever is closer.
    best_idx = None
    best_delta = None
    for candidate in (idx - 1, idx):
        if 0 <= candidate < len(ts_h1):
            delta = abs((ts_h1[candidate] - midnight).total_seconds())
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_idx = candidate

    if best_idx is None or best_delta > 1800:   # >30 min gap → skip
        return None
    return bars_h1[best_idx].Open


def weekly_open(bars_d: list, ts_d, t) -> Optional[float]:
    """Open price of the daily bar for Monday of the current UTC week.

    Returns None if Monday data is not yet available (e.g. it IS Monday and
    the week has just started with no completed daily bar yet).
    """
    t_pd = pd.Timestamp(t)
    # Monday of the current ISO week at 00:00 UTC
    monday_utc = (t_pd - pd.Timedelta(days=t_pd.weekday())).normalize()

    idx = ts_d.searchsorted(monday_utc, side="left")
    if idx >= len(ts_d):
        return None
    # Allow up to 48-hour tolerance (holiday Mondays shift to Tuesday)
    if abs((ts_d[idx] - monday_utc).total_seconds()) > 2 * 86400:
        return None
    return bars_d[idx].Open


def nwog(bars_d: list, ts_d, t):
    """New Week Opening Gap (NWOG): the weekend gap between last week's final
    daily close (the prior Friday) and this week's Monday daily open.

    Returns (lo, hi, ce, gap_dir) or None:
      lo/hi   — the gap's bounds (low & high of the two prices)
      ce      — consequent encroachment (50% midpoint) — the key PD-array level
      gap_dir — +1 when the week opened ABOVE last week's close (gap up, a
                bullish PD array), -1 when it opened below (gap down).

    Returns None until this week's Monday daily bar exists, or when there is no
    gap (open == prior close). Uses the same Monday-of-current-UTC-week anchor as
    weekly_open, with the prior daily bar as the pre-weekend (Friday) close.
    """
    t_pd = pd.Timestamp(t)
    monday_utc = (t_pd - pd.Timedelta(days=t_pd.weekday())).normalize()
    idx = ts_d.searchsorted(monday_utc, side="left")
    if idx <= 0 or idx >= len(ts_d):
        return None
    # Holiday Mondays shift to Tuesday — same 48h tolerance as weekly_open.
    if abs((ts_d[idx] - monday_utc).total_seconds()) > 2 * 86400:
        return None
    week_open   = bars_d[idx].Open
    prior_close = bars_d[idx - 1].Close        # last daily bar before Monday = Fri close
    if week_open == prior_close:
        return None
    lo, hi = (min(prior_close, week_open), max(prior_close, week_open))
    return (lo, hi, (lo + hi) / 2.0, 1 if week_open > prior_close else -1)


def session_open(bars_m5: list, ts_m5, session_name: str, t) -> Optional[float]:
    """Open price of the first M5 bar of the named kill zone session (ET-based).

    Returns None if the session has not yet started today or if the name is
    not a known kill zone.
    """
    if session_name not in _KILL_ZONE_ET:
        return None

    t_pd = pd.Timestamp(t)
    t_ny = t_pd.astimezone(_NY)
    h, m = _KILL_ZONE_ET[session_name]

    sess_et = t_ny.replace(hour=h, minute=m, second=0, microsecond=0)
    if sess_et > t_ny:
        return None                          # session hasn't opened yet today

    sess_utc = pd.Timestamp(sess_et.astimezone(_UTC))
    idx = ts_m5.searchsorted(sess_utc, side="left")
    if idx >= len(ts_m5):
        return None
    # Allow up to 10-min tolerance for bar alignment
    if abs((ts_m5[idx] - sess_utc).total_seconds()) > 600:
        return None
    return bars_m5[idx].Open


# ---------------------------------------------------------------------------
# Weekly AMD (Power-of-Three on the weekly range)
# ---------------------------------------------------------------------------

@dataclass
class WeeklyAMD:
    monday_high: float
    monday_low: float
    direction: int          # +1 long / -1 short
    sweep_day_name: str     # "Tuesday" / "Wednesday" / "Thursday"


def detect_weekly_amd(
    bars_d: list,
    ts_d,
    t,
) -> Optional[WeeklyAMD]:
    """Detect whether the weekly Judas swing has fired for the current week.

    Looks for:
      1. Monday's OHLC range (the weekly accumulation box).
      2. A subsequent daily bar (Tue–Thu) that sweeps Monday's High or Low
         AND whose Close is back on the inside of Monday's range.

    Returns a WeeklyAMD(direction=+1) if Monday's LOW was swept (→ expect longs
    for the week) or direction=-1 if Monday's HIGH was swept (→ expect shorts).
    Returns None if Monday data is absent or no clean sweep has occurred yet.

    The check is intentionally loose — we only require the close to be back
    inside, not a full rejection candle, because on daily bars a "close inside"
    is already a meaningful confirmation.
    """
    t_pd = pd.Timestamp(t)
    weekday = t_pd.weekday()    # 0=Mon … 6=Sun

    if weekday == 0:
        # It IS Monday — no subsequent bars to sweep anything.
        return None

    monday_utc = (t_pd - pd.Timedelta(days=weekday)).normalize()

    # Locate Monday's bar index
    monday_idx = ts_d.searchsorted(monday_utc, side="left")
    if monday_idx >= len(ts_d):
        return None
    if abs((ts_d[monday_idx] - monday_utc).total_seconds()) > 2 * 86400:
        return None

    monday_bar = bars_d[monday_idx]
    m_high = monday_bar.High
    m_low  = monday_bar.Low

    # Gather subsequent daily bars within this calendar week, up to current bar
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                 "Saturday", "Sunday"]
    low_swept  = False
    high_swept = False
    sweep_day  = ""

    current_day_idx = ts_d.searchsorted(t_pd, side="right") - 1

    for idx in range(monday_idx + 1, current_day_idx + 1):
        if idx >= len(ts_d):
            break
        bar_ts = ts_d[idx]
        # Stop if we've crossed into the next week
        if (bar_ts - monday_utc).days >= 7:
            break

        bar = bars_d[idx]
        bar_weekday = bar_ts.weekday()
        bar_day_name = day_names[bar_weekday]

        # Sweep of low (bullish Judas swing): bar wick goes below Monday low,
        # but bar CLOSES back above Monday low.
        if bar.Low < m_low and bar.Close > m_low and not low_swept:
            low_swept = True
            sweep_day = bar_day_name

        # Sweep of high (bearish Judas swing): bar wick goes above Monday high,
        # but bar CLOSES back below Monday high.
        if bar.High > m_high and bar.Close < m_high and not high_swept:
            high_swept = True
            sweep_day = bar_day_name

    # Only clean single-direction sweeps qualify.
    if low_swept and not high_swept:
        return WeeklyAMD(monday_high=m_high, monday_low=m_low,
                         direction=+1, sweep_day_name=sweep_day)
    if high_swept and not low_swept:
        return WeeklyAMD(monday_high=m_high, monday_low=m_low,
                         direction=-1, sweep_day_name=sweep_day)
    return None


# ---------------------------------------------------------------------------
# Open-level bias helpers
# ---------------------------------------------------------------------------

def open_bias(price: float, open_price: Optional[float]) -> int:
    """Return +1 if price is above open (bullish), -1 if below (bearish), 0 if unknown."""
    if open_price is None:
        return 0
    return 1 if price > open_price else -1


def profile_score(price: float, direction: int,
                  d_open: Optional[float],
                  w_open: Optional[float],
                  s_open: Optional[float]) -> int:
    """Sum of how many open levels agree with trade direction.

    Returns 0-3: 3 = all three levels (daily, weekly, session) agree.
    Used to scale pyramid lot sizes — higher score → full pyramid lots.
    """
    score = 0
    for op in (d_open, w_open, s_open):
        if op is not None and open_bias(price, op) == direction:
            score += 1
    return score
