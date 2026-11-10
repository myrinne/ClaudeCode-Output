"""Layout for the navy/orange Canva template ('Untitled design (1).pptx', 13 slides, 'Annual Report 2026').

Same content, numbers and checks as mcu_ppt.Deck (the teal template); only the slide layouts differ.
Chosen automatically by mcu_ppt.py when the template's 2nd slide says 'Table of Contents' (Vidya 2026-11-10, PT. SKP).

Template slides used: 1 cover, 2 contents (11 slots), 3 topic (title left, navy + orange panels right),
4 company profile, 6 doughnut + text (orange panel), 8 two recommendation cards, 10 summary cards and, cleaned,
the plain navy slide for tables/charts, 12 wellness, 13 closing. People photos become the cover's building photo.
"""
from __future__ import annotations

import re
from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

import mcu_ppt as M
from mcu_ppt import (BODY_FONT, TITLE_FONT, Deck, add_bar, add_box, add_doughnut, fit_size, fmt_date, fmt_n, fmt_pct,
                     nice, remove, set_text, set_title, shape_by_id, to_building)

NAVY, ORANGE, WHITE, LIGHT, PEACH = "004561", "F9823E", "FFFFFF", "EEF3F6", "FFE3D1"
PALETTE_NAVY = [NAVY, ORANGE, "6F9FB5", "FDB98E", "A3A3A3", "2E6E8A", "C96A2E", "D0DDE4"]
M.FONT_MAP.update({"Gordita Bold": "Arial Black", "Gordita": "Arial"})
# template slide numbers
N_COVER, N_TOC, N_TOPIC, N_PROFILE, N_SPLIT2, N_DONUT, N_QUOTE, N_TWOCARD, N_TIMELINE, N_CARDS, N_LESSON, N_TWOPANEL, N_THANKS = range(1, 14)
# old layout (teal template) content band -> navy plain slide content band
Y0_OLD, Y1_OLD, Y0_NEW, Y1_NEW = 3.0, 10.6, 4.25, 10.95  # band starts below title + subtitle (PowerPoint check 2026-11-10)
K = (Y1_NEW - Y0_NEW) / (Y1_OLD - Y0_OLD)


def ty(y):
    return Y0_NEW + (y - Y0_OLD) * K


def is_navy_template(prs) -> bool:
    if len(prs.slides) < 13:
        return False
    s2 = prs.slides[1]
    return any(sh.has_text_frame and "Table of Contents" in sh.text_frame.text for sh in s2.shapes)


def add_table(slide, header, rows, x, y, w, row_h, col_fracs, hdr_pt, body_pt, left_cols=(1,)):
    """Native table: orange header, white/light rows, navy text."""
    n_r, n_c = len(rows) + 1, len(header)
    gf = slide.shapes.add_table(n_r, n_c, Inches(x), Inches(y), Inches(w), Inches(row_h * n_r))
    tbl = gf.table
    tbl._tbl.tblPr.set("bandRow", "0")
    tot = sum(col_fracs)
    for j, f in enumerate(col_fracs):
        tbl.columns[j].width = Emu(int(Inches(w) * f / tot))
    for i, vals in enumerate([header] + rows):
        tbl.rows[i].height = Inches(row_h)
        for j in range(n_c):
            v = vals[j] if j < len(vals) else ""
            c = tbl.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor.from_string(ORANGE if i == 0 else (WHITE if i % 2 else LIGHT))
            c.margin_left = c.margin_right = Inches(0.08)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = c.text_frame.paragraphs[0]
            c.text_frame.word_wrap = True
            r = p.add_run()
            r.text = "" if v is None else str(v)
            r.font.size = Pt(hdr_pt if i == 0 else body_pt)
            r.font.bold = i == 0
            r.font.name = BODY_FONT
            r.font.color.rgb = RGBColor.from_string(WHITE if i == 0 else NAVY)
            p.alignment = PP_ALIGN.LEFT if (j in left_cols and i > 0) else PP_ALIGN.CENTER
    return gf


