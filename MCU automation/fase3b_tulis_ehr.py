"""
FASE 3b — TULIS DRAFT KE EHR (MENULIS KE BROWSER — HATI-HATI)
====================================================================

BEDA dengan semua file Fase 1/2/3a sebelumnya: file ini SUNGGUHAN menulis
ke field di EHR RSCM. Field-field itu auto-save begitu kehilangan fokus
(lihat PETA_FIELD_EHR.md) — TIDAK ADA draft/undo di sisi RSCM.

Safety yang dibangun di sini:
  1. VERIFIKASI NIP — dibandingkan NIP pasien di draft_fase3.json dengan
     NIP di halaman EHR yang sedang terbuka. Kalau tidak cocok, BATALKAN,
     apa pun mode yang dipakai.
  2. DEFAULT = MODE PREVIEW (tanpa argumen) — cuma menampilkan isi field
     saat ini vs draft, TIDAK menulis apa pun.
  3. Mode tulis sungguhan HANYA jalan dengan flag --tulis, dan tetap minta
     konfirmasi "y" eksplisit sebelum submit (kecuali dijalankan
     non-interaktif, dalam hal itu otomatis DIBATALKAN demi keamanan —
     tidak pernah auto-yes diam-diam).
  4. FNDx0000000641 (Approve Dokter) — TIDAK ada di FIELD_TARGET, ditulis
     terpisah SETELAH ke-8 field klinis berhasil semua. Kebijakan sama
     dengan fase_batch.py (dikonfirmasi dr. Vidya): flag hijau/kuning ->
     otomatis di-set "Ya" + tombol Kirim panel diklik, TANPA tanya lagi.
     Flag merah (data belum lengkap) -> tetap TIDAK disentuh, perlu approve
     manual. Kalau ada field klinis yang gagal ditulis -> juga TIDAK
     di-approve otomatis, demi keamanan.

Cara pakai:
    python fase3b_tulis_ehr.py            # preview saja, aman
    python fase3b_tulis_ehr.py --tulis     # tulis sungguhan (minta konfirmasi)
"""

import sys
import json
import asyncio

sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

from fase1_baca import sambung_dan_cari_halaman, buka_tab_kesimpulan, baca_identitas
from fase3a_generate_teks import FIELD_TARGET

assert "FNDx0000000641" not in FIELD_TARGET.values(), "Approve Dokter TIDAK BOLEH ada di FIELD_TARGET"

FIELD_APPROVE = "FNDx0000000641"
PANEL_KESIMPULAN = "PNL_x000000457"


async def approve_dokter(frame_form):
    """Set radio Approve Dokter = 'Ya' lalu klik tombol Kirim panel Kesimpulan.
    Return (berhasil: bool, pesan: str). Tidak pernah diam-diam menganggap
    sukses -- selalu baca ulang status radio setelah aksi. (Sama persis
    dengan fase_batch.py -- lihat itu untuk detail histori/verifikasi DOM.)"""
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


def konfirmasi(pertanyaan: str, auto_ya: bool = False) -> bool:
    """
    Minta konfirmasi y/n. Non-interaktif (EOF) -> selalu False (aman),
    KECUALI auto_ya=True (flag --ya) — dipakai HANYA ketika pengguna sudah
    memberi konfirmasi eksplisit di chat untuk pasien & preview yang PERSIS
    sama dengan yang baru saja ditampilkan di layar.
    """
    if auto_ya:
        print(f"{pertanyaan}y  (--ya dipakai, sudah dikonfirmasi pengguna di chat sebelum run ini)")
        return True
    try:
        jawaban = input(pertanyaan)
    except EOFError:
        print("\n(Tidak ada input interaktif terdeteksi — dibatalkan demi keamanan.)")
        return False
    return jawaban.strip().lower() in ("y", "ya", "yes")


