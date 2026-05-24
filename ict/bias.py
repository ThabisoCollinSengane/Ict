"""HTF bias: Break-of-Structure + EMA filter.

ICT 2022 Episode 12 — Market Structure For Precision Technicians:
  Three-tier swing hierarchy: LTH/LTL (Daily), ITH/ITL (4H), STH/STL (1H).
  `classify_swing_structure()` returns all three tiers from a single candle list.
  Callers pass appropriately-sized lookbacks for each tier.
"""

import config


def _swings(candles, lookback: int):
    """Return (swing_high, swing_low) from the trailing `lookback` candles."""
    n = len(candles)
    if n < lookback + 2:
        return None, None
    window = candles[-lookback:]
    swing_high = max(c.High for c in window)
    swing_low = min(c.Low for c in window)
    return swing_high, swing_low


def classify_swing_structure(candles,
                              lookback_lth: int = 50,
                              lookback_ith: int = None,
                              lookback_sth: int = None) -> dict:
    """Episode 12: classify recent price swings into LTH/ITH/STH tiers.

    Returns a dict with keys: lth, ltl, ith, itl, sth, stl.
    Each value is the price level of the most recent swing of that tier, or None.

    Recommended caller usage:
      - Pass Daily bars with lookback_lth=50 for LTH/LTL.
      - Pass 4H bars with default lookback_ith (SWING_LOOKBACK) for ITH/ITL.
      - Pass 1H bars with lookback_sth (SWING_LOOKBACK_STH) for STH/STL.
    """
    lookback_ith = lookback_ith or config.SWING_LOOKBACK
    lookback_sth = lookback_sth or config.SWING_LOOKBACK_STH

    lth, ltl = _swings(candles, lookback_lth)
    ith, itl = _swings(candles, lookback_ith)
    sth, stl = _swings(candles, lookback_sth)

    return {"lth": lth, "ltl": ltl, "ith": ith, "itl": itl, "sth": sth, "stl": stl}


def htf_bias(candles, ema_value: float | None = None) -> int:
    """+1 bullish, -1 bearish, 0 neutral.

    Bullish if last close > most recent swing high (BOS up) AND > EMA.
    Bearish if last close < most recent swing low (BOS down) AND < EMA.
    Neutral otherwise.
    """
    if len(candles) < config.SWING_LOOKBACK + 2:
        return 0
    prior = candles[:-1]
    swing_high, swing_low = _swings(prior, config.SWING_LOOKBACK)
    if swing_high is None:
        return 0
    last_close = candles[-1].Close

    bull_bos = last_close > swing_high
    bear_bos = last_close < swing_low
    if ema_value is not None:
        bull_bos = bull_bos and last_close > ema_value
        bear_bos = bear_bos and last_close < ema_value

    if bull_bos:
        return +1
    if bear_bos:
        return -1
    return 0
