"""
LANGKAH 3 — ekstrak/<NRM>.json (hasil baca PDF) -> entry berformat queue.json
==============================================================================

Output-nya PERSIS format yang dihasilkan fase1_baca.py dari layar EHR,
supaya konverter_queue.py + protocol_engine.py + fase3a lama bisa dipakai
apa adanya (tidak ada logika klinis yang diduplikasi di sini).

Yang dikerjakan file ini:
  1. Nama tes vendor -> nama tes RSCM (kamus_lab.py). Tidak dikenal -> dilaporkan.
  2. Satuan vendor -> satuan RSCM. Tidak dikenal -> dilaporkan, tes tidak dipakai.
  3. Rujukan: tes "mesin" pakai rujukan vendor, tes "pedoman" pakai angka
     protokol (lihat kamus_lab.py). Flag H/L dihitung ulang dari rujukan
     yang dipakai -- tanda '*' vendor tidak dipercaya mentah-mentah.
  4. Kalau ada >1 hasil utk tes yang sama (mis. 2 PDF beda tanggal), yang
     TERBARU dipakai, yang lama dicatat sbg riwayat di notes.
  5. Gabung dengan data EHR: kalau EHR sudah punya datanya, EHR MENANG
     (dikonfirmasi dr. Vidya, 2026-10-03). PDF cuma mengisi yang kosong.
"""

import json
import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

import _jalur  # noqa: F401  (sys.path ke pipeline lama)
from protocol_engine import _baris_temuan_radiologi, KATA_KUNCI_TANPA_SARAN_GENERIK, KATA_KUNCI_TULANG, \
    KATA_KUNCI_ARAH_SP_PARU, KATA_KUNCI_ARAH_PD_PMPK
from konverter_queue import ambil_nilai, hasil_valid

from kamus_lab import (TES, PENTING_KALAU_ABNORMAL, URIN_DIPSTICK, URIN_SEDIMEN,
                       cari_tes, cari_urin, norm_nama, norm_satuan)

FOLDER_INI = Path(__file__).resolve().parent

# Substring nama tes di dict lab EHR yg menandakan tes itu SUDAH ada di EHR
# (disamakan dgn kata kunci pencarian di konverter_queue.py).
KUNCI_EHR = {
    "hemoglobin": ["hemoglobin"], "hematokrit": ["hematokrit"], "eritrosit": ["eritrosit"],
    "mcv": ["mcv"], "mch": ["mch/", "mch "], "mchc": ["mchc"],
    "leukosit": ["leukosit"], "trombosit": ["trombosit"], "led": ["laju endap"],
    "sgot": ["sgot"], "sgpt": ["sgpt"], "ggt": ["gamma", "ggt"],
    "bilirubin_total": ["bilirubin total"], "bilirubin_direk": ["bilirubin direk"],
    "bilirubin_indirek": ["bilirubin indirek"], "ureum": ["ureum"], "kreatinin": ["kreatinin"],
    "egfr": ["egfr"], "gdp": ["glukosa puasa", "gdp"], "gd2pp": ["2 jam", "gd2pp"],
    "hba1c": ["hba1c"], "kolesterol": ["kolesterol total"], "trigliserida": ["trigliserid"],
    "asam_urat": ["asam urat"], "hbsag": ["hbsag"], "anti_hbs": ["anti hbs", "anti-hbs"],
}

KATA_NEGATIF = {"negatif", "negative", "neg", "-", "normal", "nihil", "non reaktif", "non-reaktif",
                "nonreaktif", "tidak ditemukan", "tidak ada", "0", "(-)", "(-) negatif"}


# ---------------------------------------------------------------------------
# Angka, rentang, satuan
# ---------------------------------------------------------------------------

