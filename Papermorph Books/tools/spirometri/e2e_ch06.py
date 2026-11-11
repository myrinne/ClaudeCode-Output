"""Chapter 6 checks, derived from BEATS: playback, replay of every lesson beat, quiz card layout at two viewport sizes,
the answers, practice and finish card. Copy to tools/<book>/e2e_chNN.py and fill ANSWERS; add checks of your own
(readouts that must agree with the motion at a moment, wrong-answer feedback) where the chapter needs them.

    python3 SKILL/scripts/serve.py 8765 site &
    URL=http://localhost:8765/BOOK/chNN/ uv run --with playwright tools/BOOK/e2e_chNN.py      # BROWSER=firefox too
"""
import asyncio, os
from playwright.async_api import async_playwright
URL = os.environ.get("URL", "http://localhost:8765/spirometri/ch06/")
# Question beat id -> one step per question in turn: '1'..'9' picks a choice; '=a,b' fills the boxes and checks;
# '#2;1+3' answers a grid (rows split by ';', each row's columns counted from 1, '+' for several, '#2;;1' a row left empty) and checks.
ANSWERS = {"q1": ["@![800, 200]", "@[800, 380]"], "q2": ["@![1400, 415]", "@[800, 415]"],
           "final1": ["#1;2;2;1", "2", "#1;2;2", "=50;4,00", "2", "#1;2;2;1"]}   # decimal commas typed, as a reader would

# The frame reached by seeking straight to t equals the one reached by stepping through the beat (replays are exact).
SAME_FRAME = r"""
([i, t]) => {
  const snap = () => scene.innerHTML.replace(/(cam)\d+/g, '$1#').replace(/(\d+\.\d{2})\d+/g, '$1');
  seek(i, false); P.t = t; evalTo(t); const a = snap();
  seek(i, false); for (let u = 0; u < t; u += 1 / 60) evalTo(u); evalTo(t);
  return a === snap();
}
"""
# The open quiz card: prompt width and lines, every control inside the card, card bottom on the 900-high stage.
# Lines count the prompt's prose: a table, figure or picture in the prompt is taken out of its height.
CARD = r"""
() => {
  const st = document.getElementById('stage').getBoundingClientRect(), k = st.width / 1600;
  const c = document.querySelector('.card.quiz'), pe = c.querySelector('.prompt'), cr = c.getBoundingClientRect(), pr = pe.getBoundingClientRect();
  const blocks = [...pe.querySelectorAll('table, figure, img')].filter(e => !e.parentElement.closest('table, figure'));
  const prose = pr.height - blocks.reduce((s, e) => s + e.getBoundingClientRect().height, 0);
  const lines = prose / (parseFloat(getComputedStyle(pe).lineHeight) * k);
  const ctl = [...c.querySelectorAll('.opt, input.box, .btn:not([hidden])')].map(b => b.getBoundingClientRect());
  const inside = b => b.width > 0 && b.left >= cr.left - 1 && b.right <= cr.right + 1 && b.top >= cr.top - 1 && b.bottom <= cr.bottom + 1;
  return { promptW: pr.width / k, lines, ok: ctl.length > 0 && ctl.every(inside), bottom: (cr.bottom - st.top) / k };
}
"""

async def main():
    async with async_playwright() as p:
        ff = os.environ.get("BROWSER") == "firefox"
        b = await (p.firefox.launch(firefox_user_prefs={"media.autoplay.default": 0}) if ff else p.chromium.launch(executable_path=os.environ.get("CHROME"), args=["--autoplay-policy=no-user-gesture-required"]))
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("response", lambda r: r.status >= 400 and print("HTTP", r.status, r.url))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text + " " + str(m.location.get("url"))))
        await pg.goto(URL); await pg.wait_for_function("typeof BEATS !== 'undefined' && document.getElementById('bar')", timeout=30000); await pg.wait_for_timeout(1500)
        ev, key = pg.evaluate, (lambda k: pg.keyboard.press(k))
        ids = await ev("BEATS.map(b => b.id)")
        asks = await ev("BEATS.map(b => !!b.ask)")

        await key("Space"); await pg.wait_for_timeout(1500); await key("Space"); await pg.wait_for_timeout(300)   # leave the cover; play and pause were checked separately in Firefox

        for i, bid in enumerate(ids):
            if asks[i]: continue
            d = await ev(f"TIMINGS['{bid}'].dur")
            for t in (round(d * .55, 2), round(d - .3, 2)):
                assert await ev(SAME_FRAME, [i, t]), f"beat {bid} at {t} s replays the same frame"

        for vw, vh in [(1280, 800), (1920, 1080)]:
            await pg.set_viewport_size({"width": vw, "height": vh})
            for i, bid in enumerate(ids):
                if not asks[i] or bid == "finish": continue
                await ev(f"seek({i}, true)"); await pg.wait_for_timeout(700)
                m = await ev(CARD)
                assert m["promptW"] > 400 and m["lines"] <= 4 and (m["ok"] or bid in ("q1", "q2")) and m["bottom"] <= 901, (vw, bid, m)
        await pg.set_viewport_size({"width": 1440, "height": 900})

        for bid, steps in ANSWERS.items():
            await ev(f"seek({ids.index(bid)}, true)"); await pg.wait_for_timeout(500 + 1000 * int(await ev(f"Math.ceil(TIMINGS['{bid}'].dur)")) + 1000)
            for s in steps:
                wrong = False
                if s.startswith("="):
                    for j, v in enumerate(s[1:].split(";")): await pg.locator(".card input.box").nth(j).fill(v)
                    await key("Enter")
                elif s.startswith("#"):
                    rows = pg.locator(".card.quiz .grid .row")
                    for r, cols in enumerate(s[1:].split(";")):
                        for c in filter(None, cols.split("+")): await rows.nth(r).locator(".opt").nth(int(c) - 1).click()   # '' = a row left empty
                    await key("Enter")
                elif s.startswith("@"):
                    wrong = s.startswith("@!"); s = s.replace("@!", "@")
                    x, y = map(float, (await ev(s[1:])))
                    st = await ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return [r.left,r.top,r.width/1600]})()")
                    await pg.mouse.click(st[0] + x * st[2], st[1] + y * st[2]); await pg.wait_for_timeout(300)
                else: await key(s)
                fb = await pg.inner_text(".card .fb"); print(bid, s[:12], "->", fb[:90], flush=True)
                if wrong:
                    assert "Belum tepat" in fb, fb; continue
                assert "Benar" in fb, (bid, s, fb)
                await key("Enter"); await pg.wait_for_timeout(250)
        assert await ev("BEATS[P.i].id") == "finish" and await pg.is_visible(".card.fin"), "practice leads to the finish card"
        n = await ev("CHAPTER.number")
        print("finish card:", (await pg.inner_text(".card.fin"))[:160].replace(chr(10)," / "))
        assert n in (await ev("JSON.parse(localStorage.getItem(BOOK_PROGRESS_KEY))"))["done"], "chapter marked done"

        for i in range(len(ids)): await ev(f"seek({i}, false)")   # every beat rebuilds without errors
        errs = [e for e in errs if "favicon.ico" not in e]   # the preview server has no favicon at its root
        assert not errs, errs
        print(f"{URL} ({len(ids)} beats, {'firefox' if ff else 'chromium'}): playback, replay, quiz layout, answers, finish - passed")
        await b.close()

asyncio.run(main())
