"""Build a Canva-friendly PDF (live text, 1 page per poster) from the 4-poster board.

- swaps Bahnschrift (not in Canva) for Barlow Semi Condensed (in Canva / Google Fonts)
- drops text-shadows (they export as duplicate text layers)
- prints each 1200 x 2290 poster as its own PDF page, then merges them

usage: python make_editable_pdf.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter, PdfReader

here = Path(__file__).parent
src = (here / "concept-1-2-funrun-4posters.html").read_text(encoding="utf-8")

FONT = "'Barlow Semi Condensed',Arial,sans-serif"
link = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:ital,wght@0,600;0,700;0,800;1,700;1,800&display=swap" rel="stylesheet">')
html = src.replace("</head>", link + "</head>")
html = html.replace("'Bahnschrift','Segoe UI',Arial,sans-serif", FONT)
html = html.replace("Bahnschrift,'Segoe UI',Arial", FONT.replace("'", "\\'") if False else "'Barlow Semi Condensed',Arial")
html = html.replace("text-shadow:10px 10px 0 var(--navy)", "").replace("text-shadow:10px 10px 0 #000", "")
out_html = here / "concept-1-2-funrun-4posters-editable.html"
out_html.write_text(html, encoding="utf-8")

W, H = 1200, 2290
names = ["1 - LARI", "2 - KUAT", "3 - PULIH", "4 - LEBIH KUAT"]
parts = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": W, "height": H})
    for i, n in enumerate(names):
        pg.goto(out_html.as_uri())
        pg.wait_for_function("document.fonts.ready.then(()=>true)")
        pg.wait_for_timeout(600)
        pg.add_style_tag(content=f"html,body{{width:{W}px;height:{H}px;overflow:hidden;margin:0}} #b{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;overflow:hidden}}")
        pg.wait_for_timeout(200)
        # keep ONLY this poster's elements so nothing from neighbours sits off-page in Canva
        pg.evaluate("""(i)=>{
          const x0=i*1200,b=document.getElementById('b');
          const inner=document.createElement('div');
          inner.style.cssText='position:absolute;left:'+(-x0)+'px;top:0;width:4800px;height:2290px';
          while(b.firstChild)inner.appendChild(b.firstChild);b.appendChild(inner);
          [...inner.children].forEach(c=>{
            if(c.tagName.toLowerCase()==='svg'||c.classList.contains('strip')||c.classList.contains('edge'))return;
            const r=c.getBoundingClientRect(); if(r.right<=0||r.left>=1200)c.style.display='none';});
          const svg=document.getElementById('fx');
          [...svg.children].forEach(e=>{
            if(e.getAttribute('stroke-dasharray')&&e.tagName.toLowerCase()==='line'){e.remove();return;}
            if(e.tagName.toLowerCase()==='line'){ // route line: trim to this poster
              const a=+e.getAttribute('x1'),z=+e.getAttribute('x2');
              e.setAttribute('x1',Math.max(a,x0));e.setAttribute('x2',Math.min(z,x0+1200));return;}
            const r=e.getBoundingClientRect(); if(r.right<=-2||r.left>=1202)e.remove();});
          const s=document.querySelector('.strip');s.style.left=x0+'px';s.style.width='1200px';s.style.backgroundPosition=(-x0)+'px -199px';
          document.querySelectorAll('.edge').forEach(e=>{e.style.left=x0+'px';e.style.width='1200px'});
        }""", i)
        pg.wait_for_timeout(200)
        f = here / f"_tmp_poster_{i+1}.pdf"
        pg.pdf(path=str(f), width=f"{W}px", height=f"{H}px", print_background=True, page_ranges="1",
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        parts.append(f)
        pg.screenshot(path=str(here / f"_tmp_check_{i+1}.png"))
    b.close()

w = PdfWriter()
for f in parts:
    for page in PdfReader(str(f)).pages:
        w.add_page(page)
final = here / "Fun Run 4 Poster - EDITABLE (Canva).pdf"
with open(final, "wb") as fh:
    w.write(fh)
for f in parts:
    f.unlink()
print("wrote", final.name, "pages:", len(w.pages))
