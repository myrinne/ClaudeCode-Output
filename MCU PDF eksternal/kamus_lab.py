"""
KAMUS LAB — nama tes vendor -> nama tes RSCM, satuan, dan kebijakan cutoff
============================================================================

KEBIJAKAN CUTOFF (dikonfirmasi dr. Vidya, 2026-10-03):
  - "mesin"    : tes yang batas normalnya tergantung alat/metode lab
                 (SGOT/SGPT, GGT, kreatinin, ureum, asam urat, bilirubin,
                 Hb, leukosit, trombosit, LED, eritrosit, sedimen urin) ->
                 pakai NILAI RUJUKAN VENDOR yang tercetak di PDF. Hb juga
                 masuk sini (Hb 11.9 dgn rujukan vendor 11.7-15.5 = normal).
  - "pedoman"  : ambang diagnostik/guideline (GDP 100/126, GD2PP 140,
                 HbA1c 5.7/6.5, kolesterol 200/240, TG 150, eGFR) -> pakai
                 ANGKA PROTOKOL yang tetap, rujukan vendor DIABAIKAN.
  - "kualitatif": HBsAg / Anti-HBs -> baca teks reaktif/angka.
  - "info"     : tidak diinterpretasi protokol (LDL/HDL, Vit D, hs-CRP,
                 tumor marker, hitung jenis, dst) -- dikonfirmasi dr. Vidya:
                 tidak perlu masuk ringkasan, KECUALI hal penting yang bisa
                 mengubah kelaikan -> dicatat di notes (lihat PENTING_*).

Kalau nama tes vendor TIDAK ada di kamus ini -> tidak ditebak. Dilaporkan
di notes (dan flag kuning kalau vendor menandainya abnormal) supaya
kamusnya ditambah, bukan diam-diam dibuang.
"""

import re
from typing import Optional


