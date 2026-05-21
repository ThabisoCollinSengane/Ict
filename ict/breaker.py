"""Breaker block detection.

A breaker forms when an order block fails: price violates an OB's extreme
and then closes back through, flipping the OB's polarity. The most reliable
breakers per ICT are on M15 and H4.

We only expose the M15/H4 TFs to the entry pipeline (config.BREAKER_TFS).
"""

from dataclasses import dataclass
from typing import Optional

from ict.order_block import detect_order_blocks, OrderBlock


@dataclass
class Breaker:
    direction: int          # +1 bullish breaker, -1 bearish breaker
    top: float
    bottom: float
    origin_index: int
    flipped_index: int
    mitigated: bool = False

    @property
    def mid(self) -> float:
        return (self.top + self.bottom) / 2.0


def detect_breakers(candles, tf: Optional[str] = None) -> list[Breaker]:
    """Find breakers in `candles`.

    `tf` is informational; the caller is responsible for only invoking this
    on bars belonging to a tradable TF (config.BREAKER_TFS).
    """
    obs = detect_order_blocks(candles)
    out: list[Breaker] = []
    for ob in obs:
        # A bullish OB becomes a bearish breaker when price closes below its low.
        # A bearish OB becomes a bullish breaker when price closes above its high.
        for j in range(ob.bar_index + 1, len(candles)):
            c = candles[j]
            if ob.direction > 0 and c.Close < ob.bottom:
                br = Breaker(-1, top=ob.top, bottom=ob.bottom,
                             origin_index=ob.bar_index, flipped_index=j)
                _mark_mitigation(candles, br)
                out.append(br)
                break
            if ob.direction < 0 and c.Close > ob.top:
                br = Breaker(+1, top=ob.top, bottom=ob.bottom,
                             origin_index=ob.bar_index, flipped_index=j)
                _mark_mitigation(candles, br)
                out.append(br)
                break
    return out


def _mark_mitigation(candles, br: Breaker) -> None:
    """Breaker is "tapped" when price re-enters the zone after the flip."""
    for c in candles[br.flipped_index + 1:]:
        if br.direction > 0 and c.Low <= br.top and c.High >= br.bottom:
            br.mitigated = True
            return
        if br.direction < 0 and c.High >= br.bottom and c.Low <= br.top:
            br.mitigated = True
            return


def is_tradable_tf(tf: str) -> bool:
    import config
    return tf in config.BREAKER_TFS
