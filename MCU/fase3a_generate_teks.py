"""
FASE 3a — GENERATE TEKS DRAFT (READ-ONLY, TIDAK MENYENTUH BROWSER)
====================================================================

Mengubah hasil Fase 2 (protocol_engine + konverter_queue) jadi teks draft
per field EHR, dicetak ke layar dan disimpan ke draft_fase3.json.

TIDAK ADA interaksi browser di file ini sama sekali — aman, tidak akan
mengubah apa pun di RSCM. Fase 3b (menulis ke EHR) adalah file TERPISAH
yang baru dibuat setelah Anda review & approve teks dari sini, karena field
EHR auto-save begitu kehilangan fokus (tidak ada draft/undo di sisi RSCM).

Cara pakai:
    python fase3a_generate_teks.py
"""

import sys
import json
import re

sys.stdout.reconfigure(encoding="utf-8")

from protocol_engine import proses_pegawai
from konverter_queue import queue_ke_datapegawai


# ---------------------------------------------------------------------------
# Pemetaan hasil.HasilInterpretasi -> field EHR yang BENAR-BENAR editable
# (lihat PETA_FIELD_EHR.md). FNDx0000000578 (Ringkasan Radiologi) SENGAJA
# tidak ada di sini — dikonfirmasi tidak punya textarea editable terpisah
# di DOM, cuma tabel laporan radiologi hasil import otomatis. Kesimpulan
# radiologi masuk lewat section "Rontgen thorax :" di dalam field
# 'kesimpulan' (581) gabungan (lihat format_kesimpulan_gabungan).
# ---------------------------------------------------------------------------

FIELD_TARGET = {
    "ringkasan_jasmani":  "FNDx0000000576",
    "ringkasan_lab":      "FNDx0000000577",
    "hasil_ekg":          "FNDx0000000580",
    "hasil_audiometri":   "FNDx0000000874",
    "hasil_spirometri":   "FNDx0000000875",
    "catatan_tambahan":   "FNDx0000000964",
    "kesimpulan":         "FNDx0000000581",
    "saran":              "FNDx0000000926",
}


def format_ringkasan_jasmani(hasil) -> str:
    """Kosong HANYA terjadi kalau TD/BMI/Lingkar Perut semuanya belum
    diukur (lihat vital_belum_diukur di protocol_engine.py) — bukan berarti
    normal. Jangan tulis 'Normal' di sini, itu menyesatkan."""
    if hasil.kesimpulan_jasmani:
        return "\n".join(hasil.kesimpulan_jasmani)
    return "[BELUM DIUKUR — tanda vital (TD/BMI/Lingkar Perut) belum diinput]"


def format_ringkasan_lab(hasil, override_urinalisa=None) -> str:
    """Pisahkan baris 'Urinalisa : ...' jadi sub-bagian sendiri, meniru
    format contoh yang sudah ada di field readonly EHR (lihat
    Protokol_Interpretasi_MCU_Draft.md / contoh existing di queue.json).

    override_urinalisa (kalau ada) MENGGANTIKAN teks urinalisa dari
    protocol_engine — dipakai saat klasifikasi otomatis tidak bisa
    menentukan kategori (mis. darah tanpa albumin), supaya draft TIDAK
    diam-diam bilang 'Dalam batas normal' untuk temuan yang belum jelas."""
    baris_urinalisa = [l for l in hasil.kesimpulan_lab if l.startswith("Urinalisa :")]
    baris_lain = [l for l in hasil.kesimpulan_lab if not l.startswith("Urinalisa :")]

    bagian = []
    bagian.append("Laboratorium :\n" + ("\n".join(baris_lain) if baris_lain else "Normal"))
    if override_urinalisa:
        bagian.append("Urinalisa :\n" + override_urinalisa)
    elif baris_urinalisa:
        # BISA >1 baris sekarang (mis. leukosituria_bakteriuria + glukosuria
        # sekaligus, dikonfirmasi dr. Vidya 2026-07-31, kasus Herawati NRM
        # 306-55-27) -- gabung SEMUANYA, bukan cuma baris pertama, supaya
        # tidak ada temuan urinalisa yang diam-diam hilang dari draft.
        isi_list = [l.split(":", 1)[1].strip() for l in baris_urinalisa]
        bagian.append("Urinalisa :\n" + "\n".join(isi_list))
    return "\n\n".join(bagian)


