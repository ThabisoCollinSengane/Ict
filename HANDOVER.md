# HANDOVER — ICT algo continuation

Audience: a fresh Claude Code session that has Google Drive access and
can read the user's `ict 2022` PDF folder. This doc tells you everything
you need to resume work without re-doing the discovery the previous
session already did.

Repo: `ThabisoCollinSengane/Ict`. Working branch: `claude/github-app-scope-issue-Pnllt`.

---

## 1. The user (operator) in one paragraph

5+ year discretionary ICT trader. Break-even due to psychology, building
an algo to lock the edge into systematic execution. SAST-based (UTC+2),
on mobile most of the time. Speaks ICT fluently — when they reference
"intermediate term high", "draw on liquidity", "M5 FVG retest", "SMT
divergence", "fractal pattern", they mean the canonical ICT
definitions. Don't reinterpret their terms; align the code to their
meaning, not vice versa.

Target trade frequency: **2 trades per day** (1 London + 1 NY), on 3-5
tradable days per week. NY trade is often a pyramid continuation of the
London trade, sometimes a reversal after exiting London at NY open.

## 2. Your FIRST job in this new session

**Read the ICT 2022 PDFs in the user's Google Drive** (folder named
`ict 2022`). Particular attention to:

- **Episode 12** — market structure. This is the canonical reference
  for ITH/ITL/STH/STL/LTH/LTL classification and how price moves
  fractally between them. The current `ict/structure.py`
  `classify_intermediates` was written before reading this PDF; verify
  it matches Mark's exact rules.
- All other episodes that touch: FVG (validity criteria, mitigation
  rules), Order Block (last opposite-color candle before displacement),
  Breaker block (failed OB that flips), Liquidity (buy-side / sell-side
  / equal H/L / draw-on-liquidity), SMT (correlated asset divergence,
  whether the diverging pair becomes a reverse-trade candidate),
  Killzones (London / NY AM definitions), Macro time windows,
  Power-of-Three (AMD), Asian range / CBDR.

After reading, compare what Mark teaches to what's in this repo
(critical files listed below). For each meaningful gap or
misinterpretation, propose an adjustment. Don't blanket-rewrite — the
current code reflects 30+ iterations of user feedback and works
acceptably on real M1 data.

## 3. What's been built (architecture)

### Data layer

- `data/store.py` — gzipped-CSV M1 OHLCV+V (tick-count as volume).
  Path: `data/store/{symbol}_M1.csv.gz`. Format is the canonical
  source-of-truth; everything else is derived by resampling.
- `data/loader.py` — `get_bars(symbol, tf)` is the single read
  interface. Prefers M1 store → resampled; falls back to legacy
  `data/yf/{symbol}_5m.csv` if no M1.
