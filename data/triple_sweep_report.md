# Triple liquidity raid — EURUSD + GBPUSD vs DXY

Timeframe **15T**, sync window **4** bars, forward horizon **32** bars, MSS confirms within **6** bars.

**Bar coverage** (bars present in ALL THREE symbols): 2022: 21543 / 2023: 16745 / 2024: 21585 / 2025: 21573  
IS **38288** / OOS **43158**. An empty OOS bucket below usually means missing UDXUSD data for those years, not an absence of setups — check this line first.

`rev_rate` = share of events where price travelled FURTHER in the reversal direction than against it. `rev20` = share reaching 20+ pips our way. `single` = the same pair raided its own level while the trio did NOT align — the control that decides whether triple confirmation is worth anything. `trip+MSS` additionally requires structure to shift after the raid.

`n` counts PER-PAIR observations: one aligned trio contributes two rows (the EURUSD read and the GBPUSD read), so n = 2 x trios.

**QUAD-ok / QUAD-no** is the conditioned test — the one that matches the traded model rather than the raid stripped bare. At the bar the trio completes, DXY x EURGBP name a pair AND a direction (the four golden conditions); QUAD-ok is the subset where they name THIS pair in THIS direction, QUAD-no the rest. If the raid is only a trigger and the quadrant is the filter, the gap between those two rows is where it shows.

Direction read: most recent BOS, going flat after **48** bars without one. Quadrant occupancy — flat (no setup) on **9** bars; 1a 20458, 1b 21392, 2a 20373, 2b 19214.

## short (pairs take HIGHS, DXY takes LOWS)

Aligned trios: **5644**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS    5266   51.0%    58.1%     25.2     23.1   35.3%
triple OOS   6022   49.8%    44.3%     17.2     17.5   33.4%
single IS    4370   49.8%    56.3%     23.6     23.4   38.9%
single OOS   5024   48.3%    43.3%     16.6     17.3   38.6%
trip+MSS IS   1858   45.9%    56.5%     23.1     27.1  100.0%
trip+MSS OOS   2012   47.6%    44.8%     17.5     19.7  100.0%
QUAD-ok IS    121   48.8%    58.7%     27.2     28.5   56.2%
QUAD-ok OOS    108   50.0%    51.9%     20.6     19.6   55.6%
QUAD-no IS   5145   51.1%    58.1%     25.2     23.0   34.8%
QUAD-no OOS   5914   49.8%    44.2%     17.2     17.5   33.0%
```

**Verdict (raid vs single-pair control): YELLOW** — positive but weak (+1.2pp IS / +1.5pp OOS)
**Verdict (quadrant-aligned vs not): RED** — no consistent lift (-2.3pp IS / +0.2pp OOS)

## long  (pairs take LOWS,  DXY takes HIGHS)

Aligned trios: **5694**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS    5398   51.2%    57.7%     24.6     23.7   34.0%
triple OOS   5990   51.7%    46.9%     18.2     17.2   34.1%
single IS    4410   50.3%    56.4%     23.8     23.1   38.7%
single OOS   4936   52.3%    45.6%     18.0     16.6   38.6%
trip+MSS IS   1836   48.7%    57.4%     24.6     27.0  100.0%
trip+MSS OOS   2043   51.9%    49.2%     19.6     18.0  100.0%
QUAD-ok IS     50   58.0%    60.0%     24.6     23.4   68.0%
QUAD-ok OOS     44   54.5%    59.1%     22.2     19.5   50.0%
QUAD-no IS   5348   51.1%    57.6%     24.6     23.7   33.7%
QUAD-no OOS   5946   51.7%    46.8%     18.2     17.2   34.0%
```

**Verdict (raid vs single-pair control): RED** — no consistent lift (+0.9pp IS / -0.6pp OOS)
**Verdict (quadrant-aligned vs not): YELLOW** — positive but weak (+6.9pp IS / +2.8pp OOS)

---

Measurement only. A GREEN earns an IS/OOS validation of a real lever; YELLOW/RED stands as the record of why nothing shipped.
