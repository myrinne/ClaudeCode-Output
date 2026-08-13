"""
INPUT_DICT — angka lab mentah -> status kategori untuk protocol_engine.py
===========================================================================

PRINSIP UTAMA: pakai "Nilai Rujukan" (dan "Catatan") yang sudah tertulis
di EHR RSCM untuk tiap hasil lab, BUKAN ambang standar buku teks yang
di-hardcode. Rujukan RSCM sudah disesuaikan metode lab & gender pasien
(mis. Hemoglobin rujukan pasien perempuan otomatis "12.0 - 15.0", beda
dengan laki-laki) — jauh lebih akurat daripada saya menebak.

🟡 SISA DUA ASUMSI YANG TIDAK BISA DIAMBIL DARI RUJUKAN (karena rujukan
cuma kasih SATU batas normal, bukan grading bertingkat) — ini masih pakai
konvensi klinis standar dan PERLU KONFIRMASI Anda sebelum dipakai untuk
pasien sungguhan:
  1. Grading anemia ringan/sedang/berat di bawah batas normal
     (pakai konvensi WHO/Kemenkes: ringan 10.0-<normal, sedang 8.0-9.9, berat <8.0)
  2. Batas GDP "naik" (prediabetes) vs "suspek_dm"
     (pakai konvensi ADA/PERKENI: suspek_dm bila >=126 mg/dL)
Selain dua itu, semua klasifikasi murni membaca rujukan yang ada di layar EHR.
"""

import re
from typing import Optional, Tuple


# ---------------------------------------------------------------------------
# PARSER RENTANG RUJUKAN — "12.0 - 15.0" / "< 25" / "> 10" / "=> 240" dll
# ---------------------------------------------------------------------------