def ke_float(teks) -> Optional[float]:
    """'16,86' -> 16.86 ; '1000 (+4)' -> 1000 ; '0 - 1' -> 0 (pakai maks_rentang utk sedimen)."""
    if teks is None:
        return None
    t = str(teks).strip()
    if "," in t and "." not in t:
        t = t.replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", t)
    return float(m.group()) if m else None


def maks_rentang(teks) -> Optional[float]:
    """Sedimen urin '0 - 1' / '0-2' / '1-2 /LPB' -> 1 / 2 / 2. 'Negatif' -> 0."""
    t = str(teks or "").strip().lower()
    if not t or t in KATA_NEGATIF:
        return 0.0
    angka = re.findall(r"\d+(?:[.,]\d+)?", t)
    return max(float(a.replace(",", ".")) for a in angka) if angka else None


def parse_rujukan(rujukan) -> tuple:
    """Rujukan vendor -> (bawah, atas). Menangani '13.2 - 17.3', '< 33', '<=10.0',
    '>= 40', '≤ 5', '=> 240', koma desimal. (None, None) kalau bukan angka."""
    t = str(rujukan or "").strip().replace("≤", "<=").replace("≥", ">=").replace("=>", ">=")
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    m = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", t)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"<=?\s*(\d+(?:\.\d+)?)", t)
    if m:
        return None, float(m.group(1))
    m = re.search(r">=?\s*(\d+(?:\.\d+)?)", t)
    if m:
        return float(m.group(1)), None
    return None, None


def fmt(x: Optional[float]) -> str:
    if x is None:
        return ""
    x = round(x, 2)
    return str(int(x)) if x == int(x) else f"{x:g}"


def fmt_rentang(bawah, atas) -> str:
    if bawah is not None and atas is not None:
        return f"{fmt(bawah)} - {fmt(atas)}"
    if atas is not None:
        return f"< {fmt(atas)}"
    if bawah is not None:
        return f"> {fmt(bawah)}"
    return ""


def faktor_konversi(kunci: str, satuan_vendor: str):
    """Return (faktor, catatan|None). faktor None = satuan tidak dikenal -> jangan dipakai."""
    t = TES[kunci]
    s = norm_satuan(satuan_vendor)
    if not t["konversi"]:
        return 1.0, None
    if not s:
        return 1.0, f"satuan tidak tercetak di PDF, diasumsikan {t['satuan']}"
    if s in t["konversi"]:
        return float(t["konversi"][s]), None
    return None, f"satuan '{satuan_vendor}' tidak dikenal utk {t['nama_rscm']}"


def egfr_ckd_epi_2021(kreatinin: float, usia: int, jk: str) -> float:
    k, a = (0.7, -0.241) if jk == "P" else (0.9, -0.302)
    r = kreatinin / k
    e = 142 * (min(r, 1) ** a) * (max(r, 1) ** -1.200) * (0.9938 ** usia)
    return e * 1.012 if jk == "P" else e


def reaktif(teks) -> Optional[bool]:
    t = str(teks or "").lower()
    if any(k in t for k in ("non reaktif", "non-reaktif", "nonreaktif", "negatif", "negative", "non reactive", "non-reactive")):
        return False
    if any(k in t for k in ("reaktif", "positif", "positive", "reactive")):
        return True
    return None


# ---------------------------------------------------------------------------
# Laboratorium darah
# ---------------------------------------------------------------------------

def _terbaru(items: list) -> tuple:
    """Pilih item dgn tanggal terbaru. Return (dipakai, list_riwayat_lama)."""
    urut = sorted(items, key=lambda x: x.get("tanggal") or "", reverse=True)
    return urut[0], urut[1:]