PREFIX_POLI_PEGAWAI = "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk "
PREFIX_TATALAKSANA_MANDIRI = "Memerlukan tatalaksana terhadap "
PREFIX_SPPD_HOM = "Cek ulang dan bila perlu konsultasi ke Sp.PD Divisi HOM terkait temuan "
PREFIX_CEK_ULANG_POLI_PEGAWAI = "Cek ulang dan bila perlu konsultasi ke Dokter Umum Poli Pegawai terkait temuan "
PREFIX_CEK_ULANG_URINALISA_POLI_PEGAWAI = ("Cek ulang urinalisa (terutama bila ada keluhan) dan konsultasi "
                                            "Dokter Umum Poli Pegawai untuk ")
SARAN_PROTEINURIA_RINGAN = "Cek ulang urin, bila perlu konsultasi ke Dokter Umum Poli Pratama"
SARAN_KRISTAL = "Cek ulang urinalisa untuk kristal dalam urin"

# Saran yang diganti langsung ke spesialis (skip Dokter Umum/Poli Pratama)
# kalau pasien_dokter=True — dikonfirmasi Anda per kasus, ditambah satu-satu
# saat muncul (bukan aturan umum otomatis, karena tujuan spesialisnya
# beda-beda tergantung temuan).
GANTI_SARAN_PASIEN_DOKTER = {
    "Konsultasi Dokter Umum Klinik Pratama untuk tatalaksana abnormal EKG, "
    "bila perlu konsultasi Sp.PD Divisi KKV":
        "Lakukan konsultasi ke Dokter Spesialis Penyakit Dalam-KKV untuk tatalaksana temuan EKG",
}


def pasien_adalah_dokter(nama: str) -> bool:
    """Deteksi gelar 'dr.' di nama pasien (bukan cuma title, karena mereka
    sendiri dokter). Dipakai supaya tidak menyarankan konsultasi ke Dokter
    Umum Poli Pratama untuk pasien yang dokter sendiri (dikonfirmasi Anda,
    kasus dr. Rian Hidayatullah)."""
    return bool(re.search(r'(^|[\s,])dr\.?(\s|,|$)', nama, re.IGNORECASE))


def _gabung_saran_by_prefix(daftar_saran: list, prefix: str, prefix_pengganti: str = None) -> list:
    """Gabungkan semua saran yang berawalan persis `prefix` jadi satu baris
    dengan alasan dipisah koma. Generalisasi dari gabung_saran_poli_pegawai()
    supaya bisa dipakai utk grup destinasi lain juga (mis. Sp.PD Divisi HOM)
    — dikonfirmasi dr. Vidya, 2026-07-28, kasus Ismiati NRM 328-40-35:
    trombositosis + LED sama-sama ke Sp.PD HOM tapi ditulis 2 kalimat
    terpisah, harusnya digabung sama seperti grup Poli Pegawai."""
    alasan = []
    lainnya = []
    for s in daftar_saran:
        if s.startswith(prefix):
            alasan.append(s[len(prefix):])
        else:
            lainnya.append(s)
    if not alasan:
        return lainnya
    prefix_final = prefix_pengganti if prefix_pengganti else prefix
    gabungan = prefix_final + ", ".join(alasan)
    return [gabungan] + lainnya


def gabung_saran_poli_pegawai(daftar_saran: list, pasien_dokter: bool = False) -> list:
    """Saran yang MURNI 'konsultasi Poli Pegawai untuk X' (tanpa tindakan
    lain) digabung jadi satu baris dengan alasan dipisah koma, mis.
    'Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk hipertensi
    grade II, peningkatan enzim fungsi hati, hiperurisemia' — dikonfirmasi
    Anda, karena tujuannya sama saja. Saran majemuk (mis. 'Cek ulang X +
    konsultasi...') TIDAK digabung, tetap baris terpisah.

    Kalau pasien_dokter=True, prefix diganti 'Memerlukan tatalaksana
    terhadap X' — tidak masuk akal menyuruh dokter konsultasi ke Dokter
    Umum Poli Pratama untuk temuan sendiri (dikonfirmasi Anda)."""
    prefix_final = PREFIX_TATALAKSANA_MANDIRI if pasien_dokter else PREFIX_POLI_PEGAWAI
    return _gabung_saran_by_prefix(daftar_saran, PREFIX_POLI_PEGAWAI, prefix_final)


