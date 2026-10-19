"""Build 'Catatan Tambahan - Gap Kompilasi' docx from short/*.md.
Usage: python build_gap.py OUT.docx
Reuses mdconv/extras from the toxicology build folder. md extras: lines starting
'!PEARL ' (yellow callout) and '!SUMBER ' (red callout)."""
import sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.dirname(HERE)                                  # .../Gap Kompilasi - bahan mentah NotebookLM
BOARD = os.path.dirname(RAW)                                 # .../PPDS Okupasi Board Notes
sys.path.insert(0, os.path.join(BOARD, "Toksikologi - bahan mentah NotebookLM", "skrip build"))
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import mdconv as M
from extras import callout

SHORT = os.path.join(RAW, "short")
OUT = sys.argv[1]


def read(name):
    with open(os.path.join(SHORT, name + ".md"), encoding="utf-8") as f:
        return f.read().replace("\r", "").split("\n")


def render(doc, lines):
    buf = []

    def flush():
        if buf:
            M.render(doc, buf, h_off=1)
            buf.clear()

    for l in lines:
        if l.startswith("!PEARL "):
            flush()
            callout(doc, "Clinical pearl: " + re.sub(r"\*+", "", l[7:]), fill="FFF2CC")
        elif l.startswith("!SUMBER "):
            flush()
            callout(doc, "CATATAN SUMBER: " + re.sub(r"\*+", "", l[8:]), fill="FDE0DC")
        else:
            buf.append(l)
    flush()


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.6), Cm(27.9)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.font.size = Pt(10.5)
for nm, sz in (("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 11)):
    h = doc.styles[nm]
    h.font.name = "Calibri"
    h.font.size = Pt(sz)

fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
for t, instr in (("begin", None), (None, "PAGE"), ("end", None)):
    r = fp.add_run()
    if t:
        c = OxmlElement("w:fldChar"); c.set(qn("w:fldCharType"), t); r._r.append(c)
    else:
        i = OxmlElement("w:instrText"); i.set(qn("xml:space"), "preserve"); i.text = instr; r._r.append(i)
    r.font.size = Pt(8)

doc.add_paragraph("CATATAN TAMBAHAN BOARD: GAP DARI KOMPILASI SOAL 2016 SAMPAI 2026", style="Title")
p = doc.add_paragraph(); r = p.add_run("Bagian A (pilot): Ergonomi kantor dan antropometri"); r.font.size = Pt(13)
p = doc.add_paragraph()
r = p.add_run("Catatan persiapan ujian board Kedokteran Okupasi (Sp.Ok). Disusun mengikuti 'Outline Catatan Tambahan - Gap Kompilasi' dari jawaban NotebookLM (notebook Board Notes - Gap), "
              "ditambah teks resmi Permenaker No. 5 Tahun 2018 beserta Lampiran 2 (pencahayaan) dan Lampiran 6 (standar ergonomi) yang dibaca langsung dari salinan teks karena "
              "salinan di notebook adalah hasil pindai. Standar Indonesia diutamakan; sumber internasional (Bodyspace, LaDou & Harrison, OSHA) dipakai sebagai pelengkap dan ditandai. "
              "Tiap bab berdiri sendiri. Kotak kuning = clinical pearl; kotak merah muda = catatan sumber yang perlu diverifikasi. "
              "STATUS: bagian A selesai; bagian B sampai G dan tambahan H menyusul setelah format ini disetujui.")
r.font.size = Pt(9.5); r.italic = True

doc.add_paragraph().add_run("Daftar isi").bold = True
for t in ("A.1 Pengertian dan keluhan khas pekerja komputer", "A.2 Monitor", "A.3 Keyboard dan mouse",
          "A.4 Kursi dan meja", "A.5 Pencahayaan ruang kerja", "A.6 Istirahat mikro dan rotasi",
          "A.7 Antropometri", "A.8 Alat penilaian (ROSA dan lainnya)",
          "A.9 Rangkuman: soal yang pernah keluar, latihan hitung, soal vignette",
          "A.10 Catatan kualitas dan sumber"):
    doc.add_paragraph(t, style="List Bullet").paragraph_format.space_after = Pt(0)
doc.add_page_break()

doc.add_heading("A. ERGONOMI KANTOR DAN ANTROPOMETRI", level=1)
SECTIONS = [("A.1 Pengertian dan keluhan khas pekerja komputer", "A1"), ("A.2 Monitor", "A2"),
            ("A.3 Keyboard dan mouse", "A3"), ("A.4 Kursi dan meja", "A4"),
            ("A.5 Pencahayaan ruang kerja", "A5"), ("A.6 Istirahat mikro dan rotasi", "A6"),
            ("A.7 Antropometri", "A7"), ("A.8 Alat penilaian (ROSA dan lainnya)", "A8"),
            ("A.9 Rangkuman: soal yang pernah keluar, latihan hitung, soal vignette", "A9"),
            ("A.10 Catatan kualitas dan sumber", "A10")]
for title, f in SECTIONS:
    doc.add_heading(title, level=2)
    render(doc, read(f))

doc.save(OUT)
print("saved", OUT)
