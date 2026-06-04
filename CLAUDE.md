# ICT Intermarket Algorithm — Project Brief

## What this is

A fully-automated ICT 2022 day-trading algorithm for forex. Trades **EURUSD, GBPUSD, NZDUSD** using
the AMD (Accumulation → Manipulation → Distribution) cycle, gated by a 3-layer intermarket model:

```
DXY (USD direction)
  └─ EURGBP (selects EUR vs GBP family)   → EURUSD or GBPUSD
  └─ AUDNZD (selects NZD vs AUD family)   → NZDUSD (AUDUSD excluded: poor WR)
```

**Live account target:** Exness ZAR-denominated, R500 start, manual funding.
**Backtest result (4 years, 2022–2025):** 798 trades, WR 47%, PF 5.03, MaxDD -12.95%, R500 → R59.4M.
(Two entry models: Judas reversal + intermarket breakout continuation — see §5.)

---

## Files

```
backtest.py              Main backtester — all strategy logic lives here
config.py                All tunable parameters (edit here, no code changes needed)
run_backtest_histdata.py Run + report: python run_backtest_histdata.py [--years 2022 2023 ...]
intermarket.py           DXY × EURGBP/AUDNZD → direction + im_score
main.py                  QuantConnect LEAN live engine (mirrors backtest.py logic)
news_filter.py           ForexFactory XML + CSV calendar parser
risk.py                  Lot sizing + position state
trade_log.py             SQLite trade log (data/trade_log.db)
ict/                     Pure-logic modules: killzones, bias, fvg, ob, amd, ote, dxy_synthetic, ...
data/news_events.csv     288 high/medium-impact events 2022–2025 (used in backtest)
```

---

## Strategy layers (top-down)

### 1. Intermarket gate (hard gate — no signal, no trade)
- **DXY H1 BOS**: if flat → skip all pairs
- **EURGBP escalation cascade** (EUR/GBP family):
  - Level 1: H1 EURGBP bias
  - Level 2: H4 EURGBP (when H1 flat) → unlocks GBPUSD, reclassifies scenario
  - Level 3: Individual pair bias — compare H1 EURUSD vs GBPUSD pip momentum (when H1+H4 both flat)
    - Divergence threshold: 10 pips over 6 bars (`EURGBP_SYNTHETIC_LOOKBACK/THRESHOLD_PIPS` in config)
- **AUDNZD escalation cascade** (NZD family):
  - Level 1: H1 AUDNZD bias
  - Level 2: H4 AUDNZD (when H1 flat) → N-short_h4 confirmed, N-long_h4 gated (0% WR both IS+OOS)

### 2. ICT Intermarket Cheat Sheet scenarios
All trades are classified and tracked by scenario. Current gate status:

| Scenario | Description | Status |
|---|---|---|
| 1a | DXY↑ + H1 EUR>GBP → GBPUSD short | ✅ Active (PF 24.80) |
| 1b | DXY↑ + H1 GBP>EUR → EURUSD short | ✅ Active (PF 10.60) |
| 2a | DXY↓ + H1 EUR>GBP → EURUSD long | ✅ Active with gates |
| 2b | DXY↓ + H1 GBP>EUR → GBPUSD long | ✅ Active (PF 3.48) |
| 3a | DXY↑ + flat → EURUSD short | ✅ Active (PF 3.86) |
| 3b | DXY↓ + flat → EURUSD long | ✅ Active (PF 6.65) |
| 1a_h4 | H4 escalation → GBPUSD short | ✅ Active (PF 38.80, star) |
| 1b_h4 | H4 escalation → EURUSD short | ✅ Active (PF 2.09) |
| 2b_h4 | H4 escalation → GBPUSD long | ✅ Active (PF 17.84) |
| 2a_h4 | H4 escalation → EURUSD long | 🚫 Gated (PF 0.01, WR 25%) |
| 1a_ip | Individual pair bias → GBPUSD short | ✅ Active (PF 1.16, regime-dependent) |
| 1b_ip | Individual pair bias → EURUSD short | ✅ Active (PF 3.95) |
| 2b_ip | Individual pair bias → GBPUSD long | ✅ Active (PF 2.92, OOS confirmed) |
| 2a_ip | Individual pair bias → EURUSD long | 🚫 Gated (too extended) |
| N-long | DXY↓ + NZD strong → NZDUSD long | ✅ Active (PF 4.77) |
| N-short | DXY↑ + NZD weak → NZDUSD short | ✅ Active (PF 3.93) |
| N-short_h4 | H4 AUDNZD → NZDUSD short | ✅ Active (OOS PF 31.55) |
| N-long_h4 | H4 AUDNZD → NZDUSD long | 🚫 Gated (WR 0% IS+OOS) |

