# Replay Backtest (02 Jul - 02 Sep 2026)

Generated: 2026-09-02 06:46 UTC
Strategy: SELL GBPUSD (dollar UP) | BUY EURUSD (dollar DOWN)
Gate: Bonds/Yields → DXY → EURGBP → pair selection (intermarket cascade)
Models: **MM** (IFVG zone + MSS + SMT + FBC) | **AMD** (Judas reversal + breakout)
MM gate: IFVG+MSS+SMT (full triple) | AMD gate: MSS-2/3 minimum
Cascade gate: **ON (skip trades where dollar opposes direction)**
Max trades/day: 2 | Stop: structural M5, capped 10 pips | Trail: BE at +10, lock +10 at +20 | Target: 20 pips

## Weekly Summary

| Metric | Value |
|---|---|
| Total setups | **51** |
| Wins (hit 20-pip target) | **11** |
| Trail exits (+10 lock) | 2 |
| Session-end close (positive) | 8 |
| Breakeven | 7 |
| Session-end close (negative) | 3 |
| Losses (stop hit) | **20** |
| Profitable trades | **21** (41%) |
| Total pips | **+119.8** |
| Avg pips/trade | 2.3 |

## Per-Pair Summary

| Pair | Direction | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|---|
| GBPUSD | SELL | 21 | 11 | 5 | 52% | +75.1 |
| EURUSD | BUY | 30 | 10 | 15 | 33% | +44.7 |

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

### Friday 10 Jul 2026 — 2 setups (0P/2L, -15.4 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **LOSS** | -5.4 |
| 2 | 05:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **LOSS** | -10.0 |

### Monday 13 Jul 2026 — 1 setups (0P/1L, -10.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 05:00 | AMD | EURUSD | BUY | MODERATE | BREAKOUT+MSS-2/3 | Y | **LOSS** | -10.0 |

### Tuesday 14 Jul 2026 — 1 setups (1P/0L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **WIN** | +20.0 |

### Wednesday 15 Jul 2026 — 2 setups (2P/0L, +40.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | — | **WIN** | +20.0 |
| 2 | 08:30 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | — | **WIN** | +20.0 |

### Thursday 16 Jul 2026 — 2 setups (2P/0L, +31.1 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | Y | **WIN** | +20.0 |
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

### Thursday 30 Jul 2026 — 1 setups (1P/0L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 08:30 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **WIN** | +20.0 |

### Friday 31 Jul 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Monday 03 Aug 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Tuesday 04 Aug 2026 — 2 setups (2P/0L, +29.3 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 05:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | — | **WIN** | +20.0 |
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

### Friday 07 Aug 2026 — 2 setups (1P/0L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **WIN** | +20.0 |
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

### Thursday 27 Aug 2026 — 2 setups (2P/0L, +40.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | MM | GBPUSD | SELL | STRONG | IFVG+MSS+SMT | — | **WIN** | +20.0 |
| 2 | 04:00 | AMD | GBPUSD | SELL | STRONG | BREAKOUT+MSS-2/3+SMT | — | **WIN** | +20.0 |

### Friday 28 Aug 2026 — 2 setups (2P/0L, +20.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **TRAIL** | +10.0 |
| 2 | 05:00 | AMD | GBPUSD | SELL | MODERATE | JUDAS+MSS-2/3 | Y | **TRAIL** | +10.0 |

### Monday 31 Aug 2026 — 2 setups (2P/0L, +40.0 pips)

| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 07:00 | MM | EURUSD | BUY | STRONG | IFVG+MSS+SMT | Y | **WIN** | +20.0 |
| 2 | 10:00 | AMD | EURUSD | BUY | MODERATE | JUDAS+MSS-2/3 | Y | **WIN** | +20.0 |

### Tuesday 01 Sep 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

### Wednesday 02 Sep 2026 — No setups

No setups (MM or AMD) met the 2-confirmation threshold during any killzone.

## Session Breakdown

| Session | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| London Open | 17 | 7 | 8 | 41% | +35.8 |
| London→NY Overlap | 12 | 3 | 8 | 25% | -1.1 |
| NY AM | 9 | 4 | 2 | 44% | +61.6 |
| NY PM | 13 | 7 | 2 | 54% | +23.5 |

