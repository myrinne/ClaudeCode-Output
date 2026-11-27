"""Recolour the vendor techmeet deck IN PLACE, touching only fills, lines and text colours, never the text.
Applies to the cream content slides (background EDEAE7) built from Template 3; cover, closing and her own
picture slides are left alone. Prints a text fingerprint before and after so the words are proven unchanged.
Run: python recolor_techmeet.py "Techmeet Vendor - Hari H.pptx" """
import hashlib
import sys
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

MAROON, ORANGE, PINK, PALE_PINK, CREAM_NA, WHITE = "6C202D", "FE702F", "FDC6E9", "FCE3F0", "F7EFE6", "FFFFFF"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def fingerprint(prs):
    parts = []
    for i, s in enumerate(prs.slides):
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text:
                parts.append(f"{i}:{sh.text_frame.text}")
            if getattr(sh, "has_table", False) and sh.has_table:
                parts += [f"{i}:{c.text}" for r in sh.table.rows for c in r.cells]
    return hashlib.sha1("\n".join(parts).encode()).hexdigest(), len(parts)


def bg_colour(slide):
    bg = slide._element.cSld.find(qn("p:bg"))
    if bg is None:
        return None
    v = bg.xpath(".//a:srgbClr/@val")
    return v[0] if v else None


def fill_hex(el):
    v = el.xpath("./a:solidFill/a:srgbClr/@val") if el is not None else []
    return v[0] if v else None


def set_cell_fill(cell, hexc):
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor.from_string(hexc)


def colour_runs(tf, hexc):
    for p in tf.paragraphs:
        for r in p.runs:
            r.font.color.rgb = RGBColor.from_string(hexc)


def main(path):
    prs = Presentation(path)
    before = fingerprint(prs)
    n = {"slides": 0, "tables": 0, "kickers": 0, "rules": 0, "chevrons": 0, "arrows": 0, "accents": 0}
    for slide in prs.slides:
        if bg_colour(slide) != "EDEAE7":
            continue
        n["slides"] += 1
        title = None
        for sh in list(slide.shapes):
            # tables: maroon header row with white text, pink highlighted rows, warm N/A cells
            if getattr(sh, "has_table", False) and sh.has_table:
                n["tables"] += 1
                tbl = sh.table
                for c in tbl.rows[0].cells:
                    set_cell_fill(c, MAROON)
                    colour_runs(c.text_frame, WHITE)
                for r in list(tbl.rows)[1:]:
                    for c in r.cells:
                        f = fill_hex(c._tc.tcPr) if c._tc.tcPr is not None else None
                        if f in ("F7E3D8", "E4ECF5"):
                            set_cell_fill(c, PALE_PINK)
                        elif f == "F2F2F2":
                            set_cell_fill(c, CREAM_NA)
                continue
            if sh.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                spPr = sh._element.spPr
                fill = fill_hex(spPr)
                ast = sh.auto_shape_type
                # kicker chip: unfilled rectangle with a maroon outline near the top right
                if ast == MSO_SHAPE.RECTANGLE and fill is None and sh.top < Inches(1.0) and sh.has_text_frame and sh.text_frame.text:
                    sh.fill.solid()
                    sh.fill.fore_color.rgb = RGBColor.from_string(MAROON)
                    sh.line.fill.background()
                    colour_runs(sh.text_frame, PINK)
                    n["kickers"] += 1
                elif ast in (MSO_SHAPE.CHEVRON, MSO_SHAPE.PENTAGON):
                    if fill == "D9D9D9":          # steps that were gray
                        sh.fill.solid()
                        sh.fill.fore_color.rgb = RGBColor.from_string(PINK)
                    elif fill == MAROON:          # the one highlighted step
                        sh.fill.solid()
                        sh.fill.fore_color.rgb = RGBColor.from_string(ORANGE)
                    n["chevrons"] += 1
                elif ast == MSO_SHAPE.ISOSCELES_TRIANGLE or ast == MSO_SHAPE.FLOWCHART_MERGE:
                    sh.fill.solid()
                    sh.fill.fore_color.rgb = RGBColor.from_string(ORANGE)
                    n["arrows"] += 1
            # column-heading rules (maroon connectors) -> thicker orange
            if sh.shape_type == MSO_SHAPE_TYPE.LINE or sh._element.tag == qn("p:cxnSp"):
                ln = sh._element.spPr.find(qn("a:ln"))
                col = ln.xpath("./a:solidFill/a:srgbClr/@val") if ln is not None else []
                if col and col[0] == MAROON:
                    sh.line.color.rgb = RGBColor.from_string(ORANGE)
                    sh.line.width = Pt(3)
                    n["rules"] += 1
            if sh.shape_id == 26 and sh.has_text_frame:
                title = sh
        # an orange accent bar to the left of the slide title, as in the template's orange bands
        if title is not None:
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), title.top + Inches(0.12), Inches(0.2), Inches(1.2))
            bar.fill.solid()
            bar.fill.fore_color.rgb = RGBColor.from_string(ORANGE)
            bar.line.fill.background()
            n["accents"] += 1
    after = fingerprint(prs)
    assert before == after, "text changed!"
    prs.save(path)
    print(n)
    print("text fingerprint unchanged:", before[0][:12], before[1], "text items")


if __name__ == "__main__":
    main(sys.argv[1])
