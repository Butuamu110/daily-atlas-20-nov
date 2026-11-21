#!/usr/bin/env python3
"""THE DAILY ATLAS — variant D of the make.fun News Image entry for
Friday 20 November 2026. Deterministic Pillow composition, stdlib + PIL
only, no network. Draws a 1024x1024 gazetteer-style page: masthead,
UTC timeline, the day in numbers, region counts, 13 pictured stories,
a wide hero map of real country polygons with numbered pins, 27 briefs,
a date-check box and a footer. Every fact comes from the shared pool.
Run: python3 draw.py  ->  writes entry.png beside this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from mapdata import WORLD

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
M = 24                      # page margin
CW = W - 2 * M              # content width = 976

# ---- palette (atlas / gazetteer identity) ----
BG     = (243, 234, 211)    # parchment
PAPER  = (250, 246, 233)    # card paper
INK    = (38, 51, 42)       # ink green-black
FOREST = (31, 81, 48)       # forest green
BURG   = (123, 45, 38)      # burgundy
RULE   = (178, 164, 128)    # hairline tan
CARDB  = (196, 184, 152)    # card border
MAPBG  = (24, 54, 38)       # deep green map panel
LAND   = (168, 191, 165)    # sage land
PARCH  = (243, 234, 211)    # parchment text on dark
GOLD   = (201, 162, 39)

REGIONS = {
    "EUROPE":   (176, 58, 46),
    "ASIA":     (29, 111, 184),
    "MIDEAST":  (125, 60, 152),
    "AFRICA":   (30, 132, 73),
    "AMERICAS": (202, 111, 30),
    "OCEANIA":  (20, 143, 119),
    "GLOBAL":   (93, 109, 126),
}

# ---- fonts ----
def _font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)

_cache = {}
def PF(size):   # Playfair Display 900 — headlines, masthead, numbers
    return _cache.setdefault(("pf", size), _font("PlayfairDisplay-900.ttf", size))
def AB(size):   # Archivo Bold — labels, chips, briefs heads
    return _cache.setdefault(("ab", size), _font("Archivo-Bold.ttf", size))
def AM(size):   # Archivo Medium — decks, body
    return _cache.setdefault(("am", size), _font("Archivo-Medium.ttf", size))

# ---- pool data: numbers strip + timeline + region counts (verbatim) ----
NUMBERS = [
    ("3",        "bridges over the Dnipro damaged in Kyiv"),
    ("300,000+", "people moved to shelters before Akvan"),
    ("-6.2%",    "Taiwan's share index, Friday's close"),
    ("100,000",  "youth visas a year in the UK-EU deal"),
    ("$120bn",   "adaptation finance gap left open at COP31"),
    ("118",      "runs by Glenn Phillips against India"),
]
TIMELINE = [
    ("OVERNIGHT", "Kyiv barrage: seven waves from 01:25 local"),
    ("02:30 UTC", "Cyclone Akvan makes landfall in Odisha"),
    ("06:00 UTC", "Tokyo close: Nikkei -5.1% in the AI sell-off"),
    ("MIDDAY",    'Brussels: UK and EU seal the "reset" deal'),
    ("EVENING",   "Wellington: Phillips completes 118 vs India"),
]
REGION_COUNTS = [
    ("EUROPE", 9), ("ASIA", 10), ("MIDEAST", 3), ("AFRICA", 5),
    ("AMERICAS", 5), ("OCEANIA", 3), ("GLOBAL", 5),
]

# ---- pool data: the 13 pictured stories ----
# deck = pool deck (leads verbatim incl. sources; feature decks trimmed
# only where the column cannot hold them, always keeping >= 2 facts).
CARDS = [
 dict(no=1, place="KYIV, UKRAINE", region="EUROPE", topic="WAR",
      headline="Russian missiles hit three Kyiv bridges",
      deck="An overnight barrage of about 110 missiles and 400 drones killed at least nine people across Ukraine and cut power and water in the capital. (Kyiv Independent, BBC)",
      tag="Officials' count", label="3 BRIDGES HIT",
      caption="KYIV - DNIPRO RIVER", lon=30.5, lat=50.4, scene="kyiv"),
 dict(no=2, place="ODISHA, INDIA", region="ASIA", topic="WEATHER",
      headline="Cyclone Akvan comes ashore in eastern India",
      deck="The storm crossed the coast near Gopalpur from about 8 am after more than 300,000 people were moved to shelters. No deaths were reported. (IMD, Deccan Herald)",
      tag="Weather office", label="LANDFALL - 8 AM",
      caption="GOPALPUR - ODISHA COAST", lon=84.9, lat=19.3, scene="cyclone"),
 dict(no=3, place="TAIPEI - SEOUL - TOKYO", region="ASIA", topic="MARKETS",
      headline="AI sell-off sinks Asia's stock markets",
      deck="Taiwan's index fell 6.2% to end its worst week since 1991. Seoul lost 5.2% and Tokyo 5.1% as chipmakers led the slide. (Al Jazeera, Anadolu)",
      tag="Closing prices", label="TAIPEI -6.2% - SEOUL -5.2% - TOKYO -5.1% - HONG KONG -1.9%",
      caption="TAIPEI - SEOUL - TOKYO", lon=121.0, lat=25.0, scene="markets"),
 dict(no=4, place="BRUSSELS", region="EUROPE", topic="DIPLOMACY",
      headline='UK and EU seal a "reset" deal',
      deck="Food trade, youth visas, carbon link. 100,000 youth visas a year.",
      tag="Agreed - Reuters", label="AGREED",
      caption="BRUSSELS - RESET DEAL", lon=4.3, lat=50.8, scene="flags"),
 dict(no=5, place="ANTALYA", region="GLOBAL", topic="CLIMATE",
      headline="COP31 reaches its last day with no deal",
      deck="Draft omits fossil fuels; $120bn adaptation gap unresolved.",
      tag="Ongoing - UN News", label="NO DEAL - FINAL DAY",
      caption="ANTALYA - FINAL DAY", lon=30.7, lat=36.9, scene="cop"),
 dict(no=6, place="EASTERN POLAND", region="EUROPE", topic="WAR",
      headline="Russian cruise missile lands in Poland",
      deck="It fell in a field; two airports paused in the Kyiv barrage.",
      tag="Minister says - Reuters", label="FELL IN A FIELD",
      caption="EASTERN POLAND - FIELD", lon=22.5, lat=51.2, scene="field"),
 dict(no=7, place="CENTRAL IRAQ", region="MIDEAST", topic="CONFLICT",
      headline="Iraqi army enters militia stronghold",
      deck="Troops deploy to Jurf al-Sakhar - first push there in years.",
      tag="Witnessed - Reuters", label="JURF AL-SAKHAR",
      caption="JURF AL-SAKHAR - CENTRAL IRAQ", lon=44.2, lat=32.9, scene="iraq"),
 dict(no=8, place="ITALY", region="EUROPE", topic="LABOUR",
      headline="General strike over Italy's budget",
      deck="Marches in about 100 squares in a 24-hour CGIL stoppage.",
      tag="Reported - Reuters", label="SCIOPERO - 24H",
      caption="ITALY - 100 SQUARES", lon=12.5, lat=41.9, scene="strike"),
 dict(no=9, place="TOKYO", region="ASIA", topic="ECONOMY",
      headline="Japan's inflation picks up to 2.3%",
      deck="Inflation 2.3% in October, up from 2.1% - above target again.",
      tag="Official data - Reuters", label="CPI +2.3% OCT",
      caption="TOKYO - OCTOBER CPI", lon=139.7, lat=35.7, scene="bars"),
 dict(no=10, place="SEOUL", region="ASIA", topic="POLITICS",
      headline="Korea's ruling party to impeach top judge",
      deck="The party voted to impeach Chief Justice Cho Hee-dae.",
      tag="Party decision - Korea Herald", label="CAUCUS VOTE",
      caption="SEOUL - NATIONAL ASSEMBLY", lon=127.0, lat=37.6, scene="court"),
 dict(no=11, place="TURKANA, KENYA", region="AFRICA", topic="ENERGY",
      headline="Kenya starts drilling its first oil well",
      deck="Turkana field ceremony held; first crude due 1 December.",
      tag="Ceremony held - allAfrica", label="FIRST CRUDE 1 DEC",
      caption="TURKANA - FIRST WELL", lon=35.9, lat=3.1, scene="oil"),
 dict(no=12, place="SAN SALVADOR", region="AMERICAS", topic="POLITICS",
      headline="Bukele files to run for a third term",
      deck="Filed with the tribunal Friday; vote is 28 February 2027. (AP)",
      tag="Filed - AP", label="VOTE 28 FEB 2027",
      caption="SAN SALVADOR - TRIBUNAL", lon=-89.2, lat=13.7, scene="ballot"),
 dict(no=13, place="WELLINGTON", region="OCEANIA", topic="CRICKET",
      headline="Phillips hits 118 against India",
      deck="Phillips 118, Nicholls 175 - a stand of 216. (ICC)",
      tag="Scorecard - ICC", label="118 - RECORD",
      caption="WELLINGTON - BASIN RESERVE", lon=174.8, lat=-41.3, scene="cricket"),
]

# ---- pool data: briefs 14-40 (text verbatim, source in parens) ----
# region is used only for the colour of the brief's dot on the map.
BRIEFS = [
 (14, "Lviv A strike on a railway station kills two (BBC)", "EUROPE", 24.0, 49.8),
 (15, "Moscow Russia decries Estonia's border closure (Reuters)", "ASIA", 37.6, 55.8),
 (16, "Berlin School pupils strike against military service (Al Jazeera)", "EUROPE", 13.4, 52.5),
 (17, "London General says UK runs cyber attacks abroad (Sky News)", "EUROPE", -0.1, 51.5),
 (18, "Beijing China holds its loan rates for an 18th month (Xinhua)", "ASIA", 116.4, 39.9),
 (19, "Tokyo SoftBank shares fall more than 14% in a day (Al Jazeera)", "ASIA", 139.7, 35.7),
 (20, "Seoul Kospi index ends the week 7.9% lower (Anadolu)", "ASIA", 127.0, 37.6),
 (21, "Ganjam 209 mm of rain falls as Akvan crosses Odisha (PTI)", "ASIA", 84.9, 19.3),
 (22, "Lebanon Israeli air strikes hit the south and the east (Anadolu)", "MIDEAST", 35.5, 33.3),
 (23, "Yemen Gunmen fire on a cargo ship off the coast (UKMTO)", "GLOBAL", 43.3, 11.8),
 (24, "Abuja Court bars new evidence against Tinubu (Channels TV)", "AFRICA", 7.5, 9.1),
 (25, "Kampala Police told to enforce Ebola ban on rallies (allAfrica)", "AFRICA", 32.6, 0.3),
 (26, "Malawi Fuel crisis brings night-long petrol queues (Al Jazeera)", "AFRICA", 33.8, -13.9),
 (27, "Africa AfDB says 22 countries are in debt distress (allAfrica)", "AFRICA", 20.0, 5.0),
 (28, "Las Vegas Russell fastest in wet Grand Prix practice (Autosport)", "AMERICAS", -115.1, 36.2),
 (29, "New York Nasdaq futures fall 1.6% before the bell (24/7 Wall St)", "AMERICAS", -74.0, 40.7),
 (30, "Washington Democrats query law firm's free work (Al Jazeera)", "AMERICAS", -77.0, 38.9),
 (31, "Sydney Australian shares fall 1.6% in the sell-off (Reuters)", "OCEANIA", 151.2, -33.9),
 (32, "Antalya Panama asks COP31 to cap world oil output (Al Jazeera)", "GLOBAL", 30.7, 36.9),
 (33, "Antalya EU official calls the climate draft unacceptable (RTE)", "GLOBAL", 30.7, 36.9),
 (34, "Turin ATP backs a plan to lift player pay past $350m (Anadolu)", "EUROPE", 7.7, 45.1),
 (35, "Bougainville Rio Tinto pledges $370m for Panguna mine cleanup (Reuters)", "OCEANIA", 155.9, -6.3),
 (36, "Iowa US Army sets noon detonation of 68 unstable explosive barrels (AP)", "AMERICAS", -93.6, 41.9),
 (37, "Hormuz Four attacks on vessels in 96 hours, maritime centre says (UKMTO)", "MIDEAST", 56.3, 26.6),
 (38, "Jakarta Indonesia's parliament passes asset-forfeiture bill (Reuters)", "ASIA", 106.8, -6.2),
 (39, "Barcelona Pancreatic cancer pill shrinks tumours 60.7% in early trial (Reuters)", "EUROPE", 2.2, 41.4),
 (40, "Mercury BepiColombo reaches Mercury after 8 years; orbit insertion set for Saturday (ESA, BBC)", "GLOBAL", None, None),
]

DATE_CHECK = ("Left out as Thursday 19 November's news: the World Court's ruling on Myanmar, "
 "the three-leader declaration in Shenzhen, the migrant boat lost off Senegal, Anthropic's "
 "$83bn IPO pricing, the GTA VI midnight launch, the $190.4m Van Gogh sale and the Senate's "
 "48-51 Iran war-powers vote. Not yet happened, so not shown: COP31's final text and "
 "BepiColombo's entry into orbit around Mercury (set for Saturday).")
FOOTER_L = "Every story here happened, or was first reported, on Friday 20 November 2026. Contested claims are attributed."
FOOTER_R = "Sources named beside each story - original drawings"

# ---- text helpers ----
def tw(d, s, f):
    return d.textlength(s, font=f)

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines

def fit(d, s, name, start, maxw, floor=8):
    """Largest Archivo-Bold size <= start whose width fits maxw."""
    size = start
    while size > floor and tw(d, s, AB(size)) > maxw:
        size -= 1
    return AB(size)

def ctext(d, cx, y, s, f, fill):
    d.text((cx - tw(d, s, f) / 2, y), s, font=f, fill=fill)

# ---- flat illustration scenes (drawn inside the strip box) ----
def sc_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(43, 56, 84))
    river_y = y + int(h * 0.72)
    d.rectangle([x, river_y, x + w, y + h], fill=(52, 92, 122))
    for i in range(3):  # three bridges: deck + arc + piers
        bx = x + int(w * (0.10 + 0.30 * i)); bw = int(w * 0.24)
        by = river_y - int(h * (0.10 + 0.07 * i))
        d.line([bx, by, bx + bw, by], fill=(232, 220, 180), width=2)
        d.arc([bx, by - int(h * 0.16), bx + bw, by + int(h * 0.16)], 180, 360, fill=(232, 220, 180), width=1)
        d.line([bx + bw // 2, by, bx + bw // 2, river_y + 4], fill=(200, 190, 160), width=1)
    for i in range(3):  # missile arcs + bursts
        sx = x + int(w * (0.62 + 0.12 * i)); sy = y + 3
        ex = x + int(w * (0.24 + 0.26 * i)); ey = river_y - int(h * 0.22)
        for t in range(0, 11, 2):
            px = sx + (ex - sx) * t / 10; py = sy + (ey - sy) * t / 10 - int(h * 0.18) * (1 - abs(t / 5 - 1))
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 190, 90))
        d.polygon([(ex - 4, ey), (ex, ey - 5), (ex + 4, ey), (ex, ey + 5)], fill=(255, 160, 60))

def sc_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(84, 118, 148))
    d.rectangle([x, y + int(h * 0.66), x + w, y + h], fill=(46, 84, 110))
    cx, cy = x + int(w * 0.62), y + int(h * 0.40)
    for r in (int(h * 0.34), int(h * 0.24), int(h * 0.14)):
        d.arc([cx - r, cy - int(r * 0.62), cx + r, cy + int(r * 0.62)], 20, 300, fill=(235, 240, 244), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255))
    for i in range(9):  # rain streaks
        rx = x + 6 + i * (w - 12) // 9; ry = y + int(h * (0.12 + 0.09 * (i % 3)))
        d.line([rx, ry, rx - 3, ry + 6], fill=(200, 220, 235), width=1)
    shore = y + int(h * 0.66)
    for i in range(3):  # shelter tents on the shore
        tx = x + int(w * (0.06 + 0.13 * i)); tw_ = max(10, int(w * 0.10))
        d.polygon([(tx, shore), (tx + tw_ // 2, shore - int(h * 0.16)), (tx + tw_, shore)], fill=(240, 200, 120))

def sc_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(29, 33, 43))
    for i in range(1, 4):
        gy = y + int(h * i / 4)
        d.line([x + 3, gy, x + w - 3, gy], fill=(58, 66, 80), width=1)
    pts = [(0.04, 0.22), (0.24, 0.30), (0.42, 0.26), (0.60, 0.48), (0.78, 0.55), (0.96, 0.78)]
    xy = [(x + int(w * fx), y + int(h * fy)) for fx, fy in pts]
    d.line(xy, fill=(232, 76, 60), width=2)
    for px, py in xy:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(232, 76, 60))
    ax, ay = xy[-1]
    d.polygon([(ax - 4, ay - 5), (ax + 5, ay - 4), (ax, ay + 4)], fill=(232, 76, 60))

def sc_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(112, 146, 186))
    d.rectangle([x, y + int(h * 0.80), x + w, y + h], fill=(90, 120, 84))
    def flag(fx, fw, fh, eu):
        fy = y + int(h * 0.16)
        d.line([fx, fy, fx, y + int(h * 0.82)], fill=(60, 54, 44), width=2)
        d.rectangle([fx + 2, fy, fx + 2 + fw, fy + fh], fill=(36, 52, 120))
        if eu:
            import math
            ccx, ccy, rr = fx + 2 + fw / 2, fy + fh / 2, fh * 0.30
            for k in range(8):
                a = 2 * math.pi * k / 8
                sx, sy = ccx + rr * math.cos(a), ccy + rr * math.sin(a)
                d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(245, 197, 24))
        else:
            d.line([fx + 2, fy, fx + 2 + fw, fy + fh], fill=(240, 240, 240), width=2)
            d.line([fx + 2, fy + fh, fx + 2 + fw, fy], fill=(240, 240, 240), width=2)
            d.rectangle([fx + 2 + fw // 2 - 2, fy, fx + 2 + fw // 2 + 2, fy + fh], fill=(200, 40, 50))
            d.rectangle([fx + 2, fy + fh // 2 - 2, fx + 2 + fw, fy + fh // 2 + 2], fill=(200, 40, 50))
    fw, fh = int(w * 0.30), int(h * 0.40)
    flag(x + int(w * 0.10), fw, fh, eu=False)
    flag(x + int(w * 0.56), fw, fh, eu=True)

def sc_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(86, 128, 156))
    gx, gy, gr = x + int(w * 0.30), y + int(h * 0.48), int(h * 0.34)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 90))
    d.ellipse([gx - gr * 0.55, gy - gr * 0.5, gx - gr * 0.05, gy - gr * 0.05], fill=(120, 160, 90))
    d.ellipse([gx + gr * 0.1, gy + gr * 0.05, gx + gr * 0.6, gy + gr * 0.55], fill=(120, 160, 90))
    tx = x + int(w * 0.68); tw_ = max(5, int(w * 0.05))
    d.rectangle([tx, y + int(h * 0.14), tx + tw_, y + int(h * 0.66)], outline=(240, 240, 240), width=2)
    d.rectangle([tx + 1, y + int(h * 0.40), tx + tw_ - 1, y + int(h * 0.66)], fill=(220, 70, 50))
    d.ellipse([tx - 3, y + int(h * 0.62), tx + tw_ + 3, y + int(h * 0.62) + tw_ + 6], fill=(220, 70, 50))
    d.rectangle([x, y + int(h * 0.86), x + w, y + h], fill=(60, 96, 120))

def sc_field(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(140, 170, 100))
    for i in range(4):
        fy = y + int(h * (0.30 + 0.17 * i))
        d.line([x, fy, x + w, fy - int(h * 0.05)], fill=(110, 140, 74), width=2)
    mx, my = x + int(w * 0.60), y + int(h * 0.34)  # fallen missile, diagonal
    d.polygon([(mx, my), (mx + int(w * 0.26), my + int(h * 0.20)), (mx + int(w * 0.23), my + int(h * 0.30)), (mx - int(w * 0.03), my + int(h * 0.10))], fill=(150, 152, 156))
    d.polygon([(mx - int(w * 0.03), my + int(h * 0.10)), (mx - int(w * 0.09), my + int(h * 0.02)), (mx - int(w * 0.08), my + int(h * 0.16))], fill=(110, 112, 118))
    d.ellipse([mx + int(w * 0.16), my + int(h * 0.30), mx + int(w * 0.30), my + int(h * 0.40)], outline=(90, 80, 60), width=2)

def sc_iraq(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(206, 178, 128))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(188, 152, 96))
    def vehicle(vx, vy, s):
        d.rectangle([vx, vy, vx + int(34 * s), vy + int(10 * s)], fill=(96, 96, 70))
        d.rectangle([vx + int(22 * s), vy - int(6 * s), vx + int(32 * s), vy], fill=(80, 80, 58))
        for wx in (vx + int(7 * s), vx + int(26 * s)):
            d.ellipse([wx - int(4 * s), vy + int(7 * s), wx + int(4 * s), vy + int(15 * s)], fill=(40, 40, 36))
    s = max(0.5, h / 90)
    vehicle(x + int(w * 0.14), y + int(h * 0.44), s)
    vehicle(x + int(w * 0.55), y + int(h * 0.50), s * 0.85)

def sc_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 108, 92))
    bx0, bx1 = x + int(w * 0.30), x + int(w * 0.78)  # plain banner
    d.rectangle([bx0, y + int(h * 0.14), bx1, y + int(h * 0.40)], fill=(246, 240, 220))
    d.line([bx0, y + int(h * 0.14), bx0, y + h], fill=(70, 54, 44), width=1)
    d.line([bx1, y + int(h * 0.14), bx1, y + h], fill=(70, 54, 44), width=1)
    for i in range(7):  # crowd silhouettes
        hx = x + int(w * (0.05 + 0.135 * i)); hy = y + int(h * 0.66)
        r = max(3, int(h * 0.10))
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(52, 44, 40))
        d.rectangle([hx - r - 1, hy + r - 1, hx + r + 1, y + h], fill=(52, 44, 40))

def sc_bars(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 46, 56))
    base = y + int(h * 0.84)
    d.line([x + 4, base, x + w - 4, base], fill=(200, 200, 200), width=1)
    for i, fh in enumerate((0.34, 0.52, 0.72)):
        bx = x + int(w * (0.18 + 0.26 * i)); bw = int(w * 0.16)
        d.rectangle([bx, base - int(h * fh), bx + bw, base], fill=(226, 110, 60) if i < 2 else (232, 76, 60))

def sc_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(104, 116, 138))
    cx = x + w // 2
    d.polygon([(cx - int(w * 0.34), y + int(h * 0.30)), (cx + int(w * 0.34), y + int(h * 0.30)), (cx, y + int(h * 0.08))], fill=(226, 222, 208))
    d.rectangle([cx - int(w * 0.34), y + int(h * 0.32), cx + int(w * 0.34), y + int(h * 0.38)], fill=(226, 222, 208))
    for i in range(4):
        cxx = cx - int(w * 0.27) + i * int(w * 0.18)
        d.rectangle([cxx, y + int(h * 0.40), cxx + int(w * 0.07), y + int(h * 0.78)], fill=(238, 236, 226))
    d.rectangle([cx - int(w * 0.36), y + int(h * 0.80), cx + int(w * 0.36), y + int(h * 0.88)], fill=(226, 222, 208))

def sc_oil(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 164, 108))
    d.rectangle([x, y + int(h * 0.78), x + w, y + h], fill=(120, 92, 58))
    cx = x + int(w * 0.42); top = y + int(h * 0.10); bot = y + int(h * 0.80); hw = int(w * 0.20)
    d.line([cx - hw, bot, cx, top], fill=(52, 48, 44), width=2)
    d.line([cx + hw, bot, cx, top], fill=(52, 48, 44), width=2)
    d.line([cx - hw * 0.6, y + int(h * 0.52), cx + hw * 0.6, y + int(h * 0.52)], fill=(52, 48, 44), width=1)
    d.line([cx - hw * 0.6, y + int(h * 0.52), cx, top], fill=(52, 48, 44), width=1)
    d.line([cx + hw * 0.6, y + int(h * 0.52), cx, top], fill=(52, 48, 44), width=1)
    d.rectangle([cx - 3, top - 3, cx + 3, top + 3], fill=(52, 48, 44))
    d.rectangle([x + int(w * 0.68), y + int(h * 0.60), x + int(w * 0.84), y + int(h * 0.78)], fill=(90, 74, 50))

def sc_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(96, 118, 96))
    bx0, bx1 = x + int(w * 0.30), x + int(w * 0.72)
    by0, by1 = y + int(h * 0.44), y + int(h * 0.86)
    d.rectangle([bx0, by0, bx1, by1], fill=(226, 220, 200))
    d.rectangle([bx0 + int(w * 0.06), by0 + int(h * 0.08), bx1 - int(w * 0.06), by0 + int(h * 0.15)], fill=(52, 48, 44))
    px0 = x + int(w * 0.40)  # ballot paper sliding into the slot
    d.polygon([(px0, by0 - int(h * 0.26)), (px0 + int(w * 0.20), by0 - int(h * 0.30)), (px0 + int(w * 0.20), by0 - int(h * 0.02)), (px0, by0 + int(h * 0.02))], fill=(250, 250, 246))
    d.line([px0 + int(w * 0.04), by0 - int(h * 0.16), px0 + int(w * 0.09), by0 - int(h * 0.08)], fill=(31, 81, 48), width=2)
    d.line([px0 + int(w * 0.09), by0 - int(h * 0.08), px0 + int(w * 0.17), by0 - int(h * 0.22)], fill=(31, 81, 48), width=2)

def sc_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(92, 142, 82))
    d.rectangle([x + int(w * 0.28), y, x + int(w * 0.72), y + h], fill=(198, 172, 112))
    sx = x + int(w * 0.60)  # stumps
    for i in range(3):
        d.line([sx + i * 4 - 4, y + int(h * 0.30), sx + i * 4 - 4, y + int(h * 0.72)], fill=(240, 230, 190), width=2)
    d.line([sx - 5, y + int(h * 0.28), sx + 5, y + int(h * 0.28)], fill=(240, 230, 190), width=1)
    d.polygon([(x + int(w * 0.10), y + int(h * 0.78)), (x + int(w * 0.20), y + int(h * 0.74)), (x + int(w * 0.34), y + int(h * 0.30)), (x + int(w * 0.28), y + int(h * 0.26))], fill=(214, 178, 120))
    bx, by = x + int(w * 0.82), y + int(h * 0.34)  # ball
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(196, 40, 44))
    d.arc([bx - 3, by - 3, bx + 3, by + 3], 100, 260, fill=(250, 220, 220), width=1)

SCENES = {"kyiv": sc_kyiv, "cyclone": sc_cyclone, "markets": sc_markets,
          "flags": sc_flags, "cop": sc_cop, "field": sc_field, "iraq": sc_iraq,
          "strike": sc_strike, "bars": sc_bars, "court": sc_court,
          "oil": sc_oil, "ballot": sc_ballot, "cricket": sc_cricket}

# ---- strip furniture: accent rule, source tag (top-right), data label
# chip (bottom-left), caption band (bottom edge). Zones never overlap. ----
def draw_strip(d, card, x, y, w, h, lead=False):
    SCENES[card["scene"]](d, x, y, w, h)
    rc = REGIONS[card["region"]]
    d.rectangle([x, y, x + w, y + 3], fill=rc)
    band_h = 16 if lead else 12
    d.rectangle([x, y + h - band_h, x + w, y + h], fill=INK)
    cf = fit(d, card["caption"], "ab", 10 if lead else 9, w - 10)
    ctext(d, x + w / 2, y + h - band_h + (1 if lead else 0), card["caption"], cf, PARCH)
    tag_f = AB(9 if lead else 8)
    tag_w = tw(d, card["tag"], tag_f) + 8
    ty = y + 5 if lead else y + 2
    d.rectangle([x + w - tag_w - 3, ty, x + w - 3, ty + (13 if lead else 11)], fill=INK)
    d.text((x + w - tag_w + 1, ty + 1), card["tag"], font=tag_f, fill=PARCH)
    lab_f = fit(d, card["label"], "ab", 12 if lead else 10, w - 12)
    lab_w = tw(d, card["label"], lab_f) + 9
    lab_h = 16 if lead else 13
    ly = y + h - band_h - lab_h - 2
    d.rectangle([x + 3, ly, x + 3 + lab_w, ly + lab_h], fill=BURG)
    d.text((x + 7, ly + 2), card["label"], font=lab_f, fill=(255, 255, 255))

def draw_card(d, card, x, y, w, strip_h, lead=False):
    d.rectangle([x, y, x + w, y + strip_h], outline=CARDB, width=1)
    draw_strip(d, card, x, y, w, strip_h, lead)
    rc = REGIONS[card["region"]]
    ry = y + strip_h + (5 if lead else 3)
    d.text((x + 1, ry), "%d  %s - %s - %s" % (card["no"], card["place"], card["region"], card["topic"]),
           font=AB(11 if lead else 9), fill=rc)
    hy = ry + (15 if lead else 12)
    hf = PF(22 if lead else 14)
    for ln in wrap(d, card["headline"], hf, w - 2)[:2]:
        d.text((x + 1, hy), ln, font=hf, fill=INK)
        hy += 23 if lead else 15
    df = AM(11)
    for ln in wrap(d, card["deck"], df, w - 2):
        d.text((x + 1, hy + 1), ln, font=df, fill=(64, 74, 62))
        hy += 12.5 if lead else 11
    return hy

# ---- page head ----
def draw_top(d):
    d.rectangle([0, 0, W, 24], fill=FOREST)
    d.text((M, 5), "THE DAILY ATLAS  ·  THE WORLD IN ONE DAY", font=AB(12), fill=PARCH)
    right = "40 STORIES - 7 REGIONS - EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    d.text((W - M - tw(d, right, AB(11)), 6), right, font=AB(11), fill=PARCH)
    ctext(d, W / 2, 30, "Friday 20 November 2026", PF(42), INK)
    ctext(d, W / 2, 76, "Kyiv's bridges hit · Cyclone Akvan ashore in Odisha · an AI sell-off sinks Asian markets · UK and EU seal a reset deal", AM(12), (84, 92, 76))
    d.line([M, 92, W - M, 92], fill=FOREST, width=2)
    # UTC timeline strip
    cw5 = CW / 5
    for i, (lab, ev) in enumerate(TIMELINE):
        cx = M + i * cw5
        if i:
            d.line([cx, 98, cx, 128], fill=RULE, width=1)
        d.text((cx + 8, 93), lab, font=AB(10), fill=FOREST)
        ey = 104
        for ln in wrap(d, ev, AM(10), cw5 - 14)[:2]:
            d.text((cx + 8, ey), ln, font=AM(10), fill=INK)
            ey += 11
    d.line([M, 128, W - M, 128], fill=RULE, width=1)
    # THE DAY IN NUMBERS
    d.text((M, 132), "THE DAY IN NUMBERS", font=AB(10), fill=FOREST)
    cw6 = CW / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cw6
        ctext(d, cx + cw6 / 2, 144, num, PF(25), BURG)
        cy = 173
        for ln in wrap(d, cap, AM(9), cw6 - 8)[:2]:
            ctext(d, cx + cw6 / 2, cy, ln, AM(9), (84, 92, 76))
            cy += 10
    # region count chips
    cw7 = (CW - 6 * 6) / 7
    for i, (name, n) in enumerate(REGION_COUNTS):
        cx = M + i * (cw7 + 6)
        d.rectangle([cx, 196, cx + cw7, 214], fill=REGIONS[name])
        ctext(d, cx + cw7 / 2, 200, "%s %d" % (name, n), AB(10), (255, 255, 255))
    d.line([M, 220, W - M, 220], fill=RULE, width=1)

def draw_cards(d):
    lead_w = (CW - 2 * 12) / 3
    end = 0
    for i, card in enumerate(CARDS[:3]):
        end = max(end, draw_card(d, card, M + i * (lead_w + 12), 224, lead_w, 64, lead=True))
    fy = end + 8
    feat_w = (CW - 4 * 10) / 5
    for r in range(2):
        end = 0
        for c in range(5):
            card = CARDS[3 + r * 5 + c]
            end = max(end, draw_card(d, card, M + c * (feat_w + 10), fy, feat_w, 41, lead=False))
        fy = end + 8
    return fy

# ---- hero map panel (bottom-left, 430 wide) ----
def draw_map(d, top, bottom=960):
    x0, x1 = M, M + 430
    d.rectangle([x0, top, x1, bottom], fill=MAPBG)
    d.text((x0 + 12, top + 7), "WHERE IT HAPPENED", font=AB(12), fill=PARCH)
    mx0, mx1, my0, my1 = x0 + 10, x1 - 10, top + 28, bottom - 30
    def px(lon):
        return mx0 + (lon + 180) / 360 * (mx1 - mx0)
    def py(lat):
        return my0 + (82 - lat) / 140 * (my1 - my0)
    for glon in range(-150, 181, 30):
        d.line([px(glon), my0, px(glon), my1], fill=(36, 74, 52), width=1)
    for glat in range(-45, 76, 15):
        d.line([mx0, py(glat), mx1, py(glat)], fill=(36, 74, 52), width=1)
    for rings in WORLD.values():
        for ring in rings.split("|"):
            pts = []
            for pair in ring.split(","):
                lo, la = pair.split(":")
                pts.append((px(float(lo)), py(float(la))))
            if len(pts) >= 3:
                d.polygon(pts, fill=LAND)
    for no, _t, region, lon, lat in BRIEFS:  # brief dots under the pins
        if lon is not None:
            cx, cy = px(lon), py(lat)
            d.ellipse([cx - 2.2, cy - 2.2, cx + 2.2, cy + 2.2], fill=REGIONS[region])
    for card in CARDS:  # numbered pins for the 13 pictured stories
        cx, cy = px(card["lon"]), py(card["lat"])
        r = 6.5
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=REGIONS[card["region"]], outline=PARCH, width=1)
        s = str(card["no"])
        f = AB(7 if len(s) > 1 else 8)
        d.text((cx - tw(d, s, f) / 2, cy - 4), s, font=f, fill=(255, 255, 255))
    ax0, ay = mx0 + 8, my1 - 8  # exit arrow for story 40 (Mercury)
    for sx in range(int(ax0), int(ax0) + 44, 7):
        d.line([sx, ay, sx + 4, ay], fill=GOLD, width=2)
    d.polygon([(ax0 + 48, ay - 3.5), (ax0 + 56, ay), (ax0 + 48, ay + 3.5)], fill=GOLD)
    d.text((ax0, ay - 15), "40 -> to Mercury", font=AB(9), fill=GOLD)
    d.text((x0 + 12, bottom - 18), "Numbered pins = the 13 pictured stories - small dots = the briefs",
           font=AM(9), fill=PARCH)

# ---- briefs column (bottom-right) ----
def draw_briefs(d, top):
    x = M + 430 + 16
    w = W - M - x
    d.text((x, top + 5), "ALSO ON FRIDAY 20 NOVEMBER - 27 MORE STORIES", font=AB(12), fill=FOREST)
    d.line([x, top + 21, W - M, top + 21], fill=FOREST, width=1)
    y0 = top + 26
    lh = (960 - y0) / len(BRIEFS)
    y = y0
    for no, text, region, _lon, _lat in BRIEFS:
        ns = str(no)
        d.text((x, y), ns, font=AB(10), fill=REGIONS[region])
        off = tw(d, ns, AB(10)) + 5
        lines = wrap(d, text, AM(10), w - off)
        for j, ln in enumerate(lines):
            d.text((x + off if j == 0 else x + off, y + j * 11), ln, font=AM(10), fill=(52, 62, 54))
        y += lh
    return lh

# ---- date check + footer ----
def draw_bottom_bands(d):
    y0, y1 = 966, 1004
    d.rectangle([M, y0, W - M, y1], fill=PAPER, outline=BURG, width=2)
    lab = "DATE CHECK"
    d.text((M + 8, y0 + 5), lab, font=AB(10), fill=BURG)
    tx = M + 8 + tw(d, lab, AB(10)) + 8
    lines = wrap(d, DATE_CHECK, AM(9), (W - M - 8) - tx)[:1]
    rest = wrap(d, DATE_CHECK, AM(9), CW - 16)
    # first line beside the label, remainder full width below
    words = DATE_CHECK.split()
    first, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, AM(9)) <= (W - M - 8) - tx:
            cur = t
        else:
            break
    first = cur
    remainder = DATE_CHECK[len(first):].strip()
    d.text((tx, y0 + 5), first, font=AM(9), fill=INK)
    yy = y0 + 16
    for ln in wrap(d, remainder, AM(9), CW - 16)[:2]:
        d.text((M + 8, yy), ln, font=AM(9), fill=INK)
        yy += 11
    d.text((M, 1010), FOOTER_L, font=AM(9), fill=(84, 92, 76))
    d.text((W - M - tw(d, FOOTER_R, AM(9)), 1010), FOOTER_R, font=AM(9), fill=(84, 92, 76))

def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_top(d)
    bottom_top = draw_cards(d)
    lh = draw_briefs(d, bottom_top)
    draw_map(d, bottom_top)
    draw_bottom_bands(d)
    out = os.path.join(HERE, "entry.png")
    img.save(out)
    print("bottom_top:", bottom_top, "brief leading: %.2f" % lh)
    print("saved", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    build()
