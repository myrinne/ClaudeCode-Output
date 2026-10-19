"""Build the Obsidian version of a gap-note section from short/*.md.
Usage: python build_vault_md.py "<vault Board folder>" "<vault Attachments folder>"
md extras: !PEARL / !SUMBER -> Obsidian callouts; !IMG name | caption -> ![[name]] + caption;
[[wikilinks]] are kept. Images are copied into the vault Attachments folder."""
import sys, os, re, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.dirname(HERE)
BOARD = os.path.dirname(RAW)
SHORT = os.path.join(RAW, "short")
IMGDIR = os.path.join(BOARD, "Gap Kompilasi - gambar")
OUT_DIR, ATT = sys.argv[1], sys.argv[2]

SECTIONS = [("A.1 Pengertian dan keluhan khas pekerja komputer", "A1"), ("A.2 Monitor", "A2"),
            ("A.3 Keyboard dan mouse", "A3"), ("A.4 Kursi dan meja", "A4"),
            ("A.5 Pencahayaan ruang kerja", "A5"), ("A.6 Istirahat mikro dan rotasi", "A6"),
            ("A.7 Antropometri", "A7"), ("A.8 Alat penilaian", "A8"),
            ("A.9 Rangkuman: soal yang pernah keluar, latihan hitung, soal vignette", "A9"),
            ("A.10 Catatan kualitas dan sumber", "A10")]

TITLE = "Catatan Tambahan - A Ergonomi Kantor dan Antropometri"
head = """---
type: knowledge
date: "2026-10-19"
tags:
  - "type/literature"
  - "domain/board-exam"
  - "domain/occupational-medicine"
sumber: "Outline Catatan Tambahan - Gap Kompilasi (bagian A); NotebookLM Board Notes - Gap; Permenaker 5/2018 Lampiran 2 dan 6"
---
# %s

_Catatan persiapan ujian board Kedokteran Okupasi (Sp.Ok), bagian A dari [[Outline Catatan Tambahan - Gap Kompilasi]]. Standar Indonesia (Permenaker No. 5 Tahun 2018 beserta Lampiran 2 dan 6) diutamakan; sumber internasional ditandai. Yang sudah ada di catatan lama tidak diulang, hanya ditautkan (misalnya ROSA, RULA, REBA di [[Catatan_JSA - Job Safety Analysis]]). Callout hijau = clinical pearl; callout kuning = catatan sumber yang perlu diverifikasi._

""" % TITLE


def conv(line):
    if line.startswith("!PEARL "):
        return "> [!tip] Clinical pearl\n> " + line[7:].replace("**", "**")
    if line.startswith("!SUMBER "):
        return "> [!warning] Catatan sumber\n> " + line[8:]
    if line.startswith("!IMG "):
        name, cap = [x.strip() for x in line[5:].split("|", 1)]
        return "![[%s|480]]\n*%s*" % (name, cap)
    return line


parts = [head]
for title, f in SECTIONS:
    parts.append("## " + title + "\n")
    with open(os.path.join(SHORT, f + ".md"), encoding="utf-8") as fh:
        lines = fh.read().replace("\r", "").split("\n")
    out = []
    for l in lines:
        c = conv(l)
        out.append(c)
        if l.startswith("!") and not l.startswith("!IMG"):
            out.append("")
        if l.startswith("!IMG"):
            out.append("")
    parts.append("\n".join(out).strip() + "\n")

os.makedirs(ATT, exist_ok=True)
for fn in os.listdir(IMGDIR):
    if fn.startswith("A_") and fn.endswith(".png"):
        dst = os.path.join(ATT, fn)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(IMGDIR, fn), dst)

dst_md = os.path.join(OUT_DIR, TITLE + ".md")
if os.path.exists(dst_md):
    print("EXISTS, not overwriting:", dst_md)
    sys.exit(1)
with open(dst_md, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(parts))
print("wrote", dst_md)
