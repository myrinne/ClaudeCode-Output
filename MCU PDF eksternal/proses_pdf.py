"""
PROSES 1 PASIEN MCU DARI PDF EKSTERNAL
=======================================

Prasyarat: ekstrak/<NRM>.json sudah diisi (hasil baca PDF, lihat README.md).

    python proses_pdf.py 385-45-12 --tanpa-ehr   # uji offline: tanpa Chrome, identitas dari PDF, TIDAK bisa menulis
    python proses_pdf.py 385-45-12               # baca EHR + gabung + draft, PREVIEW saja (tidak menulis)
    python proses_pdf.py 385-45-12 --tulis       # tulis 8 field ke EHR

APPROVE DOKTER TIDAK PERNAH DISENTUH oleh script ini (dikonfirmasi dr.
Vidya, 2026-10-03: approve manual dulu sampai alur PDF terbukti andal).
Beda dari fase3b/fase_batch lama yang auto-approve flag hijau/kuning.

Urutan (mode dengan EHR):
  1. Buka pasien by NRM (fungsi fase0 lama), baca SEMUA data layar (fase1 lama)
  2. Cek identitas PDF vs EHR: nama longgar (gelar diabaikan), tgl lahir wajib sama
  3. Cek ulang hasil baca PDF: tiap angka dari halaman teks harus benar2 ada di halaman itu
  4. Gabung EHR + PDF (EHR menang), generate draft
  5. Simpan draft/<NRM>.json + tambah ke notes_pdf_<tanggal>.md
  6. (--tulis) cek NIP halaman lagi, tulis 8 field, verifikasi tiap field
"""

import asyncio
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import _jalur  # noqa: F401
from fase3a_generate_teks import FIELD_TARGET

from pdf_ke_queue import gabung, muat_ekstrak, cek_identitas, ke_tanggal
from generate_pdf import generate_draft_pdf

FOLDER_INI = Path(__file__).resolve().parent
assert "FNDx0000000641" not in FIELD_TARGET.values(), "Approve Dokter TIDAK BOLEH ada di FIELD_TARGET"


# ---------------------------------------------------------------------------
# Cek ulang hasil baca PDF terhadap text layer
# ---------------------------------------------------------------------------

def _bentuk_angka(teks: str) -> set:
    """'16,86' -> {'16,86','16.86'}; '1000 (+4)' -> {'1000'}."""
    hasil = set()
    for a in re.findall(r"\d+(?:[.,]\d+)?", str(teks)):
        hasil |= {a, a.replace(",", "."), a.replace(".", ",")}
    return hasil


def periksa_ekstrak(nrm: str, ekstrak: dict) -> tuple:
    """Return (daftar_masalah, jumlah_dari_scan). Item 'dibaca_dari: teks' -> SETIAP angka di
    hasil-nya harus muncul di teks halaman sumber. Item dari gambar/scan tidak bisa dicek
    otomatis -> dihitung & ditandai di tabel verifikasi utk dicek mata."""
    folder = FOLDER_INI / "pdf_masuk" / nrm
    masalah, dari_scan = [], 0
    for bagian in ("lab", "urin"):
        for it in ekstrak.get(bagian, []):
            if it.get("dibaca_dari", "teks") != "teks":
                dari_scan += 1
                continue
            f = folder / f"{it.get('berkas')}_hal{it.get('halaman')}.txt"
            if not f.exists():
                masalah.append(f"{it['nama']}: file teks sumber {f.name} tidak ada")
                continue
            teks_hal = f.read_text(encoding="utf-8")
            angka_hal = _bentuk_angka(teks_hal)
            angka_item = {a for a in re.findall(r"\d+(?:[.,]\d+)?", str(it.get("hasil", "")))}
            if angka_item and not any(_bentuk_angka(a) & angka_hal for a in angka_item):
                masalah.append(f"{it['nama']} = '{it.get('hasil')}' TIDAK ditemukan di {f.name}")
            elif not angka_item and it.get("hasil") and str(it["hasil"]).lower() not in teks_hal.lower():
                masalah.append(f"{it['nama']} = '{it.get('hasil')}' TIDAK ditemukan di {f.name}")
    return masalah, dari_scan


# ---------------------------------------------------------------------------
# Tampilan & notes
# ---------------------------------------------------------------------------

