"""Sp.Ok flyer v3: restyle of 'Flyer Kedokteran Okupasi FKUI-1.pdf' into the capsule-brochure look.
All data of that PDF is kept (small fixes agreed: '(dr. )' removed, LBUI -> LBI UI, 'luaskan',
stray full stop). No AI images. Images taken from the PDF where no original exists.
  V1  fasilitas as icons + 7 lecturers (portraits cut from the PDF's page 3)
  V2  fasilitas as numbered list, no lecturers (photo instead)
"""
import os
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from pptx.util import Mm
from pptx.enum.shapes import MSO_SHAPE

import build_flyer as bf
from build_flyer import box, text, P, new_deck, blank, icon, icon_disc, HEAD
from build_template2 import framed

HERE = bf.HERE
A = bf.A
G, Y, INK, SAGE, BG, MUTE = "0E4D2F", "FFD200", "22332A", "E1EAD8", "F4F2EA", "5B6B62"
LIGHT = "D6E3DA"


# ---------------------------------------------------------------- helpers
def grade_pdf_photos():
    src = {"laik_klinik": "p1_x360_605x807.png", "cover_lab": "p1_x185_605x807.png",
           "cover_industri": "p1_x186_384x289.png", "cover_periksa": "p1_x187_384x512.png",
           "gedung": "p2_x395_1870x1052.png"}
    for name, f in src.items():
        out = os.path.join(bf.PH, name + ".jpg")
        im = Image.open(os.path.join(A, "pdf", f)).convert("RGB")
        im = ImageOps.autocontrast(im, cutoff=0.5)
        im = ImageEnhance.Color(im).enhance(1.05)
        im.filter(ImageFilter.UnsharpMask(1.2, 50, 3)).save(out, quality=93)


def ph(n):
    return os.path.join(bf.PH, n + ".jpg")


def cap(sl, x, y, w, h, fill, r=None, name="Kapsul", line=None):
    s = box(sl, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, name=name, line=line)
    r = min(w, h) / 2 if r is None else r
    s.adjustments[0] = min(0.5, r / min(w, h))
    return s


def ttl(sl, x, y, w, t, size=15, col=G, h=8, rule=True, align="l"):
    text(sl, x, y, w, h, [P(t, font=HEAD, bold=True, size=size, color=col, ls=0.98, align=align)])
    if rule:
        box(sl, x, y + h + 1, 12, 0.9, fill=Y, name="Garis aksen")


def para(t, size=7.2, col=INK, **kw):
    return P(runs=t if isinstance(t, list) else [(t, {})], size=size, color=col, ls=1.08, after=0.6, **kw)


def head(t, col=G, first=False, size=8.2):
    return P(t, bold=True, size=size, color=col, before=0 if first else 4.2, after=0.8)


def B(t, **o):
    return (t, {"bold": True, **o})


# ---------------------------------------------------------------- content (from the PDF)
DOK = [("Praktik industri", "Tahap magang/mandiri pada proses pendidikan untuk mengimplementasikan hasil pembelajaran di lapangan/tempat kerja.", "lapangan_briefing", .55, .5),
       ("Penilaian laik kerja", "Pemeriksaan klinis untuk keputusan fit, unfit, atau fit dengan catatan.", "laik_klinik", .55, .55),
       ("Praktikum Radiografi ILO", "Mempelajari pembacaan hasil skrining radiografi ILO pada pekerja terpajan debu dan dengan penyakit paru akibat kerja.", "radiograf_close", .62, .45),
       ("Edukasi pekerja", "Promosi kesehatan dan pencegahan penyakit akibat kerja.", "edukasi_pekerja", .85, .5)]

KARIR = [("tabler_pick", "Migas dan pertambangan"), ("tabler_building-factory-2", "Manufaktur dan industri"),
         ("tabler_building-hospital", "Rumah sakit (K3RS) dan klinik"), ("tabler_shield-check", "BPJS Ketenagakerjaan dan asuransi"),
         ("tabler_briefcase", "Konsultan K3 / HSE"), ("tabler_building-bank", "Pemerintah dan regulator"),
         ("tabler_school", "Pendidikan dan riset")]

VISI = ("Menjadi program studi yang mandiri dan unggul di tingkat global dalam pendidikan, penelitian, "
        "dan pengabdian masyarakat berbasis kedokteran okupasi yang terintegrasi dan inovatif, guna "
        "mewujudkan ekosistem kesehatan pekerja yang tangguh dan bersinambung bagi Indonesia dan dunia.")