def bangun_lab(ekstrak: dict, usia: int, jk: str):
    """Return (lab_dict_format_ehr, baris_verifikasi, catatan_manual, info_luar_protokol)."""
    kelompok, tidak_dikenal, info = {}, [], []
    for it in ekstrak.get("lab", []):
        kunci, adalah_info = cari_tes(it["nama"])
        if kunci:
            kelompok.setdefault(kunci, []).append(it)
        elif adalah_info:
            info.append(it)
        else:
            tidak_dikenal.append(it)

    lab, verif, catatan = {}, [], []
    tanggal_terbaru = max((x.get("tanggal") or "" for x in ekstrak.get("lab", [])), default="")
    for kunci, items in kelompok.items():
        it, lama = _terbaru(items)
        t = TES[kunci]
        if (it.get("tanggal") or "") < tanggal_terbaru:
            catatan.append(f"PERLU_CEK_MANUAL: {t['nama_rscm']} TIDAK ada di pemeriksaan terbaru ({tanggal_terbaru}) "
                           f"-- dipakai hasil LAMA {it.get('tanggal')} ({it.get('hasil')}). Hapus dari ekstrak "
                           f"kalau hasil lama tidak boleh dipakai.")
        baris = {"vendor_nama": it["nama"], "vendor_hasil": f"{it.get('hasil', '')} {it.get('satuan', '')}".strip(),
                 "vendor_rujukan": it.get("rujukan", ""), "nama_rscm": t["nama_rscm"],
                 "vendor": it.get("vendor", ""), "tanggal": it.get("tanggal", ""),
                 "halaman": f"{it.get('berkas', '')} hal {it.get('halaman', '')}",
                 "dibaca_dari": it.get("dibaca_dari", "teks")}
        if lama:
            baris["riwayat"] = "; ".join(f"{x.get('hasil')} {x.get('satuan', '')} ({x.get('tanggal')})" for x in lama)

        if t["kategori"] == "kualitatif":
            hasil_teks = str(it.get("hasil", "")).strip()
            pos = reaktif(hasil_teks)
            if kunci == "anti_hbs":
                angka = ke_float(it.get("nilai_angka", hasil_teks))
                if angka is not None:
                    pos = angka >= 10
                    hasil_teks = f"{fmt(angka)} {'Reaktif' if pos else 'Non-Reaktif'}"
            lab[t["nama_rscm"]] = {"hasil": hasil_teks, "flag": "*" if pos and kunci == "hbsag" else "",
                                   "satuan": t["satuan"], "rujukan": "", "catatan": ""}
            baris.update(nilai_rscm=hasil_teks, rujukan_dipakai="(kualitatif)", sumber_rujukan="-",
                         flag="*" if pos and kunci == "hbsag" else "")
            verif.append(baris)
            continue

        nilai_v = ke_float(it.get("hasil"))
        faktor, cat_satuan = faktor_konversi(kunci, it.get("satuan", ""))
        if nilai_v is None or faktor is None:
            alasan = cat_satuan or f"hasil '{it.get('hasil')}' bukan angka"
            catatan.append(f"PERLU_CEK_MANUAL: {t['nama_rscm']} dari PDF TIDAK dipakai -- {alasan}")
            baris.update(nilai_rscm="(tidak dipakai)", rujukan_dipakai="", sumber_rujukan="", flag="?")
            verif.append(baris)
            continue
        if cat_satuan:
            catatan.append(f"{t['nama_rscm']}: {cat_satuan}")
        nilai = nilai_v * faktor

        if t["kategori"] == "pedoman":
            rujukan = t["rujukan_pedoman"]
            bawah, atas = parse_rujukan(rujukan)
            sumber = "protokol"
        else:
            b, a = parse_rujukan(it.get("rujukan"))
            bawah = b * faktor if b is not None else None
            atas = a * faktor if a is not None else None
            rujukan = fmt_rentang(bawah, atas)
            sumber = "vendor"
            if not rujukan:
                catatan.append(f"PERLU_CEK_MANUAL: {t['nama_rscm']} -- rujukan vendor tidak terbaca, "
                               f"status normal/abnormal tidak bisa dinilai pakai rujukan lab")
        flag = "H" if atas is not None and nilai > atas else ("L" if bawah is not None and nilai < bawah else "")
        lab[t["nama_rscm"]] = {"hasil": fmt(nilai), "flag": flag, "satuan": t["satuan"],
                               "rujukan": rujukan, "catatan": t.get("catatan_pedoman", "")}
        baris.update(nilai_rscm=f"{fmt(nilai)} {t['satuan']}", rujukan_dipakai=rujukan,
                     sumber_rujukan=sumber, flag=flag)
        verif.append(baris)

    # eGFR dihitung sendiri kalau vendor cuma kasih kreatinin (EHR RSCM selalu punya eGFR)
    if "Kreatinin Darah" in lab and "eGFR" not in lab and usia and usia < 900:
        kr = ke_float(lab["Kreatinin Darah"]["hasil"])
        if kr:
            e = egfr_ckd_epi_2021(kr, usia, jk)
            rujukan = TES["egfr"]["rujukan_pedoman"]
            bawah, _ = parse_rujukan(rujukan)
            flag = "L" if e < bawah else ""
            lab["eGFR"] = {"hasil": fmt(e), "flag": flag, "satuan": TES["egfr"]["satuan"],
                           "rujukan": rujukan, "catatan": "dihitung CKD-EPI 2021 dari kreatinin PDF"}
            verif.append({"vendor_nama": "(dihitung)", "vendor_hasil": "", "vendor_rujukan": "",
                          "nama_rscm": "eGFR", "nilai_rscm": f"{fmt(e)} (CKD-EPI 2021)",
                          "rujukan_dipakai": rujukan, "sumber_rujukan": "protokol", "flag": flag,
                          "vendor": "", "tanggal": "", "halaman": "", "dibaca_dari": "hitung"})

    for it in tidak_dikenal:
        tanda = f" (vendor menandai abnormal: '{it.get('flag_vendor')}')" if it.get("flag_vendor") else ""
        catatan.append(f"PERLU_CEK_MANUAL: nama tes '{it['nama']}' = {it.get('hasil')} {it.get('satuan', '')} "
                       f"belum ada di kamus_lab.py{tanda} -- tambahkan ke kamus supaya bisa dinilai")

    info_luar = []
    for it in info:
        abnormal = bool(it.get("flag_vendor"))
        b, a = parse_rujukan(it.get("rujukan"))
        v = ke_float(it.get("hasil"))
        if v is not None and ((a is not None and v > a) or (b is not None and v < b)):
            abnormal = True
        if not abnormal and reaktif(it.get("hasil")):
            abnormal = True
        if abnormal:
            penting = norm_nama(it["nama"]) in {norm_nama(x) for x in PENTING_KALAU_ABNORMAL}
            teks = f"{it['nama']} = {it.get('hasil')} {it.get('satuan', '')} (rujukan vendor: {it.get('rujukan', '-')})"
            info_luar.append(("PENTING" if penting else "info", teks))
    for tingkat, teks in info_luar:
        if tingkat == "PENTING":
            catatan.append(f"PERLU_CEK_MANUAL: hasil di luar protokol yang BISA memengaruhi kelaikan -- {teks}")
    return lab, verif, catatan, info_luar


