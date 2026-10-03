"""
MODE MCU FINAL — kelaikan tetap diberikan walau data belum lengkap
==================================================================

Dipakai bersama oleh:
  - fase_batch.py --final   (pipeline EHR, MCU yang sudah final -- tidak akan
                             ada lagi TTV/EKG/lab/rontgen yang masuk)
  - MCU PDF eksternal/generate_pdf.py

Beda dengan alur biasa (dikonfirmasi dr. Vidya, 2026-10-03):

  Data belum lengkap (EKG usia >=35 / tanda vital) di alur biasa ->
  "Saat ini belum dapat diberikan status kelaikan kerja ...". Di mode final,
  kelaikan TETAP diberikan berdasarkan temuan yang ada, disambung
  "... dan melengkapi pemeriksaan X", mis.
      "Laik kerja dengan catatan memerlukan konsultasi dengan dokter terkait
       temuan hasil MCU dan melengkapi pemeriksaan EKG"
  Saran "Mohon segera lengkapi: ..." tetap ada.

Caranya: protocol_engine dijalankan DUA kali. Run 1 = data asli (dipakai utk
semua teks: kesimpulan, "EKG : Belum dilakukan", saran). Run 2 = salinan
dengan item yang belum lengkap diisi nilai NETRAL (EKG normal, TD 110/70)
HANYA untuk menghitung jumlah temuan -> kelaikan. Nilai netral itu tidak
pernah muncul di teks mana pun.

Flag (menentukan auto-approve di fase_batch.py --final, dikonfirmasi dr.
Vidya 2026-10-03):
  - data belum lengkap saja            -> kuning (approve otomatis)
  - merah dari temuan nyata (mis. eGFR berat, curiga hemodialisa) -> tetap
    merah = approve manual
  - kelaikan tetap tidak bisa dihitung walau item dinetralkan -> merah
  - DATA LAB TIDAK TERBACA             -> merah (fase_batch tidak menulis sama sekali)
"""

import dataclasses

from protocol_engine import proses_pegawai
from konverter_queue import queue_ke_datapegawai
from input_dict import gabung_temuan_dan
from fase3a_generate_teks import (format_ringkasan_jasmani, format_ringkasan_lab, format_hasil_ekg,
                                  format_catatan_tambahan, format_kesimpulan_gabungan, format_saran,
                                  pasien_adalah_dokter)

PREFIX_BELUM_LENGKAP = "Saat ini belum dapat diberikan status kelaikan kerja"
SUFFIX_VAKSIN = " dan diberikan vaksinasi Hepatitis B"
ALASAN_ENGINE_BELUM_LENGKAP = "Data pemeriksaan belum lengkap — TIDAK BOLEH auto-approve"
# Aturan GDP+HbA1c ("Suspek DM tipe 2") & saran GD2PP ada di protocol_engine.py
# (dipindah 2026-10-03 supaya berlaku utk pipeline EHR lama juga).


def _kelaikan_tetap_diberikan(d, hasil, pasien_dokter):
    """Return (teks_catatan_tambahan | None, daftar_yang_belum_lengkap, hasil_run2 | None)."""
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
        return None, belum, None
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
    return teks, belum, hasil2


PREFIX_SEGERA_LENGKAPI = "Mohon segera lengkapi: "


def _saran_lengkapi_rapi(saran, belum):
    """Ganti kalimat engine 'Mohon segera lengkapi: EKG belum dilakukan (usia >= 35
    tahun), ...' (terdengar seperti catatan internal) jadi 'Mohon melengkapi
    pemeriksaan EKG, tanda vital' (dikonfirmasi dr. Vidya, 2026-10-03, hanya
    mode final/PDF; rekam yg sudah di-approve dibiarkan)."""
    for i, x in enumerate(saran):
        if x.startswith(PREFIX_SEGERA_LENGKAPI):
            item = [b.replace("pemeriksaan ", "", 1) for b in belum]
            if "pemeriksaan urinalisa" in x and "urinalisa" not in item:
                item.append("urinalisa")
            return saran[:i] + [f"Mohon melengkapi pemeriksaan {', '.join(item)}"] + saran[i + 1:]
    return list(saran)


