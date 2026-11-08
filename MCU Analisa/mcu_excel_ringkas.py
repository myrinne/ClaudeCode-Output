"""Vendor Excel + summary sheet next to it, for the doctor who supplied the file (step 4).

Makes a duplicate of the vendor's own workbook (all original sheets kept as they are) and
adds a "Ringkasan" sheet right after the vendor's main sheet: the same tables as the PPT
report, each with a native Excel chart where the PPT has one.

Traceability: the calculation sheets of the analysis workbook (SUMMARY, PEKERJA, DICT_*,
CHECK) are copied into the duplicate with every reference to RAW rewritten to the vendor's
main sheet (RAW was an exact copy, same rows and columns). So Ringkasan -> SUMMARY ->
PEKERJA -> the vendor's own sheet, and Excel's "Trace Precedents" ends on the worker's row
in the original data. The calculation sheets are hidden, not removed.

Usage:
    uv run --with openpyxl --with python-pptx python mcu_excel_ringkas.py "<... - Analisa.xlsx>"

Output: "<vendor file> - dengan Ringkasan.xlsx" next to the vendor file (the vendor file is
not modified). After saving, the file is recalculated with LibreOffice and every Ringkasan
cell is compared with the analysis workbook's SUMMARY.
"""
from __future__ import annotations

import argparse
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
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as CL

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcu_ppt import SOFFICE, Summary  # noqa: E402  (same SUMMARY reader as the PPT step)

TEAL, DARK, SAND = "307F7F", "112929", "D1B984"
PALETTE = [TEAL, SAND, DARK, "7FB8B8", "EADBB4", "A3A3A3", "4F9A9A", "BFA36A"]
# plain, raw-Excel look for the tables (Vidya 2026-11-08): default font, bold headers only, gridlines on
HEAD_FONT = Font(bold=True)
TITLE_FONT = Font(bold=True)
PCT = "0.0%"
CALC_SHEETS = ["SUMMARY", "PEKERJA", "DICT_TEMUAN", "DICT_NILAI", "DICT_CUTOFF", "CHECK"]


def col_of(letter: str) -> int:
    n = 0
    for ch in letter:
        n = n * 26 + ord(ch) - 64
    return n


