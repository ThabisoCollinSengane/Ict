"""Entry signal composition.

Pulls together every gate from the new pipeline and returns a single
`EntrySignal` (or None). Side-effect-free: pure function of the inputs.
"""

from dataclasses import dataclass
from typing import Optional

import config
from ict.fvg import FVG
from ict.target import Target
from risk import pip_size, adjust_entry


@dataclass
class EntrySignal:
    pair: str
    direction: int
    entry: float         # cost-adjusted
    raw_entry: float     # FVG mid before costs
    stop: float
    target: Target
    confluence_score: float
    swept_level_name: Optional[str]
    htf_zone_kind: Optional[str]
    htf_zone_tf: Optional[str]
    risk_pips: float
    reward_pips: float

    @property
    def rr(self) -> float:
        return self.reward_pips / self.risk_pips if self.risk_pips > 0 else 0.0


def build(
    *,
    pair: str,
    direction: int,
    trigger_fvg: FVG,
    swept_price: float,
    target: Target,
    confluence_score: float,
    swept_level_name: Optional[str],
    htf_zone_kind: Optional[str],
    htf_zone_tf: Optional[str],
) -> Optional[EntrySignal]:
    pip = pip_size(pair)
    raw_entry = trigger_fvg.mid

    # Stop beyond the swept extreme by 1 pip of structural slack (costs added separately).
    stop = (swept_price - pip) if direction > 0 else (swept_price + pip)
    entry = adjust_entry(raw_entry, direction, pair)

    risk = abs(entry - stop)
    if risk <= 0:
        return None
    risk_pips = risk / pip
    reward_pips = abs(target.price - entry) / pip
    if reward_pips < config.MIN_PIPS_TARGET:
        return None
    if reward_pips / risk_pips < config.MIN_RR:
        return None

    return EntrySignal(
        pair=pair, direction=direction,
        entry=entry, raw_entry=raw_entry, stop=stop,
        target=target, confluence_score=confluence_score,
        swept_level_name=swept_level_name,
        htf_zone_kind=htf_zone_kind, htf_zone_tf=htf_zone_tf,
        risk_pips=risk_pips, reward_pips=reward_pips,
    )