def gabung_saran_sppd_hom(daftar_saran: list) -> list:
    """Sama seperti gabung_saran_poli_pegawai() tapi utk saran yang menuju
    Sp.PD Divisi HOM (trombositosis, leukopenia, eritrosit, kombinasi
    Hb+eritrosit) — dikonfirmasi dr. Vidya, 2026-07-28."""
    return _gabung_saran_by_prefix(daftar_saran, PREFIX_SPPD_HOM)


SARAN_ANEMIA_BERAT = "Segera lakukan konsultasi ke Dokter Spesialis Penyakit Dalam Divisi KHOM untuk anemia berat"


def gabung_saran_anemia_berat_hom(daftar_saran: list) -> list:
    """Kalau anemia berat (SARAN_ANEMIA_BERAT, wajib/urgent) muncul BERSAMA
    saran lain yang menuju Sp.PD Divisi HOM (leukopenia/trombositosis/
    eritrosit/LED, PREFIX_SPPD_HOM), gabung jadi SATU baris -- keduanya
    sebenarnya divisi yang sama (HOM/KHOM cuma beda penulisan), jadi terasa
    dobel kalau dipisah 2 kalimat -- dikonfirmasi dr. Vidya, 2026-08-05,
    kasus Aris Miyanti NRM 204-06-63 (anemia berat + leukopenia). Tetap
    pakai kalimat 'Segera lakukan' (urgent) krn anemia berat wajib
    intervensi; naming diseragamkan jadi 'Sp.PD Divisi HOM'.

    HARUS dipanggil SETELAH gabung_saran_sppd_hom() supaya semua temuan
    HOM lain sudah jadi 1 baris sebelum ikut digabung ke sini."""
    if SARAN_ANEMIA_BERAT not in daftar_saran:
        return daftar_saran
    alasan_lain = []
    lainnya = []
    for s in daftar_saran:
        if s == SARAN_ANEMIA_BERAT:
            continue
        elif s.startswith(PREFIX_SPPD_HOM):
            alasan = s[len(PREFIX_SPPD_HOM):]
            alasan_lain.append(alasan[0].lower() + alasan[1:])
        else:
            lainnya.append(s)
    if not alasan_lain:
        return daftar_saran
    gabungan = "Segera lakukan konsultasi ke Sp.PD Divisi HOM untuk anemia berat, " + ", ".join(alasan_lain)
    return [gabungan] + lainnya


def gabung_saran_cek_ulang_poli_pegawai(daftar_saran: list) -> list:
    """Sama seperti gabung_saran_sppd_hom() tapi utk saran 'Cek ulang ...
    terkait temuan X' yang menuju Dokter Umum Poli Pegawai (mis. LED) --
    dikonfirmasi dr. Vidya, 2026-07-31 (LED dipindah dari Sp.PD Divisi HOM
    ke sini). Dipisah dari gabung_saran_poli_pegawai() krn pola kalimatnya
    beda ('Cek ulang ... terkait temuan' vs 'Konsultasi ... untuk')."""
    return _gabung_saran_by_prefix(daftar_saran, PREFIX_CEK_ULANG_POLI_PEGAWAI)


