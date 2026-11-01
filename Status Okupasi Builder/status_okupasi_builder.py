"""
Status Okupasi Builder
======================
Isi ulang dokumen "Berkas/Status Okupasi" (format PPDS Sp.Ok FKUI) memakai
docx milik sendiri sebagai BASIS, sehingga format (font, numbering, tabel,
checkbox, logo, body map) tetap persis seperti aslinya.

Pemakaian:
    python status_okupasi_builder.py isi_pasien.json
    python status_okupasi_builder.py isi_pasien.json --map     # cetak peta anchor basis

Semua isi pasien ada di file JSON (lihat README.md untuk skema). Skrip ini
tidak menyimpan data pasien apa pun.
"""
import argparse
import copy
import json
import os
import sys

import docx
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def q14(tag):
    return "{%s}%s" % (W14, tag)


# ----------------------------------------------------------------- helpers
def ptext(p_el):
    """Teks paragraf dari run langsung (tanpa isi checkbox sdt)."""
    out = []
    for child in p_el.iter():
        if child.tag == qn("w:t"):
            # lewati teks di dalam sdt checkbox
            anc = child.getparent()
            in_cb = False
            while anc is not None and anc is not p_el:
                if anc.tag == qn("w:sdt") and anc.find(".//" + q14("checkbox")) is not None:
                    in_cb = True
                    break
                anc = anc.getparent()
            if not in_cb:
                out.append(child.text or "")
        elif child.tag == qn("w:tab"):
            out.append("\t")
    return "".join(out)


def has_num(p_el):
    return p_el.find(".//" + qn("w:numPr")) is not None


def has_img(p_el):
    return p_el.find(".//" + qn("w:drawing")) is not None or p_el.find(".//" + qn("w:pict")) is not None


def has_cb(el):
    return el.find(".//" + q14("checkbox")) is not None


def is_sect(p_el):
    return p_el.find(qn("w:pPr") + "/" + qn("w:sectPr")) is not None


def strip_ids(el):
    for e in el.iter():
        for a in (q14("paraId"), q14("textId")):
            if a in e.attrib:
                del e.attrib[a]


def make_para(tpl, text, bold=None):
    """Paragraf baru dengan pPr + rPr run pertama dari tpl."""
    new = copy.deepcopy(tpl)
    strip_ids(new)
    rpr = None
    for r in tpl.iter(qn("w:r")):
        if r.find(qn("w:rPr")) is not None:
            rpr = copy.deepcopy(r.find(qn("w:rPr")))
            break
    for ch in list(new):
        if ch.tag != qn("w:pPr"):
            new.remove(ch)
    ppr = new.find(qn("w:pPr"))
    if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
        ppr.remove(ppr.find(qn("w:sectPr")))
    r = new.makeelement(qn("w:r"), {})
    if rpr is not None:
        for tag in ("w:highlight", "w:shd"):
            e = rpr.find(qn(tag))
            if e is not None:
                rpr.remove(e)
        if bold is not None:
            for tag in ("w:b", "w:bCs"):
                e = rpr.find(qn(tag))
                if e is not None:
                    rpr.remove(e)
            if bold:
                rpr.insert(0, rpr.makeelement(qn("w:b"), {}))
        r.append(rpr)
    elif bold:
        rp = r.makeelement(qn("w:rPr"), {})
        rp.append(rp.makeelement(qn("w:b"), {}))
        r.append(rp)
    parts = text.split("\t")
    for i, part in enumerate(parts):
        if i:
            r.append(r.makeelement(qn("w:tab"), {}))
        if part:
            t = r.makeelement(qn("w:t"), {})
            t.text = part
            t.set(XML_SPACE, "preserve")
            r.append(t)
    new.append(r)
    return new


def parse_line(line):
    """Penanda awal baris (boleh digabung):
    '• '  = pakai paragraf asli bernomor/bullet berikutnya sebagai template
    '~ '  = pakai paragraf asli tanpa nomor berikutnya sebagai template
    '@N ' = pakai paragraf asli ke-N (0-based) di section tsb sebagai template
    '!b ' = tebal
    Tanpa penanda: template = paragraf asli pada posisi yang sama."""
    kind, bold = None, None
    while True:
        if line.startswith("• "):
            kind, line = "list", line[2:]
        elif line.startswith("~ "):
            kind, line = "plain", line[2:]
        elif line.startswith("!b "):
            bold, line = True, line[3:]
        elif line.startswith("@") and " " in line and line[1:line.index(" ")].isdigit():
            kind, line = int(line[1:line.index(" ")]), line[line.index(" ") + 1:]
        else:
            return kind, bold, line