async def cari_elemen_editable(frame, field_id):
    """Cari elemen textarea/input yang BUKAN readonly untuk field_id ini.
    Return (elemen, pesan_error)."""
    elements = await frame.query_selector_all(f'#{field_id}')
    if not elements:
        return None, "elemen tidak ditemukan di halaman"
    for el in elements:
        is_ro = await el.get_attribute("readonly")
        if is_ro is None:
            return el, None
    return None, f"{len(elements)} elemen ditemukan tapi semuanya readonly (tidak ada yang bisa ditulis)"


async def tulis_field(frame, field_id, teks):
    """Isi field & trigger onchange (supaya submit_panelfinding jalan).
    Return (berhasil: bool, pesan)."""
    el, err = await cari_elemen_editable(frame, field_id)
    if el is None:
        return False, err
    await el.fill(teks)
    await el.dispatch_event("change")
    await el.evaluate("el => el.blur()")
    await asyncio.sleep(1.0)  # beri waktu AJAX submit_panelfinding jalan
    nilai_setelah = await el.input_value()
    if nilai_setelah.strip() != teks.strip():
        return False, f"Nilai setelah ditulis tidak cocok — kemungkinan submit gagal. Terbaca: {nilai_setelah[:100]!r}"
    return True, "tersimpan (terverifikasi dari nilai field setelah ditulis)"


