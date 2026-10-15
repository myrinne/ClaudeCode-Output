"""Rebuild the whole toxicology notes docx (parts 1 to 3C, plus 3D/3E when their md files exist).
Usage: python build_all.py OUT.docx
Reads md sections and infographics from the repo folders (no temp dirs needed)."""
import sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.dirname(HERE)                                  # .../Toksikologi - bahan mentah NotebookLM
BOARD = os.path.dirname(RAW)                                 # .../PPDS Okupasi Board Notes
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(RAW, "skrip build"))
sys.path.insert(0, os.path.join(RAW, "skrip build 3B"))
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image
import mdconv as M
import extras_3b as X
import extras_3cde as Y
from extras import para, bullets, callout

OUT = sys.argv[1]
SHORT = os.path.join(RAW, "skrip build", "short")
SHORT3B = os.path.join(RAW, "skrip build 3B", "short3b")
SHORT3C = os.path.join(HERE, "short3c")
SHORT3D = os.path.join(HERE, "short3d")
SHORT3E = os.path.join(HERE, "short3e")
IMG3A = os.path.join(BOARD, "Toksikologi - infografik 3A")
IMG3B = os.path.join(BOARD, "Toksikologi - infografik 3B")
IMG3C = os.path.join(BOARD, "Toksikologi - infografik 3C")
IMG3D = os.path.join(BOARD, "Toksikologi - infografik 3D")
IMG3E = os.path.join(BOARD, "Toksikologi - infografik 3E")
CACHE = os.path.join(os.environ.get("CLAUDE_JOB_DIR", HERE), "tmp", "img_cache")
os.makedirs(CACHE, exist_ok=True)


def small(path):
    """Return a <=2000px JPEG path for any infographic file."""
    if path.lower().endswith(".jpg"):
        return path
    out = os.path.join(CACHE, os.path.basename(os.path.dirname(path)) + "_" + os.path.splitext(os.path.basename(path))[0] + ".jpg")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(path):
        im = Image.open(path).convert("RGB")
        im.thumbnail((2000, 2000))
        im.save(out, quality=88, optimize=True)
    return out


def read(folder, name):
    with open(os.path.join(folder, name + ".md"), encoding="utf-8") as f:
        return f.read().replace("\r", "").split("\n")


def find_img(folder, prefix):
    if not os.path.isdir(folder):
        return None
    for fn in sorted(os.listdir(folder)):
        if fn.startswith(prefix) and fn.lower().endswith((".png", ".jpg")):
            return small(os.path.join(folder, fn))
    return None


def add_img(doc, path, title):
    cp = doc.add_paragraph()
    cp.paragraph_format.keep_with_next = True
    cr = cp.add_run("Infografik: " + title)
    cr.bold = True
    cr.font.size = Pt(9.5)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Cm(17.2))


def has(folder, name):
    return os.path.exists(os.path.join(folder, name + ".md"))


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

HAS_3D = os.path.isdir(SHORT3D) and any(f.endswith(".md") for f in os.listdir(SHORT3D)) and os.environ.get("INCLUDE_3D") == "1"
HAS_3E = os.path.isdir(SHORT3E) and any(f.endswith(".md") for f in os.listdir(SHORT3E)) and os.environ.get("INCLUDE_3E") == "1"
LAST = "3E" if HAS_3E else ("3D" if HAS_3D else "3C")
SUB = {"3C": "prinsip dasar, regulasi Indonesia, logam berat, pelarut organik, dan pestisida",
       "3D": "prinsip dasar, regulasi Indonesia, logam berat, pelarut organik, pestisida, serta gas dan korosif",
       "3E": "prinsip dasar, regulasi Indonesia, logam berat, pelarut organik, pestisida, gas dan korosif, serta debu dan serat"}[LAST]
REST = {"3C": "Topik 3D (gas dan korosif) dan 3E (debu dan serat) menyusul dari notebook lain.",
        "3D": "Topik 3E (debu dan serat) menyusul.",
        "3E": ""}[LAST]

doc.add_paragraph("CATATAN BELAJAR: TOKSIKOLOGI & BIOMONITORING", style="Title")
p = doc.add_paragraph(); r = p.add_run("Bagian 1 sampai %s: %s" % (LAST, SUB)); r.font.size = Pt(13)
p = doc.add_paragraph(); r = p.add_run("Catatan persiapan ujian board Kedokteran Okupasi (Sp.Ok), versi ringkas. Disusun dari jawaban NotebookLM mengikuti outline (notebook logam berat, organic solvents, dan pesticide; gas dan korosif serta debu bila ada). Penomoran 3D (gas dan korosif) dan 3E (debu dan serat) mengikuti urutan terbaru dari Vidya, bukan outline lama (3D debu, 3E gas, 3F korosif). " + REST); r.font.size = Pt(9.5); r.italic = True
p = doc.add_paragraph(); r = p.add_run("Daftar isi"); r.bold = True; r.font.size = Pt(12)
toc_anchor = doc.add_paragraph()
doc.add_page_break()

