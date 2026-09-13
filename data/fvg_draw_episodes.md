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

How many entries the algo made AIMING at each daily gap before it filled. This is the question P75 never asked. An episode belongs to the half its gap FORMED in, and only entries from that same half are counted against it — see the cross-boundary note below.

```
split   episodes  with>=1  toward   away  inside  med/ep  max/ep
----------------------------------------------------------------
IS           409       84     126    157      72     1.0       6
OOS          389       79     109    114      82     1.0       6
```

**Cross-boundary entries excluded from §2:** 76 of 736. These fall in one half but belong to an episode whose gap formed in the other; §3 and §4 date every trade by its own open time, so they are counted there.


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

**Straddled:** 605 of 736 entries (82%) had unfilled daily gaps on BOTH sides, so 'toward' is ambiguous for them. Counted in the nearest-gap classification above but flagged here rather than folded silently into one side. §4 is the cut that removes them.


## 4. THE UNAMBIGUOUS SUBSET — toward vs away with no competing draw

§3 classifies every entry against its NEAREST live gap, but most entries straddle two. Here the same comparison runs only where the label is not a coin flip: `one_sided` = a live gap on ONE side only; `dominant` = gaps both sides but the near one is within 0.5x the far one's distance (at least 2x closer). `ambiguous` is the remainder, shown as the internal control — if aiming at the gap is real, the clean cuts should be SHARPER and this one flatter. Entries INSIDE a gap are excluded: no direction aims at a gap you are in.

```
subset       split bucket   trades  wins    WR%      P&L ZAR      PF  WRlift
----------------------------------------------------------------------------
one_sided    IS    toward       28    13  46.4%       796.18    3.98        
one_sided    IS    away         67    25  37.3%      3923.42    2.55    +9.1
one_sided    OOS   toward       10     6  60.0%      6144.74   32.96        
one_sided    OOS   away         11     5  45.5%      3274.16    3.90   +14.5
dominant     IS    toward       61    26  42.6%      8883.07    3.09        
dominant     IS    away         48    22  45.8%      7689.59    2.95    -3.2
dominant     OOS   toward       85    41  48.2%     20736.68    4.63        
dominant     OOS   away         68    28  41.2%     14825.59    4.17    +7.1
one+dominant IS    toward       89    39  43.8%      9679.24    3.14        
one+dominant IS    away        115    47  40.9%     11613.01    2.80    +3.0
one+dominant OOS   toward       95    47  49.5%     26881.41    5.55        
one+dominant OOS   away         79    33  41.8%     18099.75    4.12    +7.7
ambiguous    IS    toward       37    18  48.6%      4819.65    2.65        
ambiguous    IS    away         42    16  38.1%      7874.27    4.41   +10.6
ambiguous    OOS   toward       52    23  44.2%     11141.50    3.60        
ambiguous    OOS   away         50    23  46.0%     13626.05    4.62    -1.8
```

```
population      trades   share
------------------------------
one_sided          116   15.8%
dominant           262   35.6%
ambiguous          181   24.6%
inside             177   24.0%
no_gap               0    0.0%
```

**Read the WRlift column, in both splits.** A toward/away edge that is real survives the cut to `one+dominant` at the same sign and roughly the same magnitude in IS and OOS, and is weaker in the `ambiguous` control. An edge that lives only in the ambiguous bucket, or flips sign between halves, was the straddle.

