"""Looks at chapter frames: peek.py CH OUT beat:t,t,t ... (beat id or index, times in seconds). One 2-column sheet per beat.
    CHROME=... uv run --no-project --with playwright --with pillow python tools/spirometri/peek.py ch02 OUT epp:20,35,45,50
"""
import asyncio, os, sys, io
from playwright.async_api import async_playwright
from PIL import Image
CH, OUT, specs = sys.argv[1], sys.argv[2], sys.argv[3:]
URL = os.environ.get("URL", f"http://localhost:8765/spirometri/{CH}/")
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        ff = os.environ.get("BROWSER") == "firefox"
        b = await (p.firefox.launch() if ff else p.chromium.launch(executable_path=os.environ.get("CHROME"), args=["--autoplay-policy=no-user-gesture-required"]))
        pg = await b.new_page(viewport={"width": 1280, "height": 720})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.keyboard.press("Space"); await pg.wait_for_timeout(800); await pg.keyboard.press("Space")
        ids = await pg.evaluate("BEATS.map(b => b.id)")
        for sp in specs:
            bid, ts = sp.split(":"); i = ids.index(bid) if bid in ids else int(bid)
            ims = []
            for t in map(float, ts.split(",")):
                await pg.evaluate(f"seek({i}, false); P.t = {t}; evalTo({t})")
                await pg.add_style_tag(content=".paused-mark{display:none!important}"); await pg.wait_for_timeout(250)
                ims.append(Image.open(io.BytesIO(await pg.locator("#stage").screenshot())).convert("RGB").resize((800, 450)))
            cols = 2; rows = (len(ims) + 1) // 2
            sheet = Image.new("RGB", (800 * cols, 450 * rows), "white")
            for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * 800, (k // cols) * 450))
            sheet.save(f"{OUT}/{CH}_{bid}.jpg", quality=82)
            print("saved", f"{OUT}/{CH}_{bid}.jpg", [round(float(x), 1) for x in ts.split(",")])
        print("errors:", errs)
        await b.close()
asyncio.run(main())
