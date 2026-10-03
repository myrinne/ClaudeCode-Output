"""
BUAT PAKET "automation external pdf" untuk dibagikan ke rekan
==============================================================

    python buat_paket.py

Hasil: dist/automation external pdf.zip  (folder dist/ di-.gitignore)

Isi paket MANDIRI (tidak bergantung pada pipeline MCU lama milik rekan):
  - script pipeline PDF eksternal (folder ini)
  - engine/ : salinan protocol_engine, input_dict, konverter_queue, fase0, fase1, fase3a
    dari ../MCU automation/
  - SENGAJA TIDAK disertakan: fase_batch.py (banyak NRM + auto-approve),
    fase3b_tulis_ehr.py (auto-approve), queue.json/notes/PDF/ekstrak (data pasien)
  - pengaturan.py di paket: SATU_NRM_SAMPAI_APPROVE = True

Komentar & docstring di semua .py DISAMARKAN: NRM dan nama pasien ("kasus X NRM
...") diganti -- komentar riwayat aturan berisi data pasien asli. Kode tidak
berubah: dibuktikan dgn membandingkan AST (tanpa docstring) sebelum/sesudah.
"""

import ast
import io
import re
import shutil
import sys
import tempfile
import tokenize
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FOLDER_INI = Path(__file__).resolve().parent
NAMA_PAKET = "automation external pdf"
DIST = FOLDER_INI / "dist"
STAGING = Path(tempfile.mkdtemp(prefix="paket_mcu_")) / NAMA_PAKET  # di luar OneDrive (hindari kunci sinkronisasi)
PAKET_DOC = FOLDER_INI / "paket"  # README/CLAUDE.md/contoh khusus paket

import _jalur  # noqa: E402
FOLDER_LAMA = _jalur.FOLDER_LAMA

FILE_PIPELINE = ["ambil_pdf.py", "kamus_lab.py", "pdf_ke_queue.py", "generate_pdf.py",
                 "proses_pdf.py", "ehr_akses.py"]
FILE_ENGINE = ["protocol_engine.py", "input_dict.py", "konverter_queue.py",
               "fase0_buka_pasien.py", "fase1_baca.py", "fase3a_generate_teks.py",
               "kelaikan_final.py"]

JALUR_PAKET = '''"""Menyambungkan script ke folder engine/ (salinan protocol_engine dkk di dalam paket ini)."""

import sys
from pathlib import Path

FOLDER_INI = Path(__file__).resolve().parent
FOLDER_LAMA = FOLDER_INI / "engine"
if not (FOLDER_LAMA / "protocol_engine.py").exists():
    raise ImportError(f"Folder engine/ tidak lengkap: {FOLDER_LAMA}")
if str(FOLDER_LAMA) not in sys.path:
    sys.path.insert(0, str(FOLDER_LAMA))
'''

PENGATURAN_PAKET = '''"""
Pengaturan paket "automation external pdf".

SATU_NRM_SAMPAI_APPROVE = True -> --tulis utk NRM BARU ditolak selama NRM terakhir
yang ditulis belum di-approve dokter di EHR (dicek langsung ke EHR). Tujuannya:
setiap hasil PASTI dibaca & di-approve dokter sebelum pasien berikutnya.
JANGAN diubah ke False.
"""

SATU_NRM_SAMPAI_APPROVE = True
BOLEH_APPROVE_OTOMATIS = False  # paket tidak berisi ehr_approve.py; approve selalu manual
'''

# ---------------------------------------------------------------------------
# Penyamaran komentar
# ---------------------------------------------------------------------------

POLA_NRM = re.compile(r"\b\d{3}-\d{2}-\d{2}\b")
GELAR = {"dr", "dr.", "Dr", "Dr.", "DR", "DR.", "drg", "drg.", "Ny", "Ny.", "Tn", "Tn."}
BUKAN_NAMA = {"NRM", "Paru", "Bedah", "PMK", "KKV", "KP", "Sp", "Sp.", "EHR", "RSCM", "DD",
              "Overweight", "Obesitas", "Normal", "Normoweight", "Prehipertensi", "Hipertensi"}


def samarkan_teks(teks: str, nama_ketemu: set, nama_global: set = frozenset()) -> str:
    teks = POLA_NRM.sub("xxx-xx-xx", teks)
    # Pass 2: nama yang sudah dikenal dari file mana pun (mis. nama terpotong ganti baris
    # setelah "kasus") -- hapus nama depan + kata Kapital sesudahnya.
    for k in nama_global:
        teks = re.sub(rf"\b{re.escape(k)}\b", "[pasien]", teks)
    teks = re.sub(r"\[pasien\](?:\s+(?:[A-Z]\.|\[pasien\]))+", "[pasien]", teks)
    # Kata Kapital tepat sebelum NRM (nama tanpa kata "kasus")
    teks = re.sub(r"((?:\b[A-Z][a-z]+\.?\s+){1,4})(NRM xxx-xx-xx)",
                  lambda m: m.group(0) if all(w.rstrip(".") in BUKAN_NAMA for w in m.group(1).split())
                  else f"[pasien] {m.group(2)}", teks)

    def ganti_kasus(m):
        kata = m.group(2).split(" ")
        dipakai = []
        for k in kata:
            bersih = k.rstrip(",.;:)")
            if k in GELAR or (bersih and bersih[0].isupper() and not bersih.isupper()
                              and bersih not in BUKAN_NAMA and bersih.isalpha()):
                dipakai.append(k)
                if bersih != k and k not in GELAR:  # tanda baca menutup nama (titik di "dr." bukan penutup)
                    break
            else:
                break
        if not any(k not in GELAR for k in dipakai):
            return m.group(0)
        nama = " ".join(dipakai)
        nama_ketemu.add(nama.rstrip(",.;:)"))
        sisa = " ".join(kata[len(dipakai):])
        akhir = nama[len(nama.rstrip(",.;:)")):]
        return f"{m.group(1)}[pasien]{akhir}" + (f" {sisa}" if sisa else "")

    return re.sub(r"(kasus\s+)([^\n]*)", ganti_kasus, teks)


