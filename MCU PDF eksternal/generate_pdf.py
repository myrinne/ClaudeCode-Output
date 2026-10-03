"""
LANGKAH 4 — entry gabungan -> draft teks 8 field EHR
=====================================================

Memakai fungsi format_* dari fase3a_generate_teks.py lama APA ADANYA.
Satu-satunya beda dari pipeline lama (dikonfirmasi dr. Vidya, 2026-10-03):

  Data belum lengkap (EKG usia >=35 / tanda vital) di pipeline lama ->
  "Saat ini belum dapat diberikan status kelaikan kerja ...". Untuk pasien
  PDF eksternal, kelaikan TETAP diberikan berdasarkan temuan yang ada,
  disambung "... dan melengkapi pemeriksaan X", mis.
      "Laik kerja dengan catatan memerlukan konsultasi dengan dokter terkait
       temuan hasil MCU dan melengkapi pemeriksaan EKG"
  Saran "Mohon segera lengkapi: ..." tetap ada.

Caranya: protocol_engine dijalankan DUA kali. Run 1 = data asli (dipakai utk
semua teks: kesimpulan, "EKG : Belum dilakukan", saran). Run 2 = salinan
dengan item yang belum lengkap diisi nilai NETRAL (EKG normal, TD 110/70)
HANYA untuk menghitung jumlah temuan -> kelaikan. Nilai netral itu tidak
pernah muncul di teks mana pun.
"""

import dataclasses

import _jalur  # noqa: F401
from protocol_engine import proses_pegawai
from konverter_queue import queue_ke_datapegawai
from input_dict import gabung_temuan_dan
from fase3a_generate_teks import (format_ringkasan_jasmani, format_ringkasan_lab, format_hasil_ekg,
                                  format_catatan_tambahan, format_kesimpulan_gabungan, format_saran,
                                  pasien_adalah_dokter)

PREFIX_BELUM_LENGKAP = "Saat ini belum dapat diberikan status kelaikan kerja"
# Dikonfirmasi dr. Vidya, 2026-10-03 (NRM 385-45-12): kalau HbA1c sudah diperiksa,
# saran cek GD2PP utk GDP terganggu tidak perlu. Temuan GDP-nya tetap ditulis.
SARAN_GD2PP_GDP = "Cek GD2PP dan konsultasi Poli Pegawai untuk GDP terganggu"
SUFFIX_VAKSIN = " dan diberikan vaksinasi Hepatitis B"

# Dikonfirmasi dr. Vidya, 2026-10-03 (NRM 385-45-12): GDP naik + HbA1c DM ->
# SATU temuan saja "Suspek DM tipe 2" (baris GDP & sarannya dibuang, dan GDP
# tidak dihitung sbg temuan terpisah utk kelaikan). Kasus GDP+GD2PP naik sudah
# digabung sendiri oleh protocol_engine ("Suspek DM 2") -> tidak disentuh di sini.
KESIMPULAN_GDP = ("Peningkatan GDP / Dugaan GDP terganggu", "Suspek DM")
SARAN_GDP = (SARAN_GD2PP_GDP, "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk suspek DM")
KESIMPULAN_HBA1C_DM = "Suspek DM tipe 2 berdasarkan HbA1c"
KESIMPULAN_DM_GABUNGAN = "Suspek DM tipe 2"


def _gdp_digabung_ke_hba1c(d) -> bool:
    return d.hba1c_status == "dm2" and d.gdp_status in ("naik", "suspek_dm") and not d.gd2pp_meningkat


