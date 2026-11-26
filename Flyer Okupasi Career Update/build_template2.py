"""Sp.Ok career-update trifold, template 2 (after the 'Pula Outdoor' capsule brochure reference):
white page, big photos in capsule/arch frames bleeding off the edges, one tall green capsule
holding info + QR, small uppercase section heads, round badge overlapping a photo.
  C  capsule frames (full round ends), cover = AI stethoscope
  D  door-arch frames (soft round top),  cover = AI keyhole
Editable PPTX (Canva import) + PDF.
"""
import os
import numpy as np
from PIL import Image, ImageDraw
from pptx.util import Mm
from pptx.enum.shapes import MSO_SHAPE

import build_flyer as bf
from build_flyer import box, text, P, workplaces_list, contact_block, qr_pair, new_deck, blank, icon_disc, VISI, HEAD

HERE = bf.HERE
AI = os.path.join(bf.A, "ai")
OUTD = os.path.join(bf.A, "shaped2")
os.makedirs(OUTD, exist_ok=True)
PXMM = 11.8

G, G2, Y, INK, MUTE, LINE = "0E4D2F", "1F6B45", "FFD200", "22332A", "5B6B62", "D9E3DC"
PL = dict(dark=G, accent="C99A00", text=INK, muted=MUTE, disc=G, link="1F7A4A", yellow=Y)


# ---------------------------------------------------------------- shaped photos
def mask_img(W, H, radii):
    """radii (tl, tr, br, bl) in px; each corner drawn as a quarter circle."""
    ss = 3
    m = Image.new("L", (W * ss, H * ss), 255)
    d = ImageDraw.Draw(m)
    tl, tr, br, bl = [int(r * ss) for r in radii]
    Wf, Hf = W * ss, H * ss
    for r, (cx, cy), box_ in [(tl, (tl, tl), (0, 0, tl, tl)), (tr, (Wf - tr, tr), (Wf - tr, 0, Wf, tr)),
                              (br, (Wf - br, Hf - br), (Wf - br, Hf - br, Wf, Hf)), (bl, (bl, Hf - bl), (0, Hf - bl, bl, Hf))]:
        if r <= 0:
            continue
        d.rectangle(box_, fill=0)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    return m.resize((W, H), Image.LANCZOS)


def framed(sl, src, x, y, w, h, radii_mm, fx=.5, fy=.5, zoom=1.0, ring=None, tag=""):
    im = Image.open(src).convert("RGB")
    iw, ih = im.size
    ar = w / h
    cw, ch = (int(ih * ar), ih) if iw / ih > ar else (iw, int(iw / ar))
    cw, ch = int(cw / zoom), int(ch / zoom)
    l = min(max(int(fx * iw - cw / 2), 0), iw - cw)
    t = min(max(int(fy * ih - ch / 2), 0), ih - ch)
    W, H = max(1, int(w * PXMM)), max(1, int(h * PXMM))
    im = im.crop((l, t, l + cw, t + ch)).resize((W, H), Image.LANCZOS)
    m = mask_img(W, H, [r * PXMM for r in radii_mm])
    out = Image.new("RGBA", (W, H))
    out.paste(im, (0, 0), m)
    if ring:
        bw = int(1.2 * PXMM)
        inner = mask_img(W - 2 * bw, H - 2 * bw, [max(0, r - 1.2) * PXMM for r in radii_mm])
        rim = Image.new("RGBA", (W, H), "#" + ring)
        hole = Image.new("L", (W, H), 0)
        hole.paste(inner, (bw, bw))
        rm = Image.fromarray(np.clip(np.asarray(m, int) - np.asarray(hole, int), 0, 255).astype(np.uint8))
        out.paste(rim, (0, 0), rm)
    base = os.path.splitext(os.path.basename(src))[0]
    p = os.path.join(OUTD, f"{base}_{tag}{int(x)}_{int(y)}_{int(w)}x{int(h)}.png")
    out.save(p, optimize=True)
    pic = sl.shapes.add_picture(p, Mm(x), Mm(y), Mm(w), Mm(h))
    pic.name = "Foto " + base
    return pic


def ph(name):
    return os.path.join(bf.PH, name + ".jpg")


def R(v, w, h, where):
    """Corner radii for a frame: C = full round ends, D = soft door arch."""
    full = min(w, h) / 2
    r = full if v == "C" else min(14, full)
    return {"top": (r, r, 0, 0), "bottom": (0, 0, r, r), "all": (r, r, r, r),
            "tl": (r, 0, 0, 0), "br": (0, 0, r, 0)}[where]


def capsule(sl, v, x, y, w, h, fill, name):
    if v == "C":
        s = box(sl, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, name=name)
        s.adjustments[0] = 0.5
    else:
        s = box(sl, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE, name=name)
        s.adjustments[0] = min(0.5, 14 / min(w, h))
        s.adjustments[1] = 0.0
    return s


