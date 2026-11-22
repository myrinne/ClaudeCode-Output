"""Raw-data workbook for the WBGT-TEWL-H2O2 thesis (Instalasi Gizi RSCM,
30 Nov - 2 Des 2026).

Sheets follow the field forms made by make_berkas.py (kuesioner Bagian A-J,
Lampiran 4 skoring beban kerja SNI 7269:2009) and Bab 3.6-3.7 of the proposal.
Raw entry sheets hold values only; every derived variable is a formula.

Usage:
  python make_workbook.py            -> empty template in the OneDrive thesis folder
  python make_workbook.py --test DIR -> filled copy with test data in DIR (for checking)
The script refuses to overwrite an existing workbook, so entered data is never lost.
"""
import sys
from datetime import date, time
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

OUT_DIR = Path(r"C:\Users\vidya\OneDrive\Documents\PPDS Okupasi\Usulan Thesis\Gizi\Data Penelitian")
FILE_NAME = "Data Mentah Tesis WBGT-TEWL-H2O2.xlsx"
FIRST, LAST = 2, 101                      # subject rows (85 codes + 15 spare rows)
DAYS = [("H1", date(2026, 11, 30), "pagi", 25), ("H2", date(2026, 12, 1), "pagi", 35),
        ("H3", date(2026, 12, 2), "subuh", 25)]
SHIFTS = ["subuh", "pagi", "siang"]
ZONES = [("E1", "Zona memasak makanan utama", "Panas"), ("E2", "Zona memasak makanan selingan", "Panas"),
         ("E3", "Dapur susu / enteral", "Panas"), ("E4", "Zona pemorsian, penyajian, dan pencucian", "Panas"),
         ("E5", "Ruang persiapan bahan sayuran", "Tidak panas"),
         ("E6", "Ruang persiapan bahan daging", "Tidak panas"),
         ("E7", "Ruang penerimaan bahan", "Tidak panas"), ("E8", "Ruang administrasi gizi", "Tidak panas")]
BK_NILAI = {"F1": 1.00, "F2": 1.30, "F3": 3.30, "F4": 5.25}   # Lampiran 4, SNI 7269:2009 Lampiran A

INPUT = PatternFill("solid", fgColor="FFF8DC")     # cream = type here
CALC = PatternFill("solid", fgColor="EDEDED")      # grey = formula, do not type
HEAD = PatternFill("solid", fgColor="1F4E78")
HFONT = Font(bold=True, color="FFFFFF")
RED = Font(color="C00000", bold=True)
THIN = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
WRAP = Alignment(wrap_text=True, vertical="top")

# ---------------------------------------------------------------- 1_Subjek
# (key, header, kind, validation)  kind: text/date/time/num/list ; validation: (min,max) or list
SUBJ = [
    ("kode", "A1 Kode subjek", "text", None),
    ("hari", "Hari", "text", None),
    ("tanggal", "A2 Tanggal data", "date", None),
    ("shift", "Shift", "list", SHIFTS),
    ("partisipasi", "Status partisipasi", "list", ["Ikut", "Tidak bersedia", "Tereksklusi saat skrining"]),
    ("enum", "A3 Enumerator", "text", None),
    ("jabatan", "A4 Departemen / jabatan", "text", None),
    ("lahir", "B1 Tanggal lahir", "date", None),
    ("jk", "B2 Jenis kelamin (L/P)", "list", ["L", "P"]),
    ("didik", "B3 Pendidikan", "list", ["SD", "SMP", "SMA/SMK", "D3/S1", "Lainnya"]),
    ("bb", "C1 Berat badan (kg)", "num", (30, 150)),
    ("tb", "C2 Tinggi badan (cm)", "num", (130, 200)),
    ("masa_th", "D1 Masa kerja (tahun)", "num", (0, 40)),
    ("masa_bl", "D1 Masa kerja (bulan)", "num", (0, 11)),
    ("jam_mulai", "D2 Jam mulai kerja", "time", None),
    ("jam_selesai", "D3 Jam selesai kerja", "time", None),
    ("lama", "D4 Lama kerja per hari (jam)", "num", (1, 16)),
    ("hari_mg", "D5 Hari kerja per minggu", "num", (1, 7)),
    *[(z, f"{z} {n} (jam)", "num", (0, 16)) for z, n, _ in ZONES],
    *[(f, f"{f} jam/hari", "num", (0, 16)) for f in BK_NILAI],
    ("g1", "G1 Status merokok", "list", ["Tidak pernah", "Berhenti", "Aktif"]),
    ("g1_th", "G1 Berhenti sejak tahun", "num", (1950, 2026)),
    ("g2", "G2 Batang per hari", "num", (0, 80)),
    ("g3", "G3 Lama merokok (tahun)", "num", (0, 60)),
    ("g5", "G5 Merokok 3 jam terakhir", "list", ["Ya", "Tidak"]),
    *[(f"h{i}", f"H{i}", "list", ["Ya", "Tidak"]) for i in range(1, 8)],
    ("i1", "I1 Pelembap lengan 1 minggu", "list", ["Ya", "Tidak"]),
    ("i2", "I2 Kontak air/sabun >=2 jam/hari", "list", ["Ya", "Tidak"]),
    ("j1", "J1 Jam selesai shift", "time", None),
    ("j2", "J2 Jam mulai aklimatisasi", "time", None),
    ("j3", "J3 Jam pengukuran TEWL", "time", None),
    ("j4_suhu", "J4 Suhu ruang (°C)", "num", (10, 40)),
    ("j4_rh", "J4 Kelembapan relatif (%)", "num", (5, 100)),
    ("tewl1", "J5 TEWL bacaan 1 (g/m²/h)", "num", (0, 150)),
    ("tewl2", "J5 TEWL bacaan 2", "num", (0, 150)),
    ("tewl3", "J5 TEWL bacaan 3", "num", (0, 150)),
    ("j6", "J6 Jam pengambilan darah", "time", None),
    ("j7", "J7 Catatan", "text", None),
    ("sampel", "Status sampel", "list", ["Layak", "Gagal pungsi", "Hemolisis", "TEWL tidak layak"]),
]
S = {k: get_column_letter(i + 1) for i, (k, *_) in enumerate(SUBJ)}
DOUBLE = ["lahir", "bb", "tb", *[z for z, *_ in ZONES], *BK_NILAI, "g2", "g3",
          "tewl1", "tewl2", "tewl3", "j1", "j6"]

wb = Workbook()


def header(ws, row, labels, widths=None, height=45):
    for c, lab in enumerate(labels, 1):
        cell = ws.cell(row=row, column=c, value=lab)
        cell.fill, cell.font, cell.alignment, cell.border = HEAD, HFONT, Alignment(wrap_text=True,
                                                                                  vertical="center"), THIN
        if widths:
            ws.column_dimensions[get_column_letter(c)].width = widths[c - 1] if isinstance(widths, list) else widths
    ws.row_dimensions[row].height = height


def paint(ws, rng, fill):
    for row in ws[rng]:
        for c in row:
            c.fill, c.border = fill, THIN


