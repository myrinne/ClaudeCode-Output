"""
LANGKAH 1 — AMBIL PDF dari link Google Drive + siapkan untuk dibaca
=====================================================================

Unduh satu atau lebih PDF (link Drive publik, tanpa login) untuk satu NRM,
lalu per halaman simpan:
  - teks (kalau PDF punya text layer)  -> pdf_masuk/<NRM>/<berkas>_hal<N>.txt
  - gambar (selalu, utk halaman scan/EKG) -> pdf_masuk/<NRM>/<berkas>_hal<N>.png

Folder pdf_masuk/ di-.gitignore (data pasien).

Cara pakai:
    python ambil_pdf.py 385-45-12 <link_drive_1> [<link_drive_2> ...]
"""

import re
import sys
import urllib.request
from pathlib import Path

import pdfplumber
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")

FOLDER_INI = Path(__file__).resolve().parent
BATAS_TEKS_MINIMAL = 40  # halaman dgn teks < ini dianggap scan -> wajib dibaca dari gambar


def id_drive(link: str) -> str:
    for pola in (r"/file/d/([\w-]+)", r"[?&]id=([\w-]+)", r"/d/([\w-]+)"):
        m = re.search(pola, link)
        if m:
            return m.group(1)
    raise ValueError(f"ID Google Drive tidak ditemukan di link: {link}")


def unduh(link: str, tujuan: Path) -> None:
    fid = id_drive(link)
    url = f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise RuntimeError(
            f"Yang terunduh dari {link} BUKAN PDF (kemungkinan file tidak dibagikan publik "
            f"'Anyone with the link'). 200 byte awal: {data[:200]!r}")
    tujuan.write_bytes(data)


def siapkan_halaman(pdf: Path, folder: Path) -> list:
    """Return list ringkasan per halaman: (no, jumlah_karakter_teks, perlu_baca_gambar)."""
    ringkas = []
    dok = pymupdf.open(pdf)
    with pdfplumber.open(pdf) as p:
        for i, hal in enumerate(p.pages, start=1):
            teks = hal.extract_text() or ""
            (folder / f"{pdf.stem}_hal{i}.txt").write_text(teks, encoding="utf-8")
            dok[i - 1].get_pixmap(dpi=130).save(folder / f"{pdf.stem}_hal{i}.png")
            ringkas.append((i, len(teks.strip()), len(teks.strip()) < BATAS_TEKS_MINIMAL))
    return ringkas


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    nrm, links = sys.argv[1], sys.argv[2:]
    folder = FOLDER_INI / "pdf_masuk" / nrm
    folder.mkdir(parents=True, exist_ok=True)

    for n, link in enumerate(links, start=1):
        pdf = folder / f"berkas{n}.pdf"
        print(f"Mengunduh berkas{n} ...")
        unduh(link, pdf)
        ringkas = siapkan_halaman(pdf, folder)
        print(f"  {pdf.name}: {len(ringkas)} halaman")
        for no, nchar, scan in ringkas:
            ket = "SCAN/GAMBAR -> baca dari .png" if scan else f"teks {nchar} karakter"
            print(f"    hal {no}: {ket}")
        (folder / f"berkas{n}.link.txt").write_text(link, encoding="utf-8")

    print(f"\nSelesai. Berkas di {folder}")
    print(f"Langkah berikut: baca semua halaman -> isi ekstrak/{nrm}.json (lihat README.md)")


if __name__ == "__main__":
    main()
