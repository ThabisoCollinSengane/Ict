# Replay Backtest (01 Jul - 01 Sep 2026)

Generated: 2026-09-01 05:50 UTC
Strategy: SELL GBPUSD (dollar UP) | BUY EURUSD (dollar DOWN)
Gate: Bonds/Yields → DXY → EURGBP → pair selection (intermarket cascade)
Models: **MM** (IFVG zone + MSS + SMT + FBC) | **AMD** (Judas reversal + breakout)
MM gate: IFVG+MSS+SMT (full triple) | AMD gate: MSS-2/3 minimum
Cascade gate: **ON (skip trades where dollar opposes direction)**
Max trades/day: 2 | Stop: structural M5, capped 10 pips | Trail: BE at +10, lock +10 at +20 | Target: 30 pips

## Weekly Summary

| Metric | Value |
|---|---|
| Total setups | **53** |
| Wins (hit 30-pip target) | **5** |
| Trail exits (+10 lock) | 7 |
| Session-end close (positive) | 10 |
| Breakeven | 7 |
| Session-end close (negative) | 3 |
| Losses (stop hit) | **21** |
| Profitable trades | **22** (42%) |
| Total pips | **+128.9** |
| Avg pips/trade | 2.4 |

## Per-Pair Summary

| Pair | Direction | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|---|
| GBPUSD | SELL | 23 | 12 | 6 | 52% | +55.1 |
| EURUSD | BUY | 30 | 10 | 15 | 33% | +73.8 |

## Day-by-Day Breakdown

### Wednesday 01 Jul 2026 — 2 setups (1P/1L, +0.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **LOSS** | -10.0 |
| 2 | 07:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **TRAIL** | +10.0 |

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

### Friday 10 Jul 2026 — 2 setups (0P/2L, -15.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **LOSS** | -5.4 |
| 2 | 05:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |

### Monday 13 Jul 2026 — 1 setups (0P/1L, -10.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 05:00 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **LOSS** | -10.0 |

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

### Wednesday 29 Jul 2026 — 2 setups (0P/2L, -13.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 05:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **LOSS** | -10.0 |
| 2 | 06:00 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **LOSS** | -3.0 |

### Thursday 30 Jul 2026 — 1 setups (1P/0L, +30.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 08:30 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **WIN** | +30.0 |

### Friday 31 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Monday 03 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Tuesday 04 Aug 2026 — 2 setups (2P/0L, +19.3 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 05:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | — | **TRAIL** | +10.0 |
| 2 | 14:30 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **CLOSE** | +9.3 |

### Wednesday 05 Aug 2026 — 2 setups (1P/0L, +5.3 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +5.3 |
| 2 | 14:30 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +0.0 |

### Thursday 06 Aug 2026 — 1 setups (1P/0L, +2.7 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 16:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +2.7 |

### Friday 07 Aug 2026 — 2 setups (1P/0L, +30.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **WIN** | +30.0 |
| 2 | 10:00 | AMD | EURUSD | BUY | STRONG | JUDAS+MSS-2/3+SMT | Y | **BE** | +0.0 |

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

### Monday 17 Aug 2026 — 2 setups (0P/2L, -20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **LOSS** | -10.0 |
| 2 | 06:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **LOSS** | -10.0 |

### Tuesday 18 Aug 2026 — 1 setups (0P/1L, -5.7 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | Y | **LOSS** | -5.7 |

### Wednesday 19 Aug 2026 — 1 setups (0P/0L, +0.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 05:00 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **BE** | +0.0 |

### Thursday 20 Aug 2026 — 1 setups (0P/1L, -7.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -7.0 |

### Friday 21 Aug 2026 — 1 setups (0P/1L, -10.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |

### Monday 24 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Tuesday 25 Aug 2026 — 1 setups (0P/0L, +0.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 05:00 | AMD | GBPUSD | SELL | STRONG | JUDAS+MSS-2/3+SMT | Y | **BE** | +0.0 |

### Wednesday 26 Aug 2026 — 2 setups (0P/2L, -20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |
| 2 | 07:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |

### Thursday 27 Aug 2026 — 2 setups (2P/0L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **TRAIL** | +10.0 |
| 2 | 04:00 | AMD | GBPUSD | SELL | STRONG | BREAKOUT+MSS-2/3+SMT | — | **TRAIL** | +10.0 |

