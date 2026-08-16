"""Strategy parameters. Tweak here, no other code changes needed."""

import os as _os


def _envf(name, default):
    """Tolerant float env read: strips whitespace + any trailing inline comment
    (e.g. a shell '#value' glued on by a missing space), falls back to default on
    a bad value. Prevents one bad env var from crashing the whole config import
    (which would take the live bot down too)."""
    v = _os.environ.get(name)
    if v is None:
        return float(default)
    try:
        return float(v.split("#", 1)[0].strip())
    except (ValueError, AttributeError):
        return float(default)


def _envi(name, default):
    return int(_envf(name, default))


# --- Capital + risk ---
STARTING_CASH = _envi("STARTING_CASH", 500)   # ZAR starting capital (env-overridable)
ACCOUNT_CURRENCY = "ZAR"          # account denomination

# --- Profit withdrawal model (realistic account, no runaway compounding) ---
# When the working balance reaches WITHDRAW_AT, cash out everything above
# WITHDRAW_KEEP (i.e. bank the profit) and keep trading from WITHDRAW_KEEP. This
# keeps position sizing, growth AND drawdowns realistic instead of compounding to
# hundreds of millions. Money withdrawn is tracked separately; the reported MaxDD
# is on the TOTAL-value curve (working + withdrawn) so a withdrawal never shows as
# a drawdown. WITHDRAW_AT=0 disables it (byte-identical baseline).
#   e.g. WITHDRAW_AT=20000 WITHDRAW_KEEP=500  -> grow 500->20k, bank ~19.5k, repeat.
WITHDRAW_AT   = _envf("WITHDRAW_AT", 0)          # ceiling; 0 = off
WITHDRAW_KEEP = _envf("WITHDRAW_KEEP", STARTING_CASH)  # initial keep-working level
# Fraction of each cycle's profit to actually WITHDRAW (income); the rest is
# reinvested — the keep-level and ceiling ratchet UP by the reinvested amount, so
# the working base compounds while you still draw income. 1.0 = withdraw everything
# above keep (fixed base, steady income, no compounding of the base). 0.6 = draw
# 60%, compound 40% — "make ends meet AND grow". Only active when WITHDRAW_AT>0.
WITHDRAW_FRACTION = _envf("WITHDRAW_FRACTION", 1.0)

# --- Scheduled (calendar) withdrawal cadence ---
# The realistic income model: withdraw on a SCHEDULE, and the frequency steps up as
# the working base grows — monthly while small, twice a month once it's built,
# weekly when it's big. Each scheduled withdrawal banks WITHDRAW_FRACTION of the
# profit above the keep-level and reinvests the rest (so the base compounds and the
# cadence can climb). Uses WITHDRAW_KEEP as the initial working base. Enable with
# WITHDRAW_SCHEDULE=1 (this then OWNS withdrawals — the ceiling trigger is off).
WITHDRAW_SCHEDULE      = bool(_envi("WITHDRAW_SCHEDULE", 0))
WITHDRAW_MONTHLY_DAYS  = _envi("WITHDRAW_MONTHLY_DAYS", 30)   # cadence when small
WITHDRAW_BIWEEKLY_DAYS = _envi("WITHDRAW_BIWEEKLY_DAYS", 14)
WITHDRAW_WEEKLY_DAYS   = _envi("WITHDRAW_WEEKLY_DAYS", 7)
WITHDRAW_BIWEEKLY_AT   = _envf("WITHDRAW_BIWEEKLY_AT", 10_000)  # (legacy tier)
WITHDRAW_WEEKLY_AT     = _envf("WITHDRAW_WEEKLY_AT", 30_000)    # (legacy tier)
# R10k-band cadence: withdrawals START once the account reaches the keep-level
# (set WITHDRAW_KEEP=10000), then every additional R10k BAND the account reaches
# makes withdrawals MORE FREQUENT (interval = MONTHLY_DAYS / band, floored at
# WEEKLY_DAYS) AND larger (a fraction of a bigger base). Evenly distributed at a
# regular interval within each band. band = floor(equity / WITHDRAW_BAND).
WITHDRAW_BAND          = _envf("WITHDRAW_BAND", 10_000)
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
MIN_PIPS_TARGET = int(_os.environ.get("MIN_PIPS_TARGET", 30))  # min pips to target (30: higher PF + lower DD, user pref)
MIN_ENTRY_PIPS_TARGET = MIN_PIPS_TARGET   # kept in sync with MIN_PIPS_TARGET
# Equity-scaled target floor (OFF by default). The 20-vs-30 validation showed 20
# wins the small-account phase (more frequent hits = compounding fuel below R3k)
# while 30 wins the large-account phase (higher PF, lower DD). This uses the small
# floor below the R3k multiplier threshold (DRAW_SIZE_MIN_EQUITY) and the large
# floor above it — best-of-both, if it validates. OFF → flat MIN_PIPS_TARGET (30).
MIN_TARGET_SCALED     = bool(int(_os.environ.get("MIN_TARGET_SCALED", 0)))
MIN_PIPS_TARGET_SMALL = int(_os.environ.get("MIN_PIPS_TARGET_SMALL", 20))
MIN_PIPS_TARGET_LARGE = int(_os.environ.get("MIN_PIPS_TARGET_LARGE", 30))
MIN_RR = 1.2                       # minimum reward:risk
FIXED_STOP_PIPS = 10               # max/fallback stop distance — 10 pips from entry
TRAIL_BE_PIPS   = 10               # move stop to breakeven when +10 pips profit
TRAIL_LOCK_PIPS = 20               # lock in +10 pips profit when +20 pips profit

# Milestone trailing stop: extends the TRAIL_LOCK step continuously for long HTF-
# target trades.  Every MILESTONE_TRAIL_STEP pips of progress, the stop is locked
# at (milestone - MILESTONE_TRAIL_BUFFER) pips from entry.  Kicks in after +20 pips
# (TRAIL_LOCK already handles the first step); from +40 pips onward this governs.
#   +40 pips → stop at entry + 30   +60 → entry + 50   +80 → entry + 70  etc.
# When the main target is a short fib-extension (20-30 pips) the trade exits before
# any new milestone fires — no behaviour change on short-target trades.
MILESTONE_TRAIL_ENABLED = bool(int(_os.environ.get("MILESTONE_TRAIL_ENABLED", 1)))
MILESTONE_TRAIL_STEP    = int(_os.environ.get("MILESTONE_TRAIL_STEP",   20))
MILESTONE_TRAIL_BUFFER  = int(_os.environ.get("MILESTONE_TRAIL_BUFFER", 5))

# Semi-auto structure trail (live only, opt-in per pair via Telegram /trail).
# Follows the latest intact fractal swing on M15/M5/M1 (STH/STL or ITH/ITL),
# keeping a trader-set pip buffer; only ever tightens. Backtest is unaffected
# (the live layer reads it; the backtester never sets a /trail).
STRUCT_TRAIL_LOOKBACK       = int(_os.environ.get("STRUCT_TRAIL_LOOKBACK", 200))
STRUCT_TRAIL_DEFAULT_BUFFER = float(_os.environ.get("STRUCT_TRAIL_DEFAULT_BUFFER", 2))