def tabel_verifikasi(lap: dict) -> str:
    baris = ["| Tes (vendor) | Hasil PDF | Rujukan vendor | → RSCM | Nilai dipakai | Rujukan dipakai | Flag | Sumber |",
             "|---|---|---|---|---|---|---|---|"]
    for v in lap["verifikasi"]:
        sumber = f"{v.get('vendor', '')} {v.get('tanggal', '')} {v.get('halaman', '')}".strip()
        if v.get("dibaca_dari") not in ("teks", "hitung", None):
            sumber += " ⚠️SCAN-cek"
        catatan = v.get("catatan") or ""
        if v.get("riwayat"):
            catatan += f" riwayat: {v['riwayat']}"
        rujukan = f"{v.get('rujukan_dipakai', '')} ({v.get('sumber_rujukan', '')})"
        baris.append(f"| {v['vendor_nama']} | {v['vendor_hasil']} | {v['vendor_rujukan']} | {v['nama_rscm']} | "
                     f"{v.get('nilai_rscm', '')} | {rujukan} | {v.get('flag', '')} | {sumber} {catatan} |")
    return "\n".join(baris)


def format_notes(nrm, ident_status, ident_pesan, lap, hasil, masalah_baca, dari_scan, status_tulis, ekstrak):
    emoji = {"hijau": "🟢", "kuning": "🟡", "merah": "🔴"}.get(hasil.get("flag") if hasil else None, "❔")
    nama = hasil["nama"] if hasil else "(belum terbaca)"
    out = [f"## {nama} (NRM {nrm}) — {emoji}", f"- Identitas: **{ident_status}** — {ident_pesan}"]
    out.append("- Sumber PDF: " + "; ".join(f"{s.get('berkas')} = {s.get('vendor')} {s.get('tanggal')} "
                                          f"({s.get('isi', '')})" for s in ekstrak.get("sumber", [])))
    if lap:
        out.append("- Sumber data per bagian: " + "; ".join(f"{k}: {v}" for k, v in lap["sumber"].items()))
        if lap["dipakai_dari_ehr"]:
            out.append(f"- Lab yang sudah ada di EHR (EHR menang): {', '.join(lap['dipakai_dari_ehr'])}")
    if masalah_baca:
        out.append("- 🔴 **Hasil baca PDF tidak cocok dgn text layer**: " + "; ".join(masalah_baca))
    if dari_scan:
        out.append(f"- ⚠️ {dari_scan} nilai dibaca dari halaman SCAN — cocokkan dgn PDF (ditandai ⚠️SCAN-cek di tabel)")
    if hasil:
        semua = list(hasil["flag_alasan"]) + list(hasil["catatan_manual"])
        if semua:
            out.append("- ⚠️ CATATAN MANUAL:")
            out += [f"  - {c}" for c in semua]
    if lap and lap["info_luar"]:
        out.append("- Hasil abnormal DI LUAR protokol (tidak masuk ringkasan): " +
                   "; ".join(f"[{t}] {x}" for t, x in lap["info_luar"]))
    for x in ekstrak.get("lain", []):
        out.append(f"- Info lain dari PDF: {x}")
    if lap:
        out += ["", tabel_verifikasi(lap), ""]
    if hasil:
        d = hasil["draft"]
        out.append(f"- Kesimpulan:\n```\n{d['kesimpulan']}\n```")
        out.append(f"- Saran:\n```\n{d['saran']}\n```")
        out.append(f"- Kelaikan/Catatan tambahan: {d['catatan_tambahan']}")
    out.append(f"- Status: {status_tulis}")
    return "\n".join(out)


def simpan(nrm, teks_notes, hasil, entry, lap):
    (FOLDER_INI / "draft").mkdir(exist_ok=True)
    if hasil:
        (FOLDER_INI / "draft" / f"{nrm}.json").write_text(
            json.dumps({"hasil": hasil, "entry": entry, "laporan": lap}, ensure_ascii=False, indent=2),
            encoding="utf-8")
    notes = FOLDER_INI / f"notes_pdf_{datetime.now():%Y-%m-%d}.md"
    with open(notes, "a", encoding="utf-8") as f:
        f.write(f"\n# {datetime.now():%Y-%m-%d %H:%M}\n\n{teks_notes}\n")
    return notes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def jalankan(entry_ehr: dict, ekstrak: dict, masalah_baca: list):
    """Gabung + generate draft + satukan semua catatan. Return (entry, laporan, hasil)."""
    entry, lap = gabung(entry_ehr, ekstrak)
    hasil = generate_draft_pdf(entry)
    hasil["catatan_manual"] = list(lap["catatan"]) + hasil["catatan_manual"]
    if lap["catatan"] and hasil["flag"] == "hijau":
        hasil["flag"] = "kuning"
    if masalah_baca:
        hasil["catatan_manual"].insert(0, "HASIL BACA PDF TIDAK COCOK TEXT LAYER -- " + "; ".join(masalah_baca))
        hasil["flag"] = "merah"
    return entry, lap, hasil


