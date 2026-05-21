"""Time-bucketed levels: NYO (true day open), PDH/PDL, PWH/PWL, session H/L.

All inputs are pandas DataFrames indexed by tz-aware UTC timestamps and a
column set {Open, High, Low, Close}. We convert to America/New_York for the
day-bucket boundary because ICT's "true day" opens at 00:00 NY.
"""

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional

try:
    from zoneinfo import ZoneInfo
except ImportError:                                  # pragma: no cover
    from backports.zoneinfo import ZoneInfo         # type: ignore

import pandas as pd

import config


NY = ZoneInfo(config.NY_TZ)


@dataclass
class DayLevels:
    nyo_date: pd.Timestamp           # 00:00 NY of this trading day
    nyo: float                       # the M5 Open at 00:00 NY
    pdh: Optional[float] = None      # previous (NY) day's High
    pdl: Optional[float] = None      # previous day's Low
    pwh: Optional[float] = None      # previous week's High
    pwl: Optional[float] = None      # previous week's Low
    asia_high: Optional[float] = None
    asia_low: Optional[float] = None
    london_high: Optional[float] = None
    london_low: Optional[float] = None


def _ny_date(ts) -> pd.Timestamp:
    """Convert any UTC pd.Timestamp to the NY-local date as a pd.Timestamp."""
    return pd.Timestamp(ts).tz_convert(NY).normalize().tz_localize(None)


def nyo_for(df_5m: pd.DataFrame, ts) -> Optional[tuple]:
    """Return (nyo_date, nyo_open_price) for the trading day containing `ts`.

    nyo = the M5 Open at the first bar whose NY-local time is on or after 00:00.
    """
    ny_dt = pd.Timestamp(ts).tz_convert(NY)
    day_start_ny = ny_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_start_utc = day_start_ny.tz_convert("UTC")
    # First bar at or after midnight NY of that calendar day.
    pos = df_5m.index.searchsorted(day_start_utc, side="left")
    if pos >= len(df_5m):
        return None
    open_px = float(df_5m.iloc[pos].Open)
    return (pd.Timestamp(day_start_ny.tz_convert(None)).normalize(), open_px)


def prior_day_hl(df_5m: pd.DataFrame, ts) -> tuple[Optional[float], Optional[float]]:
    """Previous NY trading day's (High, Low)."""
    today = pd.Timestamp(ts).tz_convert(NY).normalize()
    prior_start = (today - pd.Timedelta(days=1)).tz_convert("UTC")
    prior_end = today.tz_convert("UTC")
    sl = df_5m.loc[(df_5m.index >= prior_start) & (df_5m.index < prior_end)]
    if sl.empty:
        return None, None
    return float(sl.High.max()), float(sl.Low.min())


def prior_week_hl(df_5m: pd.DataFrame, ts) -> tuple[Optional[float], Optional[float]]:
    """Previous calendar-week (NY) High/Low. Week boundary = Monday 00:00 NY."""
    now = pd.Timestamp(ts).tz_convert(NY)
    monday = (now - pd.Timedelta(days=now.weekday())).normalize()
    prev_monday = monday - pd.Timedelta(days=7)
    sl = df_5m.loc[
        (df_5m.index >= prev_monday.tz_convert("UTC"))
        & (df_5m.index < monday.tz_convert("UTC"))
    ]
    if sl.empty:
        return None, None
    return float(sl.High.max()), float(sl.Low.min())


# Session windows in NY local time.
_SESSIONS = {
    "asia":   (time(20, 0), time(2, 0)),     # 20:00 prev day -> 02:00 NY
    "london": (time(2, 0),  time(7, 0)),
    "ny_am":  (time(7, 0),  time(12, 0)),
}


def session_hl(df_5m: pd.DataFrame, ts, session: str) -> tuple[Optional[float], Optional[float]]:
    """High/Low of the most recently *completed* (or current, if asked at end)
    instance of `session` prior to `ts`.

    For asia the window crosses midnight; handled explicitly.
    """
    start, end = _SESSIONS[session]
    now_ny = pd.Timestamp(ts).tz_convert(NY)
    today_ny = now_ny.normalize()

    if session == "asia":
        # Asia: yesterday 20:00 -> today 02:00 NY.
        s_ny = today_ny.replace(hour=20) - pd.Timedelta(days=1)
        e_ny = today_ny.replace(hour=2)
    else:
        s_ny = today_ny.replace(hour=start.hour, minute=start.minute)
        e_ny = today_ny.replace(hour=end.hour, minute=end.minute)

    s_utc = s_ny.tz_convert("UTC")
    e_utc = e_ny.tz_convert("UTC")
    sl = df_5m.loc[(df_5m.index >= s_utc) & (df_5m.index < e_utc)]
    if sl.empty:
        return None, None
    return float(sl.High.max()), float(sl.Low.min())


def build_day_levels(df_5m: pd.DataFrame, ts) -> Optional[DayLevels]:
    nyo = nyo_for(df_5m, ts)
    if nyo is None:
        return None
    pdh, pdl = prior_day_hl(df_5m, ts)
    pwh, pwl = prior_week_hl(df_5m, ts)
    ah, al = session_hl(df_5m, ts, "asia")
    lh, ll = session_hl(df_5m, ts, "london")
    return DayLevels(nyo_date=nyo[0], nyo=nyo[1], pdh=pdh, pdl=pdl, pwh=pwh, pwl=pwl,
                     asia_high=ah, asia_low=al, london_high=lh, london_low=ll)
