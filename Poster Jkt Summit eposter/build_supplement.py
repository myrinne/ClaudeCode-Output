"""Build the QR supplement (A4 PDF): 13 included studies, study characteristics and JBI grid.

Data are read from the vault notes, so the PDF stays in step with the review.
"""
import html
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
VAULT = Path(r"C:\Users\vidya\OneDrive\Documents\ClaudeCode Vault\Projects\Poster Ilmiah - Jakarta 1st Summit")
v5 = (VAULT / "Abstract v5 - Systematized Review.md").read_text(encoding="utf-8")
ext = (VAULT / "Systematized Review - Data Extraction and Analysis.md").read_text(encoding="utf-8")
app = (VAULT / "Critical Appraisal - JBI DTA Checklist.md").read_text(encoding="utf-8")

refs = re.findall(r"^(\d{1,2})\. (.+)$", v5.split("## References (Vancouver, ICMJE/NLM)")[1].split("Refs 14")[0], re.M)
refs = [t for n, t in refs if 1 <= int(n) <= 13]
assert len(refs) == 13, len(refs)


def table(md, start):
    block = md.split(start, 1)[1].strip().split("\n\n")[0]
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in block.splitlines() if ln.startswith("|")]
    return rows[0], [r for r in rows[2:]]


h1, t1 = table(ext, "### Table 1. Study characteristics")
h2, t2 = table(ext, "### Table 2. Performance, validation and reporting")
hj, tj = table(app, "## 2. Appraisal grid")
assert len(t1) == len(t2) == len(tj) == 13

esc = html.escape

# PRISMA 2020 flow, labels taken from the diagram so the supplement matches it
drawio = (VAULT / "PRISMA Flow v2.drawio").read_text(encoding="utf-8")
labels = []
for v in re.findall(r'value="([^"]*)"', drawio):
    v = html.unescape(v)
    lines = [re.sub(r"<[^>]+>", "", x).strip() for x in re.split(r"<br\s*/?>", v)]
    labels.append([x for x in lines if x])


def box(prefix):
    hit = [b for b in labels if b and b[0].startswith(prefix)]
    assert len(hit) == 1, prefix
    head, rest = hit[0][0], hit[0][1:]
    return f"<b>{esc(head)}</b>" + "".join(f"<br>{esc(x)}" for x in rest)


notes = next(b for b in labels if b and b[0].startswith("¹"))
TD = 'style="border:1px solid #408038;padding:3px 5px;vertical-align:top"'
STAGE = 'style="background-color:#185038;color:#ffffff;font-weight:bold;padding:5px;vertical-align:middle"'
NONE = 'style="border:0;padding:0;text-align:center;color:#408038"'
GREY = 'style="border:1px dashed #9AA8A0;padding:5px;vertical-align:top;color:#4A5F55"'
INC = 'style="background-color:#D5EBCF;border:2px solid #185038;padding:3px 5px;vertical-align:top"'


def row(stage, main, side, other, main_style=TD):
    side_cell = f"<td {NONE}>&#8594;</td><td {GREY}>{side}</td>" if side else f"<td {NONE}></td><td {NONE}></td>"
    other_cell = f"<td {GREY}>{other}</td>" if other else f"<td {NONE}></td>"
    return f"<tr><td {STAGE}>{stage}</td><td {main_style}>{main}</td>{side_cell}{other_cell}</tr>"


down = f"<tr><td {NONE}></td><td {NONE}>&#8595;</td><td {NONE}></td><td {NONE}></td><td {NONE}>&#8595;</td></tr>"
down_main = f"<tr><td {NONE}></td><td {NONE}>&#8595;</td><td {NONE}></td><td {NONE}></td><td {NONE}></td></tr>"
prisma = (
    '<!--prisma--><h2 style="color:#185038">PRISMA 2020 flow diagram</h2>'
    '<table style="border-collapse:collapse;font-size:8pt;line-height:1.25;width:100%;table-layout:fixed">'
    '<tr><td style="width:10%;border:0;padding:0"></td><td style="width:29%;border:0;padding:0"></td><td style="width:3%;border:0;padding:0"></td>'
    '<td style="width:30%;border:0;padding:0"></td><td style="width:28%;border:0;padding:0"></td></tr>'
    f'<tr><th {NONE}></th><th style="background-color:#408038;color:#ffffff;padding:5px" colspan="3">Identification of studies via databases</th>'
    f'<th style="background-color:#9AA8A0;color:#ffffff;padding:5px">Identification via other methods</th></tr>'
    + row("Identification", box("Records identified from databases"), box("Records removed before screening"),
          box("Records identified via supplementary"))
    + down
    + row("Screening", box("Records screened by title/abstract"), box("Records excluded at title/abstract"),
          box("Records screened against eligibility"))
    + down_main
    + row("Screening", box("Reports sought for retrieval"), box("Reports not retrieved"), "")
    + down_main
    + row("Screening", box("Reports assessed for eligibility"), box("Reports excluded at full text"), "")
    + down
    + row("Included", box("Studies included in the review"), "", box("Studies added from other methods"), INC)
    + "</table>"
    + '<p style="font-size:7.5pt;color:#4A5F55;margin:1mm 0 0">' + '<br>'.join(esc(n) for n in notes) + '</p>'
    + "<!--/prisma-->"
)

