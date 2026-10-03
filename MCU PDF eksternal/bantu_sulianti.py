"""
Pembantu menulis ekstrak/<NRM>.json untuk template RSPI Sulianti Saroso (paket MCU CPNS:
SKS + SK jiwa + SK NAPZA + lab hematologi/urin/NAPZA 2 hal + rontgen), yang sering
datang sebagai scan. Nilai tetap DIBACA dari gambar oleh Claude; file ini cuma
mengisi struktur JSON + rujukan yang tercetak sama di setiap lembar template ini
(beda per jenis kelamin). Kalau rujukan di lembar tertentu beda, tulis manual.

Pakai dari Python:
    from bantu_sulianti import tulis
    tulis("455-95-42", nama=..., tgl_lahir="1998-09-13", jk="P", nip=..., tanggal="2026-04-29",
          hal_lab=(3, 4), hal_rad=5,
          darah=dict(Hemoglobin="12.5", ...), flag=dict(Eosinofil="H"),
          urin=dict(...), rad_kesimpulan="...", rad_deskripsi="...", lain=[...])
"""

import json
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
VENDOR = "RSPI Sulianti Saroso"

RUJUKAN_DARAH = {
    "P": {"Hemoglobin": "11.7 - 15.5", "Hematokrit": "35 - 47", "Eritrosit": "3.8 - 5.2", "Leukosit": "3.6 - 11.0"},
    "L": {"Hemoglobin": "13.2 - 17.3", "Hematokrit": "40 - 52", "Eritrosit": "4.4 - 5.9", "Leukosit": "3.8 - 10.6"},
}
RUJUKAN_UMUM = {"M.C.V": "80 - 100", "M.C.H": "26 - 34", "M.C.H.C": "32 - 36", "RDW-CV": "11.5 - 14.5",
                "Trombosit": "150 - 440", "Basofil": "0 - 1", "Eosinofil": "2 - 4", "Neutrofil": "50 - 70",
                "Limfosit": "25 - 40", "Monosit": "2 - 8", "Neutrofil Limfosit Ratio": "", "Limfosit Absolut": ""}
SATUAN = {"Hemoglobin": "g/dL", "Hematokrit": "%", "Eritrosit": "10^6/µL", "M.C.V": "fL", "M.C.H": "pg",
          "M.C.H.C": "g/dL", "RDW-CV": "%", "Leukosit": "10^3/µL", "Trombosit": "10^3/µL", "Basofil": "%",
          "Eosinofil": "%", "Neutrofil": "%", "Limfosit": "%", "Monosit": "%", "Neutrofil Limfosit Ratio": "",
          "Limfosit Absolut": "10^3/µL"}
URIN_RUJUKAN = {"Warna": "", "Kejernihan": "", "Berat Jenis": "1.010 - 1.025", "pH": "4.6 - 8.0",
                "Leukosit Esterase": "Negatif", "Nitrit": "Negatif", "Protein": "Negatif", "Glukosa": "Negatif",
                "Keton": "Negatif", "Urobilinogen": "<=16", "Bilirubin": "Negatif", "Darah (Blood)": "Negatif",
                "Eritrosit": "0 - 2", "Leukosit": "0 - 5", "Silinder": "Negatif", "Epitel": "", "Kristal": "Negatif",
                "Bakteria": "Negatif"}
URIN_SATUAN = {"Glukosa": "mg/dL", "Keton": "mg/dL", "Urobilinogen": "µmol/L", "Eritrosit": "/LPB",
               "Leukosit": "/LPB", "Silinder": "/LPK"}
URIN_HAL1 = ("Warna", "Kejernihan", "Berat Jenis", "pH", "Leukosit Esterase")
NAPZA = ("Morphine", "Cocaine", "Amphetamine", "THC", "Methamphetamine", "BZO", "SOMA")


def tulis(nrm, *, nama, tgl_lahir, jk, nip, tanggal, hal_lab, hal_rad, darah, urin, flag=None,
          napza="Negatif", rad_kesimpulan=None, rad_deskripsi="", lain=None, ekg=None):
    flag = flag or {}
    h1, h2 = hal_lab
    rujuk = {**RUJUKAN_UMUM, **RUJUKAN_DARAH[jk]}
    base = {"vendor": VENDOR, "tanggal": tanggal, "berkas": "berkas1", "dibaca_dari": "gambar"}
    lab = [{"nama": k, "hasil": v, "satuan": SATUAN.get(k, ""), "rujukan": rujuk.get(k, ""),
            "flag_vendor": flag.get(k, ""), "halaman": h1, **base} for k, v in darah.items()]
    lab += [{"nama": k, "hasil": napza, "satuan": "", "rujukan": "Negatif", "flag_vendor": "", "halaman": h2, **base}
            for k in NAPZA]
    ur = [{"nama": k, "hasil": v, "satuan": URIN_SATUAN.get(k, ""), "rujukan": URIN_RUJUKAN.get(k, ""),
           "flag_vendor": flag.get("urin:" + k, ""), "halaman": h1 if k in URIN_HAL1 else h2, **base}
          for k, v in urin.items()]
    data = {
        "nrm": nrm,
        "sumber": [{"berkas": "berkas1", "vendor": VENDOR, "tanggal": tanggal,
                    "isi": "paket MCU CPNS (SKS, SK jiwa, SK NAPZA, lab, rontgen); halaman scan"}],
        "identitas_pdf": {"nama": nama, "tgl_lahir": tgl_lahir, "jenis_kelamin": jk, "nip": nip},
        "tanda_vital": {},
        "lab": lab,
        "urin": ur,
        "radiologi": ({"ada": True, "vendor": VENDOR, "tanggal": tanggal, "berkas": "berkas1", "halaman": hal_rad,
                       "deskripsi": rad_deskripsi, "kesimpulan": rad_kesimpulan} if rad_kesimpulan else None),
        "ekg": ekg,
        "lain": lain or [],
    }
    p = FOLDER / "ekstrak" / f"{nrm}.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
