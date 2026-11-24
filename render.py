#!/usr/bin/env python3
"""
news-image-20261124 — v1 renderer (Pillow).

40 stories for Tuesday 24 November 2026 (UTC): Nvidia brings Jensen
Huang back, Zelenskyy seeks four-way talks "tomorrow", Iran vows to
defy the US blockade — each story tagged CONFIRMED / REPORTED /
CLAIM / FORECAST / ONGOING. Same craft as the 22 Nov v7: Playfair
Display headlines (serif), Inter body, Libre Franklin kickers,
richer scene-like illustrations, and a dot-matrix world map with
numbered pins. Date discipline: every story's event or report is
dated Mon 23 or Tue 24 Nov 2026; older stories live only in the
DATE CHECK exclusions.

Run:  python3 render.py
Writes: output/entry.png (1024x1024, <= 1 MiB)
"""
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"

# ---------------------------------------------------------------- palette
PAPER = (247, 240, 222)
INK = (22, 22, 22)
NAVY = (30, 42, 68)
RED = (168, 30, 35)
RED_DK = (140, 22, 28)
GRAY = (107, 101, 88)
RULE = (22, 22, 22)
WHITE = (255, 255, 255)

W, H = 1024, 1024

# ---------------------------------------------------------------- fonts
def _load(name, size, weight=None, fallbacks=()):
    for cand in [FONTS / name, Path.home() / ".fonts" / name, *fallbacks]:
        if cand.is_file():
            f = ImageFont.truetype(str(cand), size)
            if weight is not None:
                try:
                    f.set_variation_by_axes([weight])
                except Exception:
                    pass
            return f
    raise SystemExit(f"missing font: {name}")


def playfair(size, weight=800):
    return _load("PlayfairDisplay.ttf", size, weight,
                 [FONTS / "DejaVuSerif-Bold.ttf"])


def playfair_italic(size, weight=500):
    return _load("PlayfairDisplay-Italic.ttf", size, weight,
                 [FONTS / "DejaVuSerif-Bold.ttf"])


def inter(size, weight=400):
    return _load("Inter.ttf", size, weight, [FONTS / "DejaVuSans.ttf"])


def franklin(size, weight=700):
    return _load("LibreFranklin.ttf", size, weight,
                 [FONTS / "DejaVuSans-Bold.ttf"])


# ---------------------------------------------------------------- text utils
def text_w(font, s):
    return font.getlength(s)


