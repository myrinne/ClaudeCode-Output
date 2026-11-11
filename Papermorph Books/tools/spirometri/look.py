"""Quick look at moments of a beat, one montage image: look.py ch03 OUT.jpg beat:t1,t2,t3,t4 [beat:...]
Moments are seconds on the beat clock, or a mark name (a, b, ...) with an optional +offset (c+1.5). Chromium ($CHROME)."""
import asyncio, os, sys, io, re
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
CH, OUT, SPECS = sys.argv[1], sys.argv[2], sys.argv[3:]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get("CHROME"), args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1600, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(f"http://localhost:8765/spirometri/{CH}/"); await pg.wait_for_timeout(1200)
        await pg.keyboard.press("Space"); await pg.wait_for_timeout(600); await pg.keyboard.press("Space")
        await pg.add_style_tag(content=".paused-mark{display:none!important}")
        ids = await pg.evaluate("BEATS.map(b => b.id)")
        tiles = []
        for spec in SPECS:
            bid, ts = spec.split(":")
            i = ids.index(bid)
            for t in ts.split(","):
                mm = re.match(r"([a-z0-9]+)([+-][\d.]+)?$", t)
                if mm and not re.match(r"^[\d.]+$", t):
                    tt = await pg.evaluate(f"TIMINGS['{bid}'].marks['{mm.group(1)}']") + float(mm.group(2) or 0)
                else: tt = float(t)
                await pg.evaluate(f"seek({i}, false); P.t = {tt}; evalTo({tt})"); await pg.wait_for_timeout(350)
                im = Image.open(io.BytesIO(await pg.locator("#stage").screenshot())).convert("RGB").resize((800, 450))
                ImageDraw.Draw(im).text((8, 6), f"{bid} {t} ({tt:.1f}s)", fill=(200, 60, 0))
                tiles.append(im)
        cols = 2; rows = (len(tiles) + 1) // 2
        sheet = Image.new("RGB", (cols * 800, rows * 450), "white")
        for k, im in enumerate(tiles): sheet.paste(im, ((k % cols) * 800, (k // cols) * 450))
        sheet.save(OUT, quality=82)
        print("errors:", errs[:5])
        await b.close()
asyncio.run(main())
