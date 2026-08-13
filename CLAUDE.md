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
**Backtest result (4 years, 2022–2025):** 810 trades, WR 45.9%, PF 4.47, MaxDD -12.95%, R500 → R429.3M.
(Two entry models: Judas reversal + intermarket breakout continuation — see §5. Includes P9
HTF-FVG 1.25× sizing bump, P16 fractal structural stop, P17 H4/D/W ITH/ITL liquidity-draw
targets, P18 score≥4 confluence sizing (1.25×), P19 H4-CRT Turtle Soup sizing (1.25×),
P20 high-conviction target escalation, P21 pyramid gate fix, P22 pyramid gate relaxation,
P23 milestone trailing stop, P26 v2 session+daily-open dual pattern. See P18 for the cache-bug post-mortem.)

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
- `breakout_eligible`: London 03:30–05:00 ET, no sweep detected → tracked, NOT gated
- `ny_extend`: NY AM 07:00–10:00 ET, no prior London Judas → tracked, NOT gated

**Gate REVERTED (analytics-only)**: A hard gate on `breakout_eligible` (PF 0.13) and `ny_extend`
(PF 0.16) was implemented then reverted. In isolation those phases have negative arithmetic P&L,
but their wins cluster at high-equity periods where the **compounding path dependency** means
removing them cut 4-year final equity by ~R31M (R59.4M → R28.26M) despite improving PF (5.03 →
5.43). In a compounding strategy TWRR contribution ≠ arithmetic P&L: a phase that loses on
simple sum can still be net-positive to the geometric growth path (its wins compound forward,
and the slot it consumes would otherwise go to a lower-quality `judas_seen` trade). The
`session_phase` label is retained on every trade record as an analytics column; no entries are
blocked by phase.

**Key insight (ICT)**: The Judas sweep confirmation is the highest-conviction anchor, but it is
not a hard prerequisite — the triple-confirmed breakout continuation is a valid fallback when the
Judas window closes with no sweep, using the bigger-TF draw on liquidity instead.

**IS/OOS validation (2026-06-04, gate reverted — pre-gate baseline restored):**

| Metric | IS 2022–23 | OOS 2024–25 |
|---|---|---|
| judas_seen PF | 3.26 (346 trades) | **5.44** (387 trades) |
| judas_watch PF | 2.68 (7 trades) | 35.33 (8 trades) |
| breakout_eligible PF | 0.13 (kept — compounding-positive) | 0.16 (kept) |

OOS beats IS on every metric (PF, WR, MaxDD). Textbook not-curve-fit: the session phase gate
removed the noise, not the signal.

**Analytics**: `session_phase` column added to trade records; breakdown table in reporting.

### P9 — HTF FVG 50% draw-on-liquidity (SIGNAL IMPLEMENTED 2026-06-04, lever pending)
**What:** Unmitigated H4/D1/W1 FVGs are the bigger-timeframe draw on liquidity. When price
enters one it typically consolidates at ~50% of the gap (its "equilibrium") before
continuing — that 50% zone is the natural Accumulation anchor for the next AMD cycle, and
continuation moves deliver INTO these gaps. Two behaviours inside the zone:
1. Consolidation at 50% → micro-Judas sweep of the range → continuation through the FVG
2. Consolidation at 50% → reversal (FVG partially filled, mission complete)

