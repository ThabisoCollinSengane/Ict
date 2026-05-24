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


# Ep 5 + 7: New York noon hour is hard no-trade (12:00–13:00 ET).
# "Not a clean time of day for price action."
_NOON_START = time(12, 0)
_NOON_END   = time(13, 0)


def can_open_new_trade(utc_dt) -> bool:
    """True if inside a killzone, not in the last N minutes, and not in the noon block."""
    ny_t = _ensure_utc(utc_dt).astimezone(NY).time()
    if _NOON_START <= ny_t < _NOON_END:
        return False
    remaining = minutes_until_killzone_end(utc_dt)
    return remaining is not None and remaining > config.NO_NEW_TRADES_LAST_MIN
