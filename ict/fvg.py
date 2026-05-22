"""Fair Value Gap detection.

A 3-candle FVG forms when candle[0] and candle[2] don't overlap:
- Bullish FVG (up displacement): low[2] > high[0]  -> gap from high[0] .. low[2]
- Bearish FVG (down displacement): high[2] < low[0] -> gap from high[2] .. low[0]

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
    # Context fields populated lazily by the entry pipeline (None = not measured).
    displacement_strength: float | None = None  # middle range / median(prev N)
    time_in_zone_pre_formation: float | None = None  # [0, 1]
    realized_vol_at_formation: float | None = None
    range_expansion: float | None = None
    news_proximity_minutes: int | None = None
    news_impact: str | None = None
    formed_in_macro_window: bool | None = None

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

    if c2.Low > c0.High and (c2.Low - c0.High) >= min_size:
        return FVG(+1, top=c2.Low, bottom=c0.High, bar_index=len(candles) - 2)
    if c2.High < c0.Low and (c0.Low - c2.High) >= min_size:
        return FVG(-1, top=c0.Low, bottom=c2.High, bar_index=len(candles) - 2)
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


def enumerate_fvgs(candles, symbol: str) -> list[FVG]:
    """Find every FVG in the series; mark mitigated state from later bars."""
    out: list[FVG] = []
    for i in range(2, len(candles)):
        g = detect_new_fvg(candles[: i + 1], symbol)
        if g is not None:
            out.append(g)
    for g in out:
        for c in candles[g.bar_index + 1:]:
            if g.direction > 0 and c.Low <= g.bottom:
                g.mitigated = True
                break
            if g.direction < 0 and c.High >= g.top:
                g.mitigated = True
                break
    return out


def first_fvg_after(candles, symbol: str, after_index: int, direction: int) -> FVG | None:
    """First FVG whose displacement candle index >= `after_index` in `direction`."""
    for g in enumerate_fvgs(candles, symbol):
        if g.bar_index >= after_index and g.direction == direction and not g.mitigated:
            return g
    return None


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