def _tambah_lengkapi(saran, item):
    """Sisipkan item ke kalimat 'Mohon (segera) lengkapi/melengkapi ...' yg sudah ada; kalau belum ada, buat baru."""
    for i, x in enumerate(saran):
        if x.startswith("Mohon segera lengkapi: ") or x.startswith("Mohon melengkapi pemeriksaan "):
            return saran[:i] + [f"{x}, pemeriksaan {item}" if x.startswith("Mohon segera") else f"{x}, {item}"] + saran[i + 1:]
    return list(saran) + [f"Mohon melengkapi pemeriksaan {item}"]


def _kelaikan_tambah_lab(teks):
    """Lab darah tidak ada -> kelaikan ikut menyebutnya. Format dikonfirmasi dr. Vidya
    (2026-10-03, NRM 493-14-16): 'Laik kerja dengan catatan melengkapi laboratorium darah, radiologi'."""
    if "melengkapi pemeriksaan " in teks:
        return teks.replace("melengkapi pemeriksaan ", "melengkapi laboratorium darah, ", 1)
    if not teks.startswith("Laik kerja"):
        return teks
    vaksin = teks.endswith(SUFFIX_VAKSIN)
    inti = teks[: -len(SUFFIX_VAKSIN)] if vaksin else teks
    inti = f"{inti} dan melengkapi laboratorium darah" if "dengan catatan" in inti \
        else f"{inti} dengan catatan melengkapi laboratorium darah"
    return inti + (SUFFIX_VAKSIN if vaksin else "")


def generate_draft_final(entry, sumber="mode MCU final"):
    """Return dict: nama, nip, draft, catatan_manual, flag, flag_alasan, temuan."""
    d, catatan_manual, override_urinalisa = queue_ke_datapegawai(entry)
    hasil = proses_pegawai(d)
    pasien_dokter = pasien_adalah_dokter(d.nama)

    flag = hasil.flag
    flag_alasan = list(hasil.flag_alasan)

    catatan_tambahan = format_catatan_tambahan(hasil, pasien_dokter)
    if hasil.kelaikan.startswith(PREFIX_BELUM_LENGKAP):
        teks, belum, hasil2 = _kelaikan_tetap_diberikan(d, hasil, pasien_dokter)
        if teks:
            catatan_tambahan = teks
            hasil.saran = _saran_lengkapi_rapi(hasil.saran, belum)
            # Alasan merah lain dari engine (mis. eGFR berat) TETAP dipertahankan;
            # hanya alasan "belum lengkap" yang diganti.
            flag_alasan = [a for a in flag_alasan if a != ALASAN_ENGINE_BELUM_LENGKAP]
            flag_alasan.append(f"Data belum lengkap ({gabung_temuan_dan(belum)}) -- kelaikan tetap diberikan ({sumber})")
            flag = "merah" if hasil2.flag == "merah" else "kuning"
        else:
            flag = "merah"
            flag_alasan.append("Kelaikan TIDAK bisa dihitung otomatis walau item belum-lengkap dinetralkan -- cek manual")

    teks_jasmani = format_ringkasan_jasmani(hasil)
    teks_lab = format_ringkasan_lab(hasil, override_urinalisa)
    # Tidak ada lab darah sama sekali (mis. PDF cuma vital/PF, RSKD Duren Sawit 2026-10-03):
    # engine menulis "Laboratorium : Normal" -- menyesatkan. Ganti "Belum dilakukan" + minta lengkapi.
    lab_darah = {k: v for k, v in (entry.get("laboratorium") or {}).items() if k != "_error"}
    if not lab_darah and teks_lab.startswith("Laboratorium :\nNormal"):
        teks_lab = teks_lab.replace("Laboratorium :\nNormal", "Laboratorium :\nBelum dilakukan", 1)
        hasil.saran = _tambah_lengkapi(hasil.saran, "laboratorium darah")
        catatan_tambahan = _kelaikan_tambah_lab(catatan_tambahan)
        flag_alasan.append(f"Laboratorium darah belum dilakukan -- kelaikan tetap diberikan ({sumber})")
        if flag == "hijau":
            flag = "kuning"

    if any("DATA LAB TIDAK TERBACA" in c for c in catatan_manual):
        flag = "merah"
    elif catatan_manual and flag == "hijau":
        flag = "kuning"

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