def fmt(ws, col, rows, kind):
    nf = {"date": "DD/MM/YYYY", "time": "HH:MM"}.get(kind)
    if nf:
        for r in rows:
            ws[f"{col}{r}"].number_format = nf


def validate(ws, col, r1, r2, kind, spec):
    rng = f"{col}{r1}:{col}{r2}"
    if kind == "list":
        dv = DataValidation(type="list", formula1='"' + ",".join(spec) + '"', allow_blank=True)
    elif kind == "num" and spec:
        dv = DataValidation(type="decimal", operator="between", formula1=str(spec[0]),
                            formula2=str(spec[1]), allow_blank=True)
        dv.error, dv.errorTitle = f"Nilai harus {spec[0]}–{spec[1]}", "Di luar rentang wajar"
    elif kind == "time":
        dv = DataValidation(type="time", operator="between", formula1="0", formula2="0.999988",
                            allow_blank=True)
        dv.error = "Tulis jam sebagai hh:mm, misalnya 13:45"
    elif kind == "date":
        dv = DataValidation(type="date", operator="between", formula1="1", formula2="73051",
                            allow_blank=True)
        dv.error = "Tulis tanggal sebagai dd/mm/yyyy"
    else:
        return
    dv.showErrorMessage = True
    ws.add_data_validation(dv)
    dv.add(rng)


def entry_sheet(ws, cols, prefill=True):
    header(ws, 1, [h for _, h, *_ in cols], 14)
    ws.freeze_panes = "B2"
    for i, (k, _, kind, spec) in enumerate(cols, 1):
        col = get_column_letter(i)
        paint(ws, f"{col}{FIRST}:{col}{LAST}", INPUT)
        fmt(ws, col, range(FIRST, LAST + 1), kind)
        validate(ws, col, FIRST, LAST, kind, spec)
    if prefill:
        r = FIRST
        for day, tgl, shift, n in DAYS:
            for j in range(1, n + 1):
                ws[f"{S['kode']}{r}"] = f"{day}-{j:02d}"
                ws[f"{S['hari']}{r}"] = day
                ws[f"{S['tanggal']}{r}"] = tgl
                ws[f"{S['shift']}{r}"] = shift
                r += 1


ws1 = wb.active
ws1.title = "1_Subjek"
entry_sheet(ws1, SUBJ)

# ------------------------------------------------------- 1b double entry + check
ws1b = wb.create_sheet("1b_Entri_Ulang")
cols1b = [("kode", "Kode (otomatis)", "text", None)] + [c for c in SUBJ if c[0] in DOUBLE]
header(ws1b, 1, [h for _, h, *_ in cols1b], 14)
ws1b.freeze_panes = "B2"
for i, (k, _, kind, spec) in enumerate(cols1b, 1):
    col = get_column_letter(i)
    for r in range(FIRST, LAST + 1):
        if k == "kode":
            ws1b[f"{col}{r}"] = f'=IF(\'1_Subjek\'!{S["kode"]}{r}="","",\'1_Subjek\'!{S["kode"]}{r})'
            ws1b[f"{col}{r}"].fill = CALC
        else:
            ws1b[f"{col}{r}"].fill, ws1b[f"{col}{r}"].border = INPUT, THIN
    fmt(ws1b, col, range(FIRST, LAST + 1), kind)
    if k != "kode":
        validate(ws1b, col, FIRST, LAST, kind, spec)

wsc = wb.create_sheet("Cek_Entri")
wsc["A1"] = "Jumlah sel BEDA antara 1_Subjek dan 1b_Entri_Ulang:"
wsc["A1"].font = Font(bold=True)
header(wsc, 3, [h for _, h, *_ in cols1b], 14)
for i, (k, *_) in enumerate(cols1b, 1):
    col = get_column_letter(i)
    for r in range(FIRST, LAST + 1):
        rr = r + 2
        if k == "kode":
            wsc[f"{col}{rr}"] = f"='1b_Entri_Ulang'!A{r}"
        else:
            a, b = f"'1_Subjek'!{S[k]}{r}", f"'1b_Entri_Ulang'!{col}{r}"
            wsc[f"{col}{rr}"] = f'=IF(AND({a}="",{b}=""),"",IF({b}="","belum",IF({a}={b},"","BEDA")))'
last_col = get_column_letter(len(cols1b))
wsc["E1"] = f'=COUNTIF(B4:{last_col}{LAST + 2},"BEDA")'
wsc["F1"] = f'=COUNTIF(B4:{last_col}{LAST + 2},"belum")&" sel belum dientri ulang"'
wsc.conditional_formatting.add(f"B4:{last_col}{LAST + 2}",
                               FormulaRule(formula=['B4="BEDA"'], font=RED,
                                           fill=PatternFill("solid", fgColor="FFC7CE")))
wsc.freeze_panes = "B4"

# ---------------------------------------------------------------- 2_Lingkungan
wsl = wb.create_sheet("2_Lingkungan")
LCOL = ["Shift", "Tanggal ukur", "Putaran", "Zona", "Nama zona", "Jam pasang/pindah alat", "Jam baca",
        "WBGT 1 (°C)", "WBGT 2", "WBGT 3", "Suhu kering Ta (°C)", "RH (%)", "Tg (°C)", "PM2.5 1 (µg/m³)",
        "PM2.5 2", "PM2.5 3", "Catatan", "WBGT rerata", "PM2.5 rerata", "Tren bacaan", "Ekuilibrasi (menit)"]
header(wsl, 1, LCOL, [8, 12, 8, 7, 30, 11, 9, 9, 9, 9, 10, 8, 8, 10, 9, 9, 22, 10, 10, 26, 12])
wsl.freeze_panes = "F2"
r = 2
for sh in SHIFTS:
    for put in (1, 2):
        for z, nm, _ in ZONES:
            wsl[f"A{r}"], wsl[f"C{r}"], wsl[f"D{r}"], wsl[f"E{r}"] = sh, put, z, nm
            r += 1
LROWS = range(2, r)
LLAST = r - 1
for rr in LROWS:
    for c in "BFGHIJKLMNOPQ":
        wsl[f"{c}{rr}"].fill, wsl[f"{c}{rr}"].border = INPUT, THIN
    wsl[f"B{rr}"].number_format = "DD/MM/YYYY"
    wsl[f"F{rr}"].number_format = wsl[f"G{rr}"].number_format = "HH:MM"
    wsl[f"R{rr}"] = f'=IF(COUNT(H{rr}:J{rr})=0,"",ROUND(AVERAGE(H{rr}:J{rr}),2))'
    wsl[f"S{rr}"] = f'=IF(COUNT(N{rr}:P{rr})=0,"",ROUND(AVERAGE(N{rr}:P{rr}),1))'
    wsl[f"T{rr}"] = (f'=IF(COUNT(H{rr}:J{rr})<3,"",IF(OR(AND(H{rr}<I{rr},I{rr}<J{rr}),'
                     f'AND(H{rr}>I{rr},I{rr}>J{rr})),"TREN: perpanjang ekuilibrasi",""))')
    wsl[f"U{rr}"] = (f'=IF(COUNT(F{rr}:G{rr})<2,"",IF(ROUND((G{rr}-F{rr})*1440,0)<20,'
                     f'ROUND((G{rr}-F{rr})*1440,0)&" (<20!)",ROUND((G{rr}-F{rr})*1440,0)))')
    for c in "RSTU":
        wsl[f"{c}{rr}"].fill = CALC