MISI = [("tabler_award", "Unggul", "Menghasilkan dokter spesialis Kedokteran Okupasi yang kompeten, berintegritas, dan berdaya saing global."),
        ("tabler_bulb", "Penelitian dan inovasi", "Mengembangkan penelitian translasional yang kolaboratif dan berdampak pada ilmu pengetahuan serta kebijakan kesehatan kerja."),
        ("tabler_users", "Budaya akademik", "Membangun lingkungan akademik yang inklusif, kolaboratif, dan mendukung profesionalisme serta kepemimpinan."),
        ("tabler_heart-handshake", "Kemitraan strategis", "Memperkuat Academic Health System (AHS) melalui kolaborasi dengan rumah sakit pendidikan, pemerintah, dan industri."),
        ("tabler_scale", "Tata kelola bermutu", "Mewujudkan tata kelola yang transparan, akuntabel, efektif, dan berorientasi pada peningkatan mutu berkelanjutan.")]

FASILITAS = [("tabler_chalkboard", "Ruang kuliah dan diskusi akademik."),
             ("tabler_presentation-analytics", "Ruang seminar dan presentasi ilmiah."),
             ("tabler_books", "Perpustakaan dan akses jurnal ilmiah internasional."),
             ("tabler_microscope", "Fasilitas laboratorium pembelajaran berstandar."),
             ("tabler_building-hospital", "Fasilitas rumah sakit pendidikan."),
             ("tabler_building-factory-2", "Wahana praktik dan kunjungan industri."),
             ("tabler_device-laptop", "Fasilitas pembelajaran digital dan e-learning."),
             ("tabler_world", "Akses jejaring kerja sama universitas luar negeri."),
             ("tabler_affiliate", "Jejaring rumah sakit, industri nasional, dan fasilitas pelayanan kesehatan."),
             ("tabler_report-search", "Fasilitas pendukung penelitian dan publikasi ilmiah."),
             ("tabler_users-group", "Kegiatan ekstrakurikuler melalui Kerukunan PPDS Kedokteran Okupasi.")]

DOSEN = ["dr. Dewi Yunia, Sp.Ok",
         "Dr. dr. Dewi Soemarko, MS, Sp.Ok, Subsp. PsiKO (K)",
         "dr. Feni Fitriani Taufik, Sp.P (K), M.Pd.Ked",
         "Dr. dr. Herqutanto, MPH, MARS",
         "dr. Indah Suci Widyahening, M.S, M.Sc, CM-FM, Ph.D",
         "dr. Nuri Purwito Adi, MSc, MKK, Sp.Ok, Subsp. PsiKO (K)",
         "dr. Rina Ladistia Nora, Sp.M (K), PhD"]


def syarat():
    return [head(size=9.0, t="Persyaratan umum", first=True),
            para(size=8.05, t="CV, STR aktif, ijazah dan transkrip Sarjana Kedokteran serta Profesi Dokter yang dilegalisasi, "
                 "dan asuransi kesehatan aktif. Pengalaman klinis diutamakan."),
            head(size=9.0, t="Lulusan Dokter Umum"),
            para(size=8.05, t="Usia maksimal 45 tahun, TOEFL ≥450 (disarankan dari LBI UI), IPK ≥2,75. Bagi yang bekerja, "
                 "sertakan surat rekomendasi atau tugas belajar."),
            head(size=9.0, t="Lulusan Magister Kedokteran Kerja"),
            para(size=8.05, t="Usia maksimal 45 tahun, TOEFL ≥450 (disarankan dari LBI UI), IPK ≥3,00, pengalaman di industri "
                 "terkait minimal 3 tahun, atau penugasan dari daerah atau industri."),
            head(size=9.0, t="Peminatan"),
            para(size=8.05, t=[B("Reguler: "), ("Dokter umum dan lulusan Magister Kedokteran Kerja.", {})]),
            para(size=8.05, t=[B("Khusus: "), ("Lulusan Magister Kedokteran Kerja di lingkungan SKK Migas dengan rekomendasi pejabat berwenang.", {})]),
            head(size=9.0, t="Tahapan seleksi"),
            para(size=8.05, t=[B("2"), (" periode seleksi per tahun:", {})]),
            para(size=8.05, t=[B("Ganjil: "), ("Pendaftaran Februari–Maret, masuk kuliah Agustus.", {})]),
            para(size=8.05, t=[B("Genap: "), ("Pendaftaran Agustus–September, mulai kuliah Februari.", {})]),
            para(size=8.05, t="Tes meliputi Tes Potensi Akademik, Bahasa Inggris, psikotes (MMPI dan wawancara psikiatri), "
                 "serta ujian tulis dan wawancara di program studi.", before=1.5)]


