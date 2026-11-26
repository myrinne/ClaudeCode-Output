"""Build the Sp.Ok career-update trifold flyer (A4 landscape, double-sided) as editable PPTX.

Two concepts:
  A  "Hijau UI x Sehari sebagai Sp.Ok"   (concept 1 + 2)
  B  "Di balik pintu pabrik x Peta pajanan" (concept 5 + 6)

Every text, shape and photo is a separate element so the file imports into Canva
(Upload -> .pptx) as an editable design. Fonts: Lora (headings) + Open Sans (body),
both available in Canva. Photos are pre-cropped to their frames (Canva-safe).

Roll fold, panel widths (mm):
  outside: [inner flap 97 | back 100 | cover 100]
  inside : [100 | 100 | 97]
"""
import os
from PIL import Image
from pptx import Presentation
from pptx.util import Mm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.dml import MSO_LINE
from pptx.oxml.ns import qn
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
PH = os.path.join(A, "photos")
ICO = os.path.join(A, "icons")
CROP = os.path.join(A, "crops")
os.makedirs(CROP, exist_ok=True)

HEAD, BODY = "Lora", "Open Sans"

# ----------------------------------------------------------------- helpers
def rgb(h):
    return RGBColor.from_string(h.strip("#").upper())


def box(sl, x, y, w, h, fill=None, alpha=None, line=None, lw=0.75,
        shape=MSO_SHAPE.RECTANGLE, name=None):
    s = sl.shapes.add_shape(shape, Mm(x), Mm(y), Mm(w), Mm(h))
    st = s._element.find(qn("p:style"))
    if st is not None:
        s._element.remove(st)
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:
            clr = s.fill._xPr.find(qn("a:solidFill"))[0]
            etree.SubElement(clr, qn("a:alpha")).set("val", str(int(alpha * 100000)))
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(lw)
    else:
        s.line.fill.background()
    if s.has_text_frame:
        s.text_frame.text = ""
    if name:
        s.name = name
    return s


DEF = dict(font=BODY, size=8, bold=False, italic=False, color="1E2A27",
           align="l", after=0, before=0, ls=1.12, spc=0)


def P(text=None, runs=None, **kw):
    d = dict(kw)
    d["runs"] = runs if runs is not None else [(text, {})]
    return d


def text(sl, x, y, w, h, paras, anchor="t", name=None):
    tb = sl.shapes.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        st = dict(DEF)
        st.update({k: v for k, v in p.items() if k != "runs"})
        para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[st["align"]]
        para.space_after = Pt(st["after"])
        para.space_before = Pt(st["before"])
        para.line_spacing = st["ls"]
        for t, o in p["runs"]:
            s2 = dict(st)
            s2.update(o)
            r = para.add_run()
            r.text = t
            f = r.font
            f.name = s2["font"]
            f.size = Pt(s2["size"])
            f.bold = s2["bold"]
            f.italic = s2["italic"]
            f.color.rgb = rgb(s2["color"])
            if s2["spc"]:
                r._r.get_or_add_rPr().set("spc", str(s2["spc"]))
    if name:
        tb.name = name
    return tb


def photo(sl, name, x, y, w, h, fx=0.5, fy=0.5, zoom=1.0):
    """Pre-crop the photo to the frame aspect around focus (fx, fy), then place it."""
    im = Image.open(os.path.join(PH, name + ".jpg"))
    iw, ih = im.size
    ar = w / h
    if iw / ih > ar:
        cw, ch = int(ih * ar), ih
    else:
        cw, ch = iw, int(iw / ar)
    cw, ch = int(cw / zoom), int(ch / zoom)
    l = min(max(int(fx * iw - cw / 2), 0), iw - cw)
    t = min(max(int(fy * ih - ch / 2), 0), ih - ch)
    out = os.path.join(CROP, f"{name}_{int(w)}x{int(h)}.jpg")
    im.crop((l, t, l + cw, t + ch)).save(out, quality=92)
    pic = sl.shapes.add_picture(out, Mm(x), Mm(y), Mm(w), Mm(h))
    pic.name = "Foto " + name
    return pic


def icon(sl, key, col, x, y, s):
    p = os.path.join(ICO, f"{key}_{col.strip('#').upper()}.png")
    pic = sl.shapes.add_picture(p, Mm(x), Mm(y), Mm(s), Mm(s))
    pic.name = "Ikon " + key
    return pic