for c, lo, hi in (("H", 10, 45), ("I", 10, 45), ("J", 10, 45), ("K", 10, 50), ("L", 5, 100),
                  ("M", 10, 70), ("N", 0, 5000), ("O", 0, 5000), ("P", 0, 5000)):
    validate(wsl, c, 2, LLAST, "num", (lo, hi))
validate(wsl, "B", 2, LLAST, "date", None)
validate(wsl, "F", 2, LLAST, "time", None)
validate(wsl, "G", 2, LLAST, "time", None)
wsl.conditional_formatting.add(f"T2:U{LLAST}", FormulaRule(formula=['OR(LEFT(T2,4)="TREN",ISNUMBER(SEARCH("<20",U2)))'],
                                                           font=RED))

# ---------------------------------------------------------------- 3_Matriks_Zona
wsm = wb.create_sheet("3_Matriks_Zona")
wsm["A1"] = "Rerata per zona dan shift (dari 2_Lingkungan). Dipakai untuk WBGT/PM2.5 individual dan Tabel 4.2."
wsm["A1"].font = Font(bold=True)
wsm["D3"], wsm["G3"], wsm["J3"] = "WBGT (°C)", "PM2.5 setara-optik (µg/m³)", "Rerata semua shift"
for c in ("D3", "G3", "J3"):
    wsm[c].font = Font(bold=True)
header(wsm, 4, ["Zona", "Nama zona", "Area", *SHIFTS, *SHIFTS, "RH (%)", "Ta (°C)"],
       [7, 34, 12, 9, 9, 9, 9, 9, 9, 9, 9], height=30)
for i, (z, nm, area) in enumerate(ZONES):
    rr = 5 + i
    wsm[f"A{rr}"], wsm[f"B{rr}"], wsm[f"C{rr}"] = z, nm, area
    for j, sh in enumerate(SHIFTS):
        for base, src in ((4, "R"), (7, "S")):
            col = get_column_letter(base + j)
            wsm[f"{col}{rr}"] = (f"=IFERROR(ROUND(AVERAGEIFS('2_Lingkungan'!${src}$2:${src}${LLAST},"
                                 f"'2_Lingkungan'!$A$2:$A${LLAST},\"{sh}\",'2_Lingkungan'!$D$2:$D${LLAST},$A{rr}),2),\"\")")
            wsm[f"{col}{rr}"].fill = CALC
    for col, src in (("J", "L"), ("K", "K")):
        wsm[f"{col}{rr}"] = (f"=IFERROR(ROUND(AVERAGEIFS('2_Lingkungan'!${src}$2:${src}${LLAST},"
                             f"'2_Lingkungan'!$D$2:$D${LLAST},$A{rr}),1),\"\")")
        wsm[f"{col}{rr}"].fill = CALC
MAT_W, MAT_W_HDR = "'3_Matriks_Zona'!$D$5:$F$12", "'3_Matriks_Zona'!$D$4:$F$4"
MAT_P, MAT_P_HDR = "'3_Matriks_Zona'!$G$5:$I$12", "'3_Matriks_Zona'!$G$4:$I$4"

# ---------------------------------------------------------------- 4_Lab_H2O2
wsh = wb.create_sheet("4_Lab_H2O2")
wsh["A1"] = ("Kurva standar H2O2 (Elabscience E-BC-K102-M, 405 nm). Bila laboratorium sudah memberi kadar akhir, "
             "isi kolom H; kolom H dipakai lebih dulu daripada hasil hitung. Cocokkan rumus dengan manual kit.")
wsh["A1"].alignment = WRAP
wsh.merge_cells("A1:L1")
wsh.row_dimensions[1].height = 32
for rr, lab in ((3, "Faktor pengenceran"), (4, "Absorbans blanko"), (5, "Slope"), (6, "Intersep"),
                (7, "R² kurva standar"), (8, "Standar terendah / tertinggi (mmol/L)")):
    wsh[f"A{rr}"] = lab
wsh["B3"], wsh["B3"].fill = 1, INPUT
wsh["B4"].fill = INPUT
header(wsh, 10, ["Standar (mmol/L)", "Abs 1", "Abs 2", "Rerata", "Rerata − blanko"], height=30)
for rr in range(11, 19):
    for c in "ABC":
        wsh[f"{c}{rr}"].fill, wsh[f"{c}{rr}"].border = INPUT, THIN
    wsh[f"D{rr}"] = f'=IF(COUNT(B{rr}:C{rr})=0,"",AVERAGE(B{rr}:C{rr}))'
    wsh[f"E{rr}"] = f'=IF(D{rr}="","",D{rr}-N($B$4))'
    wsh[f"D{rr}"].fill = wsh[f"E{rr}"].fill = CALC
wsh["B5"] = '=IF(COUNT(A11:A18)<2,"",SLOPE(E11:E18,A11:A18))'
wsh["B6"] = '=IF(COUNT(A11:A18)<2,"",INTERCEPT(E11:E18,A11:A18))'
wsh["B7"] = '=IF(COUNT(A11:A18)<2,"",ROUND(RSQ(E11:E18,A11:A18),4))'
wsh["B8"] = '=IF(COUNT(A11:A18)=0,"",MIN(A11:A18)&" / "&MAX(A11:A18))'
for c in ("B5", "B6", "B7", "B8"):
    wsh[c].fill = CALC
header(wsh, 20, ["Kode subjek", "Sumur", "Abs 1", "Abs 2", "Rerata Abs", "CV duplo (%)",
                 "Kadar hitung (mmol/L)", "Kadar dari lab (mmol/L)", "Hemolisis", "Catatan",
                 "H2O2 final (mmol/L)", "Peringatan"], [12, 8, 9, 9, 10, 10, 12, 12, 10, 22, 12, 30], height=30)
HFIRST, HLAST = 21, 120
for rr in range(HFIRST, HLAST + 1):
    for c in "ABCDHIJ":
        wsh[f"{c}{rr}"].fill, wsh[f"{c}{rr}"].border = INPUT, THIN
    wsh[f"E{rr}"] = f'=IF(COUNT(C{rr}:D{rr})=0,"",AVERAGE(C{rr}:D{rr}))'
    wsh[f"F{rr}"] = f'=IF(COUNT(C{rr}:D{rr})<2,"",ROUND(STDEV(C{rr}:D{rr})/AVERAGE(C{rr}:D{rr})*100,1))'
    wsh[f"G{rr}"] = (f'=IF(OR(E{rr}="",$B$5="",$B$5=0),"",'
                     f'ROUND((E{rr}-N($B$4)-$B$6)/$B$5*N($B$3),3))')
    wsh[f"K{rr}"] = f'=IF(ISNUMBER(H{rr}),H{rr},G{rr})'
    wsh[f"L{rr}"] = (f'=IF(K{rr}="","",IF(COUNT($A$11:$A$18)=0,"",'
                     f'IF(K{rr}<MIN($A$11:$A$18),"di bawah standar terendah",'
                     f'IF(K{rr}>MAX($A$11:$A$18),"di atas standar tertinggi","")))'
                     f'&IF(AND(ISNUMBER(F{rr}),N(F{rr})>10)," CV>10%",""))')
    for c in "EFGKL":
        wsh[f"{c}{rr}"].fill = CALC
