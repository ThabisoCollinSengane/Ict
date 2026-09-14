# Replay Backtest (02 Jul - 02 Sep 2026)

Generated: 2026-09-02 06:47 UTC
Strategy: SELL GBPUSD (dollar UP) | BUY EURUSD (dollar DOWN)
Gate: Bonds/Yields → DXY → EURGBP → pair selection (intermarket cascade)
Models: **MM** (IFVG zone + MSS + SMT + FBC) | **AMD** (Judas reversal + breakout)
MM gate: IFVG+MSS+SMT (full triple) | AMD gate: MSS-2/3 minimum
Cascade gate: **ON (skip trades where dollar opposes direction) + SKIP-OVERLAP (no 05:00-07:00 ET)**
Max trades/day: 2 | Stop: structural M5, capped 10 pips | Trail: BE at +10, lock +10 at +20 | Target: 30 pips

## Weekly Summary

| Metric | Value |
|---|---|
| Total setups | **43** |
| Wins (hit 30-pip target) | **5** |
| Trail exits (+10 lock) | 6 |
| Session-end close (positive) | 10 |
| Breakeven | 5 |
| Session-end close (negative) | 4 |
| Losses (stop hit) | **13** |
| Profitable trades | **21** (49%) |
| Total pips | **+188.0** |
| Avg pips/trade | 4.4 |

## Per-Pair Summary

| Pair | Direction | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|---|
| GBPUSD | SELL | 19 | 12 | 3 | 63% | +100.8 |
| EURUSD | BUY | 24 | 9 | 10 | 38% | +87.2 |

## Day-by-Day Breakdown

### Thursday 02 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Friday 03 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Monday 06 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Tuesday 07 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Wednesday 08 Jul 2026 — 2 setups (0P/2L, -20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |
| 2 | 16:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **LOSS** | -10.0 |

### Thursday 09 Jul 2026 — 1 setups (0P/1L, -5.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 14:30 | AMD | EURUSD | BUY | STRONG | JUDAS+MSS-2/3+SMT | Y | **LOSS** | -5.4 |

### Friday 10 Jul 2026 — 1 setups (0P/1L, -5.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **LOSS** | -5.4 |

### Monday 13 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Tuesday 14 Jul 2026 — 1 setups (1P/0L, +30.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **WIN** | +30.0 |

### Wednesday 15 Jul 2026 — 2 setups (2P/0L, +40.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | — | **TRAIL** | +10.0 |
| 2 | 08:30 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | — | **WIN** | +30.0 |

### Thursday 16 Jul 2026 — 2 setups (2P/0L, +41.1 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | Y | **WIN** | +30.0 |
| 2 | 16:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **CLOSE** | +11.1 |

### Friday 17 Jul 2026 — 2 setups (0P/1L, -4.1 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | EURUSD | BUY | STRONG | JUDAS+MSS-2/3+SMT | — | **LOSS** | -4.1 |
| 2 | 10:00 | AMD | GBPUSD | SELL | STRONG | JUDAS+MSS-2/3+SMT | Y | **BE** | +0.0 |

### Monday 20 Jul 2026 — 2 setups (0P/1L, -5.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **LOSS** | -5.4 |
| 2 | 14:30 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | Y | **BE** | +0.0 |

### Tuesday 21 Jul 2026 — 2 setups (0P/1L, -13.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |
| 2 | 16:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | -3.0 |

### Wednesday 22 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Thursday 23 Jul 2026 — 2 setups (1P/0L, +1.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 14:30 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **CLOSE** | -3.0 |
| 2 | 16:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **CLOSE** | +4.4 |

### Friday 24 Jul 2026 — 2 setups (1P/1L, -5.6 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |
| 2 | 16:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **CLOSE** | +4.4 |

### Monday 27 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Tuesday 28 Jul 2026 — 1 setups (1P/0L, +10.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 16:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **CLOSE** | +10.4 |