def icon_disc(sl, key, x, y, d, disc, icol, ring=None):
    box(sl, x, y, d, d, fill=disc, shape=MSO_SHAPE.OVAL, line=ring, lw=1.25)
    m = d * 0.22
    icon(sl, key, icol, x + m, y + m, d - 2 * m)


def line(sl, x1, y1, x2, y2, col, w=0.75, dash=False):
    c = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Mm(x1), Mm(y1), Mm(x2), Mm(y2))
    c.line.color.rgb = rgb(col)
    c.line.width = Pt(w)
    if dash:
        c.line.dash_style = MSO_LINE.DASH
    return c


def heading(sl, x, y, w, txt, Pl, size=17, h=9, rule=True):
    text(sl, x, y, w, h, [P(txt, font=HEAD, size=size, bold=True, color=Pl["dark"], ls=1.0)])
    if rule:
        box(sl, x, y + h + 1.2, 12, 0.9, fill=Pl["accent"], name="Garis aksen")
    return y + h + 4


# ----------------------------------------------------------------- content
DOING = [
    ("tabler_stethoscope", "MCU dan surveilans", "Pra-kerja, berkala, khusus; memantau tren kesehatan pekerja."),
    ("tabler_clipboard-check", "Laik kerja (FTW/RTW)", "Fit, unfit, atau fit dengan restriksi; kembali bekerja."),
    ("tabler_lungs", "Diagnosis PAK", "Tujuh langkah diagnosis penyakit akibat kerja."),
    ("tabler_building-factory-2", "Survei tempat kerja", "Walk-through survey, HRA, dan pengendalian bahaya."),
    ("tabler_stretching", "Ergonomi", "Postur, angkat-angkut, dan desain pekerjaan."),
    ("tabler_flask", "Toksikologi industri", "Pajanan bahan kimia dan biomonitoring."),
    ("tabler_wheelchair", "Penilaian kecacatan", "Persentase kecacatan untuk jaminan sosial."),
    ("tabler_speakerphone", "Promosi kesehatan", "Edukasi pekerja dan program kesehatan kerja."),
]

WORKPLACES = [
    ("tabler_pick", "Migas dan pertambangan"),
    ("tabler_building-factory-2", "Manufaktur dan industri"),
    ("tabler_building-hospital", "Rumah sakit (K3RS) dan klinik"),
    ("tabler_shield-check", "BPJS Ketenagakerjaan dan asuransi"),
    ("tabler_briefcase", "Konsultan K3 / HSE"),
    ("tabler_building-bank", "Pemerintah dan regulator"),
    ("tabler_school", "Pendidikan dan riset"),
]

VISI = ("Menjadi program studi yang mandiri dan unggul di tingkat global dalam pendidikan, "
        "penelitian, dan pengabdian masyarakat berbasis kedokteran okupasi yang terintegrasi "
        "dan inovatif, guna mewujudkan ekosistem kesehatan pekerja yang tangguh dan "
        "bersinambung bagi Indonesia dan dunia.")


def sect(title, body_runs, Pl, first=False):
    """Subheading + body paragraphs for a flowing text box."""
    out = [P(title, bold=True, size=8.6, color=Pl["dark"], before=0 if first else 7.5, after=1.5)]
    for runs in body_runs:
        out.append(P(runs=runs if isinstance(runs, list) else [(runs, {})], size=7.9, color=Pl["text"], after=1))
    return out


def B(t):
    return (t, {"bold": True})


