"""Generate the ICT Intermarket Algorithm operator's manual as a PDF.

    python scripts/build_manual_pdf.py [output.pdf]

Pure reportlab (no network). Content is kept faithful to the shipped engine
(config.py / backtest.py / live/*). Re-run after strategy changes to refresh.
"""
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, ListFlowable, ListItem, KeepTogether,
)

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/ICT_Algorithm_Manual.pdf"

# ── palette ──────────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#0B2545")
BLUE   = colors.HexColor("#13315C")
ACCENT = colors.HexColor("#1B7A43")   # green (tips / positive)
WARN   = colors.HexColor("#B23A2E")   # red (warnings)
GOLD   = colors.HexColor("#B8860B")
GREY   = colors.HexColor("#5A6B7B")
LIGHT  = colors.HexColor("#EAF1F7")
RULE   = colors.HexColor("#D5DEE6")

styles = getSampleStyleSheet()


def S(name, **kw):
    styles.add(ParagraphStyle(name, parent=styles["Normal"], **kw))


S("Cover",       fontName="Helvetica-Bold", fontSize=30, textColor=NAVY, leading=34, spaceAfter=6)
S("CoverSub",    fontName="Helvetica",      fontSize=13, textColor=GREY, leading=18)
S("H1",          fontName="Helvetica-Bold", fontSize=17, textColor=NAVY, spaceBefore=6, spaceAfter=4, leading=20)
S("H2",          fontName="Helvetica-Bold", fontSize=12.5, textColor=BLUE, spaceBefore=10, spaceAfter=3, leading=15)
S("Body",        fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#1A1A1A"), leading=14.5, spaceAfter=6, alignment=TA_LEFT)
S("BodyTight",   fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#1A1A1A"), leading=14, spaceAfter=2)
S("Bull",      fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#1A1A1A"), leading=14, spaceAfter=2)
S("Callout",     fontName="Helvetica",      fontSize=9.5, textColor=colors.HexColor("#1A1A1A"), leading=13.5)
S("Cell",        fontName="Helvetica",      fontSize=9,  textColor=colors.HexColor("#1A1A1A"), leading=12)
S("CellB",       fontName="Helvetica-Bold", fontSize=9,  textColor=NAVY, leading=12)
S("Mono",        fontName="Courier-Bold",   fontSize=9.5, textColor=colors.HexColor("#0A3D2A"), leading=13)
S("Foot",        fontName="Helvetica",      fontSize=8,  textColor=GREY)
S("TOC",         fontName="Helvetica",      fontSize=10.5, textColor=BLUE, leading=18)


def P(t, s="Body"):
    return Paragraph(t, styles[s])


def H1(t):
    return KeepTogether([Spacer(1, 4),
                         Paragraph(t, styles["H1"]),
                         HRFlowable(width="100%", thickness=1.4, color=NAVY,
                                    spaceBefore=2, spaceAfter=6)])


def H2(t):
    return Paragraph(t, styles["H2"])


def bullets(items, s="Bull"):
    return ListFlowable(
        [ListItem(Paragraph(i, styles[s]), leftIndent=6, value="•") for i in items],
        bulletType="bullet", bulletColor=NAVY, leftIndent=12, bulletFontSize=8,
    )


def callout(text, kind="tip", label=None):
    color = {"tip": ACCENT, "warn": WARN, "note": BLUE, "gold": GOLD}[kind]
    bg = {"tip": colors.HexColor("#EAF6EE"), "warn": colors.HexColor("#FBECEA"),
          "note": LIGHT, "gold": colors.HexColor("#FBF3E0")}[kind]
    lab = label or {"tip": "TIP", "warn": "IMPORTANT", "note": "NOTE", "gold": "KEY IDEA"}[kind]
    p = Paragraph(f'<font color="{color.hexval()}"><b>{lab}</b></font>&nbsp;&nbsp;{text}',
                  styles["Callout"])
    t = Table([[p]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBEFORE", (0, 0), (0, -1), 3, color),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
    ]))
    return KeepTogether([Spacer(1, 2), t, Spacer(1, 6)])


def table(rows, widths, header=True, font=8.8):
    data = []
    for r in rows:
        data.append([c if hasattr(c, "wrap") else Paragraph(str(c),
                     styles["CellB"] if (header and rows.index(r) == 0) else styles["Cell"])
                     for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
    ]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), NAVY),
               ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
               ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F8FB")])]
    t.setStyle(TableStyle(st))
    return KeepTogether([Spacer(1, 2), t, Spacer(1, 8)])


def mono(lines):
    txt = "<br/>".join(lines)
    p = Paragraph(txt, styles["Mono"])
    t = Table([[p]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F2")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD9CF")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([Spacer(1, 2), t, Spacer(1, 8)])


# ── page furniture ───────────────────────────────────────────────────────────
def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.5 * cm, 19.0 * cm, 1.5 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(2 * cm, 1.05 * cm, "ICT Intermarket Algorithm - Operator's Manual")
    canvas.drawRightString(19.0 * cm, 1.05 * cm, "Page %d" % doc.page)
    canvas.restoreState()


def build():
    doc = BaseDocTemplate(
        OUT, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
        title="ICT Intermarket Algorithm - Operator's Manual",
        author="ICT Algo",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=footer)])
    doc.build(story())


