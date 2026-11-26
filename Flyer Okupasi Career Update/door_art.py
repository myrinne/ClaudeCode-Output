"""Raster art for Concept B cover: corrugated factory wall, open steel door, light spill.
Background only; the photo in the doorway and all text stay separate editable elements."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 12                      # px per mm
W, H = 100 * S, 210 * S     # cover panel
OX0, OY0, OX1, OY1 = 26, 86, 86, 196   # door opening (panel mm)
FR = 3.2                    # frame thickness
YEL = np.array([255, 196, 60]) / 255


def mm(*v):
    return [int(round(a * S)) for a in v]


def wall():
    x = np.arange(W)[None, :]
    y = np.arange(H)[:, None]
    ridge = (0.5 + 0.5 * np.sin(2 * np.pi * x / (5 * S))) ** 2
    c0, c1 = np.array([20, 29, 26]) / 255, np.array([44, 58, 53]) / 255
    img = c0 + (c1 - c0) * ridge[..., None]
    img = img * (0.78 + 0.22 * np.sin(np.pi * y / H))[..., None]
    for sy in (58, 140):                                 # horizontal sheet seams
        a = sy * S
        img[a:a + 4] *= 0.55
        img[a + 4:a + 6] *= 1.25
    # glow from the doorway
    dx = np.maximum(np.maximum(OX0 * S - x, 0), np.maximum(x - OX1 * S, 0))
    dy = np.maximum(np.maximum(OY0 * S - y, 0), np.maximum(y - OY1 * S, 0))
    g = np.exp(-np.sqrt(dx ** 2 + dy ** 2) / (11 * S))[..., None] * 0.42
    img = 1 - (1 - img) * (1 - YEL * g)
    # floor
    fy = OY1 * S
    floor = np.linspace(0.20, 0.12, H - fy)[:, None, None] * np.ones((1, W, 3))
    img[fy:] = floor * np.array([1, 1.05, 1.0])
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(mm(OX0, OY1)), tuple(mm(OX1, OY1)), tuple(mm(106, 214)), tuple(mm(6, 214))], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(4 * S)), dtype=float)[..., None] / 255
    img = img + (YEL - img) * m * 0.42 * (np.arange(H)[:, None, None] >= fy)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB")


def door(im):
    d = ImageDraw.Draw(im, "RGBA")
    # shadow of the open leaf on the wall
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).polygon([tuple(mm(10, 80)), tuple(mm(2, 84)), tuple(mm(2, 204)), tuple(mm(10, 204))], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(2.5 * S))
    im.paste(Image.new("RGB", (W, H), (5, 8, 7)), (0, 0), sh)
    # frame
    d.rectangle(mm(OX0 - FR, OY0 - FR, OX1 + FR, OY1), fill=(88, 98, 93))
    d.line(mm(OX0 - FR, OY1, OX0 - FR, OY0 - FR, OX1 + FR, OY0 - FR), fill=(150, 160, 154), width=S // 2)
    d.rectangle(mm(OX0, OY0, OX1, OY1), fill=(255, 226, 140))
    # open leaf (perspective), hinge at the left jamb
    leaf = [(26, 86), (10, 79.5), (10, 204), (26, 196)]
    lm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lm).polygon([tuple(mm(*p)) for p in leaf], fill=255)
    xs = np.arange(W)[None, :] / S
    t = np.clip((xs - 10) / 16, 0, 1)
    lc = (np.array([128, 138, 132]) * (1 - t)[..., None] + np.array([62, 70, 66]) * t[..., None])
    lc = np.broadcast_to(lc, (H, W, 3)).astype(np.uint8)
    im.paste(Image.fromarray(lc, "RGB"), (0, 0), lm)
    inset = [(12.6, 84.5), (23.6, 89.2), (23.6, 192.5), (12.6, 197.5)]
    d.line([tuple(mm(*p)) for p in inset + inset[:1]], fill=(45, 52, 49, 255), width=S // 3)
    d.line(mm(10, 79.5, 10, 204), fill=(185, 192, 187), width=S // 3)        # lit outer edge
    d.rectangle(mm(11.4, 140, 15.6, 142.6), fill=(30, 34, 32))                 # handle shadow
    d.rectangle(mm(11.0, 139.2, 15.2, 141.6), fill=(205, 210, 206))            # lever handle
    d.ellipse(mm(10.9, 138.6, 13.1, 142.2), fill=(170, 176, 172))
    # kick plate
    d.polygon([tuple(mm(*p)) for p in [(10.4, 190), (25.6, 188.5), (25.6, 195.6), (10.4, 203.6)]], fill=(98, 106, 101, 255))
    return im


def jamb_shadow(path):
    w, h = (OX1 - OX0) * S, (OY1 - OY0) * S
    a = np.zeros((h, w))
    x = np.arange(w)[None, :] / S
    y = np.arange(h)[:, None] / S
    a = np.maximum(a, 0.6 * np.clip(1 - x / 9, 0, 1))
    a = np.maximum(a, 0.45 * np.clip(1 - y / 7, 0, 1))
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = (8, 12, 10)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(path)


def build(outdir):
    bg = os.path.join(outdir, "cover_b_background.jpg")
    door(wall()).save(bg, quality=93)
    js = os.path.join(outdir, "cover_b_jamb_shadow.png")
    jamb_shadow(js)
    return bg, js


if __name__ == "__main__":
    print(build(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")))