def samarkan_kode(src: str, nama_ketemu: set, nama_global: set = frozenset()) -> str:
    """Hanya COMMENT & STRING triple-quote (docstring) yang diubah."""
    hasil = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        s = tok.string
        if tok.type == tokenize.COMMENT or (tok.type == tokenize.STRING and s.lstrip("rbuRBU").startswith(('"""', "'''"))):
            s = samarkan_teks(s, nama_ketemu, nama_global)
        hasil.append(tok._replace(string=s))
    return tokenize.untokenize(hasil)


KATA_UMUM = {"Buka", "Dalam", "Normal", "Overweight", "Obesitas", "Konsultasi", "Kalau", "Sebelumnya",
             "Kasus", "Dikonfirmasi", "Pasien", "Paru", "Bedah", "Laik", "Saran", "Tidak", "Untuk", "Sekarang",
             "Jadi", "Hanya", "Juga", "Catatan", "Data", "Lihat", "Temuan", "Hasil", "Direvisi", "Ditambahkan",
             "Contoh", "Kesimpulan", "Urinalisa", "Field", "Lama", "Dulu", "Baris", "Mohon", "Pertama", "Tapi",
             "Karena", "Dengan", "Pola", "Sama", "Bukan", "Setelah", "Masih", "Supaya", "Nama", "Vidya"}


def kumpulkan_nama(sumber_list) -> set:
    """Pass 1: SEMUA kata nama (>=4 huruf) dari teks mentah semua file -- setelah 'kasus' (boleh
    lanjut ke baris komentar berikutnya) atau kata Kapital tepat sebelum 'NRM'."""
    teks = "\n".join(p.read_text(encoding="utf-8") for p in sumber_list)
    kata = set()
    for m in re.finditer(r"kasus\s*(?:\n\s*#\s*)?((?:(?:dr|Dr|DR)\.?\s+)*(?:[A-Z][a-z]+\.?\s*(?:\n\s*#\s*)?){1,5})", teks):
        kata |= {w.strip(".#") for w in m.group(1).split() if len(w.strip(".#")) >= 4}
    for m in re.finditer(r"((?:[A-Z][a-z]+\s+(?:#\s*)?){1,4})NRM", teks):
        kata |= {w for w in m.group(1).split() if len(w) >= 4}
    return kata - KATA_UMUM - BUKAN_NAMA


def ast_tanpa_docstring(src: str) -> str:
    pohon = ast.parse(src)
    for node in ast.walk(pohon):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            badan = node.body
            if badan and isinstance(badan[0], ast.Expr) and isinstance(getattr(badan[0], "value", None), ast.Constant) \
                    and isinstance(badan[0].value.value, str):
                node.body = badan[1:] or [ast.Pass()]
    return ast.dump(pohon, include_attributes=False)


def salin_samarkan(sumber: Path, tujuan: Path, nama_ketemu: set, nama_global: set):
    asli = sumber.read_text(encoding="utf-8")
    baru = samarkan_kode(asli, nama_ketemu, nama_global)
    if ast_tanpa_docstring(asli) != ast_tanpa_docstring(baru):
        raise RuntimeError(f"{sumber.name}: penyamaran MENGUBAH KODE (bukan cuma komentar) -- dibatalkan")
    tujuan.write_text(baru, encoding="utf-8")


# ---------------------------------------------------------------------------

def main():
    DIST.mkdir(exist_ok=True)
    (STAGING / "engine").mkdir(parents=True)
    nama_ketemu = set()
    sumber = [FOLDER_INI / f for f in FILE_PIPELINE] + [FOLDER_LAMA / f for f in FILE_ENGINE]
    nama_global = kumpulkan_nama(sumber)

    for f in FILE_PIPELINE:
        salin_samarkan(FOLDER_INI / f, STAGING / f, nama_ketemu, nama_global)
    for f in FILE_ENGINE:
        salin_samarkan(FOLDER_LAMA / f, STAGING / "engine" / f, nama_ketemu, nama_global)
    (STAGING / "_jalur.py").write_text(JALUR_PAKET, encoding="utf-8")
    (STAGING / "pengaturan.py").write_text(PENGATURAN_PAKET, encoding="utf-8")
    for f in PAKET_DOC.iterdir():
        shutil.copy2(f, STAGING / f.name)

    # Periksa sisa data pasien di SEMUA file paket
    sisa = []
    nama_panjang = {n for n in nama_ketemu if len(n) >= 4} | set(nama_global)
    for p in STAGING.rglob("*"):
        if p.is_file():
            t = p.read_text(encoding="utf-8")
            for m in POLA_NRM.finditer(t):
                sisa.append(f"{p.name}: NRM {m.group()}")
            for n in nama_panjang:
                if n in t:
                    sisa.append(f"{p.name}: nama '{n}'")
    if sisa:
        print("🔴 MASIH ADA DATA PASIEN -- paket TIDAK dibuat:")
        for s in sisa:
            print("  ", s)
        sys.exit(1)

    zip_path = DIST / f"{NAMA_PAKET}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(STAGING.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                z.write(p, Path(NAMA_PAKET) / p.relative_to(STAGING))
    print(f"✓ {len(nama_ketemu)} nama pasien disamarkan di komentar; kode terbukti tidak berubah (AST).")
    print(f"✓ Paket: {zip_path}")
    shutil.rmtree(STAGING.parent, ignore_errors=True)


if __name__ == "__main__":
    main()
