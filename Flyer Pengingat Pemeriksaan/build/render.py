"""Render flyer.html to ../Flyer Sebelum Pemeriksaan.png (1080 x 1920 layout at 2x = 2160 x 3840), plus a small preview."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'Flyer Sebelum Pemeriksaan.png'

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=2)
    pg.goto((HERE / 'flyer.html').as_uri(), wait_until='networkidle')
    pg.evaluate('document.fonts.ready')
    pg.wait_for_timeout(400)
    # overflow check: every text block must stay inside its card
    bad = pg.evaluate("""() => [...document.querySelectorAll('.txt, .step p, .hrs')].filter(e => {
        const r = e.getBoundingClientRect(), p = e.parentElement.getBoundingClientRect();
        return r.bottom > p.bottom + 1 || r.right > p.right + 1 || r.top < p.top - 1; }).map(e => e.textContent.trim().slice(0, 40))""")
    print('overflow:', bad or 'none')
    pg.screenshot(path=str(OUT))
    b.close()
im = Image.open(OUT)
print(OUT, im.size)
im.resize((810, 1440), Image.LANCZOS).save(HERE / '_preview.png')
