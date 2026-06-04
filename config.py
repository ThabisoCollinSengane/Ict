"""Strategy parameters. Tweak here, no other code changes needed."""

# --- Capital + risk ---
STARTING_CASH = 500                # R500 ZAR starting capital
ACCOUNT_CURRENCY = "ZAR"          # account denomination
USD_ZAR = 18.5                    # fixed conversion — approximate 2022-2025 mid-rate
RISK_PER_TRADE_PCT = 1.0           # % of equity risked per leg (used when above minimum)
# Max-risk-per-trade guard: at small equity the broker min-lot floor (0.01) overrides
# the 1% risk sizing, so a wide structural stop can risk 10%+ in a single trade. Skip
# any setup whose floor-lot risk exceeds this % of current equity — the cap self-lifts
# as the account grows. Set to a high value (e.g. 100) to disable.
MAX_RISK_PER_TRADE_PCT = 8.0
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
PYRAMID_LOTS    = (0.02, 0.02, 0.02)    # flat — same lot on every leg
MIN_LOT_SIZE    = PYRAMID_LOTS[0]

# Equity tiers — all legs stay equal; only the lot size grows with the account.
# Format: (min_equity_ZAR, (leg1_lots, leg2_lots, leg3_lots))
#
#   R0    → 0.01 flat  — full pyramid win R166  on 40-pip trade  (3.7% risk at R500)
#   R750  → 0.02 flat  — full pyramid win R333  on 40-pip trade  (4.4% risk at R750)
#   R1500 → 0.03 flat  — full pyramid win R499  on 40-pip trade  (3.3% risk at R1500)
#   R3000 → 0.05 flat  — full pyramid win R832  on 40-pip trade
#   R6000 → 0.10 flat  — full pyramid win R1665 on 40-pip trade
EQUITY_TIERS = [
    (6_000, (0.10, 0.10, 0.10)),
    (3_000, (0.05, 0.05, 0.05)),
    (1_500, (0.03, 0.03, 0.03)),
    (750,   (0.02, 0.02, 0.02)),
    (0,     (0.01, 0.01, 0.01)),
]

# --- Targets ---
MIN_CONVICTION = 6                 # minimum conviction score to open a trade (0–9+ scale)
# Draw-weighted position sizing: the HTF draw cascade (0-3) is the strongest edge
# predictor (PF by bucket: 0/3≈1.2, 1/3≈3.2, 2/3≈4.1, 3/3≈6.2). Scale position
# size by how many of Weekly/Daily/H4 agree with the draw, concentrating capital
# in the highest-edge setups. The MAX_RISK_PER_TRADE_PCT guard still bounds the tail.
DRAW_SIZE_MULT = {0: 1.0, 1: 1.0, 2: 2.0, 3: 3.0}
# Draw-weighted sizing only engages once equity can absorb the larger position.
# Below this the account trades flat lots (preservation): the early small-account
# phase is where 2x sizing produced the deepest drawdowns.
DRAW_SIZE_MIN_EQUITY = 3000        # ZAR equity floor before draw multipliers apply
MIN_PIPS_TARGET = 20               # minimum pips to target (entry and pyramid checks)
MIN_ENTRY_PIPS_TARGET = 20         # same as MIN_PIPS_TARGET — keep them in sync here
MIN_RR = 1.2                       # minimum reward:risk
FIXED_STOP_PIPS = 10               # max/fallback stop distance — 10 pips from entry
TRAIL_BE_PIPS   = 10               # move stop to breakeven when +10 pips profit
TRAIL_LOCK_PIPS = 20               # lock in +10 pips profit when +20 pips profit
# Structure trailing: once a trade is in profit, trail the stop behind the most
# recent confirmed M5 swing point (the "manual trail off structure"). The trade
# stays open until price breaks that structural point (an MSS against the
# position), letting winners run to deep fib extensions instead of capping at the
# first target. The fixed target becomes a soft objective, not a hard exit.
STRUCTURE_TRAIL          = False   # disabled — pure fib target has highest compounded return
STRUCTURE_TRAIL_TF       = "15T"   # timeframe whose swings define the trail (M5 too fine)
STRUCTURE_TRAIL_ACTIVATE = 12      # pips of profit before structure trail engages
STRUCTURE_TRAIL_LOOKBACK = 8       # swing-TF bars to scan for the most recent swing
STRUCTURE_TRAIL_BUFFER   = 2.0     # pips beyond the swing point for the trail stop
STRUCTURE_TRAIL_LET_RUN  = True    # don't hard-close at target; let structure trail govern
# M1 market-structure stop: the stop is anchored to the nearest 1-minute swing
# (STL for longs / STH for shorts) plus this buffer. Episode 12 — stop sits just
# beyond the short-term structural point. M1 keeps it naturally tight (a few pips).
# Entries still come from M5/M15/H1; M1 is used ONLY for stop placement.
M1_STOP_BUFFER_PIPS = 1.0          # pips beyond the M1 swing point
M1_STOP_MIN_PIPS    = 4.0          # floor — don't place a stop tighter than this (noise)
M1_STOP_LOOKBACK    = 30           # M1 bars to scan for the nearest swing

