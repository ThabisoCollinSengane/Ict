"""Order Block detection — ICT 2022 Episodes 12, 18, 35.

Episode 18 rules implemented here:
1. OB = LAST opposite-color candle before a displacement that breaks structure.
   (Not simply the immediately preceding candle.)
2. OB is only valid if a FVG (imbalance) exists between the OB and the
   displacement candle. "What makes an order block valid? It has to have an
   imbalance after it." — Ep. 18.

Episode 35 note: OB zone is defined by the candle BODY (open/close), not wicks.
   `body_top` / `body_bottom` expose the 50% mean-threshold zone.
   `top` / `bottom` still hold wick extremes for stop/target calculations.

Breaker Block (Ep. 12):
A mitigated OB of the OPPOSITE direction that price is returning to.
Example — Bullish Breaker:
  1. A bearish OB existed (last bullish candle before bearish BOS + FVG).
  2. Price later broke ABOVE that OB (mitigated it).
  3. Now price retraces back DOWN into the old OB body zone.
  4. That zone is now SUPPORT — a bullish breaker entry.
Used for pyramid adds: "chasing a move but in a disciplined manner."
"""

from dataclasses import dataclass, field
from typing import Optional
import config


@dataclass
class OrderBlock:
    direction: int          # +1 bullish, -1 bearish
    top: float              # wick high of the OB candle
    bottom: float           # wick low of the OB candle
    body_top: float         # max(open, close) — Ep. 35 body zone
    body_bottom: float      # min(open, close) — Ep. 35 body zone
    bar_index: int
    mitigated: bool = False

    @property
    def mid(self) -> float:
        return (self.top + self.bottom) / 2.0

    @property
    def body_mid(self) -> float:
        """50% mean threshold per Episode 35."""
        return (self.body_top + self.body_bottom) / 2.0


def _has_fvg_between(candles, ob_idx: int, disp_idx: int, direction: int) -> bool:
    """Episode 18: there must be an imbalance between the OB and displacement."""
    for j in range(ob_idx + 2, disp_idx + 1):
        c0, c2 = candles[j - 2], candles[j]
        if direction > 0 and c2.Low > c0.High:
            return True
        if direction < 0 and c2.High < c0.Low:
            return True
    return False


def detect_order_blocks(candles, lookback: int = None) -> list[OrderBlock]:
    """Scan `candles` (oldest -> newest) for OBs in the last `lookback` bars."""
    lookback = lookback or config.OB_LOOKBACK_BARS
    n = len(candles)
    obs: list[OrderBlock] = []
    start = max(3, n - lookback)
    seen: set[int] = set()

    for i in range(start, n):
        cur = candles[i]

        # Bullish displacement: up-close candle that breaks above a prior bearish OB.
        if cur.Close > cur.Open:
            for j in range(i - 1, max(0, i - 50) - 1, -1):
                ob_c = candles[j]
                if ob_c.Close < ob_c.Open:  # last bearish candle = bullish OB candidate
                    if cur.Close > ob_c.High and j not in seen:
                        if _has_fvg_between(candles, j, i, +1):
                            obs.append(OrderBlock(
                                direction=+1,
                                top=ob_c.High,
                                bottom=ob_c.Low,
                                body_top=ob_c.Open,
                                body_bottom=ob_c.Close,
                                bar_index=j,
                            ))
                            seen.add(j)
                    break

        # Bearish displacement: down-close candle that breaks below a prior bullish OB.
        elif cur.Close < cur.Open:
            for j in range(i - 1, max(0, i - 50) - 1, -1):
                ob_c = candles[j]
                if ob_c.Close > ob_c.Open:  # last bullish candle = bearish OB candidate
                    if cur.Close < ob_c.Low and j not in seen:
                        if _has_fvg_between(candles, j, i, -1):
                            obs.append(OrderBlock(
                                direction=-1,
                                top=ob_c.High,
                                bottom=ob_c.Low,
                                body_top=ob_c.Close,
                                body_bottom=ob_c.Open,
                                bar_index=j,
                            ))
                            seen.add(j)
                    break

    # Mark mitigated: price trades back through the OB body (Ep. 35: body is the zone).
    for ob in obs:
        future = candles[ob.bar_index + 2:]
        for c in future:
            if ob.direction > 0 and c.Low <= ob.body_bottom:
                ob.mitigated = True
                break
            if ob.direction < 0 and c.High >= ob.body_top:
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


def find_breaker_zone(
    candles,
    direction: int,
    current_price: float,
    pip_value: float,
    lookback: int = None,
) -> Optional[OrderBlock]:
    """Return the nearest breaker block that current price is returning to, or None.

    A BULLISH BREAKER (+1): a BEARISH OB (-1) that was mitigated upward (price
    broke above its body_top). Price has since retraced back into the OB body
    zone — this level now acts as support.

    A BEARISH BREAKER (-1): a BULLISH OB (+1) that was mitigated downward (price
    broke below its body_bottom). Price has rallied back into the OB body zone —
    this level now acts as resistance.

    Tolerance: ±3 pips of the body zone is considered "at the breaker."
    """
    lookback = lookback or config.OB_LOOKBACK_BARS
    obs = detect_order_blocks(candles, lookback=lookback)
    tol = 3 * pip_value
    candidates = []

    for ob in obs:
        # Need mitigated OBs of the OPPOSITE direction.
        if ob.direction != -direction:
            continue
        if not ob.mitigated:
            continue
        # Price must be inside or within tolerance of the body zone.
        if ob.body_bottom - tol <= current_price <= ob.body_top + tol:
            candidates.append(ob)

    if not candidates:
        return None
    return min(candidates, key=lambda o: abs(o.mid - current_price))
