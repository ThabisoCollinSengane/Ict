# Triple liquidity raid — EURUSD + GBPUSD vs DXY

Timeframe **60T**, sync window **4** bars, forward horizon **24** bars.

`rev_rate` = share of events where price travelled FURTHER in the reversal direction than against it. `rev20` = share reaching 20+ pips our way. `single` = the same pair raided its own level while the trio did NOT align — the control that decides whether triple confirmation is worth anything. `trip+MSS` additionally requires structure to shift after the raid.

`n` counts PER-PAIR observations: one aligned trio contributes two rows (the EURUSD read and the GBPUSD read), so n = 2 x trios.

## short (pairs take HIGHS, DXY takes LOWS)

Aligned trios: **6**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS      12   41.7%    41.7%     17.5     72.0   41.7%
triple OOS      0   —
single IS      14   57.1%    57.1%     49.1     37.3   78.6%
single OOS     21   61.9%    76.2%     50.0     25.5   47.6%
trip+MSS IS      5  100.0%   100.0%     79.5      9.1  100.0%
trip+MSS OOS      0   —
```

**Verdict: RED** — no events in one or both splits

## long  (pairs take LOWS,  DXY takes HIGHS)

Aligned trios: **30**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS      60   51.7%    75.0%     47.2     37.4   50.0%
triple OOS      0   —
single IS     101   43.6%    73.3%     44.2     56.5   49.5%
single OOS      0   —
trip+MSS IS     30   83.3%   100.0%    101.8     19.5  100.0%
trip+MSS OOS      0   —
```

**Verdict: RED** — no events in one or both splits

---

Measurement only. A GREEN earns an IS/OOS validation of a real lever; YELLOW/RED stands as the record of why nothing shipped.
