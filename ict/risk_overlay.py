"""Portfolio-level risk overlay.

Sits between the strategy's signal layer and order placement. Vetoes new
entries when capital-protective limits are hit, and adjusts position size
when a correlated-pair group is already loaded.

Layer responsibilities (in order of veto priority):

1. Daily loss cap — once realized PnL for the day reaches -DAILY_LOSS_CAP_PCT
   of starting-day equity, no new entries until midnight rollover.
2. Weekly drawdown cap — once equity drops more than WEEKLY_DD_CAP_PCT below
   the week's high-water mark, halve sizing on new entries.
3. Max concurrent positions — hard cap on simultaneous open legs.
4. Correlated-group sizing — symbols in the same group (e.g. EURUSD+GBPUSD)
   share a total-risk budget. If a candidate entry would push the group's
   combined risk above CORRELATED_GROUP_RISK_CAP_PCT, the entry is shrunk
   (or vetoed if the shrunk size goes to zero).

Pure bookkeeping: no I/O, no time-source coupling. The host passes in the
current UTC datetime and the running equity; the overlay tracks daily and
weekly anchors against those inputs.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional

import config


@dataclass
class OpenLeg:
    symbol: str
    direction: int
    risk_pct: float       # % of equity this leg has at risk


@dataclass
class RiskOverlay:
    start_equity: float
    equity: float = 0.0
    day_anchor_date: Optional[date] = None
    day_anchor_equity: float = 0.0
    week_anchor_iso: Optional[tuple] = None   # (iso_year, iso_week)
    week_high_equity: float = 0.0
    open_legs: dict = field(default_factory=dict)   # leg_id -> OpenLeg
    vetoes: dict = field(default_factory=dict)       # reason -> count

    def __post_init__(self):
        if self.equity <= 0:
            self.equity = self.start_equity

    # ---- equity + rollovers ----

    def update_equity(self, equity: float, now: datetime) -> None:
        self.equity = equity
        d = now.date()
        if self.day_anchor_date != d:
            self.day_anchor_date = d
            self.day_anchor_equity = equity
        iso_year, iso_week, _ = now.isocalendar()
        if self.week_anchor_iso != (iso_year, iso_week):
            self.week_anchor_iso = (iso_year, iso_week)
            self.week_high_equity = equity
        else:
            self.week_high_equity = max(self.week_high_equity, equity)

    # ---- queries ----

    def daily_drawdown_pct(self) -> float:
        if self.day_anchor_equity <= 0:
            return 0.0
        return (self.equity - self.day_anchor_equity) / self.day_anchor_equity * 100.0

    def weekly_drawdown_pct(self) -> float:
        if self.week_high_equity <= 0:
            return 0.0
        return (self.equity - self.week_high_equity) / self.week_high_equity * 100.0

    def correlated_group_for(self, symbol: str) -> Optional[tuple]:
        for grp in config.RISK_CORRELATED_GROUPS:
            if symbol in grp:
                return grp
        return None

    def group_open_risk_pct(self, symbol: str) -> float:
        grp = self.correlated_group_for(symbol)
        if grp is None:
            return sum(l.risk_pct for l in self.open_legs.values() if l.symbol == symbol)
        return sum(l.risk_pct for l in self.open_legs.values() if l.symbol in grp)

    # ---- gate ----

    def can_enter(self, symbol: str, direction: int, candidate_risk_pct: float
                  ) -> tuple[bool, str, float]:
        """Return (allowed, reason, size_multiplier).

        size_multiplier == 1.0 means full size; < 1.0 means shrink the
        candidate; 0.0 means veto.
        """
        # 1. Daily loss cap.
        if self.daily_drawdown_pct() <= -config.RISK_DAILY_LOSS_CAP_PCT:
            self._note_veto("daily_loss_cap")
            return (False, "daily_loss_cap", 0.0)

        # 2. Max concurrent positions.
        if len(self.open_legs) >= config.RISK_MAX_CONCURRENT_LEGS:
            self._note_veto("max_concurrent")
            return (False, "max_concurrent", 0.0)

        mult = 1.0

        # 3. Weekly drawdown halving.
        if self.weekly_drawdown_pct() <= -config.RISK_WEEKLY_DD_HALVE_PCT:
            mult *= 0.5

        # 4. Correlated group cap. If the group is already loaded, shrink the
        # candidate to fit within the group's total risk cap. If even a
        # minimum-size leg won't fit, veto.
        cap = config.RISK_CORRELATED_GROUP_RISK_CAP_PCT
        if cap > 0:
            open_risk = self.group_open_risk_pct(symbol)
            remaining = cap - open_risk
            if remaining <= 0:
                self._note_veto("group_cap")
                return (False, "group_cap", 0.0)
            if candidate_risk_pct * mult > remaining:
                # Shrink to fit. Compute the multiplier needed.
                fit_mult = remaining / candidate_risk_pct
                mult = min(mult, fit_mult)
                if candidate_risk_pct * mult < config.RISK_MIN_RISK_PCT:
                    self._note_veto("group_cap_shrunk_to_zero")
                    return (False, "group_cap_shrunk_to_zero", 0.0)

        return (True, "ok", mult)

    def note_entry(self, leg_id: str, symbol: str, direction: int, risk_pct: float) -> None:
        self.open_legs[leg_id] = OpenLeg(symbol=symbol, direction=direction, risk_pct=risk_pct)

    def note_exit(self, leg_id: str) -> None:
        self.open_legs.pop(leg_id, None)

    def _note_veto(self, reason: str) -> None:
        self.vetoes[reason] = self.vetoes.get(reason, 0) + 1