validate(wsh, "I", HFIRST, HLAST, "list", ["Ya", "Tidak"])
for c in "CD":
    validate(wsh, c, HFIRST, HLAST, "num", (0, 4))
wsh.freeze_panes = "B21"
LAB_CODE, LAB_VAL, LAB_HEM = (f"'4_Lab_H2O2'!$A${HFIRST}:$A${HLAST}", f"'4_Lab_H2O2'!$K${HFIRST}:$K${HLAST}",
                              f"'4_Lab_H2O2'!$I${HFIRST}:$I${HLAST}")

# ---------------------------------------------------------------- 5_Hitung
wsk = wb.create_sheet("5_Hitung")


def s(key, r):
    return f"'1_Subjek'!{S[key]}{r}"


CALCS = [  # (key, header, formula builder)
    ("kode", "Kode", lambda r, c: f'=IF({s("kode", r)}="","",{s("kode", r)})'),
    ("shift", "Shift", lambda r, c: f'=IF({s("shift", r)}="","",{s("shift", r)})'),
    ("usia", "Usia (tahun)", lambda r, c: f'=IF(OR({s("lahir", r)}="",{s("tanggal", r)}=""),"",'
                                           f'INT(YEARFRAC({s("lahir", r)},{s("tanggal", r)},1)))'),
    ("jk01", "JK (1=L, 0=P)", lambda r, c: f'=IF({s("jk", r)}="L",1,IF({s("jk", r)}="P",0,""))'),
    ("imt", "IMT (kg/m²)", lambda r, c: f'=IF(OR({s("bb", r)}="",{s("tb", r)}=""),"",'
                                         f'ROUND({s("bb", r)}/({s("tb", r)}/100)^2,2))'),
    ("masa", "Masa kerja (tahun)", lambda r, c: f'=IF(AND({s("masa_th", r)}="",{s("masa_bl", r)}=""),"",'
                                                f'ROUND(N({s("masa_th", r)})+N({s("masa_bl", r)})/12,2))'),
    ("e_tot", "Total jam E1–E8", lambda r, c: f"=IF(COUNT('1_Subjek'!{S['E1']}{r}:{S['E8']}{r})=0,\"\","
                                              f"SUM('1_Subjek'!{S['E1']}{r}:{S['E8']}{r}))"),
    ("e_cek", "Cek total E vs D4", lambda r, c: f'=IF(OR({c["e_tot"]}{r}="",{s("lama", r)}=""),"",'
                                                f'IF(ABS({c["e_tot"]}{r}-{s("lama", r)})>0.25,"Total E tidak sama D4",""))'),
    *[(f"p{z}", f"Proporsi {z}", (lambda zz: lambda r, c: f'=IF(OR({c["e_tot"]}{r}="",{c["e_tot"]}{r}=0),"",'
                                                       f'N({s(zz, r)})/{c["e_tot"]}{r})')(z))
      for z, *_ in ZONES],
    ("jam_panas", "Jam area panas (E1–E4)", lambda r, c: f"=IF({c['e_tot']}{r}=\"\",\"\","
                                                         f"SUM('1_Subjek'!{S['E1']}{r}:{S['E4']}{r}))"),
    ("jam_tidak", "Jam area tidak panas (E5–E8)", lambda r, c: f"=IF({c['e_tot']}{r}=\"\",\"\","
                                                               f"SUM('1_Subjek'!{S['E5']}{r}:{S['E8']}{r}))"),
    ("area_kat", "Area kerja", lambda r, c: f'=IF({c["e_tot"]}{r}="","",IF({c["jam_panas"]}{r}>6,"Panas",'
                                            f'IF({c["jam_tidak"]}{r}>6,"Tidak panas","Tidak memenuhi (>6 jam)")))'),
    ("area01", "Area (1=panas, 0=tidak)", lambda r, c: f'=IF({c["area_kat"]}{r}="Panas",1,'
                                                       f'IF({c["area_kat"]}{r}="Tidak panas",0,""))'),
    ("wbgt", "WBGT individual (°C)", None),
    ("pm25", "PM2.5 individual (µg/m³)", None),
    ("ib", "Indeks Brinkman", lambda r, c: f'=IF({s("g1", r)}="","",IF({s("g1", r)}="Tidak pernah",0,'
                                           f'N({s("g2", r)})*N({s("g3", r)})))'),
    ("rokok_kat", "Kategori rokok (0 bukan,1 IB<200,2 IB200–599,3 IB>=600)",
     lambda r, c: f'=IF({c["ib"]}{r}="","",IF({s("g1", r)}="Tidak pernah",0,IF({c["ib"]}{r}<200,1,'
                  f'IF({c["ib"]}{r}<600,2,3))))'),
    ("rokok_ak", "Perokok aktif (1/0)", lambda r, c: f'=IF({s("g1", r)}="","",IF({s("g1", r)}="Aktif",1,0))'),
    ("f_tot", "Total jam F1–F4", lambda r, c: f"=IF(COUNT('1_Subjek'!{S['F1']}{r}:{S['F4']}{r})=0,\"\","
                                              f"SUM('1_Subjek'!{S['F1']}{r}:{S['F4']}{r}))"),
    ("f_cek", "Cek total F vs D4", lambda r, c: f'=IF(OR({c["f_tot"]}{r}="",{s("lama", r)}=""),"",'
                                                f'IF(ABS({c["f_tot"]}{r}-{s("lama", r)})>0.25,"Total F tidak sama D4",""))'),
    ("bk_rerata", "Rerata beban kerja (kkal/jam)",
     lambda r, c: f'=IF(OR({c["f_tot"]}{r}="",{c["f_tot"]}{r}=0),"",('
                  + "+".join(f'{v}*N({s(f, r)})' for f, v in BK_NILAI.items())
                  + f')/{c["f_tot"]}{r}*60)'),
    ("bk_mb", "Metabolisme basal (kkal/jam)", lambda r, c: f'=IF(OR({s("bb", r)}="",{c["jk01"]}{r}=""),"",'
                                                           f'{s("bb", r)}*IF({c["jk01"]}{r}=1,1,0.9))'),
    ("bk_kkal", "Total beban kerja (kkal/jam)", lambda r, c: f'=IF(OR({c["bk_rerata"]}{r}="",{c["bk_mb"]}{r}=""),"",'
                                                             f'ROUND({c["bk_rerata"]}{r}+{c["bk_mb"]}{r},1))'),
    ("bk_kat", "Kategori beban kerja", lambda r, c: f'=IF({c["bk_kkal"]}{r}="","",IF({c["bk_kkal"]}{r}<=200,"Ringan",'
                                                    f'IF({c["bk_kkal"]}{r}<=350,"Sedang","Berat")))'),
    ("tewl", "TEWL rerata (g/m²/h)", lambda r, c: f"=IF(COUNT('1_Subjek'!{S['tewl1']}{r}:{S['tewl3']}{r})=0,\"\","
                                                  f"ROUND(AVERAGE('1_Subjek'!{S['tewl1']}{r}:{S['tewl3']}{r}),2))"),
    ("tewl_n", "Jumlah bacaan TEWL", lambda r, c: f"=COUNT('1_Subjek'!{S['tewl1']}{r}:{S['tewl3']}{r})"),
    ("aklim", "Aklimatisasi (menit)", lambda r, c: f'=IF(OR({s("j2", r)}="",{s("j3", r)}=""),"",'
                                                   f'ROUND(({s("j3", r)}-{s("j2", r)})*1440,0))'),
    ("selang", "Akhir shift → darah (menit)", lambda r, c: f'=IF(OR({s("j1", r)}="",{s("j6", r)}=""),"",'
                                                           f'ROUND(({s("j6", r)}-{s("j1", r)})*1440,0))'),
    ("h2o2", "H2O2 (mmol/L)", lambda r, c: f'=IF({c["kode"]}{r}="","",IFERROR(INDEX({LAB_VAL},'
                                           f'MATCH({c["kode"]}{r},{LAB_CODE},0)),""))'),
    ("hemolisis", "Hemolisis (lab)", lambda r, c: f'=IF({c["kode"]}{r}="","",IFERROR(INDEX({LAB_HEM},'
                                                  f'MATCH({c["kode"]}{r},{LAB_CODE},0))&"",""))'),
    ("peringatan", "Peringatan protokol", None),
    ("eksklusi", "Alasan eksklusi", None),
    ("analisis", "Dianalisis (1/0)", None),
    ("alasan", "Alasan tidak dianalisis", None),
]
K = {k: get_column_letter(i + 1) for i, (k, *_) in enumerate(CALCS)}


