"""Strategy parameters. Tweak here, no other code changes needed."""

# --- Capital + risk ---
STARTING_CASH = 10_000
RISK_PER_TRADE_PCT = 1.0           # % of equity risked per leg
MAX_LEGS = 3                       # pyramiding cap (initial + 2 adds)

# --- Targets ---
MIN_PIPS_TARGET = 10               # skip trade if nearest valid target < 10 pips
MIN_RR = 1.5                       # minimum reward:risk on initial entry

# --- Killzones (New York time, 24h) ---
KILLZONES = [
    ("London Open",  "02:00", "05:00"),
    ("New York AM",  "07:00", "10:00"),
]
NO_NEW_TRADES_LAST_MIN = 15        # skip new entries in final N min of a killzone

# --- ICT 2022 Episode 12: Market Structure hierarchy ---
# Episode 12 defines three swing tiers: LTH/LTL (Daily ~50 bars), ITH/ITL (1H ~20
# bars), STH/STL (1H ~8 bars). SWING_LOOKBACK is the ITH/ITL tier; the new
# SWING_LOOKBACK_STH covers the short-term tier used in classify_swing_structure().
SWING_LOOKBACK_STH = 8

# Episode 12 + 18: "Daily is the most important, bias is found off daily."
# When True, the daily chart BOS must agree with the intermarket signal direction.
REQUIRE_DAILY_BIAS = True

# Ep 12: "Limit your forecast to a 5-day time horizon."
MAX_FORWARD_DAYS = 5

# --- News filter ---
NEWS_BLOCK_MINUTES_BEFORE = 15
NEWS_BLOCK_MINUTES_AFTER  = 15
NEWS_IMPACTS = ("High", "Medium")
NEWS_CURRENCIES = ("USD", "EUR", "GBP")
FOREXFACTORY_XML_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

# --- Timeframes ---
LTF_ENTRY_RES_MIN = 5              # 5m execution
LTF_SETUP_RES_MIN = 15             # 15m setup (sweep + displacement)
HTF_BIAS_RES_MIN  = 60             # 1H bias
# Targets are searched across H4, Daily, Weekly; nearest viable wins.
TARGET_TF_MINUTES = (240, 1440, 10080)

# --- Structure lookbacks ---
SWING_LOOKBACK = 20                # bars to define swing high/low for BOS
EQ_HIGH_LOW_TOLERANCE_PIPS = 5     # max pip diff to call two highs "equal"
FVG_MIN_SIZE_PIPS = 3              # ignore micro FVGs
OB_LOOKBACK_BARS = 200             # how far back on HTF to scan for unmitigated OB

# --- AMD (Accumulation / Manipulation / Distribution) on M15 ---
# A consolidation range must satisfy ALL of:
#   - at least AMD_MIN_RANGE_BARS consecutive M15 bars,
#   - no wider than AMD_MAX_RANGE_PIPS (high - low),
#   - both extremes touched at least AMD_MIN_TOUCHES times.
# A manipulation = a sweep of one extreme + close back inside within the last
# AMD_SWEEP_LOOKBACK bars from NOW (not from range end).
# AMD_RANGE_END_LOOKBACK controls how far back the range end can be (separate
# from AMD_SWEEP_LOOKBACK); Asia consolidation ends hours before London/NY
# manipulation so these two windows must be independently configurable.
AMD_MIN_RANGE_BARS = 8             # ~2 hours on M15
AMD_MAX_RANGE_BARS = 96            # ~24 hours on M15
AMD_MAX_RANGE_PIPS = 35            # tight-enough coil to qualify as accumulation
AMD_MIN_TOUCHES = 2                # the high and low each tagged at least twice
AMD_RANGE_END_LOOKBACK = 96        # range can have ended up to 24 H ago (Asia → London)
AMD_SWEEP_LOOKBACK = 48            # sweep must be within last 48 M15 bars (12 H) from now

# --- News data source ---
# In backtest, the live ForexFactory "thisweek" XML is useless (it only returns
# the current real-world week). Set NEWS_SOURCE = "csv" for backtests; the loader
# reads NEWS_CSV_PATH from the algorithm bundle. "xml" hits FOREXFACTORY_XML_URL.
NEWS_SOURCE = "csv"
NEWS_CSV_PATH = "data/news_events.csv"

# --- Symbols ---
PAIRS = ("GBPUSD", "EURUSD")       # tradeable
REF_EURGBP = "EURGBP"              # relative strength reference
# DXY synthetic uses these (all available on OANDA):
DXY_CONSTITUENTS = ("EURUSD", "USDJPY", "GBPUSD", "USDCAD", "USDSEK", "USDCHF")