def gabung_saran_urinalisa_proteinuria(daftar_saran: list) -> list:
    """Kalau saran ISK/hematuria ('Cek ulang urinalisa ... Poli Pegawai
    untuk X') muncul BERSAMA saran proteinuria ringan sendirian ('Cek ulang
    urin, bila perlu konsultasi ke Dokter Umum Poli Pratama'), gabung jadi
    SATU baris cek ulang ke Poli Pegawai saja, alasan dipisah koma --
    dikonfirmasi dr. Vidya, 2026-08-03, kasus Martha Susanty NRM 185-10-73:
    dua baris 'cek ulang urin(alisa)' terpisah terasa dobel/redundan untuk
    dibaca walau tujuan aslinya beda (Poli Pegawai vs Poli Pratama).

    Kombinasi urinalisa lain (mis. proteinuria + silinder/glukosuria/
    albuminuria, tanpa ISK/hematuria) BELUM dicakup di sini -- baris
    proteinuria dibiarkan apa adanya kalau tidak ada saran ISK/hematuria
    yang bisa jadi tujuan gabungan (sesuai pola 'ditambah satu-satu saat
    muncul' di GANTI_SARAN_PASIEN_DOKTER)."""
    if SARAN_PROTEINURIA_RINGAN not in daftar_saran:
        return daftar_saran
    alasan_urin = None
    lainnya = []
    for s in daftar_saran:
        if s.startswith(PREFIX_CEK_ULANG_URINALISA_POLI_PEGAWAI):
            alasan_urin = s[len(PREFIX_CEK_ULANG_URINALISA_POLI_PEGAWAI):]
        elif s == SARAN_PROTEINURIA_RINGAN:
            continue  # dibuang, digabung ke baris ISK/hematuria di bawah
        else:
            lainnya.append(s)
    if alasan_urin is None:
        return daftar_saran  # proteinuria sendirian, tidak ada yang digabung
    gabungan = PREFIX_CEK_ULANG_URINALISA_POLI_PEGAWAI + f"{alasan_urin}, proteinuria"
    return [gabungan] + lainnya


def gabung_saran_kristal_proteinuria(daftar_saran: list) -> list:
    """Kalau saran Kristal dalam urin ('Cek ulang urinalisa untuk kristal
    dalam urin') muncul BERSAMA saran proteinuria ringan sendirian ('Cek
    ulang urin, bila perlu konsultasi ke Dokter Umum Poli Pratama' --
    SARAN_PROTEINURIA_RINGAN, kalau belum digabung duluan ke baris ISK/
    hematuria oleh gabung_saran_urinalisa_proteinuria), gabung jadi SATU
    baris "Cek ulang urinalisa untuk kristal dalam urin, proteinuria, bila
    perlu konsultasi ke Dokter Umum Poli Pratama" -- dikonfirmasi dr. Vidya,
    2026-08-04, kasus Hasbi NRM 429-27-73."""
    if SARAN_KRISTAL not in daftar_saran or SARAN_PROTEINURIA_RINGAN not in daftar_saran:
        return daftar_saran
    lainnya = [s for s in daftar_saran if s not in (SARAN_KRISTAL, SARAN_PROTEINURIA_RINGAN)]
    gabungan = "Cek ulang urinalisa untuk kristal dalam urin, proteinuria, bila perlu konsultasi ke Dokter Umum Poli Pratama"
    return [gabungan] + lainnya


def gabung_saran_cek_ulang_darah_urinalisa(daftar_saran: list) -> list:
    """Kalau saran 'cek ulang' darah (LED/leukositosis, PREFIX_CEK_ULANG_
    POLI_PEGAWAI) DAN saran 'cek ulang' urinalisa (ISK/hematuria/proteinuria,
    PREFIX_CEK_ULANG_URINALISA_POLI_PEGAWAI) SAMA-SAMA muncul dan SAMA-SAMA
    menuju Dokter Umum Poli Pegawai, gabung jadi SATU kalimat "Cek ulang
    darah dan urinalisa ..." -- dikonfirmasi dr. Vidya, 2026-08-04, kasus
    Zaenal Muttaqin NRM 409-58-07: leukositosis ("Cek ulang ... terkait
    temuan Leukositosis") + hematuria ("Cek ulang urinalisa ... untuk
    hematuria") dua-duanya "Cek ulang ... Poli Pegawai" terasa dobel; beliau
    juga menandai teks leukositosis sendiri ambigu ("cek ulang apa?").

    HARUS dipanggil SETELAH gabung_saran_cek_ulang_poli_pegawai() dan
    gabung_saran_urinalisa_proteinuria() supaya masing-masing sisi sudah
    jadi maksimal 1 baris sebelum digabung lagi di sini."""
    baris_darah = next((s for s in daftar_saran if s.startswith(PREFIX_CEK_ULANG_POLI_PEGAWAI)), None)
    baris_urin = next((s for s in daftar_saran if s.startswith(PREFIX_CEK_ULANG_URINALISA_POLI_PEGAWAI)), None)
    if baris_darah is None or baris_urin is None:
        return daftar_saran
    alasan_darah = baris_darah[len(PREFIX_CEK_ULANG_POLI_PEGAWAI):]
    alasan_urin = baris_urin[len(PREFIX_CEK_ULANG_URINALISA_POLI_PEGAWAI):]
    lainnya = [s for s in daftar_saran if s not in (baris_darah, baris_urin)]
    gabungan = ("Cek ulang darah dan urinalisa (terutama bila ada keluhan) dan konsultasi "
                f"Dokter Umum Poli Pegawai untuk {alasan_darah}, {alasan_urin}")
    return [gabungan] + lainnya