def wbgt_formula(r, mat, hdr):
    m = f"MATCH({K['shift']}{r},{hdr},0)"
    terms = "+".join(f"IF({K['p' + z]}{r}=0,0,{K['p' + z]}{r}*INDEX({mat},{i + 1},{m}))"
                     for i, (z, *_) in enumerate(ZONES))
    return f'=IF(OR({K["e_tot"]}{r}="",{K["e_tot"]}{r}=0),"",IFERROR(ROUND({terms},2),"data zona belum lengkap"))'


def yes(key, r):
    return f'{s(key, r)}="Ya"'


def num_out(col, r, lo, hi):
    return f"AND(ISNUMBER({col}{r}),OR({col}{r}<{lo},{col}{r}>{hi}))"


header(wsk, 1, [h for _, h, _ in CALCS], 12, height=60)
wsk.freeze_panes = "B2"
for r in range(FIRST, LAST + 1):
    for k, _, f in CALCS:
        cell = wsk[f"{K[k]}{r}"]
        if f:
            cell.value = f(r, K)
        cell.fill = CALC
    wsk[f"{K['wbgt']}{r}"] = wbgt_formula(r, MAT_W, MAT_W_HDR)
    wsk[f"{K['pm25']}{r}"] = wbgt_formula(r, MAT_P, MAT_P_HDR)
    wsk[f"{K['peringatan']}{r}"] = (
        f'=IF({K["kode"]}{r}="","",'
        f'IF({num_out(K["aklim"], r, 15, 600)},"aklimatisasi<15 mnt; ","")'
        f'&IF({num_out(K["selang"], r, 30, 60)},"selang darah di luar 30–60 mnt; ","")'
        f'&IF(AND(ISNUMBER({s("j4_suhu", r)}),OR({s("j4_suhu", r)}<18,{s("j4_suhu", r)}>22)),"suhu ruang di luar 18–22; ","")'
        f'&IF(AND(ISNUMBER({s("j4_rh", r)}),OR({s("j4_rh", r)}<40,{s("j4_rh", r)}>60)),"RH di luar 40–60%; ","")'
        f'&IF(AND({K["tewl_n"]}{r}>0,{K["tewl_n"]}{r}<3),"TEWL <3 bacaan; ","")'
        f'&{K["e_cek"]}{r}&IF({K["e_cek"]}{r}<>"","; ","")'
        f'&{K["f_cek"]}{r}&IF({K["f_cek"]}{r}<>"","; ",""))')
    wsk[f"{K['eksklusi']}{r}"] = (
        f'=IF({K["kode"]}{r}="","",'
        f'IF({num_out(K["usia"], r, 18, 55)},"usia di luar 18–55; ","")'
        f'&IF(AND(ISNUMBER({K["masa"]}{r}),{K["masa"]}{r}<0.25),"masa kerja <3 bulan; ","")'
        f'&IF({K["area_kat"]}{r}="Tidak memenuhi (>6 jam)","jam di area <=6; ","")'
        f'&IF({yes("h1", r)},"H1 penyakit; ","")&IF({yes("h2", r)},"H2 infeksi akut; ","")'
        f'&IF({yes("h3", r)},"H3 kelainan kulit lengan; ","")&IF({yes("h4", r)},"H4 suplemen antioksidan; ","")'
        f'&IF(AND(ISNUMBER({K["rokok_kat"]}{r}),{K["rokok_kat"]}{r}=3),"IB>=600 (perokok berat); ","")'
        f'&IF({yes("h6", r)},"H6 topikal 24 jam; ","")&IF({yes("h7", r)},"H7 air/sabun 2 jam; ","")'
        f'&IF({yes("g5", r)},"G5 merokok 3 jam; ",""))')
    wsk[f"{K['analisis']}{r}"] = (
        f'=IF({K["kode"]}{r}="","",IF(AND({s("partisipasi", r)}="Ikut",{K["eksklusi"]}{r}="",'
        f'OR({s("sampel", r)}="",{s("sampel", r)}="Layak"),{K["hemolisis"]}{r}<>"Ya",'
        f'ISNUMBER({K["wbgt"]}{r}),ISNUMBER({K["tewl"]}{r}),ISNUMBER({K["h2o2"]}{r})),1,0))')
    wsk[f"{K['alasan']}{r}"] = (
        f'=IF(OR({K["kode"]}{r}="",{K["analisis"]}{r}=1),"",'
        f'IF({s("partisipasi", r)}="","belum diisi",IF({s("partisipasi", r)}<>"Ikut",{s("partisipasi", r)},'
        f'IF({K["eksklusi"]}{r}<>"","eksklusi: "&{K["eksklusi"]}{r},'
        f'IF(AND({s("sampel", r)}<>"",{s("sampel", r)}<>"Layak"),{s("sampel", r)},'
        f'IF({K["hemolisis"]}{r}="Ya","Hemolisis (lab)","data belum lengkap"))))))')
