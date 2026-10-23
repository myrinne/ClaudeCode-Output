"""Rebuild the PERDOKI template header text (wordmark, theme, date badge) in high quality.

The committee template is only 1080 x 1920, so its lettering blurs when used at 2160 x 3840.
This script
  1. upscales the template and inpaints away the old wordmark, theme line and date badge
     -> assets/template_hq.png
  2. redraws them as vector SVG with the committee's own fonts, whose glyph outlines are taken from
     the announcement PDF (fonts there are subsets without a unicode cmap, so the char -> glyph
     mapping is read from the cover page text)                     -> assets/header_text.svg
Logos, the "1st" mark, skyline and footer art stay as in the template.
"""
import io
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from fontTools.cffLib import CFFFontSet
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image

HERE = Path(__file__).parent
GUIDE = Path(r"C:\Users\vidya\OneDrive\Documents\PPDS Okupasi\Jkt Summit\Poster Guide")
ANN = GUIDE / "Announcement PERDOKI 2026 21.10.pdf"
TPL = GUIDE / "Template E Poster PERDOKI 2026.png"
W, H = 2160, 3840

# colours from the announcement PDF text
SLANT = -12  # the wordmark is set oblique in the template
DARK, LIGHT, ORANGE, BADGE = "#06502B", "#4B9337", "#F05B10", "#1C5738"


class Face:
    """Glyph outlines of one embedded CFF subset, addressed by unicode via the page's text trace."""

    def __init__(self, doc, xref, cmap):
        buf = doc.extract_font(xref)[3]
        cff = CFFFontSet(); cff.decompile(io.BytesIO(buf), None)
        self.top = cff[cff.fontNames[0]]
        self.upm = round(1 / self.top.FontMatrix[0])
        self.cs = self.top.CharStrings
        self.order = self.top.charset
        self.cmap = cmap  # unicode -> gid

    def glyph(self, ch):
        gid = self.cmap[ch]
        c = self.cs[self.order[gid]]
        pen = SVGPathPen(None); c.draw(pen)
        bp = BoundsPen(None); c.draw(bp)
        return pen.getCommands(), c.width, bp.bounds

    def cap_height(self, ch="H"):
        return self.glyph(ch)[2][3]

    def width(self, text, size, track=0.0):
        w = 0.0
        for ch in text:
            w += (self.glyph(ch)[1] if ch in self.cmap else self.upm * 0.26) * size / self.upm + track
        return w - track

    def svg(self, text, x, baseline, size, fill, track=0.0, skew=0.0, extra=""):
        s = size / self.upm
        out = []
        for ch in text:
            if ch in self.cmap:
                d, adv, _ = self.glyph(ch)
                if d:
                    out.append(f'<path transform="translate({x:.2f},{baseline:.2f}) skewX({skew}) scale({s:.5f},{-s:.5f})" d="{d}"/>')
            else:
                adv = self.upm * 0.26  # space
            x += adv * s + track
        return f'<g fill="{fill}"{extra}>' + "".join(out) + "</g>", x - track


def faces():
    doc = pymupdf.open(ANN)
    cmaps = {}
    for span in doc[0].get_texttrace():
        m = cmaps.setdefault(span["font"], {})
        for uni, gid, *_ in span["chars"]:
            m[chr(uni)] = gid
    xrefs = {name.split("+")[-1]: x for x, _, _, name, *_ in doc[0].get_fonts(full=True)}
    def face(name):
        key = next(k for k in cmaps if name in k)
        return Face(doc, xrefs[next(k for k in xrefs if name in k)], cmaps[key])
    return face("Okine"), face("Aptos-Bold"), face("ClearSans-Bold")


def clean_template():
    t = Image.open(TPL).convert("RGB").resize((W, H), Image.LANCZOS)
    a = np.array(t)
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    coloured = ((hsv[..., 1] > 40) | (hsv[..., 2] < 150)).astype(np.uint8)
    mask = np.zeros(a.shape[:2], np.uint8)
    mask[96:188, 132:1312] = coloured[96:188, 132:1312]      # PERDOKI JAKARTA SUMMIT
    mask[:114, :192] = 0                                      # keep the "1st" ribbon
    mask[186:218, 118:1292] = coloured[186:218, 118:1292]    # theme line
    mask = cv2.dilate(mask, np.ones((7, 7), np.uint8))
    mask[222:266, 402:934] = 1                                # date badge (redrawn on top)
    out = cv2.inpaint(a, mask * 255, 6, cv2.INPAINT_TELEA)
    Image.fromarray(out).save(HERE / "assets" / "template_hq.png", optimize=True)


def header_svg():
    okine, aptos, clear = faces()
    parts = []
    # wordmark: cap height 64 px, baseline 172 px, starting where the template's "P" starts
    size = 64 / okine.cap_height("P") * okine.upm
    span = okine.width("PERDOKI JAKARTA", size) + 0.30 * size + okine.width("SUMMIT", size)
    size *= (1296 - 140) / span  # fit the template's span exactly
    word1, x1 = okine.svg("PERDOKI JAKARTA", 140, 172, size, DARK, skew=SLANT)
    sum_x = x1 + 0.30 * size
    word2, x2 = okine.svg("SUMMIT", sum_x, 172, size, LIGHT, skew=SLANT)
    halo = ' stroke="#FFFFFF" stroke-width="14" stroke-linejoin="round"'
    parts += [okine.svg("PERDOKI JAKARTA", 140, 172, size, "#FFFFFF", skew=SLANT, extra=halo)[0],
              okine.svg("SUMMIT", sum_x, 172, size, "#FFFFFF", skew=SLANT, extra=halo)[0], word1, word2]
    # theme line: italic, spread to the template's width (x 132 -> 1270)
    theme = "Cross-Sector Synergy: Breakthrough Approaches to Increase and Encourage Occupational Health Outcomes"
    tsize = 13 / aptos.cap_height("C") * aptos.upm
    track = (1270 - 132 - aptos.width(theme, tsize)) / (len(theme) - 1)
    parts.append(aptos.svg(theme, 132, 207, tsize, ORANGE, track=track, skew=-11)[0])
    # date badge
    parts.append(f'<rect x="408" y="225" width="522" height="38" rx="12" fill="{BADGE}"/>')
    bsize = 17 / clear.cap_height("O") * clear.upm
    g, bx = clear.svg("24 October 2026", 426, 251, bsize, "#FFFFFF")
    parts.append(g)
    parts.append(f'<rect x="{bx + 10:.1f}" y="230" width="3" height="27" fill="#FFFFFF"/>')
    venue = "M\u00f6venpick Hotel Jakarta"
    vx = bx + 22
    vtrack = max(-1.0, min(2.0, (912 - vx - clear.width(venue, bsize)) / (len(venue) - 1)))
    parts.append(clear.svg(venue, vx, 251, bsize, "#FFFFFF", track=vtrack)[0])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="300" viewBox="0 0 {W} 300">'
           + "".join(parts) + "</svg>")
    (HERE / "assets" / "header_text.svg").write_text(svg, encoding="utf-8")
    print("wordmark ends at", round(x2), "(template SUMMIT ends ~1296); theme track", round(track, 2))


if __name__ == "__main__":
    clean_template()
    header_svg()
