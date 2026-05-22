"""HTF bias: delegates to ICT structural classifier.

Previous implementation derived bias from raw swing pivots + an EMA filter.
The structural pull from `ict/structure.py` (most-recent unmitigated ITH vs
ITL) is the authoritative ICT read, so we use that as the single source of
truth. `ema_value` is accepted for backwards compatibility but ignored.
"""

from ict.structure import directional_pull


def htf_bias(candles, ema_value: float | None = None) -> int:
    """+1 bullish / -1 bearish / 0 neutral, per most-recent unmitigated ITH/ITL."""
    if not candles:
        return 0
    return directional_pull(candles)
