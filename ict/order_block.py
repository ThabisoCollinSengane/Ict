"""Order Block detection.

Bullish OB = last DOWN candle before a strong UP displacement that breaks structure.
Bearish OB = last UP candle before a strong DOWN displacement that breaks structure.

We only consider OBs that have not been mitigated (price hasn't traded back through them).
"""

from dataclasses import dataclass
import config


@dataclass
class OrderBlock:
    direction: int          # +1 bullish, -1 bearish
    top: float
    bottom: float
    bar_index: int
    mitigated: bool = False

    @property
    def mid(self) -> float:
        return (self.top + self.bottom) / 2.0


def detect_order_blocks(candles, lookback: int = None) -> list[OrderBlock]:
    """Scan `candles` (oldest -> newest) for OBs in the last `lookback` bars."""
    lookback = lookback or config.OB_LOOKBACK_BARS
    n = len(candles)
    obs: list[OrderBlock] = []
    start = max(2, n - lookback)

    for i in range(start, n - 1):
        prev = candles[i - 1]
        cur = candles[i]
        nxt = candles[i + 1]

        # Bullish OB: prev is bearish, current is strong bullish that takes prev high
        if prev.Close < prev.Open and cur.Close > cur.Open:
            if cur.Close > prev.High and (nxt.Close > cur.Close):
                obs.append(OrderBlock(+1, top=prev.High, bottom=prev.Low, bar_index=i - 1))
        # Bearish OB: prev is bullish, current is strong bearish that takes prev low
        elif prev.Close > prev.Open and cur.Close < cur.Open:
            if cur.Close < prev.Low and (nxt.Close < cur.Close):
                obs.append(OrderBlock(-1, top=prev.High, bottom=prev.Low, bar_index=i - 1))

    # Mark mitigated using later price action
    for ob in obs:
        future = candles[ob.bar_index + 2 :]
        for c in future:
            if ob.direction > 0 and c.Low <= ob.bottom:
                ob.mitigated = True
                break
            if ob.direction < 0 and c.High >= ob.top:
                ob.mitigated = True
                break
    return obs


def nearest_unmitigated_ob(obs: list[OrderBlock], price: float, direction: int) -> OrderBlock | None:
    candidates = [
        o for o in obs
        if not o.mitigated and o.direction == direction and (
            (direction > 0 and o.bottom > price) or
            (direction < 0 and o.top < price)
        )
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda o: abs(o.mid - price))
