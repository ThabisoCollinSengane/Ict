# Which gap fills FIRST — structure vs distance (gap race)

At every bar where an unfilled daily gap sits ABOVE *and* BELOW price, two rules each predict which one fills first: **structure** (the Ep-12 intermediate trend) and **distance** (the nearer gap — the naive rule, and the one P76 used to break the tie). The outcome is which gap actually fills first within the horizon.

**Read the DISAGREE table.** Where the two rules agree, structure scores well for free simply because price that has moved up is both trending up and nearer the upper gap. Only the disagree cases separate real structural information from that confound.

Horizon 60 days · structure window 120 bars · min gap 3.0 pips

## 1. Coverage

```
set         straddle bars  unique pairs  resolved
----------------------------------------------------
all days             3157           785      3068
unique                785           785       774
```

Consecutive days usually straddle the SAME two gaps, so the per-day count is full of near-duplicates. **`unique` — the first day each distinct gap pair straddles price — is what the verdict is read off.**


## 2. All straddle cases (unique gap pairs)

```
split  rule            n  correct     rate      SE   vs 50%
----------------------------------------------------------
IS     struct_h1     240      156    65.0%    3.1   +4.87
IS     struct_d      206       97    47.1%    3.5   -0.84
IS     dollar_h1     247      149    60.3%    3.1   +3.32
IS     dist          364      252    69.2%    2.4   +7.95
OOS    struct_h1     267      150    56.2%    3.0   +2.04
OOS    struct_d      256      118    46.1%    3.1   -1.25
OOS    dollar_h1     256      136    53.1%    3.1   +1.00
OOS    dist          410      272    66.3%    2.3   +7.00
both   struct_h1     507      306    60.4%    2.2   +4.77
both   struct_d      462      215    46.5%    2.3   -1.49
both   dollar_h1     503      285    56.7%    2.2   +3.01
both   dist          774      524    67.7%    1.7  +10.53
```

## 3. ⭐ THE DECIDER — `struct_h1` and distance DISAGREE

Structure is pointing at the FARTHER gap. **Do not read this against 50%** -- the nearer level wins on geometry alone (~62% even on a random walk), so a useless structure reads ~38% here. Section 5 makes the comparison that is actually calibrated.

```
split  rule            n  correct     rate      SE   vs 50%
----------------------------------------------------------
IS     struct_h1      67       28    41.8%    6.0   -1.36
IS     struct_d       41       21    51.2%    7.8   +0.16
IS     dollar_h1      45       25    55.6%    7.4   +0.75
IS     dist           67       39    58.2%    6.0   +1.36
OOS    struct_h1      93       37    39.8%    5.1   -2.01
OOS    struct_d       52       19    36.5%    6.7   -2.02
OOS    dollar_h1      58       23    39.7%    6.4   -1.61
OOS    dist           93       56    60.2%    5.1   +2.01
both   struct_h1     160       65    40.6%    3.9   -2.41
both   struct_d       93       40    43.0%    5.1   -1.36
both   dollar_h1     103       48    46.6%    4.9   -0.69
both   dist          160       95    59.4%    3.9   +2.41
```

## 4. Control — the two rules AGREE

Both rules name the same gap, so this cannot separate them. Shown to confirm the setup detects a real effect at all: if this is also ~50%, neither rule works and section 3 is moot.

```
split  rule            n  correct     rate      SE   vs 50%
----------------------------------------------------------
IS     struct_h1     173      128    74.0%    3.3   +7.19
IS     struct_d       94       41    43.6%    5.1   -1.25
IS     dollar_h1     121       81    66.9%    4.3   +3.96
IS     dist          173      128    74.0%    3.3   +7.19
OOS    struct_h1     174      113    64.9%    3.6   +4.13
OOS    struct_d      118       58    49.2%    4.6   -0.18
OOS    dollar_h1     119       72    60.5%    4.5   +2.34
OOS    dist          174      113    64.9%    3.6   +4.13
both   struct_h1     347      241    69.5%    2.5   +7.87
both   struct_d      212       99    46.7%    3.4   -0.96
both   dollar_h1     240      153    63.8%    3.1   +4.43
both   dist          347      241    69.5%    2.5   +7.87
```

## 5. Raw agree-vs-disagree drop — NOT the verdict

⚠️ **A random walk produces this same drop (10.2pp).** Structure only disagrees with distance when the two gaps are near EQUIDISTANT — the share of disagree cases climbs 19% → 38% → 64% → 67% as the gaps even up — and that is precisely where 'take the nearer one' is weakest. So the disagree bucket is pre-loaded with geometrically ambiguous setups and distance scores worse there **with no structural information involved at all.** Section 6 removes that confound; read it, not this.

```
split   dist on agree   on disagree     drop      SE   in SE
------------------------------------------------------------
IS              74.0%         58.2%   +15.8    6.6  +2.38
OOS             64.9%         60.2%    +4.7    6.2  +0.76
both            69.5%         59.4%   +10.1    4.5  +2.23
```

## 6. ⭐ THE VERDICT — matched on GEOMETRY

Within each band the two gaps are equally (un)balanced, so distance faces the same problem on both sides of the comparison. If structure carries information the drop SURVIVES here. If it collapses, the whole effect was 'structure disagrees when the call is close', which is a restatement of the geometry and is what the random walk shows.

```
near/far band     n ag  n dis    agree  disagree     drop   in SE      IS     OOS
--------------------------------------------------------------------------------
0.00-0.25            94     44    69.1%     68.2%    +1.0  +0.11   +10.9    -6.4
0.25-0.50            50     31    70.0%     61.3%    +8.7  +0.81    -3.0   +21.3
0.50-0.75            41     23    65.9%     39.1%   +26.7  +2.07   +33.9   +17.1
0.75-1.01            26     26    65.4%     61.5%    +3.8  +0.29   +19.2    -5.1
```

**The last two columns are the hardest test in this project (criterion #2).** A drop that is real holds in BOTH halves at a similar size. One that lives in the first half and fades in the second is the signature that has killed nearly everything here — P48's HTF OB (+10.0pp -> +0.9pp), P68's `target_pd` (2.2x -> 1.18x), P69's D1 respect (+9.7 -> +3.5).


### Verdict

Matched drop **+10.1pp** across 4 bands, positive in 4. Per half: IS **+15.2pp**, OOS **+6.7pp**.

⚠️ Compare against the RANDOM-WALK null, which on comparable n gives a matched average of **+6.4pp** — the bar is not zero.

🟡 **SUGGESTIVE, NOT CONFIRMED** — the pooled drop clears the bar, but the halves are +15.2 / +6.7. An effect that lives in one half is the failure signature of P48 / P68 / P69. Criterion #2 is not met.

**Ship gate (corrected):** the geometry-matched drop must average >=8pp, be positive in EVERY band, and reach 2 SE in at least one. The old gate compared the raw drop against zero — but the random-walk null clears that bar (10.2pp), so it could only ever have passed.