SARAN_TD_PREHIPERTENSI = "Periksa tekanan darah secara teratur, modifikasi gaya hidup"
SARAN_TD_PREHIPERTENSI_SINGKAT = "Periksa tekanan darah secara teratur"


def dedup_modifikasi_gaya_hidup(daftar_saran: list) -> list:
    """Kalau saran TD Pre-hipertensi ('...modifikasi gaya hidup') muncul
    BERSAMA saran lain yang sudah menyebut 'modifikasi gaya hidup' sendiri
    (mis. dari IMT overweight/obesitas/kolesterol batas tinggi), potong
    suffix duplikatnya dari saran TD -- supaya tidak disebut 2x di saran
    yang sama (dikonfirmasi dr. Vidya 2026-07-31, kasus Juwita Fitrianingsih
    NRM 418-39-26: 'Modifikasi gaya hidup, olahraga...' + 'Periksa tekanan
    darah secara teratur, modifikasi gaya hidup' dianggap berulang)."""
    if SARAN_TD_PREHIPERTENSI not in daftar_saran:
        return daftar_saran
    ada_saran_lain_sebut_gaya_hidup = any(
        "modifikasi gaya hidup" in s.lower()
        for s in daftar_saran if s != SARAN_TD_PREHIPERTENSI
    )
    if not ada_saran_lain_sebut_gaya_hidup:
        return daftar_saran
    return [SARAN_TD_PREHIPERTENSI_SINGKAT if s == SARAN_TD_PREHIPERTENSI else s
            for s in daftar_saran]


SARAN_OBESITAS_GRADE_1 = "Modifikasi gaya hidup dan diet rendah kalori"
SARAN_KOLESTEROL_ATAU_OVERWEIGHT = "Modifikasi gaya hidup, olahraga 3x/minggu @30 menit dan diet rendah lemak"
SARAN_GABUNGAN_OBESITAS_KOLESTEROL = ("Modifikasi gaya hidup, olahraga 3x/minggu @30 menit, "
                                       "diet rendah kalori dan rendah lemak")


def gabung_saran_obesitas_kolesterol_gaya_hidup(daftar_saran: list) -> list:
    """Obesitas grade 1 ('...dan diet rendah kalori') + Kolesterol batas
    tinggi/Overweight ('...olahraga ... dan diet rendah lemak') SAMA-SAMA
    'Modifikasi gaya hidup ...' tapi teksnya beda (beda dari kasus Overweight
    + Kolesterol yang sudah di-dedup exact-match karena teksnya sengaja
    disamakan). Digabung jadi SATU kalimat yang tetap menyebut kedua diet --
    dikonfirmasi dr. Vidya, 2026-08-04, kasus Erwin Budi Santoso NRM
    385-59-24: 'seluruh saran tidak boleh dobel untuk kalimatnya'."""
    if SARAN_OBESITAS_GRADE_1 not in daftar_saran or SARAN_KOLESTEROL_ATAU_OVERWEIGHT not in daftar_saran:
        return daftar_saran
    idx = daftar_saran.index(SARAN_OBESITAS_GRADE_1)
    hasil = [s for s in daftar_saran if s not in (SARAN_OBESITAS_GRADE_1, SARAN_KOLESTEROL_ATAU_OVERWEIGHT)]
    hasil.insert(idx, SARAN_GABUNGAN_OBESITAS_KOLESTEROL)
    return hasil


