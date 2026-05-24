"""News calendar filter (ForexFactory live XML + offline CSV).

For backtests, the live ForexFactory `ff_calendar_thisweek.xml` is useless because
it only returns the current real-world week. Use the CSV loader and bundle a
file of historical events at `data/news_events.csv` with the format:

    utc_datetime,currency,impact
    2024-06-07 12:30:00,USD,High
    2024-06-12 18:00:00,USD,High

Lines starting with `#` are comments. `utc_datetime` is ISO-ish (`YYYY-MM-DD HH:MM:SS`).
Currency must be one of NEWS_CURRENCIES; impact one of NEWS_IMPACTS.
"""

from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import pytz
import config

UTC = pytz.utc


class NewsCalendar:
    def __init__(self):
        self.events = []  # list of (utc_dt, currency, impact)
        # Date of the most recent FOMC day that caused a major whipsaw, or None.
        # Set externally by main.py when a FOMC-whipsaw is detected.
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
            impact = (ev.findtext("impact") or "").strip().title()
            date_s = (ev.findtext("date") or "").strip()
            time_s = (ev.findtext("time") or "").strip()
            if currency not in config.NEWS_CURRENCIES:
                continue
            if impact not in config.NEWS_IMPACTS:
                continue
            if not date_s or not time_s or time_s.lower() in ("all day", "tentative"):
                continue
            try:
                naive = datetime.strptime(f"{date_s} {time_s}", "%m-%d-%Y %I:%M%p")
                eastern = pytz.timezone("America/New_York").localize(naive)
                self.events.append((eastern.astimezone(UTC), currency, impact))
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
            dt_s, currency, impact = parts[0], parts[1].upper(), parts[2].title()
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
            self.events.append((UTC.localize(naive), currency, impact))
        return len(self.events)

    def is_blocked(self, utc_dt: datetime) -> bool:
        """True if `utc_dt` is within block window of a relevant event."""
        if utc_dt.tzinfo is None:
            utc_dt = UTC.localize(utc_dt)
        before = timedelta(minutes=config.NEWS_BLOCK_MINUTES_BEFORE)
        after = timedelta(minutes=config.NEWS_BLOCK_MINUTES_AFTER)
        for ev_dt, _, _ in self.events:
            if ev_dt - before <= utc_dt <= ev_dt + after:
                return True
        return False

    def is_nfp_week(self, utc_dt: datetime) -> bool:
        """Return True if the ISO week of `utc_dt` contains a USD Non-Farm Payrolls event.

        NFP is typically released on the first Friday of each month at 08:30 NY time.
        We detect it by scanning our loaded events for a USD High-impact event on a
        Friday between 12:00–14:00 UTC (08:00–10:00 ET), which is the standard NFP slot.
        If no events are loaded we conservatively return False.
        """
        if utc_dt.tzinfo is None:
            utc_dt = UTC.localize(utc_dt)
        week_start = utc_dt.date() - __import__("datetime").timedelta(days=utc_dt.weekday())
        week_end = week_start + __import__("datetime").timedelta(days=6)
        for ev_dt, currency, impact in self.events:
            if currency != "USD" or impact != "High":
                continue
            ev_date = ev_dt.date()
            if not (week_start <= ev_date <= week_end):
                continue
            # NFP is on a Friday (weekday 4) and released around 12:30 UTC
            if ev_dt.weekday() == 4 and 12 <= ev_dt.hour <= 14:
                return True
        return False
