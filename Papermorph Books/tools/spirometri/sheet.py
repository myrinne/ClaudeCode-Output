"""Whole-chapter contact sheet: two frames per lesson beat (middle, end) and the open card of each question beat.
    CHROME=... uv run --no-project --with playwright --with pillow python tools/spirometri/sheet.py ch02 OUT.jpg
"""
import asyncio, os, sys, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
CH, OUT = sys.argv[1], sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROME"), args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1280, "height": 720})
        await pg.goto(f"http://localhost:8765/spirometri/{CH}/"); await pg.wait_for_timeout(1500)
        await pg.keyboard.press("Space"); await pg.wait_for_timeout(800); await pg.keyboard.press("Space")
        await pg.add_style_tag(content=".paused-mark{display:none!important}")
        beats = await pg.evaluate("BEATS.map(b => [b.id, !!b.ask, (TIMINGS[b.id]||{}).dur||0])")
        tiles = []
        for i, (bid, ask, d) in enumerate(beats):
            if bid in ("finish", "final1"): continue
            if ask:
                await pg.evaluate(f"seek({i}, true)"); await pg.wait_for_timeout(5500)
                shots = [(f"{bid} (card)", None)]
            else:
                shots = [(f"{bid} {d*.5:.0f} s", d * .5), (f"{bid} {d-.4:.0f} s", d - .4)]
            for lab, t in shots:
                if t is not None:
                    await pg.evaluate(f"seek({i}, false); P.t = {t}; evalTo({t})"); await pg.wait_for_timeout(300)
                im = Image.open(io.BytesIO(await pg.locator("#stage").screenshot())).convert("RGB").resize((560, 315))
                ImageDraw.Draw(im).text((8, 6), lab, fill=(200, 120, 0))
                tiles.append(im)
        cols = 4; rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (560 * cols, 315 * rows), "white")
        for k, im in enumerate(tiles): sheet.paste(im, ((k % cols) * 560, (k // cols) * 315))
        sheet.save(OUT, quality=85); print("saved", OUT, len(tiles), "tiles")
        await b.close()
asyncio.run(main())
