"""
FASE BATCH — Proses banyak NRM sekaligus: baca -> interpretasi -> tulis 8
field klinis -> (kalau data lengkap) approve dokter otomatis + kirim ->
catat semua ke notes_YYYY-MM-DD.md (satu file per hari, dikonfirmasi dr.
Vidya 2026-07-24 supaya tidak menumpuk panjang) untuk direview di akhir
(BUKAN per-pasien).
====================================================================

Menggabungkan fase0 (buka pasien) + fase1 (baca) + fase3a (generate teks)
+ fase3b (tulis field) jadi SATU sesi Playwright yang connect sekali ke
Chrome, lalu loop per NRM di `page` yang sama -- tidak lewat queue.json /
draft_fase3.json (itu untuk alur manual satu-pasien, tetap ada terpisah).

KEBIJAKAN APPROVE OTOMATIS (dikonfirmasi dr. Vidya):
  - Flag MERAH (data belum lengkap / lab rusak) -> 8 field klinis TETAP
    ditulis (teksnya sudah jujur bilang "belum lengkap"), Approve Dokter
    TIDAK disentuh -- tetap perlu approve manual.
  - Flag HIJAU dan KUNING (termasuk trombositosis) -> 8 field ditulis DAN
    Approve Dokter otomatis di-set "Ya" + tombol Kirim panel diklik.
    Catatan manual (mis. trombositosis) tetap lengkap di notes.md.

Approve Dokter (FNDx0000000641) adalah RADIO Ya/Tidak di panel Kesimpulan
yang sama dgn 8 field lain (frmfinding_PNL_x000000457), auto-save lewat
submit_panelfinding persis seperti field lain begitu diklik -- dipastikan
lewat inspeksi DOM langsung (bukan tebakan), lihat riwayat sesi kerja.
Panel itu juga punya SATU tombol "Kirim" umum yang diklik sesudahnya utk
memastikan tersimpan, sesuai instruksi Anda ("approve dokter: ya, dan kirim").

Setiap pasien diproses dalam try/except sendiri -- kegagalan 1 pasien
TIDAK menghentikan batch, dicatat sebagai gagal di notes.md dan lanjut ke
NRM berikutnya.

Cara pakai:
    python fase_batch.py --ya 406-66-04 123-45-67      # tulis + approve sungguhan
    python fase_batch.py 406-66-04 123-45-67           # preview saja, tidak menulis apa pun
"""

import sys
import asyncio
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

from fase0_buka_pasien import cari_pasien, cari_kandidat_kunjungan_mcu, render_form_klinis
from fase1_baca import baca_halaman_aktif, buka_tab_kesimpulan, baca_identitas
from fase3a_generate_teks import generate_draft, FIELD_TARGET
from fase3b_tulis_ehr import cari_elemen_editable, tulis_field

FIELD_APPROVE = "FNDx0000000641"
PANEL_KESIMPULAN = "PNL_x000000457"

def notes_path_hari_ini():
    """Satu file notes per hari (dikonfirmasi dr. Vidya, 2026-07-24) --
    supaya tidak menumpuk panjang ke bawah di satu file. Nama file otomatis
    ikut tanggal jalannya batch, mis. notes_2026-07-25.md."""
    return f"notes_{datetime.now().strftime('%Y-%m-%d')}.md"


async def approve_dokter(frame_form):
    """Set radio Approve Dokter = 'Ya' lalu klik tombol Kirim panel Kesimpulan.
    Return (berhasil: bool, pesan: str). Tidak pernah diam-diam menganggap
    sukses -- selalu baca ulang status radio setelah aksi."""
    radio = await frame_form.query_selector(f'#{FIELD_APPROVE}Ya')
    if radio is None:
        return False, "Radio Approve Dokter (Ya) tidak ditemukan di halaman -- TIDAK di-approve."

    if await radio.is_checked():
        return True, "Approve Dokter sudah 'Ya' sebelumnya (tidak diubah lagi)."

    await radio.click()
    await asyncio.sleep(1.0)

    tombol_kirim = None
    for tk in await frame_form.query_selector_all('input[value="Kirim"]'):
        onclick = await tk.get_attribute("onclick") or ""
        if PANEL_KESIMPULAN in onclick:
            tombol_kirim = tk
            break
    if tombol_kirim:
        await tombol_kirim.click()
        await asyncio.sleep(1.0)

    if not await radio.is_checked():
        return False, "Radio TIDAK ter-check setelah diklik -- kemungkinan submit gagal atau field terkunci (sudah pernah di-approve/locked)."

    pesan = "Approve Dokter = Ya tersimpan"
    pesan += " & tombol Kirim panel diklik." if tombol_kirim else " (tombol Kirim panel tidak ditemukan -- hanya andalkan auto-save radio)."
    return True, pesan