def entry_dari_pdf_saja(ekstrak: dict) -> dict:
    """Mode --tanpa-ehr: identitas dari PDF, semua bagian EHR kosong."""
    ip = ekstrak.get("identitas_pdf", {})
    tl = ke_tanggal(ip.get("tgl_lahir"))
    tgl_periksa = ke_tanggal(max((s.get("tanggal") or "" for s in ekstrak.get("sumber", [])), default="")) or date.today()
    usia = (tgl_periksa.year - tl.year - ((tgl_periksa.month, tgl_periksa.day) < (tl.month, tl.day))) if tl else 999
    ident = {"nama_raw": ip.get("nama", ""), "jenis_kelamin": ip.get("jenis_kelamin", "P"),
             "tgl_lahir": ip.get("tgl_lahir"), "nip": ip.get("nip")}
    if tl:
        ident["usia"] = usia
    return {"identitas": ident, "tanda_vital": {}, "kesimpulan_existing": {}, "laboratorium": {},
            "urinalisa_raw": {}, "radiologi": {}, "ekg_asli": {}}


def cetak_ringkas(nrm, ident_status, ident_pesan, lap, hasil, masalah_baca, dari_scan):
    print("=" * 72)
    print(f"NRM {nrm} — {hasil['nama']}")
    print(f"Identitas: {ident_status} — {ident_pesan}")
    print("=" * 72)
    print("\nSumber per bagian:")
    for k, v in lap["sumber"].items():
        print(f"  {k}: {v}")
    if masalah_baca:
        print("\n🔴 HASIL BACA PDF TIDAK COCOK TEXT LAYER:")
        for m in masalah_baca:
            print(f"  - {m}")
    if dari_scan:
        print(f"\n⚠️  {dari_scan} nilai dibaca dari halaman scan — cocokkan dengan PDF.")
    print("\n" + tabel_verifikasi(lap))
    if lap["info_luar"]:
        print("\nAbnormal di luar protokol:")
        for t, x in lap["info_luar"]:
            print(f"  [{t}] {x}")
    print(f"\nFLAG: {hasil['flag'].upper()}")
    for c in list(hasil["flag_alasan"]) + list(hasil["catatan_manual"]):
        print(f"  - {c}")
    for kunci, fid in FIELD_TARGET.items():
        print(f"\n--- {kunci} ({fid}) ---\n{hasil['draft'][kunci]}")
    print()