def build_paras(originals, lines, fallback):
    texts = [p for p in originals if ptext(p).strip() and not has_cb(p)] or [fallback]
    lst = [p for p in texts if has_num(p)] or texts
    pln = [p for p in texts if not has_num(p)] or texts
    n_list = n_plain = 0
    out = []
    for k, line in enumerate(lines):
        kind, bold, txt = parse_line(line)
        if not txt.strip() and kind is None:
            # baris kosong: jangan sampai jadi bullet kosong
            tpl = [p for p in originals if not has_num(p)][:1] or [pln[0]]
            out.append(make_para(tpl[0], "", bold))
            continue
        if kind == "list":
            tpl = lst[min(n_list, len(lst) - 1)]
            n_list += 1
        elif kind == "plain":
            tpl = pln[min(n_plain, len(pln) - 1)]
            n_plain += 1
        elif isinstance(kind, int):
            tpl = texts[min(kind, len(texts) - 1)]
        else:
            tpl = texts[min(k, len(texts) - 1)]
        out.append(make_para(tpl, txt, bold))
    return out


# ------------------------------------------------------------------ engine
class Builder:
    def __init__(self, base):
        self.doc = docx.Document(base)
        self.body = self.doc.element.body
        self.log = []

    def blocks(self):
        return list(self.body.iterchildren())

    def find_body(self, prefix, start=0, occ=0):
        n = 0
        for i, el in enumerate(self.blocks()):
            if i < start or el.tag != qn("w:p"):
                continue
            if ptext(el).strip().startswith(prefix):
                if n == occ:
                    return i
                n += 1
        raise KeyError("Anchor tidak ditemukan: %r" % prefix)

    def all_paras(self):
        return list(self.body.iter(qn("w:p")))

    # -- sections
    def section(self, start, end, lines, start_occ=0, drop_images=True):
        bl = self.blocks()
        i = self.find_body(start, occ=start_occ)
        j = self.find_body(end, start=i + 1) if end else len(bl)
        between = bl[i + 1:j]
        paras = [e for e in between if e.tag == qn("w:p")]
        removable = [p for p in paras if not is_sect(p) and not has_cb(p) and
                     (ptext(p).strip() or (drop_images and has_img(p)))]
        new = build_paras(removable, lines, bl[i])
        for p in removable:
            p.getparent().remove(p)
        anchor = bl[i]
        for p in reversed(new):
            anchor.addnext(p)
        self.log.append("section %r..%r: %d -> %d paragraf" % (start, end, len(removable), len(new)))

    # -- single paragraph text
    def para(self, prefix, text, occ=0):
        n = 0
        for p in self.all_paras():
            if ptext(p).strip().startswith(prefix):
                if n == occ:
                    if has_cb(p):
                        raise ValueError("Paragraf %r berisi checkbox; pakai 'subs'" % prefix)
                    p.addnext(make_para(p, text))
                    p.getparent().remove(p)
                    return
                n += 1
        raise KeyError("Paragraf tidak ditemukan: %r" % prefix)

    # -- substring replace across runs
    def sub(self, old, new, all_=False):
        hits = 0
        for p in self.all_paras():
            ts = []
            for t in p.iter(qn("w:t")):
                anc, ok = t.getparent(), True
                while anc is not None and anc is not p:
                    if anc.tag == qn("w:sdt") and anc.find(".//" + q14("checkbox")) is not None:
                        ok = False
                    anc = anc.getparent()
                if ok:
                    ts.append(t)
            full = "".join(t.text or "" for t in ts)
            pos = full.find(old)
            while pos >= 0:
                end = pos + len(old)
                acc, first = 0, True
                for t in ts:
                    s = t.text or ""
                    a, b = acc, acc + len(s)
                    acc = b
                    if b <= pos or a >= end:
                        continue
                    lo, hi = max(pos, a) - a, min(end, b) - a
                    if first:
                        t.text = s[:lo] + new + s[hi:]
                        first = False
                    else:
                        t.text = s[:lo] + s[hi:]
                    t.set(XML_SPACE, "preserve")
                hits += 1
                if not all_:
                    return
                full = "".join(t.text or "" for t in ts)
                pos = full.find(old, pos + len(new))
        if not hits:
            raise KeyError("Teks untuk subs tidak ditemukan: %r" % old)

    # -- checkboxes
    @staticmethod
    def set_cb(sdt, on):
        sdt.find(".//" + q14("checked")).set(q14("val"), "1" if on else "0")
        run = sdt.find(qn("w:sdtContent") + "/" + qn("w:r"))
        if run is None:
            return
        for ch in list(run):
            if ch.tag in (qn("w:t"), qn("w:sym")):
                run.remove(ch)
        rpr = run.find(qn("w:rPr"))
        if rpr is None:
            rpr = run.makeelement(qn("w:rPr"), {})
            run.insert(0, rpr)
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.insert(0, fonts)
        if on:
            for a in ("w:ascii", "w:hAnsi"):
                fonts.set(qn(a), "Wingdings 2")
            sym = run.makeelement(qn("w:sym"), {qn("w:font"): "Wingdings 2", qn("w:char"): "F052"})
            run.append(sym)
        else:
            for a in ("w:ascii", "w:hAnsi", "w:eastAsia"):
                fonts.set(qn(a), "MS Gothic")
            t = run.makeelement(qn("w:t"), {})
            t.text = "☐"
            run.append(t)

    @staticmethod
    def checkboxes(el):
        out = []
        for p in el.iter(qn("w:p")):
            cur, lab = None, ""
            for k in p:
                if k.tag == qn("w:sdt") and k.find(".//" + q14("checkbox")) is not None:
                    if cur is not None:
                        out.append((cur, lab.strip()))
                    cur, lab = k, ""
                elif k.tag == qn("w:r"):
                    lab += "".join(t.text or "" for t in k.iter(qn("w:t")))
            if cur is not None:
                out.append((cur, lab.strip()))
        return out

    def check_para(self, prefix, values, occ=0):
        n = 0
        for p in self.all_paras():
            if ptext(p).strip().startswith(prefix):
                if n == occ:
                    cbs = self.checkboxes(p)
                    if isinstance(values, list):
                        if len(values) != len(cbs):
                            raise ValueError("%r punya %d checkbox, diberi %d" % (prefix, len(cbs), len(values)))
                        for (sdt, _), v in zip(cbs, values):
                            self.set_cb(sdt, bool(v))
                    else:
                        for sdt, lab in cbs:
                            for key, v in values.items():
                                if lab.startswith(key):
                                    self.set_cb(sdt, bool(v))
                    return
                n += 1
        raise KeyError("Paragraf checkbox tidak ditemukan: %r" % prefix)

    IDENTITY_GROUPS = [("jenis_kelamin", 2), ("agama", 5), ("status_kawin", 3), ("pendidikan", 6),
                       ("kedudukan", 5), ("alasan_datang", 3), ("diobati_sebelumnya", 2),
                       ("sistem_bayar", 5), ("alergi_obat", 2)]

    def identity_checks(self, choices, table_index=1):
        cbs = self.checkboxes(self.doc.tables[table_index]._tbl)
        total = sum(n for _, n in self.IDENTITY_GROUPS)
        if len(cbs) != total:
            raise ValueError("Tabel identitas: %d checkbox, diharapkan %d" % (len(cbs), total))
        k = 0
        for name, n in self.IDENTITY_GROUPS:
            if name in choices:
                for j in range(n):
                    self.set_cb(cbs[k + j][0], j + 1 == int(choices[name]))
            k += n

    # -- tables
    def set_cell(self, tc, value):
        lines = value if isinstance(value, list) else str(value).split("\n")
        ps = tc.findall(qn("w:p"))
        new = build_paras(ps, lines, ps[0])
        for p in ps:
            tc.remove(p)
        for p in new:
            tc.append(p)

    def table_by_label(self, ti, values):
        tbl = self.doc.tables[ti]._tbl
        done = set()
        for tr in tbl.findall(qn("w:tr")):
            tcs = tr.findall(qn("w:tc"))
            if len(tcs) < 2:
                continue
            lab = "".join(ptext(p) for p in tcs[0].findall(qn("w:p"))).strip()
            for key, v in values.items():
                if key not in done and lab.startswith(key):
                    self.set_cell(tcs[-1], v)
                    done.add(key)
                    break
        missing = set(values) - done
        if missing:
            raise KeyError("Label tabel %d tidak ditemukan: %s" % (ti, sorted(missing)))

    def table_cells(self, ti, cells):
        trs = self.doc.tables[ti]._tbl.findall(qn("w:tr"))
        for r, c, v in cells:
            self.set_cell(trs[r].findall(qn("w:tc"))[c], v)

    def table_rows(self, ti, header_rows, rows):
        """rows: list baris; tiap sel str/list, atau null = gabung (vMerge) dengan sel di atasnya."""
        tbl = self.doc.tables[ti]._tbl
        trs = tbl.findall(qn("w:tr"))
        tpls = trs[header_rows:]
        last = trs[header_rows - 1] if header_rows else None
        for tr in tpls:
            tbl.remove(tr)
        built = []
        for k, row in enumerate(rows):
            tr = copy.deepcopy(tpls[min(k, len(tpls) - 1)])
            strip_ids(tr)
            tcs = tr.findall(qn("w:tc"))
            if len(tcs) != len(row):
                raise ValueError("Tabel %d baris %d: %d sel, diberi %d" % (ti, k, len(tcs), len(row)))
            for c, (tc, v) in enumerate(zip(tcs, row)):
                tcpr = tc.find(qn("w:tcPr"))
                vm = tcpr.find(qn("w:vMerge")) if tcpr is not None else None
                if vm is not None:
                    tcpr.remove(vm)
                if v is None:
                    tcpr.append(tcpr.makeelement(qn("w:vMerge"), {}))
                    self.set_cell(tc, "")
                else:
                    nxt = rows[k + 1][c] if k + 1 < len(rows) else ""
                    if nxt is None:
                        tcpr.append(tcpr.makeelement(qn("w:vMerge"), {qn("w:val"): "restart"}))
                    self.set_cell(tc, v)
            built.append(tr)
        anchor = last
        for tr in built:
            if anchor is None:
                tbl.append(tr)
            else:
                anchor.addnext(tr)
            anchor = tr

    def bold_row(self, ti, selected_prefix):
        for tr in self.doc.tables[ti]._tbl.findall(qn("w:tr")):
            tcs = tr.findall(qn("w:tc"))
            on = "".join(ptext(p) for p in tcs[0].findall(qn("w:p"))).strip().startswith(selected_prefix)
            for r in tr.iter(qn("w:r")):
                if r.find(qn("w:rPr")) is None:
                    r.insert(0, r.makeelement(qn("w:rPr"), {}))
            # termasuk rPr penanda paragraf (pPr/rPr)
            for rpr in tr.iter(qn("w:rPr")):
                for tag in ("w:b", "w:bCs"):
                    e = rpr.find(qn(tag))
                    if e is not None:
                        rpr.remove(e)
                if on:
                    rpr.insert(0, rpr.makeelement(qn("w:b"), {}))

    def remove_images_between(self, start, end):
        bl = self.blocks()
        i = self.find_body(start)
        j = self.find_body(end, start=i + 1)
        n = 0
        for el in bl[i + 1:j]:
            for d in list(el.iter(qn("w:drawing"))):
                run = d.getparent()
                run.getparent().remove(run)
                n += 1
        self.log.append("hapus %d gambar antara %r..%r" % (n, start, end))

    def save(self, out):
        self.doc.save(out)