# ---------------------------------------------------------------------------
# Urinalisa
# ---------------------------------------------------------------------------

def _positif_dipstick(hasil) -> bool:
    t = str(hasil or "").strip().lower()
    if not t or t in KATA_NEGATIF or t.startswith("negatif") or t.startswith("negative"):
        return False
    return True


def bangun_urin(ekstrak: dict):
    """Return (urin_dict_format_ehr, catatan). Beberapa baris vendor bisa jatuh ke 1 nama
    RSCM (mis. Silinder Hialin + Silinder Lain) -- positif kalau salah satu positif."""
    hasil, catatan = {}, []
    baris_urin = ekstrak.get("urin", [])
    if not baris_urin:
        return {}, []
    terbaru = max((x.get("tanggal") or "" for x in baris_urin), default="")
    for it in baris_urin:
        if (it.get("tanggal") or "") != terbaru:
            continue  # urinalisa lama (PDF tahun lalu) tidak dicampur
        nama = cari_urin(it["nama"])
        if nama is None:
            catatan.append(f"PERLU_CEK_MANUAL: parameter urin '{it['nama']}' = {it.get('hasil')} belum ada di kamus_lab.py")
            continue
        h = str(it.get("hasil", "")).strip()
        bawah, atas = parse_rujukan(it.get("rujukan"))
        flag = ""
        if nama in URIN_SEDIMEN:
            m = maks_rentang(h)
            if atas is None:
                catatan.append(f"PERLU_CEK_MANUAL: urin {it['nama']} = {h} -- rujukan vendor tidak terbaca, "
                               f"tidak bisa dinilai naik/tidak")
            elif m is not None and m > atas:
                flag = "H"
        elif nama == "Urobilinogen":
            v = ke_float(h)
            if v is not None and atas is not None:
                flag = "*" if v > atas else ""
            elif _positif_dipstick(h):
                flag = "*"
        elif nama == "Silinder":
            m = maks_rentang(h)
            if atas is not None and m is not None:
                flag = "*" if m > atas else ""
            elif _positif_dipstick(h):
                flag = "*"
        elif nama in URIN_DIPSTICK and ke_float(h) is not None and atas is not None:
            # Vendor flowcytometry (mis. Fatmawati: Bakteri 122.5 /uL, rujukan <=385.8) --
            # angka dinilai thd rujukan, BUKAN dianggap "positif" krn bukan teks Negatif.
            flag = "*" if ke_float(h) > atas else ""
        elif nama in URIN_DIPSTICK:
            flag = "*" if _positif_dipstick(h) else ""
        angka_vs_rujukan = ke_float(h) is not None and atas is not None and nama not in ("Silinder", "Urobilinogen")
        rujukan_rscm = fmt_rentang(bawah, atas) if angka_vs_rujukan else "Negatif" if nama in URIN_DIPSTICK or nama == "Silinder" else (
            "Normal" if nama == "Urobilinogen" else fmt_rentang(bawah, atas))

        if nama in hasil:  # baris kedua utk nama RSCM yg sama (mis. Kristal Normal + Kristal Abnormal)
            lama = hasil[nama]
            # Teks hasil gabungan HARUS tetap "Negatif" kalau semua negatif -- klasifikasi_urinalisa()
            # menilai positif dari teks hasil != "negatif", jadi teks campuran = salah dianggap positif.
            if flag and not lama["flag"]:
                lama["hasil"] = f"{it['nama']}: {h}"
            elif flag and lama["flag"]:
                lama["hasil"] = f"{lama['hasil']}; {it['nama']}: {h}"
            lama["flag"] = lama["flag"] or flag
        else:
            hasil[nama] = {"hasil": h, "flag": flag, "satuan": it.get("satuan", ""), "rujukan": rujukan_rscm, "catatan": ""}
    return hasil, catatan


