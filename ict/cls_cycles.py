"""CLS time cycles + ICT macros.

ICT teaches that institutional price discovery happens in specific time
windows anchored to 5pm NY (CLS settlement). Within "macro" 20-min windows
price tends to *deliver* toward its liquidity target; outside them it tends
to consolidate or manipulate.

This module classifies any tz-aware timestamp into:
  - the CLS cycle phase it's in (asia/london/pre_ny/ny_am/lunch/ny_pm/cbdr)
  - whether it's inside an ICT macro window (and which)

Also computes CBDR (Central Bank Dealers Range) High/Low: 14:00 - 20:00 NY.
"""

from datetime import time
from typing import Optional

try:
    from zoneinfo import ZoneInfo
except ImportError:                                  # pragma: no cover
    from backports.zoneinfo import ZoneInfo         # type: ignore

import pandas as pd

import config


NY = ZoneInfo(config.NY_TZ)


def _t(hhmm: str) -> time:
    h, m = hhmm.split(":")
    return time(int(h), int(m))


_CYCLES = [(name, _t(s), _t(e)) for name, s, e in config.CLS_CYCLES]
_MACROS = [(name, _t(s), _t(e)) for name, s, e in config.ICT_MACROS]
_CBDR_START = _t(config.CBDR_START_NY)
_CBDR_END = _t(config.CBDR_END_NY)


def _to_ny(ts):
    return pd.Timestamp(ts).tz_convert(NY)


def _in_window(t: time, start: time, end: time) -> bool:
    if start <= end:
        return start <= t < end
    # crosses midnight (e.g., asia 20:00 -> 02:00)
    return t >= start or t < end


def cycle_phases(ts) -> list[str]:
    """All CLS phases containing `ts` (cbdr overlaps ny_pm and beyond)."""
    ny = _to_ny(ts).time()
    return [name for name, s, e in _CYCLES if _in_window(ny, s, e)]


def in_macro_window(ts) -> Optional[str]:
    """Name of the ICT macro window containing `ts`, or None."""
    ny = _to_ny(ts).time()
    for name, s, e in _MACROS:
        if _in_window(ny, s, e):
            return name
    return None


def cbdr_hl(df_5m: pd.DataFrame, ts) -> tuple[Optional[float], Optional[float]]:
    """Most recently *completed* CBDR (14:00-20:00 NY) High/Low prior to `ts`.

    If `ts` falls before today's CBDR end, returns yesterday's CBDR window.
    """
    now_ny = _to_ny(ts)
    end_today = now_ny.normalize().replace(
        hour=_CBDR_END.hour, minute=_CBDR_END.minute
    )
    if now_ny >= end_today:
        s_ny = end_today.replace(hour=_CBDR_START.hour, minute=_CBDR_START.minute)
        e_ny = end_today
    else:
        s_ny = end_today.replace(
            hour=_CBDR_START.hour, minute=_CBDR_START.minute
        ) - pd.Timedelta(days=1)
        e_ny = end_today - pd.Timedelta(days=1)
    sl = df_5m.loc[
        (df_5m.index >= s_ny.tz_convert("UTC"))
        & (df_5m.index < e_ny.tz_convert("UTC"))
    ]
    if sl.empty:
        return None, None
    return float(sl.High.max()), float(sl.Low.min())
