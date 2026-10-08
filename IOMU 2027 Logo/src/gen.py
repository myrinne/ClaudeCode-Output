"""IOMU 2027 logo concepts - hand-built SVG generator.

Writes concepts/<concept>_<palette>_v1.svg. Text is converted to outlines
with fontTools so the SVGs do not depend on installed fonts.
"""
import math
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "fonts")
OUT = os.path.join(ROOT, "concepts")
VERSION = "v1"

PALETTES = {
    "B": {"name": "Emerald Green & Gold", "primary": "#214940", "accent": "#C69C54", "cream": "#F4E9D7"},
    "C": {"name": "Heritage Sogan & Cream", "primary": "#6E442C", "accent": "#B37B56", "cream": "#F4E9D7"},
}

_fonts = {}


def font(name, wght=None):
    key = (name, wght)
    if key not in _fonts:
        f = TTFont(os.path.join(FONTS, name))
        if wght is not None and "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        _fonts[key] = f
    return _fonts[key]


def text_width(f, text, size, tracking=0.0):
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    w = sum(hmtx[cmap[ord(c)]][0] for c in text) * size / upm
    return w + tracking * size * (len(text) - 1)


def text_path(f, text, x, y, size, fill, anchor="start", tracking=0.0):
    """Outlined text; (x, y) is the baseline point given by anchor."""
    upm = f["head"].unitsPerEm
    s = size / upm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    w = text_width(f, text, size, tracking)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    parts = []
    for c in text:
        g = cmap[ord(c)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        parts.append(pen.getCommands())
        x += hmtx[g][0] * s + tracking * size
    return f'<path fill="{fill}" d="{" ".join(parts)}"/>'


def ring_text(f, text, cx, cy, r, size, fill, tracking=0.08, start_deg=-90):
    """Text centred on start_deg, running clockwise along a circle of radius r (baseline)."""
    upm = f["head"].unitsPerEm
    s = size / upm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    total = text_width(f, text, size, tracking)
    ang = math.radians(start_deg) - total / r / 2
    parts = []
    for c in text:
        g = cmap[ord(c)]
        adv = hmtx[g][0] * s
        mid = ang + adv / 2 / r
        px, py = cx + r * math.cos(mid), cy + r * math.sin(mid)
        rot = mid + math.pi / 2
        cr, sr = math.cos(rot), math.sin(rot)
        # glyph local: x from -adv/2, y up -> rotate, then translate
        a, b, c2, d = s * cr, s * sr, s * sr, -s * cr
        e = px - (adv / 2) * cr
        f2 = py - (adv / 2) * sr
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (a, b, c2, d, e, f2)))
        parts.append(pen.getCommands())
        ang += (adv + tracking * size) / r
    return f'<path fill="{fill}" d="{" ".join(parts)}"/>'


# ---------- motifs ----------

def parang_pattern(pid, fg, bg, unit=36, stroke=None):
    """Parang rusak, simplified: diagonal rows of S-blades with mlinjon diamonds."""
    u = unit
    sw = stroke or u * 0.2
    return f'''<pattern id="{pid}" width="{u}" height="{u}" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
  <rect width="{u}" height="{u}" fill="{bg}"/>
  <path d="M{u*0.18} {u*0.95} C{u*0.18} {u*0.55} {u*0.82} {u*0.45} {u*0.82} {u*0.05}" fill="none" stroke="{fg}" stroke-width="{sw}" stroke-linecap="round"/>
  <path d="M{u*0.5} {u*0.08} l{u*0.09} {u*0.09} l-{u*0.09} {u*0.09} l-{u*0.09} -{u*0.09} z" fill="{fg}"/>
</pattern>'''


