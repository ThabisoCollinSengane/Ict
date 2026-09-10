# Triple liquidity raid — EURUSD + GBPUSD vs DXY

Timeframe **60T**, sync window **4** bars, forward horizon **24** bars, MSS confirms within **6** bars.

**Bar coverage** (bars present in ALL THREE symbols): 2022: 5389 / 2023: 4189 / 2024: 5400 / 2025: 5396  
IS **9578** / OOS **10796**. An empty OOS bucket below usually means missing UDXUSD data for those years, not an absence of setups — check this line first.

`rev_rate` = share of events where price travelled FURTHER in the reversal direction than against it. `rev20` = share reaching 20+ pips our way. `single` = the same pair raided its own level while the trio did NOT align — the control that decides whether triple confirmation is worth anything. `trip+MSS` additionally requires structure to shift after the raid.

`n` counts PER-PAIR observations: one aligned trio contributes two rows (the EURUSD read and the GBPUSD read), so n = 2 x trios.

**QUAD-ok / QUAD-no** is the conditioned test — the one that matches the traded model rather than the raid stripped bare. At the bar the trio completes, DXY x EURGBP name a pair AND a direction (the four golden conditions); QUAD-ok is the subset where they name THIS pair in THIS direction, QUAD-no the rest. If the raid is only a trigger and the quadrant is the filter, the gap between those two rows is where it shows.

Direction read: most recent BOS, going flat after **48** bars without one. Quadrant occupancy — flat (no setup) on **9** bars; 1a 4892, 1b 5675, 2a 5188, 2b 4610.

## short (pairs take HIGHS, DXY takes LOWS)

Aligned trios: **1531**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS    1424   52.7%    77.4%     49.0     41.5   40.0%
triple OOS   1638   50.5%    67.6%     32.8     32.2   37.6%
single IS    1045   50.6%    76.2%     46.7     43.9   44.2%
single OOS   1263   49.1%    67.4%     31.9     33.2   42.0%
trip+MSS IS    569   47.1%    74.9%     42.0     47.5  100.0%
trip+MSS OOS    616   50.3%    67.2%     34.4     33.8  100.0%
QUAD-ok IS     44   52.3%    75.0%     61.8     40.2   47.7%
QUAD-ok OOS     40   45.0%    65.0%     32.5     43.0   57.5%
QUAD-no IS   1380   52.8%    77.5%     48.9     41.6   39.7%
QUAD-no OOS   1598   50.7%    67.7%     32.9     32.1   37.1%
```

**Verdict (raid vs single-pair control): YELLOW** — positive but weak (+2.1pp IS / +1.5pp OOS)
**Verdict (quadrant-aligned vs not): RED** — no consistent lift (-0.5pp IS / -5.7pp OOS)

## long  (pairs take LOWS,  DXY takes HIGHS)

Aligned trios: **1497**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS    1424   49.3%    75.6%     43.8     44.6   38.0%
triple OOS   1570   51.6%    71.1%     35.6     31.6   39.0%
single IS    1065   47.5%    72.7%     41.5     48.8   42.3%
single OOS   1201   52.3%    68.5%     33.6     30.7   43.2%
trip+MSS IS    541   50.1%    75.6%     47.6     46.8  100.0%
trip+MSS OOS    613   50.6%    69.8%     34.4     32.5  100.0%
QUAD-ok IS     12   58.3%    75.0%     50.3     48.1   50.0%
QUAD-ok OOS     14   50.0%    85.7%     32.3     23.5   85.7%
QUAD-no IS   1412   49.2%    75.6%     43.8     44.6   37.9%
QUAD-no OOS   1556   51.6%    71.0%     36.0     31.7   38.6%
```

**Verdict (raid vs single-pair control): RED** — no consistent lift (+1.8pp IS / -0.7pp OOS)
**Verdict (quadrant-aligned vs not): YELLOW** — small sample (IS n=12, OOS n=14)

---

Measurement only. A GREEN earns an IS/OOS validation of a real lever; YELLOW/RED stands as the record of why nothing shipped.