# NWOG — New Week Opening Gap (the weekend gap between last week's Friday daily
# close and this week's Monday daily open). An ICT higher-timeframe PD array:
# price is drawn to its 50% midpoint (consequent encroachment) and the gap acts
# as support/resistance. Wired as (a) a confluence/target source family ("nwog")
# and (b) a +NWOG_CONVICTION_PTS conviction add when price sits at the NWOG CE
# aligned with the trade (gap-up NWOG supports longs, gap-down supports shorts).
# NWOG_ENABLED=0 makes the engine byte-identical to the pre-NWOG baseline.
# VALIDATED 🔴 RED (commit e3b24ed, true 4yr + IS/OOS): WR/PF/MaxDD byte-identical
# to baseline in all three splits (44.9% / 4.95 / -12.76%), equity fractionally
# DOWN everywhere (full -1.4%, IS -0.6%, OOS -0.5%); only 26 CE-hits/4yr. The +1
# conviction is saturation-inert (like P9/P15/P16/P19) and the confluence-source
# nudge to P18 sizing costs a hair. A real ICT concept, no tradeable edge here.
# DEFAULT OFF. Set NWOG_ENABLED=1 to re-measure; code retained for reference.
NWOG_ENABLED            = bool(int(_os.environ.get("NWOG_ENABLED", 0)))
NWOG_MID_TOLERANCE_PIPS = float(_os.environ.get("NWOG_MID_TOLERANCE_PIPS", 10))
NWOG_CONVICTION_PTS     = int(_os.environ.get("NWOG_CONVICTION_PTS", 1))

# HTF draw preference: when an unswept ITH/ITL, PDH/PDL, or PWH/PWL is within
# this many pips, prefer it over a closer fib extension as the primary target.
# These are RESTING LIQUIDITY pools (actual institutional destination); fib
# extensions are projected levels.  Set 0 to disable.
HTF_TARGET_PREF_PIPS = int(_os.environ.get("HTF_TARGET_PREF_PIPS", 0))  # off by default — tested, reverted (WR drop + MaxDD -22%)
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
# Ep 12 structural stop: anchor the stop beyond the intact M1 INTERMEDIATE swing
# (ITL/ITH) instead of the raw short-term extreme (STL/STH). The short-term swing
# is exactly what a minor liquidity run sweeps — placing the stop one fractal tier
# up (at the ITL/ITH that survives the sweep) avoids being stopped on the Judas.
# Naturally bounded by the 10-pip universal cap ("if 10 pips permit"). When no
# intact intermediate swing exists within the cap, falls back to the M1 STL/STH.
STRUCTURE_STOP_ENABLED = True     # A/B toggle — validate on full continuous run
STRUCTURE_STOP_TF      = "1T"      # timeframe whose fractal ITL/ITH anchors the stop
STRUCTURE_STOP_LOOKBACK = 90       # bars to scan for the intermediate swing

# --- Structure-based entry trigger (Ep-12 "read HTF, enter LTF") — OPTIONAL ---
# After the HTF read + 2-of-3 MSS confirm the ITH/ITL, require a freshly-confirmed
# lower-TF fractal REVERSAL swing in the trade direction before entering — the
# trader's "anticipate the STL/STH forming and enter on it, the moment its 3rd bar
# prints" model. LONG needs a confirmed, still-intact Short-Term LOW (STL); SHORT a
# Short-Term HIGH (STH). This makes the entry literally the swing formation rather
# than the FVG/OB alone. Default OFF -> baseline byte-identical; validate full + IS/OOS.
STRUCTURE_ENTRY_ENABLED  = int(_os.environ.get("STRUCTURE_ENTRY_ENABLED", "0"))
STRUCTURE_ENTRY_TF       = _os.environ.get("STRUCTURE_ENTRY_TF", "5T")   # LTF for the swing
STRUCTURE_ENTRY_LOOKBACK = int(_os.environ.get("STRUCTURE_ENTRY_LOOKBACK", "60"))
STRUCTURE_ENTRY_MAX_AGE  = int(_os.environ.get("STRUCTURE_ENTRY_MAX_AGE", "3"))  # bars since 3rd bar printed

# --- Telegram access sharing (optional; comma/;-separated chat ids) ---
# Owner = TELEGRAM_CHAT_ID (full). ADMIN_IDS get full control too; VIEWER_IDS get
# read-only (/read /positions /account ...). Empty = owner-only (default).
TELEGRAM_ADMIN_IDS  = _os.environ.get("TELEGRAM_ADMIN_IDS", "")
TELEGRAM_VIEWER_IDS = _os.environ.get("TELEGRAM_VIEWER_IDS", "")
# 1 = ANYONE who messages the bot gets READ-ONLY access automatically (no id setup)
# — so you can just share the bot link. Trading control still needs ADMIN ids.
TELEGRAM_OPEN_VIEW  = int(_os.environ.get("TELEGRAM_OPEN_VIEW", "0"))

# --- Account protection (wipeout prevention) ---
# 1. Peak drawdown halt: if equity falls >MAX_DRAWDOWN_HALT_PCT% from its highest
#    point, stop trading for DRAWDOWN_PAUSE_DAYS calendar days before retrying.
#
#    Growth-phase override (equity < GROWTH_PHASE_EQUITY):
#    The % breaker is too tight at small equity — a normal 2-trade losing run from
#    R500 peak can exceed -15% (R75 down). During growth, use a hard ZAR floor
#    instead: halt only when equity drops to GROWTH_PHASE_FLOOR_ZAR (half of
#    starting capital). Normal % breaker resumes once equity >= GROWTH_PHASE_EQUITY.
MAX_DRAWDOWN_HALT_PCT   = 15.0    # normal phase: -15% from peak → 10-day pause
DRAWDOWN_PAUSE_DAYS     = 10      # 2-week break outlasts most short-term adverse regimes
GROWTH_PHASE_EQUITY     = 3_000   # ZAR — below this the growth-phase floor applies
GROWTH_PHASE_FLOOR_ZAR  = _envf("GROWTH_PHASE_FLOOR_ZAR", STARTING_CASH / 2)  # half of funding
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
MAX_PAIR_TRADES_PER_DAY_PM = 1   # max PM initial entries per pair per UTC day

# --- Killzones (New York time, 24h) ---
KILLZONES = [
    ("London Open",  "03:00", "05:00"),
    ("New York AM",  "07:00", "10:00"),
]
# NY afternoon session — analytics-first, default OFF until IS/OOS validated.
# PM character: position squaring, mean-reversion, Fedwire close flow (13:30-16:00 ET).
# Smaller banks and Tier 2 participants are the dominant flow (CLS funding done, London closed).
NY_PM_ENABLED   = False
NY_PM_KILLZONE  = ("New York PM", "13:30", "16:00")

# Oceanic currencies (AUD, NZD) peak during Asian session, not London/NY.
AUD_NZD_KILLZONES = [
    ("Asian Open",  "20:00", "22:00"),   # Sydney open
    ("Tokyo Kill",  "23:00", "01:00"),   # Tokyo volume peak
]
NO_NEW_TRADES_LAST_MIN = 15        # skip new entries in final N min of a killzone

