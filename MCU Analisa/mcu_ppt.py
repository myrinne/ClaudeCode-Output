"""MCU report PPT builder (step 3 of the MCU Data Analyst pipeline).

Fills her chosen Canva template with the numbers from the SUMMARY sheet of the
analysis workbook. No number is typed by hand: every number comes from a SUMMARY
cell (recalculated with LibreOffice), the speaker notes of each slide list the
cells used, and after saving the deck is re-opened and every number is compared
with SUMMARY again.

Usage:
    uv run --with openpyxl --with python-pptx python mcu_ppt.py "<... - Analisa.xlsx>" --template "<Untitled design.pptx>"

Output: "<... - Laporan MCU.pptx>" next to the analysis workbook.
Fixed texts (education, recommendations) live in ppt_konten.json (taken from her old report).
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl
from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

TEAL, DARK, SAND, LTEAL, LSAND = "307F7F", "112929", "D1B984", "7FB8B8", "EADBB4"
PALETTE = [TEAL, SAND, DARK, LTEAL, LSAND, "A3A3A3", "4F9A9A", "BFA36A"]
FONT_MAP = {"Helios": "Arial", "Helios Bold": "Arial", "Neue Montreal Bold": "Arial Black", "Neue Montreal": "Arial"}
TITLE_FONT, BODY_FONT = "Arial Black", "Arial"
# template slide numbers (1-based) in Untitled design.pptx
PAK_KOSONG = "Tidak ada"  # same label as mcu_summary.PAK_KOSONG (her PT. SKP edit)
T_COVER, T_TOC, T_ABOUT, T_CARDS, T_TABLE, T_SEGMENTS, T_ABOUT2, T_STRATEGY, T_TWOBOX, T_RISK, T_PLANS, T_THANKS = range(1, 13)


# ============================================================ formatting
def fmt_pct(v) -> str:
    return f"{(v or 0) * 100:.1f}%".replace(".", ",")


def fmt_n(v) -> str:
    return f"{int(round(v or 0)):,}".replace(",", ".")


def fmt_date(v) -> str:
    if isinstance(v, dt.datetime):
        v = v.date()
    return v.strftime("%d-%m-%Y") if isinstance(v, dt.date) else str(v)


def nice(label: str) -> str:
    """'FIT WITH NOTES' -> 'Fit with notes'; leaves mixed-case labels alone; '>=' -> '≥'."""
    s = str(label).replace(">=", "≥")
    return s[:1] + s[1:].lower() if s.isupper() else s


# ============================================================ reading SUMMARY
class Summary:
    def __init__(self, xlsx: Path):
        side = xlsx.with_name(xlsx.stem + " - summary_cells.json")
        if not side.exists():
            sys.exit(f"'{side.name}' tidak ada: jalankan mcu_summary.py dulu.")
        self.meta = json.loads(side.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "in.xlsx"
            shutil.copy(xlsx, src)
            out = Path(td) / "out"
            out.mkdir()
            subprocess.run([str(SOFFICE), "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(out), str(src)],
                           check=True, capture_output=True, timeout=900)
            wb = openpyxl.load_workbook(out / "in.xlsx", data_only=True, read_only=True)
            self.s = [list(r) for r in wb["SUMMARY"].iter_rows(values_only=True)]
            self.check_beda = list(wb["CHECK"].iter_rows(min_row=2, max_row=2, values_only=True))[0][1]
            self.raw_a1 = list(wb["RAW"].iter_rows(min_row=1, max_row=1, values_only=True))[0][0]
            maprows = list(wb["MAP"].iter_rows(values_only=True))
            wb.close()
        hi = next(i for i, r in enumerate(maprows) if r and r[0] == "Grup" and r[1] == "Kode variabel")
        self.labels = {r[1]: r[2] for r in maprows[hi + 1:] if r and r[1]}
        # company name: RAW A1 unless that cell is a vendor section title (e.g. "IDENTITAS", PT. SKP); then the vendor file name
        sections = {str(r[4]).strip().upper() for r in maprows[hi + 1:] if r and len(r) > 4 and r[4]}
        a1 = str(self.raw_a1 or "").strip()
        if not a1 or a1.upper() in sections:
            a1 = Path(str(maprows[0][1] or "")).stem.strip() or a1
        self.company = a1
        self.used: list[str] = []

    def cell(self, ref: str):
        """ref like 'SUMMARY!C3' or 'C3'."""
        ref = ref.split("!")[-1]
        m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
        col = 0
        for ch in m.group(1):
            col = col * 26 + ord(ch) - 64
        row = int(m.group(2))
        self.used.append(ref)
        return self.s[row - 1][col - 1]

    def block(self, key):
        """Rows of a block: list of dicts {row, A, B, C, ...}."""
        rng = self.meta["blok"].get(key)
        if not rng:
            return []
        self.used.append(rng.split("!")[-1])
        a, b = rng.split("!")[-1].split(":")
        r1, r2 = int(re.sub(r"[A-Z]", "", a)), int(re.sub(r"[A-Z]", "", b))
        c2 = re.sub(r"\d", "", b)
        ncol = 0
        for ch in c2:
            ncol = ncol * 26 + ord(ch) - 64
        out = []
        for r in range(r1, r2 + 1):
            vals = self.s[r - 1][:ncol]
            out.append({"row": r, **{chr(65 + i) if i < 26 else f"C{i}": v for i, v in enumerate(vals)}})
        return out

    def periode(self):
        a, b = self.meta["blok"]["S3_periode"].split("!")[-1].split(":")
        return self.cell(a), self.cell(b)

    def find_row(self, prefix):
        for i, r in enumerate(self.s):
            for v in (r[:2] if r else []):
                if isinstance(v, str) and v.startswith(prefix):
                    return i + 1, v
        return None, None


# ============================================================ pptx helpers
def dup_slide(prs, src):
    new = prs.slides.add_slide(src.slide_layout)
    tree = new.shapes._spTree
    for el in list(tree):
        if el.tag not in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            tree.remove(el)
    rid_map = {}
    for rid, rel in src.part.rels.items():
        if rel.reltype.endswith(("/slideLayout", "/notesSlide")):
            continue
        if rel.is_external:
            rid_map[rid] = new.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            rid_map[rid] = new.part.relate_to(rel.target_part, rel.reltype)
    for el in src.shapes._spTree:
        if el.tag in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            continue
        c = copy.deepcopy(el)
        for node in c.iter():
            for k, v in list(node.attrib.items()):
                if k.startswith("{%s}" % R_NS) and v in rid_map:
                    node.set(k, rid_map[v])
        tree.append(c)
    bg = src._element.cSld.find(qn("p:bg"))
    if bg is not None:
        new._element.cSld.insert(0, copy.deepcopy(bg))
    return new


def to_building(slide, shape_id, building_part, img_aspect):
    """Point the photo inside a template shape to the building picture, centre-cropped to the frame."""
    try:
        top = shape_by_id(slide, shape_id)._element
    except KeyError:
        return
    for blip in top.iter(qn("a:blip")):
        rid = slide.part.relate_to(building_part, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
        blip.set(qn("r:embed"), rid)
        fill = blip.getparent()
        sp = fill.getparent()
        while sp is not None and sp.find(qn("p:spPr")) is None and sp.find(qn("p:spPr")) is None:
            sp = sp.getparent()
        ext = sp.find(qn("p:spPr")).find(qn("a:xfrm")).find(qn("a:ext")) if sp is not None else None
        frame = int(ext.get("cx")) / int(ext.get("cy")) if ext is not None else 1.0
        for e in fill.findall(qn("a:srcRect")):
            fill.remove(e)
        src = etree.Element(qn("a:srcRect"))
        if frame > img_aspect:  # frame wider than picture: crop top and bottom
            cut = int((1 - img_aspect / frame) / 2 * 100000)
            src.set("t", str(cut)); src.set("b", str(cut))
        else:  # crop left and right
            cut = int((1 - frame / img_aspect) / 2 * 100000)
            src.set("l", str(cut)); src.set("r", str(cut))
        blip.addnext(src)


def shape_by_id(slide, sid):
    for sh in slide.shapes:
        if sh.shape_id == sid:
            return sh
    raise KeyError(sid)


def remove(slide, *ids):
    for sid in ids:
        try:
            el = shape_by_id(slide, sid)._element
            el.getparent().remove(el)
        except KeyError:
            pass


def text_lines_needed(text, width_in, size_pt, factor):
    chars = max(1, int(width_in * 72 / (size_pt * factor)))
    n = 0
    for para in str(text).split("\n"):
        words, cur = para.split(), 0
        lines = 1
        for w in words:
            if cur and cur + 1 + len(w) > chars:
                lines += 1
                cur = len(w)
            else:
                cur += (1 if cur else 0) + len(w)
        n += lines
    return n


def fit_size(text, width_in, height_in, max_pt, min_pt, factor=0.52, spacing=1.2):
    size = max_pt
    while size > min_pt:
        if text_lines_needed(text, width_in, size, factor) * size * spacing / 72 <= height_in:
            return size
        size -= 1
    return min_pt


def set_text(shape, paras, size=None, bold=None, color=None, align=None, font=None, space_after=None):
    """paras: str (\\n = new paragraph) or list of paragraphs; a paragraph may be a list of (text, bold) runs."""
    if isinstance(paras, str):
        paras = paras.split("\n")
    tx = shape.text_frame._txBody
    ps = tx.findall(qn("a:p"))
    p0 = ps[0]
    r0 = p0.find(qn("a:r"))
    rpr0 = copy.deepcopy(r0.find(qn("a:rPr"))) if r0 is not None and r0.find(qn("a:rPr")) is not None else etree.SubElement(etree.Element("x"), qn("a:rPr"))
    for p in ps:
        tx.remove(p)
    body = tx.find(qn("a:bodyPr"))
    for k in ("normAutofit", "spAutoFit"):
        for e in body.findall(qn("a:" + k)):
            body.remove(e)
    body.set("wrap", "square")
    for para in paras:
        p = copy.deepcopy(p0)
        for child in list(p):
            if child.tag in (qn("a:r"), qn("a:br"), qn("a:fld"), qn("a:endParaRPr")):
                p.remove(child)
        ppr = p.find(qn("a:pPr"))
        if ppr is None:
            ppr = etree.SubElement(p, qn("a:pPr"))
            p.insert(0, ppr)
        for e in ppr.findall(qn("a:lnSpc")):
            ppr.remove(e)
        ln = etree.SubElement(ppr, qn("a:lnSpc"))
        etree.SubElement(ln, qn("a:spcPct")).set("val", "105000")
        ppr.insert(0, ln)
        if space_after is not None:
            for e in ppr.findall(qn("a:spcAft")):
                ppr.remove(e)
            sa = etree.SubElement(ppr, qn("a:spcAft"))
            etree.SubElement(sa, qn("a:spcPts")).set("val", str(int(space_after * 100)))
        if align:
            ppr.set("algn", align)
        runs = para if isinstance(para, list) else [(para, None)]
        for txt, b in runs:
            r = etree.SubElement(p, qn("a:r"))
            rpr = copy.deepcopy(rpr0)
            if size:
                rpr.set("sz", str(int(size * 100)))
            bb = b if b is not None else bold
            if bb is not None:
                rpr.set("b", "1" if bb else "0")
            if color:
                for e in rpr.findall(qn("a:solidFill")):
                    rpr.remove(e)
                sf = etree.Element(qn("a:solidFill"))
                etree.SubElement(sf, qn("a:srgbClr")).set("val", color)
                rpr.insert(0, sf)
            if font:
                for tag in ("latin", "ea", "cs", "sym"):
                    for e in rpr.findall(qn("a:" + tag)):
                        e.set("typeface", font)
            r.append(rpr)
            t = etree.SubElement(r, qn("a:t"))
            t.text = str(txt)
        tx.append(p)


def set_title(shape, text, max_pt, min_pt=24, factor=0.95):
    w, h = shape.width / 914400, shape.height / 914400
    set_text(shape, text, size=fit_size(text, w - 0.2, h, max_pt, min_pt, factor, 1.1), font=TITLE_FONT)


def map_fonts(slide):
    for el in slide._element.iter(qn("a:latin"), qn("a:ea"), qn("a:cs"), qn("a:sym")):
        f = el.get("typeface")
        if f in FONT_MAP:
            el.set("typeface", FONT_MAP[f])


def add_box(slide, x, y, w, h, paras, size, color=DARK, bold=False, align="l", font=BODY_FONT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    if isinstance(paras, str):
        paras = paras.split("\n")
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": 1, "ctr": 2, "r": 3}[align]
        runs = para if isinstance(para, list) else [(para, None)]
        for txt, b in runs:
            r = p.add_run()
            r.text = str(txt)
            r.font.size = Pt(size)
            r.font.name = font
            r.font.bold = bold if b is None else b
            r.font.color.rgb = RGBColor.from_string(color)
        p.space_after = Pt(size * 0.4)
    return tb


def chart_fill(chart, hexcolor="FFFFFF"):
    cs = chart._chartSpace
    sppr = cs.find(qn("c:spPr"))
    if sppr is None:
        sppr = etree.SubElement(cs, qn("c:spPr"))
        txpr = cs.find(qn("c:txPr"))
        if txpr is not None:
            txpr.addprevious(sppr)
    for e in list(sppr):
        sppr.remove(e)
    sf = etree.SubElement(sppr, qn("a:solidFill"))
    etree.SubElement(sf, qn("a:srgbClr")).set("val", hexcolor)
    ln = etree.SubElement(sppr, qn("a:ln"))
    etree.SubElement(ln, qn("a:noFill"))


def add_bar(slide, cats, vals, x, y, w, h, title=None, color=TEAL, size=18, fill="FFFFFF"):
    data = CategoryChartData()
    data.categories = cats
    data.add_series("Jumlah pekerja", vals)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), data)
    ch = gf.chart
    ch.font.name = BODY_FONT
    ch.font.size = Pt(size)
    ch.font.color.rgb = RGBColor.from_string(DARK)
    ch.has_legend = False
    ch.has_title = bool(title)
    if title:
        ch.chart_title.text_frame.text = title
        tp = ch.chart_title.text_frame.paragraphs[0]
        tp.runs[0].font.size = Pt(size + 1)
        tp.runs[0].font.bold = True
        tp.runs[0].font.name = BODY_FONT
    plot = ch.plots[0]
    plot.gap_width = 55 if len(vals) > 3 else 200
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = "0"
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(size)
    dl.font.bold = True
    ser = plot.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = RGBColor.from_string(color)
    ca = ch.category_axis
    ca.reverse_order = True
    ca.tick_labels.font.size = Pt(size)
    ca.format.line.color.rgb = RGBColor.from_string("BFBFBF")
    ca.has_major_gridlines = False
    va = ch.value_axis
    va.visible = False
    va.has_major_gridlines = False
    va.minimum_scale = 0
    va.maximum_scale = max(vals + [1]) * 1.18
    chart_fill(ch, fill)
    return gf


def add_doughnut(slide, cats, vals, x, y, w, h, size=18, fill="FFFFFF", palette=None, text_color=DARK):
    data = CategoryChartData()
    data.categories = cats
    data.add_series("Jumlah pekerja", vals)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(x), Inches(y), Inches(w), Inches(h), data)
    ch = gf.chart
    ch.font.name = BODY_FONT
    ch.font.size = Pt(size)
    ch.font.color.rgb = RGBColor.from_string(text_color)
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.BOTTOM
    ch.legend.include_in_layout = False
    ch.legend.font.size = Pt(size)
    plot = ch.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.show_percentage = True
    dl.show_value = False
    dl.show_category_name = False
    dl.number_format = "0.0%"
    dl.number_format_is_linked = False
    dl.font.size = Pt(size)
    dl.font.bold = True
    dl.font.color.rgb = RGBColor.from_string("FFFFFF")
    for i, pt in enumerate(plot.series[0].points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = RGBColor.from_string((palette or PALETTE)[i % len(palette or PALETTE)])
    dn = ch._chartSpace.find(".//" + qn("c:doughnutChart"))
    hs = dn.find(qn("c:holeSize"))
    if hs is None:
        hs = etree.SubElement(dn, qn("c:holeSize"))
    hs.set("val", "55")
    chart_fill(ch, fill)
    return gf


def fill_table(slide, tbl_shape, header, rows, x, y, w, row_h, col_fracs, hdr_pt=16, body_pt=14, left_cols=(1,)):
    gf = tbl_shape._element
    tbl = gf.find(".//" + qn("a:tbl"))
    trs = tbl.findall(qn("a:tr"))
    hdr_t, body_t = trs[0], trs[1]
    for tr in trs:
        tbl.remove(tr)
    grid = tbl.find(qn("a:tblGrid"))
    for gc in list(grid):
        grid.remove(gc)
    ncol = len(header)
    W = Inches(w)
    widths = [int(W * f / sum(col_fracs)) for f in col_fracs]
    for wd in widths:
        etree.SubElement(grid, qn("a:gridCol")).set("w", str(wd))

    def make_row(tpl, values, pt, is_hdr):
        tcs = tpl.findall(qn("a:tc"))
        tr = etree.SubElement(tbl, qn("a:tr"))
        tr.set("h", str(int(Inches(row_h))))
        for j in range(ncol):
            src = tcs[0] if j == 0 else (tcs[-1] if j == ncol - 1 else tcs[1])
            tc = copy.deepcopy(src)
            tcpr = tc.find(qn("a:tcPr"))
            for k in ("marL", "marR"):
                tcpr.set(k, str(int(Inches(0.08))))
            for k in ("marT", "marB"):
                tcpr.set(k, str(int(Inches(0.03))))
            p = tc.find(".//" + qn("a:p"))
            ppr = p.find(qn("a:pPr"))
            for e in ppr.findall(qn("a:lnSpc")):
                ppr.remove(e)
            ppr.set("algn", "l" if (j in left_cols and not is_hdr) else "ctr")
            rs = p.findall(qn("a:r"))
            for extra in rs[1:]:
                p.remove(extra)
            rpr = rs[0].find(qn("a:rPr"))
            rpr.set("sz", str(int(pt * 100)))
            rs[0].find(qn("a:t")).text = "" if values[j] is None else str(values[j])
            tr.append(tc)
        return tr

    make_row(hdr_t, header, hdr_pt, True)
    for r in rows:
        make_row(body_t, r, body_pt, False)
    gf.find(qn("p:xfrm")).find(qn("a:off")).set("x", str(int(Inches(x))))
    gf.find(qn("p:xfrm")).find(qn("a:off")).set("y", str(int(Inches(y))))
    gf.find(qn("p:xfrm")).find(qn("a:ext")).set("cx", str(sum(widths)))
    gf.find(qn("p:xfrm")).find(qn("a:ext")).set("cy", str(int(Inches(row_h) * (len(rows) + 1))))


def add_notes(slide, lines):
    slide.notes_slide.notes_text_frame.text = "\n".join(lines)


# ============================================================ deck builder
class Deck:
    MAX_FIT_BOXES = 3  # status categories written next to the doughnut (the teal slide has 4 boxes, one for risk)
    def __init__(self, summary: Summary, template: Path, konten, aset_dir: Path | None = None):
        self.aset_dir = aset_dir
        self.aset = json.loads((aset_dir / "aset_edukasi.json").read_text(encoding="utf-8")) if aset_dir else None
        self.S = summary
        self.k = konten
        self.prs = Presentation(str(template))
        self.tpl = list(self.prs.slides)
        self.n_orig = len(self.tpl)
        self.checks: list[tuple[int, str]] = []      # (slide no, text that must appear)
        self.chart_checks: list[tuple[int, list]] = []
        self.N = summary.cell("C3")
        self.company = summary.company or "Perusahaan"
        self.judul_fit = summary.meta.get("judul_fitness", "Status kelaikan kerja")
        self.setup_template()

    def setup_template(self):
        # the template's only non-people photo (building, slide 7) replaces the people photos (Vidya 2026-11-08)
        self.use_building(self.tpl[T_ABOUT2 - 1], 22)

    def use_building(self, slide, shape_id):
        from PIL import Image
        import io
        bl = shape_by_id(slide, shape_id)._element.find(".//" + qn("a:blip"))
        self.building = slide.part.related_part(bl.get(qn("r:embed")))
        w, h = Image.open(io.BytesIO(self.building.blob)).size
        self.building_aspect = w / h

    def new(self, tno):
        self.S.used = []
        s = dup_slide(self.prs, self.tpl[tno - 1])
        return s

    def done(self, slide, title):
        map_fonts(slide)
        refs = sorted(set(self.S.used), key=lambda r: (int(re.sub(r"[A-Z]", "", r.split(":")[0])), r))
        add_notes(slide, [f"Slide: {title}", "Sumber angka (sheet SUMMARY di workbook Analisa): " + (", ".join(refs) if refs else "-")])

    def expect(self, slide, text):
        self.checks.append((len(self.prs.slides) - self.n_orig, text))

    def toc_items(self):
        stat = self.judul_fit if self.judul_fit != "Status kelaikan kerja" else "Status Kelaikan Kerja"
        if self.S.meta["blok"].get("pak_dugaan"):
            stat += " & Dugaan PAK"  # the template has 10 TOC slots, all used
        return [stat if x == "Status Kelaikan Kerja" else x for x in self.k["daftar_isi"]]

    def kebiasaan(self, hab):
        boxes = [f"{fmt_n(r['C'])} dari {fmt_n(self.N)} pekerja ({fmt_pct(r['D'])})" for lab, r, _ in hab]
        s = self.new(T_TABLE)
        set_title(shape_by_id(s, 13), "KEBIASAAN PEKERJA", 50)
        tbl = next(sh for sh in s.shapes if sh.has_table)
        tbl._element.getparent().remove(tbl._element)
        add_bar(s, [f"{lab} ({fmt_pct(r['D'])})" for lab, r, _ in hab], [r["C"] for _, r, _ in hab], 1.2, 2.5, 10.0, 7.6,
                title="Jumlah pekerja", size=17)
        self.chart_checks.append((len(self.prs.slides) - self.n_orig, [r["C"] for _, r, _ in hab]))
        paras = []
        for (lab, _, _), b in zip(hab, boxes):  # label bold on its own line, number below, blank line between
            paras += [[(f"{lab}: ", True)], [(b, False)], [("", False)]]
        add_box(s, 11.8, 3.0, 7.2, 6.5, paras[:-1], 24)
        for b in boxes:
            self.expect(s, b)
        self.done(s, "Kebiasaan pekerja")

    # ---------------------------------------------------------------- slides
    def cover(self):
        s = self.new(T_COVER)
        d1, d2 = self.S.periode()
        set_title(shape_by_id(s, 38), "ANALISA HASIL MCU " + str(d2.year if isinstance(d2, (dt.date, dt.datetime)) else ""), 80, 40)
        set_text(shape_by_id(s, 39), self.company, size=26, bold=True, color=TEAL)
        pres = self.k.get("penyaji") or ""  # she deletes the placeholder, so none
        set_text(shape_by_id(s, 40), [[("Disusun oleh: " if pres else "Disusun oleh:", True), (pres, False)]], size=20)
        set_text(shape_by_id(s, 41), [[("Periode MCU: ", True), (f"{fmt_date(d1)} s/d {fmt_date(d2)}", False)]], size=20)
        set_text(shape_by_id(s, 42), self.company, size=20)
        to_building(s, 27, self.building, self.building_aspect)
        self.expect(s, fmt_date(d1))
        self.done(s, "Sampul")

    def toc(self, items):
        s = self.new(T_TOC)
        set_title(shape_by_id(s, 56), "DAFTAR ISI", 58)
        slots = [61, 63, 65, 67, 69, 62, 64, 66, 68, 70]
        nums = [57, 59, 71, 73, 75, 58, 60, 72, 74, 76]
        for i, sid in enumerate(slots):
            if i < len(items):
                set_text(shape_by_id(s, sid), items[i], size=22)
                shape_by_id(s, sid).width = Inches(4.4)
            else:
                remove(s, sid, nums[i])
        self.done(s, "Daftar isi")

    def ringkasan(self):
        s = self.new(T_CARDS)
        set_title(shape_by_id(s, 44), "RINGKASAN", 58)
        remove(s, 10, 13, 19, 25)  # stock photos in the card circles
        for sh in list(s.shapes):  # their frames and shadows
            if 2.0 < sh.top / 914400 < 3.6 and 2.2 < sh.width / 914400 < 4.7 and sh.shape_type != 17:
                sh._element.getparent().remove(sh._element)
        fit = self.S.block("kelaikan_fitness")
        top = self.S.block("S4_top_ten")
        d1, d2 = self.S.periode()
        cards = [(fmt_n(self.N), f"peserta MCU\n{fmt_date(d1)} s/d {fmt_date(d2)}")]
        for r in fit[:2]:
            lab = nice(r["B"]) if self.judul_fit == "Status kelaikan kerja" else f"{self.judul_fit} {nice(r['B'])}"
            cards.append((fmt_pct(r["D"]), f"{lab}\n({fmt_n(r['C'])} pekerja)"))
        if top:
            cards.append((fmt_pct(top[0]["D"]), f"temuan terbanyak:\n{top[0]['B']} ({fmt_n(top[0]['C'])} pekerja)"))
        boxes = [27, 45, 46, 28]
        xs = [1.37, 5.75, 10.13, 14.51]
        for i, (big, small) in enumerate(cards[:4]):
            add_box(s, xs[i] + 0.1, 5.0, 3.92, 1.2, big, 48, color="FFFFFF", bold=True, align="ctr", font=TITLE_FONT)
            sh = shape_by_id(s, boxes[i])
            sh.top, sh.height, sh.left, sh.width = Inches(6.5), Inches(3.0), Inches(xs[i] + 0.2), Inches(3.72)
            set_text(sh, small, size=fit_size(small, 3.6, 2.9, 24, 16), align="ctr", color="FFFFFF")
            self.expect(s, big)
        self.done(s, "Ringkasan eksekutif")

    def profil(self, groups):
        s = self.new(T_ABOUT)
        set_title(shape_by_id(s, 18), "PROFIL PERUSAHAAN", 54)
        d1, d2 = self.S.periode()
        lines = [[("Perusahaan: ", True), (self.company, False)],
                 [("Peserta MCU: ", True), (f"{fmt_n(self.N)} pekerja", False)],
                 [("Periode MCU: ", True), (f"{fmt_date(d1)} s/d {fmt_date(d2)}", False)]]
        for key, rows in groups:
            lines.append([(f"Jumlah {self.S.labels.get(key, key).lower()}: ", True), (f"{len(rows)}", False)])
        to_building(s, 10, self.building, self.building_aspect)
        set_text(shape_by_id(s, 19), lines, size=26, space_after=12)
        self.done(s, "Profil perusahaan")

    def segments(self, title, cats, vals, boxes, chart_title=None):
        s = self.new(T_SEGMENTS)
        set_title(shape_by_id(s, 47), title, 54)
        remove(s, 3)
        add_doughnut(s, cats, vals, 1.0, 2.3, 9.0, 8.5, size=18, fill="FFFFFF")
        self.chart_checks.append((len(self.prs.slides) - self.n_orig, vals))
        ids = [48, 49, 50, 51]
        groups = [4, 7, 10, 13]
        icons = [16, 19, 22, 25]
        for i, sid in enumerate(ids):
            if i < len(boxes):
                sh = shape_by_id(s, sid)
                sh.width = Inches(5.7)
                set_text(sh, boxes[i], size=fit_size(boxes[i], 5.6, 1.0, 24, 15), color="FFFFFF")
                sh.top = Inches(3.02 + 1.84 * i + 0.25)
                sh.height = Inches(1.1)
            else:
                remove(s, sid, groups[i], icons[i])
        self.done(s, title)
        return s

    def table_slide(self, title, header, rows, col_fracs, x=1.0, y=3.0, w=17.2, row_h=0.55, hdr_pt=18, body_pt=17,
                    left_cols=(1,), chart=None, subtitle=None):
        s = self.new(T_TABLE)
        set_title(shape_by_id(s, 13), title, 50, 26)
        t = shape_by_id(s, 13)
        t.left, t.width = Inches(1.0), Inches(18.0)
        tbl = next(sh for sh in s.shapes if sh.has_table)
        fill_table(s, tbl, header, rows, x, y, w, row_h, col_fracs, hdr_pt, body_pt, left_cols)
        if subtitle:
            add_box(s, 2.0, 2.15, 16.0, 0.8, subtitle, 17, color=TEAL, align="ctr")
        if chart:
            cats, vals, cx, cy, cw, chh = chart
            add_bar(s, cats, vals, cx, cy, cw, chh, size=16)
            self.chart_checks.append((len(self.prs.slides) - self.n_orig, vals))
        for r in rows:
            for v in r:
                if v not in (None, "") and re.search(r"\d", str(v)):
                    self.expect(s, str(v))
        self.done(s, title)
        return s

    def pak(self):
        """Vendor's 'Dugaan PAK' column, as written (Vidya 2026-11-10: always its own slide when the column exists)."""
        rows = self.S.block("pak_dugaan")
        if not rows:
            return
        filled = [r for r in rows if r["B"] != PAK_KOSONG]
        body = [[r["A"], r["B"], fmt_n(r["C"]), fmt_pct(r["D"])] for r in rows]
        if filled:
            sub = f"Isi kolom Dugaan PAK dari vendor, apa adanya; % dari total peserta MCU (N = {fmt_n(self.N)})"
        else:
            sub = f"Kolom Dugaan PAK pada data vendor tidak diisi untuk seluruh {fmt_n(self.N)} peserta MCU"
        self.table_slide("DUGAAN PENYAKIT AKIBAT KERJA (PAK)", ["No", "Dugaan PAK (vendor)", "Jumlah", "%"], body,
                         [0.6, 6.0, 1.3, 1.3], x=1.5, y=3.2, w=16.8, row_h=0.66, hdr_pt=19, body_pt=19, subtitle=sub)
        self.expect(self.prs.slides[-1], sub)

    def topik(self, cfg):
        tp = cfg["topik"]
        key = next((k for k in self.S.meta["blok"] if re.fullmatch(r"S\d+_" + re.escape(tp), k) or k == f"Topik_{tp}"), None)
        rows = self.S.block(key) if key else []
        if not rows:
            return
        items = [r for r in rows if not str(r["B"]).startswith(("Salah satu", "Tanpa"))]
        anyr = next(r for r in rows if str(r["B"]).startswith("Salah satu"))
        s = self.new(T_ABOUT2)
        t = shape_by_id(s, 36)
        t.width, t.height = Inches(9.4), Inches(2.4)
        set_title(t, cfg["judul"], 50, 28)
        remove(s, 22, 24)  # photo circle and the icon circle
        top = sorted([r for r in items if (r["C"] or 0) > 0], key=lambda r: -r["C"])
        sent = f"Dari {fmt_n(self.N)} peserta MCU, {fmt_n(anyr['C'])} pekerja ({fmt_pct(anyr['D'])}) memiliki temuan {tp.lower()}"
        if top:
            sent += ", terbanyak " + "; ".join(f"{r['B'].lower() if r['B'][1:].islower() else r['B']} {fmt_n(r['C'])} pekerja ({fmt_pct(r['D'])})" for r in top[:2])
        sent += "."
        self.expect(s, fmt_pct(anyr["D"]))
        paras = [[(sent, True)]] + [[(e, False)] for e in cfg["edukasi"]]
        body = shape_by_id(s, 37)
        body.left, body.top, body.height, body.width = Inches(1.64), Inches(4.0), Inches(6.4), Inches(9.2)
        alltxt = "\n".join([sent] + cfg["edukasi"])
        set_text(body, paras, size=fit_size(alltxt, 9.0, 6.2, 24, 15, 0.5, 1.45), space_after=10)
        ck = cfg.get("kategori_interpretasi")
        if ck and self.S.block(ck):
            crow = self.S.block(ck)
            cats = [f"{r['B']} ({fmt_pct(r['D'])})" for r in crow]
            vals = [r["C"] or 0 for r in crow]
            ctitle = "Kesimpulan spirometri (interpretasi vendor)"
        else:
            cats = [f"{r['B']} ({fmt_pct(r['D'])})" for r in items]
            vals = [r["C"] or 0 for r in items]
            ctitle = f"Jumlah pekerja dengan temuan {tp.lower()}"  # "dengan", not "per" (Vidya 2026-11-10)
        add_bar(s, cats, vals, 11.4, 2.2, 8.1, 7.6, title=ctitle, size=16)
        self.chart_checks.append((len(self.prs.slides) - self.n_orig, vals))
        self.done(s, cfg["judul"])

    def aset_slide(self, entry, folder: Path):
        from PIL import Image
        s = self.new(T_TABLE)
        set_title(shape_by_id(s, 13), entry["judul"], 50, 26)
        t = shape_by_id(s, 13)
        t.left, t.width = Inches(1.0), Inches(18.0)
        tbl = next(sh for sh in s.shapes if sh.has_table)
        tbl._element.getparent().remove(tbl._element)
        imgs = entry["gambar"]
        area_x, area_y, area_w, area_h, gap, cap_h = 1.4, 2.5, 17.2, 6.9, 0.8, 1.2
        n = len(imgs)
        aspects = [(lambda wh: wh[0] / wh[1])(Image.open(folder / g["file"]).size) for g in imgs]
        weights = [min(max(a, 0.7), 2.5) for a in aspects]  # wide pictures get wider columns
        free = area_w - gap * (n - 1)
        sx = area_x
        for i, g in enumerate(imgs):
            a = aspects[i]
            slot_w = free * weights[i] / sum(weights)
            w = min(slot_w, area_h * a)
            h = w / a
            x = sx + (slot_w - w) / 2
            y = area_y + (area_h - h) / 2
            pic = s.shapes.add_picture(str(folder / g["file"]), Inches(x), Inches(y), Inches(w), Inches(h))
            pic._element.find(".//" + qn("p:cNvPr")).set("descr", g.get("keterangan", ""))
            add_box(s, sx, y + h + 0.15, slot_w, cap_h, g.get("keterangan", ""), 18, color=DARK, align="ctr")
            sx += slot_w + gap
        self.done(s, entry["judul"])

    def rekomendasi(self, recs):
        for i in range(0, len(recs), 2):
            s = self.new(T_TWOBOX)
            set_title(shape_by_id(s, 32), "REKOMENDASI INDIVIDU", 46, 26)
            remove(s, 18, 21)  # money icons of the template
            for sh in list(s.shapes):  # their loose glyphs
                if 8.0 < sh.left / 914400 < 10.3 and sh.width / 914400 < 1.8 and sh.shape_type != 17:
                    sh._element.getparent().remove(sh._element)
            long_first = len(recs[i][0]) > 300  # Vidya's layout: a tall top box for the long lifestyle text
            if long_first:
                frames = [(1.48, 4.70, 10.8), (6.94, 2.19, 10.8)]  # the tall top box covers the dark bar
            else:
                frames = [(1.48, 3.45, 11.3), (5.87, 3.38, 11.3)]
                remove(s, 11)  # dark bar between the boxes (she removed it here)
            for j, sid in enumerate((33, 34)):
                sh = shape_by_id(s, sid)
                box = shape_by_id(s, (12, 15)[j])
                if i + j < len(recs):
                    text, basis = recs[i + j]
                    by, bh, bw = frames[j]
                    box.top, box.height, box.width = Inches(by), Inches(bh), Inches(bw)
                    tw = bw - 0.8
                    sh.left, sh.top, sh.height, sh.width = Inches(8.2), Inches(by + 0.17), Inches(bh - 0.3), Inches(tw)
                    full = text + "\n" + basis
                    set_text(sh, [[(text, False)], [(basis, True)]], size=fit_size(full, tw - 0.2, bh - 0.4, 28, 14, 0.5, 1.4), space_after=8)
                else:
                    remove(s, sid, (12, 15)[j])
            self.done(s, "Rekomendasi individu")

    def wellness(self):
        w = self.k["wellness"]
        s = self.new(T_ABOUT)
        set_title(shape_by_id(s, 18), w["judul"], 46, 26)
        paras = [[(w["pengantar"], False)]] + [[(f"{i}. {b}", False)] for i, b in enumerate(w["butir"], 1)]
        set_text(shape_by_id(s, 19), paras, size=24, space_after=10, align="l")
        to_building(s, 10, self.building, self.building_aspect)
        self.done(s, "Rekomendasi program wellness")

    def hra(self):
        h = self.k["hra"]
        s = self.new(T_ABOUT2)
        set_title(shape_by_id(s, 36), h["judul"], 50, 28)
        body = shape_by_id(s, 37)
        set_text(body, h["teks"], size=26, align="l")
        pics = (self.aset or {}).get("hra_gambar", [])
        if pics:
            remove(s, 21, 22)  # building photo circle
            body.top = Inches(3.67)
            for g in pics:
                s.shapes.add_picture(str(self.aset_dir / g["file"]), Inches(g["x"]), Inches(g["y"]), Inches(g["w"]), Inches(g["h"]))
        self.done(s, "Health risk assessment")

    def wellness_overview(self):
        w = self.k.get("wellness_overview")
        if not w:
            return
        s = self.new(T_TABLE)
        set_title(shape_by_id(s, 13), w["judul"], 50, 26)
        t = shape_by_id(s, 13)
        t.left, t.width = Inches(1.0), Inches(18.0)
        tbl = next(sh for sh in s.shapes if sh.has_table)
        tbl._element.getparent().remove(tbl._element)
        from pptx.enum.shapes import MSO_SHAPE
        fills = [LSAND, "D8E9E9"]
        # two columns like her example: left 3 cards, right 2 cards
        pos = [(1.3, 2.6), (1.3, 5.05), (1.3, 7.5), (10.3, 2.6), (10.3, 5.05)]
        for k, card in enumerate(w["kartu"][:5]):
            x, y = pos[k]
            h = 2.3 if k != 2 else 2.6
            box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(8.4), Inches(h))
            box.fill.solid()
            box.fill.fore_color.rgb = RGBColor.from_string(fills[k % 2])
            box.line.fill.background()
            box.shadow.inherit = False
            add_box(s, x + 0.3, y + 0.2, 7.8, h - 0.3, [[(card["judul"], True)], [(card["teks"], False)]], 22)
        self.done(s, w["judul"])

    def penutup(self):
        s = self.new(T_THANKS)
        set_title(shape_by_id(s, 54), "TERIMA KASIH", 80, 40)
        pres = self.k.get("penyaji") or ""
        set_text(shape_by_id(s, 55), [[("Disusun oleh: " if pres else "Disusun oleh:", True), (pres, False)]], size=20)
        d1, d2 = self.S.periode()
        set_text(shape_by_id(s, 56), [[("Periode MCU: ", True), (f"{fmt_date(d1)} s/d {fmt_date(d2)}", False)]], size=20)
        set_text(shape_by_id(s, 57), self.company, size=20)
        remove(s, 58, 59, 60, 61, 38, 41, 44, 45, 46, 49, 50)
        to_building(s, 27, self.building, self.building_aspect)
        for sh in list(s.shapes):  # any remaining contact icon at the left column
            if 1.7 < sh.left / 914400 < 2.2 and 4.8 < sh.top / 914400 < 9.3:
                sh._element.getparent().remove(sh._element)
        self.done(s, "Penutup")

    # ---------------------------------------------------------------- whole deck
    def build(self):
        S = self.S
        groups = [(k, S.block(f"S5_{k}_top3")) for k, _ in S.meta["grup"]]
        self.cover()
        self.toc(self.toc_items())
        self.profil([(k, [r for r in S.block(f"S5_{k}_semua_grup")]) for k, _ in S.meta["grup"]])
        self.ringkasan()
        # demographics
        umur = S.block("S3_kelompok_umur")
        jk = S.block("S3_jenis_kelamin")
        umur = [r for r in umur if r["C"]]
        jk = [r for r in jk if r["C"]]
        boxes = [f"Umur {nice(r['B'])}: {fmt_n(r['C'])} pekerja ({fmt_pct(r['D'])})" for r in umur[:2]] + \
                [f"{r['B']}: {fmt_n(r['C'])} pekerja ({fmt_pct(r['D'])})" for r in jk[:2]]
        s = self.segments("KARAKTERISTIK DEMOGRAFI", [f"Umur {nice(r['B'])}" for r in umur], [r["C"] for r in umur], boxes)
        for b in boxes:
            self.checks.append((len(self.prs.slides) - self.n_orig, b))
        # habits
        hab = []
        for key, yes, lab in (("S3_merokok", "Merokok", "Merokok"), ("S3_alkohol", "Ya", "Konsumsi alkohol"), ("S3_olahraga", "Ya", "Berolahraga")):
            blk = S.block(key)
            r = next((x for x in blk if x["B"] == yes), None)
            if r:
                nd = next((x for x in blk if x["B"] == "Tidak ada data"), None)
                hab.append((lab, r, nd))
        if hab:
            self.kebiasaan(hab)
        # fitness
        fit = S.block("kelaikan_fitness")
        ris = S.block("kelaikan_risiko")
        boxes = [f"{nice(r['B'])}: {fmt_n(r['C'])} pekerja ({fmt_pct(r['D'])})" for r in fit[:self.MAX_FIT_BOXES]]
        if ris:
            boxes.append("Risiko kesehatan: " + "; ".join(f"{nice(r['B']).replace('Risiko ', '')} {fmt_n(r['C'])}" for r in ris))
        self.segments(self.judul_fit.upper(), [nice(r["B"]) for r in fit], [r["C"] for r in fit], boxes)
        for b in boxes:
            self.checks.append((len(self.prs.slides) - self.n_orig, b))
        self.pak()
        # top ten
        top = S.block("S4_top_ten")
        rows = [[r["A"], r["B"], fmt_n(r["C"]), fmt_pct(r["D"])] for r in top if r["B"] != "-"]
        self.table_slide("TOP 10 PENYAKIT DAN TEMUAN", ["No", "Jenis penyakit / temuan", "Jumlah", "%"], rows,
                         [0.6, 4.6, 1.3, 1.3], x=1.5, y=3.0, w=9.6, row_h=0.66, hdr_pt=19, body_pt=19,
                         chart=([r["B"] for r in top if r["B"] != "-"], [r["C"] for r in top if r["B"] != "-"], 11.3, 3.0, 8.0, 7.6),
                         subtitle=f"% dari total peserta MCU (N = {fmt_n(self.N)})")
        # per group
        for key, n in S.meta["grup"]:
            lab = S.labels.get(key, key)
            t3 = S.block(f"S5_{key}_top3")
            sizes = {r["B"]: r["C"] for r in S.block(f"S5_{key}_semua_grup")}
            by_g = []
            for r in t3:
                if not by_g or by_g[-1][0] != r["B"]:
                    by_g.append((r["B"], []))
                by_g[-1][1].append(r)
            npages = -(-len(by_g) // 4)
            per = -(-len(by_g) // max(npages, 1))  # spread groups evenly over the pages
            pages = [by_g[i:i + per] for i in range(0, len(by_g), per)]
            for pi, page in enumerate(pages, 1):
                rows = []
                for g, rs in page:
                    for j, r in enumerate(rs):
                        rows.append([f"{g} (n = {fmt_n(sizes.get(g, 0))})" if j == 0 else "", r["C"],
                                     fmt_n(r["D"]) if r["C"] != "-" else "-", fmt_pct(r["E"]) if r["C"] != "-" else "-"])
                suffix = f" ({pi}/{len(pages)})" if len(pages) > 1 else ""
                self.table_slide(f"TOP 3 TEMUAN PER {lab.upper()}{suffix}", [lab, "Jenis penyakit / temuan", "Jumlah", f"% dari {lab.lower()}"],
                                 rows, [3.4, 4.6, 1.2, 1.7], x=1.5, y=3.0, w=16.8, row_h=0.58, hdr_pt=19, body_pt=18, left_cols=(0, 1),
                                 subtitle=f"{n} {lab.lower()} dengan jumlah pekerja terbanyak; % dari jumlah pekerja di {lab.lower()} tersebut")
        # combination
        tot = S.block("S6_kombinasi_total")
        if tot:
            r_note, note = S.find_row("Abnormal 1 rasio")
            lr, _ = S.find_row("Pekerja dengan data lengkap")
            n_lengkap = S.cell(f"C{lr}")
            rows = [[r["B"], fmt_n(r["C"]), fmt_pct(r["D"])] for r in tot]
            self.table_slide("ANALISA 3 KATEGORI KELAINAN", ["Kategori", "Jumlah", "%"], rows, [4.2, 1.3, 1.3],
                             x=1.5, y=3.2, w=9.2, row_h=0.68, hdr_pt=19, body_pt=19, left_cols=(0,),
                             chart=([r["B"] for r in tot], [r["C"] for r in tot], 11.0, 3.2, 8.2, 6.9),
                             subtitle=self.k.get("subjudul_kombinasi") or ((note or "") + f" Data lengkap: {fmt_n(n_lengkap)} pekerja."))
            for key, n in S.meta["grup"]:
                lab = S.labels.get(key, key)
                blk = S.block(f"S6_kombinasi_{key}")
                if not blk:
                    continue
                cats = ["Ketiganya", "Rasio + HbA1c", "Rasio + LP", "HbA1c + LP", "Hanya rasio", "Hanya HbA1c", "Hanya LP", "Tidak ada"]
                letters = [chr(65 + 3 + 2 * i) for i in range(8)]
                rows = []
                for r in blk:
                    rows.append([r["B"], fmt_n(r["C"])] + [f"{fmt_n(r[L])} ({fmt_pct(r[chr(ord(L) + 1)])})" for L in letters])
                for pi in range(0, len(rows), 10):
                    self.table_slide(f"3 KATEGORI KELAINAN PER {lab.upper()}", [lab, "Data lengkap"] + cats, rows[pi:pi + 10],
                                     [2.6, 1.1] + [1.3] * 8, x=1.5, y=3.0, w=16.8, row_h=0.70, hdr_pt=15, body_pt=15, left_cols=(0,),
                                     subtitle="Jumlah pekerja (% dari pekerja dengan data lengkap di grup tersebut)")
        # topics
        for cfg in self.k["topik"]:
            self.topik(cfg)
            for entry in (self.aset or {}).get("slide", []):
                if entry["setelah_topik"] == cfg["topik"]:
                    self.aset_slide(entry, self.aset_dir)
        # other topics in one table
        rows = []
        for tp in self.k["topik_lain"]:
            key = next((k for k in S.meta["blok"] if k == f"Topik_{tp}" or re.fullmatch(r"S\d+_" + re.escape(tp), k)), None)
            blk = S.block(key) if key else []
            if not blk:
                continue
            anyr = next(r for r in blk if str(r["B"]).startswith("Salah satu"))
            items = sorted([r for r in blk if not str(r["B"]).startswith(("Salah satu", "Tanpa")) and (r["C"] or 0) > 0], key=lambda r: -r["C"])
            if not anyr["C"]:
                continue
            rows.append([tp, fmt_n(anyr["C"]), fmt_pct(anyr["D"]), "; ".join(f"{r['B']} ({fmt_n(r['C'])})" for r in items[:3])])
        if rows:
            self.table_slide("TEMUAN LAIN", ["Topik", "Pekerja dengan temuan", "%", "Temuan terbanyak (jumlah pekerja)"], rows,
                             [2.4, 2.0, 1.2, 8.0], x=1.5, y=2.8, w=16.8, row_h=0.74, left_cols=(0, 3), hdr_pt=18, body_pt=17)
        # recommendations (her old texts, only where the topic has findings)
        recs = []
        for rec in self.k["rekomendasi_individu"]:
            parts, best = [], 0
            for tp in rec["syarat_topik"]:
                key = next((k for k in S.meta["blok"] if k == f"Topik_{tp}" or re.fullmatch(r"S\d+_" + re.escape(tp), k)), None)
                blk = S.block(key) if key else []
                anyr = next((r for r in blk if str(r["B"]).startswith("Salah satu")), None)
                if anyr and anyr["C"]:
                    parts.append((anyr["D"] or 0, f"{tp.lower()} {fmt_n(anyr['C'])} pekerja ({fmt_pct(anyr['D'])})"))
            if parts:
                parts.sort(key=lambda x: -x[0])
                recs.append((parts[0][0], rec["teks"], "Dasar: temuan " + "; ".join(t for _, t in parts) + "."))
        recs.sort(key=lambda x: -x[0])  # highest finding first (Vidya 2026-11-08)
        recs = [(t, b) for _, t, b in recs]
        if recs:
            self.rekomendasi(recs)
        self.wellness()
        self.wellness_overview()
        self.hra()
        self.penutup()
        # drop the original template slides
        sld = self.prs.slides._sldIdLst
        for sid in list(sld)[: self.n_orig]:
            self.prs.part.drop_rel(sid.rId)
            sld.remove(sid)


# ============================================================ verification
def verify(pptx: Path, checks, chart_checks):
    prs = Presentation(str(pptx))
    slides = list(prs.slides)
    texts, charts = [], []
    for s in slides:
        buf = []
        vals = []
        for sh in s.shapes:
            if sh.has_text_frame:
                buf.append(sh.text_frame.text)
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for c in row.cells:
                        buf.append(c.text)
            if getattr(sh, "has_chart", False) and sh.has_chart:
                vals.append([v for v in sh.chart.plots[0].series[0].values])
        texts.append("\n".join(buf))
        charts.append(vals)
    bad = []
    for no, t in checks:
        if t not in texts[no - 1]:
            bad.append(f"slide {no}: '{t}' tidak ditemukan")
    for no, vals in chart_checks:
        if not any([float(x) for x in v] == [float(x) for x in vals] for v in charts[no - 1]):
            bad.append(f"slide {no}: data chart {vals} tidak cocok")
    left = re.compile(r"ingoude|ginyard|lorem|reallygreatsite|anywhere st|olivia|petros|petrakis|\+123", re.I)
    for i, t in enumerate(texts, 1):
        if left.search(t):
            bad.append(f"slide {i}: sisa teks template: {left.search(t).group(0)}")
    return len(slides), len(checks) + len(chart_checks), bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("analisa", type=Path)
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--aset", type=Path, help="folder gambar edukasi berisi aset_edukasi.json (opsional)")
    ap.add_argument("--penyedia", default="", help="nama penyedia MCU untuk kartu Personal Tracker, mis. \"Hermina Samarinda\"")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    konten = json.loads((HERE / "ppt_konten.json").read_text(encoding="utf-8"))
    for card in (konten.get("wellness_overview") or {}).get("kartu", []):  # "{penyedia}" -> MCU provider, or nothing
        card["teks"] = " ".join(card["teks"].replace("{penyedia}", args.penyedia).split())
    S = Summary(args.analisa.resolve())
    if S.check_beda not in (0, None):
        sys.exit(f"Sheet CHECK menunjukkan {S.check_beda} BEDA: perbaiki SUMMARY dulu sebelum membuat PPT.")
    sys.path.insert(0, str(HERE))
    import mcu_ppt_navy  # navy/orange template ('Untitled design (1).pptx'), Vidya 2026-11-10
    cls = mcu_ppt_navy.DeckNavy if mcu_ppt_navy.is_navy_template(Presentation(str(args.template))) else Deck
    print(f"Layout : {'navy-oranye (Untitled design (1))' if cls is not Deck else 'teal (Untitled design)'}")
    deck = cls(S, args.template.resolve(), konten, args.aset.resolve() if args.aset else None)
    deck.build()
    out = args.analisa.with_name(args.analisa.stem.replace(" - Analisa", "") + " - Laporan MCU.pptx")
    deck.prs.save(str(out))
    n, k, bad = verify(out, deck.checks, deck.chart_checks)
    print(f"Hasil  : {out}")
    print(f"Slide  : {n} | angka/teks dicek ulang terhadap SUMMARY: {k} | masalah: {len(bad)}")
    for b in bad[:30]:
        print("   ", b)
    if not konten.get("penyaji"):
        print("Catatan: nama penyaji kosong (ppt_konten.json -> 'penyaji'); slide hanya menulis 'Disusun oleh:'.")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