def persyaratan_paras(Pl):
    p = []
    p += sect("Persyaratan umum", ["CV, STR aktif, ijazah dan transkrip Sarjana Kedokteran serta Profesi "
                                    "Dokter yang dilegalisasi, dan asuransi kesehatan aktif. Pengalaman klinis diutamakan."], Pl, True)
    p += sect("Lulusan dokter umum", ["Usia maksimal 45 tahun, TOEFL ≥450 (diutamakan dari LBUI), IPK ≥2,75. "
                                       "Bagi yang bekerja, sertakan surat rekomendasi atau tugas belajar."], Pl)
    p += sect("Lulusan Magister Kedokteran Kerja", ["Usia maksimal 45 tahun, TOEFL ≥450 (LIA atau LBI UI), IPK ≥3,00, "
                                                     "pengalaman di industri terkait minimal 3 tahun, atau penugasan dari daerah atau industri."], Pl)
    p += sect("Peminatan", [[B("Reguler"), (" · Dokter umum dan lulusan Magister Kedokteran Kerja.", {})],
                            [B("Khusus"), (" · Lulusan Magister Kedokteran Kerja di lingkungan SKK Migas "
                                           "dengan rekomendasi pejabat berwenang.", {})]], Pl)
    p += sect("Tahapan seleksi", ["Tes Potensi Akademik, Bahasa Inggris, psikotes, ujian tertulis, dan wawancara."], Pl)
    p += sect("MMPI dan wawancara psikiatrik", [[("Wajib bagi calon peserta PPDS. Jadwal dan pendaftaran: ", {}),
                                                 ("@pusbangki.fkui", {"bold": True, "color": Pl["link"]})],
                                                [("Kontak UKK Pusbangki: ", {}), ("+62 812-2678-7767", {"bold": True, "color": Pl["link"]})]], Pl)
    return p


def biaya_paras(Pl):
    p = []
    p += sect("Perkuliahan dan praktik", ["Senin–Sabtu, sesuai jadwal. Diskusi kasus, telaah literatur, "
                                           "publikasi ilmiah, serta magang klinik dan industri."], Pl, True)
    p += sect("Dua periode seleksi per tahun", [[B("Ganjil"), (" · Unggah data Februari–Maret, masuk kuliah Agustus.", {})],
                                                [B("Genap"), (" · Daftar Agustus–September, mulai kuliah Februari.", {})]], Pl)
    p += sect("Biaya pendaftaran", [[B("Rp1.650.000"), (" · TPA dan Bahasa Inggris (SIMAK UI)", {})],
                                    [B("Rp600.000"), (" · Tes psikiatri (Bagian Psikiatri FKUI-RSCM)", {})]], Pl)
    p += sect("Biaya pendidikan per semester", [[B("Rp25.000.000"), (" · Reguler (WNI)", {})],
                                                [B("Rp33.000.000"), (" · Khusus (S1 Non-UI)", {})]], Pl)
    p += sect("Pendaftaran daring", [[("Hanya melalui ", {}), ("enrollment.ui.ac.id", {"bold": True, "color": Pl["link"]}),
                                      (", tanpa melalui CHS.", {})]], Pl)
    return p