# --- Target confluence scoring ---
# When multiple independent sources (fib extension, FVG, equal high/low, OB, round
# number, PDH/PDL, PWH/PWL) agree on the same TP level, that level is magnetically
# stronger — price is far more likely to reach it. Score each candidate by confluence
# count and prefer the highest-scoring TP. Score adds directly to conviction →
# more pyramid legs unlocked for high-confluence targets.
TARGET_CONFLUENCE_TOL_PIPS = 8   # pips tolerance for two sources to be "at same level"
# When the chosen TP has score≥threshold (fib + ITH/ITL + FVG/OB agreeing at same price),
# scale up the position. Same equity floor as draw-cascade (DRAW_SIZE_MIN_EQUITY).
# Mirrors P9's 1.25× HTF FVG multiplier logic. Set to 1.0 to disable.
# Env-overridable for sweeps: TARGET_SCORE_MULT / TARGET_SCORE_MULT_THRESHOLD.
TARGET_SCORE_MULT           = float(_os.environ.get("TARGET_SCORE_MULT", 1.25))
TARGET_SCORE_MULT_THRESHOLD = int(_os.environ.get("TARGET_SCORE_MULT_THRESHOLD", 4))
# P20 — high-conviction target escalation.
# When strong confluence signals fire (CRT-D/W, draw≥2, Judas minor sweep), skip raw
# swing / round-number targets and require a structural liquidity draw (ITH/ITL,
# PDH/PDL, PWH/PWL, FVG, OB, fib) to be available.  Falls back to the full candidate
# list if no premium target clears the RR floor — so this is strictly additive.
TARGET_ESCALATE_ENABLED  = bool(int(_os.environ.get("TARGET_ESCALATE_ENABLED", 1)))
TARGET_ESCALATE_MIN_DRAW = int(_os.environ.get("TARGET_ESCALATE_MIN_DRAW", 2))
# Timeframes that contribute unswept ITH/ITL target candidates (P17). Default H4/D/W
# (full history — the edge is in older major intermediate highs/lows). Empty tuple =
# none (pure P16 target set). Env override: ITHL_TARGET_TFS="240T,D,W" (comma-separated).
# Do NOT add 15T/60T without also setting ITHL_TARGET_MAX_BARS (those series are ~100k
# bars — uncapped classify dominates runtime — and they hurt PnL by ~R10M in testing).
ITHL_TARGET_TFS = tuple(
    _tf for _tf in _os.environ.get("ITHL_TARGET_TFS", "240T,D,W").split(",") if _tf
)
# Lookback cap (bars) for ITH/ITL target scanning. 0 = full history (correct for H4/D/W).
# Set >0 only if including large intraday TFs (15T/60T) to bound runtime.
ITHL_TARGET_MAX_BARS = int(_os.environ.get("ITHL_TARGET_MAX_BARS", 0))

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
NEWS_CURRENCIES = ("USD", "EUR", "GBP", "NZD")
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

# Minimum draw_score for the im_score=0.75 unlock (DXY agrees, cross flat).
# Default 1: unlock when at least one HTF timeframe agrees — ICT rationale:
# DXY agreement + any HTF draw = sufficient conviction for a pyramid add.
# Backtest: 3→1 with favour=15: IS +3.5%, OOS flat, MaxDD unchanged (P22).
PYRAMID_DRAW_UNLOCK_MIN = int(_os.environ.get("PYRAMID_DRAW_UNLOCK_MIN", 1))

# Minimum pips in favour of the last leg before adding a pyramid leg.
# Higher values give more confirmation; lower values catch earlier in the move.
# Backtest: 20→15 with draw_unlock=1: IS +3.5%, OOS flat, MaxDD unchanged (P22).
PYRAMID_MIN_FAVOUR_PIPS = float(_os.environ.get("PYRAMID_MIN_FAVOUR_PIPS", 15))

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

# DXY level tracking (P13): DXY's own W/D/H4 FVGs reveal where the dollar has
# an undelivered HTF draw — room to run vs approaching a key opposing level.
# DXY pip = 0.001 (DXY trades ~100 scale with 3 decimal places).
DXY_FVG_MID_TOLERANCE_PIPS = 100  # 100 * 0.001 = 0.10 DXY points tolerance (≈10 EURUSD pips)
# Sizing multiplier when a breakout/continuation is anchored at an HTF FVG 50%.
# Applied on top of any draw-cascade multiplier; same equity floor applies.
# A continuation at the gap's equilibrium is the highest-conviction setup — the
# HTF draw is the target, the AMD cycle confirms the timing.
HTF_FVG_BREAKOUT_MULT      = 1.25
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

# --- HTF CRT Turtle Soup timing conviction (P19) ---
# ICT Candlestick Range Theory: the High/Low of a completed H4/D candle (or prior
# 2-bar range) define CRT H / CRT L. A "Turtle Soup" = price wicks BEYOND CRT H
# (for shorts) or below CRT L (for longs), then CLOSES BACK INSIDE — the same
# Judas sweep logic applied at the bigger timeframe. When this pattern fires on a
# H4 or Daily bar within the last 2-3 completed bars, the trade has HTF timing
# confluence: the manipulation phase already happened on the higher timeframe.
# D1 sweep = +2 conviction (bigger TF = stronger manipulation signal)
# H4 sweep = +1 conviction
CRT_SWEEP_ENABLED  = True
CRT_SWEEP_MIN_PIPS = 2.0   # minimum wick beyond CRT H/L to qualify as a genuine sweep
# Sizing multiplier for the H4-CRT-sweep bucket (P19 active lever). The H4 Turtle
# Soup is the highest-WR HTF-timing bucket (WR 50.4%, PF 3.40 IS / 3.80 OOS — both
# splits positive, same ballpark). Scale that bucket up the same way P9 (HTF-FVG)
# and P18 (score≥4 confluence) size their high-conviction buckets. Same equity floor
# (DRAW_SIZE_MIN_EQUITY). MUST be tuned against the FULL continuous 4yr run, not
# per-split — size bumps amplify tail risk on the compounding path (P9 2.0× lesson).
# 1.0 = no-op (analytics only); >1.0 = active lever. CRT_SWEEP_MULT_TF picks which
# sweep timeframe earns the bump ("240T" = H4 only; the D1 bucket is weaker).
CRT_SWEEP_MULT     = float(_os.environ.get("CRT_SWEEP_MULT", "1.25"))
CRT_SWEEP_MULT_TF  = "240T"   # H4 CRT sweep is the lever; D1 bucket excluded

# --- PDH/PDL-sweep sizing lever (price-based; OFF by default) ---
# When the AMD manipulation swept prior-day liquidity (within ~5 pips of PDH/PDL)
# the raid hit a genuine resting-liquidity pool — the setup-quality bucket that
# held WR 55% (2022) / 53% (2024) above the ~45% baseline in BOTH years
# (data/amd_tickvol_report.md §9). Price-based (no tick data) so it applies to all
# pairs/years. Same 1.25× magnitude + R3k floor (DRAW_SIZE_MIN_EQUITY) as P18/P19.
# 1.0 = no-op; 1.25 = active. SHIPPED ON after run_pdliq_validation.sh passed the
# full + IS/OOS gate (equity up in all three, PF flat, MaxDD held to the decimal).
PDLIQ_SWEEP_MULT   = float(_os.environ.get("PDLIQ_SWEEP_MULT", "1.25"))