for k in ("e_cek", "f_cek", "peringatan", "eksklusi", "alasan"):
    wsk.conditional_formatting.add(f"{K[k]}{FIRST}:{K[k]}{LAST}",
                                   FormulaRule(formula=[f'LEN({K[k]}{FIRST})>0'], font=RED))
for k in ("peringatan", "eksklusi", "alasan"):
    wsk.column_dimensions[K[k]].width = 34

# ---------------------------------------------------------------- 6_Ekspor_SPSS
EXP = [  # (spss name, label, source formula on 5_Hitung / 1_Subjek)
    ("kode", "Kode subjek", lambda r: f"'5_Hitung'!{K['kode']}{r}"),
    ("hari", "Hari (1-3)", lambda r: f"VALUE(MID({s('hari', r)},2,1))"),
    ("shift", "Shift (1 subuh, 2 pagi, 3 siang)", lambda r: f"MATCH({s('shift', r)},{{\"subuh\",\"pagi\",\"siang\"}},0)"),
    ("ikut", "Ikut pemeriksaan (1/0)", lambda r: f'IF({s("partisipasi", r)}="Ikut",1,0)'),
    ("analisis", "Dianalisis (1/0)", lambda r: f"'5_Hitung'!{K['analisis']}{r}"),
    ("area", "Area (1 panas, 0 tidak panas)", lambda r: f"'5_Hitung'!{K['area01']}{r}"),
    ("usia", "Usia (tahun)", lambda r: f"'5_Hitung'!{K['usia']}{r}"),
    ("jk", "Jenis kelamin (1 L, 0 P)", lambda r: f"'5_Hitung'!{K['jk01']}{r}"),
    ("imt", "IMT (kg/m2)", lambda r: f"'5_Hitung'!{K['imt']}{r}"),
    ("masakrj", "Masa kerja (tahun)", lambda r: f"'5_Hitung'!{K['masa']}{r}"),
    ("brinkman", "Indeks Brinkman", lambda r: f"'5_Hitung'!{K['ib']}{r}"),
    ("rokok", "Kategori rokok (0 bukan, 1 IB<200, 2 IB 200-599)", lambda r: f"'5_Hitung'!{K['rokok_kat']}{r}"),
    ("rokok_ak", "Perokok aktif (1/0)", lambda r: f"'5_Hitung'!{K['rokok_ak']}{r}"),
    ("bk_kkal", "Beban kerja total (kkal/jam)", lambda r: f"'5_Hitung'!{K['bk_kkal']}{r}"),
    ("bk_kat", "Beban kerja (1 ringan, 2 sedang, 3 berat)",
     lambda r: f"IFERROR(MATCH('5_Hitung'!{K['bk_kat']}{r},{{\"Ringan\",\"Sedang\",\"Berat\"}},0),\"\")"),
    ("bk_sdg", "Dummy beban kerja sedang", lambda r: f"IF('5_Hitung'!{K['bk_kat']}{r}=\"\",\"\",IF('5_Hitung'!{K['bk_kat']}{r}=\"Sedang\",1,0))"),
    ("bk_brt", "Dummy beban kerja berat", lambda r: f"IF('5_Hitung'!{K['bk_kat']}{r}=\"\",\"\",IF('5_Hitung'!{K['bk_kat']}{r}=\"Berat\",1,0))"),
    ("wbgt", "WBGT individual (C)", lambda r: f"IF(ISNUMBER('5_Hitung'!{K['wbgt']}{r}),'5_Hitung'!{K['wbgt']}{r},\"\")"),
    ("pm25", "PM2.5 individual (ug/m3, setara-optik)", lambda r: f"IF(ISNUMBER('5_Hitung'!{K['pm25']}{r}),'5_Hitung'!{K['pm25']}{r},\"\")"),
    ("tewl", "TEWL (g/m2/h)", lambda r: f"'5_Hitung'!{K['tewl']}{r}"),
    ("h2o2", "H2O2 plasma (mmol/L)", lambda r: f"IF(ISNUMBER('5_Hitung'!{K['h2o2']}{r}),'5_Hitung'!{K['h2o2']}{r},\"\")"),
    ("pelembap", "Pelembap lengan 1 minggu (1/0)", lambda r: f'IF({s("i1", r)}="Ya",1,IF({s("i1", r)}="Tidak",0,""))'),
    ("wetwork", "Kontak air/sabun >=2 jam (1/0)", lambda r: f'IF({s("i2", r)}="Ya",1,IF({s("i2", r)}="Tidak",0,""))'),
    ("selang", "Akhir shift ke darah (menit)", lambda r: f"'5_Hitung'!{K['selang']}{r}"),
]
X = {k: get_column_letter(i + 1) for i, (k, *_) in enumerate(EXP)}
wse = wb.create_sheet("6_Ekspor_SPSS")
header(wse, 1, [k for k, *_ in EXP], 10, height=20)
wse.freeze_panes = "B2"
for r in range(FIRST, LAST + 1):
    for k, _, f in EXP:
        wse[f"{X[k]}{r}"] = f"=IF('5_Hitung'!$A{r}=\"\",\"\",{f(r)})"
        wse[f"{X[k]}{r}"].fill = CALC

# ---------------------------------------------------------------- 7_Tabel1_SMD
wst = wb.create_sheet("7_Tabel1_SMD")
wsb = wb.create_sheet("_bantu")          # squares for SD (keeps every formula non-array)
CONT = ["usia", "imt", "masakrj", "brinkman", "bk_kkal", "wbgt", "pm25", "tewl", "h2o2"]
B = {}
for i, k in enumerate(CONT):
    col = get_column_letter(i + 1)
    B[k] = col
    wsb[f"{col}1"] = k + "^2"
    for r in range(FIRST, LAST + 1):
        wsb[f"{col}{r}"] = f"=IF(ISNUMBER('6_Ekspor_SPSS'!{X[k]}{r}),'6_Ekspor_SPSS'!{X[k]}{r}^2,\"\")"
wsb.sheet_state = "hidden"

E = lambda k: f"'6_Ekspor_SPSS'!${X[k]}${FIRST}:${X[k]}${LAST}"
Q = lambda k: f"'_bantu'!${B[k]}${FIRST}:${B[k]}${LAST}"


