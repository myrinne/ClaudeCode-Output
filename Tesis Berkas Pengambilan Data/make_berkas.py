"""Generate field documents for the WBGT-TEWL-H2O2 thesis data collection
(Instalasi Gizi RSCM, 30 Nov - 2 Des 2026).

Content follows the proposal "Proposal Penelitian_Vidya Cecilia-Kedokteran
Okupasi_RSCM.docx" (Lampiran 3 kuesioner, Lampiran 4 skoring beban kerja,
Bab 3.6). The informed consent is copied unchanged from the ethics-approved
v02 (3 Nov 2026).

Usage:  python make_berkas.py [output_dir|-] [file numbers, e.g. 03 04]
Output defaults to the thesis folder in OneDrive (the repo is public, so the
generated documents are not stored in it).
"""
import shutil
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

DOCS = Path(r"C:\Users\vidya\OneDrive\Documents")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] != "-" else DOCS / "PPDS Okupasi/Usulan Thesis/Gizi/Berkas Pengambilan Data"
IC_SRC = DOCS / ("PPDS Okupasi/Usulan Thesis/Redcap/Etik UI/Perbaikan/"
                 "Lembar Penjelasan dan Persetujuan (Informed Consent) - Vidya Cecilia_v02_3 Nov 2026.docx")

JUDUL = ("Hubungan Pajanan Panas (WBGT) terhadap Beban Oksidatif Sistemik (H\u2082O\u2082) "
         "melalui Gangguan Sawar Kulit pada Pekerja Penyelenggaraan Makanan Institusional")
LOKASI = "Instalasi Gizi RSUPN Dr. Cipto Mangunkusumo"
BOX = "\u2610"
# Two collection days (Prodia only available 30 Nov and 2 Des). Each day covers
# the subuh, pagi and sore shifts; the shift is ticked per subject on the data
# sheet. Day 1 takes as many workers as possible (about 61 on duty), day 2 the rest.
HARI = [  # (kode hari, label tanggal, tanggal singkat)
    ("H1", "Hari 1 \u2013 Senin, 30 November 2026", "30/11/2026"),
    ("H2", "Hari 2 \u2013 Rabu, 2 Desember 2026", "02/12/2026"),
]
JUMLAH = {"H1": 60, "H2": 35}  # kode per hari
SHIFT_JAM = (f"{BOX} Subuh (05.00\u201312.30)   {BOX} Pagi (07.00\u201314.30)   "
             f"{BOX} Sore (11.30\u201319.00)")
FONT = "Arial"


# ---------------------------------------------------------------- helpers
def new_doc(margin_cm=2.0, font_pt=10.5):
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(margin_cm)
    s.top_margin = s.bottom_margin = Cm(margin_cm)
    st = d.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(font_pt)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    pf = st.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.0
    return d


def para(container, text="", bold=False, size=None, align=None, italic=False, after=None, before=None):
    p = container.add_paragraph()
    if text:
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
    if align is not None:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if before is not None:
        p.paragraph_format.space_before = Pt(before)
    return p


def cell_text(cell, text, bold=False, size=None, align=None, italic=False):
    cell.text = ""
    lines = text.split("\n")
    p = cell.paragraphs[0]
    for i, line in enumerate(lines):
        if i:
            p = cell.add_paragraph()
        r = p.add_run(line)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
        if align is not None:
            p.alignment = align
        p.paragraph_format.space_after = Pt(0)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    return cell


def shade(cell, fill="E7E6E6"):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), fill)
    tcPr.append(sh)


def set_grid(t, widths_cm):
    """Fix column widths in tblGrid + every cell (LibreOffice reads gridCol, Word reads tcW)."""
    tbl = t._tbl
    grid = tbl.tblGrid
    for gc in list(grid):
        grid.remove(gc)
    for w in widths_cm:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(int(w * 567)))
        grid.append(gc)
    tblPr = tbl.tblPr
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    for row in t.rows:
        for j, c in enumerate(row.cells):
            c.width = Cm(widths_cm[j])


