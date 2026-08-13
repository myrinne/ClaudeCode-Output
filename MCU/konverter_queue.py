"""
KONVERTER queue.json -> protokol
=================================

Menyambungkan data hasil Fase 1 (queue.json) ke mesin protokol.

Beda dengan input_dict.py: file ini membaca NAMA LAB ASLI dari EHR
("Kolesterol Total", "SGPT (ALT)", "Anti HBs", dst) dan tanda vital
berformat {"editable": "113"}, lalu mengubahnya jadi DataPegawai.

Cara pakai (uji):
    python konverter_queue.py
Akan membaca queue.json, memproses semua pasien, menampilkan hasil.
"""

import sys
import json
import re

sys.stdout.reconfigure(encoding="utf-8")

from protocol_engine import DataPegawai, proses_pegawai

# Ambil ulang fungsi klasifikasi angka mentah dari input_dict
from input_dict import (
    klasifikasi_hb, klasifikasi_leukosit, klasifikasi_trombosit,
    klasifikasi_led, klasifikasi_eritrosit_darah, klasifikasi_sgot_sgpt, klasifikasi_kreatinin,
    klasifikasi_kolesterol, klasifikasi_trigliserida, klasifikasi_gdp, klasifikasi_hba1c,
    klasifikasi_asam_urat, klasifikasi_urinalisa, klasifikasi_bilirubin_direk,
)


# ---------------------------------------------------------------------------
# Pembaca nilai — menangani format {"editable": "..", "readonly": ".."}
# ---------------------------------------------------------------------------

def ambil_nilai(field):
    """Dari {"readonly":.., "editable":..} ambil yang terisi. Editable diutamakan."""
    if field is None:
        return None
    if isinstance(field, dict):
        for kunci in ("editable", "readonly"):
            v = field.get(kunci)
            if v is not None and str(v).strip() != "":
                return str(v).strip()
        return None
    return str(field).strip() or None


def ke_angka(teks):
    """Ubah teks jadi angka. '113' -> 113, '18.82' -> 18.82, None kalau gagal."""
    if teks is None:
        return None
    teks = str(teks).strip().replace(",", ".")
    m = re.search(r'-?\d+\.?\d*', teks)
    if not m:
        return None
    angka = float(m.group())
    return int(angka) if angka == int(angka) else angka


# ---------------------------------------------------------------------------
# Pencari lab — nama EHR bisa bervariasi, jadi kita cari fleksibel
# ---------------------------------------------------------------------------

# Ambang: hasil lab yang valid selalu pendek (angka atau teks singkat).
# Kalau "hasil" panjangnya ratusan karakter, itu gumpalan teks tabel yang
# gagal ter-parse — JANGAN dipakai, tandai sebagai rusak.
BATAS_PANJANG_HASIL_VALID = 60


def hasil_valid(hasil):
    """True kalau nilai 'hasil' tampak seperti hasil lab asli, bukan gumpalan teks."""
    if hasil is None:
        return False
    teks = str(hasil).strip()
    if len(teks) > BATAS_PANJANG_HASIL_VALID:
        return False
    # Gumpalan teks tabel selalu mengandung penanda ini
    penanda_gumpalan = ["Nama Test", "Responsible Name", "Order No", "Kesimpulan BMI",
                         "Nilai Rujukan", "\n\t", "UREG", "HE-RTN"]
    for p in penanda_gumpalan:
        if p in teks:
            return False
    return True


def cari_lab(lab_dict, *kata_kunci):
    """
    Cari entri lab yang namanya mengandung SALAH SATU kata_kunci (case-insensitive).
    HANYA mengembalikan nilai yang lolos hasil_valid(). Kalau yang ketemu adalah
    gumpalan teks, kembalikan penanda khusus "__RUSAK__" agar pemanggil tahu
    data untuk parameter ini tidak bisa dibaca (dan pasien di-flag merah).
    """
    ada_yang_cocok_tapi_rusak = False
    for nama, isi in lab_dict.items():
        nama_low = nama.lower()
        for kk in kata_kunci:
            if kk.lower() in nama_low:
                hasil = isi.get("hasil", "") if isinstance(isi, dict) else str(isi)
                if hasil_valid(hasil):
                    return hasil
                else:
                    ada_yang_cocok_tapi_rusak = True
    if ada_yang_cocok_tapi_rusak:
        return "__RUSAK__"
    return None


