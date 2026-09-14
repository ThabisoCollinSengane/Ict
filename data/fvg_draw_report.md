# Does the FVG call price to it?

Every 3-bar gap on W, D, 240T, all pairs, followed forward up to **30 days**. `reach` = ever traded into. `fast` = reached within 2 days (a tradeable draw rather than a distant magnet). `MSS` = structure broke toward the gap; `IM` = the prior daily dollar close favours the move; `both` = the trader's full condition. Structure must shift within **6** bars of the gap forming — if an MSS bucket reads 0 on a timeframe, that window is too tight for it, not an absence of shifts.

**`control` is the row that decides the question.** It is a band of the SAME width at the SAME distance on the OPPOSITE side of price. Price trades into a nearby band whether or not a gap is there, so only the gap's LIFT over its control is evidence that the gap itself calls price. A high reach rate with a flat lift means the level was near, not special.

MSS rows measure the reach FROM the shift bar forward, off a swing that sits clear of the gap, and skip gaps already filled before the shift — so the confirmation cannot contain its own outcome.

## W

```
bucket              n   reach%   fast%  med days
------------------------------------------------
all IS             66    69.7%    n/a       5.0
all OOS            66    78.8%    n/a       5.0
control IS         66    71.2%    n/a      10.0
control OOS        66    80.3%    n/a       5.0
MSS IS              5    60.0%    n/a      10.0
MSS OOS             1     0.0%    n/a         —
MSS ctrl IS         5    60.0%    n/a       5.0
MSS ctrl OOS        1   100.0%    n/a       5.0
IM IS              32    62.5%    n/a       5.0
IM OOS             30    86.7%    n/a       5.0
both IS             4    75.0%    n/a      10.0
both OOS            0   —
```

**Verdict: RED** — reached 70%/79% vs control 71%/80% (lift -1.5pp IS / -1.5pp OOS) — no edge over an identical band on the other side; the reach rate is what any nearby level scores

## D

```
bucket              n   reach%   fast%  med days
------------------------------------------------
all IS            420    90.2%   60.5%       1.0
all OOS           398    87.2%   56.5%       1.0
control IS        420    91.0%   57.6%       1.0
control OOS       398    86.4%   53.3%       1.0
MSS IS             15    60.0%   40.0%       1.0
MSS OOS            20    85.0%   40.0%       3.0
MSS ctrl IS        15    86.7%   20.0%       3.0
MSS ctrl OOS       20    70.0%   30.0%       5.0
IM IS             374    90.6%   61.2%       1.0
IM OOS            371    87.9%   57.7%       1.0
both IS            15    60.0%   40.0%       1.0
both OOS           19    84.2%   36.8%       4.0
```

**Verdict: RED** — reached 90%/87% vs control 91%/86% (lift -0.7pp IS / +0.8pp OOS) — no edge over an identical band on the other side; the reach rate is what any nearby level scores

## 240T

```
bucket              n   reach%   fast%  med days
------------------------------------------------
all IS           2166    95.2%   82.2%       0.3
all OOS          2066    95.3%   80.5%       0.3
control IS       2166    95.0%   80.7%       0.3
control OOS      2066    95.3%   81.3%       0.3
MSS IS             94    85.1%   61.7%       0.7
MSS OOS           100    86.0%   56.0%       0.8
MSS ctrl IS        94    92.6%   68.1%       1.0
MSS ctrl OOS      100    96.0%   63.0%       1.0
IM IS             999    96.8%   84.5%       0.3
IM OOS            926    95.4%   79.8%       0.3
both IS            42    88.1%   64.3%       0.5
both OOS           54    88.9%   59.3%       0.8
```

**Verdict: RED** — reached 95%/95% vs control 95%/95% (lift +0.2pp IS / +0.0pp OOS) — no edge over an identical band on the other side; the reach rate is what any nearby level scores

---

A high reach rate with a long median is a real magnet and a poor intraday target — which would argue for the gap as a BIAS held across days, not as a take-profit. But read the LIFT over the control first: without it, a high reach rate only says the band was close. Measurement only; nothing ships.