async def mode_ehr(nrm, ekstrak, mode_tulis, masalah_baca, dari_scan):
    from playwright.async_api import async_playwright
    from fase_batch import buka_pasien_dari_nrm
    from fase1_baca import baca_halaman_aktif, buka_tab_kesimpulan, baca_identitas
    from fase3b_tulis_ehr import tulis_field

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            print("GAGAL menyambung ke Chrome. Pastikan Chrome debug (port 9222) sudah terbuka & login EHR.")
            return
        if not browser.contexts or not browser.contexts[0].pages:
            print("Tidak ada tab terbuka di Chrome.")
            return
        page = browser.contexts[0].pages[0]

        ok, pesan = await buka_pasien_dari_nrm(page, nrm)
        if not ok:
            notes = simpan(nrm, format_notes(nrm, "-", "-", None, None, masalah_baca, dari_scan,
                                             f"⚠️ Gagal buka pasien: {pesan}", ekstrak), None, None, None)
            print(f"Gagal buka pasien: {pesan}\nDicatat di {notes.name}")
            return

        entry_ehr = await baca_halaman_aktif(page)
        st, psn = cek_identitas(entry_ehr.get("identitas", {}), ekstrak.get("identitas_pdf", {}))
        if st == "stop":
            notes = simpan(nrm, format_notes(nrm, st, psn, None, None, masalah_baca, dari_scan,
                                             "🔴 DIHENTIKAN — identitas PDF tidak cocok dgn EHR", ekstrak),
                           None, entry_ehr, None)
            print(f"🔴 DIHENTIKAN — {psn}\nDicatat di {notes.name}")
            return

        entry, lap, hasil = jalankan(entry_ehr, ekstrak, masalah_baca)
        if st == "kuning":
            hasil["catatan_manual"].insert(0, f"Identitas perlu dicek: {psn}")
            if hasil["flag"] == "hijau":
                hasil["flag"] = "kuning"
        cetak_ringkas(nrm, st, psn, lap, hasil, masalah_baca, dari_scan)

        status = "👁️ Preview saja (tidak ditulis)"
        if mode_tulis:
            if masalah_baca:
                status = "🔴 TIDAK ditulis — hasil baca PDF tidak cocok text layer, perbaiki ekstrak dulu"
            elif any("DATA LAB TIDAK TERBACA" in c for c in hasil["catatan_manual"]):
                status = "🔴 TIDAK ditulis — data lab EHR rusak/menggumpal"
            else:
                frame_form = await buka_tab_kesimpulan(page)
                nip_hal = (await baca_identitas(frame_form)).get("nip")
                approve_ya = await frame_form.query_selector("#FNDx0000000641Ya")
                sudah_approve = bool(approve_ya) and await approve_ya.is_checked()
                if nip_hal != hasil["nip"]:
                    status = f"🔴 TIDAK ditulis — NIP halaman ({nip_hal}) beda dgn data yang dibaca ({hasil['nip']})"
                elif sudah_approve:
                    # Field terkunci setelah approve (ditemukan 2026-10-03, NRM 385-45-12) --
                    # jangan coba menulis; perubahan harus lewat dr. Vidya (un-approve manual).
                    status = ("⛔ TIDAK ditulis — Approve Dokter sudah 'Ya', field terkunci. "
                              "Kalau perlu diubah: un-approve manual dulu, lalu jalankan ulang --tulis")
                else:
                    gagal, dilewati = [], []
                    for kunci, fid in FIELD_TARGET.items():
                        try:
                            ok_t, psn_t = await tulis_field(frame_form, fid, hasil["draft"][kunci])
                        except Exception as ex:  # mis. field terkunci -> Playwright timeout
                            ok_t, psn_t = False, f"error: {str(ex).splitlines()[0][:150]}"
                        # Pasien tanpa order lab RSCM: 577 cuma tabel import otomatis ("Kosong"),
                        # tidak ada textarea (dicek DOM 2026-10-03, NRM 489-56-50). Isi lab sudah
                        # masuk field Kesimpulan (581) -> bukan kegagalan.
                        if not ok_t and kunci == "ringkasan_lab" and "tidak ditemukan" in psn_t:
                            print(f"– {kunci}: dilewati (tidak ada textarea; lab sudah ada di Kesimpulan)")
                            dilewati.append(kunci)
                            continue
                        print(f"{'✓' if ok_t else '✗ GAGAL'} {kunci}: {psn_t}")
                        if not ok_t:
                            gagal.append(f"{kunci} ({psn_t})")
                    jumlah = len(FIELD_TARGET) - len(dilewati)
                    ket = f" (dilewati: {', '.join(dilewati)} — tidak ada textarea)" if dilewati else ""
                    status = (f"✍️ {jumlah} field ditulis{ket} — **APPROVE MANUAL** (script tidak menyentuh Approve Dokter)"
                              if not gagal else f"⚠️ Sebagian gagal ditulis: {'; '.join(gagal)}")
        print(f"\nStatus: {status}")
        notes = simpan(nrm, format_notes(nrm, st, psn, lap, hasil, masalah_baca, dari_scan, status, ekstrak),
                       hasil, entry, lap)
        print(f"Dicatat di {notes.name}, draft di draft/{nrm}.json")


def main():
    args = sys.argv[1:]
    nrm_list = [a for a in args if not a.startswith("--")]
    if len(nrm_list) != 1:
        print(__doc__)
        sys.exit(1)
    nrm = nrm_list[0]
    ekstrak = muat_ekstrak(nrm)
    masalah_baca, dari_scan = periksa_ekstrak(nrm, ekstrak)

    if "--tanpa-ehr" in args:
        entry, lap, hasil = jalankan(entry_dari_pdf_saja(ekstrak), ekstrak, masalah_baca)
        cetak_ringkas(nrm, "offline", "mode --tanpa-ehr (identitas dari PDF, data EHR tidak dibaca)",
                      lap, hasil, masalah_baca, dari_scan)
        print("Mode --tanpa-ehr: TIDAK ada yang ditulis, notes tidak dibuat.")
        return

    asyncio.run(mode_ehr(nrm, ekstrak, "--tulis" in args, masalah_baca, dari_scan))


if __name__ == "__main__":
    main()