doc.add_heading("1. BAGIAN AWAL: PRINSIP DASAR", level=1)
P1 = [("1.1 Dosis-respons", "q01"), ("1.2 LD50 dan LC50", "q02"), ("1.3 NAB/TLV", "q03"),
      ("1.4 TWA dan penyesuaian shift panjang", "q04"), ("1.5 Campuran: rumus unity (aditif)", "q05"),
      ("1.6 Biomarker", "q06"), ("1.7 BEI", "q07"), ("1.8 Koreksi urin (kreatinin dan berat jenis)", "q08"),
      ("1.9 Biotransformasi", "q09"), ("1.10 Toksikokinetik umum", "q10"), ("1.11 Mekanisme toksisitas", "q11"),
      ("1.12 Klasifikasi karsinogen", "q12")]
for title, f in P1:
    doc.add_heading(title, level=2)
    M.render(doc, read(SHORT, f), h_off=1)

doc.add_page_break()
doc.add_heading("2. REGULASI INDONESIA", level=1)
P2 = [("2.1 Permenaker 5/2018 (NAB, IPB) dan Kepmenaker 187/1999", "q13"),
      ("2.2 PAK: Perpres 7/2019 dan Permenkes 11/2022", "q14"),
      ("2.3 Status PP 88/2019 dan PP 28/2024", "q15"),
      ("2.4 ARKL: Pedoman Ditjen PP&PL Kemenkes 2012", "q16")]
for title, f in P2:
    doc.add_heading(title, level=2)
    M.render(doc, read(SHORT, f), h_off=1)
X.regulasi_lain(doc)

doc.add_page_break()
doc.add_heading("3. BAGIAN TENGAH: TEMPLATE PER ZAT (3A. LOGAM BERAT)", level=1)
X.template_intro(doc)
METALS = [("3A.1 Kromium (Cr VI vs Cr III)", "m01_Cr"), ("3A.2 Merkuri (Hg)", "m02_Hg"), ("3A.3 Arsen (As)", "m03_As"),
          ("3A.4 Timbal (Pb)", "m04_Pb"), ("3A.5 Kadmium (Cd)", "m05_Cd"), ("3A.6 Mangan (Mn)", "m06_Mn"),
          ("3A.7 Nikel (Ni)", "m07_Ni"), ("3A.8 Berilium (Be)", "m08_Be"), ("3A.9 Kobalt dan hard metal", "m09_Co"),
          ("3A.10 Seng / zinc (metal fume fever)", "m10_Zn"), ("3A.11 Talium (Tl)", "m11_Tl")]
for title, f in METALS:
    doc.add_page_break()
    doc.add_heading(title, level=2)
    M.render(doc, read(SHORT, f), h_off=1)
    num = title.split(" ", 1)[0].split(".")[1]
    ip = find_img(IMG3A, "3A.%s " % num)
    if ip:
        add_img(doc, ip, title.split(" ", 1)[1])

doc.add_page_break()
doc.add_heading("3B. ORGANIC SOLVENT: TEMPLATE PER ZAT", level=1)
X.intro_3b(doc)
SOLV = [("3B.1 Benzena", "s01_Benzena"), ("3B.2 Toluena", "s02_Toluena"), ("3B.3 Xilena", "s03_Xilena"),
        ("3B.4 Stirena", "s04_Stirena"), ("3B.5 Anilin dan nitrobenzena (methemoglobinemia)", "s05_Anilin_Nitrobenzena"),
        ("3B.6 n-Heksana", "s06_nHeksana"), ("3B.7 MEK dan MBK", "s07_MEK_MBK"),
        ("3B.8 Aseton, isopropil eter, etil asetat", "s17_Aseton_IPE_EtilAsetat"), ("3B.9 Metanol", "s08_Metanol"),
        ("3B.10 Etilen glikol dan PEG", "s09_EtilenGlikol_PEG"), ("3B.11 Formaldehida", "s10_Formaldehida"),
        ("3B.12 Vinil klorida monomer (VCM)", "s11_VCM"), ("3B.13 Diklorometana (metilen klorida)", "s12_DCM"),
        ("3B.14 Karbon tetraklorida (CCl4)", "s13_CCl4"), ("3B.15 Trikloroetilen (TCE)", "s14_TCE"),
        ("3B.16 Perkloroetilen (PCE)", "s15_PCE"), ("3B.17 Karbon disulfida (CS2)", "s16_CS2"),
        ("3B.18 Dioksin / TCDD", "s18_TCDD"), ("3B.19 Toluena diisosianat (TDI)", "s19_TDI")]