def pill_label(sl, x, y, w, t, fill=G, col="FFFFFF", h=6.6, size=7.4):
    s = box(sl, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, name="Label")
    s.adjustments[0] = 0.5
    text(sl, x, y, w, h, [P(t, bold=True, size=size, color=col, align="c")], anchor="m")


def kicker(sl, x, y, w, t, col=G, size=8.6):
    text(sl, x, y, w, 5, [P(t.upper(), bold=True, size=size, color=col, spc=120)])


def title(sl, x, y, w, h, t, col=INK, size=14):
    text(sl, x, y, w, h, [P(t, font=HEAD, bold=True, size=size, color=col, ls=1.0)])


def round_badge(sl, cx, cy, d, l1, l2, fill=Y, col=G):
    box(sl, cx - d / 2, cy - d / 2, d, d, fill=fill, shape=MSO_SHAPE.OVAL, line="FFFFFF", lw=2.2, name="Badge bulat")
    text(sl, cx - d / 2 + 1.5, cy - d / 2, d - 3, d, [P(l1, font=HEAD, bold=True, size=15, color=col, align="c", ls=0.9),
                                                      P(l2, bold=True, size=6.4, color=col, align="c", ls=1.0)], anchor="m")


# ---------------------------------------------------------------- content (condensed)
DOING2 = [
    ("tabler_stethoscope", "MCU dan surveilans", "Pra-kerja, berkala, khusus."),
    ("tabler_clipboard-check", "Laik kerja (FTW/RTW)", "Fit, unfit, fit dengan restriksi."),
    ("tabler_lungs", "Diagnosis PAK", "Tujuh langkah diagnosis."),
    ("tabler_building-factory-2", "Survei tempat kerja", "Walk-through survey dan HRA."),
    ("tabler_stretching", "Ergonomi", "Postur, angkat-angkut, desain kerja."),
    ("tabler_flask", "Toksikologi industri", "Pajanan kimia, biomonitoring."),
    ("tabler_wheelchair", "Penilaian kecacatan", "Untuk jaminan sosial."),
    ("tabler_speakerphone", "Promosi kesehatan", "Edukasi dan program K3."),
]


def H_(t):
    return P(t, bold=True, size=8.4, color=G, before=5, after=1)


def T_(runs, **kw):
    return P(runs=runs if isinstance(runs, list) else [(runs, {})], size=7.6, color=INK, after=0.6, ls=1.08, **kw)


def B(t):
    return (t, {"bold": True})


def syarat_paras():
    return [
        P("Persyaratan umum", bold=True, size=8.4, color=G, after=1),
        T_("CV, STR aktif, ijazah dan transkrip Sarjana Kedokteran serta Profesi Dokter (dilegalisasi), asuransi kesehatan aktif. Pengalaman klinis diutamakan."),
        H_("Lulusan dokter umum"),
        T_("Usia maks. 45 tahun, TOEFL ≥450 (diutamakan LBUI), IPK ≥2,75. Bila bekerja: surat rekomendasi atau tugas belajar."),
        H_("Lulusan Magister Kedokteran Kerja"),
        T_("Usia maks. 45 tahun, TOEFL ≥450 (LIA/LBI UI), IPK ≥3,00, pengalaman industri terkait ≥3 tahun atau penugasan daerah/industri."),
        H_("Peminatan"),
        T_([B("Reguler"), (" · dokter umum dan lulusan Magister Kedokteran Kerja.", {})]),
        T_([B("Khusus"), (" · lulusan Magister Kedokteran Kerja di lingkungan SKK Migas, dengan rekomendasi pejabat berwenang.", {})]),
        H_("Tahapan seleksi"),
        T_("TPA, Bahasa Inggris, psikotes, ujian tertulis, wawancara; MMPI dan wawancara psikiatrik."),
        T_([("Jadwal MMPI: ", {}), ("@pusbangki.fkui", {"bold": True, "color": "1F7A4A"})]),
        T_([("Kontak UKK Pusbangki: ", {}), ("+62 812-2678-7767", {"bold": True, "color": "1F7A4A"})]),
    ]


def biaya_paras():
    return [
        P("Periode seleksi", bold=True, size=8.4, color=G, after=1),
        T_([B("Ganjil"), (" · unggah data Februari–Maret, kuliah Agustus.", {})]),
        T_([B("Genap"), (" · daftar Agustus–September, kuliah Februari.", {})]),
        T_([("Daring hanya melalui ", {}), ("enrollment.ui.ac.id", {"bold": True, "color": "1F7A4A"}), (", tanpa CHS.", {})]),
        H_("Biaya"),
        T_([B("Rp1.650.000"), (" · pendaftaran TPA dan Bahasa Inggris (SIMAK UI)", {})]),
        T_([B("Rp600.000"), (" · tes psikiatri (Psikiatri FKUI-RSCM)", {})]),
        T_([B("Rp25.000.000"), (" / semester · reguler (WNI)", {})]),
        T_([B("Rp33.000.000"), (" / semester · khusus (S1 non-UI)", {})]),
    ]


