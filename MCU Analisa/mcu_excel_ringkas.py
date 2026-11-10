"""Vendor Excel + "Ringkasan" sheet next to it, for the doctor who supplied the file (step 4).

Makes a duplicate of the vendor's own workbook (all original sheets kept as they are, the
vendor file itself is not modified) and adds one sheet, "Ringkasan", right after the vendor's
main sheet: the same tables as the PPT report, each with a native Excel chart where the PPT
has one. No other sheet is added.

Every number in Ringkasan is a formula that calculates straight from the vendor's main sheet
(e.g. SUMPRODUCT over 'Rekap MCU'!$O$5:$O$513), using the same keywords, categories and
cutoffs as the analysis workbook (taken from its DICT_* sheets). Top ten and top 3 per group
are picked by formula from the "Semua temuan" table and a helper table on the same sheet.
Tables are plain (raw-Excel look); charts in the report colours.

Usage:
    uv run --with openpyxl --with python-pptx python mcu_excel_ringkas.py "<... - Analisa.xlsx>"

Output: "<vendor file> - dengan Ringkasan.xlsx" next to the vendor file. After saving, the file
is recalculated with LibreOffice and every Ringkasan number is compared with the analysis
workbook's SUMMARY (which is itself checked against an independent Python recount).
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
from pathlib import Path

import openpyxl
from openpyxl.chart import BarChart, DoughnutChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.styles import Alignment, Font
from openpyxl.utils import column_index_from_string as col_index
from openpyxl.worksheet.formula import ArrayFormula
from openpyxl.utils import get_column_letter as CL

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcu_ppt import SOFFICE, Summary, untuk_pembaca  # noqa: E402
from mcu_summary import KOMB, PAK_KOSONG, as_date, date_pattern, read_map, xl_serial, xl_uf  # noqa: E402

TEAL, DARK, SAND = "307F7F", "112929", "D1B984"
PALETTE = [TEAL, SAND, DARK, "7FB8B8", "EADBB4", "A3A3A3", "4F9A9A", "BFA36A"]
BOLD = Font(bold=True)
PCT = "0.0%"
NO_DATA = "Tidak ada data"
HELPER_COL = 30  # helper tables start in column AD, away from the readable area
ZERO_COL = 200   # GR:GS, beyond the AD+ helper matrix (one column per finding): per chart, the rows whose value is not 0
OTG = json.loads((Path(__file__).resolve().parent / "temuan_standar.json").read_text(encoding="utf-8")).get("obesitas_tanpa_grade") or {}


def q(s) -> str:
    return '"' + str(s).replace('"', '""') + '"'


def arr(values) -> str:
    return "{" + ",".join(q(v) for v in values) + "}"


# ================================================================ reading the analysis workbook
def read_dicts(wb):
    temuan = []
    for r in wb["DICT_TEMUAN"].iter_rows(min_row=4, values_only=True):
        if r and r[0]:
            temuan.append({"key": str(r[0]), "label": str(r[1]), "topik": str(r[2]), "top_ten": str(r[3]).strip().lower() == "ya",
                           "kata": [str(x) for x in r[5:15] if x not in (None, "")],
                           "kecuali": [str(x) for x in r[15:19] if x not in (None, "")]})
    nilai, cur = {}, None
    for r in wb["DICT_NILAI"].iter_rows(values_only=True):
        if r and isinstance(r[0], str) and r[0].startswith("Variabel: "):
            cur = r[0].split("Variabel: ", 1)[1].split(" ")[0]
            nilai[cur] = {}
        elif cur and r and r[0] not in (None, "", "Nilai (huruf besar, spasi dirapikan)") and r[1]:
            nilai[cur][str(r[0])] = str(r[1])
    cutoff = {}
    for r in wb["DICT_CUTOFF"].iter_rows(min_row=4, values_only=True):
        if r and r[0]:
            cutoff[str(r[0])] = {"nilai": r[3], "dasar": (r[5] if len(r) > 5 else None) or "cutoff",
                                 "temuan_vendor": [x.strip() for x in str((r[6] if len(r) > 6 else "") or "").split(",") if x.strip()]}
    return temuan, nilai, cutoff


# ================================================================ formula factory
class F:
    """Builds array expressions over the vendor sheet (used inside SUMPRODUCT/AGGREGATE)."""

    def __init__(self, sheet, first, last, cols, nilai, temuan, cutoff, pat_mcu, pat_lahir, bersih=()):
        self.V = "'" + sheet.replace("'", "''") + "'!"
        self.a, self.b = first, last
        self.cols, self.nilai, self.cutoff = cols, nilai, cutoff
        self.t = {t["key"]: t for t in temuan}
        self.pat_mcu, self.pat_lahir = pat_mcu, pat_lahir
        self.bersih = list(bersih)  # same clean-ups as DICT_BERSIH of the Analisa file (summary_cells.json)

    def R(self, key):
        L = self.cols[key]
        return f"{self.V}${L}${self.a}:${L}${self.b}"

    def U(self, key):
        u = f"UPPER(TRIM({self.R(key)}))"
        for b in self.bersih:  # e.g. Bagian TAMANAN -> TANAMAN, written out so the vendor can read it
            if b["var"] == key:
                u = f'IF({u}={q(str(b["asli"]).strip().upper())},{q(str(b["bersih"]).strip().upper())},{u})'
        return u

    def named(self):
        return f'(TRIM({self.R("nama")})<>"")'

    def count(self, expr):
        return f"=SUMPRODUCT(({expr})*{self.named()})"

    # findings ------------------------------------------------------
    def hit(self, words):
        K = self.R("kesimpulan")
        # "--" turns TRUE/FALSE into 1/0: in Excel FALSE>0 is TRUE (logicals sort above numbers), so a
        # single-keyword test without it would count every worker
        return "--((" + "+".join(f'--ISNUMBER(SEARCH({q(w)},TRIM({K})&" "))' for w in words) + ")>0)"

    def flag(self, key):
        t = self.t[key]
        h = self.hit(t["kata"]) if t["kata"] else "0"
        h = f"({h}*(1-{self.hit(t['kecuali'])}))" if t["kecuali"] else h
        ext = self.extra(key)
        return f"--(({h})+({ext})>0)" if ext else h

    def extra(self, key):
        """Same extra conditions as mcu_summary: waist cutoff for central obesity, IMT grade when the vendor wrote none."""
        c = self.cutoff
        if key == "obes_sentral" and c.get("lp_l", {}).get("dasar") == "cutoff" and "lp" in self.cols and "jk" in self.cols:
            R = self.R("lp")
            male, fem = f"--{self.cat('jk', 'Laki-laki')}", f"--{self.cat('jk', 'Perempuan')}"
            return (f"IFERROR(--ISNUMBER({R})*(({male})*--({R}>={c['lp_l']['nilai']})+({fem})*--({R}>={c['lp_p']['nilai']})),0)")
        rule = (OTG.get("imt") or {}).get(key)
        if rule and "imt" in self.cols and all(k in self.t for k in ("obes1", "obes2")):
            lo, hi = rule
            I = self.R("imt")
            imt = f"IFERROR(--ISNUMBER({I})*--({I}>={lo})" + (f"*--({I}<{hi})" if hi else "") + ",0)"
            num = self.hit(self.t["obes1"]["kata"] + self.t["obes2"]["kata"])
            return f"{self.hit(OTG['kata'])}*(1-{num})*{imt}"
        return None

    def any_flag(self, keys):
        return "--((" + "+".join(f"({self.flag(k)})" for k in keys) + ")>0)"

    # categories ----------------------------------------------------
    def cat(self, var, category):
        vals = [v for v, c in self.nilai.get(var, {}).items() if c == category]
        if category == NO_DATA:
            return f'(TRIM({self.R(var)})="")'
        if not vals:
            return "0"
        # one-line text, like DICT_NILAI keys (multi-line X-ray texts)
        return f"ISNUMBER(MATCH({xl_uf(self.R(var))},{arr(vals)},0))"

    def eq(self, key, label):
        return f"({self.U(key)}={q('' if label in ('(kosong)', PAK_KOSONG) else label)})"

    # dates ---------------------------------------------------------
    def date(self, key, pat):
        """Date per row: Excel dates as they are, text dates parsed (vendors mix both), then DICT_BERSIH date fixes."""
        R = self.R(key)
        if pat == "dmy":
            txt = f"DATE(VALUE(MID({R},7,4)),VALUE(MID({R},4,2)),VALUE(LEFT({R},2)))"
        elif pat == "ymd":
            txt = f"DATE(VALUE(LEFT({R},4)),VALUE(MID({R},6,2)),VALUE(MID({R},9,2)))"
        else:
            txt = R
        d = f"IF(ISNUMBER({R}),{R},{txt})" if pat in ("dmy", "ymd") else R
        fixes = [(xl_serial(as_date(b["asli"])), xl_serial(as_date(b["bersih"]))) for b in self.bersih if b["var"] == key]
        if fixes:
            d = f"({d})" + "".join(f"+(({d})={o})*({n - o})" for o, n in fixes)
        return d

    def ymd(self, key, pat):
        d = self.date(key, pat)
        return f"YEAR({d})", f"MONTH({d})", f"DAY({d})"

    def age(self):
        y1, m1, d1 = self.ymd("tgl_mcu", self.pat_mcu)
        y0, m0, d0 = self.ymd("tgl_lahir", self.pat_lahir)
        return f"(({y1})-({y0})-((({m1})*100+({d1}))<(({m0})*100+({d0}))))"

    # combination ---------------------------------------------------
    def jk_valid(self):
        return f'({self.cat("jk", "Laki-laki")}+{self.cat("jk", "Perempuan")})'

    def komb_parts(self):
        R, c = self.R, self.cutoff
        complete = (f"ISNUMBER({R('tg')})*ISNUMBER({R('hdl')})*IFERROR(--({R('hdl')}>0),0)*ISNUMBER({R('hba1c')})"
                    f"*ISNUMBER({R('lp')})*{self.jk_valid()}")
        ab1 = f"IFERROR(--({R('tg')}/{R('hdl')}>={c['tg_hdl']['nilai']}),0)"
        if c["hba1c"]["dasar"] == "vendor":
            keys = [k for k in c["hba1c"]["temuan_vendor"] if k in self.t]
            ab2 = self.any_flag(keys) if keys else "0"
        else:
            ab2 = f"IFERROR(--({R('hba1c')}>={c['hba1c']['nilai']}),0)"
        if c["lp_l"]["dasar"] == "vendor":
            keys = [k for k in c["lp_l"]["temuan_vendor"] if k in self.t]
            ab3 = self.any_flag(keys) if keys else "0"
        else:
            male = self.cat("jk", "Laki-laki")
            ab3 = f"IFERROR(--({R('lp')}>=IF({male},{c['lp_l']['nilai']},{c['lp_p']['nilai']})),0)"
        return f"({complete})", f"({ab1})", f"({ab2})", f"({ab3})"

    def komb(self, label):
        cpl, a1, a2, a3 = self.komb_parts()
        n = lambda x: f"(1-{x})"  # noqa: E731
        combos = {"Ketiganya": [a1, a2, a3], "Rasio TG/HDL + HbA1c": [a1, a2, n(a3)], "Rasio TG/HDL + LP": [a1, n(a2), a3],
                  "HbA1c + LP": [n(a1), a2, a3], "Hanya rasio TG/HDL": [a1, n(a2), n(a3)], "Hanya HbA1c": [n(a1), a2, n(a3)],
                  "Hanya LP": [n(a1), n(a2), a3], "Tidak ada": [n(a1), n(a2), n(a3)]}
        return "*".join([cpl] + combos[label])


# ================================================================ builder
class Ringkasan:
    def __init__(self, analisa: Path):
        self.S = Summary(analisa)
        if self.S.check_beda not in (0, None):
            sys.exit(f"Sheet CHECK menunjukkan {self.S.check_beda} BEDA: perbaiki SUMMARY dulu.")
        try:
            wa = openpyxl.load_workbook(analisa)
        except PermissionError:  # open in Excel: read a temporary copy (read only)
            tmp = Path(tempfile.gettempdir()) / f"ringkas_{analisa.name}"
            shutil.copy2(analisa, tmp)
            wa = openpyxl.load_workbook(tmp)
        self.vendor = Path(str(wa["MAP"]["B1"].value))
        self.main = str(wa["MAP"]["B2"].value)
        first, last, cols, labels = read_map(wa)
        temuan, nilai, cutoff = read_dicts(wa)
        self.temuan = temuan
        try:
            self.wb = openpyxl.load_workbook(self.vendor)
        except PermissionError:
            tmp = Path(tempfile.gettempdir()) / f"ringkas_{self.vendor.name}"
            shutil.copy2(self.vendor, tmp)
            self.wb = openpyxl.load_workbook(tmp)
        main_ws = self.wb[self.main]
        vals = lambda key: [main_ws[f"{cols[key]}{r}"].value for r in range(first, last + 1)] if key in cols else []  # noqa: E731
        self.f = F(self.main, first, last, cols, nilai, temuan, cutoff,
                   date_pattern(vals("tgl_mcu")), date_pattern(vals("tgl_lahir")), self.S.meta.get("bersih", []))
        for name in ("Ringkasan", "SUMMARY", "PEKERJA", "DICT_TEMUAN", "DICT_NILAI", "DICT_CUTOFF", "CHECK"):
            if name in self.wb.sheetnames:
                del self.wb[name]
        self.ws = self.wb.create_sheet("Ringkasan", self.wb.sheetnames.index(self.main) + 1)
        self.r = 1
        self.expected = {}   # (row, col) -> SUMMARY address in the analysis workbook
        self.charts = 0
        self.cols = cols

    # ------------------------------------------------------------ writing helpers
    def put(self, row, col, formula, summary_addr=None, fmt=None):
        if isinstance(formula, str):
            formula = re.sub(r"(?<![\w.])AGGREGATE\(", "_xlfn.AGGREGATE(", formula)  # Excel 2010+ function prefix
            if formula.startswith("=") and ":" in formula:
                # store as an array formula ({=...}): otherwise Excel evaluates IFERROR/MID/DATE inside
                # SUMPRODUCT/AGGREGATE on one row only (implicit intersection) and shows 0 or 100%
                ref = f"{CL(col)}{row}"
                formula = ArrayFormula(ref, formula)
        c = self.ws.cell(row=row, column=col, value=formula)
        if fmt:
            c.number_format = fmt
        if summary_addr:
            self.expected[(row, col)] = summary_addr
        return c

    def title(self, text, note=None):
        text, note = untuk_pembaca(text), (untuk_pembaca(note) if note else note)  # read by the vendor
        self.r += 1
        self.ws.cell(row=self.r, column=1, value=text).font = BOLD
        if note:
            self.r += 1
            c = self.ws.cell(row=self.r, column=1, value=note)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            self.ws.merge_cells(start_row=self.r, start_column=1, end_row=self.r, end_column=5)
            self.ws.row_dimensions[self.r].height = 15 * max(1, len(note) // 70 + 1)
        self.r += 1

    def head(self, row, values, start=1):
        for j, v in enumerate(values):
            self.ws.cell(row=row, column=start + j, value=v).font = BOLD

    def chart_rows(self, first, last, cat_col, val_col):
        """Rows a chart shows: zero values left out (Vidya 2026-11-10). When some are zero, the chart reads a formula
        list of the other rows in columns BH:BI (outside the print area); returns (first, last, cat_col, val_col)."""
        keep = []
        for rr in range(first, last + 1):
            addr = self.expected.get((rr, val_col))
            v = self.S.cell(addr) if addr else None
            if v not in (0, 0.0):
                keep.append(rr)
        if len(keep) == last - first + 1 or not keep:
            return first, last, cat_col, val_col
        for i, rr in enumerate(keep):
            if any(self.ws.cell(row=first + i, column=ZERO_COL + j).value is not None for j in (0, 1)):
                sys.exit(f"Ringkasan: kolom {CL(ZERO_COL)} baris {first + i} sudah terisi; geser ZERO_COL.")
            self.ws.cell(row=first + i, column=ZERO_COL, value=f"={CL(cat_col)}{rr}")
            self.ws.cell(row=first + i, column=ZERO_COL + 1, value=f"={CL(val_col)}{rr}").number_format = "0"
        return first, first + len(keep) - 1, ZERO_COL, ZERO_COL + 1

    def bar(self, first, last, title, anchor_row, cat_col=2, val_col=3):
        first, last, cat_col, val_col = self.chart_rows(first, last, cat_col, val_col)
        ch = BarChart()
        ch.type = "bar"
        ch.style = 10
        ch.title = untuk_pembaca(title)
        ch.legend = None
        ch.add_data(Reference(self.ws, min_col=val_col, min_row=first, max_row=last), titles_from_data=False)
        ch.set_categories(Reference(self.ws, min_col=cat_col, min_row=first, max_row=last))
        s = ch.series[0]
        s.graphicalProperties = GraphicalProperties(solidFill=TEAL)
        s.graphicalProperties.line.solidFill = TEAL
        ch.dataLabels = DataLabelList(showVal=True, showCatName=False, showSerName=False, showLegendKey=False,
                                      showPercent=False, showLeaderLines=False)
        ch.gapWidth = 60 if last - first >= 3 else 180
        ch.x_axis.scaling.orientation = "maxMin"
        ch.x_axis.delete = False
        ch.y_axis.delete = True
        ch.y_axis.majorGridlines = None
        ch.height = max(6.0, 0.9 * (last - first + 1) + 2.5)
        ch.width = 17
        self.ws.add_chart(ch, f"G{anchor_row}")
        self.charts += 1
        return int(ch.height / 0.5) + 1

    def doughnut(self, first, last, title, anchor_row):
        first, last, cat_col, val_col = self.chart_rows(first, last, 2, 3)
        ch = DoughnutChart()
        ch.title = untuk_pembaca(title)
        ch.holeSize = 55
        ch.add_data(Reference(self.ws, min_col=val_col, min_row=first, max_row=last), titles_from_data=False)
        ch.set_categories(Reference(self.ws, min_col=cat_col, min_row=first, max_row=last))
        s = ch.series[0]
        for i in range(last - first + 1):
            pt = DataPoint(idx=i)
            pt.graphicalProperties = GraphicalProperties(solidFill=PALETTE[i % len(PALETTE)])
            s.dPt.append(pt)
        ch.dataLabels = DataLabelList(showPercent=True, showVal=False, showCatName=False, showSerName=False,
                                      showLegendKey=False, showLeaderLines=False)
        ch.height, ch.width = 7.5, 11
        self.ws.add_chart(ch, f"G{anchor_row}")
        self.charts += 1
        return 16

    def simple(self, title, rows, chart=None, chart_rows=None, header=("No", "Kategori", "Jumlah", "%"), note=None):
        """rows: list of (label, count_formula, pct_formula_or_None, summary_row). Columns A-D."""
        start = self.r
        self.title(title, note)
        self.head(self.r, header)
        first = self.r + 1
        for i, (lab, fc, fp, srow) in enumerate(rows):
            rr = first + i
            self.ws.cell(row=rr, column=1, value=i + 1)
            self.ws.cell(row=rr, column=2, value=lab)
            self.put(rr, 3, fc, f"C{srow}" if srow else None, "0")
            if fp:
                self.put(rr, 4, fp(rr) if callable(fp) else fp, f"D{srow}" if srow else None, PCT)
        last = first + len(rows) - 1
        self.r = last + 2
        used = 0
        if chart == "bar":
            n = chart_rows if chart_rows is not None else len(rows)
            used = self.bar(first, first + n - 1, title, start + 1)
        elif chart == "doughnut":
            used = self.doughnut(first, last, title, start + 1)
        self.r = max(self.r, start + 1 + used + 1)
        return first, last

    def pct_n(self, rr):
        return f"=IFERROR(C{rr}/$C$5,0)"

    def blk(self, key):
        return self.S.block(key)

    def topic_block(self, tp):
        k = next((k for k in self.S.meta["blok"] if k == f"Topik_{tp}" or re.fullmatch(r"S\d+_" + re.escape(tp), k)), None)
        return self.blk(k) if k else []

    # ------------------------------------------------------------ build
    def build(self):
        ws, f, S = self.ws, self.f, self.S
        ws["A1"] = "RINGKASAN HASIL MCU"
        ws["A1"].font = BOLD
        ws["A2"] = S.company
        ws["A2"].font = BOLD
        ws["A3"] = f"Setiap angka di sheet ini adalah rumus yang menghitung langsung dari sheet '{self.main}'."
        ws["A5"] = "Jumlah peserta MCU (N)"
        self.put(5, 3, f"=SUMPRODUCT(--{f.named()})", "C3", "0")
        a, b = S.meta["blok"]["S3_periode"].split("!")[-1].split(":")
        ws["A6"] = "Tanggal MCU pertama"
        self.put(6, 3, f"=AGGREGATE(15,6,{f.date('tgl_mcu', f.pat_mcu)},1)", a, "dd-mm-yyyy")
        ws["A7"] = "Tanggal MCU terakhir"
        self.put(7, 3, f"=AGGREGATE(14,6,{f.date('tgl_mcu', f.pat_mcu)},1)", b, "dd-mm-yyyy")
        for r in (5, 6, 7):
            ws.cell(row=r, column=1).font = BOLD
        self.r = 8

        # demographics ---------------------------------------------
        cut = f.cutoff["umur_batas"]["nilai"]
        age = f.age()
        rows = []
        for r in self.blk("S3_kelompok_umur"):
            if r["B"].startswith("<"):
                fc = f"=SUMPRODUCT(IFERROR(--({age}<{cut}),0)*{f.named()})"
            elif r["B"].startswith(">="):
                fc = f"=SUMPRODUCT(IFERROR(--({age}>={cut}),0)*{f.named()})"
            else:
                continue
            rows.append((r["B"].replace(">=", "≥"), fc, self.pct_n, r["row"]))
        self.simple("Karakteristik demografi: kelompok umur", rows, "doughnut")
        rows = [(r["B"], f.count(f.cat("jk", r["B"])), self.pct_n, r["row"]) for r in self.blk("S3_jenis_kelamin") if r["C"]]
        self.simple("Karakteristik demografi: jenis kelamin", rows)
        hab = []
        for key, var, lab, yes in (("S3_merokok", "merokok", "Merokok", "Merokok"), ("S3_alkohol", "alkohol", "Konsumsi alkohol", "Ya"),
                                   ("S3_olahraga", "olahraga", "Olahraga", "Ya")):
            blk = self.blk(key)
            if not blk:
                continue
            rows = [(r["B"], f.count(f.cat(var, r["B"])), self.pct_n, r["row"]) for r in blk]
            first, _ = self.simple(f"Kebiasaan: {lab.lower()}", rows)
            for i, r in enumerate(blk):
                if r["B"] == yes:
                    hab.append((lab, first + i))
        if hab:
            rows = [(lab, f"=C{rr}", self.pct_n, None) for lab, rr in hab]
            self.simple("Kebiasaan pekerja (ringkasan, seperti grafik di PPT)", rows, "bar", header=("No", "Kebiasaan", "Jumlah", "%"))
        jf = S.meta.get("judul_fitness", "Status kelaikan kerja")
        for key, var, ttl, ch in (("kelaikan_fitness", "fitness", jf, "doughnut"),
                                  ("kelaikan_risiko", "risiko", "Risiko kesehatan", None),
                                  ("pak_dugaan", "dugaan_pak", "Dugaan penyakit akibat kerja (PAK)", None)):
            rows = [(r["B"], f.count(f.eq(var, r["B"])), self.pct_n, r["row"]) for r in self.blk(key)]
            if rows:
                self.simple(ttl, rows, ch)

        # all findings (basis for top ten and topics) -------------------
        self.title("Semua temuan (dasar Top Ten dan tabel per topik)")
        self.head(self.r, ["No", "Temuan", "Jumlah", "%", "Topik", "Ikut Top ten"])
        first = self.r + 1
        srows = {r["B"]: r["row"] for r in self.blk("semua_temuan")}
        self.trow = {}
        for i, t in enumerate(self.temuan):
            rr = first + i
            self.trow[t["key"]] = rr
            ws.cell(row=rr, column=1, value=i + 1)
            ws.cell(row=rr, column=2, value=t["label"])
            self.put(rr, 3, f.count(f.flag(t["key"])), f"C{srows.get(t['label'])}" if t["label"] in srows else None, "0")
            self.put(rr, 4, self.pct_n(rr), f"D{srows.get(t['label'])}" if t["label"] in srows else None, PCT)
            ws.cell(row=rr, column=5, value=t["topik"])
            ws.cell(row=rr, column=6, value="Ya" if t["top_ten"] else "Tidak")
        last = first + len(self.temuan) - 1
        self.all_rng = (first, last)
        self.r = last + 2

        # top ten -------------------------------------------------------
        J, L, T = (f"$C${first}:$C${last}", f"$B${first}:$B${last}", f"$F${first}:$F${last}")
        score = f"({J}-ROW({J})/10000)"
        start = self.r
        self.title("Top ten penyakit dan temuan")
        self.head(self.r, ["No", "Jenis penyakit / temuan", "Jumlah", "% dari total peserta MCU"])
        tf = self.r + 1
        top = self.blk("S4_top_ten")
        for k in range(1, 11):
            rr = tf + k - 1
            val = f"AGGREGATE(14,6,{score}/({T}=\"Ya\"),{k})"
            idx = f"AGGREGATE(15,6,(ROW({J})-ROW($C${first})+1)/({score}={val}),1)"
            ws.cell(row=rr, column=1, value=k)
            srow = top[k - 1]["row"] if k <= len(top) else None
            self.put(rr, 2, f'=IFERROR(IF({val}<0,"-",INDEX({L},{idx})),"-")', f"B{srow}" if srow else None)
            self.put(rr, 3, f"=IFERROR(IF({val}<0,0,INDEX({J},{idx})),0)", f"C{srow}" if srow else None, "0")
            self.put(rr, 4, self.pct_n(rr), f"D{srow}" if srow else None, PCT)
        self.r = tf + 11
        used = self.bar(tf, tf + 9, "Top ten penyakit dan temuan", start + 1)
        self.r = max(self.r, start + 1 + used + 1)

        # per group -----------------------------------------------------
        helper_row = 2
        for key, n in S.meta["grup"]:
            helper_row = self.group(key, n, helper_row)

        # combination ---------------------------------------------------
        tot = self.blk("S6_kombinasi_total")
        if tot and all(k in self.cols for k in ("tg", "hdl", "hba1c", "lp", "jk")):
            nr, note = S.find_row("Abnormal 1 rasio")
            lr, _ = S.find_row("Pekerja dengan data lengkap")
            start = self.r
            self.title("Analisa 3 kategori kelainan (rasio TG/HDL, HbA1c, lingkar perut)", note)
            ws.cell(row=self.r, column=2, value="Pekerja dengan data lengkap (ketiga parameter)")
            cpl = f.komb_parts()[0]
            self.put(self.r, 3, f"=SUMPRODUCT({cpl}*{f.named()})", f"C{lr}", "0")
            lrow = self.r
            self.r += 2
            self.head(self.r, ["No", "Kategori", "Jumlah", "%"])
            kf = self.r + 1
            for i, r in enumerate(tot):
                rr = kf + i
                ws.cell(row=rr, column=1, value=i + 1)
                ws.cell(row=rr, column=2, value=r["B"])
                self.put(rr, 3, f"=SUMPRODUCT({f.komb(r['B'])}*{f.named()})", f"C{r['row']}", "0")
                self.put(rr, 4, f"=IFERROR(C{rr}/$C${lrow},0)", f"D{r['row']}", PCT)
            self.r = kf + len(tot) + 1
            used = self.bar(kf, kf + len(tot) - 1, "Analisa 3 kategori kelainan", start + 1)
            self.r = max(self.r, start + 1 + used + 1)
            for key, n in S.meta["grup"]:
                self.komb_group(key)

        # topics --------------------------------------------------------
        order = [("Profil lemak", "Gangguan metabolisme lemak"), ("Status gizi", "Status gizi"), ("Tekanan darah", "Tekanan darah"),
                 ("Fungsi paru", "Fungsi pernapasan (kesimpulan spirometri)"), ("Asam urat", "Metabolisme asam urat"),
                 ("Fungsi hati", "Peningkatan enzim transaminase"), ("Gigi", "Kelainan gigi"), ("Tajam penglihatan", "Gangguan tajam penglihatan")]
        for tp, ttl in order:
            if tp == "Fungsi paru" and S.meta["blok"].get("S11b_spiro_kesimpulan") and "spiro_kesimpulan" in self.cols:
                blk = self.blk("S11b_spiro_kesimpulan")
                have_row, _ = S.find_row("Pekerja dengan hasil pemeriksaan")
                start = self.r
                self.title(ttl, "% dari pekerja yang punya hasil pemeriksaan spirometri.")
                ws.cell(row=self.r, column=2, value="Pekerja dengan hasil pemeriksaan")
                # the first such row in SUMMARY after the spirometry title
                srow_have = self.find_after("S11b", "Pekerja dengan hasil pemeriksaan")
                self.put(self.r, 3, f"=SUMPRODUCT((TRIM({f.R('spiro_kesimpulan')})<>\"\")*{f.named()})", f"C{srow_have}", "0")
                hrow = self.r
                self.r += 2
                self.head(self.r, ["No", "Kategori", "Jumlah", "%"])
                sf = self.r + 1
                for i, r in enumerate(blk):
                    rr = sf + i
                    ws.cell(row=rr, column=1, value=i + 1)
                    ws.cell(row=rr, column=2, value=r["B"])
                    self.put(rr, 3, f.count(f.cat("spiro_kesimpulan", r["B"])), f"C{r['row']}", "0")
                    self.put(rr, 4, f"=IFERROR(C{rr}/$C${hrow},0)", f"D{r['row']}", PCT)
                self.r = sf + len(blk) + 1
                used = self.bar(sf, sf + len(blk) - 1, ttl, start + 1)
                self.r = max(self.r, start + 1 + used + 1)
                continue
            blk = self.topic_block(tp)
            if not blk:
                continue
            keys = [t["key"] for t in self.temuan if t["topik"] == tp]
            rows = []
            for r in blk:
                if str(r["B"]).startswith("Tanpa"):
                    continue
                if str(r["B"]).startswith("Salah satu"):
                    rows.append((r["B"], f.count(f.any_flag(keys)), self.pct_n, r["row"]))
                else:
                    tk = next(t["key"] for t in self.temuan if t["label"] == r["B"] and t["topik"] == tp)
                    rows.append((r["B"], f"=C{self.trow[tk]}", self.pct_n, r["row"]))
            self.simple(ttl, rows, "bar", chart_rows=len(rows) - 1, header=("No", "Temuan", "Jumlah", "%"))

        # other topics --------------------------------------------------
        rows = []
        for tp in ["Gula darah", "Fungsi ginjal", "Hematologi", "Urinalisa", "THT", "Rontgen thorax", "EKG", "Muskuloskeletal", "Lain-lain"]:
            r = next((x for x in self.topic_block(tp) if str(x["B"]).startswith("Salah satu")), None)
            if r and r["C"]:
                keys = [t["key"] for t in self.temuan if t["topik"] == tp]
                rows.append((tp, f.count(f.any_flag(keys)), self.pct_n, r["row"]))
        if rows:
            self.simple("Temuan lain (pekerja dengan salah satu temuan pada topik tersebut)", rows, header=("No", "Topik", "Jumlah", "%"))

        ws.column_dimensions["A"].width = 8
        ws.column_dimensions["B"].width = 46
        ws.column_dimensions["C"].width = 26
        for c in range(4, HELPER_COL + 40):
            ws.column_dimensions[CL(c)].width = 12
        ws.column_dimensions["E"].width = 18
        ws.print_area = f"A1:Q{self.r + 2}"  # helper tables to the right stay out of the printout
        self.wb.active = self.wb.sheetnames.index("Ringkasan")
        for sh in self.wb.worksheets:
            sh.sheet_view.tabSelected = sh.title == "Ringkasan"
        self.wb.calculation.fullCalcOnLoad = True

    def find_after(self, block_prefix, label):
        key = next(k for k in self.S.meta["blok"] if k.startswith(block_prefix))
        start = int(re.sub(r"[A-Z]", "", self.S.meta["blok"][key].split("!")[-1].split(":")[0]))
        for r in range(start - 1, 0, -1):
            row = self.S.s[r - 1]
            if len(row) > 1 and row[1] == label:
                return r
        return None

    def group(self, key, n, helper_row):
        """Group list + helper matrix (to the right) + top 3 table. Returns next helper row."""
        ws, f, S = self.ws, self.f, self.S
        lab = S.labels.get(key, key)
        groups = self.blk(f"S5_{key}_semua_grup")
        hc = HELPER_COL
        # group sizes (helper, to the right)
        ws.cell(row=helper_row, column=hc, value=f"Tabel bantu: jumlah pekerja per {lab.lower()} (dipakai untuk Top 3)").font = BOLD
        self.head(helper_row + 1, ["No", lab, "Jumlah pekerja"], start=hc)
        g1 = helper_row + 2
        for i, g in enumerate(groups):
            rr = g1 + i
            ws.cell(row=rr, column=hc, value=i + 1)
            ws.cell(row=rr, column=hc + 1, value=g["B"])
            self.put(rr, hc + 2, f.count(f.eq(key, g["B"])), f"C{g['row']}", "0")
        g2 = g1 + len(groups) - 1
        GL, GN = f"${CL(hc + 1)}${g1}:${CL(hc + 1)}${g2}", f"${CL(hc + 2)}${g1}:${CL(hc + 2)}${g2}"
        valid = f'(({GL}<>"-")*({GL}<>"(kosong)"))'
        gscore = f"({GN}-ROW({GN})/100000)"
        ranked = [g for g in groups if g["B"] not in ("-", "(kosong)")]
        topn = min(n, len(ranked))
        # matrix rank x finding (helper)
        m0 = g2 + 3
        ws.cell(row=m0, column=hc, value=f"Tabel bantu: jumlah temuan per {lab.lower()} ({topn} terbesar)").font = BOLD
        self.head(m0 + 1, ["Rank", lab, "Jumlah pekerja"] + [t["label"] for t in self.temuan], start=hc)
        ws.cell(row=m0 + 2, column=hc + 1, value="Ikut Top ten:")
        for j, t in enumerate(self.temuan):
            ws.cell(row=m0 + 2, column=hc + 3 + j, value="Ya" if t["top_ten"] else "Tidak")
        mr1 = m0 + 3
        c1, c2 = CL(hc + 3), CL(hc + 2 + len(self.temuan))
        for k in range(1, topn + 1):
            rr = mr1 + k - 1
            gval = f"AGGREGATE(14,6,{gscore}/{valid},{k})"
            gidx = f"AGGREGATE(15,6,(ROW({GN})-ROW(${CL(hc + 2)}${g1})+1)/({gscore}={gval}),1)"
            ws.cell(row=rr, column=hc, value=k)
            self.put(rr, hc + 1, f'=IFERROR(INDEX({GL},{gidx}),"")')
            self.put(rr, hc + 2, f"=IFERROR(INDEX({GN},{gidx}),0)")
            G = f"{CL(hc + 1)}{rr}"
            for j, t in enumerate(self.temuan):
                self.put(rr, hc + 3 + j, f'=IF(${G}="",0,SUMPRODUCT(({f.U(key)}=${G})*{f.flag(t["key"])}*{f.named()}))')
        # top 3 table (readable area)
        t3 = self.blk(f"S5_{key}_top3")
        self.title(f"Top 3 temuan per {lab.lower()} ({topn} {lab.lower()} terbesar)")
        self.head(self.r, ["No", lab, "Jenis penyakit / temuan", "Jumlah", f"% dari {lab.lower()}"])
        tr = self.r + 1
        names = f"${c1}${m0 + 1}:${c2}${m0 + 1}"
        flags = f"${c1}${m0 + 2}:${c2}${m0 + 2}"
        i = 0
        for k in range(1, topn + 1):
            mrow = mr1 + k - 1
            cnt = f"${c1}${mrow}:${c2}${mrow}"
            sc = f"({cnt}-COLUMN({cnt})/1000)"
            for p in range(1, 4):
                rr = tr + i
                srow = t3[i]["row"] if i < len(t3) else None
                val = f"AGGREGATE(14,6,{sc}/(({flags}=\"Ya\")*({cnt}>0)),{p})"
                idx = f"AGGREGATE(15,6,(COLUMN({cnt})-COLUMN(${c1}${mrow})+1)/({sc}={val}),1)"
                ws.cell(row=rr, column=1, value=i + 1)
                self.put(rr, 2, f"={CL(hc + 1)}{mrow}", f"B{srow}" if srow else None)
                self.put(rr, 3, f'=IFERROR(INDEX({names},{idx}),"-")', f"C{srow}" if srow else None)
                self.put(rr, 4, f"=IFERROR(INDEX({cnt},{idx}),0)", f"D{srow}" if srow else None, "0")
                self.put(rr, 5, f"=IFERROR(D{rr}/{CL(hc + 2)}{mrow},0)", f"E{srow}" if srow else None, PCT)
                i += 1
        self.r = tr + i + 1
        self.group_rows = getattr(self, "group_rows", {})
        self.group_rows[key] = (mr1, topn)
        return mr1 + topn + 3

    def komb_group(self, key):
        ws, f, S = self.ws, self.f, self.S
        lab = S.labels.get(key, key)
        blk = self.blk(f"S6_kombinasi_{key}")
        if not blk or key not in getattr(self, "group_rows", {}):
            return
        mr1, topn = self.group_rows[key]
        self.title(f"3 kategori kelainan per {lab.lower()} (jumlah dan % dari pekerja dengan data lengkap)")
        heads = ["Rank", lab, "Data lengkap"]
        for l in KOMB[:-1]:
            heads += [l, "%"]
        self.head(self.r, heads)
        cpl = f.komb_parts()[0]
        for i, r in enumerate(blk):
            rr = self.r + 1 + i
            g = f"{CL(HELPER_COL + 1)}{mr1 + i}"
            ws.cell(row=rr, column=1, value=i + 1)
            self.put(rr, 2, f"={g}", f"B{r['row']}")
            self.put(rr, 3, f"=SUMPRODUCT(({f.U(key)}={g})*{cpl}*{f.named()})", f"C{r['row']}", "0")
            for j, kl in enumerate(KOMB[:-1]):
                col = 4 + 2 * j
                self.put(rr, col, f"=SUMPRODUCT(({f.U(key)}={g})*{f.komb(kl)}*{f.named()})", f"{CL(col)}{r['row']}", "0")
                self.put(rr, col + 1, f"=IFERROR({CL(col)}{rr}/$C{rr},0)", f"{CL(col + 1)}{r['row']}", PCT)
        self.r += len(blk) + 2

    def save(self) -> Path:
        out = self.vendor.with_name(self.vendor.stem.strip() + " - dengan Ringkasan.xlsx")
        tmp = out.with_suffix(".tmp.xlsx")
        self.wb.save(tmp)
        try:
            tmp.replace(out)
        except PermissionError:
            tmp.unlink(missing_ok=True)
            sys.exit(f"'{out.name}' sedang terbuka di Excel. Tutup dulu lalu jalankan ulang.")
        return out


def same(got, want):
    if isinstance(want, dt.datetime):
        want = want.date()
    if isinstance(got, dt.datetime):
        got = got.date()
    if isinstance(want, dt.date) and isinstance(got, (int, float)):
        got = dt.date(1899, 12, 30) + dt.timedelta(days=int(got))
    if isinstance(got, (int, float)) and isinstance(want, (int, float)):
        return abs(got - want) < 1e-9
    if got in (None, "") and want in (None, ""):
        return True
    return got == want


def verify(out: Path, S: Summary, expected) -> list:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "in.xlsx"
        shutil.copy(out, src)
        o = Path(td) / "o"
        o.mkdir()
        subprocess.run([str(SOFFICE), "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(o), str(src)],
                       check=True, capture_output=True, timeout=1800)
        wb = openpyxl.load_workbook(o / "in.xlsx", data_only=True, read_only=True)
        rk = [list(r) for r in wb["Ringkasan"].iter_rows(values_only=True)]
        names = wb.sheetnames
        wb.close()
    bad = []
    for (r, c), addr in expected.items():
        got = rk[r - 1][c - 1] if r - 1 < len(rk) and c - 1 < len(rk[r - 1]) else None
        m = re.fullmatch(r"([A-Z]+)(\d+)", addr)
        want = S.s[int(m.group(2)) - 1][col_index(m.group(1)) - 1]
        if not same(got, want):
            bad.append(f"Ringkasan!{CL(c)}{r} = {got!r}, SUMMARY!{addr} (file Analisa) = {want!r}")
    for extra in ("SUMMARY", "PEKERJA", "DICT_TEMUAN", "DICT_NILAI", "DICT_CUTOFF", "CHECK"):
        if extra in names:
            bad.append(f"sheet {extra} masih ada")
    return bad


PS_RECALC = r"""param([string]$Src, [string]$Out)
$xl = New-Object -ComObject Excel.Application
try {
    $xl.Visible = $false; $xl.DisplayAlerts = $false; $xl.AskToUpdateLinks = $false
    $wb = $xl.Workbooks.Open($Src, 0, $false)
    $xl.CalculateFullRebuild()
    $wb.SaveAs($Out, 51); $wb.Close($false)
} finally {
    $xl.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null; [GC]::Collect()
}
"""


def excel_check(out: Path) -> list:
    """Recalculate a copy in a separate hidden Excel instance and compare every Ringkasan formula cell
    with LibreOffice. Catches Excel-only behaviour (e.g. FALSE>0 is TRUE in Excel)."""
    td = Path(tempfile.mkdtemp())
    src, xl_out = td / "in.xlsx", td / "excel.xlsx"
    shutil.copy(out, src)
    ps = td / "recalc.ps1"
    ps.write_text(PS_RECALC, encoding="utf-8")
    subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps), "-Src", str(src), "-Out", str(xl_out)],
                   check=True, capture_output=True, timeout=1800)
    subprocess.run([str(SOFFICE), "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(td / "lo"), str(src)],
                   check=True, capture_output=True, timeout=1800)
    ex = [list(r) for r in openpyxl.load_workbook(xl_out, data_only=True, read_only=True)["Ringkasan"].iter_rows(values_only=True)]
    lo = [list(r) for r in openpyxl.load_workbook(td / "lo" / "in.xlsx", data_only=True, read_only=True)["Ringkasan"].iter_rows(values_only=True)]
    fw = openpyxl.load_workbook(src, read_only=True)["Ringkasan"]
    cells = [(c.row, c.column) for row in fw.iter_rows() for c in row
             if c.value is not None and str(getattr(c.value, "text", c.value)).startswith("=")]
    bad = []
    for r, c in cells:
        a = lo[r - 1][c - 1] if r - 1 < len(lo) and c - 1 < len(lo[r - 1]) else None
        b = ex[r - 1][c - 1] if r - 1 < len(ex) and c - 1 < len(ex[r - 1]) else None
        if not same(b, a):
            bad.append(f"Excel {CL(c)}{r} = {b!r}, LibreOffice = {a!r}")
    print(f"Excel  : {len(cells)} sel rumus dihitung di Excel (tersembunyi) | beda dengan LibreOffice: {len(bad)}")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("analisa", type=Path)
    ap.add_argument("--cek-excel", action="store_true",
                    help="hitung ulang salinan di Excel tersembunyi dan bandingkan semua sel rumus (perlu izin membuka Excel)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    R = Ringkasan(args.analisa.resolve())
    R.build()
    out = R.save()
    bad = verify(out, R.S, R.expected)
    n_ok = len(R.expected) - len([b for b in bad if b.startswith("Ringkasan")])
    print(f"Hasil  : {out}")
    print(f"Sheet  : hanya 'Ringkasan' ditambahkan di sebelah '{R.main}' | grafik: {R.charts}")
    print(f"Angka dicocokkan dengan SUMMARY file Analisa setelah dihitung ulang: {n_ok}/{len(R.expected)}")
    if args.cek_excel:
        bad += excel_check(out)
    for b in bad[:25]:
        print("   BEDA", b)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