- `scripts/import_histdata.py` — converts HistData.com ASCII zips
  (which the operator can download on mobile from https://www.histdata.com)
  into the store. Currently has ~70 days of M1 for EURUSD / GBPUSD /
  EURGBP / DXY (Feb 1 – Apr 10 2026).
- `scripts/import_dukascopy.py` — alternative downloader (BI5 binary +
  LZMA); needs network. Untested but written.

### Strategy modules (`ict/`)

| Module | Purpose | Key functions |
|---|---|---|
| `swings.py` | Pivot-based swing detection | `find_swings(bars, left=2, right=2)` |
| `structure.py` | ITH/ITL classification + tri-state cascade helper | `classify_intermediates`, `last_unmitigated`, `bias_holds_on_tf` (True/False/None), `directional_pull` |
| `mss.py` | Market Structure Shift (BOS / CHoCH) on per-TF basis | `mss_direction(candles)` returns +1/-1/0 |
| `amd.py` | Power-of-Three / AMD phase classification | `classify_phase` returns ACCUMULATION/MANIPULATION/DISTRIBUTION/NONE |
| `levels.py` | PDH/PDL/PWH/PWL, NYO, NWO, session H/L | `build_day_levels` |
| `cls_cycles.py` | CLS time cycles + ICT macro windows | `cycle_phases`, `in_macro_window`, `cbdr_hl` |
| `liquidity_zones.py` | HTF FVG/OB/Breaker/Swing tap detection | `collect_zones`, `most_recent_tap`. Swings added as zone class. |
| `liquidity_run.py` | Sweep validation (fake-run rule, next-higher-TF close) | `validate`, `confirm_tf_for` |
| `liquidity.py` | Equal H/L detection | `find_equal_highs`, `find_equal_lows` |
| `fvg.py` | 3-candle FVG detection + audit fields | `FVG` dataclass has displacement_strength etc.; `first_fvg_after` |
| `order_block.py` | OB detection (last opposite-color before displacement) | `detect_order_blocks` |
| `breaker.py` | Breaker blocks (flipped OBs); M15/H4 only per spec | `detect_breakers` |
| `target.py` | Draw-on-liquidity picker (HTF ITH/ITL anchored) | `pick_dol` walks D→H4→H1→M15 |
| `smt.py` | TWO SMT systems (see §4): structural + session-open | `structural_walk`, `session_open_smt`, `confirm` (legacy) |
| `intermarket.py` | DXY + EURGBP → pair selection | `resolve(dxy_bias, eurgbp_bias)` |
| `dxy_synthetic.py` | DXY from constituents (fallback when no DXY series) | `compute_dxy` |
| `killzones.py` | London + NY AM gates | `in_used_killzone`, `first_hour_elapsed` |
| `entry.py` | Compose signal with cost adjustments | `build(... raw_entry_override, stop_override)` |
| `context.py` | Time-in-zone, dwell, compression — pure helpers | `time_in_zone_pre_event` etc. |
| `volatility.py` | Realized vol + range expansion + regime | `realized_vol`, `range_expansion`, `vol_regime` |
| `game_theory.py` | All scoring lives here. Big sum-of-bonuses model. | `score_setup` |
| `risk_overlay.py` | Daily loss cap, correlated-group cap, max concurrent | `RiskOverlay.can_enter` |

### Backtest driver

- `backtest.py` (~1450 lines). Top-level orchestration in `_maybe_open`.
  Bar loop calls `_update_orders` (fills + exits + TP1-scale + runners),
  then `_maybe_pyramid` for open positions, then `_maybe_open` for
  empty pairs. `_maybe_session_handoff` at NY open closes London
  positions whose direction conflicts with D1.

## 4. SMT in this codebase (important — most-iterated module)

There are **three** SMT-related code paths. Don't conflate them.

### 4a. Legacy NYO lag-detection (`smt.confirm`)

Two-pair NYO-distance comparison. Mostly dormant now — kept only for
backward compatibility with `scripts/smoke_test.py`. Not on the
critical path.

### 4b. Structural SMT walk (`smt.structural_walk`) — primary

For a trade direction:

- For SHORT: DXY should have broken a recent swing HIGH, EUR a recent
  swing LOW, GBP a recent swing LOW.
- Mirror for longs.
- Walks W → D → H4 → H1 → M15 and returns the FIRST timeframe that
  produces a non-absent reading. **All three instruments are evaluated
  on the SAME timeframe** — no cross-TF mixing.
- States: `confirmed` (3/3 aligned), `divergence` (2/3 + 1 lagging,
  `divergent` list names the laggard), `absent` (<2 aligned).
- Currently: HTF divergence (W/D/H4/H1) is a hard veto. M15 divergence
  is soft (score penalty only).

### 4c. Session-open SMT (`smt.session_open_smt`)

Anchored to the killzone OPEN price (not NYO, not swings). For each
instrument, did its current price move in the expected direction (by
≥3 pips) from its session-open price? Same `confirmed`/`divergence`/
`absent` semantics. Used as additional confluence.

### Tiebreaker

When structural SMT and session SMT explicitly disagree (one says
confirmed, the other says divergence), the trade is **skipped**
(conservative default). Reflected in funnel as `smt_disagreement_skip`.

## 5. Current strategy gate funnel (real M1 data, Feb 1 - Apr 10 2026)

```
checks                   6235
killzone+first_hour      3616   (~58%)
news_clear               3616   (news block off — scoring only)
intermarket              3566
pair_match               1716   (intermarket pair must match)
bias_cascade D1           143 supports + 1195 neutral + 378 against
                                 (against = hard veto on D1+H4)
bias_cascade H4           981 supports + 357 against (vetoes)
bias_cascade H1, M15      981 each (soft only)
htf_zone_tap              714   (HTF FVG/OB/Breaker/Swing zone tapped)
kz_swing_identified       624
retail_pool_swept         640
sweep_validated           382   (fake-run on next-higher TF)
mss_2_of_3_pass            30   ← biggest bottleneck after cascade
smt_struct_confirmed       41   ← most readings come from M15/H1
smt_struct_divergence     109   (most diverge)
smt_divergence_veto_htf    70   (vetoed at H4/H1)
smt_divergence_m15_soft    39   (allowed through, scoring penalty)
smt_disagreement_skip      34   (struct vs session conflict)
m5_fvg_trigger             21
target_found               21
game_theory_pass           15
rr_ok                      12
limit_placed               12
trades                      6 — 1 winner (+$5235 EUR short Mar 11), 5 losers
```

PnL: +44% over 51 days. Profit factor 6.45. Max DD -2.86%. The 1
winner carries the equity curve.

## 6. The user's open spec when this session paused

Mid-implementation of TWO changes when conversation pivoted to PDFs.
Pick these up first (or update them based on PDF findings):

1. **Per-pair SMT classification.** Currently SMT divergence vetoes
   the trade in that direction REGARDLESS of which pair is the
   laggard. User's spec (which matches ICT canon, verify against
   Episode 12 / SMT episode): the divergent pair is the **laggard**;
   the ALIGNED pair is the trade candidate. So:
   - If `divergent = ["GBP"]` and we're evaluating GBPUSD → SKIP (GBP
     is the laggard).
   - If `divergent = ["GBP"]` and we're evaluating EURUSD → PROCEED
     (EUR is aligned, SMT actually CONFIRMS the EUR trade).
   - Existing veto logic in `backtest.py::_maybe_open` (around the
     `smt_struct.state == "divergence"` block) needs the per-pair
     classification before it can veto. Implementation sketch:
     ```python
     pair_to_sym = {"EURUSD": "EUR", "GBPUSD": "GBP"}
     sym = pair_to_sym[pair]
     if smt_struct.state == "divergence" and sym in smt_struct.divergent:
         # this pair IS the laggard — veto
         return
     # else: aligned pair, treat as confirmed for scoring
     ```