def wrap(text, font, max_w):
    """Greedy word wrap to a pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if text_w(font, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, font, max_w, max_lines):
    """Wrap; if it overflows max_lines, drop words from the end with …"""
    lines = wrap(text, font, max_w)
    if len(lines) <= max_lines:
        return lines
    flat = " ".join(lines)
    # binary-ish trim: keep removing last word until it fits
    words = flat.split(" ")
    while len(words) > 1:
        words.pop()
        trial = wrap(" ".join(words) + " …", font, max_w)
        if len(trial) <= max_lines:
            return trial
    return wrap(words[0] + " …", font, max_w)


def draw_wrapped(d, x, y, text, font, fill, max_w, max_lines, lh):
    lines = fit_lines(text, font, max_w, max_lines)
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def autofit_font(loader, text, start_size, max_w, min_size=7, **kw):
    """Largest size (stepping down 0.5) whose text fits max_w."""
    size = start_size
    while size > min_size:
        f = loader(int(round(size)), **kw)
        if text_w(f, text) <= max_w:
            return f
        size -= 0.5
    return loader(int(round(min_size)), **kw)


# ---------------------------------------------------------------- drawing utils
def vgrad(d, box, c_top, c_bot):
    """Vertical gradient fill of box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(c_top[j] + (c_bot[j] - c_top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def stars(d, box, n, seed, color=(255, 255, 255)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = rnd.randint(x0 + 2, x1 - 2)
        y = rnd.randint(y0 + 2, y1 - 2)
        r = rnd.choice([1, 1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def dashed_arc(d, box, a0, a1, fill, width=2, dash=7, gap=5):
    """Arc drawn as dashes (degrees)."""
    span = a1 - a0
    steps = max(1, int(abs(span) / 2))
    on = True
    run = 0
    prev = None
    for i in range(steps + 1):
        a = math.radians(a0 + span * i / steps)
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        rx = (box[2] - box[0]) / 2
        ry = (box[3] - box[1]) / 2
        pt = (cx + rx * math.cos(a), cy + ry * math.sin(a))
        if prev is not None and on:
            d.line([prev, pt], fill=fill, width=width)
        prev = pt
        run += 1
        if on and run >= dash:
            on, run = False, 0
        elif not on and run >= gap:
            on, run = True, 0


def skyline(d, x0, y_base, x1, seed, color, win=(255, 214, 120), hmax=52):
    """Dark building silhouettes with lit windows along y_base."""
    rnd = random.Random(seed)
    x = x0
    while x < x1 - 6:
        bw = rnd.randint(10, 26)
        bh = rnd.randint(14, hmax)
        d.rectangle([x, y_base - bh, x + bw, y_base], fill=color)
        for wy in range(y_base - bh + 4, y_base - 3, 7):
            for wx in range(x + 3, x + bw - 3, 7):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=win)
        x += bw + rnd.randint(1, 4)


def flames(d, x, y_base, widths, color1=(255, 140, 30), color2=(255, 210, 60)):
    """Row of flame triangles at (x, y_base). widths: list of (w, h)."""
    cx = x
    for w, h in widths:
        d.polygon([(cx, y_base), (cx + w / 2, y_base - h),
                   (cx + w, y_base)], fill=color1)
        d.polygon([(cx + w * 0.25, y_base), (cx + w / 2, y_base - h * 0.6),
                   (cx + w * 0.75, y_base)], fill=color2)
        cx += w + 3


def waves(d, box, color=(120, 180, 220), n=4):
    x0, y0, x1, y1 = box
    for i in range(n):
        y = y0 + (y1 - y0) * (i + 1) / (n + 1)
        d.arc([x0, y - 6, x1, y + 6], 200, 340, fill=color, width=2)


def globe(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(66, 135, 200))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
    # stylised continents
    d.ellipse([cx - r * 0.55, cy - r * 0.45, cx - r * 0.05, cy + r * 0.05],
              fill=(90, 170, 90))
    d.ellipse([cx + r * 0.1, cy + r * 0.1, cx + r * 0.6, cy + r * 0.55],
              fill=(90, 170, 90))
    d.ellipse([cx - r * 0.2, cy - r * 0.8, cx + r * 0.35, cy - r * 0.35],
              fill=(120, 190, 100))
    # stand
    d.rectangle([cx - 2, cy + r, cx + 2, cy + r + 6], fill=(120, 90, 60))
    d.rectangle([cx - 10, cy + r + 6, cx + 10, cy + r + 8], fill=(120, 90, 60))


def kicker_strip(d, x, y, text, font=None):
    """Small white-on-red label at the top-left of an illustration."""
    f = font or franklin(10, 700)
    tw = text_w(f, text)
    d.rectangle([x, y, x + tw + 12, y + 17], fill=RED)
    d.text((x + 6, y + 3), text, font=f, fill=WHITE)
    return tw + 12


def caption_chip(d, x, y, text):
    f = inter(11, 700)
    tw = text_w(f, text)
    d.rectangle([x, y, x + tw + 10, y + 17], fill=WHITE, outline=INK, width=1)
    d.text((x + 5, y + 3), text, font=f, fill=INK)


# ---------------------------------------------------------------- lead scenes
def lead_cop31(d, x, y, w, h):
    """COP31: day sky, globe, negotiation table, clock."""
    vgrad(d, (x, y, x + w, y + h), (168, 205, 235), (232, 222, 190))
    # sun
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=(255, 214, 110))
    # globe on the left
    globe(d, x + 34, y + 46, 24)
    # negotiation table
    ty = y + h - 26
    d.rectangle([x + 78, ty, x + w - 70, ty + 7], fill=(122, 82, 52))
    d.rectangle([x + 84, ty + 7, x + 88, y + h - 2], fill=(96, 64, 40))
    d.rectangle([x + w - 76, ty + 7, x + w - 72, y + h - 2], fill=(96, 64, 40))
    # delegates: coloured heads + flags
    cols = [(200, 60, 60), (60, 120, 200), (60, 160, 90), (220, 160, 40),
            (150, 80, 180)]
    for i, c in enumerate(cols):
        dx = x + 96 + i * 34
        d.ellipse([dx, ty - 16, dx + 12, ty - 4], fill=(232, 196, 160))
        d.polygon([(dx + 6, ty - 4), (dx - 4, ty + 2), (dx + 16, ty + 2)],
                  fill=c)
        d.line([dx + 6, ty - 26, dx + 6, ty - 16], fill=(80, 80, 80), width=1)
        d.polygon([(dx + 6, ty - 26), (dx + 16, ty - 23), (dx + 6, ty - 20)],
                  fill=c)
    # papers on the table
    d.rectangle([x + 150, ty - 2, x + 178, ty + 4], fill=WHITE)
    d.rectangle([x + 196, ty - 2, x + 224, ty + 4], fill=WHITE)
    # clock (deadline)
    ccx, ccy, cr = x + w - 34, y + 62, 17
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=WHITE,
              outline=INK, width=2)
    d.line([ccx, ccy, ccx, ccy - 11], fill=INK, width=2)
    d.line([ccx, ccy, ccx + 8, ccy], fill=INK, width=2)
    d.ellipse([ccx - 2, ccy - 2, ccx + 2, ccy + 2], fill=RED)


def lead_ukraine(d, x, y, w, h):
    """Ukraine barrage: night sky, stars, skyline, missile arcs."""
    vgrad(d, (x, y, x + w, y + h), (16, 22, 52), (44, 52, 96))
    stars(d, (x, y, x + w, y + int(h * 0.55)), 26, seed=7)
    # moon
    d.ellipse([x + w - 48, y + 10, x + w - 22, y + 36], fill=(240, 232, 200))
    # missile arcs with glowing heads
    dashed_arc(d, (x + 20, y + 8, x + 200, y + 70), 200, 330,
               (255, 170, 60), width=2)
    d.ellipse([x + 176, y + 48, x + 184, y + 56], fill=(255, 220, 120))
    dashed_arc(d, (x + 130, y + 2, x + 300, y + 44), 210, 320,
               (255, 120, 60), width=2)
    d.ellipse([x + 282, y + 22, x + 290, y + 30], fill=(255, 200, 100))
    # skyline
    skyline(d, x + 4, y + h - 2, x + w - 4, seed=11,
            color=(10, 14, 34), hmax=48)
    # explosions over the city
    flames(d, x + 60, y + h - 2, [(16, 26), (12, 18)])
    flames(d, x + 250, y + h - 2, [(14, 22)])


def lead_bahrain(d, x, y, w, h):
    """Bahrain: dusk sky, sea, burning ship, radar dome."""
    vgrad(d, (x, y, x + w, y + h), (196, 84, 52), (48, 52, 92))
    # low sun
    d.ellipse([x + w - 62, y + 12, x + w - 26, y + 48], fill=(255, 190, 90))
    # radar dome (Patriot) on the left
    d.rectangle([x + 14, y + 52, x + 22, y + 78], fill=(210, 210, 205))
    d.pieslice([x + 2, y + 30, x + 34, y + 62], 180, 360, fill=(240, 240, 235))
    d.line([x + 18, y + 34, x + 34, y + 22], fill=(240, 240, 235), width=2)
    # sea
    d.rectangle([x, y + 78, x + w, y + h], fill=(24, 40, 74))
    waves(d, (x, y + 80, x + w, y + h), color=(90, 140, 200), n=3)
    # ship silhouette with smoke and fire
    sx, sy = x + 120, y + 82
    d.polygon([(sx, sy), (sx + 150, sy), (sx + 138, sy + 16),
               (sx + 12, sy + 16)], fill=(18, 18, 22))
    d.rectangle([sx + 34, sy - 14, sx + 78, sy], fill=(30, 30, 36))
    d.rectangle([sx + 96, sy - 22, sx + 106, sy], fill=(40, 40, 46))
    for i, (ox, oy, r) in enumerate([(0, -30, 7), (8, -40, 9), (18, -50, 11)]):
        d.ellipse([sx + 96 + ox - r, sy + oy - r, sx + 96 + ox + r,
                   sy + oy + r], fill=(60, 60, 66))
    flames(d, sx + 44, sy - 1, [(16, 24), (12, 16)])
    flames(d, sx + 108, sy - 1, [(14, 20)])


def lead_nvidia(d, x, y, w, h):
    """Nvidia: dark boardroom green, big AI chip, rising chart."""
    vgrad(d, (x, y, x + w, y + h), (18, 52, 34), (8, 26, 18))
    # rising chart
    pts = [(x + 10, y + h - 22), (x + 60, y + h - 44), (x + 110, y + h - 34),
           (x + 160, y + h - 58), (x + 210, y + h - 70), (x + 260, y + h - 82)]
    d.line(pts, fill=(110, 240, 150), width=3, joint="curve")
    for px, py in pts[1:]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(140, 250, 170))
    # big chip, centre-left
    d.rectangle([x + 96, y + 14, x + 216, y + h - 16], fill=(30, 140, 70),
                outline=(20, 100, 50), width=2)
    d.rectangle([x + 116, y + 26, x + 196, y + h - 28], fill=(20, 110, 55))
    d.text((x + 132, y + 30), "AI", font=franklin(26, 700), fill=WHITE)
    # chip pins
    for i in range(5):
        d.line([(x + 110 + i * 22, y + 14), (x + 110 + i * 22, y + 6)],
               fill=(200, 200, 190), width=2)
        d.line([(x + 110 + i * 22, y + h - 16), (x + 110 + i * 22, y + h - 8)],
               fill=(200, 200, 190), width=2)
    # gold coin (regained value)
    cx, cy, r = x + w - 44, y + 26, 18
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 200, 60),
              outline=(180, 130, 20), width=2)
    d.text((cx - 6, cy - 12), "$", font=inter(18, 700), fill=(140, 90, 0))


def lead_talks(d, x, y, w, h):
    """Four-way talks: day sky, table, four flags, four delegates."""
    vgrad(d, (x, y, x + w, y + h), (168, 205, 235), (232, 222, 190))
    # sun
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=(255, 214, 110))
    # negotiation table
    ty = y + h - 26
    d.rectangle([x + 30, ty, x + w - 30, ty + 7], fill=(122, 82, 52))
    d.rectangle([x + 36, ty + 7, x + 40, y + h - 2], fill=(96, 64, 40))
    d.rectangle([x + w - 40, ty + 7, x + w - 36, y + h - 2], fill=(96, 64, 40))
    # four flags above the table: UA, RU, US, EU
    flags = [
        [(0, 90, 200), (255, 215, 0)],
        [(255, 255, 255), (0, 60, 160), (220, 40, 40)],
        [(180, 30, 40), (255, 255, 255), (30, 50, 140)],
        [(0, 40, 120), (255, 215, 0)],
    ]
    for i, bands in enumerate(flags):
        fx = x + 52 + i * 66
        fy = y + 12
        bh = 22 // len(bands)
        for j, c in enumerate(bands):
            d.rectangle([fx, fy + j * bh, fx + 34, fy + (j + 1) * bh], fill=c)
        d.rectangle([fx, fy, fx + 34, fy + 22], outline=(60, 60, 60), width=1)
        d.line([fx + 2, fy + 22, fx + 2, ty - 14], fill=(80, 80, 80), width=1)
    # four delegates
    cols = [(0, 90, 200), (200, 60, 60), (30, 50, 140), (0, 40, 120)]
    for i, c in enumerate(cols):
        dx = x + 62 + i * 66
        d.ellipse([dx, ty - 16, dx + 12, ty - 4], fill=(232, 196, 160))
        d.polygon([(dx + 6, ty - 4), (dx - 4, ty + 2), (dx + 16, ty + 2)],
                  fill=c)
    # papers on the table
    d.rectangle([x + 130, ty - 2, x + 158, ty + 4], fill=WHITE)
    d.rectangle([x + 176, ty - 2, x + 204, ty + 4], fill=WHITE)