def biaya():
    W = "FFFFFF"
    return [P(runs=[B("Biaya pendaftaran ", color=Y), ("(tahun 2026)", {"italic": True, "color": Y})], size=8.2, after=1),
            para([B("Rp1.650.000"), (" · TPA dan Bahasa Inggris (SIMAK UI)", {})], col=W),
            para([B("Rp600.000"), (" · Tes psikiatri (Bagian Psikiatri FKUI-RSCM)", {})], col=W),
            P(runs=[B("Biaya pendidikan per semester ", color=Y), ("(tahun 2026)", {"italic": True, "color": Y})], size=8.2, before=4, after=1),
            para([B("Rp25.000.000"), (" · Reguler", {})], col=W),
            para([B("Rp33.000.000"), (" · Khusus", {})], col=W)]


# ---------------------------------------------------------------- OUTSIDE
def outside(prs):
    sl = blank(prs, "Luar")
    box(sl, 0, 0, 297, 210, fill=BG, name="Latar")

    # flap: dokumentasi
    text(sl, 6, 7, 86, 15, [P("Dokumentasi beberapa aktivitas pendidikan", font=HEAD, bold=True, size=14, color=G, ls=0.98)])
    box(sl, 6, 22.5, 12, 0.9, fill=Y)
    for i, (t, d, ph_, fx, fy) in enumerate(DOK):
        y = 26.5 + i * 44.5
        cap(sl, 4, y, 89, 42, SAGE, name="Kapsul " + t)
        framed(sl, ph(ph_), 6, y + 3, 36, 36, (18, 18, 18, 18), fx, fy, tag="v3")
        text(sl, 45, y + 3, 44, 36, [P(t, font=HEAD, bold=True, size=9.4, color=G, after=1.5, ls=1.0),
                                     P(d, size=7.2, color=INK, ls=1.08)], anchor="m")

    # back: peluang karir + kontak
    cap(sl, 101, 5, 92, 98, SAGE, r=18, name="Kapsul peluang karir")
    ttl(sl, 109, 12, 78, "Peluang karir")
    for i, (ic, t) in enumerate(KARIR):
        yy = 28 + i * 9.6
        icon_disc(sl, ic, 109, yy, 7, G, "FFFFFF")
        text(sl, 118.5, yy, 70, 7, [P(t, size=8.8, color=INK)], anchor="m")
    cap(sl, 101, 107, 92, 98, G, r=18, name="Kapsul kontak")
    framed(sl, ph("lapangan_gudang"), 101, 107, 92, 44, (18, 18, 0, 0), .55, .5, tag="v3")
    box(sl, 101, 150.4, 92, 1.3, fill=Y)
    text(sl, 109, 155, 78, 8, [P("Kontak kami", font=HEAD, bold=True, size=14, color="FFFFFF")])
    text(sl, 109, 164, 78, 5, [P("Sekretariat Program Studi", bold=True, size=8.6, color=Y)])
    rows = [("tabler_map-pin", ["Departemen Ilmu Kedokteran Komunitas FK UI", "Jl. Pegangsaan Timur No.16, Jakarta, 10320"], 8.4),
            ("tabler_phone", ["Telp/Fax: +62 21 31905502"], 5.2),
            ("tabler_mail", ["Email: ppds.okupasi@ui.ac.id"], 5.2)]
    yy = 171
    for ic, lines, h in rows:
        icon(sl, ic, "FFD200", 109, yy + 0.2, 4)
        text(sl, 115, yy, 74, h, [P(l, size=7.8, color="FFFFFF", ls=1.05) for l in lines])
        yy += h + 1.6

    # cover
    box(sl, 197, 0, 100, 210, fill=G, name="Latar sampul")
    framed(sl, ph("gedung"), 197, 0, 100, 92, (0, 0, 40, 40), .5, .5, tag="v3")
    logo = sl.shapes.add_picture(os.path.join(A, "pdf", "p1_x184_290x122.png"), Mm(246), Mm(6), Mm(46), Mm(46 / 2.377))
    logo.name = "Logo FKUI"
    text(sl, 204, 96, 88, 5, [P("PROGRAM STUDI", bold=True, size=8.6, color=Y, spc=200)])
    text(sl, 204, 102, 88, 20, [P("SPESIALIS", font=HEAD, bold=True, size=15, color="FFFFFF", ls=0.95),
                                P("KEDOKTERAN OKUPASI", font=HEAD, bold=True, size=15, color="FFFFFF", ls=0.95),
                                P("(Sp. Ok)", font=HEAD, bold=True, size=15, color=Y, ls=0.95)])
    box(sl, 204, 124, 12, 0.9, fill=Y)
    text(sl, 204, 127, 88, 11, [P("Dari klinik ke industri,", italic=True, size=9.6, color="FFFFFF", ls=1.05),
                                P("luaskan peranmu sebagai dokter.", italic=True, size=9.6, color="FFFFFF", ls=1.05)])
    for i, (n, fx, fy) in enumerate([("cover_lab", .5, .4), ("cover_industri", .62, .5), ("cover_periksa", .5, .5)]):
        framed(sl, ph(n), 204 + i * 30, 141, 28.5, 42, (14.25,) * 4, fx, fy, tag="v3")
    icon(sl, "tabler_award", "FFD200", 204, 187.4, 4.4)
    text(sl, 209.5, 187, 52, 5.4, [P("Terakreditasi LAM-PTKes: Unggul", bold=True, size=7.4, color="FFFFFF")], anchor="m")
    cap(sl, 262, 186.2, 30.5, 7.2, Y, name="Apply now")
    text(sl, 262, 186.2, 30.5, 7.2, [P("APPLY NOW", bold=True, size=8, color=G, align="c", spc=80)], anchor="m")
    text(sl, 230, 196.5, 62.5, 5, [P("enrollment.ui.ac.id", size=7.8, color="FFFFFF", align="r")])


