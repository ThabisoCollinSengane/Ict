# Idea log

One row per idea. Workflow: trader adds an idea -> spec-writer drafts research/specs/P<n>_*.md ->
trader approves -> builder -> auditor -> reporter (verdict + CLAUDE.md). Status: queued / spec /
approved / running / passed / failed / closed.

| # | Date | Idea (trader's words) | Spec | Status | Verdict |
|---|---|---|---|---|---|
| 1 | 2026-11-07 | Revisit the original algo (~42% WR, base + MM model) that collapsed once the backtest was made honest; correct it and get back to the same or higher win rate | [P125](specs/P125_honest_rebuild.md) | Phase A done; Phase B awaiting trader choice | Phase A: the dollar's H1 read alone carried the 42% (see data/p125_phaseA_report.md) |
| 2 | 2026-11-07 | Find an honest forecast of where the dollar's current H1 candle closes, to replace the leaky DXY H1 read | [P126](specs/P126_dollar_hour_forecast.md) | failed (Stage 1) | 0 of 7 rules beat a coin on the hour's DXY close (46.8-51.3% vs 55% bar); Stage 0: 42% WR needs ~78-85% accuracy. data/dollar_hour_forecast_report.md |
| 3 | 2026-11-07 | Start the volatility strategy using the same-clock-time pattern (seas20, P123) | [P127](specs/P127_clock_volatility.md) | failed | 0 of 16 cells; every bracket/fade loses after costs in IS/OOS/2026 (PF 0.35-0.80). data/clock_vol_report.md |