# =============================================================================
#  CONTENT
# =============================================================================
def story():
    s = []

    # ---- COVER ----
    s += [Spacer(1, 4.5 * cm)]
    s += [Paragraph("ICT Intermarket Algorithm", styles["Cover"])]
    s += [Paragraph("Operator's Manual", styles["Cover"])]
    s += [Spacer(1, 6)]
    s += [HRFlowable(width="42%", thickness=2, color=GOLD, spaceAfter=14, hAlign="LEFT")]
    s += [Paragraph(
        "How to run the bot, talk to it from Telegram, place your buy-side / "
        "sell-side levels, and read the session handovers to time entries.",
        styles["CoverSub"])]
    s += [Spacer(1, 1.2 * cm)]
    stat = table([
        ["Instruments", "Backtest (2022-2025)", "Win rate", "Profit factor", "Max drawdown"],
        ["EURUSD - GBPUSD - NZDUSD", "810 trades", "45.9%", "4.47", "-12.95%"],
    ], widths=[5.2 * cm, 3.4 * cm, 2.3 * cm, 2.7 * cm, 2.8 * cm])
    s += [stat]
    s += [Spacer(1, 0.4 * cm)]
    s += [callout(
        "This manual describes the shipped strategy and the semi-auto Telegram "
        "controls. Everything you set is <b>optional and per-day</b>: leave it alone "
        "and the bot trades fully automatically, exactly as backtested. START ON A "
        "DEMO ACCOUNT.", kind="gold", label="READ FIRST")]
    s += [PageBreak()]

    # ---- CONTENTS ----
    s += [H1("Contents")]
    toc = [
        "1.  What the algorithm is",
        "2.  The trading day - sessions &amp; killzones",
        "3.  The AMD cycle - the heartbeat of every trade",
        "4.  The intermarket gate - which pair, which way",
        "5.  How the bot enters - the two models",
        "6.  Session handovers - reading them, trading them",
        "7.  Liquidity levels - your buy-side / sell-side inputs",
        "8.  Targets &amp; exits - where the bot takes profit",
        "9.  Talking to the algorithm - the Telegram manual",
        "10. Risk &amp; circuit breakers",
        "11. A day in the life - worked example",
        "12. Go-live checklist &amp; quick reference",
    ]
    s += [Paragraph(t, styles["TOC"]) for t in toc]
    s += [PageBreak()]

    # ---- 1 ----
    s += [H1("1 - What the algorithm is")]
    s += [P("A fully-automated ICT (Inner Circle Trader) 2022 day-trading system for "
            "three FX pairs: <b>EURUSD, GBPUSD, NZDUSD</b>. It trades the "
            "<b>AMD cycle</b> (Accumulation &#8594; Manipulation &#8594; Distribution) "
            "during the London and New York killzones, gated by a three-layer "
            "intermarket model built on the US Dollar Index (DXY).")]
    s += [P("The core idea, in one sentence: <b>the market moves to liquidity.</b> "
            "Big players push price to where retail stop-losses rest (a sweep / "
            "\"Judas swing\"), fill their orders against that liquidity, then deliver "
            "price to the opposite pool. The bot is built to fade that sweep (reversal) "
            "or ride the confirmed break (continuation).")]
    s += [H2("What you bring")]
    s += [P("The bot is complete on its own. The <b>semi-auto</b> layer lets you add "
            "your read of the day on top of it: the lot to use, which direction to "
            "hunt on a pair, the liquidity levels you're watching, and whether to let "
            "a trade run across sessions. Your inputs <b>filter and aim</b> the bot - "
            "they never override its risk rules or force a trade with no setup.")]
    s += [callout("Everything in this manual is opt-in. If you send no commands, every "
                  "pair trades fully automatically. The Telegram controls are there for "
                  "the days you have a strong view.", kind="tip")]

    # ---- 2 ----
    s += [H1("2 - The trading day: sessions &amp; killzones")]
    s += [P("The bot only looks for trades inside defined <b>killzones</b> - the windows "
            "when institutional flow is active. All times are <b>New York time (ET)</b>, "
            "which is what the engine uses internally.")]
    s += [table([
        ["Session", "Window (ET)", "Pairs", "Character"],
        ["London Open", "02:00 - 05:00", "EURUSD, GBPUSD, NZDUSD", "Judas reversal home - the day's manipulation"],
        ["NY AM", "07:00 - 10:00", "EURUSD, GBPUSD", "Continuation / second delivery (NZD drains here)"],
        ["NY noon block", "12:00 - 13:00", "none", "Hard no-trade - lunchtime chop"],
        ["NY PM", "13:00 - 16:00", "optional (off by default)", "Position-squaring / mean-reversion"],
    ], widths=[3.0 * cm, 2.9 * cm, 4.3 * cm, 6.2 * cm])]
    s += [P("Each session is evaluated <b>independently</b> - a clean handover. London's "
            "read does not bleed into New York; when NY opens it starts a fresh AMD "
            "cycle. That separation is exactly what lets you treat the handover as its "
            "own trade setup (Section 6).")]

    # ---- 3 ----
    s += [H1("3 - The AMD cycle: the heartbeat of every trade")]
    s += [P("Every setup the bot takes is a phase of the same three-part cycle. Learn to "
            "see it and the rest of the manual clicks into place.")]
    s += [table([
        ["Phase", "When", "What is happening", "Your levels"],
        ["Accumulation", "Asian / pre-session", "Price coils in a tight range. Orders build. Volume is quiet.", "The range that will be swept"],
        ["Manipulation", "Session open (the Judas)", "Price spikes through one side of the range to grab stops, then snaps back.", "The side that gets swept"],
        ["Distribution", "The real move", "Price delivers in the opposite direction, toward the far liquidity pool.", "The side it targets"],
    ], widths=[2.7 * cm, 3.1 * cm, 6.7 * cm, 3.9 * cm])]
    s += [callout("The Judas swing (manipulation) is the anchor. A sweep of one side that "
                  "closes back inside the range is the bot's highest-conviction signal to "
                  "trade the other way. Your <b>/levels</b> tell it which pools you expect "
                  "to be swept and delivered to.", kind="gold")]

    # ---- 4 ----
    s += [H1("4 - The intermarket gate: which pair, which way")]
    s += [P("Before any pair can trade, the dollar has to agree. This is a hard gate - "
            "no intermarket signal, no trade.")]
    s += [bullets([
        "<b>DXY (US Dollar Index)</b> sets USD direction on the H1 chart. If DXY is flat "
        "(no break of structure), every pair is skipped.",
        "<b>EURGBP</b> selects the EUR-vs-GBP family: it decides whether the cleaner "
        "short/long is on EURUSD or GBPUSD.",
        "<b>AUDNZD</b> selects the NZD family, routing to NZDUSD.",
    ])]
    s += [P("The result is a <b>scenario</b> (e.g. \"DXY up + EUR stronger than GBP "
            "&#8594; short GBPUSD\"). You don't need to memorise the scenarios - the bot "
            "classifies them - but it's why a `/bias` you set must still line up with a "
            "real intermarket signal to produce a trade.")]

    # ---- 5 ----
    s += [H1("5 - How the bot enters: the two models")]
    s += [H2("Model 1 - Judas reversal (the default)")]
    s += [bullets([
        "An M15 consolidation range must exist (both extremes tested).",
        "Price sweeps one extreme (the Judas swing) and closes back inside.",
        "2-of-3 market-structure shifts confirm (EURUSD + GBPUSD + DXY inverse).",
        "Entry is a limit into an M5/M15/H1 fair-value gap (FVG) or order block (OB).",
        "Stop sits beyond the structural swing, capped tight (about 10 pips).",
    ])]
    s += [H2("Model 2 - Intermarket breakout / continuation")]
    s += [P("The inverse of Judas: instead of fading a sweep, the bot rides a confirmed "
            "break. It requires <b>triple confirmation</b> - EURUSD and GBPUSD both break "
            "their M15 ranges in agreement AND DXY confirms with a break of structure. A "
            "single-pair break is treated as a fakeout and ignored. These continuations "
            "run <b>with</b> the higher-timeframe draw and are the natural NY-session trade.")]
    s += [callout("Reversal fades the sweep; breakout rides the break. The bot tags every "
                  "trade as <b>judas</b> or <b>breakout</b> so you can see which model "
                  "fired in the Telegram trade alert.", kind="note")]

    # ---- 6  (the requested deep dive) ----
    s += [H1("6 - Session handovers: reading them, trading them")]
    s += [P("A <b>handover</b> is the gap between two sessions - most importantly "
            "<b>London &#8594; New York</b> (roughly 05:00-07:00 ET). This is where a lot "
            "of the day's best entries are made, so it's worth understanding well.")]
    s += [H2("What happens at a handover")]
    s += [bullets([
        "London runs its Judas + delivery and sets the <b>day's USD direction</b> "
        "(a DXY-wide move).",
        "Into the handover, price <b>consolidates</b> - it pulls back, often to the "
        "session open, a 50% level, or an unfilled FVG. This is a fresh accumulation for NY.",
        "At the NY open, price <b>shifts structure</b> (a break on M5/M15) and either "
        "<b>continues</b> London's direction or starts a fresh NY Judas.",
    ])]
    s += [H2("How the bot manages your open trade at the handover")]
    s += [P("At the 02:00 and 07:00 ET boundaries the bot runs a single check. It closes "
            "a position <b>only if BOTH</b>: (a) it is losing, AND (b) it is fighting the "
            "confirmed weekly bias. Anything winning, or aligned with the week, is left "
            "to run. So a good London trade already carries into New York by default.")]
    s += [callout("Use <b>/hold EURUSD</b> to exempt a pair from that close entirely - it "
                  "then runs into NY (and NY-AM into the afternoon) on its stop, target "
                  "and trailing only. That is the instruction for \"leave my London trade "
                  "open and let it run.\"", kind="tip")]
    s += [H2("How to trade the handover for entries")]
    s += [P("A simple, repeatable playbook that lines up with what the bot already does:")]
    s += [bullets([
        "<b>Read London's direction.</b> Which way did the dollar go after the London "
        "Judas? That is the day's bias.",
        "<b>Mark the handover consolidation.</b> Note the high and low price coils into "
        "over 05:00-07:00 ET - the buy-side (above) and sell-side (below).",
        "<b>Feed those to the bot.</b> Set <b>/levels</b> with sell-side below (for a "
        "long continuation) or buy-side above (for a short), and <b>/bias</b> to London's "
        "direction so the bot only hunts the continuation.",
        "<b>Let the sweep confirm the entry.</b> At NY open price typically sweeps the "
        "handover range once (a small Judas) then continues - the bot enters the retrace "
        "into the FVG, targeting the far side.",
        "<b>/hold the London trade</b> if you'd rather ride the original position through "
        "than take a fresh NY entry.",
    ])]
    s += [callout("The continuation \"looks like a small Judas swing but is really a "
                  "continuation\" - a sweep of the handover range in the direction of the "
                  "London/DXY move. That is the single most reliable NY-session entry, and "
                  "your /levels + /bias point the bot straight at it.", kind="gold")]

    # ---- 7  (levels deep dive) ----
    s += [H1("7 - Liquidity levels: your buy-side / sell-side inputs")]
    s += [P("This is how you hand the bot the levels you're watching. In ICT terms:")]
    s += [table([
        ["Term", "Where", "What rests there", "Typical sources"],
        ["Buy-side liquidity", "ABOVE price", "Resting buy stops (shorts' stops, breakout buys)",
         "Old highs, PDH, session high, equal highs, round numbers"],
        ["Sell-side liquidity", "BELOW price", "Resting sell stops (longs' stops, breakdown sells)",
         "Old lows, PDL, session low, equal lows, round numbers"],
    ], widths=[3.0 * cm, 2.3 * cm, 4.9 * cm, 6.2 * cm])]
    s += [H2("How to add them")]
    s += [mono(["/levels EURUSD buy 1.0975 1.0990 sell 1.0900 1.0880"])]
    s += [P("<b>buy</b> = the pools above price; <b>sell</b> = the pools below. List as "
            "many as you like on each side, space-separated. They apply to that pair for "
            "the rest of the UTC day and expire overnight.")]
    s += [H2("What the bot does with them - full manual AMD")]
    s += [P("Your two sides define the day's range, and the bot trades the AMD cycle "
            "across them:")]
    s += [bullets([
        "Price sweeps the <b>sell-side</b> and reclaims &#8594; the bot hunts <b>LONG</b>, "
        "targeting the <b>buy-side</b>.",
        "Price sweeps the <b>buy-side</b> and drops back &#8594; the bot hunts "
        "<b>SHORT</b>, targeting the <b>sell-side</b>.",
        "Neither side swept yet &#8594; the bot <b>waits</b> (manipulation hasn't happened).",
    ])]
    s += [P("So the same levels do two jobs at once: <b>entries</b> (the sweep of one side "
            "arms the trade and its direction) and <b>exits</b> (the opposite side becomes "
            "the take-profit draw). The bot's own structure + FVG entry must still trigger "
            "- your levels decide <b>which way</b> and <b>where to</b>, the engine decides "
            "<b>whether the setup is there</b>.")]
    s += [callout("Put your sell-side where you expect stops to be run BEFORE a long (just "
                  "under an obvious low / round number), and your buy-side at the draw you "
                  "expect price to deliver to. The bot will wait for the sweep, then aim "
                  "for your target.", kind="tip")]

    # ---- 8 ----
    s += [H1("8 - Targets &amp; exits: where the bot takes profit")]
    s += [P("Left on auto, the bot chooses the <b>nearest qualifying</b> institutional "
            "draw as its target - never a far moonshot. Candidate draws, scored by how "
            "many agree at one price (confluence):")]
    s += [bullets([
        "Fibonacci extensions (the workhorse), fair-value-gap and order-block midpoints,",
        "Previous day / week high &amp; low (PDH/PDL, PWH/PWL), intermediate swing highs/lows,",
        "Equal highs/lows and round numbers.",
    ])]
    s += [P("Minimum target distance is <b>30 pips</b>. When you set <b>/levels</b>, the "
            "opposite side replaces the auto target (if it's a valid, far-enough draw).")]
    s += [H2("Protecting the trade - the trailing ladder")]
    s += [table([
        ["Profit reached", "Stop moves to"],
        ["+10 pips", "Break-even (entry)"],
        ["+20 pips", "Locked at +10 pips"],
        ["+40 / +60 / +80 ...", "Milestone trail: +30 / +50 / +70 ... (locks every +20)"],
    ], widths=[4.5 * cm, 11.9 * cm])]
    s += [P("Short-target trades exit at the take-profit before any milestone fires. "
            "Long-running trades (into distant draws) ratchet the stop up every 20 pips so "
            "a late reversal still banks most of the move.")]
    s += [callout("The take-profit is the END of the AMD delivery cycle. The bot exits "
                  "into the draw rather than holding for more - testing showed holding past "
                  "it gives back profit. The far pools are the NEXT cycle's job.", kind="note")]

    # ---- 9  (Telegram manual) ----
    s += [H1("9 - Talking to the algorithm: the Telegram manual")]
    s += [P("You control the bot by replying to its messages in Telegram. It only obeys "
            "<b>your</b> chat - no one else can steer it. Every command is acknowledged so "
            "you always see what registered. Send <b>/help</b> any time for the list.")]
    s += [H2("Session templates - you get one at every session start")]
    s += [P("At the top of each session the bot messages you a template to reply to "
            "(<b>LONDON</b> ~02:00 ET, <b>NEW YORK AM</b> ~07:00 ET, and <b>NEW YORK PM</b> "
            "if enabled). The NY templates also list what's already open, so you can "
            "decide whether to <b>/hold</b> it across the handover.")]
    s += [H2("Command reference")]
    s += [table([
        ["Command", "What it does"],
        ["/lot 0.02", "Day lot for all pairs (/lot GBPUSD 0.03 for one). Base lot - the sizing multipliers still stack."],
        ["/bias EURUSD long", "Hunt one direction only (long | short | both). A filter: the bot still needs its own setup."],
        ["/levels EURUSD buy 1.0975 sell 1.0900", "Your buy-side / sell-side liquidity -> full manual AMD (Section 7)."],
        ["/hold EURUSD", "Let this pair run across the session handover (also /hold all). /release EURUSD undoes it."],
        ["/close EURUSD", "Close this pair's open position(s) at market now (/close all flattens everything)."],
        ["/halt", "Stop ALL new entries and pyramid adds. Open trades keep running on their stops."],
        ["/resume", "Re-enable new entries after a /halt."],
        ["/status", "Echo today's plan for every pair."],
        ["/auto EURUSD", "Revert one pair to full auto (/clear reverts all)."],
        ["/help", "The command list."],
    ], widths=[5.6 * cm, 10.8 * cm])]
    s += [callout("To go flat and stay out: <b>/close all</b> then <b>/halt</b>. To stop "
                  "new trades but let current winners run: just <b>/halt</b>.", kind="tip")]

    # ---- 10 ----
    s += [H1("10 - Risk &amp; circuit breakers")]
    s += [P("Sizing follows equity tiers (it grows as the account grows). A day lot you "
            "set with <b>/lot</b> becomes the base; the conviction multipliers "
            "(2x/3x on a full higher-timeframe draw, 1.25x on high-confluence / CRT / "
            "prior-day-liquidity sweeps) still stack on top - but only above R3,000 equity, "
            "so they stay dormant while the account is small.")]
    s += [P("Four automatic breakers protect the account. They run regardless of any "
            "semi-auto input:")]
    s += [table([
        ["Breaker", "Trigger", "Action"],
        ["Max drawdown halt", "-15% from peak equity", "Pause trading 10 days"],
        ["Daily loss cap", "-6% of the day's opening equity", "No new entries rest of day"],
        ["Consecutive losses", "5 losses in a row", "Pause rest of day"],
        ["Session kill switch", "-10% from session open", "Close all positions, halt the day"],
    ], widths=[3.6 * cm, 5.6 * cm, 7.2 * cm])]

    # ---- 11 ----
    s += [H1("11 - A day in the life")]
    s += [P("A worked example of driving the bot through a full day.")]
    s += [H2("07:55 ET - the LONDON template already fired; you reply")]
    s += [mono([
        "/lot 0.02",
        "/bias EURUSD long",
        "/levels EURUSD buy 1.0975 sell 1.0900 1.0880",
        "/hold EURUSD",
    ])]
    s += [P("The bot acks each line. It will trade EURUSD <b>long only</b>, and only "
            "<b>after</b> price sweeps 1.0900 / 1.0880 and reclaims - aiming at 1.0975 - "
            "and only if its own structure + FVG entry fires. GBPUSD and NZDUSD keep "
            "trading fully automatically.")]
    s += [H2("08:30 ET - TRADE OPENED alert")]
    s += [P("The bot messages you the entry, stop, target, scenario and model. Your "
            "London long is on. You watch from your phone; no need to sit at the screen.")]
    s += [H2("07:00 ET next block - NEW YORK AM template")]
    s += [P("\"Open now: EURUSD - holding: EURUSD.\" Because you set /hold, the London long "
            "is running into New York instead of being closed at the handover. You could "
            "add <b>/bias GBPUSD short</b> for the NY session, or <b>/release EURUSD</b> if "
            "you've changed your mind. If it's gone far enough, <b>/close EURUSD</b> banks it.")]
    s += [H2("Anytime - things go wrong")]
    s += [P("News spike, or you just want out: <b>/close all</b> flattens everything and "
            "<b>/halt</b> stops new entries until you <b>/resume</b>.")]

    # ---- 12 ----
    s += [H1("12 - Go-live checklist &amp; quick reference")]
    s += [H2("Go-live checklist (do not skip)")]
    s += [bullets([
        "Bootstrap the VM, install MT5, log into your Exness <b>DEMO</b> account.",
        "Smoke test passes (every symbol resolves, DXY reads ~90-115).",
        "Semi-auto self-test passes: <font face='Courier'>python -m live.test_semi_auto</font>.",
        "Run on DEMO for at least 2 weeks; reconcile a few fills against data\\live.log.",
        "Confirm a /hold across a real handover behaves as expected on demo.",
        "Only then switch live.env to the funded account and start small.",
    ])]
    s += [H2("Quick reference card")]
    s += [table([
        ["/lot 0.02", "day lot (base; multipliers stack)"],
        ["/bias EURUSD long|short|both", "direction filter"],
        ["/levels EURUSD buy ... sell ...", "manual-AMD liquidity (sweep -> target)"],
        ["/hold EURUSD  |  /release EURUSD", "run across the handover / undo"],
        ["/close EURUSD  |  /close all", "close now / flatten"],
        ["/halt  |  /resume", "pause / re-enable new entries + adds"],
        ["/status  |  /auto EURUSD  |  /clear", "review / revert one / revert all"],
    ], widths=[6.4 * cm, 10.0 * cm], header=False)]
    s += [callout("The strategy is validated in backtest, not yet proven live. This manual "
                  "gets you operating it correctly; the demo-first discipline is what keeps "
                  "the R500 safe while live behaviour is confirmed.", kind="warn")]
    s += [Spacer(1, 6)]
    s += [Paragraph("Generated from the shipped engine. Re-run "
                    "<font face='Courier'>python scripts/build_manual_pdf.py</font> after "
                    "strategy changes to refresh.", styles["Foot"])]

    return s


if __name__ == "__main__":
    import os
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    build()
    print(f"wrote {OUT}")