2. **Loosen intermarket pair-match gate.** `_maybe_open` returns early
   when `sig.pair != pair`. That means if intermarket picks GBP and
   GBP is diverging, EUR never gets evaluated. Either remove the
   strict gate or let both pairs through with intermarket alignment as
   a score bonus.

The user demonstrated this with a TradingView walkthrough of Mar 4
(GBP short — loser) where GBP failed to take its low but EUR DID. The
algo took the GBP short; the right trade was EUR short the next day.
Episode 12 + the SMT episode in the PDFs should confirm whether this
is canon ICT or the user's personal refinement.

## 7. Key recent design decisions (rationale + commit refs)

- **Tri-state bias cascade** (`c763d2b`): True/False/None instead of
  flat bool. None ("no read") falls through; only False ("structure
  against") blocks. Lets the algo trade when HTF has no formed
  ITH/ITL yet (common with 60 days of M1).
- **HTF FVG promotion** (`9cc9dc7`): H1 FVGs added to HTF tap pool.
  Operator: "H1 FVGs always taken — they precede the LTF".
- **M5/M15 swing-based stops** (`2935f91`): replaced c0-based stops
  after a 42-pip outlier. `MAX_STRUCTURAL_STOP_PIPS = 30` cap.
- **TP1-scale + runner extension** (`c15b58e`): when initial DOL hits,
  close leg 1, trail runner stops to nearest M15 ITH/ITL, retarget
  via `pick_dol` to next HTF level. If no further DOL beyond TP1 →
  close runners (we're against the HTF draw).
- **Session-handoff reversal** (`c15b58e`): at NY-AM open, force-
  close any open position whose direction conflicts with D1.
- **Per-session entry cap** (`c15b58e`): one initial entry per pair
  per killzone per UTC date.
- **HTF FVG zone-direct entry/stop** (`205cd69`): when zone is H1+
  FVG, entry = FVG near edge (mid if wide on H4+), stop beyond the
  opposite edge.
- **Structural SMT** (`4b4a3bf`): replaced NYO lag-detection with
  3-asset structural-break walk; W → D → H4 → H1 → M15.
- **MSS-2-of-3 gate** (`2935f91`, restored `70db7e0`): at least 2 of
  EURUSD/GBPUSD/DXY M15 must show MSS in trade direction (DXY
  inverted). HARD requirement now.
- **HTF swing as liquidity zone** (`66e24c9`): unmitigated D/H4/H1
  swing highs/lows are now first-class zones (zone width = price ±
  HTF_SWING_TOL_PIPS).
- **Risk overlay** (`a0faff3`): daily loss cap 2%, weekly DD halve
  4%, max 2 concurrent legs, EUR+GBP correlated group cap 1%.

## 8. Files the operator most cares about (read before any change)

- `/root/.claude/plans/here-is-my-strategy-elegant-squid.md` — the
  long-form plan + addenda. Every architectural decision is there
  with rationale. Read sections "Addendum — ITH/ITL-anchored DOL",
  "Addendum — Volume, time-spent, volatility, M1 source, news-as-
  feature" first.
- `config.py` — all tunable thresholds. Every constant is operator-
  specified, don't redesign casually.
- `backtest.py::_maybe_open` — the orchestration. ~300 lines, but
  every line is a gate the operator has signed off on.

## 9. How to verify changes

```
PYTHONPATH=. python scripts/smoke_test.py    # synthetic module smoke
python backtest.py                            # real-data 51-day run
```

Smoke test must print `ALL MODULES OK`. Backtest should produce a
funnel + per-setup detail + pattern audit + rejection log + per-trade
table + calibration vs the 2-trades/day target. After a change, the
funnel numbers should move in a direction that matches your stated
intent — if they don't, the change has a bug or an unexpected
interaction.

The operator audits trades on TradingView using the per-trade table.
Always include enough detail per trade for that audit: timestamp (UTC),
day-of-week, killzone, direction, entry/stop/target, swept-level
name, HTF zone kind+TF, trigger kind+TF, MSS hits, SMT state, RR,
final outcome.

## 10. Resume checklist for the new session

1. Read this whole doc.
2. Read the plan file at the path above.
3. Read the Drive PDFs (Episode 12 first, then SMT, then FVG, then
   anything on liquidity / market structure).
4. For each PDF, take notes on: (a) anything that contradicts the
   current code, (b) anything that refines a concept currently
   approximated, (c) anything the algo doesn't address at all that
   the operator clearly values.
5. **Before changing code**, present findings to the operator as a
   short bulleted summary with a proposed change per item, and let
   them prioritize. Don't blanket-rewrite based on PDF interpretation
   alone — the operator's discretionary calls override Mark's
   teaching when they conflict.
6. Then continue the two pending items in §6: per-pair SMT and
   intermarket loosening. These were already operator-approved; PDF
   review may refine them but probably won't kill them.

Last known-good commit on the working branch: **`66e24c9`**. If
anything you change breaks the funnel, reset to this and start over
from the relevant earlier commit.

Good luck.
