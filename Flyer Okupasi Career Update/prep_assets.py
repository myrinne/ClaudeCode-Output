"""Prepare photos (colour-corrected, letterbox removed) and icons (SVG -> coloured PNG)
for the Sp.Ok career-update trifold flyer.

Usage: python prep_assets.py <pylib-dir-with-pillow_heif>
Photos are NOT committed (people's faces, public repo); only this script is.
"""
import os, sys, re
if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageStat
import pillow_heif
import fitz

pillow_heif.register_heif_opener()
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\vidya\Downloads"
OUT = os.path.join(HERE, "assets", "photos")
ICO = os.path.join(HERE, "assets", "icons")

PHOTOS = {  # output name : source file
    "cover_radiograf": "20241114_141020.jpg",      # #17 reading radiograph with faculty
    "radiograf_dosen": "20241114_141024.jpg",      # #16
    "radiograf_close": "20241114_140603.jpg",      # #1
    "diskusi_toraks": "20241114_135008.jpg",       # #15
    "lab_pipet": "20240607_134122.heic",           # #5
    "lab_tim": "20240607_143002.heic",             # #4
    "periksa_fisik": "Screenshot_20240508_234512_Gallery.jpg",   # #14
    "periksa_fisik2": "Screenshot_20240508_234733_Gallery.jpg",  # #12
    "edukasi_pekerja": "20251014_092847.heic",     # field: worker education
    "lapangan_briefing": "Picture1.jpg",           # field safety briefing, oil & gas site
    "lapangan_gudang": "Picture2.jpg",             # warehouse door + crane truck
}


def strip_letterbox(im):
    g = im.convert("L")
    w, h = g.size
    top, bot = 0, h
    while top < h // 3 and ImageStat.Stat(g.crop((0, top, w, top + 1))).mean[0] < 12:
        top += 1
    while bot > 2 * h // 3 and ImageStat.Stat(g.crop((0, bot - 1, w, bot))).mean[0] < 12:
        bot -= 1
    return im.crop((0, top, w, bot))


def grade(im):
    # partial grey-world white balance (indoor fluorescent casts)
    r, g, b = ImageStat.Stat(im).mean
    avg = (r + g + b) / 3
    k = 0.55  # strength
    fr, fg, fb = [1 + k * (avg / c - 1) for c in (r, g, b)]
    ch = im.split()
    im = Image.merge("RGB", [c.point(lambda p, f=f: min(255, int(p * f))) for c, f in zip(ch, (fr, fg, fb))])
    im = ImageOps.autocontrast(im, cutoff=0.6)
    im = ImageEnhance.Color(im).enhance(1.10)
    im = ImageEnhance.Brightness(im).enhance(1.03)
    return im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=3))


def photos():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in PHOTOS.items():
        im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, fn))).convert("RGB")
        if fn.startswith("Screenshot"):
            im = strip_letterbox(im)
        im.thumbnail((2600, 2600), Image.LANCZOS)
        grade(im).save(os.path.join(OUT, name + ".jpg"), quality=90)
        print("photo", name, im.size)


def icon(svg_name, hexcol, px=256):
    svg = open(os.path.join(ICO, svg_name + ".svg"), encoding="utf-8").read()
    svg = svg.replace("currentColor", hexcol)
    svg = re.sub(r'width="1em" height="1em"', f'width="{px}" height="{px}"', svg)
    doc = fitz.open(stream=svg.encode(), filetype="svg")
    pix = doc[0].get_pixmap(alpha=True, dpi=72 * 4)
    out = os.path.join(ICO, f"{svg_name}_{hexcol.strip('#')}.png")
    pix.save(out)
    return out


if __name__ == "__main__":
    photos()
    if "--photos-only" in sys.argv: sys.exit()
    for f in os.listdir(ICO):
        if f.endswith(".svg"):
            for col in ("#0E4D2F", "#FFFFFF", "#FFC20E", "#1E2A27"):
                icon(f[:-4], col)
    print("icons done")