def cari_lab_angka(lab_dict, *kata_kunci):
    hasil = cari_lab(lab_dict, *kata_kunci)
    if hasil == "__RUSAK__":
        return "__RUSAK__"
    return ke_angka(hasil)


def cari_lab_rujukan(lab_dict, *kata_kunci):
    """Cari (rujukan, catatan) dari entri lab pertama yang cocok kata_kunci & valid.
    Dipakai supaya klasifikasi_* di input_dict.py membaca batas normal
    LANGSUNG dari EHR, bukan angka hardcode."""
    for nama, isi in lab_dict.items():
        nama_low = nama.lower()
        for kk in kata_kunci:
            if kk.lower() in nama_low and isinstance(isi, dict):
                hasil = isi.get("hasil", "")
                if hasil_valid(hasil):
                    return isi.get("rujukan", ""), isi.get("catatan", "")
    return None, None


def cari_lab_flag(lab_dict, *kata_kunci):
    """Return flag (H/L/*) untuk lab tertentu."""
    for nama, isi in lab_dict.items():
        nama_low = nama.lower()
        for kk in kata_kunci:
            if kk.lower() in nama_low and isinstance(isi, dict):
                return isi.get("flag", "")
    return ""


def teks_reaktif(nilai):
    """'0.34 Non-Reaktif' -> False, '> 1000 Reaktif' -> True, None kalau tak jelas."""
    if nilai is None:
        return None
    t = str(nilai).lower()
    if "non-reaktif" in t or "non reaktif" in t or "nonreaktif" in t:
        return False
    if "reaktif" in t:
        return True
    if "negatif" in t:
        return False
    if "positif" in t:
        return True
    return None


# ---------------------------------------------------------------------------
# Interpretasi Anti HBs berbasis ANGKA (bukan cuma teks reaktif)
# ---------------------------------------------------------------------------

def anti_hbs_positif_dari_nilai(lab_dict):
    """
    Anti HBs >= 10 IU/L = ada kekebalan (positif).
    Menangani '> 1000.0', '< 2.0', angka biasa.
    Return (diperiksa: bool, positif: bool|None)
    """
    for nama, isi in lab_dict.items():
        if "anti hbs" in nama.lower() or "anti-hbs" in nama.lower():
            hasil = isi.get("hasil", "") if isinstance(isi, dict) else str(isi)
            t = str(hasil).lower()
            # Coba baca reaktif dulu
            r = teks_reaktif(hasil)
            if r is not None:
                return (True, r)
            # Baca angka + tanda < / >
            angka = ke_angka(hasil)
            if angka is None:
                return (True, None)
            if "<" in t:
                return (True, angka > 10)   # '< 2.0' -> di bawah 10 -> negatif
            if ">" in t:
                return (True, angka >= 10)  # '> 1000' -> positif
            return (True, angka >= 10)
    return (False, None)


# ---------------------------------------------------------------------------
# Radiologi
# ---------------------------------------------------------------------------

def ekstrak_kesimpulan_radiologi(raw_text):
    """
    Ambil HANYA bagian Kesimpulan/[Conclusion] dari laporan radiologi mentah —
    bukan seluruh laporan (No. MRN, Teknik, Deskripsi, dst). Field EHR
    Ringkasan Radiologi cuma perlu kesimpulannya, bukan laporan lengkap.
    """
    if not raw_text:
        return raw_text
    m = re.search(r'\[?conclusion\]?\s*=*\s*\n', raw_text, re.I)
    if not m:
        return raw_text  # marker tidak ketemu — kembalikan apa adanya, jangan buang data
    sisa = raw_text[m.end():]
    idx_dokter = sisa.find("Dokter Penanggung Jawab Pasien")
    if idx_dokter != -1:
        sisa = sisa[:idx_dokter]
    return sisa.strip()


