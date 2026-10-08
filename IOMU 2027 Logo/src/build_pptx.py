"""Build the IOMU 2027 logo voting deck (palette B, 3 AI concepts)."""
import os
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMG = os.path.join(ROOT, "ai-concepts")
OUT = os.path.join(ROOT, "IOMU 2027 Logo Concepts v2.pptx")

EMERALD = RGBColor(0x21, 0x49, 0x40)
GOLD = RGBColor(0xC6, 0x9C, 0x54)
CREAM = RGBColor(0xF4, 0xE9, 0xD7)
INK = RGBColor(0x2B, 0x2B, 0x2B)
HEAD, BODY = "Georgia", "Calibri"

CONCEPTS = [
    ("1", "Healthy Worker", "iomu2027_chatgpt_c1_ribbon-figure_B.png", [
        ("Figure", "An abstract worker with arms raised: a healthy, thriving workforce"),
        ("Hard-hat head", "Occupational safety and the worker as the centre of the specialty"),
        ("Rod of Asclepius", "Medicine, forming the figure's backbone"),
        ("Parang ribbon", "Solo batik; parang stands for strength and unbroken continuity"),
        ("Kawung in the O", "Solo batik; order and integrity"),
    ]),
    ("2", "Kawung Cross", "iomu2027_chatgpt_c2_kawung-cross_B.png", [
        ("Four kawung petals", "Arranged as a medical cross: health built on Javanese heritage"),
        ("Batik engraving", "Parang pattern inside each petal"),
        ("Hard hat + rod", "Occupational safety and medicine at the centre"),
        ("Crest above the M", "Ornament inspired by the carved crest of Keraton Surakarta"),
        ("Sans-serif wordmark", "Modern, strong, highly legible at small sizes"),
    ]),
    ("3", "Gunungan", "iomu2027_chatgpt_c3_gunungan_B.png", [
        ("Gunungan", "Wayang kulit tree of life; Solo is a centre of wayang tradition"),
        ("Hard hat + rod", "Occupational safety and medicine inside the gunungan"),
        ("Batik bands", "Semen rante and parang engraving with gold scrollwork"),
        ("Kawung in the O", "Solo batik; order and integrity"),
        ("Serif wordmark", "Classic, formal, matches a scientific meeting"),
    ]),
    ("4", "Healthy Worker × Kawung type", "iomu2027_merge_c1-symbol_c2-type_B_v1.png", [
        ("Symbol from Concept 1", "Thriving worker with hard-hat head, rod of Asclepius and parang ribbon"),
        ("Type from Concept 2", "Bold geometric sans wordmark: modern and legible at small sizes"),
        ("Crest above the M", "Ornament inspired by the carved crest of Keraton Surakarta"),
        ("Gold rules", "Frame the full name and SOLO 2027"),
    ]),
]


def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color


def text(slide, x, y, w, h, s, size, color, font=BODY, bold=False, align=PP_ALIGN.LEFT, spacing=None):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = s
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.name = font
    r.font.bold = bold
    if spacing is not None:
        r.font._element.set("spc", str(spacing))
    return tb


def rule(slide, x, y, w, color=GOLD, h=Pt(2)):
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    ln.fill.solid()
    ln.fill.fore_color.rgb = color
    ln.line.fill.background()
    return ln


def footer(slide, s="Concept draft, AI-generated. The chosen logo will be redrawn as a clean vector file."):
    text(slide, Inches(0.6), Inches(7.0), Inches(12.1), Inches(0.35), s, 10, RGBColor(0x8A, 0x80, 0x70))


def main():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    # title
    s = prs.slides.add_slide(blank)
    bg(s, EMERALD)
    text(s, Inches(0.9), Inches(2.3), Inches(11.5), Inches(1.2), "IOMU 2027 Logo Concepts", 48, CREAM, HEAD)
    rule(s, Inches(0.95), Inches(3.55), Inches(2.2))
    text(s, Inches(0.9), Inches(3.8), Inches(11.5), Inches(0.6),
         "19th Indonesian Occupational Medicine Updates · Solo · PERDOKI", 20, GOLD, BODY)
    text(s, Inches(0.9), Inches(4.5), Inches(11.5), Inches(0.6),
         "Four candidates for voting · Palette: Emerald Green & Gold", 16, CREAM, BODY)

    # one slide per concept
    for num, name, img, notes in CONCEPTS:
        s = prs.slides.add_slide(blank)
        bg(s, RGBColor(0xFF, 0xFF, 0xFF))
        text(s, Inches(0.6), Inches(0.35), Inches(9), Inches(0.7), f"Concept {num} · {name}", 30, EMERALD, HEAD)
        rule(s, Inches(0.62), Inches(1.05), Inches(1.6))
        s.shapes.add_picture(os.path.join(IMG, img), Inches(0.6), Inches(1.75), width=Inches(8.8))
        # meaning panel
        panel = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.6), Inches(1.75), Inches(3.15), Inches(4.4))
        panel.fill.solid()
        panel.fill.fore_color.rgb = CREAM
        panel.line.fill.background()
        tb = s.shapes.add_textbox(Inches(9.75), Inches(1.95), Inches(2.85), Inches(4.1))
        tf = tb.text_frame
        tf.word_wrap = True
        first = True
        for k, v in notes:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_after = Pt(6)
            r1 = p.add_run()
            r1.text = k + ": "
            r1.font.bold = True
            r1.font.size = Pt(12)
            r1.font.color.rgb = EMERALD
            r1.font.name = BODY
            r2 = p.add_run()
            r2.text = v
            r2.font.size = Pt(12)
            r2.font.color.rgb = INK
            r2.font.name = BODY
        footer(s)

    # voting overview
    s = prs.slides.add_slide(blank)
    bg(s, RGBColor(0xFF, 0xFF, 0xFF))
    text(s, Inches(0.6), Inches(0.35), Inches(12), Inches(0.7), "Vote: which logo for IOMU 2027?", 30, EMERALD, HEAD)
    rule(s, Inches(0.62), Inches(1.05), Inches(1.6))
    w = Inches(2.95)
    for i, (num, name, img, _) in enumerate(CONCEPTS):
        x = Inches(0.6) + i * (w + Inches(0.13))
        s.shapes.add_picture(os.path.join(IMG, img), x, Inches(2.6), width=w)
        text(s, x, Inches(4.25), w, Inches(0.8), f"{num} · {name}", 15, EMERALD, HEAD, align=PP_ALIGN.CENTER)
    footer(s)

    prs.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