for title, f in SOLV:
    doc.add_page_break()
    doc.add_heading(title, level=2)
    M.render(doc, read(SHORT3B, f), h_off=1)
    num = int(title.split(" ", 1)[0].split(".")[1])
    ip = find_img(IMG3B, "3B.%02d_" % num)
    if ip:
        add_img(doc, ip, title.split(" ", 1)[1])

# ---------------- 3C ----------------
doc.add_page_break()
doc.add_heading("3C. PESTISIDA: TEMPLATE PER ZAT", level=1)
Y.intro_3c(doc)
PEST = [("3C.1 Organofosfat (diklorvos, paration, malation, klorpirifos)", "c01_Organofosfat"),
        ("3C.2 Organoklorin (DDT, lindane, siklodiena)", "c02_Organoklorin"),
        ("3C.3 Karbamat", "c03_Karbamat"),
        ("3C.4 Piretroid dan piretrin", "c04_Piretroid"),
        ("3C.5 Paraquat (dan diquat)", "c05_Paraquat"),
        ("3C.6 Fosfin dan aluminium fosfida", "c06_Fosfin"),
        ("3C.7 Metil bromida", "c07_MetilBromida")]
for title, f in PEST:
    doc.add_page_break()
    doc.add_heading(title, level=2)
    M.render(doc, read(SHORT3C, f), h_off=1)
    num = int(title.split(" ", 1)[0].split(".")[1])
    ip = find_img(IMG3C, "3C.%02d_" % num)
    if ip:
        add_img(doc, ip, title.split(" ", 1)[1])

# ---------------- 3D / 3E (optional) ----------------
if HAS_3D:
    import extras_3de as Z
    Z.build_3d(doc, read, find_img, add_img, SHORT3D, IMG3D)
if HAS_3E:
    import extras_3de as Z
    Z.build_3e(doc, read, find_img, add_img, SHORT3E, IMG3E)

doc.add_page_break()
X.formula(doc)
doc.add_page_break()
X.quick_table(doc)
doc.add_page_break()
X.quick_table_3b(doc)
doc.add_page_break()
Y.quick_table_3c(doc)
if HAS_3D:
    doc.add_page_break()
    Z.quick_table_3d(doc)
if HAS_3E:
    doc.add_page_break()
    Z.quick_table_3e(doc)
doc.add_page_break()
X.penutup(doc)
X.penutup_3b(doc)
Y.penutup_3c(doc)
if HAS_3D:
    Z.penutup_3d(doc)
if HAS_3E:
    Z.penutup_3e(doc)
X.quality(doc)
Y.quality_extra_3c(doc)
if HAS_3D:
    Z.quality_extra_3d(doc)
if HAS_3E:
    Z.quality_extra_3e(doc)

# tidy heading texts that were hard-coded for an earlier scope
for p in doc.paragraphs:
    if p.style.name.startswith("Heading") and p.text.startswith("6. BAGIAN PENUTUP"):
        for r in p.runs[1:]:
            r.text = ""
        p.runs[0].text = "6. BAGIAN PENUTUP (3A SAMPAI %s)" % LAST

# TOC
heads = [p for p in doc.paragraphs if p.style.name in ("Heading 1", "Heading 2")]
bm_id = 100
entries = []
for n, h in enumerate(heads):
    name = "toc_%03d" % n
    s = OxmlElement("w:bookmarkStart"); s.set(qn("w:id"), str(bm_id + n)); s.set(qn("w:name"), name)
    e = OxmlElement("w:bookmarkEnd"); e.set(qn("w:id"), str(bm_id + n))
    h._p.insert(1 if h._p.pPr is not None else 0, s)
    h._p.append(e)
    entries.append((name, h.text, h.style.name))
prev = toc_anchor._p
for name, text, sty in entries:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.left_indent = Cm(0 if sty == "Heading 1" else 0.8)
    hl = OxmlElement("w:hyperlink"); hl.set(qn("w:anchor"), name); hl.set(qn("w:history"), "1")
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    if sty == "Heading 1":
        rpr.append(OxmlElement("w:b"))
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "20" if sty == "Heading 1" else "19"); rpr.append(sz)
    col = OxmlElement("w:color"); col.set(qn("w:val"), "1F3864"); rpr.append(col)
    r.append(rpr)
    t = OxmlElement("w:t"); t.set(qn("xml:space"), "preserve"); t.text = text; r.append(t)
    hl.append(r)
    p._p.append(hl)
    prev.addnext(p._p)
    prev = p._p

doc.save(OUT)
print("saved", OUT)
