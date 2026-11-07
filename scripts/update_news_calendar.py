"""ForexFactory news calendar updater.

Downloads the ForexFactory XML calendar (this week + next week), merges new
High/Medium-impact events into data/news_events.csv, and sends a Telegram
summary of the upcoming week's schedule.

Usage
-----
    # Auto-download (requires network access to nfs.faireconomy.media):
    python scripts/update_news_calendar.py

    # Use a locally-saved XML file (e.g. downloaded in browser):
    python scripts/update_news_calendar.py --xml /path/to/ff_calendar.xml

    # Preview only — don't write CSV or send Telegram:
    python scripts/update_news_calendar.py --dry-run

    # Skip Telegram even if credentials are configured:
    python scripts/update_news_calendar.py --no-notify

Run this every Sunday evening (or any day of the week — it only appends
events that aren't already in the CSV so duplicates are never written).

ForexFactory XML URL:  https://nfs.faireconomy.media/ff_calendar_thisweek.xml
Next-week URL:         https://nfs.faireconomy.media/ff_calendar_nextweek.xml
"""

import argparse
import os
import ssl
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

import pytz

# Allow running as `python scripts/update_news_calendar.py` from the repo root
_HERE  = Path(__file__).resolve().parent
_ROOT  = _HERE.parent
sys.path.insert(0, str(_ROOT))

import config
from scripts.notify import send_message

UTC = pytz.utc
ET_ZONE = pytz.timezone("America/New_York")

# Currencies to track (adds NZD for NZDUSD trading pair)
_CURRENCIES = frozenset({"USD", "EUR", "GBP", "NZD"})

# ForexFactory XML endpoints (thisweek + nextweek)
_FF_URLS = [
    "https://nfs.faireconomy.media/ff_calendar_thisweek.xml",
    "https://nfs.faireconomy.media/ff_calendar_nextweek.xml",
]

# Impact levels to keep (match news_filter.py convention)
_IMPACTS = frozenset({"High", "Medium"})

# Event name normalisation for the CRITICAL set
_CRITICAL = frozenset({"CPI", "NFP", "FOMC", "RBNZ", "BOE", "ECB"})

# Data file
_CSV_PATH = _ROOT / "data" / "news_events.csv"