def interpretasi_radiologi(radio):
    """
    Dari dict radiologi Fase 1 -> (dilakukan, status, deskripsi).
    Menangani kesan: normal / belum_dilakukan / section_tidak_termuat / dst.
    """
    if not radio or radio == {}:
        # queue.json lama: {} kosong = tidak jelas. Anggap perlu cek manual.
        return (False, None, "", "PERLU_CEK_MANUAL: radiologi kosong di queue.json")

    kesan = radio.get("kesan", "")
    if kesan == "normal":
        # Dikonfirmasi dr. Vidya: dulu di sini mengembalikan raw_text PENUH
        # (heading, No. MRN, Teknik, Deskripsi, dst) padahal protocol_engine
        # ujung2nya tidak pernah memakainya (hardcode kalimat generik) --
        # sekarang keduanya diperbaiki bersamaan. Pakai ekstrak_kesimpulan_
        # radiologi() yang sama dengan jalur "ada_temuan_perlu_review" di
        # bawah, supaya SELURUH isi kesimpulan (termasuk temuan tulang/
        # vertebra yang bukan soal jantung-paru) ikut tertulis, bukan cuma
        # potongan pertama.
        kesimpulan = ekstrak_kesimpulan_radiologi(radio.get("raw_text", ""))
        return (True, "normal", kesimpulan, "")
    if kesan == "belum_dilakukan":
        return (False, None, "", "")
    if kesan in ("section_tidak_termuat", "kosong_perlu_cek_manual", "error"):
        return (False, None, "",
                f"PERLU_CEK_MANUAL: radiologi kesan='{kesan}' — buka section radiologi di layar & ulangi Fase 1")
    if kesan == "ada_temuan_perlu_review":
        kesimpulan = ekstrak_kesimpulan_radiologi(radio.get("raw_text", ""))
        return (True, "abnormal_deskripsi", kesimpulan,
                "PERLU_CEK_MANUAL: radiologi ada temuan — review deskripsi")
    return (False, None, "", f"PERLU_CEK_MANUAL: kesan tidak dikenal '{kesan}'")


# ---------------------------------------------------------------------------
# EKG (dari kesimpulan_existing)
# ---------------------------------------------------------------------------

def interpretasi_ekg_existing(kes_existing, ekg_asli=None):
    """
    PRIORITAS: tab 'Formulir EKG' (ekg_asli — sumber ASLI dari dokter
    penganalisa EKG) di atas field 580 'Hasil Pemeriksaan EKG'
    (kes_existing — ringkasan kita sendiri, bisa ketinggalan/masih bilang
    'Belum dilakukan' walau EKG sudah selesai dianalisa). Ditemukan lewat
    kasus dr. Reyhan Eddy Yunus: field 580 kosong/belum, tapi field 955
    sudah berisi 'OMI Anteroseptal Iskemik Anterior'.

    Klasifikasi Normal/Abnormal diambil dari radio "Kesan" (field 954) —
    OTORITATIF, BUKAN ditebak dari isi teks field 955. Teks field 955
    (kelainan_bermakna) SELALU dipakai sebagai deskripsi kalau ada, baik
    untuk kesan Normal maupun Abnormal (mis. "Normal - Sinus Bradikardi"
    tetap menampilkan teks "Sinus Bradikardi", bukan diganti generik
    "Gambaran Normal EKG" — dikonfirmasi Anda).

    Field 953 ("Keterangan lainnya") TERPISAH dari 955 -- dokter penganalisa
    EKG kadang isi salah satu saja atau dua-duanya (dikonfirmasi dr. Vidya,
    2026-08-04, kasus Yusli Revika NRM 448-96-86: "Sinus Bradikardi" ada di
    953, field 955 kosong). Kalau dua-duanya ada isi, digabung "953, lalu
    955" dipisah koma -- tidak ada yang hilang.
    """
    if ekg_asli and ekg_asli.get("tab_ditemukan") and ekg_asli.get("kesan"):
        kelainan = (ekg_asli.get("kelainan_bermakna") or "").strip()
        keterangan_lain = (ekg_asli.get("keterangan_lain") or "").strip()
        gabungan = ", ".join(x for x in (keterangan_lain, kelainan) if x)
        if ekg_asli["kesan"] == "Abnormal":
            return (True, "abnormal_deskripsi", gabungan or "Gambaran Abnormal EKG")
        return (True, "normal", gabungan)  # gabungan bisa "" -> fallback generik di protocol_engine.py

    field = kes_existing.get("hasil_ekg") if kes_existing else None
    nilai = ambil_nilai(field)
    if nilai is None or nilai == "":
        return (False, None, "")  # kosong -> belum dilakukan (nanti dicek usia)
    # Field sumber sering sudah diawali label "EKG :" sendiri — buang supaya
    # tidak dobel waktu label "EKG :" ditambahkan lagi di fase3a_generate_teks.py
    nilai = re.sub(r'^\s*EKG\s*:\s*\n?', '', nilai, flags=re.I).strip()
    t = nilai.lower()
    if "normal" in t:
        return (True, "normal", nilai)
    if "tidak dilakukan" in t or "belum" in t:
        return (False, None, "")
    return (True, "abnormal_deskripsi", nilai)