def doing_grid(sl, x, y, Pl, cw=42, rh=19):
    for i, (ic, t, d) in enumerate(DOING):
        cx, cy = x + (i % 2) * (cw + 2), y + (i // 2) * rh
        icon_disc(sl, ic, cx, cy, 8.5, Pl["disc"], "FFFFFF")
        text(sl, cx + 10.5, cy - 0.3, cw - 10.5, rh - 1,
             [P(t, bold=True, size=8, color=Pl["dark"], after=1, ls=1.0),
              P(d, size=7, color=Pl["text"], ls=1.05)])


def workplaces_list(sl, x, y, Pl, rh=7.4, w=84):
    for i, (ic, t) in enumerate(WORKPLACES):
        cy = y + i * rh
        icon_disc(sl, ic, x, cy, 6, Pl["disc"], "FFFFFF")
        text(sl, x + 8.5, cy, w - 8.5, 6, [P(t, size=8.4, color=Pl["text"], bold=False)], anchor="m")


def contact_block(sl, x, y, w, Pl, col_text, col_head, icol):
    text(sl, x, y, w, 12, [
        P("Admin PPDS Kedokteran Okupasi", bold=True, size=8.4, color=col_head, after=1),
        P("Departemen Ilmu Kedokteran Komunitas FKUI", size=7.6, color=col_text),
        P("Jl. Pegangsaan Timur No. 16, Jakarta 10320", size=7.6, color=col_text)])
    rows = [("tabler_brand-whatsapp", "0852-1151-8148"), ("tabler_mail", "ppds.okupasi@ui.ac.id")]
    for i, (ic, t) in enumerate(rows):
        yy = y + 14 + i * 5.4
        icon(sl, ic, icol, x, yy, 4)
        text(sl, x + 5.6, yy - 0.2, w - 6, 4.4, [P(t, size=7.9, bold=True, color=col_head)], anchor="m")


def qr_pair(sl, x, y, Pl, col_head, col_text, s=21, gap=22):
    items = [("qr_pendaftaran", "Pendaftaran", "enrollment.ui.ac.id"),
             ("qr_profil", "Profil prodi", "fk.ui.ac.id")]
    for i, (q, t, u) in enumerate(items):
        xx = x + i * (s + gap)
        box(sl, xx, y, s, s, fill="FFFFFF")
        pic = sl.shapes.add_picture(os.path.join(A, q + ".png"), Mm(xx + 0.8), Mm(y + 0.8), Mm(s - 1.6), Mm(s - 1.6))
        pic.name = "QR " + t
        text(sl, xx, y + s + 1.5, s + gap - 2, 8, [P(t, bold=True, size=7.8, color=col_head, ls=1.0),
                                                   P(u, size=7, color=col_text, ls=1.0)])


def logo_plate(sl, x, y, w=60):
    h = w / 2.866
    box(sl, x, y, w + 4, h + 3, fill="FFFFFF", name="Pelat logo")
    pic = sl.shapes.add_picture(os.path.join(A, "logo-FKUI.png"), Mm(x + 2), Mm(y + 1.5), Mm(w), Mm(h))
    pic.name = "Logo FKUI"


def badge(sl, x, y, w, t, border, col, h=6.4, fill=None):
    s = box(sl, x, y, w, h, fill=fill, line=border, lw=0.9)
    text(sl, x, y, w, h, [P(t, size=6.8, bold=True, color=col, align="c")], anchor="m")


def cta(sl, x, y, w, h, fill, head_col, body_col):
    box(sl, x, y, w, h, fill=fill, name="Ajakan")
    text(sl, x + 4, y + 2.5, w - 8, h - 4, [
        P("Siap bergabung?", font=HEAD, bold=True, size=11, color=head_col, after=1.5, ls=1.0),
        P("Pindai QR di panel belakang atau hubungi WA:", size=7.6, color=body_col),
        P("0852-1151-8148", bold=True, size=8.4, color=body_col)])


def new_deck():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Mm(297), Mm(210)
    return prs


def blank(prs, name):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    sl.name = name
    return sl


# ================================================================ CONCEPT A
PA = dict(dark="0E4D2F", accent="D9A400", bg1="FBF7EC", bg2="EAF0DF", text="22332A", muted="5B6B62",
          disc="0E4D2F", link="1F7A4A", yellow="FFD400")


def concept_a():
    Pl = PA
    prs = new_deck()

    # ---------------- OUTSIDE: flap | back | cover
    sl = blank(prs, "Luar")
    # flap 0-97 : Sehari sebagai Sp.Ok
    box(sl, 0, 0, 97, 210, fill=Pl["bg2"], name="Latar panel lipat")
    heading(sl, 7, 10, 84, "Sehari sebagai Sp.Ok", Pl)
    text(sl, 7, 24, 84, 8, [P("Dari lapangan, klinik, sampai ruang diskusi kasus.", size=8.2, italic=True, color=Pl["muted"])])
    rows = [("07.30", "Turun ke lapangan", "Safety briefing dan walk-through survey untuk mengenali bahaya di area kerja.", "lapangan_briefing", .55, .5),
            ("10.00", "Penilaian laik kerja", "Pemeriksaan klinis untuk keputusan fit, unfit, atau fit dengan restriksi.", "periksa_fisik", .5, .45),
            ("13.00", "Diskusi radiograf toraks", "Menelaah kasus pajanan debu dan penyakit paru akibat kerja.", "radiograf_close", .55, .4),
            ("15.00", "Edukasi pekerja", "Promosi kesehatan dan pencegahan penyakit akibat kerja.", "edukasi_pekerja", .8, .5)]
    y0, rh = 35, 39.5
    line(sl, 45, y0 + 2, 45, y0 + 3 * rh + 2, "9BBF5A", 1.25)
    for i, (tm, tt, dd, ph, fx, fy) in enumerate(rows):
        yy = y0 + i * rh
        photo(sl, ph, 7, yy, 34, 31, fx, fy)
        box(sl, 43.2, yy + 0.4, 3.6, 3.6, fill=Pl["accent"], shape=MSO_SHAPE.OVAL, line="FFFFFF", lw=1)
        text(sl, 49, yy, 42, 31, [P(tm, bold=True, size=8, color=Pl["accent"], after=1),
                                   P(tt, font=HEAD, bold=True, size=10, color=Pl["dark"], after=2, ls=1.0),
                                   P(dd, size=7.5, color=Pl["text"])])
    text(sl, 7, 195, 84, 6, [P("Ilustrasi kegiatan; ritme kerja menyesuaikan tempat kerja.", size=6.5, italic=True, color=Pl["muted"])])

    # back 97-197 : tempat kerja + informasi
    box(sl, 97, 0, 100, 210, fill=Pl["bg1"], name="Latar panel belakang")
    photo(sl, "lapangan_gudang", 97, 0, 100, 40, .55, .55)
    heading(sl, 104, 46, 86, "Tempat kerja lulusan", Pl)
    workplaces_list(sl, 104, 61, Pl)
    heading(sl, 104, 117, 86, "Informasi", Pl)
    contact_block(sl, 104, 131, 86, Pl, Pl["text"], Pl["dark"], "0E4D2F")
    qr_pair(sl, 104, 158, Pl, Pl["dark"], Pl["text"])

    # cover 197-297
    photo(sl, "cover_radiograf", 197, 0, 100, 130, .42, .5)
    logo_plate(sl, 203, 7)
    box(sl, 197, 130, 100, 80, fill=Pl["dark"], name="Blok hijau sampul")
    box(sl, 197, 128.8, 100, 1.4, fill=Pl["yellow"], name="Garis kuning")
    text(sl, 205, 137, 86, 5, [P("PROGRAM STUDI", bold=True, size=8, color=Pl["yellow"], spc=200)])
    text(sl, 205, 143, 86, 20, [P("Spesialis Kedokteran Okupasi", font=HEAD, bold=True, size=20, color="FFFFFF", ls=0.95)])
    text(sl, 205, 160.5, 86, 8, [P("(Sp.Ok)", font=HEAD, bold=True, size=15, color=Pl["yellow"])])
    box(sl, 205, 171, 12, 0.9, fill=Pl["yellow"])
    text(sl, 205, 175, 86, 9, [P("Dokter bagi pekerja, dokter bagi tempat kerja.", size=9, italic=True, color="FFFFFF")])
    badge(sl, 205, 192, 31, "Akreditasi UNGGUL", Pl["yellow"], "FFFFFF")
    badge(sl, 238.5, 192, 50, "Prodi Sp.Ok pertama di Indonesia", Pl["yellow"], "FFFFFF")

    # ---------------- INSIDE: P1 | P2 | P3
    sl = blank(prs, "Dalam")
    box(sl, 0, 0, 100, 210, fill=Pl["bg1"], name="Latar panel 1")
    heading(sl, 7, 10, 86, "Apa yang dikerjakan Sp.Ok?", Pl, size=16)
    text(sl, 7, 24, 86, 9, [P("Melayani tiga sasaran: komunitas pekerja, individu, dan masyarakat sekitar industri.",
                              size=7.9, color=Pl["text"])])
    doing_grid(sl, 7, 36, Pl)
    box(sl, 7, 114, 86, 33, fill=Pl["bg2"], name="Kotak visi")
    box(sl, 7, 114, 1.4, 33, fill=Pl["accent"])
    text(sl, 12, 117.5, 78, 28, [P("VISI", bold=True, size=7.5, color=Pl["accent"], spc=150, after=2),
                               P("“" + VISI + "”", italic=True, size=7.6, color=Pl["dark"], ls=1.15)])
    box(sl, 7, 151, 86, 21, fill=Pl["dark"], name="Kotak gelar")
    text(sl, 12, 154, 78, 16, [P("GELAR LULUSAN", bold=True, size=7.5, color=Pl["yellow"], spc=150, after=2),
                               P(runs=[("Spesialis Kedokteran Okupasi ", {}), ("(Sp.Ok)", {"color": Pl["yellow"]})],
                                 font=HEAD, bold=True, size=11.5, color="FFFFFF", ls=1.0)])
    photo(sl, "lab_pipet", 7, 176, 86, 27, .55, .4)

    box(sl, 100, 0, 100, 210, fill=Pl["bg2"], name="Latar panel 2")
    heading(sl, 107, 10, 86, "Persyaratan peserta", Pl)
    text(sl, 107, 26, 86, 132, persyaratan_paras(Pl), name="Teks persyaratan")
    photo(sl, "diskusi_toraks", 107, 143, 86, 58, .45, .45)

    box(sl, 200, 0, 97, 210, fill=Pl["bg1"], name="Latar panel 3")
    heading(sl, 207, 10, 83, "Pembelajaran dan biaya", Pl)
    for i, (big, sub) in enumerate([("7 semester · 98 SKS", "Lulusan dokter umum"),
                                    ("4 semester · tambahan 65 SKS", "Lulusan Magister Kedokteran Kerja")]):
        yy = 26 + i * 17
        box(sl, 207, yy, 83, 15, fill=Pl["bg2"])
        box(sl, 207, yy, 1.4, 15, fill=Pl["dark"])
        text(sl, 211, yy + 1.8, 77, 12, [P(big, font=HEAD, bold=True, size=11.5, color=Pl["dark"], after=1, ls=1.0),
                                         P(sub, size=7.4, color=Pl["text"])])
    text(sl, 207, 64, 83, 80, biaya_paras(Pl), name="Teks pembelajaran dan biaya")
    photo(sl, "radiograf_dosen", 207, 146, 83, 32, .45, .5)
    cta(sl, 207, 180, 83, 21, Pl["dark"], Pl["yellow"], "FFFFFF")

    out = os.path.join(HERE, "Flyer Sp.Ok - Konsep A (Hijau UI x Sehari sebagai Sp.Ok).pptx")
    prs.save(out)
    return out


# ================================================================ CONCEPT B
PB = dict(dark="1B2622", deep="0F4B33", accent="FFC20E", bg1="F4F2EC", bg2="E4E8E1", text="1E2A27",
          muted="5E6B66", disc="0F4B33", link="0F4B33", steel="3A4A44")


def hazard_stripe(sl, x, y, w, h, step=7):
    box(sl, x, y, w, h, fill="FFC20E", name="Garis bahaya")
    xx = x - h
    while xx < x + w:
        a, b = max(xx, x), min(xx + step / 2 + h, x + w)
        if b - a > h * 0.6:
            s = box(sl, a, y, b - a, h, fill="1B2622", shape=MSO_SHAPE.PARALLELOGRAM)
            s.adjustments[0] = min(0.9, h / (b - a))
        xx += step


def concept_b():
    Pl = PB
    prs = new_deck()

    # ---------------- OUTSIDE
    sl = blank(prs, "Luar")
    # flap: peta pajanan
    box(sl, 0, 0, 97, 210, fill=Pl["bg1"], name="Latar panel lipat")
    text(sl, 7, 10, 84, 8, [P("Satu pekerja, banyak bahaya.", font=HEAD, bold=True, size=15, color=Pl["dark"], ls=1.0)])
    text(sl, 7, 18.5, 84, 7, [P("Satu spesialis yang melihat semuanya.", font=HEAD, italic=True, size=11, color=Pl["deep"])])
    hazard_stripe(sl, 7, 28, 16, 2.2, step=4)
    text(sl, 7, 33, 84, 10, [P(runs=[("Lima faktor bahaya lingkungan kerja ", {}),
                                     ("(Permenaker No. 5 Tahun 2018)", {"bold": True}),
                                     (": fisika, kimia, biologi, ergonomi, dan psikologi.", {})],
                               size=7.4, color=Pl["muted"])])
    cx, cy, rx, ry, d = 48.5, 110, 33, 41, 14
    hz = [("tabler_volume", "Bising"), ("tabler_temperature-sun", "Panas"), ("tabler_flask-2", "Bahan kimia"),
          ("tabler_biohazard", "Biologis"), ("tabler_brain", "Psikososial"), ("tabler_stretching", "Ergonomi"),
          ("tabler_wind", "Debu"), ("tabler_radioactive", "Radiasi")]
    import math
    pos = []
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        pos.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
    for (px, py) in pos:
        line(sl, cx, cy, px, py, "9AA59F", 0.75, dash=True)
    box(sl, cx - 21, cy - 21, 42, 42, fill=Pl["bg2"], shape=MSO_SHAPE.OVAL, name="Lingkar pekerja")
    icon(sl, "healthicons_construction-worker", "1E2A27", cx - 16, cy - 17, 32)
    for (px, py), (ic, lab) in zip(pos, hz):
        icon_disc(sl, ic, px - d / 2, py - d / 2, d, Pl["deep"], "FFFFFF", ring="FFC20E")
        text(sl, px - 12, py + d / 2 + 0.6, 24, 4, [P(lab, bold=True, size=7, color=Pl["dark"], align="c")])
    box(sl, 7, 172, 83, 26, fill=Pl["dark"], name="Kotak peran")
    text(sl, 11, 175.5, 75, 21, [P("Di sinilah peran Sp.Ok", font=HEAD, bold=True, size=10, color=Pl["accent"], after=2),
                                 P("Menilai pajanan, mendiagnosis penyakit akibat kerja dengan tujuh langkah, "
                                   "dan menentukan apakah pekerja laik kembali bekerja.", size=7.6, color="FFFFFF")])

    # back: tempat kerja + informasi
    box(sl, 97, 0, 100, 210, fill=Pl["bg1"], name="Latar panel belakang")
    photo(sl, "lapangan_gudang", 97, 0, 100, 42, .55, .5)
    box(sl, 104, 36, 52, 9, fill=Pl["accent"], name="Label foto")
    text(sl, 106, 36, 50, 9, [P("TEMPAT KERJA LULUSAN", bold=True, size=8, color=Pl["dark"], spc=100)], anchor="m")
    workplaces_list(sl, 104, 51, Pl)
    box(sl, 97, 107, 100, 103, fill=Pl["dark"], name="Blok informasi")
    text(sl, 104, 113, 86, 9, [P("Informasi", font=HEAD, bold=True, size=17, color="FFFFFF", ls=1.0)])
    box(sl, 104, 123.2, 12, 0.9, fill=Pl["accent"])
    contact_block(sl, 104, 128, 86, Pl, "D5DBD7", "FFFFFF", "FFC20E")
    qr_pair(sl, 104, 157, Pl, "FFFFFF", "D5DBD7")
    hazard_stripe(sl, 97, 203, 100, 7)

    # cover: factory skyline with lit door
    box(sl, 197, 0, 100, 210, fill=Pl["dark"], name="Latar sampul")
    logo_plate(sl, 203, 7)
    text(sl, 204, 42, 88, 9, [P("Di balik setiap tempat kerja,", font=HEAD, size=15, color="FFFFFF", ls=1.0)])
    text(sl, 204, 51, 88, 11, [P("ada dokter okupasi.", font=HEAD, bold=True, italic=True, size=20, color=Pl["accent"], ls=1.0)])
    text(sl, 204, 66, 88, 12, [P("PROGRAM STUDI SPESIALIS", bold=True, size=8, color="D5DBD7", spc=150),
                               P("KEDOKTERAN OKUPASI (Sp.Ok)", bold=True, size=10, color="FFFFFF", spc=60)])
    badge(sl, 204, 82, 31, "Akreditasi UNGGUL", Pl["accent"], "FFFFFF")
    badge(sl, 237.5, 82, 50, "Prodi Sp.Ok pertama di Indonesia", Pl["accent"], "FFFFFF")
    # skyline
    sky = "2A3833"
    box(sl, 199, 116, 18, 87, fill=sky)                       # left block
    box(sl, 203, 100, 4.5, 18, fill=sky)                      # chimney
    box(sl, 210, 106, 4, 12, fill=sky)                        # chimney 2
    for k, (sx, sy, sd) in enumerate([(205.5, 95, 3.5), (207.5, 90, 4.5)]):
        box(sl, sx, sy, sd, sd, fill="5E6B66", alpha=0.5 - 0.15 * k, shape=MSO_SHAPE.OVAL)
    box(sl, 219, 117, 66, 86, fill=Pl["deep"], name="Gedung pabrik")
    for k in range(3):                                         # saw-tooth roof
        box(sl, 219 + k * 22, 104, 22, 13.2, fill=Pl["deep"], shape=MSO_SHAPE.RIGHT_TRIANGLE)
    box(sl, 287, 136, 10, 67, fill=sky)                        # right block
    for wx in (201.5, 208.5):
        for wy in (124, 134, 144, 154, 164):
            box(sl, wx, wy, 4, 5, fill=Pl["accent"], alpha=0.55)
    for wy in (142, 152, 162):
        box(sl, 289.5, wy, 4, 5, fill=Pl["accent"], alpha=0.55)
    box(sl, 229, 138, 44, 65, fill=Pl["accent"], alpha=0.28, name="Cahaya pintu")
    photo(sl, "edukasi_pekerja", 232, 141, 38, 62, .82, .55, zoom=1.35)
    box(sl, 232, 141, 38, 62, line=Pl["accent"], lw=2.25, name="Bingkai pintu")
    hazard_stripe(sl, 197, 203, 100, 7)

    # ---------------- INSIDE
    sl = blank(prs, "Dalam")
    box(sl, 0, 0, 100, 210, fill=Pl["bg1"], name="Latar panel 1")
    photo(sl, "lapangan_briefing", 0, 0, 100, 44, .5, .5)
    box(sl, 7, 39, 60, 8, fill=Pl["accent"], name="Label foto")
    text(sl, 9, 39, 58, 8, [P("DI BALIK PINTU: Sp.Ok DI LAPANGAN", bold=True, size=7, color=Pl["dark"], spc=60)], anchor="m")
    heading(sl, 7, 52, 86, "Apa yang dikerjakan Sp.Ok?", Pl | {"dark": Pl["dark"]}, size=15, h=8)
    doing_grid(sl, 7, 67, Pl, rh=17)
    box(sl, 7, 138, 86, 31, fill=Pl["bg2"], name="Kotak visi")
    box(sl, 7, 138, 1.4, 31, fill=Pl["accent"])
    text(sl, 12, 141, 78, 27, [P("VISI", bold=True, size=7.2, color=Pl["deep"], spc=150, after=1.5),
                               P("“" + VISI + "”", italic=True, size=7.2, color=Pl["dark"], ls=1.1)])
    box(sl, 7, 174, 86, 22, fill=Pl["deep"], name="Kotak gelar")
    text(sl, 12, 177.5, 78, 17, [P("GELAR LULUSAN", bold=True, size=7, color=Pl["accent"], spc=150, after=2),
                               P(runs=[("Spesialis Kedokteran Okupasi ", {}), ("(Sp.Ok)", {"color": Pl["accent"]})],
                                 font=HEAD, bold=True, size=11.5, color="FFFFFF", ls=1.0)])

    box(sl, 100, 0, 100, 210, fill=Pl["bg2"], name="Latar panel 2")
    heading(sl, 107, 10, 86, "Persyaratan peserta", Pl)
    text(sl, 107, 26, 86, 132, persyaratan_paras(Pl), name="Teks persyaratan")
    photo(sl, "lab_tim", 107, 143, 86, 58, .5, .55)

    box(sl, 200, 0, 97, 210, fill=Pl["bg1"], name="Latar panel 3")
    heading(sl, 207, 10, 83, "Pembelajaran dan biaya", Pl)
    for i, (big, sub) in enumerate([("7 semester · 98 SKS", "Lulusan dokter umum"),
                                    ("4 semester · tambahan 65 SKS", "Lulusan Magister Kedokteran Kerja")]):
        yy = 26 + i * 17
        box(sl, 207, yy, 83, 15, fill=Pl["dark"])
        text(sl, 211, yy + 1.8, 77, 12, [P(big, font=HEAD, bold=True, size=11.5, color=Pl["accent"], after=1, ls=1.0),
                                         P(sub, size=7.4, color="FFFFFF")])
    text(sl, 207, 64, 83, 80, biaya_paras(Pl), name="Teks pembelajaran dan biaya")
    photo(sl, "radiograf_dosen", 207, 146, 83, 30, .45, .5)
    cta(sl, 207, 178, 83, 21, Pl["accent"], Pl["dark"], Pl["dark"])
    hazard_stripe(sl, 200, 203, 97, 7)

    out = os.path.join(HERE, "Flyer Sp.Ok - Konsep B (Pintu Pabrik x Peta Pajanan).pptx")
    prs.save(out)
    return out


if __name__ == "__main__":
    for f in (concept_a(), concept_b()):
        print(f)
