# P78 — the institutional FX clock (Yahoo last 58d — RECENT WINDOW)

_coverage: EURUSD 2026-07-16→2026-10-06 (16,475 bars), GBPUSD 2026-07-16→2026-10-06 (16,475 bars), NZDUSD 2026-07-16→2026-10-06 (16,482 bars); trading days IS 29 / OOS 29; window ±2h around each anchor_

> ⚠️ **58 trading days. This cannot confirm or reject the clock.** The published effect is ~2bp/day; read the t-stats and the §3 MDE — at this n the noise is several times the effect. Here 'IS' = 2026-07-17→2026-08-26, 'OOS' = 2026-08-27→2026-10-06 (halves of the window, not the 2022-25 split). The 4-year verdict lives in fx_clock_report.md and needs the HistData M1 set.

## §2 The fix reversal — the verdict

R = dollar move into the anchor minus dollar move after it, USD basket, bp/day. Positive = dollar bid into the fix, offered after. `pctl` = share of placebo clock times this fix beats (needs ≥95 in BOTH halves).

| fix | R IS | t IS | pctl IS | R OOS | t OOS | pctl OOS | pooled t | verdict |
|---|---|---|---|---|---|---|---|---|
| ECB | +5.81 | +1.9 | 100 | -2.81 | -0.9 | 17 | +0.6 | **RED** |
| WMR | +0.33 | +0.1 | 56 | -3.38 | -1.2 | 13 | -0.8 | **RED** |
| TOKYO | +0.48 | +0.3 | 60 | +0.47 | +0.2 | 46 | +0.3 | **RED** |

> ⚠️ **ECB and WMR windows overlap** (±2h each, fixes 2.75h apart). A real ECB effect leaks into WMR with the OPPOSITE sign — the planted-effect drive showed WMR at t −3.5 with nothing planted there. Narrowing the window (`--window 1.375`) cut that to t −2.5 but did NOT remove it: the effect itself lasts hours, longer than the gap. **ECB and WMR are not independent tests.** If ECB is GREEN, a negative WMR is the expected echo, not a second finding.

**VERDICT: RED** (ECB RED · WMR RED · Tokyo RED — Tokyo is reported but not counted; it is outside every killzone).

_placebo: 52 clock times, every 15 min ET, excluding ±90 min around the real fixes._

### §2a The two legs separately — did the dollar rise INTO the fix, fall AFTER?

USD basket bp per day, `+` = dollar up. The research says BEFORE > 0 and AFTER < 0. R above is simply BEFORE − AFTER.

| fix | before IS (t) | after IS (t) | before OOS (t) | after OOS (t) |
|---|---|---|---|---|
| ECB | +1.21 (+0.7) | -4.60 (-1.5) | -2.09 (-1.0) | +0.72 (+0.3) |
| WMR | -0.27 (-0.1) | -0.60 (-0.4) | +0.69 (+0.4) | +4.07 (+1.6) |
| TOKYO | -0.41 (-0.3) | -0.89 (-0.7) | +1.76 (+1.3) | +1.29 (+0.7) |

### §2b Direction-free: does price REVERSE at the fix, whichever way it was going?

giveback = bp the after-window gives back against the before-window's move (> 0 = reversal). A dollar that ran UP into the fix one day and DOWN the next cancels out in R but counts here both times. Same 52-placebo control.

| fix | giveback IS (t) | pctl IS | giveback OOS (t) | pctl OOS | pooled t | verdict |
|---|---|---|---|---|---|---|
| ECB | -0.84 (-0.3) | 25 | +1.25 (+0.5) | 67 | +0.1 | **RED** |
| WMR | -1.58 (-1.0) | 8 | -2.00 (-0.8) | 4 | -1.2 | **RED** |
| TOKYO | +0.52 (+0.4) | 67 | +0.11 (+0.1) | 46 | +0.3 | **RED** |

_Real FX mean-reverts a little at ANY time of day; the placebo percentile is what separates 'the fix' from 'any two-hour window'._

## §1 Average dollar move by ET hour (USD basket)

Mean bp per hour; positive = dollar up. t = mean / SE.

| ET hour | IS bp | t | OOS bp | t | clock |
|---|---|---|---|---|---|
| 00:00 | +0.72 | +1.4 | -0.30 | -0.4 |  |
| 01:00 | -0.71 | -1.2 | -0.90 | -0.9 | CLS window opens |
| 02:00 | +0.29 | +0.3 | -1.06 | -0.9 |  |
| 03:00 | -0.49 | -0.4 | +1.07 | +0.8 | London open / CLS settle target · **London KZ** |
| 04:00 | -0.29 | -0.3 | +1.81 | +1.4 | London KZ |
| 05:00 | -1.14 | -1.1 | +2.29 | +2.7 |  |
| 06:00 | +1.36 | +1.6 | -0.12 | -0.1 | CLS window closes |
| 07:00 | +0.44 | +0.4 | -1.63 | -1.1 | **NY AM KZ** |
| 08:00 | -1.53 | -0.7 | +1.08 | +0.5 | ECB fix 08:15 · US data 08:30 · NY AM |
| 09:00 | -2.31 | -1.2 | -0.88 | -0.5 | NY AM |
| 10:00 | +1.72 | +1.0 | +1.22 | +0.7 | NY option cut 10:00 |
| 11:00 | -1.38 | -1.0 | +4.57 | +2.8 | WMR fix 11:00 |
| 12:00 | +0.75 | +0.9 | -1.08 | -0.8 | noon block |
| 13:00 | +0.77 | +0.6 | +0.52 | +0.5 |  |
| 14:00 | -2.66 | -1.4 | +1.38 | +0.6 |  |
| 15:00 | -0.37 | -0.5 | -0.31 | -0.4 |  |
| 16:00 | +0.49 | +1.0 | +0.41 | +1.0 |  |
| 17:00 | +1.23 | +2.1 | -0.60 | -1.6 | NY close / rollover |
| 18:00 | -1.14 | -1.3 | -0.23 | -0.4 |  |
| 19:00 | +0.18 | +0.2 | +0.47 | +0.8 |  |
| 20:00 | -0.52 | -0.6 | +1.25 | +1.2 | Tokyo fix 20:55 |
| 21:00 | +0.41 | +0.4 | +1.70 | +1.4 |  |
| 22:00 | -1.03 | -1.1 | -0.12 | -0.1 |  |
| 23:00 | +1.29 | +1.4 | +0.49 | +0.4 |  |

_Home-hours claim (Ranaldo): dollar up during European hours (~03-09 ET), down during US hours (~11-15 ET). Read sign AND both halves._

## §3 Daylight-saving natural experiment

0 mismatch days (Europe 5h ahead of New York, not 6). On those days the European fixes sit one hour LATER in ET. If the effect follows the European clock, `at Euro clock` carries it and `at usual ET` does not.

| fix | at Euro clock R (n) | MDE | at usual ET R | MDE | normal days R |
|---|---|---|---|---|---|
| ECB | — (0) | nan | — | nan | +1.50 (58) |
| WMR | — (0) | nan | — | nan | -1.52 (58) |

_MDE = minimum detectable effect (2 SE). Where |R| < MDE the comparison is UNDERPOWERED — that is a statement about sample size, not about the clock._