def norm_nama(teks: str) -> str:
    """'- Basofil Absolut' / 'AST/SGOT' / 'Hemoglobin •' -> bentuk baku utk dicocokkan."""
    t = (teks or "").lower()
    t = t.replace("•", " ").replace("*", " ")
    t = re.sub(r"^[\s\-–]+", "", t)
    t = re.sub(r"[().,:]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def norm_satuan(teks: Optional[str]) -> str:
    t = (teks or "").strip().lower()
    t = t.replace("µ", "u").replace("μ", "u").replace("³", "^3").replace("⁶", "^6")
    t = t.replace(" ", "").replace("x10", "10").replace("10e", "10^")
    if t in ("10^3/ul", "10^9/l", "ribu/ul", "10^3/mm3", "rb/ul"):
        return "10^3/ul"
    if t in ("10^6/ul", "10^12/l", "juta/ul", "10^6/mm3", "jt/ul"):
        return "10^6/ul"
    if t in ("/ul", "/mm3", "sel/ul", "sel/mm3"):
        return "/ul"
    if t in ("mm/jam", "mm/h", "mm/1jam", "mm/1h", "mm", "mm/hr"):
        return "mm/jam"
    if t in ("iu/l", "u/l", "ui/l"):
        return "u/l"
    if t in ("umol/l", "mikromol/l"):
        return "umol/l"
    if t in ("ml/menit/1.73m²", "ml/menit/1.73m^2", "ml/min/1.73m²", "ml/min/1.73m^2",
             "ml/menit/1.73", "ml/min/1.73", "ml/menit/1,73m²", "ml/min/1.73m2", "ml/menit/1.73m2"):
        return "ml/min"
    return t


# ---------------------------------------------------------------------------
# TES YANG DIINTERPRETASI PROTOKOL (masuk dict 'laboratorium' konverter lama)
# nama_rscm HARUS mengandung substring yang dicari konverter_queue.py
# (mis. "jumlah leukosit", "sgpt", "kolesterol total") -- jangan diganti
# sembarangan.
# konversi: satuan_vendor_ternormalisasi -> faktor pengali ke satuan RSCM
# ---------------------------------------------------------------------------

TES = {
    "hemoglobin": dict(
        nama_rscm="Hemoglobin", satuan="g/dL", kategori="mesin",
        alias=["hemoglobin", "hb", "haemoglobin", "hgb"],
        konversi={"g/dl": 1, "g/l": 0.1, "mmol/l": 1.611}),
    "hematokrit": dict(
        nama_rscm="Hematokrit", satuan="%", kategori="mesin",
        alias=["hematokrit", "ht", "hct", "haematocrit", "hematocrit"],
        konversi={"%": 1}),
    "eritrosit": dict(
        nama_rscm="Eritrosit", satuan="10^6/uL", kategori="mesin",
        alias=["eritrosit", "rbc", "erytrocyte", "erythrocyte", "jumlah eritrosit"],
        konversi={"10^6/ul": 1}),
    "mcv": dict(nama_rscm="MCV/VER", satuan="fL", kategori="mesin",
                alias=["mcv", "m c v", "ver", "mcv/ver"], konversi={"fl": 1}),
    "mch": dict(nama_rscm="MCH/HER", satuan="pg", kategori="mesin",
                alias=["mch", "m c h", "her", "mch/her"], konversi={"pg": 1}),
    "mchc": dict(nama_rscm="MCHC/KHER", satuan="g/dL", kategori="mesin",
                 alias=["mchc", "m c h c", "kher", "mchc/kher"], konversi={"g/dl": 1, "%": 1}),
    "leukosit": dict(
        nama_rscm="Jumlah Leukosit", satuan="10^3/uL", kategori="mesin",
        alias=["leukosit", "jumlah leukosit", "lekosit", "wbc", "leucocyte", "leukocyte"],
        konversi={"10^3/ul": 1, "/ul": 0.001}),
    "trombosit": dict(
        nama_rscm="Jumlah Trombosit", satuan="10^3/uL", kategori="mesin",
        alias=["trombosit", "jumlah trombosit", "platelet", "plt", "thrombocyte", "thrombosit", "trombosit plt"],
        konversi={"10^3/ul": 1, "/ul": 0.001}),
    "led": dict(
        nama_rscm="Laju Endap Darah", satuan="mm/jam", kategori="mesin",
        alias=["led", "laju endap darah", "esr", "laju endap darah led"],
        konversi={"mm/jam": 1}),
    "sgot": dict(
        nama_rscm="SGOT (AST)", satuan="U/L", kategori="mesin",
        alias=["sgot", "ast", "ast/sgot", "sgot/ast", "got", "sgot ast", "ast sgot"],
        konversi={"u/l": 1}),
    "sgpt": dict(
        nama_rscm="SGPT (ALT)", satuan="U/L", kategori="mesin",
        alias=["sgpt", "alt", "alt/sgpt", "sgpt/alt", "gpt", "sgpt alt", "alt sgpt"],
        konversi={"u/l": 1}),
    "ggt": dict(
        nama_rscm="Gamma GT", satuan="U/L", kategori="mesin",
        alias=["gamma gt", "ggt", "gamma glutamyl transferase", "gamma-gt", "y-gt"],
        konversi={"u/l": 1}),
    "bilirubin_total": dict(
        nama_rscm="Bilirubin Total", satuan="mg/dL", kategori="mesin",
        alias=["bilirubin total", "total bilirubin", "bilirubin t"],
        konversi={"mg/dl": 1, "umol/l": 1 / 17.1}),
    "bilirubin_direk": dict(
        nama_rscm="Bilirubin Direk", satuan="mg/dL", kategori="mesin",
        alias=["bilirubin direk", "bilirubin direct", "direct bilirubin", "bilirubin d"],
        konversi={"mg/dl": 1, "umol/l": 1 / 17.1}),
    "bilirubin_indirek": dict(
        nama_rscm="Bilirubin Indirek", satuan="mg/dL", kategori="mesin",
        alias=["bilirubin indirek", "bilirubin indirect", "indirect bilirubin"],
        konversi={"mg/dl": 1, "umol/l": 1 / 17.1}),
    "ureum": dict(
        nama_rscm="Ureum Darah", satuan="mg/dL", kategori="mesin",
        alias=["ureum", "urea", "urea darah", "ureum darah"],
        konversi={"mg/dl": 1, "mmol/l": 6.006}),
    "kreatinin": dict(
        nama_rscm="Kreatinin Darah", satuan="mg/dL", kategori="mesin",
        alias=["kreatinin", "kreatinin darah", "creatinine", "kreatinin serum"],
        konversi={"mg/dl": 1, "umol/l": 1 / 88.4}),
    "egfr": dict(
        # Pedoman: KDIGO -- <60 = penurunan bermakna. Rujukan RSCM sendiri
        # beda per usia (mis. 63-147), vendor sering pakai >=90. 60 sbg angka
        # guideline tetap -- dikonfirmasi dr. Vidya, 2026-10-03.
        nama_rscm="eGFR", satuan="mL/min/1.73m^2", kategori="pedoman",
        alias=["egfr", "elfg", "elfg ckd-epi", "egfr ckd-epi", "lfg", "egfr ckd epi", "elfg ckd epi"],
        konversi={"ml/min": 1},
        rujukan_pedoman="60 - 200"),
    "gdp": dict(
        nama_rscm="Glukosa Puasa", satuan="mg/dL", kategori="pedoman",
        alias=["glukosa puasa", "gula darah puasa", "gdp", "glukosa darah puasa", "fasting glucose", "fbs"],
        konversi={"mg/dl": 1, "mmol/l": 18.016},
        rujukan_pedoman="70 - 99"),
    "gd2pp": dict(
        nama_rscm="Glukosa 2 Jam PP", satuan="mg/dL", kategori="pedoman",
        alias=["glukosa 2jpp", "glukosa 2 jpp", "gd2pp", "gula darah 2 jam pp", "glukosa 2 jam pp",
               "glukosa 2 jam post prandial", "2 jam pp", "gdpp", "glukosa pp"],
        konversi={"mg/dl": 1, "mmol/l": 18.016},
        rujukan_pedoman="< 140"),
    "hba1c": dict(
        nama_rscm="HbA1c", satuan="%", kategori="pedoman",
        alias=["hba1c", "hba1c ngsp", "hemoglobin a1c", "hb a1c"],
        konversi={"%": 1},
        rujukan_pedoman="< 5.7"),
    "kolesterol": dict(
        nama_rscm="Kolesterol Total", satuan="mg/dL", kategori="pedoman",
        alias=["kolesterol total", "cholesterol total", "cholesterol", "kolesterol", "total cholesterol"],
        konversi={"mg/dl": 1, "mmol/l": 38.67},
        rujukan_pedoman="< 200",
        catatan_pedoman="Normal : <200\nBorderline : 200 - 239\nHigh : => 240"),
    "trigliserida": dict(
        nama_rscm="Trigliserida", satuan="mg/dL", kategori="pedoman",
        alias=["trigliserida", "trigliserid", "triglyceride", "triglycerides", "tg"],
        konversi={"mg/dl": 1, "mmol/l": 88.57},
        rujukan_pedoman="< 150"),
    "asam_urat": dict(
        nama_rscm="Asam Urat", satuan="mg/dL", kategori="mesin",
        alias=["asam urat", "uric acid", "urat"],
        konversi={"mg/dl": 1, "umol/l": 1 / 59.48}),
    "hbsag": dict(nama_rscm="HBsAg", satuan="", kategori="kualitatif",
                  alias=["hbsag", "hbs ag"], konversi={}),
    "anti_hbs": dict(nama_rscm="Anti HBs", satuan="mIU/mL", kategori="kualitatif",
                     alias=["anti hbs", "anti-hbs", "antihbs", "anti hbsag"], konversi={}),
}

# Tes yang SENGAJA tidak diinterpretasi (dikonfirmasi dr. Vidya) -- tetap
# dikenali supaya tidak dilaporkan sbg "nama tes tidak dikenal".
TES_INFO = [
    "cholesterol ldl direk", "kolesterol ldl", "ldl", "ldl direk", "cholesterol ldl", "ldl cholesterol",
    "cholesterol hdl", "kolesterol hdl", "hdl", "hdl cholesterol",
    "vitamin d 25-oh total", "vitamin d", "25-oh vitamin d",
    "hs-crp", "hscrp", "crp",
    "glukosa sewaktu", "gds", "gula darah sewaktu", "luc", "jumlah neutrofil absolut", "jumlah limfosit absolut",
    "rasio neutrofil limfosit", "netrofil", "netrofil limfosit ratio", "neutrofil limfosit ratio",
    "cea", "psa", "free psa", "afp", "ca 125", "ca 19-9",
    "d-dimer", "apo-b", "apo b", "ck", "cpk",
    "protein total", "albumin", "globulin", "urea n", "bun",
    "hba1c ifcc", "estimasi glukosa rata-rata", "estimasi glukosa rata-rata eag", "eag",
    "rdw", "rdw-cv", "rdw-sd", "mpv", "pdw", "pct",
    "basofil", "eosinofil", "basophil", "eosinophil", "neutrofil", "neutrophil", "limfosit", "monosit",
    "basofil absolut", "eosinofil absolut", "neutrofil absolut", "limfosit absolut", "monosit absolut",
    "neutrofil limfosit ratio", "nlr", "nrbc", "nrbc absolut",
    "adp 1 0 um", "adp 2 0 um", "adp 5 0 um", "adp 10 0 um", "kesan",
    "morphine", "morphin", "cocaine", "coccain", "amphetamine", "amphetamin", "thc",
    "methamphetamine", "methamphetamin", "bzo", "soma", "benzodiazepin", "morfin", "metamphetamine", "metamfetamin", "benzodiazepine", "kokain", "mariyuana", "marijuana", "ganja", "amfetamin", "ganja/thc", "opiat", "metamfetamin", "opiate", "cannabis", "benzodiazepin", "canabis", "cocain", "mdma", "metamphetamin",
]

# Tes info yang TETAP harus dilaporkan ke dr. Vidya kalau abnormal krn bisa
# mengubah kelaikan kerja (dikonfirmasi: "kalau penting & bisa mengubah
# kelaikan, kasih notes ke saya"). Dicek di pdf_ke_queue.py.
PENTING_KALAU_ABNORMAL = ("hs-crp", "hscrp", "crp", "cea", "psa", "afp", "ca 125", "ca 19-9",
                          "d-dimer", "morphine", "morphin", "cocaine", "coccain", "amphetamine",
                          "amphetamin", "thc", "methamphetamine", "methamphetamin", "bzo", "soma",
                          "benzodiazepin", "morfin", "metamphetamine", "metamfetamin", "benzodiazepine", "kokain", "mariyuana",
                          "marijuana", "ganja", "amfetamin")


# ---------------------------------------------------------------------------
# URINALISA -- nama HARUS persis nama EHR RSCM, krn klasifikasi_urinalisa()
# (input_dict.py) mencocokkan nama secara exact, bukan substring.
# ---------------------------------------------------------------------------

URIN = {
    "Warna": ["warna", "color", "colour"],
    "Kejernihan": ["kejernihan", "clarity", "kekeruhan"],
    "Berat Jenis": ["berat jenis", "bj", "specific gravity"],
    "pH": ["ph"],
    "Albumin": ["albumin", "albumin urine", "protein", "protein urine", "albumin urin", "protein urin"],
    "Glukosa": ["glukosa", "glukosa urin", "glukosa urine", "glucose", "reduksi"],
    "Keton": ["keton", "ketone", "keton urin"],
    "Darah / Hb": ["darah", "darah urin", "darah blood", "blood", "darah / hb", "darah/hb", "hb urin"],
    "Bilirubin": ["bilirubin", "bilirubin urin"],
    "Urobilinogen": ["urobilinogen"],
    "Nitrit": ["nitrit", "nitrite"],
    "Leukosit Esterase": ["leukosit esterase", "lekosit esterase", "leukocyte esterase", "leukosit esterase dipstick", "leukosit strip", "leukosit dipstick"],
    "Leukosit": ["leukosit", "lekosit", "leukosit sedimen", "wbc"],
    "Eritrosit": ["eritrosit", "eritrosit sedimen", "rbc"],
    "Silinder": ["silinder", "silinder hialin", "silinder lain", "cylinder", "cast"],
    "Sel Epitel": ["sel epitel", "epitel", "epitel skuamosa", "epitel transisional",
                   "epitel tubulus ginjal", "epithel"],
    "Kristal": ["kristal", "kristal normal", "kristal abnormal", "crystal"],
    "Bakteria": ["bakteri", "bakteria", "bacteria"],
    "Lain-lain": ["lain-lain", "lain lain", "jamur", "parasit", "ragi"],
}

# Parameter urin yang dinilai via flag: kualitatif dipstick vs sedimen semi-kuantitatif
URIN_DIPSTICK = ("Albumin", "Glukosa", "Keton", "Darah / Hb", "Bilirubin", "Nitrit",
                 "Leukosit Esterase", "Kristal", "Bakteria")
URIN_SEDIMEN = ("Leukosit", "Eritrosit")
URIN_ABAIKAN = ("Warna", "Kejernihan", "Berat Jenis", "pH", "Sel Epitel", "Lain-lain")


_INDEKS_TES = {}
for _kunci, _t in TES.items():
    for _a in _t["alias"]:
        _INDEKS_TES[norm_nama(_a)] = _kunci
_INDEKS_INFO = {norm_nama(a) for a in TES_INFO}
_INDEKS_URIN = {}
for _nama, _alias in URIN.items():
    for _a in _alias:
        _INDEKS_URIN[norm_nama(_a)] = _nama


def _varian(nama_vendor: str):
    """Nama asli, lalu tanpa singkatan dalam kurung ('Hemoglobin (HGB)' -> 'Hemoglobin',
    'Netrofil Limfosit Ratio(NLR)' -> 'Netrofil Limfosit Ratio'), lalu tanpa akhiran urin."""
    tanpa_kurung = re.sub(r"\([^)]*\)", " ", nama_vendor or "")
    hasil = [norm_nama(nama_vendor), norm_nama(tanpa_kurung)]
    hasil.append(re.sub(r"\s+urin[e]?$", "", hasil[-1]))
    return hasil


def cari_tes(nama_vendor: str):
    """Return (kunci_tes | None, adalah_info: bool)."""
    for n in _varian(nama_vendor):
        if n in _INDEKS_TES:
            return _INDEKS_TES[n], False
    for n in _varian(nama_vendor):
        if n in _INDEKS_INFO:
            return None, True
    return None, False


def cari_urin(nama_vendor: str) -> Optional[str]:
    for n in _varian(nama_vendor):
        if n in _INDEKS_URIN:
            return _INDEKS_URIN[n]
    return None
