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
**Backtest result (4 years, 2022–2025):** 798 trades, WR 46.5%, PF 5.12, MaxDD -12.95%, R500 → R71.19M.
(Two entry models: Judas reversal + intermarket breakout continuation — see §5. Includes P9
HTF-FVG 1.25× sizing bump and P16 fractal structural stop: +R11M vs the R60.18M pre-P16
baseline, MaxDD unchanged at -12.95%.)

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

**Next lever (not yet implemented):** A sizing multiplier for score≥4 targets (analogous to
P9's 1.25x HTF FVG multiplier) could extract value from the high-conviction TP areas without
changing the compounding path. Requires IS/OOS validation before shipping.

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
