"""ICT SMT (Smart Money Technique) — divergence at a swept liquidity level.

Precise SMT: at a recent swing, one instrument makes a NEW directional extreme
(sweeps liquidity) while a CORRELATED instrument FAILS to confirm it. That failure
to confirm is the reversal signal.

Two correlation modes, because an index book has two SMT relationships:

  * POSITIVE correlation (index vs index — US500 / US100 / US30):
      they should make the SAME extremes. Divergence = primary sweeps a lower low
      but the reference makes a HIGHER low (or primary a higher high, ref a lower
      high). This is the classic ES/NQ/YM SMT.

  * INVERSE correlation (index vs the DOLLAR):
      indices move opposite the dollar, so they should make OPPOSITE extremes.
      Divergence = primary (index) sweeps a lower low but the dollar FAILS to make
      the corresponding higher high (or index higher high, dollar fails lower low).

The two most recent swings are proxied by the two halves of a lookback window
(prior half vs recent half min/max) — deterministic, no cross-instrument swing
alignment needed, and it matches how SMT scanners read "the last two swings".

Bars use the shared Open/High/Low/Close namedtuple (oldest -> newest).
"""
from __future__ import annotations

from . import market_structure as _mstruct


def smt_divergence(primary, ref, direction: int, inverse: bool = False,
                   lookback: int = 20) -> bool:
    """True when `primary` made a new directional extreme that `ref` did NOT confirm.

    direction +1 (long / sell-side sweep): primary made a LOWER low.
      positive ref  -> divergence if ref did NOT make a lower low (held higher).
      inverse ref   -> divergence if ref (dollar) did NOT make a higher high.
    direction -1 (short / buy-side sweep): primary made a HIGHER high.
      positive ref  -> divergence if ref did NOT make a higher high.
      inverse ref   -> divergence if ref (dollar) did NOT make a lower low.
    """
    if direction == 0 or len(primary) < lookback or len(ref) < lookback:
        return False
    p = primary[-lookback:]
    r = ref[-lookback:]
    half = lookback // 2
    if half < 2:
        return False
    p_prior, p_recent = p[:half], p[half:]
    r_prior, r_recent = r[:half], r[half:]

    def lo(bars):
        return min(b.Low for b in bars)

    def hi(bars):
        return max(b.High for b in bars)

    if direction > 0:
        # primary must have swept a lower low (new sell-side liquidity taken)
        if not (lo(p_recent) < lo(p_prior)):
            return False
        if inverse:
            return hi(r_recent) <= hi(r_prior)   # dollar failed to make a higher high
        return lo(r_recent) >= lo(r_prior)       # positive ref made a higher low
    else:
        # primary must have swept a higher high (new buy-side liquidity taken)
        if not (hi(p_recent) > hi(p_prior)):
            return False
        if inverse:
            return lo(r_recent) >= lo(r_prior)   # dollar failed to make a lower low
        return hi(r_recent) <= hi(r_prior)       # positive ref made a lower high


def smt_divergence_fractal(primary, ref, direction: int, inverse: bool = False,
                           lookback: int = 60, max_age: int = 6,
                           tol: int = 2) -> bool:
    """REACTIVE SMT — fires on actual fractal swing pivots, aligned across the two
    instruments, only when the sweep is FRESH (within `max_age` bars of now).

    vs the block-half proxy above: this uses the real STH/STL fractal swings, so
    it triggers at the precise pivot of the sweep (not a smoothed block extreme)
    and only when that pivot is recent — the point-in-time ICT SMT read.

    Long (direction +1): the primary's two most recent swing LOWS show a LOWER low
    (it swept liquidity); the reference at the SAME two pivots did NOT confirm —
    a HIGHER low (positive corr) or, for the inverse dollar, FAILED to make the
    corresponding higher high. Short is the mirror on swing HIGHS.

    Alignment is by offset-from-end (robust to the two series differing in length
    from data gaps), with a +/- `tol`-bar window around each pivot on the reference.
    """
    if direction == 0 or len(primary) < 6 or len(ref) < 6:
        return False
    p = primary[-lookback:]
    r = ref[-lookback:]
    n = len(p)
    res = _mstruct.classify(p)
    swings = res.get("stl" if direction > 0 else "sth", [])
    if len(swings) < 2:
        return False
    prev, last = swings[-2], swings[-1]
    # primary made a new directional extreme (swept the prior swing)…
    if direction > 0 and not (last.price < prev.price):
        return False
    if direction < 0 and not (last.price > prev.price):
        return False
    # …and it is FRESH (reactive — the pivot is near the current bar)
    if last.bar_index < n - max_age:
        return False

    def _ref(bar_index, side):
        off = (n - 1) - bar_index                 # offset from the end of p
        ridx = (len(r) - 1) - off                 # same offset into r
        seg = r[max(0, ridx - tol):min(len(r), ridx + tol + 1)]
        if not seg:
            return None
        return (min(b.Low for b in seg) if side == "low"
                else max(b.High for b in seg))

    if direction > 0:
        if inverse:                                # dollar should make a higher high
            hp, hl = _ref(prev.bar_index, "high"), _ref(last.bar_index, "high")
            return hp is not None and hl is not None and hl <= hp
        lp, ll = _ref(prev.bar_index, "low"), _ref(last.bar_index, "low")
        return lp is not None and ll is not None and ll > lp   # ref made a higher low
    else:
        if inverse:                                # dollar should make a lower low
            lp, ll = _ref(prev.bar_index, "low"), _ref(last.bar_index, "low")
            return lp is not None and ll is not None and ll >= lp
        hp, hl = _ref(prev.bar_index, "high"), _ref(last.bar_index, "high")
        return hp is not None and hl is not None and hl < hp   # ref made a lower high