# ---------------------------------------------------------------------------
# CATCH-ALL — temuan lab yang BELUM ADA aturan interpretasinya di protokol
# (dikonfirmasi dr. Vidya, 2026-07-24: "kalau ada temuan yang belum ada di
# protokol, notifikasi saya agar bisa dibuatkan kesimpulan dan sarannya.
# jangan diabaikan"). Daftar di bawah HARUS disinkronkan manual dengan
# semua kata kunci yang dipakai cari_lab_angka/cari_lab/cari_lab_flag di
# queue_ke_datapegawai -- kalau menambah tes baru yang sudah diklasifikasi,
# tambahkan juga substring-nya di sini supaya tidak dobel-lapor.
# ---------------------------------------------------------------------------

TES_SUDAH_DIKENAL = (
    "hemoglobin", "leukosit", "trombosit", "laju endap", "led",
    "sgpt", "alt", "sgot", "ast", "bilirubin direk", "kreatinin", "egfr",
    "ureum", "kolesterol total", "kolesterol ldl", "ldl", "kolesterol hdl", "hdl",
    "trigliserida", "trigliserid",
    "glukosa puasa", "gdp", "glukosa 2 jam", "gd2pp", "hba1c", "asam urat", "urat", "hbsag", "anti hbs", "anti-hbs",
    # Dikonfirmasi dr. Vidya (2026-07-24): MCV/MCH/MCHC dan Hematokrit
    # abnormal SENDIRIAN (tanpa penurunan Hb) tidak bermakna klinis --
    # abaikan, jangan dilaporkan lewat catch-all. Kalau Hb memang turun,
    # sudah tercakup oleh klasifikasi anemia (hb_status) yang sudah ada.
    "hematokrit", "mcv", "mch",
    # Eritrosit (RBC) darah sekarang diklasifikasi sendiri (lihat
    # klasifikasi_eritrosit_darah/interpretasi_eritrosit_darah) -- masuk
    # daftar dikenal supaya tidak dobel-lapor lewat catch-all.
    "eritrosit",
)

# Sama persis dengan parameter_urin di klasifikasi_urinalisa() (input_dict.py)
# -- dipakai TERPISAH dari TES_SUDAH_DIKENAL karena lab_urin adalah dict
# tersendiri (lihat catatan pemisahan panel di atas), bukan tes darah.
TES_URIN_SUDAH_DIKENAL = (
    "albumin", "darah / hb", "leukosit esterase", "nitrit",
    "bakteria", "kristal", "leukosit", "eritrosit", "silinder",
    "sel epitel",  # dikonfirmasi dr. Vidya (2026-07-24): abaikan, tidak bermakna klinis
    "warna", "kejernihan", "berat jenis",  # dikonfirmasi dr. Vidya (2026-07-24): abaikan
    "glukosa",  # sekarang diklasifikasi sendiri (lihat "glukosuria" di input_dict.py)
    "keton",  # sekarang diklasifikasi sendiri (lihat "ketonuria" di input_dict.py, 2026-08-04)
    "urobilinogen",  # sekarang diklasifikasi sendiri (lihat "urobilinogenuria" di input_dict.py, 2026-08-04)
)