_CSV_HEADER = """\
# High-impact news events — auto-maintained by scripts/update_news_calendar.py
# Format: utc_datetime,currency,impact,event_name
utc_datetime,currency,impact,event_name
"""


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def _fetch_xml(url: str, timeout: int = 12) -> str | None:
    """Download the ForexFactory XML calendar. Returns raw text or None."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/xml,application/xml,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Build SSL contexts to try in order: certifi → default → unverified fallback
    ctxs: list[ssl.SSLContext | None] = []
    try:
        import certifi
        ctxs.append(ssl.create_default_context(cafile=certifi.where()))
    except ImportError:
        pass
    ctxs.append(ssl.create_default_context())
    _unverified = ssl.create_default_context()
    _unverified.check_hostname = False
    _unverified.verify_mode    = ssl.CERT_NONE
    ctxs.append(_unverified)   # last resort — warns if used

    req = urllib.request.Request(url, headers=headers)
    last_exc: Exception | None = None
    for i, ctx in enumerate(ctxs):
        try:
            opener = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=ctx)
            )
            with opener.open(req, timeout=timeout) as resp:
                if i == len(ctxs) - 1:
                    print("  [SSL] warning: using unverified connection (proxy CA?)")
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            print(f"  [fetch] HTTP {exc.code} — {url}")
            return None   # 403/404 won't be fixed by switching SSL context
        except urllib.error.URLError as exc:
            # URLError wraps ssl.SSLError — cascade to next context
            if isinstance(exc.reason, ssl.SSLError) or "SSL" in str(exc.reason):
                last_exc = exc
                continue
            last_exc = exc
            break
        except ssl.SSLError as exc:
            last_exc = exc
            continue
        except Exception as exc:
            last_exc = exc
            break

    print(f"  [fetch] {last_exc} — {url}")
    return None


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _parse_xml(xml_text: str) -> list[tuple]:
    """Parse ForexFactory XML into a list of (utc_dt, currency, impact, name).

    Handles both the 12-hour ET format ("06-09-2025 8:30am") and any variants
    ForexFactory has used over the years.
    """
    events = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        print(f"  [parse] XML error: {exc}", flush=True)
        return events

    for ev in root.findall("event"):
        currency = (ev.findtext("country") or "").strip().upper()
        impact   = (ev.findtext("impact")  or "").strip().title()
        title    = (ev.findtext("title")   or "").strip()
        date_s   = (ev.findtext("date")    or "").strip()
        time_s   = (ev.findtext("time")    or "").strip()

        if currency not in _CURRENCIES:
            continue
        if impact not in _IMPACTS:
            continue
        if not date_s or not time_s:
            continue
        if time_s.lower() in ("all day", "tentative", ""):
            continue

        # ForexFactory date format: "06-09-2025"  time: "8:30am" or "12:30am"
        for fmt in ("%m-%d-%Y %I:%M%p", "%m-%d-%Y %I:%M %p",
                    "%m-%d-%Y %H:%M",   "%Y-%m-%d %H:%M:%S"):
            try:
                naive   = datetime.strptime(f"{date_s} {time_s}", fmt)
                eastern = ET_ZONE.localize(naive)
                utc_dt  = eastern.astimezone(UTC)
                events.append((utc_dt, currency, impact, title))
                break
            except ValueError:
                continue

    return events


# ---------------------------------------------------------------------------
# CSV load / save
# ---------------------------------------------------------------------------

def _load_csv() -> list[tuple]:
    """Load existing events from news_events.csv. Returns list of (utc_dt, ccy, impact, name)."""
    if not _CSV_PATH.exists():
        return []
    events = []
    for raw in _CSV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("utc_datetime"):
            continue
        parts = [p.strip() for p in line.split(",", 3)]
        if len(parts) < 3:
            continue
        dt_s, ccy, impact = parts[0], parts[1].upper(), parts[2].title()
        name = parts[3].strip() if len(parts) == 4 else ""
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                utc_dt = UTC.localize(datetime.strptime(dt_s, fmt))
                events.append((utc_dt, ccy, impact, name))
                break
            except ValueError:
                continue
    return events


def _event_key(ev: tuple) -> str:
    """Stable dedup key: datetime rounded to minute + currency + impact."""
    dt, ccy, impact, _ = ev
    return f"{dt.strftime('%Y-%m-%d %H:%M')},{ccy},{impact}"


def _normalise_name(title: str) -> str:
    """Map ForexFactory verbose titles to the short names the algo uses."""
    t = title.upper()
    if "NON-FARM" in t or "NFP" in t:
        return "NFP"
    if "CPI" in t:
        return "CPI"
    if "FOMC" in t or "FEDERAL OPEN" in t:
        return "FOMC"
    if "RBNZ" in t or "RESERVE BANK OF NEW ZEALAND" in t:
        return "RBNZ"
    if "BOE" in t or "BANK OF ENGLAND" in t:
        return "BOE"
    if "ECB" in t or "EUROPEAN CENTRAL BANK" in t:
        return "ECB"
    if "BOC" in t or "BANK OF CANADA" in t:
        return "BOC"
    if "GDP" in t:
        return "GDP"
    if "PMI" in t:
        return "PMI"
    if "ISM" in t:
        return "ISM"
    if "RETAIL" in t and "SALES" in t:
        return "Retail Sales"
    if "UNEMPLOYMENT" in t or "CLAIMANT" in t or "JOBLESS" in t:
        return "Unemployment"
    if "INFLATION" in t:
        return "Inflation"
    # Keep first 30 chars of raw title as fallback
    return title[:30]


def _save_csv(events: list[tuple], dry_run: bool) -> None:
    """Write all events to news_events.csv, sorted by datetime."""
    events_sorted = sorted(events, key=lambda e: e[0])
    lines = [_CSV_HEADER.rstrip("\n")]
    for dt, ccy, impact, name in events_sorted:
        dt_s = dt.strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"{dt_s},{ccy},{impact},{name}")
    content = "\n".join(lines) + "\n"
    if dry_run:
        print(f"\n[dry-run] Would write {len(events_sorted)} events to {_CSV_PATH}")
    else:
        _CSV_PATH.write_text(content, encoding="utf-8")
        print(f"\nSaved {len(events_sorted)} events → {_CSV_PATH}")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _week_summary(events: list[tuple], title: str = "Upcoming week") -> str:
    """Format a human-readable weekly calendar for Telegram / stdout."""
    now = datetime.now(UTC)
    # Show events in the next 10 days
    cutoff = now + timedelta(days=10)
    upcoming = [e for e in events if now <= e[0] <= cutoff]
    upcoming.sort(key=lambda e: e[0])

    if not upcoming:
        return f"{title}\nNo High/Medium events found in the next 10 days."

    lines = [f"{title} — high-impact schedule"]
    current_day = None
    for dt, ccy, impact, name in upcoming:
        et_dt = dt.astimezone(ET_ZONE)
        day   = et_dt.strftime("%A %d %b")
        time  = et_dt.strftime("%H:%M ET")
        if day != current_day:
            lines.append(f"\n{day}")
            current_day = day
        flag  = "🔴" if impact == "High" else "🟡"
        lines.append(f"  {flag} {time}  {ccy}  {name or impact}")

    # Highlight critical events
    critical = [
        f"{e[0].astimezone(ET_ZONE).strftime('%a %H:%M ET')} {e[1]} {e[3]}"
        for e in upcoming
        if e[3].upper() in _CRITICAL
    ]
    if critical:
        lines.append("\n⚠️ CRITICAL (hard-blocked):")
        for c in critical:
            lines.append(f"  {c}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Update ForexFactory news calendar.")
    ap.add_argument("--xml",        help="Path to a locally-saved ForexFactory XML file.")
    ap.add_argument("--dry-run",    action="store_true",
                    help="Parse and print but don't write CSV or send Telegram.")
    ap.add_argument("--no-notify",  action="store_true",
                    help="Skip Telegram notification even if credentials exist.")
    ap.add_argument("--show-all",   action="store_true",
                    help="Print ALL upcoming events (default: next 10 days only).")
    args = ap.parse_args()

    # ---- Step 1: collect new events from ForexFactory ----
    new_events: list[tuple] = []

    if args.xml:
        # Local file provided
        xml_path = Path(args.xml)
        if not xml_path.exists():
            print(f"ERROR: file not found: {xml_path}")
            sys.exit(1)
        print(f"Reading XML from {xml_path}...")
        xml_text = xml_path.read_text(encoding="utf-8", errors="replace")
        parsed   = _parse_xml(xml_text)
        new_events.extend(parsed)
        print(f"  Parsed {len(parsed)} events.")
    else:
        print("Fetching ForexFactory calendar...")
        for url in _FF_URLS:
            print(f"  {url}")
            xml_text = _fetch_xml(url)
            if xml_text:
                parsed = _parse_xml(xml_text)
                new_events.extend(parsed)
                print(f"  → {len(parsed)} events parsed.")
            else:
                print("  → Failed (no data). Try --xml with a manually saved file.")

    if not new_events:
        print("\nNo events fetched. Exiting.")
        print(
            "\nTo update manually:\n"
            "  1. Open https://www.forexfactory.com in your browser\n"
            "  2. Download/save the XML from:\n"
            "     https://nfs.faireconomy.media/ff_calendar_thisweek.xml\n"
            "  3. Run: python scripts/update_news_calendar.py --xml /path/to/file.xml"
        )
        return

    # Normalise event names
    new_events = [(dt, ccy, impact, _normalise_name(name))
                  for dt, ccy, impact, name in new_events]

    # ---- Step 2: merge with existing CSV ----
    existing = _load_csv()
    existing_keys = {_event_key(e) for e in existing}
    added = [e for e in new_events if _event_key(e) not in existing_keys]

    print(f"\nExisting events in CSV: {len(existing)}")
    print(f"New events from feed:   {len(new_events)}")
    print(f"New (not in CSV):       {len(added)}")

    if added:
        all_events = existing + added
        _save_csv(all_events, args.dry_run)
    else:
        print("Nothing new to add.")

    # ---- Step 3: print upcoming schedule ----
    all_events_for_display = existing + added if added else existing
    summary = _week_summary(all_events_for_display)
    print(f"\n{'='*60}")
    print(summary)
    print('='*60)

    # ---- Step 4: Telegram notification ----
    if not args.dry_run and not args.no_notify:
        ok = send_message(summary)
        if ok:
            print("\n✓ Telegram notification sent.")
        else:
            print("\n  Telegram not configured or failed — skipped.")
            print("  Set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in config.py or env vars.")


if __name__ == "__main__":
    main()
