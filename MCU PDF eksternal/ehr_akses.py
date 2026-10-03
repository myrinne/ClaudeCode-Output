"""
Akses EHR yang dipakai proses_pdf.py: buka pasien by NRM, tulis 1 field,
cek status Approve Dokter.

Sengaja TIDAK meng-import fase_batch.py / fase3b_tulis_ehr.py -- dua file itu
punya fungsi auto-approve. Pipeline PDF eksternal tidak pernah approve, jadi
yang diambil cuma fungsi yang diperlukan (logikanya sama persis dgn aslinya).
"""

import asyncio

import _jalur  # noqa: F401
from fase0_buka_pasien import cari_pasien, cari_kandidat_kunjungan_mcu, render_form_klinis
from fase1_baca import buka_tab_kesimpulan

FIELD_APPROVE = "FNDx0000000641"


async def buka_pasien_dari_nrm(page, nrm):
    """Cari pasien, pilih kunjungan MCU terbaru, render form klinis (sama dgn fase_batch.py).
    Return (berhasil, nama_atau_pesan_error)."""
    mpi_pid, nama, error = await cari_pasien(page, nrm)
    if error:
        return False, error
    kandidat, _semua, error = await cari_kandidat_kunjungan_mcu(page)
    if error:
        return False, f"{error} (pasien: {nama})"
    for k in kandidat[:5]:
        ok, _url = await render_form_klinis(page, mpi_pid, k["adm_id"])
        if ok:
            return True, nama
    return False, f"Tidak ada kunjungan yang berhasil me-render form klinis penuh (pasien: {nama})."


async def cari_elemen_editable(frame, field_id):
    elements = await frame.query_selector_all(f'#{field_id}')
    if not elements:
        return None, "elemen tidak ditemukan di halaman"
    for el in elements:
        if await el.get_attribute("readonly") is None:
            return el, None
    return None, f"{len(elements)} elemen ditemukan tapi semuanya readonly"


async def tulis_field(frame, field_id, teks):
    """Isi field + trigger onchange (auto-save EHR), lalu verifikasi nilainya (sama dgn fase3b)."""
    el, err = await cari_elemen_editable(frame, field_id)
    if el is None:
        return False, err
    await el.fill(teks)
    await el.dispatch_event("change")
    await el.evaluate("el => el.blur()")
    await asyncio.sleep(1.0)
    nilai = await el.input_value()
    if nilai.strip() != teks.strip():
        return False, f"Nilai setelah ditulis tidak cocok. Terbaca: {nilai[:100]!r}"
    return True, "tersimpan (terverifikasi dari nilai field setelah ditulis)"


async def sudah_approve(frame_form) -> bool:
    r = await frame_form.query_selector(f"#{FIELD_APPROVE}Ya")
    return bool(r) and await r.is_checked()


async def cek_approve_nrm(page, nrm):
    """Buka NRM lain & baca status Approve Dokter-nya (read-only). Return (bisa_dibaca, sudah_approve, pesan)."""
    ok, pesan = await buka_pasien_dari_nrm(page, nrm)
    if not ok:
        return False, False, pesan
    frame_form = await buka_tab_kesimpulan(page)
    return True, await sudah_approve(frame_form), pesan