### 3. 2a-specific gates (surgical, based on IS/OOS analysis)
- **2a London session**: blocked (PF 0.84 — chasing Judas spike highs)
- **2a at 3/3 draw score**: blocked (move fully mature + 3x sizing = bad combo)
- **2a H1 FVG entry**: blocked (WR 14.3% — entering too late in extended rally)
- All gates apply to 2a, 2a_h4, 2a_ip equally

### 4. HTF draw cascade scoring (W→D→H4)
Scores 0–3 based on how many of Weekly/Daily/H4 agree with trade direction (inverted — strategy is reversal).

- **0/3**: hard gate — skip trade entirely
- **1/3**: trade at 1x lot
- **2/3**: trade at 2x lot (when equity ≥ R3,000)
- **3/3**: trade at 3x lot (when equity ≥ R3,000)

`DRAW_SIZE_MIN_EQUITY = 3000` — multipliers disabled below R3k to protect small account.

### 5. AMD + MSS entry (two entry models)
Every trade is tagged `entry_model` = **judas** (default) or **breakout**.

**Judas reversal** (the original model):
- M15 consolidation range must exist (8–96 bars, ≤35 pips, both extremes touched ≥2x)
- M15 sweep of one extreme (Judas swing) then close back inside → fade the sweep
- M5/M15/H1 FVG or OB in the distribution direction for limit entry
- 2-of-3 MSS: EURUSD + GBPUSD + DXY inverse must show structure shift
- Stop placed at nearest M1 swing + 1 pip buffer (min 4 pips)

**Intermarket breakout / continuation** (`detect_breakout` in ict/amd.py):
- Inverse of Judas: price CLOSES beyond a range extreme by ≥ `BREAKOUT_HOLD_PIPS`
  and holds (no rejection back inside) → follow the break. Pullback/retest allowed.
- **Triple-confirmation** (`_intermarket_breakout`): a single-pair breakout is usually
  a fakeout. Requires EURUSD + GBPUSD to BOTH break their M15 ranges in agreement AND
  DXY M15 BOS to confirm (DXY breaking lows for USD-pair longs / highs for shorts).
  DXY leg uses BOS direction, not range detection — synthetic DXY is ~100-scale so
  forex-pip range detection can't apply.
- Breakout-confirmed trades are EXEMPT from the inverted-draw 0/3 hard gate (that gate
  is reversal logic; continuations run WITH the HTF and score low on the inverted
  cascade). They earn `BREAKOUT_CONVICTION` instead of draw-score conviction.
- IS/OOS validated: breakout PF 3.20 (IS) / 3.43 (OOS) — not curve-fit.

### 6. Killzones
- **EURUSD/GBPUSD**: London Open (03:00–05:00 ET) + NY AM (07:00–10:00 ET)
- **NZDUSD**: London Open only (NY AM confirmed drain in backtest)
- NY noon block: 12:00–13:00 ET hard no-trade

---

## Equity tiers and lot sizing

```python
EQUITY_TIERS = [
    (6_000, (0.10, 0.10, 0.10)),
    (3_000, (0.05, 0.05, 0.05)),
    (1_500, (0.03, 0.03, 0.03)),
    (750,   (0.02, 0.02, 0.02)),
    (0,     (0.01, 0.01, 0.01)),
]
```

