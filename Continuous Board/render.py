"""Render board.html to PNG + PDF with the installed Chrome."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

here = Path(__file__).parent
html = (here / "board.html").as_uri()
stem = sys.argv[1] if len(sys.argv) > 1 else "One Line of Care - prototype v1"

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 4800, "height": 1400})
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text))
    pg.on("pageerror", lambda e: msgs.append("ERR " + str(e)))
    pg.goto(html)
    pg.wait_for_timeout(500)
    pg.screenshot(path=str(here / f"{stem}.png"), clip={"x": 0, "y": 0, "width": 4800, "height": 1400})
    pg.pdf(path=str(here / f"{stem}.pdf"), width="4800px", height="1400px", print_background=True,
           margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    b.close()
    print("\n".join(msgs) or "no console messages")
