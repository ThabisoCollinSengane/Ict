"""HTF liquidity zones: D1/W1 FVGs (top-rank), H4 FVGs/OBs, M15/H4 breakers.

Per user spec: Daily/Weekly FVGs always provoke a reaction even if brief, so
they're the highest-rank HTF zone. Below them sit H4 FVGs and OBs, then
M15/H4 breakers.

The pipeline calls `most_recent_tap(now, current_price)` to ask: did price
just enter a fresh HTF zone aligned with our bias? If yes, we look for the
manipulation+sweep on lower TFs.
"""

from dataclasses import dataclass
from typing import Optional

import config
from ict.fvg import detect_new_fvg, update_mitigation, FVG
from ict.order_block import detect_order_blocks, OrderBlock
from ict.breaker import detect_breakers, Breaker
from ict.swings import find_swings


@dataclass
class Zone:
    kind: str               # "fvg" | "ob" | "breaker"
    tf: str
    direction: int          # +1 bullish (price reacts UP), -1 bearish
    top: float
    bottom: float
    rank: int               # lower = higher priority

    @property
    def mid(self) -> float:
        return (self.top + self.bottom) / 2.0

    def contains(self, price: float) -> bool:
        return self.bottom <= price <= self.top


_RANK_BY_KIND_TF = {
    ("fvg", "W"):     0,
    ("fvg", "D"):     1,
    ("fvg", "240T"):  3,
    ("fvg", "60T"):   3,
    ("ob",  "D"):     2,
    ("ob",  "240T"):  4,
    ("ob",  "60T"):   4,
    ("breaker", "240T"): 4,
    ("breaker", "15T"):  5,
    ("swing", "D"):    3,
    ("swing", "240T"): 4,
    ("swing", "60T"):  5,
}


def collect_zones(tf_bars_by_tf: dict, direction: int) -> list[Zone]:
    """Build the list of currently *unmitigated* zones across HTFs.

    `tf_bars_by_tf` maps tf-name -> list[Bar] for the symbol of interest.
    `direction` filters to zones that would act as support (+1) or resistance (-1).
    """
    zones: list[Zone] = []

    for tf in config.HTF_FVG_TFS:
        bars = tf_bars_by_tf.get(tf, [])
        zones += _scan_fvgs(bars, tf, direction)

    for tf in config.HTF_OB_TFS:
        bars = tf_bars_by_tf.get(tf, [])
        zones += _scan_obs(bars, tf, direction)

    for tf in config.BREAKER_TFS:
        bars = tf_bars_by_tf.get(tf, [])
        zones += _scan_breakers(bars, tf, direction)

    # HTF swings themselves are liquidity — resting orders stack just above
    # a swing high (buyside) and just below a swing low (sellside). Tap-
    # detection picks these up so a setup forming at a clean H4 / H1 swing
    # qualifies even when no FVG / OB / Breaker overlaps the level.
    for tf in config.HTF_SWING_TFS:
        bars = tf_bars_by_tf.get(tf, [])
        zones += _scan_swings(bars, tf, direction)

    zones.sort(key=lambda z: (z.rank, -z.top))
    return zones


def _scan_fvgs(bars, tf, direction) -> list[Zone]:
    if len(bars) < 4:
        return []
    fvgs: list[FVG] = []
    # Walk the whole series to enumerate FVGs (cheap on HTF — few hundred bars).
    for i in range(2, len(bars)):
        g = detect_new_fvg(bars[: i + 1], "EURUSD")  # symbol used only for pip floor
        if g is not None:
            fvgs.append(g)
    for g in fvgs:
        for c in bars[g.bar_index + 1:]:
            if g.direction > 0 and c.Low <= g.bottom:
                g.mitigated = True
                break
            if g.direction < 0 and c.High >= g.top:
                g.mitigated = True
                break
    out = []
    for g in fvgs:
        if g.mitigated or g.direction != direction:
            continue
        out.append(Zone(
            kind="fvg", tf=tf, direction=g.direction,
            top=g.top, bottom=g.bottom,
            rank=_RANK_BY_KIND_TF.get(("fvg", tf), 9),
        ))
    return out


def _scan_obs(bars, tf, direction) -> list[Zone]:
    obs = detect_order_blocks(bars)
    out = []
    for ob in obs:
        if ob.mitigated or ob.direction != direction:
            continue
        out.append(Zone(
            kind="ob", tf=tf, direction=ob.direction,
            top=ob.top, bottom=ob.bottom,
            rank=_RANK_BY_KIND_TF.get(("ob", tf), 9),
        ))
    return out


def _scan_breakers(bars, tf, direction) -> list[Zone]:
    brs = detect_breakers(bars, tf=tf)
    out = []
    for br in brs:
        if br.mitigated or br.direction != direction:
            continue
        out.append(Zone(
            kind="breaker", tf=tf, direction=br.direction,
            top=br.top, bottom=br.bottom,
            rank=_RANK_BY_KIND_TF.get(("breaker", tf), 9),
        ))
    return out


def _scan_swings(bars, tf, direction) -> list[Zone]:
    """Unmitigated swing highs (for short setups) or swing lows (longs) as
    standalone liquidity zones. Zone width = swing price ± SWING_ZONE_TOL.
    """
    if not bars or len(bars) < 5:
        return []
    swings = find_swings(bars)
    if not swings:
        return []
    target_kind = +1 if direction < 0 else -1
    out = []
    # Use the last ~10 swings of relevant kind; earlier ones are noise.
    for s in [sw for sw in swings if sw.kind == target_kind][-10:]:
        # Check if subsequent close has broken this swing → mitigated.
        tail = bars[s.index + 1:]
        mitigated = any(
            (target_kind == +1 and c.Close > s.price)
            or (target_kind == -1 and c.Close < s.price)
            for c in tail
        )
        if mitigated:
            continue
        tol = config.HTF_SWING_TOL_PIPS * 0.0001
        out.append(Zone(
            kind="swing", tf=tf, direction=direction,
            top=s.price + tol if target_kind == +1 else s.price,
            bottom=s.price if target_kind == +1 else s.price - tol,
            rank=_RANK_BY_KIND_TF.get(("swing", tf), 6),
        ))
    return out


def most_recent_tap(zones: list[Zone], recent_bars) -> Optional[Zone]:
    """Highest-priority unmitigated zone whose range was entered by any of the
    `recent_bars`' wicks (High/Low). Use the last 5-10 entry-TF bars so a tap
    that just happened is still detectable.
    """
    if not recent_bars:
        return None
    for z in zones:
        for b in recent_bars:
            if b.Low <= z.top and b.High >= z.bottom:
                return z
    return None