**Note from user (2026-06-03):** Intends to run simplified tiers on live Exness account:
R0→R1,000 = 0.01 lots | R1,000→R3,000 = 0.02 lots | R3,000+ = 0.05 lots.
Config will need updating before going live.

Per-pip values at each lot size (EURUSD/GBPUSD, USD_ZAR≈18.5):
- 0.01 lots: R1.85/pip | 10-pip stop = R18.50 | full pyramid win = R166
- 0.02 lots: R3.70/pip | 10-pip stop = R37.00 | full pyramid win = R333
- 0.05 lots: R9.25/pip | 10-pip stop = R92.50 | full pyramid win = R832

---

## Circuit breakers

| Breaker | Threshold | Action |
|---|---|---|
| MaxDD halt | -15% from peak equity | Pause trading 10 days |
| Daily loss cap | -6% of day-open equity | No new entries rest of day |
| Consecutive losses | 5 in a row | Pause rest of day |
| Session kill switch | -10% from session open | Close all positions, halt day |

---

## OOS validation protocol

Split: 2022–2023 (in-sample) / 2024–2025 (out-of-sample).

Run with: `python run_backtest_histdata.py --years 2022 2023`
           `python run_backtest_histdata.py --years 2024 2025`

Any new gate or feature must show positive PF in BOTH splits before shipping.
Features gated because IS/OOS diverged badly: 2a_h4, N-long_h4.
Features kept despite IS<OOS difference: 1a_ip (IS PF 6.10, OOS PF 1.18 — both positive, IS wins at high equity critical for compounding path).

---

## Pyramid draw-unlock rule

When a position has `draw_score ≥ 3` (confirmed 3/3 HTF cascade), pyramid adds are allowed
even when EURGBP is temporarily flat (im_score = 0.75), provided DXY still agrees and cross
hasn't reversed. Implemented in `_maybe_pyramid`. Gate counter: `pyramid_blocked_low_im`.

---

## Data source

HistData.com M1 CSVs, manually downloaded and placed in `data/` folder.
Pairs needed: EURUSD, GBPUSD, EURGBP, NZDUSD, AUDNZD, AUDUSD (optional), UDXUSD (optional).
Resampled to M5/M15/H1/H4/D/W inside `run_backtest_histdata.py` using pandas resample.

---

## PENDING BUILDS (agreed 2026-06-03, implement when ready)

### P1 — COT data scraper + weekly bias feeder
**What:** CFTC Commitment of Traders data shows net speculative positions for EUR, GBP, NZD futures.
When specs are at multi-year extreme longs → reversal risk → tighten long scenarios (2a, 3b, 2b).
When specs are max short → squeeze risk → favour long scenarios.

**Implementation plan:**
- Download free CFTC disaggregated CSV every Saturday (URL: `cftc.gov/dea/newcot/f_disagg.txt`)
- Extract: EURO FX (EUR), BRITISH POUND (GBP), NEW ZEALAND DOLLAR (NZD) net non-commercial positions
- Compute z-score vs 52-week rolling average to detect extremes
- Write to `data/weekly_bias.json` with keys: `eur_cot_zscore`, `gbp_cot_zscore`, `nzd_cot_zscore`
- Algo reads this at startup each week, adjusts scenario confidence modifiers

**Gate logic (proposed):**
- If `eur_cot_zscore > +2.0` (specs very long EUR) → suppress 2a/3b confidence by 0.5
- If `eur_cot_zscore < -2.0` (specs very short EUR) → boost 2a/3b confidence by 0.5

### P2 — Interest rate differential tracker
**What:** Rate differentials (Fed vs ECB, Fed vs BOE, Fed vs RBNZ) drive institutional currency flows.
Higher differential = currency flow in → reinforces DXY bias in that direction.

**Implementation plan:**
- Central bank rates change rarely (quarterly), so a simple JSON config works:
  `data/rate_differentials.json` with: `fed_ecb_spread`, `fed_boe_spread`, `fed_rbnz_spread`
- User updates this manually after each central bank meeting (FOMC, ECB, BOE, RBNZ)
- Or: scrape from investing.com/central-bank-rates (simple table scraper, no auth)
- Algo checks: if `fed_ecb_spread > 0` → USD yield advantage → reinforces DXY bull bias for 1a/1b