def block(top, title, g1, g2, cont, cats, labels):
    """g1/g2 = list of (column_key, value) criteria pairs for each group."""
    wst[f"A{top}"] = title
    wst[f"A{top}"].font = Font(bold=True, size=12)
    header(wst, top + 1, ["Variabel", f"n {labels[0]}", f"Rerata / % {labels[0]}", f"SD {labels[0]}",
                          f"n {labels[1]}", f"Rerata / % {labels[1]}", f"SD {labels[1]}", "SMD"],
           [34, 10, 14, 10, 10, 14, 10, 10], height=30)
    crit = lambda g: ",".join(f"{E(k)},{v}" for k, v in g)
    r = top + 2
    for k in cont:
        wst[f"A{r}"] = k
        for (n, m, sd), g in ((("B", "C", "D"), g1), (("E", "F", "G"), g2)):
            wst[f"{n}{r}"] = f"=SUMPRODUCT(--(" + ")*--(".join(
                f"{E(kk)}={v}" for kk, v in g) + f"),--ISNUMBER({E(k)}))"
            wst[f"{m}{r}"] = f'=IFERROR(ROUND(AVERAGEIFS({E(k)},{crit(g)}),2),"")'
            wst[f"{sd}{r}"] = (f'=IFERROR(ROUND(SQRT((SUMIFS({Q(k)},{crit(g)})-{n}{r}*AVERAGEIFS({E(k)},{crit(g)})^2)'
                               f'/({n}{r}-1)),2),"")')
        wst[f"H{r}"] = f'=IFERROR(ROUND(ABS(C{r}-F{r})/SQRT((D{r}^2+G{r}^2)/2),3),"")'
        r += 1
    for k, val, lab in cats:
        wst[f"A{r}"] = lab
        for (n, p), g in ((("B", "C"), g1), (("E", "F"), g2)):
            wst[f"{n}{r}"] = f"=COUNTIFS({crit(g)},{E(k)},{val})"
            denom = "SUMPRODUCT(--(" + ")*--(".join(f"{E(kk)}={v}" for kk, v in g) + f"),--ISNUMBER({E(k)}))"
            wst[f"{p}{r}"] = f'=IFERROR(ROUND({n}{r}/{denom}*100,1),"")'
        wst[f"H{r}"] = (f'=IFERROR(ROUND(ABS(C{r}/100-F{r}/100)/SQRT((C{r}/100*(1-C{r}/100)+'
                        f'F{r}/100*(1-F{r}/100))/2),3),"")')
        r += 1
    for row in wst[f"B{top + 2}:H{r - 1}"]:
        for c in row:
            c.fill = CALC
    wst.conditional_formatting.add(f"H{top + 2}:H{r - 1}",
                                   FormulaRule(formula=[f'AND(ISNUMBER(H{top + 2}),H{top + 2}>0.25)'], font=RED))
    return r + 2


CATS = [("jk", 1, "Laki-laki, %"), ("rokok", 0, "Bukan perokok, %"), ("rokok", 1, "Perokok ringan (IB<200), %"),
        ("rokok", 2, "Perokok sedang (IB 200–599), %"), ("bk_kat", 1, "Beban kerja ringan, %"),
        ("bk_kat", 2, "Beban kerja sedang, %"), ("bk_kat", 3, "Beban kerja berat, %"),
        ("pelembap", 1, "Pelembap lengan 1 minggu, %"), ("wetwork", 1, "Kontak air/sabun ≥2 jam, %")]
nxt = block(1, "Tabel 4.3 — karakteristik per area (hanya subjek dianalisis). SMD >0,25 = tidak seimbang (merah).",
            [("analisis", 1), ("area", 1)], [("analisis", 1), ("area", 0)],
            CONT, CATS, ("panas", "tidak panas"))
block(nxt, "Tabel 4.1 — atrisi: subjek yang ikut, dianalisis vs tidak dianalisis.",
      [("ikut", 1), ("analisis", 1)], [("ikut", 1), ("analisis", 0)],
      ["usia", "imt", "masakrj"], [("jk", 1, "Laki-laki, %"), ("area", 1, "Area panas, %")],
      ("dianalisis", "tidak dianalisis"))
wst["J1"] = ("Median (min–maks) untuk variabel tidak normal dan uji normalitas dihitung di SPSS. "
             "Jumlah n memakai SUMPRODUCT agar sel kosong tidak terhitung.")
wst["J1"].alignment = WRAP
wst.column_dimensions["J"].width = 40

# ---------------------------------------------------------------- Codebook
wcb = wb.create_sheet("Codebook", 0)
header(wcb, 1, ["Nama SPSS", "Label", "Jenis data", "Kode / satuan", "Sumber"], [12, 44, 12, 34, 36], height=20)
CB = {"kode": ("teks", "H1-01 … H3-25", "Kuesioner A1"), "hari": ("kategorik", "1 = 30 Nov, 2 = 1 Des, 3 = 2 Des", "1_Subjek"),
      "shift": ("kategorik", "1 subuh, 2 pagi, 3 siang", "1_Subjek"), "ikut": ("kategorik", "1 ikut, 0 tidak", "Status partisipasi"),
      "analisis": ("kategorik", "1 dianalisis, 0 tidak", "5_Hitung"), "area": ("kategorik", "1 panas (E1–E4 >6 jam), 0 tidak panas", "Kuesioner E"),
      "usia": ("numerik", "tahun", "B1 dan A2"), "jk": ("kategorik", "1 laki-laki, 0 perempuan", "B2"),
      "imt": ("numerik", "kg/m²", "C1, C2"), "masakrj": ("numerik", "tahun", "D1"),
      "brinkman": ("numerik", "batang/hari × tahun", "G2 × G3"),
      "rokok": ("kategorik", "0 bukan perokok, 1 IB<200, 2 IB 200–599 (IB≥600 dieksklusi)", "G1–G3"),
      "rokok_ak": ("kategorik", "1 perokok aktif, 0 tidak", "G1"),
      "bk_kkal": ("numerik", "kkal/jam, SNI 7269:2009 (kovariat kontinu)", "F1–F4, C1, B2 (Lampiran 4)"),
      "bk_kat": ("kategorik", "1 ringan ≤200, 2 sedang >200–350, 3 berat >350", "bk_kkal"),
      "bk_sdg": ("kategorik", "dummy (referensi ringan)", "bk_kat"), "bk_brt": ("kategorik", "dummy (referensi ringan)", "bk_kat"),
      "wbgt": ("numerik", "°C, Σ(WBGT zona × proporsi waktu)", "2_Lingkungan, E1–E8"),
      "pm25": ("numerik", "µg/m³ setara-optik, Σ(PM2.5 zona × proporsi)", "2_Lingkungan, E1–E8"),
      "tewl": ("numerik", "g/m²/h, rerata 3 bacaan", "J5"), "h2o2": ("numerik", "mmol/L", "4_Lab_H2O2"),
      "pelembap": ("kategorik", "1 ya, 0 tidak", "I1"), "wetwork": ("kategorik", "1 ya (≥2 jam), 0 tidak", "I2"),
      "selang": ("numerik", "menit", "J1, J6")}
for i, (k, lab, _) in enumerate(EXP, 2):
    jenis, kode, src = CB[k]
    for c, v in enumerate((k, lab, jenis, kode, src), 1):
        wcb.cell(row=i, column=c, value=v).border = THIN

