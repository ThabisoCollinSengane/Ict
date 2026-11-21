# The algo measured against reachable zones

**Premise, corrected.** P68b found unfilled W/D/H4 gaps are reached 90-95% of the time — and that an identical band the same distance away on the OPPOSITE side of price is reached 90-95% too. So a zone here is a REACHABLE LEVEL, never a magnet, and every rate below carries a control. The question is not whether gaps pull price; it is **where our trades sit relative to levels price demonstrably gets to.**

## 1. Geometry — where our TARGET sits vs the nearest zone ahead

```
split target vs zone   trades  wins    WR%      PF
--------------------------------------------------
IS    short of zone       221   109  49.3%    4.36
IS    at zone              28     8  28.6%    2.44
IS    beyond zone          30     6  20.0%    0.69
OOS   short of zone       234   120  51.3%    6.54
OOS   at zone              31    12  38.7%    4.46
OOS   beyond zone          72    20  27.8%    1.01
```

*Median distance to the nearest zone ahead at entry — winners 83 pips, losers 65 pips.*

## 2 & 3. EARLY or WRONG — the first-passage race after our exit

From the bar after each trade closed, which came first within **120 hours**: the zone we were aiming at, or a MIRROR level the same distance on the other side of our exit?

**This is the whole test.** "Price eventually got there" is worthless — price eventually gets everywhere. Against an equidistant mirror, **~50% means we were simply WRONG about direction**; well above 50% means we were **RIGHT and EARLY**, and the problem is timing. Bars that touched both levels are reported, never assigned.

```
split outcome   ours  mirror   both  neither   ours%  verdict
------------------------------------------------------------------------------
IS    lost        57      50      1       48   53.3%  COIN FLIP — no directional information
IS    won         51      34      2       36   60.0%  EARLY — right direction, wrong timing
OOS   lost        71      74      0       40   49.0%  COIN FLIP — no directional information
OOS   won         61      55      4       32   52.6%  COIN FLIP — no directional information
```

The **lost** rows are the ones that matter. If they read EARLY, the thesis was right and the stop was in the wrong place or the entry too soon — a timing problem, and the first thing in this project that would point at a fix rather than a null. If they read COIN FLIP, the losses were simply wrong-way trades and no amount of stop or entry tuning recovers them.

---

Measurement only; nothing ships. Zones scanned on W, D, 240T; a zone counts only if it was confirmed before entry and still unfilled at entry.