# --- Market Maker model: IFVG continuation to opposing liquidity (OFF by default) ---
# The distribution leg. After the Judas sweep + reversal (which the strategy already
# trades), price delivers to the OPPOSING liquidity pool, retracing into inversion
# FVGs (IFVGs) along the way — each a re-entry / pyramid add on the M15→M5→M1 cascade.
# This is what the base strategy does NOT do: it fades the sweep once and exits at the
# nearest draw, instead of riding the distribution to the far pool via IFVG re-entries.
# Distinct from the reverted far-target holds (HTF_TARGET_PREF/TRAIL_AT_TP/TP_RUNNER):
# those held ONE position through the consolidation; this BANKS and re-enters on a
# fresh IFVG + M1 structure shift, so it's flat during the chop. Default OFF and
# byte-identical when off (the loop hook returns immediately). Validate IS/OOS + full
# 4yr with run_mm_validation.py before shipping — MaxDD must hold.
MM_CONTINUATION_ENABLED = bool(int(_os.environ.get("MM_CONTINUATION_ENABLED", 0)))
def _mm_tf_tuple(_name, _default):
    _v = _os.environ.get(_name)
    return tuple(x.strip() for x in _v.split(",") if x.strip()) if _v else _default

# FVG hunt cascade, HIGHEST → lowest. We take the FIRST (highest) TF that has an
# FVG; its inversion (full-body close) is judged on that TF AND the next-lower one.
# Env-overridable (comma-separated) — the winner-profile study showed W1/D1 IFVG
# adds are the big losers (tight M5 stop vs a weekly/daily-scale draw), so excluding
# them (MM_IFVG_TFS=240T,60T,30T,20T,15T,10T,5T) is the first filter to test.
MM_IFVG_TFS         = _mm_tf_tuple("MM_IFVG_TFS",
                                   ("W", "D", "240T", "60T", "30T", "20T", "15T", "10T", "5T", "1T"))
# SMT cascade (the reversal confirmation), HIGHEST → lowest.
MM_SMT_TFS          = ("D", "240T", "60T", "30T", "15T", "5T", "1T")
# Extra intraday rungs that aren't in the base resample set (M5→30/20/10min). Built
# ONLY when MM is enabled, so the default backtester is byte-identical.
MM_EXTRA_TFS        = (("30T", "30min"), ("20T", "20min"), ("10T", "10min"))
# CRITICAL — the retracement swing scales with the IFVG timeframe. A W1/D1 IFVG's
# reversal swing forms on H4/H1 (close + relevant to the gap), NOT on M1. Hunting the
# swing at M1 for an HTF gap reads noise and ruins the model. Map: IFVG-TF → the TF(s)
# the retracement swing (high/low) must form on. The ENTRY + stop are then placed on
# MM_ENTRY_TF (M1) — the small TFs are used ONLY for entry precision / risk, never for
# the swing read.
MM_SWING_TF_MAP     = {
    "W":    ("240T", "60T"),      # W1 IFVG  → H4/H1 swing
    "D":    ("240T", "60T"),      # D1 IFVG  → H4/H1 swing
    "240T": ("60T", "30T"),       # H4 IFVG  → H1/M30 swing
    "60T":  ("30T", "15T"),       # H1 IFVG  → M30/M15 swing
    "30T":  ("15T", "5T"),        # M30 IFVG → M15/M5 swing
    "20T":  ("15T", "5T"),        # M20 IFVG → M15/M5 swing
    "15T":  ("5T", "1T"),         # M15 IFVG → M5/M1 swing
    "10T":  ("5T", "1T"),         # M10 IFVG → M5/M1 swing
    "5T":   ("1T",),              # M5 IFVG  → M1 swing
    "1T":   ("1T",),              # M1 IFVG  → M1 swing
}
# Entry PD-array cascade: START on M15, drop to M5 then M1. The entry must be a PD
# array (FVG / OB / breaker) that forms INSIDE the IFVG gap; the small TFs are entry
# precision only. (Trader's rule: "start taking these fvg entries from the m15 tf".)
MM_ENTRY_TFS        = _mm_tf_tuple("MM_ENTRY_TFS", ("15T", "5T", "1T"))
# Stop is STRUCTURAL — placed just beyond the IFVG gap edge (the side an internal
# manipulation would sweep), NOT a flat FIXED_STOP_PIPS cap. Short → above the gap
# high; long → below the gap low; + MM_STOP_BUF_PIPS. This is the R-negativity fix:
# the old flat 10-pip stop ignored the gap and sat where the internal AMD manipulation
# sweeps it. MM_MAX_STOP_PIPS is a generous safety ceiling (the H4/H1/M30 gaps run
# ~10-20 pips; >10 is riskier but the structural stop above the last high is correct).
MM_STOP_BUF_PIPS    = float(_os.environ.get("MM_STOP_BUF_PIPS", "1.5"))
MM_MAX_STOP_PIPS    = float(_os.environ.get("MM_MAX_STOP_PIPS", "25"))
# Require an INTERNAL mini-AMD inside the gap before entry (the trader's core model):
# an internal short-term extreme AGAINST the trade is swept + closed back (the internal
# manipulation), THEN we enter with the stop just beyond THAT extreme — tight AND
# survivable, instead of the full gap-edge (which is too wide on >10-pip gaps and
# blew MaxDD to -38%). Default on for the MM paths. `MM_WIDE_GAP_PIPS` = the >10-pip
# threshold above which the gap is "riskier" and the internal-AMD stop is mandatory.
MM_REQUIRE_INTERNAL_AMD = bool(int(_os.environ.get("MM_REQUIRE_INTERNAL_AMD", 1)))
MM_WIDE_GAP_PIPS    = float(_os.environ.get("MM_WIDE_GAP_PIPS", "10"))
MM_IFVG_SCAN_BARS   = 120                 # bars per TF fed to the FVG scan
MM_MIN_FAVOUR_PIPS  = float(_os.environ.get("MM_MIN_FAVOUR_PIPS", "3"))
# Cap MM re-entry adds per position (0 = unlimited). The raw validation showed the
# adds cluster losses and deepen MaxDD; a low cap (1–2) limits that. Env-overridable.
MM_MAX_ADDS         = int(_os.environ.get("MM_MAX_ADDS", "0"))
# Require the parent trade's HTF draw cascade ≥ this for an MM add (winner study:
# draw_score=0 adds were 3% WR / near-total loss). 0 = no gate. Env-overridable.
MM_MIN_DRAW_SCORE   = int(_os.environ.get("MM_MIN_DRAW_SCORE", "0"))
# STANDALONE MM entry (OFF by default). The MM continuation above is a pyramid ADD —
# it only fires while a base position is open, so it's capped by the base strategy's
# ~4-trades/week frequency (why only ~14 fired over 4yr). This opens the MM model as
# its OWN trade using the EXTERNAL/INTERNAL range-liquidity model (ict.dealing_range):
# the dealing range's two swept extremes are EXTERNAL liquidity (ERL). When price takes
# out ONE external side (sweeps the DR high or low) and closes back inside — the Judas —
# it reverses to deliver toward INTERNAL liquidity (IRL: an FVG / the opposite half).
# Entry = a PD array in the correct premium/discount half (sell in premium after
# sweeping the high, buy in discount); DRAW/target = INTERNAL (nearest qualifying draw,
# clamped to the range equilibrium so it never overshoots the opposite external — the
# far-external target is the repeatedly-failed config). Not gated by MSS/consolidation/
# draw-cascade. Default OFF + validate — standalone gate-bypass entries have failed
# before (SOJ bypass -17%), so this must clear the same MaxDD gate before shipping.
MM_STANDALONE_ENABLED = bool(int(_os.environ.get("MM_STANDALONE_ENABLED", 0)))
MM_STANDALONE_MAX_PER_DAY = int(_os.environ.get("MM_STANDALONE_MAX_PER_DAY", "2"))
MM_SWEEP_LOOKBACK   = 96          # M5 bars scanned for the day's sweep (~8h session)
MM_SWEEP_MIN_PIPS   = 2.0         # wick must exceed the reference by this to count
MM_STANDALONE_TARGET_OPPOSING = bool(int(_os.environ.get("MM_STANDALONE_TARGET_OPPOSING", 0)))
# Size throttle for standalone MM entries (1.0 = full risk). The standalone edge is
# real but high-DD (MaxDD -23.9% at full size); with +354% equity headroom, sizing
# down is nearly free and drops DD roughly proportionally. Applied to the risk-based
# size, floored at the min lot.
MM_STANDALONE_SIZE_MULT = float(_os.environ.get("MM_STANDALONE_SIZE_MULT", "1.0"))
# De-correlate: EURUSD/GBPUSD/NZDUSD are all X/USD, so a single daily DOLLAR sweep
# opens the SAME direction on all of them — one dollar bet at 2-3x risk, the main
# driver of the clustered -23% DD (breakers + size throttle can't touch it; in the
# IS phase entries are already at min lot). When on (default 1), a standalone entry is
# blocked if a same-direction standalone position is already open on any pair — caps
# concurrent same-direction dollar exposure to one position. Works at min lot.
MM_STANDALONE_ONE_PER_DIR = bool(int(_os.environ.get("MM_STANDALONE_ONE_PER_DIR", 1)))
# Live semi-auto /mm: minutes between consecutive MM entries/adds on a pair (stops
# same-bar spam while the model is armed and persistently hunting the distribution).
MM_LIVE_COOLDOWN_MIN = _envi("MM_LIVE_COOLDOWN_MIN", 15)
MM_STRUCTURE_MAX_AGE = 4                  # retracement swing must be this fresh (bars of its TF)
# Escalate the position target to the opposing liquidity pool so the trade rides the
# full distribution (the "until reached" part). Kept a SEPARATE flag (default OFF) so
# validation can isolate the IFVG adds from the far-target change — the far-target
# change is the one that has repeatedly failed, so it's opt-in on top of the adds.
MM_TARGET_OPPOSING  = bool(int(_os.environ.get("MM_TARGET_OPPOSING", 0)))
MM_TARGET_TFS       = ("240T", "D", "W")  # where the opposing ITH/ITL pool is drawn from
# H1 EURUSD↔GBPUSD SMT divergence — the reversal confirmation that STARTS the model
# (one pair sweeps liquidity, the correlated pair fails to confirm). Tagged on every
# trade (htf_smt column); as a hard requirement for MM adds only when REQUIRED=1.
MM_HTF_SMT_TF       = "60T"
MM_HTF_SMT_LOOKBACK = 20
MM_HTF_SMT_REQUIRED = bool(int(_os.environ.get("MM_HTF_SMT_REQUIRED", 0)))

