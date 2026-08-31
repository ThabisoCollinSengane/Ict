# Replay Backtest (30 Jun - 31 Aug 2026)

Generated: 2026-08-31 17:50 UTC
Strategy: SELL GBPUSD (dollar UP) | BUY EURUSD (dollar DOWN)
Gate: Bonds/Yields → DXY → EURGBP → pair selection (intermarket cascade)
Models: **MM** (IFVG zone + MSS + SMT + FBC) | **AMD** (Judas reversal + breakout)
MM gate: IFVG+MSS+SMT (full triple) | AMD gate: MSS-2/3 minimum
Cascade gate: **ON (skip trades where dollar opposes direction)**
Max trades/day: 2 | Stop: structural M5, capped 10 pips | Trail: BE at +10, lock +10 at +20 | Target: 30 pips

## Weekly Summary

| Metric | Value |
|---|---|
| Total setups | **57** |
| Wins (hit 30-pip target) | **7** |
| Trail exits (+10 lock) | 7 |
| Session-end close (positive) | 13 |
| Breakeven | 6 |
| Session-end close (negative) | 3 |
| Losses (stop hit) | **21** |
| Profitable trades | **27** (47%) |
| Total pips | **+212.9** |
| Avg pips/trade | 3.7 |

## Per-Pair Summary

| Pair | Direction | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|---|
| GBPUSD | SELL | 25 | 15 | 6 | 60% | +81.6 |
| EURUSD | BUY | 32 | 12 | 15 | 38% | +131.3 |

## Day-by-Day Breakdown

### Tuesday 30 Jun 2026 — 2 setups (2P/0L, +60.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | — | **WIN** | +30.0 |
| 2 | 08:30 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | — | **WIN** | +30.0 |

### Wednesday 01 Jul 2026 — 2 setups (1P/1L, +0.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **LOSS** | -10.0 |
| 2 | 07:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **TRAIL** | +10.0 |

### Thursday 02 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Friday 03 Jul 2026 — 2 setups (2P/0L, +19.8 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **CLOSE** | +15.5 |
| 2 | 16:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **CLOSE** | +4.3 |

### Monday 06 Jul 2026 — 1 setups (0P/1L, -8.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | — | **LOSS** | -8.0 |

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

### Friday 17 Jul 2026 — 1 setups (1P/0L, +6.7 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 16:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | — | **CLOSE** | +6.7 |

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

### Monday 31 Aug 2026 — 2 setups (2P/0L, +40.5 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **CLOSE** | +21.6 |
| 2 | 10:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **CLOSE** | +18.9 |

## Session Breakdown

| Session | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| London Open | 18 | 8 | 8 | 44% | +7.4 |
| London→NY Overlap | 15 | 5 | 9 | 33% | +50.5 |
| NY AM | 9 | 5 | 2 | 56% | +120.5 |
| NY PM | 15 | 9 | 2 | 60% | +34.5 |

## Signal Strength

| Strength | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| STRONG (>=3 confirms) | 30 | 15 | 9 | 50% | +163.1 |
| MODERATE (>=2 confirms) | 27 | 12 | 12 | 44% | +49.8 |

## All Trades (detailed)