def kawung(cx, cy, r, fill, inner, rot=0):
    """Four kawung petals pointing N/E/S/W = a cross; small centre dot."""
    out = [f'<g transform="translate({cx} {cy}) rotate({rot})">']
    for a in (0, 90, 180, 270):
        out.append(f'<g transform="rotate({a})">'
                   f'<ellipse cx="0" cy="{-r*0.56}" rx="{r*0.30}" ry="{r*0.44}" fill="{fill}"/>'
                   f'<path d="M{-r*0.06} {-r*0.58} l{r*0.06} {-r*0.08} l{r*0.06} {r*0.08} l{-r*0.06} {r*0.08} z" fill="{inner}"/>'
                   f'</g>')
    out.append(f'<circle r="{r*0.07}" fill="{fill}"/>')
    out.append('</g>')
    return "".join(out)


def rod(cx, y_top, y_bot, staff_w, staff_col, snake_col, gap_col, amp, turns=2.5, snake_w=None):
    """Rod of Asclepius: staff + single snake, head at top right."""
    sw = snake_w or staff_w * 0.9
    out = [f'<rect x="{cx - staff_w/2}" y="{y_top}" width="{staff_w}" height="{y_bot - y_top}" rx="{staff_w/2}" fill="{staff_col}"/>']
    y0, y1 = y_bot - (y_bot - y_top) * 0.08, y_top + (y_bot - y_top) * 0.22
    pts = []
    n = 120
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        x = cx + amp * math.sin(t * turns * 2 * math.pi) * (0.55 + 0.45 * t)
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    out.append(f'<path d="{d}" fill="none" stroke="{gap_col}" stroke-width="{sw + staff_w*0.5}" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<path d="{d}" fill="none" stroke="{snake_col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    hx, hy = pts[-1]
    hx2 = hx + amp * 0.35
    out.append(f'<ellipse cx="{hx2:.2f}" cy="{hy - sw*0.25:.2f}" rx="{sw*1.05}" ry="{sw*0.72}" fill="{snake_col}" transform="rotate(-18 {hx2:.2f} {hy:.2f})"/>')
    out.append(f'<path d="M{hx:.2f} {hy:.2f} L{hx2:.2f} {hy - sw*0.25:.2f}" stroke="{snake_col}" stroke-width="{sw}" stroke-linecap="round"/>')
    return "".join(out)


def helmet(cx, base_y, w, fill, ridge, brim=None):
    """Front view hard hat: dome + centre ridge + brim. base_y = bottom of brim."""
    brim = brim or fill
    h = w * 0.62
    bh = w * 0.11
    dome_b = base_y - bh
    out = [f'<path d="M{cx - w/2} {dome_b} C{cx - w/2} {dome_b - h*1.05} {cx + w/2} {dome_b - h*1.05} {cx + w/2} {dome_b} Z" fill="{fill}"/>',
           f'<path d="M{cx - w*0.08} {dome_b - h*0.78} C{cx - w*0.08} {dome_b - h*0.80} {cx + w*0.08} {dome_b - h*0.80} {cx + w*0.08} {dome_b - h*0.78} L{cx + w*0.07} {dome_b} L{cx - w*0.07} {dome_b} Z" fill="{ridge}"/>',
           f'<rect x="{cx - w*0.64}" y="{dome_b - bh*0.15}" width="{w*1.28}" height="{bh}" rx="{bh/2}" fill="{brim}"/>']
    return "".join(out)


def tower(cx, base_y, w, fill, line):
    """Panggung Sangga Buwana, simplified: base, two galleried tiers, flared roof + finial.
    Returns (svg, roof_base_y)."""
    o = []
    # base block
    o.append(f'<rect x="{cx - w/2}" y="{base_y - w*0.55}" width="{w}" height="{w*0.55}" fill="{fill}"/>')
    for i in range(3):  # arched windows
        x = cx - w*0.3 + i * w*0.3
        o.append(f'<path d="M{x - w*0.07} {base_y} L{x - w*0.07} {base_y - w*0.25} A{w*0.07} {w*0.07} 0 0 1 {x + w*0.07} {base_y - w*0.25} L{x + w*0.07} {base_y} Z" fill="{line}"/>')
    # gallery 1
    y = base_y - w*0.55
    o.append(f'<rect x="{cx - w*0.62}" y="{y - w*0.07}" width="{w*1.24}" height="{w*0.07}" fill="{fill}"/>')
    o.append(f'<rect x="{cx - w*0.36}" y="{y - w*0.52}" width="{w*0.72}" height="{w*0.45}" fill="{fill}"/>')
    for i in range(4):
        x = cx - w*0.27 + i * w*0.18
        o.append(f'<rect x="{x - w*0.035}" y="{y - w*0.42}" width="{w*0.07}" height="{w*0.25}" rx="{w*0.035}" fill="{line}"/>')
    # gallery 2
    y2 = y - w*0.52
    o.append(f'<rect x="{cx - w*0.48}" y="{y2 - w*0.06}" width="{w*0.96}" height="{w*0.06}" fill="{fill}"/>')
    o.append(f'<rect x="{cx - w*0.24}" y="{y2 - w*0.34}" width="{w*0.48}" height="{w*0.28}" fill="{fill}"/>')
    roof_base = y2 - w*0.34
    return "".join(o), roof_base


def svg_doc(w, h, body, bg=None):
    bgr = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{bgr}{body}</svg>'


# ---------- concepts ----------

def c1_series(p):
    """Series layout: IOMU wordmark + year, round emblem on the right."""
    P, A, CR = p["primary"], p["accent"], p["cream"]
    fb = font("Poppins-ExtraBold.ttf")
    b = [parang_pattern("par1", P, A, unit=26)]
    b.append(text_path(fb, "IOMU", 70, 360, 250, P, tracking=-0.01))
    iw = text_width(fb, "IOMU", 250, -0.01)
    b.append(text_path(fb, "2027", 70 + iw, 500, 150, A, anchor="end", tracking=0.0))
    # emblem
    r = 230
    cx, cy = 70 + iw + 60 + r, 310
    W, H = int(cx + r + 70), 620
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{P}"/>')
    # parang crescent (outer circle minus an offset circle) on the lower-left, like the series swoosh
    b.append(f'<clipPath id="cres"><path clip-rule="evenodd" d="M{cx - r} {cy} a{r} {r} 0 1 0 {2*r} 0 a{r} {r} 0 1 0 {-2*r} 0 Z '
             f'M{cx + r*0.14 - r*0.86} {cy - r*0.12} a{r*0.86} {r*0.86} 0 1 0 {2*r*0.86} 0 a{r*0.86} {r*0.86} 0 1 0 {-2*r*0.86} 0 Z"/></clipPath>')
    b.append(f'<rect x="{cx - r}" y="{cy - r}" width="{2*r}" height="{2*r}" fill="url(#par1)" clip-path="url(#cres)"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 3}" fill="none" stroke="{A}" stroke-width="6"/>')
    tw, roof = tower(cx - r*0.08, cy + r*0.6, r*0.66, CR, P)
    b.append(tw)
    # roof = helmet-free conical roof here (series keeps it architectural)
    rw, tx = r*0.66, cx - r*0.08
    b.append(f'<path d="M{tx - rw*0.42} {roof} Q{tx} {roof - rw*0.12} {tx} {roof - rw*0.55} Q{tx} {roof - rw*0.12} {tx + rw*0.42} {roof} Z" fill="{A}"/>')
    b.append(f'<rect x="{tx - 3}" y="{roof - rw*0.78}" width="6" height="{rw*0.25}" fill="{A}"/>')
    b.append(rod(cx + r*0.55, cy - r*0.6, cy + r*0.5, 18, A, CR, P, 28, turns=2.0, snake_w=14))
    return svg_doc(W, H, "".join(b)), "Series layout: wordmark + 2027 + round emblem (parang crescent, Panggung Sangga Buwana, rod of Asclepius)"


def c2_kawung_badge(p):
    W, H = 900, 1060
    P, A, CR = p["primary"], p["accent"], p["cream"]
    fb = font("Poppins-ExtraBold.ttf")
    fs = font("Poppins-SemiBold.ttf")
    cx, cy, R = 450, 440, 400
    b = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{P}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R*0.97}" fill="none" stroke="{A}" stroke-width="5"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R*0.72}" fill="{CR}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R*0.68}" fill="none" stroke="{A}" stroke-width="4"/>']
    b.append(ring_text(fs, "INDONESIAN OCCUPATIONAL MEDICINE UPDATES", cx, cy, R*0.80, 31, CR, tracking=0.06, start_deg=-90))
    # bottom arc text, read left-to-right: place on circle running counter-clockwise
    b.append(bottom_arc_text(fs, "SOLO · 2027", cx, cy, R*0.80 + 30, 40, A, tracking=0.2))
    for a in (180, 0):
        x = cx + R*0.80 * math.cos(math.radians(a)) + (12 if a == 180 else -12)
        b.append(f'<circle cx="{x}" cy="{cy + 14}" r="7" fill="{A}"/>')
    b.append(kawung(cx, cy, R*0.62, P, CR))
    b.append(rod(cx, cy - R*0.58, cy + R*0.58, 22, A, A, CR, 38, turns=2.0, snake_w=16))
    b.append(text_path(fb, "IOMU 2027", cx, 1020, 120, P, anchor="middle", tracking=0.02))
    return svg_doc(W, H, "".join(b)), "Kawung badge: four kawung petals form the medical cross, rod of Asclepius at the centre"