### Wednesday 29 Jul 2026 — 1 setups (1P/0L, +10.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 16:00 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **TRAIL** | +10.0 |

### Thursday 30 Jul 2026 — 1 setups (1P/0L, +30.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 08:30 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **WIN** | +30.0 |

### Friday 31 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Monday 03 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Tuesday 04 Aug 2026 — 1 setups (1P/0L, +9.3 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 14:30 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **CLOSE** | +9.3 |

### Wednesday 05 Aug 2026 — 2 setups (1P/0L, +5.3 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +5.3 |
| 2 | 14:30 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +0.0 |

### Thursday 06 Aug 2026 — 1 setups (1P/0L, +2.7 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 16:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +2.7 |

### Friday 07 Aug 2026 — 2 setups (0P/0L, -5.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10:00 | AMD | EURUSD | BUY | STRONG | JUDAS+MSS-2/3+SMT | Y | **BE** | +0.0 |
| 2 | 14:30 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | -5.4 |

### Monday 10 Aug 2026 — 1 setups (1P/0L, +2.6 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 14:30 | AMD | GBPUSD | SELL | STRONG | JUDAS+MSS-2/3+SMT | Y | **CLOSE** | +2.6 |

### Tuesday 11 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Wednesday 12 Aug 2026 — 1 setups (0P/0L, +0.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 08:30 | AMD | EURUSD | BUY | STRONG | JUDAS+MSS-2/3+SMT | Y | **BE** | +0.0 |

### Thursday 13 Aug 2026 — 2 setups (0P/1L, -8.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **BE** | +0.0 |
| 2 | 08:30 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **LOSS** | -8.4 |

### Friday 14 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Monday 17 Aug 2026 — 2 setups (0P/2L, -14.2 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **LOSS** | -10.0 |
| 2 | 08:30 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **LOSS** | -4.2 |

### Tuesday 18 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Wednesday 19 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Thursday 20 Aug 2026 — 1 setups (0P/1L, -7.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -7.0 |

### Friday 21 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Monday 24 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Tuesday 25 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Wednesday 26 Aug 2026 — 2 setups (1P/1L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |
| 2 | 08:30 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **WIN** | +30.0 |

### Thursday 27 Aug 2026 — 2 setups (2P/0L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **TRAIL** | +10.0 |
| 2 | 04:00 | AMD | GBPUSD | SELL | STRONG | BREAKOUT+MSS-2/3+SMT | — | **TRAIL** | +10.0 |

### Friday 28 Aug 2026 — 2 setups (2P/0L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **TRAIL** | +10.0 |
| 2 | 07:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **TRAIL** | +10.0 |

### Monday 31 Aug 2026 — 2 setups (2P/0L, +39.1 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +20.2 |
| 2 | 10:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **CLOSE** | +18.9 |

### Tuesday 01 Sep 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Wednesday 02 Sep 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

## Session Breakdown

| Session | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| London Open | 10 | 5 | 5 | 50% | +5.8 |
| London→NY Overlap | 7 | 3 | 3 | 43% | +37.8 |
| NY AM | 11 | 5 | 3 | 45% | +116.3 |
| NY PM | 15 | 8 | 2 | 53% | +28.1 |

## Signal Strength

| Strength | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| STRONG (>=3 confirms) | 22 | 9 | 6 | 41% | +68.1 |
| MODERATE (>=2 confirms) | 21 | 12 | 7 | 57% | +119.9 |

## All Trades (detailed)