# ---------------------------------------------------------------- outside
def outside(prs, v):
    sl = blank(prs, "Luar")
    box(sl, 0, 0, 297, 210, fill="FFFFFF", name="Latar putih")

    # FLAP 0-97: tempat kerja lulusan + field photo
    kicker(sl, 7, 10, 84, "Tempat kerja lulusan")
    title(sl, 7, 15.5, 84, 14, "Ke mana lulusan Sp.Ok berkarier?", size=14)
    workplaces_list(sl, 7, 32, PL, rh=7.7, w=84, d=6.2, fs=8.6)
    framed(sl, ph("lapangan_briefing"), 7, 93, 83, 117, R(v, 83, 117, "top"), .55, .5, tag=v)
    pill_label(sl, 13, 193, 71, "Turun ke lapangan: safety briefing di site")

    # BACK 97-197: visi + green capsule (photo, contact, QR)
    kicker(sl, 104, 10, 86, "Visi")
    text(sl, 104, 15.5, 86, 26, [P("“" + VISI + "”", font=HEAD, italic=True, size=8.2, color=INK, ls=1.1)])
    cx0, cw, cy0, chh = 107, 80, 45, 161
    capsule(sl, v, cx0, cy0, cw, chh, G, "Kapsul informasi")
    framed(sl, ph("lapangan_gudang"), cx0, cy0, cw, 56, R(v, cw, 56, "top") if v == "D" else (40, 40, 0, 0), .55, .5, tag=v)
    box(sl, cx0, cy0 + 55.4, cw, 1.2, fill=Y)
    text(sl, cx0 + 6, 106, cw - 12, 8, [P("Informasi", font=HEAD, bold=True, size=14, color="FFFFFF")])
    contact_block(sl, cx0 + 6, 115, cw - 12, PL, "D6E3DA", "FFFFFF", "FFC20E")
    qr_pair(sl, cx0 + 8, 142, PL, "FFFFFF", "D6E3DA", s=18, gap=14)
    pill_label(sl, cx0 + 14, 178, cw - 28, "Prodi Sp.Ok pertama di Indonesia", fill=Y, col=G, size=7)

    # COVER 197-297
    if v == "C":
        framed(sl, os.path.join(AI, "stetoskop_natural.jpg"), 197, 0, 100, 150, (0, 0, 50, 50), .5, .5, tag="C")
        text(sl, 204, 11, 86, 9, [P("Satu stetoskop,", font=HEAD, size=19, color="FFFFFF", align="c", ls=1.0)])
        text(sl, 204, 20, 86, 11, [P("ribuan tempat kerja.", font=HEAD, bold=True, italic=True, size=22, color=Y, align="c", ls=1.0)])
    else:
        framed(sl, os.path.join(AI, "gateway_natural.jpg"), 204, 7, 86, 143, (14, 14, 0, 0), .5, .52, tag="D")
        text(sl, 204, 12, 86, 7, [P("Buka kunci karier Anda", font=HEAD, size=14, color="FFFFFF", align="c", ls=1.0)])
        text(sl, 204, 19, 86, 10, [P("di seluruh dunia kerja.", font=HEAD, bold=True, italic=True, size=17.5, color=Y, align="c", ls=1.0)])
    logo = sl.shapes.add_picture(os.path.join(bf.A, "logo-FKUI-white.png"), Mm(219), Mm(155), Mm(58), Mm(58 / 2.89))
    logo.name = "Logo FKUI"
    text(sl, 200, 177, 94, 9, [P("PROGRAM STUDI SPESIALIS", bold=True, size=7.4, color=MUTE, align="c", spc=150),
                               P("KEDOKTERAN OKUPASI (Sp.Ok)", bold=True, size=10, color=G, align="c", spc=60)])
    pill_label(sl, 222, 189, 50, "Akreditasi UNGGUL", fill=Y, col=G, size=7.2)
    text(sl, 200, 199, 94, 5, [P("enrollment.ui.ac.id", size=7.4, color=MUTE, align="c", spc=40)])


