"""Build the fun-run posters as A3 LANDSCAPE (420 x 297 mm), live text, Canva-importable.

Layout per poster: left text column + right illustration slice (one clinician station).
Content follows her Canva edits (RSCM 107th logo, no footer band, subtitles on 1 and 3,
"VAKSINASI & Return To Work").

usage: python make_a3_landscape.py <rscm-logo-with-black-bg.png>
output: concept-fun-run-a3-landscape.html + 'Fun Run A3 Landscape - EDITABLE (Canva).pdf' (+ single-page PDFs)
"""
import sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

here = Path(__file__).parent
img_dir = here / "images"

# 1) logo: key out the black background -> transparent PNG
src_logo = Path(sys.argv[1]) if len(sys.argv) > 1 else img_dir / "rscm-107-black-bg.png"
logo_out = img_dir / "rscm-107.png"
if src_logo.exists():
    im = Image.open(src_logo).convert("RGB")
    px = im.load()
    out = Image.new("RGBA", im.size)
    po = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            a = max(r, g, b) / 255.0
            al = min(1.0, a * 2.4)
            if al < 0.02:
                po[x, y] = (0, 0, 0, 0)
            else:
                f = 1.0 / max(a, 1e-3)
                po[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), int(al * 255))
    out.save(logo_out)

# 2) one 4x-upscaled slice per poster (run upscale_classical.py first) -> small, sharp backgrounds
big = Image.open(img_dir / "corridor-long-4x.png").convert("RGB")
for k in range(4):
    sl = big.crop((k * 543 * 4, 90 * 4, (k + 1) * 543 * 4, 660 * 4))
    sl.save(img_dir / f"a3-slice-{k+1}.jpg", quality=92, optimize=True)
big.close()

PAGE_W, PAGE_H = 1588, 1123           # CSS px for 420 x 297 mm
PANEL_W = 518                         # left text column
SCALE = PAGE_H / 570.0                # source rows 90..660 -> full page height
SLICE = 543 * SCALE                   # one quarter of the 2172 px wide corridor image

posters = [
    dict(word="LARI", sub="RUTE PERAWATAN LENGKAP DI SATU ATAP", km="KM 1", name="ORTOPEDI",
         title="ORTOPEDI", text="Nyeri lutut, pergelangan kaki, atau punggung? Periksakan sebelum mengganggu lari berikutnya.",
         top="a", card="c1"),
    dict(word="KUAT.", sub="", km="KM 2", name="REHABILITASI",
         title="REHABILITASI", text="Kembali berlari dengan aman: cara jalan, kekuatan, dan program pemulihan bertahap.",
         top="b", card="c2"),
    dict(word="PULIH", sub="CEGAH SEBELUM TERJADI", km="KM 3", name="VAKSINASI",
         title="VAKSINASI &amp; Return To Work", text="Tetap terlindungi untuk latihan, perjalanan, dan pekerjaan.",
         top="a", card="c3"),
    dict(word="LEBIH<br>KUAT.", sub="", km="KM 4", name="AKUPUNKTUR",
         title="AKUPUNKTUR", text="Redakan otot pegal dan nyeri yang tak kunjung hilang.",
         top="b", card="c4"),
]

pages = []
for i, p in enumerate(posters):
    dots = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(4))
    sub = f'<div class="sub">{p["sub"]}</div>' if p["sub"] else ""
    pages.append(f"""
<section class="page">
  <div class="img" style="background:url(images/a3-slice-{i+1}.jpg) 0 0/100% 100% no-repeat"></div>
  {'<div class="patch">Jadwal<br>Vaksinasi</div>' if i == 2 else ''}
  <div class="bar"></div>
  <div class="panel">
    <div class="top {p['top']}">
      <div class="logo"><img src="images/rscm-107.png" alt="107th RSCM"></div>
      <div class="word">{p['word']}</div>
      {sub}
      <div class="pn">{i+1} / 4</div>
    </div>
    <div class="tab"><em>{p['km']}</em>{p['name']}</div>
    <div class="card {p['card']}"><div class="n">0{i+1}</div><b>{p['title']}</b><span>{p['text']}</span></div>
    <div class="dots">{dots}</div>
  </div>
</section>""")

