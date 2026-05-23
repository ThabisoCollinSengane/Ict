"""Strategy parameters. Tweak here, no other code changes needed."""

# --- Capital + risk ---
STARTING_CASH = 10_000
RISK_PER_TRADE_PCT = 1.0           # % of equity risked per leg
MAX_LEGS = 3                       # pyramiding cap (initial + 2 adds)

# --- Targets ---
MIN_PIPS_TARGET = 15               # skip trade if nearest valid target < this many pips
MIN_RR = 1.5                       # minimum reward:risk on initial entry

# --- Killzones (New York time, 24h) ---
KILLZONES = [
    ("London Open",  "02:00", "05:00"),
    ("New York AM",  "07:00", "10:00"),
    ("London Close", "10:00", "12:00"),
]
NO_NEW_TRADES_LAST_MIN = 15        # skip new entries in final N min of a killzone

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
EQ_HIGH_LOW_TOLERANCE_PIPS = 2     # max pip diff to call two highs "equal"
FVG_MIN_SIZE_PIPS = 3              # ignore micro FVGs
OB_LOOKBACK_BARS = 200             # how far back on HTF to scan for unmitigated OB

# --- AMD (Accumulation / Manipulation / Distribution) on M15 ---
# A consolidation range must satisfy ALL of:
#   - at least AMD_MIN_RANGE_BARS consecutive M15 bars,
#   - no wider than AMD_MAX_RANGE_PIPS (high - low),
#   - both extremes touched at least AMD_MIN_TOUCHES times.
# A manipulation = a sweep of one extreme + close back inside within the last
# AMD_SWEEP_LOOKBACK bars after the range ended.
AMD_MIN_RANGE_BARS = 8             # ~2 hours on M15
AMD_MAX_RANGE_BARS = 96            # ~24 hours on M15
AMD_MAX_RANGE_PIPS = 35            # tight-enough coil to qualify as accumulation
AMD_MIN_TOUCHES = 2                # the high and low each tagged at least twice
AMD_SWEEP_LOOKBACK = 4             # manipulation must occur within last N M15 bars

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

# ============================================================================
# NEW STRATEGY (ICT rewrite) — additions below
# Plan: /root/.claude/plans/here-is-my-strategy-elegant-squid.md
# ============================================================================

# --- True Day Open ---
# Captured once per day at 00:00 New York time. zoneinfo handles DST.
NY_TZ = "America/New_York"
NYO_HOUR_NY = 0                    # 00:00 NY local

# --- New killzones (NY time, 24h) — first hour is manipulation, no entries ---
# Entry only AFTER first_hour_minutes inside the killzone.
KZ_LONDON   = ("London",  "02:00", "05:00")
KZ_NY_AM    = ("NY AM",   "07:00", "10:00")
KZ_FIRST_HOUR_MIN = 60             # block entries during first 60 min of killzone
KZ_USED = (KZ_LONDON, KZ_NY_AM)    # only trade these in new pipeline

# --- Swing pivot ---
PIVOT_LEFT  = 2                    # bars to the left a pivot must dominate
PIVOT_RIGHT = 2                    # bars to the right (confirmation lag)

# --- Liquidity sweep / fake-run validation ---
# Wick depth in pips: piercing >= MIN qualifies; >= STRONG gets a score multiplier.
SWEEP_MIN_PIPS    = {"EURUSD": 2.0, "GBPUSD": 3.0, "DEFAULT": 2.0}
SWEEP_STRONG_PIPS = {"EURUSD": 6.0, "GBPUSD": 8.0, "DEFAULT": 6.0}
# Fake-run validation: the confirm-TF candle closes inside the level (not beyond).
# Tolerance for "closed back inside" expressed in pips of slack past the level.
FAKE_RUN_CLOSE_TOL_PIPS = 1.0

# --- Breakers ---
# Only M15 and H4 breakers are tradable (user spec).
BREAKER_TFS = ("15T", "240T")

