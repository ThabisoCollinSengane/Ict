# Daily FVG as a standing DRAW — entries per episode (P76)

The unit is the gap EPISODE (formation -> fill), not the trade. `toward` = the entry direction aims at the gap positionally; `away` = the opposite. Completed daily candles only; fill = full body close through the far side (ICT Ep 9).

## 1. Episode census

```
split    gaps  filled   fill%  medDays  p90Days
------------------------------------------------
IS        409     391   95.6%      9.0    151.0
OOS       389     352   90.5%      5.5     63.8
```

## 2. THE HEADLINE — entries aimed at the gap per episode

How many entries the algo made AIMING at each daily gap before it filled. This is the question P75 never asked.

```
split   episodes  with>=1  toward   away  inside  med/ep  max/ep
----------------------------------------------------------------
IS           409       93     164    172      95     1.0       7
OOS          389       79     109    114      82     1.0       6
```

## 3. toward vs away — the internal control

Both buckets are the algo's own entries, same pair, same episode, same gates. No mirror band needed.

```
split  bucket     trades  wins    WR%      P&L ZAR      PF
--------------------------------------------------------
IS     toward        126    57  45.2%     14498.90    2.95
IS     away          157    63  40.1%     19487.28    3.22
IS     inside         72    33  45.8%     13434.80    4.53
OOS    toward        147    70  47.6%     38022.91    4.73
OOS    away          129    56  43.4%     31725.80    4.32
OOS    inside        105    44  41.9%     22406.03    4.39
```

**Straddled:** 605 entries had unfilled daily gaps on BOTH sides, so 'toward' is ambiguous for them. Counted in the nearest-gap classification above but flagged here rather than folded silently into one side.

