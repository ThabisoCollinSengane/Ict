"""Game-theory setup scoring.

Rewards setups where:
  - the manipulation swept a recognizable retail pool (PDH/PDL/PWH/PWL/
    session H/L/CBDR/equal H/L), because that's where stops are clustered;
  - the wick depth is "strong" (per config.SWEEP_STRONG_PIPS);
  - NY-AM is reversing London's first-hour displacement (Judas pattern);
  - the manipulation tapped a D1/W1 FVG (always reacts);
  - entry fires inside an ICT macro delivery window;
  - the sweep took out the CBDR (14:00-20:00 NY) extreme.
"""

from dataclasses import dataclass, field
from typing import Optional

import config
from ict.cls_cycles import in_macro_window


@dataclass
class ScoreBreakdown:
    base: float = 1.0
    bonuses: dict = field(default_factory=dict)

    @property
    def total(self) -> float:
        return self.base + sum(self.bonuses.values())


def score_setup(
    *,
    swept_level_name: Optional[str],       # e.g. "PDH", "AsiaLow", "PDL", "CBDRHigh", or None
    sweep_strong: bool,
    htf_zone_kind: Optional[str],          # "fvg" | "ob" | "breaker" | None
    htf_zone_tf: Optional[str],            # "W" | "D" | "240T" | "15T" | None
    timestamp,
    london_first_hour_dir: Optional[int],  # +1/-1/None
    trade_direction: int,
    session_phase: str,                    # "ny_am" | "london" | ...
) -> ScoreBreakdown:
    s = ScoreBreakdown()

    # Retail pool sweep bonus.
    retail_pools = {"PDH", "PDL", "PWH", "PWL",
                    "LondonHigh", "LondonLow",
                    "AsiaHigh", "AsiaLow",
                    "CBDRHigh", "CBDRLow"}
    if swept_level_name in retail_pools:
        s.bonuses["retail_pool"] = config.GT_RETAIL_POOL_BONUS
    if swept_level_name in {"CBDRHigh", "CBDRLow"}:
        s.bonuses["cbdr_sweep"] = config.GT_CBDR_SWEEP_BONUS

    if sweep_strong:
        s.bonuses["strong_wick"] = config.GT_STRONG_WICK_BONUS

    # D1/W1 FVG tap.
    if htf_zone_kind == "fvg" and htf_zone_tf in ("D", "W"):
        s.bonuses["daily_fvg"] = config.GT_DAILY_FVG_BONUS

    # ICT macro window.
    if in_macro_window(timestamp):
        s.bonuses["macro_window"] = config.GT_MACRO_BONUS

    # Judas: NY-AM reversing London's first-hour displacement.
    if (
        session_phase == "ny_am"
        and london_first_hour_dir is not None
        and london_first_hour_dir == -trade_direction
    ):
        s.bonuses["judas"] = config.GT_JUDAS_BONUS

    return s


def passes(score: ScoreBreakdown) -> bool:
    return score.total >= config.GT_MIN_SCORE