async def buka_pasien_dari_nrm(page, nrm):
    """Gabungan logika fase0: cari pasien, pilih kunjungan MCU terbaru, render
    form klinis. Return (berhasil: bool, pesan: str) -- TIDAK menebak kalau
    ambigu, sama seperti fase0_buka_pasien.py asli."""
    mpi_pid, nama, error = await cari_pasien(page, nrm)
    if error:
        return False, error

    kandidat, semua_baris, error = await cari_kandidat_kunjungan_mcu(page)
    if error:
        return False, f"{error} (pasien: {nama})"

    for i, k in enumerate(kandidat[:5]):
        ok, url_form = await render_form_klinis(page, mpi_pid, k["adm_id"])
        if ok:
            return True, nama
    return False, f"Tidak ada kandidat kunjungan yang berhasil me-render form klinis penuh (pasien: {nama})."


async def proses_satu_pasien(page, nrm, mode_tulis):
    """Proses 1 NRM penuh: buka -> baca -> draft -> tulis field -> approve.
    Return dict ringkasan untuk notes.md. TIDAK melempar exception ke luar --
    semua kegagalan ditangkap dan direkam di dict."""
    hasil = {"nrm": nrm, "status": None, "detail": "", "nama": None, "nip": None,
             "flag": None, "draft": None, "field_writes": [], "approve": None,
             "catatan_manual": [], "flag_alasan": []}

    ok, pesan = await buka_pasien_dari_nrm(page, nrm)
    if not ok:
        hasil["status"] = "perlu_cek_manual"
        hasil["detail"] = pesan
        return hasil
    hasil["nama"] = pesan

    entry = await baca_halaman_aktif(page)
    nama, draft, catatan_manual, flag, flag_alasan, nip = generate_draft(entry)
    hasil.update(nama=nama, nip=nip, flag=flag, draft=draft,
                 catatan_manual=catatan_manual, flag_alasan=flag_alasan)

    frame_form = await buka_tab_kesimpulan(page)
    ident_halaman = await baca_identitas(frame_form)
    if ident_halaman.get("nip") != nip:
        hasil["status"] = "gagal"
        hasil["detail"] = f"NIP tidak cocok (draft={nip}, halaman={ident_halaman.get('nip')}) -- dibatalkan demi keamanan."
        return hasil

    ada_data_rusak = any("DATA LAB TIDAK TERBACA" in c for c in catatan_manual)
    if ada_data_rusak:
        hasil["status"] = "gagal"
        hasil["detail"] = "DATA LAB TIDAK TERBACA/rusak -- tidak ditulis sama sekali. Perbaiki baca data dulu."
        return hasil

    if not mode_tulis:
        hasil["status"] = "preview"
        hasil["detail"] = "Mode preview -- tidak ada yang ditulis."
        return hasil

    for kunci, field_id in FIELD_TARGET.items():
        teks_baru = draft[kunci]
        ok_tulis, pesan_tulis = await tulis_field(frame_form, field_id, teks_baru)
        hasil["field_writes"].append((kunci, ok_tulis, pesan_tulis))

    semua_field_ok = all(ok for _, ok, _ in hasil["field_writes"])

    if flag == "merah":
        hasil["status"] = "ditahan_data_belum_lengkap"
        hasil["detail"] = "; ".join(flag_alasan) if flag_alasan else "Data pemeriksaan belum lengkap."
    elif not semua_field_ok:
        hasil["status"] = "ditulis_sebagian_tidak_di_approve"
        hasil["detail"] = "Sebagian field klinis gagal ditulis -- TIDAK di-approve otomatis demi keamanan."
    else:
        ok_approve, pesan_approve = await approve_dokter(frame_form)
        hasil["approve"] = (ok_approve, pesan_approve)
        hasil["status"] = "approved_terkirim" if ok_approve else "ditulis_approve_gagal"
        hasil["detail"] = pesan_approve

    return hasil