# ---------------------------------------------------------------------------
# Radiologi & EKG -> format fase1
# ---------------------------------------------------------------------------

def bangun_radiologi(ekstrak: dict) -> Optional[dict]:
    """Sama logikanya dgn baca_radiologi() fase1_baca.py, tapi dari teks kesimpulan PDF."""
    r = ekstrak.get("radiologi")
    if not r or not r.get("ada"):
        return None
    kes = (r.get("kesimpulan") or "").strip()
    raw = f"Radiologi {r.get('vendor', '')} {r.get('tanggal', '')}\n{r.get('deskripsi', '')}\n[Conclusion]\n{kes}"
    baris_temuan = _baris_temuan_radiologi(kes)
    sudah_dikenal = KATA_KUNCI_TANPA_SARAN_GENERIK + KATA_KUNCI_TULANG
    pengecualian = KATA_KUNCI_ARAH_SP_PARU + KATA_KUNCI_ARAH_PD_PMPK
    belum_dikenal = any(any(k in b.lower() for k in pengecualian) or not any(k in b.lower() for k in sudah_dikenal)
                        for b in baris_temuan)
    if not baris_temuan or ("tidak tampak kelainan" in kes.lower() and not belum_dikenal):
        kesan = "normal"
    else:
        kesan = "ada_temuan_perlu_review"
    return {"kesan": kesan, "section_ada_di_dom": True, "raw_text": raw, "sumber": "pdf"}


