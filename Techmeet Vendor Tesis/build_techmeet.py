"""Techmeet deck for the blood-sampling vendor (analis + petugas TB/BB), on her Template 3.
Run: python build_techmeet.py  ->  Techmeet Vendor - Hari H.pptx next to this script.
Template 3 is slide-based: slide 1 = cover, slide 8 = cream content background, slide 14 = closing.
The original template is opened read-only and never written."""
import sys
from pathlib import Path
sys.path.insert(0, r"C:/Users/vidya/.claude/skills/consulting-pptx-editable/scripts")
from deckkit import Deck, Box, Inches, Pt, PP_ALIGN, MSO_ANCHOR

TPL = r"C:/Users/vidya/OneDrive/Documents/Project/Professional MCU Template/Template 3.pptx"
OUT = Path(__file__).resolve().parent / "Techmeet Vendor - Hari H.pptx"
MAROON, ORANGE, PINK = "6C202D", "FE702F", "FDC6E9"

d = Deck(TPL, main=MAROON, body_pt=27, title_pt=40)
d.HDR_H = Inches(0.7)
d.C["hl"] = "F7E3D8"
X0, W = Inches(1.12), Inches(17.76)
BODY_TOP, BODY_BOT = Inches(3.05), Inches(10.55)


def drop(slide, keep_ids):
    for sh in list(slide.shapes):
        if sh.shape_id not in keep_ids:
            sh._element.getparent().remove(sh._element)