def bottom_arc_text(f, text, cx, cy, r, size, fill, tracking=0.1):
    """Text along the bottom of a circle, upright and left-to-right (baseline radius r - cap)."""
    upm = f["head"].unitsPerEm
    s = size / upm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    total = text_width(f, text, size, tracking)
    ang = math.pi / 2 + total / r / 2  # start on the left, move counter-clockwise
    parts = []
    for c in text:
        g = cmap[ord(c)]
        adv = hmtx[g][0] * s
        mid = ang - adv / 2 / r
        px, py = cx + r * math.cos(mid), cy + r * math.sin(mid)
        sm, cm = math.sin(mid), math.cos(mid)
        # reading direction (sin, -cos); glyph up points to centre (-cos, -sin)
        a, b, c2, d = s * sm, -s * cm, -s * cm, -s * sm
        e = px - (adv / 2) * sm
        f2 = py + (adv / 2) * cm
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (a, b, c2, d, e, f2)))
        parts.append(pen.getCommands())
        ang -= (adv + tracking * size) / r
    return f'<path fill="{fill}" d="{" ".join(parts)}"/>'


def c3_tower_rod(p):
    W, H = 820, 1180
    P, A, CR = p["primary"], p["accent"], p["cream"]
    fc = font("Cinzel.ttf", 800)
    fs = font("Poppins-SemiBold.ttf")
    cx = 410
    b = [parang_pattern("par3", A, P, unit=26)]
    base = 700
    tw = 300
    # stepped plinth with parang band
    b.append(f'<rect x="{cx - 230}" y="{base}" width="460" height="46" fill="url(#par3)"/>')
    b.append(f'<rect x="{cx - 230}" y="{base}" width="460" height="46" fill="none" stroke="{P}" stroke-width="6"/>')
    t, roof = tower(cx, base, tw, P, CR)
    b.append(t)
    # roof = safety helmet
    b.append(helmet(cx, roof + 6, tw*0.86, A, P))
    b.append(f'<rect x="{cx - 4}" y="{roof - tw*0.66 - 40}" width="8" height="44" fill="{A}"/>')
    b.append(f'<circle cx="{cx}" cy="{roof - tw*0.66 - 44}" r="10" fill="{A}"/>')
    # snake winding round the tower = rod of Asclepius
    b.append(snake_around(cx, roof + 10, base - 6, tw*0.68, A, CR, 20))
    b.append(text_path(fc, "IOMU", cx, 900, 170, P, anchor="middle", tracking=0.08))
    b.append(f'<rect x="{cx - 260}" y="{935}" width="520" height="4" fill="{A}"/>')
    b.append(text_path(fs, "2027", cx - 20, 1020, 70, A, anchor="end", tracking=0.12))
    b.append(text_path(fs, "SOLO", cx + 20, 1020, 70, P, anchor="start", tracking=0.12))
    b.append(f'<circle cx="{cx}" cy="996" r="7" fill="{A}"/>')
    return svg_doc(W, H, "".join(b)), "Tower as rod: Panggung Sangga Buwana is the staff, its roof is a safety helmet, the snake winds around it"