def cek_flag_tidak_dikenal(lab_dict, kata_kunci_dikenal):
    """Cari entri lab dengan flag abnormal (H/L/* dari EHR) yang namanya
    TIDAK cocok satu pun tes yang sudah dikenali protokol (kata_kunci_dikenal
    beda untuk lab darah vs lab_urin, lihat pemanggil). Return list string
    deskriptif (kosong kalau tidak ada) -- dipakai supaya temuan di luar
    protokol TIDAK diam-diam diabaikan, melainkan tercatat di catatan_manual
    (flag naik ke kuning, muncul di notes.md)."""
    tidak_dikenal = []
    for nama, isi in lab_dict.items():
        if not isinstance(isi, dict):
            continue
        flag = (isi.get("flag") or "").strip()
        if not flag:
            continue
        nama_low = nama.strip().lower()
        if any(k in nama_low for k in kata_kunci_dikenal):
            continue
        tidak_dikenal.append(f"{nama} (flag '{flag}', hasil: {isi.get('hasil', '')})")
    return tidak_dikenal


# ---------------------------------------------------------------------------
# KONVERTER UTAMA
# ---------------------------------------------------------------------------

def queue_ke_datapegawai(entry):
    """Ubah satu entry queue.json jadi (DataPegawai, catatan_manual: list,
    override_urinalisa: str|None). override_urinalisa berisi teks placeholder
    kalau urinalisa TIDAK bisa diklasifikasi otomatis (mis. darah tanpa
    albumin) — dipakai fase3a_generate_teks.py supaya draft TIDAK diam-diam
    bilang 'Dalam batas normal' untuk temuan yang sebenarnya belum jelas."""
    catatan_manual = []
    override_urinalisa = None

    ident = entry.get("identitas", {})
    tv = entry.get("tanda_vital", {})
    lab = entry.get("laboratorium", {})
    lab_urin = entry.get("urinalisa_raw", {})
    kes_existing = entry.get("kesimpulan_existing", {})
    radio = entry.get("radiologi", {})

    nama = ident.get("nama_raw", "(tanpa nama)")
    jk = ident.get("jenis_kelamin", "P")

    # PENGAMAN: kalau usia gagal terbaca sama sekali (mis. format ID pegawai
    # tidak dikenali regex identitas), JANGAN diam-diam default ke 0 — itu
    # bisa salah membuat sistem mengira EKG tidak wajib (usia<35) padahal
    # usia sebenarnya tidak diketahui. Default ke usia tinggi supaya jalur
    # "EKG wajib" tetap terpicu dan pasien di-flag utk cek manual, bukan
    # diam-diam lolos sebagai hijau.
    if "usia" not in ident:
        usia = 999
        catatan_manual.append(
            "PERINGATAN: usia TIDAK TERBACA dari halaman (kemungkinan format ID pegawai "
            "tidak dikenali). Usia di-set 999 sementara sebagai pengaman supaya sistem TIDAK "
            "salah mengasumsikan EKG tidak wajib — WAJIB cek usia asli pasien & perbaiki manual."
        )
    else:
        usia = ident.get("usia", 0)

    # --- DETEKSI DATA RUSAK ---
    # Kalau lab tersimpan sebagai gumpalan teks (bukan tabel rapi), semua
    # pembacaan lab tidak bisa dipercaya. Deteksi ini DULU, sebelum apa pun.
    lab_rusak = False
    for nama_lab, isi in lab.items():
        h = isi.get("hasil", "") if isinstance(isi, dict) else str(isi)
        if not hasil_valid(h) and any(p in str(h) for p in ["Nama Test", "Order No", "\n\t"]):
            lab_rusak = True
            break

    if lab_rusak:
        # Jangan proses apa pun dari lab. Buat DataPegawai minimal + flag merah.
        d = DataPegawai(
            nama=nama, usia=usia, jenis_kelamin=jk,
            hamil=ident.get("hamil", False),
            td_sistolik=ke_angka(ambil_nilai(tv.get("td_sistolik"))),
            td_diastolik=ke_angka(ambil_nilai(tv.get("td_diastolik"))),
            imt=ke_angka(ambil_nilai(tv.get("bmi"))),
            lingkar_perut=ke_angka(ambil_nilai(tv.get("lingkar_perut"))),
        )
        catatan_manual = [
            "DATA LAB TIDAK TERBACA — tabel laboratorium tersimpan sebagai teks "
            "menggumpal, bukan tabel. Ini terjadi kalau section lab TIDAK di-expand "
            "penuh saat Fase 1. WAJIB: buka penuh section Laboratorium di layar, "
            "jalankan ulang Fase 1 untuk pasien ini. JANGAN approve dari data ini."
        ]
        return d, catatan_manual, override_urinalisa

    # Tanda vital
    sistolik = ke_angka(ambil_nilai(tv.get("td_sistolik")))
    diastolik = ke_angka(ambil_nilai(tv.get("td_diastolik")))
    bmi = ke_angka(ambil_nilai(tv.get("bmi")))
    lp = ke_angka(ambil_nilai(tv.get("lingkar_perut")))

    # Lab — helper: ubah "__RUSAK__" jadi None (sudah ditangani di atas, ini jaga2)
    def bersih(v):
        return None if v == "__RUSAK__" else v

    hb = bersih(cari_lab_angka(lab, "hemoglobin"))
    rujukan_hb, _ = cari_lab_rujukan(lab, "hemoglobin")
    hb_meningkat = cari_lab_flag(lab, "hemoglobin") == "H"
    leuko = bersih(cari_lab_angka(lab, "jumlah leukosit", "leukosit"))
    rujukan_leuko, _ = cari_lab_rujukan(lab, "jumlah leukosit", "leukosit")
    tromb = bersih(cari_lab_angka(lab, "jumlah trombosit", "trombosit"))
    rujukan_tromb, _ = cari_lab_rujukan(lab, "jumlah trombosit", "trombosit")
    led = bersih(cari_lab_angka(lab, "laju endap", "led"))
    rujukan_led, _ = cari_lab_rujukan(lab, "laju endap", "led")
    eritrosit_darah = bersih(cari_lab_angka(lab, "eritrosit"))
    rujukan_eritrosit_darah, _ = cari_lab_rujukan(lab, "eritrosit")
    sgpt = bersih(cari_lab_angka(lab, "sgpt", "alt"))
    rujukan_sgpt, _ = cari_lab_rujukan(lab, "sgpt", "alt")
    sgot = bersih(cari_lab_angka(lab, "sgot", "ast"))
    rujukan_sgot, _ = cari_lab_rujukan(lab, "sgot", "ast")
    bilirubin_direk = bersih(cari_lab_angka(lab, "bilirubin direk"))
    rujukan_bilirubin_direk, _ = cari_lab_rujukan(lab, "bilirubin direk")
    kreatinin = bersih(cari_lab_angka(lab, "kreatinin"))
    rujukan_kreatinin, _ = cari_lab_rujukan(lab, "kreatinin")
    egfr = bersih(cari_lab_angka(lab, "egfr"))
    rujukan_egfr, _ = cari_lab_rujukan(lab, "egfr")
    ureum = bersih(cari_lab_angka(lab, "ureum"))
    rujukan_ureum, _ = cari_lab_rujukan(lab, "ureum")
    # "kolesterol total" spesifik -- JANGAN cuma "kolesterol", supaya tidak
    # salah tangkap "Kolesterol HDL"/"Kolesterol LDL" kalau namanya mirip.
    kolesterol = bersih(cari_lab_angka(lab, "kolesterol total"))
    rujukan_kolesterol, catatan_kolesterol = cari_lab_rujukan(lab, "kolesterol total")
    # LDL/HDL: status langsung dari flag H/L EHR (bukan angka+rujukan) --
    # sama seperti hb_meningkat/gd2pp_meningkat di bawah. None kalau tidak
    # diperiksa sama sekali, supaya interpretasi_lipid() bisa bedakan
    # "diperiksa & normal" vs "tidak diperiksa" (dikonfirmasi dr. Vidya,
    # 2026-08-13, kasus Utri Heryani NRM 410-26-87).
    ldl_diperiksa = any("ldl" in n.lower() for n in lab)
    hdl_diperiksa = any("hdl" in n.lower() for n in lab)
    ldl_status = ("tinggi" if cari_lab_flag(lab, "ldl") == "H" else "normal") if ldl_diperiksa else None
    hdl_status = ("rendah" if cari_lab_flag(lab, "hdl") == "L" else "normal") if hdl_diperiksa else None
    trigliserida = bersih(cari_lab_angka(lab, "trigliserida", "trigliserid"))
    rujukan_trigliserida, _ = cari_lab_rujukan(lab, "trigliserida", "trigliserid")
    gdp = bersih(cari_lab_angka(lab, "glukosa puasa", "gdp"))
    rujukan_gdp, _ = cari_lab_rujukan(lab, "glukosa puasa", "gdp")
    gd2pp_meningkat = cari_lab_flag(lab, "glukosa 2 jam", "gd2pp") == "H"
    hba1c = bersih(cari_lab_angka(lab, "hba1c"))
    asam_urat = bersih(cari_lab_angka(lab, "asam urat", "urat"))
    rujukan_asam_urat, _ = cari_lab_rujukan(lab, "asam urat", "urat")

    hbsag_raw = cari_lab(lab, "hbsag")
    if hbsag_raw == "__RUSAK__":
        hbsag_raw = None
    hbsag_positif = teks_reaktif(hbsag_raw)
    anti_hbs_cek, anti_hbs_pos = anti_hbs_positif_dari_nilai(lab)

    # Urinalisa — baca dari flag/rujukan tiap parameter di lab_urin, dict
    # TERPISAH dari lab umum (lihat baca_tabel_lab di fase1_baca.py). HARUS
    # terpisah karena panel HEMATOLOGI RUTIN dan URIN LENGKAP sama-sama
    # punya baris bernama persis "Eritrosit" (dan pencarian lab lain di atas
    # pakai substring match) -- kalau digabung, satu bisa menimpa/tertukar
    # dengan yang lain (kasus Dwiria Maharani Purba, NRM 455-93-96: urinalisa
    # salah kebaca "normal" padahal tidak pernah dikerjakan, gara-gara CBC-nya
    # kebetulan juga punya baris "Eritrosit"). klasifikasi_urinalisa() sendiri
    # yang menentukan "tidak_dilakukan" kalau lab_urin kosong sama sekali.
    # catatan_manual ditambah supaya flag naik ke kuning (perlu dibaca sebelum
    # approve), TAPI ini TIDAK memblokir kelaikan kerja (beda dari
    # data_belum_lengkap) -- dikonfirmasi dr. Vidya: semua pekerja wajib
    # urinalisa, tapi kalau belum dilakukan tetap bisa "Laik kerja" + saran
    # melengkapi.
    urinalisa_status_list, urinalisa_leukosituria_detail = klasifikasi_urinalisa(lab_urin)
    urinalisa_tidak_dilakukan = urinalisa_status_list == ["tidak_dilakukan"]
    if urinalisa_tidak_dilakukan:
        catatan_manual.append("Urinalisa belum dilakukan — mohon lengkapi (tidak memengaruhi kelaikan kerja)")
        urinalisa_status_list = []

    # Radiologi
    r_dilakukan, r_status, r_desk, r_catatan = interpretasi_radiologi(radio)
    if r_catatan:
        catatan_manual.append(r_catatan)

    # EKG
    e_dilakukan, e_status, e_desk = interpretasi_ekg_existing(kes_existing, entry.get("ekg_asli"))
    if usia >= 35 and not e_dilakukan:
        catatan_manual.append(f"Usia {usia} (>=35) tapi EKG belum terbaca/belum dilakukan — WAJIB dicek")

    # Catch-all: tes lab dengan flag abnormal yang belum ada aturan
    # interpretasinya di protokol -- JANGAN diabaikan (dikonfirmasi dr. Vidya).
    tidak_dikenal = (cek_flag_tidak_dikenal(lab, TES_SUDAH_DIKENAL)
                     + cek_flag_tidak_dikenal(lab_urin, TES_URIN_SUDAH_DIKENAL))
    if tidak_dikenal:
        catatan_manual.append(
            "PERLU_CEK_MANUAL: ada hasil dengan flag abnormal yang BELUM ADA "
            "aturan interpretasinya di protokol -- mohon buatkan kesimpulan & "
            "sarannya: " + "; ".join(tidak_dikenal)
        )

    d = DataPegawai(
        nama=nama, usia=usia, jenis_kelamin=jk,
        hamil=ident.get("hamil", False),
        td_sistolik=sistolik, td_diastolik=diastolik,
        imt=bmi, lingkar_perut=lp,
        hb_status=klasifikasi_hb(hb, rujukan_hb),
        leukosit_status=klasifikasi_leukosit(leuko, rujukan_leuko),
        trombosit_status=klasifikasi_trombosit(tromb, rujukan_tromb),
        led_rasio_dari_rujukan_atas=klasifikasi_led(led, rujukan_led),
        eritrosit_selisih_atas=klasifikasi_eritrosit_darah(eritrosit_darah, rujukan_eritrosit_darah),
        hb_meningkat=hb_meningkat,
        sgot_sgpt_status=klasifikasi_sgot_sgpt(sgpt, sgot, rujukan_sgpt, rujukan_sgot),
        ggt_status=None,
        bilirubin_direk_status=klasifikasi_bilirubin_direk(bilirubin_direk, rujukan_bilirubin_direk),
        hbsag_positif=hbsag_positif,
        anti_hbs_diperiksa=anti_hbs_cek,
        anti_hbs_positif=anti_hbs_pos,
        kreatinin_status=klasifikasi_kreatinin(
            kreatinin, egfr, ureum, rujukan_kreatinin, rujukan_egfr, rujukan_ureum
        ),
        riwayat_ggk=entry.get("riwayat_ggk", False),
        kolesterol_status=klasifikasi_kolesterol(kolesterol, rujukan_kolesterol, catatan_kolesterol),
        ldl_status=ldl_status,
        hdl_status=hdl_status,
        trigliserida_status=klasifikasi_trigliserida(trigliserida, rujukan_trigliserida),
        gdp_status=klasifikasi_gdp(gdp, rujukan_gdp),
        gd2pp_meningkat=gd2pp_meningkat,
        hba1c_status=klasifikasi_hba1c(hba1c),
        asam_urat_status=klasifikasi_asam_urat(asam_urat, rujukan_asam_urat),
        urinalisa_tidak_dilakukan=urinalisa_tidak_dilakukan,
        urinalisa_status_list=urinalisa_status_list,
        urinalisa_leukosituria_detail=urinalisa_leukosituria_detail,
        rontgen_dilakukan=r_dilakukan, rontgen_status=r_status,
        rontgen_abnormal_deskripsi=r_desk,
        ekg_dilakukan=e_dilakukan, ekg_status=e_status,
        ekg_abnormal_deskripsi=e_desk,
    )
    return d, catatan_manual, override_urinalisa