def lead_iran(d, x, y, w, h):
    """Iran blockade: dusk strait, tanker, mine buoy, patrol boat."""
    vgrad(d, (x, y, x + w, y + h), (210, 110, 60), (52, 56, 96))
    # low sun
    d.ellipse([x + w - 62, y + 12, x + w - 26, y + 48], fill=(255, 190, 90))
    # sea
    d.rectangle([x, y + 78, x + w, y + h], fill=(24, 40, 74))
    waves(d, (x, y + 80, x + w, y + h), color=(90, 140, 200), n=3)
    # tanker silhouette with containers
    sx, sy = x + 70, y + 84
    d.polygon([(sx, sy), (sx + 170, sy), (sx + 158, sy + 14),
               (sx + 12, sy + 14)], fill=(16, 16, 20))
    for i, c in enumerate([(200, 60, 50), (60, 120, 200), (220, 160, 40)]):
        d.rectangle([sx + 22 + i * 44, sy - 12, sx + 58 + i * 44, sy],
                    fill=c)
    d.rectangle([sx + 158, sy - 20, sx + 168, sy], fill=(36, 36, 42))
    # mine buoy with spikes
    mx, my = x + 34, y + 88
    d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(30, 30, 34),
              outline=(200, 200, 190), width=1)
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([(mx + 7 * math.cos(r), my + 7 * math.sin(r)),
                (mx + 12 * math.cos(r), my + 12 * math.sin(r))],
               fill=(200, 200, 190), width=2)
    # patrol boat, small, far right
    bx, by = x + w - 56, y + 86
    d.polygon([(bx, by), (bx + 44, by), (bx + 38, by + 8), (bx + 6, by + 8)],
              fill=(200, 200, 195))
    d.rectangle([bx + 12, by - 8, bx + 28, by], fill=(200, 200, 195))


# ---------------------------------------------------------------- small scenes
def small_ship(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (70, 110, 150), (28, 48, 84))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(18, 34, 62))
    waves(d, (x, y + int(h * 0.62), x + w, y + h), color=(110, 160, 220), n=2)
    sx, sy = x + 30, y + int(h * 0.62)
    d.polygon([(sx, sy), (sx + 130, sy), (sx + 120, sy + 12),
               (sx + 10, sy + 12)], fill=(16, 16, 20))
    d.rectangle([sx + 40, sy - 12, sx + 80, sy], fill=(28, 28, 34))
    d.rectangle([sx + 96, sy - 18, sx + 104, sy], fill=(36, 36, 42))
    flames(d, sx + 46, sy - 1, [(14, 20), (10, 14)])
    for ox, oy, r in [(0, -26, 6), (7, -34, 8)]:
        d.ellipse([sx + 96 + ox - r, sy + oy - r, sx + 96 + ox + r,
                   sy + oy + r], fill=(70, 70, 78))


def small_city(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (52, 62, 96), (24, 28, 52))
    stars(d, (x, y, x + w, y + int(h * 0.5)), 10, seed=3)
    d.ellipse([x + w - 34, y + 6, x + w - 16, y + 24], fill=(240, 228, 180))
    skyline(d, x + 4, y + h - 2, x + w - 4, seed=5, color=(12, 15, 30), hmax=34)
    flames(d, x + 84, y + h - 2, [(14, 20)])


def small_boat(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (120, 170, 210), (40, 90, 150))
    d.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(22, 62, 120))
    waves(d, (x, y + int(h * 0.55), x + w, y + h), color=(160, 200, 240), n=3)
    # capsized hull
    cx, cy = x + w // 2, y + int(h * 0.55)
    d.pieslice([cx - 46, cy - 16, cx + 46, cy + 16], 180, 360, fill=(150, 60, 40))
    d.rectangle([cx - 46, cy - 2, cx + 46, cy + 2], fill=(120, 45, 30))
    # small figures in the water
    for ox in (-58, 58):
        d.ellipse([cx + ox - 4, cy + 8, cx + ox + 4, cy + 16],
                  fill=(232, 196, 160))


def small_parliament(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (190, 200, 220), (150, 160, 185))
    # dome + columns
    bx, by = x + 30, y + h - 6
    d.pieslice([bx + 52, y + 4, bx + 92, y + 34], 180, 360, fill=(240, 235, 220))
    d.rectangle([bx, by - 22, bx + 144, by], fill=(226, 220, 205))
    for i in range(6):
        cx = bx + 8 + i * 24
        d.rectangle([cx, by - 20, cx + 8, by - 2], fill=(250, 246, 236))
    d.rectangle([bx - 4, by - 24, bx + 148, by - 20], fill=(210, 202, 185))
    # speech bubble with ?
    d.ellipse([x + w - 46, y + 6, x + w - 10, y + 30], fill=WHITE,
              outline=INK, width=1)
    d.polygon([(x + w - 34, y + 28), (x + w - 30, y + 38), (x + w - 22, y + 28)],
              fill=WHITE, outline=INK)
    d.text((x + w - 32, y + 9), "?", font=franklin(16, 700), fill=INK)


def small_badge(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (60, 50, 70), (24, 20, 30))
    # desert mountains
    d.polygon([(x, y + h), (x + 60, y + 12), (x + 120, y + h)], fill=(90, 70, 90))
    d.polygon([(x + 80, y + h), (x + 150, y + 20), (x + w, y + h)],
              fill=(70, 52, 70))
    # gold star badge
    cx, cy, r = x + w - 42, y + 26, 20
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
    d.polygon(pts, fill=(255, 200, 60), outline=(180, 130, 20))
    d.text((cx - 4, cy - 7), "★", font=inter(13, 700), fill=(140, 90, 0))


def small_bitcoin(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (20, 60, 40), (10, 34, 24))
    # rising chart
    pts = [(x + 8, y + h - 12), (x + 50, y + h - 30), (x + 90, y + h - 22),
           (x + 130, y + h - 40), (x + 168, y + h - 46)]
    d.line(pts, fill=(90, 220, 140), width=3, joint="curve")
    for px, py in pts[1:]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(120, 240, 160))
    # coin
    cx, cy, r = x + w - 40, y + 22, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26),
              outline=(200, 110, 10), width=2)
    d.text((cx - 6, cy - 11), "₿", font=inter(18, 700), fill=WHITE)


def small_chip(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (240, 240, 235), (200, 205, 200))
    # green chip
    d.rectangle([x + 56, y + 10, x + 140, y + h - 10], fill=(30, 140, 70),
                outline=(20, 100, 50), width=2)
    d.rectangle([x + 72, y + 20, x + 124, y + h - 20], fill=(20, 110, 55))
    d.text((x + 82, y + 18), "AI", font=franklin(16, 700), fill=WHITE)
    # red down-trend
    d.line([(x + 8, y + 12), (x + 48, y + 26), (x + 88, y + 20),
            (x + 128, y + 40), (x + 168, y + 34), (x + 188, y + 48)],
           fill=(200, 40, 40), width=3, joint="curve")
    # magnifier
    mx, my = x + w - 26, y + h - 18
    d.ellipse([mx - 10, my - 10, mx + 10, my + 10], outline=INK, width=3)
    d.line([mx + 7, my + 7, mx + 16, my + 16], fill=INK, width=3)


def small_hospital(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (220, 235, 245), (180, 200, 220))
    # bed
    bx, by = x + 30, y + h - 14
    d.rectangle([bx, by - 16, bx + 130, by - 10], fill=(240, 240, 235),
                outline=INK, width=1)
    d.rectangle([bx + 4, by - 10, bx + 8, by], fill=INK)
    d.rectangle([bx + 148, by - 10, bx + 152, by], fill=INK)
    d.ellipse([bx + 6, by - 26, bx + 22, by - 14], fill=(232, 196, 160))
    d.rectangle([bx + 22, by - 20, bx + 120, by - 14], fill=(90, 140, 200))
    # heartbeat line
    d.line([(x + 8, y + 16), (x + 40, y + 16), (x + 52, y + 6),
            (x + 64, y + 26), (x + 76, y + 16), (x + 120, y + 16)],
           fill=(200, 40, 40), width=2, joint="curve")
    # red cross sign
    d.rectangle([x + w - 34, y + 8, x + w - 10, y + 32], fill=WHITE,
                outline=RED, width=2)
    d.rectangle([x + w - 29, y + 13, x + w - 15, y + 27], fill=RED)
    d.rectangle([x + w - 27, y + 15, x + w - 17, y + 25], fill=RED)