html = f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<title>Fun Run A3 Landscape</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:ital,wght@0,600;0,700;1,700&display=swap" rel="stylesheet">
<style>
  @page {{ size: 420mm 297mm; margin: 0 }}
  :root{{--navy:#0A2B35;--coral:#F26A4B;--teal:#2B8791;--yellow:#FFD23F}}
  html,body{{margin:0;background:var(--navy);font-family:'Barlow Semi Condensed',Arial,sans-serif;color:var(--navy)}}
  .page{{position:relative;width:{PAGE_W}px;height:{PAGE_H}px;overflow:hidden;background:var(--navy);page-break-after:always;break-after:page}}
  .img{{position:absolute;left:{PANEL_W}px;top:0;width:{PAGE_W-PANEL_W}px;height:{PAGE_H}px;
        filter:saturate(1.55) contrast(1.1) brightness(1.02)}}
  .bar{{position:absolute;left:{PANEL_W-7}px;top:0;width:14px;height:{PAGE_H}px;background:var(--yellow)}}
  .panel{{position:absolute;left:0;top:0;width:{PANEL_W}px;height:{PAGE_H}px}}
  .top{{position:absolute;left:0;top:0;width:{PANEL_W}px;height:560px}}
  .top.a{{background:linear-gradient(120deg,#FF5A36 0,#F26A4B 55%,#FF8A3D 100%)}}
  .top.b{{background:linear-gradient(120deg,#0A2B35 0,#0E3B47 100%);border-bottom:0}}
  .logo{{position:absolute;left:34px;top:30px;width:250px;background:var(--navy);border-radius:14px;padding:6px 10px}}
  .logo img{{display:block;width:100%}}
  .word{{position:absolute;left:36px;top:170px;width:450px;line-height:.92;font-weight:700;font-style:italic;white-space:nowrap;letter-spacing:1px}}
  .a .word{{color:#fff}} .b .word{{color:var(--yellow)}}
  .patch{{position:absolute;left:1224px;top:124px;width:160px;height:78px;background:#F3F1E8;display:flex;align-items:center;justify-content:center;text-align:center;font-weight:700;font-size:26px;line-height:1.1;color:#0E3B47}}
  .sub{{position:absolute;left:40px;top:436px;width:440px;font-size:27px;font-weight:700;letter-spacing:3px;line-height:1.15}}
  .a .sub{{color:#fff}} .b .sub{{color:#BFD9D8}}
  .pn{{position:absolute;right:28px;top:34px;font-size:22px;font-weight:700;letter-spacing:4px}}
  .a .pn{{color:#fff}} .b .pn{{color:var(--yellow)}}
  .tab{{position:absolute;left:30px;top:522px;height:76px;background:var(--yellow);color:var(--navy);border-radius:38px;display:flex;align-items:center;gap:14px;padding:0 30px 0 9px;font-weight:700;font-size:38px;letter-spacing:3px;white-space:nowrap;box-shadow:0 7px 0 rgba(0,0,0,.35)}}
  .tab em{{font-style:italic;background:var(--navy);color:var(--yellow);border-radius:30px;height:58px;padding:0 20px;display:flex;align-items:center;font-size:32px;letter-spacing:2px}}
  .card{{position:absolute;left:30px;top:660px;width:458px;height:300px;border-radius:18px;box-sizing:border-box;padding:28px 30px;overflow:hidden;box-shadow:0 9px 0 rgba(0,0,0,.35)}}
  .card .n{{position:absolute;right:14px;bottom:-30px;font-size:150px;font-weight:700;font-style:italic;opacity:.22;line-height:1}}
  .card b{{display:block;font-size:42px;letter-spacing:2px;font-weight:700;position:relative;line-height:1.05;max-width:400px}}
  .card span{{display:block;font-size:31px;margin-top:14px;line-height:1.2;position:relative;font-weight:600;max-width:350px}}
  .c1{{background:var(--coral);color:#fff}}.c2{{background:var(--teal);color:#fff}}.c3{{background:var(--yellow);color:var(--navy)}}.c4{{background:#fff;color:var(--navy)}}
  .c4 .n{{color:var(--coral);opacity:.35}}
  .dots{{position:absolute;left:34px;top:1040px;display:flex;gap:18px}}
  .dots i{{display:block;width:26px;height:26px;border-radius:50%;border:5px solid var(--yellow);box-sizing:border-box}}
  .dots i.on{{background:var(--yellow)}}
</style></head>
<body>{''.join(pages)}
<script>
// fit each slogan word into the 450 px column
document.querySelectorAll('.word').forEach(w=>{{
  let fs=260;w.style.fontSize=fs+'px';
  while(w.scrollWidth>450&&fs>60){{fs-=4;w.style.fontSize=fs+'px'}}
  const lines=w.innerHTML.split('<br>').length;
  w.style.top=(lines>1?150:190)+'px';
}});
</script>
</body></html>"""

out_html = here / "concept-fun-run-a3-landscape.html"
out_html.write_text(html, encoding="utf-8")

final = here / "Fun Run A3 Landscape - EDITABLE (Canva).pdf"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": PAGE_W, "height": PAGE_H})
    pg.goto(out_html.as_uri())
    pg.wait_for_function("document.fonts.ready.then(()=>true)")
    pg.wait_for_timeout(800)
    pg.pdf(path=str(final), prefer_css_page_size=True, print_background=True)
    b.close()

r = PdfReader(str(final))
names = ["1 - LARI", "2 - KUAT", "3 - PULIH", "4 - LEBIH KUAT"]
for i, n in enumerate(names):
    w = PdfWriter()
    w.add_page(r.pages[i])
    with open(here / f"Poster A3 Landscape {n} - EDITABLE (Canva).pdf", "wb") as fh:
        w.write(fh)
print("pages:", len(r.pages), "size pt:", r.pages[0].mediabox.width, "x", r.pages[0].mediabox.height)
