"""Render "The World in One Day" — a one-page news digest for 24 November 2026.

Draws a 1024x1024 poster with Pillow: a navy masthead, a lead story with a
drawn strait scene, three featured cards, and a 33-item world grid. All 40
stories cover events reported on 24 November 2026. Dots mark how solid each
report is: green CONFIRMED, gold REPORTED, red RUMORED.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "output/entry.png"

PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
GOLD = (201, 162, 39)
GOLD_LT = (217, 182, 74)
RED = (158, 43, 37)
BLUE = (29, 78, 137)
GREEN = (46, 125, 50)
PURPLE = (96, 62, 143)
MUTED = (107, 101, 88)
CARD = (255, 253, 247)
EDGE = (216, 210, 192)
SEA = (29, 53, 87)
SKY = (168, 196, 214)
HULL = (16, 24, 32)

CONF = GREEN
REP = GOLD
RUM = RED

CERT = {"CONFIRMED": CONF, "REPORTED": REP, "RUMORED": RUM}


def load(name, size):
    return ImageFont.truetype("fonts/" + name, size)


F_TITLE = load("PlayfairDisplay.ttf", 56)
F_LEAD = load("PlayfairDisplay.ttf", 44)
F_CARD = load("DejaVuSans-Bold.ttf", 16)
F_GRID = load("DejaVuSans-Bold.ttf", 11)
F_BODY = load("DejaVuSans.ttf", 15)
F_SMALL = load("DejaVuSans.ttf", 13)
F_DECK = load("DejaVuSans.ttf", 12)
F_TAG = load("DejaVuSans-Bold.ttf", 12)
F_MINI = load("DejaVuSans-Bold.ttf", 11)
F_FOOT = load("DejaVuSans.ttf", 11)
F_CAP = load("DejaVuSans-Bold.ttf", 11)


def wrap(draw, text, font, width):
    """Split text into lines that fit width."""
    lines = []
    cur = ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, font, width):
    """Shorten one line with an ellipsis so it fits width."""
    if draw.textlength(text, font=font) <= width:
        return text
    while text and draw.textlength(text + "…", font=font) > width:
        if " " in text:
            text = text.rsplit(" ", 1)[0]
        else:
            text = text[:-1]
    return text + "…" if text else "…"


def centre(draw, y, text, font, fill):
    x = (W - draw.textlength(text, font=font)) / 2
    draw.text((x, y), text, font=font, fill=fill)


LEAD_TAG = "LEAD STORY — THE STRAIT OF HORMUZ"
LEAD_HEAD = "HORMUZ ON THE BRINK"
LEAD_DECK = (
    "Iran says four tankers were struck by mines as the strait "
    "'closes day by day'. Trump warns ships that defy the US "
    "blockade will be sunk to the seabed."
)
LEAD_POINTS = [
    "IRGC says its navy targeted a container ship that switched "
    "off navigation near Khasab, Oman.",
    "Tehran lists seven demands; its FM says the strait can "
    "reopen in two hours if commitments are met.",
    "Rial slides ~5% in a day; Qatar mediates as Vance and "
    "Rubio meet Doha's prime minister.",
]

CARDS = [
    {
        "tag": "UKRAINE — WAR",
        "color": BLUE,
        "head": "Kyiv strikes Russian ships in the Gulf of Finland and off Libya",
        "deck": "Sparta II hit by drones; corvette Merkury claimed sunk — "
        "Libya says badly damaged.",
        "cert": "CONFIRMED",
    },
    {
        "tag": "VERDICT — TECH",
        "color": RED,
        "head": "US jury finds Huawei guilty of trade-secret theft",
        "deck": "Guilty on 10 of 12 counts, including bank fraud; cleared "
        "of racketeering. Appeal planned.",
        "cert": "CONFIRMED",
    },
    {
        "tag": "MARKETS",
        "color": GREEN,
        "head": "Dow tops 50,000 for the first time",
        "deck": "Dow closes at 50,019 while the Nasdaq drops 1.5% as chip "
        "stocks sell off.",
        "cert": "CONFIRMED",
    },
]

GRID = [
    ("Poland: fresh Russian airspace violation", "REPORTED"),
    ("S. Korea alerts Ulleungdo over Russian jets", "CONFIRMED"),
    ("NATO vows to defend against space threats", "CONFIRMED"),
    ("Zelensky urges four-party talks soon", "CONFIRMED"),
    ("Houthi drone hits Riyadh PIF Tower; 11 hurt", "CONFIRMED"),
    ("Saudi strike in Yemen: 25 killed or missing", "REPORTED"),
    ("Houthis 60 km from Aden; UK sanctions group", "REPORTED"),
    ("Israel kills Hamas security chief in Gaza", "CONFIRMED"),
    ("Gaza warns of meningitis epidemic", "CONFIRMED"),
    ("Libya's Haftar visits Turkey for first time", "CONFIRMED"),
    ("Iraq orders federal control of Kurdish oil", "CONFIRMED"),
    ("Gunmen take 25 hostage at Cartagena store", "CONFIRMED"),
    ("Car bomb in Villavicencio injures 23", "CONFIRMED"),
    ("'El Chapo Isidro' captured with US drone help", "CONFIRMED"),
    ("Turkish helicopter crashes; five killed", "CONFIRMED"),
    ("China sentences official to death for spying", "REPORTED"),
    ("Hasina plans return to Bangladesh 16 Dec", "CONFIRMED"),
    ("14 nations uphold ICJ ruling on Myanmar", "CONFIRMED"),
    ("UN chief urges global AI risk framework", "CONFIRMED"),
    ("Nvidia slides ~8% a day after 31% surge", "CONFIRMED"),
    ("Anthropic shares fall below $83 IPO price", "CONFIRMED"),
    ("Sanofi agrees $41bn takeover of Insmed", "CONFIRMED"),
    ("US consumer confidence jumps to 103.3", "CONFIRMED"),
    ("Oil hits three-month low as Hormuz eases", "CONFIRMED"),
    ("Nikkei jumps 3.9% as Hang Seng hits low", "CONFIRMED"),
    ("GTA VI is PlayStation's biggest launch ever", "CONFIRMED"),
    ("Tidal to ban fully AI-generated music", "CONFIRMED"),
    ("BepiColombo reaches Mercury orbit", "CONFIRMED"),
    ("First foreign astronaut named for Tiangong", "CONFIRMED"),
    ("US measles outbreak: 14 dead, ~6,000 cases", "REPORTED"),
    ("CAS hands Africa Cup title back to Senegal", "CONFIRMED"),
    ("Madrid rout PSV 5-1 in Champions League", "CONFIRMED"),
    ("Liverpool thrash Man Utd 4-0 in debut", "CONFIRMED"),
]


def draw_masthead(draw):
    draw.rectangle([0, 0, W, 116], fill=NAVY)
    centre(draw, 16, "THE WORLD IN ONE DAY", F_TITLE, (250, 247, 238))
    centre(
        draw,
        84,
        "TUESDAY, 24 NOVEMBER 2026  •  40 STORIES FROM AROUND THE WORLD",
        F_MINI,
        GOLD_LT,
    )
    draw.rectangle([0, 116, W, 119], fill=GOLD)


def draw_ship(draw, x, y, w, h, hull, boxes):
    """A simple cargo ship: hull trapezoid plus container boxes."""
    draw.polygon(
        [(x, y), (x + w, y), (x + w - 12, y + h), (x + 12, y + h)], fill=hull
    )
    bw = w // len(boxes)
    for i, color in enumerate(boxes):
        draw.rectangle(
            [x + 8 + i * bw, y - 16, x + 8 + (i + 1) * bw - 4, y - 2],
            fill=color,
        )


def draw_mine(draw, cx, cy):
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(10, 10, 10))
    for k in range(8):
        ang = math.pi * k / 4
        x2 = cx + 12 * math.cos(ang)
        y2 = cy + 12 * math.sin(ang)
        draw.line([(cx, cy), (x2, y2)], fill=(10, 10, 10), width=2)


def draw_strait(draw, x0, y0, x1, y1):
    """Stylised Strait of Hormuz: sky, sea, two ships, mines, warning."""
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=SEA)
    draw.rounded_rectangle([x0, y0, x1, y0 + 70], radius=6, fill=SKY)
    draw.rectangle([x0, y0 + 64, x1, y0 + 70], fill=SKY)
    draw.ellipse([x1 - 62, y0 + 14, x1 - 30, y0 + 46], fill=GOLD_LT)
    draw.line([(x0, y0 + 70), (x1, y0 + 70)], fill=(250, 247, 238), width=2)
    for wy, ww in [(y0 + 110, 2), (y0 + 150, 2), (y0 + 195, 2)]:
        pts = []
        for px in range(x0 + 12, x1 - 8, 8):
            pts.append((px, wy + 4 * math.sin(px / 22.0)))
        draw.line(pts, fill=(210, 225, 240), width=ww)
    draw_ship(
        draw, x0 + 30, y0 + 92, 110, 16, (58, 78, 102),
        [(140, 140, 140), (180, 180, 180)],
    )
    draw_ship(
        draw, x0 + 52, y0 + 168, 220, 30, HULL,
        [RED, GOLD, BLUE, (200, 200, 200)],
    )
    draw_mine(draw, x0 + 268, y0 + 132)
    draw_mine(draw, x0 + 296, y0 + 158)
    draw_mine(draw, x0 + 40, y0 + 138)
    tri = [(x0 + 210, y0 + 118), (x0 + 226, y0 + 144), (x0 + 194, y0 + 144)]
    draw.polygon(tri, fill=GOLD)
    draw.text((x0 + 214, y0 + 124), "!", font=F_MINI, fill=INK)
    draw.text((x0 + 12, y1 - 26), "THE STRAIT OF HORMUZ", font=F_CAP, fill=(250, 247, 238))


def draw_lead(draw):
    draw.rectangle([28, 132, 996, 412], fill=CARD, outline=EDGE, width=1)
    draw.rectangle([28, 132, 36, 412], fill=RED)
    draw.text((52, 146), LEAD_TAG, font=F_TAG, fill=RED)
    draw.text((52, 168), LEAD_HEAD, font=F_LEAD, fill=INK)
    y = 226
    for line in wrap(draw, LEAD_DECK, F_BODY, 580):
        draw.text((52, y), line, font=F_BODY, fill=INK)
        y += 20
    y = 292
    for point in LEAD_POINTS:
        draw.rectangle([52, y + 4, 60, y + 12], fill=RED)
        for line in wrap(draw, point, F_SMALL, 556)[:2]:
            draw.text((68, y), line, font=F_SMALL, fill=INK)
            y += 17
        y += 6
    draw_strait(draw, 648, 148, 980, 396)


def draw_cards(draw):
    draw.text((28, 434), "TOP STORIES", font=F_TAG, fill=INK)
    draw.rectangle([28, 452, 168, 455], fill=GOLD)
    for i, card in enumerate(CARDS):
        x = 28 + i * 326
        draw.rectangle([x, 460, x + 314, 612], fill=CARD, outline=EDGE, width=1)
        draw.rectangle([x, 460, x + 314, 464], fill=card["color"])
        draw.text((x + 14, 474), card["tag"], font=F_MINI, fill=card["color"])
        y = 496
        for line in wrap(draw, card["head"], F_CARD, 286)[:3]:
            draw.text((x + 14, y), line, font=F_CARD, fill=INK)
            y += 20
        y = 558
        for line in wrap(draw, card["deck"], F_DECK, 286)[:2]:
            draw.text((x + 14, y), line, font=F_DECK, fill=MUTED)
            y += 15
        draw.ellipse(
            [x + 14, 596, x + 22, 604], fill=CERT[card["cert"]]
        )
        draw.text((x + 28, 592), card["cert"], font=F_MINI, fill=MUTED)


def draw_grid(draw):
    draw.text((28, 622), "THE REST OF THE WORLD", font=F_TAG, fill=INK)
    draw.line([(28, 640), (996, 640)], fill=EDGE, width=1)
    for row in range(11):
        y = 650 + row * 28
        for col in range(3):
            idx = row * 3 + col
            if idx >= len(GRID):
                continue
            head, cert = GRID[idx]
            x = 28 + col * 328
            draw.ellipse([x + 4, y + 8, x + 12, y + 16], fill=CERT[cert])
            text = fit(draw, head, F_GRID, 292)
            draw.text((x + 18, y + 5), text, font=F_GRID, fill=INK)


def draw_footer(draw):
    draw.line([(28, 972), (996, 972)], fill=EDGE, width=1)
    parts = [
        (CONF, "● "),
        (INK, "CONFIRMED    "),
        (REP, "● "),
        (INK, "REPORTED    "),
        (RUM, "● "),
        (INK, "RUMORED"),
    ]
    x = 28
    for color, text in parts:
        draw.text((x, 982), text, font=F_FOOT, fill=color)
        x += draw.textlength(text, font=F_FOOT)
    right = "40 STORIES"
    draw.text(
        (996 - draw.textlength(right, font=F_MINI), 982),
        right,
        font=F_MINI,
        fill=INK,
    )
    centre(
        draw,
        1000,
        "Sources: Reuters • AP • BBC • AFP — Rendered by an AI agent with Pillow",
        F_FOOT,
        MUTED,
    )


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_lead(draw)
    draw_cards(draw)
    draw_grid(draw)
    draw_footer(draw)
    img.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