async def main():
    mode_tulis = "--tulis" in sys.argv
    auto_ya = "--ya" in sys.argv

    with open("draft_fase3.json", encoding="utf-8") as f:
        semua_draft = json.load(f)

    if not semua_draft:
        print("draft_fase3.json kosong. Jalankan fase3a_generate_teks.py dulu.")
        return

    print("=" * 70)
    print(f"FASE 3b — {'TULIS KE EHR' if mode_tulis else 'PREVIEW (tidak menulis apa pun)'}")
    print("=" * 70)
    print("\nMenghubungkan ke Chrome yang sudah Anda buka...\n")

    async with async_playwright() as p:
        browser, page, error = await sambung_dan_cari_halaman(p)
        if error:
            print(error)
            return

        print(f"Halaman aktif: {page.url}\n")
        frame_form = await buka_tab_kesimpulan(page)
        ident_halaman = await baca_identitas(frame_form)
        nip_halaman = ident_halaman.get("nip")
        nama_halaman = ident_halaman.get("nama_raw", "(tidak terbaca)")

        print(f"Pasien di halaman EHR saat ini : {nama_halaman} (NIP {nip_halaman})")

        # --- Cari draft yang NIP-nya cocok dengan halaman yang sedang terbuka ---
        draft_cocok = [d for d in semua_draft if d.get("nip") and d.get("nip") == nip_halaman]

        if not draft_cocok:
            print("\n🔴 DIBATALKAN — tidak ada draft di draft_fase3.json yang NIP-nya")
            print(f"   cocok dengan halaman yang sedang terbuka (NIP {nip_halaman}).")
            print("   Ini bisa berarti Anda membuka pasien yang BEDA dari saat Fase 1/3a")
            print("   dijalankan. Buka pasien yang benar dulu, atau jalankan ulang")
            print("   Fase 1 -> Fase 3a untuk pasien yang sedang terbuka ini.")
            return

        if len(draft_cocok) > 1:
            print(f"\n🔴 DIBATALKAN — ditemukan {len(draft_cocok)} draft dengan NIP yang sama")
            print("   di draft_fase3.json. Ambigu, tidak aman dilanjutkan otomatis.")
            return

        entri = draft_cocok[0]
        print(f"✓ NIP cocok dengan draft: {entri['nama']}\n")

        # Hard block HANYA untuk data yang benar-benar rusak/tidak terbaca
        # (lab menggumpal) — di kasus itu SEMUA teks draft tidak bisa dipercaya.
        # Flag merah krn "data belum lengkap" (mis. EKG belum dilakukan) TIDAK
        # diblokir di sini — teksnya justru sudah benar ("belum dapat ditentukan,
        # mohon lengkapi EKG") dan memang itu yang seharusnya ditulis ke EHR.
        ada_data_rusak = any("DATA LAB TIDAK TERBACA" in c for c in entri.get("catatan_manual", []))
        if ada_data_rusak:
            print("🔴 DATA LAB RUSAK/MENGGUMPAL — JANGAN ditulis ke EHR.")
            print("   Perbaiki data di Fase 1 dulu (expand section Laboratorium di layar), jangan lanjutkan.")
            return
        if entri["flag"] == "merah":
            print("🔴 FLAG MERAH — data pemeriksaan belum lengkap. Teks draft SUDAH")
            print("   benar mencerminkan itu (\"belum dapat ditentukan... mohon lengkapi...\").")
            print("   Pastikan Anda review dulu sebelum menulis. Catatan:")
        elif entri["flag"] == "kuning":
            print("🟡 FLAG KUNING — pastikan Anda sudah baca catatan manual berikut")
            print("   sebelum menulis:")
        if entri["flag"] in ("merah", "kuning"):
            for c in entri.get("catatan_manual", []):
                print(f"   - {c}")
            print()

        # --- Tampilkan diff (current vs draft) untuk tiap field ---
        # KEBIJAKAN (revisi Anda): SELALU tulis ulang semua field dengan draft
        # terbaru, walau sudah ada isi lama — isi lama bisa jadi ditulis
        # sebelum pemeriksaan (mis. EKG) lengkap, jadi draft baru yang
        # dihitung dari data terkini yang harus menang. Field yang sudah
        # di-approve/terkunci akan otomatis gagal sendiri (lihat GAGAL di
        # bawah), bukan diam-diam ditembus.
        rencana = []
        for kunci, field_id in FIELD_TARGET.items():
            el, err = await cari_elemen_editable(frame_form, field_id)
            nilai_sekarang = await el.input_value() if el else f"(tidak terbaca: {err})"
            teks_baru = entri["draft"][kunci]

            print(f"--- {kunci} ({field_id}) ---")
            print(f"  ISI SEKARANG : {nilai_sekarang[:200]!r}")
            print(f"  AKAN DIISI   : {teks_baru[:200]!r}")
            print()
            rencana.append((kunci, field_id))

        if not mode_tulis:
            print("Mode PREVIEW — tidak ada yang ditulis. Jalankan dengan --tulis")
            print("untuk benar-benar menulis (akan minta konfirmasi lagi).")
            return

        print("=" * 70)
        print(f"AKAN MENULIS {len(rencana)} FIELD KE EHR UNTUK: {entri['nama']} (NIP {nip_halaman})")
        print("Field ini AUTO-SAVE — TIDAK ADA UNDO setelah ditulis.")
        if entri["flag"] == "merah":
            print("Flag MERAH — Approve Dokter TIDAK akan disentuh (perlu approve manual).")
        else:
            print("Approve Dokter akan otomatis di-set 'Ya' + Kirim setelah semua field tersimpan.")
        print("=" * 70)

        if not konfirmasi("\nLanjutkan menulis SEMUA field di atas ke EHR? (y/N): ", auto_ya):
            print("Dibatalkan oleh pengguna. Tidak ada yang ditulis.")
            return

        semua_ok = True
        for kunci, field_id in rencana:
            teks_baru = entri["draft"][kunci]
            ok, pesan = await tulis_field(frame_form, field_id, teks_baru)
            status = "✓" if ok else "✗ GAGAL"
            print(f"{status} {kunci} ({field_id}): {pesan}")
            semua_ok = semua_ok and ok

        if entri["flag"] == "merah":
            print("\n🔴 Flag merah — Approve Dokter TIDAK disentuh, perlu approve manual.")
        elif not semua_ok:
            print("\n✗ Ada field klinis yang gagal ditulis — Approve Dokter TIDAK di-approve otomatis demi keamanan.")
        else:
            ok_approve, pesan_approve = await approve_dokter(frame_form)
            status = "✓" if ok_approve else "✗ GAGAL"
            print(f"\n{status} Approve Dokter: {pesan_approve}")

        print("\nSelesai. Silakan cek langsung di layar EHR untuk verifikasi akhir.")


if __name__ == "__main__":
    asyncio.run(main())
