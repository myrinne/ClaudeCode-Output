"""Two AI-cover versions of the Sp.Ok career-update trifold (UI green + yellow):
  C  Stetoskop  - AI cover 'Stethoscope Path to Industry' (natural grade), pill photo frames, tubing timeline
  D  Keyhole    - AI cover 'Doctor Ascending Toward the Golden Industry Gateway' (natural grade), arch photo frames
Content and residents' photos are shared with concept A. Output: editable PPTX (Canva import) + PDF.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pptx.util import Mm, Pt
from pptx.enum.shapes import MSO_SHAPE

import build_flyer as bf
from build_flyer import (box, text, P, heading, doing_grid, workplaces_list, contact_block, qr_pair,
                         logo_plate, badge, cta, persyaratan_paras, biaya_paras, new_deck, blank, icon, VISI, HEAD)

HERE = bf.HERE
AI = os.path.join(bf.A, "ai")
SHAPED = os.path.join(bf.A, "shaped")
os.makedirs(SHAPED, exist_ok=True)

PL = dict(dark="0E4D2F", accent="C99A00", bg1="FBF7EC", bg2="EAF0DF", text="22332A", muted="5B6B62",
          disc="0E4D2F", link="1F7A4A", yellow="FFD200")
PXMM = 11.8  # ~300 dpi


# ---------------------------------------------------------------- image helpers
def shaped_photo(sl, name, x, y, w, h, shape="pill", fx=.5, fy=.5, zoom=1.0, border=None):
    im = Image.open(os.path.join(bf.PH, name + ".jpg")).convert("RGB")
    iw, ih = im.size
    ar = w / h
    cw, ch = (int(ih * ar), ih) if iw / ih > ar else (iw, int(iw / ar))
    cw, ch = int(cw / zoom), int(ch / zoom)
    l = min(max(int(fx * iw - cw / 2), 0), iw - cw)
    t = min(max(int(fy * ih - ch / 2), 0), ih - ch)
    W, H = int(w * PXMM), int(h * PXMM)
    im = im.crop((l, t, l + cw, t + ch)).resize((W, H), Image.LANCZOS)
    ss = 3
    m = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(m)
    if shape == "pill":
        r = min(W, H) * ss / 2
        d.rounded_rectangle((0, 0, W * ss - 1, H * ss - 1), radius=r, fill=255)
    elif shape == "arch":
        r = min(W * ss / 2, H * ss * 0.42)
        d.rounded_rectangle((0, 0, W * ss - 1, H * ss - 1 + int(r) + 2), radius=r, fill=255)
    else:
        d.rectangle((0, 0, W * ss, H * ss), fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    out = Image.new("RGBA", (W, H))
    out.paste(im, (0, 0), m)
    if border:
        bw = int(0.9 * PXMM)
        bm = m.filter(ImageFilter.MaxFilter(1))
        inner = m.filter(ImageFilter.MinFilter(bw * 2 + 1))
        ring = Image.fromarray(np.clip(np.asarray(bm, int) - np.asarray(inner, int), 0, 255).astype(np.uint8))
        out.paste(Image.new("RGBA", (W, H), "#" + border), (0, 0), ring)
    p = os.path.join(SHAPED, f"{name}_{shape}_{int(w)}x{int(h)}.png")
    out.save(p, optimize=True)
    pic = sl.shapes.add_picture(p, Mm(x), Mm(y), Mm(w), Mm(h))
    pic.name = "Foto " + name
    return pic


def extend_top(src, dst, ratio=2.1, darken=0.80, seam=170):
    """Extend a portrait image upward to the cover-panel ratio using its own sky colour."""
    im = np.asarray(Image.open(src).convert("RGB"), dtype=float) / 255
    h, w = im.shape[:2]
    H = int(w * ratio)
    add = H - h
    top = im[:12].mean(axis=(0, 1))
    grad = np.linspace(darken, 1.0, add)[:, None, None] * top[None, None, :]
    canvas = np.concatenate([np.broadcast_to(grad, (add, w, 3)), im], axis=0).copy()
    a = np.linspace(0, 1, seam)[:, None, None]                  # feather the seam
    flat = np.broadcast_to(top, (seam, w, 3))
    canvas[add:add + seam] = flat * (1 - a) + im[:seam] * a
    rng = np.random.default_rng(3)
    canvas[:add + seam] += rng.normal(0, 0.012, (add + seam, w))[..., None]
    Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8)).save(dst, quality=95)
    return dst


def crop_fill(src, dst, ratio=2.1, fx=.5):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    cw = int(h / ratio)
    l = min(max(int(fx * w - cw / 2), 0), w - cw)
    im.crop((l, 0, l + cw, h)).save(dst, quality=95)
    return dst


def poly_curve(sl, pts, col, width_pt):
    """Smooth open curve as a freeform polyline (points in mm)."""
    fb = sl.shapes.build_freeform(Mm(pts[0][0]), Mm(pts[0][1]), scale=1.0)
    fb.add_line_segments([(Mm(px), Mm(py)) for px, py in pts[1:]], close=False)
    s = fb.convert_to_shape()
    s.fill.background()
    s.line.color.rgb = bf.rgb(col)
    s.line.width = Pt(width_pt)
    st = s._element.find(bf.qn("p:style"))
    if st is not None:
        s._element.remove(st)
    s.name = "Garis selang stetoskop"
    return s


def keyhole_dot(sl, cx, cy, col):
    box(sl, cx - 1.7, cy - 1.7, 3.4, 3.4, fill=col, shape=MSO_SHAPE.OVAL)
    box(sl, cx - 1.1, cy + 0.6, 2.2, 3.2, fill=col, shape=MSO_SHAPE.TRAPEZOID)


# ---------------------------------------------------------------- panels
ROWS = [("07.30", "Turun ke lapangan", "Safety briefing dan walk-through survey untuk mengenali bahaya di area kerja.", "lapangan_briefing", .55, .5),
        ("10.00", "Penilaian laik kerja", "Pemeriksaan klinis untuk keputusan fit, unfit, atau fit dengan restriksi.", "periksa_fisik", .5, .45),
        ("13.00", "Diskusi radiograf toraks", "Menelaah kasus pajanan debu dan penyakit paru akibat kerja.", "radiograf_close", .55, .4),
        ("15.00", "Edukasi pekerja", "Promosi kesehatan dan pencegahan penyakit akibat kerja.", "edukasi_pekerja", .8, .5)]


def flap_timeline(sl, v):
    Pl = PL
    box(sl, 0, 0, 97, 210, fill=Pl["bg2"], name="Latar panel lipat")
    heading(sl, 7, 10, 84, "Sehari sebagai Sp.Ok", Pl)
    text(sl, 7, 24, 84, 8, [P("Dari lapangan, klinik, sampai ruang diskusi kasus.", size=8.6, italic=True, color=Pl["muted"])])
    y0, rh = 34, 41.3
    shape = "pill" if v == "C" else "arch"
    fw, fh = (41, 33) if v == "C" else (37, 37)
    dx = 7 + fw + 3.2
    if v == "C":   # wavy stethoscope tubing through the dots
        ys = np.linspace(y0 + 2, y0 + 3 * rh + 14, 160)
        pts = [(dx + 2.0 * np.sin((yy - (y0 + 2)) / rh * np.pi), yy) for yy in ys]
        poly_curve(sl, pts, Pl["dark"], 2.4)
        ex, ey = pts[-1]
        box(sl, ex - 3.2, ey, 6.4, 6.4, fill="B9C2BC", shape=MSO_SHAPE.OVAL, line=Pl["dark"], lw=1.6, name="Chest piece")
        box(sl, ex - 1.6, ey + 1.6, 3.2, 3.2, fill="EEF2EE", shape=MSO_SHAPE.OVAL)
    else:
        bf.line(sl, dx, y0 + 2, dx, y0 + 3 * rh + 2, "9BBF5A", 1.5)
    for i, (tm, tt, dd, ph, fx, fy) in enumerate(ROWS):
        yy = y0 + i * rh
        shaped_photo(sl, ph, 7, yy, fw, fh, shape, fx, fy)
        if v == "C":
            box(sl, dx - 2, yy + 0.3, 4, 4, fill=Pl["yellow"], shape=MSO_SHAPE.OVAL, line=Pl["dark"], lw=1)
        else:
            keyhole_dot(sl, dx, yy + 2, Pl["accent"])
        text(sl, dx + 4.3, yy, 92 - dx - 4.3, fh, [P(tm, bold=True, size=8.6, color=Pl["accent"], after=1),
                                                   P(tt, font=HEAD, bold=True, size=10.8, color=Pl["dark"], after=2, ls=1.0),
                                                   P(dd, size=7.9, color=Pl["text"], ls=1.1)])
    text(sl, 7, 201.5, 84, 5, [P("Ilustrasi kegiatan; ritme kerja menyesuaikan tempat kerja.", size=6.5, italic=True, color=Pl["muted"])])


def back_panel(sl, v):
    Pl = PL
    box(sl, 97, 0, 100, 210, fill=Pl["bg1"], name="Latar panel belakang")
    bf.photo(sl, "lapangan_gudang", 97, 0, 100, 47, .55, .55)
    box(sl, 97, 45.8, 100, 1.4, fill=Pl["yellow"])
    heading(sl, 104, 52, 86, "Tempat kerja lulusan", Pl)
    workplaces_list(sl, 104, 66.5, Pl, rh=8.1, d=6.6, fs=9)
    box(sl, 97, 127, 100, 83, fill=Pl["dark"], name="Blok informasi")
    text(sl, 104, 132, 86, 9, [P("Informasi", font=HEAD, bold=True, size=17, color="FFFFFF", ls=1.0)])
    box(sl, 104, 142.2, 12, 0.9, fill=Pl["yellow"])
    contact_block(sl, 104, 146.5, 86, Pl, "D6E3DA", "FFFFFF", "FFC20E")
    qr_pair(sl, 104, 174, Pl, "FFFFFF", "D6E3DA", s=19, gap=24)


def cover(sl, v):
    Pl = PL
    if v == "C":
        img = extend_top(os.path.join(AI, "stetoskop_natural.jpg"), os.path.join(AI, "cover_C.jpg"))
    else:
        img = crop_fill(os.path.join(AI, "gateway_natural.jpg"), os.path.join(AI, "cover_D.jpg"), fx=.47)
    pic = sl.shapes.add_picture(img, Mm(197), Mm(0), Mm(100), Mm(210))
    pic.name = "Gambar sampul"
    logo_plate(sl, 203, 7, w=52)
    if v == "C":
        text(sl, 204, 35, 88, 5, [P("PROGRAM STUDI SPESIALIS KEDOKTERAN OKUPASI", bold=True, size=6.8, color=Pl["yellow"], spc=80)])
        text(sl, 204, 41, 88, 10, [P("Satu stetoskop,", font=HEAD, size=19, color="FFFFFF", ls=1.0)])
        text(sl, 204, 51, 88, 22, [P("ribuan tempat kerja.", font=HEAD, bold=True, italic=True, size=23, color=Pl["yellow"], ls=0.95)])
        badge(sl, 204, 75, 31, "Akreditasi UNGGUL", Pl["yellow"], "FFFFFF", h=6)
        badge(sl, 237.5, 75, 50, "Prodi Sp.Ok pertama di Indonesia", Pl["yellow"], "FFFFFF", h=6)
    else:
        for k in range(8):   # soft gradient behind the text (stacked translucent bands)
            box(sl, 197, 140 + k * 2.5, 100, 2.6, fill=Pl["dark"], alpha=0.07 * (k + 1), name="Gradasi")
        box(sl, 197, 160, 100, 42, fill=Pl["dark"], alpha=0.6, name="Bayangan teks")
        text(sl, 204, 155, 88, 5, [P("PROGRAM STUDI SPESIALIS KEDOKTERAN OKUPASI", bold=True, size=6.8, color=Pl["yellow"], spc=80)])
        text(sl, 204, 161, 88, 10, [P("Buka kunci karier Anda", font=HEAD, size=17, color="FFFFFF", ls=1.0)])
        text(sl, 204, 170, 88, 13, [P("di seluruh dunia kerja.", font=HEAD, bold=True, italic=True, size=21, color=Pl["yellow"], ls=0.95)])
        badge(sl, 204, 186, 31, "Akreditasi UNGGUL", Pl["yellow"], "FFFFFF", h=6)
        badge(sl, 237.5, 186, 50, "Prodi Sp.Ok pertama di Indonesia", Pl["yellow"], "FFFFFF", h=6)
    box(sl, 197, 202, 100, 8, fill=Pl["yellow"], name="Pita kuning")
    text(sl, 197, 202, 100, 8, [P(runs=[("Pendaftaran: ", {}), ("enrollment.ui.ac.id", {"bold": True}),
                                        ("  ·  dua periode per tahun", {})], size=7.4, color=Pl["dark"], align="c")], anchor="m")


def inside(prs, v):
    Pl = PL
    shape = "pill" if v == "C" else "arch"
    sl = blank(prs, "Dalam")
    box(sl, 0, 0, 100, 210, fill=Pl["bg1"], name="Latar panel 1")
    heading(sl, 7, 10, 86, "Apa yang dikerjakan Sp.Ok?", Pl, size=16.5)
    text(sl, 7, 24, 86, 9, [P("Melayani tiga sasaran: komunitas pekerja, individu, dan masyarakat sekitar industri.",
                              size=8.4, color=Pl["text"])])
    doing_grid(sl, 7, 35.5, Pl, rh=20.5, ts=8.3, ds=7.6, d=8.5)
    box(sl, 0, 119, 100, 91, fill=Pl["dark"], name="Blok visi dan gelar")
    text(sl, 7, 124, 86, 5, [P("VISI", bold=True, size=7.5, color=Pl["yellow"], spc=200)])
    text(sl, 7, 129.5, 86, 32, [P("“" + VISI + "”", font=HEAD, italic=True, size=9, color="FFFFFF", ls=1.12)])
    box(sl, 7, 163.5, 86, 0.4, fill="5E8C70")
    text(sl, 7, 166, 86, 15, [P("GELAR LULUSAN", bold=True, size=7.5, color=Pl["yellow"], spc=200, after=1.5),
                              P(runs=[("Spesialis Kedokteran Okupasi ", {}), ("(Sp.Ok)", {"color": Pl["yellow"]})],
                                font=HEAD, bold=True, size=11.5, color="FFFFFF", ls=1.0)])
    shaped_photo(sl, "lab_pipet", 7, 183, 86, 22, "pill" if v == "C" else "rect", .55, .38)

    box(sl, 100, 0, 100, 210, fill=Pl["bg2"], name="Latar panel 2")
    heading(sl, 107, 10, 86, "Persyaratan peserta", Pl)
    text(sl, 107, 26, 86, 125, persyaratan_paras(Pl), name="Teks persyaratan")
    shaped_photo(sl, "diskusi_toraks", 107, 151, 86, 52, shape, .45, .5)

    box(sl, 200, 0, 97, 210, fill=Pl["bg1"], name="Latar panel 3")
    heading(sl, 207, 10, 83, "Pembelajaran dan biaya", Pl)
    for i, (big, sub) in enumerate([("7 semester · 98 SKS", "Lulusan dokter umum"),
                                    ("4 semester · tambahan 65 SKS", "Lulusan Magister Kedokteran Kerja")]):
        yy = 26 + i * 18
        box(sl, 207, yy, 83, 16, fill=Pl["bg2"])
        box(sl, 207, yy, 1.4, 16, fill=Pl["yellow"])
        text(sl, 211, yy + 2, 77, 13, [P(big, font=HEAD, bold=True, size=12.5, color=Pl["dark"], after=1, ls=1.0),
                                       P(sub, size=8, color=Pl["text"])])
    text(sl, 207, 66, 83, 82, biaya_paras(Pl), name="Teks pembelajaran dan biaya")
    shaped_photo(sl, "radiograf_dosen", 207, 147, 83, 44, shape, .45, .45)
    cta(sl, 207, 184, 83, 20, Pl["yellow"], Pl["dark"], Pl["dark"])


def build(v):
    bf.SECT.update(head=9.3, body=8.4, gap=8)
    prs = new_deck()
    sl = blank(prs, "Luar")
    flap_timeline(sl, v)
    back_panel(sl, v)
    cover(sl, v)
    inside(prs, v)
    name = {"C": "Konsep C (Stetoskop)", "D": "Konsep D (Keyhole)"}[v]
    out = os.path.join(HERE, f"Flyer Sp.Ok - {name}.pptx")
    prs.save(out)
    return out


if __name__ == "__main__":
    for v in ("C", "D"):
        print(build(v))
