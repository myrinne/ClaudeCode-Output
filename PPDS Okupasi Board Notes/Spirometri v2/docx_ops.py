"""Small helpers to edit Catatan_Spirometri.docx in place with python-docx.

Blocks are tuples:
  ("h1"|"h2"|"h3", text)      heading in the document's own heading styles
  ("p", text)                 Normal paragraph; **bold** spans allowed
  ("b", text) / ("n", text)   List Bullet / List Number
  ("pearl"|"flag"|"src"|"new"|"lafaz", text)  coloured callouts like the original
  ("table", [[hdr...], [row...], ...])        Table Grid, bold header row
  ("img", path, width_cm) / ("cap", text)    picture + grey italic caption
"""
import copy
import re
from docx.shared import Cm, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from docx.table import Table

CALLOUT = {
    "pearl": ("🟢 CLINICAL PEARL: ", "1E7D32", True),
    "flag": ("🔴 RED FLAG: ", "C62828", True),
    "src": ("⚠️ CATATAN SUMBER: ", "E67E22", False),
    "new": ("🆕 BARU v2 — ", "1565C0", False),
    "fix": ("✏️ DIKOREKSI v2 — ", "6A1B9A", False),
    "lafaz": ("🎤 LAFAZ: ", "1F4E79", False),
}
HSTYLE = {"h1": "Heading 1", "h2": "Heading 2", "h3": "Heading 3"}


def _runs(par, text, color=None, italic=False):
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        bold = part.startswith("**") and part.endswith("**")
        r = par.add_run(part[2:-2] if bold else part)
        r.bold = bold or None
        if italic:
            r.italic = True
        if color:
            r.font.color.rgb = RGBColor.from_string(color)


class Cursor:
    """Inserts new block-level elements after a given element, in order."""

    def __init__(self, doc, after_el):
        self.doc = doc
        self.el = after_el

    def _place(self, new_el):
        self.el.addnext(new_el)
        self.el = new_el

    def _para(self, style=None):
        p = self.doc.add_paragraph(style=style)  # appended at end, then moved
        self._place(p._p)
        return p

    def add(self, blocks):
        for b in blocks:
            kind = b[0]
            if kind in HSTYLE:
                p = self._para(HSTYLE[kind])
                p.add_run(b[1])
            elif kind == "p":
                _runs(self._para(), b[1])
            elif kind == "b":
                _runs(self._para("List Bullet"), b[1])
            elif kind == "n":
                _runs(self._para("List Number"), b[1])
            elif kind in CALLOUT:
                label, color, body_colored = CALLOUT[kind]
                p = self._para()
                r = p.add_run(label)
                r.bold = True
                r.font.color.rgb = RGBColor.from_string(color)
                _runs(p, b[1], color=color if body_colored else None,
                      italic=kind in ("src", "new", "fix"))
            elif kind == "table":
                self._table(b[1])
            elif kind == "img":
                p = self._para()
                p.alignment = 1
                p.add_run().add_picture(str(b[1]), width=Cm(b[2]))
            elif kind == "cap":
                p = self._para()
                p.alignment = 1
                r = p.add_run(b[1])
                r.italic = True
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor.from_string("555555")
            else:
                raise ValueError(kind)
        return self

    def _table(self, rows):
        ncol = max(len(r) for r in rows)
        t = self.doc.add_table(rows=0, cols=ncol)
        t.style = self.doc.styles["Table Grid"]
        for i, row in enumerate(rows):
            cells = t.add_row().cells
            for j in range(ncol):
                txt = row[j] if j < len(row) else ""
                par = cells[j].paragraphs[0]
                if i == 0:
                    r = par.add_run(txt)
                    r.bold = True
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:color"), "auto")
                    shd.set(qn("w:fill"), "DCE6F1")
                    cells[j]._tc.get_or_add_tcPr().append(shd)
                else:
                    _runs(par, txt)
        self._place(t._tbl)
        # spacer paragraph after a table, like the original layout
        self._para()


def body_items(doc):
    """Yield (kind, obj) for every block in body order."""
    for el in doc.element.body.iterchildren():
        if el.tag == qn("w:p"):
            yield "p", Paragraph(el, doc)
        elif el.tag == qn("w:tbl"):
            yield "t", Table(el, doc)


def find_par(doc, startswith, style=None, nth=0):
    hits = [p for p in doc.paragraphs
            if p.text.strip().startswith(startswith) and (style is None or p.style.name == style)]
    if len(hits) <= nth:
        raise KeyError(f"anchor not found: {startswith!r}")
    return hits[nth]


def section_end(doc, heading_par):
    """Last block element before the next heading of same or higher level."""
    lvl = int(heading_par.style.name.split()[-1])
    started = False
    last = heading_par._p
    for kind, obj in body_items(doc):
        el = obj._p if kind == "p" else obj._tbl
        if el is heading_par._p:
            started = True
            continue
        if not started:
            continue
        if kind == "p" and obj.style.name.startswith("Heading"):
            try:
                l2 = int(obj.style.name.split()[-1])
            except ValueError:
                l2 = 9
            if l2 <= lvl:
                break
        last = el
    return last


def set_text(par, new_text, keep_prefix_runs=0):
    """Replace a paragraph's text, keeping the formatting of its runs.

    keep_prefix_runs: number of leading runs (e.g. a bold callout label) to keep.
    """
    runs = par.runs
    for r in runs[keep_prefix_runs + 1:]:
        r._r.getparent().remove(r._r)
    target = runs[keep_prefix_runs] if len(runs) > keep_prefix_runs else par.add_run("")
    target.text = new_text


def replace_in(par, old, new):
    """Replace text inside one paragraph; works when old sits in a single run,
    otherwise collapses the paragraph text into the first non-label run."""
    for r in par.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return True
    full = par.text
    if old not in full:
        return False
    # collapse: keep run 0 if it is a bold label that does not contain old
    runs = par.runs
    keep = 1 if (runs and runs[0].bold and old not in runs[0].text and len(runs) > 1) else 0
    rest = "".join(r.text for r in runs[keep:])
    set_text(par, rest.replace(old, new), keep_prefix_runs=keep)
    return True


def delete(el):
    el.getparent().remove(el)