# --- Bonds/yields dollar-bias sizing lever (intermarket; OFF by default) ---
# US Treasury yields lead the dollar (higher yields -> USD bid). scripts/
# bonds_analysis.py measures whether a yield-structure confirmation of the trade's
# dollar direction adds edge, and (with --emit-bias) writes data/bond_bias.json:
# a per-date DGS10 intermediate-structure read (+1 dollar-bullish / -1 bearish /
# 0 flat). When enabled, a trade whose dollar direction (short a USD pair = dollar
# up) AGREES with the yield structure on its date is scaled BONDS_SIZE_MULT×, same
# 1.25× magnitude + R3k floor (DRAW_SIZE_MIN_EQUITY) as P18/P19/P41. Default OFF and
# byte-identical when off: the file is never read and the multiplier is a no-op
# (1.0). Flip on ONLY if run_bonds.sh returns GREEN and run_bonds_validation.sh
# passes the full + IS/OOS gate (equity up, PF flat, MaxDD held).
BONDS_BIAS_ENABLED = bool(int(_os.environ.get("BONDS_BIAS_ENABLED", 0)))
BONDS_SIZE_MULT    = float(_os.environ.get("BONDS_SIZE_MULT", "1.0"))
BONDS_BIAS_FILE    = _os.environ.get("BONDS_BIAS_FILE",
                                     _os.path.join("data", "bond_bias.json"))

# --- Draw-to-liquidity continuation entry (unswept PDH/PDL; OFF by default) ---
# The strategy is a Judas REVERSAL: wait for the sweep, fade it. This is the
# opposite thesis — open a CONTINUATION toward an UNSWEPT PDH/PDL (price is drawn
# to the resting pool) and exit AT the pool. Mechanically it's a targeted gate
# exemption: a draw_score==0 trade (which the inverted-draw 0/3 reversal gate
# normally kills) is let through ONLY when there is an unswept PDH/PDL in the trade
# direction within [MIN_PIPS_TARGET, DRAW_CONT_MAX_PIPS] — a NEAR pool (this cycle's
# draw), not a far one (the HTF_TARGET_PREF revert showed forcing far pools = -22%
# MaxDD). MSS 2-of-3 structure confirmation is still required. Tag entry_model=
# "draw_cont". OFF until run_drawcont_validation.sh clears the full + IS/OOS gate —
# strong negative prior (P11 NY_CONTINUATION_GATE_EXEMPT + SOJ-draw-bypass both
# reverted), so this must earn its way in.
DRAW_CONT_ENABLED  = bool(int(_os.environ.get("DRAW_CONT_ENABLED", 0)))
DRAW_CONT_MAX_PIPS = float(_os.environ.get("DRAW_CONT_MAX_PIPS", 60))

