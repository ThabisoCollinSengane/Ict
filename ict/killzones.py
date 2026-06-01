"""ICT killzone gating in New York time."""

from datetime import time
import pytz
import config

NY = pytz.timezone("America/New_York")

_AUD_ONLY_PAIRS = frozenset(("AUDUSD",))


def _parse(hhmm: str) -> time:
    h, m = hhmm.split(":")
    return time(int(h), int(m))


_KZ     = [(name, _parse(s), _parse(e)) for name, s, e in config.KILLZONES]
_KZ_AUD = [(name, _parse(s), _parse(e)) for name, s, e in config.AUD_NZD_KILLZONES]


def _ensure_utc(dt):
    return pytz.utc.localize(dt) if dt.tzinfo is None else dt


def _kz_list(pair: str | None):
    """Return the kill zone list appropriate for this pair."""
    # NZDUSD uses London Open + NY AM (same as EUR/GBP) — active during US session.
    # AUDUSD uses Asian session kill zones.
    return _KZ_AUD if pair in _AUD_ONLY_PAIRS else _KZ


def current_killzone(utc_dt, pair: str | None = None) -> str | None:
    """Return killzone name if `utc_dt` falls inside one, else None."""
    ny_t = _ensure_utc(utc_dt).astimezone(NY).time()
    for name, start, end in _kz_list(pair):
        if start <= end:
            if start <= ny_t < end:
                return name
        else:   # wraps midnight (e.g. 23:00–01:00)
            if ny_t >= start or ny_t < end:
                return name
    return None


def minutes_until_killzone_end(utc_dt, pair: str | None = None) -> int | None:
    """Minutes remaining in the active killzone, or None if outside."""
    ny = _ensure_utc(utc_dt).astimezone(NY)
    for _, start, end in _kz_list(pair):
        in_zone = False
        if start <= end:
            in_zone = start <= ny.time() < end
        else:
            in_zone = ny.time() >= start or ny.time() < end
        if in_zone:
            end_minutes = end.hour * 60 + end.minute
            now_minutes = ny.hour * 60 + ny.minute
            diff = end_minutes - now_minutes
            if diff <= 0:   # wrapped midnight
                diff += 24 * 60
            return diff
    return None


# Ep 5 + 7: New York noon hour is hard no-trade (12:00–13:00 ET).
_NOON_START = time(12, 0)
_NOON_END   = time(13, 0)


def can_open_new_trade(utc_dt, pair: str | None = None) -> bool:
    """True if inside the correct killzone for this pair, not final N min, not noon block."""
    ny_t = _ensure_utc(utc_dt).astimezone(NY).time()
    if _NOON_START <= ny_t < _NOON_END:
        return False
    remaining = minutes_until_killzone_end(utc_dt, pair)
    return remaining is not None and remaining > config.NO_NEW_TRADES_LAST_MIN
