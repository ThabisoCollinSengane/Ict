# What does price DO when it reaches an HTF gap?

P68b showed arrival is not informative — a gap is reached as often as an identical band on the other side of price. This asks the next question instead: once price is THERE, does the gap hold?

`respect` = a body closed back out the side price came from. `break` = a body closed through the far side. Confirmed within **3** bars of the touch; the excursion is then measured **from the confirmation bar forward** over **12** bars, so the confirmation cannot contain its own outcome.

**`control` is the row that decides it** — the same classification on a mirror band (same width, same distance, opposite side of price). Price reverses at arbitrary levels too; only the LIFT is evidence.

`medFav`/`medAdv` are median pips in favour of / against the direction the reaction implies. **Symmetric medians are a coin flip**, whatever the rate says.

## W

```
bucket            n  respect%   break%  unres%  resFav  resAdv  brkFav  brkAdv
----------------------------------------------------------------------------
gap IS           46     69.6%    23.9%    6.5%   268.0   277.5   291.3   143.9
gap OOS          52     69.2%    26.9%    3.8%   304.1   169.3   231.7   167.0
control IS       47     63.8%    27.7%    8.5%   338.7   178.2   304.1   276.7
control OOS      53     73.6%    20.8%    5.7%   170.4   265.7   157.1   254.3
```

*Breakaway -> IFVG — does a BROKEN gap hold when price comes back to it (within 30 bars)? Escaping a band you already broke is partly geometry and reads 64-72% on a random walk, so read the lift, not the rate:*

  - IS: gap 9 retests 78% held, control 12 75% -> **lift +2.8pp**
  - OOS: gap 10 retests 70% held, control 11 64% -> **lift +6.4pp**

**Verdict: RED** — respect 70%/69% vs control 64%/74% (lift +5.7pp IS / -4.4pp OOS) — arriving at a gap is no more likely to reverse than arriving at any band the same distance away

## D

```
bucket            n  respect%   break%  unres%  resFav  resAdv  brkFav  brkAdv
----------------------------------------------------------------------------
gap IS          379     70.2%    24.0%    5.8%   132.9   101.7   170.7    92.6
gap OOS         347     66.9%    23.6%    9.5%    86.3    98.4   109.5   113.0
control IS      382     60.5%    27.2%   12.3%    99.1   116.3   104.0   127.0
control OOS     344     63.4%    25.9%   10.8%    86.4    94.7    81.3    79.5
```

*Breakaway -> IFVG — does a BROKEN gap hold when price comes back to it (within 30 bars)? Escaping a band you already broke is partly geometry and reads 64-72% on a random walk, so read the lift, not the rate:*

  - IS: gap 66 retests 70% held, control 90 67% -> **lift +3.0pp**
  - OOS: gap 75 retests 64% held, control 78 68% -> **lift -3.9pp**

**Verdict: RED** — respect 70%/67% vs control 60%/63% (lift +9.7pp IS / +3.5pp OOS) — arriving at a gap is no more likely to reverse than arriving at any band the same distance away

## 240T

```
bucket            n  respect%   break%  unres%  resFav  resAdv  brkFav  brkAdv
----------------------------------------------------------------------------
gap IS         2062     64.2%    26.2%    9.6%    47.2    52.0    54.3    46.4
gap OOS        1968     66.4%    25.1%    8.5%    38.8    36.5    38.7    36.0
control IS     2058     63.7%    26.4%   10.0%    50.6    47.2    42.2    55.8
control OOS    1968     64.3%    26.3%    9.3%    38.1    38.8    38.5    37.5
```

*Breakaway -> IFVG — does a BROKEN gap hold when price comes back to it (within 30 bars)? Escaping a band you already broke is partly geometry and reads 64-72% on a random walk, so read the lift, not the rate:*

  - IS: gap 445 retests 63% held, control 471 61% -> **lift +2.6pp**
  - OOS: gap 400 retests 67% held, control 409 66% -> **lift +1.5pp**

**Verdict: RED** — respect 64%/66% vs control 64%/64% (lift +0.6pp IS / +2.1pp OOS) — arriving at a gap is no more likely to reverse than arriving at any band the same distance away

---

A respect rate at or below the control means the gap is not the actor — price was going to turn there as often as anywhere. In that case the bias-flip state machine has nothing to stand on and the reaction, not the study, is what needs rethinking. Measurement only; nothing ships.
