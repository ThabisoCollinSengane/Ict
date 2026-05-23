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
    # New continuous-feature inputs (all optional; None = not measured).
    consolidation_score: Optional[float] = None,    # time_in_zone_pre_formation in [0,1]
    amd_phase: Optional[str] = None,                # "ACCUMULATION"|"MANIPULATION"|"DISTRIBUTION"|"NONE"|None
    dwell_count: Optional[int] = None,              # bars touching swept level pre-sweep
    displacement_strength: Optional[float] = None,  # middle-bar range / median
    range_expansion_ratio: Optional[float] = None,  # at FVG bar
    vol_regime_label: Optional[str] = None,         # "DEAD" | "NORMAL" | "EXPANDING"
    news_proximity_minutes: Optional[int] = None,   # signed minutes
    news_impact: Optional[str] = None,              # "High" | "Medium" | None
    smt_confirmed: Optional[bool] = None,           # True when NYO lag-divergence confirms
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

    # HTF FVG tap is the highest-conviction zone class — Daily/Weekly get
    # the strongest bonus, H4 / H1 a smaller but meaningful one (user-spec:
    # HTF FVGs reliably react even when the LTF looks like noise).
    if htf_zone_kind == "fvg":
        if htf_zone_tf in ("D", "W"):
            s.bonuses["daily_fvg"] = config.GT_DAILY_FVG_BONUS
        elif htf_zone_tf in ("240T", "60T"):
            s.bonuses["htf_fvg"] = config.GT_HTF_FVG_BONUS

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

    # --- New continuous-feature bonuses ---
    # Consolidation bonus only counts when AMD says we're in (or just left)
    # accumulation -> the consolidation is institutional buildup, not the dead
    # zone mid-distribution. If amd_phase is not provided, default to allowing
    # the bonus (back-compat).
    consolidation_in_accumulation = (
        amd_phase is None
        or amd_phase in ("ACCUMULATION", "MANIPULATION")
    )
    if (consolidation_score is not None
            and consolidation_score >= config.GT_CONSOLIDATION_THRESHOLD
            and consolidation_in_accumulation):
        s.bonuses["consolidation"] = config.GT_CONSOLIDATION_BONUS

    if (dwell_count is not None
            and dwell_count >= config.GT_DWELL_THRESHOLD_BARS):
        s.bonuses["dwell_at_sweep"] = config.GT_DWELL_BONUS

    if (displacement_strength is not None
            and displacement_strength >= config.GT_DISPLACEMENT_THRESHOLD):
        s.bonuses["displacement"] = config.GT_DISPLACEMENT_BONUS

    if (range_expansion_ratio is not None
            and range_expansion_ratio >= config.GT_RANGE_EXPANSION_THRESHOLD):
        s.bonuses["range_expansion"] = config.GT_RANGE_EXPANSION_BONUS

    if vol_regime_label == "DEAD":
        s.bonuses["vol_regime_dead"] = -abs(config.GT_DEAD_REGIME_PENALTY)
    elif vol_regime_label == "EXPANDING":
        s.bonuses["vol_regime_expanding"] = config.GT_EXPANDING_REGIME_BONUS

    if (news_proximity_minutes is not None and news_impact is not None
            and abs(news_proximity_minutes) <= config.GT_NEWS_PROXIMITY_MINUTES
            and news_impact in ("High", "Medium")):
        s.bonuses["news_proximity"] = config.GT_NEWS_PROXIMITY_BONUS

    if smt_confirmed:
        s.bonuses["smt"] = config.GT_SMT_BONUS

    return s


def passes(score: ScoreBreakdown) -> bool:
    return score.total >= config.GT_MIN_SCORE
