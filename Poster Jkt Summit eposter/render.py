"""Render poster.html to a 2160 x 3840 PNG (PERDOKI e-poster, 9:16) with layout checks."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
W, H = 2160, 3840
MIN_PX = 29.3  # 22 pt

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    page.goto((HERE / "poster.html").as_uri())
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    checks = page.evaluate(f"""() => {{
        const c = document.querySelector('.content');
        const kids = [...c.children];
        const last = kids[kids.length - 1].getBoundingClientRect();
        const small = [];
        for (const el of document.querySelectorAll('.poster *')) {{
            if (!el.childNodes.length) continue;
            const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
            if (!hasText || el.closest('sup')) continue;
            const fs = parseFloat(getComputedStyle(el).fontSize);
            if (fs < {MIN_PX} - 0.5) small.push(el.tagName + ':' + fs + ':' + el.textContent.trim().slice(0, 30));
        }}
        const over = [...document.querySelectorAll('.card, .concl, .title, .stat')]
            .filter(e => e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2)
            .map(e => e.className + ' ' + e.scrollHeight + '>' + e.clientHeight);
        const refs = document.querySelector('.refs').getBoundingClientRect();
        return {{contentBottom: Math.round(last.bottom), limit: 3562, refsBottom: Math.round(Math.max(...[...document.querySelectorAll('.refs li')].map(l=>l.getBoundingClientRect().bottom))),
                 smallText: small.slice(0, 15), overflow: over}};
    }}""")
    print("checks:", checks)
    page.screenshot(path=str(HERE / "Poster_AI_OHE_PERDOKI2026.png"), full_page=False,
                    clip={"x": 0, "y": 0, "width": W, "height": H})
    browser.close()