## Signal Strength

| Strength | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| STRONG (>=3 confirms) | 26 | 10 | 9 | 38% | +67.6 |
| MODERATE (>=2 confirms) | 25 | 11 | 11 | 44% | +52.2 |

## All Trades (detailed)

1. **LOSS** [AMD] BUY EURUSD — Wed 08 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14299, Stop 1.14199, Target 1.14499 — **-10.0 pips**
2. **LOSS** [MM] BUY EURUSD — Wed 08 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.14299, Stop 1.14199, Target 1.14499 — **-10.0 pips** MFE +1
3. **LOSS** [AMD] BUY EURUSD — Thu 09 14:30 ET (NY PM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.14364, Stop 1.14310, Target 1.14564 — **-5.4 pips** MFE +1
4. **LOSS** [MM] BUY EURUSD — Fri 10 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.14430, Stop 1.14375, Target 1.14630 — **-5.4 pips** MFE +3
5. **LOSS** [AMD] BUY EURUSD — Fri 10 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14364, Stop 1.14264, Target 1.14564 — **-10.0 pips** MFE +4
6. **LOSS** [AMD] BUY EURUSD — Mon 13 05:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.14390, Stop 1.14290, Target 1.14590 — **-10.0 pips** MFE +1
7. **WIN** [AMD] BUY EURUSD — Tue 14 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13947, Stop 1.13880, Target 1.14147 — **+20.0 pips** MFE +21 ★20
8. **WIN** [AMD] SELL GBPUSD — Wed 15 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34073, Stop 1.34173, Target 1.33873 — **+20.0 pips** MFE +22 ★20
9. **WIN** [MM] BUY EURUSD — Wed 15 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.14247, Stop 1.14147, Target 1.14447 — **+20.0 pips** MFE +21 ★20
10. **WIN** [MM] SELL GBPUSD — Thu 16 10:00 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.35108, Stop 1.35208, Target 1.34908 — **+20.0 pips** MFE +20 ★20
11. **CLOSE** [AMD] SELL GBPUSD — Thu 16 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.34760, Stop 1.34860, Target 1.34560 — **+11.1 pips** MFE +12
12. **LOSS** [AMD] BUY EURUSD — Fri 17 04:00 ET (London Open) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.14495, Stop 1.14454, Target 1.14695 — **-4.1 pips** MFE +1
13. **BE** [AMD] SELL GBPUSD — Fri 17 10:00 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.34499, Stop 1.34599, Target 1.34299 — **+0.0 pips** MFE +11
14. **LOSS** [MM] BUY EURUSD — Mon 20 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.14351, Stop 1.14297, Target 1.14551 — **-5.4 pips** MFE +8
15. **BE** [MM] SELL GBPUSD — Mon 20 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.34344, Stop 1.34444, Target 1.34144 — **+0.0 pips** MFE +11
16. **LOSS** [AMD] SELL GBPUSD — Tue 21 10:00 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33847, Stop 1.33947, Target 1.33647 — **-10.0 pips**
17. **CLOSE** [MM] SELL GBPUSD — Tue 21 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33803, Stop 1.33893, Target 1.33603 — **-3.0 pips** MFE +9
18. **CLOSE** [AMD] SELL GBPUSD — Thu 23 14:30 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33188, Stop 1.33275, Target 1.32988 — **-3.0 pips** MFE +8
19. **CLOSE** [AMD] SELL GBPUSD — Thu 23 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.33189, Stop 1.33275, Target 1.32989 — **+4.4 pips** MFE +9
20. **LOSS** [AMD] BUY EURUSD — Fri 24 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13908, Stop 1.13808, Target 1.14108 — **-10.0 pips** MFE +5
21. **CLOSE** [MM] SELL GBPUSD — Fri 24 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.33230, Stop 1.33281, Target 1.33030 — **+4.4 pips** MFE +6
22. **CLOSE** [AMD] BUY EURUSD — Tue 28 16:00 ET (NY PM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.13908, Stop 1.13808, Target 1.14108 — **+10.4 pips** MFE +13
23. **LOSS** [MM] BUY EURUSD — Wed 29 05:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.13999, Stop 1.13899, Target 1.14199 — **-10.0 pips**
24. **LOSS** [AMD] BUY EURUSD — Wed 29 06:00 ET (London→NY Overlap) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.13947, Stop 1.13917, Target 1.14147 — **-3.0 pips** MFE +1
25. **WIN** [AMD] BUY EURUSD — Thu 30 08:30 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.14771, Stop 1.14671, Target 1.14971 — **+20.0 pips** MFE +28 ★20
26. **WIN** [AMD] BUY EURUSD — Tue 04 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.15088, Stop 1.15058, Target 1.15288 — **+20.0 pips** MFE +23 ★20
27. **CLOSE** [AMD] BUY EURUSD — Tue 04 14:30 ET (NY PM) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.15287, Stop 1.15187, Target 1.15487 — **+9.3 pips** MFE +9
28. **CLOSE** [MM] BUY EURUSD — Wed 05 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.15420, Stop 1.15339, Target 1.15620 — **+5.3 pips** MFE +17
29. **CLOSE** [MM] BUY EURUSD — Wed 05 14:30 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.15594, Stop 1.15494, Target 1.15794 — **+0.0 pips** MFE +4
30. **CLOSE** [MM] SELL GBPUSD — Thu 06 16:00 ET (NY PM) — STRONG [IFVG+MSS+SMT] — Entry 1.34553, Stop 1.34614, Target 1.34353 — **+2.7 pips** MFE +9
31. **WIN** [MM] BUY EURUSD — Fri 07 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15300, Stop 1.15206, Target 1.15500 — **+20.0 pips** MFE +45 ★20
32. **BE** [AMD] BUY EURUSD — Fri 07 10:00 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.15567, Stop 1.15467, Target 1.15767 — **+0.0 pips** MFE +11
33. **CLOSE** [AMD] SELL GBPUSD — Mon 10 14:30 ET (NY PM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.35104, Stop 1.35204, Target 1.34904 — **+2.6 pips** MFE +5
34. **BE** [AMD] BUY EURUSD — Wed 12 08:30 ET (NY AM) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.15540, Stop 1.15440, Target 1.15740 — **+0.0 pips** MFE +11
35. **BE** [AMD] BUY EURUSD — Thu 13 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.15380, Stop 1.15280, Target 1.15580 — **+0.0 pips** MFE +11
36. **LOSS** [MM] SELL GBPUSD — Thu 13 08:30 ET (NY AM) — STRONG [IFVG+MSS+SMT] — Entry 1.34896, Stop 1.34981, Target 1.34696 — **-8.4 pips**
37. **LOSS** [AMD] BUY EURUSD — Mon 17 04:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.16077, Stop 1.15977, Target 1.16277 — **-10.0 pips** MFE +9
38. **LOSS** [MM] BUY EURUSD — Mon 17 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15982, Stop 1.15882, Target 1.16182 — **-10.0 pips** MFE +4
39. **LOSS** [MM] SELL GBPUSD — Tue 18 06:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.35300, Stop 1.35357, Target 1.35100 — **-5.7 pips** MFE +9
40. **BE** [AMD] BUY EURUSD — Wed 19 05:00 ET (London Open) — MODERATE [BREAKOUT+MSS-2/3] — Entry 1.16036, Stop 1.15936, Target 1.16236 — **+0.0 pips** MFE +12
41. **LOSS** [AMD] BUY EURUSD — Thu 20 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.16986, Stop 1.16917, Target 1.17186 — **-7.0 pips** MFE +1
42. **LOSS** [AMD] BUY EURUSD — Fri 21 06:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.17069, Stop 1.16969, Target 1.17269 — **-10.0 pips** MFE +7
43. **BE** [AMD] SELL GBPUSD — Tue 25 05:00 ET (London Open) — STRONG [JUDAS+MSS-2/3+SMT] — Entry 1.36448, Stop 1.36548, Target 1.36248 — **+0.0 pips** MFE +18
44. **LOSS** [AMD] SELL GBPUSD — Wed 26 06:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.36251, Stop 1.36351, Target 1.36051 — **-10.0 pips** MFE +7
45. **LOSS** [AMD] SELL GBPUSD — Wed 26 07:00 ET (London→NY Overlap) — MODERATE [JUDAS+MSS-2/3] — Entry 1.36234, Stop 1.36334, Target 1.36034 — **-10.0 pips** MFE +1
46. **WIN** [MM] SELL GBPUSD — Thu 27 04:00 ET (London Open) — STRONG [IFVG+MSS+SMT] — Entry 1.35927, Stop 1.35979, Target 1.35727 — **+20.0 pips** MFE +20 ★20
47. **WIN** [AMD] SELL GBPUSD — Thu 27 04:00 ET (London Open) — STRONG [BREAKOUT+MSS-2/3+SMT] — Entry 1.35927, Stop 1.35979, Target 1.35727 — **+20.0 pips** MFE +20 ★20
48. **TRAIL** [AMD] SELL GBPUSD — Fri 28 04:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.35877, Stop 1.35977, Target 1.35677 — **+10.0 pips** MFE +34 ★20
49. **TRAIL** [AMD] SELL GBPUSD — Fri 28 05:00 ET (London Open) — MODERATE [JUDAS+MSS-2/3] — Entry 1.35827, Stop 1.35925, Target 1.35627 — **+10.0 pips** MFE +29 ★20
50. **WIN** [MM] BUY EURUSD — Mon 31 07:00 ET (London→NY Overlap) — STRONG [IFVG+MSS+SMT] — Entry 1.15996, Stop 1.15896, Target 1.16196 — **+20.0 pips** MFE +22 ★20
51. **WIN** [AMD] BUY EURUSD — Mon 31 10:00 ET (NY AM) — MODERATE [JUDAS+MSS-2/3] — Entry 1.16023, Stop 1.15940, Target 1.16223 — **+20.0 pips** MFE +20 ★20

## Outcome Breakdown

| Outcome | Count | Total Pips | Avg Pips |
|---|---|---|---|
| WIN (target hit) | 11 | +220.0 | +20.0 |
| TRAIL (+10 lock) | 2 | +20.0 | +10.0 |
| CLOSE (session end +) | 8 | +50.2 | +6.3 |
| BE (breakeven) | 7 | +0.0 | +0.0 |
| CLOSE (session end -) | 3 | -6.0 | -2.0 |
| LOSS (stop hit) | 20 | -164.4 | -8.2 |

## 20-Pip Milestone (notification point)

**13 of 51 trades reached +20 pips** — these would trigger a notification.

| Group | Trades | WR | Pips | Avg | Avg MFE |
|---|---|---|---|---|---|
| Reached +20 (★20) | 13 | 100% | +240.0 | +18.5 | +25 |
| Never reached +20 | 38 | 21% | -120.2 | -3.2 | +7 |

**2 trades reached +20 but exited below +20** (trail/close/loss after reversal).
Closing at +20 would have gained **+20 extra pips** on those trades.

*★20 = trade reached +20 pips MFE (notification would fire). Use `--close-at-20` to simulate closing all trades at 20 pips.*

## Model Breakdown (MM vs AMD)

| Model | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| MM | 18 | 8 | 7 | 44% | +54.5 | +3.0 |
| AMD (J:27 B:6) | 33 | 13 | 13 | 39% | +65.3 | +2.0 |

## Winner / Loser Analysis

### By Session

| Session | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| London Open | 17 | 7 | 8 | 41% | +35.8 |
| London→NY Overlap | 12 | 3 | 8 | 25% | -1.1 |
| NY AM | 9 | 4 | 2 | 44% | +61.6 |
| NY PM | 13 | 7 | 2 | 54% | +23.5 |

### By Confirmation Combo

| Confirmations | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| BREAKOUT+MSS-2/3 | 5 | 1 | 3 | 20% | -13.7 |
| BREAKOUT+MSS-2/3+SMT | 1 | 1 | 0 | 100% | +20.0 |
| IFVG+MSS+SMT | 18 | 8 | 7 | 44% | +54.5 |
| JUDAS+MSS-2/3 | 20 | 10 | 8 | 50% | +65.9 |
| JUDAS+MSS-2/3+SMT | 7 | 1 | 2 | 14% | -6.9 |

### By Time of Day (ET)

| Time | Trades | Prof | L | WR | Pips |
|---|---|---|---|---|---|
| 04:00 | 10 | 5 | 5 | 50% | +35.8 |
| 05:00 | 7 | 2 | 3 | 29% | +0.0 |
| 06:00 | 6 | 1 | 5 | 17% | -18.7 |
| 07:00 | 6 | 2 | 3 | 33% | +17.6 |
| 08:30 | 4 | 2 | 1 | 50% | +31.6 |
| 10:00 | 5 | 2 | 1 | 40% | +30.0 |
| 14:30 | 6 | 2 | 1 | 33% | +3.5 |
| 16:00 | 7 | 5 | 1 | 71% | +20.0 |

## Intermarket Cascade (Bonds/DXY)

| Cascade | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| Confirmed (bonds+DXY agree) | 43 | 15 | 18 | 35% | +27.9 | +0.6 |
| Flat (no dollar signal) | 8 | 6 | 2 | 75% | +91.9 | +11.5 |

## Per-Layer Cascade Breakdown

*All trades (kept + gated) for full picture of each layer's signal quality.*

### Layer 0 — Yield Curve (Bonds)

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| Yields agree (2-3/3) | 15 | 3 | 9 | 20% | -25.6 | -1.7 |
| Yields partial (1/3) | 13 | 3 | 8 | 23% | -19.6 | -1.5 |
| Yields flat (0/3) | 58 | 22 | 24 | 38% | +119.2 | +2.1 |

### Layer 1 — DXY vs Daily Open

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| DXY bid (+1) | 39 | 10 | 19 | 26% | -47.0 | -1.2 |
| DXY flat (0) | 8 | 6 | 2 | 75% | +91.9 | +11.5 |
| DXY offer (-1) | 39 | 12 | 20 | 31% | +29.1 | +0.7 |

### Layer 1b — Bonds/DXY Agreement

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| Bonds+DXY agree | 9 | 1 | 4 | 11% | -28.3 | -3.1 |
| Bonds+DXY disagree | 69 | 21 | 35 | 30% | +10.4 | +0.2 |
| N/A (DXY flat) | 8 | 6 | 2 | 75% | +91.9 | +11.5 |

### Layer 1c — Bonds/DXY SMT Divergence

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| SMT divergence | 58 | 16 | 31 | 28% | -7.8 | -0.1 |
| No SMT | 28 | 12 | 10 | 43% | +81.8 | +2.9 |

### Layer 2 — EURGBP Bias (pair selection)

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| EUR > GBP (+1) | 5 | 2 | 1 | 40% | +22.3 | +4.5 |
| Flat (0) | 80 | 26 | 40 | 32% | +51.7 | +0.6 |
| GBP > EUR (-1) | 1 | 0 | 0 | 0% | +0.0 | +0.0 |

### Layer 3 — EU/GU Entry SMT

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|
| No entry SMT | 86 | 28 | 41 | 33% | +74.0 | +0.9 |

### Curve Stress

| State | Trades | Prof | L | WR | Pips | Avg |
|---|---|---|---|---|---|---|

## Cascade Gate Impact

| Scenario | Trades | WR | Losses | Pips | Avg |
|---|---|---|---|---|---|
| WITHOUT gate (all) | 86 | 33% | 41 | +74.0 | +0.9 |
| **WITH gate (shipped)** | **51** | **41%** | **20** | **+119.8** | **+2.3** |
| Gated out (all reasons) | 35 | 20% | 21 | -45.8 | -1.3 |
|   — against | 35 | 20% | 21 | -45.8 | -1.3 |

**Gate effect:** WR 33% -> 41% (+9pp), avg pips/trade +0.9 -> +2.3

### Gated Trades (skipped)

| # | Date | Time (ET) | Model | Pair | Dir | Gate | Would-be Result | Pips |
|---|---|---|---|---|---|---|---|---|
| 1 | Fri 03 Jul | 04:00 | MM | GBPUSD | SELL | against | WIN | +20.0 |
| 2 | Fri 03 Jul | 16:00 | MM | GBPUSD | SELL | against | CLOSE | +4.3 |
| 3 | Mon 06 Jul | 04:00 | AMD | EURUSD | BUY | against | LOSS | -8.0 |
| 4 | Tue 07 Jul | 07:00 | MM | EURUSD | BUY | against | LOSS | -10.0 |
| 5 | Tue 07 Jul | 10:00 | MM | EURUSD | BUY | against | LOSS | -4.1 |
| 6 | Mon 13 Jul | 06:00 | AMD | GBPUSD | SELL | against | LOSS | -3.7 |
| 7 | Tue 14 Jul | 04:00 | AMD | GBPUSD | SELL | against | LOSS | -10.0 |
| 8 | Wed 15 Jul | 07:00 | MM | EURUSD | BUY | against | LOSS | -10.0 |
| 9 | Thu 16 Jul | 07:00 | AMD | EURUSD | BUY | against | LOSS | -10.0 |
| 10 | Thu 16 Jul | 08:30 | MM | EURUSD | BUY | against | LOSS | -3.0 |
| 11 | Fri 17 Jul | 05:00 | AMD | EURUSD | BUY | against | LOSS | -3.0 |
| 12 | Fri 17 Jul | 06:00 | AMD | EURUSD | BUY | against | LOSS | -3.0 |
| 13 | Wed 22 Jul | 08:30 | MM | GBPUSD | SELL | against | BE | +0.0 |
| 14 | Wed 22 Jul | 16:00 | AMD | GBPUSD | SELL | against | LOSS | -3.3 |
| 15 | Fri 24 Jul | 06:00 | AMD | GBPUSD | SELL | against | LOSS | -7.0 |
| 16 | Mon 27 Jul | 05:00 | AMD | GBPUSD | SELL | against | WIN | +20.0 |
| 17 | Tue 28 Jul | 05:00 | AMD | GBPUSD | SELL | against | WIN | +20.0 |
| 18 | Mon 03 Aug | 06:00 | AMD | EURUSD | BUY | against | LOSS | -5.5 |
| 19 | Mon 03 Aug | 16:00 | AMD | EURUSD | BUY | against | CLOSE | -2.7 |
| 20 | Wed 05 Aug | 04:00 | AMD | GBPUSD | SELL | against | BE | +0.0 |
| 21 | Tue 11 Aug | 05:00 | AMD | EURUSD | BUY | against | CLOSE | +5.3 |
| 22 | Wed 12 Aug | 04:00 | AMD | EURUSD | BUY | against | BE | +0.0 |
| 23 | Wed 12 Aug | 05:00 | MM | EURUSD | BUY | against | BE | +0.0 |
| 24 | Thu 13 Aug | 04:00 | AMD | EURUSD | BUY | against | WIN | +20.0 |
| 25 | Thu 13 Aug | 05:00 | AMD | EURUSD | BUY | against | WIN | +20.0 |
| 26 | Mon 17 Aug | 06:00 | MM | GBPUSD | SELL | against | LOSS | -10.0 |
| 27 | Tue 18 Aug | 07:00 | AMD | EURUSD | BUY | against | BE | +0.0 |
| 28 | Tue 18 Aug | 08:30 | MM | EURUSD | BUY | against | BE | +0.0 |
| 29 | Wed 26 Aug | 04:00 | AMD | EURUSD | BUY | against | LOSS | -10.0 |
| 30 | Wed 26 Aug | 05:00 | MM | EURUSD | BUY | against | LOSS | -10.0 |
| 31 | Wed 26 Aug | 05:00 | AMD | EURUSD | BUY | against | LOSS | -10.0 |
| 32 | Wed 26 Aug | 06:00 | MM | EURUSD | BUY | against | LOSS | -8.3 |
| 33 | Wed 26 Aug | 07:00 | MM | EURUSD | BUY | against | LOSS | -8.3 |
| 34 | Mon 31 Aug | 06:00 | AMD | GBPUSD | SELL | against | LOSS | -10.0 |
| 35 | Tue 01 Sep | 16:00 | MM | EURUSD | BUY | against | LOSS | -5.5 |

---

*Intermarket cascade: Bonds/Yields (T5/T10/T30) -> DXY -> EURGBP -> pair selection.*
*Simulation: structural M5 stop (capped 10 pips), trail BE at +10, lock +10 at +20, target 20 pips.*
*Session-end close resolves all trades -- no "OPEN" status.*