def format_saran(hasil, nama: str = "") -> str:
    """Baris polos tanpa bullet '-' — sesuai format existing yang sudah
    Anda pakai di EHR (lihat contoh field 'saran' di queue.json)."""
    if not hasil.saran:
        return "(tidak ada saran khusus)"
    pasien_dokter = pasien_adalah_dokter(nama)
    daftar = hasil.saran
    if pasien_dokter:
        daftar = [GANTI_SARAN_PASIEN_DOKTER.get(s, s) for s in daftar]
    daftar = gabung_saran_obesitas_kolesterol_gaya_hidup(daftar)
    daftar = dedup_modifikasi_gaya_hidup(daftar)
    daftar = gabung_saran_poli_pegawai(daftar, pasien_dokter)
    daftar = gabung_saran_sppd_hom(daftar)
    daftar = gabung_saran_anemia_berat_hom(daftar)
    daftar = gabung_saran_cek_ulang_poli_pegawai(daftar)
    daftar = gabung_saran_urinalisa_proteinuria(daftar)
    daftar = gabung_saran_kristal_proteinuria(daftar)
    daftar = gabung_saran_cek_ulang_darah_urinalisa(daftar)
    return "\n".join(daftar)


def format_hasil_ekg(hasil) -> str:
    """Selalu satu label 'EKG :' (sumbernya sudah dibersihkan dari label
    dobel di konverter_queue.py)."""
    return f"EKG :\n{hasil.kesimpulan_ekg}" if hasil.kesimpulan_ekg else ""


def format_catatan_tambahan(hasil, pasien_dokter: bool = False) -> str:
    """Field 964 'Catatan Tambahan Kategori Kesehatan/Kelaikan Kerja'.
    'Laik kerja' polos (tanpa temuan) ditulis apa adanya. 'Laik kerja
    dengan catatan' HARUS disambung dengan alasannya (dikonfirmasi Anda):
    - Kalau pasien_dokter=True -> SELALU '...melakukan tatalaksana terhadap
      temuan MCU' (tidak masuk akal bilang 'konsultasi dengan dokter' ke
      pasien yang dokter sendiri — dikonfirmasi Anda, kasus dr. Reyhan
      Eddy Yunus), TERLEPAS dari apakah saran menyebut dokter atau tidak.
    - Kalau BUKAN pasien dokter DAN ADA saran yang menyebut konsultasi ke
      dokter -> '...memerlukan konsultasi dengan dokter terkait temuan
      hasil MCU'
    - Kalau BUKAN pasien dokter DAN TIDAK ADA saran yang menyebut dokter
      sama sekali (mis. kasus Hadi Eko Purwanto: pre-hipertensi +
      kolesterol batas tinggi) -> '...melakukan tatalaksana terhadap
      hasil MCU'
    Kalau ada rekomendasi vaksin Hepatitis B di antara saran, tambahkan
    eksplisit 'dan diberikan vaksinasi Hepatitis B' di akhir (dikonfirmasi
    Anda) — supaya tidak tenggelam di daftar saran."""
    teks = hasil.kelaikan
    if "dengan catatan" in hasil.kelaikan:
        if pasien_dokter:
            alasan = "melakukan tatalaksana terhadap temuan MCU"
        else:
            ada_saran_dokter = any("dokter" in s.lower() for s in hasil.saran)
            if ada_saran_dokter:
                alasan = "memerlukan konsultasi dengan dokter terkait temuan hasil MCU"
            else:
                alasan = "melakukan tatalaksana terhadap hasil MCU"
        teks = f"{hasil.kelaikan} {alasan}"

    if "Direkomendasikan untuk diberikan vaksin Hepatitis B" in hasil.saran:
        teks = f"{teks} dan diberikan vaksinasi Hepatitis B"

    return teks


def format_kesimpulan_gabungan(hasil, teks_jasmani, teks_lab, teks_ekg) -> str:
    """Field 'Kesimpulan' (581) = ringkasan SEMUA bagian digabung, meniru
    persis struktur existing Anda: Jasmani / Laboratorium+Urinalisa / EKG /
    Rontgen thorax, dipisah baris kosong (lihat contoh existing di
    queue.json field 'kesimpulan')."""
    bagian = [teks_jasmani, teks_lab]
    if teks_ekg:
        bagian.append(teks_ekg)
    if hasil.kesimpulan_radiologi:
        bagian.append(f"Rontgen thorax :\n{hasil.kesimpulan_radiologi}")
    return "\n\n".join(b for b in bagian if b and b.strip())