def format_notes_entry(h):
    emoji = {"hijau": "🟢", "kuning": "🟡", "merah": "🔴"}.get(h.get("flag"), "❔")
    nama = h.get("nama") or f"(NRM {h['nrm']}, nama tidak terbaca)"
    baris = [f"## {nama} (NRM {h['nrm']}, NIP {h.get('nip')}) — {emoji}"]

    if h["status"] == "perlu_cek_manual":
        baris.append(f"- ⚠️ PERLU DICEK MANUAL: {h['detail']}")
        return "\n".join(baris)

    # Catatan manual / alasan flag SELALU ditampilkan di sini, terpisah dari
    # baris Status di bawah -- supaya tidak diam-diam tertimpa/hilang kalau
    # approve berhasil (kasus: kuning krn trombositosis tapi datanya lengkap
    # -> approve jalan terus, tapi catatannya tetap WAJIB terlihat di sini,
    # tidak boleh diabaikan cuma karena approve-nya sukses). Dikonfirmasi
    # dr. Vidya, 2026-07-24: "kalau ada temuan yang belum ada di protokol,
    # notifikasi saya ... jangan diabaikan" -- ini juga menangkap catatan
    # PERLU_CEK_MANUAL dari catch-all flag lab yang belum dikenal protokol.
    semua_catatan = list(h.get("flag_alasan") or []) + list(h.get("catatan_manual") or [])
    if semua_catatan:
        baris.append("- ⚠️ CATATAN MANUAL (baca sebelum/sesudah approve):")
        for c in semua_catatan:
            baris.append(f"  - {c}")

    draft = h.get("draft")
    if draft:
        baris.append(f"- Temuan (Kesimpulan): {draft['kesimpulan']}")
        baris.append(f"- Saran: {draft['saran']}")
        baris.append(f"- Kelaikan/Catatan tambahan: {draft['catatan_tambahan']}")

    status_map = {
        "approved_terkirim": "✅ Ditulis & di-approve otomatis + terkirim",
        "ditahan_data_belum_lengkap": f"🔴 Ditulis, TIDAK di-approve (data belum lengkap: {h['detail']}) — approve manual",
        "ditulis_sebagian_tidak_di_approve": f"⚠️ {h['detail']}",
        "ditulis_approve_gagal": f"⚠️ Field klinis tertulis, approve GAGAL: {h['detail']} — approve manual",
        "gagal": f"⚠️ Gagal: {h['detail']}",
        "preview": "👁️ Preview saja (tidak ditulis apa pun)",
    }
    baris.append(f"- Status: {status_map.get(h['status'], h['status'])}")

    if h["field_writes"]:
        gagal = [f"{k} ({p})" for k, ok, p in h["field_writes"] if not ok]
        if gagal:
            baris.append(f"- Field GAGAL ditulis: {'; '.join(gagal)}")

    return "\n".join(baris)


async def main():
    argv = sys.argv[1:]
    mode_tulis = "--ya" in argv
    nrm_list = [a for a in argv if a != "--ya"]

    if not nrm_list:
        print("Cara pakai: python fase_batch.py [--ya] <NRM1> <NRM2> ...")
        return

    print("=" * 70)
    print(f"FASE BATCH — {'TULIS + APPROVE OTOMATIS' if mode_tulis else 'PREVIEW (tidak menulis apa pun)'}")
    print(f"NRM ({len(nrm_list)}): {', '.join(nrm_list)}")
    print("=" * 70)

    semua_hasil = []
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            print("GAGAL menyambung ke Chrome. Pastikan Chrome debug (port 9222) sudah terbuka & login.")
            return

        contexts = browser.contexts
        if not contexts or not contexts[0].pages:
            print("Tidak ada tab terbuka di Chrome.")
            return
        page = contexts[0].pages[0]

        for nrm in nrm_list:
            print(f"\n--- Memproses NRM {nrm} ---")
            try:
                hasil = await proses_satu_pasien(page, nrm, mode_tulis)
            except Exception as e:
                hasil = {"nrm": nrm, "status": "gagal", "detail": f"Exception tak terduga: {e}",
                         "nama": None, "nip": None, "flag": None, "draft": None, "field_writes": [],
                         "catatan_manual": [], "flag_alasan": []}
            print(f"  Status: {hasil['status']} — {hasil['detail']}")
            semua_hasil.append(hasil)

    notes_path = notes_path_hari_ini()
    header = f"# Batch {datetime.now().strftime('%Y-%m-%d %H:%M')} ({'TULIS+APPROVE' if mode_tulis else 'PREVIEW'})\n"
    isi = "\n\n".join(format_notes_entry(h) for h in semua_hasil)
    with open(notes_path, "a", encoding="utf-8") as f:
        f.write("\n" + header + "\n" + isi + "\n")

    print(f"\nSelesai. Ringkasan {len(semua_hasil)} pasien ditambahkan ke {notes_path}.")


if __name__ == "__main__":
    asyncio.run(main())
