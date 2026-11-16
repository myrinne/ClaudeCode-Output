"""Build 'Catatan Tambahan - J Desain Penelitian dan RR OR' (docx + Obsidian md) from ../short/*.md.
Usage: python build_epi.py OUT.docx [VAULT_NOTE.md]
Sections come from sections.txt (lines: heading|file stem).
md extras: '!PEARL ' (yellow callout), '!SUMBER ' (red callout), [[wikilinks]] (plain text in docx, kept in md)."""
import sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import mdconv as M
from extras import callout

SHORT = os.path.join(RAW, "short")
TITLE = "Catatan Tambahan - J Desain Penelitian dan RR OR"
SECTIONS = [l.strip().split("|") for l in open(os.path.join(HERE, "sections.txt"), encoding="utf-8") if l.strip()]


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
        l = re.sub(r"\[\[([^\]]+)\]\]", r"catatan '\1'", l)
        l = re.sub(r"\$\$(.+?)\$\$", lambda m: "\\[" + m.group(1) + "\\]", l)
        l = re.sub(r"\$(.+?)\$", lambda m: "\\(" + m.group(1) + "\\)", l)
        if l.startswith("!PEARL "):
            flush()
            callout(doc, "Clinical pearl: " + re.sub(r"\*+", "", l[7:]), fill="FFF2CC")
        elif l.startswith("!SUMBER "):
            flush()
            callout(doc, "CATATAN SUMBER: " + re.sub(r"\*+", "", l[8:]), fill="FDE0DC")
        else:
            buf.append(l)
    flush()


def build_docx(out):
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
    doc.add_paragraph("CATATAN TAMBAHAN BOARD: J. DESAIN PENELITIAN, OR/RR, BIAS, DAN SKRINING", style="Title")
    p = doc.add_paragraph()
    r = p.add_run("Disusun dari prediksi topik berdasarkan Kompilasi Soal Ujian Board Sp.Ok 2016-2026 (bab Epidemiologi dan Statistik: 18 soal PG, 14 soal isian). "
                  "Sumber: NotebookLM notebook 'Board Notes - Epidemiologi' (CDC Principles of Epidemiology, CDC Field Epi Manual, Penn State STAT 507, NCBI Bookshelf, "
                  "review healthy worker effect, Bradford Hill). Bagian yang berasal dari pengetahuan umum (bukan sumber notebook) diberi catatan sumber. "
                  "Kotak kuning = clinical pearl; kotak merah muda = catatan sumber yang perlu diverifikasi.")
    r.font.size = Pt(9.5); r.italic = True
    doc.add_paragraph().add_run("Daftar isi").bold = True
    for title, f in SECTIONS:
        doc.add_paragraph(title, style="List Bullet").paragraph_format.space_after = Pt(0)
    doc.add_page_break()
    for title, f in SECTIONS:
        doc.add_heading(title, level=1)
        render(doc, read(f))
    doc.save(out)
    print("saved", out)


def build_md(out):
    head = ("---\ntype: knowledge\ndate: \"2026-11-15\"\ntags:\n  - \"type/literature\"\n  - \"domain/board-exam\"\n  - \"domain/occupational-medicine\"\n"
            "sumber: \"Prediksi dari Kompilasi Soal Ujian Board Sp.Ok 2016-2026; NotebookLM Board Notes - Epidemiologi\"\n---\n"
            "# " + TITLE + "\n\n_Catatan persiapan ujian board Kedokteran Okupasi (Sp.Ok): desain penelitian, RR/OR, bias, skrining. "
            "Tautan: [[MoC Ujian Board Sp.Ok]]. Callout hijau = clinical pearl; callout kuning = catatan sumber yang perlu diverifikasi._\n\n")
    parts = [head]
    for title, f in SECTIONS:
        parts.append("## " + title + "\n")
        out_l = []
        for l in read(f):
            if l.startswith("!PEARL "):
                out_l += ["> [!tip] Clinical pearl", "> " + l[7:], ""]
            elif l.startswith("!SUMBER "):
                out_l += ["> [!warning] Catatan sumber", "> " + l[8:], ""]
            else:
                out_l.append(l)
        parts.append("\n".join(out_l).strip() + "\n")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts))
    print("wrote", out)


build_docx(sys.argv[1])
if len(sys.argv) > 2:
    build_md(sys.argv[2])
