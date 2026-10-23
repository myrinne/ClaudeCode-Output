"""Build alternative e-posters with a central hero image and leader-line callouts.

Content is taken from poster.html (the submitted design) so all versions say the same thing;
the Results section is rebuilt around a ChatGPT illustration (assets/alt*.png).
Leader lines are drawn in the page after layout, from each callout to its anchor on the image.
Usage: python build_alt.py [alt1 alt2 alt6]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
src = (HERE / "poster.html").read_text(encoding="utf-8")
STAGE_W = 1972  # inner width of a full-width card
CONTENT_LIMIT = 3437  # keep clear of the reference block (top 3453)


def between(a, b):
    i = src.index(a)
    return src[i:src.index(b, i)]


style = between("<style>", "</style>") + "</style>"
title = between("  <!-- TITLE -->", "  <!-- KEY NUMBERS -->")
methods = between("  <!-- 02 METHODS -->", "  <!-- 03 RESULTS -->")
r2 = between('  <section class="row r2">', "  <!-- LIMITATIONS OF THE EVIDENCE -->")
quality_card = between('    <div class="card dm">', "  </section>\n\n  <!-- LIMITATIONS")
lims = between("  <!-- LIMITATIONS OF THE EVIDENCE -->", "  <!-- 04 CONCLUSION -->")
concl = between("  <!-- 04 CONCLUSION -->", "\n</div>\n\n<!-- REFERENCES -->")
refs = between("<!-- REFERENCES -->", "\n</div>\n</body>")
gapmap = between('    <table class="gm">', "  </section>\n\n  <section class=\"row r2\">")

background = """  <!-- 01 BACKGROUND -->
  <section class="card bgalt">
    <div class="h"><span class="no">01</span>Background</div>
    <ul>
      <li>Periodic occupational examinations generate <b>large volumes of test results</b>.</li>
      <li>Whether <b>artificial intelligence (AI)</b> validly interprets them remains unclear.</li>
    </ul>
    <div class="aim"><b>Aim:</b> to review the evidence on AI interpreting workers' examination tests against a clinical reference standard.</div>
  </section>