def snake_around(cx, y_top, y_bot, span, col, gap, sw, turns=1.5):
    pts = []
    n = 140
    for i in range(n + 1):
        t = i / n
        y = y_bot - (y_bot - y_top) * t
        x = cx + span / 2 * math.sin(t * turns * 2 * math.pi + math.pi / 2) * (1 - 0.25 * t)
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    hx, hy = pts[-1]
    o = [f'<path d="{d}" fill="none" stroke="{gap}" stroke-width="{sw + 12}" stroke-linecap="round"/>',
         f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>',
         f'<ellipse cx="{hx + sw*0.9:.1f}" cy="{hy - sw*0.4:.1f}" rx="{sw*1.15}" ry="{sw*0.75}" fill="{col}" transform="rotate(-25 {hx:.1f} {hy:.1f})"/>']
    return "".join(o)


def c4_wordmark(p):
    P, A, CR = p["primary"], p["accent"], p["cream"]
    fb = font("Poppins-ExtraBold.ttf")
    fs = font("Poppins-SemiBold.ttf")
    size = 300
    base = 400
    cap = size * 0.70          # Poppins cap height ~0.70 em
    b = [parang_pattern("par4", A, P, unit=46)]
    x0 = 90
    # I = rod of Asclepius (stem as wide as a Poppins ExtraBold stem)
    stem = 58
    b.append(rod(x0 + 50, base - cap, base, stem, P, A, CR, 44, turns=1.5, snake_w=17))
    # O = safety helmet filled with parang; dome peak reaches cap height
    hw = 250
    hcx = x0 + 105 + hw * 0.64
    bh = 30
    dome_b = base - bh
    h = cap - bh
    dome = (f"M{hcx - hw/2} {dome_b} A{hw/2} {h} 0 0 1 {hcx + hw/2} {dome_b} Z")
    b.append(f'<clipPath id="hc4"><path d="{dome}"/></clipPath>')
    b.append(f'<rect x="{hcx - hw}" y="{base - hw}" width="{2*hw}" height="{hw}" fill="url(#par4)" clip-path="url(#hc4)"/>')
    b.append(f'<path d="{dome}" fill="none" stroke="{P}" stroke-width="10"/>')
    b.append(f'<path d="M{hcx - hw*0.075} {dome_b - h*0.985} Q{hcx} {dome_b - h*1.0} {hcx + hw*0.075} {dome_b - h*0.985} L{hcx + hw*0.065} {dome_b} L{hcx - hw*0.065} {dome_b} Z" fill="{P}"/>')
    b.append(f'<rect x="{hcx - hw*0.64}" y="{dome_b}" width="{hw*1.28}" height="{bh}" rx="{bh/2}" fill="{P}"/>')
    x = hcx + hw * 0.64 + 8
    b.append(text_path(fb, "MU", x, base, size, P, tracking=-0.01))
    right = x + text_width(fb, "MU", size, -0.01)
    b.append(f'<rect x="{x0}" y="{base + 40}" width="{right - x0}" height="7" fill="{A}"/>')
    b.append(text_path(fs, "SOLO", x0, base + 140, 80, P, tracking=0.3))
    b.append(text_path(fb, "2027", right, base + 140, 80, A, anchor="end", tracking=0.08))
    W, H = int(right + 90), 620
    return svg_doc(W, H, "".join(b)), "Wordmark: the I is the rod of Asclepius, the O is a safety helmet in parang batik"


CONCEPTS = [("c1_series", c1_series), ("c2_kawung", c2_kawung_badge), ("c3_tower", c3_tower_rod), ("c4_wordmark", c4_wordmark)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for key, fn in CONCEPTS:
        for pk, pal in PALETTES.items():
            svg, note = fn(pal)
            path = os.path.join(OUT, f"iomu2027_{key}_{pk}_{VERSION}.svg")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(svg)
            print(path)