def table(container, rows, widths_cm, header=None, size=None, row_h=None, bold_first_col=False):
    """rows: list of lists of str. header: list of str (shaded, bold)."""
    allrows = ([header] if header else []) + rows
    t = container.add_table(rows=len(allrows), cols=len(widths_cm))
    t.style = "Table Grid"
    t.autofit = False
    for i, row in enumerate(allrows):
        tr = t.rows[i]
        if row_h:
            tr.height = Cm(row_h)
            tr.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        for j, val in enumerate(row):
            c = tr.cells[j]
            c.width = Cm(widths_cm[j])
            is_head = header and i == 0
            cell_text(c, val, bold=is_head or (bold_first_col and j == 0), size=size)
            if is_head:
                shade(c)
    set_grid(t, widths_cm)
    return t


WIDTH = 17.4


def section_head(d, text):
    t = d.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    c = t.rows[0].cells[0]
    cell_text(c, text, bold=True)
    shade(c, "D9E2F3")
    set_grid(t, [WIDTH])
    para(d, "", after=0).paragraph_format.space_after = Pt(0)


def gap(d, pt=4):
    p = d.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("")
    r.font.size = Pt(pt)


def doc_header(d, title, subtitle, kode_box=True):
    t = d.add_table(rows=1, cols=2)
    t.autofit = False
    left, right = t.rows[0].cells
    set_grid(t, [12.9, 4.5])
    cell_text(left, title, bold=True, size=13)
    p = left.add_paragraph()
    r = p.add_run(subtitle)
    r.font.size = Pt(8.5)
    r.italic = True
    if kode_box:
        cell_text(right, "Kode subjek\n\nH___ \u2013 ___", bold=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        tcPr = right._tc.get_or_add_tcPr()
        borders = OxmlElement("w:tcBorders")
        for side in ("top", "left", "bottom", "right"):
            b = OxmlElement(f"w:{side}")
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), "12")
            b.set(qn("w:color"), "000000")
            borders.append(b)
        tcPr.append(borders)
    gap(d, 6)


def footer(d, text):
    for s in d.sections:
        p = s.footer.paragraphs[0]
        p.text = ""
        r = p.add_run(text)
        r.font.size = Pt(7.5)
        r.italic = True
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def no_borders(t):
    tblPr = t._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "nil")
        b.append(e)
    tblPr.append(b)


def dashed_grid(t):
    tblPr = t._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "dashed")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "808080")
        b.append(e)
    tblPr.append(b)


def kode_list():
    return [(h, f"{h}-{i:02d}", lbl, tgl)
            for h, lbl, tgl in HARI for i in range(1, JUMLAH[h] + 1)]