def small_vote(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (40, 70, 140), (24, 44, 96))
    # ballot box
    bx, by = x + 60, y + h - 8
    d.rectangle([bx, by - 26, bx + 76, by], fill=(240, 235, 220),
                outline=INK, width=1)
    d.rectangle([bx + 28, by - 32, bx + 48, by - 26], fill=(30, 30, 30))
    # ballot slip going in
    d.polygon([(bx + 30, by - 44), (bx + 46, by - 44), (bx + 44, by - 30),
               (bx + 28, by - 30)], fill=WHITE, outline=INK)
    d.text((bx + 32, by - 42), "✓", font=inter(11, 700), fill=RED)
    # rising bars (seats)
    for i, bh in enumerate([12, 20, 28]):
        dx = x + 12 + i * 14
        d.rectangle([dx, y + h - 8 - bh, dx + 10, y + h - 8],
                    fill=(255, 200, 60))


def small_aid(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (210, 200, 180), (170, 160, 140))
    # truck
    tx, ty = x + 24, y + h - 22
    d.rectangle([tx, ty - 20, tx + 110, ty], fill=(240, 240, 235),
                outline=INK, width=1)
    d.rectangle([tx + 110, ty - 14, tx + 138, ty], fill=(200, 60, 50),
                outline=INK, width=1)
    d.rectangle([tx + 112, ty - 12, tx + 124, ty - 4], fill=(180, 220, 240))
    for wx in (tx + 22, tx + 92):
        d.ellipse([wx - 8, ty - 2, wx + 8, ty + 10], fill=(20, 20, 20))
        d.ellipse([wx - 3, ty + 3, wx + 3, ty + 9], fill=(150, 150, 150))
    # AID label + cross
    d.text((tx + 34, ty - 18), "AID", font=franklin(13, 700), fill=RED)
    d.rectangle([tx + 78, ty - 18, tx + 92, ty - 4], fill=WHITE, outline=RED)
    d.rectangle([tx + 83, ty - 16, tx + 87, ty - 6], fill=RED)
    d.rectangle([tx + 80, ty - 13, tx + 90, ty - 9], fill=RED)




def small_f1(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (16, 20, 44), (40, 44, 80))
    for i in range(12):
        c = WHITE if i % 2 == 0 else INK
        d.rectangle([x + i * 16, y, x + (i + 1) * 16, y + 10], fill=c)
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(60, 60, 70))
    d.line([(x, y + int(h * 0.62) + 8), (x + w, y + int(h * 0.62) + 8)],
           fill=(255, 255, 255), width=2)
    cx, cy = x + 52, y + int(h * 0.62) - 4
    d.rectangle([cx, cy - 8, cx + 84, cy + 4], fill=(200, 30, 30))
    d.rectangle([cx + 26, cy - 16, cx + 56, cy - 8], fill=(200, 30, 30))
    d.rectangle([cx + 84, cy - 14, cx + 90, cy + 4], fill=(140, 20, 20))
    for wx in (cx + 14, cx + 66):
        d.ellipse([wx - 8, cy - 2, wx + 8, cy + 10], fill=(10, 10, 10))
        d.ellipse([wx - 3, cy + 3, wx + 3, cy + 7], fill=(160, 160, 160))
    for i, ly in enumerate([y + 22, y + 30, y + 38]):
        d.line([(x + 8, ly), (x + 44 - i * 8, ly)], fill=(255, 220, 120),
               width=2)
    stars(d, (x, y + 12, x + w, y + int(h * 0.4)), 8, seed=21)


def small_cricket(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (70, 140, 80), (30, 90, 45))
    d.rectangle([x + 60, y + 6, x + 136, y + h - 4], fill=(210, 180, 130))
    sx = x + 150
    for i in range(3):
        d.rectangle([sx + i * 6, y + 12, sx + i * 6 + 3, y + 34],
                    fill=(250, 240, 200))
    d.rectangle([sx, y + 10, sx + 16, y + 12], fill=(250, 240, 200))
    d.polygon([(x + 34, y + 40), (x + 44, y + 38), (x + 30, y + h - 6),
               (x + 20, y + h - 6)], fill=(220, 190, 140),
              outline=(120, 90, 50))
    d.ellipse([x + 116, y + h - 20, x + 128, y + h - 8], fill=(200, 40, 40))
    for i in range(8):
        d.ellipse([x + 8 + i * 6, y + 6, x + 12 + i * 6, y + 10],
                  fill=(255, 255, 255))


def small_basketball(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (30, 50, 110), (16, 28, 66))
    d.rectangle([x, y + int(h * 0.6), x + w, y + h], fill=(200, 120, 50))
    d.arc([x + 20, y + int(h * 0.55), x + 180, y + h + 20], 180, 360,
          fill=(255, 255, 255), width=2)
    d.rectangle([x + w - 52, y + 6, x + w - 10, y + 30], fill=WHITE,
                outline=INK, width=1)
    d.ellipse([x + w - 44, y + 30, x + w - 18, y + 38],
              outline=(255, 120, 40), width=3)
    d.line([(x + w - 40, y + 38), (x + w - 34, y + 48)], fill=WHITE, width=1)
    d.line([(x + w - 22, y + 38), (x + w - 28, y + 48)], fill=WHITE, width=1)
    cx, cy, r = x + 44, y + 26, 15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 120, 40),
              outline=(160, 60, 10), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=(120, 50, 10), width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=(120, 50, 10),
          width=2)


def small_fire(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (60, 60, 66), (28, 28, 32))
    d.rectangle([x + 16, y + 22, x + 120, y + h - 6], fill=(20, 20, 24))
    d.rectangle([x + 126, y + 8, x + 138, y + h - 6], fill=(20, 20, 24))
    d.rectangle([x + 142, y + 16, x + 152, y + h - 6], fill=(20, 20, 24))
    for i in range(4):
        d.rectangle([x + 28 + i * 24, y + 30, x + 38 + i * 24, y + 38],
                    fill=(255, 180, 60))
    for ox, oy, r in [(0, -6, 8), (10, -16, 10), (22, -26, 12)]:
        d.ellipse([x + 130 + ox - r, y + oy - r, x + 130 + ox + r,
                   y + oy + r], fill=(90, 90, 96))
    flames(d, x + 30, y + 22, [(18, 22), (14, 16), (12, 18)])
    flames(d, x + 96, y + 22, [(14, 18)])


def small_pope(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (240, 225, 190), (200, 180, 140))
    d.pieslice([x + 62, y + 2, x + 134, y + 40], 180, 360,
               fill=(210, 190, 150))
    d.rectangle([x + 94, y - 2, x + 102, y + 8], fill=(210, 190, 150))
    d.rectangle([x + 40, y + 38, x + 156, y + 44], fill=(190, 170, 130))
    for i in range(6):
        cx = x + 48 + i * 20
        d.rectangle([cx, y + 44, cx + 6, y + h - 2], fill=(230, 215, 180))
    ty = y + h - 12
    d.rectangle([x + 10, ty, x + w - 10, ty + 6], fill=(255, 255, 255))
    cols = [(200, 60, 60), (60, 120, 200), (60, 160, 90), (220, 160, 40),
            (150, 80, 180), (90, 90, 180), (200, 120, 60)]
    for i in range(7):
        dx = x + 18 + i * 26
        d.ellipse([dx, ty - 12, dx + 10, ty - 2], fill=(232, 196, 160))
        d.polygon([(dx + 5, ty - 2), (dx - 3, ty + 2), (dx + 13, ty + 2)],
                  fill=cols[i])


def small_power(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (24, 26, 48), (10, 12, 26))
    stars(d, (x, y, x + w, y + int(h * 0.5)), 8, seed=9)
    rnd = random.Random(17)
    xx = x + 4
    while xx < x + w - 6:
        bw = rnd.randint(12, 24)
        bh = rnd.randint(14, 34)
        d.rectangle([xx, y + h - 2 - bh, xx + bw, y + h - 2],
                    fill=(8, 10, 22))
        xx += bw + rnd.randint(1, 4)
    d.rectangle([x + 96, y + h - 30, x + 104, y + h - 22],
                fill=(255, 214, 110))
    d.ellipse([x + 140, y + h - 22, x + 156, y + h - 6],
              fill=(255, 200, 90))
    d.rectangle([x + 146, y + h - 12, x + 150, y + h - 2],
                fill=(250, 245, 230))
    d.polygon([(x + 148, y + h - 22), (x + 144, y + h - 12),
               (x + 152, y + h - 12)], fill=(255, 140, 30))