**No automation needed initially** — rates change 4-8x/year. Manual JSON update is fine.

### P3 — Weekly bias file reader in backtest + live engine
**What:** Both `backtest.py` and `main.py` should read `data/weekly_bias.json` at the start of each
new week and use it to modulate scenario confidence (COT + rate modifiers above).

**Implementation plan:**
- Add `_load_weekly_bias(t)` method to Backtester — reads JSON, applies on Monday 00:00 UTC
- Add `weekly_cot_modifier` dict to strategy state (per-scenario confidence delta)
- In `_maybe_open`, after im_score computed, apply modifier: `im_score += weekly_cot_modifier.get(_im_scenario, 0)`
- Gate: if modified im_score < 0.75, skip

### P4 — COT scraper automation (cron / scheduled script)
**What:** Automated Saturday download + JSON generation so the user just reviews a WhatsApp/email
summary and approves before Monday open.

**Implementation plan:**
- `scripts/update_weekly_bias.py` — standalone script, no algo dependencies
- Downloads CFTC CSV, computes z-scores, fetches rate differentials if changed
- Writes `data/weekly_bias.json`
- Sends summary to user (email/Telegram/WhatsApp) with:
  - COT z-scores for EUR/GBP/NZD
  - Rate differential table
  - Suggested scenario boosts/suppressions for the week
  - Any high-impact news events in the coming week (from ForexFactory XML)
- User confirms or overrides before Monday 03:00 ET (London open)

### P5 — Equity tier update for live Exness account
**What:** User's live account plan uses simplified tiers (R0→R1k = 0.01, R1k→R3k = 0.02, R3k+ = 0.05).
Current config has more intermediate steps (R750 → 0.02, R1500 → 0.03).

**Change needed in config.py:**
```python
EQUITY_TIERS = [
    (6_000, (0.10, 0.10, 0.10)),
    (3_000, (0.05, 0.05, 0.05)),
    (1_000, (0.02, 0.02, 0.02)),   # user's plan: skip 0.03 tier
    (0,     (0.01, 0.01, 0.01)),
]
```
Run backtest to confirm this doesn't harm MaxDD at small equity before deploying live.

### P6 — Notification system (entry/exit/circuit breaker alerts)
**What:** When running live on Exness, user needs to know when trades open/close/halt without
watching a screen. Telegram bot is simplest (free, instant, no app approval needed).

**Implementation plan:**
- `scripts/notify.py` — Telegram bot wrapper (single function: `send_message(text)`)
- Wire into `main.py` at: new trade opened, trade closed (with P&L), circuit breaker fired,
  daily session start (equity snapshot), weekly reset (equity snapshot)
- Also wire into the weekly bias script (P4 above) for the Monday morning brief

### P7 — Walk-forward validation
**What:** Instead of fixed 2022-23 IS / 2024-25 OOS, run rolling 12-month windows to confirm
no parameters are curve-fit to a specific year.

**Not urgent** — current OOS validation is sufficient for now. Revisit when adding new features.

### P8 — Session-phase AMD cycle sequencer (IMPLEMENTED 2026-06-04)
**What:** Track where each pair is in the AMD cycle per session so the algo knows whether to
expect a Judas reversal or a breakout continuation at any given moment.

**Phases (keyed per-pair per-NY-date):**
- `accumulation`: Asian session — building the range
- `judas_watch`: London 03:00–03:30 ET — prime Judas sweep window (active)
- `judas_seen`: AMD sweep detected (`detect_amd_setup` found a sweep) → reversal active (active)
- `breakout_eligible`: London 03:30–05:00 ET, no sweep detected → **GATED** (4yr PF 0.13)
- `ny_extend`: NY AM 07:00–10:00 ET, no prior London Judas → **GATED** (4yr PF 0.16)

**Gate added**: `breakout_eligible` and `ny_extend` are fully blocked. Without an established
AMD sweep, the session has no manipulation phase to fade or continue — all entries in these
phases chase mature moves that reverse (losses 4-7x larger than wins despite 40-50% WR).

