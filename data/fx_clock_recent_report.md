# P78 — the institutional FX clock (Yahoo last 20d — RECENT WINDOW)

_coverage: EURUSD 2026-09-08→2026-10-06 (5,662 bars), GBPUSD 2026-09-08→2026-10-06 (5,662 bars), NZDUSD 2026-09-08→2026-10-06 (5,665 bars); trading days IS 10 / OOS 10; window ±2h around each anchor_

> ⚠️ **20 trading days. This cannot confirm or reject the clock.** The published effect is ~2bp/day; read the t-stats and the §3 MDE — at this n the noise is several times the effect. Here 'IS' = 2026-09-09→2026-09-22, 'OOS' = 2026-09-23→2026-10-06 (halves of the window, not the 2022-25 split). The 4-year verdict lives in fx_clock_report.md and needs the HistData M1 set.

## §2 The fix reversal — the verdict

R = dollar move into the anchor minus dollar move after it, USD basket, bp/day. Positive = dollar bid into the fix, offered after. `pctl` = share of placebo clock times this fix beats (needs ≥95 in BOTH halves).

| fix | R IS | t IS | pctl IS | R OOS | t OOS | pctl OOS | pooled t | verdict |
|---|---|---|---|---|---|---|---|---|
| ECB | -2.14 | -0.4 | 33 | -7.04 | -1.0 | 2 | -1.1 | **RED** |
| WMR | +0.46 | +0.1 | 48 | -3.48 | -0.7 | 33 | -0.5 | **RED** |
| TOKYO | +3.87 | +1.1 | 75 | +3.89 | +0.8 | 73 | +1.3 | **RED** |

> ⚠️ **ECB and WMR windows overlap** (±2h each, fixes 2.75h apart). A real ECB effect leaks into WMR with the OPPOSITE sign — the planted-effect drive showed WMR at t −3.5 with nothing planted there. Narrowing the window (`--window 1.375`) cut that to t −2.5 but did NOT remove it: the effect itself lasts hours, longer than the gap. **ECB and WMR are not independent tests.** If ECB is GREEN, a negative WMR is the expected echo, not a second finding.

**VERDICT: RED** (ECB RED · WMR RED · Tokyo RED — Tokyo is reported but not counted; it is outside every killzone).

_placebo: 52 clock times, every 15 min ET, excluding ±90 min around the real fixes._

## §1 Average dollar move by ET hour (USD basket)

Mean bp per hour; positive = dollar up. t = mean / SE.

| ET hour | IS bp | t | OOS bp | t | clock |
|---|---|---|---|---|---|
| 00:00 | -1.50 | -1.3 | +0.48 | +0.3 |  |
| 01:00 | -1.75 | -1.1 | -0.31 | -0.2 | CLS window opens |
| 02:00 | -0.03 | -0.0 | -3.02 | -2.4 |  |
| 03:00 | +3.32 | +2.1 | -2.73 | -1.0 | London open / CLS settle target · **London KZ** |
| 04:00 | +1.11 | +0.5 | +2.21 | +0.8 | London KZ |
| 05:00 | +0.58 | +0.4 | +4.11 | +2.8 |  |
| 06:00 | +2.09 | +1.3 | -2.26 | -1.1 | CLS window closes |
| 07:00 | +0.21 | +0.1 | -3.58 | -1.2 | **NY AM KZ** |
| 08:00 | +3.20 | +0.9 | +0.14 | +0.0 | ECB fix 08:15 · US data 08:30 · NY AM |
| 09:00 | -0.44 | -0.3 | +4.17 | +1.7 | NY AM |
| 10:00 | +1.16 | +0.5 | +0.72 | +0.2 | NY option cut 10:00 |
| 11:00 | +3.53 | +1.3 | +8.22 | +2.4 | WMR fix 11:00 |
| 12:00 | -3.47 | -1.8 | +0.21 | +0.1 | noon block |
| 13:00 | +0.06 | +0.1 | -1.07 | -0.4 |  |
| 14:00 | +6.76 | +1.2 | -3.09 | -1.1 |  |
| 15:00 | -0.20 | -0.1 | -0.82 | -0.8 |  |
| 16:00 | +0.82 | +1.8 | +0.50 | +0.6 |  |
| 17:00 | -0.57 | -0.9 | -0.46 | -0.5 | NY close / rollover |
| 18:00 | -1.72 | -1.8 | +1.31 | +1.1 |  |
| 19:00 | +1.68 | +2.1 | +1.63 | +2.3 |  |
| 20:00 | +1.87 | +1.0 | +2.30 | +1.2 | Tokyo fix 20:55 |
| 21:00 | +3.38 | +1.6 | -1.22 | -0.5 |  |
| 22:00 | -1.77 | -0.8 | -0.37 | -0.1 |  |
| 23:00 | -1.32 | -0.6 | -0.35 | -0.2 |  |

_Home-hours claim (Ranaldo): dollar up during European hours (~03-09 ET), down during US hours (~11-15 ET). Read sign AND both halves._

## §3 Daylight-saving natural experiment

0 mismatch days (Europe 5h ahead of New York, not 6). On those days the European fixes sit one hour LATER in ET. If the effect follows the European clock, `at Euro clock` carries it and `at usual ET` does not.

| fix | at Euro clock R (n) | MDE | at usual ET R | MDE | normal days R |
|---|---|---|---|---|---|
| ECB | — (0) | nan | — | nan | -4.59 (20) |
| WMR | — (0) | nan | — | nan | -1.51 (20) |

_MDE = minimum detectable effect (2 SE). Where |R| < MDE the comparison is UNDERPOWERED — that is a statement about sample size, not about the clock._

