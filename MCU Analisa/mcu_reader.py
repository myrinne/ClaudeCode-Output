"""MCU column reader + mapping (step 1 of the MCU Data Analyst pipeline).

Reads a vendor MCU Excel (any layout), finds the main worker sheet and its
header row, matches every vendor column to a standard variable BY HEADER NAME
(never by column letter), and writes a NEW workbook next to the input:

    <input folder>/Analisa/<file name> - Analisa.xlsx
        RAW           exact value copy of the vendor's main sheet (same row/column letters)
        MAP           standard variable -> vendor column, status OK / CEK / TIDAK ADA,
                      fill counts as Excel formulas, and a 'Koreksi' column for her
        GRUP          candidate grouping columns (Departemen/Bagian/...) with
                      case-sensitive counts per value (EXACT formulas, no cleaning)
        KOLOM_VENDOR  every vendor column and what it was mapped to
        SHEET_LAIN    the vendor's other sheets (inventory only)

The vendor file is never modified. Re-running keeps the corrections she typed
in MAP's 'Koreksi' column (a column letter forces that column, X = not available).

Usage:
    uv run --with openpyxl python mcu_reader.py "<vendor.xlsx>" [--sheet NAME] [--cek]

--cek recalculates the output with LibreOffice (headless) and compares every
formula result with an independent Python count. It must report 0 differences.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
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
from openpyxl.utils import get_column_letter as col_letter

HERE = Path(__file__).resolve().parent
VAR_FILE = HERE / "variabel_standar.json"
SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")

FILL = {
    "OK": PatternFill("solid", fgColor="C6EFCE"),
    "CEK": PatternFill("solid", fgColor="FFEB9C"),
    "TIDAK ADA": PatternFill("solid", fgColor="D9D9D9"),
    "KOREKSI": PatternFill("solid", fgColor="BDD7EE"),
    "HEAD": PatternFill("solid", fgColor="1F4E78"),
}
BOLD = Font(bold=True)
HEAD_FONT = Font(bold=True, color="FFFFFF")


# ---------------------------------------------------------------- normalising
def norm(text) -> str:
    """lowercase, non-alphanumerics -> space, collapse spaces."""
    if text is None:
        return ""
    s = str(text).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_base(text) -> str:
    """norm() after dropping anything in parentheses (units, sides, notes)."""
    if text is None:
        return ""
    return norm(re.sub(r"\([^)]*\)?", " ", str(text)))


def is_blank(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")


# ---------------------------------------------------------------- reading
def find_header(ws_rows, keys: set[str], scan: int = 15):
    """Return (header_row_index0, score) for the row with most identity headers."""
    best = (None, 0)
    for i, row in enumerate(ws_rows[:scan]):
        score = sum(1 for v in row if norm(v) in keys or norm_base(v) in keys)
        if score > best[1]:
            best = (i, score)
    return best


def load_vendor(path: Path, sheet_name: str | None, keys: set[str]):
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except PermissionError:
        # file is open in Excel: try reading a temporary copy instead
        tmp = Path(tempfile.gettempdir()) / f"mcu_reader_{path.name}"
        try:
            shutil.copy2(path, tmp)
        except PermissionError:
            sys.exit(f"'{path.name}' sedang terbuka di Excel dan terkunci. Tutup file itu dulu, lalu jalankan ulang.")
        print(f"  (catatan: '{path.name}' sedang terbuka di Excel; dibaca dari salinan sementara)")
        wb = openpyxl.load_workbook(tmp, read_only=True, data_only=True)
    sheets = []
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        width = max((len(r) for r in rows), default=0)
        rows = [r + [None] * (width - len(r)) for r in rows]
        h, score = find_header(rows, keys)
        sheets.append({"name": ws.title, "rows": rows, "header": h, "score": score,
                       "nrows": len(rows), "ncols": width})
    wb.close()
    if sheet_name:
        main = next((s for s in sheets if s["name"].strip() == sheet_name.strip()), None)
        if main is None:
            sys.exit(f"Sheet '{sheet_name}' tidak ada. Sheet tersedia: {[s['name'] for s in sheets]}")
    else:
        good = [s for s in sheets if s["score"] >= 3]
        if not good:
            sys.exit("Tidak ketemu sheet dengan header identitas (Nama, No MCU, Jenis Kelamin...). Pakai --sheet.")
        main = max(good, key=lambda s: (s["nrows"], s["score"]))
    if main["header"] is None:
        sys.exit(f"Header di sheet '{main['name']}' tidak ketemu.")
    return main, sheets


def build_columns(main):
    """List of dicts: idx, letter, header, section (forward-filled from row above)."""
    h = main["header"]
    hdr = main["rows"][h]
    above = main["rows"][h - 1] if h > 0 else [None] * len(hdr)
    filled = sum(1 for v in above if not is_blank(v))
    use_sections = 0 < filled <= max(3, int(0.3 * len(hdr)))
    cols, sec = [], ""
    for j, v in enumerate(hdr):
        if use_sections and not is_blank(above[j]):
            sec = str(above[j]).strip()
        if is_blank(v) and not (use_sections and not is_blank(above[j])):
            if all(is_blank(r[j]) for r in main["rows"][h + 1:]):
                continue  # fully empty spacer column
        cols.append({"idx": j, "letter": col_letter(j + 1), "header": "" if v is None else str(v).strip(),
                     "section": sec, "n": norm(v), "b": norm_base(v)})
    return cols, use_sections


def data_range(main, name_idx: int | None):
    """First/last data row (1-based Excel rows) after the header."""
    h = main["header"]
    rows = main["rows"]
    first = h + 2
    last = first - 1
    for i in range(h + 1, len(rows)):
        r = rows[i]
        key_cells = [r[name_idx]] if name_idx is not None else r[:5]
        if any(not is_blank(v) for v in key_cells):
            last = i + 1
    return first, last


# ---------------------------------------------------------------- matching
def match_variables(variables, cols, use_sections, overrides):
    by_letter = {c["letter"]: c for c in cols}
    used: dict[str, str] = {}
    results = OrderedDict()

    for var in variables:
        key = var["key"]
        aliases = [norm(a) for a in var["alias"]]
        nth = var.get("ke")
        hint = norm(var.get("seksi", ""))

        if key in overrides:
            o = overrides[key]
            if o == "X":
                results[key] = {"var": var, "col": None, "status": "TIDAK ADA", "how": "dikoreksi: tidak ada"}
            elif o in by_letter:
                results[key] = {"var": var, "col": by_letter[o], "status": "OK", "how": "dikoreksi manual"}
                used.setdefault(o, key)
            else:
                results[key] = {"var": var, "col": None, "status": "CEK",
                                "how": f"koreksi '{o}' bukan kolom yang ada"}
            continue

        def pool(with_hint: bool):
            if with_hint and hint and use_sections:
                return [c for c in cols if hint in norm(c["section"])]
            return cols

        found, how, notes = [], "", []
        for with_hint in ([True, False] if hint and use_sections else [False]):
            cand = pool(with_hint)
            passes = [
                ("nama header sama persis", lambda c: c["n"] in aliases),
                ("nama header sama (tanpa isi kurung)", lambda c: c["b"] in aliases),
                ("nama header mengandung alias",
                 lambda c: c["letter"] not in used and any(len(a) >= 4 and re.search(rf"\b{re.escape(a)}\b", c["b"]) for a in aliases)),
                ("nama header mirip",
                 lambda c: c["letter"] not in used and c["b"] and max(difflib.SequenceMatcher(None, c["b"], a).ratio() for a in aliases) >= 0.88),
            ]
            if hint and use_sections and not with_hint:
                passes = passes[:2]  # outside its own section only an exact header name may match
            for label, test in passes:
                found = [c for c in cand if test(c)]
                if found:
                    how = label
                    break
            if found:
                if hint and use_sections and not with_hint:
                    notes.append(f"tidak ada di seksi '{var.get('seksi')}', diambil dari seksi lain")
                break

        if not found:
            results[key] = {"var": var, "col": None, "status": "TIDAK ADA", "how": "tidak ada header yang cocok"}
            continue

        status = "OK" if how.startswith("nama header sama") else "CEK"
        if nth:
            if len(found) < nth:
                results[key] = {"var": var, "col": None, "status": "TIDAK ADA",
                                "how": f"header '{found[0]['header']}' hanya {len(found)}x, butuh ke-{nth}"}
                continue
            pick = found[nth - 1]
            if len(found) > 1:
                if var.get("urutan_dikonfirmasi"):
                    how = f"{how}; header '{pick['header']}' muncul {len(found)}x, urutan ke-{nth} (dikonfirmasi: {var['urutan_dikonfirmasi']})"
                else:
                    status = "CEK"
                    notes.append(f"header '{pick['header']}' muncul {len(found)}x; diambil urutan ke-{nth}")
        else:
            pick = found[0]
            if len(found) > 1:
                status = "CEK"
                notes.append("cocok juga: " + ", ".join(f"{c['letter']} '{c['header']}'" for c in found[1:4]))
        if notes:
            status = "CEK"
        if pick["letter"] in used:
            status = "CEK"
            notes.append(f"kolom ini juga dipakai '{used[pick['letter']]}'")
        used.setdefault(pick["letter"], key)
        results[key] = {"var": var, "col": pick, "status": status, "how": "; ".join([how] + notes)}
    return results, used


def read_overrides(out_path: Path) -> dict[str, str]:
    if not out_path.exists():
        return {}
    try:
        wb = openpyxl.load_workbook(out_path, read_only=True)
        if "MAP" not in wb.sheetnames:
            return {}
        rows = list(wb["MAP"].iter_rows(values_only=True))
        wb.close()
    except Exception as e:  # unreadable previous output: start fresh
        print(f"  (catatan: koreksi lama tidak terbaca: {e})")
        return {}
    hdr_i = next((i for i, r in enumerate(rows) if r and r[0] == "Kode variabel"), None)
    if hdr_i is None:
        return {}
    hdr = list(rows[hdr_i])
    k_i = hdr.index("Kode variabel")
    c_i = hdr.index("Koreksi (huruf kolom / X)")
    out = {}
    for r in rows[hdr_i + 1:]:
        if r and r[k_i] and not is_blank(r[c_i]):
            out[str(r[k_i])] = str(r[c_i]).strip().upper()
    return out


# ---------------------------------------------------------------- writing
def rng(letter, first, last):
    return f"RAW!${letter}${first}:${letter}${last}"


def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[col_letter(i)].width = w


def head_row(ws, row, values):
    for j, v in enumerate(values, 1):
        c = ws.cell(row=row, column=j, value=v)
        c.font = HEAD_FONT
        c.fill = FILL["HEAD"]
        c.alignment = Alignment(wrap_text=True, vertical="center")


def xl_text(v) -> str:
    """Value as an Excel string literal for a formula."""
    return '"' + str(v).replace('"', '""') + '"'


def write_workbook(out_path, src_path, main, sheets, cols, use_sections, results, used,
                   first, last, overrides, expected, same_keys=()):
    wb = openpyxl.Workbook()
    raw = wb.active
    raw.title = "RAW"
    for r in main["rows"]:
        raw.append([v for v in r])
    raw.freeze_panes = raw.cell(row=main["header"] + 2, column=6)
    for c in raw[main["header"] + 1]:
        c.font = BOLD
    n_rows = last - first + 1
    name_col = results["nama"]["col"]["letter"] if results.get("nama", {}).get("col") else "A"

    # ---------------- MAP
    m = wb.create_sheet("MAP", 0)
    info = [
        ("File vendor", str(src_path)),
        ("Sheet utama", main["name"]),
        ("Baris header", main["header"] + 1),
        ("Baris data", f"{first} s/d {last}"),
        ("Jumlah pekerja (rumus)", f"=COUNTA({rng(name_col, first, last)})"),
        ("Seksi vendor terbaca", "ya (baris di atas header)" if use_sections else "tidak ada"),
        ("Cara baca", "Status OK = nama header cocok persis. CEK = perlu dicek (header berulang, mirip, atau dipakai 2 variabel). "
                      "TIDAK ADA = vendor tidak punya kolom ini. Untuk koreksi: isi kolom 'Koreksi' dengan huruf kolom RAW "
                      "(mis. KD) atau X bila tidak ada, simpan, lalu jalankan ulang skrip."),
    ]
    for i, (k, v) in enumerate(info, 1):
        m.cell(row=i, column=1, value=k).font = BOLD
        m.cell(row=i, column=2, value=v)
    m.cell(row=7, column=2).alignment = Alignment(wrap_text=True)
    m.merge_cells(start_row=7, start_column=2, end_row=7, end_column=11)
    m.row_dimensions[7].height = 45
    expected[("MAP", 5, 2)] = n_rows_named(main, results, first, last)

    hr = 9
    head_row(m, hr, ["Grup", "Kode variabel", "Variabel standar", "Kolom RAW", "Seksi vendor", "Header vendor",
                     "Status", "Cara cocok / catatan", "Terisi (bukan kosong/'-')", "Isi berupa angka",
                     "Contoh isi (baris data pertama yang terisi)", "Koreksi (huruf kolom / X)"])
    r = hr + 1
    for key, res in results.items():
        var, c = res["var"], res["col"]
        m.cell(row=r, column=1, value=var["grup"])
        m.cell(row=r, column=2, value=key)
        m.cell(row=r, column=3, value=var["label"])
        st = m.cell(row=r, column=7, value=res["status"])
        st.fill = FILL[res["status"]]
        m.cell(row=r, column=8, value=res["how"])
        if c:
            L = c["letter"]
            m.cell(row=r, column=4, value=L)
            m.cell(row=r, column=5, value=c["section"])
            m.cell(row=r, column=6, value=c["header"])
            R = rng(L, first, last)
            m.cell(row=r, column=9, value=f'=ROWS({R})-COUNTBLANK({R})-COUNTIF({R},"-")')
            m.cell(row=r, column=10, value=f"=COUNT({R})")
            ex_row = next((i for i in range(first, last + 1) if not is_blank(main["rows"][i - 1][c["idx"]])
                           and str(main["rows"][i - 1][c["idx"]]).strip() != "-"), None)
            if ex_row:
                m.cell(row=r, column=11, value=f"=RAW!{L}{ex_row}")
            vals = [main["rows"][i - 1][c["idx"]] for i in range(first, last + 1)]
            expected[("MAP", r, 9)] = sum(1 for v in vals if not is_blank(v) and str(v).strip() != "-")
            # COUNT also counts Excel dates (e.g. visus "6/6" that Excel turned into 6 June)
            expected[("MAP", r, 10)] = sum(1 for v in vals if isinstance(v, (int, float, dt.date)) and not isinstance(v, bool))
        if key in overrides:
            m.cell(row=r, column=12, value=overrides[key]).fill = FILL["KOREKSI"]
        r += 1
    m.freeze_panes = m.cell(row=hr + 1, column=4)
    m.auto_filter.ref = f"A{hr}:L{r - 1}"
    set_widths(m, [22, 18, 34, 9, 22, 38, 11, 48, 12, 11, 34, 14])

    # ---------------- GRUP
    g = wb.create_sheet("GRUP", 1)
    g.cell(row=1, column=1, value="Kandidat kolom pengelompokan (divisi / bagian / cabang). Kolom bertanda 'disamakan' dihitung "
                                  "dengan huruf besar/kecil dan spasi disamakan (UPPER+TRIM); kolom lain dihitung persis apa adanya (EXACT). "
                                  "RAW tidak diubah.").font = BOLD
    g.cell(row=2, column=1, value="Pilih satu kolom untuk tabel per divisi, lalu tulis kodenya di sel B3.")
    g.cell(row=3, column=1, value="Kolom grup terpilih:").font = BOLD
    gcol = 1
    cand_keys = [k for k in ("departemen", "bagian", "jabatan", "lokasi") if results.get(k, {}).get("col")]
    suggestion = suggest_group(main, results, cand_keys, first, last)
    g.cell(row=3, column=2, value=suggestion or "").fill = FILL["CEK"]
    g.cell(row=3, column=3, value="(saran skrip: jumlah nilai berbeda 3-15 dan paling sedikit kosong/'-'; mohon konfirmasi)")
    top = 5
    for key in cand_keys:
        c = results[key]["col"]
        L = c["letter"]
        R = rng(L, first, last)
        vals = [main["rows"][i - 1][c["idx"]] for i in range(first, last + 1)]
        same = key in same_keys
        VL = col_letter(gcol)
        if same:
            # same rule as Excel: TRIM (spaces only) + UPPER
            def gkey(v):
                return "" if v is None else re.sub(" +", " ", str(v).strip(" ")).upper()
            cnt = Counter(gkey(v) for v in vals)
            variants: dict[str, Counter] = {}
            for v in vals:
                if gkey(v):
                    variants.setdefault(gkey(v), Counter())[re.sub(" +", " ", str(v).strip(" "))] += 1
            uniq = sorted((k for k in cnt if k != ""), key=lambda k: (-cnt[k], k))
            shown = {k: variants[k].most_common(1)[0][0] for k in uniq}
            title = f"{key}: '{c['header']}' (kolom {L}) - disamakan"
            heads = ["Nilai (ejaan terbanyak)", "Jumlah pekerja (rumus)", "Varian di data vendor"]
        else:
            cnt = Counter("" if v is None or v == "" else str(v) for v in vals)
            uniq = sorted((v for v in cnt if v != ""), key=lambda v: (-cnt[v], v))
            shown = {v: v for v in uniq}
            title = f"{key}: '{c['header']}' (kolom {L}) - persis"
            heads = ["Nilai (apa adanya)", "Jumlah pekerja (rumus)"]
        g.cell(row=top, column=gcol, value=title).font = BOLD
        for j, h in enumerate(heads):
            cc = g.cell(row=top + 1, column=gcol + j, value=h)
            cc.font = HEAD_FONT
            cc.fill = FILL["HEAD"]
        rr = top + 2
        for v in uniq:
            g.cell(row=rr, column=gcol, value=shown[v])
            if same:
                g.cell(row=rr, column=gcol + 1, value=f"=SUMPRODUCT(--(UPPER(TRIM({R}))=UPPER(TRIM({VL}{rr}))))")
                g.cell(row=rr, column=gcol + 2, value=" | ".join(f"{s} ({n})" for s, n in variants[v].most_common()))
            else:
                g.cell(row=rr, column=gcol + 1, value=f"=SUMPRODUCT(--EXACT({R},{VL}{rr}))")
            expected[("GRUP", rr, gcol + 1)] = cnt[v]
            rr += 1
        g.cell(row=rr, column=gcol, value="(kosong)")
        g.cell(row=rr, column=gcol + 1,
               value=f'=SUMPRODUCT(--(TRIM({R})=""))' if same else f"=COUNTBLANK({R})")
        expected[("GRUP", rr, gcol + 1)] = cnt.get("", 0)
        rr += 1
        g.cell(row=rr, column=gcol, value="Total").font = BOLD
        tot = g.cell(row=rr, column=gcol + 1, value=f"=SUM({col_letter(gcol + 1)}{top + 2}:{col_letter(gcol + 1)}{rr - 1})")
        tot.font = BOLD
        expected[("GRUP", rr, gcol + 1)] = n_rows
        g.cell(row=rr + 1, column=gcol, value="Jumlah nilai berbeda")
        g.cell(row=rr + 1, column=gcol + 1, value=f"=COUNTA({col_letter(gcol)}{top + 2}:{col_letter(gcol)}{rr - 2})")
        expected[("GRUP", rr + 1, gcol + 1)] = len(uniq)
        g.cell(row=rr + 2, column=gcol, value="Cek total = jumlah pekerja")
        g.cell(row=rr + 2, column=gcol + 1,
               value=f'=IF({col_letter(gcol + 1)}{rr}=MAP!$B$5,"OK","TIDAK SAMA")')
        expected[("GRUP", rr + 2, gcol + 1)] = "OK"
        g.column_dimensions[col_letter(gcol)].width = 34
        g.column_dimensions[col_letter(gcol + 1)].width = 14
        if same:
            g.column_dimensions[col_letter(gcol + 2)].width = 40
        g.column_dimensions[col_letter(gcol + len(heads))].width = 3
        gcol += len(heads) + 1
    g.freeze_panes = "A5"

    # ---------------- KOLOM_VENDOR
    kv = wb.create_sheet("KOLOM_VENDOR", 2)
    head_row(kv, 1, ["Kolom RAW", "Seksi vendor", "Header vendor", "Dipetakan ke", "Terisi (bukan kosong/'-')", "Isi berupa angka"])
    mapped = {}
    for key, res in results.items():
        if res["col"]:
            mapped.setdefault(res["col"]["letter"], []).append(key)
    for i, c in enumerate(cols, 2):
        R = rng(c["letter"], first, last)
        kv.append([c["letter"], c["section"], c["header"], ", ".join(mapped.get(c["letter"], [])),
                   f'=ROWS({R})-COUNTBLANK({R})-COUNTIF({R},"-")', f"=COUNT({R})"])
        if c["letter"] not in mapped:
            kv.cell(row=i, column=4).fill = FILL["TIDAK ADA"]
    kv.freeze_panes = "A2"
    kv.auto_filter.ref = f"A1:F{len(cols) + 1}"
    set_widths(kv, [10, 26, 44, 26, 12, 11])

    # ---------------- SHEET_LAIN
    sl = wb.create_sheet("SHEET_LAIN", 3)
    head_row(sl, 1, ["Sheet vendor", "Baris (dibaca skrip)", "Kolom (dibaca skrip)", "Baris header terdeteksi", "Peran"])
    for s in sheets:
        sl.append([s["name"], s["nrows"], s["ncols"], (s["header"] + 1) if s["header"] is not None and s["score"] >= 3 else "-",
                   "SHEET UTAMA (disalin ke RAW)" if s is main else "lampiran vendor (belum dipakai)"])
    set_widths(sl, [26, 18, 18, 22, 34])

    wb.active = 0
    tmp = out_path.with_suffix(".tmp.xlsx")
    wb.save(tmp)
    try:
        tmp.replace(out_path)
    except PermissionError:
        tmp.unlink(missing_ok=True)
        sys.exit(f"Tidak bisa menyimpan: '{out_path.name}' sedang terbuka di Excel. Tutup dulu lalu jalankan ulang.")


def n_rows_named(main, results, first, last):
    c = results.get("nama", {}).get("col")
    idx = c["idx"] if c else 0
    return sum(1 for i in range(first, last + 1) if not is_blank(main["rows"][i - 1][idx]))


def suggest_group(main, results, keys, first, last):
    scored = []
    for key in keys:
        c = results[key]["col"]
        vals = [main["rows"][i - 1][c["idx"]] for i in range(first, last + 1)]
        empty = sum(1 for v in vals if is_blank(v) or str(v).strip() == "-")
        distinct = len({str(v).strip().lower() for v in vals if not (is_blank(v) or str(v).strip() == "-")})
        if 3 <= distinct <= 15 and empty < 0.2 * len(vals):
            scored.append((empty, distinct, key))
    return min(scored)[2] if scored else None


# ---------------------------------------------------------------- check
def recalc_and_check(out_path: Path, expected: dict) -> int:
    if not SOFFICE.exists():
        print("  --cek: LibreOffice tidak ditemukan, pengecekan dilewati.")
        return -1
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "in.xlsx"
        shutil.copy(out_path, src)
        outdir = Path(td) / "out"
        outdir.mkdir()
        subprocess.run([str(SOFFICE), "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(outdir), str(src)],
                       check=True, capture_output=True, timeout=300)
        wb = openpyxl.load_workbook(outdir / "in.xlsx", data_only=True, read_only=True)
        sheets = {name: list(wb[name].iter_rows(values_only=True)) for name in ("MAP", "GRUP")}
        wb.close()
    diffs = []
    for (sh, r, c), want in expected.items():
        got = sheets[sh][r - 1][c - 1]
        if isinstance(want, (int, float)) and isinstance(got, (int, float)):
            ok = abs(got - want) < 1e-9
        else:
            ok = got == want
        if not ok:
            diffs.append((sh, f"{col_letter(c)}{r}", want, got))
    print(f"  --cek: {len(expected)} sel rumus dibandingkan dengan hitungan Python, beda = {len(diffs)}")
    for d in diffs[:20]:
        print("    BEDA", d)
    return len(diffs)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("excel", type=Path)
    ap.add_argument("--sheet", help="nama sheet utama (bila deteksi otomatis salah)")
    ap.add_argument("--cek", action="store_true", help="hitung ulang dengan LibreOffice dan bandingkan")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    spec = json.loads(VAR_FILE.read_text(encoding="utf-8"))
    keys = {norm(k) for k in spec["identitas_kunci"]}
    src = args.excel.resolve()
    out_dir = src.parent / "Analisa"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{src.stem.strip()} - Analisa.xlsx"

    main_sheet, sheets = load_vendor(src, args.sheet, keys)
    cols, use_sections = build_columns(main_sheet)
    overrides = read_overrides(out_path)
    results, used = match_variables(spec["variabel"], cols, use_sections, overrides)
    name_idx = results["nama"]["col"]["idx"] if results.get("nama", {}).get("col") else None
    first, last = data_range(main_sheet, name_idx)
    expected = {}
    write_workbook(out_path, src, main_sheet, sheets, cols, use_sections, results, used,
                   first, last, overrides, expected, set(spec.get("grup_disamakan", [])))

    st = Counter(r["status"] for r in results.values())
    print(f"File   : {src.name}")
    print(f"Sheet  : {main_sheet['name']} (header baris {main_sheet['header'] + 1}, data baris {first}-{last}, "
          f"{n_rows_named(main_sheet, results, first, last)} pekerja)")
    print(f"Kolom  : {len(cols)} kolom vendor, {len({r['col']['letter'] for r in results.values() if r['col']})} terpetakan")
    print(f"Status : OK {st['OK']} | CEK {st['CEK']} | TIDAK ADA {st['TIDAK ADA']}"
          + (f" | koreksi dipakai {len(overrides)}" if overrides else ""))
    for k, r in results.items():
        if r["status"] == "CEK":
            print(f"   CEK  {k:<18} -> {r['col']['letter'] if r['col'] else '-':<4} {r['how']}")
    print(f"Hasil  : {out_path}")
    if args.cek:
        if recalc_and_check(out_path, expected) > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
