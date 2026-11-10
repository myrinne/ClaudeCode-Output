"""MCU SUMMARY builder (step 2 of the MCU Data Analyst pipeline).

Reads the analysis workbook made by mcu_reader.py (RAW + MAP) and adds, in the
same workbook, only Excel formulas:

    DICT_TEMUAN  findings searched in the vendor's Kesimpulan (keywords + exclusions), editable
    DICT_NILAI   categories for free-text values (sex, smoking, spirometry, X-ray, ECG...), editable
    DICT_CUTOFF  cutoffs for the 3-abnormality combination and the age split, editable
    DICT_BERSIH  small approved clean-ups (group typos, Excel-mangled dates), editable; --bersih adds rows
    PEKERJA      one row per worker, same row numbers as RAW: age, group, flags per finding
    SUMMARY      one block per report slide (S3 demographics ... S15 visus)
    CHECK        every SUMMARY cell next to an independent Python recount (must all be SAMA)

Vendor decisions (fitness status, risk, Kesimpulan, interpretations) are used as
written; nothing in RAW is changed. Re-running keeps her edits in the DICT_* sheets.

Usage:
    uv run --with openpyxl python mcu_summary.py "<... - Analisa.xlsx>" --grup bagian [--grup departemen:10] [--cek]

--grup KEY[:N]  grouping column (MAP code) for the per-group tables, N = how many of the largest groups (default 10)
--cek           recalculate with LibreOffice and compare every PEKERJA and SUMMARY formula with Python
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, OrderedDict
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import column_index_from_string as col_index
from openpyxl.utils import get_column_letter as CL

HERE = Path(__file__).resolve().parent
SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
HEAD_FILL = PatternFill("solid", fgColor="1F4E78")
HEAD_FONT = Font(bold=True, color="FFFFFF")
TITLE_FONT = Font(bold=True, size=12, color="1F4E78")
BOLD = Font(bold=True)
YELLOW = PatternFill("solid", fgColor="FFEB9C")
GREY = Font(color="A6A6A6", italic=True)
GREEN = PatternFill("solid", fgColor="C6EFCE")
RED = PatternFill("solid", fgColor="FFC7CE")
PCT = "0.0%"
NOT_CAT = "BELUM DIKATEGORIKAN"
NO_DATA = "Tidak ada data"
OUR_SHEETS = ["DICT_TEMUAN", "DICT_NILAI", "DICT_CUTOFF", "DICT_BERSIH", "PEKERJA", "SUMMARY", "CHECK"]
DATE_VARS = ("tgl_mcu", "tgl_lahir")
BERSIH_ROW0 = 4  # first data row of DICT_BERSIH
PAK_KOSONG = "Tidak ada"  # empty Dugaan PAK cell (her PT. SKP edit 2026-11-10)
N_KATA, N_KECUALI = 10, 4
KOMB = ["Ketiganya", "Rasio TG/HDL + HbA1c", "Rasio TG/HDL + LP", "HbA1c + LP",
        "Hanya rasio TG/HDL", "Hanya HbA1c", "Hanya LP", "Tidak ada", "Data tidak lengkap"]
# category code = ab1*4 + ab2*2 + ab3  -> label (CHOOSE order 0..7)
KOMB_BY_CODE = ["Tidak ada", "Hanya LP", "Hanya HbA1c", "HbA1c + LP",
                "Hanya rasio TG/HDL", "Rasio TG/HDL + LP", "Rasio TG/HDL + HbA1c", "Ketiganya"]


# ================================================================ Excel-equivalent helpers
def xl_trim(v) -> str:
    """Excel TRIM: strip spaces, collapse inner runs of spaces (char 32 only)."""
    if v is None:
        return ""
    if isinstance(v, bool):
        v = "TRUE" if v else "FALSE"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return re.sub(" +", " ", str(v).strip(" "))


def U(v) -> str:
    return xl_trim(v).upper()


def UF(v) -> str:
    """U() with line breaks removed. LibreOffice drops the line break when it reads a single text cell written by
    openpyxl but keeps it inside ranges, so 'LAMA<br>COR' only matches everywhere as 'LAMACOR'."""
    if isinstance(v, str):
        v = v.replace("\r", "").replace("\n", "")
    return U(v)


def xl_uf(ref) -> str:
    """Excel twin of UF()."""
    return f'UPPER(TRIM(SUBSTITUTE(SUBSTITUTE({ref},CHAR(13),""),CHAR(10),"")))'


def is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def q(s) -> str:
    return '"' + str(s).replace('"', '""') + '"'


def datedif_y(a: dt.date, b: dt.date) -> int:
    return b.year - a.year - ((b.month, b.day) < (a.month, a.day))


def xl_serial(d: dt.date) -> int:
    return (d - dt.date(1899, 12, 30)).days


def as_date(v):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    s = str(v).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s[:10]):
        return dt.date(int(s[:4]), int(s[5:7]), int(s[8:10]))
    raise ValueError(f"tanggal '{s}' harus ditulis YYYY-MM-DD")


def bersih_key(var, orig) -> str:
    """Same text as DICT_BERSIH column E: var|serial for dates, var|UPPER(TRIM(text)) otherwise."""
    if var in DATE_VARS:
        return f"{var}|{xl_serial(as_date(orig))}"
    return f"{var}|{U(orig)}"


def read_bersih(wb, cli, reset=False):
    """Cleaning rows [(var, orig, new, reason)]: kept from DICT_BERSIH, then --bersih VAR:ASLI=BERSIH[#alasan] added/overriding."""
    rows = OrderedDict()
    if not reset and "DICT_BERSIH" in wb.sheetnames:
        for r in wb["DICT_BERSIH"].iter_rows(min_row=BERSIH_ROW0, values_only=True):
            if r and r[0] not in (None, "") and r[1] not in (None, "") and r[2] not in (None, ""):
                var = str(r[0]).strip()
                orig = as_date(r[1]) if var in DATE_VARS else str(r[1])
                new = as_date(r[2]) if var in DATE_VARS else str(r[2])
                rows[bersih_key(var, orig)] = (var, orig, new, r[3] or "")
    for item in cli:
        body, _, why = item.partition("#")
        var, _, pair = body.partition(":")
        orig, _, new = pair.partition("=")
        var = var.strip()
        if not var or not orig or not new:
            sys.exit(f"--bersih '{item}': tulis VAR:ASLI=BERSIH, mis. bagian:TAMANAN=TANAMAN atau tgl_mcu:2026-07-10=2026-10-07")
        if var in DATE_VARS:
            orig, new = as_date(orig), as_date(new)
        else:
            orig, new = orig.strip(), new.strip()
        rows[bersih_key(var, orig)] = (var, orig, new, why.strip() or "perbaikan data kotor (disetujui Vidya)")
    return list(rows.values())


# ================================================================ default categorisation rules
def suggest(var: str, v: str) -> str:
    s = v.upper()
    if var == "jk":
        if s in ("M", "L", "LAKI-LAKI", "LAKI LAKI", "PRIA", "MALE", "LK"):
            return "Laki-laki"
        if s in ("F", "P", "PEREMPUAN", "WANITA", "FEMALE", "PR"):
            return "Perempuan"
        return NOT_CAT
    if var == "merokok":
        if "MANTAN" in s or "BERHENTI" in s:
            return "Tidak merokok"  # dua kategori saja (keputusan Vidya 2026-11-08)
        if s.startswith("TIDAK") or s in ("GA", "GAK", "ENGGAK", "NO", "TDK", "-", "N"):
            return "Tidak merokok"
        if s in ("YA", "IYA", "Y", "YES", "AKTIF") or "BATANG" in s or re.search(r"\d", s):
            return "Merokok"
        return NOT_CAT
    if var == "alkohol":
        if s.startswith("TIDAK") or s in ("GA", "GAK", "NO", "TDK", "-", "N"):
            return "Tidak"
        return "Ya"
    if var == "olahraga":
        if "TIDAK RUTIN" in s or "TIDAL RUTIN" in s or "JARANG" in s or "KADANG" in s:
            return "Ya"  # dua kategori saja; tidak rutin tetap berolahraga (Vidya 2026-11-08)
        if s.startswith("TIDAK") or s in ("GA", "GAK", "NO", "TDK", "-", "N"):
            return "Tidak"
        return "Ya"
    if var == "spiro_kesimpulan":
        if s.startswith("NORMAL") or "DALAM BATAS NORMAL" in s:
            return "Normal"
        if "MENOLAK" in s or "TIDAK DILAKUKAN" in s or "TIDAK DIPERIKSA" in s:
            return "Tidak diperiksa"
        if "CAMPUR" in s or "MIXED" in s:
            return "Campuran"
        for word, lab in (("RESTRI", "Restriksi"), ("OBSTRU", "Obstruksi")):
            if word in s:
                for grade, g in (("RINGAN", "ringan"), ("MILD", "ringan"), ("SEDANG", "sedang"),
                                 ("MODERATE", "sedang"), ("BERAT", "berat"), ("SEVERE", "berat")):
                    if grade in s:
                        return f"{lab} {g}"
                return lab
        return NOT_CAT
    if var == "ro_kesimpulan":
        # Normal only when EVERY line is a normal statement: "TB paru lama / Cor dalam batas normal" is a finding
        lines = [x.strip(" .,;") for x in re.split(r"[\r\n]+", s) if x.strip(" .,;")]
        normal = ("NORMAL", "COR DAN PULMO NORMAL", "TIDAK TAMPAK KELAINAN", "FOTO THORAX NORMAL", "THORAX NORMAL")
        organ = r"(?:(?:FOTO|THORAX|THORAKS|PARU|PULMO|COR|JANTUNG|TULANG|TULANG-TULANG|SINUS|DIAFRAGMA|DAN|&|,|/)\s*)+"
        if lines and all(x in normal or re.fullmatch(organ + r"DALAM BATAS NORMAL", x) for x in lines):
            return "Normal"
        if "MENOLAK" in s or "TIDAK DILAKUKAN" in s or "HAMIL" in s:
            return "Tidak diperiksa"
        return "Ada temuan"
    if var == "ekg_kesimpulan":
        if s in ("NORMAL EKG", "NORMAL", "SINUS RHYTHM", "NORMAL SINUS RHYTHM", "SINUS RITME", "SINUS RITMIK",
                 "NORMAL ECG", "DALAM BATAS NORMAL", "SINUS RHYTHM, NORMAL EKG"):
            return "Normal"
        if "TIDAK LAYAK" in s:  # unreadable tracing keeps its own name (Vidya 2026-11-10)
            return "Tidak layak baca"
        if "MENOLAK" in s or "TIDAK DILAKUKAN" in s:
            return "Tidak diperiksa"
        return "Ada temuan"
    if var == "audio_kesimpulan":
        if "NORMAL" in s and "TIDAK NORMAL" not in s:
            return "Normal"
        if "MENOLAK" in s or "TIDAK DILAKUKAN" in s:
            return "Tidak diperiksa"
        return "Ada temuan"
    return NOT_CAT


NILAI_VARS = OrderedDict([
    ("jk", "Jenis kelamin"),
    ("merokok", "Merokok"),
    ("alkohol", "Konsumsi alkohol"),
    ("olahraga", "Olahraga"),
    ("spiro_kesimpulan", "Kesimpulan spirometri"),
    ("ro_kesimpulan", "Kesimpulan rontgen thorax"),
    ("ekg_kesimpulan", "Kesimpulan EKG"),
    ("audio_kesimpulan", "Kesimpulan audiometri"),
])


# ================================================================ reading the analysis workbook
def read_map(wb):
    ws = wb["MAP"]
    rows = list(ws.iter_rows(values_only=True))
    first, last = (int(x) for x in re.findall(r"\d+", str(rows[3][1])))
    hdr_i = next(i for i, r in enumerate(rows) if r and r[0] == "Grup" and r[1] == "Kode variabel")
    hdr = list(rows[hdr_i])
    ki, li, ci_, kor = hdr.index("Kode variabel"), hdr.index("Variabel standar"), hdr.index("Kolom RAW"), \
        hdr.index("Koreksi (huruf kolom / X)")
    cols, labels = {}, {}
    for r in rows[hdr_i + 1:]:
        if not r or not r[ki]:
            continue
        letter = r[ci_]
        fix = str(r[kor]).strip().upper() if r[kor] else ""
        if fix == "X":
            letter = None
        elif re.fullmatch(r"[A-Z]{1,3}", fix):
            letter = fix
        if letter:
            cols[str(r[ki])] = str(letter)
        labels[str(r[ki])] = r[li]
    return first, last, cols, labels


def vendor_headers(wb):
    """MAP code -> the vendor's own header text (column F)."""
    rows = list(wb["MAP"].iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Grup" and r[1] == "Kode variabel")
    return {str(r[1]): str(r[5]).strip() for r in rows[hi + 1:] if r and r[1] and r[5]}


def judul_fitness(header) -> str | None:
    """Vendor 'Status Akhir' is reported under that name, not as fitness/kelaikan (Vidya 2026-11-10)."""
    return "Status Akhir" if header and " ".join(str(header).lower().split()) == "status akhir" else None


def read_existing_dicts(wb, spec, reset=False):
    """Her edits in DICT_* sheets override the JSON defaults (unless reset)."""
    temuan = [dict(t) for t in spec["temuan"]]
    cutoff = {c["key"]: dict(c) for c in spec["cutoff"]}
    nilai: dict[str, dict[str, str]] = {}
    edited = {"DICT_TEMUAN": False, "DICT_CUTOFF": False, "DICT_NILAI": False}
    if reset:
        return temuan, cutoff, nilai, edited
    if "DICT_TEMUAN" in wb.sheetnames:
        rows = list(wb["DICT_TEMUAN"].iter_rows(min_row=4, values_only=True))
        got = []
        for r in rows:
            if not r or not r[0]:
                continue
            got.append({"key": str(r[0]), "label": r[1] or str(r[0]), "topik": r[2] or "Lain-lain",
                        "top_ten": str(r[3] or "").strip().lower() == "ya",
                        "kata": [str(x) for x in r[5:5 + N_KATA] if x not in (None, "")],
                        "kecuali": [str(x) for x in r[5 + N_KATA:5 + N_KATA + N_KECUALI] if x not in (None, "")]})
        if got:
            def sig(ts):
                return [(t["key"], t["label"], t["topik"], bool(t["top_ten"]), list(t["kata"])[:N_KATA],
                         list(t.get("kecuali", []))[:N_KECUALI]) for t in ts]
            edited["DICT_TEMUAN"] = sig(got) != sig(temuan)
            have = {t["key"] for t in got}
            got += [t for t in temuan if t["key"] not in have]  # new findings from temuan_standar.json
            temuan = got
    if "DICT_CUTOFF" in wb.sheetnames:
        for r in wb["DICT_CUTOFF"].iter_rows(min_row=4, values_only=True):
            if r and r[0] in cutoff and is_num(r[3]):
                c0 = cutoff[r[0]]
                if r[3] != c0["nilai"] or (r[4] and r[4] != c0["sumber"]):
                    edited["DICT_CUTOFF"] = True
                c0["nilai"] = r[3]
                c0["sumber"] = r[4] or c0["sumber"]
                if len(r) > 6 and r[5] in ("vendor", "cutoff"):  # older sheets have no basis column
                    if r[5] != c0.get("dasar", "cutoff") or (r[6] or "") != ", ".join(c0.get("temuan_vendor", [])):
                        edited["DICT_CUTOFF"] = True
                    c0["dasar"] = r[5]
                    c0["temuan_vendor"] = [x.strip() for x in str(r[6] or "").split(",") if x.strip()]
    if "DICT_NILAI" in wb.sheetnames:
        cur = None
        for r in wb["DICT_NILAI"].iter_rows(min_row=1, values_only=True):
            if r and isinstance(r[0], str) and r[0].startswith("Variabel: "):
                cur = r[0].split("Variabel: ", 1)[1].split(" ")[0]
                nilai[cur] = {}
                continue
            if cur and r and r[0] not in (None, "", "Nilai (huruf besar, spasi dirapikan)") and r[1]:
                v, cat = str(r[0]), str(r[1])
                asal = r[3] if len(r) > 3 else None
                orig = r[4] if len(r) > 4 else None
                if orig not in (None, ""):
                    if cat == orig:
                        continue  # she kept the script's suggestion: recompute next time
                elif asal == "saran otomatis":
                    continue
                nilai[cur][UF(v)] = cat
                edited["DICT_NILAI"] = True
    return temuan, cutoff, nilai, edited


def date_pattern(values) -> str:
    pats = Counter()
    for v in values:
        if isinstance(v, (dt.datetime, dt.date)):
            pats["serial"] += 1
        elif v is not None:
            s = str(v).strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s[:10]):
                pats["ymd"] += 1
            elif re.fullmatch(r"\d{2}[-/]\d{2}[-/]\d{4}", s[:10]):
                pats["dmy"] += 1
    return pats.most_common(1)[0][0] if pats else "none"


def parse_date(v, pat):
    try:
        if isinstance(v, dt.datetime):
            return v.date()
        if isinstance(v, dt.date):
            return v
        if v is None:
            return None
        s = str(v)
        if pat == "ymd":
            return dt.date(int(s[0:4]), int(s[5:7]), int(s[8:10]))
        if pat == "dmy":
            return dt.date(int(s[6:10]), int(s[3:5]), int(s[0:2]))
    except (ValueError, TypeError):
        return None
    return None


def date_formula(ref, pat):
    if pat == "ymd":
        txt = f"DATE(VALUE(LEFT({ref},4)),VALUE(MID({ref},6,2)),VALUE(MID({ref},9,2)))"
    elif pat == "dmy":
        txt = f"DATE(VALUE(MID({ref},7,4)),VALUE(MID({ref},4,2)),VALUE(LEFT({ref},2)))"
    else:
        txt = '""'
    return f'=IFERROR(IF(ISNUMBER({ref}),{ref},{txt}),"")'


# ================================================================ builder
class Builder:
    def __init__(self, path: Path, grup_args, spec, reset=False, bersih_args=()):
        self.path = path
        self.wb = openpyxl.load_workbook(path)
        self.first, self.last, self.cols, self.labels = read_map(self.wb)
        self.vheader = vendor_headers(self.wb)
        self.bersih = read_bersih(self.wb, bersih_args, reset)
        self.raw_rows = {r: [c.value for c in row] for r, row in
                         enumerate(self.wb["RAW"].iter_rows(min_row=1, max_row=self.last), 1)}
        self.temuan, self.cutoff, self.nilai_edit, self.edited = read_existing_dicts(self.wb, spec, reset)
        self.abaikan = [re.compile(x, re.I) for x in spec.get("abaikan_di_daftar_tinjauan", {}).get("pola", [])]
        self.expected: dict[tuple[str, int, int], object] = {}
        self.cells: dict[str, object] = OrderedDict()
        self.grups = []
        for g in grup_args:
            key, _, n = g.partition(":")
            if key not in self.cols:
                sys.exit(f"--grup {key}: kode ini tidak ada di MAP (atau TIDAK ADA). Kode tersedia: "
                         + ", ".join(k for k in ("departemen", "bagian", "jabatan", "lokasi") if k in self.cols))
            self.grups.append((key, int(n) if n else 10))
        self.rows = list(range(self.first, self.last + 1))
        name_l = self.cols.get("nama")
        if name_l:
            ni = col_index(name_l) - 1
            self.rows = [r for r in self.rows if xl_trim(self.raw(r, ni)) != ""]
        self.N = len(self.rows)
        self.otg = spec.get("obesitas_tanpa_grade") or {}
        self.lp_auto = self.waist_fallback()

    def waist_fallback(self) -> bool:
        """Vendor first; but when the vendor interpreted nobody's waist (0 workers with its finding) while LP values exist,
        use the WHO Asia-Pacific cutoffs (Vidya 2026-11-10, PT. SKP)."""
        c = self.cutoff
        if "lp" not in self.cols or c["lp_l"].get("dasar") != "vendor":
            return False
        tmap = {t["key"]: t for t in self.temuan}
        keys = [k for k in c["lp_l"].get("temuan_vendor", []) if k in tmap]
        if any(flag(tmap[k], self.rv(r, "kesimpulan")) for r in self.rows for k in keys):
            return False
        if not any(is_num(self.rv(r, "lp")) for r in self.rows):
            return False
        for k in ("lp_l", "lp_p"):
            c[k]["dasar"] = "cutoff"
            c[k]["sumber"] = ("OTOMATIS: vendor tidak menafsirkan lingkar perut (0 pekerja dengan temuan obesitas sentral), "
                              "jadi dipakai cutoff WHO Asia-Pasifik / IDF 2005: laki-laki >=90 cm, perempuan >=80 cm (Vidya 2026-11-10).")
        return True

    def raw(self, r, idx):
        row = self.raw_rows.get(r, [])
        return row[idx] if idx < len(row) else None

    def rv(self, r, key):
        L = self.cols.get(key)
        return None if not L else self.raw(r, col_index(L) - 1)

    def exp(self, sheet, row, col, value):
        self.expected[(sheet, row, col)] = value

    # ------------------------------------------------------------ dict sheets
    def write_dicts(self):
        for name in OUR_SHEETS:
            if name in self.wb.sheetnames:
                del self.wb[name]
        # DICT_TEMUAN
        ws = self.wb.create_sheet("DICT_TEMUAN")
        ws["A1"] = ("Temuan dicari di kolom Kesimpulan vendor (RAW kolom " + self.cols.get("kesimpulan", "?") +
                    "). Pekerja dihitung punya temuan bila Kesimpulan mengandung salah satu kata kunci dan tidak "
                    "mengandung kata pengecualian (huruf besar/kecil diabaikan). Edit kata kunci / Top ten di sini, "
                    "simpan, lalu jalankan ulang skrip.")
        ws["A1"].font = BOLD
        ws["A2"] = "Sumber: " + ("hasil edit Anda di sheet ini" if self.edited["DICT_TEMUAN"]
                                 else "temuan_standar.json (default)")
        heads = (["Kode", "Temuan", "Topik", "Top ten (Ya/Tidak)", "Jumlah pekerja (rumus)"]
                 + [f"Kata kunci {i}" for i in range(1, N_KATA + 1)]
                 + [f"Kecuali {i}" for i in range(1, N_KECUALI + 1)])
        self.head(ws, 3, heads)
        self.trow = {}
        for i, t in enumerate(self.temuan):
            r = 4 + i
            self.trow[t["key"]] = r
            ws.cell(row=r, column=1, value=t["key"])
            ws.cell(row=r, column=2, value=t["label"])
            ws.cell(row=r, column=3, value=t["topik"])
            ws.cell(row=r, column=4, value="Ya" if t["top_ten"] else "Tidak")
            for j, k in enumerate(t["kata"][:N_KATA]):
                ws.cell(row=r, column=6 + j, value=k)
            for j, k in enumerate(t.get("kecuali", [])[:N_KECUALI]):
                ws.cell(row=r, column=6 + N_KATA + j, value=k)
        ws.freeze_panes = "C4"
        self.widths(ws, [16, 40, 18, 12, 12] + [18] * (N_KATA + N_KECUALI))

        # DICT_CUTOFF
        wc = self.wb.create_sheet("DICT_CUTOFF")
        wc["A1"] = ("Analisa kombinasi 3 kelainan dan batas kelompok umur. Kolom 'Dasar penilaian': vendor = pakai interpretasi "
                    "vendor di Kesimpulan (temuan di kolom G); cutoff = pakai nilai di kolom D. Kuning = nilai default.")
        wc["A1"].font = BOLD
        self.head(wc, 3, ["Kode", "Parameter", "Operator", "Nilai", "Sumber / catatan", "Dasar penilaian (vendor/cutoff)",
                          "Temuan vendor yang dipakai (kode DICT_TEMUAN)"])
        self.crow = {}
        for i, (k, c) in enumerate(self.cutoff.items()):
            r = 4 + i
            self.crow[k] = r
            wc.cell(row=r, column=1, value=k)
            wc.cell(row=r, column=2, value=c["label"])
            wc.cell(row=r, column=3, value=">=")
            cell = wc.cell(row=r, column=4, value=c["nilai"])
            if str(c["sumber"]).startswith("DEFAULT"):
                cell.fill = YELLOW
            wc.cell(row=r, column=5, value=c["sumber"])
            wc.cell(row=r, column=6, value=c.get("dasar", "cutoff")).fill = YELLOW
            wc.cell(row=r, column=7, value=", ".join(c.get("temuan_vendor", [])))
        self.widths(wc, [12, 30, 9, 9, 90, 16, 34])

        # DICT_NILAI
        wn = self.wb.create_sheet("DICT_NILAI")
        wn["A1"] = ("Kategori untuk isi teks vendor (dibandingkan setelah huruf besar & spasi dirapikan). Kuning = saran "
                    "otomatis skrip, mohon dicek; ubah kolom Kategori bila perlu, lalu jalankan ulang.")
        wn["A1"].font = BOLD
        self.nrange = {}
        self.nmap = {}
        r = 3
        for var, label in NILAI_VARS.items():
            if var not in self.cols:
                continue
            L = self.cols[var]
            idx = col_index(L) - 1
            cnt = Counter(UF(self.raw(rr, idx)) for rr in self.rows)
            values = sorted((v for v in cnt if v != ""), key=lambda v: (-cnt[v], v))
            example = {}  # one-line key -> first original text (line breaks kept, so suggest() can judge each line)
            for rr in self.rows:
                example.setdefault(UF(self.raw(rr, idx)), U(self.raw(rr, idx)))
            prev = self.nilai_edit.get(var, {})
            wn.cell(row=r, column=1, value=f"Variabel: {var} ({label}, RAW kolom {L})").font = TITLE_FONT
            self.head(wn, r + 1, ["Nilai (huruf besar, spasi dirapikan)", "Kategori", "Jumlah pekerja (rumus)", "Asal kategori",
                                  "Saran skrip (jangan diubah)"])
            start = r + 2
            mp = {}
            for i, v in enumerate(values):
                rr_ = start + i
                cat = prev.get(v) or suggest(var, example[v])
                mp[v] = cat
                wn.cell(row=rr_, column=1, value=v)
                c2 = wn.cell(row=rr_, column=2, value=cat)
                if v not in prev:
                    c2.fill = YELLOW
                rng = self.raw_rng(L)
                wn.cell(row=rr_, column=3, value=f"=SUMPRODUCT(--({xl_uf(rng)}=A{rr_}))")
                self.exp("DICT_NILAI", rr_, 3, cnt[v])
                wn.cell(row=rr_, column=4, value="edit Anda" if v in prev else "saran otomatis")
                wn.cell(row=rr_, column=5, value=suggest(var, example[v])).font = Font(color="808080")
            end = start + max(len(values), 1) - 1
            self.nrange[var] = f"DICT_NILAI!$A${start}:$B${end}"
            self.nmap[var] = mp
            r = end + 3
        self.widths(wn, [60, 24, 14, 16, 22])
        self.write_bersih()

    def write_bersih(self):
        """DICT_BERSIH: small, visible clean-ups (typos, Excel-mangled dates). RAW stays untouched."""
        allowed = set(DATE_VARS) | {k for k, _ in self.grups}
        bad = [v for v, *_ in self.bersih if v not in allowed or v not in self.cols]
        if bad:
            sys.exit(f"--bersih/DICT_BERSIH: variabel {', '.join(sorted(set(bad)))} tidak bisa dibersihkan. "
                     f"Yang bisa: kolom --grup ({', '.join(k for k, _ in self.grups)}) dan {', '.join(DATE_VARS)}.")
        wd = self.wb.create_sheet("DICT_BERSIH")
        wd["A1"] = ("Pembersihan data kecil yang disetujui Vidya. File vendor dan RAW tidak diubah; PEKERJA memakai 'Nilai bersih' "
                    "bila isi sel sama dengan 'Nilai asli'.")
        wd["A1"].font = BOLD
        wd["A2"] = ("Tambah baris (Variabel = kode MAP: kolom grup, tgl_mcu, tgl_lahir), simpan, tutup Excel, jalankan ulang mcu_summary.py. "
                    "Tanggal ditulis sebagai tanggal Excel.")
        wd["A2"].font = Font(italic=True, color="595959")
        self.head(wd, BERSIH_ROW0 - 1, ["Variabel", "Nilai asli", "Nilai bersih", "Alasan", "Kunci (rumus, abaikan)",
                                        "Jumlah sel di RAW (rumus)"])
        for i, (var, orig, new, why) in enumerate(self.bersih):
            r = BERSIH_ROW0 + i
            wd.cell(row=r, column=1, value=var)
            c2, c3 = wd.cell(row=r, column=2, value=orig), wd.cell(row=r, column=3, value=new)
            if var in DATE_VARS:
                c2.number_format = c3.number_format = "dd-mm-yyyy"
            wd.cell(row=r, column=4, value=why)
            wd.cell(row=r, column=5, value=f'=A{r}&"|"&IF(ISNUMBER(B{r}),B{r},UPPER(TRIM(B{r})))').font = GREY
            self.exp("DICT_BERSIH", r, 5, bersih_key(var, orig))
            L = self.cols[var]
            idx = col_index(L) - 1
            vals = [self.raw(rr, idx) for rr in range(self.first, self.last + 1)]
            if var in DATE_VARS:
                wd.cell(row=r, column=6, value=f"=COUNTIF({self.raw_rng(L)},B{r})")
                n = sum(1 for v in vals if isinstance(v, (dt.date, dt.datetime)) and as_date(v) == orig)
            else:
                wd.cell(row=r, column=6, value=f"=SUMPRODUCT(--(UPPER(TRIM({self.raw_rng(L)}))=UPPER(TRIM(B{r}))))")
                n = sum(1 for v in vals if U(v) == U(orig))
            self.exp("DICT_BERSIH", r, 6, n)
        end = BERSIH_ROW0 + max(len(self.bersih), 1) - 1
        self.brange = (f"DICT_BERSIH!$C${BERSIH_ROW0}:$C${end}", f"DICT_BERSIH!$E${BERSIH_ROW0}:$E${end}")
        self.bmap = {bersih_key(v, o): n for v, o, n, _ in self.bersih}
        self.widths(wd, [14, 22, 22, 60, 22, 16])

    def f_bersih(self, var, expr):
        """Wrap a PEKERJA expression (no '=') so a DICT_BERSIH match is replaced; unchanged when var has no rows."""
        if not any(v == var for v, *_ in self.bersih):
            return expr
        c, k = self.brange
        out = f'IFERROR(INDEX({c},MATCH("{var}|"&({expr}),{k},0)),{expr})'
        return out if var in DATE_VARS else f"UPPER(TRIM({out}))"

    def v_bersih(self, var, value):
        if value in ("", None):
            return value
        key = bersih_key(var, value)
        if key not in self.bmap:
            return value
        new = self.bmap[key]
        return new if var in DATE_VARS else U(new)

    # ------------------------------------------------------------ PEKERJA
    def write_pekerja(self):
        ws = self.wb.create_sheet("PEKERJA")
        hr = self.first - 1
        ws.cell(row=1, column=1, value="Satu baris per pekerja; nomor baris sama dengan RAW. Semua isi adalah rumus.").font = BOLD
        self.pcol: dict[str, str] = OrderedDict()
        self.pval: dict[str, dict[int, object]] = {}
        heads = []

        def add(key, header, formula_fn, value_fn, fmt=None):
            j = len(self.pcol) + 1
            L = CL(j)
            self.pcol[key] = L
            heads.append(header)
            vals = {}
            for r in self.rows:
                c = ws.cell(row=r, column=j, value=formula_fn(r))
                if fmt:
                    c.number_format = fmt
                v = value_fn(r)
                vals[r] = v
                self.exp("PEKERJA", r, j, v)
            self.pval[key] = vals

        C = self.cols

        def ref(key, r):
            return f"RAW!${C[key]}{r}"

        add("no_mcu", "No MCU", lambda r: f'={ref("no_mcu", r)}&""' if "no_mcu" in C else '=""',
            lambda r: xl_trim_keep(self.rv(r, "no_mcu")) if "no_mcu" in C else "")
        add("nama", "Nama", lambda r: f'={ref("nama", r)}&""', lambda r: xl_trim_keep(self.rv(r, "nama")))

        # sex
        if "jk" in C:
            add("jk", "Jenis kelamin", lambda r: self.f_nilai("jk", ref("jk", r)), lambda r: self.v_nilai("jk", self.rv(r, "jk")))
        # age
        self.pat_mcu = date_pattern([self.rv(r, "tgl_mcu") for r in self.rows]) if "tgl_mcu" in C else "none"
        self.pat_lahir = date_pattern([self.rv(r, "tgl_lahir") for r in self.rows]) if "tgl_lahir" in C else "none"
        if "tgl_mcu" in C:
            add("tgl_mcu", "Tanggal MCU", lambda r: "=" + self.f_bersih("tgl_mcu", date_formula(ref("tgl_mcu", r), self.pat_mcu)[1:]),
                lambda r: self.v_bersih("tgl_mcu", parse_date(self.rv(r, "tgl_mcu"), self.pat_mcu) or ""), "dd-mm-yyyy")
        if "tgl_lahir" in C:
            add("tgl_lahir", "Tanggal lahir", lambda r: "=" + self.f_bersih("tgl_lahir", date_formula(ref("tgl_lahir", r), self.pat_lahir)[1:]),
                lambda r: self.v_bersih("tgl_lahir", parse_date(self.rv(r, "tgl_lahir"), self.pat_lahir) or ""), "dd-mm-yyyy")
        if "tgl_mcu" in C and "tgl_lahir" in C:
            a, b = self.pcol["tgl_lahir"], self.pcol["tgl_mcu"]

            def umur_v(r):
                x, y = self.pval["tgl_lahir"][r], self.pval["tgl_mcu"][r]
                return datedif_y(x, y) if x and y and y >= x else ""
            add("umur", "Umur (tahun)", lambda r: f'=IFERROR(IF(OR({a}{r}="",{b}{r}=""),"",DATEDIF({a}{r},{b}{r},"y")),"")', umur_v)
        elif "umur" in C:
            add("umur", "Umur (tahun)", lambda r: f'=IF(ISNUMBER({ref("umur", r)}),{ref("umur", r)},"")',
                lambda r: self.rv(r, "umur") if is_num(self.rv(r, "umur")) else "")
        if "umur" in self.pcol:
            u = self.pcol["umur"]
            cut = f"DICT_CUTOFF!$D${self.crow['umur_batas']}"
            cv = self.cutoff["umur_batas"]["nilai"]
            self.lab_tua, self.lab_muda = f">={fmt_num(cv)} tahun", f"<{fmt_num(cv)} tahun"
            add("kel_umur", "Kelompok umur",
                lambda r: f'=IF({u}{r}="","{NO_DATA}",IF({u}{r}>={cut},">="&{cut}&" tahun","<"&{cut}&" tahun"))',
                lambda r: NO_DATA if self.pval["umur"][r] == "" else (self.lab_tua if self.pval["umur"][r] >= cv else self.lab_muda))
        # groups
        for key, _ in self.grups:
            add("grp_" + key, f"Grup: {key}", lambda r, k=key: "=" + self.f_bersih(k, f"UPPER(TRIM({ref(k, r)}))"),
                lambda r, k=key: self.v_bersih(k, U(self.rv(r, k))))
        # vendor decisions as written
        for key, head in (("fitness", f"{judul_fitness(self.vheader.get('fitness')) or 'Status kelaikan'} (vendor)"),
                          ("risiko", "Risiko kesehatan (vendor)"), ("dugaan_pak", "Dugaan PAK (vendor)")):
            if key in C:
                add(key, head, lambda r, k=key: f"=UPPER(TRIM({ref(k, r)}))", lambda r, k=key: U(self.rv(r, k)))
        # categorised text values
        for var in ("merokok", "alkohol", "olahraga", "spiro_kesimpulan", "ro_kesimpulan", "ekg_kesimpulan", "audio_kesimpulan"):
            if var in C:
                add(var, NILAI_VARS[var], lambda r, v=var: self.f_nilai(v, ref(v, r)), lambda r, v=var: self.v_nilai(v, self.rv(r, v)))
        # findings from Kesimpulan
        K = C.get("kesimpulan")
        if not K:
            sys.exit("Kolom kesimpulan tidak ada di MAP: temuan tidak bisa dihitung.")
        def kwr(key, col0, n):
            dr = self.trow[key]
            return f"DICT_TEMUAN!${CL(col0)}${dr}:${CL(col0 + n - 1)}${dr}"

        def hits(rng, r):
            return f'SUMPRODUCT(ISNUMBER(SEARCH({rng},TRIM(RAW!${K}{r})&" "))*({rng}<>""))'

        tmap = {t["key"]: t for t in self.temuan}
        lp_cut = self.cutoff["lp_l"].get("dasar") == "cutoff" and "lp" in C and "jk" in self.pcol
        imt_rule = self.otg.get("imt", {}) if ("imt" in C and all(k in tmap for k in ("obes1", "obes2"))) else {}
        jL = self.pcol.get("jk")

        def extra(t):
            """Extra (formula, value) conditions beyond the keywords, or None."""
            key = t["key"]
            if key == "obes_sentral" and lp_cut:
                c_l, c_p = (f"DICT_CUTOFF!$D${self.crow[k]}" for k in ("lp_l", "lp_p"))
                v_l, v_p = self.cutoff["lp_l"]["nilai"], self.cutoff["lp_p"]["nilai"]

                def fv(r):
                    lp, jk = self.rv(r, "lp"), self.pval["jk"][r]
                    return is_num(lp) and ((jk == "Laki-laki" and lp >= v_l) or (jk == "Perempuan" and lp >= v_p))
                return (lambda r: f'AND(ISNUMBER({ref("lp", r)}),OR(AND({jL}{r}="Laki-laki",{ref("lp", r)}>={c_l}),'
                                  f'AND({jL}{r}="Perempuan",{ref("lp", r)}>={c_p})))'), fv
            if key in imt_rule:
                lo, hi = imt_rule[key]
                gen = "{" + ",".join(q(w) for w in self.otg["kata"]) + "}"
                n1, n2 = kwr("obes1", 6, N_KATA), kwr("obes2", 6, N_KATA)
                words = [w.lower() for w in self.otg["kata"]]
                numbered = [w.lower() for k in ("obes1", "obes2") for w in tmap[k]["kata"] if w]

                def fv(r):
                    s = xl_trim(self.rv(r, "kesimpulan")).lower() + " "
                    imt = self.rv(r, "imt")
                    return (any(w in s for w in words) and not any(w in s for w in numbered) and is_num(imt)
                            and imt >= lo and (hi is None or imt < hi))
                return (lambda r: f'AND(SUMPRODUCT(--ISNUMBER(SEARCH({gen},TRIM(RAW!${K}{r})&" ")))>0,{hits(n1, r)}+{hits(n2, r)}=0,'
                                  f'ISNUMBER({ref("imt", r)}),{ref("imt", r)}>={lo}' + (f',{ref("imt", r)}<{hi}' if hi else "") + ")"), fv
            return None

        for t in self.temuan:
            kw, ex = kwr(t["key"], 6, N_KATA), kwr(t["key"], 6 + N_KATA, N_KECUALI)
            base = lambda r, kw=kw, ex=ex: f"AND({hits(kw, r)}>0,{hits(ex, r)}=0)"  # noqa: E731
            ext = extra(t)
            if ext:
                fx, vx = ext
                add("t_" + t["key"], t["label"], lambda r, base=base, fx=fx: f"=IF(OR({base(r)},{fx(r)}),1,0)",
                    lambda r, t=t, vx=vx: int(bool(flag(t, self.rv(r, "kesimpulan")) or vx(r))))
            else:
                add("t_" + t["key"], t["label"], lambda r, base=base: f"=IF({base(r)},1,0)",
                    lambda r, t=t: flag(t, self.rv(r, "kesimpulan")))
        # any finding per topic
        topics = list(OrderedDict.fromkeys(t["topik"] for t in self.temuan))
        self.topics = topics
        for tp in topics:
            keys = [t["key"] for t in self.temuan if t["topik"] == tp]
            Ls = [self.pcol["t_" + k] for k in keys]
            add("tp_" + tp, f"Salah satu temuan: {tp}",
                lambda r, Ls=Ls: "=IF(" + "+".join(f"{L}{r}" for L in Ls) + ">0,1,0)",
                lambda r, keys=keys: 1 if any(self.pval["t_" + k][r] for k in keys) else 0)
        # 3-abnormality combination
        self.has_komb = all(k in C for k in ("tg", "hdl", "hba1c", "lp")) and "jk" in self.pcol
        if self.has_komb:
            c_r, c_a, c_l, c_p = (f"DICT_CUTOFF!$D${self.crow[k]}" for k in ("tg_hdl", "hba1c", "lp_l", "lp_p"))
            v_r, v_a, v_l, v_p = (self.cutoff[k]["nilai"] for k in ("tg_hdl", "hba1c", "lp_l", "lp_p"))

            def ratio_v(r):
                tg, hdl = self.rv(r, "tg"), self.rv(r, "hdl")
                return tg / hdl if is_num(tg) and is_num(hdl) and hdl > 0 else ""
            add("rasio", "Rasio TG/HDL",
                lambda r: f'=IF(AND(ISNUMBER({ref("tg", r)}),ISNUMBER({ref("hdl", r)})),IF({ref("hdl", r)}>0,{ref("tg", r)}/{ref("hdl", r)},""),"")',
                ratio_v, "0.00")
            rL = self.pcol["rasio"]
            add("ab1", "Abnormal 1: rasio TG/HDL", lambda r: f'=IF({rL}{r}="","",IF({rL}{r}>={c_r},1,0))',
                lambda r: "" if self.pval["rasio"][r] == "" else int(self.pval["rasio"][r] >= v_r))
            m_a = f"DICT_CUTOFF!$F${self.crow['hba1c']}"
            f_a = self.vendor_sum("hba1c")

            def ab2_v(r):
                h = self.rv(r, "hba1c")
                if not is_num(h):
                    return ""
                if self.cutoff["hba1c"].get("dasar") == "vendor":
                    return self.vendor_flag("hba1c", r)
                return int(h >= v_a)
            add("ab2", "Abnormal 2: HbA1c",
                lambda r: (f'=IF(ISNUMBER({ref("hba1c", r)}),IF({m_a}="vendor",IF({f_a(r)}>0,1,0),'
                           f'IF({ref("hba1c", r)}>={c_a},1,0)),"")'), ab2_v)
            jL = self.pcol["jk"]

            m_l = f"DICT_CUTOFF!$F${self.crow['lp_l']}"
            f_l = self.vendor_sum("lp_l")

            def ab3_v(r):
                lp, jk = self.rv(r, "lp"), self.pval["jk"][r]
                if not is_num(lp) or jk not in ("Laki-laki", "Perempuan"):
                    return ""
                if self.cutoff["lp_l"].get("dasar") == "vendor":
                    return self.vendor_flag("lp_l", r)
                return int(lp >= (v_l if jk == "Laki-laki" else v_p))
            lp_head = ("Abnormal 3: lingkar perut (interpretasi vendor)" if self.cutoff["lp_l"].get("dasar") == "vendor" else
                       f"Abnormal 3: lingkar perut abnormal (cutoff L >= {v_l} / P >= {v_p} cm, DICT_CUTOFF)")
            add("ab3", lp_head,
                lambda r: (f'=IF(AND(ISNUMBER({ref("lp", r)}),OR({jL}{r}="Laki-laki",{jL}{r}="Perempuan")),'
                           f'IF({m_l}="vendor",IF({f_l(r)}>0,1,0),'
                           f'IF({ref("lp", r)}>=IF({jL}{r}="Laki-laki",{c_l},{c_p}),1,0)),"")'), ab3_v)
            a1, a2, a3 = self.pcol["ab1"], self.pcol["ab2"], self.pcol["ab3"]
            choose = ",".join(q(x) for x in KOMB_BY_CODE)

            def komb_v(r):
                x, y, z = self.pval["ab1"][r], self.pval["ab2"][r], self.pval["ab3"][r]
                if "" in (x, y, z):
                    return "Data tidak lengkap"
                return KOMB_BY_CODE[x * 4 + y * 2 + z]
            add("komb", "Kombinasi 3 kelainan",
                lambda r: f'=IF(OR({a1}{r}="",{a2}{r}="",{a3}{r}=""),"Data tidak lengkap",CHOOSE({a1}{r}*4+{a2}{r}*2+{a3}{r}+1,{choose}))',
                komb_v)

        self.head(ws, hr, heads)
        ws.freeze_panes = ws.cell(row=hr + 1, column=3)
        for j in range(1, len(heads) + 1):
            ws.column_dimensions[CL(j)].width = 14
        ws.column_dimensions["B"].width = 28
        self.ws_p = ws

    def vendor_keys(self, ckey):
        return [k for k in self.cutoff[ckey].get("temuan_vendor", []) if "t_" + k in self.pcol]

    def vendor_sum(self, ckey):
        keys = self.vendor_keys(ckey)
        return lambda r: ("+".join(f"{self.pcol['t_' + k]}{r}" for k in keys) or "0")

    def vendor_flag(self, ckey, r):
        return int(any(self.pval["t_" + k][r] for k in self.vendor_keys(ckey)))

    def f_nilai(self, var, ref):
        return (f'=IF(TRIM({ref})="","{NO_DATA}",IFERROR(VLOOKUP({xl_uf(ref)},{self.nrange[var]},2,FALSE),"{NOT_CAT}"))')

    def v_nilai(self, var, v):
        s = UF(v)
        if s == "":
            return NO_DATA
        return self.nmap[var].get(s, NOT_CAT)

    def prng(self, key):
        L = self.pcol[key]
        return f"PEKERJA!${L}${self.first}:${L}${self.last}"

    def raw_rng(self, L):
        return f"RAW!${L}${self.first}:${L}${self.last}"

    # ------------------------------------------------------------ SUMMARY
    def write_summary(self):
        ws = self.wb.create_sheet("SUMMARY")
        self.ws_s = ws
        self.r = 1
        src = self.wb["MAP"]["B1"].value
        ws["A1"] = "SUMMARY analisa MCU: setiap angka di sheet ini adalah rumus (klik sel untuk melihat asalnya)."
        ws["A1"].font = Font(bold=True, size=13)
        ws["A2"] = f"Sumber: {src}"
        ws["A3"] = "Jumlah pekerja (N)"
        ws["A3"].font = BOLD
        ws["C3"] = f'=SUMPRODUCT(--({self.prng("nama")}<>""))'
        self.exp("SUMMARY", 3, 3, self.N)
        self.cells["N"] = "SUMMARY!C3"
        self.Nref = "SUMMARY!$C$3"
        self.r = 5
        self.block_demografi()
        self.block_kelaikan()
        self.block_semua_temuan()
        self.block_top_ten()
        for key, n in self.grups:
            self.block_grup(key, n)
        if self.has_komb:
            self.block_kombinasi()
        self.block_topik()
        self.block_kategori()
        self.widths(ws, [8, 46, 12, 10, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12])

    # helpers ------------------------------------------------------
    def title(self, text, note=None):
        ws = self.ws_s
        self.r += 1
        ws.cell(row=self.r, column=1, value=text).font = TITLE_FONT
        if note:
            ws.cell(row=self.r + 1, column=1, value=note).font = Font(italic=True, color="595959")
            self.r += 1
        self.r += 1

    def set(self, row, col, formula, value, fmt=None):
        c = self.ws_s.cell(row=row, column=col, value=formula)
        if fmt:
            c.number_format = fmt
        self.exp("SUMMARY", row, col, value)
        return c

    def count_table(self, block, label_head, items, denom_ref, denom_val):
        """items: list of (label, formula, value). Writes No | label | Jumlah | %."""
        ws = self.ws_s
        self.head(ws, self.r, ["No", label_head, "Jumlah", "%"])
        start = self.r + 1
        for i, (lab, f, v) in enumerate(items, 1):
            rr = self.r + i
            ws.cell(row=rr, column=1, value=i)
            ws.cell(row=rr, column=2, value=lab)
            self.set(rr, 3, f, v)
            self.set(rr, 4, f"=IFERROR(C{rr}/{denom_ref},0)", (v / denom_val) if denom_val else 0, PCT)
        self.cells[block] = f"SUMMARY!A{start}:D{start + len(items) - 1}"
        self.r += len(items) + 2

    def cat_items(self, key, labels):
        rng = self.prng(key)
        return [(lab, f"=SUMPRODUCT(--({rng}={q(lab)}))", sum(1 for r in self.rows if self.pval[key][r] == lab))
                for lab in labels]

    # blocks -------------------------------------------------------
    def block_demografi(self):
        ws = self.ws_s
        self.title("S3. Karakteristik demografi pekerja")
        if "tgl_mcu" in self.pcol:
            rng = self.prng("tgl_mcu")
            dates = [self.pval["tgl_mcu"][r] for r in self.rows if self.pval["tgl_mcu"][r]]
            ws.cell(row=self.r, column=2, value="Tanggal MCU pertama")
            self.set(self.r, 3, f"=MIN({rng})", min(dates), "dd-mm-yyyy")
            ws.cell(row=self.r + 1, column=2, value="Tanggal MCU terakhir")
            self.set(self.r + 1, 3, f"=MAX({rng})", max(dates), "dd-mm-yyyy")
            self.cells["S3_periode"] = f"SUMMARY!C{self.r}:C{self.r + 1}"
            self.r += 3
        if "umur" in self.pcol:
            rng = self.prng("umur")
            ages = [self.pval["umur"][r] for r in self.rows if self.pval["umur"][r] != ""]
            for lab, f, v, fm in (("Umur rata-rata (tahun)", f"=AVERAGE({rng})", sum(ages) / len(ages), "0.0"),
                                  ("Umur termuda", f"=MIN({rng})", min(ages), "0"),
                                  ("Umur tertua", f"=MAX({rng})", max(ages), "0")):
                ws.cell(row=self.r, column=2, value=lab)
                self.set(self.r, 3, f, v, fm)
                self.r += 1
            self.cells["S3_umur_ringkas"] = f"SUMMARY!B{self.r - 3}:C{self.r - 1}"
            self.r += 1
            self.count_table("S3_kelompok_umur", "Kelompok umur",
                             self.cat_items("kel_umur", [self.lab_muda, self.lab_tua, NO_DATA]), self.Nref, self.N)
        if "jk" in self.pcol:
            labs = ["Laki-laki", "Perempuan"] + [x for x in (NO_DATA, NOT_CAT) if any(self.pval["jk"][r] == x for r in self.rows)]
            self.count_table("S3_jenis_kelamin", "Jenis kelamin", self.cat_items("jk", labs), self.Nref, self.N)
        for var in ("merokok", "alkohol", "olahraga"):
            if var in self.pcol:
                labs = list(OrderedDict.fromkeys(self.nmap[var].values()))
                labs += [x for x in (NO_DATA, NOT_CAT) if x not in labs and any(self.pval[var][r] == x for r in self.rows)]
                self.count_table(f"S3_{var}", NILAI_VARS[var], self.cat_items(var, labs), self.Nref, self.N)
            else:
                ws.cell(row=self.r, column=2, value=f"{NILAI_VARS[var]}: kolom tidak ada di data vendor").font = Font(italic=True)
                self.r += 2

    def block_kelaikan(self):
        jf = judul_fitness(self.vheader.get("fitness"))
        for key, block, title, kosong in (
                ("fitness", "kelaikan_fitness", f"{jf or 'Status kelaikan kerja'} (keputusan vendor, apa adanya)", "(kosong)"),
                ("risiko", "kelaikan_risiko", "Risiko kesehatan (keputusan vendor, apa adanya)", "(kosong)"),
                ("dugaan_pak", "pak_dugaan", "Dugaan penyakit akibat kerja / PAK (kolom vendor, apa adanya)", PAK_KOSONG)):
            if key not in self.pcol:
                continue
            self.title(title)
            cnt = Counter(self.pval[key][r] for r in self.rows)
            labs = sorted((v for v in cnt if v != ""), key=lambda v: (-cnt[v], v)) + ([""] if cnt.get("") else [])
            items = self.cat_items(key, labs)
            items = [(lab if lab else kosong, f, v) for lab, f, v in items]
            self.count_table(block, "Kategori", items, self.Nref, self.N)
        self.judul_fitness = jf or "Status kelaikan kerja"

    def block_semua_temuan(self):
        ws = self.ws_s
        self.title("Semua temuan dari Kesimpulan vendor (dasar Top Ten dan tabel per topik)",
                   "Kolom abu-abu 'Bantu urutan' hanya dipakai rumus untuk mengurutkan Top Ten (jumlah dikurangi sedikit "
                   "supaya dua temuan dengan jumlah sama tidak bentrok); tidak masuk PPT.")
        self.head(ws, self.r, ["No", "Temuan", "Jumlah", "%", "Topik", "Top ten", "Bantu urutan (abaikan)"])
        self.trow_s = {}
        start = self.r + 1
        self.tot = {}
        for i, t in enumerate(self.temuan, 1):
            rr = self.r + i
            dr = self.trow[t["key"]]
            self.trow_s[t["key"]] = rr
            ws.cell(row=rr, column=1, value=i)
            self.set(rr, 2, f"=DICT_TEMUAN!B{dr}", t["label"])
            total = sum(self.pval["t_" + t["key"]][r] for r in self.rows)
            self.tot[t["key"]] = total
            self.set(rr, 3, f"=SUM({self.prng('t_' + t['key'])})", total)
            self.set(rr, 4, f"=IFERROR(C{rr}/{self.Nref},0)", total / self.N if self.N else 0, PCT)
            self.set(rr, 5, f"=DICT_TEMUAN!C{dr}", t["topik"])
            self.set(rr, 6, f"=DICT_TEMUAN!D{dr}", "Ya" if t["top_ten"] else "Tidak")
            self.set(rr, 7, f'=IF(F{rr}="Ya",C{rr}-A{rr}/1000,-1)', (total - i / 1000) if t["top_ten"] else -1).font = GREY
            self.wb["DICT_TEMUAN"].cell(row=dr, column=5, value=f"=SUMMARY!C{rr}")
            self.exp("DICT_TEMUAN", dr, 5, total)
        end = start + len(self.temuan) - 1
        self.all_rng = (start, end)
        self.cells["semua_temuan"] = f"SUMMARY!A{start}:G{end}"
        self.r = end + 2

    def block_top_ten(self):
        ws = self.ws_s
        self.title("S4. Top ten penyakit dan temuan (% dari total peserta MCU)")
        s, e = self.all_rng
        sk, lb, ct = f"$G${s}:$G${e}", f"$B${s}:$B${e}", f"$C${s}:$C${e}"
        scores = sorted(((self.tot[t["key"]] - i / 1000, t) for i, t in enumerate(self.temuan, 1) if t["top_ten"]),
                        key=lambda x: -x[0])
        self.head(ws, self.r, ["No", "Jenis penyakit / temuan", "Jumlah", "% (dari total peserta MCU)"])
        start = self.r + 1
        for k in range(1, 11):
            rr = self.r + k
            ws.cell(row=rr, column=1, value=k)
            ok = k <= len(scores)
            self.set(rr, 2, f'=IF(LARGE({sk},{k})<0,"-",INDEX({lb},MATCH(LARGE({sk},{k}),{sk},0)))',
                     scores[k - 1][1]["label"] if ok else "-")
            v = self.tot[scores[k - 1][1]["key"]] if ok else 0
            self.set(rr, 3, f'=IF(LARGE({sk},{k})<0,0,INDEX({ct},MATCH(LARGE({sk},{k}),{sk},0)))', v)
            self.set(rr, 4, f"=IFERROR(C{rr}/{self.Nref},0)", v / self.N if self.N else 0, PCT)
        self.cells["S4_top_ten"] = f"SUMMARY!A{start}:D{start + 9}"
        self.r = start + 11

    def block_grup(self, key, topn):
        ws = self.ws_s
        gkey = "grp_" + key
        label = self.labels.get(key, key)
        self.title(f"S5. Temuan per {label} ({topn} {label.lower()} terbesar)",
                   f"Grup = isi kolom {label} dengan huruf besar/kecil dan spasi disamakan; '-' dan kosong tidak dirangking.")
        cnt = Counter(self.pval[gkey][r] for r in self.rows)
        groups = sorted(cnt, key=lambda g: (-cnt[g], g))
        # list of all groups with size and score
        self.head(ws, self.r, ["No", f"{label} (semua)", "Jumlah pekerja", "%", "Bantu urutan (abaikan)"])
        gs = self.r + 1
        pr = self.prng(gkey)
        for i, g in enumerate(groups, 1):
            rr = self.r + i
            ws.cell(row=rr, column=1, value=i)
            ws.cell(row=rr, column=2, value=g if g else "(kosong)")
            self.set(rr, 3, f'=SUMPRODUCT(--({pr}={q(g)}))', cnt[g])
            self.set(rr, 4, f"=IFERROR(C{rr}/{self.Nref},0)", cnt[g] / self.N, PCT)
            valid = g not in ("", "-")
            self.set(rr, 5, f'=IF(OR(B{rr}="-",B{rr}="(kosong)"),-1,C{rr}-A{rr}/10000)', (cnt[g] - i / 10000) if valid else -1).font = GREY
        ge = gs + len(groups) - 1
        self.cells[f"S5_{key}_semua_grup"] = f"SUMMARY!A{gs}:D{ge}"
        self.r = ge + 2
        ranked = sorted(((cnt[g] - i / 10000, g) for i, g in enumerate(groups, 1) if g not in ("", "-")), key=lambda x: -x[0])
        topn = min(topn, len(ranked))
        top = [g for _, g in ranked[:topn]]
        # matrix: rank x finding counts
        sk, lb, sz = f"$E${gs}:$E${ge}", f"$B${gs}:$B${ge}", f"$C${gs}:$C${ge}"
        ws.cell(row=self.r, column=1, value=f"Matriks jumlah temuan per {label} (bantu)").font = BOLD
        self.r += 1
        heads = ["Rank", label, "Jumlah pekerja"] + [t["label"] for t in self.temuan]
        self.head(ws, self.r, heads)
        ms = self.r + 1
        self.mat = {}
        for k in range(1, topn + 1):
            rr = self.r + k
            g = top[k - 1] if k <= len(top) else ""
            ws.cell(row=rr, column=1, value=k)
            self.set(rr, 2, f'=IFERROR(IF(LARGE({sk},{k})<0,"",INDEX({lb},MATCH(LARGE({sk},{k}),{sk},0))),"")', g)
            self.set(rr, 3, f'=IF(B{rr}="",0,INDEX({sz},MATCH(B{rr},{lb},0)))', cnt[g] if g else 0)
            for j, t in enumerate(self.temuan):
                c = 4 + j
                v = sum(self.pval["t_" + t["key"]][r] for r in self.rows if self.pval[gkey][r] == g) if g else 0
                self.set(rr, c, f'=IF($B{rr}="",0,SUMPRODUCT(({pr}=$B{rr})*{self.prng("t_" + t["key"])}))', v)
                self.mat[(k, j)] = v
        me = ms + topn - 1
        self.r = me + 2
        # score matrix (helper) to the right
        sc0 = 4 + len(self.temuan) + 1
        ws.cell(row=ms - 2, column=sc0, value="Skor bantu (jumlah - kolom/1000; -1 bila 0 atau bukan Top ten)").font = BOLD
        top_flags = {j: t["top_ten"] for j, t in enumerate(self.temuan)}
        for k in range(1, topn + 1):
            rr = ms + k - 1
            for j, t in enumerate(self.temuan):
                c = sc0 + j
                srow = self.trow_s[t["key"]]
                cntcell = f"{CL(4 + j)}{rr}"
                v = (self.mat[(k, j)] - (j + 1) / 1000) if (top_flags[j] and self.mat[(k, j)] > 0) else -1
                self.set(rr, c, f'=IF(AND($F${srow}="Ya",{cntcell}>0),{cntcell}-{j + 1}/1000,-1)', v).font = GREY
        # top 3 per group
        ws.cell(row=self.r, column=1, value=f"Top 3 temuan per {label} (% dari jumlah pekerja di grup)").font = BOLD
        self.r += 1
        self.head(ws, self.r, ["No", label, "Jenis penyakit / temuan", "Jumlah", "% (dari grup)"])
        ts = self.r + 1
        names = f"${CL(4)}${ms - 1}:${CL(3 + len(self.temuan))}${ms - 1}"
        n = 0
        for k in range(1, topn + 1):
            rr_m = ms + k - 1
            srow_rng = f"${CL(sc0)}${rr_m}:${CL(sc0 + len(self.temuan) - 1)}${rr_m}"
            crow_rng = f"${CL(4)}${rr_m}:${CL(3 + len(self.temuan))}${rr_m}"
            scores = sorted(((self.mat[(k, j)] - (j + 1) / 1000, j) for j in range(len(self.temuan))
                             if top_flags[j] and self.mat[(k, j)] > 0), key=lambda x: -x[0])
            g = top[k - 1] if k <= len(top) else ""
            for p in range(1, 4):
                n += 1
                rr = self.r + n
                ws.cell(row=rr, column=1, value=n)
                self.set(rr, 2, f"=$B${rr_m}", g)
                has = p <= len(scores)
                lab = self.temuan[scores[p - 1][1]]["label"] if has else "-"
                v = self.mat[(k, scores[p - 1][1])] if has else 0
                self.set(rr, 3, f'=IF(LARGE({srow_rng},{p})<0,"-",INDEX({names},MATCH(LARGE({srow_rng},{p}),{srow_rng},0)))', lab)
                self.set(rr, 4, f'=IF(LARGE({srow_rng},{p})<0,0,INDEX({crow_rng},MATCH(LARGE({srow_rng},{p}),{srow_rng},0)))', v)
                size = cnt[g] if g else 0
                self.set(rr, 5, f"=IFERROR(D{rr}/$C${rr_m},0)", v / size if size else 0, PCT)
        self.cells[f"S5_{key}_top3"] = f"SUMMARY!A{ts}:E{ts + n - 1}"
        self.cells[f"S5_{key}_matriks"] = f"SUMMARY!A{ms - 1}:{CL(3 + len(self.temuan))}{me}"
        self.r = ts + n + 1
        self.top_groups = getattr(self, "top_groups", {})
        self.top_groups[key] = (top, ms)

    def block_kombinasi(self):
        ws = self.ws_s
        c = self.cutoff
        def basis(k, cut_txt):
            if c[k].get("dasar") == "vendor":
                labs = [t["label"] for t in self.temuan if t["key"] in c[k].get("temuan_vendor", [])]
                return "interpretasi vendor (" + " / ".join(labs) + ")"
            return cut_txt
        self.title("S6. Analisa 3 kategori kelainan (rasio TG/HDL, HbA1c, lingkar perut)",
                   f"Abnormal 1 rasio TG/HDL: {basis('tg_hdl', '>= ' + fmt_num(c['tg_hdl']['nilai']))}; "
                   f"abnormal 2 HbA1c: {basis('hba1c', '>= ' + fmt_num(c['hba1c']['nilai']) + '%')}; "
                   f"abnormal 3 lingkar perut: {basis('lp_l', '>= ' + fmt_num(c['lp_l']['nilai']) + ' cm (L) / >= ' + fmt_num(c['lp_p']['nilai']) + ' cm (P)')}. "
                   "Dasar penilaian diatur di DICT_CUTOFF. % dihitung dari pekerja yang ketiga nilainya terukur.")
        kv = Counter(self.pval["komb"][r] for r in self.rows)
        lengkap = self.N - kv.get("Data tidak lengkap", 0)
        ws.cell(row=self.r, column=2, value="Pekerja dengan data lengkap (ketiga parameter)")
        lr = self.r
        rng = self.prng("komb")
        self.set(lr, 3, f'=SUMPRODUCT(--({rng}<>"Data tidak lengkap"))', lengkap)
        self.r += 2
        items = [(lab, f"=SUMPRODUCT(--({rng}={q(lab)}))", kv.get(lab, 0)) for lab in KOMB[:-1]]
        self.count_table("S6_kombinasi_total", "Kategori", items, f"$C${lr}", lengkap)
        ws.cell(row=self.r - 1, column=2, value="Data tidak lengkap (tidak masuk %)")
        self.set(self.r - 1, 3, f'=SUMPRODUCT(--({rng}="Data tidak lengkap"))', kv.get("Data tidak lengkap", 0))
        self.r += 1
        for key, (top, ms) in getattr(self, "top_groups", {}).items():
            label = self.labels.get(key, key)
            gk = "grp_" + key
            ws.cell(row=self.r, column=1, value=f"Kombinasi per {label} (jumlah dan % dari data lengkap di grup)").font = BOLD
            self.r += 1
            heads = ["Rank", label, "Data lengkap"]
            for lab in KOMB[:-1]:
                heads += [f"{lab} (#)", "%"]
            self.head(ws, self.r, heads)
            start = self.r + 1
            for k in range(1, len(top) + 1):
                rr = self.r + k
                g = top[k - 1]
                ws.cell(row=rr, column=1, value=k)
                self.set(rr, 2, f"=$B${ms + k - 1}", g)
                gl = sum(1 for r in self.rows if self.pval[gk][r] == g and self.pval["komb"][r] != "Data tidak lengkap")
                self.set(rr, 3, f'=SUMPRODUCT(({self.prng(gk)}=$B{rr})*({rng}<>"Data tidak lengkap"))', gl)
                for j, lab in enumerate(KOMB[:-1]):
                    col = 4 + 2 * j
                    v = sum(1 for r in self.rows if self.pval[gk][r] == g and self.pval["komb"][r] == lab)
                    self.set(rr, col, f'=SUMPRODUCT(({self.prng(gk)}=$B{rr})*({rng}={q(lab)}))', v)
                    self.set(rr, col + 1, f"=IFERROR({CL(col)}{rr}/$C{rr},0)", v / gl if gl else 0, PCT)
            self.cells[f"S6_kombinasi_{key}"] = f"SUMMARY!A{start}:{CL(3 + 2 * len(KOMB[:-1]))}{start + len(top) - 1}"
            self.r = start + len(top) + 1

    def block_topik(self):
        ws = self.ws_s
        order = ["Profil lemak", "Status gizi", "Tekanan darah", "Fungsi paru", "Asam urat", "Fungsi hati", "Gigi",
                 "Tajam penglihatan", "Gula darah", "Fungsi ginjal", "Hematologi", "Urinalisa", "THT",
                 "Rontgen thorax", "EKG", "Muskuloskeletal", "Lain-lain", "Faktor risiko"]
        topics = [t for t in order if t in self.topics] + [t for t in self.topics if t not in order]
        slide = {"Profil lemak": "S8", "Status gizi": "S9", "Tekanan darah": "S10", "Fungsi paru": "S11",
                 "Asam urat": "S12", "Fungsi hati": "S13", "Gigi": "S14", "Tajam penglihatan": "S15"}
        for tp in topics:
            sid = slide.get(tp, "Topik")
            self.title(f"{sid}. {tp} (dari Kesimpulan vendor)")
            items = []
            for t in self.temuan:
                if t["topik"] != tp:
                    continue
                srow = self.trow_s[t["key"]]
                items.append((t["label"], f"=C{srow}", self.tot[t["key"]]))
            any_v = sum(self.pval["tp_" + tp][r] for r in self.rows)
            items.append((f"Salah satu temuan {tp.lower()} (pekerja dihitung sekali)", f"=SUM({self.prng('tp_' + tp)})", any_v))
            items.append((f"Tanpa temuan {tp.lower()} di Kesimpulan", f"={self.Nref}-SUM({self.prng('tp_' + tp)})", self.N - any_v))
            self.count_table(f"{sid}_{tp}", "Temuan", items, self.Nref, self.N)

    def block_kategori(self):
        for var, sid in (("spiro_kesimpulan", "S11b"), ("ro_kesimpulan", "Rontgen"), ("ekg_kesimpulan", "EKG"),
                         ("audio_kesimpulan", "Audiometri")):
            if var not in self.pcol:
                continue
            self.title(f"{sid}. {NILAI_VARS[var]} (interpretasi vendor, dikelompokkan lewat DICT_NILAI)",
                       "% dihitung dari pekerja yang punya hasil pemeriksaan ini (tanpa 'Tidak ada data').")
            cnt = Counter(self.pval[var][r] for r in self.rows)
            labs = list(OrderedDict.fromkeys(self.nmap[var].values()))
            labs += [x for x in (NOT_CAT,) if x not in labs and cnt.get(x)]
            labs = [x for x in labs if cnt.get(x) and x != NO_DATA] or [x for x in labs if x != NO_DATA]
            rng = self.prng(var)
            ws = self.ws_s
            ws.cell(row=self.r, column=2, value="Pekerja dengan hasil pemeriksaan")
            dr = self.r
            have = self.N - cnt.get(NO_DATA, 0)
            self.set(dr, 3, f'=SUMPRODUCT(--({rng}<>"{NO_DATA}"))-SUMPRODUCT(--({rng}=""))', have)
            ws.cell(row=dr + 1, column=2, value="Tidak ada data (tidak masuk %)")
            self.set(dr + 1, 3, f'=SUMPRODUCT(--({rng}="{NO_DATA}"))', cnt.get(NO_DATA, 0))
            self.r += 3
            self.count_table(f"{sid}_{var}", "Kategori", self.cat_items(var, labs), f"$C${dr}", have)

    # ------------------------------------------------------------ CHECK
    def write_check(self):
        ws = self.wb.create_sheet("CHECK")
        ws["A1"] = "CHECK: setiap sel SUMMARY dibandingkan dengan hitungan ulang independen oleh Python (angka statis kolom D)."
        ws["A1"].font = BOLD
        ws["A2"] = "Jumlah BEDA:"
        ws["A2"].font = BOLD
        self.head(ws, 4, ["Sel SUMMARY", "Isi rumus (nilai sekarang)", "Hitungan Python", "Status"])
        items = sorted(((r, c, v) for (s, r, c), v in self.expected.items() if s == "SUMMARY"))
        for i, (r, c, v) in enumerate(items):
            rr = 5 + i
            ref = f"SUMMARY!{CL(c)}{r}"
            ws.cell(row=rr, column=1, value=ref)
            ws.cell(row=rr, column=2, value=f"={ref}")
            vv = to_excel(v)
            cc = ws.cell(row=rr, column=3, value=vv)
            if isinstance(vv, dt.date):
                cc.number_format = "dd-mm-yyyy"
                ws.cell(row=rr, column=2).number_format = "dd-mm-yyyy"
            if is_num(vv) or isinstance(vv, dt.date):
                f = f'=IF(ABS(B{rr}-C{rr})<0.000001,"SAMA","BEDA")'
            else:
                f = f'=IF(B{rr}&""=C{rr}&"","SAMA","BEDA")'
            ws.cell(row=rr, column=4, value=f)
        end = 4 + len(items)
        ws["B2"] = f'=COUNTIF(D5:D{end},"BEDA")'
        # values that still need a category
        r = 3
        ws.cell(row=1, column=7, value="Nilai teks yang belum dikategorikan (perlu diisi di DICT_NILAI)").font = BOLD
        self.head(ws, 2, ["", "", "", "", "", "", "Variabel", "Jumlah pekerja"])
        for var in self.nmap:
            if var in self.pcol:
                ws.cell(row=r, column=7, value=NILAI_VARS[var])
                ws.cell(row=r, column=8, value=f'=COUNTIF({self.prng(var)},"{NOT_CAT}")')
                self.exp("CHECK", r, 8, sum(1 for x in self.rows if self.pval[var][x] == NOT_CAT))
                r += 1
        # Kesimpulan fragments not matched by any finding (for review)
        r += 2
        ws.cell(row=r, column=7, value="Potongan Kesimpulan yang tidak cocok dengan temuan mana pun (dibaca skrip; untuk ditinjau)").font = BOLD
        r += 1
        self.head(ws, r, ["", "", "", "", "", "", "Potongan kalimat", "Jumlah"])
        for frag, n in unmatched(self.temuan, [self.rv(x, "kesimpulan") for x in self.rows], self.abaikan).most_common(80):
            r += 1
            ws.cell(row=r, column=7, value=frag)
            ws.cell(row=r, column=8, value=n)
        self.widths(ws, [16, 26, 26, 10, 3, 3, 70, 14])
        ws.freeze_panes = "A5"

    # ------------------------------------------------------------ util
    @staticmethod
    def head(ws, row, values):
        for j, v in enumerate(values, 1):
            if v in (None, ""):
                continue  # never overwrite neighbouring cells with blanks
            c = ws.cell(row=row, column=j, value=v)
            if True:
                c.font = HEAD_FONT
                c.fill = HEAD_FILL
                c.alignment = Alignment(wrap_text=True, vertical="center")

    @staticmethod
    def widths(ws, ws_widths):
        for i, w in enumerate(ws_widths, 1):
            ws.column_dimensions[CL(i)].width = w

    def save(self):
        order = ["SUMMARY", "CHECK", "MAP", "GRUP", "DICT_TEMUAN", "DICT_NILAI", "DICT_CUTOFF", "DICT_BERSIH", "PEKERJA",
                 "KOLOM_VENDOR", "SHEET_LAIN", "RAW"]
        self.wb._sheets.sort(key=lambda s: order.index(s.title) if s.title in order else 99)
        self.wb.active = 0
        tmp = self.path.with_suffix(".tmp.xlsx")
        self.wb.save(tmp)
        try:
            tmp.replace(self.path)
        except PermissionError:
            tmp.unlink(missing_ok=True)
            sys.exit(f"Tidak bisa menyimpan: '{self.path.name}' sedang terbuka di Excel. Tutup dulu lalu jalankan ulang.")
        side = self.path.with_name(self.path.stem + " - summary_cells.json")
        bersih = [{"var": v, "asli": o.isoformat() if isinstance(o, dt.date) else o,
                   "bersih": n.isoformat() if isinstance(n, dt.date) else n, "alasan": w} for v, o, n, w in self.bersih]
        side.write_text(json.dumps({"grup": self.grups, "N": self.N, "blok": self.cells,
                                    "judul_fitness": getattr(self, "judul_fitness", "Status kelaikan kerja"), "bersih": bersih},
                                   ensure_ascii=False, indent=1), encoding="utf-8")


# ================================================================ python mirrors
def xl_trim_keep(v):
    return "" if v is None else (str(int(v)) if isinstance(v, float) and v.is_integer() else str(v))


def flag(t, text) -> int:
    if text is None or str(text) == "":
        return 0
    s = xl_trim(text).lower() + " "
    hit = any(k.lower() in s for k in t["kata"] if k)
    bad = any(k.lower() in s for k in t.get("kecuali", []) if k)
    return int(hit and not bad)


def unmatched(temuan, texts, abaikan=()) -> Counter:
    normal = re.compile(r"dalam batas normal|^normal|tidak ditemukan|tidak tampak|^baik|^-$", re.I)
    out = Counter()
    for t in texts:
        clean = re.sub(r"\([^)]*\)", " ", str(t or ""))  # drop '(26,34 kg/m2)' etc. before splitting on commas
        for ln in re.split(r"\n|\.\s+|;\s*|,\s*", clean):
            s = re.sub(r"^\s*(\d+\.|-|•)\s*", "", ln).strip()
            s2 = xl_trim(re.sub(r"\(.*?\)", "", s)).strip(" _").lower()
            if len(s2) < 4 or normal.search(s2) or any(a.search(s2) for a in abaikan):
                continue
            if not any(flag(x, s2) for x in temuan):
                out[s2[:70]] += 1
    return out


def fmt_num(v):
    return str(int(v)) if float(v).is_integer() else str(v)


def to_excel(v):
    return v


def same(want, got) -> bool:
    if isinstance(want, dt.date) and not isinstance(want, dt.datetime):
        if isinstance(got, dt.datetime):
            return got.date() == want
        if is_num(got):
            return (dt.date(1899, 12, 30) + dt.timedelta(days=int(got))) == want
        return False
    if is_num(want):
        return is_num(got) and abs(got - want) < 1e-6
    if want == "":
        return got in (None, "")
    return (got if got is not None else "") == want


def recalc_and_check(path: Path, expected) -> int:
    if not SOFFICE.exists():
        print("  --cek: LibreOffice tidak ditemukan, dilewati.")
        return -1
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "in.xlsx"
        shutil.copy(path, src)
        out = Path(td) / "out"
        out.mkdir()
        subprocess.run([str(SOFFICE), "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(out), str(src)],
                       check=True, capture_output=True, timeout=900)
        wb = openpyxl.load_workbook(out / "in.xlsx", data_only=True, read_only=True)
        sheets = {}
        for name in {s for s, _, _ in expected} | {"CHECK"}:
            sheets[name] = [list(r) for r in wb[name].iter_rows(values_only=True)]
        wb.close()
    diffs = []
    for (s, r, c), want in expected.items():
        rows = sheets[s]
        got = rows[r - 1][c - 1] if r - 1 < len(rows) and c - 1 < len(rows[r - 1]) else None
        if not same(want, got):
            diffs.append((s, f"{CL(c)}{r}", want, got))
    beda_check = sheets["CHECK"][1][1]
    by_sheet = Counter(s for s, _, _ in expected)
    print(f"  --cek: {len(expected)} sel rumus dibandingkan ({', '.join(f'{k} {v}' for k, v in by_sheet.items())}); "
          f"beda = {len(diffs)}; sheet CHECK 'Jumlah BEDA' = {beda_check}")
    for d in diffs[:25]:
        print("    BEDA", d)
    return len(diffs) + (beda_check or 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("analisa", type=Path, help="file '<nama> - Analisa.xlsx' hasil mcu_reader.py")
    ap.add_argument("--grup", action="append", default=[], help="KODE[:N], mis. bagian atau departemen:10")
    ap.add_argument("--cek", action="store_true")
    ap.add_argument("--reset-dict", action="store_true",
                    help="buang isi DICT_* di workbook dan pakai ulang default JSON (editan DICT hilang)")
    ap.add_argument("--bersih", action="append", default=[],
                    help="VAR:ASLI=BERSIH[#alasan], mis. bagian:TAMANAN=TANAMAN atau tgl_mcu:2026-07-10=2026-10-07 "
                         "(disimpan di DICT_BERSIH, tetap dipakai di putaran berikutnya)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if not args.grup:
        sys.exit("Tentukan minimal satu --grup (mis. --grup bagian).")
    spec = json.loads((HERE / "temuan_standar.json").read_text(encoding="utf-8"))
    b = Builder(args.analisa.resolve(), args.grup, spec, args.reset_dict, args.bersih)
    b.write_dicts()
    b.write_pekerja()
    b.write_summary()
    b.write_check()
    b.save()
    print(f"File   : {b.path.name}")
    print(f"Pekerja: {b.N} | temuan dicari: {len(b.temuan)} | grup: {', '.join(f'{k} (top {n})' for k, n in b.grups)}")
    print(f"Tanggal: MCU format {b.pat_mcu}, lahir format {b.pat_lahir} | kombinasi 3 kelainan: {'ya' if b.has_komb else 'tidak (kolom kurang)'}")
    print("DICT   : " + ", ".join(f"{k} {'(edit Anda)' if v else '(default)'}" for k, v in b.edited.items()))
    if b.bersih:
        print("Bersih : " + "; ".join(f"{v}: {o} -> {n}" for v, o, n, _ in b.bersih))
    print(f"Judul  : {b.judul_fitness}")
    lp = b.cutoff["lp_l"]
    print(f"LP     : {lp.get('dasar')} {'(otomatis: vendor tidak menafsirkan lingkar perut)' if b.lp_auto else ''}"
          + (f" L>={lp['nilai']} / P>={b.cutoff['lp_p']['nilai']} cm" if lp.get("dasar") == "cutoff" else ""))
    nc = {v: sum(1 for r in b.rows if b.pval[v][r] == NOT_CAT) for v in b.nmap if v in b.pval}
    if any(nc.values()):
        print("Belum dikategorikan: " + ", ".join(f"{k} {n}" for k, n in nc.items() if n))
    top = sorted(((b.tot[t["key"]], t["label"]) for t in b.temuan if t["top_ten"]), reverse=True)[:10]
    print("Top ten: " + "; ".join(f"{lab} {n}" for n, lab in top))
    if args.cek:
        if recalc_and_check(b.path, b.expected) > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