# ---------------------------------------------------------------- 1. kuesioner
def make_kuesioner(path):
    d = new_doc(margin_cm=1.8)
    doc_header(d, "KUESIONER PENELITIAN", JUDUL)
    para(d, "Petunjuk: mohon isi atau beri tanda \u2713 pada kotak yang sesuai. Tidak ada jawaban benar atau "
            "salah. Bila ada pertanyaan yang kurang jelas, silakan tanyakan kepada petugas.",
         size=9, italic=True, after=6)

    W3 = [1.2, 8.6, 7.6]
    section_head(d, "BAGIAN A. Identitas")
    table(d, [["A1", "Kode subjek (diisi petugas)", "H___ \u2013 ___"],
              ["A2", "Tanggal pengambilan data", "____ / ____ / 2026"],
              ["A3", "Nama", ""],
              ["A4", "Departemen / jabatan sesuai penugasan", ""]],
          W3, header=["No", "Butir", "Isian"], row_h=0.75)
    gap(d)

    section_head(d, "BAGIAN B. Demografi")
    table(d, [["B1", "Tanggal lahir", "____ / ____ / ________"],
              ["B2", "Jenis kelamin", f"{BOX} Laki-laki    {BOX} Perempuan"],
              ["B3", "Pendidikan terakhir", f"{BOX} SD   {BOX} SMP   {BOX} SMA/SMK\n{BOX} D3/S1   {BOX} lainnya: ________"]],
          W3, header=["No", "Butir", "Isian"], row_h=0.75)
    gap(d)

    section_head(d, "BAGIAN D. Data Pekerjaan")
    table(d, [["D1", "Sudah berapa lama bekerja pada posisi ini?", "______ tahun ______ bulan"],
              ["D2", "Jam mulai kerja hari ini", "________"],
              ["D3", "Jam selesai kerja hari ini", "________"],
              ["D4", "Lama kerja per hari", "________ jam"],
              ["D5", "Berapa hari kerja per minggu?", "________ hari"]],
          W3, header=["No", "Butir", "Isian"], row_h=0.75)
    gap(d)

    section_head(d, "BAGIAN E. Zona Kerja dan Alokasi Waktu")
    para(d, "Mohon perkirakan berapa lama Bapak/Ibu bekerja pada masing-masing zona berikut dalam satu hari "
            "kerja (dalam jam dari total jam kerja). Total keseluruhan sama dengan jumlah jam kerja "
            "Bapak/Ibu dalam sehari.", size=9.5, after=3)
    table(d, [["E1", "Zona memasak makanan utama", ""],
              ["E2", "Zona memasak makanan selingan", ""],
              ["E3", "Dapur susu / enteral", ""],
              ["E4", "Zona pemorsian, penyajian, dan pencucian", ""],
              ["E5", "Ruang persiapan bahan sayuran", ""],
              ["E6", "Ruang persiapan bahan daging", ""],
              ["E7", "Ruang penerimaan bahan", ""],
              ["E8", "Ruang administrasi gizi", ""],
              ["", "Total (harus sama dengan D4 \u2013 Lama kerja per hari)", ""]],
          [1.2, 11.2, 5.0], header=["Kode", "Zona kerja", "Perkiraan waktu (jam/hari)"], row_h=0.7)
    gap(d)

    section_head(d, "BAGIAN F. Aktivitas Beban Kerja Fisik")
    para(d, "\u201cDalam satu hari kerja biasa, kira-kira berapa jam Bapak/Ibu melakukan hal seperti ini?\u201d "
            "Jumlah seluruh baris harus sama dengan D4 (Lama kerja per hari).", size=9.5, after=3)
    table(d, [["F1", "Menyiapkan menu dan administrasi sambil duduk, memotong bahan ringan sambil duduk atau "
                     "berdiri, mengawasi proses", ""],
              ["F2", "Mengaduk masakan di atas kompor, mencuci dan memotong bahan berdiri, memorsikan makanan, "
                     "mencuci peralatan", ""],
              ["F3", "Mengangkat panci atau wajan besar berisi, memindahkan dandang, mendorong troli distribusi "
                     "makanan bermuatan penuh antar-ruang", ""],
              ["F4", "Mengangkat beban berat secara berulang dengan kecepatan tinggi tanpa jeda", ""],
              ["", "TOTAL (harus sama dengan D4 \u2013 Lama kerja per hari)", ""]],
          [1.2, 13.2, 3.0], header=["No", "Kegiatan", "Jam per hari"], row_h=0.8)
    gap(d)

    section_head(d, "BAGIAN G. Riwayat Merokok")
    table(d, [["G1", "Status merokok", f"{BOX} Tidak pernah\n{BOX} Sudah berhenti (berhenti sejak tahun ______)\n{BOX} Aktif"],
              ["G2", "Rata-rata jumlah batang per hari", "________ batang"],
              ["G3", "Sudah berapa tahun merokok", "________ tahun"],
              ["G5", "Merokok dalam 3 jam terakhir?", f"{BOX} Tidak    {BOX} Ya \u2192 tunda pengambilan darah"]],
          W3, header=["No", "Butir", "Isian"], row_h=0.75)
    gap(d)

    section_head(d, "BAGIAN H. Penyaring Kriteria Eksklusi")
    table(d, [["H1", "Penyakit DM tipe 2, penyakit jantung, gagal jantung, stroke, penyakit ginjal kronis, penyakit "
                     "autoimun, keganasan, gangguan neurologis, psikiatri, atau rutin minum obat diuretik (obat "
                     "pelancar buang air kecil)", BOX, BOX],
              ["H2", "Demam, batuk-pilek, atau infeksi lain dalam 1 minggu terakhir", BOX, BOX],
              ["H3", "Dermatitis, eksim, psoriasis, luka, tato, atau bekas luka pada lengan bawah", BOX, BOX],
              ["H4", "Mengonsumsi suplemen antioksidan (vitamin C, vitamin E, glutation, atau N-acetylcysteine) "
                     "dalam 24 jam terakhir", BOX, BOX],
              ["H5", "Merokok lebih dari 20 batang per hari", BOX, BOX],
              ["H6", "Mengoleskan pelembap, losion, minyak, tabir surya, atau produk apa pun pada lengan bawah "
                     "dalam 24 jam terakhir", BOX, BOX],
              ["H7", "Lengan bawah terkena air, sabun, atau deterjen dalam 2 jam terakhir", BOX, BOX]],
          [1.2, 13.4, 1.4, 1.4], header=["No", "Pertanyaan", "Ya", "Tidak"], row_h=0.75)
    for row in d.tables[-1].rows:
        for c in row.cells[2:]:
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    gap(d)

    section_head(d, "BAGIAN I. Kebiasaan Perawatan dan Pajanan Kulit")
    table(d, [["I1", "Dalam 1 minggu terakhir, apakah Bapak/Ibu mengoleskan pelembap atau losion pada lengan bawah "
                     "setiap hari?", f"{BOX} Ya    {BOX} Tidak"],
              ["I2", "Dalam satu hari kerja biasa, apakah tangan atau lengan bawah Bapak/Ibu kontak dengan air, "
                     "sabun, atau deterjen (mencuci bahan, peralatan, atau tangan) selama 2 jam atau lebih?",
               f"{BOX} Ya (\u2265 2 jam)\n{BOX} Tidak (< 2 jam)"]],
          [1.2, 11.7, 4.5], header=["No", "Pertanyaan", "Jawaban"], row_h=0.8)
    gap(d, 8)
    para(d, "Terima kasih atas waktu dan kesediaan Bapak/Ibu.", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    footer(d, "Kuesioner (Lampiran 3, tanpa Bagian C dan J) \u2013 versi 22 Nov 2026")
    d.save(path)


# ---------------------------------------------------------------- 2. lembar data
def make_lembar_data(path):
    d = new_doc(margin_cm=1.8, font_pt=10)
    doc_header(d, "LEMBAR DATA PENGUKURAN", "Diisi oleh petugas. Tidak memuat nama subjek, hanya kode subjek.")
    table(d, [["Tanggal", f"{BOX} Sen 30/11   {BOX} Rab 02/12", "Jenis kelamin", f"{BOX} Laki-laki   {BOX} Perempuan"],
              ["Shift hari ini", SHIFT_JAM, "", ""]],
          [3.0, 5.4, 2.8, 6.2], row_h=0.75, bold_first_col=True)
    t = d.tables[-1]
    t.rows[0].cells[2].paragraphs[0].runs[0].bold = True
    merged = t.rows[1].cells[1].merge(t.rows[1].cells[3])
    for p in merged.paragraphs[1:]:
        if not p.text:
            p._p.getparent().remove(p._p)
    gap(d)

    section_head(d, "1. Verifikasi penyaring (kuesioner Bagian G5), sebelum pemeriksaan")
    table(d, [["G5", f"{BOX} Tidak merokok 3 jam terakhir    {BOX} Ya \u2192 pengambilan darah ditunda"]],
          [2.4, 15.0], row_h=0.75, bold_first_col=True)
    gap(d)

    section_head(d, "2. Antropometri (Bagian C)")
    table(d, [["C1", "Berat badan", "________ kg"],
              ["C2", "Tinggi badan", "________ cm"],
              ["C3", "Indeks massa tubuh = BB \u00f7 (TB/100)\u00b2", "________ kg/m\u00b2"]],
          [1.2, 10.2, 6.0], header=["No", "Butir", "Isian"], row_h=0.75)
    gap(d)

    section_head(d, "3. Dokumentasi pengukuran (Bagian J)")
    table(d, [["J1", "Jam selesai shift pada hari ini", "________"],
              ["J2", "Jam mulai aklimatisasi (minimal 15\u201330 menit)", "________"],
              ["J3", "Jam pengukuran TEWL", "________"],
              ["", "Lengan yang diukur (volar forearm non-dominan)", f"{BOX} Kiri    {BOX} Kanan"],
              ["J4", "Suhu ruang dan kelembapan relatif saat pengukuran", "______ \u00b0C  /  ______ %"],
              ["J5", "Nilai TEWL bacaan 1 / 2 / 3 (g/m\u00b2/jam)", "______ / ______ / ______"],
              ["", "Rerata TEWL", "________ g/m\u00b2/jam"],
              ["J6", "Jam pengambilan darah", "________"],
              ["J7", "Catatan (hemolisis, kekeruhan plasma, kendala lain)",
               f"Hemolisis: {BOX} Tidak  {BOX} Ya\n\n"]],
          [1.2, 10.2, 6.0], header=["No", "Butir", "Isian"], row_h=0.75)
    footer(d, "Lembar Data Pengukuran (Bagian C dan J) \u2013 versi 23 Nov 2026")
    d.save(path)


# ---------------------------------------------------------------- 3. kartu alur
LANGKAH = [
    "Daftar hadir dan lembar persetujuan ditandatangani",
    "Penyaring (Bagian G5) diperiksa petugas",
    "Timbang berat badan dan ukur tinggi badan",
    "Pemeriksaan kulit (TEWL)",
    "Pengambilan darah",
    "Konsumsi dan souvenir diterima",
]


def fill_card(cell, kode, lbl):
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run("KARTU ALUR PEMERIKSAAN")
    r.bold = True
    r.font.size = Pt(10)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(1)
    p = cell.add_paragraph()
    r = p.add_run(lbl)
    r.font.size = Pt(7.5)
    r.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    p = cell.add_paragraph()
    r = p.add_run("Kode: ")
    r.font.size = Pt(9)
    r = p.add_run(kode)
    r.bold = True
    r.font.size = Pt(14)
    r = p.add_run("     Nama: _______________")
    r.font.size = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    t = cell.add_table(rows=len(LANGKAH) + 1, cols=3)
    t.style = "Table Grid"
    t.autofit = False
    widths = [0.7, 6.3, 1.5]
    for j, h in enumerate(["\u2713", "Langkah", "Paraf"]):
        c = t.rows[0].cells[j]
        c.width = Cm(widths[j])
        cell_text(c, h, bold=True, size=7.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        shade(c)
    for i, step in enumerate(LANGKAH, 1):
        row = t.rows[i]
        row.height = Cm(0.7)
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        vals = [BOX, f"{i}. {step}", ""]
        for j, v in enumerate(vals):
            row.cells[j].width = Cm(widths[j])
            cell_text(row.cells[j], v, size=7.5, align=WD_ALIGN_PARAGRAPH.CENTER if j == 0 else None)
    set_grid(t, widths)
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    r = p.add_run("Bawa kartu ini ke setiap meja. Serahkan kepada petugas di meja terakhir.")
    r.font.size = Pt(7)
    r.italic = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def make_kartu(path):
    d = new_doc(margin_cm=0.9)
    kodes = kode_list()
    per_page = 6
    for start in range(0, len(kodes), per_page):
        if start:
            d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        chunk = kodes[start:start + per_page]
        t = d.add_table(rows=3, cols=2)
        dashed_grid(t)
        t.autofit = False
        for k in range(per_page):
            c = t.rows[k // 2].cells[k % 2]
            c.width = Cm(9.6)
            if k < len(chunk):
                _, kode, lbl, _ = chunk[k]
                fill_card(c, kode, lbl)
        set_grid(t, [9.6, 9.6])
        for row in t.rows:
            row.height = Cm(9.0)
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
    # remove the leading empty paragraph python-docx adds
    first = d.paragraphs[0]
    if not first.text and first._p.getnext() is not None and first._p.getparent() is d.element.body:
        first._p.getparent().remove(first._p)
    d.save(path)


# ---------------------------------------------------------------- 4. label nama
def make_label_nama(path):
    d = new_doc(margin_cm=1.0)
    kodes = kode_list()
    cols, rows = 3, 7
    per_page = cols * rows
    for start in range(0, len(kodes), per_page):
        if start:
            d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        chunk = kodes[start:start + per_page]
        t = d.add_table(rows=rows, cols=cols)
        dashed_grid(t)
        t.autofit = False
        for k in range(per_page):
            c = t.rows[k // cols].cells[k % cols]
            c.width = Cm(6.3)
            if k >= len(chunk):
                continue
            _, kode, lbl, _ = chunk[k]
            c.text = ""
            p = c.paragraphs[0]
            r = p.add_run(kode)
            r.bold = True
            r.font.size = Pt(22)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(4)
            p = c.add_paragraph()
            r = p.add_run("Nama: ____________________")
            r.font.size = Pt(10)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(3)
            p = c.add_paragraph()
            r = p.add_run(lbl.split(" \u2013 ")[1])
            r.font.size = Pt(7.5)
            r.italic = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_grid(t, [6.3] * cols)
        for row in t.rows:
            row.height = Cm(3.75)
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
    first = d.paragraphs[0]
    if not first.text and first._p.getparent() is d.element.body:
        first._p.getparent().remove(first._p)
    d.save(path)


# ---------------------------------------------------------------- 5. label tabung
def make_label_tabung(path):
    d = new_doc(margin_cm=1.0, font_pt=9)
    items = []
    for _, kode, _, tgl in kode_list():
        for jenis in ("EDTA", "P1", "P2"):
            items.append((kode, jenis, tgl))
    cols, rows = 6, 13
    per_page = cols * rows
    for start in range(0, len(items), per_page):
        if start:
            d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        chunk = items[start:start + per_page]
        t = d.add_table(rows=rows, cols=cols)
        dashed_grid(t)
        t.autofit = False
        for k in range(per_page):
            c = t.rows[k // cols].cells[k % cols]
            c.width = Cm(3.15)
            if k >= len(chunk):
                continue
            kode, jenis, tgl = chunk[k]
            c.text = ""
            p = c.paragraphs[0]
            r = p.add_run(kode)
            r.bold = True
            r.font.size = Pt(12)
            r = p.add_run(f"  {jenis}")
            r.bold = True
            r.font.size = Pt(9)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            p = c.add_paragraph()
            r = p.add_run(tgl)
            r.font.size = Pt(7)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_grid(t, [3.15] * cols)
        for row in t.rows:
            row.height = Cm(2.0)
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
    first = d.paragraphs[0]
    if not first.text and first._p.getparent() is d.element.body:
        first._p.getparent().remove(first._p)
    d.save(path)


# ---------------------------------------------------------------- 6. daftar hadir
def make_absen(path):
    d = new_doc(margin_cm=1.5)
    for n, (hk, lbl, _) in enumerate(HARI):
        if n:
            d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        para(d, "DAFTAR HADIR PESERTA PEMERIKSAAN", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, after=1)
        para(d, LOKASI, size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=1)
        para(d, f"{lbl} \u00b7 Shift: SB = Subuh, P = Pagi, S = Sore", bold=True, size=10.5,
             align=WD_ALIGN_PARAGRAPH.CENTER, after=8)
        rows = [[str(i), "", "", "", "", ""] for i in range(1, max(30, JUMLAH[hk]) + 1)]
        t = table(d, rows, [1.0, 6.6, 1.6, 2.4, 3.2, 3.2],
                  header=["No", "Nama", "Shift", "Jam Datang", "TTD Hadir", "TTD Terima Souvenir"], row_h=0.66)
        for row in t.rows:
            row.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        t.rows[0].height = Cm(0.9)
        rep = OxmlElement("w:tblHeader")  # repeat header row on page 2 (day 1 has 60 rows)
        rep.set(qn("w:val"), "true")
        t.rows[0]._tr.get_or_add_trPr().append(rep)
    d.save(path)


# ---------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("01 Kuesioner Penelitian.docx", make_kuesioner),
        ("02 Lembar Penjelasan dan Persetujuan (IC) v02 - disetujui etik.docx", lambda p: shutil.copy2(IC_SRC, p)),
        ("03 Lembar Data Pengukuran.docx", make_lembar_data),
        ("04 Kartu Alur Peserta.docx", make_kartu),
        # 05 Label Nama Peserta: dropped by her on 22 Nov ("tidak usah"); run with "05" to make it anyway.
        ("06 Label Tabung EDTA dan Mikrotube.docx", make_label_tabung),
        ("07 Daftar Hadir 2 Hari (kosong).docx", make_absen),
    ]
    only = sys.argv[2:]  # optional file-number filter, e.g. 03 04
    if "05" in only:
        jobs.append(("05 Label Nama Peserta.docx", make_label_nama))
    for name, fn in jobs:
        if only and name[:2] not in only:
            continue
        try:
            fn(OUT / name)
            print("ok  ", name)
        except PermissionError:
            print("SKIP (file sedang terbuka di Word):", name)


if __name__ == "__main__":
    main()
