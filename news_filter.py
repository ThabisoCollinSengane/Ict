"""ForexFactory weekly news calendar filter.

Loads https://nfs.faireconomy.media/ff_calendar_thisweek.xml once per session
(refresh on a weekly schedule from main.py). Blocks new entries within a window
around High/Medium impact USD/EUR/GBP events.
"""

from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import pytz
import config

UTC = pytz.utc


class NewsCalendar:
    def __init__(self):
        self.events: list[tuple[datetime, str, str]] = []  # (utc_dt, currency, impact)

    def load(self, xml_text: str) -> int:
        """Parse ForexFactory weekly XML. Returns number of relevant events kept."""
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
                # ForexFactory format: MM-DD-YYYY  h:mmam/pm (US Eastern)
                naive = datetime.strptime(f"{date_s} {time_s}", "%m-%d-%Y %I:%M%p")
                eastern = pytz.timezone("America/New_York").localize(naive)
                self.events.append((eastern.astimezone(UTC), currency, impact))
            except ValueError:
                continue
        return len(self.events)

    def is_blocked(self, utc_dt: datetime) -> bool:
        """True if `utc_dt` is within block window of a relevant event."""
        before = timedelta(minutes=config.NEWS_BLOCK_MINUTES_BEFORE)
        after = timedelta(minutes=config.NEWS_BLOCK_MINUTES_AFTER)
        for ev_dt, _, _ in self.events:
            if ev_dt - before <= utc_dt <= ev_dt + after:
                return True
        return False
