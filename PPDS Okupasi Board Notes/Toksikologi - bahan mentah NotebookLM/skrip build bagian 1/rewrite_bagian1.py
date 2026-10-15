# -*- coding: utf-8 -*-
"""Tulis ulang Bagian 1 (1.1 sampai 1.12) di 'Catatan Toksikologi.docx' dengan jawaban panjang NotebookLM
(q01 sampai q12) + vignette OSCE dan lafaz untuk topik kasus (1.4 sampai 1.8). Bagian 2 dst tidak disentuh.

Pemakaian: python rewrite_bagian1.py <docx_in> <docx_out>
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn
import mdconv as M
from vign1 import V

SRC, DST = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
ANS = os.path.join(HERE, "..", "jawaban")


def read(name):
    with open(os.path.join(ANS, name + ".txt"), encoding="utf-8") as f:
        return f.read().replace("[suspicious link removed]., ", "").replace(", [suspicious link removed].", "")


# Vignette OSCE hanya untuk topik berbasis kasus (hitungan dan biomonitoring), bukan topik konsep
CASE_KEYS = set()  # kosong: Bagian 1 tanpa vignette; kasus OSCE ada di bagian 6 (rewrite_lafaz.py)

P1 = [
    ("1.1", "1.1 Dosis-respons", "q01"), ("1.2", "1.2 LD50 dan LC50", "q02"), ("1.3", "1.3 NAB/TLV", "q03"),
    ("1.4", "1.4 TWA dan penyesuaian shift panjang", "q04"), ("1.5", "1.5 Campuran: rumus unity (aditif)", "q05"),
    ("1.6", "1.6 Biomarker", "q06"), ("1.7", "1.7 BEI", "q07"),
    ("1.8", "1.8 Koreksi urin (kreatinin dan berat jenis)", "q08"),
    ("1.9", "1.9 Biotransformasi", "q09"), ("1.10", "1.10 Toksikokinetik umum", "q10"),
    ("1.11", "1.11 Mekanisme toksisitas", "q11"), ("1.12", "1.12 Klasifikasi karsinogen", "q12"),
]

PETA = [
    ["Sub-bab", "Pertanyaan inti yang harus bisa dijawab", "Menyambung ke"],
    ["1.1 Dosis-respons", "Dari kurva dosis-respons, titik mana yang dipakai untuk menurunkan batas aman (NOAEL, BMDL)?", "1.3 (NAB), 2.4 (ARKL)"],
    ["1.2 LD50 dan LC50", "Bagaimana toksisitas akut diklasifikasikan (GHS) dan mengapa angka ini bukan batas aman?", "SDS dan label bahan kimia"],
    ["1.3 NAB/TLV", "Batas pajanan udara apa saja (TWA, STEL, Ceiling) dan apa beda ACGIH dengan Permenaker?", "1.4, 1.5, 2.1"],
    ["1.4 TWA dan shift panjang", "Bagaimana menghitung TWA dan menyesuaikan NAB pada shift 12 jam?", "Bagian 4 (formula wajib hitung)"],
    ["1.5 Rumus unity", "Bagaimana menilai campuran zat dengan organ target yang sama?", "1.3"],
    ["1.6 Biomarker", "Pemantauan udara mengukur lingkungan; biomarker mengukur dosis internal. Jenis dan kualitasnya?", "1.7, 1.8"],
    ["1.7 BEI", "Apa arti nilai BEI, kapan sampel diambil, dan apa yang BUKAN BEI?", "1.6, 1.10 (waktu paruh)"],
    ["1.8 Koreksi urin", "Kapan hasil urin layak diinterpretasi dan bagaimana dikoreksi (kreatinin, berat jenis)?", "1.7"],
    ["1.9 Biotransformasi", "Bagaimana tubuh mengubah zat (fase I dan II) dan kapan malah menjadi lebih toksik?", "1.10, 1.11"],
    ["1.10 Toksikokinetik", "Bagaimana zat diserap, didistribusi, dan dieliminasi (Vd, klirens, waktu paruh)?", "1.7 (waktu sampling)"],
    ["1.11 Mekanisme toksisitas", "Lewat mekanisme apa zat merusak sel (oksidatif, kovalen, inhibisi enzim)?", "Bagian 3 (per zat)"],
    ["1.12 Klasifikasi karsinogen", "Bagaimana IARC, GHS, dan ACGIH mengklasifikasikan karsinogen?", "1.1 (non-threshold)"],
]


def osce_block(doc, key):
    v = V[key]
    doc.add_heading("Latihan OSCE %s: vignette dan lafaz" % key, level=3)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Skenario fiktif untuk latihan. "); r.italic = True
    r = p.add_run("Vignette: "); r.bold = True
    p.add_run(v["skenario"])
    rows = [["Pertanyaan penguji", "Lafaz OSCE (diucapkan ke penguji)"]]
    for i, (q, a) in enumerate(v["qa"], 1):
        rows.append(["%d. %s" % (i, q), a])
    M.add_table(doc, rows, header=True, font=9, widths=[5.3, 11.9])


doc = Document(SRC)
body = doc.element.body
kids = [k for k in body.iterchildren() if k.tag != qn("w:sectPr")]


def text_of(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


i_h1 = next(i for i, k in enumerate(kids) if k.tag == qn("w:p") and text_of(k).startswith("1. BAGIAN AWAL"))
i_h2 = next(i for i, k in enumerate(kids) if k.tag == qn("w:p") and text_of(k).startswith("2. REGULASI INDONESIA"))
brk = kids[i_h2 - 1]            # paragraf pemisah halaman sebelum Bagian 2: dipertahankan
old = kids[i_h1 + 1:i_h2 - 1]   # isi Bagian 1 lama: dibuang

# --- bangun konten baru di akhir body, lalu pindahkan
n_before = len([k for k in body.iterchildren() if k.tag != qn("w:sectPr")])

p = doc.add_paragraph()
r = p.add_run("Bagian 1 ini ditulis ulang dalam versi panjang: jawaban lengkap NotebookLM (q01 sampai q12) dipertahankan "
              "dengan penjelasan alasan di balik tiap angka. Bagian 2 dan seterusnya tetap versi ringkas. Angka dan nomor pasal berasal dari "
              "keluaran NotebookLM; cek ulang ke sumber asli sebelum dihafal (lihat Bagian 7).")
r.italic = True; r.font.size = Pt(9.5)

doc.add_heading("Peta Bagian 1: apa yang diuji dan bagaimana sub-bab saling menyambung", level=2)
M.add_table(doc, PETA, header=True, font=8.5, widths=[3.6, 9.6, 4.0])

for key, title, f in P1:
    doc.add_heading(title, level=2)
    b, refs = M.clean_answer(read(f))
    M.render(doc, b, h_off=1)
    M.render_refs(doc, refs)
    if key in CASE_KEYS:
        osce_block(doc, key)

new = [k for k in body.iterchildren() if k.tag != qn("w:sectPr")][n_before:]
for el in new:
    brk.addprevious(el)
for el in old:
    body.remove(el)

# --- catatan di paragraf pembuka
for para in doc.paragraphs[:6]:
    if para.text.startswith("Catatan persiapan ujian board"):
        r = para.add_run(" Bagian 1 (prinsip dasar) sudah ditulis ulang dalam versi panjang (15 Okt 2026).")
        r.italic = True
        break

# Daftar isi (field TOC) masih memuat entri Bagian 1 lama: minta Word memperbaruinya saat file dibuka
from docx.oxml import OxmlElement
st = doc.settings.element
if st.find(qn("w:updateFields")) is None:
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    st.find(qn("w:footnotePr")).addprevious(uf)  # urutan skema: sebelum footnotePr

doc.save(DST)
print("saved", DST)
