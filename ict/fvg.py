"""Fair Value Gap detection.

A 3-candle FVG forms when candle[0] and candle[2] don't overlap:
- Bullish FVG: low[0] > high[2]  (gap = high[2] .. low[0])
- Bearish FVG: high[0] < low[2]  (gap = high[0] .. low[2])

`candles` is ordered oldest -> newest. `candles[-1]` is the most recent closed bar.
"""

from dataclasses import dataclass
import config


@dataclass
class FVG:
    direction: int          # +1 bullish, -1 bearish
    top: float
    bottom: float
    bar_index: int          # index of middle (displacement) candle
    mitigated: bool = False

    @property
    def mid(self) -> float:
        return (self.top + self.bottom) / 2.0

    @property
    def size(self) -> float:
        return self.top - self.bottom


def _pip_size(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


def detect_new_fvg(candles, symbol: str) -> FVG | None:
    """Check the latest 3 bars for an FVG. Return it or None."""
    if len(candles) < 3:
        return None
    c0, c1, c2 = candles[-3], candles[-2], candles[-1]
    pip = _pip_size(symbol)
    min_size = config.FVG_MIN_SIZE_PIPS * pip

    if c0.Low > c2.High and (c0.Low - c2.High) >= min_size:
        return FVG(+1, top=c0.Low, bottom=c2.High, bar_index=len(candles) - 2)
    if c0.High < c2.Low and (c2.Low - c0.High) >= min_size:
        return FVG(-1, top=c2.Low, bottom=c0.High, bar_index=len(candles) - 2)
    return None


def update_mitigation(fvgs: list[FVG], last_candle) -> None:
    """Mark FVGs mitigated when price trades back into the gap."""
    for g in fvgs:
        if g.mitigated:
            continue
        if g.direction > 0 and last_candle.Low <= g.top:
            g.mitigated = True
        elif g.direction < 0 and last_candle.High >= g.bottom:
            g.mitigated = True


def nearest_unmitigated(fvgs: list[FVG], price: float, direction: int) -> FVG | None:
    """Closest unmitigated FVG above (direction +1) or below (direction -1) price."""
    candidates = [
        g for g in fvgs
        if not g.mitigated and g.direction == direction and (
            (direction > 0 and g.bottom > price) or
            (direction < 0 and g.top < price)
        )
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda g: abs(g.mid - price))