# --- P40 conditional-volume modulator (FVG/OB, tick-volume; OFF by default) ---
# Data-derived from data/amd_tickvol_report.md (both-year-consistent per §3-7):
# high-volume FVG entries lose more -> size down; high-volume OB entries win more
# -> size up. Only fires when tick volume is available (EU/GU 2022+2024 in the
# backtest; MT5 tick_volume live) — otherwise neutral 1.0x. MUST clear the full
# IS/OOS + MaxDD validation before it ships; OFF until then.
USE_CONDITIONAL_VOLUME = bool(int(_os.environ.get("USE_CONDITIONAL_VOLUME", 0)))
VOL_MOD_HIGH_RATIO = float(_os.environ.get("VOL_MOD_HIGH_RATIO", 1.2))  # "high volume" threshold
VOL_MOD_FVG_DOWN   = float(_os.environ.get("VOL_MOD_FVG_DOWN", 0.80))   # high-vol FVG -> -20%
VOL_MOD_OB_UP      = float(_os.environ.get("VOL_MOD_OB_UP", 1.15))      # high-vol OB  -> +15%
VOL_MOD_MIN        = float(_os.environ.get("VOL_MOD_MIN", 0.70))
VOL_MOD_MAX        = float(_os.environ.get("VOL_MOD_MAX", 1.25))

# --- London-Judas priority (P10): size down the same-day NY-AM breakout echo ---
# REVERTED — set to 1.0 (no-op). The counter below stays as analytics.
# Hypothesis: when a London-Open Judas already fired on a pair that day, the
# same-pair NY-AM breakout is the weaker echo (on dual-model days the London Judas
# runs WR 62.7% / PF 16.4 vs the breakout's WR 46.9%) — so size the echo down.
# Result (4yr, downsize 0.5): the SAME path-dependency trap as P8/P9. MaxDD did
# NOT improve (full -12.95%, IS -12.95%, OOS -15.62% — all identical to baseline),
# while equity FELL R60.18M → R54.33M (-R5.84M, -9.7%) and PF 5.03 → 4.98. The
# "weaker" echoes are still net-positive to the compounding path: their wins land
# at high-equity points and compound forward, and they weren't driving the
# drawdowns, so shrinking them was pure lost upside. Lever disabled.
# 1.0 = no change (shipped); <1.0 = size the same-day NY breakout echo down.
LONDON_JUDAS_NY_BREAKOUT_DOWNSIZE = 1.0

# --- NY-AM continuation gate exemption (P11) ---
# The inverted-draw 0/3 hard gate is REVERSAL logic: it kills trades that run WITH
# the HTF daily draw (draw_score 0 = trade agrees with the trend = continuation).
# That's correct for a fresh fade, but a NY-AM trade that continues the direction
# London already established (handover consolidation → MSS → continue) is a real
# continuation that only LOOKS like a Judas swing. Exempt those from the 0/3 gate
# the same way breakout continuations are exempt.
# RESULT — REVERTED (False). Exempting the draw_score-EXACTLY-0 NY continuations
# cost R10.3M over 4yr (R60.18M → R49.85M), worse MaxDD (-12.95% → -13.56%), lower
# PF (5.03 → 5.02). Only 6 trades exempted but path-dependency amplified the damage.
# Key learning: the PROFITABLE NY continuations (34 trades, WR 52.9%) already pass
# the gate because they have draw_score > 0 — the algo ALREADY captures the user's
# edge (tagged "judas" in NY-AM, see ny_cont column). The ones the 0/3 gate blocks
# are the genuinely weak draw_score-0 subset; the gate is correctly separating them.
NY_CONTINUATION_GATE_EXEMPT = False

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
AMD_MIN_RANGE_BARS = _envi("AMD_MIN_RANGE_BARS", 8)   # ~2 hours on M15 (env-overridable)
AMD_MAX_RANGE_BARS = _envi("AMD_MAX_RANGE_BARS", 96)  # ~24 hours on M15
AMD_MAX_RANGE_PIPS = _envf("AMD_MAX_RANGE_PIPS", 35)  # tight-enough coil to qualify
AMD_MIN_TOUCHES    = _envi("AMD_MIN_TOUCHES", 2)      # high and low each tagged ≥ this
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

# --- Session-open patterns (P26) ---
# The session open price is the AMD equilibrium reference for the current cycle.
# Two patterns, both anchored to the open and firing every session:
#
# Judas sweep (+2): price swept SWEEP_SOJ_MIN_PIPS through the open in the
#   manipulation direction then closed back — classic stop-hunt at the open.
#
# Pullback retest (+1): price first extended SOJ_EXTEND_MIN_PIPS in the trade
#   direction, then pulled back to within SOJ_RETEST_TOL_PIPS of the open.
#   This is the "return to the open after the initial move" — happens every session.
SOJ_SWEEP_ENABLED  = bool(int(_os.environ.get("SOJ_SWEEP_ENABLED",   1)))
SWEEP_SOJ_MIN_PIPS = float(_os.environ.get("SWEEP_SOJ_MIN_PIPS",  3.0))  # Judas wick depth
SOJ_EXTEND_MIN_PIPS = float(_os.environ.get("SOJ_EXTEND_MIN_PIPS", 8.0)) # min move before retest
SOJ_RETEST_TOL_PIPS = float(_os.environ.get("SOJ_RETEST_TOL_PIPS", 5.0)) # tolerance at open
SOJ_LOOKBACK_BARS  = int(_os.environ.get("SOJ_LOOKBACK_BARS",      48))   # covers full session

# Multi-TF breakout calibration (v4 — per-TF parameters for detect_breakout).
# Each instrument (EU, GU) independently confirms on its highest available TF
# (D1 → H4 → H1 → M15 cascade); directions must still all agree.  Parameters
# are scaled to keep the same clock-time coverage as the M15 defaults while
# widening pip tolerances appropriately for each TF's typical range magnitude.
# M15 uses the global AMD_* defaults above.
BREAKOUT_H1_PARAMS = dict(
    min_bars=3, max_bars=20, max_range_pips=40, min_touches=2,
    range_end_lookback=20, sweep_lookback=10, hold_pips=5.0,
)
BREAKOUT_H4_PARAMS = dict(
    min_bars=2, max_bars=8,  max_range_pips=70, min_touches=2,
    range_end_lookback=8,  sweep_lookback=4,  hold_pips=8.0,
)
BREAKOUT_D1_PARAMS = dict(
    min_bars=2, max_bars=5,  max_range_pips=100, min_touches=2,
    range_end_lookback=5,  sweep_lookback=3,  hold_pips=15.0,
)

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

# --- Stale-feed guard (live safety) ---
# The MT5 terminal can silently drop the broker connection while its Python API
# keeps answering with CACHED bars. The strategy then re-evaluates identical data
# forever: equity frozen, open positions never resolve, no new entries — a silent
# freeze. This guard checks the age of the latest completed EURUSD M5 bar on every
# wake; when it exceeds STALE_FEED_MAX_MINUTES during forex market hours it alerts
# on Telegram once and holds (no trading) until the feed recovers. Weekend gaps are
# expected and suppressed. Set STALE_FEED_GUARD_ENABLED=0 to disable.
STALE_FEED_GUARD_ENABLED = bool(int(_os.environ.get("STALE_FEED_GUARD_ENABLED", 1)))
STALE_FEED_MAX_MINUTES   = float(_os.environ.get("STALE_FEED_MAX_MINUTES", 15))