def _kelaikan_tetap_diberikan(d, hasil, pasien_dokter):
    """Return (teks_catatan_tambahan, daftar_yang_belum_lengkap) untuk kasus data belum lengkap."""
    belum = []
    d2 = dataclasses.replace(d)
    if d.usia >= 35 and not d.ekg_dilakukan:
        belum.append("pemeriksaan EKG")
        d2 = dataclasses.replace(d2, ekg_dilakukan=True, ekg_status="normal", ekg_abnormal_deskripsi="")
    if d.imt is None and d.lingkar_perut is None and d.td_sistolik is None and d.td_diastolik is None:
        belum.append("pemeriksaan tanda vital")
        d2 = dataclasses.replace(d2, td_sistolik=110, td_diastolik=70)
    if hasil.radiologi_belum_lengkap:
        belum.append("pemeriksaan radiologi")

    hasil2 = proses_pegawai(d2)
    if hasil2.kelaikan.startswith(PREFIX_BELUM_LENGKAP):
        # Ada penyebab "belum lengkap" lain yg belum ditangani di sini -- jangan menebak.
        return None, belum
    hasil2.radiologi_belum_lengkap = False  # ditangani sendiri lewat 'belum' di bawah
    hasil2.saran = list(hasil.saran)  # alasan "konsultasi dokter" dinilai dari saran yg BENAR2 ditulis
    teks = format_catatan_tambahan(hasil2, pasien_dokter)
    vaksin = teks.endswith(SUFFIX_VAKSIN)
    if vaksin:
        teks = teks[: -len(SUFFIX_VAKSIN)]
    lengkapi = f"melengkapi {gabung_temuan_dan(belum)}"
    teks = f"{teks} dan {lengkapi}" if "dengan catatan" in teks else f"{teks} dengan catatan {lengkapi}"
    if vaksin:
        teks += SUFFIX_VAKSIN
    return teks, belum


def generate_draft_pdf(entry):
    """Return dict: nama, nip, draft, catatan_manual, flag, flag_alasan, kelaikan."""
    d, catatan_manual, override_urinalisa = queue_ke_datapegawai(entry)
    hasil = proses_pegawai(d)
    if d.hba1c_status is not None:
        hasil.saran = [s for s in hasil.saran if s != SARAN_GD2PP_GDP]
    d_kelaikan = d
    if _gdp_digabung_ke_hba1c(d):
        # Teks dari run asli (GDP dibuang, HbA1c diganti nama); kelaikan & jumlah temuan dari
        # run TANPA GDP. gdp_status=None TIDAK dipakai utk teks krn mengubah saran glukosuria.
        d_kelaikan = dataclasses.replace(d, gdp_status=None)
        hasil_k = proses_pegawai(d_kelaikan)
        hasil.kesimpulan_lab = [KESIMPULAN_DM_GABUNGAN if x == KESIMPULAN_HBA1C_DM else x
                                for x in hasil.kesimpulan_lab if x not in KESIMPULAN_GDP]
        hasil.saran = [s for s in hasil.saran if s not in SARAN_GDP]
        hasil.kelaikan, hasil.temuan, hasil.catatan_tambahan = hasil_k.kelaikan, hasil_k.temuan, hasil_k.catatan_tambahan
    pasien_dokter = pasien_adalah_dokter(d.nama)

    flag = hasil.flag
    flag_alasan = list(hasil.flag_alasan)
    if any("DATA LAB TIDAK TERBACA" in c for c in catatan_manual):
        flag = "merah"
    elif catatan_manual and flag == "hijau":
        flag = "kuning"

    catatan_tambahan = format_catatan_tambahan(hasil, pasien_dokter)
    if hasil.kelaikan.startswith(PREFIX_BELUM_LENGKAP):
        teks, belum = _kelaikan_tetap_diberikan(d_kelaikan, hasil, pasien_dokter)
        if teks:
            catatan_tambahan = teks
            flag_alasan = [f"Data belum lengkap ({gabung_temuan_dan(belum)}) -- kelaikan tetap diberikan "
                           f"sesuai aturan pasien PDF eksternal"]
        else:
            flag_alasan.append("Kelaikan TIDAK bisa dihitung otomatis walau item belum-lengkap dinetralkan -- cek manual")

    teks_jasmani = format_ringkasan_jasmani(hasil)
    teks_lab = format_ringkasan_lab(hasil, override_urinalisa)
    teks_ekg = format_hasil_ekg(hasil)
    draft = {
        "ringkasan_jasmani": teks_jasmani,
        "ringkasan_lab": teks_lab,
        "ringkasan_radiologi": hasil.kesimpulan_radiologi,
        "hasil_ekg": teks_ekg,
        "hasil_audiometri": "Tidak dilakukan",
        "hasil_spirometri": "Tidak dilakukan",
        "catatan_tambahan": catatan_tambahan,
        "kesimpulan": format_kesimpulan_gabungan(hasil, teks_jasmani, teks_lab, teks_ekg),
        "saran": format_saran(hasil, d.nama),
    }
    return {"nama": d.nama, "nip": entry.get("identitas", {}).get("nip"), "draft": draft,
            "catatan_manual": catatan_manual, "flag": flag, "flag_alasan": flag_alasan,
            "temuan": hasil.temuan}
