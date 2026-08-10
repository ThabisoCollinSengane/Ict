# Talking to the algorithm — the Telegram manual

Everything you can tell the live bot from your phone, and exactly how to say it.
You steer it; it still runs its full validated ICT logic underneath. Your inputs
**filter, aim, and hold** it — they never replace the strategy.

Everything is **opt-in, per pair, per day.** Say nothing → that pair trades fully
automatic, exactly as backtested. All inputs auto-expire at **00:00 UTC**, so
nothing you set today leaks into tomorrow.

---

## Session templates — you get one at the start of every session

At the top of **each** session the bot messages you a template. You reply with
that session's plan (or ignore it and it runs on full auto):

- **LONDON SESSION START** — ~02:00 ET
- **NEW YORK AM SESSION START** — ~07:00 ET (also lists what's already open, so
  you can decide to `/hold` it into NY)
- **NEW YORK PM SESSION START** — ~13:00 ET (only if PM trading is enabled)

You don't have to wait for the template — any command works any time.

---

## The commands

### 0 · Ask the bot (read anytime — no effect on trading)
```
/brief           FULL session brief: account + structure + open trades + commands
/read            market-structure template for all pairs
/read EURUSD     just that pair
/markets         all pairs at a glance
/positions       open trades broken out PER LEG (e.g. 2 x 0.02 = 0.04), each with
                 its entry, live pips, SL and ticket — so you can /close one leg.
                 Plus total P&L, % to target, Model, TP idea + SL basis (saved,
                 survives restarts).
/account         equity, day P&L, drawdown, halt state (also /equity)
/dxy             synthetic dollar index right now
/session         full day timeline in SAST | ET — every window (London KZ,
                 silver bullets, NY AM, lunch, NY PM, NY close 16:00-17:00), which
                 is active NOW + when the next starts, what the earlier sessions
                 did today (range + delivery), and the PD arrays near price
/news            next high-impact news events (UTC)
/whoami          your chat id + access level
```
`/brief` is the same rich summary the bot sends you at the start of every
session — call it any time to get the current picture in one message.
The `/read` template shows, per pair: current price, H4/H1/M15 structure
(bullish / bearish / flat), the intact **ITH** (buy-side draw) and **ITL**
(sell-side draw), and your current plan for that pair. Example:
```
MARKET READ - 08:20 UTC
Session: NY AM

BIAS (gate drivers):
DXY: UP (USD strong)  [99.97]
EURGBP: EUR > GBP (EUR family)

EURUSD  1.15206   SHORT lean 75%
  H4 bullish | H1 bearish | M15 bullish
  buy-side draw (ITH): 1.15800
  sell-side draw (ITL): 1.14900
  bot would: SHORT (1b)
  your plan: EURUSD long only, levels set
```
Every read leads with the **two gate drivers** — **DXY** (dollar direction) and
**EURGBP** (which family, EUR vs GBP). Then each pair gets:
- a **directional lean %** — the market's structural pressure (H4/H1/M15 + dollar);
- **bot would** — the bot's *intended trade direction + scenario* from the
  intermarket gate right now (e.g. `SHORT (1b)`), or `no gate signal` / `no trade
  (DXY flat)`. A setup + killzone must still fire for it to actually enter — this
  is what it's *leaning to trade*, not a guarantee it will.

### 1 · Lot for the day
```
/lot 0.02              → all pairs
/lot GBPUSD 0.03       → one pair
```
Becomes the **base** lot. The draw 2×/3× and the 1.25× confluence/CRT/PDL bumps
still stack on top (they only fire at R3k+ equity anyway).

### 2 · Direction to hunt
```
/bias EURUSD long      → longs only on EURUSD today
/bias EURUSD short     → shorts only
/bias EURUSD both      → clear the filter (back to auto)
```
A **filter**: the bot still needs its own ICT setup to fire — it just won't take
the other side.