### Friday 28 Aug 2026 — 2 setups (2P/0L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **TRAIL** | +10.0 |
| 2 | 05:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **TRAIL** | +10.0 |

### Monday 31 Aug 2026 — 2 setups (2P/0L, +39.1 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +20.2 |
| 2 | 10:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **CLOSE** | +18.9 |

### Tuesday 01 Sep 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

## Session Breakdown

| Session | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| London Open | 17 | 7 | 8 | 41% | -4.2 |
| London→NY Overlap | 14 | 4 | 9 | 29% | +19.1 |
| NY AM | 9 | 4 | 2 | 44% | +90.5 |
| NY PM | 13 | 7 | 2 | 54% | +23.5 |

## Signal Strength

| Strength | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| STRONG (>=3 confirms) | 28 | 11 | 10 | 39% | +77.8 |
| MODERATE (>=2 confirms) | 25 | 11 | 11 | 44% | +51.1 |

## All Trades (detailed)

1. **LOSS** [MM] SELL GBPUSD — Wed 01 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.32459, Stop 1.32559, Target 1.32159 — **-10.0 pips**
2. **TRAIL** [MM] SELL GBPUSD — Wed 01 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.32489, Stop 1.32579, Target 1.32189 — **+10.0 pips**
3. **LOSS** [AMD] BUY EURUSD — Wed 08 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14299, Stop 1.14199, Target 1.14599 — **-10.0 pips**
4. **LOSS** [MM] BUY EURUSD — Wed 08 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.14299, Stop 1.14199, Target 1.14599 — **-10.0 pips**
5. **LOSS** [AMD] BUY EURUSD — Thu 09 14:30 ET (NY PM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.14364, Stop 1.14310, Target 1.14664 — **-5.4 pips**
6. **LOSS** [MM] BUY EURUSD — Fri 10 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.14430, Stop 1.14375, Target 1.14730 — **-5.4 pips**
7. **LOSS** [AMD] BUY EURUSD — Fri 10 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14364, Stop 1.14264, Target 1.14664 — **-10.0 pips**
8. **LOSS** [AMD] BUY EURUSD — Mon 13 05:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.14390, Stop 1.14290, Target 1.14690 — **-10.0 pips**
9. **WIN** [AMD] BUY EURUSD — Tue 14 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13947, Stop 1.13880, Target 1.14247 — **+30.0 pips**
10. **TRAIL** [AMD] SELL GBPUSD — Wed 15 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34073, Stop 1.34173, Target 1.33773 — **+10.0 pips**
11. **WIN** [MM] BUY EURUSD — Wed 15 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.14247, Stop 1.14147, Target 1.14547 — **+30.0 pips**
12. **WIN** [MM] SELL GBPUSD — Thu 16 10:00 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.35108, Stop 1.35208, Target 1.34808 — **+30.0 pips**
13. **CLOSE** [AMD] SELL GBPUSD — Thu 16 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34760, Stop 1.34860, Target 1.34460 — **+11.1 pips**
14. **LOSS** [AMD] BUY EURUSD — Fri 17 04:00 ET (London Open) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.14495, Stop 1.14454, Target 1.14795 — **-4.1 pips**
15. **BE** [AMD] SELL GBPUSD — Fri 17 10:00 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.34499, Stop 1.34599, Target 1.34199 — **+0.0 pips**
16. **LOSS** [MM] BUY EURUSD — Mon 20 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.14351, Stop 1.14297, Target 1.14651 — **-5.4 pips**
17. **BE** [MM] SELL GBPUSD — Mon 20 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.34344, Stop 1.34444, Target 1.34044 — **+0.0 pips**
18. **LOSS** [AMD] SELL GBPUSD — Tue 21 10:00 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33847, Stop 1.33947, Target 1.33547 — **-10.0 pips**
19. **CLOSE** [MM] SELL GBPUSD — Tue 21 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33803, Stop 1.33893, Target 1.33503 — **-3.0 pips**
20. **CLOSE** [AMD] SELL GBPUSD — Thu 23 14:30 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33188, Stop 1.33275, Target 1.32888 — **-3.0 pips**
21. **CLOSE** [AMD] SELL GBPUSD — Thu 23 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33189, Stop 1.33275, Target 1.32889 — **+4.4 pips**
22. **LOSS** [AMD] BUY EURUSD — Fri 24 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13908, Stop 1.13808, Target 1.14208 — **-10.0 pips**
23. **CLOSE** [MM] SELL GBPUSD — Fri 24 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33230, Stop 1.33281, Target 1.32930 — **+4.4 pips**
24. **CLOSE** [AMD] BUY EURUSD — Tue 28 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13908, Stop 1.13808, Target 1.14208 — **+10.4 pips**
25. **LOSS** [MM] BUY EURUSD — Wed 29 05:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.13999, Stop 1.13899, Target 1.14299 — **-10.0 pips**
26. **LOSS** [AMD] BUY EURUSD — Wed 29 06:00 ET (London→NY Overlap) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.13947, Stop 1.13917, Target 1.14247 — **-3.0 pips**
27. **WIN** [AMD] BUY EURUSD — Thu 30 08:30 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14771, Stop 1.14671, Target 1.15071 — **+30.0 pips**
28. **TRAIL** [AMD] BUY EURUSD — Tue 04 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.15088, Stop 1.15058, Target 1.15388 — **+10.0 pips**
29. **CLOSE** [AMD] BUY EURUSD — Tue 04 14:30 ET (NY PM) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.15287, Stop 1.15187, Target 1.15587 — **+9.3 pips**
30. **CLOSE** [MM] BUY EURUSD — Wed 05 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.15420, Stop 1.15339, Target 1.15720 — **+5.3 pips**
31. **CLOSE** [MM] BUY EURUSD — Wed 05 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.15594, Stop 1.15494, Target 1.15894 — **+0.0 pips**
32. **CLOSE** [MM] SELL GBPUSD — Thu 06 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.34553, Stop 1.34614, Target 1.34253 — **+2.7 pips**
33. **WIN** [MM] BUY EURUSD — Fri 07 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15300, Stop 1.15206, Target 1.15600 — **+30.0 pips**
34. **BE** [AMD] BUY EURUSD — Fri 07 10:00 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.15567, Stop 1.15467, Target 1.15867 — **+0.0 pips**
35. **CLOSE** [AMD] SELL GBPUSD — Mon 10 14:30 ET (NY PM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.35104, Stop 1.35204, Target 1.34804 — **+2.6 pips**
36. **BE** [AMD] BUY EURUSD — Wed 12 08:30 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.15540, Stop 1.15440, Target 1.15840 — **+0.0 pips**
37. **BE** [AMD] BUY EURUSD — Thu 13 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.15380, Stop 1.15280, Target 1.15680 — **+0.0 pips**
38. **LOSS** [MM] SELL GBPUSD — Thu 13 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.34896, Stop 1.34981, Target 1.34596 — **-8.4 pips**
39. **LOSS** [AMD] BUY EURUSD — Mon 17 04:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.16077, Stop 1.15977, Target 1.16377 — **-10.0 pips**
40. **LOSS** [MM] BUY EURUSD — Mon 17 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15982, Stop 1.15882, Target 1.16282 — **-10.0 pips**
41. **LOSS** [MM] SELL GBPUSD — Tue 18 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.35300, Stop 1.35357, Target 1.35000 — **-5.7 pips**
42. **BE** [AMD] BUY EURUSD — Wed 19 05:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.16036, Stop 1.15936, Target 1.16336 — **+0.0 pips**
43. **LOSS** [AMD] BUY EURUSD — Thu 20 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.16986, Stop 1.16917, Target 1.17286 — **-7.0 pips**
44. **LOSS** [AMD] BUY EURUSD — Fri 21 06:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.17069, Stop 1.16969, Target 1.17369 — **-10.0 pips**
45. **BE** [AMD] SELL GBPUSD — Tue 25 05:00 ET (London Open) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.36448, Stop 1.36548, Target 1.36148 — **+0.0 pips**
46. **LOSS** [AMD] SELL GBPUSD — Wed 26 06:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.36251, Stop 1.36351, Target 1.35951 — **-10.0 pips**
47. **LOSS** [AMD] SELL GBPUSD — Wed 26 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.36234, Stop 1.36334, Target 1.35934 — **-10.0 pips**
48. **TRAIL** [MM] SELL GBPUSD — Thu 27 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.35927, Stop 1.35979, Target 1.35627 — **+10.0 pips**
49. **TRAIL** [AMD] SELL GBPUSD — Thu 27 04:00 ET (London Open) — STRONG [BREAKOUT+MSS-2/3+SMT] — Entry 1.35927, Stop 1.35979, Target 1.35627 — **+10.0 pips**
50. **TRAIL** [AMD] SELL GBPUSD — Fri 28 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.35877, Stop 1.35977, Target 1.35577 — **+10.0 pips**
51. **TRAIL** [AMD] SELL GBPUSD — Fri 28 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.35827, Stop 1.35925, Target 1.35527 — **+10.0 pips**
52. **CLOSE** [MM] BUY EURUSD — Mon 31 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15996, Stop 1.15896, Target 1.16296 — **+20.2 pips**
53. **CLOSE** [AMD] BUY EURUSD — Mon 31 10:00 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.16023, Stop 1.15940, Target 1.16323 — **+18.9 pips**

## Outcome Breakdown

| Outcome | Count | Total Pips | Avg Pips |
|---|---|---|---|
| WIN (target hit) | 5 | +150.0 | +30.0 |
| TRAIL (+10 lock) | 7 | +70.0 | +10.0 |
| CLOSE (session end +) | 10 | +89.3 | +8.9 |
| BE (breakeven) | 7 | +0.0 | +0.0 |
| CLOSE (session end -) | 3 | -6.0 | -2.0 |
| LOSS (stop hit) | 21 | -174.4 | -8.3 |

## Model Breakdown (MM vs AMD)

| Model | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| MM | 20 | 9 | 8 | 45% | +74.7 | +3.7 |
| AMD (J:27 B:6) | 33 | 13 | 13 | 39% | +54.2 | +1.6 |

## Winner / Loser Analysis

### By Session

| Session | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| London Open | 17 | 7 | 8 | 41% | -4.2 |
| London→NY Overlap | 14 | 4 | 9 | 29% | +19.1 |
| NY AM | 9 | 4 | 2 | 44% | +90.5 |
| NY PM | 13 | 7 | 2 | 54% | +23.5 |

### By Confirmation Combo

| Confirmations | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| BREAKOUT+MSS-2/3 | 5 | 1 | 3 | 20% | -13.7 |
| BREAKOUT+MSS-2/3+SMT | 1 | 1 | 0 | 100% | +10.0 |
| IFVG+MSS+SMT | 20 | 9 | 8 | 45% | +74.7 |
| JUDAS+MSS-2/3 | 20 | 10 | 8 | 50% | +64.8 |
| JUDAS+MSS-2/3+SMT | 7 | 1 | 2 | 14% | -6.9 |

### By Time of Day (ET)

| Time | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| 04:00 | 10 | 5 | 5 | 50% | +5.8 |
| 05:00 | 7 | 2 | 3 | 29% | -10.0 |
| 06:00 | 7 | 1 | 6 | 14% | -18.7 |
| 07:00 | 7 | 3 | 3 | 43% | +37.8 |
| 08:30 | 4 | 2 | 1 | 50% | +51.6 |
| 10:00 | 5 | 2 | 1 | 40% | +38.9 |
| 14:30 | 6 | 2 | 1 | 33% | +3.5 |
| 16:00 | 7 | 5 | 1 | 71% | +20.0 |

## Intermarket Cascade (Bonds/DXY)

| Cascade | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| Confirmed (bonds+DXY agree) | 43 | 15 | 18 | 35% | +67.0 | +1.6 |
| Flat (no dollar signal) | 10 | 7 | 3 | 70% | +61.9 | +6.2 |

## Cascade Gate Impact

| Scenario | Trades | WR | Losses | Pips | Avg |
|---|---|---|---|---|---|
| WITHOUT gate (all) | 87 | 33% | 41 | +64.1 | +0.7 |
| **WITH gate (shipped)** | **53** | **42%** | **21** | **+128.9** | **+2.4** |
| Gated out (against) | 34 | 21% | 20 | -64.8 | -1.9 |

**Gate effect:** WR 33% -> 42% (+8pp), avg pips/trade +0.7 -> +2.4

### Gated Trades (skipped — dollar opposed direction)

| # | Date | Time (ET) | Model | Pair | Dir | Would-be Result | Pips |
|---|---|---|---|---|---|---|---|
| 1 | Fri 03 Jul | 04:00 | MM | GBPUSD | SELL | CLOSE | +15.5 |
| 2 | Fri 03 Jul | 16:00 | MM | GBPUSD | SELL | CLOSE | +4.3 |
| 3 | Mon 06 Jul | 04:00 | AMD | EURUSD | BUY | LOSS | -8.0 |
| 4 | Tue 07 Jul | 07:00 | MM | EURUSD | BUY | LOSS | -10.0 |
| 5 | Tue 07 Jul | 10:00 | MM | EURUSD | BUY | LOSS | -4.1 |
| 6 | Mon 13 Jul | 06:00 | AMD | GBPUSD | SELL | LOSS | -3.7 |
| 7 | Tue 14 Jul | 04:00 | AMD | GBPUSD | SELL | LOSS | -10.0 |
| 8 | Wed 15 Jul | 07:00 | MM | EURUSD | BUY | LOSS | -10.0 |
| 9 | Thu 16 Jul | 07:00 | AMD | EURUSD | BUY | LOSS | -10.0 |
| 10 | Thu 16 Jul | 08:30 | MM | EURUSD | BUY | LOSS | -3.0 |
| 11 | Fri 17 Jul | 05:00 | AMD | EURUSD | BUY | LOSS | -3.0 |
| 12 | Fri 17 Jul | 06:00 | AMD | EURUSD | BUY | LOSS | -3.0 |
| 13 | Wed 22 Jul | 08:30 | MM | GBPUSD | SELL | BE | +0.0 |
| 14 | Wed 22 Jul | 16:00 | AMD | GBPUSD | SELL | LOSS | -3.3 |
| 15 | Fri 24 Jul | 06:00 | AMD | GBPUSD | SELL | LOSS | -7.0 |
| 16 | Mon 27 Jul | 05:00 | AMD | GBPUSD | SELL | WIN | +30.0 |
| 17 | Tue 28 Jul | 05:00 | AMD | GBPUSD | SELL | TRAIL | +10.0 |
| 18 | Mon 03 Aug | 06:00 | AMD | EURUSD | BUY | LOSS | -5.5 |
| 19 | Mon 03 Aug | 16:00 | AMD | EURUSD | BUY | CLOSE | -2.7 |
| 20 | Wed 05 Aug | 04:00 | AMD | GBPUSD | SELL | BE | +0.0 |
| 21 | Tue 11 Aug | 05:00 | AMD | EURUSD | BUY | CLOSE | +5.3 |
| 22 | Wed 12 Aug | 04:00 | AMD | EURUSD | BUY | BE | +0.0 |
| 23 | Wed 12 Aug | 05:00 | MM | EURUSD | BUY | BE | +0.0 |
| 24 | Thu 13 Aug | 04:00 | AMD | EURUSD | BUY | TRAIL | +10.0 |
| 25 | Thu 13 Aug | 05:00 | AMD | EURUSD | BUY | TRAIL | +10.0 |
| 26 | Mon 17 Aug | 06:00 | MM | GBPUSD | SELL | LOSS | -10.0 |
| 27 | Tue 18 Aug | 07:00 | AMD | EURUSD | BUY | BE | +0.0 |
| 28 | Tue 18 Aug | 08:30 | MM | EURUSD | BUY | BE | +0.0 |
| 29 | Wed 26 Aug | 04:00 | AMD | EURUSD | BUY | LOSS | -10.0 |
| 30 | Wed 26 Aug | 05:00 | MM | EURUSD | BUY | LOSS | -10.0 |
| 31 | Wed 26 Aug | 05:00 | AMD | EURUSD | BUY | LOSS | -10.0 |
| 32 | Wed 26 Aug | 06:00 | MM | EURUSD | BUY | LOSS | -8.3 |
| 33 | Wed 26 Aug | 07:00 | MM | EURUSD | BUY | LOSS | -8.3 |
| 34 | Mon 31 Aug | 06:00 | AMD | GBPUSD | SELL | LOSS | -10.0 |

---

*Intermarket cascade: Bonds/Yields (T5/T10/T30) -> DXY -> EURGBP -> pair selection.*
*Simulation: structural M5 stop (capped 10 pips), trail BE at +10, lock +10 at +20, target 30 pips.*
*Session-end close resolves all trades -- no "OPEN" status.*
