"""
Approve Dokter otomatis -- HANYA utk versi dr. Vidya (dikonfirmasi 2026-10-03:
"langsung approve semua tanpa menunggu lengkap, saya akan baca hasil review di
notes per hari"). File ini SENGAJA tidak ikut paket "automation external pdf"
(lihat buat_paket.py), jadi paket rekan secara fisik tidak bisa approve.

Logika sama dgn approve_dokter() di fase_batch.py: radio Approve Dokter = Ya,
klik tombol Kirim panel Kesimpulan, lalu baca ulang status radio (tidak pernah
menganggap sukses tanpa verifikasi).
"""

import asyncio

FIELD_APPROVE = "FNDx0000000641"
PANEL_KESIMPULAN = "PNL_x000000457"


async def approve_dokter(frame_form):
    radio = await frame_form.query_selector(f'#{FIELD_APPROVE}Ya')
    if radio is None:
        return False, "Radio Approve Dokter (Ya) tidak ditemukan -- TIDAK di-approve."
    if await radio.is_checked():
        return True, "Approve Dokter sudah 'Ya' sebelumnya."
    await radio.click()
    await asyncio.sleep(1.0)
    tombol = None
    for tk in await frame_form.query_selector_all('input[value="Kirim"]'):
        if PANEL_KESIMPULAN in (await tk.get_attribute("onclick") or ""):
            tombol = tk
            break
    if tombol:
        await tombol.click()
        await asyncio.sleep(1.0)
    if not await radio.is_checked():
        return False, "Radio TIDAK ter-check setelah diklik -- kemungkinan submit gagal/terkunci."
    return True, "Approve Dokter = Ya tersimpan" + (" & Kirim diklik." if tombol else " (tombol Kirim tidak ditemukan).")
