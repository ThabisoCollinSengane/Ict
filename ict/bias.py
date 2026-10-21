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


def daily_sweep_bias(daily_candles) -> int:
    """Ep 40: 3-bar daily sweep pattern for bias.

    Bearish: candles[-3] sweeps a prior swing high; candles[-2] makes a lower high
    than candles[-3]; this indicates the next day is likely short.
    Bullish: inverse — candles[-3] sweeps a prior swing low and candles[-2] makes
    a higher low.

    Returns +1, -1, or 0.
    """
    if len(daily_candles) < config.SWING_LOOKBACK + 3:
        return 0
    prior = daily_candles[:-3]
    if len(prior) < 2:
        return 0
    prior_high = max(c.High for c in prior)
    prior_low  = min(c.Low  for c in prior)
    c_minus3, c_minus2 = daily_candles[-3], daily_candles[-2]
    # Bearish 3-bar sweep: candles[-3] took out a prior high; candles[-2] lower high
    if c_minus3.High > prior_high and c_minus2.High < c_minus3.High:
        return -1
    # Bullish 3-bar sweep: candles[-3] took out a prior low; candles[-2] higher low
    if c_minus3.Low < prior_low and c_minus2.Low > c_minus3.Low:
        return +1
    return 0


def weekly_expansion_bias(weekly_candles) -> int:
    """Ep 40: determine which direction weekly price is likely to expand into.

    Bullish weekly bias if the most recent weekly close broke above a prior
    swing high (BOS up); bearish if it broke below a prior swing low.
    Returns +1 bullish, -1 bearish, 0 neutral.
    """
    if len(weekly_candles) < config.SWING_LOOKBACK + 2:
        return 0
    prior = weekly_candles[:-1]
    w_high = max(c.High for c in prior[-config.SWING_LOOKBACK:])
    w_low  = min(c.Low  for c in prior[-config.SWING_LOOKBACK:])
    last_close = weekly_candles[-1].Close
    if last_close > w_high:
        return +1
    if last_close < w_low:
        return -1
    return 0


def htf_bias(candles, lookback: int = None, ema_value: float | None = None) -> int:
    """+1 bullish, -1 bearish, 0 neutral.

    Bullish if last close > most recent swing high (BOS up) AND > EMA.
    Bearish if last close < most recent swing low (BOS down) AND < EMA.
    Neutral otherwise.

    `lookback` defaults to config.SWING_LOOKBACK (20). Pass a smaller value
    (e.g. config.SWING_LOOKBACK_STH = 8) for faster short-term MSS reads.
    """
    lb = lookback if lookback is not None else config.SWING_LOOKBACK
    if len(candles) < lb + 2:
        return 0
    prior = candles[:-1]
    swing_high, swing_low = _swings(prior, lb)
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
