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
    PageBreak, HRFlowable, ListFlowable, ListItem, KeepTogether, Preformatted,
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


def sketch(text):
    """Monospace ASCII diagram with whitespace preserved (Preformatted). Use for
    price-ladder sketches where alignment matters - Paragraph collapses spaces."""
    p = Preformatted(text.strip("\n"), styles["Mono"])
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
        "4.  How market structure is detected &amp; traded",
        "5.  The intermarket gate - which pair, which way",
        "6.  How the bot enters - the entry models (incl. Market Maker IFVG)",
        "7.  Session handovers - reading them, trading them",
        "8.  Liquidity levels - your buy-side / sell-side inputs",
        "9.  Targets &amp; exits - where the bot takes profit",
        "10. Talking to the algorithm - the Telegram manual",
        "11. Risk &amp; circuit breakers",
        "12. A day in the life - worked example",
        "13. Go-live checklist &amp; quick reference",
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
        ["Session / window", "ET", "SAST", "Character"],
        ["London KZ", "03:00 - 05:00", "10:00 - 12:00", "Judas reversal home - the day's manipulation"],
        ["London silver bullet", "03:00 - 04:00", "10:00 - 11:00", "High-probability window inside London"],
        ["NY AM KZ", "07:00 - 10:00", "14:00 - 17:00", "Continuation / second delivery (incl. 9:30 open)"],
        ["NY AM silver bullet", "10:00 - 11:00", "17:00 - 18:00", "Prime NY-AM window"],
        ["Lunch (no-trade)", "12:00 - 13:00", "19:00 - 20:00", "Hard no-trade - lunchtime chop"],
        ["NY PM KZ", "13:30 - 16:00", "20:30 - 23:00", "Position-squaring / mean-reversion (opt., off by default)"],
        ["NY PM silver bullet", "14:00 - 15:00", "21:00 - 22:00", "Prime PM window"],
        ["NY close / after", "16:00 - 17:00", "23:00 - 00:00", "Cash close, late delivery"],
    ], widths=[3.6 * cm, 2.7 * cm, 2.7 * cm, 7.4 * cm], font=8.0)]
    s += [P("<b>SAST is UTC+2 (no DST); ET shifts with US daylight time</b>, so the SAST "
            "column drifts ~1h in the US winter. The <b>silver bullets</b> are the "
            "one-hour high-probability windows inside the killzones. Send <b>/session</b> "
            "any time and the bot shows this whole timeline live in SAST | ET, which "
            "window is active now, when the next starts, what the earlier sessions did "
            "today, and the PD arrays near price.")]
    s += [callout("When the US index gate is enabled (INDICES_ENABLED), <b>US500 and "
                  "US100</b> trade these same NY sessions (gated by DXY + the sibling index "
                  "+ US30) and are steerable from Telegram exactly like a currency - "
                  "<font face='Courier'>/bias US100 long</font>, <font face='Courier'>/lot "
                  "US500 0.20</font>, <font face='Courier'>/mm</font>, <font face='Courier'>"
                  "/trail</font>. ICT logic (SMT, the 9:30 open, silver bullets) is most "
                  "active on the indices.", kind="note")]
    s += [P("Each session is evaluated <b>independently</b> - a clean handover. London's "
            "read does not bleed into New York; when NY opens it starts a fresh AMD "
            "cycle. That separation is exactly what lets you treat the handover as its "
            "own trade setup (Section 7).")]

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

    # ---- 4  (structure detection + the HTF-read / LTF-entry play) ----
    s += [H1("4 - How market structure is detected &amp; traded")]
    s += [P("Structure is the skeleton the whole strategy hangs on - it says where the "
            "swing highs and lows are, which are still holding, and therefore which way "
            "price is really going. Here is how the bot finds them, and the key point: it "
            "<b>reads structure on the higher timeframe but takes the entry on the lower</b>.")]

    s += [H2("The atomic unit - a 3-bar fractal")]
    s += [P("A swing is the simplest ICT pattern: a candle whose extreme is beyond the "
            "candle on <b>each</b> side.")]
    s += [mono([
        "Swing HIGH (STH) - middle bar's HIGH above BOTH neighbours:",
        "",
        "          b2",
        "         /  \\          b2.High &gt; b1.High  AND  b2.High &gt; b3.High",
        "       b1    b3        -&gt; b2 is a Short-Term High (STH)",
        "",
        "Swing LOW (STL) - middle bar's LOW below BOTH neighbours:",
        "",
        "       b1    b3        b2.Low &lt; b1.Low   AND  b2.Low &lt; b3.Low",
        "         \\  /          -&gt; b2 is a Short-Term Low (STL)",
        "          b2",
    ])]
    s += [P("Because a swing needs a candle on <b>each</b> side, it is only confirmed when "
            "the <b>third (right-side) bar</b> prints. The bot works off completed bars, so "
            "nothing repaints - and that third-bar rule is the whole key to the entry "
            "timing below.")]

    s += [H2("The tiers are recursive, not wider lookbacks")]
    s += [P("The three ICT tiers are built by promoting the tier below - each is a fractal "
            "of the one under it:")]
    s += [table([
        ["Tier", "Definition"],
        ["STH / STL (short-term)", "A 3-bar fractal on the raw candles."],
        ["ITH / ITL (intermediate)", "A short-term high with a LOWER short-term high on each side (a fractal WITHIN the STH sequence). ITL is the inverse on STLs."],
        ["LTH / LTL (long-term)", "An intermediate high with a lower intermediate high on each side - one tier up again."],
    ], widths=[4.6 * cm, 11.8 * cm])]

    s += [H2("Swept vs. intact - the level that still matters")]
    s += [P("After classifying, every swing is tagged: a high is <b>swept</b> once a later "
            "bar trades through it, a low once a later bar drops below it. The most recent "
            "<b>unswept</b> swing of a tier is the live reference - the level still holding. "
            "That one distinction drives the strategy:")]
    s += [bullets([
        "The <b>stop</b> sits beyond the intact intermediate swing (ITL for longs / ITH for "
        "shorts) - not the short-term swing, which gets run constantly.",
        "The <b>trend read</b> is the intermediate tier: higher ITLs = bullish, lower ITHs "
        "= bearish.",
        "<b>Judas vs. real break:</b> short-term swings getting taken while the ITH/ITL "
        "stays intact is a minor liquidity run (a Judas) - NOT a trend change. That double "
        "sweep is exactly what the bot fades.",
    ])]

    s += [H2("The play: read structure HIGH, enter LOW")]
    s += [P("This is the heart of the entry. Structure is confirmed on the higher "
            "timeframe, but the entry is taken on the lower - so you are filled early, not "
            "waiting for a slow HTF candle to close.")]
    s += [bullets([
        "<b>1. Read the HTF.</b> On H4/H1 the draw cascade + fractal show the ITH/ITL is in "
        "place and an MSS (break of structure) has fired - you now know the bias and the "
        "draw (which way, and the pool price is headed for).",
        "<b>2. Anticipate the reversal swing on the LTF.</b> Drop to M5/M15 and wait for the "
        "counter-swing to form - an <b>STL</b> for a long (or <b>STH</b> for a short) at "
        "your entry zone (the FVG / OB).",
        "<b>3. Enter as that swing confirms.</b> The moment the LTF swing's <b>third bar</b> "
        "prints, the reversal is confirmed and price is already turning your way - you are "
        "in the move as it happens, stop just beyond the swing.",
    ])]
    s += [callout("Because the LTF swing's third bar confirms in minutes, you do NOT wait "
                  "for the higher-timeframe candle to close - by the time an H1/H4 candle "
                  "would confirm the same swing, the move is long gone. The HTF gives the "
                  "direction and the draw; the LTF 3-bar swing gives the early, precise "
                  "entry.", kind="gold")]
    s += [P("In the engine this is literal: the HTF draw cascade (W/D/H4) sets the bias, the "
            "<b>MSS is checked on M15/M5</b>, entry is a limit into the M5/M15 FVG/OB, and "
            "the stop is anchored on the <b>M1</b> intact swing. The bot re-evaluates on "
            "<b>every M5 close</b> - so the LTF swing confirms and you are filled while the "
            "H1/H4 candle is still only part-formed.")]

    # ---- 5 ----
    s += [H1("5 - The intermarket gate: which pair, which way")]
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
    s += [H1("6 - How the bot enters: the entry models")]
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

    s += [H2("Model 3 - Market Maker IFVG model (watch or auto-enter)")]
    s += [P("A third, <b>opt-in</b> model you arm per pair from Telegram with "
            "<b>/mm</b>. It watches the higher timeframes for an <b>inversion fair-value "
            "gap (IFVG)</b> - a gap that price later closes a full body back through, "
            "flipping its polarity. That flip is a <b>Judas swing one timeframe up</b>: "
            "the level that repelled price now supports it, drawing price toward the same "
            "liquidity targets the bot already uses.")]
    s += [P("An FVG that gets a bullish full-body close back <b>above</b> it becomes a "
            "<b>demand (support)</b> zone; a bearish full-body close <b>below</b> makes a "
            "<b>supply (resistance)</b> zone. The bot scans <b>D1, H4 and H1</b> and keeps "
            "only the still-defended zones in your model's direction.")]
    s += [sketch(
        "BUY model - a demand IFVG (support)\n"
        "\n"
        "  a bearish gap forms as price drops through it, then price\n"
        "  RETURNS and closes a full body back ABOVE it -> the gap\n"
        "  inverts into a DEMAND zone that now holds price up.\n"
        "\n"
        "     1.15470  +----------------+  zone top\n"
        "              |  DEMAND  IFVG  |\n"
        "     1.15400  +----------------+  zone bottom")]
    s += [H2("The three beats - what to do, and when")]
    s += [P("In <b>/read</b> and <b>/brief</b> each armed zone shows how far price is "
            "(pips + % of the way from where you armed it) and <b>which beat</b> of the "
            "setup it is on. Read the beat, take the action:")]
    s += [table([
        ["Beat", "Read shows", "Meaning", "Do"],
        ["[1]", "approaching NN%", "price still travelling to the zone", "wait (watch the % climb)"],
        ["[2]", "TAGGED", "price is inside the zone", "get ready - a touch is not the entry"],
        ["[3]", "CONFIRMED", "a fresh lower-TF swing formed off the zone", "ENTER (auto fires here)"],
        ["[x]", "BROKEN", "a full body closed through the zone", "skip it - use the next zone down"],
    ], widths=[1.5 * cm, 3.4 * cm, 6.6 * cm, 4.9 * cm])]
    s += [sketch(
        "BUY entry (demand IFVG sits BELOW price)\n"
        "\n"
        "  1.15800  = = = TARGET (buy-side draw: ITH / PDH)     ^ 3 ride up\n"
        "  1.15600  o  price now                                |\n"
        "             |  1 price retraces DOWN toward the zone\n"
        "             v\n"
        "  1.15470  +----------------+  zone top\n"
        "           |  DEMAND  IFVG  |   2 TAG -> swing UP = ENTER (beat 3)\n"
        "  1.15400  +----------------+  zone bottom\n"
        "  1.15380  x  stop (just below the zone - bot's structural stop)")]
    s += [sketch(
        "SELL entry (supply IFVG sits ABOVE price) - the mirror\n"
        "\n"
        "  1.16120  x  stop (just above the zone)\n"
        "  1.16100  +----------------+  zone top\n"
        "           |  SUPPLY  IFVG  |   2 TAG -> swing DOWN = ENTER (beat 3)\n"
        "  1.16030  +----------------+  zone bottom\n"
        "             ^  1 price rises UP toward the zone\n"
        "  1.15900  o  price now\n"
        "             |  3 ride down\n"
        "             v\n"
        "  1.15600  = = = TARGET (sell-side draw: ITL / PDL)")]
    s += [sketch(
        "A zone that FAILS (beat [x] BROKEN) - do NOT trade it\n"
        "\n"
        "  1.15470  +----------------+  zone top\n"
        "           |  DEMAND  IFVG  |\n"
        "  1.15400  +----------------+  zone bottom\n"
        "             |  a full body CLOSES below the zone\n"
        "             v\n"
        "  1.15350  XX  zone SPENT -> skip it, drop to the next zone")]
    s += [H2("Watch vs. auto-enter")]
    s += [bullets([
        "<b>/mm EURUSD buy</b> (or <b>sell</b>) - <b>WATCH</b> mode: the bot only alerts "
        "you (\"price REACHED ...\", \"... IFVG BROKEN\") and shows the beats. You place the "
        "entry yourself at beat [3] with <b>/test</b> (or <b>/pyramid</b> to add to a winner).",
        "<b>/mm EURUSD buy auto</b> - <b>AUTO</b> mode: you pre-permit <b>one</b> entry. "
        "When a zone hits beat [3] (price inside the IFVG AND a fresh LTF swing confirms) "
        "the bot enters it for you - own structural stop, nearest-liquidity target, your "
        "/lot size - then <b>disarms</b> (one shot). The header shows <b>[AUTO-ARMED]</b>.",
        "<b>/mm EURUSD off</b> - disarm. Everything expires at 00:00 UTC like all inputs.",
    ])]
    s += [callout("Auto is one entry only and obeys every safety rule: <b>/halt</b> blocks "
                  "it, and if a same-direction winner is already open it adds a pyramid leg "
                  "instead of a second position (opposite - it skips). Re-arm with "
                  "<b>/mm PAIR buy auto</b> to allow another.", kind="gold")]

    # ---- 6  (the requested deep dive) ----
    s += [H1("7 - Session handovers: reading them, trading them")]
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
    s += [H1("8 - Liquidity levels: your buy-side / sell-side inputs")]
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
    s += [H1("9 - Targets &amp; exits: where the bot takes profit")]
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
    s += [H2("Structure trail - riding the swings (optional)")]
    s += [P("On top of the automatic ladder you can trail the stop by <b>market "
            "structure</b> from Telegram with <b>/trail</b> - the stop follows the latest "
            "<b>intact fractal swing</b> on a lower timeframe, keeping a pip buffer you "
            "choose. It only ever tightens, and stacks with the ladder above (whichever "
            "stop is tighter wins).")]
    s += [table([
        ["Choice", "Options", "Effect"],
        ["Timeframe", "m15 / m5 / m1", "How fine the swings it follows are (m1 = tightest)."],
        ["Tier", "st = STH/STL, it = ITH/ITL", "Short-term locks faster; intermediate is looser, fewer stop-outs."],
        ["Buffer", "a pip number (default 2)", "How far beyond the swing the stop sits."],
    ], widths=[2.8 * cm, 5.0 * cm, 8.6 * cm])]
    s += [P("For a <b>long</b> the stop trails under the latest intact low (STL/ITL minus "
            "buffer); for a <b>short</b>, above the latest intact high (STH/ITH plus buffer) "
            "- the bot picks the correct side. Example: <font face='Courier'>/trail EURUSD "
            "m5 st 3</font> rides the M5 short-term structure 3 pips behind each swing; "
            "<font face='Courier'>/trail EURUSD off</font> stops it.")]

    # ---- 9  (Telegram manual) ----
    s += [H1("10 - Talking to the algorithm: the Telegram manual")]
    s += [P("You control the bot by replying to its messages in Telegram. It only obeys "
            "<b>your</b> chat - no one else can steer it. Every command is acknowledged so "
            "you always see what registered. Send <b>/help</b> any time for the list.")]
    s += [H2("Session templates - you get one at every session start")]
    s += [P("At the top of each session the bot messages you a template to reply to "
            "(<b>LONDON</b> ~02:00 ET, <b>NEW YORK AM</b> ~07:00 ET, and <b>NEW YORK PM</b> "
            "if enabled). The NY templates also list what's already open, so you can "
            "decide whether to <b>/hold</b> it across the handover.")]
    s += [H2("Ask the bot (read anytime - no effect on trading)")]
    s += [table([
        ["Command", "What it shows"],
        ["/brief", "Full session brief: account + structure + open trades + your plan. The same rich summary the bot sends at each session start."],
        ["/read [EURUSD]", "Market-structure template per pair: price, H4/H1/M15 structure, ITH/ITL draws, directional lean %, the bot's intended trade + scenario, plus any armed MM IFVG beats. /markets = all at a glance."],
        ["/positions", "Open trades broken out PER LEG (e.g. 2 x 0.02 = 0.04), each with entry, live pips, SL and ticket - plus P&amp;L, % to target, model, TP idea + SL basis (survives restarts)."],
        ["/account", "Equity, day P&amp;L, drawdown, halt state (also /equity)."],
        ["/dxy - /session - /news", "Dollar index - full day session timeline (SAST|ET: killzones, silver bullets, PM, NY close) with active/next + earlier-session recap + PD arrays near price - next high-impact news."],
        ["/whoami", "Your chat id + access level."],
    ], widths=[4.3 * cm, 12.1 * cm])]
    s += [H2("Plan &amp; control")]
    s += [table([
        ["Command", "What it does"],
        ["/lot 0.02", "Day lot for all pairs (/lot GBPUSD 0.03 for one). Base lot - the sizing multipliers still stack."],
        ["/bias EURUSD long", "Hunt one direction only (long | short | both). A filter: the bot still needs its own setup."],
        ["/levels EURUSD buy 1.0975 sell 1.0900", "Your buy-side / sell-side liquidity -> full manual AMD (Section 8)."],
        ["/mm EURUSD buy [auto]", "Arm the Market Maker IFVG model: watch-only, or 'auto' to pre-permit one entry (Section 6, Model 3). /mm EURUSD off disarms."],
        ["/hold EURUSD", "Let this pair run across the session handover (also /hold all). /release EURUSD undoes it."],
        ["/trail EURUSD m5 st 3", "Trail the stop behind the latest intact swing: tf m15|m5|m1, tier st (STH/STL) or it (ITH/ITL), pip buffer. Only tightens. /trail EURUSD off."],
        ["/test EURUSD long [0.05]", "Open a trade NOW (also short; /buy /sell) with the bot's structural stop + 2R target, at an optional lot size."],
        ["/pyramid EURUSD [1.1600]", "Add a leg to a WINNING position - same TP, or a level you give."],
        ["/sl EURUSD 1.1555 - /be EURUSD", "Move the stop to a price (or /sl EURUSD 2 ... for one leg); /be moves it to break-even."],
        ["/close EURUSD [2]", "Close the whole position, or just leg 2 (/close all flattens everything; /flat is the shortcut)."],
        ["/halt - /resume", "Stop ALL new entries + pyramid adds (open trades keep running) - then re-enable."],
        ["/status - /auto EURUSD - /clear - /help", "Echo today's plan - revert one pair - revert all - command list."],
    ], widths=[5.6 * cm, 10.8 * cm])]
    s += [callout("To go flat and stay out: <b>/close all</b> then <b>/halt</b>. To stop "
                  "new trades but let current winners run: just <b>/halt</b>.", kind="tip")]
    s += [H2("Sharing the bot with a partner")]
    s += [P("Your partner opens the <b>same</b> bot (share the link) and texts it - you do "
            "NOT create a second bot. What they can do depends on how you list their Telegram "
            "chat id (they get theirs from @userinfobot, or /whoami once they can read):")]
    s += [bullets([
        "<b>Admin</b> (full control, trades like you) - add their id to "
        "<font face='Courier'>TELEGRAM_ADMIN_IDS</font> in live.env.",
        "<b>Viewer</b> (read-only + alerts) - add it to "
        "<font face='Courier'>TELEGRAM_VIEWER_IDS</font>.",
        "<b>Open read-only</b> for anyone with the link - set "
        "<font face='Courier'>TELEGRAM_OPEN_VIEW=1</font> (trading still needs an admin id).",
    ])]
    s += [callout("Easiest way to add someone: "
                  "<font face='Courier'>scripts\\add_access.ps1 -Id &lt;id&gt; -Role admin|viewer</font> "
                  "on the VM, then restart the bot so it re-reads live.env. Trading control "
                  "can never be open - it moves real money.", kind="note")]

    # ---- 10 ----
    s += [H1("11 - Risk &amp; circuit breakers")]
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
    s += [H1("12 - A day in the life")]
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
    s += [H1("13 - Go-live checklist &amp; quick reference")]
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
        ["/mm EURUSD buy|sell [auto]|off", "Market Maker IFVG model (watch / auto-enter)"],
        ["/test EURUSD long [0.05]  |  /pyramid EURUSD", "open now / add to a winner"],
        ["/sl EURUSD 1.1555  |  /be EURUSD", "move stop to price / break-even"],
        ["/trail EURUSD m15|m5|m1 st|it [pips]", "trail stop behind the latest intact swing"],
        ["/hold EURUSD  |  /release EURUSD", "run across the handover / undo"],
        ["/close EURUSD [leg]  |  /close all", "close position / one leg / flatten"],
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
