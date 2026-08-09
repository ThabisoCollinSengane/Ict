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