# --- Account protection (wipeout prevention) ---
# 1. Peak drawdown halt: if equity falls >20% from its highest point, stop trading
#    for DRAWDOWN_PAUSE_DAYS calendar days before retrying. Prevents cascading losses
#    in trending-against conditions.
MAX_DRAWDOWN_HALT_PCT   = 15.0    # halt earlier — 20% was allowing too much cascade loss
DRAWDOWN_PAUSE_DAYS     = 10      # 2-week break outlasts most short-term adverse regimes
# 2. Daily loss cap: stop opening new trades for the rest of the calendar day once
#    daily losses exceed this % of the account equity at day open.
MAX_DAILY_LOSS_PCT      = 6.0     # ~2 full stop-losses at 0.03 lots
# 3. Consecutive loss pause: after N straight losses, sit out the rest of the day.
#    Counter resets automatically at the start of each new trading day.
MAX_CONSECUTIVE_LOSSES  = 5

# --- Trade frequency — no weekly cap; take every valid setup ---
# Protection comes from conviction score, daily cap, and circuit breakers only.
MAX_TRADES_PER_DAY       = 3     # max new entries per calendar day (UTC)
MAX_PAIR_TRADES_PER_DAY  = 1     # max 1 initial entry per pair per UTC day
MAX_PAIR_TRADES_PER_WEEK = 999   # effectively unlimited per-pair weekly entries

# --- NY session overrides ---
# NY AM gets its own daily entry slot (separate from London) so a London trade
# on the same pair doesn't block the NY continuation or reversal.
MIN_CONVICTION_NY        = 5   # lower gate: NY needs fewer confirms than London
MAX_PAIR_TRADES_PER_DAY_NY = 1   # max NY initial entries per pair per UTC day

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
# CPI/NFP/FOMC create 20-40+ pip Judas spikes that always blow through a 10-pip stop.
# These are blocked entirely (like Medium). All other High-impact events are allowed
# with the normal 10-pip stop + widened news spread.
CRITICAL_NEWS_EVENTS: frozenset = frozenset({"CPI", "NFP", "FOMC"})
# During high-impact news the broker spread typically widens to 4-6 pips.
# This is applied to entry friction AND exit friction on stop-outs during news
# windows, so the backtest reflects the realistic ~15-pip worst case (10-pip
# stop + widened spread) rather than the optimistic ~10.75 pips.
NEWS_HIGH_SPREAD_PIPS = 5.0

# --- Timeframes ---
LTF_ENTRY_RES_MIN = 5              # 5m execution
LTF_SETUP_RES_MIN = 15             # 15m setup (sweep + displacement)
HTF_BIAS_RES_MIN  = 60             # 1H bias
# Targets are searched across H4, Daily, Weekly; nearest viable wins.
TARGET_TF_MINUTES = (240, 1440, 10080)

# --- Entry pattern block list ---
# Patterns to never trade as initial entries (confirmed losers from backtest).
# breaker_m15 had only 2 sample trades on the old reactive-entry system.
# With anticipatory limit entries we collect a fresh sample — cleared for now.
BLOCKED_ENTRY_PATTERNS: frozenset = frozenset()

# Block pyramid adds when intermarket score is neutral (im_score=0.5, direction unclear).
# Backtest: 5 pyramid_im0.5 trades → 0W/5L, -R740. No edge; skip neutral-conviction adds.
BLOCK_NEUTRAL_PYRAMID = True

# Require confirmed weekly AMD direction before any pyramid add.
# When True, pyramids are only allowed if the weekly AMD sweep already fired
# in the same direction as the trade — eliminates mid-week guessing.
PYRAMID_REQUIRE_WEEKLY_AMD = False

# Minimum pips in favour of the last leg before adding a pyramid leg.
# Higher values give more confirmation; lower values catch earlier in the move.
PYRAMID_MIN_FAVOUR_PIPS = 20

# --- Structure lookbacks ---
SWING_LOOKBACK = 20                # bars to define swing high/low for BOS
EQ_HIGH_LOW_TOLERANCE_PIPS = 5     # max pip diff to call two highs "equal"
FVG_MIN_SIZE_PIPS = 3              # ignore micro FVGs
OB_LOOKBACK_BARS = 200             # how far back on HTF to scan for unmitigated OB