1. **WIN** [MM] BUY EURUSD — Tue 30 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.13999, Stop 1.13899, Target 1.14299 — **+30.0 pips**
2. **WIN** [MM] BUY EURUSD — Tue 30 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.13947, Stop 1.13854, Target 1.14247 — **+30.0 pips**
3. **LOSS** [MM] SELL GBPUSD — Wed 01 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.32459, Stop 1.32559, Target 1.32159 — **-10.0 pips**
4. **TRAIL** [MM] SELL GBPUSD — Wed 01 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.32489, Stop 1.32579, Target 1.32189 — **+10.0 pips**
5. **CLOSE** [MM] SELL GBPUSD — Fri 03 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.33695, Stop 1.33795, Target 1.33395 — **+15.5 pips**
6. **CLOSE** [MM] SELL GBPUSD — Fri 03 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33542, Stop 1.33598, Target 1.33242 — **+4.3 pips**
7. **LOSS** [AMD] BUY EURUSD — Mon 06 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14273, Stop 1.14192, Target 1.14573 — **-8.0 pips**
8. **LOSS** [AMD] BUY EURUSD — Wed 08 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14299, Stop 1.14199, Target 1.14599 — **-10.0 pips**
9. **LOSS** [MM] BUY EURUSD — Wed 08 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.14299, Stop 1.14199, Target 1.14599 — **-10.0 pips**
10. **LOSS** [AMD] BUY EURUSD — Thu 09 14:30 ET (NY PM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.14364, Stop 1.14310, Target 1.14664 — **-5.4 pips**
11. **LOSS** [MM] BUY EURUSD — Fri 10 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.14430, Stop 1.14375, Target 1.14730 — **-5.4 pips**
12. **LOSS** [AMD] BUY EURUSD — Fri 10 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14364, Stop 1.14264, Target 1.14664 — **-10.0 pips**
13. **LOSS** [AMD] BUY EURUSD — Mon 13 05:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.14390, Stop 1.14290, Target 1.14690 — **-10.0 pips**
14. **WIN** [AMD] BUY EURUSD — Tue 14 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13947, Stop 1.13880, Target 1.14247 — **+30.0 pips**
15. **TRAIL** [AMD] SELL GBPUSD — Wed 15 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34073, Stop 1.34173, Target 1.33773 — **+10.0 pips**
16. **WIN** [MM] BUY EURUSD — Wed 15 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.14247, Stop 1.14147, Target 1.14547 — **+30.0 pips**
17. **WIN** [MM] SELL GBPUSD — Thu 16 10:00 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.35108, Stop 1.35208, Target 1.34808 — **+30.0 pips**
18. **CLOSE** [AMD] SELL GBPUSD — Thu 16 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34760, Stop 1.34860, Target 1.34460 — **+11.1 pips**
19. **CLOSE** [AMD] SELL GBPUSD — Fri 17 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34591, Stop 1.34691, Target 1.34291 — **+6.7 pips**
20. **LOSS** [MM] BUY EURUSD — Mon 20 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.14351, Stop 1.14297, Target 1.14651 — **-5.4 pips**
21. **BE** [MM] SELL GBPUSD — Mon 20 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.34344, Stop 1.34444, Target 1.34044 — **+0.0 pips**
22. **LOSS** [AMD] SELL GBPUSD — Tue 21 10:00 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33847, Stop 1.33947, Target 1.33547 — **-10.0 pips**
23. **CLOSE** [MM] SELL GBPUSD — Tue 21 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33803, Stop 1.33893, Target 1.33503 — **-3.0 pips**
24. **CLOSE** [AMD] SELL GBPUSD — Thu 23 14:30 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33188, Stop 1.33275, Target 1.32888 — **-3.0 pips**
25. **CLOSE** [AMD] SELL GBPUSD — Thu 23 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33189, Stop 1.33275, Target 1.32889 — **+4.4 pips**
26. **LOSS** [AMD] BUY EURUSD — Fri 24 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13908, Stop 1.13808, Target 1.14208 — **-10.0 pips**
27. **CLOSE** [MM] SELL GBPUSD — Fri 24 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33230, Stop 1.33281, Target 1.32930 — **+4.4 pips**
28. **CLOSE** [AMD] BUY EURUSD — Tue 28 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13908, Stop 1.13808, Target 1.14208 — **+10.4 pips**
29. **LOSS** [MM] BUY EURUSD — Wed 29 05:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.13999, Stop 1.13899, Target 1.14299 — **-10.0 pips**
30. **LOSS** [AMD] BUY EURUSD — Wed 29 06:00 ET (London→NY Overlap) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.13947, Stop 1.13917, Target 1.14247 — **-3.0 pips**
31. **WIN** [AMD] BUY EURUSD — Thu 30 08:30 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14771, Stop 1.14671, Target 1.15071 — **+30.0 pips**
32. **TRAIL** [AMD] BUY EURUSD — Tue 04 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.15088, Stop 1.15058, Target 1.15388 — **+10.0 pips**
33. **CLOSE** [AMD] BUY EURUSD — Tue 04 14:30 ET (NY PM) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.15287, Stop 1.15187, Target 1.15587 — **+9.3 pips**
34. **CLOSE** [MM] BUY EURUSD — Wed 05 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.15420, Stop 1.15339, Target 1.15720 — **+5.3 pips**
35. **CLOSE** [MM] BUY EURUSD — Wed 05 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.15594, Stop 1.15494, Target 1.15894 — **+0.0 pips**
36. **CLOSE** [MM] SELL GBPUSD — Thu 06 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.34553, Stop 1.34614, Target 1.34253 — **+2.7 pips**
37. **WIN** [MM] BUY EURUSD — Fri 07 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15300, Stop 1.15206, Target 1.15600 — **+30.0 pips**
38. **BE** [AMD] BUY EURUSD — Fri 07 10:00 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.15567, Stop 1.15467, Target 1.15867 — **+0.0 pips**
39. **CLOSE** [AMD] SELL GBPUSD — Mon 10 14:30 ET (NY PM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.35104, Stop 1.35204, Target 1.34804 — **+2.6 pips**
40. **BE** [AMD] BUY EURUSD — Wed 12 08:30 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.15540, Stop 1.15440, Target 1.15840 — **+0.0 pips**
41. **BE** [AMD] BUY EURUSD — Thu 13 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.15380, Stop 1.15280, Target 1.15680 — **+0.0 pips**
42. **LOSS** [MM] SELL GBPUSD — Thu 13 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.34896, Stop 1.34981, Target 1.34596 — **-8.4 pips**
43. **LOSS** [AMD] BUY EURUSD — Mon 17 04:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.16077, Stop 1.15977, Target 1.16377 — **-10.0 pips**
44. **LOSS** [MM] BUY EURUSD — Mon 17 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15982, Stop 1.15882, Target 1.16282 — **-10.0 pips**
45. **LOSS** [MM] SELL GBPUSD — Tue 18 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.35300, Stop 1.35357, Target 1.35000 — **-5.7 pips**
46. **BE** [AMD] BUY EURUSD — Wed 19 05:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.16036, Stop 1.15936, Target 1.16336 — **+0.0 pips**
47. **LOSS** [AMD] BUY EURUSD — Thu 20 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.16986, Stop 1.16917, Target 1.17286 — **-7.0 pips**
48. **LOSS** [AMD] BUY EURUSD — Fri 21 06:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.17069, Stop 1.16969, Target 1.17369 — **-10.0 pips**
49. **BE** [AMD] SELL GBPUSD — Tue 25 05:00 ET (London Open) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.36448, Stop 1.36548, Target 1.36148 — **+0.0 pips**
50. **LOSS** [AMD] SELL GBPUSD — Wed 26 06:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.36251, Stop 1.36351, Target 1.35951 — **-10.0 pips**
51. **LOSS** [AMD] SELL GBPUSD — Wed 26 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.36234, Stop 1.36334, Target 1.35934 — **-10.0 pips**
52. **TRAIL** [MM] SELL GBPUSD — Thu 27 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.35927, Stop 1.35979, Target 1.35627 — **+10.0 pips**
53. **TRAIL** [AMD] SELL GBPUSD — Thu 27 04:00 ET (London Open) — STRONG [BREAKOUT+MSS-2/3+SMT] — Entry 1.35927, Stop 1.35979, Target 1.35627 — **+10.0 pips**
54. **TRAIL** [AMD] SELL GBPUSD — Fri 28 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.35877, Stop 1.35977, Target 1.35577 — **+10.0 pips**
55. **TRAIL** [AMD] SELL GBPUSD — Fri 28 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.35827, Stop 1.35925, Target 1.35527 — **+10.0 pips**
56. **CLOSE** [MM] BUY EURUSD — Mon 31 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15996, Stop 1.15896, Target 1.16296 — **+21.6 pips**
57. **CLOSE** [AMD] BUY EURUSD — Mon 31 10:00 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.16023, Stop 1.15940, Target 1.16323 — **+18.9 pips**

## Outcome Breakdown

| Outcome | Count | Total Pips | Avg Pips |
|---|---|---|---|
| WIN (target hit) | 7 | +210.0 | +30.0 |
| TRAIL (+10 lock) | 7 | +70.0 | +10.0 |
| CLOSE (session end +) | 13 | +117.2 | +9.0 |
| BE (breakeven) | 6 | +0.0 | +0.0 |
| CLOSE (session end -) | 3 | -6.0 | -2.0 |
| LOSS (stop hit) | 21 | -178.3 | -8.5 |

## Model Breakdown (MM vs AMD)

| Model | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| MM | 24 | 13 | 8 | 54% | +155.9 | +6.5 |
| AMD (J:27 B:6) | 33 | 14 | 13 | 42% | +57.0 | +1.7 |

## Winner / Loser Analysis

### By Session

| Session | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| London Open | 18 | 8 | 8 | 44% | +7.4 |
| London→NY Overlap | 15 | 5 | 9 | 33% | +50.5 |
| NY AM | 9 | 5 | 2 | 56% | +120.5 |
| NY PM | 15 | 9 | 2 | 60% | +34.5 |

### By Confirmation Combo

| Confirmations | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| BREAKOUT+MSS-2/3 | 5 | 1 | 3 | 20% | -13.7 |
| BREAKOUT+MSS-2/3+SMT | 1 | 1 | 0 | 100% | +10.0 |
| IFVG+MSS+SMT | 24 | 13 | 8 | 54% | +155.9 |
| JUDAS+MSS-2/3 | 22 | 11 | 9 | 50% | +63.5 |
| JUDAS+MSS-2/3+SMT | 5 | 1 | 1 | 20% | -2.8 |

### By Time of Day (ET)

| Time | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| 04:00 | 11 | 6 | 5 | 55% | +17.4 |
| 05:00 | 7 | 2 | 3 | 29% | -10.0 |
| 06:00 | 8 | 2 | 6 | 25% | +11.3 |
| 07:00 | 7 | 3 | 3 | 43% | +39.2 |
| 08:30 | 5 | 3 | 1 | 60% | +81.6 |
| 10:00 | 4 | 2 | 1 | 50% | +38.9 |
| 14:30 | 6 | 2 | 1 | 33% | +3.5 |
| 16:00 | 9 | 7 | 1 | 78% | +31.0 |

## Intermarket Cascade (Bonds/DXY)

| Cascade | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| Confirmed (bonds+DXY agree) | 42 | 15 | 18 | 36% | +68.4 | +1.6 |
| Flat (no dollar signal) | 15 | 12 | 3 | 80% | +144.5 | +9.6 |

## Cascade Gate Impact

| Scenario | Trades | WR | Losses | Pips | Avg |
|---|---|---|---|---|---|
| WITHOUT gate (all) | 86 | 37% | 38 | +142.3 | +1.7 |
| **WITH gate (shipped)** | **57** | **47%** | **21** | **+212.9** | **+3.7** |
| Gated out (against) | 29 | 17% | 17 | -70.6 | -2.4 |

**Gate effect:** WR 37% -> 47% (+10pp), avg pips/trade +1.7 -> +3.7

### Gated Trades (skipped — dollar opposed direction)

| # | Date | Time (ET) | Model | Pair | Dir | Would-be Result | Pips |
|---|---|---|---|---|---|---|---|
| 1 | Tue 07 Jul | 07:00 | MM | EURUSD | BUY | LOSS | -10.0 |
| 2 | Tue 07 Jul | 10:00 | MM | EURUSD | BUY | LOSS | -4.1 |
| 3 | Mon 13 Jul | 06:00 | AMD | GBPUSD | SELL | LOSS | -3.7 |
| 4 | Tue 14 Jul | 04:00 | AMD | GBPUSD | SELL | LOSS | -10.0 |
| 5 | Wed 15 Jul | 07:00 | MM | EURUSD | BUY | LOSS | -10.0 |
| 6 | Thu 16 Jul | 07:00 | AMD | EURUSD | BUY | LOSS | -10.0 |
| 7 | Thu 16 Jul | 08:30 | MM | EURUSD | BUY | LOSS | -3.0 |
| 8 | Wed 22 Jul | 08:30 | MM | GBPUSD | SELL | BE | +0.0 |
| 9 | Wed 22 Jul | 16:00 | AMD | GBPUSD | SELL | LOSS | -3.3 |
| 10 | Fri 24 Jul | 06:00 | AMD | GBPUSD | SELL | LOSS | -7.0 |
| 11 | Mon 27 Jul | 05:00 | AMD | GBPUSD | SELL | WIN | +30.0 |
| 12 | Tue 28 Jul | 05:00 | AMD | GBPUSD | SELL | TRAIL | +10.0 |
| 13 | Mon 03 Aug | 06:00 | AMD | EURUSD | BUY | LOSS | -5.5 |
| 14 | Mon 03 Aug | 16:00 | AMD | EURUSD | BUY | CLOSE | -2.7 |
| 15 | Wed 05 Aug | 04:00 | AMD | GBPUSD | SELL | BE | +0.0 |
| 16 | Tue 11 Aug | 05:00 | AMD | EURUSD | BUY | CLOSE | +5.3 |
| 17 | Wed 12 Aug | 04:00 | AMD | EURUSD | BUY | BE | +0.0 |
| 18 | Wed 12 Aug | 05:00 | MM | EURUSD | BUY | BE | +0.0 |
| 19 | Thu 13 Aug | 04:00 | AMD | EURUSD | BUY | TRAIL | +10.0 |
| 20 | Thu 13 Aug | 05:00 | AMD | EURUSD | BUY | TRAIL | +10.0 |
| 21 | Mon 17 Aug | 06:00 | MM | GBPUSD | SELL | LOSS | -10.0 |
| 22 | Tue 18 Aug | 07:00 | AMD | EURUSD | BUY | BE | +0.0 |
| 23 | Tue 18 Aug | 08:30 | MM | EURUSD | BUY | BE | +0.0 |
| 24 | Wed 26 Aug | 04:00 | AMD | EURUSD | BUY | LOSS | -10.0 |
| 25 | Wed 26 Aug | 05:00 | MM | EURUSD | BUY | LOSS | -10.0 |
| 26 | Wed 26 Aug | 05:00 | AMD | EURUSD | BUY | LOSS | -10.0 |
| 27 | Wed 26 Aug | 06:00 | MM | EURUSD | BUY | LOSS | -8.3 |
| 28 | Wed 26 Aug | 07:00 | MM | EURUSD | BUY | LOSS | -8.3 |
| 29 | Mon 31 Aug | 06:00 | AMD | GBPUSD | SELL | LOSS | -10.0 |

---

*Intermarket cascade: Bonds/Yields (T5/T10/T30) -> DXY -> EURGBP -> pair selection.*
*Simulation: structural M5 stop (capped 10 pips), trail BE at +10, lock +10 at +20, target 30 pips.*
*Session-end close resolves all trades -- no "OPEN" status.*