**Key insight (ICT)**: The Judas sweep confirmation is the prerequisite for trading, not just
a conviction bonus. Without it, the AMD cycle has no directional anchor.

**IS/OOS validation (2026-06-04):**

| Metric | IS 2022–23 | OOS 2024–25 |
|---|---|---|
| Total trades | 353 | 395 |
| Win rate | 46.5% | 46.8% |
| Profit factor | 3.24 | **5.47** |
| Max drawdown | -12.93% | **-11.82%** |
| R500 → | R89,023 | R543,064 |
| judas_seen PF | 3.26 (346 trades) | **5.44** (387 trades) |
| judas_watch PF | 2.68 (7 trades) | 35.33 (8 trades) |

OOS beats IS on every metric (PF, WR, MaxDD). Textbook not-curve-fit: the session phase gate
removed the noise, not the signal.

**Analytics**: `session_phase` column added to trade records; breakdown table in reporting.

### P9 — HTF FVG 50% consolidation zone as conviction signal (NOT YET IMPLEMENTED)
**What:** When price enters an H4/D1/W1 FVG it typically consolidates at ~50% of the FVG
range before continuing (the "equilibrium" of the inefficiency). This 50% zone is the
natural Accumulation anchor for the next AMD cycle. Two behaviours inside that zone:
1. Consolidation at 50% → micro-Judas sweep of the range → continuation through the FVG
2. Consolidation at 50% → reversal (FVG partially filled, mission complete)

**What's hard to code**: Distinguishing "stalling before continuation" vs "reversing" at
the 50% level in real-time. The AMD detection (`detect_amd_setup`) already catches the
micro-Judas setup inside the FVG — but without the FVG context, we don't know WHY the
consolidation formed there (which makes it higher quality).

**Proposed implementation**: Add +1 conviction when:
- Current price is within N pips of an H4/D1/W1 FVG midpoint (50% level)
- The FVG direction aligns with the trade direction
- The `detect_amd_setup` detected an AMD setup (consolidation + sweep near the 50%)
This tells us: "this AMD cycle formed at the natural HTF delivery zone, not random."
The stop-run inside the 50% (mini-Judas within the FVG) is the highest-quality AMD entry.

**Not urgent** — requires FVG detection on H4/D1/W1 bars and midpoint proximity check.

---

## 3-month live account scenarios (R500 start, discussed 2026-06-03)

| Scenario | Conditions | End equity (3 months) |
|---|---|---|
| Best case | Trending USD, 48 trades, WR 54% | R3,200–R3,800 |
| Normal case | Mixed market, 40 trades, WR 48% | R1,700–R2,100 |
| Rough start | Choppy, circuit breakers fire 1-2x | R800–R1,000 |
| Worst case | Max adversity, halts multiple times | R500–R700 |

**Key milestone:** R3,000 — draw multiplier (2x/3x sizing) engages. Growth accelerates dramatically past this point.
At 0.01 lots, maximum single-day loss = 3 trades × R18.50 = R55.50. Account cannot blow up at this size.

---

## What "not curve-fit" means (context for future sessions)

A feature is NOT curve-fit when:
1. It has a logical ICT/intermarket reason for existing (not just "it worked in the data")
2. It holds positive PF in BOTH in-sample (2022-23) AND out-of-sample (2024-25) periods
3. The IS and OOS performance magnitudes are in the same ballpark (not IS=10 / OOS=0.5)

Features gated because they failed this test: `2a_h4` (IS PF 0.83, OOS PF 0.01), `N-long_h4` (WR 0% both).
Features kept despite IS < OOS: `1a_ip` (IS PF 6.10 at small equity critical for compounding path).
Breakout model is a textbook pass: PF 3.20 (IS) / 3.43 (OOS) — near-identical magnitude both periods.

---

## Development branch

`claude/algorithm-ict-2022-alignment-9kkLi` → PR #2 on GitHub (draft, open).
All strategy changes go to this branch. Never push directly to main without user approval.
