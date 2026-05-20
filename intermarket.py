"""Intermarket decision table — picks pair + direction from DXY and EURGBP bias.

| DXY    | EURGBP | Decision         |
|--------|--------|------------------|
| Bear   | Bull   | LONG EURUSD      |
| Bear   | Bear   | LONG GBPUSD      |
| Bull   | Bull   | SHORT GBPUSD     |
| Bull   | Bear   | SHORT EURUSD     |
| Neutral or any side neutral -> no trade
"""

from dataclasses import dataclass


@dataclass
class IntermarketSignal:
    pair: str       # "GBPUSD" or "EURUSD"
    direction: int  # +1 long, -1 short


_TABLE = {
    (-1, +1): IntermarketSignal("EURUSD", +1),
    (-1, -1): IntermarketSignal("GBPUSD", +1),
    (+1, +1): IntermarketSignal("GBPUSD", -1),
    (+1, -1): IntermarketSignal("EURUSD", -1),
}


def resolve(dxy_bias: int, eurgbp_bias: int) -> IntermarketSignal | None:
    if dxy_bias == 0 or eurgbp_bias == 0:
        return None
    return _TABLE.get((dxy_bias, eurgbp_bias))
