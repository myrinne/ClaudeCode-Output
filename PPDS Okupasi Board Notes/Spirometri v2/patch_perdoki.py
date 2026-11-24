"""In-place corrections to Catatan_Spirometri_v2.docx after checking the PERDOKI 2019 PDF (18 pages).

Usage: python patch_perdoki.py FILE.docx   (stops without saving unless every replacement is found)
"""
import pathlib
import sys
import docx

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from docx_ops import replace_in  # noqa: E402

REPL = [  # (old, new, expected count)
    ("Konsensus PERDOKI 2019 (slide 23)", "Konsensus PERDOKI 2019 (halaman 16)", 2),
    ("(bab penilaian antar waktu, slide 22–23)", "(halaman 16, \"Signifikansi pemeriksaan\")", 1),
    ("Teks Konsensus PERDOKI 2019 sendiri berbunyi \"3 hasil yang dapat diterima dan dua di antaranya reprodusibel "
     "(perbedaan KVP tidak melebihi 150 mL)\"",
     "Konsensus PERDOKI 2019 (halaman 11) berbunyi \"Dinyatakan reproduksibel bila 2 manuver dengan nilai terbesar "
     "memiliki perbedaan volume absolut kurang dari 150 mL\"", 1),
    ("Lafazkan \"selisih dua nilai terbesar tidak melebihi 150 mL\"",
     "Lafazkan \"selisih dua nilai terbesar kurang dari 150 mL\"", 1),
    ("Tapi konsensus PERDOKI 2019 untuk OSCE board Indonesia tetap menggunakan 75%/80% sebagai cut-off Versi Paru. "
     "Patuhi PERDOKI di OSCE.",
     "Cut-off 75%/80% Versi Paru berasal dari materi ujian board, bukan dari Konsensus PERDOKI 2019, yang hanya "
     "memakai NNT (halaman 12–13). Di OSCE sebut kedua versi dan simpulkan dengan Versi Okupasi (NNT).", 1),
    ("Konsensus PERDOKI 2019 untuk ujian board tetap memakai 75%/80% (versi paru) dan NNT (versi okupasi), dikotomis "
     "tanpa gradasi. Sebutkan konsep 2022 sebagai pengetahuan pembanding, lalu simpulkan dengan lafaz PERDOKI.",
     "Konsensus PERDOKI 2019 hanya memakai NNT (versi okupasi), dikotomis tanpa gradasi; 75%/80% (versi paru) "
     "berasal dari materi ujian board. Sebutkan konsep 2022 sebagai pengetahuan pembanding, lalu simpulkan dengan "
     "NNT.", 1),
    ("mengatur penegakan diagnosis PAK dengan 7 langkah.",
     "penegakan diagnosis PAK dengan pendekatan 7 langkah (Pasal 5); Pasal 15 mencabut Permenkes 56/2016 (dibaca "
     "dari salinan sekunder, cocokkan dengan naskah resmi).", 1),
]


def paragraphs(doc):
    yield from doc.paragraphs
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                yield from cell.paragraphs


doc = docx.Document(sys.argv[1])
bad = []
for old, new, want in REPL:
    got = sum(1 for p in paragraphs(doc) if old in p.text and replace_in(p, old, new))
    print(got, want, old[:60])
    if got != want:
        bad.append(old[:60])
if bad:
    raise SystemExit(f"NOT SAVED, count differs: {bad}")
doc.save(sys.argv[1])
print("saved")