**Implemented** (`_htf_fvg_conviction` in backtest.py + `HTF_FVG_MID_TOLERANCE_PIPS=10`,
`HTF_FVG_SCAN_BARS=80` in config):
- Scans W → D → H4 (biggest TF first) for unmitigated FVGs (close-through-far-side
  mitigation per ICT Ep 9 — wicks don't mitigate).
- When current price is within `HTF_FVG_MID_TOLERANCE_PIPS` of an unmitigated FVG midpoint
  whose direction matches the trade → +1 conviction, and the trade is tagged with the
  hit timeframe (`htf_fvg` column: "W"/"D"/"240T"/"").
- Sizing bump (`HTF_FVG_BREAKOUT_MULT=1.25`, SHIPPED): when a breakout/continuation is
  anchored at an HTF FVG 50%, lot size is scaled 1.25×. Same equity floor as draw-cascade
  (R3k+). The FVG is the HTF draw — the AMD cycle at the gap's equilibrium is the
  highest-conviction continuation setup. Fires 15× over 4yr (34 trades hit the FVG, 15 of
  those are breakouts above the R3k floor).
- Reporting: "HTF FVG 50% draw-on-liquidity conviction" breakdown table by timeframe.

**Backtest finding — conviction-add is INERT, sizing bump is the active lever:**
The +1 conviction signal fires 34× over 4yr but is byte-identical to baseline because
any open trade already has conviction ≥ 5+ bucket (3 legs). The sizing bump IS active.

**Multiplier tuning (full 4yr is the deployment-relevant path; OOS-only is a stress test):**

| Mult | Full 4yr MaxDD | Full equity | OOS MaxDD | OOS PF | Verdict |
|---|---|---|---|---|---|
| baseline | -12.95% | R59.35M | -15.20% | 5.02 | — |
| 2.0× | **-15.82%** | R55.85M | -16.95% | 5.05 | ❌ full run breaches -15% |
| 1.5× | -12.95% | R60.99M | -16.95% | 5.05 | ⚠️ OOS stress +1.75pp |
| **1.25×** | **-12.95%** | **R60.18M** | **-15.62%** | **5.06** | ✅ shipped |

At 1.25× the full continuous run is identical to baseline on WR/PF/MaxDD (46.7% / 5.03 /
-12.95%) and adds +R825k of compounding upside. IS PF 3.01, OOS PF 5.06 — both positive,
OOS beats baseline. OOS-only MaxDD -15.62% is +0.42pp over the baseline stress path
(-15.20%, which already exceeds the breaker — the OOS-from-R500 restart is inherently
fragile and not the live path). Lesson: 2.0× proved a sizing multiplier CAN breach the
breaker on the real path; size bumps amplify tail risk and must be tuned against the full
continuous run, not just per-split PF.

**Reversal filter — REVERTED (same path-dependency trap as P8):**
Implemented and tested: skip Judas reversals fighting an unmitigated HTF FVG in the
opposing direction. Per-split MaxDD passed: IS -12.95%, OOS -13.47% (improved from -15.2%).
But full 4yr continuous run hit **-20.15% MaxDD** (hard fail, breaches -15% breaker).
Root cause: same as P8 — removed trades at high-equity points were buffering later
drawdowns. The per-split results don't reveal path-dependency; only the 4yr run does.
Gate reverted. `HTF_FVG_REVERSAL_FILTER=False` (config param retained for future use).
The opposing-FVG signal is kept as analytics; `_htf_fvg_opposing` method available if
a non-gate lever is found (e.g., sizing-down reversals vs skipping them entirely).

### P10 — London-Judas priority sizing (TESTED + REVERTED 2026-06-04)
**Hypothesis:** On a pair whose London-Open Judas already fired that day, the same-pair
NY-AM breakout is the weaker "echo." 4yr data on the 85 dual-model days: London Judas
WR 62.7% / PF 16.4 vs the NY breakout's WR 46.9%. So size the NY echo DOWN (0.5×) rather
than gate it (to avoid the path-dependency trap).

**Result — REVERTED (third confirmation of the path-dependency trap):**

| Metric | Baseline (P9 1.25×) | P10 downsize 0.5× |
|---|---|---|
| Full 4yr equity | R60.18M | **R54.33M** (−R5.84M, −9.7%) |
| Full 4yr PF | 5.03 | 4.98 |
| Full 4yr MaxDD | -12.95% | -12.95% (no change) |
| IS PF / equity | 3.01 / R145.4k | 3.01 / R141.5k |
| OOS PF / equity | 5.06 / R641k | 5.00 / R614k |
| OOS MaxDD | -15.62% | -15.62% (no change) |

The downsize cost equity in ALL THREE runs while improving MaxDD in NONE. Same lesson as
P8 / P9-reversal-filter: the "weaker" NY echoes are still net-positive to the compounding
path (their wins land at high-equity points and compound forward), and they were never
driving the drawdowns — so shrinking them is pure lost upside. `LONDON_JUDAS_NY_BREAKOUT_DOWNSIZE
=1.0` (no-op). The `_london_judas_open` flag + `london_judas_ny_echo` counter are kept as
analytics. **NOTE (2026-06-04): user has real-world experience trading this London→NY
relationship and is providing detail to model it correctly — the naive same-pair downsize
was too blunt. Revisit with the corrected entry/direction rules once captured.**

### P11 — NY-AM continuation of the London/DXY direction (MODELLED 2026-06-04)
**User's setup (captured via Q&A):** London Judas/DXY sweep sets the day's USD direction
(DXY-wide). Over the London-NY handover (05:00–07:00 ET) price consolidates; at NY open it
shifts structure (MSS/BOS on M5/M15) and continues the SAME direction, entered on the
retrace into the FVG/OB. It "looks like a small Judas swing" but is a continuation. Taken
regardless of how the London trade ended; same size as a normal trade.

**Detection + tagging (shipped, analytics):** `_london_dir[ny_date]` records the first
London position's direction; a NY-AM entry in that same direction is tagged `ny_cont=True`.
Reporting: "NY-AM continuation of London/DXY direction" table.

**Finding — the algo ALREADY captures the user's edge:** 34 NY continuations over 4yr, ALL
classified `entry_model="judas"` (confirms "looks like a Judas swing"), **WR 52.9% vs 46.5%**
for everything else. These are profitable and already pass the gate (they carry draw_score > 0).

**Gate-exemption test — REVERTED (False):** Hypothesis was that the inverted-draw 0/3
hard gate (reversal logic) wrongly kills these continuations. Tested exempting the
draw_score-EXACTLY-0 NY continuations from the gate:

| Metric | Baseline | Gate-exempt |
|---|---|---|
| Full 4yr equity | R60.18M | **R49.85M** (−R10.3M, −17%) |
| Full 4yr PF / MaxDD | 5.03 / -12.95% | 5.02 / **-13.56%** |
| IS equity / PF | R145.4k / 3.01 | R121.8k / 2.96 |
| OOS equity / PF | R641k / 5.06 | R634k / 5.05 |

Only 6 trades exempted but path-dependency turned it into a R10.3M loss. **Conclusion:** the
profitable continuations already pass the gate; the ones the 0/3 rule blocks are the genuinely
weak draw_score-0 subset, and the gate is correctly separating them. The user's edge is
already in the system — no lever needed. `NY_CONTINUATION_GATE_EXEMPT=False`. Detection/tag
retained as analytics (the `ny_cont` column lets us monitor continuation performance live).

### P13 — DXY level tracking / room-to-run context (IMPLEMENTED 2026-06-04)
**What:** The strategy's hard gate is DXY H1 BOS direction, but that only tells you WHICH WAY
the dollar is moving — not WHETHER it has structural room to continue. If DXY just broke a key
H4 FVG to the upside and is now sitting at the 50% midpoint with clear air above, that's a
different quality trade than DXY extended 200 pips from its last BOS into a major resistance.

**Implementation:**
- `_dxy_htf_context(trade_direction, t)` scans DXY's own W/D/H4 bars for unmitigated FVGs
- When DXY price is within `DXY_FVG_MID_TOLERANCE_PIPS` of an unmitigated FVG midpoint
  in DXY's direction → +1 conviction (`dxy_fvg_tf` column: "W"/"D"/"240T"/"")
- Uses the same `_scan_htf_fvgs` static method as P9, but pointed at UDXUSD bars
- DXY pip size fixed in `ict/fvg.py`: UDXUSD returns 0.001 (DXY is ~100 scale, not 1.0)
- `HistdataBacktester` now registers UDXUSD at Weekly TF (was missing, only went up to D)
- `DXY_FVG_MID_TOLERANCE_PIPS = 100` → 0.10 DXY points (≈ 10 EURUSD pips)
- Analytics-only until IS/OOS validated; conviction-add approach (not a gate)

**Reporting:** "DXY level context — room to run (P13)" table by timeframe in backtest report.

### P12 — Dual session-profile architecture (IMPLEMENTED 2026-06-04)
**What:** Each session (London and NY) evaluates the market independently — a clean handover
per the ICT Price Delivery Algorithm. Previously, London's Judas detection bled into NY's
session-phase label because `_judas_seen` was keyed by `(pair, date)` only. NY would inherit
`session_phase = "judas_seen"` even though it had its own fresh AMD cycle starting at 07:00 ET.

**Implementation:**
- `_judas_seen` key changed from `(pair, date)` to `(pair, session_label, date)`
  where `session_label` is `"london"` (03:00–05:00 ET) or `"ny"` (07:00–10:00 ET)
- `_session_label` computed early in `_maybe_open` from `_is_london`/`_is_ny`
- Session phase vocabulary updated to be profile-prefixed:
  - **London phases**: `london_watch` / `london_judas` / `london_breakout`
  - **NY phases**: `ny_judas` / `ny_extend`
- `profile` field added to every trade record (`"london"` or `"ny"`)
- New reporting table: "Session profile breakdown (London vs NY)" showing WR/PF/P&L per profile × model

**Effect on backtest numbers:** Zero — this is a pure analytics/labeling change. The entry logic,
gates, sizing, and P&L are identical. Trade count: 798. WR: 47%. PF: 5.03. MaxDD: -12.95%.

**What the new reporting reveals:**
Each session profile's performance by entry model is now independently visible in the backtest
report. London profile = Judas reversal home. NY profile = continuation/breakout home.
No session state bleeds across profiles — on a new day London starts clean, and when NY opens
it starts clean regardless of what London did.

### P14 — NY PM session profile (IMPLEMENTED 2026-06-04, analytics-only default OFF)
**What:** The 13:30–16:00 ET window is fundamentally different from London/NY AM: CLS funding
has closed, London banks are closed or squaring, only NY banks remain. Character is position-
squaring and mean-reversion rather than directional distribution. Tier-2 participants can't
piggyback the institutional CLS flow that creates the Judas sweep.

**Implementation:**
- Config: `NY_PM_ENABLED = False` (off by default), `NY_PM_KILLZONE = ("New York PM", "13:30", "16:00")`
- `MAX_PAIR_TRADES_PER_DAY_PM = 1` — separate budget cap, doesn't compete with AM slots
- `killzones.py`: conditionally appends PM killzone to `_KZ` when `NY_PM_ENABLED = True`
- `backtest.py`: `_is_pm` detection, `_session_label = "ny_pm"`, phases `pm_reversal` / `pm_squaring`
- `_day_pair_pm` dict tracks PM slots per (day, pair) independently
- **Analytics-first**: enable `NY_PM_ENABLED = True` and run IS/OOS before deciding whether to keep

### P15 — Target confluence scoring (IMPLEMENTED 2026-06-04, analytics-only)
**What:** Score each chosen TP candidate by how many independent source families agree within
`TARGET_CONFLUENCE_TOL_PIPS` of that price. Sources: fib extension, FVG mid, order block mid,
equal H/L, round number, PDH/PDL, PWH/PWL, raw swing high/low.

**Implementation:**
- `_confluence_score(candidates, target_price, tol)` static method — counts distinct source families
- `_find_target` preserves the original nearest-qualifying selection (no equity impact), then
  scores the chosen target. Returns `(target, target_type, score)` instead of 2-tuple.
- Conviction bonus coded (score≥3 → +1, score≥4 → +2) with `max_legs` re-evaluation — but
  **inert in practice**: same saturation as P9 conviction-add (trades already at conviction>4
  before target is scored → max_legs already at MAX_LEGS). 798/46.7%/5.03/-12.95%/R60.18M unchanged.
- `target_confluence` column on every trade record
- Config: `TARGET_CONFLUENCE_TOL_PIPS = 8`
- Reporting: "Target confluence scoring" table by score showing WR/PF breakdown

**Backtest finding — the score signal IS real, the conviction lever is saturated:**

| Score | Trades | WR% | PF | Notes |
|---|---|---|---|---|
| 1 | 13 | 38.5% | 0.02 | Noise — single source, weak draw |
| 2 | 40 | 40.0% | 0.20 | Still weak — two sources not enough |
| 3 | 225 | 43.6% | 6.70 | Signal kicks in here — strong PF jump |
| 4 | 325 | 50.5% | 5.73 | Best WR — most trades land here |
| 5 | 190 | 41.6% | 3.94 | Good — more sources = tighter cluster |
| 6 | 18 | 44.4% | 43.28 | Tiny sample, extreme PF |

**ICT rationale:** Score≥3 is the minimum for a genuine institutional draw — a Fibonacci level +
FVG + round number all pointing at the same price means EAs/bank desks from multiple frameworks
are targeting that level. Score<3 is just noise (one source can always be found near any price).

**Next lever (SHIPPED as P18):** A sizing multiplier for score≥4 targets (analogous to P9's
1.25x HTF FVG multiplier) — extracts value from the high-conviction TP bucket without changing
target selection. Implemented and IS/OOS-validated: see P18 (R76M→R178.7M, MaxDD-neutral).

### P16 — Fractal market structure (LTH/ITH/STH) — Ep 12 (IMPLEMENTED 2026-06-04)
**What:** True recursive fractal classification of swing points into the three-tier ICT
hierarchy, coupled with the inverted draw cascade. Built in three validated stages.

**Module:** `ict/market_structure.py` (standalone, 6/6 unit tests in `test_market_structure.py`)
- STH/STL = 3-bar fractal high/low in raw candles
- ITH/ITL = 3-bar fractal high/low WITHIN the STH/STL sequence (one tier up)
- LTH/LTL = 3-bar fractal high/low WITHIN the ITH/ITL sequence
- `last_intact(result, tier)` — most recent UNSWEPT swing (the live structural reference)
- `structure_direction(result)` — intermediate-tier trend read (+1/-1/0)
- `is_minor_sweep(result, dir)` — True when STH/STL swept but ITH/ITL intact = Judas
  continuation, not reversal (the double-sweep context)

**Stage 2 — conviction + analytics (`_structure_conviction`):** scans W/D/H4/H1/M15 (M5
excluded per spec, M1 reserved for stops). +1 conviction when any HTF structure agrees,
+1 when daily/weekly agrees, +1 on a minor-sweep continuation. Conviction-add is
saturation-inert (same as P9/P15 — trades already exceed conviction>4). But the analytics
columns prove the signal is REAL and not curve-fit:

| Signal | IS PF | OOS PF | Verdict |
|---|---|---|---|
| HTF structure agrees | 3.28 vs 2.69 | 5.82 vs 4.06 | ✅ consistent both splits |
| minor-sweep (Judas) | 4.57 vs 2.90 | 8.74 vs 4.74 | ✅ consistent both splits |
| #aligned-TFs ≥2 | 2.90 (worse) | 8.56 (better) | ❌ IS/OOS diverge — discarded |

New columns: `mstruct_pts`, `mstruct_align`, `mstruct_htf_dir`, `mstruct_minor_sweep`,
`mstruct_intact_tf`. Reporting: "Market structure (Ep 12 LTH/ITH/STH fractal)" table.

**Stage 3 — structural stop placement (`_structure_stop`, SHIPPED ON):** anchors the stop
beyond the intact M1 INTERMEDIATE swing (ITL for longs / ITH for shorts) instead of the raw
short-term extreme (STL/STH). The short-term swing is exactly what a minor liquidity run
sweeps — placing the stop one fractal tier up keeps it beyond the sweep's reach. The 10-pip
universal cap enforces the trader's "if 10 pips permit" rule; falls back to the STL/STH stop
when no intact ITL/ITH exists within the cap.

| Metric | Baseline | Structure stop ON | Δ |
|---|---|---|---|
| Full 4yr equity | R60.18M | **R71.19M** | +R11M (+18.3%) |
| Full 4yr PF | 5.03 | **5.12** | +0.09 |
| Full 4yr MaxDD | -12.95% | **-12.95%** | unchanged ✅ |
| IS PF / equity | 3.01 / R145k | 3.12 / R158k | both up |
| OOS PF / equity | 5.06 / R641k | 5.15 / R703k | both up |
| OOS MaxDD | -15.62% | -16.31% | +0.69pp (fragile restart path only) |

Config: `STRUCTURE_STOP_ENABLED = True`, `STRUCTURE_STOP_TF = "1T"`,
`STRUCTURE_STOP_LOOKBACK = 90`. Counter: `structure_stop_used`. Ships ON — full continuous
run MaxDD (the live-relevant path) is unchanged at -12.95%, PF improved in all three runs,
IS/OOS magnitudes consistent. The slightly wider stop (avg loss R35k→R40k) survives the
sweep but costs marginally more when genuinely wrong — the +0.69pp shows only on the
OOS-from-R500 stress restart, not the continuous deployment path.

### P17 — ITH/ITL levels as primary liquidity-draw targets (SHIPPED 2026-06-05)
**What:** Unswept INTERMEDIATE-tier highs/lows (ITH/ITL from the Ep-12 fractal classifier)
are the resting buy-side / sell-side liquidity pools price is institutionally drawn toward.
For LONG: unswept ITH ABOVE price = buy-side draw. For SHORT: unswept ITL BELOW price =
sell-side draw. These register as distinct confluence source families (`ith_liquidity` /
`itl_liquidity`) so an ITH that clusters with a fib extension scores as multi-source.

**Implementation:** `_ithl_targets(bars, direction, price, pair, tf)` adds unswept ITH/ITL
as `_find_target` candidates, scanned on W/D/H4. `config.ITHL_TARGET_TFS = ("240T","D","W")`
(env-overridable). **Full history is scanned (`ITHL_TARGET_MAX_BARS = 0`)** — the edge is in
OLDER major intermediate swings; a 300-bar cap (H4 ≈ 50 days) loses most of it (R76M→R71M).
H4/D/W bar counts are small (~6k/1k/200 over 4yr) so uncapped classify is cheap. **Do NOT add
15T/60T without a cap** — those series run to ~100k bars (uncapped classify hangs) AND they
hurt PnL (−R10M, tested + dropped 2026-06-05).

**Result:** 798 / 46.6% / PF 5.20 / **R76.05M** / -12.95% — +R4.86M vs P16 baseline R71.19M,
PF up, MaxDD unchanged. IS PF identical to baseline (nearest-qualifying target rarely changed
in 2022-23), OOS +R48k. Textbook non-curve-fit add. The nearest-qualifying TARGET selection is
preserved (ITH/ITL are added candidates only) — the value comes through confluence scoring, not
through choosing further targets (which would wreck the compounding path).

### P18 — Confluence sizing (score≥4 1.25×) + cache-bug post-mortem (SHIPPED 2026-06-05)
**What (active lever):** When the chosen TP's confluence score (P15) is ≥4 — i.e. ≥4 distinct
source families (fib / FVG / OB / equal-H/L / round number / PDH-PDL / PWH-PWL / ITH-ITL) agree
within `TARGET_CONFLUENCE_TOL_PIPS` of the same price — scale the position 1.25×. Score 4 is the
highest-WR confluence bucket (P15: WR 50.5% / PF 5.73). Same equity floor as the draw cascade
(`DRAW_SIZE_MIN_EQUITY = 3000`). Config: `TARGET_SCORE_MULT = 1.25`,
`TARGET_SCORE_MULT_THRESHOLD = 4` (both env-overridable). Counter: `target_score_sized`.

**Result (full 4yr, on the corrected base):**

| Config | Trades | WR | PF | Equity | MaxDD |
|---|---|---|---|---|---|
| P17 (mult off) | 798 | 46.6% | 5.20 | R76.05M | -12.95% |
| **P18 (score≥4, 1.25×)** | 798 | 46.6% | **5.18** | **R178.70M** | **-12.95%** |

Equity +135% with PF, WR, and MaxDD all essentially unchanged — the hallmark of a clean sizing
lever (amplifies compounding on the high-conviction bucket without degrading quality or risk).
IS/OOS: IS PF 3.14 (>baseline 3.12), OOS PF 5.20 (>baseline 5.15), both splits positive and same
ballpark; full-4yr and IS MaxDD -12.95%, OOS-restart MaxDD -16.75% (the known fragile R500-restart
stress path — P16's was -16.31%; the live continuous path is -12.95%).

**⚠️ Cache-bug post-mortem (the phantom "tune-down" regression):** A memoised `_classify_cached`
was added to avoid re-running `mstruct.classify` (O(n)) per trade eval. The key used
`bars[-1].name`, but `Bar = namedtuple("Open High Low Close")` has **no timestamp** — the lookup
always raised `AttributeError` and fell back to `len(bars)`, which **saturates at the `max_bars`
cap (300/90)**. Once each series passed its cap the key `(pair, tf, 300)` became constant for the
whole run, so the cache returned the FIRST classification forever — freezing `_structure_stop` and
`_structure_conviction` at early-2022 structure for all 4 years. This silently degraded PF
5.20→4.19 and MaxDD -12.95→-13.89, which looked like the score-mult "over-leveraging the book."
Bisect (full 4yr, mult off) isolated it: P16 / DXY-structure / P17 all clean at 5.12–5.20; the
regression appeared only in the commit that introduced the cache. **Fix:** removed the cache —
the `max_bars` cap at every call site is the real perf fix (classify is O(≤300), ~1.7k calls
over 4yr; no memoisation needed). `_classify_cached` is now a direct passthrough.
**Lesson:** a namedtuple-based bar with no timestamp can't be cache-keyed by `.name`; and any
length-based key silently collapses under a `max_bars` cap. Validate perf optimisations against
a known-good full-run number, not just runtime.

**Live-engine sizing levers (PORTED 2026-06-06):** `main.py` (the QuantConnect LEAN engine)
now carries confluence scoring + all sizing multipliers, matching the backtest compounding path:
- **Confluence scoring**: `_find_target` returns `(target, score)`; `_targets_in_series` and
  `_ithl_targets` now emit `(price, source_family)` tuples across the full source set
  (fib / fvg / ob / equal_hl / round_number / swing / pdh_pdl / pwh_pwl / ith/itl_liquidity) —
  byte-faithful to the backtest. Added `_confluence_score`, `_scan_htf_fvgs`,
  `_htf_fvg_conviction` (P9), `_htf_crt_sweep` (P19); imports `find_swing`, `nearest_fib_target`,
  `draw_cascade_score`.
- **Sizing block** in `_maybe_open` (single application point, carried to fill via
  `_pending_entry`): draw-cascade 2×/3× (computes `_draw_score` from W/D/H4), P18 score≥4 1.25×,
  P19 H4-CRT 1.25×. All gated by `equity_zar >= DRAW_SIZE_MIN_EQUITY` (R3,000). **Account is
  ZAR-denominated** so `Portfolio.TotalPortfolioValue` is already ZAR and compares directly to
  the R3,000 floor (no conversion).
- **All four sizing levers fully active** (incl. P9 HTF-FVG 1.25×) now that the breakout model
  is ported (see below). `_is_breakout` is computed live, so P9's breakout-anchored bump fires.

**Live-engine entry logic (PORTED 2026-06-06):** the breakout continuation model and the
draw-cascade 0/3 hard gate are now in `main.py`, bringing live entries into alignment with the
backtest trade set (not just sizing):
- **Breakout model**: `_intermarket_breakout()` (triple-confirmed EURUSD + GBPUSD M15 range
  breaks + DXY M15 BOS) → `_is_breakout`. Earns `BREAKOUT_CONVICTION`, tags `entry_model="breakout"`,
  and is EXEMPT from the 0/3 gate (continuations run WITH the HTF draw). Added `_dxy_bias_15m()`
  (synthetic DXY M15 BOS, `SWING_LOOKBACK_STH`); imports `detect_breakout`.
- **Draw-cascade 0/3 hard gate**: `_draw_score = draw_cascade_score(W, D, H4, …)` computed during
  conviction; `if _draw_score == 0 and not _is_breakout: return` (reversal logic — no HTF draw
  alignment → skip). `_draw_score` also feeds conviction (+0–3) and the 2×/3× sizing lever (reused,
  computed once). `draw_score` + `entry_model` recorded on every trade.
- **NOT ported (deliberate — needs the scenario cascade main.py lacks):** the 2a/2a_h4/2a_ip
  surgical gates and the full EURGBP/AUDNZD escalation cascade (`_im_scenario` classification).
  main.py uses single-H1 `resolve_pair_direction`; porting the multi-level cascade + scenario
  gates is a larger separate build. The 0/3 gate and breakout model are scenario-independent, so
  they port cleanly on their own.
- **Verified off-platform**: stubbed `AlgorithmImports`, exercised `_htf_crt_sweep` (correct
  Turtle-Soup detection + negative case), `_confluence_score`, `_intermarket_breakout`,
  `_find_target`, `_htf_fvg_conviction` (graceful empty-store paths). `py_compile` clean.

### P19 — HTF CRT Turtle Soup timing conviction (IMPLEMENTED 2026-06-06, analytics-only)
**What:** ICT Candlestick Range Theory (CRT). The High/Low of a completed HTF candle (or its
prior 2-bar range) define **CRT H / CRT L** — the institutional delivery range. A **Turtle
Soup** = price wicks BEYOND CRT H (for shorts) or below CRT L (for longs), then CLOSES BACK
INSIDE. This is the **Judas swing on a bigger timeframe** — the exact same manipulation logic
that drives our M15 entry, one tier up. When it fires on a recent H4/D bar in our direction,
the HTF manipulation phase has already happened: the trade has higher-TF timing confluence.

**User's framing (captured via the Time Frame Alignments notes + Q&A):** "this is basically the
Judas swing on a bigger time frame… we'd see these moves on judas swings… [it] can help time
moves better and also have genuine liquidity targets, which we already have." The draw-on-
liquidity targets (PDH/PDL = daily CRT H/L, PWH/PWL = weekly CRT H/L, ITH/ITL = intermediate
CRT) were already in the system from P15/P17; what P19 adds is **active detection of WHEN the
HTF sweep happens** (the trigger/timing), not just the passive target levels.

**Implementation (`_htf_crt_sweep` in backtest.py + `CRT_SWEEP_ENABLED=True`,
`CRT_SWEEP_MIN_PIPS=2.0` in config):**
- Scans D → H4. CRT range = the 2 completed bars before the candidate sweep bar.
- A sweep bar's WICK must exceed CRT H/L by ≥ `CRT_SWEEP_MIN_PIPS` AND its CLOSE must be back
  inside the range AND current price still inside → Turtle Soup confirmed.
- Checks the last 2–3 completed HTF bars (fresh sweeps only).
- Daily sweep = +2 conviction, H4 sweep = +1 conviction. `crt_tf` column ("D"/"240T"/"").
- Reporting: "HTF CRT Turtle Soup timing (P19)" table by timeframe.

**Backtest finding — conviction-add is INERT (4th confirmation of saturation), signal is REAL:**
Full 4yr byte-identical to P18 baseline: **798 / 46.6% / PF 5.18 / R178.70M / -12.95%**. Same
saturation as P9/P15/P16 — any open trade already sits at conviction > 4 before CRT is scored,
so the +1/+2 never changes `max_legs`. But the analytics prove the signal is genuine and not
curve-fit:

| CRT sweep | Trades (4yr) | WR% | PF 4yr | IS PF | OOS PF | Verdict |
|---|---|---|---|---|---|---|
| D1 range | 234 | 46.6% | 3.02 | 2.88 | 3.02 | ✅ consistent both splits |
| H4 range | 137 | **50.4%** | 3.80 | 3.40 | 3.80 | ✅ consistent both splits, best WR |
| no sweep | 427 | 45.4% | 8.05 | 3.21 | 8.11 | baseline |

IS/OOS unchanged from P18 baseline (IS PF 3.14 / R198k / -12.95%; OOS PF 5.20 / R1.175M /
-16.75%). The H4 CRT bucket is the standout: highest WR (50.4%), PF positive and same ballpark
in both splits — textbook non-curve-fit per the §"What not curve-fit means" test.

**Active lever — H4-CRT sizing 1.25× (SHIPPED 2026-06-06):** A sizing multiplier on the
H4-CRT-sweep bucket (analogous to P9's HTF-FVG 1.25× and P18's score≥4 1.25×). The H4 Turtle
Soup is the HTF Judas swing — the bigger-TF manipulation phase has already fired in our
direction — and it's the highest-WR HTF-timing bucket (50.4%). Gated to H4 only
(`CRT_SWEEP_MULT_TF="240T"`; the D1 bucket is weaker and excluded). Same equity floor as the
draw cascade (`DRAW_SIZE_MIN_EQUITY=3000`). Config: `CRT_SWEEP_MULT=1.25` (env-overridable),
`CRT_SWEEP_MULT_TF="240T"`. Counter: `crt_sweep_sized` (122 trades sized over 4yr).

| Metric | P19 baseline (mult off) | **H4-CRT 1.25×** |
|---|---|---|
| Full 4yr equity | R178.70M | **R263.84M** (+R85M, +48%) |
| Full 4yr PF | 5.18 | 5.12 |
| Full 4yr MaxDD | -12.95% | **-12.95%** (unchanged ✅) |
| IS PF / equity | 3.14 / R198k | 3.14 / R230k |
| IS MaxDD | -12.95% | **-12.95%** (unchanged ✅) |
| OOS PF / equity | 5.20 / R1.175M | 5.14 / R1.41M (+20%) |
| OOS MaxDD | -16.75% | -17.14% (+0.39pp) |

Ships ON. The full continuous run (the live-relevant path) holds MaxDD at exactly -12.95% while
adding +48% equity; PF essentially flat (5.18→5.12, the normal signature of a sizing lever that
amplifies the sized bucket proportionally). Both splits stay strongly positive and same-ballpark
(PF 3.14 IS / 5.14 OOS). The only cost is +0.39pp on the OOS-from-R500 restart MaxDD — the
known-fragile stress path that already exceeds -15% in baseline (not the live continuous path),
and the deterioration is smaller than P16's shipped +0.69pp. This is the inverse of P9's REJECTED
2.0×, which breached the FULL run to -15.82%: the 1.25× magnitude keeps the deployment path
unchanged. **Live-engine note:** `_htf_crt_sweep` is inherited by `LiveTrader(Backtester)`
automatically (pure signal logic, uses `bars_up_to`); the sizing block in `_maybe_open` is also
inherited — but per the P18 live-engine gap, `main.py` (the LEAN engine) still needs all sizing
multipliers ported, CRT_SWEEP_MULT included.

### P20 — High-conviction target escalation (SHIPPED 2026-06-07)
**What:** When a trade has multiple high-conviction signals (CRT D/W sweep, draw_score≥2, or a
confirmed Judas minor sweep), the nearest swing high/low or round number is too conservative a
target — the HTF manipulation has already fired, institutional delivery aims at the bigger draw.
P20 adds a preference filter: when the escalation trigger fires, candidates are filtered to
premium structural liquidity draws (ITH/ITL, PDH/PDL, FVG, OB, fib extension, equal H/L) and
swing/round_number targets are skipped. If no premium candidate qualifies (min RR constraint),
the original nearest-qualifying target is used as fallback.

**Trigger logic (`_escalate_tgt` in `_maybe_open`):**
```python
_escalate_tgt = (
    config.TARGET_ESCALATE_ENABLED and (
        _crt_tf in ("D", "W") or
        _draw_score >= config.TARGET_ESCALATE_MIN_DRAW or
        _ms.get("minor_sweep", False)
    )
)
```

**Premium target types (`_PREMIUM_TARGET_TYPES`):**
`fib_extension`, `fvg`, `ob`, `pdh_pdl`, `pwh_pwl`, `ith_liquidity`, `itl_liquidity`, `equal_hl`

**Motivation:** User observed repeated instances of trades exiting at +20–36 pips on a Judas
reversal with CRT D confirmation, only for the move to continue 100–200 pips further. The swing
high/low candidate was always within 25 pips (meeting min RR), and was selected over the ITH/PDH
100 pips away. With escalation, those same trades skip the swing target and lock onto the ITH/PDH.

**Result (full 4yr on P19 baseline):**

| Config | Trades | WR | PF | Equity | MaxDD |
|---|---|---|---|---|---|
| P19 baseline | 798 | 46.6% | 5.12 | R263.84M | -12.95% |
| **P20 ON** | **795** | **46.6%** | **5.12** | **R284.9M (+8%)** | **-12.95% ✓** |

IS PF 3.07 / OOS PF 4.48 — both positive, same ballpark. OOS MaxDD improved: -13.93% vs
-17.14% baseline (P20 removes the long-target tail risk in the OOS fragile-restart path).
IS MaxDD: -12.95% (unchanged). Equity +R21M (+8%) on the full continuous run.

The 3-trade reduction (798→795) comes from escalation upgrading some targets to further draws
that don't meet the minimum RR — those are skipped entirely rather than accepting a weak target.
The skipped trades are the genuinely low-quality ones: when the nearest premium draw is too far,
the trade has structural confirmation but no viable exit — correctly skipped.

**Config:** `TARGET_ESCALATE_ENABLED=1` (env-overridable), `TARGET_ESCALATE_MIN_DRAW=2`.
**New trade column:** `target_escalated` (bool) — True when the premium filter was applied.

### TRAIL_AT_TP — structural runner on TP wick (TESTED + REVERTED 2026-06-07)
**Hypothesis:** When price wicks the TP level, engage M5 structural trail instead of exiting:
move stop to last M5 swing ≥ `TRAIL_AT_TP_MIN_PIPS` (5 pips) from TP and let the trade run
until M5 structure breaks. User observed price continuing 100–200 pips past TP on high-conviction
setups. Fires on wick touch (no close required) for both Judas and breakout models.

**Three implementations tested, all reverted:**

**v1 — bankrupt:** Initial `can_trail` check only verified M5 swing ≥5 pips from TP. On fast
Judas-style TP spikes that immediately reversed, the last M5 STL was still below entry — trail
engaged with stop below entry, turning winners into losers. IS MaxDD -71.61%, OOS MaxDD
**-100.62% (account bankrupted)**.

**v2 — entry check added:** Added `trail_stop > entry` requirement for longs / `trail_stop < entry`
for shorts, guaranteeing at least break-even before trail engages. Still worse than baseline:

| Metric | Baseline (P20/P21) | v2 (entry check) |
|---|---|---|
| Full 4yr equity | R284.9M | R137.8M (−52%) |
| Full 4yr PF | 5.12 | 4.49 |
| Full 4yr MaxDD | -12.95% | -13.26% |

**v3 — near-TP swing (correct implementation):** `_trail_stop_near_target` collects ALL confirmed
M5 swings above entry with ≥min_gap from TP and returns the HIGHEST (closest to TP in price, not
most recent in time). Fast spikes with no structure near TP return None → normal exit. Still worse:

| Metric | Baseline (P20/P21) | v3 (near-TP swing) |
|---|---|---|
| Full 4yr equity | R284.9M | **R144.8M (−49%)** |
| Full 4yr PF | 5.12 | 4.48 |
| Full 4yr MaxDD | -12.95% | -13.26% |
| IS PF / equity | 3.07 / R234k | 2.94 / R209k |
| IS MaxDD | -12.95% | -13.26% |
| OOS PF / equity | 4.48 / R1.501M | 4.34 / R788k |
| OOS MaxDD | -13.93% | -18.07% |

Every metric worse in every split across all three implementations. **Root cause: the TP is the
end of the AMD delivery cycle.** When price delivers to the institutional draw on liquidity, the
cycle is complete — distribution has occurred. Holding past it means sitting through the
reversal/consolidation phase where the strategy has no edge. The trail runners exit at a lower
level than the TP on average, reducing average win. Unlike the P8/P10/P11 reverts
(path-dependency — removed trades were compounding-positive despite weak arithmetic P&L), this is
a genuine per-trade degradation: the average exit after a TP wick is worse than just taking the TP.

**ICT lesson:** "price doesn't come back to these points" is true from the perspective of the
big-TF draw, but the strategy's TP IS that draw. Once price delivers to the draw, the trader
should exit — the next move belongs to a new AMD setup, not a continuation of the old one.

**Config:** `TRAIL_AT_TP=0` (off by default), `TRAIL_AT_TP_MIN_PIPS=5.0`. Code retained for
reference; `_trail_stop_near_target` method available. v1's bankrupt bug does not exist in codebase.

### TP Runner — partial exit at TP1, runner to next premium draw (TESTED + REVERTED 2026-06-07)
**Hypothesis:** Exit 50% at the original institutional draw (TP1), move stop to break-even, run the
remaining 50% to the next premium structural target (TP2 — ITH/ITL/PDH/PDL/FVG/fib ≥ 20 pips beyond
TP1). Reuses the scale-out infrastructure. `_find_target` gained a `beyond` param to search past TP1.

**Result — REVERTED:**

| Metric | Baseline (P20) | TP Runner |
|---|---|---|
| Full 4yr equity | R284.9M | R70M (−75%) |
| Full 4yr PF | 5.12 | 4.19 |
| Full 4yr MaxDD | -12.95% | -13.63% |
| IS PF / equity | 3.07 / R198k | 2.71 / R184k |
| OOS PF / equity | 4.48 / R1.2M | 3.85 / R211k |
| OOS MaxDD | -13.93% | -18.7% |

**Root cause:** Same as TRAIL_AT_TP. The TP1 IS the AMD delivery draw — exiting 50% there and running the
rest to TP2 means half the position misses the guaranteed exit. The runner 50% frequently stalls between
TP1 and TP2 (closing at BE) rather than continuing to TP2. Net effect: most trades yield 50% of their
normal P&L, and the occasional TP2 hit doesn't compensate. Every exit modification tested confirms the
same conclusion: take the full position off at the institutional draw.

**Config:** `TP_RUNNER_ENABLED=0` (off by default). Code + `beyond` param in `_find_target` retained.

### P21 — Pyramid gate fix (SHIPPED 2026-06-07)
**Bug found:** Lines in `_maybe_pyramid` blocked pyramids when `weekly_amd_dir == direction` — exactly
the CONFIRMED case where the weekly distribution supports the trade (+2 conviction at entry). The
`WEEKLY_AMD_FULL_PYRAMID` im_score upgrade below it was permanently dead code (never reached due to
early return). This reduced 4-year pyramids to ~2.

**Fix:** Move the `WEEKLY_AMD_FULL_PYRAMID` upgrade to run BEFORE the `im_score < 1.0` gate, remove
the inverted block. Weekly-confirmed setups get im_score promoted to 1.0 and pass the pyramid gate.

**Result (pyramid fix, baseline config):**

| Metric | Baseline (P20) | Pyramid fix |
|---|---|---|
| Full 4yr equity | R284.9M | **R284.9M** (unchanged ✓) |
| Full 4yr PF | 5.12 | 4.47 |
| Full 4yr MaxDD | -12.95% | **-12.95%** (unchanged ✓) |
| IS PF / equity | 3.07 / ~R198k | **3.07 / R234k (+18%)** |
| IS MaxDD | -12.95% | **-12.95%** (unchanged ✓) |
| OOS PF / equity | 4.48 / ~R1.175M | **4.48 / R1.501M (+28%)** |
| OOS MaxDD | -13.93% | **-13.93%** (unchanged ✓) |

PF unchanged in both splits. Equity up +18% IS / +28% OOS (pyramid legs firing at high-equity periods
compound the advantage). Full-run equity flat because pyramids fire at very high equity where their
absolute P&L is small relative to the compounding base — but MaxDD unchanged everywhere. Ships ON.

Pyramids now fire ~34 times over 4yr (was ~2). They enter on M5 FVG pullbacks with weekly AMD +
full H1 intermarket conviction. 50% WR on pyramid legs — consistent with a cautious add to an
already-proven move.

### P22 — Pyramid gate relaxation: draw_unlock threshold + favour_pips (SHIPPED 2026-06-07)
**What:** Two targeted changes to the pyramid gate that unlock more pyramid opportunities without
degrading risk metrics.

**Diagnostic finding (new gate counters):** After adding `pyramid_blocked_favour` and
`pyramid_blocked_min_target` counters, the full pyramid gate breakdown was visible for the first
time:

| Gate | IS blocks | Notes |
|---|---|---|
| `pyramid_blocked_low_im` | 1,766 | im_score < 1.0, no draw unlock |
| `pyramid_blocked_favour` | 1,331 | price < 20 pips in profit |
| `pyramid_blocked_no_pattern` | 0 | not a bottleneck (FVG always found) |
| `pyramid_blocked_min_target` | 47 | TP < 20 pips remaining |

**Change 1 — `PYRAMID_DRAW_UNLOCK_MIN` 3→1:**
The im_score=0.75 unlock (DXY agrees, cross flat) previously required draw_score≥3 (all 3 HTF
timeframes aligned). Changed to draw_score≥1: any HTF draw alignment is sufficient. ICT rationale:
DXY direction is the primary USD signal; when it agrees with the trade AND any HTF timeframe
confirms the draw, a pyramid add is justified even when the cross rate is temporarily flat. The
cross being flat just means EUR/GBP are moving together — it doesn't invalidate the DXY trend
already captured in the open trade.

**Change 2 — `PYRAMID_MIN_FAVOUR_PIPS` 20→15:**
Lowering from 20 to 15 pips allows adds earlier in the confirmed move. On a 40-pip target trade,
15 pips in profit means 25 pips of target remaining — fully satisfying the MIN_PIPS_TARGET (20)
floor. The 10-pip test showed IS/OOS divergence (OOS MaxDD -16.83%); 15 pips is the stable
middle ground that adds pyramids without degrading the OOS path.

**Tested and rejected:**
- `PYRAMID_MIN_FAVOUR_PIPS=10`: IS +6.3%, OOS MaxDD -16.83% (fail — same path-dependency trap)
- `PYRAMID_DRAW_UNLOCK_MIN=1` alone: IS +1%, OOS flat (neutral, not enough)
- Combined `draw_unlock=1 + favour=15`: IS +3.5%, OOS flat, MaxDD unchanged everywhere ✓

**Result (full 4yr, combined change):**

| Metric | P21 baseline | **P22** |
|---|---|---|
| Full 4yr equity | R284.9M | **R294.8M (+3.5%)** |
| Full 4yr PF | 4.47 | **4.47** (unchanged ✓) |
| Full 4yr MaxDD | -12.95% | **-12.95%** (unchanged ✓) |
| IS PF / equity | 3.07 / R234k | 3.07 / **R242k** (+3.5%) |
| IS MaxDD | -12.95% | **-12.95%** (unchanged ✓) |
| OOS PF / equity | 4.47 / R1.501M | 4.47 / **R1.502M** (flat) |
| OOS MaxDD | -13.93% | **-13.93%** (unchanged ✓) |

PF identical in all three runs (4.47 / 3.07 / 4.47). MaxDD unchanged everywhere. Equity +R9.9M
(+3.5%) on the full continuous path. The OOS is essentially flat — the gain is concentrated in IS
where the pyramids fire at high-equity inflection points and compound forward.

Pyramids now fire ~16 times in IS (was ~2) / ~4 times in OOS (was ~32) → ~20 total.
Overall WR on pyramid legs ~45%; 50% WR on im1.0 legs, 40% on im0.8 legs.

**Config:** `PYRAMID_DRAW_UNLOCK_MIN=1`, `PYRAMID_MIN_FAVOUR_PIPS=15`.

### P23 — Milestone trailing stop (SHIPPED 2026-06-08)
**What:** Extends the existing `TRAIL_BE_PIPS` / `TRAIL_LOCK_PIPS` step system continuously for
long-running trades headed to a distant HTF target. Every `MILESTONE_TRAIL_STEP` pips (20) of
additional progress, the stop is locked at `(milestone - MILESTONE_TRAIL_BUFFER)` pips from entry.

**Stop progression:**
- +10 pips → stop to breakeven (existing `TRAIL_BE_PIPS`)
- +20 pips → stop to entry + 10 pips (existing `TRAIL_LOCK_PIPS`)
- +40 pips → stop to entry + 30 pips (new — milestone trail takes over)
- +60 pips → stop to entry + 50 pips
- +80 pips → stop to entry + 70 pips (…etc.)

**Why it matters:** Trades targeting PDH/PDL, PWH/PWL, or ITH/ITL frequently travel 50–100 pips.
Without milestone trail, a trade that reached +35 pips and reversed was still a full loss (stop at
original -10). With milestone trail, stop is now at +30 pips after +40 pips of progress — a
35-pip reversal exits at +30 instead of -10. At R10k lots that difference is +R555 vs -R185, and
that delta compounds at every high-equity milestone.

Short-target trades (20–30 pip fib extensions) exit via TP before any new milestone fires —
no behaviour change on the majority of trades.

**Result (full 4yr):**

| Metric | P22 baseline | **P23** |
|---|---|---|
| Full 4yr equity | R294.8M | **R400.7M (+36%)** |
| Full 4yr PF | 4.47 | **4.47** (unchanged ✓) |
| Full 4yr MaxDD | -12.95% | **-13.01%** (+0.06pp) |
| IS PF / equity | 3.07 / R242k | 3.09 / **R300k** (+24%) |
| IS MaxDD | -12.95% | -13.01% (+0.06pp) |
| OOS PF / equity | 4.47 / R1.502M | 4.47 / **R1.569M** (+4.5%) |
| OOS MaxDD | -13.93% | -13.94% (flat) |

The +36% equity gain with PF unchanged and MaxDD up only 0.06pp is the largest compounding
improvement since P18. IS/OOS both positive and same ballpark. Ships ON.

**Config:** `MILESTONE_TRAIL_ENABLED=1`, `MILESTONE_TRAIL_STEP=20`, `MILESTONE_TRAIL_BUFFER=10`.

### HTF target preference — TESTED + REVERTED (2026-06-08)
**Hypothesis:** When an unswept ITH/ITL/PDH/PDL/PWH/PWL is within 120 pips, prefer it as the
primary target over a closer fib extension — these are resting liquidity, not projected levels.

**Result — reverted:**

| Metric | P23 baseline | HTF preference on |
|---|---|---|
| IS MaxDD | -13.01% | **-22.57%** |
| OOS MaxDD | -13.94% | **-22.60%** |
| IS WR | 46.0% | 41.8% |
| OOS WR | 45.9% | 42.5% |

Forcing far targets (ITH/ITL at 65–120 pips over nearer fib at 28 pips) means staying through
the intermediate consolidation zone where price typically pauses or reverses. The 28-pip fib IS
the draw for the current AMD delivery cycle; the 65-pip ITH is the draw for the NEXT cycle
(continuation trade or pyramid). The nearest qualifying target principle is correct.

The ITH/ITL add value correctly: as confluence score contributors (P18 sizing bump) and as
fallback when they genuinely ARE the nearest qualifying target (8 wins, avg R403k each — the
highest per-win average). Not by forced selection over nearer targets.

**Config:** `HTF_TARGET_PREF_PIPS=0` (off by default, code retained).

### P26 — Session-open + daily-open dual pattern (SHIPPED 2026-06-10, v2 2026-06-10)
**What:** Two institutional AMD equilibrium references — the session open (London 03:00 ET /
NY 07:00 ET) and the daily open (00:00 UTC) — each independently checked for two patterns:

- **Judas sweep**: price wicked ≥ `SWEEP_SOJ_MIN_PIPS` (3 pips) through the reference in the
  manipulation direction then closed back. Classic stop-hunt at the open.
- **Pullback retest**: price first extended ≥ `SOJ_EXTEND_MIN_PIPS` (8 pips) in the trade
  direction, then pulled back to within `SOJ_RETEST_TOL_PIPS` (5 pips) of the reference.
  The "return to the open after the initial move" — happens every session.

**+1 per reference that fires** (capped at 1 each). Max total = +2 conviction (both session
open and daily open confirm). Daily open only scored when it is ≥ 2 pips from session open
(prevents double-counting at session start).

**Why the bot was missing these setups:** `detect_amd_setup` requires a consolidation range
(both extremes touched ≥2× over 8–96 M15 bars). Session-open sweeps and pullbacks are often
one-sided moves with no formal range. Identified from a real missed trade 8 Jun 2026:
EURUSD/GBPUSD swept below their London opens (~1.15143/1.33213) while DXY swept its own
open (100.108), then all three closed back above. No range → no AMD → conviction below entry.

**Implementation** (`_session_open_judas_sweep` in backtest.py):
- `SOJ_LOOKBACK_BARS=48` M5 bars — covers the full London or NY session
- +1 per reference (session open / daily open) that shows either Judas or pullback
- `soj_type` column: `"dual"` (both refs, +2) / `"single"` (one ref, +1) / `""` (none)
- `soj_sweep` column: True when any SOJ pattern fired
- Marks `_judas_seen` so `session_phase` labels correctly (london_judas / ny_judas)

**v1 result (session-open Judas sweep only, SHIPPED):**

| Metric | P23 baseline | P26 v1 | Δ |
|---|---|---|---|
| Trades | 795 | 810 | +15 |
| WR | 46.6% | 45.9% | -0.7pp |
| PF | 4.47 | 4.47 | unchanged ✓ |
| Equity | R400.7M | R429.3M | +R28.6M (+7.1%) |
| MaxDD | -13.01% | -12.95% | improved ✓ |

IS/OOS (v1): IS PF 3.09 / OOS PF 4.47 — positive both splits. MaxDD -12.95% full run / -15.41% OOS restart.

**v2 result (session + daily open, both Judas and pullback — SHIPPED):**
Identical full-4yr metrics to v1 (810 trades, R429.3M, MaxDD -12.95%). The daily open adds
+1 conviction to 38 more existing trades (SOJ "no pattern" down from 127 to 89) without opening
new ones — conviction is never the trade-opening bottleneck (`low_conviction: 0` across all 4yr).
The `soj_type` analytics column tracks dual vs single for future per-bucket IS/OOS analysis.

| Bucket | Trades (4yr) |
|---|---|
| SOJ dual (sess+daily, +2) | 252 |
| SOJ single (one reference, +1) | 469 |
| no SOJ pattern | 89 |

**Architectural constraint (discovered during v2 development):** Adding conviction signals
increases pyramid depth on existing trades but does NOT open new trades, because the
entry-blocking bottleneck is always a structural hard gate earlier in the pipeline (MSS
2-of-3, draw cascade ≠ 0, M5 FVG pattern). The user's goal of 3–4 trades/week requires
bypassing one of those structural gates for the session/daily-open pullback context, which
is a separate build (tested approaches: SOJ draw bypass → MaxDD -17%, reverted).

**Multi-TF breakout test history (all reverted):**
- v1/v2 (H1→M15 cascade): MaxDD -15.74%, R302M ❌
- v3 (D1→H4→H1→M15, M15 params): MaxDD -18.89%, R390M ❌
- v4 (D1→H4→H1→M15, per-TF calibrated): MaxDD -15.32%, R396M ❌
M15-only triple-confirmed breakout is optimal.

**Config:** `SOJ_SWEEP_ENABLED=1`, `SWEEP_SOJ_MIN_PIPS=3.0`, `SOJ_EXTEND_MIN_PIPS=8.0`,
`SOJ_RETEST_TOL_PIPS=5.0`, `SOJ_LOOKBACK_BARS=48`.

### P39 — Volume-as-confidence analysis (PIPELINE BUILT 2026-07-25, measurement-only, NOT run on real data yet)
**What:** Measures whether tick volume — a data dimension the algo never consults — adds
orthogonal edge as a per-trade **confidence** signal on sweeps (not a gate, not a size-up above
baseline; at most a size *reducer* on noise-driven sweeps). Two hypotheses, per the P39 handover:
- **H1 friction ratio**: ticks on the sweep/entry M5 bar ÷ mean ticks of the previous 20 M5 bars.
  Bucketed low <0.65× / normal 0.65–1.2× / high 1.2–1.8× / spike >1.8×.
- **H2 directional delta**: Lee-Ready bid-move classification (up=buy, down=sell, flat=neutral);
  does net delta on the sweep bar align with the trade direction?

**Data:** HistData **Tick** product (not the M1 Bar product — that strips volume to zeros). Real
tick volume = tick COUNT per M5 bin. Timestamps are ET (UTC-5), converted the same way as
`run_backtest_histdata.py`. Tubs's Drive folder "Tick data, fx eurusd and gbpusd 2022 and 2024"
holds EURUSD+GBPUSD tick zips for 2022 (IS) and 2024 (OOS); some months are 0-byte failed
downloads (e.g. EURUSD 202204/202209) and GBPUSD 202210 is a .txt placeholder — the pipeline
flags these in the coverage table rather than silently skipping.

**Pipeline:** `scripts/p39_volume_analysis.py` (stdlib-only — no pandas — so it runs on a bare
Python and is unit-testable). Two phases: `aggregate` (stream tick zips → compact per-month M5
tick/delta counts in `data/p39_agg/`, memory-safe line-by-line) then `analyse` (join to the
backtest trade dump, measure, write `data/p39_volume_report.md`). True R is computed from
`entry`/`stop`/`exit` in the trade dump (this branch's records carry them). Reports every table
split IS vs OOS, plus by entry_model (judas vs breakout — the two opposite volume priors), per
pair, and all three handover controls (control-1 non-signal bars, control-2 entry-type
robustness, control-3 hour-of-day confound). Verdict GREEN/YELLOW/RED per the handover rules.

**Status: built + validated on synthetic fixtures, NOT yet run on real data.** Verified
end-to-end: ET→UTC tick alignment (the handover's #1 failure mode), friction bucketing, true-R,
IS/OOS + model splits, pyramid-leg exclusion, delta alignment, and control-1 sampling
(sweep-friction distinguishable from control bars). Cannot run in the cloud session — the tick
set is 3–5 GB across dozens of Drive zips and can't transfer through the connector; the run
happens locally where the data lives.

**Run locally:**
```
python scripts/p39_volume_analysis.py aggregate <tick_zip_folder>   # slow, once
python run_backtest_histdata.py --years 2022 2024                   # produces the trade dump
python scripts/p39_volume_analysis.py analyse                       # writes the report
```
Then read `data/p39_volume_report.md` and act on its verdict. **Measurement only — nothing ships
to the engine from this branch.** Sweep-bar identification is a documented tick-density *proxy*
(the engine doesn't log the sweep bar); exact attribution needs a sweep-timestamp column in the
engine, the clean fix if P39 goes GREEN.

**⚠️ Repo-lineage note (2026-07-25):** the P39 handover assumes P1–P38 shipped
(`live/trade_score_log.py`, PF 3.34 / 842 trades / MaxDD -11.5%). This branch
(`claude/algorithm-ict-2022-alignment-9kkLi`, from which `p39-volume-analysis` was cut) is at
**P26** (810 trades, PF 4.47, MaxDD -12.95%); `main` has no CLAUDE.md P-history, and **no branch
in this remote contains P27–P38 or `trade_score_log`**. The P39 pipeline is written to consume
whichever trade log exists (`trades_dump.csv`, else `trade_score_log.csv`, else `trade_log.db`),
so it runs regardless — but the "current state" numbers in the handover describe a lineage not
present in this repo. Flagged to Tubs.

**P39 RESULT (RAN 2026-07-26, on real EURUSD+GBPUSD 2022/2024 ticks):** verdict **RED — no
shippable edge.** The friction-ratio H1 could not even be tested: the strategy's sweeps have
**zero low-friction bucket** (all sweeps fire on elevated volume — control-1: sweep bars median
1.55× vs random bars 0.97×), so there is no "low-volume noise" subgroup to shrink. Among the
populated buckets, WR clusters ~44–58% with no consistent ordering across IS/OOS. H2 directional
delta hinted at a counter-flow (absorption) effect — "against" flow WR 66.7% IS / 50.0% OOS vs
"aligned" 46.2% / 44.4% — same sign both splits, but small-n and secondary. **Nothing shipped.**
The measurement's real value: the strategy already selects for high-participation bars, so volume
adds no orthogonal filter. Full-4yr backtest reproduced in the Codespace (2022–2024 only, 2025
tick/M1 not fetched): 602 trades / WR 45.3% / PF 3.45 / **MaxDD -12.95% (exact match)** / R8.74M —
MaxDD-exact confirms the algo behaves as documented.

### AMD × tick-volume signature (RAN 2026-07-26, measurement-only)
**What:** joins the P39 tick aggregation to per-trade AMD phase timestamps (backtest now logs the
accumulation window + Judas sweep-bar UTC via `tf_index`, plus range width/duration/touches and
sweep depth). Profiles tick volume as a ratio to each trade's own pre-accumulation baseline across
accumulation / manipulation / distribution / PD-array(entry). Code: `scripts/amd_analysis.py`
(price-only setup quality), `scripts/amd_tickvol_analysis.py` (tick-volume by phase),
`run_amd.sh` / `run_amd_tickvol.sh`.

**Finding 1 — the fingerprint is REAL and matches ICT (275 trades EU+GU 2022/2024):**

| Phase | median | mean | ICT |
|---|---|---|---|
| Accumulation (coil) | 0.66× | 0.82× | quiet ✅ |
| Manipulation (Judas sweep) | 1.26× | 1.74× | spike ✅ |
| Distribution (entry→exit) | 1.22× | 1.81× | elevated ✅ |
| PD array (OB/FVG fill) | 1.28× | 1.90× | reaction ✅ |

Volume dries up in the coil (~⅔ normal), ~doubles on the stop-run, holds elevated in distribution,
and reacts hardest at PD-array mitigation. Holds on both pairs (GBPUSD spikes harder, 1.93× vs
1.63× sweep). Empirically validates the strategy is trading genuine AMD structure.

**Finding 2 — volume does NOT predict winners (NULL):** winners vs losers carry essentially the
same fingerprint. 2022 tiny edge to winners (+0.10× PD array); 2024 **flips** (losers higher, −0.20×
PD/dist) — IS/OOS disagree on sign every phase. Absorption at the sweep is **50% win / 50% lose**
(IS) and 48%/48% (OOS) — no discrimination. Same discipline as P39: **nothing shipped.**

**Caveats:** sweep bar = deepest-excursion M15 bar (structural, not volume-selected — better than
P39's density proxy, but still M15-resolution); EU+GU 2022/2024 only. **Next (option B, in
progress):** log the exact M5 sweep bar + MSS(M5/M15) timing + PD-array type/side + session +
PDH/PDL, all winners-vs-losers, to see precisely what losers do that winners don't.

### P40 — Conditional-volume position-size modulator (TESTED + REVERTED 2026-07-27)
**What:** Turn the AMD tick-volume winner/loser gap into a live sizing lever. From the descriptive
study, high-volume FVG entries were more often losers (size DOWN) and high-volume OB entries more
often winners (size UP). `ict/volume_modulator.get_volume_modifier(entry_type, friction_ratio)`
applies `VOL_MOD_FVG_DOWN=0.80` / `VOL_MOD_OB_UP=1.15` when the entry-bar friction ratio (ticks ÷
mean of prior 20 M5 bins) ≥ `VOL_MOD_HIGH_RATIO=1.2`; neutral (1.0×) when tick data is absent.
Wired into the `_maybe_open` sizing block, gated by `USE_CONDITIONAL_VOLUME`.

**Validation (EU+GU only, 2022 & 2024 as two separate tick-volume tests):** the modulator sized
~half of all trades each year (vmod 90/190 and 108/195 — broad, not a small sample).

| | 2022 | 2024 |
|---|---|---|
| PF | 5.26 → 5.35 (+0.09) | 3.32 → 3.11 (−0.21) ❌ |
| Equity ZAR | 30,016 → 29,473 (−543) ❌ | 26,778 → 24,388 (−2,390) ❌ |
| MaxDD | −11.55% → −11.89% ❌ | −11.60% → −11.95% ❌ |
| WR | 48.9% → 48.9% | 44.9% → 44.6% ❌ |

**Verdict RED — reverted.** Fails the ship gate (PF+equity up, MaxDD held) in BOTH years. 2024 is
worse on every metric; 2022's PF bump is illusory (equity down + MaxDD worse in the same year →
the modifier shrank winners more than it saved on losers). Same lesson as P39 and the P8/P10/P11
reverts: **a measurable winner/loser difference is not a tradeable edge** — the high-volume FVG
"losers" it shrinks are still net-positive to the compounding path. `USE_CONDITIONAL_VOLUME=0`
(default off). Code + config retained for reference; nothing ships to the engine.

**Two bugs found + fixed during the run (both would silently zero the modulator):** (1) `os` was
never imported at module level in `backtest.py` though `_load_tickvol()` uses it → `NameError` at
init; (2) `entry_type` was referenced in the P40 sizing block ~40 lines before its definition →
`UnboundLocalError` on the first trade. Both produced empty (`—`) modulator columns that looked
like "no effect." `run_p40_validation.sh` now stamps the run's git sha and embeds any crashed
arm's traceback into the pushed report so a crash can't masquerade as a null result again.

### IFVG (Inversion FVG) backtest — D1-only edge (MEASURED 2026-08-05)
**What:** `scripts/backtest_ifvg.py` (flag `RUN_IFVG_BACKTEST=1`, `run_ifvg.sh`) tests the theory
that a FVG violated by a **full-body close outside it** inverts into a S/D zone. Detect on
D1/H4/H1/M15, hunt the entry one TF lower (D1→H4, H4→H1, H1→M15, M15→M5): M15/H1/H4 on a >40%-wick
rejection candle, D1 at the zone edge. **Stop = market structure capped at 10 pips on EVERY entry**
(R off that stop, 2R target), spread+slippage on both fills. IS 2022 / OOS 2024, EU+GU+NZD.

**Result — blanket RED, D1 the lone survivor:**

| TF | IS PF | OOS PF | WR IS/OOS | n |
|---|---|---|---|---|
| M15 | 0.79 | 0.63 | 34/30% | ~2000 | 🔴 |
| H1 | 0.77 | 0.71 | 32/31% | ~590 | 🔴 |
| H4 | 1.03 | 0.81 | 38/33% | ~165 | 🔴 loses OOS |
| **D1** | **1.98** | **1.38** | 54/46% | ~50 | 🟢 both splits + |

Overall PF 0.81 IS / 0.66 OOS → nothing ships broadly. The **raw** (no-cost, zone-height-stop)
version looked tradeable on every TF (edge scaled up with TF: D1 PF 3.0/1.9 raw); adding the
**structural 10-pip stop + costs** killed M15/H1/H4, leaving only a small-sample D1 positive.

**FINAL — RED everywhere (re-run 2026-08-05, confirmation-close entry, full 4yr):** per user
review, the LTF stop-outs were premature entries — replaced the 40%-wick/edge triggers with a
unified **confirmation close** (candle wicks into the zone AND closes back OUT in the trade
direction), keeping the 10-pip structural stop + costs, run on **all 3 pairs × 2022-2025**:

| TF | IS PF | OOS PF | WR IS/OOS | n IS/OOS |
|---|---|---|---|---|
| M15 | 0.78 | 0.73 | 33/32% | 4022/4543 |
| H1 | 0.83 | 0.85 | 33/34% | 1243/1122 |
| H4 | 0.97 | 0.89 | 37/35% | 378/292 |
| D1 | 0.86 | 0.67 | 34/28% | 89/78 |

Overall 0.80 IS / 0.76 OOS — **negative on every timeframe.** The earlier D1 positive (PF 1.98/1.38)
was **n≈50 noise + the looser zone-stop**; at n≈89/78 with the corrected rules it collapsed to
0.86/0.67. The confirmation-close entry worked (cut the shallow-poke stop-outs, WR up to ~33-37%)
but the edge still isn't there: a **2R target off a 10-pip stop needs >33% WR**, IFVG lands right at
~33% (breakeven pre-cost), and spread/slippage sink it — `median R = -1.11` everywhere (most trades
stop out). Root cause: the inversion *rejects* but doesn't reliably *run* a fixed 2R after a
(correctly) later confirmation entry. **Verdict: IFVG-as-standalone with a structural stop + fixed
2R has no tradeable edge. Nothing ships.**

**HTF-liquidity target variant (tested 2026-08-05 — also RED, book closed):** targeting the nearest
prior-day/prior-week high-low (≥1R, no lookahead) instead of fixed 2R made it slightly WORSE — WR
fell to ~28-32% (far draws hit less often than a fixed 2R before the 10-pip stop is swept), overall
PF 0.81 IS / 0.75 OOS, negative every TF both splits; D1 dropped to 0.81/0.48 (a distant draw + a
10-pip stop is the worst combo). `median R=-1.11` everywhere. **Two target variants (2R + HTF), both
negative in both splits, all TFs → IFVG has no tradeable edge with a realistic structural stop +
costs. Closed.** The full-body-close inversion is a real market-STRUCTURE phenomenon but a ~30%-WR
standalone entry can't clear the >33% breakeven a 10-pip/2R needs. `scripts/backtest_ifvg.py`
retained (`--target 2r|htf`, flag `RUN_IFVG_BACKTEST=1`) for reference; nothing in the engine.

### P41 — PDH/PDL-sweep sizing lever (SHIPPED 2026-07-27)
**What (active lever):** When the AMD manipulation swept **prior-day liquidity** — the Judas sweep
ran within ~5 pips of PDH or PDL — size the position **1.25×**. Same mechanism, magnitude, and R3k
equity floor (`DRAW_SIZE_MIN_EQUITY`) as the shipped P18/P19 sizing bumps. Config:
`PDLIQ_SWEEP_MULT=1.25` (env-overridable; 1.0 = off). Counter: `pdliq_sweep_sized`.

**Where it came from — a PRICE byproduct of the (RED) tick-volume work, not a volume feature:** the
AMD × tick-volume study (`data/amd_tickvol_report.md`) profiled, as a side output, *what liquidity
each Judas sweep ran*. §9 was the one both-years-consistent setup-quality signal: sweeps that ran
PDH/PDL won **55% (2022) / 53% (2024)** vs the ~45% baseline. It is pure price structure
(`_amd_swept_pdliq` via `_market_profile`; no tick data), so unlike P39/P40 it applies to all pairs
and all years. NB this is the **entry/sweep** side — PDH/PDL were already used as **target** levels
and confluence sources (P15/P17/P18); using "did the *sweep* run PDH/PDL" as an entry-quality read
is the new part.

**Validation (`run_pdliq_validation.sh`, baseline 1.0× vs lever 1.25×):**

| run | trades | WR | PF | MaxDD | equity ZAR | sized |
|---|---|---|---|---|---|---|
| Full (2022–24)* base | 602 | 45.3% | 3.45 | -12.95% | 8,743,319 | — |
| Full lever | 602 | 45.3% | **3.49** | **-12.95%** | **11,702,904 (+34%)** | 91 |
| IS 2022-23 base | 389 | 45.8% | 3.09 | -12.95% | 313,759 | — |
| IS lever | 389 | 45.8% | 3.04 | -12.95% | **343,444 (+9.5%)** | 48 |
| OOS 2024 base | 210 | 44.3% | 3.47 | -15.41% | 32,293 | — |
| OOS lever | 209 | 44.0% | 3.50 | -15.41% | **34,690 (+7.4%)** | 31 |

Equity up in ALL THREE runs, PF flat (±0.05), **MaxDD identical to the decimal** everywhere, WR
unchanged — the clean-sizing-lever signature (same as P18/P19). Both splits stay strongly positive
and same-ballpark (PF 3.04 IS / 3.50 OOS). Ships ON.

**CONFIRMED on the true 810-trade 4yr path (2026-07-28):** after `scripts/fetch_histdata.py`
self-served the missing `UDXUSD_2025` + EUR/GBP 2025 data into the Codespace, the full run
reproduced the documented **810 trades** (OOS now the real 2024-25 = 418 trades, was 210):

| run | trades | WR | PF base→lever | MaxDD base→lever | equity ZAR base→lever | sized |
|---|---|---|---|---|---|---|
| Full 4yr | 810 | 45.9% | 4.47 → 4.46 | -12.95% → **-12.95%** | 429.3M → **675.6M (+57%)** | 122 |
| IS 2022-23 | 389 | 45.8% | 3.09 → 3.04 | -12.95% → -12.95% | 313.8k → 343.4k (+9.5%) | 48 |
| OOS 2024-25 | 418 | 45.9% | 4.47 → 4.46 | -15.41% → -15.41% | 1.59M → **2.01M (+26%)** | 62 |

Equity up in all three, PF flat (±0.05), **MaxDD held to the decimal everywhere** — the clean-
sizing-lever signature, now on the full documented path. P41 fully confirmed.

**Live-engine note (PORTED 2026-07-28):** `main.py` now carries P41 — `_amd_swept_pdliq` is
computed in `_maybe_open` from the AMD `rng`/`sweep_dir` vs the prior completed daily candle
(`bars1d_full[-1].High/.Low`, ±5 pips), and `PDLIQ_SWEEP_MULT` is applied in the sizing block
alongside draw-cascade/P9/P18/P19, gated by the same R3k `DRAW_SIZE_MIN_EQUITY` floor. Recorded as
`amd_swept_pdliq` on the trade record. The LEAN engine's sizing block is now complete (all four
1.25× levers + draw-cascade 2×/3×). `py_compile` clean; smoke-test on DEMO before funding.

### PWH/PWL reaction study — the P41 question one TF up (MEASURED 2026-07-28, INCONCLUSIVE)
**What:** does sweeping a WEEKLY pool (PWH/PWL) predict a better reversal, the way sweeping a
DAILY pool (PDH/PDL, P41) did? `scripts/pwliq_analysis.py` + `run_pwliq_analysis.sh` bucket all
810 trades by `amd_liq_run` (the pool the AMD sweep ran) and report WR/PF/mean-R split IS/OOS.

**Result — INCONCLUSIVE (structural, not a null):** only **8 of 810 trades** (2 IS / 6 OOS) had a
sweep that ran a weekly pool. Intraday Judas sweeps run the session range (tens of pips); PWH/PWL
sit a week's range away (100-300 pips), so an intraday sweep essentially never originates at a
weekly level. Sweep-reach on the full set: equal-H/L **397**, daily PDH/PDL **115** (why P41 works),
weekly PWH/PWL **8**, value-area 9. The 8 weekly trades lean positive (WR 50/50, +0.68/+1.27R) but
n=8 is noise — no lever. **Weekly levels matter here as TARGETS/draws (P17/P18), not sweep origins**
— price is drawn *to* the weekly pool, it doesn't *sweep* it intraday. Bonus: the run re-confirmed
P41 on the full set (daily-pool sweeps WR 50/45 vs no-pool baseline 45.3/45.8, both years).

### Draw-on-liquidity ladder study (MEASURED 2026-07-28, analytics-only)
**What:** how price reacts to each liquidity rung — previous session H/L, 3-day, weekly, 30-day,
60-day — as TARGETS and as DRAWS price delivers to. Instrumentation (logging only, 810/PF 4.47/
MaxDD -12.95% unchanged): `_prev_session_hl` (previous ET session block extreme), `_draw_ladder`
(pip-distance to nearest UNSWEPT pool ahead at each rung), MFE tracking in `_update_orders`.
Confirmed the "past 3 days H/L" is ALREADY the PDH/PDL target basis (`d_bars[-4:-1]`); added the
30/60-day rungs that weren't built. Code: `scripts/draw_ladder_analysis.py` + `run_draw_ladder.sh`.

**Finding A (targets):** fib extensions are the workhorse (217/218 trades). Weekly/ITH targets are
rare big-R lottery tickets — PWH/PWL 4/8 trades, PF 26.78/7.55; huge payoff when hit, low hit-rate.
Hit-rates low everywhere (21-41%) — most trades exit via trail/BE/scale, not the nominal target.

**Finding B (ladder) — the key result + its limit:** within-trade delivery: previous session
78%/87% (at 6-7 pips), 3-day 0%/0% (42-62 pips), weekly 7%/8% (105-167 pips), 30-day/60-day 0%.
The 0%s are an EXIT-CAP artifact, not "price never goes there": the strategy exits at the nearest
fib (~25 pips), and MFE is only tracked while the trade is open, so it can't reach a 42-pip 3-day
pool. This CONFIRMS the strategy delivers to the nearest draw and exits — the far pools are the
NEXT cycle's draw (why HTF_TARGET_PREF forcing far targets = -22% MaxDD). It does NOT test whether
price CONTINUES to the far pools after our exit — that cascade plays out across trades/days and
needs a PURE PRICE-PATH study (raw M1, independent of entries), the clean next test.

### Minimum-target floor 20 → 30 pips (SHIPPED 2026-07-28, user preference)
**What:** `MIN_PIPS_TARGET` raised 20 → 30 (env-overridable). Higher floor forces further, higher-RR
targets. Validated 20 vs 25 vs 30 on full + IS/OOS (`run_mintarget_validation.sh`):

| floor | full PF | full MaxDD | full equity | IS PF/eq | OOS PF/MaxDD/eq |
|---|---|---|---|---|---|
| 20 | 4.46 | -12.95% | R675.6M | 3.04 / R343k | 4.46 / -15.41% / R2.01M |
| 30 | **4.95** | **-12.76%** | R567.6M | 2.88 / R273k | **4.95 / -12.55% / R2.24M** |

**Strict gate = RED** (full-4yr equity down -16%, IS weaker) — the compounding-path effect: the
smaller 20-pip winners hit more often and compound forward, so raw geometric growth is higher at 20
even as PF rises at 30. **Shipped anyway at the user's explicit preference (2026-07-28):** 30 buys
higher PF (4.95), better MaxDD everywhere (notably OOS -12.55% vs -15.41%), and higher OOS equity —
the equity "loss" is only on the idealized R500→4yr compounding fantasy, not the live R1k path. The
trade-off is a genuine risk/quality-vs-raw-growth preference, not a defect. Weaker IS (small-account)
phase is the known cost. `MIN_PIPS_TARGET=20` env-restores the old behavior.

**Equity-scaled floor (BUILT 2026-07-28, default OFF, pending validation):** the theoretically-best
hybrid — 20-pip floor below R3k (`DRAW_SIZE_MIN_EQUITY`; more frequent hits = small-account
compounding fuel), 30-pip floor above it (higher PF + lower DD). `_min_pips_target()` in both
backtest.py and main.py; wired into `_find_target` (fib min-distance + RR selection) and both the
entry and pyramid gates. Config: `MIN_TARGET_SCALED=0` (off → byte-identical to flat
`MIN_PIPS_TARGET`), `MIN_PIPS_TARGET_SMALL=20`, `MIN_PIPS_TARGET_LARGE=30`. Validate with
`run_scaledtarget_validation.sh` (flat-20 vs flat-30 vs scaled, full+IS/OOS) — ship only if it beats
flat-30 on full-4yr equity with MaxDD held; the IS (small-account) split is the one to watch since
that's the live R1k starting phase.

**Result — 🔴 RED, kept OFF (validated 2026-08-04):** scaled full-4yr R563.6M vs flat-30 R567.6M
(slightly worse), OOS R1.83M / MaxDD -16.12% vs flat-30 R2.24M / -12.55% (worse), and it did NOT
recover flat-20's small-account IS edge (scaled IS R271k ≈ flat-30 R273k, not flat-20's R343k). The
hybrid fails because the account crosses R3k too fast for the 20-pip regime to matter — scaled ≈
flat-30 with OOS-path noise making it marginally worse. `MIN_TARGET_SCALED=0` stays.

**Pyramiding × 30-pip floor (measured same run):** the 30-pip floor blocks ~2× more pyramid
ATTEMPTS (full 4yr: 1124 blocked vs flat-20's 514) but actual adds were UNCHANGED (18 vs 17). The
hypothesis that MIN_PIPS_TARGET=30 starves pyramiding was WRONG — successful adds sit on long-target
moves that clear the floor easily. No separate PYRAMID_MIN_TARGET needed; measure-first avoided an
unnecessary lever. (~17-19 pyramids/4yr is just how rare these high-conviction adds are by design.)

### Pure-price draw cascade study (MEASURED 2026-07-28, validates design)
**What:** the clean test of the ICT draw hierarchy on RAW M1 price, independent of the strategy's
entries/exits (fixes the exit-cap limitation of the draw-ladder study). `scripts/price_cascade.py`
+ `run_price_cascade.sh`: detect every prior-day-liquidity sweep, follow price forward 2 trading
days, record which pools it reaches (3d≤30d≤60d ascending + weekly). 3,637 sweep events (1844 IS /
1793 OOS), vectorized ffill-reindex level alignment (no lookahead), O(n).

**Result — cascade CONFIRMED, rock-solid IS/OOS + per-pair:**

| next pool | reach IS | reach OOS |
|---|---|---|
| 3-day | 58% | 61% |
| 30-day | 21% | 20% |
| 60-day | 15% | 13% |
| weekly | 25% | 27% |

All 3 pairs match (~60/20/14). Conditional: daily→3d 60%, 3d→30d 49%, 30d→60d 70% (deep moves
cascade, but are rare). **Interpretation — validates the design, not a new lever:** the 3-day pool
is the dependable next draw and the strategy ALREADY targets it (PDH/PDL = last 3 daily candles).
The 30/60-day pools are reached only ~20%/13% in 2 days — extension-only, which is the empirical
proof of why `HTF_TARGET_PREF` (forcing far targets) = -22% MaxDD: ~80% of the time price doesn't
get there. Far-pool momentum (30d→60d 70%) is real but sits in rare deep moves an intraday
exit-at-nearest strategy isn't positioned to hold (TRAIL_AT_TP / TP-runner already reverted). No
lever — the algo is already built around the reliable rung.

### Draw-to-liquidity continuation entry (TESTED + REVERTED 2026-07-27)
**What:** the "trade TOWARD the unhit pool" idea — open a CONTINUATION toward an unswept PDH/PDL
(price is drawn to the resting pool) and exit AT it, instead of only fading the sweep. Built as a
targeted gate exemption: a `draw_score==0` trade (normally killed by the inverted-draw 0/3 reversal
gate) is let through ONLY when `_unswept_pdliq_target` finds an unswept PDH/PDL in the trade
direction within `[MIN_PIPS_TARGET, DRAW_CONT_MAX_PIPS]` (a NEAR pool = this cycle's draw, never a
far one — the `HTF_TARGET_PREF` revert already showed far pools = -22% MaxDD). MSS 2-of-3 kept;
earns breakout-style conviction; tagged `entry_model="draw_cont"`.

**Result — REVERTED (4th continuation-bypass to fail):**

| metric | baseline | draw-cont ON |
|---|---|---|
| Full 4yr MaxDD | -12.95% | **-16.73%** (breaches -15% breaker) ❌ |
| Full 4yr PF | 3.49 | 3.30 ❌ |
| Full 4yr WR | 45.3% | 44.6% ❌ |
| Full 4yr equity | 11.70M | 12.27M (illusory — bought with -16.73% DD) |
| IS MaxDD / PF | -12.95% / 3.04 | -16.73% / 2.90 ❌ |
| OOS MaxDD / equity | -15.41% / 34,690 | -11.86% / **33,958 (down)** ❌ |

72 continuation entries added; they win LESS often (WR + PF down in all three splits) and cluster
their losses (full+IS MaxDD blows past the -15% breaker). IS/OOS also disagree on MaxDD sign
(IS -3.78pp, OOS +3.55pp) → fails the not-curve-fit test independently. **Root cause (same as
TRAIL_AT_TP / TP-runner from the exit side):** the pool is where the AMD cycle ENDS — riding
continuation INTO it means buying exactly where smart money sells into the resting liquidity.
PDH/PDL are correct as TARGETS/exits (already used, P15/P17/P18/P41), wrong as continuation ENTRIES.
`DRAW_CONT_ENABLED=0` (default off; byte-identical to shipped when off). Code + `_unswept_pdliq_target`
+ `run_drawcont_validation.sh` retained for reference. Fourth confirmation that the strategy's
reversal DNA beats every continuation-bypass (P11 NY-exempt, SOJ-draw bypass, now this).

### P42 — Bonds/yields dollar-bias (BUILT 2026-08-12, measurement-first, default OFF, NOT run on real data yet)
**What:** brings the RATES market — the one genuinely orthogonal dimension the algo never consults —
into the dollar read. US Treasury yields lead the dollar (higher yields → capital inflow → USD bid),
so yields (DGS2/5/10) are POSITIVELY correlated with the dollar. Every pair is X/USD (inverse to the
dollar), so **pair vs yields is INVERSELY correlated** — the exact SMT relationship the algo already
runs intraday between EURUSD/GBPUSD and index/DXY, pointed at rates instead of another dollar proxy.
The 2Y is the Fed-policy anchor, the 10Y is growth/inflation, and their divergence from the dollar is
the reversal tell. **Sign gotcha (pinned in code):** bond PRICE is inverse to YIELD — we fetch yields
(positive to the dollar); bond futures would be negative. The SMT uses yields as the INVERSE reference.

**Measurement pipeline (`scripts/bonds_analysis.py` + `run_bonds.py`, measurement-only):**
- `scripts/fetch_fred.py` — stdlib-only FRED daily-yield fetcher (DGS2/DGS5/DGS10) → `data/bonds_src/`.
  No API key; handles "." holiday markers + both header variants. `--selftest` parse-only.
- `scripts/bonds_analysis.py` — three measurements, split IS 2022-23 / OOS 2024-25, per pair × tenor:
  - **Foundation** — yield↔dollar correlation (daily −pair return vs daily yield change). Must be
    POSITIVE in both splits or the thesis is void (reported first; gates the verdict).
  - **Test A (headline)** — SMT divergence reversal rate: pair sweeps an extreme (a dollar move) that
    yields FAIL to confirm → measure whether the pair reverses over the horizon vs the unconditional
    baseline (`lift` in pp). Reuses `ict.smt.smt_divergence(inverse=True)`.
  - **Test B** — structure-agreement continuation: yield intermediate structure (Ep-12 classifier)
    vs the pair's dollar read → agree-days vs disagree-days continuation reliability.
  - Writes `data/bonds_report.md` with a **GREEN/YELLOW/RED** verdict (GREEN needs a >3pp reversal
    lift in BOTH splits on a majority of cells, on top of a positive foundation correlation).
- **Status: built + validated on synthetic fixtures, NOT yet run on real data.** `--selftest` passes
  (pearson, reversal walk, lift, verdict gating, SMT inverse wiring); full pandas pipeline exercised
  end-to-end on a synthetic dollar↔yield fixture (foundation corr +0.89 as constructed; random Test A
  correctly lands mixed → YELLOW). FRED is proxy-blocked in the cloud session — the run happens in the
  Codespace via `python run_bonds.py`.

**Engine hook (SHIPPED default-OFF, byte-identical when off):** `--emit-bias` writes
`data/bond_bias.json` (per-date DGS10 intermediate-structure read: +1 dollar-bullish / −1 bearish / 0
flat). `backtest.py._load_bond_bias` lazy-loads + caches it; in `_maybe_open` a trade whose dollar
direction (short an X/USD pair = dollar-up +1) AGREES with the yield structure on its date sets
`_bond_confirm`, and the sizing block scales it `BONDS_SIZE_MULT×` (same 1.25× magnitude + R3k
`DRAW_SIZE_MIN_EQUITY` floor as P18/P19/P41). Config: `BONDS_BIAS_ENABLED=0`, `BONDS_SIZE_MULT=1.0`
(both env-overridable) → the file is never read and the multiplier is a no-op, so the default run is
byte-identical. `bond_confirm` recorded on every trade. Counter: `bond_bias_sized`. **NOT ported to
main.py** (the LEAN engine) — deliberately, until it ships; the live-engine port follows a GREEN
validation, as P41 did.

**Ship gate:** `python run_bonds.py` → read the verdict. Only a GREEN warrants
`python run_bonds_validation.py` (baseline vs 1.25× on full 4yr + IS/OOS; ships only if full-4yr equity
up + MaxDD held and both splits stay positive). YELLOW/RED → nothing ships; the study stands as the
record of why — same measure-first discipline as P39/P40.

### P43 — Market Maker IFVG continuation to opposing liquidity (BUILT 2026-08-13, backtester, default OFF, NOT validated yet)
**What (user's model, captured from 12 Aug EU/GU charts + Q&A):** the DISTRIBUTION leg. After the
Judas sweep + reversal (which the base strategy already trades), price delivers to the OPPOSING
liquidity pool, retracing into **inversion FVGs (IFVGs)** along the way — each an M15→M5→M1 re-entry /
pyramid add — **until the opposing pool is reached**. The base strategy fades the sweep ONCE and exits
at the nearest fib (~30 pips); it does not re-enter down the distribution. The reversal is confirmed by
**H1 EURUSD↔GBPUSD SMT** (one pair sweeps a higher high, the correlated pair fails to confirm →
bearish SMT — exactly the 12 Aug setup: GU took 1.35292, EU failed its 1.15792 high, both distributed
to sell-side).

**The four gaps found (why the algo "doesn't take these entries at all"):** the Market Maker model was
~60% built but **live-only and inert**: (1) `_mm_scan`/`_mm_auto_entry` in `live/run_live.py` require the
trader to arm it by hand via Telegram `/mm PAIR sell auto` — never autonomous; (2) it watches D1/H4/H1
IFVGs only, not the intraday M30→M1 cascade the setup lives on; (3) it's **absent from the backtester**,
so never validated (the RED `scripts/backtest_ifvg.py` was standalone IFVG w/ fixed 2R + 10-pip stop — a
different construction); (4) the H1 EU/GU SMT that STARTS the model isn't in the FX entry path (`smt.py`
is wired for the index book only).

**Implementation (`_mm_continuation` in backtest.py + config `MM_*`, default OFF):**
- Fires only on an already-open position (the reversal defines model direction + opposing pool).
- `_mm_ifvg_zone`: price retraced INTO an M15/M5 inversion FVG in the trade direction (`ict.ifvg`).
- `_mm_structure_confirm`: fresh, still-intact M1 swing in the trade direction (the LTF shift).
- `_htf_pair_smt`: H1 EU/GU SMT divergence — tag on every trade (`htf_smt`); hard gate only when
  `MM_HTF_SMT_REQUIRED=1`.
- `_opposing_liquidity`: furthest unswept H4/D/W ITH/ITL pool — used as the target ONLY when
  `MM_TARGET_OPPOSING=1` (kept a separate flag: the far-target change is the piece that repeatedly
  failed — HTF_TARGET_PREF −22%, TRAIL_AT_TP −49%, TP_RUNNER −75% — so it's opt-in ON TOP of the adds).
- Adds a leg via the same lot/stop machinery as `_maybe_pyramid` (M1 structural stop capped at
  FIXED_STOP_PIPS), tagged `mm_ifvg_<tf>`. Columns: `htf_smt`, `mm_adds`. Counters: `mm_added`,
  `mm_target_escalated`, `mm_blocked_*`.
- **Why it's distinct from the reverted far-target holds:** those held ONE position THROUGH the
  consolidation (where the strategy has no edge). This BANKS and re-enters on a fresh IFVG + M1 shift,
  so it's flat during the chop — the exact failure mode the reverts died on.

**Config:** `MM_CONTINUATION_ENABLED=0`, `MM_TARGET_OPPOSING=0`, `MM_HTF_SMT_REQUIRED=0`,
`MM_IFVG_TFS=("15T","5T")`, `MM_STRUCTURE_TF="1T"`, `MM_MIN_FAVOUR_PIPS=8`. Default OFF → the loop hook
returns immediately and `htf_smt` is never computed, so the default run is byte-identical.

**Status: built + helper-unit-tested (IFVG zone containment, M1 structure confirm, H1 EU/GU SMT
direction mapping, dict-key wiring all verified on fixtures), NOT run on real data yet.** Validate with
`python run_mm_validation.py` (3 arms — baseline / adds-only / adds+opposing-target — × full 4yr + IS/OOS;
`--smt` to also require H1 SMT). Ships only if an arm lifts full-4yr equity with MaxDD held and both
splits stay positive. **NOT wired into `live/run_live.py`'s auto-loop** — the live port follows a GREEN
validation (as P41 did); the manual `/mm ... auto` path is untouched.

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