# --- HTF FVG 50% draw-on-liquidity conviction (P9) ---
# Unmitigated H4/D1/W1 FVGs are the bigger-timeframe draw on liquidity.
# Continuation moves deliver INTO the gap and consolidate at ~50% (its
# equilibrium) before continuing — the natural HTF Accumulation anchor for the
# next AMD cycle. When price sits within this tolerance of an unmitigated HTF
# FVG midpoint whose direction matches the trade, award +1 conviction.
HTF_FVG_MID_TOLERANCE_PIPS = 10    # how close to the 50% level counts as "at equilibrium"
HTF_FVG_SCAN_BARS          = 80    # how many recent HTF bars to scan for FVGs per TF
# Sizing multiplier when a breakout/continuation is anchored at an HTF FVG 50%.
# Applied on top of any draw-cascade multiplier; same equity floor applies.
# A continuation at the gap's equilibrium is the highest-conviction setup — the
# HTF draw is the target, the AMD cycle confirms the timing.
HTF_FVG_BREAKOUT_MULT      = 2.0
# Reversal filter: if an unmitigated HTF FVG exists in the opposing direction
# (i.e., a draw that price hasn't yet delivered to), the Judas reversal is
# fighting the HTF delivery — skip it. Gate only applies to reversals, not
# breakout continuations (which run WITH the draw).
HTF_FVG_REVERSAL_FILTER    = False   # REVERTED — hard gate disrupts compounding path
# A hard reversal gate passes per-split MaxDD validation (-12.95% IS, -13.47% OOS)
# but the full 4yr continuous run hits -20.15% MaxDD (hard fail). Same path-dependency
# trap as P8: trades removed by the gate are winners at high-equity that buffer later
# drawdowns. The opposing-FVG signal is retained as an analytics tag (future use).
HTF_FVG_OPPOSING_MAX_PIPS  = 80

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

# --- Breakout (continuation) model ---
# The inverse of the Judas sweep. After a consolidation, a genuine multi-pair
# breakout means price CLOSES beyond a range extreme by at least BREAKOUT_HOLD_PIPS
# and holds, rather than sweeping and rejecting back inside. Validated by the
# intermarket triple-confirmation (EURUSD + GBPUSD + DXY all break in agreement) —
# a single-pair breakout is usually a fakeout/Judas; three together is real
# USD-driven expansion. Breakout trades are continuation (follow the break) and are
# therefore exempted from the inverted-draw 0/3 hard gate (which is reversal logic).
BREAKOUT_MODEL_ENABLED = True
BREAKOUT_HOLD_PIPS     = 3.0       # min close beyond the range extreme to call it a hold
BREAKOUT_CONVICTION    = 2         # conviction credit when the intermarket breakout confirms

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

# --- Spread + slippage simulation ---
# Applied to every fill in backtest to model realistic execution friction.
# Spread = broker bid/ask spread (you pay half on entry, half on exit = full round-trip).
# Slippage = market-impact / execution lag on market orders (entry only).
PAIR_SPREAD_PIPS = {
    "EURUSD": 0.8,
    "GBPUSD": 1.0,
    "NZDUSD": 1.5,
    "default": 1.0,
}
SLIPPAGE_PIPS = 0.5          # one-way slippage on market order entries

# --- Drawdown kill switch (live hard stop) ---
# In addition to the rolling MAX_DRAWDOWN_HALT_PCT (which pauses and resumes),
# a SESSION_DRAWDOWN_PCT breach closes all open positions and halts the algorithm
# for the remainder of the day — no automatic resume.  Set to 0 to disable.
SESSION_DRAWDOWN_PCT = 10.0  # halt day if session equity falls >10% from session open

# --- Symbols ---
PAIRS = ("GBPUSD", "EURUSD", "NZDUSD")   # tradeable (AUDUSD excluded: poor Asian WR)
REF_EURGBP = "EURGBP"              # EUR vs GBP relative strength
REF_AUDNZD = "AUDNZD"              # AUDNZD data (loaded for AUDUSD MSS bars; not used as bias signal)
# DXY synthetic uses these (all available on OANDA):
DXY_CONSTITUENTS = ("EURUSD", "USDJPY", "GBPUSD", "USDCAD", "USDSEK", "USDCHF")

# --- Individual pair bias (synthetic EURGBP from EURUSD vs GBPUSD momentum) ---
# When EURGBP is flat at both H1 and H4, compare which USD pair moved more over
# EURGBP_SYNTHETIC_LOOKBACK H1 bars. If the divergence exceeds the threshold,
# the more-moved pair determines the synthetic EURGBP direction.
EURGBP_SYNTHETIC_LOOKBACK         = 6    # H1 bars to look back
EURGBP_SYNTHETIC_THRESHOLD_PIPS   = 10   # minimum divergence (pips) to fire