# ---------------------------------------------------------------- INSIDE
def inside(prs, v):
    sl = blank(prs, "Dalam")
    box(sl, 0, 0, 297, 210, fill=BG, name="Latar")

    # P1 visi + misi (+ dosen in V1)
    ttl(sl, 6, 7, 88, "Visi dan Misi")
    cap(sl, 4, 20, 92, 40, G, r=16, name="Kapsul visi")
    text(sl, 11, 22.5, 78, 35, [P("VISI", bold=True, size=7.6, color=Y, spc=200, align="c", after=1.5),
                                P("“" + VISI + "”", font=HEAD, italic=True, size=8.2, color="FFFFFF", align="c", ls=1.1)],
         anchor="m")
    misi_h = 78 if v == "V1" else 84
    cap(sl, 4, 63, 92, misi_h, SAGE, r=14, name="Kapsul misi")
    text(sl, 10, 65.5, 80, 5, [P("MISI", bold=True, size=7.6, color=G, spc=200)])
    step = (misi_h - 9) / 5
    for i, (ic, t, d) in enumerate(MISI):
        yy = 71.5 + i * step
        icon_disc(sl, ic, 9, yy, 6.4, G, "FFFFFF")
        text(sl, 18, yy - 0.4, 75, step, [P(t, bold=True, size=8, color=G, after=0.3, ls=1.0),
                                         P(d, size=6.9, color=INK, ls=1.05)])
    if v == "V1":
        cap(sl, 4, 144, 92, 62, G, r=16, name="Kapsul dosen")
        text(sl, 4, 146.5, 92, 6, [P("Dosen pengajar", font=HEAD, bold=True, size=10, color="FFFFFF", align="c")])
        d = 15
        spots = [(4 + 92 * (i + .5) / 4, 153.5, 22.5) for i in range(4)] + [(4 + 92 * (i + .5) / 3, 177.5, 29) for i in range(3)]
        for i, ((cx, cy, nw), name) in enumerate(zip(spots, DOSEN), 1):
            p = sl.shapes.add_picture(os.path.join(A, "dosen", f"dosen_{i}.png"), Mm(cx - d / 2), Mm(cy), Mm(d), Mm(d))
            p.name = f"Dosen {i}"
            box(sl, cx - d / 2, cy, d, d, line=Y, lw=1.1, shape=MSO_SHAPE.OVAL, name="Cincin")
            text(sl, cx - nw / 2, cy + d + 0.6, nw, 7.5, [P(name, bold=True, size=5.8, color="FFFFFF", align="c", ls=1.0)])
    else:
        framed(sl, ph("diskusi_toraks"), 4, 150, 92, 56, (28, 28, 28, 28), .45, .45, tag="v3")

    # P2 persyaratan dan biaya
    ttl(sl, 106, 7, 88, "Persyaratan dan Biaya")
    cap(sl, 104, 20, 92, 112, SAGE, r=14, name="Kapsul persyaratan")
    text(sl, 110, 23.5, 81, 107, syarat(), name="Teks persyaratan")
    cap(sl, 104, 135, 92, 40, G, r=14, name="Kapsul biaya")
    text(sl, 110, 137.5, 81, 35, biaya(), name="Teks biaya", anchor="m")
    framed(sl, ph("lab_pipet"), 104, 178, 92, 28, (14,) * 4, .55, .4, tag="v3")

    # P3 kurikulum dan fasilitas
    text(sl, 205, 7, 88, 8, [P("Kurikulum dan Fasilitas Pendidikan", font=HEAD, bold=True, size=14, color=G, ls=0.98)])
    box(sl, 205, 16.5, 12, 0.9, fill=Y)
    for i, (big, sub) in enumerate([("7 semester (98 SKS)", "Lulusan dokter umum"),
                                    ("4 semester (65 SKS)", "Lulusan Magister Kedokteran Kerja")]):
        x = 204 + i * 46
        cap(sl, x, 25, 44, 18, Y, name="Kapsul kurikulum")
        text(sl, x + 3, 25, 38, 18, [P(big, font=HEAD, bold=True, size=9.6, color=G, align="c", ls=1.0, after=0.5),
                                     P(sub, size=6.6, color=G, align="c", ls=1.0)], anchor="m")
    cap(sl, 204, 46, 90, 31, "FFFFFF", r=10, name="Kapsul tahap")
    tp = sl.shapes.add_picture(os.path.join(A, "pdf", "p2_x220_652x218.png"), Mm(207), Mm(47.5), Mm(84), Mm(84 / 2.99))
    tp.name = "Tahap pendidikan"
    cap(sl, 204, 80, 90, 66, SAGE, r=12, name="Kapsul fasilitas")
    text(sl, 210, 82.5, 78, 5, [P("Fasilitas Perkuliahan", bold=True, size=8.4, color=G)])
    if v == "V1":
        for i, (ic, t) in enumerate(FASILITAS):
            cx, cy = 208 + (i % 2) * 43, 89 + (i // 2) * 9.4
            icon_disc(sl, ic, cx, cy, 6.2, G, "FFFFFF")
            text(sl, cx + 7.4, cy - 0.6, 35, 8.6, [P(t, size=6.5, color=INK, ls=1.02)], anchor="m")
    else:
        text(sl, 210, 89.5, 80, 56, [P(f"{i}. {t}", size=7.5, color=INK, ls=1.05, after=1.35)
                                   for i, (_, t) in enumerate(FASILITAS, 1)])
    cap(sl, 204, 149, 90, 57, "FFFFFF", r=12, name="Kapsul kerjasama")
    text(sl, 208, 151.5, 82, 9, [P("Kerjasama program studi dengan universitas dan lembaga dalam penyelenggaraan pendidikan",
                                   bold=True, size=7.6, color=G, align="c", ls=1.05)])
    a = sl.shapes.add_picture(os.path.join(A, "pdf", "p2_x221_392x56.png"), Mm(213), Mm(162), Mm(72), Mm(72 / 7.0))
    a.name = "Logo mitra 1"
    b = sl.shapes.add_picture(os.path.join(A, "pdf", "p2_x222_399x149.png"), Mm(213), Mm(173.5), Mm(72), Mm(72 / 2.678))
    b.name = "Logo mitra 2"


def build(v):
    bf.SECT.update(head=8.6, body=7.9, gap=7.5)
    prs = new_deck()
    outside(prs)
    inside(prs, v)
    name = {"V1": "V1 (ikon + dosen)", "V2": "V2 (tanpa dosen)"}[v]
    out = os.path.join(HERE, f"Flyer Sp.Ok v3 - {name}.pptx")
    prs.save(out)
    return out


if __name__ == "__main__":
    grade_pdf_photos()
    for v in ("V1", "V2"):
        print(build(v))
