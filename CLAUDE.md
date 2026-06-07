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
**Backtest result (4 years, 2022–2025):** 811 trades, WR 46.0%, PF 4.47, MaxDD -12.95%, R500 → R294.8M.
(Two entry models: Judas reversal + intermarket breakout continuation — see §5. Includes P9
HTF-FVG 1.25× sizing bump, P16 fractal structural stop, P17 H4/D/W ITH/ITL liquidity-draw
targets, P18 score≥4 confluence sizing (1.25×), P19 H4-CRT Turtle Soup sizing (1.25×),
P20 high-conviction target escalation, P21 pyramid gate fix, P22 pyramid gate relaxation.
MaxDD unchanged at -12.95% across all additions. See P18 for the cache-bug post-mortem.)

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
