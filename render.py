#!/usr/bin/env python3
"""Render 'The World in One Day' — a one-page newspaper front page
summing up world news for Tuesday, 24 November 2026.

Draws 40 stories (23-24 Nov 2026) on a 1024x1024 sheet with Pillow
and the bundled fonts. Run it from this directory:
    python3 render.py
It writes output/entry.png.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "output", "entry.png")

W, H = 1024, 1024
MARGIN = 32
CW = W - 2 * MARGIN

PAPER = (247, 243, 232)
INK = (26, 26, 26)
SOFT = (74, 72, 66)
GRAY = (112, 108, 98)
RULE = (198, 190, 172)
RED = (166, 30, 30)
BLUE = (31, 58, 95)
GREEN = (58, 104, 66)
TEAL = (38, 106, 106)
RUST = (168, 88, 28)
PLUM = (108, 68, 138)
TINT = (238, 232, 214)
TINT_BLUE = (229, 235, 243)

CAT_COLORS = {
    "Geopolitics": RED,
    "War": RED,
    "US Politics": RED,
    "World Politics": RED,
    "Diplomacy": BLUE,
    "Law": BLUE,
    "Technology": BLUE,
    "AI": BLUE,
    "AI/Science": TEAL,
    "AI/Policy": BLUE,
    "Tech/Law": BLUE,
    "Economy": GREEN,
    "Business": GREEN,
    "Climate": GREEN,
    "Science": TEAL,
    "Space": TEAL,
    "Health": TEAL,
    "Health/Conflict": TEAL,
    "Disaster": RUST,
    "Sport": PLUM,
    "Entertainment": PLUM,
    "Latin America": RUST,
    "Education/AI": BLUE,
}


def load_font(name, size):
    path = os.path.join(FONTS, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def font_playfair(size):
    return load_font("PlayfairDisplay.ttf", size)


def font_inter(size):
    return load_font("Inter.ttf", size)


def font_franklin(size):
    return load_font("LibreFranklin.ttf", size)


def font_bold(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def wrap_text(draw, text, font, max_width):
    """Split text into lines that fit max_width. Returns a list."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, font, max_width, fill, leading=None):
    """Draw wrapped text starting at (x, y). Returns the y after it."""
    if leading is None:
        leading = int(font.size * 1.22)
    for line in wrap_text(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def text_height(draw, text, font, max_width, leading=None):
    if leading is None:
        leading = int(font.size * 1.22)
    return len(wrap_text(draw, text, font, max_width)) * leading


def kicker_color(category):
    return CAT_COLORS.get(category, GRAY)


STORIES = [
    {
        "title": "Tankers struck by mines as US-Iran standoff deepens",
        "summary": "Tehran vows to defy a US naval blockade after three oil tankers are hit by mines in the Strait of Hormuz.",
        "category": "Geopolitics",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Climate talks collapse over fossil fuels",
        "summary": "UN climate talks in Antalya end with no deal on phasing out fossil fuels.",
        "category": "Climate",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Ukraine strikes Kerch Bridge again",
        "summary": "Kyiv hits the Kerch Bridge as Russia fires 160+ missiles at Ukraine's grid.",
        "category": "War",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Ukraine says it sank a Russian corvette off Libya",
        "summary": "Kyiv says its sea drones sank the Russian corvette Mercury off Benghazi.",
        "category": "War",
        "date": "23 Nov",
        "certainty": "REPORTED",
    },
    {
        "title": "Israeli strike kills Hamas security chief",
        "summary": "An Israeli airstrike in Gaza kills Hamas internal security director Naeem Abu Nahel and six others.",
        "category": "War",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "NATO sends AWACS to Poland after Russian missiles land",
        "summary": "NATO deploys surveillance aircraft to Poland after three Russian cruise missiles land on Polish soil.",
        "category": "Geopolitics",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "EU moves to cut 60 Russian banks from SWIFT",
        "summary": "The European Commission proposes its 22nd sanctions package, cutting about 60 Russian banks from SWIFT.",
        "category": "Geopolitics",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Russia warns Estonia is nearing open war",
        "summary": "Moscow accuses Estonia of hostile acts 'on the verge of triggering open war' after border crossing closures.",
        "category": "Geopolitics",
        "date": "24 Nov",
        "certainty": "REPORTED",
    },
    {
        "title": "Ukraine-Russia talks end without breakthrough",
        "summary": "US-mediated trilateral talks in Abu Dhabi end with no major progress as Moscow rejects territorial concessions.",
        "category": "Geopolitics",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Democrats win biggest House majority since 1992",
        "summary": "Democrats take at least 258 House seats and 56 in the Senate, their largest House majority since 1992.",
        "category": "US Politics",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Nvidia brings Jensen Huang back as CEO",
        "summary": "Nvidia reinstates Jensen Huang as chief executive after his abrupt resignation, with Trump claiming he persuaded the board.",
        "category": "Technology",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Trump orders fast-track federal executions",
        "summary": "Trump orders the Justice Department to speed up federal death sentences and fight California's commutations.",
        "category": "US Politics",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Fourteen nations back ICJ Rohingya genocide ruling",
        "summary": "Fourteen countries including the UK, Spain, Canada and Australia endorse the ICJ ruling that Myanmar committed genocide against the Rohingya.",
        "category": "Law",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Tajikistan starts withdrawal from ICC during Putin visit",
        "summary": "Tajikistan begins a one-year withdrawal from the International Criminal Court during President Putin's visit.",
        "category": "World Politics",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Trump and Pashinyan launch TRIPP corridor",
        "summary": "Trump and Armenia's PM announce the TRIPP transit corridor, a new route for peace and prosperity in the South Caucasus.",
        "category": "Diplomacy",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Stocks surge as Nvidia jumps 31.5%",
        "summary": "US stocks soar, Nasdaq up 6.51% and the S&P 500 up 4.73%, led by Nvidia's 31.5% jump on Huang's return.",
        "category": "Economy",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Sanofi to buy Insmed for $41 billion",
        "summary": "Sanofi agrees to acquire biotech firm Insmed for $175 a share in cash, valuing the deal at $41 billion.",
        "category": "Business",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "DR Congo reimposes cobalt export ban",
        "summary": "The world's top cobalt producer suspends all cobalt exports from 30 November to tackle oversupply.",
        "category": "Economy",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Anthropic publishes Claude-written VP versus VNP proof",
        "summary": "Anthropic releases a 70-page paper it says Claude wrote entirely, claiming a proof that VP is not equal to VNP, still unverified.",
        "category": "AI/Science",
        "date": "24 Nov",
        "certainty": "RUMORED",
    },
    {
        "title": "Gemini agents cut quantum algorithm cost 290-fold",
        "summary": "Google DeepMind's Gemini agents find faster quantum algorithms for fusion and drug design, cutting costs up to 290-fold.",
        "category": "AI/Science",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "OpenAI delays open-source reasoning model",
        "summary": "OpenAI indefinitely delays its open-source AI model as CEO Sam Altman says more safety testing is needed.",
        "category": "AI",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Amazon to buy Decart's AI optimization tech",
        "summary": "Amazon agrees to buy AI optimization technology from Decart and hire its founders and engineering team.",
        "category": "Technology",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "OpenAI and Cisco launch Shirudo security runtime",
        "summary": "OpenAI and Cisco launch Shirudo, an open-source Linux runtime that protects systems while security patches apply.",
        "category": "Technology",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "UN chief urges AI risk framework within a year",
        "summary": "Secretary-General Guterres urges member states to build a multilateral framework for managing AI risks within a year.",
        "category": "AI/Policy",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Oregon and Virginia sue SpaceX over Grok images",
        "summary": "State attorneys general sue SpaceX over alleged child abuse images generated by the Grok chatbot.",
        "category": "Tech/Law",
        "date": "24 Nov",
        "certainty": "REPORTED",
    },
    {
        "title": "China opens Tiangong to first foreign astronaut",
        "summary": "China opens its Tiangong space station to its first foreign astronaut, Pakistan's Zeeshan Ali, on the Shenzhou-24 mission.",
        "category": "Space",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Space-tested coating keeps medicines stable in orbit",
        "summary": "A chitosan coating tested on a rocket keeps liquid medicine stable during launch and weightlessness.",
        "category": "Science",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Pennsylvania measles outbreak claims ninth life",
        "summary": "Pennsylvania records a ninth death from a measles outbreak now spread across 46 counties.",
        "category": "Health",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "FDA approves Roche breast cancer drug",
        "summary": "The FDA approves Roche's Wilserdly (giredestrant) for early-stage ER-positive breast cancer.",
        "category": "Health",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Deadly floods in China force 500,000 to flee",
        "summary": "Floods across central and southern China force more than 500,000 evacuations and kill over 100 people.",
        "category": "Disaster",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Florida river breaks 1953 flood record",
        "summary": "The St. Johns River hits a record 18.76 feet, breaking the 1953 mark, as DeSantis seeks a second federal disaster declaration.",
        "category": "Disaster",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Magnitude 5.6 earthquake strikes Nepal",
        "summary": "A 5.6-magnitude quake shakes Koshi Province, Nepal, near the Chinese border.",
        "category": "Disaster",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Factory blaze in Indonesia kills 24",
        "summary": "A factory fire in Indonesia kills 24 people, with dozens still sought by rescuers.",
        "category": "Disaster",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Commanders stun Bengals 22-20 on final kick",
        "summary": "Washington beats Cincinnati 22-20 on a last-play field goal in Monday Night Football.",
        "category": "Sport",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "49ers thrash Vikings 35-10 in Mexico City",
        "summary": "San Francisco crushes Minnesota 35-10 in an NFL game in Mexico City, with Brock Purdy throwing three touchdowns.",
        "category": "Sport",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Miley Cyrus marries drummer Maxx Morando",
        "summary": "Pop star Miley Cyrus marries drummer Maxx Morando in a private ceremony in California.",
        "category": "Entertainment",
        "date": "23 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Mexico to try 'El Chapo Isidro' despite US bid",
        "summary": "Mexico will try drug lord Fausto Meza Flores itself on drug and weapons charges despite a US extradition request.",
        "category": "Latin America",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Super Bowl heads to IMAX theaters",
        "summary": "Disney, ESPN and the NFL partner with IMAX to screen the Super Bowl in cinemas for the first time.",
        "category": "Entertainment",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "South Korea offers $375,000 to catch AI exam cheats",
        "summary": "Seoul offers rewards of up to $375,000 to catch students using AI to cheat on the CSAT college exam.",
        "category": "Education/AI",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
    {
        "title": "Fighting in DR Congo traps Ebola responders",
        "summary": "Heavy fighting near a hospital in Ituri Province traps a WHO Ebola response team for over 24 hours.",
        "category": "Health/Conflict",
        "date": "24 Nov",
        "certainty": "CONFIRMED",
    },
]


def draw_masthead(draw):
    title = "THE WORLD IN ONE DAY"
    f_title = font_playfair(58)
    tw = draw.textlength(title, font=f_title)
    draw.text(((W - tw) / 2, 30), title, font=f_title, fill=INK)
    sub = "Tuesday, 24 November 2026  ·  40 stories from around the world"
    f_sub = font_inter(18)
    sw = draw.textlength(sub, font=f_sub)
    draw.text(((W - sw) / 2, 100), sub, font=f_sub, fill=SOFT)
    draw.line([(MARGIN, 126), (W - MARGIN, 126)], fill=INK, width=2)
    draw.line([(MARGIN, 131), (W - MARGIN, 131)], fill=INK, width=1)


def draw_kicker(draw, x, y, story, size=14):
    cat = story["category"].upper()
    tag = f"{cat}  ·  {story['date']}  ·  {story['certainty']}"
    draw.text((x, y), tag, font=font_bold(size), fill=kicker_color(story["category"]))
    return y + size + 6


def draw_lead(draw, story, y0):
    x0 = MARGIN
    x1 = W - MARGIN
    inner_w = x1 - 28 - (x0 + 28)
    kicker_h = 15 + 6
    title_h = text_height(draw, story["title"], font_playfair(38), inner_w, leading=44)
    summary_h = text_height(draw, story["summary"], font_inter(18), inner_w, leading=22)
    panel_h = 14 + kicker_h + 2 + title_h + 6 + summary_h + 16
    y1 = y0 + panel_h
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=TINT)
    x = x0 + 28
    y = y0 + 14
    y = draw_kicker(draw, x, y, story, size=15)
    y = draw_wrapped(draw, x, y + 2, story["title"], font_playfair(38),
                     inner_w, INK, leading=44)
    draw_wrapped(draw, x, y + 6, story["summary"], font_inter(18),
                 inner_w, SOFT, leading=22)
    return y1


def draw_medium(draw, stories, y0):
    gutter = 24
    col_w = (CW - 2 * gutter) // 3
    for i, story in enumerate(stories):
        x = MARGIN + i * (col_w + gutter)
        if i > 0:
            draw.line([(x - gutter // 2, y0), (x - gutter // 2, y0 + 122)],
                      fill=RULE, width=1)
        y = draw_kicker(draw, x, y0, story, size=12)
        y = draw_wrapped(draw, x, y + 2, story["title"], font_playfair(21),
                         col_w, INK, leading=25)
        draw_wrapped(draw, x, y + 4, story["summary"], font_inter(14),
                     col_w, SOFT, leading=18)
    return y0 + 122


def draw_section_header(draw, y):
    label = "THE REST OF THE WORLD"
    f = font_bold(14)
    draw.text((MARGIN, y), label, font=f, fill=INK)
    tw = draw.textlength(label, font=f)
    draw.line([(MARGIN + tw + 12, y + 8), (W - MARGIN, y + 8)], fill=RULE, width=1)
    return y + 26


def draw_grid(draw, stories, y0, row_h=54):
    cols = 4
    gutter_x = 16
    col_w = (CW - (cols - 1) * gutter_x) // cols
    for idx, story in enumerate(stories):
        row, col = divmod(idx, cols)
        x = MARGIN + col * (col_w + gutter_x)
        y = y0 + row * row_h
        if col > 0:
            draw.line([(x - gutter_x // 2, y + 2), (x - gutter_x // 2, y + row_h - 6)],
                      fill=RULE, width=1)
        y = draw_kicker(draw, x, y, story, size=10)
        draw_wrapped(draw, x, y + 1, story["title"], font_inter(13),
                     col_w, INK, leading=16)


def draw_footer(draw, y):
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)
    note = "Compiled from public wires  ·  Tuesday 24 November 2026  ·  40 stories"
    f = font_inter(13)
    tw = draw.textlength(note, font=f)
    draw.text(((W - tw) / 2, y + 8), note, font=f, fill=GRAY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    y = draw_lead(draw, STORIES[0], 144)
    y = draw_medium(draw, STORIES[1:4], y + 12)
    y = draw_section_header(draw, y + 12)
    rows = (len(STORIES) - 4 + 3) // 4
    row_h = max(48, (968 - y) // rows)
    draw_grid(draw, STORIES[4:], y, row_h)
    draw_footer(draw, 978)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes, {len(STORIES)} stories)")


if __name__ == "__main__":
    build()
