"""Intermarket pair selection from DXY + EURGBP direction.

Decision table (DXY bias, EURGBP bias) -> (pair, direction):

    Bear DXY + Bull EURGBP  ->  LONG  EURUSD     (USD down; EUR > GBP so EUR leads up)
    Bear DXY + Bear EURGBP  ->  LONG  GBPUSD     (USD down; GBP > EUR so GBP leads up)
    Bull DXY + Bull EURGBP  ->  SHORT GBPUSD     (USD up;   GBP weaker, leads down)
    Bull DXY + Bear EURGBP  ->  SHORT EURUSD     (USD up;   EUR weaker, leads down)

Any neutral leg -> no signal.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IntermarketSignal:
    pair: str
    direction: int


_TABLE = {
    (-1, +1): IntermarketSignal("EURUSD", +1),
    (-1, -1): IntermarketSignal("GBPUSD", +1),
    (+1, +1): IntermarketSignal("GBPUSD", -1),
    (+1, -1): IntermarketSignal("EURUSD", -1),
}


def resolve(dxy_bias: int, eurgbp_bias: int) -> Optional[IntermarketSignal]:
    if dxy_bias == 0 or eurgbp_bias == 0:
        return None
    return _TABLE.get((dxy_bias, eurgbp_bias))
