"""HTF bias: Break-of-Structure + EMA filter."""

import config


def _swings(candles, lookback: int):
    """Return (last_swing_high, last_swing_low) from the lookback window."""
    n = len(candles)
    if n < lookback + 2:
        return None, None
    window = candles[-lookback:]
    swing_high = max(c.High for c in window)
    swing_low = min(c.Low for c in window)
    return swing_high, swing_low


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
