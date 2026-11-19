"""Render a board html to PNG + PDF with the installed Chrome.
usage: python render.py <html file> <output stem> <width> <height>"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

here = Path(__file__).parent
f, stem, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": w, "height": h})
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text))
    pg.on("pageerror", lambda e: msgs.append("ERR " + str(e)))
    pg.goto((here / f).as_uri())
    pg.wait_for_timeout(500)
    pg.screenshot(path=str(here / f"{stem}.png"), clip={"x": 0, "y": 0, "width": w, "height": h})
    pg.pdf(path=str(here / f"{stem}.pdf"), width=f"{w}px", height=f"{h}px", print_background=True,
           margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    b.close()
    print("\n".join(msgs) or "no console messages")