def cetak(hasil, nama, catatan_manual):
    print("\n" + "=" * 72)
    print(f"PASIEN: {nama}")
    print("=" * 72)

    flag = hasil.flag
    # Data lab rusak = SELALU merah (jangan pernah kuning)
    ada_data_rusak = any("DATA LAB TIDAK TERBACA" in c for c in catatan_manual)
    if ada_data_rusak:
        flag = "merah"
    elif catatan_manual and flag == "hijau":
        flag = "kuning"

    if flag == "merah":
        print("\n🔴 FLAG MERAH")
    elif flag == "kuning":
        print("\n🟡 FLAG KUNING")
    else:
        print("\n🟢 FLAG HIJAU")

    for a in hasil.flag_alasan:
        print(f"   - {a}")
    for c in catatan_manual:
        print(f"   - {c}")

    print("\n--- Ringkasan Jasmani ---")
    for l in hasil.kesimpulan_jasmani:
        print(l)
    print("\n--- Laboratorium ---")
    for l in hasil.kesimpulan_lab:
        print(l)
    print(f"Rontgen : {hasil.kesimpulan_radiologi}")
    print(f"EKG : {hasil.kesimpulan_ekg}")
    print("\n--- Catatan Kelaikan ---")
    print(hasil.catatan_tambahan or "(tidak ada)")
    print("\n--- Saran ---")
    for s in hasil.saran:
        print(f"- {s}")
    print(f"\n>>> {hasil.kelaikan} <<<")
    if hasil.temuan:
        print(f"[{len(hasil.temuan)} temuan] {', '.join(hasil.temuan)}")
    print("=" * 72)


if __name__ == "__main__":
    with open("queue.json", encoding="utf-8") as f:
        antrian = json.load(f)

    print(f"Memproses {len(antrian)} pasien dari queue.json\n")
    for entry in antrian:
        d, catatan, _override_urinalisa = queue_ke_datapegawai(entry)
        hasil = proses_pegawai(d)
        cetak(hasil, d.nama, catatan)