def small_rubble(d, x, y, w, h):
    """Collapsed apartment block: night sky, broken slabs, dust, light."""
    vgrad(d, (x, y, x + w, y + h), (52, 56, 84), (22, 24, 44))
    stars(d, (x, y, x + w, y + int(h * 0.4)), 8, seed=13)
    # standing part of the block
    d.rectangle([x + 14, y + 10, x + 78, y + h - 4], fill=(30, 32, 48))
    for wy in range(y + 16, y + h - 10, 10):
        for wx in range(x + 20, x + 72, 12):
            d.rectangle([wx, wy, wx + 5, wy + 6], fill=(255, 214, 120))
    # collapsed part: tilted slabs
    d.polygon([(x + 78, y + h - 4), (x + 120, y + 26), (x + 150, y + 34),
               (x + 132, y + h - 4)], fill=(44, 44, 54))
    d.polygon([(x + 96, y + h - 4), (x + 150, y + 40), (x + 186, y + 52),
               (x + 178, y + h - 4)], fill=(58, 58, 68))
    # dust clouds
    for ox, oy, r in [(0, -6, 9), (12, -14, 11), (26, -8, 8)]:
        d.ellipse([x + 150 + ox - r, y + 30 + oy - r, x + 150 + ox + r,
                   y + 30 + oy + r], fill=(140, 135, 125))
    # searchlight beam
    d.polygon([(x + w - 30, y + h - 4), (x + w - 8, y + h - 4),
               (x + w - 2, y + 12), (x + w - 24, y + 12)],
              fill=(255, 240, 180))


def small_refinery(d, x, y, w, h):
    """Oil refinery at dusk: tanks, tower, flames, smoke."""
    vgrad(d, (x, y, x + w, y + h), (230, 140, 60), (90, 50, 40))
    # tanks
    for tx in (x + 14, x + 66):
        d.rectangle([tx, y + 26, tx + 46, y + h - 6], fill=(120, 120, 118),
                    outline=(70, 70, 68), width=1)
        d.pieslice([tx, y + 18, tx + 46, y + 34], 180, 360,
                   fill=(150, 150, 148))
    # distillation tower
    d.polygon([(x + 140, y + h - 6), (x + 148, y + 8), (x + 162, y + 8),
               (x + 170, y + h - 6)], fill=(90, 90, 88))
    flames(d, x + 22, y + 26, [(18, 24), (14, 16)])
    flames(d, x + 146, y + 8, [(12, 18)])
    for ox, oy, r in [(0, -8, 8), (10, -18, 10), (22, -28, 12)]:
        d.ellipse([x + 150 + ox - r, y + oy - r, x + 150 + ox + r,
                   y + oy + r], fill=(70, 66, 62))


def small_chess(d, x, y, w, h):
    """Chess: board, two kings, clock."""
    vgrad(d, (x, y, x + w, y + h), (70, 60, 90), (30, 26, 44))
    # board 6x6
    bx, by, s = x + 14, y + 8, 13
    for r in range(6):
        for c in range(6):
            col = (240, 225, 200) if (r + c) % 2 == 0 else (120, 80, 50)
            d.rectangle([bx + c * s, by + r * s, bx + (c + 1) * s,
                         by + (r + 1) * s], fill=col)
    d.rectangle([bx, by, bx + 6 * s, by + 6 * s], outline=(60, 40, 20),
                width=2)
    # white king
    kx, ky = bx + 14, by + 10
    d.ellipse([kx - 7, ky - 7, kx + 7, ky + 7], fill=WHITE, outline=INK,
              width=1)
    d.rectangle([kx - 8, ky + 4, kx + 8, ky + 12], fill=WHITE, outline=INK,
                width=1)
    d.text((kx - 3, ky - 5), "+", font=inter(9, 700), fill=INK)
    # black king
    kx2, ky2 = bx + 52, by + 44
    d.ellipse([kx2 - 7, ky2 - 7, kx2 + 7, ky2 + 7], fill=(30, 30, 34),
              outline=WHITE, width=1)
    d.rectangle([kx2 - 8, ky2 + 4, kx2 + 8, ky2 + 12], fill=(30, 30, 34),
                outline=WHITE, width=1)
    d.text((kx2 - 3, ky2 - 5), "+", font=inter(9, 700), fill=WHITE)
    # clock
    ccx, ccy, cr = x + w - 30, y + h - 22, 13
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=WHITE,
              outline=INK, width=2)
    d.line([ccx, ccy, ccx, ccy - 8], fill=INK, width=2)
    d.line([ccx, ccy, ccx + 6, ccy], fill=INK, width=2)


def small_drone(d, x, y, w, h):
    """Drone over a city at night, UN-blue building below."""
    vgrad(d, (x, y, x + w, y + h), (30, 34, 64), (14, 16, 34))
    stars(d, (x, y, x + w, y + int(h * 0.5)), 10, seed=23)
    # drone: X arms, 4 rotors, body
    cx, cy = x + w // 2, y + 26
    for dx, dy in [(-16, -8), (16, -8), (-16, 8), (16, 8)]:
        d.line([(cx, cy), (cx + dx, cy + dy)], fill=(180, 180, 180), width=2)
        d.ellipse([cx + dx - 6, cy + dy - 2, cx + dx + 6, cy + dy + 2],
                  fill=(120, 120, 130))
    d.ellipse([cx - 8, cy - 5, cx + 8, cy + 5], fill=(60, 60, 70),
              outline=(200, 200, 200), width=1)
    d.ellipse([cx - 2, cy + 5, cx + 2, cy + 9], fill=(255, 60, 60))
    # skyline with one UN-blue building
    skyline(d, x + 4, y + h - 2, x + w - 4, seed=31, color=(10, 14, 30),
            hmax=30)
    d.rectangle([x + w - 52, y + h - 30, x + w - 26, y + h - 2],
                fill=(40, 90, 180))
    d.rectangle([x + w - 48, y + h - 26, x + w - 30, y + h - 6],
                fill=(90, 140, 220))


