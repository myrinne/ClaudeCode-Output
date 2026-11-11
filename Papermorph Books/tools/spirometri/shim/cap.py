import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ['CHROME'], args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1600, 'height': 1000})
        await pg.goto('http://localhost:8765/spirometri/ch01/'); await pg.wait_for_timeout(800)
        await pg.screenshot(path='books/spirometri/review/ch01/shots/cover.png')
        await pg.keyboard.press('Space'); await pg.wait_for_timeout(600)
        await pg.keyboard.press('c')
        await pg.evaluate("seek(2, true)")
        await pg.wait_for_timeout(9000)
        print(repr(await pg.evaluate("document.getElementById('caption').textContent")))
        await pg.screenshot(path='books/spirometri/review/ch01/shots/caption.png')
        await pg.evaluate("seek(0,true)")
        await b.close()
asyncio.run(main())