def bangun_ekg(ekstrak: dict) -> Optional[dict]:
    e = ekstrak.get("ekg")
    if not e or not e.get("ada"):
        return None
    kesan = "Abnormal" if str(e.get("kesan", "")).lower().startswith("abnormal") else "Normal"
    return {"kelainan_bermakna": e.get("deskripsi", ""), "keterangan_lain": "", "kesan": kesan,
            "tab_ditemukan": True, "sumber": "pdf"}


# ---------------------------------------------------------------------------
# Identitas
# ---------------------------------------------------------------------------

_GELAR = re.compile(r"^(dr|drg|dra|drs|prof|tn|ny|nn|bpk|bp|ibu|sdr|sdri|an|h|hj|ir|mr|mrs|ms|"
                    r"sp\w*|subsp\w*|k|kai|kgh|mkk|mked\w*|msc|mph|mars|phd|dphil|skm|ssi|se|sh|"
                    r"st|skep|ners|amd\w*|spd|mm|mkes|mpd|mt|mba|fisr|finasim|facp|fics|kkv)$")


def token_nama(nama: str) -> list:
    t = unicodedata.normalize("NFKD", nama or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\(.*?\)", " ", t)
    t = re.sub(r"[^a-z\s]", " ", t.replace(".", " ").replace(",", " ").replace("-", " "))
    return [w for w in t.split() if len(w) > 1 and not _GELAR.match(w)]


def skor_nama(a: str, b: str) -> float:
    """Kecocokan nama tanpa gelar, 0..1. Per token cari pasangan terbaik (toleran typo),
    dihitung terhadap nama yang lebih PENDEK (vendor sering menyingkat)."""
    ta, tb = token_nama(a), token_nama(b)
    if not ta or not tb:
        return 0.0
    pendek, panjang = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    total = sum(max(SequenceMatcher(None, w, x).ratio() for x in panjang) for w in pendek)
    return total / len(pendek)


_BULAN = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "may": 5, "jun": 6, "jul": 7,
          "agu": 8, "agt": 8, "aug": 8, "sep": 9, "okt": 10, "oct": 10, "nov": 11, "des": 12, "dec": 12}