# ---------------------------------------------------------------- Petunjuk
wp = wb.create_sheet("Petunjuk", 0)
wp.column_dimensions["A"].width = 110
TEXT = [
    ("Data Mentah Tesis WBGT–TEWL–H2O2 (Instalasi Gizi RSCM, 30 Nov – 2 Des 2026)", True),
    ("Warna sel: krem = diisi manual; abu-abu = rumus, jangan diketik.", False),
    ("", False),
    ("Urutan kerja", True),
    ("1. 1_Subjek: entri lembar data petugas + kuesioner per subjek. Kode H1-01 … H3-25 sudah terisi; baris 87–101 cadangan.", False),
    ("   Ya/Tidak, L/P, shift, dan status dipilih dari daftar. Jam ditulis hh:mm, tanggal dd/mm/yyyy.", False),
    ("2. 1b_Entri_Ulang: orang kedua mengetik ulang kolom kunci tanpa melihat entri pertama. Cek_Entri menghitung sel BEDA.", False),
    ("3. 2_Lingkungan: WBGT dan PM2.5 per shift × putaran × zona (3 bacaan). Kolom Tren memberi tanda bila bacaan masih naik/turun.", False),
    ("4. 4_Lab_H2O2: kurva standar + absorbans sampel, ATAU kadar akhir dari lab di kolom H.", False),
    ("5. 5_Hitung (rumus): usia, IMT, proporsi zona, WBGT/PM2.5 individual, Indeks Brinkman, beban kerja SNI 7269, TEWL, ", False),
    ("   H2O2, peringatan protokol, alasan eksklusi, dan status dianalisis. Baca kolom merah sebelum analisis.", False),
    ("6. 7_Tabel1_SMD: Tabel 4.3 (keseimbangan per area) dan Tabel 4.1 (atrisi) terhitung otomatis.", False),
    ("", False),
    ("Ke SPSS", True),
    ("Salin seluruh 6_Ekspor_SPSS → workbook baru → Paste Special › Values → simpan sebagai CSV → SPSS: File › Import Data › CSV.", False),
    ("Jangan impor sheet berumus langsung: sel kosong hasil rumus terbaca sebagai teks dan kolom bisa berubah menjadi string.", False),
    ("Di SPSS jalankan analisis dengan filter analisis = 1; atrisi memakai ikut = 1.", False),
    ("", False),
    ("Aturan yang dipakai", True),
    ("Eksklusi perokok berat: Indeks Brinkman ≥600 (G2 × G3). Butir H5 (>20 batang/hari) tidak dipakai sebagai kriteria.", False),
    ("Area: >6 jam di E1–E4 = panas; >6 jam di E5–E8 = tidak panas; selain itu tidak memenuhi kriteria inklusi.", False),
    ("Beban kerja: [Σ(nilai × jam) ÷ Σ jam] × 60 + MB (BB × 1 laki-laki, × 0,9 perempuan); nilai F1 1,00 · F2 1,30 · F3 3,30 · F4 5,25.", False),
    ("Kovariat beban kerja di model: bk_kkal (kontinu). Kolom dummy bk_sdg/bk_brt tetap ada bila diperlukan.", False),
    ("Peringatan (bukan eksklusi): aklimatisasi <15 menit, selang darah di luar 30–60 menit, ruang ukur di luar 18–22 °C / 40–60%.", False),
    ("Data hilang dibiarkan kosong, jangan diisi 0. Data mentah tidak diubah; koreksi dicatat di kolom catatan.", False),
    ("Data subjek bersifat rahasia: simpan hanya di OneDrive, jangan diunggah ke repo GitHub.", False),
]
for i, (t, bold) in enumerate(TEXT, 1):
    wp[f"A{i}"] = t
    wp[f"A{i}"].font = Font(bold=bold, size=13 if i == 1 else 11)
wb.active = 0


# ---------------------------------------------------------------- output
def fill_test():
    """Three test subjects whose results can be checked by hand (Lampiran 4 worked examples)."""
    rows = {2: dict(partisipasi="Ikut", lahir=date(1990, 5, 1), jk="L", bb=65, tb=170, masa_th=5, masa_bl=6,
                    lama=8, E1=6, E4=2, F1=2, F3=4, F4=2, g1="Aktif", g2=12, g3=10, g5="Tidak",
                    j1=time(12, 0), j2=time(12, 5), j3=time(12, 30), j4_suhu=21, j4_rh=50,
                    tewl1=10, tewl2=11, tewl3=12, j6=time(12, 45), sampel="Layak"),
            3: dict(partisipasi="Ikut", lahir=date(1980, 1, 15), jk="L", bb=70, tb=165, masa_th=10, masa_bl=0,
                    lama=8, E2=7, E5=1, F1=1, F3=3, F4=4, g1="Aktif", g2=20, g3=30, g5="Tidak",
                    j1=time(12, 0), j2=time(12, 10), j3=time(12, 20), tewl1=15, tewl2=15, tewl3=15,
                    j6=time(13, 30), sampel="Layak"),
            4: dict(partisipasi="Ikut", lahir=date(1995, 12, 31), jk="P", bb=60, tb=155, masa_th=0, masa_bl=6,
                    lama=8, E8=8, F1=7, F2=1, g1="Tidak pernah", g5="Tidak", j1=time(12, 0),
                    j2=time(12, 0), j3=time(12, 20), tewl1=8, tewl2=9, tewl3=10, j6=time(12, 40), sampel="Layak")}
    for h in range(1, 8):
        for r in rows:
            rows[r][f"h{h}"] = "Tidak"
    for r, vals in rows.items():
        for k, v in vals.items():
            ws1[f"{S[k]}{r}"] = v
    for rr in LROWS:          # WBGT reading = 30 - zone index (+0.1, +0.2 except E3), PM = 100 + 10*index
        zi = int(wsl[f"D{rr}"].value[1])
        base = 30 - zi + (1 if wsl[f"A{rr}"].value == "siang" else 0)
        wsl[f"H{rr}"], wsl[f"I{rr}"], wsl[f"J{rr}"] = (base, base, base) if zi == 3 else (base, base + .1, base + .2)
        wsl[f"N{rr}"] = wsl[f"O{rr}"] = wsl[f"P{rr}"] = 100 + 10 * zi
        wsl[f"K{rr}"], wsl[f"L{rr}"] = 32, 60
    wsh["B4"] = 0
    for i, c in enumerate((0, 0.5, 1, 2, 4)):
        wsh[f"A{11 + i}"], wsh[f"B{11 + i}"], wsh[f"C{11 + i}"] = c, 0.05 + 0.1 * c, 0.05 + 0.1 * c
    wsh["A21"], wsh["C21"], wsh["D21"] = "H1-01", 0.35, 0.35
    wsh["A22"], wsh["C22"] = "H1-02", 0.25
    wsh["A23"], wsh["H23"] = "H1-03", 1.5


if len(sys.argv) > 2 and sys.argv[1] == "--test":
    fill_test()
    out = Path(sys.argv[2]) / f"TEST_{FILE_NAME}"
else:
    out = OUT_DIR / FILE_NAME
if out.exists():
    sys.exit(f"{out} sudah ada; tidak ditimpa. Hapus/rename dulu bila memang ingin membuat ulang.")
out.parent.mkdir(parents=True, exist_ok=True)
wb.save(out)
print("saved", out)
