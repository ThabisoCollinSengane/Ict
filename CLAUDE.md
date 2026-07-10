# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A fully-autonomous ICT (Inner Circle Trader) day-trading algorithm for **GBPUSD** and **EURUSD**, built around the Accumulation → Manipulation → Distribution (AMD) cycle gated by intermarket analysis (synthetic DXY + EURGBP relative strength) and a news filter. It targets the QuantConnect (LEAN) cloud engine for live/cloud backtesting, with a secondary local Python backtester for quick iteration without QC.

Read `README.md` first — it documents the strategy, AMD flow, config knobs, and intermarket decision table in detail. This file focuses on how the code is organized and how to work in it.

## Two parallel execution paths, one shared core

This is the single most important architectural fact: **the same strategy logic runs in two different harnesses**, and both must be kept in sync manually since there is no shared abstraction layer between them.

- **`main.py`** — a `QCAlgorithm` subclass (`ICTIntermarketAlgorithm`) that only runs inside QuantConnect's cloud IDE/LEAN engine. It imports `AlgorithmImports`, which does not exist outside QC — this file cannot be run or imported locally.
- **`backtest.py`** — a standalone pandas/yfinance backtester that reimplements the same order lifecycle (entry gating, pyramiding, exits, gate-funnel diagnostics) against free Yahoo Finance 5-minute data, with no QuantConnect dependency. Run with `python backtest.py`.

Both files independently call into the **shared strategy core**, which is the part that actually encodes ICT logic and must stay engine-agnostic (plain dicts/lists/dataclasses, no QC types):

- `config.py` — every tunable parameter (risk, killzones, AMD thresholds, timeframes, symbols). Change behavior here, not by hardcoding values elsewhere.
- `ict/` — pure ICT concept detectors, each independent and unit-testable in isolation:
  - `killzones.py` — NY-time session gating (`can_open_new_trade`)
  - `bias.py` — HTF bias via Break-of-Structure (`htf_bias`)
  - `amd.py` — accumulation range detection + manipulation (Judas swing) detection
  - `fvg.py` — Fair Value Gap detection + mitigation tracking
  - `order_block.py` — Order Block detection + mitigation tracking
  - `liquidity.py` — equal highs/lows clustering + liquidity sweep detection
  - `dxy_synthetic.py` — ICE-formula synthetic DXY from 6 OANDA-available constituent pairs
- `intermarket.py` — pure lookup table mapping `(dxy_bias, eurgbp_bias) -> (pair, direction)`
- `news_filter.py` — `NewsCalendar` class; loads either live ForexFactory XML (`.load()`, real-time only — the feed only ever returns "this week") or an offline CSV (`.load_csv()`, used for backtests since a fixed historical calendar is needed)
- `risk.py` — `position_size()` and the `TradeState` dataclass used to track pyramided legs

All ICT detector functions take plain candle-like objects (anything with `.Open/.High/.Low/.Close`) and lists ordered **oldest → newest** — `main.py`'s `_asc()` helper reverses QC's `RollingWindow` (which yields newest-first) before calling into `ict/`. Keep this convention when adding new detectors or call sites.

When changing detection logic in `ict/`, `intermarket.py`, `risk.py`, or `news_filter.py`, verify the change makes sense from both call sites (`main.py` and `backtest.py`) — they duplicate the entry/pyramid/exit orchestration logic (`_maybe_open` / `_maybe_pyramid` / target-finding), so a change to gating order or a new required signal generally needs to be mirrored in both `_maybe_open` implementations.

## Order lifecycle (both engines)

1. **Entry**: `_maybe_open` checks, in order: killzone window → news block → intermarket signal resolves to this pair → H1 bias agrees → H4 bias agrees → M15 AMD range + manipulation sweep in trade direction → M5 fresh FVG in trade direction → HTF target found (H4/D/W FVG, Order Block, or equal-high/low) → reward ≥ `MIN_PIPS_TARGET` and R:R ≥ `MIN_RR`. Only then is a limit order placed.
2. **Fill**: on entry fill, a stop and take-profit are placed as a bracket. If this is a pyramid leg (2nd/3rd), the *prior* leg's stop is promoted to break-even at that moment (not continuously trailed).
3. **Pyramid**: while a position is open, `_maybe_pyramid` adds up to `MAX_LEGS` (default 3) total legs, each requiring a fresh same-direction M5 FVG and ≥10 pips of favorable movement since the last entry.
4. **Exit**: SL or TP fill cancels the sibling order for that leg; when all legs are flat, the pair's tracking state is cleared.

`backtest.py`'s `Backtester` class reimplements this same state machine against synthetic bar dicts (`self.active`, `self.pending`) instead of QC order tickets/`TradeState`, plus a `self.gate` funnel counter dict that's useful for diagnosing why a strategy run produces few/no trades — check it first when debugging "no trades" in a backtest.

## Running things

There is no `requirements.txt`/`pyproject.toml` in this repo. Dependencies are inferred from imports:

- `backtest.py` needs: `pandas`, `yfinance`, `pytz` — install with `pip install pandas yfinance pytz` before running `python backtest.py`. It fetches 60 days of 5-minute data from Yahoo Finance live (no local fixtures), resamples to 15m/1H/4H/D/W, and prints a gate funnel + trade log + summary stats (win rate, profit factor, drawdown).
- `main.py` only runs inside the QuantConnect cloud IDE (`AlgorithmImports` is a QC-provided module) — see README's "Quickstart (QuantConnect cloud)" section for upload/backtest/live-deploy steps. Do not try to run it locally.
- There is no test suite and no linter configuration in this repo currently. If you add one, wire it into `.github/workflows/`.

`.github/workflows/cache-data.yml` runs weekly (and on manual dispatch) expecting a `scripts/cache_yf_data.py` script that writes to `data/yf/*.csv` — this script does not currently exist in the repo (`data/` is gitignored). If asked to work on the data-caching workflow, you'll need to create `scripts/cache_yf_data.py` first.

## Conventions worth preserving

- All strategy parameters live in `config.py` — new tunables should go there, not as literals in `main.py`/`backtest.py`/`ict/*`.
- Pip size is duplicated as a small `_pip`/`pip_size` helper in several files (`risk.py`, `ict/fvg.py`, `ict/liquidity.py`, `ict/amd.py`) rather than imported from one place — match this pattern (`0.01` for JPY pairs, `0.0001` otherwise) if you add another detector needing pip math, rather than introducing a new shared import.
- Detector modules return dataclasses (`FVG`, `OrderBlock`, `Range`) with a `mitigated` flag that callers update by scanning forward bars — mitigation is not tracked incrementally/statefully within the dataclasses themselves.
- Timezone handling: killzones and news windows operate in explicit UTC/NY conversions via `pytz` (see `ict/killzones.py`, `news_filter.py`) — don't assume naive datetimes are UTC without checking `tzinfo`.