"""

ALT_CSS = """
  .bgalt{display:grid;grid-template-columns:auto 1fr 700px;gap:28px;align-items:center;padding:14px 28px}
  .bgalt .h{margin:0}
  .bgalt ul{font-size:31px;line-height:1.25}
  .bgalt .aim{margin-top:0;font-size:31px;line-height:1.25}
  .hero2{background:#FAF9F2;border:2px solid var(--line);border-radius:24px;padding:16px 28px 20px}
  .hero2 .h{margin-bottom:4px}
  .hero2 .kick{font-size:40px;font-weight:800;color:var(--or);margin-left:22px;line-height:1.1}
  .hero2 .kick.solo{margin:0 0 8px 0}
  .stage.grid{display:grid;align-items:center;gap:20px}
  .stage.grid img{position:static;width:100%;height:auto}
  .stage.grid .col{position:static;display:flex;flex-direction:column;justify-content:center;gap:8px}
  .stage{position:relative}
  .stage img{position:absolute;display:block}
  .stage svg.lead{position:absolute;left:0;top:0;pointer-events:none;overflow:visible}
  .stage .col{position:absolute;top:0;bottom:0;display:flex;flex-direction:column;justify-content:space-between}
  .cl{position:relative;background:rgba(255,255,255,.95);border:2px solid var(--line);border-left:12px solid var(--g600);border-radius:14px;padding:5px 14px 6px;font-size:29px;line-height:1.18;color:var(--ink)}
  .stage>.cl{position:absolute}
  .cl.z{border-left-color:var(--or)}
  .cl .t{display:flex;align-items:baseline;justify-content:space-between;gap:12px;font-weight:800;color:var(--g900);font-size:31px}
  .cl .t .n{font-size:50px;font-weight:900;line-height:1;color:var(--g900)}
  .cl.z .t .n{color:var(--or)}
  .cl .m{color:var(--muted)}
  .cl .tag{margin:4px 0 0}
  .row2{display:grid;grid-template-columns:1fr 840px;gap:22px}
  .row2 .dots{grid-template-columns:repeat(13,20px);gap:4px}
  .row2 .dots span{width:20px;height:20px;border-radius:10px}
  .row2 .dr{grid-template-columns:1fr 308px 40px}
"""

LEADER_JS = """
<script>
function drawLeaders(){
  for (const st of document.querySelectorAll('.stage')) {
    const sr = st.getBoundingClientRect(), img = st.querySelector('img').getBoundingClientRect();
    const svg = st.querySelector('svg.lead'); svg.setAttribute('width', sr.width); svg.setAttribute('height', sr.height);
    let out = '';
    for (const c of st.querySelectorAll('.cl')) for (const pt of c.dataset.anchors.split(';')) {
      const [px, py] = pt.split(',').map(Number);
      const r = c.getBoundingClientRect();
      const ax = img.left - sr.left + img.width * px / 100, ay = img.top - sr.top + img.height * py / 100;
      const L = r.left - sr.left, R = r.right - sr.left, T = r.top - sr.top, B = r.bottom - sr.top;
      let sx, sy;
      if (ax > R) { sx = R; sy = T + 30; } else if (ax < L) { sx = L; sy = T + 30; }
      else { sx = Math.min(Math.max(ax, L + 40), R - 40); sy = ay < T ? T : B; }
      const col = c.classList.contains('z') ? '#E85820' : '#185038';
      out += `<line x1="${sx}" y1="${sy}" x2="${ax}" y2="${ay}" stroke="${col}" stroke-width="4"/>` +
             `<circle cx="${ax}" cy="${ay}" r="11" fill="#fff" stroke="${col}" stroke-width="5"/>`;
    }
    svg.innerHTML = out;
  }
}
document.fonts.ready.then(drawLeaders);
</script>
"""


def callout(c, absolute=False):
    cls = "cl z" if c.get("zero") else "cl"
    pos = f' style="left:{c["x"]}px;top:{c["y"]}px;width:{c["w"]}px"' if absolute else ""
    lines = "".join(f'<div class="m">{x}</div>' for x in c["lines"])
    anchors = ";".join(f"{x},{y}" for x, y in (c["anchors"] if "anchors" in c else [(c["ax"], c["ay"])]))
    return (f'<div class="{cls}" data-anchors="{anchors}"{pos}>'
            f'<div class="t"><span>{c["name"]}</span><span class="n">{c["n"]}</span></div>{lines}</div>')


def stage(v, width=STAGE_W):
    if v.get("mode") == "grid":  # left column | image | right column; height follows the taller part
        cw = v["col_w"]
        cols = lambda cs: '<div class="col">' + "".join(callout(c) for c in cs) + "</div>"
        return (f'<div class="stage grid" style="width:{width}px;grid-template-columns:{cw}px 1fr {cw}px">'
                f'{cols(v["left"])}<img src="assets/{v["img"]}" alt=""><svg class="lead"></svg>{cols(v["right"])}</div>')
    iw = v["img_w"]; ih = round(iw * 1024 / 1536)
    ix = v.get("img_x", (width - iw) // 2); iy = v.get("img_y", 0)
    h = v.get("stage_h", ih)
    parts = [f'<img src="assets/{v["img"]}" alt="" style="left:{ix}px;top:{iy}px;width:{iw}px;height:{ih}px">',
             '<svg class="lead"></svg>']
    cw = v.get("col_w", 0)
    if v.get("left"):
        parts.append(f'<div class="col" style="left:0;width:{cw}px">' + "".join(callout(c) for c in v["left"]) + "</div>")
    if v.get("right"):
        parts.append(f'<div class="col" style="right:0;width:{cw}px">' + "".join(callout(c) for c in v["right"]) + "</div>")
    parts += [callout(c, absolute=True) for c in v.get("free", [])]
    return f'<div class="stage" style="width:{width}px;height:{h}px">{"".join(parts)}</div>'


def hero(v, width=STAGE_W, num=True):
    bg = f' style="background:{v["bg"]}"' if v.get("bg") else ""  # match the illustration's own background
    return (f'  <section class="hero2"{bg}><div class="h"><span class="no">03</span>Results<span class="kick">{v["kick"]}</span></div>'
            f'\n    {stage(v, width)}\n  </section>\n')


NB = '<span style="white-space:nowrap">{}</span>'
EXT = NB.format("External validation {e}") + " · " + NB.format("Prospective 0")
CHEST = dict(name="Chest radiography", n="9", lines=["Reference: expert reading or clinical diagnosis",
             NB.format("AUC 0.84–1.00") + " · " + NB.format("Se 62–100%") + " · " + NB.format("Sp 46–98%"),
             EXT.format(e=3)])
AUDIO = dict(name="Audiometry", n="1", lines=["Reference: claimants vs unexposed controls",
             "Se 98.6%, Sp 90.2%", EXT.format(e=0)])
ECG = dict(name="Electrocardiography", n="1", lines=["Reference: examination ECG diagnosis",
           "AUC 0.92–0.98", EXT.format(e=0)])
MULTI = dict(name="Multimodal records", n="2", lines=["Reference: physicians' fit/unfit status",
             "AUC 0.60; kappa 1.00 vs one physician rating documents",
             '<span class="tag">agreement ≠ accuracy</span>'])
SPIRO = dict(name="Spirometry", n="0", zero=True, lines=["No eligible study"])
LAB = dict(name="Laboratory", n="0", zero=True, lines=["No eligible study"])
FTW = dict(name="Fitness to work", n="0", zero=True,
           lines=["No study provided AI with the job-demand information required for fitness-to-work decisions"])

VARIANTS = {
    "alt1": dict(
        img="alt1b_worker_iso.png", kick="AI reads the tests. No study showed it the job.",
        mode="grid", col_w=450,
        left=[{**AUDIO, "ax": 45, "ay": 9}, {**CHEST, "ax": 47, "ay": 26},
              {**SPIRO, "ax": 48.5, "ay": 33}, {**LAB, "ax": 40.5, "ay": 51}],
        right=[{**MULTI, "ax": 63, "ay": 27}, {**ECG, "ax": 55, "ay": 32}, {**FTW, "ax": 82, "ay": 63}]),
    "alt3": dict(
        img="alt3c_museum_semiflat.png", kick="Admired behind glass: 0 of 13 evaluated prospectively.",
        mode="grid", col_w=470, bg="#F8ECD6",
        left=[{**CHEST, "ax": 43, "ay": 25}, {**AUDIO, "ax": 16, "ay": 35}, {**ECG, "ax": 17, "ay": 62}],
        right=[{**FTW, "ax": 75, "ay": 22}, {**MULTI, "ax": 86, "ay": 45},
               dict(name="Spirometry, laboratory", n="0", zero=True, anchors=[(75, 69), (44, 73)],
                    lines=["No eligible study: two empty pedestals"])]),
    "alt6": dict(
        img="alt6_factory.png", kick="One busy station, two closed ones, and no view of the workplace.",
        img_w=1140, img_x=480, col_w=450, stage_h=760,
        left=[{**CHEST, "ax": 18, "ay": 25}, {**AUDIO, "ax": 35, "ay": 27}, {**ECG, "ax": 45, "ay": 38}],
        free=[{**SPIRO, "x": 1170, "y": 0, "w": 380, "ax": 56, "ay": 40},
              {**LAB, "x": 1592, "y": 0, "w": 380, "ax": 64, "ay": 46},
              {**MULTI, "x": 1592, "y": 170, "w": 380, "ax": 73, "ay": 58},
              {**FTW, "x": 1592, "y": 520, "w": 380, "ax": 92, "ay": 66}]),
    "alt2": dict(
        img="alt2_dummies.png", kick="Strong on curated datasets. Not yet evaluated prospectively in workers.",
        img_w=1080, img_x=10, img_y=130, stage_h=850,
        free=[dict(name="Case-control or enriched", n="7/13", zero=True, x=0, y=0, w=520, ax=58, ay=42,
                   lines=["Curated datasets likely overstate screening performance"]),
              dict(name="High AUC ≠ sensitivity", n="0.88", x=10, y=700, w=520, ax=33, ay=60,
                   lines=["AUC 0.88 with sensitivity 62%<sup>1</sup>; AUC up to 1.00 in cross-validation"]),
              dict(name="Prospective in workers", n="0/13", zero=True, x=580, y=0, w=500, ax=91, ay=28,
                   lines=["External validation 3/13 · NPV 2/13"])]),
}


def build(key):
    v = VARIANTS[key]
    body = title + background + methods
    if key == "alt2":
        body += ('  <section class="card">\n    <div class="h"><span class="no">03</span>Results</div>\n'
                 + gapmap + "  </section>\n")
        body += ('  <section class="row2">\n  <section class="hero2"><div class="kick solo">'
                 + v["kick"] + "</div>\n    " + stage(v, 1100) + "\n  </section>\n" + quality_card + "  </section>\n")
    else:
        body += hero(v) + r2
    body += lims + concl
    page = (src[:src.index("<style>")] + style.replace("</style>", ALT_CSS + "</style>")
            + "\n</head>\n<body>\n<div class=\"poster\">\n<div class=\"content\">\n\n" + body
            + "\n</div>\n\n" + refs + "\n</div>\n" + LEADER_JS + "</body>\n</html>\n")
    out = HERE / f"poster_{key}.html"
    out.write_text(page, encoding="utf-8")
    return out


CHECK = """() => {
  const kids=[...document.querySelector('.content').children];
  const small=[];
  for (const el of document.querySelectorAll('.poster *')) {
    const t=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
    if(!t||el.closest('sup')||el.closest('.refs')) continue;
    const fs=parseFloat(getComputedStyle(el).fontSize); if(fs<28.8) small.push(el.textContent.trim().slice(0,30)+':'+fs);
  }
  const cls=[...document.querySelectorAll('.cl')].map(e=>e.getBoundingClientRect());
  const overlap=[]; cls.forEach((a,i)=>cls.forEach((b,j)=>{ if(j>i && a.left<b.right && b.left<a.right && a.top<b.bottom && b.top<a.bottom) overlap.push(i+'x'+j); }));
  const st=document.querySelector('.stage').getBoundingClientRect();
  const outside=cls.filter(r=>r.bottom>st.bottom+1||r.top<st.top-1).length;
  const over=[...document.querySelectorAll('.card,.concl,.title,.cl,.hero2')].filter(e=>e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2).map(e=>e.className);
  return {bottom:Math.round(kids[kids.length-1].getBoundingClientRect().bottom), limit:%d, overlap, outsideStage:outside, small:small.slice(0,8), over};
}""" % CONTENT_LIMIT

if __name__ == "__main__":
    keys = sys.argv[1:] or list(VARIANTS)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 2160, "height": 3840}, device_scale_factor=1)
        for k in keys:
            pg.goto(build(k).as_uri()); pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready"); pg.evaluate("drawLeaders()")
            print(k, pg.evaluate(CHECK))
            pg.screenshot(path=str(HERE / f"Poster_AI_OHE_PERDOKI2026_{k}.png"),
                          clip={"x": 0, "y": 0, "width": 2160, "height": 3840})
            # single-page PDF at poster size with live text, for editing in Canva
            pg.pdf(path=str(HERE / f"Poster_AI_OHE_PERDOKI2026_{k}.pdf"), width="2160px", height="3840px",
                   print_background=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                   page_ranges="1")
        b.close()