class DeckNavy(Deck):
    MAX_FIT_BOXES = 8  # the text box beside the doughnut has room for every status category
    def setup_template(self):
        self.use_building(self.tpl[N_COVER - 1], 14)  # skyline photo on the cover

    def done(self, slide, title):
        for sh in slide.shapes:  # template company label -> this company
            if sh.has_text_frame and "Ginyard" in sh.text_frame.text:
                set_text(sh, self.company)
                sh.width = Inches(7.0)
        super().done(slide, title)

    # ------------------------------------------------------------ building blocks
    def plain(self, title, subtitle=None):
        """Navy slide 10 without its cards: title on top, content band y 3.85-10.95."""
        s = self.new(N_CARDS)
        remove(s, 9, 10, 11, 12, *range(16, 26))
        t = shape_by_id(s, 14)
        # title well below the logo row (1.74-2.36"): PowerPoint draws it higher than LibreOffice
        t.left, t.top, t.width, t.height = Inches(1.56), Inches(2.65), Inches(17.2), Inches(0.95)
        t.text_frame.vertical_anchor = MSO_ANCHOR.TOP
        set_title(t, title, 42, 26)
        if subtitle:
            add_box(s, 1.56, 3.62, 17.2, 0.5, subtitle, 16, color=ORANGE)
        return s

    def toc_items(self):
        items = []
        for x in self.k["daftar_isi"]:
            if x == "Status Kelaikan Kerja":
                items.append(self.judul_fit if self.judul_fit != "Status kelaikan kerja" else x)
                if self.S.meta["blok"].get("pak_dugaan"):
                    items.append("Dugaan PAK")  # 11 slots here, so PAK gets its own line
            else:
                items.append(x)
        return items

    # ------------------------------------------------------------ slides
    def cover(self):
        s = self.new(N_COVER)
        d1, d2 = self.S.periode()
        year = str(d2.year) if hasattr(d2, "year") else ""
        # her PT. SKP edit: one two-line title box, the year right under it
        t = shape_by_id(s, 23)
        t.width = Inches(8.4)
        set_text(t, ["ANALISA", "HASIL MCU"], size=fit_size("HASIL MCU", 8.2, 1.0, 62, 40, 0.95, 1.0), font=TITLE_FONT)
        remove(s, 22)
        yr = shape_by_id(s, 30)
        yr.top = Inches(4.08)
        set_text(yr, year, font=TITLE_FONT)
        set_text(shape_by_id(s, 36), self.company, size=24, bold=True)
        set_text(shape_by_id(s, 33), "Periode MCU:")
        per = shape_by_id(s, 31)
        per.height, per.width = Inches(0.8), Inches(2.75)
        set_text(per, f"{fmt_date(d1)} s/d\n{fmt_date(d2)}", size=17)
        set_text(shape_by_id(s, 34), "Disusun oleh:")
        pres = shape_by_id(s, 32)
        if self.k.get("penyaji"):
            pres.width = Inches(3.4)
            set_text(pres, self.k["penyaji"], size=18)
        else:
            remove(s, 32)  # she deletes the placeholder
        self.expect(s, fmt_date(d1))
        self.done(s, "Sampul")

    def toc(self, items):
        s = self.new(N_TOC)
        set_title(shape_by_id(s, 19), "DAFTAR ISI", 80, 40)
        slots = [21, 23, 28, 30, 22, 24, 29, 31, 32, 33, 34]
        nums = [20, 25, 26, 27, 12, 13, 14, 15, 7, 8, 9]
        for i, sid in enumerate(slots):
            if i < len(items):
                sh = shape_by_id(s, sid)
                sh.width = Inches(3.55)
                set_text(sh, items[i], size=fit_size(items[i], 3.5, 0.32, 17, 12, 0.55, 1.0))
            else:
                remove(s, sid, nums[i])
        self.done(s, "Daftar isi")

    def card(self, s, x, y, w, h, head, lines, size=24, fill=WHITE):
        box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor.from_string(fill)
        box.line.fill.background()
        box.shadow.inherit = False
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.75))
        bar.fill.solid()
        bar.fill.fore_color.rgb = RGBColor.from_string(ORANGE)
        bar.line.fill.background()
        bar.shadow.inherit = False
        add_box(s, x + 0.3, y + 0.1, w - 0.6, 0.6, head, 24, color=WHITE, bold=True, font=BODY_FONT)
        add_box(s, x + 0.3, y + 1.0, w - 0.6, h - 1.2, lines, size, color=NAVY)

    def profil(self, groups):
        # the template's company-overview slide has tiny list boxes; two plain cards read better
        s = self.plain("PROFIL PERUSAHAAN")
        d1, d2 = self.S.periode()
        self.card(s, 1.3, 4.35, 8.6, 5.6, "Data MCU",
                  [[("Perusahaan: ", True), (self.company, False)],
                   [("Peserta MCU: ", True), (f"{fmt_n(self.N)} pekerja", False)],
                   [("Periode MCU: ", True), (f"{fmt_date(d1)} s/d {fmt_date(d2)}", False)]], 26)
        self.card(s, 10.4, 4.35, 8.6, 5.6, "Pengelompokan",
                  [[(f"Jumlah {self.S.labels.get(k, k).lower()}: ", True), (str(len(rows)), False)] for k, rows in groups], 26)
        self.done(s, "Profil perusahaan")

    def ringkasan(self):
        s = self.new(N_CARDS)
        set_title(shape_by_id(s, 14), "RINGKASAN", 80, 40)
        fit = self.S.block("kelaikan_fitness")
        top = self.S.block("S4_top_ten")
        d1, d2 = self.S.periode()
        cards = [("Peserta", fmt_n(self.N), f"peserta MCU {fmt_date(d1)} s/d {fmt_date(d2)}")]

        def fit_card(r):
            lab = nice(r["B"]) if self.judul_fit == "Status kelaikan kerja" else f"{self.judul_fit} {nice(r['B'])}"
            return (nice(r["B"]), fmt_pct(r["D"]), f"{lab} ({fmt_n(r['C'])} pekerja)")
        cards += [fit_card(r) for r in fit[:2]]
        if top:
            cards.append(("Terbanyak", fmt_pct(top[0]["D"]), f"temuan terbanyak: {top[0]['B']} ({fmt_n(top[0]['C'])} pekerja)"))
        # the template's 5th "card" is a stack of narrow strips, so: 4 cards, centred on the slide
        remove(s, 11, 12, 20, 25)
        shift = Inches((20.0 - 13.15) / 2 - 1.64)
        for sid in (10, 16, 17, 18, 19, 21, 22, 23, 24):
            sh = shape_by_id(s, sid)
            sh.left = sh.left + shift
        for i, (head, big, small) in enumerate(cards[:4]):
            set_text(shape_by_id(s, 16 + i), head, size=fit_size(head, 1.9, 0.3, 18, 12, 0.6, 1.0))
            body = shape_by_id(s, 21 + i)
            body.top, body.height = Inches(6.75), Inches(2.85)  # below the label circle's ring (ends ~6.6" in PowerPoint)
            body.left, body.width = body.left + Inches(0.15), body.width - Inches(0.25)  # off the card's edge
            set_text(body, [[(big, True)], [(small, False)]], size=None, align="l")
            body.text_frame.vertical_anchor = MSO_ANCHOR.TOP  # template boxes are centred: numbers rose into the circle
            ps = body.text_frame.paragraphs
            for r in ps[0].runs:
                r.font.size = Pt(fit_size(big, 2.6, 0.8, 40, 28, 0.62, 1.0))
            for p in ps[1:]:
                for r in p.runs:
                    r.font.size = Pt(fit_size(small, 2.55, 2.4, 19, 13, 0.55, 1.3))
            self.expect(s, big)
        self.done(s, "Ringkasan eksekutif")

    def segments(self, title, cats, vals, boxes, chart_title=None):
        s = self.new(N_DONUT)
        set_title(shape_by_id(s, 18), title, 72, 36)
        remove(s, 16, 17, 19, 20, 21)
        gf = add_doughnut(s, cats, vals, 0.78, 5.0, 8.54, 5.7, size=16, fill=WHITE, palette=PALETTE_NAVY, text_color=NAVY)
        if len(cats) > 3:  # many categories (PT. KED status): legend at the side, smaller, so the ring keeps its size
            from pptx.enum.chart import XL_LEGEND_POSITION
            gf.chart.legend.position = XL_LEGEND_POSITION.RIGHT
            gf.chart.legend.font.size = Pt(12)
            gf.chart.plots[0].data_labels.font.size = Pt(12)
        self.chart_checks.append((len(self.prs.slides) - self.n_orig, vals))
        body = shape_by_id(s, 22)
        body.left, body.top, body.width, body.height = Inches(10.0), Inches(4.9), Inches(8.9), Inches(5.8)
        txt = "\n".join(boxes)
        set_text(body, [[(b, False)] for b in boxes], size=fit_size(txt, 8.7, 5.6, 24, 14, 0.52, 1.6), space_after=14, align="l")
        self.done(s, title)
        return s

    def table_slide(self, title, header, rows, col_fracs, x=1.0, y=3.0, w=17.2, row_h=0.55, hdr_pt=18, body_pt=17,
                    left_cols=(1,), chart=None, subtitle=None):
        s = self.plain(title, subtitle)
        add_table(s, header, rows, x, ty(y), w, row_h * K, col_fracs, max(11, round(hdr_pt * K)), max(11, round(body_pt * K)), left_cols)
        if chart:
            cats, vals, cx, cy, cw, chh = chart
            add_bar(s, cats, vals, cx, ty(cy), cw, chh * K, size=15, color=ORANGE, fill=WHITE)
            self.chart_checks.append((len(self.prs.slides) - self.n_orig, vals))
        for r in rows:
            for v in r:
                if v not in (None, "") and re.search(r"\d", str(v)):
                    self.expect(s, str(v))
        self.done(s, title)
        return s

    def kebiasaan(self, hab):
        boxes = [f"{fmt_n(r['C'])} dari {fmt_n(self.N)} pekerja ({fmt_pct(r['D'])})" for lab, r, _ in hab]
        s = self.plain("KEBIASAAN PEKERJA")
        add_bar(s, [f"{lab} ({fmt_pct(r['D'])})" for lab, r, _ in hab], [r["C"] for _, r, _ in hab], 1.2, 4.3, 10.0, 6.5,
                title="Jumlah pekerja", size=17, color=ORANGE, fill=WHITE)
        self.chart_checks.append((len(self.prs.slides) - self.n_orig, [r["C"] for _, r, _ in hab]))
        paras = []
        for (lab, _, _), b in zip(hab, boxes):
            paras += [[(f"{lab}: ", True)], [(b, False)], [("", False)]]
        add_box(s, 11.8, 4.5, 7.2, 6.2, paras[:-1], 24, color=WHITE)
        for b in boxes:
            self.expect(s, b)
        self.done(s, "Kebiasaan pekerja")

    def topik(self, cfg):
        tp = cfg["topik"]
        key = next((k for k in self.S.meta["blok"] if re.fullmatch(r"S\d+_" + re.escape(tp), k) or k == f"Topik_{tp}"), None)
        rows = self.S.block(key) if key else []
        if not rows:
            return
        items = [r for r in rows if not str(r["B"]).startswith(("Salah satu", "Tanpa"))]
        anyr = next(r for r in rows if str(r["B"]).startswith("Salah satu"))
        s = self.new(N_TOPIC)
        t = shape_by_id(s, 27)
        t.top, t.height = Inches(2.55), Inches(2.4)
        set_title(t, cfg["judul"], 60, 28)
        remove(s, 5, 6, 9, 10, 20)  # photo circle: the chart goes there
        top = sorted([r for r in items if (r["C"] or 0) > 0], key=lambda r: -r["C"])
        sent = f"Dari {fmt_n(self.N)} peserta MCU, {fmt_n(anyr['C'])} pekerja ({fmt_pct(anyr['D'])}) memiliki temuan {tp.lower()}"
        if top:
            sent += ", terbanyak " + "; ".join(f"{r['B'].lower() if r['B'][1:].islower() else r['B']} {fmt_n(r['C'])} pekerja ({fmt_pct(r['D'])})" for r in top[:2])
        sent += "."
        self.expect(s, fmt_pct(anyr["D"]))
        set_text(shape_by_id(s, 28), "Ringkasan temuan")
        b1 = shape_by_id(s, 26)
        b1.height = Inches(3.3)
        set_text(b1, [[(sent, True)]], size=fit_size(sent, 8.1, 3.2, 24, 14, 0.52, 1.4), align="l")
        set_text(shape_by_id(s, 29), "Edukasi")
        b2 = shape_by_id(s, 32)
        b2.height = Inches(3.75)
        edu = "\n".join(cfg["edukasi"])
        set_text(b2, [[(e, False)] for e in cfg["edukasi"]], size=fit_size(edu, 8.1, 3.6, 20, 11, 0.5, 1.45), space_after=6, align="l")
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
        add_bar(s, cats, vals, 0.9, 5.15, 8.6, 5.75, title=ctitle, size=13, color=ORANGE, fill=WHITE)
        self.chart_checks.append((len(self.prs.slides) - self.n_orig, vals))
        self.done(s, cfg["judul"])

    def place_images(self, s, files, area, captions=None, cap_h=0.9):
        """Fit pictures side by side inside area (x, y, w, h), keeping their aspect."""
        from PIL import Image
        ax, ay, aw, ah = area
        gap = 0.6
        n = len(files)
        aspects = [(lambda wh: wh[0] / wh[1])(Image.open(f).size) for f in files]
        weights = [min(max(a, 0.7), 2.5) for a in aspects]
        free = aw - gap * (n - 1)
        hh = ah - (cap_h if captions else 0)
        sx = ax
        for i, f in enumerate(files):
            slot_w = free * weights[i] / sum(weights)
            w = min(slot_w, hh * aspects[i])
            h = w / aspects[i]
            x = sx + (slot_w - w) / 2
            y = ay + (hh - h) / 2
            pic = s.shapes.add_picture(str(f), Inches(x), Inches(y), Inches(w), Inches(h))
            if captions:
                pic._element.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr").set("descr", captions[i])
                add_box(s, sx, y + h + 0.12, slot_w, cap_h, captions[i], 16, color=WHITE, align="ctr")
            sx += slot_w + gap

    def aset_slide(self, entry, folder: Path):
        s = self.plain(entry["judul"])
        imgs = entry["gambar"]
        self.place_images(s, [folder / g["file"] for g in imgs], (1.4, 4.25, 17.2, 6.65),
                          [g.get("keterangan", "") for g in imgs])
        self.done(s, entry["judul"])

    def rekomendasi(self, recs):
        # the template's two-card slide has an orange circle baked into each card image that the long texts ran into,
        # so recommendations use plain cards (same look as the profile slide)
        for i in range(0, len(recs), 2):
            s = self.plain("REKOMENDASI INDIVIDU")
            for j in range(2):
                if i + j < len(recs):
                    text, basis = recs[i + j]
                    full = text + "\n" + basis
                    self.card(s, (1.3, 10.4)[j], 4.3, 8.6, 6.5, f"Rekomendasi {i + j + 1}", [[(text, False)], [(basis, True)]],
                              fit_size(full, 7.8, 5.1, 22, 13, 0.52, 1.5))
            self.done(s, "Rekomendasi individu")

    def wellness(self):
        w = self.k["wellness"]
        s = self.new(N_TWOPANEL)
        set_title(shape_by_id(s, 11), w["judul"], 60, 30)
        shape_by_id(s, 11).width = Inches(17.0)
        set_text(shape_by_id(s, 18), "Tujuan")
        set_text(shape_by_id(s, 27), "Program")
        b1 = shape_by_id(s, 30)
        set_text(b1, w["pengantar"], size=fit_size(w["pengantar"], 7.8, 3.3, 24, 14, 0.5, 1.4), align="l")
        items = [f"{i}. {b}" for i, b in enumerate(w["butir"], 1)]
        set_text(shape_by_id(s, 31), [[(x, False)] for x in items], size=fit_size("\n".join(items), 8.2, 3.3, 22, 13, 0.5, 1.4), space_after=4, align="l")
        self.done(s, "Rekomendasi program wellness")

    def hra(self):
        h = self.k["hra"]
        s = self.plain(h["judul"])
        teks = h["teks"] if isinstance(h["teks"], str) else "\n".join(h["teks"])
        pics = (self.aset or {}).get("hra_gambar", [])
        if pics:
            add_box(s, 1.56, 4.3, 8.3, 3.0, teks, fit_size(teks, 8.2, 2.9, 22, 13, 0.5, 1.4), color=WHITE)
            files = [self.aset_dir / g["file"] for g in pics]
            self.place_images(s, files[:1], (10.3, 4.25, 9.2, 6.65))
            if len(files) > 1:
                self.place_images(s, files[1:], (1.56, 7.45, 8.3, 3.45))
        else:
            add_box(s, 1.56, 4.3, 17.0, 6.4, teks, 26, color=WHITE)
        self.done(s, "Health risk assessment")

    def wellness_overview(self):
        w = self.k.get("wellness_overview")
        if not w:
            return
        s = self.plain(w["judul"])
        pos = [(1.3, 4.3), (1.3, 6.5), (1.3, 8.7), (10.3, 4.3), (10.3, 6.5)]
        for k, card in enumerate(w["kartu"][:5]):
            x, y = pos[k]
            hgt = 2.0 if k != 2 else 2.2
            box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(8.4), Inches(hgt))
            box.fill.solid()
            box.fill.fore_color.rgb = RGBColor.from_string((WHITE, PEACH)[k % 2])
            box.line.fill.background()
            box.shadow.inherit = False
            add_box(s, x + 0.3, y + 0.15, 7.8, hgt - 0.25, [[(card["judul"], True)], [(card["teks"], False)]],
                    fit_size(card["judul"] + "\n" + card["teks"], 7.7, hgt - 0.3, 20, 13, 0.5, 1.5), color=NAVY)
        self.done(s, w["judul"])

    def penutup(self):
        s = self.new(N_THANKS)
        set_title(shape_by_id(s, 15), "TERIMA KASIH", 96, 50)  # 110pt ran into the orange ring
        pill = shape_by_id(s, 25)
        set_text(pill, self.company, size=fit_size(self.company, 4.4, 0.45, 26, 14, 0.6, 1.0))
        d1, d2 = self.S.periode()
        remove(s, 18, 30, 31)  # web / address icons
        for sid, txt, bold in ((29, "Disusun oleh:", True), (28, self.k.get("penyaji") or "", False),
                               (27, "Periode MCU:", True), (26, f"{fmt_date(d1)} s/d {fmt_date(d2)}", False)):
            if sid == 28 and not self.k.get("penyaji"):
                remove(s, 28)  # no placeholder text (her edit)
                continue
            sh = shape_by_id(s, sid)
            sh.left, sh.width = Inches(1.70), Inches(7.0)
            set_text(sh, txt, bold=bold)
        to_building(s, 9, self.building, self.building_aspect)
        self.done(s, "Penutup")