# ---------------------------------------------------------------- inside
def inside(prs, v):
    sl = blank(prs, "Dalam")
    box(sl, 0, 0, 297, 210, fill="FFFFFF", name="Latar putih")

    # P1 0-100: what Sp.Ok does
    framed(sl, ph("edukasi_pekerja"), 0, 0, 100, 64, (0, 0, 32 if v == "C" else 14, 0), .62, .55, tag=v)
    pill_label(sl, 7, 54, 58, "Edukasi pekerja di tempat kerja")
    kicker(sl, 7, 70, 86, "Apa yang dikerjakan Sp.Ok")
    title(sl, 7, 75.5, 86, 12, "Klinik dan industri dalam satu profesi.", size=13)
    cw = 42
    for i, (ic, t, d) in enumerate(DOING2):
        x, y = 7 + (i % 2) * (cw + 2), 90 + (i // 2) * 14
        icon_disc(sl, ic, x, y, 8, G, "FFFFFF")
        text(sl, x + 10, y - 0.2, cw - 10, 13, [P(t, bold=True, size=8, color=G, after=0.5, ls=1.0),
                                                 P(d, size=7.2, color=INK, ls=1.05)])
    text(sl, 7, 148, 86, 9, [P(runs=[("Melayani tiga sasaran: ", {"bold": True, "color": G}),
                                     ("komunitas pekerja, individu, dan masyarakat sekitar industri.", {})],
                               size=7.8, color=INK)])
    gb = capsule(sl, v, 7, 162, 86, 22, Y, "Kotak gelar")
    text(sl, 14, 162, 72, 22, [P("GELAR LULUSAN", bold=True, size=7, color=G, spc=150, align="c", after=1),
                               P("Spesialis Kedokteran Okupasi (Sp.Ok)", font=HEAD, bold=True, size=11, color=G, align="c")],
         anchor="m")
    framed(sl, ph("lab_pipet"), 7, 188, 86, 22, (11, 11, 0, 0) if v == "C" else (8, 8, 0, 0), .55, .38, tag=v)

    # P2 100-200: tall green capsule (photo + learning)
    x0, w0, y0, h0 = 110, 80, 7, 197
    capsule(sl, v, x0, y0, w0, h0, G, "Kapsul pembelajaran")
    framed(sl, ph("cover_radiograf"), x0, y0, w0, 92, R(v, w0, 92, "top") if v == "D" else (40, 40, 0, 0), .42, .45, tag=v)
    box(sl, x0, y0 + 91.4, w0, 1.2, fill=Y)
    framed(sl, ph("periksa_fisik"), 170, 70, 28, 28, (14, 14, 14, 14), .5, .45, ring="FFFFFF", tag=v)
    kicker(sl, x0 + 7, 104, w0 - 14, "Pembelajaran", col=Y, size=8)
    for i, (big, sub) in enumerate([("7 semester · 98 SKS", "Lulusan dokter umum"),
                                    ("4 semester · +65 SKS", "Lulusan Magister Kedokteran Kerja")]):
        yy = 110 + i * 14
        text(sl, x0 + 7, yy, w0 - 14, 13, [P(big, font=HEAD, bold=True, size=13, color="FFFFFF", ls=1.0, after=0.5),
                                           P(sub, size=7.4, color="D6E3DA")])
    box(sl, x0 + 7, 139.5, w0 - 14, 0.4, fill="5E8C70")
    text(sl, x0 + 7, 142, w0 - 14, 26, [P("Perkuliahan dan praktik", bold=True, size=8.2, color=Y, after=1),
                                        P("Senin–Sabtu. Diskusi kasus, telaah literatur, publikasi ilmiah, "
                                          "magang klinik dan industri.", size=7.6, color="FFFFFF", ls=1.1)])
    text(sl, x0 + 10, 168, w0 - 20, 14, [P("Dari klinik ke lapangan:", bold=True, size=7.4, color=Y, align="c"),
                                         P("MCU · FTW · PAK · HRA · ergonomi", size=7.4, color="FFFFFF", align="c")])
    pill_label(sl, x0 + 17, 184, w0 - 34, "Akreditasi UNGGUL", fill=Y, col=G, size=7)

    # P3 200-297: requirements + selection/fees, photo bleeding bottom-right, round badge
    kicker(sl, 207, 10, 84, "Persyaratan dan seleksi")
    text(sl, 207, 16, 84, 84, syarat_paras(), name="Teks persyaratan")
    text(sl, 207, 101, 84, 44, biaya_paras(), name="Teks seleksi dan biaya")
    framed(sl, ph("radiograf_dosen"), 214, 148, 83, 62, (31 if v == "C" else 14, 0, 0, 0), .45, .42, tag=v)
    round_badge(sl, 214, 152, 23, "2×", "periode seleksi per tahun")
    pill_label(sl, 222, 195, 70, "Siap bergabung? WA 0852-1151-8148", fill=G, size=7.4)


def build(v):
    prs = new_deck()
    outside(prs, v)
    inside(prs, v)
    name = {"C": "Template 2 - C (Stetoskop)", "D": "Template 2 - D (Keyhole)"}[v]
    out = os.path.join(HERE, f"Flyer Sp.Ok - {name}.pptx")
    prs.save(out)
    return out


if __name__ == "__main__":
    for v in ("C", "D"):
        print(build(v))