class Ringkasan:
    def __init__(self, analisa: Path):
        self.src = analisa
        self.S = Summary(analisa)          # recalculated values + block map
        if self.S.check_beda not in (0, None):
            sys.exit(f"Sheet CHECK menunjukkan {self.S.check_beda} BEDA: perbaiki SUMMARY dulu.")
        wa = openpyxl.load_workbook(analisa)
        self.vendor = Path(str(wa["MAP"]["B1"].value))
        self.main = str(wa["MAP"]["B2"].value)
        try:
            self.wb = openpyxl.load_workbook(self.vendor)
        except PermissionError:  # vendor file open in Excel: read a temporary copy
            tmp = Path(tempfile.gettempdir()) / f"ringkas_{self.vendor.name}"
            shutil.copy2(self.vendor, tmp)
            self.wb = openpyxl.load_workbook(tmp)
        if self.main not in self.wb.sheetnames:
            sys.exit(f"Sheet '{self.main}' tidak ada di file vendor.")
        for name in ["Ringkasan"] + CALC_SHEETS:
            if name in self.wb.sheetnames:
                del self.wb[name]
        target = "'" + self.main.replace("'", "''") + "'!"
        for name in CALC_SHEETS:
            self.copy_sheet(wa[name], self.wb.create_sheet(name), target)
        self.ws = self.wb.create_sheet("Ringkasan", self.wb.sheetnames.index(self.main) + 1)
        self.r = 1
        self.expected = {}                 # (row, col) in RINGKASAN -> SUMMARY address
        self.charts = 0

    @staticmethod
    def copy_sheet(src, dst, target):
        from copy import copy as cp
        for row in src.iter_rows():
            for c in row:
                if c.value is None and not c.has_style:
                    continue
                v = c.value
                if isinstance(v, str) and v.startswith("="):
                    v = v.replace("RAW!", target)
                d = dst.cell(row=c.row, column=c.column, value=v)
                if c.has_style:
                    d.font, d.fill, d.number_format = cp(c.font), cp(c.fill), c.number_format
                    d.alignment, d.border = cp(c.alignment), cp(c.border)
        for k, dim in src.column_dimensions.items():
            dst.column_dimensions[k].width = dim.width
        dst.freeze_panes = src.freeze_panes
        for m in src.merged_cells.ranges:
            dst.merge_cells(str(m))

    # ------------------------------------------------------------ helpers
    def ref(self, row, col_letter):
        return f"=SUMMARY!{col_letter}{row}"

    def put(self, row, col, srow, scol, fmt=None):
        c = self.ws.cell(row=row, column=col, value=self.ref(srow, scol))
        if fmt:
            c.number_format = fmt
        self.expected[(row, col)] = f"{scol}{srow}"
        return c

    def title(self, text, note=None):
        self.r += 1
        self.ws.cell(row=self.r, column=1, value=text).font = TITLE_FONT
        if note:
            self.r += 1
            c = self.ws.cell(row=self.r, column=1, value=note)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            self.ws.merge_cells(start_row=self.r, start_column=1, end_row=self.r, end_column=5)
            self.ws.row_dimensions[self.r].height = 15 * max(1, len(note) // 70 + 1)
        self.r += 1

    def head(self, row, values, start=1):
        for j, v in enumerate(values):
            c = self.ws.cell(row=row, column=start + j, value=v)
            c.font = HEAD_FONT

    def table(self, block, cols, headers, fmts=None, skip=None):
        """Copy a SUMMARY block: cols = SUMMARY letters to show. Returns (first_row, last_row)."""
        rows = [r for r in self.S.block(block) if not (skip and skip(r))]
        if not rows:
            return None
        self.head(self.r, headers)
        first = self.r + 1
        for i, r in enumerate(rows):
            rr = first + i
            for j, L in enumerate(cols):
                self.put(rr, 1 + j, r["row"], L, (fmts or {}).get(L))
        last = first + len(rows) - 1
        self.r = last + 2
        return first, last

    def bar(self, first, last, cat_col, val_col, title, anchor_row, height_rows=None):
        ch = BarChart()
        ch.type = "bar"
        ch.style = 10
        ch.title = title
        ch.legend = None
        data = Reference(self.ws, min_col=val_col, min_row=first, max_row=last)
        cats = Reference(self.ws, min_col=cat_col, min_row=first, max_row=last)
        ch.add_data(data, titles_from_data=False)
        ch.set_categories(cats)
        s = ch.series[0]
        s.graphicalProperties = GraphicalProperties(solidFill=TEAL)
        s.graphicalProperties.line.solidFill = TEAL
        ch.dataLabels = DataLabelList(showVal=True, showCatName=False, showSerName=False, showLegendKey=False,
                                      showPercent=False, showLeaderLines=False)
        ch.gapWidth = 60 if last - first >= 3 else 180
        ch.x_axis.scaling.orientation = "maxMin"   # first row on top, like the PPT
        ch.x_axis.delete = False
        ch.y_axis.delete = True
        ch.y_axis.majorGridlines = None
        n = last - first + 1
        ch.height = max(6.0, 0.9 * n + 2.5)
        ch.width = 17
        self.ws.add_chart(ch, f"G{anchor_row}")
        self.charts += 1
        return int(ch.height / 0.5) + 1         # rows covered (approx.)

    def doughnut(self, first, last, cat_col, val_col, title, anchor_row):
        ch = DoughnutChart()
        ch.title = title
        ch.holeSize = 55
        data = Reference(self.ws, min_col=val_col, min_row=first, max_row=last)
        cats = Reference(self.ws, min_col=cat_col, min_row=first, max_row=last)
        ch.add_data(data, titles_from_data=False)
        ch.set_categories(cats)
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

    def section(self, title, block, cols, headers, fmts, chart=None, skip=None, note=None):
        start = self.r
        self.title(title, note)
        res = self.table(block, cols, headers, fmts, skip)
        if not res:
            self.r = start
            return None
        first, last = res
        used = 0
        rows = [r for r in self.S.block(block) if not (skip and skip(r))]
        chart_last = last - sum(1 for r in rows if str(r["B"]).startswith("Salah satu"))
        if chart == "bar":
            used = self.bar(first, chart_last, 2, 3, title, start + 1)
        elif chart == "doughnut":
            used = self.doughnut(first, last, 2, 3, title, start + 1)
        self.r = max(self.r, start + 1 + used + 1)
        return first, last

    def find_block(self, topik):
        return next((k for k in self.S.meta["blok"] if k == f"Topik_{topik}" or re.fullmatch(r"S\d+_" + re.escape(topik), k)), None)

    # ------------------------------------------------------------ build
    def build(self):
        ws, S = self.ws, self.S
        ws["A1"] = "RINGKASAN HASIL MCU"
        ws["A1"].font = Font(bold=True)
        ws["A2"] = str(S.raw_a1 or "").strip()
        ws["A2"].font = Font(bold=True)
        ws["A3"] = (f"Setiap angka di sheet ini adalah rumus ke sheet SUMMARY, yang dihitung dari sheet PEKERJA dan sheet '{self.main}' "
                    "(data asli). Sheet hitungan disembunyikan; tampilkan lewat klik kanan tab > Unhide. Data asli tidak diubah.")
        ws["A5"] = "Jumlah peserta MCU (N)"
        self.put(5, 3, 3, "C")
        a, b = S.meta["blok"]["S3_periode"].split("!")[-1].split(":")
        ws["A6"] = "Tanggal MCU pertama"
        self.put(6, 3, int(a[1:]), a[0], "dd-mm-yyyy")
        ws["A7"] = "Tanggal MCU terakhir"
        self.put(7, 3, int(b[1:]), b[0], "dd-mm-yyyy")
        for r in (5, 6, 7):
            ws.cell(row=r, column=1).font = Font(bold=True)
        self.r = 8
        f3 = {"C": "0", "D": PCT}
        hdr = ["No", "Kategori", "Jumlah", "%"]
        cols = ["A", "B", "C", "D"]

        self.section("Karakteristik demografi: kelompok umur", "S3_kelompok_umur", cols, hdr, f3, "doughnut",
                     skip=lambda r: not r["C"])
        self.section("Karakteristik demografi: jenis kelamin", "S3_jenis_kelamin", cols, hdr, f3, skip=lambda r: not r["C"])
        hab = []
        for key, lab, yes in (("S3_merokok", "Merokok", "Merokok"), ("S3_alkohol", "Konsumsi alkohol", "Ya"), ("S3_olahraga", "Olahraga", "Ya")):
            if self.section(f"Kebiasaan: {lab.lower()}", key, cols, hdr, f3):
                r = next((x for x in S.block(key) if x["B"] == yes), None)
                if r:
                    hab.append((lab, r))
        if hab:
            start = self.r
            self.title("Kebiasaan pekerja (ringkasan, seperti grafik di PPT)")
            self.head(self.r, ["", "Kebiasaan", "Jumlah", "%"])
            first = self.r + 1
            for i, (lab, r) in enumerate(hab):
                rr = first + i
                ws.cell(row=rr, column=2, value=lab)
                self.put(rr, 3, r["row"], "C", "0")
                self.put(rr, 4, r["row"], "D", PCT)
            last = first + len(hab) - 1
            used = self.bar(first, last, 2, 3, "Kebiasaan pekerja", start + 1)
            self.r = max(last + 2, start + 1 + used + 1)
        self.section("Status kelaikan kerja (keputusan vendor)", "kelaikan_fitness", cols, hdr, f3, "doughnut")
        self.section("Risiko kesehatan (keputusan vendor)", "kelaikan_risiko", cols, hdr, f3)
        n_row = f"% dari total peserta MCU"
        self.section("Top ten penyakit dan temuan", "S4_top_ten", cols, ["No", "Jenis penyakit / temuan", "Jumlah", n_row], f3, "bar")
        for key, n in S.meta["grup"]:
            lab = S.labels.get(key, key)
            self.section(f"Top 3 temuan per {lab.lower()} ({n} {lab.lower()} terbesar)", f"S5_{key}_top3", ["A", "B", "C", "D", "E"],
                         ["No", lab, "Jenis penyakit / temuan", "Jumlah", f"% dari {lab.lower()}"], {"D": "0", "E": PCT})
        nr, note = S.find_row("Abnormal 1 rasio")
        self.section("Analisa 3 kategori kelainan (rasio TG/HDL, HbA1c, lingkar perut)", "S6_kombinasi_total", cols, hdr, f3, "bar",
                     note=note)
        for key, n in S.meta["grup"]:
            lab = S.labels.get(key, key)
            blk = S.block(f"S6_kombinasi_{key}")
            if not blk:
                continue
            self.title(f"3 kategori kelainan per {lab.lower()} (jumlah dan % dari pekerja dengan data lengkap)")
            heads = ["Rank", lab, "Data lengkap"]
            labels = ["Ketiganya", "Rasio + HbA1c", "Rasio + LP", "HbA1c + LP", "Hanya rasio", "Hanya HbA1c", "Hanya LP", "Tidak ada"]
            for l in labels:
                heads += [l, "%"]
            self.head(self.r, heads)
            letters = [CL(c) for c in range(1, 4 + 2 * 8)]
            for i, r in enumerate(blk):
                rr = self.r + 1 + i
                for j, L in enumerate(letters):
                    fmt = PCT if j >= 4 and j % 2 == 0 else ("0" if j >= 2 else None)
                    self.put(rr, 1 + j, r["row"], L, fmt)
            self.r += len(blk) + 2
        for cfg in self._topics():
            tp, block, ttl = cfg
            self.section(ttl, block, cols, ["No", "Temuan / kategori", "Jumlah", "%"], f3, "bar",
                         skip=lambda r: str(r["B"]).startswith("Tanpa"))
        # other topics: one line each (any finding in the topic)
        other = ["Gula darah", "Fungsi ginjal", "Hematologi", "Urinalisa", "THT", "Rontgen thorax", "EKG", "Muskuloskeletal", "Lain-lain"]
        rows = []
        for tp in other:
            k = self.find_block(tp)
            for r in (S.block(k) if k else []):
                if str(r["B"]).startswith("Salah satu") and r["C"]:
                    rows.append((tp, r))
        if rows:
            self.title("Temuan lain (pekerja dengan salah satu temuan pada topik tersebut)")
            self.head(self.r, ["Topik", "Keterangan", "Jumlah", "%"])
            for i, (tp, r) in enumerate(rows):
                rr = self.r + 1 + i
                ws.cell(row=rr, column=1, value=tp)
                self.put(rr, 2, r["row"], "B")
                self.put(rr, 3, r["row"], "C", "0")
                self.put(rr, 4, r["row"], "D", PCT)
            self.r += len(rows) + 2
        ws.column_dimensions["A"].width = 8
        ws.column_dimensions["B"].width = 46
        ws.column_dimensions["C"].width = 26
        for c in range(4, 20):
            ws.column_dimensions[CL(c)].width = 12
        ws.sheet_view.showGridLines = True
        # calculation sheets at the end, hidden; Ringkasan right after the vendor's main sheet
        for name in CALC_SHEETS:
            self.wb[name].sheet_state = "hidden"
            self.wb[name].sheet_properties.tabColor = "A6A6A6"
        self.wb.active = self.wb.sheetnames.index("Ringkasan")
        for sh in self.wb.worksheets:
            sh.sheet_view.tabSelected = sh.title == "Ringkasan"
        self.wb.calculation.fullCalcOnLoad = True

    def _topics(self):
        out = []
        order = [("Profil lemak", "Gangguan metabolisme lemak"), ("Status gizi", "Status gizi"), ("Tekanan darah", "Tekanan darah"),
                 ("Fungsi paru", "Fungsi pernapasan (kesimpulan spirometri vendor)"), ("Asam urat", "Metabolisme asam urat"),
                 ("Fungsi hati", "Peningkatan enzim transaminase"), ("Gigi", "Kelainan gigi"), ("Tajam penglihatan", "Gangguan tajam penglihatan")]
        for tp, ttl in order:
            if tp == "Fungsi paru" and self.S.meta["blok"].get("S11b_spiro_kesimpulan"):
                out.append((tp, "S11b_spiro_kesimpulan", ttl))
            else:
                k = self.find_block(tp)
                if k:
                    out.append((tp, k, ttl))
        return out

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


def verify(out: Path, S: Summary, expected) -> list:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "in.xlsx"
        shutil.copy(out, src)
        o = Path(td) / "o"
        o.mkdir()
        subprocess.run([str(SOFFICE), "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(o), str(src)],
                       check=True, capture_output=True, timeout=900)
        wb = openpyxl.load_workbook(o / "in.xlsx", data_only=True, read_only=True)
        rk = [list(r) for r in wb["Ringkasan"].iter_rows(values_only=True)]
        beda = list(wb["CHECK"].iter_rows(min_row=2, max_row=2, values_only=True))[0][1]
        wb.close()
    bad = []
    for (r, c), addr in expected.items():
        got = rk[r - 1][c - 1] if c - 1 < len(rk[r - 1]) else None
        m = re.fullmatch(r"([A-Z]+)(\d+)", addr)
        want = S.s[int(m.group(2)) - 1][col_of(m.group(1)) - 1]
        same = (got == want) or (isinstance(got, (int, float)) and isinstance(want, (int, float)) and abs(got - want) < 1e-9) \
            or (got in (None, "") and want in (None, ""))
        if not same:
            bad.append(f"Ringkasan!{CL(c)}{r} = {got!r}, SUMMARY!{addr} (file Analisa) = {want!r}")
    if beda not in (0, None):
        bad.append(f"sheet CHECK: {beda} BEDA")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("analisa", type=Path)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    R = Ringkasan(args.analisa.resolve())
    R.build()
    out = R.save()
    bad = verify(out, R.S, R.expected)
    print(f"Hasil  : {out}")
    print(f"Sel rumus di Ringkasan: {len(R.expected)} | grafik: {R.charts} | cocok dengan SUMMARY file Analisa setelah dihitung ulang: "
          f"{len(R.expected) - len([b for b in bad if b.startswith('Ringkasan')])}/{len(R.expected)}")
    for b in bad[:20]:
        print("   BEDA", b)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
