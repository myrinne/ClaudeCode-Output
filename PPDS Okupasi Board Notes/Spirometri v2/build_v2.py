"""Build Catatan_Spirometri_v2.docx from the original notes.

Usage: python build_v2.py SRC.docx OUT.docx FIGDIR
The original file is never modified.
"""
import sys
import pathlib
import docx

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from docx_ops import Cursor, find_par, section_end, replace_in, set_text  # noqa: E402
from content_prosedur import SOP, SVC, GRADING  # noqa: E402
from content_infeksi_interp import INFEKSI, INTERP2022  # noqa: E402
from content_kunci import KUNCI  # noqa: E402
import content_late as L  # noqa: E402

SRC, OUT, FIG = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
doc = docx.Document(SRC)
LOG = []


def must(ok, what):
    if not ok:
        raise SystemExit(f"FAILED: {what}")
    LOG.append(what)


def rep(start, old, new, nth=0):
    p = find_par(doc, start, nth=nth)
    must(replace_in(p, old, new), f"replace in '{start[:40]}': {old[:40]}")


def rewrite(start, new, keep_label=False):
    p = find_par(doc, start)
    set_text(p, new, keep_prefix_runs=1 if keep_label else 0)
    LOG.append(f"rewrite '{start[:50]}'")
    return p


def after(par_or_el, blocks):
    el = getattr(par_or_el, "_p", par_or_el)
    return Cursor(doc, el).add(blocks)


def at_section_end(heading_start, blocks):
    h = find_par(doc, heading_start)
    return Cursor(doc, section_end(doc, h)).add(blocks)


# ---------------------------------------------------------------- B fixes
# B1 regulasi (1.3)
for start, new in L.REG_REWRITE:
    rewrite(start, new)
after(find_par(doc, "Konsensus Pemeriksaan Spirometri Okupasi"), L.REG_ADD)

# 2.1 static vs dynamic wording
rewrite("Volume STATIK paru", "Volume yang dapat diekspirasikan: KVP (Kapasitas Vital Paksa = FVC), diukur dengan "
        "manuver ekspirasi paksa (dinamis); VC/SVC diukur dengan manuver lambat.")
rewrite("Volume DINAMIK paru", "Parameter aliran (dinamis, bergantung waktu): VEP1 (Volume Ekspirasi Paksa detik "
        "pertama = FEV1), rasio VEP1/KVP, dan PEF.")

# B3 kontraindikasi (4.1)
rewrite("Kardiovaskular: infark miokard", L.KONTRA_KARDIO)
rewrite("Neurologis/Okular:", "Neurologis/Okular: aneurisma serebral; operasi otak dalam 4 minggu; konkusi baru "
        "dengan gejala menetap; operasi mata dalam 1 minggu.")
after(find_par(doc, "Kontrol Infeksi: hemoptisis"), [
    ("b", "Hentikan manuver bila pasien merasa nyeri. Kontraindikasi relatif tidak otomatis melarang pemeriksaan; "
          "dokter pengirim menimbang manfaat dan risiko, dan pasien berisiko bisa diperiksa di laboratorium paru "
          "dengan operator berpengalaman dan akses gawat darurat (ATS/ERS 2019)."),
])
# 4.4 posisi
rewrite("Posisi: berdiri lebih disukai", L.POSISI)

# artefact figure at end of 4.5.3 (after the PERDOKI 5-criteria list region ends at 4.6 heading)
at_section_end("4.5.3 Detail Artefak Teknis Lanjutan", [
    ("img", FIG / "fig_artefak_volume_time.png", 16.5),
    ("cap", "Gambar v2: galeri artefak kurva volume-time (skematis, dibuat untuk catatan ini; bukan data pasien)."),
])

# new sections 4.7-4.10 after 4.6
c = at_section_end("4.6 Kriteria Repeatability", SOP)
c.add(SVC).add(INFEKSI).add(GRADING)

