"""ICT killzone gating in New York time."""

from datetime import time
import pytz
import config

NY = pytz.timezone("America/New_York")


def _parse(hhmm: str) -> time:
    h, m = hhmm.split(":")
    return time(int(h), int(m))


_KZ = [(name, _parse(s), _parse(e)) for name, s, e in config.KILLZONES]


def _ensure_utc(dt):
    return pytz.utc.localize(dt) if dt.tzinfo is None else dt


def current_killzone(utc_dt) -> str | None:
    """Return killzone name if `utc_dt` falls inside one, else None."""
    ny_t = _ensure_utc(utc_dt).astimezone(NY).time()
    for name, start, end in _KZ:
        if start <= ny_t < end:
            return name
    return None


def minutes_until_killzone_end(utc_dt) -> int | None:
    """Minutes remaining in the active killzone, or None if outside."""
    ny = _ensure_utc(utc_dt).astimezone(NY)
    for _, start, end in _KZ:
        if start <= ny.time() < end:
            end_minutes = end.hour * 60 + end.minute
            now_minutes = ny.hour * 60 + ny.minute
            return end_minutes - now_minutes
    return None


def can_open_new_trade(utc_dt) -> bool:
    """True if inside a killzone AND not in the last N minutes of it."""
    remaining = minutes_until_killzone_end(utc_dt)
    return remaining is not None and remaining > config.NO_NEW_TRADES_LAST_MIN


# ---- New pipeline helpers (only KZ_USED windows, first-hour gate) ----

_USED = [(name, _parse(s), _parse(e)) for name, s, e in config.KZ_USED]


def in_used_killzone(utc_dt) -> str | None:
    ny_t = _ensure_utc(utc_dt).astimezone(NY).time()
    for name, start, end in _USED:
        if start <= ny_t < end:
            return name
    return None


def minutes_into_killzone(utc_dt) -> int | None:
    ny = _ensure_utc(utc_dt).astimezone(NY)
    for _, start, end in _USED:
        if start <= ny.time() < end:
            start_min = start.hour * 60 + start.minute
            now_min = ny.hour * 60 + ny.minute
            return now_min - start_min
    return None


def first_hour_elapsed(utc_dt) -> bool:
    """True if we're past the first `KZ_FIRST_HOUR_MIN` of a used killzone."""
    m = minutes_into_killzone(utc_dt)
    return m is not None and m >= config.KZ_FIRST_HOUR_MIN


def can_enter_new_pipeline(utc_dt) -> bool:
    """In a USED killzone, past the first hour, not in the last 15 min."""
    if not first_hour_elapsed(utc_dt):
        return False
    remaining = minutes_until_killzone_end(utc_dt)
    return remaining is not None and remaining > config.NO_NEW_TRADES_LAST_MIN
