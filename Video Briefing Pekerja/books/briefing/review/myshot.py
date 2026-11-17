"""Screenshot several moments of ONE beat with a single page load (long timeout: the page bakes puppets live and is slow).
   uv run --with playwright --with pillow python myshot.py BEAT OUTDIR T1 T2 ...   (T = seconds on the beat clock)"""
import asyncio, io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / '..' / '.claude' / 'skills' / 'papermorph' / 'scripts'))
from playwright.async_api import async_playwright
from PIL import Image
from browsers import answers, exe

CLEAN = """#bar, #caption, #ui, #soundNote, #help, #cover, .paused-mark { display: none !important; }
#frame { border-radius: 0 !important; box-shadow: none !important; }"""

async def main(beat, out, times):
    Path(out).mkdir(parents=True, exist_ok=True)
    url = 'http://localhost:8765/briefing/ch01/index.html'
    answers(url)
    async with async_playwright() as p:
        b = await p.chromium.launch(**exe())
        pg = await b.new_page(viewport={'width': 1640, 'height': 1000}, reduced_motion='reduce')
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type == 'error' and not m.location.get('url', '').endswith('/favicon.ico') and errs.append(m.text))
        await pg.goto(f'{url}?beat={beat}&t=0', timeout=240000)
        await pg.wait_for_timeout(1500)
        await pg.add_style_tag(content=CLEAN)
        for t in times:
            await pg.evaluate(f'P.t = {t}; evalTo({t})')
            await pg.wait_for_timeout(1200)
            clip = await pg.evaluate("(() => { const r = document.getElementById('stage').getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height}; })()")
            im = Image.open(io.BytesIO(await pg.screenshot(clip=clip, timeout=120000))).convert('RGB').resize((1600, 900))
            f = Path(out) / f'b{beat:02d}_{t}.png'
            im.save(f); print(f)
        await b.close()
    print('errors:', sorted(set(errs))[:8] or 'none')

asyncio.run(main(int(sys.argv[1]), sys.argv[2], [float(x) for x in sys.argv[3:]]))