# --- Symbols ---
# Env-overridable so a focused test can restrict the traded set, e.g.
# TRADE_PAIRS="GBPUSD EURUSD" for the tick-volume study (only EU/GU have ticks).
_tp = _os.environ.get("TRADE_PAIRS")
PAIRS = tuple(_tp.split()) if _tp else ("GBPUSD", "EURUSD", "NZDUSD")   # AUDUSD excluded: poor Asian WR
REF_EURGBP = "EURGBP"              # EUR vs GBP relative strength
REF_AUDNZD = "AUDNZD"              # AUDNZD data (loaded for AUDUSD MSS bars; not used as bias signal)

# --- Gold (XAUUSD) intermarket gate — DXY + silver + AUDUSD 2-of-3 breadth ---
# Gold is inverse to the dollar; silver (XAGUSD) and AUDUSD are positive intraday
# confirmers (metals complex + commodity/risk currency). See intermarket
# .resolve_gold_direction. Default OFF: when GOLD_ENABLED=0 gold is NOT in PAIRS,
# so the engine is byte-identical to the pre-gold baseline. Validate IS/OOS with
# run_gold_validation.sh before shipping ON.
GOLD_ENABLED    = bool(int(_os.environ.get("GOLD_ENABLED", 0)))
GOLD_PAIR       = _os.environ.get("GOLD_PAIR", "XAUUSD")
GOLD_REF_SILVER = _os.environ.get("GOLD_REF_SILVER", "XAGUSD")
GOLD_REF_AUD    = _os.environ.get("GOLD_REF_AUD", "AUDUSD")
# Gold "pip" = 1.0 USD so the FX-calibrated pip thresholds (≈10-pip stop, 30-pip
# target) map to sane gold moves ($10 stop / $30 target ≈ intraday ATR). PROVISIONAL
# — the first thing to re-check in validation; PF/WR/MaxDD are scale-invariant so the
# gate's edge is measurable even before this is tuned, but absolute ZAR equity is not.
GOLD_PIP        = float(_os.environ.get("GOLD_PIP", 1.0))
SILVER_PIP      = float(_os.environ.get("SILVER_PIP", 0.01))
# XAUUSD contract size: 1.0 lot = 100 oz, vs the FX 100,000-unit lot. Gold prices
# move in DOLLARS, so sizing gold with the FX contract makes every position ~1000x
# oversized (an early gold validation blew MaxDD to -21% purely from this). P&L is
# (exit-entry) x units, so the contract must match the instrument. PROVISIONAL —
# confirm against the broker's XAUUSD spec before trusting absolute gold equity.
GOLD_LOT_UNITS  = int(_os.environ.get("GOLD_LOT_UNITS", 100))
# Gold stop is placed PURELY by market structure (intact ITL/ITH) — no fixed-pip
# cap and no news 10-pip override (those are FX conventions; a $10 fixed stop is
# far too tight for a ~$2000 instrument and also over-sizes the position). Gold
# reads structure on a slightly higher TF than FX (M1 is noise at gold's scale);
# risk-based sizing scales the position down for the wider structural stop.
GOLD_STOP_TF       = _os.environ.get("GOLD_STOP_TF", "5T")
GOLD_STOP_LOOKBACK = int(_os.environ.get("GOLD_STOP_LOOKBACK", 120))
# Gold gate strictness. 1.0 = require FULL triple-confirmation (DXY + silver + AUD
# all agree); 0.75 = allow the weak-breadth bucket (only one confirmer). The first
# clean gold run (167 trades, PF 3.5-3.7 both splits — real edge) breached the -15%
# breaker (MaxDD full -15.67%, OOS -20%); requiring all-3 agreement is the principled
# fix (drop the low-breadth trades the research flagged as a failure mode).
GOLD_MIN_IMSCORE   = float(_os.environ.get("GOLD_MIN_IMSCORE", 1.0))
# Gold position multiplier — trade gold at a fraction of FX size to cap its
# drawdown contribution (edge exists, but it clusters DD). 1.0 = off.
GOLD_SIZE_MULT     = float(_os.environ.get("GOLD_SIZE_MULT", 1.0))
if GOLD_ENABLED and GOLD_PAIR not in PAIRS:
    PAIRS = PAIRS + (GOLD_PAIR,)

# --- US index intermarket gate — US500 + US100 traded, US30 + DXY confirm ---
# Indices move INVERSE to the dollar (weak USD -> risk-on -> indices up), so the
# SAME 3-market breadth logic as gold applies: DXY (primary, sign-flipped) + the
# sibling index + US30 (ref). SMT is the mechanism — the two traded indices should
# move together; if the SIBLING diverges the move lacks breadth -> suppress. US500
# and US100 are traded; US30 is a confirmer only. ICT index concepts (SMT, the
# 9:30 cash open, NY killzones) are heavily active on these. Default OFF ->
# byte-identical baseline (indices not in PAIRS).
INDICES_ENABLED   = bool(int(_os.environ.get("INDICES_ENABLED", 0)))
_ip = _os.environ.get("INDEX_PAIRS")
INDEX_PAIRS       = tuple(_ip.split()) if _ip else ("US500", "US100")   # traded
INDEX_REF         = _os.environ.get("INDEX_REF", "US30")                # confirmer only
INDEX_MIN_IMSCORE = float(_os.environ.get("INDEX_MIN_IMSCORE", 0.75))   # 0.75=2of3, 1.0=all3
INDEX_PIP         = float(_os.environ.get("INDEX_PIP", 1.0))            # indices move in points
INDEX_LOT_UNITS   = int(_os.environ.get("INDEX_LOT_UNITS", 1))         # PROVISIONAL contract
INDEX_STOP_TF       = _os.environ.get("INDEX_STOP_TF", "5T")            # structural stop TF
INDEX_STOP_LOOKBACK = int(_os.environ.get("INDEX_STOP_LOOKBACK", 120))
INDEX_SIZE_MULT   = float(_os.environ.get("INDEX_SIZE_MULT", 1.0))      # DD-fit lever; 1.0=off
# --- Index frequency levers (more trades = more income) ---
# Indices are POINT-priced, so the FX pip thresholds are wrong-scaled and starve
# the index Judas/AMD path: the 35-"pip" consolidation cap reads as 35 POINTS,
# which index coils (esp. Nasdaq, 100-200pt coils) blow straight through, so the
# reversal setup at the NY open rarely qualifies. These override that scale for
# index pairs only. 0 = use the FX global (off / baseline unchanged).
INDEX_AMD_MAX_RANGE_PIPS = _envf("INDEX_AMD_MAX_RANGE_PIPS", 0)  # points; fixed index consolidation cap
# Better: a %-of-price cap auto-scales across indices (US500 ~4.5k vs US100 ~18k),
# so one setting fits both. 0.8 -> US500 ~36pt / US100 ~144pt coil cap. Takes
# precedence over the fixed-point cap when >0. 0 = off.
INDEX_AMD_MAX_RANGE_PCT  = _envf("INDEX_AMD_MAX_RANGE_PCT", 0)   # % of price
# Separate daily trade budget for indices so they don't compete with the 3
# currencies for the basket-wide MAX_TRADES_PER_DAY slots. 0 = share the FX cap.
INDEX_MAX_TRADES_PER_DAY = _envi("INDEX_MAX_TRADES_PER_DAY", 0)
# SEMI-AUTO ONLY for indices (default ON): the auto index gate is NOT robust
# enough to pick index direction on its own (OOS fresh-start hit 25% DD), so live
# the trader supplies the direction with /bias US100 long|short and the algo only
# hunts its ICT setup on THAT side and manages the trade. No /bias -> no index
# trade. Backtest (no semi-auto inputs) still uses the auto gate so the validation
# scripts keep measuring it. Set 0 to let indices auto-trade live (not recommended).
INDEX_SEMI_AUTO_ONLY = bool(_envi("INDEX_SEMI_AUTO_ONLY", 1))
# Precise ICT SMT divergence (ict/smt.py). Two independent reads per index trade:
# index-vs-index (US500/US100/US30, positive correlation) and index-vs-dollar
# (inverse correlation). Each firing adds SMT_CONVICTION_PTS. INDEX_SMT_REQUIRED=1
# makes an index entry REQUIRE at least one SMT confirmation (a quality gate to
# validate). SMT_TF/SMT_LOOKBACK define the two-swing window.
SMT_TF             = _os.environ.get("SMT_TF", "15T")
SMT_LOOKBACK       = int(_os.environ.get("SMT_LOOKBACK", 20))
SMT_CONVICTION_PTS = int(_os.environ.get("SMT_CONVICTION_PTS", 1))
INDEX_SMT_REQUIRED = bool(int(_os.environ.get("INDEX_SMT_REQUIRED", 0)))
# SMT detector: "proxy" = block-half window (robust, smoothed); "fractal" =
# reactive fractal-swing alignment (fires at the real pivot, only when fresh).
SMT_MODE           = _os.environ.get("SMT_MODE", "proxy")
SMT_FRACTAL_LOOKBACK = int(_os.environ.get("SMT_FRACTAL_LOOKBACK", 60))
SMT_FRACTAL_MAX_AGE  = int(_os.environ.get("SMT_FRACTAL_MAX_AGE", 6))   # bars: freshness = reactivity
if INDICES_ENABLED:
    for _s in INDEX_PAIRS:
        if _s not in PAIRS:
            PAIRS = PAIRS + (_s,)