def parse_rentang(rujukan: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    """Ubah teks rujukan EHR jadi (batas_bawah, batas_atas). None kalau tak ada."""
    if not rujukan:
        return (None, None)
    s = rujukan.strip()

    m = re.match(r'^([\d.]+)\s*-\s*([\d.]+)$', s)
    if m:
        return (float(m.group(1)), float(m.group(2)))

    m = re.match(r'^[<≤]=?\s*([\d.]+)$', s)  # "< 25", "<= 25"
    if m:
        return (None, float(m.group(1)))

    m = re.match(r'^=?[>≥]=?\s*([\d.]+)$', s)  # "> 10", ">= 10", "=> 10"
    if m:
        return (float(m.group(1)), None)

    return (None, None)


def parse_tier_kolesterol_dari_catatan(catatan: Optional[str]) -> Optional[Tuple[float, float]]:
    """
    Baca tier Borderline/High langsung dari teks catatan EHR, mis:
    'Normal : <200\\nBorderline : 200 - 239\\nHigh : => 240'
    -> (200.0, 240.0) = (batas_bawah_borderline, batas_bawah_high)
    """
    if not catatan:
        return None
    m_border = re.search(r'Borderline\s*:?\s*([\d.]+)', catatan, re.I)
    m_high = re.search(r'High\s*:?\s*=?[>≥]=?\s*([\d.]+)', catatan, re.I)
    if m_border and m_high:
        return (float(m_border.group(1)), float(m_high.group(1)))
    return None


def _kosong(nilai):
    return nilai is None


# ---------------------------------------------------------------------------
# HEMATOLOGI
# ---------------------------------------------------------------------------

def klasifikasi_hb(hb: Optional[float], rujukan: Optional[str] = None) -> Optional[str]:
    """Batas normal DIAMBIL DARI RUJUKAN EHR (sudah gender-specific).
    🟡 Grading di bawah batas normal (ringan/sedang/berat) pakai konvensi
    WHO/Kemenkes, bukan dari EHR — lihat catatan di atas file ini."""
    if _kosong(hb):
        return None
    bawah, _atas = parse_rentang(rujukan)
    if bawah is None:
        bawah = 12.0  # fallback kalau rujukan tak terbaca
    if hb >= bawah:
        return "normal"
    elif hb >= 10.0:
        return "anemia_ringan"
    elif hb >= 8.0:
        return "anemia_sedang"
    else:
        return "anemia_berat"


def klasifikasi_leukosit(leukosit: Optional[float], rujukan: Optional[str] = None) -> Optional[str]:
    if _kosong(leukosit):
        return None
    bawah, atas = parse_rentang(rujukan)
    # Satuan lab "10^3/uL" -- "kurang dari seribu" sel = kurang dari 1.0 di
    # satuan ini. Kenaikan sekecil itu diabaikan (variasi wajar), dikonfirmasi Anda.
    if atas is not None and leukosit > atas + 1.0:
        return "leukositosis"
    if bawah is not None and leukosit < bawah:
        return "leukopenia"
    return "normal"


def klasifikasi_trombosit(trombosit: Optional[float], rujukan: Optional[str] = None) -> Optional[str]:
    """protocol_engine cuma punya enum 'normal'/'trombositosis' (tidak ada
    trombositopenia) — nilai rendah tetap dilaporkan 'normal' di sini,
    sesuai struktur yang sudah ada di protocol_engine.py."""
    if _kosong(trombosit):
        return None
    _bawah, atas = parse_rentang(rujukan)
    # Satuan lab "10^3/uL" -- kenaikan <= 15 di satuan ini diabaikan (variasi
    # wajar), dikonfirmasi dr. Vidya 2026-07-31. Sama pola dgn klasifikasi_leukosit().
    if atas is not None and trombosit > atas + 15.0:
        return "trombositosis"
    return "normal"


def klasifikasi_led(led: Optional[float], rujukan: Optional[str] = None) -> Optional[float]:
    """Kembalikan RASIO led / batas_atas_rujukan (field
    led_rasio_dari_rujukan_atas di DataPegawai) — protocol_engine yang
    menentukan signifikan (>=2x) atau tidak. Batas atas MURNI dari rujukan
    EHR (sudah gender-specific), tidak ada asumsi tambahan."""
    if _kosong(led):
        return None
    _bawah, atas = parse_rentang(rujukan)
    if atas is None or atas == 0:
        return None  # rujukan tak terbaca, tak bisa hitung rasio
    return led / atas


def klasifikasi_eritrosit_darah(eritrosit: Optional[float], rujukan: Optional[str] = None) -> Optional[float]:
    """Kembalikan SELISIH eritrosit - batas_atas_rujukan (BUKAN rasio spt
    LED) -- protocol_engine yang menentukan signifikan (>=1.0) atau tidak.
    Eritrosit RENDAH (selisih negatif) sengaja TIDAK dianggap masalah
    (dikonfirmasi dr. Vidya, 2026-07-24) -- fungsi ini tetap mengembalikan
    nilainya apa adanya (termasuk negatif), interpretasi_eritrosit_darah()
    di protocol_engine.py yang mengabaikan kalau negatif/di bawah 1.0."""
    if _kosong(eritrosit):
        return None
    _bawah, atas = parse_rentang(rujukan)
    if atas is None or atas == 0:
        return None
    return eritrosit - atas


# ---------------------------------------------------------------------------
# FUNGSI HATI
# ---------------------------------------------------------------------------

def klasifikasi_sgot_sgpt(sgpt: Optional[float], sgot: Optional[float],
                           rujukan_sgpt: Optional[str] = None,
                           rujukan_sgot: Optional[str] = None) -> Optional[str]:
    """
    Dua tingkat (dikonfirmasi Anda):
    - "naik_suspek" (suspek gangguan fungsi hati): SGOT dan/atau SGPT
      naik >= 2x lipat batas atas rujukan
    - "naik_ringan" (peningkatan enzim fungsi hati): naik >5 poin di atas
      batas atas rujukan (tapi belum sampai 2x lipat)
    - Kenaikan <=5 poin di atas rujukan masih dianggap "normal" (variasi wajar)
    """
    if _kosong(sgpt) and _kosong(sgot):
        return None

    tingkat = "normal"  # normal < naik_ringan < naik_suspek
    urutan = {"normal": 0, "naik_ringan": 1, "naik_suspek": 2}

    for nilai, rujukan in ((sgpt, rujukan_sgpt), (sgot, rujukan_sgot)):
        if _kosong(nilai):
            continue
        _b, atas = parse_rentang(rujukan)
        if atas is None or atas <= 0:
            continue
        if nilai >= 2 * atas:
            tingkat_ini = "naik_suspek"
        elif nilai > atas + 5:
            tingkat_ini = "naik_ringan"
        else:
            tingkat_ini = "normal"
        if urutan[tingkat_ini] > urutan[tingkat]:
            tingkat = tingkat_ini

    return tingkat


def klasifikasi_bilirubin_direk(nilai: Optional[float], rujukan: Optional[str] = None) -> Optional[str]:
    """Batas diambil dari rujukan EHR (mis. '<= 0.20')."""
    if _kosong(nilai):
        return None
    _b, atas = parse_rentang(rujukan)
    if atas is not None and nilai > atas:
        return "naik"
    return "normal"


# ---------------------------------------------------------------------------
# GINJAL
# ---------------------------------------------------------------------------

def klasifikasi_kreatinin(kreatinin: Optional[float], egfr: Optional[float],
                           ureum: Optional[float],
                           rujukan_kreatinin: Optional[str] = None,
                           rujukan_egfr: Optional[str] = None,
                           rujukan_ureum: Optional[str] = None) -> Optional[str]:
    """Semua batas diambil dari rujukan EHR masing-masing test (kreatinin
    sudah gender-specific dari lab, eGFR & ureum ikut angka lab)."""
    if _kosong(kreatinin) and _kosong(egfr) and _kosong(ureum):
        return None

    _b1, atas_kreatinin = parse_rentang(rujukan_kreatinin)
    bawah_egfr, _a2 = parse_rentang(rujukan_egfr)
    _b3, atas_ureum = parse_rentang(rujukan_ureum)

    kreatinin_naik = (kreatinin is not None and atas_kreatinin is not None
                       and kreatinin > atas_kreatinin)
    egfr_turun = (egfr is not None and bawah_egfr is not None
                  and egfr < bawah_egfr)
    ureum_naik = (ureum is not None and atas_ureum is not None
                  and ureum > atas_ureum)

    if not kreatinin_naik and not egfr_turun:
        return "normal"
    if kreatinin_naik and egfr_turun and ureum_naik:
        return "naik_egfr_turun_ureum_naik"
    if kreatinin_naik and egfr_turun:
        return "naik_egfr_turun_ureum_normal"
    if kreatinin_naik:
        # Kreatinin naik SENDIRIAN, eGFR masih dalam rujukan (dikonfirmasi
        # dr. Vidya, 2026-08-03, kasus Hendi Muslim NRM 418-38-36: kreatinin
        # 1.23/H rujukan atas 1.17, eGFR 72.4 dalam rujukan 63-147) -- tidak
        # boleh dianggap "normal" begitu saja, tapi juga BUKAN suspek
        # gangguan ginjal (itu perlu eGFR ikut turun). Kategori ringan
        # terpisah -- lihat interpretasi_ginjal() di protocol_engine.py.
        return "naik_ringan"
    return "normal"


# ---------------------------------------------------------------------------
# PROFIL LEMAK
# ---------------------------------------------------------------------------

def klasifikasi_kolesterol(kolesterol: Optional[float], rujukan: Optional[str] = None,
                            catatan: Optional[str] = None) -> Optional[str]:
    """Utamakan tier Borderline/High dari teks CATATAN EHR (sudah lengkap
    di data RSCM). Fallback ke NCEP ATP III standar (200/240) kalau
    catatan tak terbaca."""
    if _kosong(kolesterol):
        return None
    tier = parse_tier_kolesterol_dari_catatan(catatan)
    if tier is None:
        tier = (200.0, 240.0)  # fallback NCEP ATP III
    batas_borderline, batas_high = tier
    if kolesterol < batas_borderline:
        return "normal"
    elif kolesterol < batas_high:
        return "batas_tinggi"
    return "tinggi"


def klasifikasi_trigliserida(trigliserida: Optional[float], rujukan: Optional[str] = None) -> Optional[str]:
    """🟡 Kalau rujukan EHR tersedia, pakai batas atasnya. Kalau tidak,
    fallback ke NCEP ATP III (150 mg/dL)."""
    if _kosong(trigliserida):
        return None
    _bawah, atas = parse_rentang(rujukan)
    if atas is None:
        atas = 150.0  # fallback NCEP ATP III
    return "normal" if trigliserida < atas else "tinggi"


# ---------------------------------------------------------------------------
# GULA DARAH
# ---------------------------------------------------------------------------

def klasifikasi_gdp(gdp: Optional[float], rujukan: Optional[str] = None) -> Optional[str]:
    """Batas normal diambil dari rujukan EHR (mis. '70 - 99').
    🟡 Batas suspek_dm (>=126 mg/dL) pakai konvensi ADA/PERKENI, tidak ada
    di rujukan EHR (rujukan cuma kasih 1 batas normal, bukan 2 tier)."""
    if _kosong(gdp):
        return None
    _bawah, atas = parse_rentang(rujukan)
    if atas is None:
        atas = 99.0  # fallback
    if gdp <= atas:
        return "normal"
    elif gdp < 126:
        return "naik"
    return "suspek_dm"


def klasifikasi_hba1c(hba1c: Optional[float]) -> Optional[str]:
    """Batas ADA/PERKENI (dikonfirmasi dr. Vidya, 2026-08-13, kasus Tri
    Erlani NRM 347-08-97): <5.7% normal, 5.7-6.4% prediabetes, >6.4% DM
    tipe 2. Hardcode (bukan dari rujukan EHR) -- sama seperti batas
    suspek_dm di klasifikasi_gdp(), rujukan EHR utk HbA1c juga cuma kasih
    1 batas normal, bukan 2 tier."""
    if _kosong(hba1c):
        return None
    if hba1c < 5.7:
        return "normal"
    elif hba1c <= 6.4:
        return "prediabetes"
    return "dm2"


# ---------------------------------------------------------------------------
# ASAM URAT
# ---------------------------------------------------------------------------

def klasifikasi_asam_urat(asam_urat: Optional[float], rujukan: Optional[str] = None) -> Optional[str]:
    """Batas diambil dari rujukan EHR (biasanya sudah gender-specific)."""
    if _kosong(asam_urat):
        return None
    _bawah, atas = parse_rentang(rujukan)
    if atas is None:
        atas = 7.0  # fallback umum
    return "hiperurisemia" if asam_urat > atas else "normal"


# ---------------------------------------------------------------------------
# URINALISA
# ---------------------------------------------------------------------------

def gabung_temuan_dan(items: list[str]) -> str:
    """Gabung list temuan jadi teks Indonesia dgn koma + 'dan' sebelum item
    terakhir (dikonfirmasi dr. Vidya 2026-07-31: JANGAN pakai '/' sbg
    pemisah temuan urinalisa -- pakai koma/'dan' sesuai temuan yg ada)."""
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " dan " + items[-1]


def klasifikasi_urinalisa(lab_dict: dict) -> tuple[list[str], Optional[str]]:
    """
    Baca beberapa parameter urinalisa LANGSUNG dari dict lab (flag 'H'/'L'/'*'
    dan rujukan yang sudah ditulis EHR per parameter — bukan angka hardcode),
    lalu klasifikasikan ke SATU ATAU LEBIH status komposit sesuai enum
    protocol_engine.

    Return (daftar_status, detail_leukosituria_bakteriuria). Return-nya
    LIST (bisa >1 status sekaligus) -- SEBELUMNYA fungsi ini return SATU
    status saja lewat cascade prioritas (kristal > silinder > leukosituria >
    albuminuria/hematuria > proteinuria > glukosuria), yang diam-diam
    MEMBUANG temuan lain yang sebenarnya ada (dikonfirmasi dr. Vidya
    2026-07-31, kasus Herawati NRM 306-55-27: leukosit/nitrit/bakteri
    positif -> leukosituria_bakteriuria "menang" duluan, Glukosa 4+ dan
    Albumin Trace-nya HILANG TOTAL dari kesimpulan padahal keduanya
    parameter dipstick yang independen, tidak overlap dgn temuan WBC/
    bakteri). Sekarang glukosa & albumin (kalau belum "tercakup" oleh
    kombinasi silinder/hematuria di atas) SELALU ditambahkan sbg status
    terpisah, tidak pernah di-suppress oleh temuan lain.

    `detail` cuma terisi kalau "leukosituria_bakteriuria" ada di daftar --
    teks temuan spesifik apa saja yang positif (leukosit/nitrit/bakteri),
    digabung pakai gabung_temuan_dan() bukan '/', supaya kesimpulan tidak
    menyebut temuan yang sebenarnya tidak ada.

    🟡 Satu asumsi yang PERLU KONFIRMASI (rujukan urinalisa cuma 'Negatif',
    tidak ada grading ringan/jelas seperti lab kuantitatif):
    - Albumin positif SENDIRIAN (tanpa darah) -> "proteinuria_ringan"
      (belum tentu benar untuk semua kadar 1+/2+/3+)

    Kategori lain (dikonfirmasi Anda):
    - Darah/Hb atau Eritrosit sedimen naik SENDIRIAN (tanpa albumin) -> "hematuria"
    - Albumin + darah bersamaan -> "albuminuria_hematuria"
    """
    parameter_urin = ("albumin", "darah / hb", "leukosit esterase", "nitrit",
                       "bakteria", "kristal", "leukosit", "eritrosit", "silinder")
    if not any(nama.strip().lower() in parameter_urin for nama in lab_dict):
        # Beda dengan "normal" (semua parameter diperiksa & negatif) -- ini
        # urinalisa TIDAK DIPERIKSA SAMA SEKALI. Harus dibedakan dari []
        # (dipakai utk "normal") supaya protocol_engine tidak diam-diam
        # menulis "Dalam batas normal" utk pemeriksaan yang belum dilakukan
        # (dikonfirmasi dr. Vidya -- semua pekerja wajib urinalisa).
        return ["tidak_dilakukan"], None

    def cari(nama_target):
        for nama, isi in lab_dict.items():
            if nama.strip().lower() == nama_target.lower() and isinstance(isi, dict):
                return isi.get("hasil", "").strip(), isi.get("flag", "").strip(), isi.get("rujukan", "").strip()
        return None, "", ""

    def positif(nama_target):
        hasil, flag, rujukan = cari(nama_target)
        if hasil is None:
            return False
        if flag:
            return True
        if rujukan.lower() == "negatif":
            return hasil.lower() not in ("negatif", "")
        return False

    kristal_pos = positif("Kristal")
    leukosit_esterase_pos = positif("Leukosit Esterase")
    nitrit_pos = positif("Nitrit")
    bakteria_pos = positif("Bakteria")
    _h, flag_leuko, _r = cari("Leukosit")
    leukosit_sedimen_naik = bool(flag_leuko)

    albumin_hasil, _f_alb, _r_alb = cari("Albumin")
    albumin_pos = positif("Albumin")
    darah_hasil, _f_dar, _r_dar = cari("Darah / Hb")
    darah_pos = positif("Darah / Hb")
    _h2, flag_erit, _r2 = cari("Eritrosit")
    eritrosit_sedimen_naik = bool(flag_erit)

    silinder_pos = positif("Silinder")
    glukosa_pos = positif("Glukosa")

    def trace(hasil_teks):
        return bool(hasil_teks) and "trace" in hasil_teks.lower()

    status = []
    detail_leuko = None

    # Kategori yang MASIH saling eksklusif (overlap fisik: sel darah/protein
    # yang sama) -- urutan prioritas dipertahankan persis seperti sebelumnya.
    if kristal_pos:
        status.append("kristal")
    elif silinder_pos:
        # Silinder + albumin trace bersamaan -> kategori gabungan
        # (dikonfirmasi Anda, kasus Zati Khairunnisa Fajriany). Silinder
        # sendirian (tanpa albumin) -> kategori silinder saja.
        if albumin_pos:
            status.append("silinder_albuminuria_trace" if trace(albumin_hasil) else "silinder_albuminuria")
        else:
            status.append("silinder")
    elif leukosit_esterase_pos or nitrit_pos or bakteria_pos or leukosit_sedimen_naik:
        temuan = []
        if leukosit_esterase_pos or leukosit_sedimen_naik:
            temuan.append("leukosit")
        if nitrit_pos:
            temuan.append("nitrit")
        if bakteria_pos:
            temuan.append("bakteri")
        status.append("leukosituria_bakteriuria")
        detail_leuko = gabung_temuan_dan(temuan)
    elif albumin_pos and (darah_pos or eritrosit_sedimen_naik):
        # Albumin & darah SAMA-SAMA cuma trace -> saran lebih ringan
        # (dikonfirmasi Anda, kasus Muhammad Faisal Ramadhan)
        status.append("albuminuria_hematuria_trace" if (trace(albumin_hasil) and trace(darah_hasil)) else "albuminuria_hematuria")
    elif darah_pos or eritrosit_sedimen_naik:
        status.append("hematuria")
    elif albumin_pos:
        status.append("proteinuria_ringan")

    # Albumin & Glukosa adalah parameter dipstick TERPISAH dari WBC/
    # nitrit/bakteri/darah di atas -- JANGAN pernah ke-suppress kalau
    # kebetulan ada temuan lain yang lebih "menang" duluan (dikonfirmasi
    # dr. Vidya 2026-07-31, kasus Herawati NRM 306-55-27: leukosituria_
    # bakteriuria bikin Glukosa 4+ dan Albumin Trace hilang total dari
    # kesimpulan). Kalau albumin BELUM masuk lewat kombinasi di atas
    # (silinder_albuminuria*/albuminuria_hematuria*/proteinuria_ringan),
    # tambahkan sebagai proteinuria_ringan terpisah.
    albumin_sudah_masuk = any(s in ("silinder_albuminuria", "silinder_albuminuria_trace",
                                     "albuminuria_hematuria", "albuminuria_hematuria_trace",
                                     "proteinuria_ringan") for s in status)
    if albumin_pos and not albumin_sudah_masuk:
        status.append("proteinuria_ringan")

    if glukosa_pos:
        # Dikonfirmasi dr. Vidya (2026-07-24): saran akhir glukosuria
        # tergantung status GDP darah, diputuskan di protocol_engine.py
        # (proses_pegawai), bukan di sini karena fungsi ini tidak tahu GDP.
        status.append("glukosuria")

    if positif("Keton"):
        # Parameter dipstick terpisah, sama seperti Albumin/Glukosa --
        # ditambahkan 2026-08-04, kasus Handayani Meytri NRM 400-54-82
        # (Keton 2+, flag '*', sebelumnya belum ada aturan interpretasinya
        # sama sekali). TIDAK dapat saran (dikonfirmasi dr. Vidya, direvisi
        # hari yang sama -- saran awal terlalu ambigu) -- lihat
        # interpretasi_urinalisa() di protocol_engine.py.
        status.append("ketonuria")

    if positif("Urobilinogen"):
        # Parameter dipstick terpisah juga -- ditambahkan 2026-08-04, kasus
        # Ambar Setiyowati NRM 350-26-11 (hasil 34, flag '*', rujukan
        # "Normal" bukan "Negatif" spt parameter lain, tapi positif() sudah
        # menangani via cek flag duluan). Dikonfirmasi dr. Vidya: saran cek
        # ulang urinalisa + konsultasi Dokter Umum Poli Pratama bila perlu
        # (pola sama seperti silinder/albuminuria trace) -- lihat
        # interpretasi_urinalisa() di protocol_engine.py.
        status.append("urobilinogenuria")

    return status, detail_leuko