1. **LOSS** [AMD] BUY EURUSD — Wed 08 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14299, Stop 1.14199, Target 1.14599 — **-10.0 pips**
2. **LOSS** [MM] BUY EURUSD — Wed 08 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.14299, Stop 1.14199, Target 1.14599 — **-10.0 pips** MFE +1
3. **LOSS** [AMD] BUY EURUSD — Thu 09 14:30 ET (NY PM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.14364, Stop 1.14310, Target 1.14664 — **-5.4 pips** MFE +1
4. **LOSS** [MM] BUY EURUSD — Fri 10 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.14430, Stop 1.14375, Target 1.14730 — **-5.4 pips** MFE +3
5. **WIN** [AMD] BUY EURUSD — Tue 14 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13947, Stop 1.13880, Target 1.14247 — **+30.0 pips** MFE +68 ★20
6. **TRAIL** [AMD] SELL GBPUSD — Wed 15 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34073, Stop 1.34173, Target 1.33773 — **+10.0 pips** MFE +26 ★20
7. **WIN** [MM] BUY EURUSD — Wed 15 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.14247, Stop 1.14147, Target 1.14547 — **+30.0 pips** MFE +30 ★20
8. **WIN** [MM] SELL GBPUSD — Thu 16 10:00 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.35108, Stop 1.35208, Target 1.34808 — **+30.0 pips** MFE +32 ★20
9. **CLOSE** [AMD] SELL GBPUSD — Thu 16 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34760, Stop 1.34860, Target 1.34460 — **+11.1 pips** MFE +12
10. **LOSS** [AMD] BUY EURUSD — Fri 17 04:00 ET (London Open) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.14495, Stop 1.14454, Target 1.14795 — **-4.1 pips** MFE +1
11. **BE** [AMD] SELL GBPUSD — Fri 17 10:00 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.34499, Stop 1.34599, Target 1.34199 — **+0.0 pips** MFE +11
12. **LOSS** [MM] BUY EURUSD — Mon 20 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.14351, Stop 1.14297, Target 1.14651 — **-5.4 pips** MFE +8
13. **BE** [MM] SELL GBPUSD — Mon 20 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.34344, Stop 1.34444, Target 1.34044 — **+0.0 pips** MFE +11
14. **LOSS** [AMD] SELL GBPUSD — Tue 21 10:00 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33847, Stop 1.33947, Target 1.33547 — **-10.0 pips**
15. **CLOSE** [MM] SELL GBPUSD — Tue 21 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33803, Stop 1.33893, Target 1.33503 — **-3.0 pips** MFE +9
16. **CLOSE** [AMD] SELL GBPUSD — Thu 23 14:30 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33188, Stop 1.33275, Target 1.32888 — **-3.0 pips** MFE +8
17. **CLOSE** [AMD] SELL GBPUSD — Thu 23 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33189, Stop 1.33275, Target 1.32889 — **+4.4 pips** MFE +9
18. **LOSS** [AMD] BUY EURUSD — Fri 24 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13908, Stop 1.13808, Target 1.14208 — **-10.0 pips** MFE +5
19. **CLOSE** [MM] SELL GBPUSD — Fri 24 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33230, Stop 1.33281, Target 1.32930 — **+4.4 pips** MFE +6
20. **CLOSE** [AMD] BUY EURUSD — Tue 28 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13908, Stop 1.13808, Target 1.14208 — **+10.4 pips** MFE +13
21. **TRAIL** [AMD] BUY EURUSD — Wed 29 16:00 ET (NY PM) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.14521, Stop 1.14421, Target 1.14821 — **+10.0 pips** MFE +41 ★20
22. **WIN** [AMD] BUY EURUSD — Thu 30 08:30 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14771, Stop 1.14671, Target 1.15071 — **+30.0 pips** MFE +33 ★20
23. **CLOSE** [AMD] BUY EURUSD — Tue 04 14:30 ET (NY PM) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.15287, Stop 1.15187, Target 1.15587 — **+9.3 pips** MFE +9
24. **CLOSE** [MM] BUY EURUSD — Wed 05 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.15420, Stop 1.15339, Target 1.15720 — **+5.3 pips** MFE +17
25. **CLOSE** [MM] BUY EURUSD — Wed 05 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.15594, Stop 1.15494, Target 1.15894 — **+0.0 pips** MFE +4
26. **CLOSE** [MM] SELL GBPUSD — Thu 06 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.34553, Stop 1.34614, Target 1.34253 — **+2.7 pips** MFE +9
27. **BE** [AMD] BUY EURUSD — Fri 07 10:00 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.15567, Stop 1.15467, Target 1.15867 — **+0.0 pips** MFE +11
28. **CLOSE** [MM] BUY EURUSD — Fri 07 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.15674, Stop 1.15574, Target 1.15974 — **-5.4 pips** MFE +5
29. **CLOSE** [AMD] SELL GBPUSD — Mon 10 14:30 ET (NY PM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.35104, Stop 1.35204, Target 1.34804 — **+2.6 pips** MFE +5
30. **BE** [AMD] BUY EURUSD — Wed 12 08:30 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.15540, Stop 1.15440, Target 1.15840 — **+0.0 pips** MFE +11
31. **BE** [AMD] BUY EURUSD — Thu 13 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.15380, Stop 1.15280, Target 1.15680 — **+0.0 pips** MFE +11
32. **LOSS** [MM] SELL GBPUSD — Thu 13 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.34896, Stop 1.34981, Target 1.34596 — **-8.4 pips**
33. **LOSS** [AMD] BUY EURUSD — Mon 17 04:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.16077, Stop 1.15977, Target 1.16377 — **-10.0 pips** MFE +9
34. **LOSS** [AMD] BUY EURUSD — Mon 17 08:30 ET (NY AM) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.15942, Stop 1.15900, Target 1.16242 — **-4.2 pips** MFE +8
35. **LOSS** [AMD] BUY EURUSD — Thu 20 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.16986, Stop 1.16917, Target 1.17286 — **-7.0 pips** MFE +1
36. **LOSS** [AMD] SELL GBPUSD — Wed 26 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.36234, Stop 1.36334, Target 1.35934 — **-10.0 pips** MFE +1
37. **WIN** [AMD] SELL GBPUSD — Wed 26 08:30 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.36158, Stop 1.36258, Target 1.35858 — **+30.0 pips** MFE +30 ★20
38. **TRAIL** [MM] SELL GBPUSD — Thu 27 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.35927, Stop 1.35979, Target 1.35627 — **+10.0 pips** MFE +22 ★20
39. **TRAIL** [AMD] SELL GBPUSD — Thu 27 04:00 ET (London Open) — STRONG [BREAKOUT+MSS-2/3+SMT] — Entry 1.35927, Stop 1.35979, Target 1.35627 — **+10.0 pips** MFE +22 ★20
40. **TRAIL** [AMD] SELL GBPUSD — Fri 28 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.35877, Stop 1.35977, Target 1.35577 — **+10.0 pips** MFE +34 ★20
41. **TRAIL** [AMD] SELL GBPUSD — Fri 28 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.35905, Stop 1.35953, Target 1.35605 — **+10.0 pips** MFE +37 ★20
42. **CLOSE** [MM] BUY EURUSD — Mon 31 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15996, Stop 1.15896, Target 1.16296 — **+20.2 pips** MFE +24 ★20
43. **CLOSE** [AMD] BUY EURUSD — Mon 31 10:00 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.16023, Stop 1.15940, Target 1.16323 — **+18.9 pips** MFE +22 ★20

## Outcome Breakdown

| Outcome | Count | Total Pips | Avg Pips |
|---|---|---|---|
| WIN (target hit) | 5 | +150.0 | +30.0 |
| TRAIL (+10 lock) | 6 | +60.0 | +10.0 |
| CLOSE (session end +) | 10 | +89.3 | +8.9 |
| BE (breakeven) | 5 | +0.0 | +0.0 |
| CLOSE (session end -) | 4 | -11.4 | -2.9 |
| LOSS (stop hit) | 13 | -99.9 | -7.7 |

## 20-Pip Milestone (notification point)

**13 of 43 trades reached +20 pips** — these would trigger a notification.

| Group | Trades | WR | Pips | Avg | Avg MFE |
|---|---|---|---|---|---|
| Reached +20 (★20) | 13 | 100% | +249.1 | +19.2 | +32 |
| Never reached +20 | 30 | 27% | -61.1 | -2.0 | +7 |

**7 trades reached +20 but exited below +20** (trail/close/loss after reversal).
Closing at +20 would have gained **+61 extra pips** on those trades.

*★20 = trade reached +20 pips MFE (notification would fire). Use `--close-at-20` to simulate closing all trades at 20 pips.*

## Model Breakdown (MM vs AMD)

| Model | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| MM | 15 | 7 | 4 | 47% | +65.0 | +4.3 |
| AMD (J:23 B:5) | 28 | 14 | 9 | 50% | +123.0 | +4.4 |

## Winner / Loser Analysis

### By Session

| Session | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| London Open | 10 | 5 | 5 | 50% | +5.8 |
| London→NY Overlap | 7 | 3 | 3 | 43% | +37.8 |
| NY AM | 11 | 5 | 3 | 45% | +116.3 |
| NY PM | 15 | 8 | 2 | 53% | +28.1 |

### By Confirmation Combo

| Confirmations | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| BREAKOUT+MSS-2/3 | 4 | 2 | 2 | 50% | +5.1 |
| BREAKOUT+MSS-2/3+SMT | 1 | 1 | 0 | 100% | +10.0 |
| IFVG+MSS+SMT | 15 | 7 | 4 | 47% | +65.0 |
| JUDAS+MSS-2/3 | 17 | 10 | 5 | 59% | +114.8 |
| JUDAS+MSS-2/3+SMT | 6 | 1 | 2 | 17% | -6.9 |

### By Time of Day (ET)

| Time | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| 04:00 | 10 | 5 | 5 | 50% | +5.8 |
| 07:00 | 7 | 3 | 3 | 43% | +37.8 |
| 08:30 | 6 | 3 | 2 | 50% | +77.4 |
| 10:00 | 5 | 2 | 1 | 40% | +38.9 |
| 14:30 | 7 | 2 | 1 | 29% | -1.9 |
| 16:00 | 8 | 6 | 1 | 75% | +30.0 |

## Intermarket Cascade (Bonds/DXY)

| Cascade | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| Confirmed (bonds+DXY agree) | 36 | 16 | 11 | 44% | +136.1 | +3.8 |
| Flat (no dollar signal) | 7 | 5 | 2 | 71% | +51.9 | +7.4 |

## Per-Layer Cascade Breakdown

*All trades (kept + gated) for full picture of each layer's signal quality.*

### Layer 0 — Yield Curve (Bonds)

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| Yields agree (2-3/3) | 16 | 3 | 10 | 19% | -20.9 | -1.3 |
| Yields partial (1/3) | 13 | 3 | 8 | 23% | +0.6 | +0.0 |
| Yields flat (0/3) | 64 | 26 | 25 | 41% | +115.7 | +1.8 |

### Layer 1 — DXY vs Daily Open

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| DXY bid (+1) | 41 | 12 | 19 | 29% | -17.0 | -0.4 |
| DXY flat (0) | 8 | 6 | 2 | 75% | +61.9 | +7.7 |
| DXY offer (-1) | 44 | 14 | 22 | 32% | +50.5 | +1.1 |

### Layer 1b — Bonds/DXY Agreement

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| Bonds+DXY agree | 9 | 1 | 4 | 11% | -28.3 | -3.1 |
| Bonds+DXY disagree | 76 | 25 | 37 | 33% | +61.8 | +0.8 |
| N/A (DXY flat) | 8 | 6 | 2 | 75% | +61.9 | +7.7 |

### Layer 1c — Bonds/DXY SMT Divergence

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| SMT divergence | 62 | 17 | 33 | 27% | -1.9 | -0.0 |
| No SMT | 31 | 15 | 10 | 48% | +97.3 | +3.1 |

### Layer 2 — EURGBP Bias (pair selection)

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| EUR > GBP (+1) | 6 | 3 | 1 | 50% | +42.3 | +7.0 |
| Flat (0) | 86 | 29 | 42 | 34% | +53.1 | +0.6 |
| GBP > EUR (-1) | 1 | 0 | 0 | 0% | +0.0 | +0.0 |

### Layer 3 — EU/GU Entry SMT

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| No entry SMT | 93 | 32 | 43 | 34% | +95.4 | +1.0 |

### Curve Stress

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|

## Cascade Gate Impact

| Scenario | Trades | WR | Losses | Pips | Avg |
|---|---|---|---|---|---|
| WITHOUT gate (all) | 93 | 34% | 43 | +95.4 | +1.0 |
| **WITH gate (shipped)** | **43** | **49%** | **13** | **+188.0** | **+4.4** |
| Gated out (all reasons) | 50 | 22% | 30 | -92.6 | -1.9 |
|   — against | 36 | 22% | 21 | -65.7 | -1.8 |
|   — overlap | 14 | 21% | 9 | -26.9 | -1.9 |

**Gate effect:** WR 34% -> 49% (+14pp), avg pips/trade +1.0 -> +4.4

### Gated Trades (skipped)

| # | Date | Time (ET) | Model | Pair | Dir | Gate | Would-be Result | Pips |
|---|---|---|---|---|---|---|---|---|
| 1 | Fri 03 Jul | 04:00 | MM | GBPUSD | SELL | against | CLOSE | +15.5 |
| 2 | Fri 03 Jul | 16:00 | MM | GBPUSD | SELL | against | CLOSE | +4.3 |
| 3 | Mon 06 Jul | 04:00 | AMD | EURUSD | BUY | against | LOSS | -8.0 |
| 4 | Tue 07 Jul | 07:00 | MM | EURUSD | BUY | against | LOSS | -10.0 |
| 5 | Tue 07 Jul | 10:00 | MM | EURUSD | BUY | against | LOSS | -4.1 |
| 6 | Fri 10 Jul | 05:00 | AMD | EURUSD | BUY | overlap | LOSS | -10.0 |
| 7 | Mon 13 Jul | 05:00 | AMD | EURUSD | BUY | overlap | LOSS | -10.0 |
| 8 | Mon 13 Jul | 06:00 | AMD | GBPUSD | SELL | against | LOSS | -3.7 |
| 9 | Tue 14 Jul | 04:00 | AMD | GBPUSD | SELL | against | LOSS | -10.0 |
| 10 | Wed 15 Jul | 07:00 | MM | EURUSD | BUY | against | LOSS | -10.0 |
| 11 | Thu 16 Jul | 07:00 | AMD | EURUSD | BUY | against | LOSS | -10.0 |
| 12 | Thu 16 Jul | 08:30 | MM | EURUSD | BUY | against | LOSS | -3.0 |
| 13 | Fri 17 Jul | 05:00 | AMD | EURUSD | BUY | against | LOSS | -3.0 |
| 14 | Fri 17 Jul | 06:00 | AMD | EURUSD | BUY | against | LOSS | -3.0 |
| 15 | Wed 22 Jul | 08:30 | MM | GBPUSD | SELL | against | BE | +0.0 |
| 16 | Wed 22 Jul | 16:00 | AMD | GBPUSD | SELL | against | LOSS | -3.3 |
| 17 | Fri 24 Jul | 06:00 | AMD | GBPUSD | SELL | against | LOSS | -7.0 |
| 18 | Mon 27 Jul | 05:00 | AMD | GBPUSD | SELL | against | WIN | +30.0 |
| 19 | Tue 28 Jul | 05:00 | AMD | GBPUSD | SELL | against | TRAIL | +10.0 |
| 20 | Wed 29 Jul | 05:00 | MM | EURUSD | BUY | overlap | LOSS | -10.0 |
| 21 | Wed 29 Jul | 06:00 | AMD | EURUSD | BUY | overlap | LOSS | -3.0 |
| 22 | Mon 03 Aug | 06:00 | AMD | EURUSD | BUY | against | LOSS | -5.5 |
| 23 | Mon 03 Aug | 16:00 | AMD | EURUSD | BUY | against | CLOSE | -2.7 |
| 24 | Tue 04 Aug | 05:00 | AMD | EURUSD | BUY | overlap | TRAIL | +10.0 |
| 25 | Wed 05 Aug | 04:00 | AMD | GBPUSD | SELL | against | BE | +0.0 |
| 26 | Fri 07 Aug | 06:00 | MM | EURUSD | BUY | overlap | WIN | +30.0 |
| 27 | Fri 07 Aug | 16:00 | MM | GBPUSD | SELL | against | CLOSE | +4.6 |
| 28 | Tue 11 Aug | 05:00 | AMD | EURUSD | BUY | against | CLOSE | +5.3 |
| 29 | Wed 12 Aug | 04:00 | AMD | EURUSD | BUY | against | BE | +0.0 |
| 30 | Wed 12 Aug | 05:00 | MM | EURUSD | BUY | against | BE | +0.0 |
| 31 | Thu 13 Aug | 04:00 | AMD | EURUSD | BUY | against | TRAIL | +10.0 |
| 32 | Thu 13 Aug | 05:00 | AMD | EURUSD | BUY | against | TRAIL | +10.0 |
| 33 | Mon 17 Aug | 06:00 | MM | GBPUSD | SELL | against | LOSS | -10.0 |
| 34 | Mon 17 Aug | 06:00 | MM | EURUSD | BUY | overlap | LOSS | -10.0 |
| 35 | Mon 17 Aug | 06:00 | AMD | EURUSD | BUY | overlap | LOSS | -8.2 |
| 36 | Tue 18 Aug | 06:00 | MM | GBPUSD | SELL | overlap | LOSS | -5.7 |
| 37 | Tue 18 Aug | 07:00 | AMD | EURUSD | BUY | against | BE | +0.0 |
| 38 | Tue 18 Aug | 08:30 | MM | EURUSD | BUY | against | BE | +0.0 |
| 39 | Wed 19 Aug | 05:00 | AMD | EURUSD | BUY | overlap | BE | +0.0 |
| 40 | Fri 21 Aug | 06:00 | AMD | EURUSD | BUY | overlap | LOSS | -10.0 |
| 41 | Tue 25 Aug | 05:00 | AMD | GBPUSD | SELL | overlap | BE | +0.0 |
| 42 | Wed 26 Aug | 04:00 | AMD | EURUSD | BUY | against | LOSS | -10.0 |
| 43 | Wed 26 Aug | 05:00 | MM | EURUSD | BUY | against | LOSS | -10.0 |
| 44 | Wed 26 Aug | 05:00 | AMD | EURUSD | BUY | against | LOSS | -10.0 |
| 45 | Wed 26 Aug | 06:00 | MM | EURUSD | BUY | against | LOSS | -8.3 |
| 46 | Wed 26 Aug | 06:00 | AMD | GBPUSD | SELL | overlap | LOSS | -10.0 |
| 47 | Wed 26 Aug | 07:00 | MM | EURUSD | BUY | against | LOSS | -8.3 |
| 48 | Fri 28 Aug | 05:00 | AMD | GBPUSD | SELL | overlap | TRAIL | +10.0 |
| 49 | Mon 31 Aug | 06:00 | AMD | GBPUSD | SELL | against | LOSS | -10.0 |
| 50 | Tue 01 Sep | 16:00 | MM | EURUSD | BUY | against | LOSS | -5.5 |

---

*Intermarket cascade: Bonds/Yields (T5/T10/T30) -> DXY -> EURGBP -> pair selection.*
*Simulation: structural M5 stop (capped 10 pips), trail BE at +10, lock +10 at +20, target 30 pips.*
*Session-end close resolves all trades -- no "OPEN" status.*