def generate_draft(entry):
    """Return (nama, draft, catatan_manual, flag, flag_alasan, nip) untuk satu entri queue.json."""
    d, catatan_manual, override_urinalisa = queue_ke_datapegawai(entry)
    hasil = proses_pegawai(d)
    nip = entry.get("identitas", {}).get("nip")

    flag = hasil.flag
    ada_data_rusak = any("DATA LAB TIDAK TERBACA" in c for c in catatan_manual)
    if ada_data_rusak:
        flag = "merah"
    elif catatan_manual and flag == "hijau":
        flag = "kuning"

    teks_jasmani = format_ringkasan_jasmani(hasil)
    teks_lab = format_ringkasan_lab(hasil, override_urinalisa)
    teks_ekg = format_hasil_ekg(hasil)

    draft = {
        "ringkasan_jasmani":   teks_jasmani,
        "ringkasan_lab":       teks_lab,
        "ringkasan_radiologi": hasil.kesimpulan_radiologi,
        "hasil_ekg":           teks_ekg,
        # Audiometri & Spirometri tidak termasuk dalam paket MCU ini —
        # selalu "Tidak dilakukan" (dikonfirmasi Anda)
        "hasil_audiometri":    "Tidak dilakukan",
        "hasil_spirometri":    "Tidak dilakukan",
        # 964 "Catatan Tambahan Kategori Kesehatan/Kelaikan Kerja" = status
        # laik/tidak, disambung alasan kalau "dengan catatan" (dikonfirmasi Anda)
        "catatan_tambahan":    format_catatan_tambahan(hasil, pasien_adalah_dokter(d.nama)),
        # 581 "Kesimpulan" = gabungan semua bagian (dikonfirmasi dr. Vidya)
        "kesimpulan":          format_kesimpulan_gabungan(hasil, teks_jasmani, teks_lab, teks_ekg),
        "saran":               format_saran(hasil, d.nama),
    }
    return d.nama, draft, catatan_manual, flag, hasil.flag_alasan, nip


def cetak_draft(nama, draft, catatan_manual, flag, flag_alasan):
    print("\n" + "=" * 72)
    print(f"PASIEN: {nama}")
    print("=" * 72)

    ada_data_rusak = any("DATA LAB TIDAK TERBACA" in c for c in catatan_manual)

    if flag == "merah" and ada_data_rusak:
        print("\n🔴 FLAG MERAH — DATA LAB RUSAK/MENGGUMPAL. JANGAN dipakai untuk isi EHR.")
    elif flag == "merah":
        print("\n🔴 FLAG MERAH — data pemeriksaan belum lengkap. Teks draft di bawah SUDAH")
        print("   mencerminkan itu dengan benar (\"belum dapat ditentukan... mohon lengkapi...\") —")
        print("   ini AMAN ditulis, tapi tetap baca catatan berikut dulu.")
    elif flag == "kuning":
        print("\n🟡 FLAG KUNING — baca catatan di bawah SEBELUM menyalin ke EHR.")
    else:
        print("\n🟢 FLAG HIJAU")

    for a in flag_alasan:
        print(f"   - {a}")
    for c in catatan_manual:
        print(f"   - {c}")

    if flag == "merah" and ada_data_rusak:
        print("\n(Draft teks tetap ditampilkan di bawah untuk transparansi, TAPI")
        print(" JANGAN disalin ke EHR sampai data lab diperbaiki di Fase 1.)")

    for kunci, fid in FIELD_TARGET.items():
        print(f"\n--- {kunci} ({fid}) ---")
        print(draft[kunci])

    print("\n" + "=" * 72)


if __name__ == "__main__":
    with open("queue.json", encoding="utf-8") as f:
        antrian = json.load(f)

    print(f"Memproses {len(antrian)} pasien dari queue.json (generate teks draft, TIDAK menyentuh browser)\n")

    semua_draft = []
    for entry in antrian:
        nama, draft, catatan_manual, flag, flag_alasan, nip = generate_draft(entry)
        cetak_draft(nama, draft, catatan_manual, flag, flag_alasan)
        semua_draft.append({
            "nama": nama,
            "nip": nip,
            "flag": flag,
            "catatan_manual": catatan_manual,
            "draft": draft,
        })

    with open("draft_fase3.json", "w", encoding="utf-8") as f:
        json.dump(semua_draft, f, indent=2, ensure_ascii=False)

    print(f"\nDraft tersimpan di draft_fase3.json ({len(semua_draft)} pasien).")
    print("Review teksnya dulu. Fase 3b (tulis ke EHR) belum dibuat — menyusul")
    print("setelah Anda approve isi draft ini.")
