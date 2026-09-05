"""Narrative context scoring — contextual story layer for trade conviction.

Factors a narrative for WHY a move should happen using:
  1. Day-of-week tendency (Tue/Wed = distribution days)
  2. NFP-week consolidation context (Mon/Tue of NFP week = tight range = quality Judas)
  3. Rate decision context (day-after-FOMC/ECB/BOE = post-decision continuation)
  4. Prior-session PD array provenance (previous session sweep agrees with direction)
  5. Seasonal/monthly tendency (monthly directional lean per pair)

Each factor contributes 0 or 1 to the total narrative score (0-5).
Analytics-only on first deployment — conviction contributor, NOT a gate.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

import config


class NarrativeContext:
    def __init__(self):
        self._seasonal_data = None
        self._seasonal_loaded = False

    def score(self, pair, direction, t, news_cal=None,
              prev_session_sweep_dir=None):
        """Compute narrative conviction score.

        Args:
            pair: "EURUSD", "GBPUSD", "NZDUSD"
            direction: +1 (long) or -1 (short)
            t: pandas Timestamp or datetime (UTC)
            news_cal: NewsCalendar instance (for NFP/rate decision factors)
            prev_session_sweep_dir: +1/-1/None — the AMD sweep direction from
                the previous session (London for NY, Asian for London). Caller
                computes this from _session_range_amd or _prev_session_range.

        Returns:
            dict with keys: total, dow, nfp, rate, pd_prov, seasonal
        """
        result = {"total": 0, "dow": False, "nfp": False,
                  "rate": 0, "pd_prov": False, "seasonal": False}

        if not config.NARRATIVE_ENABLED:
            return result

        dt = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if hasattr(dt, "tzinfo") and dt.tzinfo is not None:
            pass
        else:
            import pytz
            dt = pytz.utc.localize(dt)

        if config.NARRATIVE_DOW_ENABLED:
            result["dow"] = self._dow_score(dt)
            if result["dow"]:
                result["total"] += 1

        if config.NARRATIVE_NFP_ENABLED and news_cal is not None:
            result["nfp"] = self._nfp_week_score(dt, news_cal)
            if result["nfp"]:
                result["total"] += 1

        if config.NARRATIVE_RATE_ENABLED and news_cal is not None:
            result["rate"] = self._rate_decision_score(dt, news_cal)
            if result["rate"] > 0:
                result["total"] += 1

        if config.NARRATIVE_PD_PROV_ENABLED:
            result["pd_prov"] = self._pd_prov_score(
                direction, prev_session_sweep_dir)
            if result["pd_prov"]:
                result["total"] += 1

        if config.NARRATIVE_SEASONAL_ENABLED:
            result["seasonal"] = self._seasonal_score(pair, direction, dt)
            if result["seasonal"]:
                result["total"] += 1

        return result

    def _dow_score(self, dt):
        """Tue/Wed are the strongest distribution days (ICT)."""
        dow_days = [int(d) for d in config.NARRATIVE_DOW_DAYS.split(",")]
        return dt.weekday() in dow_days

    def _nfp_week_score(self, dt, news_cal):
        """Mon/Tue of NFP week: tight consolidation = high-quality Judas."""
        if not news_cal.is_nfp_week(dt):
            return False
        return dt.weekday() in (0, 1)

    def _rate_decision_score(self, dt, news_cal):
        """Day-after-FOMC/ECB/BOE = post-decision continuation (+1).
        FOMC day itself = whipsaw (-1). Otherwise 0."""
        today = dt.date()
        yesterday = today - timedelta(days=1)
        if yesterday.weekday() == 6:
            yesterday -= timedelta(days=2)
        elif yesterday.weekday() == 5:
            yesterday -= timedelta(days=1)

        for ev_dt, currency, impact, event_name in news_cal.events:
            if impact != "High":
                continue
            name_upper = event_name.upper() if event_name else ""
            if name_upper not in ("FOMC", "CPI", "NFP"):
                if currency in ("GBP", "EUR") and impact == "High":
                    if ev_dt.date() == yesterday:
                        return 1
                continue
            if name_upper == "FOMC":
                if ev_dt.date() == today:
                    return -1
                if ev_dt.date() == yesterday:
                    return 1
        return 0

    def _pd_prov_score(self, direction, prev_session_sweep_dir):
        """Previous session sweep agrees with current trade direction."""
        if prev_session_sweep_dir is None:
            return False
        return prev_session_sweep_dir == direction

    def _seasonal_score(self, pair, direction, dt):
        """Monthly tendency agrees with trade direction."""
        data = self._load_seasonal()
        if data is None:
            return False
        pair_data = data.get(pair)
        if pair_data is None:
            return False
        month_data = pair_data.get("month", {})
        month_key = str(dt.month)
        bucket = month_data.get(month_key)
        if bucket is None:
            return False
        grade = bucket.get("grade", "noise")
        if grade in ("noise", "mild"):
            return False
        up_rate = bucket.get("up_rate", 0.5)
        if direction > 0 and up_rate > 0.5:
            return True
        if direction < 0 and up_rate < 0.5:
            return True
        return False

    def _load_seasonal(self):
        if self._seasonal_loaded:
            return self._seasonal_data
        self._seasonal_loaded = True
        path = config.NARRATIVE_SEASONAL_FILE
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                self._seasonal_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
        return self._seasonal_data