### 3 · Your liquidity levels (full manual AMD)
```
/levels EURUSD buy 1.0950 1.0975 sell 1.0900 1.0880
```
- **buy** = buy-side liquidity **above** price · **sell** = sell-side **below**.
- The bot waits for **manipulation** — price sweeps one side and reclaims — then
  trades the **distribution** toward the other side:
  - sell-side swept & reclaimed → hunt **LONG**, target the **buy-side**
  - buy-side swept & dropped back → hunt **SHORT**, target the **sell-side**
  - neither side swept yet → **waits** (no trade)
- So your levels set **which way** (direction gate) and **where to** (the opposite
  side becomes the TP). Your engine still decides **whether the setup is there.**
- If both `/bias` and `/levels` are set, **both must agree.**

### 3b · Market Maker model — IFVG watcher + auto-enter (D1/H4/H1)
```
/mm EURUSD buy       → arm the Market Maker BUY model (WATCH — alerts only)
/mm EURUSD sell      → sell model (watch)
/mm EURUSD buy auto  → arm AND pre-permit ONE auto-entry on the retracement
/mm EURUSD off       → disarm
```
Arm a model and the bot scans **D1, H4 and H1 for inversion FVGs** in that
direction (buy = demand/support zones, sell = supply/resistance) — the HTF Judas
areas that repel price toward the same liquidity draws you already target. Then:

- **In `/read` / `/brief`** each armed pair shows its IFVG zones with **how far
  price is** (pips + % of the way from where you armed it) and **which beat of the
  setup each zone is on** — so you can see at a glance what to do:
  ```
  MM BUY model - IFVG watch (D1/H4/H1)  [AUTO-ARMED]:
    D1 IFVG 1.14900-1.15050   62p  [1] approaching 73%
    H4 IFVG 1.15400-1.15470    8p  [2] TAGGED - waiting on swing
    H1 IFVG 1.15560-1.15600    0p  [3] CONFIRMED - entry trigger
  ```
  The beat tags are your playbook:
  - **`[1] approaching NN%`** — price still travelling to the zone; just watch the % climb.
  - **`[2] TAGGED - waiting on swing`** — price is *inside* the IFVG; get ready, but
    the touch alone is not the entry.
  - **`[3] CONFIRMED - entry trigger`** — a fresh LTF swing has formed off the zone;
    this is the entry (auto takes it here; by hand, `/test` or `/pyramid` now).
  - **`[x] BROKEN - spent, watch next`** — a full body closed through it; that zone is
    done — drop to the next zone down the list.
  `[AUTO-ARMED]` in the header means auto-entry is pre-permitted and will fire itself
  when a zone hits beat 3.
- **Alerts** fire once per zone: **"price REACHED H4 IFVG …"** when price enters a
  zone, and **"H4 IFVG BROKEN — closed above/below …"** when a bar closes a full
  body through it — your cue to look for the retracement entry on swing formation.

