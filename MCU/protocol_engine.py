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
    sgot_sgpt_status: Optional[str] = None  # "normal" | "naik"
    ggt_status: Optional[str] = None  # "normal" | "naik"
    hbsag_positif: Optional[bool] = None
    anti_hbs_diperiksa: bool = False
    anti_hbs_positif: Optional[bool] = None
    kreatinin_status: Optional[str] = None  # "normal" | "naik_egfr_turun_ureum_normal" | "naik_egfr_turun_ureum_naik"
    riwayat_ggk: bool = False
    kolesterol_status: Optional[str] = None  # "normal" | "batas_tinggi" | "tinggi" | "dislipidemia"
    trigliserida_status: Optional[str] = None  # "normal" | "tinggi"
    gdp_status: Optional[str] = None  # "normal" | "naik" | "suspek_dm"
    asam_urat_status: Optional[str] = None  # "normal" | "hiperurisemia"
    urinalisa_status: Optional[str] = None  # "normal" | "leukosituria_bakteriuria" | "proteinuria_ringan" | "albuminuria" | "kristal"

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


# ---------------------------------------------------------------------------
# BAGIAN 1 — STATUS GIZI (IMT, WHO Asia-Pacific)
# ---------------------------------------------------------------------------

def interpretasi_imt(imt: float) -> tuple:
    """Return (label, kesimpulan, saran, wajib_intervensi: bool)"""
    if imt < 18.5:
        return ("Underweight", "Underweight",
                "Konsultasi ke Pelayanan Konseling Gizi dan Dietetik", False)
    elif imt <= 22.9:
        return ("Normoweight", "Normal", None, False)
    elif imt <= 24.9:
        return ("Overweight", "Overweight",
                "Modifikasi gaya hidup, olahraga 3x seminggu @ 30 menit", False)
    elif imt <= 29.9:
        return ("Obese I", "Obesitas grade 1",
                "Modifikasi gaya hidup + diet rendah kalori", False)
    else:
        return ("Obese II", "Obesitas grade 2",
                "Konsultasi ke Dokter Spesialis Gizi Klinik (atau Pelayanan Konseling Gizi bila tidak ada Sp.GK)",
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
        return ("Hipertensi grade I", "Hipertensi grade I",
                "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama", False)
    else:
        return ("Hipertensi grade II", "Hipertensi grade II",
                "Konsultasi ke Dokter Umum Poli Pegawai/Klinik Pratama", False)


# ---------------------------------------------------------------------------
# BAGIAN 3 — LABORATORIUM
# ---------------------------------------------------------------------------

def interpretasi_hb(status: str) -> Optional[tuple]:
    mapping = {
        "anemia_ringan": ("Anemia ringan mikrositik hipokromik", None, False),
        "anemia_sedang": ("Anemia sedang mikrositik hipokromik",
                           "Konsultasi Dokter Umum Poli Pegawai untuk tatalaksana anemia, terutama bila ada keluhan (bila diperlukan konsultasi Sp.PD Divisi KHOM)", False),
        "anemia_berat": ("Anemia berat",
                          "Segera lakukan konsultasi ke Dokter Spesialis Penyakit Dalam Divisi KHOM", True),  # wajib intervensi
    }
    if status in mapping:
        kesimpulan, saran, wajib = mapping[status]
        return (kesimpulan, kesimpulan, saran, wajib)
    return None


def interpretasi_leukosit(status: str) -> Optional[tuple]:
    if status == "leukositosis":
        return ("Leukositosis", "Leukositosis",
                "Cek darah ulang; bila perlu konsultasi Sp.PD Divisi HOM", False)
    if status == "leukopenia":
        return ("Leukopenia", "Leukopenia",
                "Cek darah ulang; bila perlu konsultasi Sp.PD Divisi HOM", False)
    return None


def interpretasi_trombosit(status: str) -> Optional[tuple]:
    if status == "trombositosis":
        return ("Trombositosis", "Trombositosis",
                "Cek darah ulang; bila perlu konsultasi Sp.PD Divisi HOM", False)
    return None


def interpretasi_led(rasio: float) -> Optional[tuple]:
    if rasio is None or rasio < 2.0:
        return None  # diabaikan
    return ("Peningkatan LED signifikan (>=2x rujukan)", "Peningkatan Laju Endap Darah (signifikan)",
            "Konsultasi Sp.PD Divisi HOM", False)


def interpretasi_hepar(sgot_sgpt: str, ggt: str) -> list:
    hasil = []
    if sgot_sgpt == "naik":
        hasil.append(("Peningkatan enzim fungsi hati", "Peningkatan enzim fungsi hati / suspek gangguan fungsi hati",
                       "Konsultasi Poli Pegawai (ringan) atau Sp.PD-KGEH (bila gangguan fungsi hati sudah jelas)", False))
    if ggt == "naik":
        hasil.append(("Gamma GT/Fosfatase Alkali naik", "Sumbatan saluran empedu",
                       "Konsultasi Poli Pegawai (ringan) atau Sp.PD-KGEH (bila gangguan fungsi hati sudah jelas)", False))
    return hasil


def interpretasi_hepatitis_b(hbsag_positif: Optional[bool], anti_hbs_diperiksa: bool,
                               anti_hbs_positif: Optional[bool]) -> tuple:
    """Return (kesimpulan, saran, wajib_intervensi)"""
    if not anti_hbs_diperiksa:
        # Dikonfirmasi: TIDAK dianggap kekurangan data. Langsung "laik dengan catatan"
        # HANYA jika memang belum ada info Anti-HBs sama sekali.
        return ("Anti-HBs belum diperiksa", None, True)

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
    if status == "naik_egfr_turun_ureum_normal":
        return ("Peningkatan kreatinin", "Peningkatan kreatinin (suspek gangguan fungsi ginjal)",
                "Cek ulang kreatinin + konsultasi Dokter Umum Poli Pegawai (bila perlu Sp.PD Divisi Ginjal Hipertensi)", False)
    if status == "naik_egfr_turun_ureum_naik":
        return ("Impaired kidney function", "Suspek/impaired kidney function",
                "Konsultasi Sp.PD-KGH", False)
    return None


def interpretasi_lipid(kolesterol: str, trigliserida: str) -> list:
    hasil = []
    if kolesterol == "batas_tinggi":
        hasil.append(("Kolesterol batas tinggi", "Kolesterol batas tinggi",
                       "Modifikasi gaya hidup, olahraga 3x/minggu @30 menit + diet rendah lemak", False))
    elif kolesterol in ("tinggi", "dislipidemia"):
        hasil.append(("Dislipidemia", "Dislipidemia",
                       "Kontrol ke Dokter Umum Poli Pratama untuk tatalaksana", False))
    if trigliserida == "tinggi":
        hasil.append(("Hipertrigliserida", "Hipertrigliserida",
                       "Kontrol ke Dokter Umum Poli Pratama untuk tatalaksana", False))
    return hasil


def interpretasi_gdp(status: str) -> Optional[tuple]:
    if status == "naik":
        return ("Peningkatan GDP", "Peningkatan GDP / Dugaan GDP terganggu",
                "Cek GD2PP + konsultasi Poli Pegawai", False)
    if status == "suspek_dm":
        return ("Suspek DM", "Suspek DM",
                "Konsultasi Poli Pegawai", False)
    return None


def interpretasi_asam_urat(status: str) -> Optional[tuple]:
    if status == "hiperurisemia":
        return ("Hiperurisemia", "Peningkatan kadar asam urat (hiperurisemia)",
                "Konsultasi Poli Pegawai", False)
    return None


def interpretasi_urinalisa(status: str) -> Optional[tuple]:
    mapping = {
        "leukosituria_bakteriuria": ("Urinalisa: leukosit/bakteri dalam urin",
                                      "Urinalisa: terdapat leukosit/darah/bakteri dalam urin / dugaan ISK",
                                      "Cek ulang urinalisa (terutama bila ada keluhan) + konsultasi Dokter Umum Poli Pegawai"),
        "proteinuria_ringan": ("Proteinuria", "Proteinuria", "Periksa ulang (px ulang)"),
        "albuminuria": ("Albuminuria", "Albuminuria", "Konsultasi dokter"),
        "kristal": ("Kristal dalam urin", "Terdapat kristal dalam urin", "Cek ulang urinalisa"),
    }
    if status in mapping:
        label, kesimpulan, saran = mapping[status]
        return (label, kesimpulan, saran, False)
    return None


# ---------------------------------------------------------------------------
# MESIN UTAMA — proses satu pegawai
# ---------------------------------------------------------------------------

def proses_pegawai(d: DataPegawai) -> HasilInterpretasi:
    hasil = HasilInterpretasi()
    temuan_list = []      # (label, wajib_intervensi)
    saran_set = []        # urutan saran, tanpa duplikat besar-besaran

    def tambah_temuan(label, saran, wajib=False):
        temuan_list.append((label, wajib))
        if saran and saran not in saran_set:
            saran_set.append(saran)

    # --- Status gizi ---
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

    # --- Fungsi hati ---
    for _, kesimpulan, saran, wajib in interpretasi_hepar(d.sgot_sgpt_status, d.ggt_status):
        hasil.kesimpulan_lab.append(kesimpulan)
        tambah_temuan(kesimpulan, saran, wajib)

    # --- Hepatitis B ---
    kesimpulan_hbv, saran_hbv, wajib_hbv = interpretasi_hepatitis_b(
        d.hbsag_positif, d.anti_hbs_diperiksa, d.anti_hbs_positif)
    hasil.kesimpulan_lab.append(kesimpulan_hbv)
    if wajib_hbv or saran_hbv:
        tambah_temuan(kesimpulan_hbv, saran_hbv, wajib_hbv)

    # --- Ginjal ---
    if d.kreatinin_status or d.riwayat_ggk:
        r = interpretasi_ginjal(d.kreatinin_status, d.riwayat_ggk)
        if r:
            _, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(kesimpulan)
            tambah_temuan(kesimpulan, saran, wajib)

    # --- Lipid ---
    for _, kesimpulan, saran, wajib in interpretasi_lipid(d.kolesterol_status, d.trigliserida_status):
        hasil.kesimpulan_lab.append(kesimpulan)
        tambah_temuan(kesimpulan, saran, wajib)

    # --- GDP ---
    if d.gdp_status:
        r = interpretasi_gdp(d.gdp_status)
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
    if d.urinalisa_status:
        r = interpretasi_urinalisa(d.urinalisa_status)
        if r:
            label, kesimpulan, saran, wajib = r
            hasil.kesimpulan_lab.append(f"Urinalisa : {kesimpulan}")
            tambah_temuan(kesimpulan, saran, wajib)
        else:
            hasil.kesimpulan_lab.append("Urinalisa : Dalam batas normal")
    else:
        hasil.kesimpulan_lab.append("Urinalisa : Dalam batas normal")

    # --- Rontgen ---
    data_belum_lengkap = []
    if not d.rontgen_dilakukan:
        if d.hamil:
            hasil.kesimpulan_radiologi = "Tidak dilakukan rontgen (kehamilan)"
        else:
            hasil.kesimpulan_radiologi = "Belum dilakukan"
            data_belum_lengkap.append("Rontgen thorax belum dilakukan")
    else:
        if d.rontgen_status == "normal":
            hasil.kesimpulan_radiologi = "Dibandingkan pemeriksaan sebelumnya, saat ini tidak tampak kelainan radiologis pada jantung dan paru, stqa" \
                if True else "Tidak tampak kelainan radiologis pada jantung dan paru"
        elif d.rontgen_status == "abnormal_deskripsi":
            hasil.kesimpulan_radiologi = d.rontgen_abnormal_deskripsi or "Terdapat kelainan radiologis (lihat detail)"
            tambah_temuan("Kelainan radiologis thorax", "Konsultasi Sp.PD Divisi Respirologi & Penyakit Kritis / KKV / Gastro-Hepatologi sesuai temuan", False)

    # --- EKG ---
    if d.usia >= 35:
        if not d.ekg_dilakukan:
            hasil.kesimpulan_ekg = "Belum dilakukan"
            data_belum_lengkap.append("EKG belum dilakukan (usia >= 35 tahun)")
        elif d.ekg_status == "normal":
            hasil.kesimpulan_ekg = "Gambaran Normal EKG"
        elif d.ekg_status == "abnormal_deskripsi":
            hasil.kesimpulan_ekg = d.ekg_abnormal_deskripsi or "Gambaran Abnormal EKG"
            tambah_temuan("Abnormal EKG", "Konsultasi Dokter Umum Klinik Pratama untuk tatalaksana abnormal EKG, bila perlu konsultasi Sp.PD Divisi KKV", False)
    else:
        hasil.kesimpulan_ekg = "Tidak dilakukan (tidak direkomendasikan pemeriksaan pada usia ini)"

    # --------------------------------------------------------------
    # LANGKAH 1 — Data belum lengkap menang atas segalanya
    # --------------------------------------------------------------
    if data_belum_lengkap:
        hasil.kelaikan = "Saat ini belum dapat diberikan status kelaikan kerja sampai dilakukan pemeriksaan kesehatan dengan lengkap"
        hasil.catatan_tambahan = "; ".join(data_belum_lengkap)
        hasil.saran = list(saran_set) + [f"Mohon segera lengkapi: {', '.join(data_belum_lengkap)}"]
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
