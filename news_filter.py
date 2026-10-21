"""News calendar filter (ForexFactory live XML + offline CSV).

For backtests, the live ForexFactory `ff_calendar_thisweek.xml` is useless because
it only returns the current real-world week. Use the CSV loader and bundle a
file of historical events at `data/news_events.csv` with the format:

    utc_datetime,currency,impact[,event_name]
    2024-06-07 12:30:00,USD,High,NFP
    2024-06-12 13:30:00,USD,High,CPI
    2024-06-12 19:00:00,USD,High,FOMC
    2024-07-04 12:30:00,GBP,High

The optional 4th column is the event name. Events named in
CRITICAL_NEWS_EVENTS (CPI, NFP, FOMC) are blocked entirely — they produce
20-40+ pip Judas spikes that blow through any tight stop. All other High-impact
events are allowed with the normal 10-pip stop + widened news spread.

Lines starting with `#` are comments. `utc_datetime` is ISO-ish.
Currency must be one of NEWS_CURRENCIES; impact one of NEWS_IMPACTS.
"""

from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import pytz
import config

UTC = pytz.utc


class NewsCalendar:
    def __init__(self):
        self.events = []  # list of (utc_dt, currency, impact, event_name)
        self.fomc_whipsaw_date = None

    # ---- Live ForexFactory weekly XML (works only for the current week) ----
    def load(self, xml_text: str) -> int:
        self.events.clear()
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return 0
        for ev in root.findall("event"):
            currency = (ev.findtext("country") or "").strip().upper()
            impact   = (ev.findtext("impact")  or "").strip().title()
            title    = (ev.findtext("title")   or "").strip()
            date_s   = (ev.findtext("date")    or "").strip()
            time_s   = (ev.findtext("time")    or "").strip()
            if currency not in config.NEWS_CURRENCIES:
                continue
            if impact not in config.NEWS_IMPACTS:
                continue
            if not date_s or not time_s or time_s.lower() in ("all day", "tentative"):
                continue
            try:
                naive   = datetime.strptime(f"{date_s} {time_s}", "%m-%d-%Y %I:%M%p")
                eastern = pytz.timezone("America/New_York").localize(naive)
                self.events.append((eastern.astimezone(UTC), currency, impact, title))
            except ValueError:
                continue
        return len(self.events)

    # ---- Offline CSV (backtests / historical replay) ----
    def load_csv(self, csv_text: str) -> int:
        self.events.clear()
        for raw in csv_text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                continue
            dt_s     = parts[0]
            currency = parts[1].upper()
            impact   = parts[2].title()
            # Optional 4th column: event name (CPI, NFP, FOMC, or blank)
            event_name = parts[3].strip() if len(parts) >= 4 else ""
            if currency not in config.NEWS_CURRENCIES:
                continue
            if impact not in config.NEWS_IMPACTS:
                continue
            try:
                naive = datetime.strptime(dt_s, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    naive = datetime.strptime(dt_s, "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
            self.events.append((UTC.localize(naive), currency, impact, event_name))
        return len(self.events)

    def nearest_impact(self, utc_dt: datetime) -> str | None:
        """Return the effective impact level of events within the block window, or None.

        Return values:
          "Critical" — High-impact event named in CRITICAL_NEWS_EVENTS (CPI/NFP/FOMC).
                       These produce 20-40+ pip Judas spikes; blocked like Medium.
          "High"     — Other High-impact event (BOE, ECB, etc.).
                       Allowed with 10-pip stop + widened news spread.
          "Medium"   — Medium-impact event. Blocked (spread risk, no directional catalyst).
          None       — No relevant event in window.
        """
        if utc_dt.tzinfo is None:
            utc_dt = UTC.localize(utc_dt)
        before = timedelta(minutes=config.NEWS_BLOCK_MINUTES_BEFORE)
        after  = timedelta(minutes=config.NEWS_BLOCK_MINUTES_AFTER)
        found  = None
        for ev_dt, _, impact, event_name in self.events:
            if not (ev_dt - before <= utc_dt <= ev_dt + after):
                continue
            if impact == "High":
                if event_name.upper() in config.CRITICAL_NEWS_EVENTS:
                    return "Critical"   # caller must treat this as a hard block
                return "High"           # other High: allowed with tight stop
            found = impact              # "Medium" — keep scanning for a High
        return found

    def is_blocked(self, utc_dt: datetime) -> bool:
        """True if `utc_dt` is within block window of a relevant event."""
        return self.nearest_impact(utc_dt) is not None

    def pre_release_impact(
        self,
        utc_dt: datetime,
        min_minutes: int = 16,
        max_minutes: int = 90,
    ) -> str | None:
        """Return highest effective impact of events 16-90 min in the future, or None."""
        if utc_dt.tzinfo is None:
            utc_dt = UTC.localize(utc_dt)
        found = None
        for ev_dt, _, impact, event_name in self.events:
            mins_until = (ev_dt - utc_dt).total_seconds() / 60
            if not (min_minutes <= mins_until <= max_minutes):
                continue
            if impact == "High":
                if event_name.upper() in config.CRITICAL_NEWS_EVENTS:
                    return "Critical"
                return "High"
            found = impact
        return found

    def is_nfp_week(self, utc_dt: datetime) -> bool:
        """Return True if the ISO week of `utc_dt` contains a USD NFP event."""
        if utc_dt.tzinfo is None:
            utc_dt = UTC.localize(utc_dt)
        week_start = utc_dt.date() - __import__("datetime").timedelta(days=utc_dt.weekday())
        week_end   = week_start + __import__("datetime").timedelta(days=6)
        for ev_dt, currency, impact, event_name in self.events:
            if currency != "USD" or impact != "High":
                continue
            if not (week_start <= ev_dt.date() <= week_end):
                continue
            if ev_dt.weekday() == 4 and 12 <= ev_dt.hour <= 14:
                return True
        return False