rows1 ="".join(
    f"<tr><td>{esc(a[0])}</td><td>{esc(re.sub(r' \\(.*?\\)$', '', a[1]))}</td><td>{esc(a[2])}</td><td>{esc(a[4])}</td>"
    f"<td>{esc(a[6])}</td><td>{esc(b[1])}</td></tr>" for a, b in zip(t1, t2))
cell = {"Y": "y", "N": "n", "U": "u", "NA": "na"}
rowsj = "".join("<tr>" + "".join(
    f'<td class="{cell.get(c, "")}">{esc(c)}</td>' for c in r) + "</tr>" for r in tj)

page = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
@page {{ size: A4 landscape; margin: 9mm 12mm; }}
body{{font-family:Inter,Arial,sans-serif;font-size:8.2pt;color:#17302A}}
h1{{font-size:15pt;color:#185038;margin:0 0 2mm}} h2{{font-size:11.5pt;color:#185038;margin:5mm 0 2mm}}
p.s{{margin:0 0 3mm;color:#4A5F55}}
table{{border-collapse:collapse;width:100%}} th{{background:#185038;color:#fff;text-align:left;padding:1.4mm}}
td{{border-bottom:.3mm solid #DCE4DE;padding:.9mm 1.2mm;vertical-align:top}}
ol li{{margin-bottom:1.2mm}}
td.y{{background:#D5EBCF}} td.n{{background:#FDE0D2}} td.u{{background:#FFF5D6}} td.na{{color:#888}}
.pb{{page-break-before:always}}
</style></head><body>
<h1>Artificial Intelligence for Interpreting Occupational Health Examination Tests: A Systematized Review of Evidence and Gaps</h1>
<p class="s">Supplement to the e-poster, 1st PERDOKI Jakarta Summit 2026. Vidya Cecilia, Occupational Medicine Residency Program, Faculty of Medicine, Universitas Indonesia.</p>
{prisma}
<h2 class="pb">Included studies (n = 13)</h2><ol>{"".join(f"<li>{esc(t)}</li>" for t in refs)}</ol>
<h2 class="pb">Study characteristics and main results</h2>
<table><tr><th>#</th><th>Study</th><th>Country</th><th>Modality / target</th><th>Reference standard</th><th>Main results</th></tr>{rows1}</table>
<h2 class="pb">JBI diagnostic test accuracy checklist (item level; no overall score)</h2>
<table><tr>{"".join(f"<th>{esc(h)}</th>" for h in hj)}</tr>{rowsj}</table>
<p class="s" style="margin-top:3mm">Y yes · N no · U unclear · NA not applicable. Q1 consecutive or random sample; Q2 case-control design avoided; Q3 inappropriate exclusions avoided; Q4 index test read without knowledge of the reference; Q5 threshold pre-specified; Q6 reference standard likely correct; Q7 reference read without knowledge of the index test; Q8 appropriate interval; Q9 same reference for all; Q10 all participants analysed.</p>
</body></html>"""
(HERE / "supplement.html").write_text(page, encoding="utf-8")

# Google Docs version (inline colours): put the PRISMA section before the included studies
gdoc = (HERE / "supplement_gdoc.html").read_text(encoding="utf-8")
gdoc = re.sub(r"<!--prisma-->.*?<!--/prisma-->", "", gdoc, flags=re.S)
i = gdoc.index('<h2 style="color:#185038">Included studies')
(HERE / "supplement_gdoc.html").write_text(gdoc[:i] + prisma + gdoc[i:], encoding="utf-8")
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page()
    pg.goto((HERE / "supplement.html").as_uri())
    pg.wait_for_load_state("networkidle")
    pg.pdf(path=str(HERE / "Supplement_AI_OHE_PERDOKI2026.pdf"), format="A4", landscape=True, print_background=True)
    b.close()
print("refs", len(refs), "t1", len(t1), "jbi cols", len(hj))