# 5.7 table source labels
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                if "Sumber video/PPT tambahan" in p.text:
                    replace_in(p, "Sumber video/PPT tambahan", "Konsensus PERDOKI 2019 (slide 23)")
LOG.append("5.7 table source labels")

# 5.8 predicted values Indonesia (after 5.7 section)
at_section_end("5.7 Cross-Shift % Decline", L.PREDIKSI)

# 6.5 / 6.6 new sections after 6.4
c = at_section_end("6.4 Klasifikasi Kelainan Akibat Kerja", L.UAO)
c.add([("img", FIG / "fig_pola_flow_volume.png", 16.5),
       ("cap", "Gambar v2: galeri bentuk kurva flow-volume (skematis). Garis putus-putus abu = kurva normal.")])
c.add(L.ASMA_KERJA)

# B5 7.1 langkah 2
rewrite("Langkah 2 — Cek FEV1/FVC", L.LANGKAH2)

# 7.4 heading / intro / table header and 2005 table
rewrite("7.4 Grading Severity Skema Klasik", L.H74)
rewrite("Derajat keparahan gangguan ventilasi", L.P74)
for start, new in L.T74_HEADER:
    for t in doc.tables:
        if t.rows[0].cells[0].text.strip() == start:
            set_text(t.rows[0].cells[0].paragraphs[0], new)
            LOG.append(f"7.4 table header {start}")
at_section_end("7.4 Grading Severity Skema Klasik", L.T2005)
rewrite("Tabel %prediksi FEV1 (5 tingkat)", L.P75)
for t in doc.tables:
    if t.rows[0].cells[0].text.strip() == "Derajat Keparahan":
        fixes = {"−1.645 hingga −2.50": "−1,65 hingga −2,5", "−2.50 hingga −4.00": "−2,51 hingga −4,0",
                 "< −4.00": "< −4,1"}
        for row in t.rows[1:]:
            c = row.cells[1]
            if c.text.strip() in fixes:
                set_text(c.paragraphs[0], fixes[c.text.strip()])
        LOG.append("7.5 z-score table values aligned with ERS/ATS 2022")

# 7.7 reversibility statement
rewrite("Reversibilitas sempurna", L.REVERS)

# 7.10 ERS/ATS 2022 after 7.9
at_section_end("7.9 Versi Paru vs Versi Okupasi", INTERP2022)

# 8.2 table source note + FEV1Q, 8.7 kuesioner
at_section_end("8.2 Kriteria Signifikansi Penurunan", L.SRC82)
at_section_end("8.6 Isu Antropometri Khusus", L.KUESIONER)

# 11.5 kecacatan after 11.4 (ends before 12.)
at_section_end("11.4 Program Konservasi", L.KECACATAN)

# 13.2 lafaz reproducibility note
after(find_par(doc, "\"Saya menentukan hasil pemeriksaan ini REPRODUCIBLE"), [L.LAFAZ_NOTE])

# ---------------------------------------------------------------- cross-references -> inline content
for start, old, new in L.XREF:
    rep(start, old, new)
rewrite("Standar internasional saat ini merekomendasikan keluarga persamaan", L.P73)

# ---------------------------------------------------------------- answer keys + changelog at the end
last = doc.element.body[-2] if doc.element.body[-1].tag.endswith("sectPr") else doc.element.body[-1]
Cursor(doc, last).add(KUNCI).add(L.CHANGELOG)

# title marker
p = find_par(doc, "SPIROMETRI")
p.runs[0].text = "SPIROMETRI — v2 (revisi 24 November 2026)"

# ask Word to refresh the table of contents (new sections 4.7-4.10, 5.8, 6.5, 6.6, 7.10, 8.7, 11.5, 13.11)
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
settings = doc.settings.element
if settings.find(qn("w:updateFields")) is None:
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    settings.append(uf)
LOG.append("settings: updateFields=true (Word refreshes TOC on open)")

doc.save(OUT)
print("\n".join(LOG))
print("saved", OUT)