# DXY synthetic uses these (all available on OANDA):
DXY_CONSTITUENTS = ("EURUSD", "USDJPY", "GBPUSD", "USDCAD", "USDSEK", "USDCHF")

# --- Individual pair bias (synthetic EURGBP from EURUSD vs GBPUSD momentum) ---
# When EURGBP is flat at both H1 and H4, compare which USD pair moved more over
# EURGBP_SYNTHETIC_LOOKBACK H1 bars. If the divergence exceeds the threshold,
# the more-moved pair determines the synthetic EURGBP direction.
EURGBP_SYNTHETIC_LOOKBACK         = 6    # H1 bars to look back
EURGBP_SYNTHETIC_THRESHOLD_PIPS   = 10   # minimum divergence (pips) to fire

# --- Trail at TP (tested 4 times, all reverted) ---
# All four implementations (v1 swing, v2 entry-check, v3 near-TP swing, v4 HWM
# far-target-only) degraded the 4-year run by 16-52%.  Root cause: the TP IS the
# AMD delivery draw — the institutional cycle ends there.  Trailing past it means
# sitting through the reversal/consolidation phase where the algo has no edge.
# The fixed TP exit is optimal.  Code retained; TRAIL_AT_TP=0 (off by default).
TRAIL_AT_TP            = bool(int(_os.environ.get("TRAIL_AT_TP",            0)))
TRAIL_AT_TP_MIN_PIPS   = float(_os.environ.get("TRAIL_AT_TP_MIN_PIPS",    5.0))
TRAIL_AT_TP_MIN_TARGET = float(_os.environ.get("TRAIL_AT_TP_MIN_TARGET", 28.0))

# --- 5-pip HWM trail from +20 pips (v5, tested + reverted) ---
# Replaces TRAIL_LOCK (+10 pip lock) with 5-pip HWM trail from +20 pips,
# bypassing the fixed TP for far-target trades.
# Result: R211.7M vs R400.7M baseline (−47%), PF 4.03 vs 4.47.
# Root cause: let_run=True means 253 TP-hit trades (avg 23.6 pips) now exit
# at TP−5 on reversal instead of at TP.  The improvement on the 96 TRAIL_LOCK
# exits (+10 → +15) does not compensate.  Code retained; off by default.
TRAIL_5PIP_ENABLED     = bool(int(_os.environ.get("TRAIL_5PIP_ENABLED",     0)))
TRAIL_5PIP_GAP         = float(_os.environ.get("TRAIL_5PIP_GAP",          5.0))
TRAIL_5PIP_MIN_TARGET  = float(_os.environ.get("TRAIL_5PIP_MIN_TARGET",  20.0))

# --- TP Runner (partial exit AT TP1, runner to TP2) ---
# At the original institutional draw (TP1): close TP_RUNNER_RATIO of the position
# and move the stop to break-even.  The remaining units run to TP2 — the next
# premium structural draw (ITH/ITL/PDH/PDL/FVG/fib) at least TP_RUNNER_MIN_PIPS
# beyond TP1.  When no qualifying TP2 exists, exits 100% at TP1 (no change vs
# baseline).  Mutually exclusive with SCALE_OUT_ENABLED.
TP_RUNNER_ENABLED  = bool(int(_os.environ.get("TP_RUNNER_ENABLED",  0)))
TP_RUNNER_RATIO    = float(_os.environ.get("TP_RUNNER_RATIO",       0.5))   # fraction out at TP1
TP_RUNNER_MIN_PIPS = float(_os.environ.get("TP_RUNNER_MIN_PIPS",   20.0))  # TP2 must be ≥20 pips beyond TP1

# --- Scale-out (partial TP1 close) ---
# Close SCALE_OUT_RATIO of the position at SCALE_OUT_PIPS profit, then let the
# remainder run to the structural target.  Only fires when the target is at
# least SCALE_OUT_MIN_TARGET_PIPS away (avoids trivial TP2 sliver).
# SCALE_OUT_MOVE_BE: move stop to entry after TP1 fires (risk-free runner).
SCALE_OUT_ENABLED          = bool(int(_os.environ.get("SCALE_OUT_ENABLED",         0)))
SCALE_OUT_PIPS             = float(_os.environ.get("SCALE_OUT_PIPS",               20.0))
SCALE_OUT_RATIO            = float(_os.environ.get("SCALE_OUT_RATIO",              0.5))
SCALE_OUT_MOVE_BE          = bool(int(_os.environ.get("SCALE_OUT_MOVE_BE",         1)))
SCALE_OUT_MIN_TARGET_PIPS  = float(_os.environ.get("SCALE_OUT_MIN_TARGET_PIPS",    30.0))

# --- Telegram notifications (P6) ---
# Create a bot via @BotFather, then get your chat ID via @userinfobot.
# Leave empty to disable all notifications (backtest / no-live mode).
TELEGRAM_BOT_TOKEN = ""   # e.g. "123456789:AABBccDDeeFFggHHiiJJkkLLmmNNoo"
TELEGRAM_CHAT_ID   = ""   # e.g. "987654321"  (your personal chat ID)
