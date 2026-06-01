"""Strategy parameters. Tweak here, no other code changes needed."""

# --- Capital + risk ---
STARTING_CASH = 900                # R900 ZAR starting capital
ACCOUNT_CURRENCY = "ZAR"          # account denomination
USD_ZAR = 18.5                    # fixed conversion — approximate 2022-2025 mid-rate
RISK_PER_TRADE_PCT = 1.0           # % of equity risked per leg (used when above minimum)
MAX_LEGS = 3                       # pyramiding cap (initial + 2 adds)

# --- Standard-account lot sizing ---
# 1 standard lot = 100 000 base-currency units.
# Pyramid: SAME lot size on every leg — maximises pips-per-leg and keeps the
# fail-safe at exactly R0 net when the last leg stops.
#
# Fail-safe proof (R900 tier, flat 0.03 lots, L1 at X, L2 at X+10, L3 at X+20):
#   L1 trailing-stop locked at X+10  → +R55.50
#   L2 stop at BE (X+10)             → R0
#   L3 (0.03 lots) stop at X+10      → -R55.50
#   NET floor if L3 stopped           → R0  (never lose on a winning trade)
#
# Calibration (flat 0.03 lots, 40-pip trade, USD_ZAR=18.5):
#   L1 0.03 × 40 pips × R9.25/pip = R222
#   L2 0.03 × 30 pips × R9.25/pip = R166.50
#   L3 0.03 × 20 pips × R9.25/pip = R111
#   Full pyramid win: R499.50
LOT_UNITS       = 100_000
PYRAMID_LOTS    = (0.03, 0.03, 0.03)    # flat — same lot on every leg
MIN_LOT_SIZE    = PYRAMID_LOTS[0]

# Equity tiers — all legs stay equal; only the lot size grows with the account.
# Format: (min_equity_ZAR, (leg1_lots, leg2_lots, leg3_lots))
#
#   R900  → 0.03 flat  — full pyramid win R499  on 40-pip trade
#   R3000 → 0.05 flat  — full pyramid win R832  on 40-pip trade
#   R6000 → 0.10 flat  — full pyramid win R1665 on 40-pip trade
EQUITY_TIERS = [
    (6_000, (0.10, 0.10, 0.10)),
    (3_000, (0.05, 0.05, 0.05)),
    (0,     (0.03, 0.03, 0.03)),
]

# --- Targets ---
MIN_CONVICTION = 6                 # minimum conviction score to open a trade (0–9 scale)
MIN_PIPS_TARGET = 20               # minimum pips to target (entry and pyramid checks)
MIN_ENTRY_PIPS_TARGET = 20         # same as MIN_PIPS_TARGET — keep them in sync here
MIN_RR = 1.2                       # minimum reward:risk
FIXED_STOP_PIPS = 10               # fixed stop distance — 10 pips from entry
TRAIL_BE_PIPS   = 10               # move stop to breakeven when +10 pips profit
TRAIL_LOCK_PIPS = 20               # lock in +10 pips profit when +20 pips profit

# --- Account protection (wipeout prevention) ---
# 1. Peak drawdown halt: if equity falls >20% from its highest point, stop trading
#    for DRAWDOWN_PAUSE_DAYS calendar days before retrying. Prevents cascading losses
#    in trending-against conditions.
MAX_DRAWDOWN_HALT_PCT   = 20.0
DRAWDOWN_PAUSE_DAYS     = 5
# 2. Daily loss cap: stop opening new trades for the rest of the calendar day once
#    daily losses exceed this % of the account equity at day open.
MAX_DAILY_LOSS_PCT      = 6.0     # ~2 full stop-losses at 0.03 lots
# 3. Consecutive loss pause: after N straight losses, sit out the rest of the day.
#    Counter resets automatically at the start of each new trading day.
MAX_CONSECUTIVE_LOSSES  = 5

# --- Killzones (New York time, 24h) ---
KILLZONES = [
    ("London Open",  "03:00", "05:00"),
    ("New York AM",  "07:00", "10:00"),
]
# Oceanic currencies (AUD, NZD) peak during Asian session, not London/NY.
AUD_NZD_KILLZONES = [
    ("Asian Open",  "20:00", "22:00"),   # Sydney open
    ("Tokyo Kill",  "23:00", "01:00"),   # Tokyo volume peak
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

# --- Market Profile ---
# Weekly AMD: when the weekly Judas swing is confirmed (Monday range swept on
# Tue/Wed/Thu and close back inside), pyramid legs use FULL lots regardless of
# the intermarket score — the weekly distribution is the "huge pyramid" setup.
WEEKLY_AMD_FULL_PYRAMID = True

# Session handover: at the START of each kill zone, any active position whose
# direction CONFLICTS with the confirmed weekly AMD and that is currently LOSING
# (negative pnl) is closed at market. The session's own entry logic then
# re-enters in the correct direction.
SESSION_HANDOVER_CLOSE = True

# --- News data source ---
# In backtest, the live ForexFactory "thisweek" XML is useless (it only returns
# the current real-world week). Set NEWS_SOURCE = "csv" for backtests; the loader
# reads NEWS_CSV_PATH from the algorithm bundle. "xml" hits FOREXFACTORY_XML_URL.
NEWS_SOURCE = "csv"
NEWS_CSV_PATH = "data/news_events.csv"

# --- Symbols ---
PAIRS = ("GBPUSD", "EURUSD", "NZDUSD")   # tradeable (AUDUSD excluded: poor Asian WR)
REF_EURGBP = "EURGBP"              # EUR vs GBP relative strength
REF_AUDNZD = "AUDNZD"              # AUDNZD data (loaded for AUDUSD MSS bars; not used as bias signal)
# DXY synthetic uses these (all available on OANDA):
DXY_CONSTITUENTS = ("EURUSD", "USDJPY", "GBPUSD", "USDCAD", "USDSEK", "USDCHF")
