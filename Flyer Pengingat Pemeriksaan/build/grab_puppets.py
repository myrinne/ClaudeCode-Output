"""Render the paper puppets of the H-1 reminder film on a transparent background (2x), for the flyer.

Needs the video site served at http://127.0.0.1:8771/ (python -m http.server 8771 in "Video Briefing Pekerja/site").
Writes puppets_workers.png (bapak + ibu, beat b2) and puppet_doctor.png (dokter, beat b8) next to this script.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:8771/pengingat/ch01/index.html'

ISOLATE = r"""
(idx) => {
  document.documentElement.style.background = 'transparent';
  document.body.style.background = 'transparent';
  const stage = document.getElementById('stage');
  stage.style.background = 'transparent';
  const pups = [...stage.querySelectorAll('g')].filter(g => g.firstElementChild && g.firstElementChild.tagName === 'ellipse' && g.firstElementChild.hasAttribute('data-p'));
  const keep = pups[idx];
  let e = keep;
  while (e && e !== stage) {
    for (const sib of e.parentElement.children) if (sib !== e && !['defs', 'clippath', 'filter'].includes(sib.tagName.toLowerCase())) sib.style.display = 'none';
    e = e.parentElement;
  }
  for (const el of document.body.querySelectorAll('*')) {
    if (el.contains(stage) || stage.contains(el) || el.closest('svg[aria-hidden]')) continue;
    el.style.visibility = 'hidden';
  }
  return pups.length;
}
"""


def main():
    from PIL import Image, ImageChops
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 900, 'height': 1600}, device_scale_factor=2)
        for name, beat, t, idx in [('puppet_bapak', 1, 7.0, 0), ('puppet_ibu', 1, 7.0, 1), ('puppet_dokter', 7, 3.0, 0)]:
            pg.goto(f'{BASE}?beat={beat}&t={t}', wait_until='networkidle')
            pg.wait_for_timeout(1500)
            n = pg.evaluate(ISOLATE, idx)
            path = OUT / f'{name}.png'
            pg.screenshot(path=str(path), omit_background=True)
            im = Image.open(path).convert('RGB')
            bg = im.getpixel((900, 300))   # the stage's flat cream, same as the flyer's background
            inner = im.crop((80, 80, im.width - 80, im.height - 80))
            diff = ImageChops.difference(inner, Image.new('RGB', inner.size, bg)).convert('L').point(lambda v: 255 if v > 6 else 0)
            x0, y0, x1, y1 = diff.getbbox()
            pad = 24
            im.crop((x0 + 80 - pad, y0 + 80 - pad, x1 + 80 + pad, y1 + 80 + pad)).save(path)
            print('bg', bg)
            print(name, 'puppets on stage:', n)
        b.close()


if __name__ == '__main__':
    main()