**Watch mode (`/mm PAIR buy`)** is a pure alert layer — it never trades. You take
the retracement entries yourself (`/test`, `/pyramid`, or the bot's own swing entry).

**Auto mode (`/mm PAIR buy auto`)** — the *pre-permission*. You authorise **one**
entry **before** price gets to the zone; the bot then pulls the trigger for you the
moment its two conditions line up:

1. **Retracement** — price is **inside** one of the armed D1/H4/H1 IFVGs, in the
   model direction (the HTF Judas zone repelling price toward the draw).
2. **Reversal** — a **freshly-confirmed, still-intact lower-timeframe swing** in
   the model direction (the same "swing formation" you'd wait for by hand — the
   bot's `_structure_entry_confirmed` check).

When **both** are true it enters with the bot's **own structural stop** (fractal
ITL/ITH, capped ~10 pips) and its **nearest-liquidity target** — the opposite-side
level you set with `/levels` if any, else the nearest **H4 ITH/ITL** draw, else a
2R fallback. Lot = your `/lot` for the pair (or the minimum). It then **disarms
itself** — one shot. You get a full `MM AUTO-ENTRY` message with entry / stop /
target and why.

- If a position is **already open the same way and winning**, auto instead adds a
  **pyramid** leg (then disarms). If one is open the **opposite** way it does
  nothing and stays armed.
- `/halt` blocks auto-entry (and every other new entry). `/mm PAIR off` cancels it.
- Auto expires at **00:00 UTC** with everything else, and it's **one entry only** —
  re-arm with `/mm PAIR buy auto` if you want it to take another.

#### IFVG entries — how the setup plays out (sketches)

**What an inversion FVG *is* (BUY / demand example).** A fair-value gap that price
later *closes a full body back through* flips polarity — a down-gap that gets a
bullish full-body close above it becomes a **demand (support)** zone. That flip is
the "Judas on a higher timeframe": the level that once repelled price down now
holds it up, drawing price on toward your liquidity target.

```
1) a bearish gap (FVG) forms as price falls through it
2) price returns and a FULL BODY closes back ABOVE the gap
        -> the gap INVERTS into a DEMAND zone (support)
3) later price RETRACES down into that demand zone and turns up
        -> that turn is your entry, riding to the draw above
```

**BUY model — the entry sequence (demand IFVG sits BELOW price):**
```
  1.15800  = = = TARGET  (buy-side draw: ITH / PDH / your level)   ▲
                                                                   │ ③ up to target
  1.15600  ● price now                                            │
              │  ① price drops back toward the zone   (beat [1])
              ▼
  1.15470  ┌────────────────┐  zone top
           │  DEMAND  IFVG   │  ② TAG the zone (beat [2]) -> swing UP = ENTER [3]
  1.15400  └────────────────┘  zone bottom
  1.15380  ✗ stop  (just below the zone — the bot's structural stop)
```

**SELL model — the mirror (supply IFVG sits ABOVE price):**
```
  1.16120  ✗ stop  (just above the zone)
  1.16100  ┌────────────────┐  zone top
           │  SUPPLY  IFVG   │  ② TAG (beat [2]) -> swing DOWN = ENTER [3]
  1.16030  └────────────────┘  zone bottom
              ▲
              │  ① price rises back toward the zone   (beat [1])
  1.15900  ● price now
              │  ③ down to target
              ▼
  1.15600  = = = TARGET  (sell-side draw: ITL / PDL / your level)
```

**When a zone FAILS (beat `[x] BROKEN`) — do NOT trade it:**
```
  1.15470  ┌────────────────┐  zone top
           │  DEMAND  IFVG   │
  1.15400  └────────────────┘  zone bottom
              │  a full body CLOSES below the zone
              ▼
  1.15350  ██  close < zone  ->  zone is spent
           the read flips it to [x] BROKEN — drop to the NEXT zone down the list
```

**A worked BUY, arm to fill:**
```
  you send      /mm EURUSD buy auto
  /brief        H4 IFVG 1.15400-1.15470   9p  [1] approaching 88%
    ... price drifts down ...
  alert         price REACHED H4 IFVG 1.15400-1.15470
  /brief        H4 IFVG 1.15400-1.15470   0p  [2] TAGGED - waiting on swing
    ... M15 prints a higher-low off the zone (swing forms) ...
  /brief        H4 IFVG 1.15400-1.15470   0p  [3] CONFIRMED - entry trigger
  bot fires     MM BUY AUTO-ENTRY EURUSD LONG  entry 1.15430  stop 1.15380
                target 1.15800  (H4 ITH draw)  -> auto DISARMS (one shot)
```
By hand (watch mode) the sequence is identical — you just place the trade yourself
at beat `[3]` with `/test EURUSD long` (or `/pyramid` if you're adding to a winner).

**Reading the beats at a glance:** `[1]` = wait, `[2]` = get ready, `[3]` = go,
`[x]` = skip this zone. The `%` next to `[1]` is your countdown to the tag.

### 3c · Trading the US indices (US500 / US100)

When the index gate is enabled (`INDICES_ENABLED=1` in `live.env`, with the broker
symbols **US500, US100, US30, XAGUSD** in MT5), the indices join the pair list and
**every command above works on them exactly like a currency** — steer them and let
the bot manage the trade:
```
/bias US100 long        → hunt US100 longs only today
/lot US500 0.20         → day lot for US500
/mm US100 buy auto      → Market Maker IFVG model on US100
/trail US500 m5 st 3    → structure-trail an open US500 trade
/read US100             → its structure, lean %, and the bot's intended trade
```
The index gate is **DXY + US500/US100 + US30** (indices move *inverse* to the
dollar), so `/read` shows the bot's intended direction as `IDX-long` / `IDX-short`.
Your `/bias` still just filters — the bot needs its own ICT setup (AMD/MSS + FVG)
to actually enter, then manages the stop/target/trail as usual.

### 4 · Let a trade run across sessions
```
/hold EURUSD           → don't close it at the session handover; let it run
/hold all              → every pair
/release EURUSD        → back to normal handover management
```
Normally, at the London→NY (and NY→PM) boundary the bot closes a trade **only if
it's losing AND fighting the weekly bias**. `/hold` exempts that pair from that
close, so a London trade **runs into New York** — and a NY-AM trade **runs into
the afternoon** — managed purely by its **stop, target, and milestone trail**.
(Winning trades already carry across by default; `/hold` also keeps the
losing-but-you-believe-in-it ones alive.)

### 4b · Trail the stop by market structure
```
/trail EURUSD m5 st 3    → trail on M5 short-term swings, 3-pip buffer
/trail EURUSD m15 it 5   → trail on M15 intermediate swings, 5-pip buffer
/trail EURUSD m1 st      → M1 short-term, default 2-pip buffer
/trail EURUSD off        → stop trailing by structure
```
Follows the **latest intact fractal swing** and ratchets your stop behind it,
keeping a **pip buffer you choose**. Three timeframes and two structure tiers:

- **Timeframe** — `m15` · `m5` · `m1` (how fine the swings it follows are).
- **Tier** — `st` = short-term **STH/STL**, `it` = intermediate **ITH/ITL**.
  (Bigger tier = looser, fewer stop-outs; short-term = tighter, locks faster.)
- **Buffer** — the pips beyond the swing the stop sits (optional; default 2).

The bot picks the correct side automatically: for a **long** it trails under the
latest intact **low** (STL/ITL − buffer); for a **short**, above the latest intact
**high** (STH/ITH + buffer). It **only ever tightens** — the stop moves in your
favour as new swings form and never loosens. It stacks with the built-in
break-even / lock / milestone trail (whichever is tighter wins), so you can layer
your structural trail on top of the automatic protection. Per pair, expires at
00:00 UTC like every input.

### 5 · Manual control — close & halt (act now)
```
/test EURUSD long      → open a TEST trade NOW on the demo (also short; /buy /sell)
                          uses the bot's own structural stop + a 2R target
/test EURUSD long 0.05 → same, at a chosen lot size (0.01 .. 0.05 etc.)
/sl EURUSD 1.15550     → move the stop to a price (all legs)
/sl EURUSD 2 1.15560   → move only leg 2's stop
/be EURUSD             → move the stop to breakeven (each leg's entry)
/pyramid EURUSD        → add a leg to a WINNING position, exiting at the SAME TP
/pyramid EURUSD 1.1600 → same, but the whole position exits at 1.1600 instead
                          (only adds if the position is in profit; structural stop)
/close EURUSD          → close the WHOLE EURUSD position (all legs) at market
/close EURUSD 2        → close ONLY leg 2 (one pyramid), the rest keeps running
/close all             → flatten everything
/flat                  → flatten everything (shortcut for /close all)
/halt                  → stop all new entries AND pyramid adds; open trades
                          keep running on their stops
/resume                → re-enable new entries
```
To go fully flat and stay out: `/close all` then `/halt`. To stop taking new
trades but let winners keep running: just `/halt`.

### 6 · Review & reset
```
/status                → echo this session's plan for every pair
/auto EURUSD           → revert one pair to full auto
/clear                 → revert ALL pairs to full auto
/help                  → the command list
```

Every command gets an acknowledgement back, so you always see exactly what the
bot registered.

---

## A full day, worked

**London template arrives.** You reply:
```
/lot 0.02
/bias EURUSD long
/levels EURUSD buy 1.0975 sell 1.0900 1.0880
/hold EURUSD
```
→ Bot acks each line. It trades EURUSD **long-only**, but only **after** price
sweeps 1.0900/1.0880 and reclaims, aiming at **1.0975**, and only if its own
MSS+FVG setup fires. GBPUSD / NZDUSD (untouched) trade fully automatic.

**NY-AM template arrives** — "Open now: EURUSD · holding: EURUSD." Your London
long is running into New York (because you `/hold`-ed it) instead of being closed
at the handover. You could add `/bias GBPUSD short` for the NY session, or
`/release EURUSD` if you've changed your mind.

**NY-PM template** (if enabled) — same idea for the afternoon.

---

## Sharing the bot with your partner

**You do NOT create a second bot.** Your partner opens the **same GameTheory bot**
(share the link — `t.me/GameTheory2026bot`) and texts it like any normal chat.
The only question is what they're allowed to do. Three ways, easiest first:

**Option 1 — Open read-only (zero setup, "just text it"):**
Set one flag and anyone you share the link with can read the bot — no ids, no
restarts per person:
```
TELEGRAM_OPEN_VIEW=1
```
They can `/brief`, `/read`, `/positions`, `/account`, `/dxy`, `/session`, `/news`.
They **cannot** touch trades. This is the "share it like WhatsApp" mode you wanted.
(Push alerts still go only to listed people; open-view users read on demand.)

**Option 2 — Named viewer (read-only, also gets alerts):** add their chat id:
```
TELEGRAM_VIEWER_IDS=5111111111,5222222222
```

**Option 3 — Admin (full control, trades like you):** add their chat id:
```
TELEGRAM_ADMIN_IDS=5333333333
```
Trading control **can't** be open (it moves real money) — an admin must be a
listed id.

**Getting a chat id:** the person sends `/start` to @userinfobot (it replies with
their `Id`), or — once they can already read the bot — `/whoami`. Add the id in
`live.env`, restart the bot, done. Anyone not covered by the above is ignored.
The **Ops Bot** honours owner + admins only — never viewers/open-view — since it
changes settings and runs the VM.

## Safety

- **Only listed Telegram chats can use the bot** — anyone else is ignored; viewers
  are limited to read-only.
- **The backtest is byte-identical.** The two engine hooks (`_direction_allowed`,
  `_handover_exempt`) are pure no-ops in the backtester; only the live engine
  overrides them. Your 810-trade / PF 4.47 / MaxDD −12.95% numbers are untouched.
- **Offline self-test** (no MT5, no network): `python -m live.test_semi_auto`.
- **DEMO first**, same as the go-live checklist in `AZURE_WINDOWS_SETUP.md`.
  Prove the whole flow — including a `/hold` across a real handover — on a demo
  account before it touches the funded one.

---

## Quick reference card

| Command | Meaning |
|---|---|
| `/brief` | full session brief (structure + positions + account) |
| `/read [EURUSD]` · `/markets` | market-structure read (template) |
| `/positions` · `/account` · `/dxy` · `/session` · `/news` | live read-outs |
| `/flat` | flatten everything · `/whoami` your id + access |
| `/lot 0.02` / `/lot GBPUSD 0.03` | day lot (base; multipliers stack) |
| `/bias EURUSD long\|short\|both` | direction filter |
| `/levels EURUSD buy … sell …` | manual-AMD liquidity (sweep→target) |
| `/mm EURUSD buy\|sell [auto]\|off` | Market Maker IFVG model — watch, or `auto` to pre-permit one entry |
| `/hold EURUSD` / `/hold all` | run across the session handover |
| `/trail EURUSD m15\|m5\|m1 st\|it [pips]` | trail stop behind the latest intact swing |
| `/release EURUSD` | normal handover management |
| `/close EURUSD` / `/close all` | close position(s) at market now |
| `/halt` / `/resume` | pause / re-enable all new entries + adds |
| `/status` | echo today's plan |
| `/auto EURUSD` / `/clear` | revert one / all to auto |
| `/help` | command list |
