"""Position sizing and pyramiding bookkeeping."""

from dataclasses import dataclass, field
import config


def pip_size(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


def position_size(equity: float, entry: float, stop: float, symbol: str) -> float:
    """Units to trade so that |entry - stop| equals RISK_PER_TRADE_PCT of equity.

    Forex units are 1 unit = 1 base currency. Risk per unit (in account ccy, USD-quoted
    pairs) ≈ |entry - stop|. For JPY-quoted pairs divide by price for USD conversion,
    but for GBPUSD/EURUSD/EURGBP this simplification is fine since both legs are USD/GBP.
    """
    risk_amt = equity * (config.RISK_PER_TRADE_PCT / 100.0)
    per_unit = abs(entry - stop)
    if per_unit <= 0:
        return 0.0
    return risk_amt / per_unit


@dataclass
class TradeState:
    symbol: str
    direction: int                       # +1 long, -1 short
    legs: list[dict] = field(default_factory=list)
    # leg dict: {entry, stop, units, leg_idx, entry_id, sl_id, tp_id}
    pending: dict = field(default_factory=dict)
    # pending dict keyed by entry_order_id -> {stop, units, leg_idx}
    target: float = 0.0
    initial_stop: float = 0.0

    def total_units(self) -> float:
        return sum(l["units"] for l in self.legs) * self.direction

    def avg_entry(self) -> float:
        if not self.legs:
            return 0.0
        wsum = sum(l["entry"] * l["units"] for l in self.legs)
        usum = sum(l["units"] for l in self.legs)
        return wsum / usum if usum else 0.0

    def can_add(self) -> bool:
        return len(self.legs) < config.MAX_LEGS