# --- HTF FVG hierarchy for liquidity zone tap ---
# D1/W1 FVGs are first-class HTF zones. Order = preference for tap detection.
# Per user-spec: H1 FVGs are critical institutional reaction zones — many
# "M5 consolidation + sweep + reversal" setups are really just a tap of an
# H1 FVG seen from the LTF. Add H1 to the HTF tap pool.
HTF_FVG_TFS = ("W", "D", "240T", "60T")
HTF_OB_TFS  = ("D", "240T")

# --- SMT ---
# Both pair_price and other_pair_price compared to their NYO; require strict
# opposite-side relationship.
SMT_MIN_DISTANCE_PIPS = 0.5        # min pip distance from NYO to count as divergent

# --- Realism: spread + slippage (per-pair, in pips) ---
SPREAD_PIPS   = {"EURUSD": 0.5, "GBPUSD": 0.8, "DEFAULT": 1.0}
SLIPPAGE_PIPS = {"EURUSD": 0.3, "GBPUSD": 0.5, "DEFAULT": 0.5}

# --- Game-theory scoring ---
GT_MIN_SCORE = 1.0                 # below this, skip
GT_RETAIL_POOL_BONUS = 0.5         # sweep took out a recognizable retail level
GT_STRONG_WICK_BONUS = 0.4         # wick depth >= SWEEP_STRONG_PIPS
GT_JUDAS_BONUS       = 0.3         # NY-AM reversing London's first-hour displacement
GT_DAILY_FVG_BONUS   = 0.6         # manipulation tapped a D1/W1 FVG
GT_HTF_FVG_BONUS     = 0.4         # tap on H4/H1 FVG (per-user-spec: still high impact)
GT_MACRO_BONUS       = 0.5         # entry fires inside an ICT macro window
GT_CBDR_SWEEP_BONUS  = 0.4         # manipulation swept CBDR high/low

# --- CLS time cycles (NY local) ---
CLS_CYCLES = (
    ("asia",       "20:00", "02:00"),   # crosses midnight
    ("london",     "02:00", "05:00"),
    ("pre_ny",     "05:00", "07:00"),
    ("ny_am",      "07:00", "11:00"),
    ("lunch",      "11:00", "13:00"),
    ("ny_pm",      "13:00", "16:00"),
    ("cbdr",       "14:00", "20:00"),
)
# ICT macros — 20-min institutional delivery windows (NY local, hh:mm).
ICT_MACROS = (
    ("london_macro",    "02:33", "03:00"),
    ("preopen_macro",   "04:03", "04:30"),
    ("nyam_macro",      "08:50", "09:10"),
    ("ten_am_macro",    "09:50", "10:10"),
    ("nyam_close",      "10:50", "11:10"),
    ("one_pm_macro",    "13:10", "13:50"),
    ("close_macro",     "15:15", "16:00"),
)
CBDR_START_NY = "14:00"
CBDR_END_NY   = "20:00"

# --- Pyramiding ---
PYRAMID_LEG_RISK_FRAC = (1.0, 0.5, 0.5)  # leg1, leg2, leg3 risk fractions
PYRAMID_MIN_FAVOUR_PIPS = 10       # prior leg must be this many pips in profit

# --- Fractal bias cascade ---
# Every higher TF must show price still on the correct side of its most recent
# unmitigated ITH/ITL. Strict TFs MUST hold for an entry to fire; soft TFs are
# checked + reported via gate funnel but don't block.
BIAS_CASCADE_STRICT_TFS = ("D", "240T")
BIAS_CASCADE_SOFT_TFS   = ("60T", "15T")
# If an HTF ITH/ITL is broken back through AFTER a trade is open, close it?
CLOSE_ON_STRUCTURE_INVALIDATION = False

# --- New continuous-feature scoring (Addendum: volume/time/volatility/news) ---
# Pre-FVG consolidation: fraction of last N M5 bars whose range overlapped the
# FVG zone before formation. Higher = institutional accumulation.
GT_CONSOLIDATION_LOOKBACK_BARS = 12   # ~1h of M5
GT_CONSOLIDATION_THRESHOLD     = 0.50
GT_CONSOLIDATION_BONUS         = 0.4