def set_text(shape, text, size=None, color=None):
    tf = shape.text_frame
    p0 = tf.paragraphs[0]
    r0 = p0.runs[0]
    font = (r0.font.name, r0.font.bold, r0.font.size, r0.font.color.rgb if r0.font.color and r0.font.color.type else None)
    for p in list(tf.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    for r in p0.runs[1:]:
        r._r.getparent().remove(r._r)
    lines = text.split("\n")
    r0.text = lines[0]
    for line in lines[1:]:
        p = tf.add_paragraph()
        p.alignment = p0.alignment
        r = p.add_run()
        r.text = line
        r.font.name, r.font.bold = font[0], font[1]
        r.font.size = font[2]
        if font[3] is not None:
            r.font.color.rgb = font[3]
    if size or color:
        for p in tf.paragraphs:
            for r in p.runs:
                if size:
                    r.font.size = Pt(size)
                if color:
                    from pptx.dml.color import RGBColor
                    r.font.color.rgb = RGBColor.from_string(color)


def page(title, kicker, source=None):
    """Cream content slide from template slide 8: its title box, a tag chip top-right, a body Box."""
    s = d.reuse(8)
    drop(s, {26})
    t = next(sh for sh in s.shapes if sh.shape_id == 26)
    t.left, t.top, t.width, t.height = X0, Inches(1.05), W, Inches(1.9)
    set_text(t, title, size=40)
    t.text_frame.word_wrap = True
    t.text_frame.vertical_anchor = MSO_ANCHOR.TOP
    k = d.kicker(s, Box(int(Inches(15.38)), int(Inches(0.45)), int(Inches(3.5)), int(Inches(0.5))), kicker)
    for r in k.text_frame.paragraphs[0].runs:
        r.font.size = Pt(18)
    bot = BODY_BOT
    if source:
        sb = Box(int(X0), int(Inches(10.3)), int(W), int(Inches(0.4)))
        d.text(s, sb, source, size=17, color="6E6E6E", anchor=MSO_ANCHOR.BOTTOM)
        bot = Inches(10.15)
    return s, Box(int(X0), int(BODY_TOP), int(W), int(bot - BODY_TOP))


# 1. Cover ---------------------------------------------------------------------------------------
s = d.reuse(1)
drop(s, {2, 5, 10, 13, 16, 17, 18, 19})          # 8 = stock photo circle, removed
byid = {sh.shape_id: sh for sh in s.shapes}
set_text(byid[18], "Technical\nMeeting", size=120)
set_text(byid[19], "PEMERIKSAAN KULIT DAN PANAS\nINSTALASI GIZI RSCM", size=26)
byid[19].width = Inches(9.6)
set_text(byid[16], "Disiapkan oleh: dr. Vidya Cecilia", size=22)
set_text(byid[17], "Untuk: tim vendor", size=22)
date_box = Box(int(Inches(12.0)), int(Inches(2.2)), int(Inches(7.2)), int(Inches(4.6)))
d.text(s, date_box, "**Senin, 30 November 2026**\n**Rabu, 2 Desember 2026**\n11.00–20.00",
       size=40, color=MAROON, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, space_after=14)

# 2. Purpose -------------------------------------------------------------------------------------
s, b = page("Pemeriksaan ini mengukur panas dapur, kelembaban kulit,\ndan stres oksidatif darah pekerja Instalasi Gizi",
            "Tujuan", "Etik: KET-1687/UN2.F1/ETIK/PPM.00.02/2026 (protokol 26-10-1617, disetujui 9 November 2026)")
l, r = d.two_col(b, (1, 1), gap=Inches(0.8))
d.table(s, l.top(Inches(6.2)), ["Pengukuran", "Yang diukur", "Petugas"], [
    ["Panas dapur (WBGT)", "Suhu dan kelembaban di 8 zona dapur, 05.00–19.00", "dr. Vidya, asisten"],
    ["Kelembaban kulit (TEWL)", "Penguapan air dari kulit lengan bawah", "dr. Vidya"],
    ["Stres oksidatif (H₂O₂)", "Kadar H₂O₂ di plasma darah EDTA", "**Vendor**"],
], col_widths=[1.25, 1.75, 0.9], body_pt=24, highlight_rows=(2,))
d.bullets(s, r, [
    "Vendor dan tim kami memakai alur dan jam yang sama di kedua hari",
    "Setiap petugas tahu tahap yang ia pegang",
    "Darah sampai ke coolbox sebagai plasma dalam 30 menit",
    "Barang, limbah, dan pembayaran disepakati sebelum hari H",
], heading="Yang ingin disepakati hari ini")

# 3. When, where, how many -----------------------------------------------------------------------
s, b = page("Pemeriksaan berlangsung dua hari di ruang penerimaan,\n±51 peserta di hari 1 dan ±34 di hari 2",
            "Waktu dan lokasi",
            "Jumlah = undangan per shift (subuh / pagi / sore); perkiraan yang ikut dan lolos ±85%.")
l, r = d.two_col(b, (3, 2), gap=Inches(0.8))
d.table(s, l.top(Inches(6.6)), ["", "Hari 1", "Hari 2"], [
    ["Tanggal", "Senin, 30 November 2026", "Rabu, 2 Desember 2026"],
    ["Vendor datang", "11.00, siapkan sentrifus dan alat TB/BB", "11.00"],
    ["Perkiraan selesai", "±20.00", "±20.00"],
    ["Peserta diundang", "51 (5 / 30 / 16)", "±34 (2 / 25 / 7)"],
    ["Lokasi", "Ruang penerimaan Instalasi Gizi", "Ruang penerimaan Instalasi Gizi"],
], col_widths=[1.1, 1.6, 1.4], body_pt=24)
ph = d.rect(s, r.top(Inches(6.6)), line="9A8F86", text="Foto ruang penerimaan\n(menyusul)", size=20, color="6E6E6E")
ph.line.dash_style = 4

# 4. Participant flow ----------------------------------------------------------------------------
s, b = page("Darah diambil paling akhir,\nlangsung setelah pemeriksaan kulit (TEWL)", "Alur peserta")
d.chevrons(s, b.top(Inches(4.6)), ["Consent", "Istirahat + kuesioner", "Timbang + tinggi",
                                   "TEWL", "Ambil darah", "Konsumsi"],
           highlight=4, size=24, band_h=Inches(1.0), descriptions=[
    ["Asisten", "Tanda tangan, terima kartu alur berisi kode"],
    ["Ruang sejuk 15–30 menit", "Petugas TB/BB membantu kuesioner"],
    ["Petugas TB/BB", "Hasil ditulis di lembar data"],
    ["dr. Vidya", "±2–2,5 menit per orang, satu alat"],
    ["Analis", "Tabung EDTA 3–5 mL, label kode"],
    ["Asisten", "Konsumsi dan souvenir"],
])
d.text(s, Box(int(X0), int(Inches(8.3)), int(W), int(Inches(1.2))),
       "Peserta tiba di meja darah satu per satu, kira-kira satu orang tiap 2–3 menit, mengikuti kecepatan TEWL.",
       size=27, bold=True, color=MAROON)

# 5. Waves and breaks ----------------------------------------------------------------------------
s, b = page("Pengambilan darah datang dalam tiga gelombang,\ndengan puncak di gelombang pagi", "Jadwal",
            "Jam selesai = perkiraan dari TEWL ±2,25 menit per orang, hari 1. Baris berwarna = gelombang terpadat.")
l, r = d.two_col(b, (5, 2), gap=Inches(0.7))
d.table(s, l.top(Inches(5.6)),
        ["Gelombang", "Berhenti kerja", "Mulai TEWL dan darah", "Peserta H1 / H2", "Darah terakhir", "Istirahat vendor"], [
    ["Subuh", "12.00", "±12.20", "5 / 2", "±12.40", "±12.45–14.15"],
    ["Pagi", "14.00", "±14.20", "30 / 25", "±15.35", "±16.00–18.45"],
    ["Sore", "18.30", "±18.50", "16 / 7", "±19.30", "Selesai ±20.00"],
], col_widths=[1.35, 1, 1.25, 1, 1, 1.25], body_pt=24, highlight_rows=(1,))
d.bullets(s, r, [
    "Peserta pagi datang bertahap, sekitar 10 orang per kelompok",
    "Istirahat 15–30 menit di ruang sejuk sebelum TEWL",
    "Sentrifus terakhir sekitar 19.50",
], heading="Yang perlu diantisipasi", size=25)

# 6. Roles ---------------------------------------------------------------------------------------
s, b = page("Dua analis bergantian mengambil darah dan memutar\nsentrifus agar plasma terpisah dalam 30 menit",
            "Pembagian tugas")
d.table(s, b.top(Inches(7.1)), ["Petugas", "Tugas", "Jam hadir"], [
    ["dr. Vidya", ["Pengukuran WBGT pagi, lalu TEWL semua peserta", "Penanggung jawab di lokasi"], "04.40–20.00"],
    ["Asisten", ["Consent, antrean, timer istirahat", "WBGT sore, konsumsi dan souvenir"], "07.00–20.00"],
    ["Petugas TB/BB (vendor)", ["Timbang dan ukur tinggi badan", "Bantu peserta mengisi kuesioner"], "11.00–±19.30"],
    ["Analis A (vendor)", ["Ambil darah", "Bantu memipet plasma saat antrean sepi"], "11.00–±20.00"],
    ["Analis B (vendor)", ["Sentrifus per batch, pipet plasma ke mikrotube, isi log", "Ikut ambil darah bila antrean menumpuk"], "11.00–±20.00"],
], col_widths=[1.2, 3, 1], body_pt=24, highlight_rows=(3, 4))

# 7. Blood draw ----------------------------------------------------------------------------------
s, b = page("Darah EDTA harus bebas hemolisis karena H₂O₂\ndibaca pada panjang gelombang 405 nm", "Ambil darah")
l, r = d.two_col(b.top(Inches(6.0)), (1, 1), gap=Inches(0.8))
d.bullets(s, l, [
    "Tabung ungu EDTA, 3–5 mL, satu kali per peserta",
    "Lengan kiri atau kanan boleh",
    "Label tabung hanya berisi kode dari kartu alur, tanpa nama",
    "Tabung langsung masuk coolbox 4 °C sampai disentrifus",
], heading="Cara mengambil")
d.bullets(s, r, [
    "Tourniquet tidak dipasang terlalu lama",
    "Tabung dibolak-balik pelan, tidak dikocok",
    "Plasma kemerahan dicatat \"hemolisis: ya\" di log",
    "Peserta pusing atau memar dilaporkan ke dr. Vidya; penanganan tanpa biaya",
], heading="Menjaga mutu sampel dan peserta")

# 8. Centrifuge and aliquot ----------------------------------------------------------------------
s, b = page("Plasma dipisahkan dan dibagi ke dua mikrotube\npaling lambat 30 menit setelah darah diambil",
            "Sentrifus",
            "Gaikwad 2021, Sci Rep, doi:10.1038/s41598-021-82623-4. ×g = 1,118 × 10⁻⁵ × radius (cm) × rpm².")
l, r = d.two_col(b, (3, 2), gap=Inches(0.8))
d.step_flow(s, l.top(Inches(6.9)), [
    ("Simpan", "Tabung EDTA langsung ke coolbox 4 °C"),
    ("Sentrifus", "3000 rpm, 10–15 menit, per batch ±6 tabung atau setelah 15 menit menunggu"),
    ("Pipet plasma", "Lapisan atas kuning jernih, tanpa menyentuh lapisan sel"),
    ("Bagi dua", "2 mikrotube berlabel kode yang sama"),
    ("Simpan dan catat", "Mikrotube ke coolbox 4 °C, isi log sampel"),
], size=25, num_w=Inches(0.8))
d.bullets(s, r, [
    "Sentrifus memisahkan plasma dari sel darah; H₂O₂ diperiksa dari plasma",
    "H₂O₂ plasma turun bila sentrifus tertunda 30–60 menit",
    "3000 rpm setara ±1.000–1.500 ×g pada rotor 10–15 cm",
    "Log: jam ambil, jam sentrifus, jam masuk coolbox, hemolisis",
    "Coolbox tahan 12 jam; dr. Vidya membawa sampel ke freezer −20 °C",
], heading="Alasan dan catatan", size=24)

# 9. Supplies ------------------------------------------------------------------------------------
s, b = page("dr. Vidya menyediakan bahan habis pakai;\nvendor meminjamkan sentrifus, alat ukur, dan rak", "Barang")
d.table(s, b.top(Inches(7.2)), ["Kebutuhan", "Disediakan dr. Vidya", "Dipinjam dari vendor"], [
    ["Pengambilan darah", ["Vacu needle dan vacu holder, tabung EDTA", "Alkohol swab, plester, sarung tangan, hand sanitizer"],
     ["Tourniquet", "Bantal medis"]],
    ["Pemisahan dan penyimpanan sampel", ["Mikrotube, pipet Pasteur", "Label kode, marker, coolbox dan ice pack"],
     ["Sentrifus", "Rak tabung EDTA dan rak mikrotube"]],
    ["Limbah", ["Safety box (2)", "Kantong plastik kuning"], "—"],
    ["Timbang dan tinggi badan", "—", ["Stadiometer", "Timbangan"]],
], col_widths=[1.3, 2.2, 1.6], body_pt=24)

# 10. Questionnaire and documents ----------------------------------------------------------------
s, b = page("Kuesioner diisi selama istirahat sebelum TEWL,\nsehingga tidak menambah waktu antrean", "Kuesioner")
l, r = d.two_col(b.top(Inches(6.8)), (1, 1), gap=Inches(0.8))
d.bullets(s, l, [
    "Membantu peserta yang bingung membaca atau mengisi",
    ("Bagian jam kerja per area paling sering keliru", [
        "Jumlah jam harus sama dengan lama kerja sehari",
        "Contoh 8 jam: 5 memasak, 2 pemorsian, 1 persiapan"]),
    "Tidak ada jawaban benar atau salah; perkiraan sudah cukup",
], heading="Peran petugas TB/BB", size=25)
d.table(s, r, ["Dokumen", "Diisi atau dipegang oleh"], [
    ["Informed consent", "Asisten bersama peserta"],
    ["Kuesioner", "Peserta, dibantu petugas TB/BB"],
    ["Kartu alur (kode subjek)", "Peserta, dibawa ke tiap meja"],
    ["Lembar data", "TB/BB, TEWL, dan jam ambil darah oleh petugas meja masing-masing"],
    ["Log sampel", "Analis"],
], col_widths=[1, 1.5], body_pt=23)

# 11. Payment ------------------------------------------------------------------------------------
s, b = page("Total biaya vendor untuk dua hari pemeriksaan\nadalah Rp 4.100.000", "Pembayaran")
l, r = d.two_col(b.top(Inches(4.4)), (2, 3), gap=Inches(0.8))
d.stat(s, l, "Rp 4.100.000", "Total untuk Senin, 30 November dan Rabu, 2 Desember 2026", value_pt=80)
d.bullets(s, r, [
    "Petugas vendor di kedua hari, 11.00–±20.00",
    "Pinjaman sentrifus, stadiometer, timbangan, tourniquet, bantal medis, dan rak",
    "Cara dan waktu pembayaran: disepakati hari ini",
], heading="Lingkup yang dibayar (dikonfirmasi hari ini)")

# 12. Open items ---------------------------------------------------------------------------------
s, b = page("Jumlah analis, limbah medis, kontak, dan kapasitas sentrifus\nperlu dipastikan sebelum hari H",
            "Konfirmasi")
d.table(s, b.top(Inches(7.1)), ["Hal", "Yang perlu dijawab vendor"], [
    ["Jumlah analis", "Dua analis bergantian ambil darah dan sentrifus: bisa dipenuhi?"],
    ["Gelombang pagi", "Perlu tambahan petugas pada ±14.20–15.35?"],
    ["Sentrifus", "Radius rotor dan kapasitas tabung per putaran"],
    ["Limbah medis", "Safety box dan kantong kuning dibuang ke mana di RSCM?"],
    ["Kontak hari H", "Nama dan nomor PIC vendor"],
    ["Pembayaran", "Cara dan waktu pembayaran Rp 4.100.000"],
], col_widths=[1, 3], body_pt=24)

# 13. Closing ------------------------------------------------------------------------------------
s = d.reuse(14)
drop(s, {2, 11, 13, 15, 17, 19, 21, 24})
byid = {sh.shape_id: sh for sh in s.shapes}
set_text(byid[24], "Terima\nkasih")
set_text(byid[21], "Sampai bertemu Senin, 30 November dan Rabu, 2 Desember 2026.")
byid[21].width = Inches(11.5)

d.save(str(OUT))
print(OUT)
print("\n".join(d.titles()) if hasattr(d, "titles") else "")
