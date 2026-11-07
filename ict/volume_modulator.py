"""P40 — conditional-volume position-size modulator (FVG/OB only, validated dirs).

The AMD tick-volume study (data/amd_tickvol_report.md) found, split per year and
consistent in BOTH 2022 and 2024:

  FVG entries : winners had LOWER entry-bar volume than losers (entryΔ −0.13 / −0.27)
                → a high-volume FVG fill is more often a loser → size DOWN.
  OB  entries : winners had HIGHER entry-bar volume than losers (entryΔ +1.10 / +0.26)
                → a high-volume OB tap is more often a winner → size UP.

The session rule from the original P40 spec was dropped — London/NY flipped sign
between years (a year-flip artifact, not a signal). No hand-picked per-context
constants: one high-volume threshold, one down step, one up step, all in config
and all subject to the full-backtest IS/OOS + MaxDD validation before shipping.

`friction_ratio` = entry-bar tick count ÷ mean of the previous N bars. None when
tick volume is unavailable (non-EU/GU pairs, years without tick data) → 1.0×.
"""

from __future__ import annotations

import config


def get_volume_modifier(entry_type: str, friction_ratio: float | None) -> float:
    """Return a size multiplier in [VOL_MOD_MIN, VOL_MOD_MAX] for this entry.

    Neutral (1.0) unless tick volume is present AND the entry is a high-volume
    FVG (down) or OB (up). Only the high-volume tail is touched — normal/low
    volume entries are left at baseline, matching where the winner/loser volume
    gap actually lives.
    """
    if friction_ratio is None:
        return 1.0
    et = (entry_type or "").lower()
    m = 1.0
    if friction_ratio >= config.VOL_MOD_HIGH_RATIO:
        if "fvg" in et:
            m = config.VOL_MOD_FVG_DOWN
        elif "ob" in et:          # excludes 'breaker' (own tag); 'ob' matches ob_m5 etc.
            m = config.VOL_MOD_OB_UP
    return max(config.VOL_MOD_MIN, min(config.VOL_MOD_MAX, m))
