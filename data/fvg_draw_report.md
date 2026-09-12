# Does the FVG call price to it?

Every 3-bar gap on W, D, 240T, all pairs, followed forward up to **30 days**. `reach` = ever traded into. `fast` = reached within 2 days (a tradeable draw rather than a distant magnet). `MSS` = structure broke toward the gap; `IM` = the prior daily dollar close favours the move; `both` = the trader's full condition. Structure must shift within **6** bars of the gap forming — if an MSS bucket reads 0 on a timeframe, that window is too tight for it, not an absence of shifts.

## W

```
bucket            n   reach%   fast%  med days
----------------------------------------------
all IS           66    69.7%    0.0%       5.0
all OOS          66    78.8%    0.0%       5.0
MSS IS           14   100.0%    0.0%       5.0
MSS OOS          16   100.0%    0.0%       5.0
IM IS            32    62.5%    0.0%       5.0
IM OOS           30    86.7%    0.0%       5.0
both IS           4   100.0%    0.0%       5.0
both OOS          6   100.0%    0.0%       5.0
```

**Verdict: YELLOW** — reached 70% IS / 79% OOS — better than a coin flip, not a law

## D

```
bucket            n   reach%   fast%  med days
----------------------------------------------
all IS          420    90.2%   60.5%       1.0
all OOS         398    87.2%   56.5%       1.0
MSS IS           99   100.0%   87.9%       1.0
MSS OOS          91   100.0%   89.0%       1.0
IM IS           374    90.6%   61.2%       1.0
IM OOS          371    87.9%   57.7%       1.0
both IS          87   100.0%   88.5%       1.0
both OOS         86   100.0%   89.5%       1.0
```

**Verdict: GREEN** — reached 90% IS / 87% OOS — the gap does call price

## 240T

```
bucket            n   reach%   fast%  med days
----------------------------------------------
all IS         2166    95.2%   82.2%       0.3
all OOS        2066    95.3%   80.5%       0.3
MSS IS          511    99.8%   99.4%       0.2
MSS OOS         461   100.0%  100.0%       0.2
IM IS           999    96.8%   84.5%       0.3
IM OOS          926    95.4%   79.8%       0.3
both IS         256    99.6%   99.2%       0.2
both OOS        184   100.0%  100.0%       0.2
```

**Verdict: GREEN** — reached 95% IS / 95% OOS — the gap does call price

---

A high reach rate with a long median is a real magnet and a poor intraday target — which would argue for the gap as a BIAS held across days, not as a take-profit. Measurement only; nothing ships.