# --------------------------------------------------------------------- run
def run(cfg_path):
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    here = os.path.dirname(os.path.abspath(cfg_path))
    base = os.path.join(here, cfg["base_docx"]) if not os.path.isabs(cfg["base_docx"]) else cfg["base_docx"]
    out = os.path.join(here, cfg["output_docx"]) if not os.path.isabs(cfg["output_docx"]) else cfg["output_docx"]
    b = Builder(base)
    for old, new, *rest in cfg.get("subs", []):
        b.sub(old, new, all_=bool(rest and rest[0]))
    if "identity_checks" in cfg:
        b.identity_checks(cfg["identity_checks"])
    for c in cfg.get("checks", []):
        b.check_para(c["para"], c["values"], c.get("occ", 0))
    for s in cfg.get("remove_images", []):
        b.remove_images_between(*s)
    for s in cfg.get("sections", []):
        b.section(s["from"], s["to"], s["lines"], s.get("occ", 0), s.get("drop_images", True))
    for p in cfg.get("paras", []):
        b.para(p["startswith"], p["text"], p.get("occ", 0))
    for t in cfg.get("tables", []):
        op = t["op"]
        if op == "by_label":
            b.table_by_label(t["table"], t["values"])
        elif op == "rows":
            b.table_rows(t["table"], t["header_rows"], t["rows"])
        elif op == "cells":
            b.table_cells(t["table"], t["cells"])
        elif op == "bold_row":
            b.bold_row(t["table"], t["select"])
        else:
            raise ValueError("op tabel tidak dikenal: %s" % op)
    b.save(out)
    for line in b.log:
        print(" -", line)
    print("OK ->", out)


def print_map(base):
    d = docx.Document(base)
    for i, el in enumerate(d.element.body.iterchildren()):
        if el.tag == qn("w:p"):
            t = ptext(el).strip()
            if t or has_img(el):
                flags = ("N" if has_num(el) else " ") + ("C" if has_cb(el) else " ") + ("I" if has_img(el) else " ")
                print(i, "P", flags, Paragraph(el, d).style.name[:12], "|", t[:90])
        elif el.tag == qn("w:tbl"):
            print(i, "TABLE")
    for i, t in enumerate(d.tables):
        print("table", i, "rows", len(t.rows), "|", t.rows[0].cells[0].text[:40].replace("\n", " "))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("config", help="file JSON isi pasien, atau docx basis bila --map")
    ap.add_argument("--map", action="store_true", help="cetak peta anchor/tabel dari docx basis")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.map:
        print_map(a.config)
    else:
        run(a.config)
