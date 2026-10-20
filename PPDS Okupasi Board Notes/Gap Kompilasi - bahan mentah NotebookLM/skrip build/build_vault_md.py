"""Build the Obsidian note of one part (A, B, ...) from short/*.md using parts.py.
Usage: python build_vault_md.py LETTER "<vault Board folder>" "<vault Attachments folder>" [--force]
md extras: !PEARL / !SUMBER -> Obsidian callouts; !IMG name | caption -> ![[name]] + caption;
[[wikilinks]] are kept. Images are copied into the vault Attachments folder.
--force overwrites a note that this script created earlier (never use on hand-written notes)."""
import sys, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from parts import PARTS
RAW = os.path.dirname(HERE)
BOARD = os.path.dirname(RAW)
SHORT = os.path.join(RAW, "short")
IMGDIR = os.path.join(BOARD, "Gap Kompilasi - gambar")
LETTER, OUT_DIR, ATT = sys.argv[1], sys.argv[2], sys.argv[3]
FORCE = "--force" in sys.argv
part = [p for p in PARTS if p["letter"] == LETTER][0]
TITLE = part["vault_title"]

head = """---
type: knowledge
date: "2026-10-19"
tags:
  - "type/literature"
  - "domain/board-exam"
  - "domain/occupational-medicine"
sumber: "Outline Catatan Tambahan - Gap Kompilasi (bagian %s); NotebookLM Board Notes - Gap; teks resmi Permenaker 5/2018 dan lampirannya bila relevan"
---
# %s

_Catatan persiapan ujian board Kedokteran Okupasi (Sp.Ok), bagian %s dari [[Outline Catatan Tambahan - Gap Kompilasi]]. Standar Indonesia diutamakan; sumber internasional ditandai. Yang sudah ada di catatan lama tidak diulang, hanya ditautkan (mis. [[Catatan_JSA - Job Safety Analysis]], [[Catatan Toksikologi]]). Callout hijau = clinical pearl; callout kuning = catatan sumber yang perlu diverifikasi._

""" % (LETTER, TITLE, LETTER)


def conv(line):
    if line.startswith("!PEARL "):
        return "> [!tip] Clinical pearl\n> " + line[7:]
    if line.startswith("!SUMBER "):
        return "> [!warning] Catatan sumber\n> " + line[8:]
    if line.startswith("!IMG "):
        name, cap = [x.strip() for x in line[5:].split("|", 1)]
        return "![[%s|480]]\n*%s*" % (name, cap)
    return line


parts = [head]
for title, f in part["sections"]:
    parts.append("## " + title + "\n")
    with open(os.path.join(SHORT, f + ".md"), encoding="utf-8") as fh:
        lines = fh.read().replace("\r", "").split("\n")
    out = []
    for l in lines:
        out.append(conv(l))
        if l.startswith("!"):
            out.append("")
    parts.append("\n".join(out).strip() + "\n")

os.makedirs(ATT, exist_ok=True)
if os.path.isdir(IMGDIR):
    for fn in os.listdir(IMGDIR):
        if fn.startswith(LETTER + "_") and fn.endswith(".png"):
            dst = os.path.join(ATT, fn)
            if not os.path.exists(dst):
                shutil.copy2(os.path.join(IMGDIR, fn), dst)

dst_md = os.path.join(OUT_DIR, TITLE + ".md")
if os.path.exists(dst_md) and not FORCE:
    print("EXISTS, not overwriting (use --force):", dst_md)
    sys.exit(1)
with open(dst_md, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(parts))
print("wrote", dst_md)