def small_football(d, x, y, w, h):
    """Football pitch at night: green, lines, ball, goal."""
    vgrad(d, (x, y, x + w, y + h), (50, 130, 70), (24, 80, 40))
    # pitch lines
    d.rectangle([x + 8, y + 8, x + w - 8, y + h - 6], outline=WHITE, width=2)
    d.line([(x + w // 2, y + 8), (x + w // 2, y + h - 6)], fill=WHITE,
           width=2)
    d.ellipse([x + w // 2 - 16, y + h // 2 - 16, x + w // 2 + 16,
               y + h // 2 + 16], outline=WHITE, width=2)
    # goal, right
    d.rectangle([x + w - 34, y + 16, x + w - 10, y + 44], outline=WHITE,
                width=2)
    for i in range(4):
        d.line([(x + w - 34 + i * 6, y + 16), (x + w - 34 + i * 6, y + 44)],
               fill=WHITE, width=1)
    # ball
    bx, by, r = x + 46, y + h - 24, 12
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=WHITE, outline=INK,
              width=1)
    d.polygon([(bx, by - 5), (bx + 5, by - 1), (bx + 3, by + 5),
               (bx - 3, by + 5), (bx - 5, by - 1)], fill=INK)
    # floodlight glare
    d.ellipse([x + 12, y + 6, x + 22, y + 16], fill=(255, 240, 180))

# ---------------------------------------------------------------- dot map
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-110, 68), (-95, 69),
     (-90, 73), (-85, 66), (-80, 62), (-76, 60), (-70, 58), (-65, 49),
     (-60, 46), (-70, 42), (-75, 38), (-76, 35), (-80, 31), (-81, 26),
     (-84, 24), (-87, 21), (-90, 14), (-92, 15), (-95, 16), (-97, 16),
     (-100, 18), (-105, 20), (-108, 23), (-112, 28), (-117, 33), (-122, 37),
     (-124, 42), (-124, 48), (-130, 55), (-140, 60), (-150, 61), (-158, 58),
     (-165, 60)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-32, 68), (-22, 70), (-30, 74),
     (-45, 76), (-58, 76), (-60, 70)],
    # South America
    [(-79, 9), (-77, 7), (-72, 12), (-64, 10), (-59, 8), (-52, 5),
     (-50, 0), (-44, -3), (-38, -5), (-35, -8), (-37, -13), (-40, -20),
     (-41, -23), (-48, -27), (-52, -32), (-58, -38), (-62, -41), (-66, -47),
     (-69, -52), (-71, -54), (-74, -50), (-73, -44), (-72, -35), (-71, -25),
     (-70, -18), (-75, -15), (-80, -6), (-81, -1), (-80, 4)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (4, 53), (8, 57),
     (10, 59), (13, 56), (18, 56), (21, 55), (24, 59), (30, 60), (28, 62),
     (23, 65), (18, 69), (25, 71), (30, 70), (32, 68), (35, 66), (40, 66),
     (44, 68), (48, 68), (44, 64), (40, 62), (38, 58), (36, 54), (34, 50),
     (32, 46), (30, 44), (28, 41), (30, 38), (33, 36), (36, 36), (30, 36),
     (27, 37), (23, 36), (20, 40), (19, 42), (15, 44), (12, 44), (8, 44),
     (3, 42), (0, 39), (-2, 37), (-6, 36), (-9, 37)],
    # Africa
    [(-17, 15), (-16, 21), (-13, 27), (-9, 31), (-5, 35), (0, 36),
     (10, 37), (11, 34), (20, 32), (25, 32), (30, 31), (32, 31), (35, 28),
     (37, 22), (39, 18), (43, 12), (48, 11), (51, 12), (48, 6), (46, 2),
     (42, -2), (40, -8), (40, -12), (36, -18), (35, -22), (33, -26),
     (31, -29), (28, -33), (25, -34), (20, -35), (17, -32), (15, -27),
     (12, -18), (13, -12), (12, -6), (9, 4), (4, 6), (-8, 5), (-13, 8),
     (-17, 12)],
    # Asia (incl. Russia east of 30E)
    [(30, 36), (33, 36), (36, 36), (39, 38), (43, 40), (47, 39), (50, 37),
     (54, 37), (57, 37), (56, 32), (54, 29), (52, 26), (56, 26), (58, 25),
     (60, 25), (62, 25), (66, 25), (68, 24), (72, 22), (75, 20), (77, 16),
     (80, 13), (80, 8), (82, 9), (86, 12), (88, 16), (91, 22), (93, 20),
     (95, 16), (97, 15), (100, 13), (101, 8), (103, 6), (104, 2), (105, 6),
     (106, 10), (108, 12), (109, 15), (110, 20), (112, 22), (114, 22),
     (116, 23), (118, 25), (120, 28), (122, 30), (124, 32), (126, 34),
     (127, 36), (129, 38), (131, 39), (133, 42), (135, 43), (137, 44),
     (139, 45), (141, 46), (142, 50), (141, 53), (140, 55), (139, 58),
     (140, 60), (138, 62), (137, 65), (136, 68), (135, 70), (133, 71),
     (130, 71), (128, 72), (125, 73), (122, 73), (118, 74), (114, 74),
     (110, 74), (105, 76), (100, 76), (95, 76), (90, 75), (85, 74),
     (80, 73), (75, 72), (70, 72), (66, 70), (62, 69), (58, 68), (55, 68),
     (52, 68), (49, 69), (45, 68), (42, 67), (39, 66), (36, 65), (33, 66),
     (30, 68), (30, 70)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (147, -39),
     (150, -37), (153, -32), (153, -27), (151, -24), (149, -20), (146, -19),
     (142, -15), (142, -11), (141, -13), (140, -17), (139, -17), (136, -15),
     (135, -12), (132, -11), (130, -13), (126, -14), (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (168, -44), (170, -43), (172, -41), (174, -38), (175, -37),
     (177, -38), (178, -37), (176, -39), (174, -41), (172, -43), (169, -46)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8), (147, -9),
     (143, -8), (138, -7), (134, -4)],
]

# story pins: (lon, lat, dx, dy) — display offsets separate close pins
PINS = {
    1: (-122.0, 37.4, 0, -8),   # Santa Clara (Nvidia)
    2: (13.4, 52.5, 0, -8),     # Berlin (talks call)
    3: (56.5, 26.6, 0, -8),     # Strait of Hormuz
    4: (30.5, 50.4, -12, -4),   # Kyiv
    5: (30.2, 50.9, 12, -10),   # Dymer
    6: (39.7, 47.2, 0, -8),     # Novoshakhtinsk / Rostov
    7: (20.1, 32.1, 0, -8),     # Benghazi
    8: (34.5, 31.5, -14, 10),   # Gaza
    9: (106.2, -6.3, 0, 0),     # Cikande
    10: (6.1, 46.2, 0, -8),     # Geneva
    11: (32.5, 15.6, 0, 0),     # Khartoum
    12: (174.8, -41.3, 0, 0),   # Wellington
    13: (-0.1, 51.6, 0, -8),    # London
}


def _inside(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
           (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_dot_map(d, x0, y0, w, h):
    lat_top, lat_bot = 78, -58
    dot = (176, 160, 128)
    lon = -180
    while lon < 180:
        lat = lat_top
        while lat > lat_bot:
            if any(_inside(lon, lat, p) for p in CONTINENTS):
                px = x0 + (lon + 180) / 360 * w
                py = y0 + (lat_top - lat) / (lat_top - lat_bot) * h
                d.ellipse([px - 1.4, py - 1.4, px + 1.4, py + 1.4], fill=dot)
            lat -= 3
        lon += 3
    # numbered pins
    fnum = inter(9, 700)
    for num, (lon, lat, dx, dy) in PINS.items():
        px = x0 + (lon + 180) / 360 * w + dx
        py = y0 + (lat_top - lat) / (lat_top - lat_bot) * h + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=WHITE,
                  outline=RED_DK, width=1)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED)
        t = str(num)
        tw = text_w(fnum, t)
        d.text((px - tw / 2, py - 6.5), t, font=fnum, fill=WHITE)


# ---------------------------------------------------------------- content (v1: built for 24 Nov UTC)
NUMBERS = [
    ("153", "drones fired at Ukraine overnight"),
    ("134", "downed or jammed by air defence"),
    ("700k", "Russian war dead, new estimate"),
    ("+31%", "Nvidia shares in one session"),
    ("$165", "Nvidia close after Huang return"),
    ("24", "dead in Cikande factory fire"),
]

REGIONS = [
    ("EUROPE 12", 12, (47, 93, 138)),
    ("MIDDLE EAST 4", 4, (168, 30, 35)),
    ("AMERICAS 6", 6, (46, 125, 79)),
    ("ASIA-PAC 8", 8, (199, 123, 33)),
    ("AFRICA 4", 4, (122, 78, 142)),
    ("OCEANIA 2", 2, (42, 157, 143)),
    ("WORLD 4", 4, (90, 90, 90)),
]

TIMELINE = [
    ("04:35", "Sybiha at UN Council"),
    ("14:00", "Gukesh–Sindarov, Game 1"),
    ("15:00", "Davis Cup: Czechia–Canada"),
    ("17:45", "UCL: Galatasaray–Villa"),
    ("20:00", "UCL: Arsenal–Dortmund"),
    ("20:00", "UCL: Man City–Napoli"),
]

LEADS = [
    dict(num=1, strip="HUANG IS BACK", scene=lead_nvidia,
         caption="Nvidia board", tag="CONFIRMED",
         kicker="1  SANTA CLARA, US · BUSINESS",
         headline="Nvidia brings Jensen Huang back as chief",
         deck="Board reinstates him 11 days after he quit; shares jump "
              "31%, regaining about $1tn in a session. (AP)"),
    dict(num=2, strip="TALKS 'TOMORROW'", scene=lead_talks,
         caption="Zelenskyy video call", tag="REPORTED",
         kicker="2  BERLIN · UKRAINE WAR",
         headline="Zelenskyy seeks four-way talks 'literally tomorrow'",
         deck="Ukraine, Russia, US, Europe; partners want a deal before "
              "Christmas; NATO plea repeated. (europesays)"),
    dict(num=3, strip="BLOCKADE DEFIANCE", scene=lead_iran,
         caption="Strait of Hormuz", tag="REPORTED",
         kicker="3  TEHRAN · IRAN",
         headline="Iran vows 'all available means' to defy US blockade",
         deck="Trump threatened breaching tankers with the sea floor; "
              "Tehran says Hormuz can reopen in hours. (Reuters)"),
]

