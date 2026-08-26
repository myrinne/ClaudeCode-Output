"""
PROTOCOL ENGINE — Interpretasi Hasil MCU
Berdasarkan Protokol_Interpretasi_MCU_Draft.md (final, dikonfirmasi dr. Vidya)

Program ini MURNI KALKULATOR TEKS. Tidak membuka browser, tidak menyentuh
website RSCM, tidak menyimpan data ke mana pun. Input manual -> output teks.
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# STRUKTUR DATA INPUT — satu pegawai
# ---------------------------------------------------------------------------

@dataclass
class DataPegawai:
    nama: str
    usia: int
    jenis_kelamin: str  # "L" atau "P"
    hamil: bool = False

    # Tanda vital
    td_sistolik: Optional[int] = None
    td_diastolik: Optional[int] = None
    imt: Optional[float] = None
    lingkar_perut: Optional[float] = None

    # Lab — isi None kalau tidak diperiksa / tidak relevan
    hb_status: Optional[str] = None  # "normal" | "anemia_ringan" | "anemia_sedang" | "anemia_berat"
    leukosit_status: Optional[str] = None  # "normal" | "leukositosis" | "leukopenia"
    trombosit_status: Optional[str] = None  # "normal" | "trombositosis"
    led_rasio_dari_rujukan_atas: Optional[float] = None  # mis. 1.5 artinya 1.5x nilai rujukan atas
    eritrosit_selisih_atas: Optional[float] = None  # eritrosit - batas_atas_rujukan; signifikan kalau >= 1.0 (dikonfirmasi dr. Vidya); rendah/negatif diabaikan
    hb_meningkat: bool = False  # flag 'H' dari EHR -- dipakai bareng eritrosit_selisih_atas (dikonfirmasi dr. Vidya)
    sgot_sgpt_status: Optional[str] = None  # "normal" | "naik"
    ggt_status: Optional[str] = None  # "normal" | "naik"
    bilirubin_direk_status: Optional[str] = None  # "normal" | "naik"
    bilirubin_indirek_status: Optional[str] = None  # "normal" | "naik"
    bilirubin_total_status: Optional[str] = None  # "normal" | "naik"
    hbsag_positif: Optional[bool] = None
    anti_hbs_diperiksa: bool = False
    anti_hbs_positif: Optional[bool] = None
    kreatinin_status: Optional[str] = None  # "normal" | "naik_egfr_turun_ureum_normal" | "naik_egfr_turun_ureum_naik" | "egfr_sangat_rendah"
    riwayat_ggk: bool = False
    kolesterol_status: Optional[str] = None  # "normal" | "batas_tinggi" | "tinggi" | "dislipidemia"
    ldl_status: Optional[str] = None  # "normal" | "tinggi" | None kalau LDL tidak diperiksa -- flag 'H' dari EHR
    hdl_status: Optional[str] = None  # "normal" | "rendah" | None kalau HDL tidak diperiksa -- flag 'L' dari EHR
    trigliserida_status: Optional[str] = None  # "normal" | "tinggi"
    gdp_status: Optional[str] = None  # "normal" | "naik" | "suspek_dm"
    gd2pp_meningkat: bool = False  # flag 'H' dari EHR utk Glukosa 2 Jam PP -- dipakai bareng gdp_status utk "Suspek DM 2" (dikonfirmasi dr. Vidya)
    hba1c_status: Optional[str] = None  # "normal" | "prediabetes" | "dm2" -- dikonfirmasi dr. Vidya, 2026-08-13
    asam_urat_status: Optional[str] = None  # "normal" | "hiperurisemia"
    urinalisa_tidak_dilakukan: bool = False
    urinalisa_status_list: list = field(default_factory=list)  # list kosong = normal; bisa >1 status sekaligus (mis. ["leukosituria_bakteriuria", "glukosuria"]) -- lihat klasifikasi_urinalisa() input_dict.py
    urinalisa_leukosituria_detail: Optional[str] = None  # cuma terisi kalau "leukosituria_bakteriuria" ada di urinalisa_status_list -- teks temuan spesifik (leukosit/nitrit/bakteri) yg BENAR-BENAR positif, sudah digabung pakai koma/'dan' (bukan '/')

    # Radiologi
    rontgen_dilakukan: bool = True
    rontgen_status: Optional[str] = None  # "normal" | "abnormal_deskripsi"
    rontgen_abnormal_deskripsi: str = ""

    # EKG
    ekg_dilakukan: bool = False  # default False; wajib True kalau usia >= 35
    ekg_status: Optional[str] = None  # "normal" | "abnormal_deskripsi"
    ekg_abnormal_deskripsi: str = ""


@dataclass
class HasilInterpretasi:
    temuan: list = field(default_factory=list)       # daftar temuan abnormal (untuk hitung jumlah)
    kesimpulan_jasmani: list = field(default_factory=list)
    kesimpulan_lab: list = field(default_factory=list)
    kesimpulan_radiologi: str = ""
    kesimpulan_ekg: str = ""
    saran: list = field(default_factory=list)
    kelaikan: str = ""
    catatan_tambahan: str = ""
    flag: str = "hijau"  # hijau | kuning | merah
    flag_alasan: list = field(default_factory=list)
    wajib_intervensi: bool = False  # kategori Langkah 3
    radiologi_belum_lengkap: bool = False  # rontgen belum dilakukan/laporan PACS belum masuk (bukan hamil)


# ---------------------------------------------------------------------------
# BAGIAN 1 — STATUS GIZI (IMT, WHO Asia-Pacific)
# ---------------------------------------------------------------------------

def interpretasi_imt(imt: float) -> tuple:
    """Return (label, kesimpulan, saran, wajib_intervensi: bool)"""
    if imt < 18.5:
        return ("Underweight", "Underweight",
                "Konsultasi ke Pelayanan Konseling Gizi dan Dietetik untuk underweight", False)
    elif imt <= 22.9:
        return ("Normoweight", "Normal", None, False)
    elif imt <= 24.9:
        # Teks disamakan persis dengan saran Kolesterol batas tinggi
        # (interpretasi_lipid) supaya dedup saran_set di proses_pegawai
        # menggabungkan otomatis kalau dua-duanya muncul bersamaan
        # (dikonfirmasi Anda, kasus Ari Darmawan).
        return ("Overweight", "Overweight",
                "Modifikasi gaya hidup, olahraga 3x/minggu @30 menit dan diet rendah lemak", False)
    elif imt <= 29.9:
        return ("Obese I", "Obesitas grade 1",
                "Modifikasi gaya hidup dan diet rendah kalori", False)
    else:
        return ("Obese II", "Obesitas grade 2",
                "Konsultasi ke Dokter Spesialis Gizi Klinik (atau Pelayanan Konseling Gizi bila tidak ada Sp.GK) "
                "untuk obesitas grade 2",
                True)  # wajib intervensi


def interpretasi_lingkar_perut(lp: float, jenis_kelamin: str) -> Optional[tuple]:
    ambang = 80 if jenis_kelamin.upper() == "P" else 90
    if lp >= ambang:
        return ("Obesitas Sentral", "Obesitas Sentral", None, False)  # boleh cuma "pertahankan gaya hidup"
    return None


# ---------------------------------------------------------------------------
# BAGIAN 2 — TEKANAN DARAH (JNC-7)
# ---------------------------------------------------------------------------

def interpretasi_td(sistolik: int, diastolik: int) -> tuple:
    if sistolik < 120 and diastolik < 80:
        return ("Normal", "Normal", None, False)
    elif sistolik < 140 and diastolik < 90:
        return ("Pre-hipertensi", "Pre-hipertensi",
                "Periksa tekanan darah secara teratur, modifikasi gaya hidup", False)
    elif sistolik < 160 and diastolik < 100:
        return ("Hipertensi stage I", "Hipertensi stage I",
                "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk hipertensi stage I", False)
    else:
        return ("Hipertensi stage II", "Hipertensi stage II",
                "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk hipertensi stage II", False)


# ---------------------------------------------------------------------------
# BAGIAN 3 — LABORATORIUM
# ---------------------------------------------------------------------------

SARAN_ANEMIA_SEDANG = ("Konsultasi Dokter Umum Poli Pegawai untuk tatalaksana anemia, terutama bila ada keluhan "
                        "(bila diperlukan konsultasi Sp.PD Divisi KHOM)")


def interpretasi_hb(status: str) -> Optional[tuple]:
    mapping = {
        "anemia_ringan": ("Anemia ringan mikrositik hipokromik", None, False),
        "anemia_sedang": ("Anemia sedang mikrositik hipokromik", SARAN_ANEMIA_SEDANG, False),
        "anemia_berat": ("Anemia berat",
                          "Segera lakukan konsultasi ke Dokter Spesialis Penyakit Dalam Divisi KHOM untuk anemia berat", True),  # wajib intervensi
    }
    if status in mapping:
        kesimpulan, saran, wajib = mapping[status]
        return (kesimpulan, kesimpulan, saran, wajib)
    return None


def interpretasi_leukosit(status: str) -> Optional[tuple]:
    if status == "leukositosis":
        # Sebelumnya teks ini TIDAK punya suffix "terkait temuan X" (beda
        # dari leukopenia di bawah) -- ambigu, "Cek ulang" apa? darah?
        # (dikonfirmasi dr. Vidya, 2026-08-04, kasus Zaenal Muttaqin NRM
        # 409-58-07). Disamakan dgn pola leukopenia/LED/eritrosit supaya
        # jelas DAN supaya bisa digabung otomatis oleh
        # gabung_saran_cek_ulang_poli_pegawai() di fase3a_generate_teks.py.
        kesimpulan = "Leukositosis"
        return (kesimpulan, kesimpulan,
                f"Cek ulang dan bila perlu konsultasi ke Dokter Umum Poli Pegawai terkait temuan {kesimpulan}", False)
    if status == "leukopenia":
        # Direvisi dr. Vidya, 2026-08-26: leukopenia cukup ke Dokter Umum
        # Poli Pegawai saja (bukan langsung Sp.PD Divisi HOM) -- disamakan
        # dgn pola leukositosis di atas, supaya kalau >1 temuan sama-sama
        # mengarah ke Poli Pegawai, digabung otomatis oleh
        # gabung_saran_cek_ulang_poli_pegawai() di fase3a_generate_teks.py.
        kesimpulan = "Leukopenia"
        return (kesimpulan, kesimpulan,
                f"Cek ulang dan bila perlu konsultasi ke Dokter Umum Poli Pegawai terkait temuan {kesimpulan}", False)
    return None


def interpretasi_trombosit(status: str) -> Optional[tuple]:
    if status == "trombositosis":
        # Wording disamakan dgn pola LED/eritrosit -- lihat catatan di
        # interpretasi_leukosit() di atas (dikonfirmasi dr. Vidya, 2026-07-28).
        kesimpulan = "Trombositosis"
        return (kesimpulan, kesimpulan,
                f"Cek ulang dan bila perlu konsultasi ke Sp.PD Divisi HOM terkait temuan {kesimpulan}", False)
    return None


def interpretasi_led(rasio: float) -> Optional[tuple]:
    if rasio is None or rasio < 2.0:
        return None  # diabaikan
    # Format saran "Cek ulang dan bila perlu konsultasi ... terkait temuan X"
    # dikonfirmasi dr. Vidya, 2026-07-24 (sama pola dgn eritrosit di bawah).
    # Tujuan diganti ke Dokter Umum Poli Pegawai (bukan lagi Sp.PD Divisi
    # HOM) -- dikonfirmasi dr. Vidya, 2026-07-31: LED naik sendirian tidak
    # perlu langsung ke spesialis.
    kesimpulan = "Peningkatan Laju Endap Darah (signifikan)"
    return ("Peningkatan LED signifikan (>=2x rujukan)", kesimpulan,
            f"Cek ulang dan bila perlu konsultasi ke Dokter Umum Poli Pegawai terkait temuan {kesimpulan}", False)


def interpretasi_eritrosit_darah(selisih_dari_rujukan_atas: float, hb_meningkat: bool = False) -> Optional[tuple]:
    """Eritrosit (RBC darah) TINGGI, naik >=1.0 di atas batas atas rujukan
    (dikonfirmasi dr. Vidya, 2026-07-24, mis. rujukan atas 4.80 -> signifikan
    kalau hasil >= 5.80). Eritrosit RENDAH (selisih negatif) TIDAK dianggap
    masalah -- caller (proses_pegawai) hanya memanggil ini kalau selisih
    sudah dihitung, dan None/negatif otomatis lolos di bawah ini.

    Kalau Hb JUGA meningkat bersamaan (hb_meningkat=True, dikonfirmasi dr.
    Vidya, 2026-07-24, kasus Rangga Surya NRM 367-80-01: Hb 17.6/H +
    Eritrosit 6.61/H) -> kesimpulan HARUS menyebut peningkatan Hb-nya
    secara eksplisit. Wording saran diselaraskan dgn pola "...terkait
    temuan X" yang sama dipakai eritrosit sendirian/LED/trombositosis/
    leukopenia (direvisi 2026-07-28 dari versi awal yang sengaja beda
    tanpa 'terkait temuan' -- supaya kalau >1 temuan sama-sama ke Sp.PD
    HOM, semuanya ke-merge jadi satu kalimat oleh gabung_saran_sppd_hom())."""
    if selisih_dari_rujukan_atas is None or selisih_dari_rujukan_atas < 1.0:
        return None  # diabaikan (termasuk kalau rendah/normal)
    if hb_meningkat:
        kesimpulan = "Peningkatan Hemoglobin dan Eritrosit"
        return (kesimpulan, kesimpulan,
                f"Cek ulang dan bila perlu konsultasi ke Sp.PD Divisi HOM terkait temuan {kesimpulan}", False)
    kesimpulan = "Peningkatan Eritrosit"
    return ("Peningkatan Eritrosit signifikan (>=1.0 di atas rujukan atas)", kesimpulan,
            f"Cek ulang dan bila perlu konsultasi ke Sp.PD Divisi HOM terkait temuan {kesimpulan}", False)


def interpretasi_hepar(sgot_sgpt: str, ggt: str, bilirubin_direk: str = None,
                        bilirubin_indirek: str = None, bilirubin_total: str = None) -> list:
    """
    sgot_sgpt dua tingkat (dikonfirmasi Anda):
    - "naik_ringan" (>5 poin di atas rujukan, belum 2x lipat) -> "Peningkatan
      enzim fungsi hati", saran Konsultasi Poli Pegawai
    - "naik_suspek" (>=2x lipat rujukan) -> "Suspek gangguan fungsi hati",
      saran Konsultasi Sp.PD-KGEH untuk tatalaksana

    Bilirubin: SEMUA fraksi yang naik (Direk/Indirek/Total) digabung jadi
    SATU temuan "Peningkatan Bilirubin X, Y, Z" -- hanya menyebut fraksi
    yang BENAR-BENAR naik, urutan tetap Direk/Indirek/Total (dikonfirmasi
    dr. Vidya, 2026-08-14, kasus NRM 350-70-58: sebelumnya cuma Direk yang
    dicek, Indirek & Total yang sama-sama naik jatuh ke catch-all "belum
    ada aturan interpretasinya"). Saran generik "...untuk peningkatan
    Bilirubin" (TANPA sebut fraksi lagi -- sudah disebut di kesimpulan).
    """
    hasil = []
    if sgot_sgpt == "naik_ringan":
        hasil.append(("Peningkatan enzim fungsi hati", "Peningkatan enzim fungsi hati",
                       "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk peningkatan enzim fungsi hati", False))
    elif sgot_sgpt == "naik_suspek":
        hasil.append(("Suspek gangguan fungsi hati", "Suspek gangguan fungsi hati",
                       "Konsultasi ke Sp.PD-KGEH untuk tatalaksana gangguan fungsi hati", False))
    if ggt == "naik":
        hasil.append(("Gamma GT/Fosfatase Alkali naik", "Sumbatan saluran empedu",
                       "Konsultasi Poli Pegawai (ringan) atau Sp.PD-KGEH (bila gangguan fungsi hati sudah jelas) "
                       "untuk peningkatan Gamma GT/Fosfatase Alkali", False))
    fraksi_naik = []
    if bilirubin_direk == "naik":
        fraksi_naik.append("Direk")
    if bilirubin_indirek == "naik":
        fraksi_naik.append("Indirek")
    if bilirubin_total == "naik":
        fraksi_naik.append("Total")
    if fraksi_naik:
        label = f"Peningkatan Bilirubin {', '.join(fraksi_naik)}"
        hasil.append((label, label,
                       "Bila perlu konsultasi ke Dokter Spesialis Penyakit Dalam Divisi Gastro-Hepatologi "
                       "untuk peningkatan Bilirubin", False))
    return hasil


def interpretasi_hepatitis_b(hbsag_positif: Optional[bool], anti_hbs_diperiksa: bool,
                               anti_hbs_positif: Optional[bool]) -> tuple:
    """Return (kesimpulan, saran, wajib_intervensi)"""
    if not anti_hbs_diperiksa:
        # Dikonfirmasi (revisi): TIDAK dianggap kekurangan data (mis. paket
        # MCU pegawai ybs memang tidak mencakup Anti-HBs). Kesimpulan = "-"
        # (TIDAK ditulis apa pun ke ringkasan lab) DAN TIDAK LAGI memaksa
        # "Laik kerja dengan catatan" sendirian — kelaikan murni ditentukan
        # dari jumlah temuan lain (revisi dari aturan awal setelah kasus Reza
        # Zada Maulana: Anti-HBs tidak diperiksa saja tidak cukup alasan).
        return (None, None, False)

    if hbsag_positif and anti_hbs_positif:
        return ("Riwayat terpapar virus Hepatitis B dan telah memiliki kekebalan", None, False)
    if hbsag_positif and not anti_hbs_positif:
        return ("Riwayat terpapar virus Hepatitis B dan belum memiliki kekebalan", "Konsultasi lebih lanjut terkait status Hepatitis B", True)
    if not hbsag_positif and anti_hbs_positif:
        return ("Belum pernah terpapar dan telah memiliki kekebalan terhadap virus Hepatitis B", None, False)
    # not hbsag_positif and not anti_hbs_positif
    return ("Belum pernah terpapar dan belum memiliki kekebalan terhadap virus Hepatitis B",
            "Direkomendasikan untuk diberikan vaksin Hepatitis B", True)


def interpretasi_ginjal(status: str, riwayat_ggk: bool) -> Optional[tuple]:
    if riwayat_ggk:
        return ("Riwayat GGK", "Riwayat gagal ginjal kronik",
                "Lakukan konsultasi RUTIN ke Sp.PD Divisi KGH untuk tatalaksana gagal ginjal dan hipertensi", True)
    if status == "egfr_sangat_rendah":
        # eGFR <75% batas bawah rujukan -- dikonfirmasi dr. Vidya, 2026-08-14:
        # curiga pasien sudah dalam kontrol rutin Sp.PD-KGH (mungkin sudah
        # hemodialisa), jadi wording "rutin" (bukan "cek ulang"/"suspek" spt
        # tier lain di bawah) dan flag MERAH -- lihat proses_pegawai() utk
        # flag_alasan & suppression saran anemia terkait. Kesimpulan
        # ditulis singkat ("Gangguan fungsi ginjal" saja, tanpa spekulasi
        # eGFR/Sp.PD-KGH/hemodialisa) -- dikonfirmasi dr. Vidya, 2026-08-17,
        # spekulasi itu cukup di flag_alasan internal untuk reviewer, bukan
        # ditulis ke field EHR pasien.
        return ("Gangguan fungsi ginjal",
                "Gangguan fungsi ginjal",
                "Konsultasi rutin ke Sp.PD-KGH terkait temuan gangguan fungsi ginjal", True)
    if status == "naik_ringan":
        # Kreatinin naik sendirian, eGFR masih normal (dikonfirmasi dr.
        # Vidya, 2026-08-03, kasus Hendi Muslim NRM 418-38-36) -- tidak
        # disebut "suspek gangguan fungsi ginjal" (itu butuh eGFR ikut
        # turun, lihat kategori di bawah), cukup cek ulang.
        return ("Peningkatan kreatinin", "Peningkatan kreatinin",
                "Cek ulang kreatinin dan konsultasi Dokter Umum Poli Pegawai bila perlu terkait "
                "peningkatan kreatinin", False)
    if status == "naik_egfr_turun_ureum_normal":
        return ("Peningkatan kreatinin", "Peningkatan kreatinin (suspek gangguan fungsi ginjal)",
                "Cek ulang kreatinin dan konsultasi Dokter Umum Poli Pegawai (bila perlu Sp.PD Divisi Ginjal Hipertensi) "
                "untuk peningkatan kreatinin (suspek gangguan fungsi ginjal)", False)
    if status == "naik_egfr_turun_ureum_naik":
        return ("Suspek gangguan fungsi ginjal", "Suspek gangguan fungsi ginjal",
                "Konsultasi Sp.PD-KGH untuk suspek gangguan fungsi ginjal", False)
    return None


def interpretasi_lipid(kolesterol: str, trigliserida: str,
                        ldl_status: Optional[str] = None, hdl_status: Optional[str] = None) -> list:
    """
    kolesterol total tinggi DAN (LDL tinggi ATAU HDL rendah) -> "Dislipidemia".
    Kolesterol total tinggi SENDIRIAN (LDL/HDL normal atau tidak diperiksa)
    -> "Hiperkolesterolemia" (dikonfirmasi Anda — revisi setelah kasus Avita
    Ziendy Meitasari).

    LDL tinggi / HDL rendah TANPA kolesterol total tinggi (mis. cuma
    batas_tinggi, atau kolesterol total normal) -> temuan sendiri
    "Peningkatan LDL" / "Penurunan HDL", TIDAK ikut jadi Dislipidemia --
    dikonfirmasi dr. Vidya, 2026-08-13 (kasus Utri Heryani NRM 410-26-87:
    LDL 164 (H), HDL 62.30 (L) belum ada aturan interpretasinya).
    """
    hasil = []
    ldl_tinggi = ldl_status == "tinggi"
    hdl_rendah = hdl_status == "rendah"
    kolesterol_tinggi = kolesterol in ("tinggi", "dislipidemia")
    if kolesterol == "batas_tinggi":
        hasil.append(("Kolesterol batas tinggi", "Kolesterol batas tinggi",
                       "Modifikasi gaya hidup, olahraga 3x/minggu @30 menit dan diet rendah lemak", False))
    elif kolesterol_tinggi:
        # Teks tujuan disamakan dengan grup "Konsultasi ke Dokter Umum Poli
        # Pegawai/Klinik Pratama untuk X" supaya digabung otomatis oleh
        # gabung_saran_poli_pegawai() di fase3a_generate_teks.py (dikonfirmasi
        # Anda, kasus dr. Rian Hidayatullah — sebelumnya "Kontrol ke Dokter
        # Umum Poli Pratama" tidak ke-dedup karena beda kata & tujuan).
        if ldl_tinggi or hdl_rendah:
            hasil.append(("Dislipidemia", "Dislipidemia",
                           "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk dislipidemia", False))
        else:
            hasil.append(("Hiperkolesterolemia", "Hiperkolesterolemia",
                           "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk hiperkolesterolemia", False))
    if ldl_tinggi and not kolesterol_tinggi:
        hasil.append(("Peningkatan LDL", "Peningkatan LDL",
                       "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk peningkatan LDL", False))
    if hdl_rendah and not kolesterol_tinggi:
        hasil.append(("Penurunan HDL", "Penurunan HDL",
                       "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk penurunan HDL", False))
    if trigliserida == "tinggi":
        hasil.append(("Hipertrigliserida", "Hipertrigliserida",
                       "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk hipertrigliserida", False))
    return hasil


def interpretasi_gdp(status: str) -> Optional[tuple]:
    if status == "naik":
        return ("Peningkatan GDP", "Peningkatan GDP / Dugaan GDP terganggu",
                "Cek GD2PP dan konsultasi Poli Pegawai untuk GDP terganggu", False)
    if status == "suspek_dm":
        return ("Suspek DM", "Suspek DM",
                "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk suspek DM", False)
    return None


def interpretasi_hba1c(status: str) -> Optional[tuple]:
    """Batas ADA/PERKENI (dikonfirmasi dr. Vidya, 2026-08-13, kasus Tri
    Erlani NRM 347-08-97): <5.7% normal, 5.7-6.4% prediabetes, >6.4% DM
    tipe 2 -- lihat klasifikasi_hba1c() di input_dict.py."""
    if status == "prediabetes":
        return ("Prediabetes (HbA1c)", "Prediabetes berdasarkan HbA1c",
                "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk prediabetes", False)
    if status == "dm2":
        return ("Suspek DM tipe 2 (HbA1c)", "Suspek DM tipe 2 berdasarkan HbA1c",
                "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk suspek DM tipe 2", False)
    return None


def interpretasi_asam_urat(status: str) -> Optional[tuple]:
    if status == "hiperurisemia":
        return ("Hiperurisemia", "Peningkatan kadar asam urat (hiperurisemia)",
                "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama untuk hiperurisemia", False)
    return None


def interpretasi_urinalisa(status: str, leukosituria_detail: Optional[str] = None) -> Optional[tuple]:
    if status == "leukosituria_bakteriuria":
        # Teks temuan HARUS sesuai apa yg benar-benar positif (leukosit/nitrit/
        # bakteri), digabung pakai koma + 'dan' -- BUKAN '/' seolah semua
        # parameter selalu ada (dikonfirmasi dr. Vidya 2026-07-31).
        temuan = leukosituria_detail or "leukosit"
        return (f"{temuan.capitalize()} dalam urin",
                f"Terdapat {temuan} dalam urin, dugaan ISK",
                f"Cek ulang urinalisa (terutama bila ada keluhan) dan konsultasi Dokter Umum "
                f"Poli Pegawai untuk dugaan ISK", False)
    mapping = {
        "proteinuria_ringan": ("Proteinuria", "Proteinuria",
                                "Cek ulang urin, bila perlu konsultasi ke Dokter Umum Poli Pratama"),
        "albuminuria": ("Albuminuria", "Albuminuria", "Konsultasi dokter untuk albuminuria"),
        # Direvisi dr. Vidya, 2026-08-25: saran lama "Konsultasi dokter untuk
        # albuminuria dan hematuria" diganti pola "Cek ulang urin ... Poli
        # Pegawai" spt temuan urinalisa lain (hematuria/leukosituria dst),
        # supaya konsisten -- bukan langsung "konsultasi dokter" tanpa cek
        # ulang dulu.
        "albuminuria_hematuria": ("Albuminuria dan hematuria", "Ditemukan albumin dan darah pada urin",
                                   "Cek ulang urin dan bila perlu konsultasi Dokter Umum Poli Pegawai untuk temuan urinalisa"),
        # Albumin & darah SAMA-SAMA cuma trace -> saran lebih ringan (dikonfirmasi Anda)
        "albuminuria_hematuria_trace": ("Albuminuria dan hematuria (trace)", "Ditemukan albumin dan darah pada urin (trace)",
                                          "Cek ulang urinalisa, bila perlu konsultasi ke Dokter Umum Klinik Pratama"),
        "hematuria": ("Hematuria", "Ditemukan darah pada urin",
                      "Cek ulang urinalisa (terutama bila ada keluhan) dan konsultasi Dokter Umum Poli Pegawai "
                      "untuk hematuria"),
        "kristal": ("Kristal dalam urin", "Terdapat kristal dalam urin", "Cek ulang urinalisa untuk kristal dalam urin"),
        # Silinder (dikonfirmasi Anda, kasus Zati Khairunnisa Fajriany)
        "silinder": ("Silinder dalam urin", "Ditemukan silinder pada urin",
                     "Cek ulang urinalisa, bila perlu konsultasi ke Dokter Umum Klinik Pratama"),
        "silinder_albuminuria": ("Silinder dan albuminuria", "Ditemukan silinder dan albumin pada urin",
                                  "Cek ulang urinalisa, bila perlu konsultasi ke Dokter Umum Klinik Pratama"),
        "silinder_albuminuria_trace": ("Silinder dan albuminuria (trace)", "Ditemukan silinder dan albumin (trace) pada urin",
                                         "Cek ulang urinalisa, bila perlu konsultasi ke Dokter Umum Klinik Pratama"),
        # Saran GLUKOSURIA sengaja None di sini -- tergantung status GDP
        # darah (dikonfirmasi dr. Vidya, 2026-07-24), diputuskan di
        # proses_pegawai() karena fungsi ini tidak menerima info GDP.
        "glukosuria": ("Glukosuria", "Glukosuria", None),
        # Ketonuria (dikonfirmasi dr. Vidya, 2026-08-04, kasus Handayani
        # Meytri NRM 400-54-82). Saran awal "Cek ulang ... Poli Pratama"
        # DIHAPUS lagi hari yang sama -- terlalu ambigu ("cek ulang apa?"),
        # tidak menyebut keton sama sekali. Tetap masuk kesimpulan lab
        # (dicatat), tapi TANPA saran -- sama seperti pola fibrosis/
        # kalsifikasi paru (temuan dicatat, tidak perlu rujukan otomatis).
        "ketonuria": ("Ketonuria", "Ditemukan keton dalam urin", None),
        # Urobilinogenuria (dikonfirmasi dr. Vidya, 2026-08-04, kasus Ambar
        # Setiyowati NRM 350-26-11).
        "urobilinogenuria": ("Urobilinogenuria", "Ditemukan urobilinogen pada urin",
                              "Cek ulang urinalisa, bila perlu konsultasi ke Dokter Umum Poli Pratama"),
    }
    if status in mapping:
        label, kesimpulan, saran = mapping[status]
        return (label, kesimpulan, saran, False)
    return None


# ---------------------------------------------------------------------------
# RONTGEN — deteksi temuan tulang/vertebra (dikonfirmasi dr. Vidya, kasus
# Fadilatul Qoyyimah: "Skoliosis vertebra torakal ke sisi kanan")
# ---------------------------------------------------------------------------

KATA_KUNCI_TULANG = (
    "skoliosis", "vertebra", "fraktur", "spondil", "osteofit",
    "listhesis", "kompresi corpus", "wedging",
)


def ekstrak_temuan_tulang(teks_kesimpulan_radiologi: str) -> Optional[str]:
    """Cari baris temuan tulang/vertebra dari teks KESIMPULAN (bukan seluruh
    laporan -- deskripsi rontgen rutin menyebut 'tulang-tulang ... kesan
    intak' yang justru normal, jadi HARUS dicek di teks kesimpulan yang
    sudah diekstrak, bukan raw_text penuh). Return teks baris temuannya
    (dipakai di saran 'terkait temuan X', dikonfirmasi dr. Vidya) atau None
    kalau tidak ada."""
    if not teks_kesimpulan_radiologi:
        return None
    for baris in teks_kesimpulan_radiologi.split("\n"):
        b = baris.strip().lstrip("-").strip().rstrip(".")
        if not b:
            continue
        if "lateralisasi" in b.lower():
            # Dikonfirmasi dr. Vidya (2026-07-24): lateralisasi vertebra
            # torakal diabaikan -- varian posisi ringan, bukan temuan
            # struktural bermakna seperti skoliosis/fraktur.
            continue
        if any(k in b.lower() for k in KATA_KUNCI_TULANG):
            return b
    return None


# ---------------------------------------------------------------------------
# RONTGEN — struma (dikonfirmasi dr. Vidya, 2026-07-24): kalau ada temuan
# struma, saran Konsultasi Sp.PD Divisi Endokrin terkait temuan spesifiknya
# (pola sama dengan temuan tulang di atas).
# ---------------------------------------------------------------------------

KATA_KUNCI_STRUMA = ("struma",)


def ekstrak_temuan_struma(teks_kesimpulan_radiologi: str) -> Optional[str]:
    """Cari baris temuan struma dari teks KESIMPULAN (bukan raw_text penuh,
    sama alasannya dengan ekstrak_temuan_tulang). Return teks baris
    temuannya atau None kalau tidak ada."""
    if not teks_kesimpulan_radiologi:
        return None
    for baris in teks_kesimpulan_radiologi.split("\n"):
        b = baris.strip().lstrip("-").strip().rstrip(".")
        if b and any(k in b.lower() for k in KATA_KUNCI_STRUMA):
            return b
    return None


# ---------------------------------------------------------------------------
# RONTGEN — fibrosis/kalsifikasi dan/atau struma SENDIRIAN (dikonfirmasi
# dr. Vidya, 2026-07-24): kalau temuan HANYA salah satu/gabungan dari
# fibrosis/kalsifikasi/struma (tanpa temuan lain), tidak perlu saran
# konsultasi Sp.PD Divisi Respirologi -- fibrosis/kalsifikasi tidak perlu
# saran apa pun, struma tetap dapat saran Endokrin sendiri (lihat
# ekstrak_temuan_struma), tapi keduanya TIDAK perlu tambahan saran
# Respirologi yang generik.
# ---------------------------------------------------------------------------

# Fibrosis/kalsifikasi TIDAK dapat saran apa pun. Kardiomegali dan elongasi
# aorta SENDIRIAN juga diabaikan (dikonfirmasi dr. Vidya, 2026-07-24) --
# sama-sama masuk kategori "tidak perlu saran". Penebalan hilus ditambahkan
# 2026-08-13 (kasus Tri Erlani NRM 347-08-97) -- temuan jinak, tidak masuk
# akal dirujuk ke Sp. Bedah (yang bisa diapakan bedah dari penebalan hilus?).
# "aorta elongasi" (urutan kata terbalik dari "elongasi aorta") ditambahkan
# 2026-08-13 (kasus 319-05-14) -- radiolog kadang menulis urutan katanya
# terbalik, substring match "elongasi aorta" tidak menangkap variasi ini
# sehingga keliru dianggap temuan tak dikenal dan memicu rujukan Bedah.
KATA_KUNCI_FIBROSIS_KALSIFIKASI = ("fibrosis", "kalsifikasi", "calcification",
                                     "kardiomegali", "elongasi aorta", "aorta elongasi",
                                     "penebalan hilus")
KATA_KUNCI_TANPA_SARAN_GENERIK = KATA_KUNCI_FIBROSIS_KALSIFIKASI + KATA_KUNCI_STRUMA

# Temuan yang diarahkan ke Sp. Paru (Respirologi), BUKAN Sp. Bedah -- infeksi
# paru (TBC/pneumonia, dikonfirmasi dr. Vidya, 2026-08-04, kasus Ambar
# Setiyowati NRM 350-26-11: "Opasitas hingga konsolidasi ... DD/ TBC paru,
# pneumonia") dan nodul paru (dikonfirmasi dr. Vidya, 2026-08-13, kasus
# 435-84-59: "suspek nodul paru" -- workup awal nodul paru ke Sp. Paru,
# BUKAN langsung ke Bedah walau kemungkinan keganasan belum disingkirkan).
# BEDA dari saran generik Sp. Bedah (utk lesi massa/tulang/kemungkinan
# keganasan lain, lihat kasus Handayani Meytri NRM 400-54-82 di bawah).
KATA_KUNCI_ARAH_SP_PARU = ("tbc", "tb paru", "pneumonia", "nodul")

# Temuan struktural paru kronis (fibrosis + bronkiektasis/bulae/hiperinflasi,
# "DD/ proses lama") diarahkan ke Sp.PD-PMK -- dikonfirmasi dr. Vidya,
# 2026-08-13, kasus 428-45-13 ("Fibrosis dengan bronkiektasis dan multipel
# bulae ... hiperinflasi paru kanan-kiri, DD/ proses lama"). BEDA dari Sp.
# Paru (infeksi/nodul di atas) dan dari Bedah (lesi massa/tulang) -- ini pola
# penyakit paru struktural/kronis, bukan infeksi akut atau lesi butuh biopsi.
KATA_KUNCI_ARAH_PD_PMPK = ("bronkiektasis", "bulae", "hiperinflasi")


def _ada_kata_kunci_di_baris_temuan(teks_kesimpulan_radiologi: str, kata_kunci: tuple) -> bool:
    """True kalau ADA (tidak perlu SEMUA) baris temuan yang menyebut salah
    satu kata_kunci -- dipakai utk mengalihkan saran generik dari Sp. Bedah
    ke tujuan spesialis lain yang lebih sesuai berdasarkan kata kunci
    temuan."""
    baris_temuan = _baris_temuan_radiologi(teks_kesimpulan_radiologi)
    return any(any(k in b.lower() for k in kata_kunci) for b in baris_temuan)

# Baris yang dianggap BUKAN temuan sama sekali (dibuang dari perhitungan
# "hanya X" di bawah) -- normal kardiopulmoner, dan lateralisasi vertebra
# (dikonfirmasi dr. Vidya, 2026-07-24: varian posisi ringan, tidak
# bermakna). Kalau tidak dibuang di sini juga (bukan cuma di
# ekstrak_temuan_tulang), baris lateralisasi akan dianggap "temuan lain di
# luar fibrosis/struma" dan memicu saran generik Respirologi secara keliru.
# "dibandingkan" = baris pembuka perbandingan (mis. "Dibandingkan dengan
# radiografi toraks sebelumnya, saat ini:") -- bukan temuan, cuma kalimat
# pengantar. Ditambahkan 2026-08-04 supaya fase1_baca.py bisa pakai fungsi
# ini juga utk deteksi "ada baris temuan di luar tidak-tampak-kelainan"
# tanpa salah anggap baris pembuka ini sebagai temuan tak dikenal.
# "tidak membesar" = varian kalimat "jantung kesan tidak membesar" --
# secara klinis sama dengan tidak tampak kelainan jantung (kardiomegali
# negatif), cuma beda redaksi radiolog -- ditambahkan 2026-08-13 (kasus
# Hijranul Aryanto Arif NRM 486-93-31: baris ini keliru dianggap temuan tak
# dikenal dan memicu rujukan Sp. Bedah, padahal jantung normal).
# "dibanding" (bukan "dibandingkan" penuh) -- radiolog kadang salah ketik
# "Dibandingan" (huruf "k" hilang, kasus NRM 404-07-18, 2026-08-20): baris
# pembuka perbandingan itu jadi tidak ter-filter dan keliru dianggap temuan
# tak dikenal, memicu rujukan Sp. Bedah untuk kardiomegali tunggal yang
# seharusnya tidak dapat saran apa pun. Substring "dibanding" menangkap
# kedua ejaan.
KATA_KUNCI_BUKAN_TEMUAN = ("tidak tampak kelainan", "lateralisasi", "dibanding", "tidak membesar")


def _baris_temuan_radiologi(teks_kesimpulan_radiologi: str) -> list:
    if not teks_kesimpulan_radiologi:
        return []
    baris_list = [b.strip().lstrip("-").strip() for b in teks_kesimpulan_radiologi.split("\n") if b.strip()]
    return [b for b in baris_list if not any(k in b.lower() for k in KATA_KUNCI_BUKAN_TEMUAN)]


def hanya_fibrosis_kalsifikasi(teks_kesimpulan_radiologi: str) -> bool:
    """True kalau SEMUA baris temuan (selain baris normal kardiopulmoner dan
    lateralisasi, lihat KATA_KUNCI_BUKAN_TEMUAN) di kesimpulan radiologi
    HANYA menyebut fibrosis/kalsifikasi/kardiomegali/elongasi aorta --
    dipakai utk menentukan draft TIDAK dapat saran apa pun untuk temuan ini
    (beda dengan struma yang tetap dapat saran Endokrin sendiri).

    PENTING: satu baris BISA menyebut fibrosis/kalsifikasi BERSAMA temuan
    lain yang jauh lebih bermakna dalam kalimat yang sama (mis. "Opasitas
    dan fibrosis pada lapangan atas paru kanan, DD/ TB Paru, pneumonia." --
    dikonfirmasi dr. Vidya, 2026-08-04, kasus Ikhsanudin NRM 387-63-73).
    Kalau baris itu JUGA menyebut kata kunci infeksi paru/nodul/PD-PMK,
    jangan anggap baris itu "cuma fibrosis" -- itu bug yang bisa membungkam
    kecurigaan TB/pneumonia/nodul/bronkiektasis sepenuhnya (tanpa flag,
    tanpa saran sama sekali) hanya krn kata "fibrosis" kebetulan ikut
    disebut (kasus Ikhsanudin NRM 387-63-73, 2026-08-04; diperluas
    2026-08-13 kasus 428-45-13, "Fibrosis dengan bronkiektasis...")."""
    baris_temuan = _baris_temuan_radiologi(teks_kesimpulan_radiologi)
    if not baris_temuan:
        return False
    kata_kunci_pengecualian = KATA_KUNCI_ARAH_SP_PARU + KATA_KUNCI_ARAH_PD_PMPK
    return all(
        any(k in b.lower() for k in KATA_KUNCI_FIBROSIS_KALSIFIKASI)
        and not any(k in b.lower() for k in kata_kunci_pengecualian)
        for b in baris_temuan
    )


def tanpa_saran_respirologi_generik(teks_kesimpulan_radiologi: str) -> bool:
    """True kalau SEMUA baris temuan HANYA fibrosis/kalsifikasi/kardiomegali/
    elongasi aorta dan/atau struma dan/atau tulang-vertebra (gabungan) --
    dipakai utk menekan saran generik Sp. Bedah karena kategori-kategori ini
    py penanganannya sendiri (struma -> Sp.PD Endokrin, tulang/vertebra ->
    Sp. Orthopaedi, keduanya via ekstrak_temuan_struma/ekstrak_temuan_tulang
    di bawah) atau tidak perlu rujukan sama sekali (fibrosis/kalsifikasi/
    kardiomegali/elongasi). KATA_KUNCI_TULANG ditambahkan 2026-08-04 --
    sebelumnya baris tulang/vertebra SELALU dianggap "tak dikenal" di sini
    sehingga skoliosis/vertebra SENDIRIAN pun ikut memicu saran Bedah
    generik secara keliru (harusnya cuma Orthopaedi, lihat kasus Handayani
    Meytri NRM 400-54-82 di bawah untuk pola sebaliknya -- ketika tulang
    BUKAN satu-satunya temuan)."""
    baris_temuan = _baris_temuan_radiologi(teks_kesimpulan_radiologi)
    if not baris_temuan:
        return False
    kata_kunci = KATA_KUNCI_TANPA_SARAN_GENERIK + KATA_KUNCI_TULANG
    # Sama seperti hanya_fibrosis_kalsifikasi() -- baris yang JUGA menyebut
    # kata kunci infeksi paru/nodul/PD-PMK tidak boleh dianggap "aman" walau
    # kebetulan ikut menyebut fibrosis/kalsifikasi/tulang dst (kasus
    # Ikhsanudin NRM 387-63-73, 2026-08-04; diperluas 2026-08-13).
    kata_kunci_pengecualian = KATA_KUNCI_ARAH_SP_PARU + KATA_KUNCI_ARAH_PD_PMPK
    return all(
        any(k in b.lower() for k in kata_kunci) and not any(k in b.lower() for k in kata_kunci_pengecualian)
        for b in baris_temuan
    )


# ---------------------------------------------------------------------------
# MESIN UTAMA — proses satu pegawai
# ---------------------------------------------------------------------------

def proses_pegawai(d: DataPegawai) -> HasilInterpretasi:
    hasil = HasilInterpretasi()
    temuan_list = []      # (label, wajib_intervensi)
    saran_set = []        # urutan saran, tanpa duplikat besar-besaran
    data_belum_lengkap = []

    def tambah_temuan(label, saran, wajib=False):
        temuan_list.append((label, wajib))
        if saran and saran not in saran_set:
            saran_set.append(saran)

    # PENGAMAN: kalau TD/BMI/Lingkar Perut TIDAK ADA SAMA SEKALI (bukan
    # sekadar salah satu), jangan diam-diam tulis "Normal" — itu artinya
    # tanda vital belum diukur/diinput sama sekali, bukan hasil pemeriksaan
    # yang normal. Ini ditambahkan ke data_belum_lengkap di bawah.
    vital_belum_diukur = (d.imt is None and d.lingkar_perut is None
                           and d.td_sistolik is None and d.td_diastolik is None)
    if vital_belum_diukur:
        data_belum_lengkap.append("Tanda vital (TD/BMI/Lingkar Perut) belum diukur/diinput")

    # --- Status gizi ---
    # Bumil: IMT & lingkar perut TIDAK dinilai dengan kriteria biasa --
    # tulis "(hamil)" saja, bukan diklasifikasi Normal/Overweight/Obesitas
    # (dikonfirmasi dr. Vidya, lihat Protokol_Interpretasi_MCU_Draft.md
    # bagian 7 "IBU HAMIL"; celah kode ditemukan & diperbaiki 2026-08-04,
    # kasus Nisrina Ulfah NRM 405-20-12 -- sebelumnya BMI tetap diklasifikasi
    # "Obesitas grade 2" walau pasien hamil, salah dihitung sbg temuan).
    if d.hamil:
        if d.imt is not None:
            hasil.kesimpulan_jasmani.append("Kesimpulan IMT : (hamil)")
        if d.lingkar_perut is not None:
            hasil.kesimpulan_jasmani.append("Kesimpulan Lingkar Perut : (hamil)")
    else:
        if d.imt is not None:
            label, kesimpulan, saran, wajib = interpretasi_imt(d.imt)
            hasil.kesimpulan_jasmani.append(f"Kesimpulan IMT : {kesimpulan}")
            if label not in ("Normoweight",):
                tambah_temuan(label, saran, wajib)

        if d.lingkar_perut is not None:
            r = interpretasi_lingkar_perut(d.lingkar_perut, d.jenis_kelamin)
            if r:
                label, kesimpulan, saran, wajib = r
                hasil.kesimpulan_jasmani.append(f"Kesimpulan Lingkar Perut : {kesimpulan}")
                tambah_temuan(label, saran, wajib)
            else:
                hasil.kesimpulan_jasmani.append("Kesimpulan Lingkar Perut : Normal")

    # --- Tekanan darah ---
    if d.td_sistolik is not None and d.td_diastolik is not None:
        label, kesimpulan, saran, wajib = interpretasi_td(d.td_sistolik, d.td_diastolik)
        hasil.kesimpulan_jasmani.append(f"Kesimpulan Tekanan Darah : {kesimpulan}")
        if label != "Normal":
            tambah_temuan(label, saran, wajib)

    # --- Hematologi ---
    if d.hb_status:
        r = interpretasi_hb(d.hb_status)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            # Anemia ringan TIDAK dihitung sebagai temuan utk Langkah 2
            # (dikonfirmasi dr. Vidya, 2026-07-31, kasus Nenni Mawati NRM
            # 402-84-74) -- "Tidak perlu tatalaksana khusus" (tidak ada
            # saran sama sekali), beda dari temuan lain yg selalu actionable.
            # Tetap disebut di teks Kesimpulan, hanya tidak menurunkan
            # kelaikan ke "dengan catatan" kalau cuma ini + 1 temuan ringan lain.
            if d.hb_status != "anemia_ringan":
                tambah_temuan(kesimpulan, saran, wajib)

    if d.leukosit_status:
        r = interpretasi_leukosit(d.leukosit_status)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, saran, wajib)

    if d.trombosit_status:
        r = interpretasi_trombosit(d.trombosit_status)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, saran, wajib)
            hasil.flag = "kuning"
            hasil.flag_alasan.append("Trombositosis — cek konteks klinis sebelum approve")

    if d.led_rasio_dari_rujukan_atas is not None:
        r = interpretasi_led(d.led_rasio_dari_rujukan_atas)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, saran, wajib)

    if d.eritrosit_selisih_atas is not None:
        r = interpretasi_eritrosit_darah(d.eritrosit_selisih_atas, d.hb_meningkat)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, saran, wajib)

    # --- Fungsi hati ---
    for _, kesimpulan, saran, wajib in interpretasi_hepar(
            d.sgot_sgpt_status, d.ggt_status,
            d.bilirubin_direk_status, d.bilirubin_indirek_status, d.bilirubin_total_status):
        hasil.kesimpulan_lab.append(kesimpulan)
        tambah_temuan(kesimpulan, saran, wajib)

    # --- Hepatitis B ---
    kesimpulan_hbv, saran_hbv, wajib_hbv = interpretasi_hepatitis_b(
        d.hbsag_positif, d.anti_hbs_diperiksa, d.anti_hbs_positif)
    if kesimpulan_hbv:
        hasil.kesimpulan_lab.append(kesimpulan_hbv)
    if wajib_hbv or saran_hbv:
        # Anti-HBs tidak diperiksa: kesimpulan_hbv None (tidak ditulis ke
        # ringkasan lab), tapi tetap perlu label internal utk pelacakan
        # jumlah temuan & flag_alasan.
        tambah_temuan(kesimpulan_hbv or "Anti-HBs belum diperiksa", saran_hbv, wajib_hbv)

    # --- Ginjal ---
    if d.kreatinin_status or d.riwayat_ggk:
        r = interpretasi_ginjal(d.kreatinin_status, d.riwayat_ggk)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, saran, wajib)
            if d.kreatinin_status == "egfr_sangat_rendah":
                hasil.flag = "merah"
                hasil.flag_alasan.append(
                    "eGFR sangat rendah (<75% rujukan) — curiga sudah kontrol rutin Sp.PD-KGH "
                    "(mungkin hemodialisa), cek riwayat sebelum approve")
                # Anemia dianggap konsekuensi wajar gangguan ginjal (anemia
                # renal) kalau sudah dalam kontrol rutin Sp.PD-KGH -- saran
                # "Poli Pegawai" utk anemia sedang jadi redundan (dikonfirmasi
                # dr. Vidya, 2026-08-14). Anemia berat (destinasi Sp.PD-KHOM
                # urgent, bukan Poli Pegawai) SENGAJA tidak disentuh di sini.
                if SARAN_ANEMIA_SEDANG in saran_set:
                    saran_set.remove(SARAN_ANEMIA_SEDANG)

    # --- Lipid ---
    for _, kesimpulan, saran, wajib in interpretasi_lipid(d.kolesterol_status, d.trigliserida_status,
                                                            d.ldl_status, d.hdl_status):
        hasil.kesimpulan_lab.append(kesimpulan)
        tambah_temuan(kesimpulan, saran, wajib)

    # --- GDP ---
    suspek_dm2_via_gdp = False
    if d.gdp_status:
        if d.gdp_status in ("naik", "suspek_dm") and d.gd2pp_meningkat:
            # Dikonfirmasi dr. Vidya (2026-07-24, kasus Rangga Surya NRM
            # 367-80-01: GDP 123/H + GD2PP 272/H): GDP DAN GD2PP
            # sama-sama meningkat -> Suspek DM 2, saran beda dari GDP
            # sendirian.
            kesimpulan = "Suspek DM 2"
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, "Cek HbA1c, dan konsultasi Dokter Umum Poli Pegawai", False)
            suspek_dm2_via_gdp = True
        else:
            r = interpretasi_gdp(d.gdp_status)
            if r:
                _, kesimpulan, saran, wajib = r
                hasil.kesimpulan_lab.append(kesimpulan)
                tambah_temuan(kesimpulan, saran, wajib)

    # --- HbA1c ---
    if d.hba1c_status and not (d.hba1c_status == "dm2" and suspek_dm2_via_gdp):
        # Kalau GDP+GD2PP sudah sama-sama meningkat (suspek_dm2_via_gdp),
        # dan HbA1c juga dm2, jangan ditulis dobel -- "Suspek DM 2" dari GDP
        # di atas sudah mewakili temuan yang sama.
        r = interpretasi_hba1c(d.hba1c_status)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, saran, wajib)

    # --- Asam urat ---
    if d.asam_urat_status:
        r = interpretasi_asam_urat(d.asam_urat_status)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, saran, wajib)

    # --- Urinalisa ---
    # KHUSUS "tidak_dilakukan" (dikonfirmasi dr. Vidya): semua pekerja wajib
    # urinalisa, jadi kalau tidak ada data sama sekali TIDAK BOLEH ditulis
    # "Dalam batas normal" (mengada-ada). Tapi BEDA dengan rontgen/EKG yang
    # belum dilakukan -- urinalisa TIDAK masuk data_belum_lengkap (tidak
    # memblokir kelaikan kerja) dan TIDAK dihitung sebagai temuan (tidak
    # memengaruhi Laik kerja vs Laik kerja dengan catatan). Saran ditambah
    # langsung ke saran_set (bukan lewat tambah_temuan) supaya tidak ikut
    # dihitung di Langkah 2.
    if d.urinalisa_tidak_dilakukan:
        hasil.kesimpulan_lab.append("Urinalisa : Belum dilakukan")
        saran_urinalisa = "Mohon melengkapi pemeriksaan urinalisa"
        if saran_urinalisa not in saran_set:
            saran_set.append(saran_urinalisa)
    elif d.urinalisa_status_list:
        # Bisa >1 status sekaligus (mis. leukosituria_bakteriuria + glukosuria)
        # -- setiap status dapat baris "Urinalisa : ..." + saran/temuan-nya
        # sendiri, TIDAK saling menutupi (dikonfirmasi dr. Vidya 2026-07-31,
        # lihat komentar di klasifikasi_urinalisa(), input_dict.py).
        for status_urin in d.urinalisa_status_list:
            detail = d.urinalisa_leukosituria_detail if status_urin == "leukosituria_bakteriuria" else None
            r = interpretasi_urinalisa(status_urin, detail)
            if not r:
                continue
            label, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(f"Urinalisa : {kesimpulan}")
            if status_urin == "glukosuria" and d.gdp_status not in ("naik", "suspek_dm"):
                # Dikonfirmasi dr. Vidya (2026-07-24): glukosa urin SAJA
                # (tanpa GDP darah meningkat) -> saran cek ulang urin + bila
                # perlu konsul Poli Pratama. Kalau GDP darah SUDAH
                # meningkat, saran GDP sendiri (di atas) sudah cukup, tidak
                # perlu saran tambahan di sini supaya tidak duplikatif.
                saran = f"Cek ulang urin, bila perlu konsul ke Dokter Umum Poli Pratama terhadap temuan {kesimpulan}"
            tambah_temuan(kesimpulan, saran, wajib)
    else:
        hasil.kesimpulan_lab.append("Urinalisa : Dalam batas normal")

    # --- Rontgen ---
    if not d.rontgen_dilakukan:
        if d.hamil:
            hasil.kesimpulan_radiologi = "Tidak dilakukan rontgen (kehamilan)"
        else:
            # Dikonfirmasi dr. Vidya, 2026-08-14: rontgen belum dilakukan/
            # laporan PACS belum masuk TIDAK LAGI memblokir auto-approve
            # (sebelumnya masuk data_belum_lengkap -> flag merah wajib
            # approve manual). Teks tetap jujur "Belum dilakukan" (bukan
            # menebak isi laporan), kelaikan/flag murni ditentukan dari
            # temuan lain seperti biasa -- TAPI saran "Mohon melengkapi
            # pemeriksaan radiologi" tetap harus ada (mirip pola urinalisa
            # di atas: ditambah langsung ke saran_set, TIDAK lewat
            # tambah_temuan, supaya tidak ikut dihitung jumlah_temuan/wajib),
            # dan kelaikan akhir tetap harus menyebut "dengan catatan
            # melengkapi pemeriksaan radiologi" -- lihat radiologi_belum_
            # lengkap & format_catatan_tambahan() di fase3a_generate_teks.py.
            hasil.kesimpulan_radiologi = "Belum dilakukan"
            hasil.radiologi_belum_lengkap = True
            saran_radiologi = "Mohon melengkapi pemeriksaan radiologi"
            if saran_radiologi not in saran_set:
                saran_set.append(saran_radiologi)
    else:
        if d.rontgen_status == "normal":
            # Dikonfirmasi dr. Vidya (kasus Fadilatul Qoyyimah, skoliosis
            # vertebra torakal): SELURUH teks kesimpulan radiologi asli
            # (dari "[Conclusion]" sampai akhir, lihat ekstrak_kesimpulan_
            # radiologi() di konverter_queue.py) HARUS ditulis apa adanya --
            # sebelumnya kalimat di sini di-hardcode generik dan diam-diam
            # membuang temuan lain (mis. skoliosis) yang ikut disebut dalam
            # kesimpulan walau jantung/paru-nya sendiri normal.
            hasil.kesimpulan_radiologi = d.rontgen_abnormal_deskripsi or \
                "Tidak tampak kelainan radiologis pada jantung dan paru"
        bedah_generik_ditambahkan = False
        if d.rontgen_status == "abnormal_deskripsi":
            hasil.kesimpulan_radiologi = d.rontgen_abnormal_deskripsi or "Terdapat kelainan radiologis (lihat detail)"
            if hanya_fibrosis_kalsifikasi(hasil.kesimpulan_radiologi):
                # Dikonfirmasi dr. Vidya (2026-07-24): fibrosis dan/atau
                # kalsifikasi SENDIRIAN (tanpa temuan lain) tidak perlu
                # konsultasi Sp.PD Respirologi -- tetap dicatat sbg temuan
                # (masuk hitungan Langkah 2), tapi tanpa saran rujukan.
                tambah_temuan("Fibrosis/kalsifikasi paru (tanpa temuan lain)", None, False)
            elif hasil.kesimpulan_radiologi and not _baris_temuan_radiologi(hasil.kesimpulan_radiologi):
                # SEMUA baris deskripsi ternyata frasa normal-equivalent
                # (tidak tampak kelainan / jantung tidak membesar / dst) --
                # tidak ada temuan tekstual sama sekali, jadi TIDAK usah
                # dikasih rujukan spesialis generik walau "kesan" radiolog di
                # EHR sempat ditandai "ada temuan perlu review" (beda dari
                # baris kosong krn ekstraksi gagal -- itu tetap jatuh ke
                # cabang generik di bawah lewat tanpa_saran_respirologi_
                # generik() yg return False utk teks kosong). Catatan manual
                # "PERLU_CEK_MANUAL: radiologi ada temuan" (konverter_queue.py)
                # tetap ada supaya Anda tetap review kenapa kesan-nya "ada
                # temuan" padahal deskripsi normal -- dikonfirmasi dr. Vidya,
                # 2026-08-13, kasus Hijranul Aryanto Arif NRM 486-93-31.
                pass
            elif not tanpa_saran_respirologi_generik(hasil.kesimpulan_radiologi):
                # Temuan radiologi di luar kata kunci yang dikenali (bukan
                # cuma fibrosis/kalsifikasi/struma/tulang) -- dulu TIDAK
                # dikasih saran spesifik sama sekali (JANGAN menebak
                # Respirologi/KKV/Gastro-Hepatologi -- dokter yang beda-beda,
                # dikonfirmasi dr. Vidya 2026-07-31, kasus Reni Febriani NRM
                # 436-76-76). Direvisi 2026-08-04 (kasus Handayani Meytri NRM
                # 400-54-82, opasitas+limfadenopati+lesi blastik mengarah
                # kemungkinan keganasan): default saran generik utk kategori
                # ini SEKARANG "Konsultasi ke Dokter Spesialis Bedah" --
                # dikonfirmasi dr. Vidya sbg titik rujukan awal yang aman utk
                # temuan radiologi tak dikenal, BUKAN tebakan sembarang.
                # catatan_manual "PERLU_CEK_MANUAL: radiologi ada temuan"
                # (konverter_queue.py) tetap menandai perlu ditinjau dia juga.
                #
                # KECUALI kalau temuan mengarah Sp. Paru (infeksi TBC/
                # pneumonia, dikonfirmasi dr. Vidya 2026-08-04, kasus Ambar
                # Setiyowati NRM 350-26-11; atau nodul paru, dikonfirmasi
                # dr. Vidya 2026-08-13, kasus 435-84-59) -- itu diarahkan ke
                # Sp. Paru, bukan Bedah (Bedah utk lesi massa/tulang/
                # kemungkinan keganasan lain saja). ATAU kalau mengarah
                # Sp.PD-PMK (fibrosis + bronkiektasis/bulae/hiperinflasi,
                # "DD/ proses lama" -- pola penyakit paru struktural kronis,
                # dikonfirmasi dr. Vidya 2026-08-13, kasus 428-45-13).
                if _ada_kata_kunci_di_baris_temuan(hasil.kesimpulan_radiologi, KATA_KUNCI_ARAH_SP_PARU):
                    # Tidak ada Sp. Paru di RSCM -- diarahkan ke Sp.PD Divisi
                    # KP, dikonfirmasi dr. Vidya, 2026-08-20.
                    tambah_temuan("Kelainan radiologis thorax (perlu konfirmasi Anda untuk saran spesialis)",
                                  "Konsultasi ke Dokter Spesialis Penyakit Dalam Divisi KP terkait temuan rontgen thorax", False)
                    # TIDAK set bedah_generik_ditambahkan -- rujukan Paru
                    # (infeksi/nodul) tidak menggantikan/menutupi rujukan
                    # Orthopaedi kalau kebetulan ADA temuan tulang terpisah
                    # di pasien yang sama (beda dari kasus Bedah/lesi massa
                    # di bawah, yang memang sengaja saling menutupi).
                elif _ada_kata_kunci_di_baris_temuan(hasil.kesimpulan_radiologi, KATA_KUNCI_ARAH_PD_PMPK):
                    tambah_temuan("Kelainan radiologis thorax (perlu konfirmasi Anda untuk saran spesialis)",
                                  "Konsultasi ke Sp.PD-PMK terkait temuan rontgen thorax", False)
                    # TIDAK set bedah_generik_ditambahkan, alasan sama spt di atas.
                else:
                    # Default generik diganti dari Sp. Bedah ke Sp.PD Divisi
                    # KP -- dikonfirmasi dr. Vidya, 2026-08-20 (kasus NRM
                    # 404-07-18), menggantikan keputusan Sp. Bedah 2026-08-04.
                    tambah_temuan("Kelainan radiologis thorax (perlu konfirmasi Anda untuk saran spesialis)",
                                  "Konsultasi ke Dokter Spesialis Penyakit Dalam Divisi KP terkait temuan rontgen thorax", False)
                    bedah_generik_ditambahkan = True
            # else: HANYA struma (dan/atau fibrosis/kalsifikasi) tanpa temuan
            # lain -- dikonfirmasi dr. Vidya (2026-07-24): saran generik
            # Respirologi disembunyikan, struma tetap dapat saran Endokrin
            # sendiri (ditambahkan di bawah, terpisah dari status di sini).

        # Temuan tulang/vertebra pada rontgen thorax (mis. skoliosis) --
        # dikonfirmasi dr. Vidya: bisa muncul terlepas dari jantung/paru
        # normal atau tidak, jadi dicek terpisah dari status di atas. Saran
        # menyebut temuannya secara spesifik ("...terkait temuan X"), bukan
        # generik saja (dikonfirmasi dr. Vidya).
        #
        # TAPI kalau baris tulang itu SENDIRI adalah bagian dari yang memicu
        # saran generik Sp. Bedah di atas (kesimpulan radiologi punya
        # temuan tak dikenal SELAIN fibrosis/kalsifikasi/kardiomegali/
        # elongasi/struma, termasuk baris tulang itu sendiri -- baris tulang
        # TIDAK PERNAH masuk kategori "aman" itu, jadi selalu ikut memicu),
        # JANGAN tambahkan saran Orthopaedi terpisah -- Sp. Bedah sudah
        # mewakili rujukan utk temuan itu, dua rujukan utk lesi yang sama
        # membingungkan (dikonfirmasi dr. Vidya, 2026-08-04, kasus Handayani
        # Meytri NRM 400-54-82: lesi blastik costae/vertebra -- Bedah sudah
        # cukup, Orthopaedi dihapus).
        temuan_tulang = None if bedah_generik_ditambahkan else ekstrak_temuan_tulang(hasil.kesimpulan_radiologi)
        if temuan_tulang:
            tambah_temuan("Temuan tulang/vertebra pada rontgen thorax",
                          f"Bila ada keluhan, lakukan konsultasi ke Dokter Spesialis Orthopaedi "
                          f"terkait temuan {temuan_tulang}", False)

        # Temuan struma pada rontgen thorax -- dikonfirmasi dr. Vidya
        # (2026-07-24), pola sama dengan temuan tulang di atas.
        temuan_struma = ekstrak_temuan_struma(hasil.kesimpulan_radiologi)
        if temuan_struma:
            tambah_temuan("Temuan struma pada rontgen thorax",
                          f"Konsultasi Sp.PD Divisi Endokrin terkait temuan {temuan_struma}", False)

    # --- EKG ---
    if d.usia >= 35:
        if not d.ekg_dilakukan:
            hasil.kesimpulan_ekg = "Belum dilakukan"
            data_belum_lengkap.append("EKG belum dilakukan (usia >= 35 tahun)")
        elif d.ekg_status == "normal":
            # Format "Normal, <detail>" (dikonfirmasi dr. Vidya, 2026-07-24).
            # Kalau field "Kelainan yang bermakna" punya teks spesifik (mis.
            # "Sinus Bradikardi") walau tergolong Normal, teks itu HARUS
            # tetap ikut ditulis setelah "Normal," — jangan diganti generik
            # "Gambaran Normal EKG". Kalau memang tidak ada detail sama
            # sekali, cukup "Normal" saja tanpa koma menggantung.
            deskripsi = (d.ekg_abnormal_deskripsi or "").strip()
            hasil.kesimpulan_ekg = f"Normal, {deskripsi}" if deskripsi else "Normal"
        elif d.ekg_status == "abnormal_deskripsi":
            # Format "Abnormal, <temuan>" (dikonfirmasi dr. Vidya, 2026-07-24).
            deskripsi = (d.ekg_abnormal_deskripsi or "").strip()
            hasil.kesimpulan_ekg = f"Abnormal, {deskripsi}" if deskripsi else "Abnormal"
            # Langsung ke Sp.PD Divisi KKV (bukan Dokter Umum dulu) --
            # dikonfirmasi dr. Vidya, 2026-08-20.
            tambah_temuan("Abnormal EKG", "Konsultasi Sp.PD Divisi KKV untuk tatalaksana abnormal EKG", False)
    else:
        hasil.kesimpulan_ekg = "Tidak dilakukan"

    # --------------------------------------------------------------
    # LANGKAH 1 — Data belum lengkap menang atas segalanya
    # --------------------------------------------------------------
    if data_belum_lengkap:
        # Kalau saran urinalisa berdiri sendiri ("Mohon melengkapi
        # pemeriksaan urinalisa") JUGA ada bersamaan dengan data_belum_lengkap
        # (mis. rontgen/EKG), gabung jadi SATU kalimat "Mohon segera
        # lengkapi: X, Y, pemeriksaan urinalisa" -- bukan 2 kalimat "Mohon..."
        # terpisah (dikonfirmasi dr. Vidya, 2026-08-04, kasus dr. Putri
        # Maharani Tristanita M. NRM 356-94-94: "seluruh saran tidak boleh
        # dobel untuk kalimatnya"). Urinalisa TETAP tidak masuk
        # catatan_tambahan/kelaikan (tidak memblokir kelaikan kerja, aturan
        # lama tidak berubah) -- cuma teks saran-nya yang digabung.
        semua_lengkapi = list(data_belum_lengkap)
        saran_final = list(saran_set)
        saran_urinalisa_standalone = "Mohon melengkapi pemeriksaan urinalisa"
        if saran_urinalisa_standalone in saran_final:
            saran_final.remove(saran_urinalisa_standalone)
            semua_lengkapi.append("pemeriksaan urinalisa")
        # Radiologi belum lengkap SAMA polanya dengan urinalisa di atas --
        # digabung ke kalimat "Mohon segera lengkapi" yang sama, bukan jadi
        # baris "Mohon melengkapi pemeriksaan radiologi" terpisah (dikonfirmasi
        # dr. Vidya, 2026-08-14, kasus NRM 495-01-99: vital DAN radiologi
        # sama-sama belum lengkap, dua kalimat "Mohon..." terasa dobel).
        saran_radiologi_standalone = "Mohon melengkapi pemeriksaan radiologi"
        if saran_radiologi_standalone in saran_final:
            saran_final.remove(saran_radiologi_standalone)
            semua_lengkapi.append("pemeriksaan radiologi")
        hasil.kelaikan = "Saat ini belum dapat diberikan status kelaikan kerja sampai dilakukan pemeriksaan kesehatan dengan lengkap"
        hasil.catatan_tambahan = "; ".join(data_belum_lengkap)
        hasil.saran = saran_final + [f"Mohon segera lengkapi: {', '.join(semua_lengkapi)}"]
        hasil.temuan = [t[0] for t in temuan_list]
        hasil.flag = "merah"
        hasil.flag_alasan.append("Data pemeriksaan belum lengkap — TIDAK BOLEH auto-approve")
        return hasil

    # --------------------------------------------------------------
    # LANGKAH 3 checked first (override), lalu LANGKAH 2 (hitung jumlah)
    # --------------------------------------------------------------
    ada_wajib_intervensi = any(w for _, w in temuan_list)
    jumlah_temuan = len(temuan_list)

    hasil.temuan = [t[0] for t in temuan_list]
    hasil.saran = list(saran_set)

    if jumlah_temuan == 0:
        hasil.kelaikan = "Laik kerja"
        hasil.catatan_tambahan = "Pertahankan kondisi kesehatan seperti saat ini & menjalankan pola hidup bersih dan sehat"
        if not hasil.saran:
            hasil.saran = ["Pertahankan kondisi kesehatan seperti saat ini & menjalankan pola hidup bersih dan sehat"]
    elif ada_wajib_intervensi:
        hasil.kelaikan = "Laik kerja dengan catatan"
        hasil.catatan_tambahan = "Memerlukan konsultasi dengan dokter terkait temuan hasil MCU"
    elif jumlah_temuan == 1:
        hasil.kelaikan = "Laik kerja"
        hasil.catatan_tambahan = ""
    else:  # >= 2 temuan, tidak ada yang wajib intervensi tapi tetap >=2
        hasil.kelaikan = "Laik kerja dengan catatan"
        hasil.catatan_tambahan = "Memerlukan konsultasi dengan dokter terkait temuan hasil MCU"

    return hasil
