# -*- coding: utf-8 -*-
"""Sisipkan blok 'Pendalaman' (file .md di folder ini) di akhir tiap bagian zat pada Catatan Toksikologi.docx.

Pemakaian: python add_pendalaman.py <docx_in> <docx_out>
Blok memakai markdown sederhana yang dirender oleh mdconv (heading, tabel, bullet, bold).
Mulai heading dari '###' (jadi Heading 3 di bawah Heading 2 zat).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
import mdconv as M

SRC, DST = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))

# (awalan judul H2 zat, [file md yang disisipkan berurutan])
PLAN_LOGAM_BTX = [
    ("3A.1 Kromium", ["cr.md"]),
    ("3A.2 Merkuri", ["hg.md"]),
    ("3A.3 Arsen", ["as.md"]),
    ("3A.4 Timbal", ["pb.md"]),
    ("3A.5 Kadmium", ["cd.md"]),
    ("3B.1 Benzena", ["benzena.md"]),
    ("3B.2 Toluena", ["toluena.md"]),
    ("3B.3 Xilena", ["xilena.md", "btx_banding.md"]),
]

PLAN_DEBU = [
    ("3E.1 Silika", ["silika.md"]),
    ("3E.2 Asbes", ["asbes.md"]),
    ("3E.3 Debu batubara", ["batubara.md"]),
    ("3E.4 Debu kayu", ["kayu.md"]),
    ("3E.5 Debu kapas", ["kapas.md", "banding_debu.md"]),
]

# argumen ke-3: "logam" (Pb, BTX, Hg, As, Cd, Cr), "debu" (3E), atau "semua"
MODE = sys.argv[3] if len(sys.argv) > 3 else "semua"
PLAN = (PLAN_LOGAM_BTX if MODE in ("logam", "semua") else []) + (PLAN_DEBU if MODE in ("debu", "semua") else [])

CATATAN_LOGAM = [
    "Pendalaman (1 Nov 2026) untuk Pb, benzena, toluena, xilena, Hg, As, Cd, dan Cr VI disusun dari jawaban panjang NotebookLM (q17 sampai q26 dan 3B q01 sampai q02) yang tersimpan di folder bahan mentah; tabel 13 poin tidak diubah.",
    "Pendalaman Pb: nomor butir Perpres 7/2019 berbeda antar keluaran (butir 8 pada tabel Bagian 2.2, butir 5 pada NotebookLM). Rincian OSHA (medical removal, return to work) dan acuan CDC anak 3,5 µg/dL perlu dicek ke sumber primer.",
    "Pendalaman xilena: BEI MHA 0,3 g/g kreatinin dan TLV 20 ppm (ACGIH) versus NAB 100 ppm dan IPB 1,5 g/g (Permenaker 5/2018) berasal dari NotebookLM; cek ulang ke buku TLV dan BEI 2026.",
    "Pendalaman Cr VI: dosis asam askorbat oral 2 sampai 10 g dan askorbat topikal 10% berasal dari satu sumber NotebookLM dengan bukti klinis terbatas. Nomor butir Perpres untuk kanker paru dan perforasi septum kromium perlu dicek ulang.",
    "Pendalaman Cd: nilai panduan Eropa U-Cd 2 µg/g kreatinin (HBM4EU) bukan standar hukum Indonesia; BEI ACGIH tetap 5 µg/g kreatinin.",
]

CATATAN_DEBU = [
    "Pendalaman debu dan serat (3E.1 sampai 3E.5) disusun dari jawaban panjang NotebookLM (folder jawaban 3E); tabel 14 poin tidak diubah.",
    "Pendalaman asbes: ambang baru Barbieri dkk. 2025 (600 AB atau 300.000 AAF per gram paru kering) adalah usulan satu studi, bukan standar; Kriteria Helsinki tetap rujukan konsensus. Status larangan parsial asbes di Indonesia dari NotebookLM, cek ulang.",
    "Pendalaman debu kayu dan batubara: NAB Permenaker 5/2018 (kayu keras 1 mg/m3, kayu lunak 5 mg/m3 dengan STEL 10; batubara antrasit 0,4 dan bituminus 0,9 mg/m3) serta nomor butir Perpres 7/2019 berasal dari NotebookLM dan perlu dicek ke lampiran.",
    "Pendalaman kapas: rekomendasi endotoksin 90 EU/m3 bukan batas hukum; derajat Schilling dan klasifikasi WHO 1983 dari NotebookLM.",
]
CATATAN = (CATATAN_LOGAM if MODE in ("logam", "semua") else []) + (CATATAN_DEBU if MODE in ("debu", "semua") else [])


def text_of(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def style_of(el):
    ps = el.find(qn("w:pPr"))
    st = ps.find(qn("w:pStyle")) if ps is not None else None
    return st.get(qn("w:val")) if st is not None else ""


def is_pagebreak_only(el):
    if el.tag != qn("w:p") or text_of(el).strip():
        return False
    return any(b.get(qn("w:type")) == "page" for b in el.iter(qn("w:br")))


def read_md(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read().replace("\r", "").split("\n")


doc = Document(SRC)
body = doc.element.body


def kids():
    return [k for k in body.iterchildren() if k.tag != qn("w:sectPr")]


for prefix, files in PLAN:
    ks = kids()
    i0 = next(i for i, k in enumerate(ks) if k.tag == qn("w:p") and style_of(k) == "Heading2" and text_of(k).startswith(prefix))
    i1 = next(i for i in range(i0 + 1, len(ks)) if ks[i].tag == qn("w:p") and style_of(ks[i]) in ("Heading1", "Heading2"))
    anchor = ks[i1]
    while is_pagebreak_only(anchor.getprevious()):
        anchor = anchor.getprevious()
    n_before = len(kids())
    for f in files:
        M.render(doc, read_md(f), h_off=1)
    new = kids()[n_before:]
    for el in new:
        anchor.addprevious(el)
    print(prefix, "+", len(new), "elemen")

# catatan kualitas (Bagian 7): tambahkan di akhir dokumen
for t in CATATAN:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(1)
    M.add_inline(p, t)

doc.save(DST)
print("saved", DST)