SMALL = [
    dict(num=4, strip="153 DRONES", scene=small_city, tag="CONFIRMED",
         kicker="4  UKRAINE",
         headline="Russia fires 153 drones; 134 downed",
         deck="60 jet-powered Shaheds; hits at 11 sites. "
              "(Air Force, Ukrinform)"),
    dict(num=5, strip="15 KILLED", scene=small_rubble, tag="CONFIRMED",
         kicker="5  KYIV REGION",
         headline="Strikes kill 15 across Kyiv region",
         deck="Dymer block collapses; Vyshneve supermarket hit, three "
              "dead. (Officials)"),
    dict(num=6, strip="REFINERY HIT", scene=small_refinery, tag="REPORTED",
         kicker="6  ROSTOV, RUSSIA",
         headline="Ukrainian drones hit refinery and pump station",
         deck="Novoshakhtinsk ablaze; Kaleikino pumping station on fire. "
              "(h.ua)"),
    dict(num=7, strip="CORVETTE SUNK", scene=small_ship, tag="CONFIRMED",
         kicker="7  BENGHAZI, LIBYA",
         headline="Ukraine sinks Russian corvette in Libya",
         deck="Seven sea drones hit Merkury and cargo ship Angara. "
              "(Zelenskyy)"),
    dict(num=8, strip="3 KILLED", scene=small_aid, tag="CONFIRMED",
         kicker="8  GAZA",
         headline="Israeli strikes kill three in Gaza",
         deck="UNRWA worker among the dead despite the October truce. "
              "(Al Jazeera)"),
    dict(num=9, strip="TOLL 24", scene=small_fire, tag="CONFIRMED",
         kicker="9  CIKANDE, INDONESIA",
         headline="Factory fire toll rises to 24",
         deck="Candy plant blaze; search for missing workers goes on. "
              "(TOI)"),
    dict(num=10, strip="GAME 1 TODAY", scene=small_chess, tag="FORECAST",
         kicker="10  GENEVA",
         headline="Gukesh begins his title defence",
         deck="Game 1 v Sindarov, 15:00 CET; both 20, youngest match "
              "ever. (FIDE)"),
    dict(num=11, strip="UN CONDEMNS", scene=small_drone, tag="CONFIRMED",
         kicker="11  KHARTOUM, SUDAN",
         headline="UN condemns Khartoum drone strikes",
         deck="Four killed, UN building hit Sunday; drones killed 1,630 "
              "in 2026. (UN)"),
    dict(num=12, strip="DRAWN", scene=small_cricket, tag="CONFIRMED",
         kicker="12  WELLINGTON",
         headline="New Zealand hold on for a draw",
         deck="Mitchell 49* off 186; India 720/9 was a record in NZ. "
              "(ICC)"),
    dict(num=13, strip="MATCHDAY 5", scene=small_football, tag="FORECAST",
         kicker="13  EUROPE",
         headline="Champions League: De Bruyne returns",
         deck="Man City host Napoli; Arsenal face Dortmund tonight. "
              "(UEFA)"),
]

ALSO = [
    (14, "Europe: Russian war dead pass 700,000, Meduza–Mediazona estimate", "Meduza"),
    (15, "Europe: Norway court voids disputed oil licences", "Wires"),
    (16, "Europe: Hungary's Magyar to visit Zakarpattia", "Wires"),
    (17, "Europe: Poland summons Russian envoy over airspace breach", "Wires"),
    (18, "Europe: Russia accuses Estonia of hosting drone flights", "Wires"),
    (19, "Europe: Sybiha: port attacks threaten world food security", "UN"),
    (20, "Europe: Reports: Russia may put a nuclear weapon in space", "Wires"),
    (21, "Middle East: Two tankers hit by mines near Hormuz", "IRGC"),
    (22, "Middle East: US sanctions Iran's shadow banking network", "Reuters"),
    (23, "Americas: US blacklists Megaspeed in Nvidia spy case", "AP"),
    (24, "Americas: Pentagon rebukes Canada over defence and F-35", "Wires"),
    (25, "Americas: Two women indicted over faked anti-Trump attack", "Wires"),
    (26, "Americas: Princeton neuroscientist detained by ICE", "Wires"),
    (27, "Americas: FBI faces Tuesday deadline on Epstein notes", "Wires"),
    (28, "Asia-Pacific: China sentences official Ma to death for spying", "Wires"),
    (29, "Asia-Pacific: Russian aircraft enter South Korea's air zone", "Wires"),
    (30, "Asia-Pacific: India stays third in Asia Power Index", "Wires"),
    (31, "Asia-Pacific: SK hynix ADRs jump 20% on Nvidia rebound", "AP"),
    (32, "Asia-Pacific: Singapore and Australia sign two pacts", "Wires"),
    (33, "Asia-Pacific: Bangladesh unrest: six killed over Hasina return", "Al Jazeera"),
    (34, "Africa: DR Congo enacts constitutional reform law", "Wires"),
    (35, "Africa: Fighting traps Ebola responders in Ituri", "WHO"),
    (36, "Africa: DR Congo Ebola cases pass 11,000; deaths 5,400", "Africa CDC"),
    (37, "Oceania: Severe storms hit Australia's east coast", "Wires"),
    (38, "World: Oil falls 3% as Middle East flows ease", "Wires"),
    (39, "World: COP31: Guterres 'deeply disappointed', eyes COP32", "UN"),
    (40, "World: Davis Cup Finals begin in Bologna today", "Flashscore"),
]

DATE_CHECK = (
    "Wires read up to 07:00 UTC, Tue 24 Nov 2026. Left out as other "
    "days' news: the 400-drone barrage (19–20 Nov) — tonight's was "
    "153; COP31's pact never adopted (22 Nov); ATP final (22 Nov); "
    "S. Africa voted 4 Nov; Lagarde exit (29 Oct); Kenya Ebola "
    "discharge (11 Nov).")

SOURCES = (
    "Sources: Reuters, AP, Al Jazeera, AFP, Ukrinform, UN News, ICC, "
    "UEFA, FIDE, Meduza, The Guardian, TOI.")

TAGS = (
    "CONFIRMED: official or 2+ outlets · REPORTED: carried by the "
    "day's wires · CLAIM: one side's account, labelled as such · "
    "FORECAST: still to happen when drawn")


