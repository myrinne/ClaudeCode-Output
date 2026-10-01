"""Render poster.html to a 90 x 180 cm PDF and a PNG preview."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
W_PX, H_PX = round(900 / 25.4 * 96), round(1800 / 25.4 * 96)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": W_PX, "height": H_PX})
    page.goto((HERE / "poster.html").as_uri())
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    # overflow check: content taller than the page means text must shrink
    over = page.evaluate("""() => {
        const p = document.querySelector('.poster');
        const kids = [...p.children];
        const need = kids.reduce((s, k) => s + k.scrollHeight, 0);
        return {page: p.clientHeight, needed: need};
    }""")
    print("height check:", over)
    page.pdf(path=str(HERE / "Poster_SecondVictim_UOEH_90x180.pdf"),
             width="900mm", height="1800mm", print_background=True)
    page.screenshot(path=str(HERE / "preview.png"), full_page=False)
    browser.close()