def ke_tanggal(teks) -> Optional[date]:
    """'21 Jun 1984' / '1984-06-21' / '21-06-1984' / '07 Januari 1968' -> date."""
    t = str(teks or "").strip().lower()
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", t)
    if m:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.match(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", t)
    if m and m.group(2)[:3] in _BULAN:
        return date(int(m.group(3)), _BULAN[m.group(2)[:3]], int(m.group(1)))
    return None


def cek_identitas(ident_ehr: dict, ident_pdf: dict) -> tuple:
    """Return (status, pesan). status: 'ok' | 'kuning' | 'stop'.
    Nama longgar (gelar diabaikan, dikonfirmasi dr. Vidya), tanggal lahir WAJIB sama."""
    s = skor_nama(ident_ehr.get("nama_raw", ""), ident_pdf.get("nama", ""))
    tl_ehr, tl_pdf = ke_tanggal(ident_ehr.get("tgl_lahir")), ke_tanggal(ident_pdf.get("tgl_lahir"))
    ringkas = (f"EHR '{ident_ehr.get('nama_raw')}' ({ident_ehr.get('tgl_lahir')}) vs "
               f"PDF '{ident_pdf.get('nama')}' ({ident_pdf.get('tgl_lahir')}); skor nama {s:.2f}")
    if ident_pdf.get("nip") and ident_ehr.get("nip") and ident_pdf["nip"] != ident_ehr["nip"]:
        return "stop", f"NIP BEDA (EHR {ident_ehr['nip']} vs PDF {ident_pdf['nip']}) -- {ringkas}"
    if tl_ehr and tl_pdf:
        if tl_ehr != tl_pdf:
            return "stop", f"TANGGAL LAHIR BEDA -- {ringkas}"
        if s >= 0.8:
            return "ok", ringkas
        if s >= 0.5:
            return "kuning", f"Nama hanya mirip sebagian (tgl lahir sama) -- {ringkas}"
        return "stop", f"Nama TIDAK cocok walau tgl lahir sama -- {ringkas}"
    if s >= 0.9:
        return "kuning", f"Tgl lahir tidak bisa dibandingkan, nama cocok -- {ringkas}"
    return "stop", f"Tgl lahir tidak bisa dibandingkan & nama kurang cocok -- {ringkas}"


# ---------------------------------------------------------------------------
# Gabung dengan EHR
# ---------------------------------------------------------------------------

def _ehr_punya(lab_ehr: dict, kunci: str) -> bool:
    for nama, isi in lab_ehr.items():
        if not isinstance(isi, dict):
            continue
        n = nama.lower()
        if any(k in n for k in KUNCI_EHR.get(kunci, [])) and hasil_valid(isi.get("hasil")) and str(isi.get("hasil")).strip():
            return True
    return False


def _kunci_dari_nama_rscm(nama_rscm: str) -> Optional[str]:
    for k, t in TES.items():
        if t["nama_rscm"] == nama_rscm:
            return k
    return None


def gabung(entry_ehr: dict, ekstrak: dict):
    """Return (entry_gabungan, laporan) -- laporan berisi verifikasi, catatan, info, sumber per bagian."""
    e = json.loads(json.dumps(entry_ehr))  # salinan
    ident = e.setdefault("identitas", {})
    usia = ident.get("usia", 999)
    jk = ident.get("jenis_kelamin") or ekstrak.get("identitas_pdf", {}).get("jenis_kelamin") or "P"
    lap = {"sumber": {}, "catatan": [], "verifikasi": [], "info_luar": [], "dipakai_dari_ehr": []}

    # Tanda vital: EHR menang per field
    tv = e.setdefault("tanda_vital", {})
    tv_pdf = dict(ekstrak.get("tanda_vital") or {})
    if "bmi" not in tv_pdf and tv_pdf.get("tinggi_badan") and tv_pdf.get("berat_badan"):
        tb = float(tv_pdf["tinggi_badan"]) / 100
        tv_pdf["bmi"] = round(float(tv_pdf["berat_badan"]) / (tb * tb), 2)
    diisi_pdf = []
    for k, v in tv_pdf.items():
        if v in (None, ""):
            continue
        if ambil_nilai(tv.get(k)) is None:
            tv[k] = {"readonly": None, "editable": str(v), "sumber": "pdf"}
            diisi_pdf.append(k)
    lap["sumber"]["tanda_vital"] = f"PDF mengisi: {', '.join(diisi_pdf)}" if diisi_pdf else "EHR (PDF tidak dipakai)"

    # Lab darah: EHR menang per tes
    lab_ehr = {k: v for k, v in (e.get("laboratorium") or {}).items() if k != "_error"}
    lab_pdf, verif, cat, info = bangun_lab(ekstrak, usia, jk)
    for nama_rscm, isi in lab_pdf.items():
        kunci = _kunci_dari_nama_rscm(nama_rscm)
        if kunci and _ehr_punya(lab_ehr, kunci):
            lap["dipakai_dari_ehr"].append(nama_rscm)
            continue
        lab_ehr[nama_rscm] = isi
    for v in verif:
        if v["nama_rscm"] in lap["dipakai_dari_ehr"]:
            v["catatan"] = "EHR sudah ada -> nilai EHR yang dipakai"
    e["laboratorium"] = lab_ehr
    lap["verifikasi"], lap["info_luar"] = verif, info
    lap["catatan"] += cat
    # Protokol lama diam saja kalau kimia darah tidak ada (dianggap tidak diperiksa).
    # Pasien eksternal sering paket terbatas -> beri tahu dr. Vidya, tapi tidak memblokir.
    tidak_ada = [TES[k]["nama_rscm"] for k in ("hemoglobin", "gdp", "kolesterol", "sgpt", "kreatinin")
                 if not _ehr_punya(lab_ehr, k)]
    if tidak_ada:
        lap["catatan"].append(f"Lab tidak ada di PDF maupun EHR (tidak dinilai, tidak memblokir): {', '.join(tidak_ada)}")

    # Urinalisa: kalau EHR punya panel urin, EHR menang seluruhnya
    urin_ehr = e.get("urinalisa_raw") or {}
    if any(hasil_valid(v.get("hasil")) and str(v.get("hasil")).strip() for v in urin_ehr.values() if isinstance(v, dict)):
        lap["sumber"]["urinalisa"] = "EHR"
    else:
        urin_pdf, cat_u = bangun_urin(ekstrak)
        e["urinalisa_raw"] = urin_pdf
        lap["catatan"] += cat_u
        lap["sumber"]["urinalisa"] = "PDF" if urin_pdf else "tidak ada (belum dilakukan)"
        lap["urin_pdf"] = urin_pdf

    # Radiologi
    radio_ehr = e.get("radiologi") or {}
    if radio_ehr.get("kesan") in ("normal", "ada_temuan_perlu_review"):
        lap["sumber"]["radiologi"] = "EHR"
    else:
        radio_pdf = bangun_radiologi(ekstrak)
        if radio_pdf:
            e["radiologi"] = radio_pdf
            lap["sumber"]["radiologi"] = f"PDF (kesan: {radio_pdf['kesan']})"
        else:
            # Pasien eksternal: tidak ada laporan di EHR maupun PDF = memang belum
            # dilakukan -> "Mohon melengkapi pemeriksaan radiologi" (bukan PERLU_CEK_MANUAL
            # 'section tidak termuat' spt di pipeline lama).
            e["radiologi"] = {"kesan": "belum_dilakukan", "section_ada_di_dom": True, "raw_text": "", "sumber": "tidak ada"}
            lap["sumber"]["radiologi"] = f"tidak ada di EHR (kesan EHR: {radio_ehr.get('kesan')}) maupun PDF -> belum dilakukan"

    # EKG
    ekg_ehr = e.get("ekg_asli") or {}
    if ekg_ehr.get("tab_ditemukan") and ekg_ehr.get("kesan"):
        lap["sumber"]["ekg"] = "EHR"
    else:
        ekg_pdf = bangun_ekg(ekstrak)
        if ekg_pdf:
            e["ekg_asli"] = ekg_pdf
            lap["sumber"]["ekg"] = f"PDF ({ekg_pdf['kesan']}{', ' + ekg_pdf['kelainan_bermakna'] if ekg_pdf['kelainan_bermakna'] else ''})"
        else:
            lap["sumber"]["ekg"] = "tidak ada" + (" (usia <35, tidak wajib)" if usia < 35 else " -> belum dilakukan")

    e["sumber_pdf"] = ekstrak.get("sumber", [])
    return e, lap


def muat_ekstrak(nrm: str) -> dict:
    p = FOLDER_INI / "ekstrak" / f"{nrm}.json"
    if not p.exists():
        raise FileNotFoundError(f"{p} belum ada -- baca PDF dulu dan isi file ini (lihat README.md)")
    return json.loads(p.read_text(encoding="utf-8"))