# ---------------------------------------------------------------- page build
def scene_img(fn, w, h):
    """Render one illustration into its own image (clips any spill)."""
    im = Image.new("RGB", (w, h), (0, 0, 0))
    td = ImageDraw.Draw(im)
    fn(td, 0, 0, w, h)
    return im


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top bar
    d.text((10, 7), "THE WORLD IN ONE DAY", font=franklin(13, 700), fill=RED)
    rt = "40 STORIES  •  7 REGIONS  •  EVERY ONE DATED 23–24 NOVEMBER 2026"
    rf = inter(11, 600)
    d.text((1014 - text_w(rf, rt), 8), rt, font=rf, fill=NAVY)
    d.line([(10, 28), (1014, 28)], fill=RULE, width=2)

    # ---- masthead: Playfair 900 has a tall ink box, so measure it and
    # place the subline below the real ink bottom (v6.1 fix: subline
    # used to be struck through by the masthead's descenders).
    mf = autofit_font(lambda s: playfair(s, 900), "Tuesday 24 November 2026",
                      64, 1000, min_size=40)
    mw = text_w(mf, "Tuesday 24 November 2026")
    mx = (W - mw) / 2
    d.text((mx, 2), "Tuesday 24 November 2026", font=mf, fill=INK)
    bb = d.textbbox((mx, 2), "Tuesday 24 November 2026", font=mf)
    sub = ("Nvidia brings Huang back  ·  Zelenskyy seeks four-way talks "
           "'tomorrow'  ·  Iran vows to defy the blockade")
    sf = playfair_italic(16, 500)
    sub_y = bb[3] + 6
    d.text(((W - text_w(sf, sub)) / 2, sub_y), sub, font=sf, fill=RED)
    rule2 = sub_y + 22

    # downstream layout, all offsets from rule2 (the rule under the subline)
    num_y = rule2 + 4        # number strip
    reg_y = rule2 + 52       # region bar (20 high)
    tl_y = rule2 + 76        # timeline
    rule3 = rule2 + 106
    lead_y = rule2 + 110     # leads illustration top
    sm1_y = rule2 + 306      # small row 1
    sm2_y = rule2 + 438      # small row 2
    band_y = rule2 + 570     # bottom band header
    date_y = rule2 + 812     # DATE CHECK box top
    src_y = rule2 + 868      # sources line
    foot_y = rule2 + 896     # footer

    # ---- number strip
    d.line([(10, rule2), (1014, rule2)], fill=RULE, width=2)
    cell_w = 1004 / 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = 10 + i * cell_w
        if i:
            d.line([(x, num_y), (x, num_y + 42)], fill=(200, 190, 165), width=1)
        d.text((x + 6, num_y), num, font=inter(28, 700), fill=RED)
        d.text((x + 6, num_y + 34), cap, font=inter(10.5, 400), fill=INK)

    # ---- region bar (20 px tall so labels read larger)
    total = sum(c for _, c, _ in REGIONS)
    widths = [1004 * c / total for _, c, _ in REGIONS]
    widths[5] = 72          # OCEANIA 2: widen so its label fits
    widths[0] -= 72 - 1004 * 2 / total
    x = 10
    for (label, _c, color), wd in zip(REGIONS, widths):
        d.rectangle([x, reg_y, x + wd, reg_y + 20], fill=color)
        lf = autofit_font(lambda s: franklin(s, 700), label, 11, wd - 4,
                          min_size=7)
        d.text((x + (wd - text_w(lf, label)) / 2, reg_y + 4), label, font=lf,
               fill=WHITE)
        x += wd

    # ---- UTC timeline
    d.rectangle([10, tl_y, 84, tl_y + 26], fill=RED)
    tf = franklin(10, 700)
    d.text((47 - text_w(tf, "THE DAY") / 2, tl_y + 3), "THE DAY", font=tf,
           fill=WHITE)
    d.text((47 - text_w(tf, "IN UTC") / 2, tl_y + 15), "IN UTC", font=tf,
           fill=WHITE)
    ev_w = (1014 - 92) / 6
    for i, (t, label) in enumerate(TIMELINE):
        ex = 92 + i * ev_w
        if i:
            d.line([(ex, tl_y + 2), (ex, tl_y + 24)], fill=(200, 190, 165),
                   width=1)
        d.text((ex + 6, tl_y + 2), t, font=inter(13, 700), fill=NAVY)
        d.text((ex + 6, tl_y + 17), label, font=inter(10.5, 400), fill=INK)
    d.line([(10, rule3), (1014, rule3)], fill=RULE, width=1)

    # ---- leads
    lead_w, lead_x = 328, [10, 348, 686]
    for s, x in zip(LEADS, lead_x):
        img.paste(scene_img(s["scene"], lead_w, 100), (x, lead_y))
        kicker_strip(d, x, lead_y, s["strip"], font=franklin(11, 700))
        caption_chip(d, x + 6, lead_y + 100 - 21, s["caption"])
        d.text((x, lead_y + 104), s["kicker"], font=franklin(10.5, 700),
               fill=RED)
        _tf = franklin(10.5, 700)
        d.text((x + lead_w - text_w(_tf, s["tag"]), lead_y + 104),
               s["tag"], font=_tf, fill=RED)
        hf = None
        for size in (18, 17, 16, 15):
            f = playfair(size, 800)
            if len(wrap(s["headline"], f, lead_w)) <= 2:
                hf = f
                break
        y = lead_y + 117
        for ln in wrap(s["headline"], hf, lead_w)[:2]:
            d.text((x, y), ln, font=hf, fill=INK)
            y += 21
        draw_wrapped(d, x, lead_y + 161, s["deck"], inter(11.5, 400), INK,
                     lead_w, 3, 15)

    # ---- small stories (two rows of five)
    col_w, col_x = 196, [10 + i * 202 for i in range(5)]
    for row, stories in enumerate([SMALL[:5], SMALL[5:]]):
        y0 = sm1_y + row * 132
        for s, x in zip(stories, col_x):
            img.paste(scene_img(s["scene"], col_w, 52), (x, y0))
            kicker_strip(d, x, y0, s["strip"], font=franklin(10.5, 700))
            d.text((x, y0 + 56), s["kicker"], font=franklin(9.5, 700),
                   fill=RED)
            _tf2 = franklin(9.5, 700)
            d.text((x + col_w - text_w(_tf2, s["tag"]), y0 + 56),
                   s["tag"], font=_tf2, fill=RED)
            hf = None
            for size in (14, 13, 12):
                f = playfair(size, 800)
                if len(wrap(s["headline"], f, col_w)) <= 2:
                    hf = f
                    break
            y = y0 + 68
            for ln in wrap(s["headline"], hf, col_w)[:2]:
                d.text((x, y), ln, font=hf, fill=INK)
                y += 15.5
            draw_wrapped(d, x, y0 + 100, s["deck"], inter(11, 400), INK,
                         col_w, 2, 13.5)

    # ---- bottom band: dot map + ALSO list
    d.text((10, band_y), "WHERE IT HAPPENED", font=franklin(12, 700), fill=INK)
    d.text((150, band_y + 2), "pins match story numbers",
           font=inter(10, 400), fill=INK)
    draw_dot_map(d, 12, band_y + 22, 268, 184)
    d.text((10, band_y + 212), "Each number is the story with that number.",
           font=inter(10, 400), fill=INK)

    d.text((292, band_y), "ALSO ON 23–24 NOVEMBER — 27 MORE STORIES",
           font=franklin(12, 700), fill=INK)
    # pick the largest ALSO font that fits the list area
    col_w2, gap2 = 354, 14
    cols = [ALSO[:14], ALSO[14:]]
    avail = date_y - (band_y + 22) - 2
    for size, lh in [(12, 15), (11.5, 14.5), (11, 14), (10.5, 13.5)]:
        bf, nf = inter(size, 400), inter(size, 700)
        wrapped = []
        for col in cols:
            cw = []
            for num, head, src in col:
                text = f"{head} ({src})"
                cw.append(wrap(text, bf, col_w2 - text_w(nf, f"{num} ") - 4))
            wrapped.append(cw)
        total_h = 0
        for i in range(14):
            li = len(wrapped[0][i]) if i < len(wrapped[0]) else 1
            ri = len(wrapped[1][i]) if i < len(wrapped[1]) else 1
            total_h += max(li, ri) * lh + 1
        if total_h <= avail:
            break
    y = band_y + 22
    for i in range(14):
        row_h = 0
        for ci, col in enumerate(cols):
            if i >= len(col):
                continue
            num, head, src = col[i]
            cx = 292 + ci * (col_w2 + gap2)
            lines = wrapped[ci][i]
            d.text((cx, y), f"{num}", font=nf, fill=RED)
            ly = y
            for ln in lines:
                d.text((cx + text_w(nf, f"{num} ") + 4, ly), ln, font=bf,
                       fill=INK)
                ly += lh
            row_h = max(row_h, len(lines) * lh)
        y += row_h + 1

    # ---- DATE CHECK
    d.rectangle([10, date_y, 1014, date_y + 52], outline=RED, width=2)
    d.text((18, date_y + 5), "DATE CHECK", font=franklin(11, 700), fill=RED)
    draw_wrapped(d, 18, date_y + 21, DATE_CHECK, inter(10.5, 400), INK, 988,
                 3, 13.5)

    # ---- sources + footer
    d.text((10, src_y), SOURCES, font=inter(10, 400), fill=INK)
    _tpf = franklin(10, 700)
    _tag_prefix = "HOW TO READ THE TAGS — "
    d.text((10, src_y + 13), _tag_prefix, font=_tpf, fill=RED)
    d.text((10 + text_w(_tpf, _tag_prefix), src_y + 13), TAGS,
           font=inter(10, 400), fill=INK)
    d.text((10, foot_y), "THE WORLD IN ONE DAY", font=franklin(11, 700),
           fill=INK)
    ft = "TUESDAY 24 NOVEMBER 2026  •  ONE PAGE"
    ff = franklin(11, 700)
    d.text((1014 - text_w(ff, ft), foot_y), ft, font=ff, fill=INK)

    return img


def main():
    img = build()
    out = HERE / "output" / "entry.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