# Pre-sweep dwell: how many recent bars touched the swept level. High =
# equal H/L stops accumulated before the sweep.
GT_DWELL_LOOKBACK_BARS         = 12
GT_DWELL_THRESHOLD_BARS        = 4
GT_DWELL_BONUS                 = 0.3

# Displacement strength: middle-bar range / median(prev N bar ranges).
# Threshold of 2.0 = bar is twice the typical recent range.
GT_DISPLACEMENT_LOOKBACK_BARS  = 10
GT_DISPLACEMENT_THRESHOLD      = 2.0
GT_DISPLACEMENT_BONUS          = 0.3

# Range expansion at FVG bar — same threshold as displacement, but applied to
# the bar containing the FVG formation rather than only the middle candle.
GT_RANGE_EXPANSION_THRESHOLD   = 2.0
GT_RANGE_EXPANSION_BONUS       = 0.2

# Volatility regime: rolling realized-vol over the last N M5 bars classified
# into DEAD/NORMAL/EXPANDING by percentile bands. Dead-regime entries get
# penalised; expanding-regime get a bonus.
GT_REALIZED_VOL_WINDOW         = 36   # ~3h of M5
GT_REALIZED_VOL_HISTORY        = 288  # ~1 trading day of M5
GT_DEAD_REGIME_PENALTY         = 0.5
GT_EXPANDING_REGIME_BONUS      = 0.2

# News proximity (REPLACES the old hard block). Entries within +/- N minutes
# of a medium/high impact news event get a positive score contribution.
GT_NEWS_PROXIMITY_MINUTES      = 30
GT_NEWS_PROXIMITY_BONUS        = 0.5

# Master switch: drop the hard news block in backtest.py and rely on scoring.
NEWS_HARD_BLOCK_ENABLED        = False

# SMT (NYO-based lag divergence). False = informational only; SMT
# contributes to the game-theory score but doesn't gate trades.
# True = legacy hard-gate behavior (no SMT divergence -> no trade).
SMT_REQUIRED                   = False
GT_SMT_BONUS                   = 0.4

# Structural stop hard cap. Stops are computed from the nearest M5 (or
# M15) swing high/low beyond the entry; when that swing is unusually
# far away (>N pips) the setup is skipped to avoid taking 1% risk on
# a structurally over-wide stop.
MAX_STRUCTURAL_STOP_PIPS       = 30

# Entry execution mode:
#   "market" - fire immediately at the current M5 Close (after spread/slippage
#              adjustment). Used to bypass FVG-mid limits that often go unfilled.
#   "limit"  - place a limit at the FVG near edge (top for longs, bottom
#              for shorts), wait up to 60 min. Default — the near edge
#              fills on first touch into the gap.
ENTRY_MODE                     = "limit"

# --- Risk overlay (portfolio-level vetoes + correlation-aware sizing) ---
# Once realized PnL for the day reaches -RISK_DAILY_LOSS_CAP_PCT of the day-open
# equity, all new entries blocked until the next UTC date rollover.
RISK_DAILY_LOSS_CAP_PCT          = 2.0
# When equity falls more than RISK_WEEKLY_DD_HALVE_PCT below the week's high
# water mark, halve sizing on new entries (does not block).
RISK_WEEKLY_DD_HALVE_PCT         = 4.0
# Hard cap on simultaneous open legs across all pairs.
RISK_MAX_CONCURRENT_LEGS         = 2
# Pairs in the same group share a total-risk budget. EUR/GBP are ~85%
# correlated; treating them as one position for sizing purposes prevents
# accidentally taking double-exposure on a USD move.
RISK_CORRELATED_GROUPS           = (("EURUSD", "GBPUSD"),)
# Maximum total risk-pct that may be open simultaneously across a correlated
# group. 1.0 means "one full-size leg's worth across the group".
RISK_CORRELATED_GROUP_RISK_CAP_PCT = 1.0
# Smallest risk-pct we'll bother placing (anything smaller becomes a veto).
RISK_MIN_RISK_PCT                = 0.25
