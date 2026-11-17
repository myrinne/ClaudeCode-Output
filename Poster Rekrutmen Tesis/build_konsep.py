"""Bangun 3 konsep poster rekrutmen tesis (HTML -> PNG lewat Edge headless).
Jalankan: python build_konsep.py   (dari folder ini)
Ganti KONTAK di bawah, lalu jalankan ulang."""
import pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "konsep"
OUT.mkdir(exist_ok=True)

KONTAK_NAMA = "dr. Vidya Cecilia"
KONTAK_WA = "08xx-xxxx-xxxx"   # <- ISI NOMOR WHATSAPP

CRIT = [
    "Berusia 18–55 tahun",
    "Bekerja di Instalasi Gizi RSCM minimal 3 bulan",
    "Bekerja lebih dari 6 jam per shift di unit Instalasi Gizi",
    "Bersedia menandatangani lembar persetujuan",
]
EXCL = [
    "Diabetes tipe 2, penyakit jantung, stroke, ginjal kronis, autoimun, atau kanker",
    "Infeksi akut dalam 1 minggu terakhir, atau rutin minum obat diuretik",
    "Perokok berat",
    "Luka, eksim, atau psoriasis di lengan bawah",
]
SAFE = ["Sukarela", "Data dirahasiakan", "Boleh berhenti kapan saja"]

FONT = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');"

BASE_CSS = FONT + """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:794px;height:1123px}
body{font-family:'Plus Jakarta Sans','Segoe UI',Arial,sans-serif;position:relative;overflow:hidden}
.logo{position:absolute;left:36px;top:0;width:58px}
ul{list-style:none}
"""

def li(items, cls=""):
    return "".join(f"<li class='{cls}'>{t}</li>" for t in items)


# ---------------------------------------------------------------- A: termometer
def concept_a():
    css = BASE_CSS + """
    body{background:#f6f3ee;color:#17323a}
    .top{position:absolute;left:130px;right:40px;top:34px}
    .top .kick{font-size:13px;font-weight:700;letter-spacing:.14em;color:#e2582a}
    .top h1{font-size:44px;line-height:1.05;font-weight:800;margin-top:8px;color:#0f3d47}
    .top h1 em{font-style:normal;color:#e2582a}
    .hero{position:absolute;left:0;top:210px}
    .band{position:absolute;left:0;right:0;top:740px;height:215px;background:#0f3d47;color:#fff;padding:26px 40px 0 40px;display:flex;gap:34px}
    .band h3{font-size:13px;letter-spacing:.14em;font-weight:700;color:#ffb089;margin-bottom:10px}
    .band li{font-size:14px;line-height:1.35;margin-bottom:7px;padding-left:16px;position:relative}
    .band li:before{content:'';position:absolute;left:0;top:7px;width:7px;height:7px;border-radius:50%;background:#ffb089}
    .band .no li:before{background:#ff6b57}
    .col{flex:1}
    .safe{position:absolute;left:40px;top:976px;display:flex;gap:10px}
    .safe span{font-size:13px;font-weight:700;color:#0f3d47;border:2px solid #0f3d47;border-radius:20px;padding:6px 14px}
    .foot{position:absolute;left:40px;right:40px;bottom:26px;height:66px;border-radius:33px;background:#e2582a;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 34px}
    .foot b{font-size:15px}.foot small{display:block;font-size:12px;opacity:.9}
    .foot .wa{font-size:22px;font-weight:800}
    """
    hero = """
    <svg class='hero' width='794' height='520' viewBox='0 0 794 520'>
      <defs>
        <linearGradient id='hg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffb089'/><stop offset='1' stop-color='#e2582a'/></linearGradient>
        <radialGradient id='glow' cx='.5' cy='.5' r='.5'><stop offset='0' stop-color='#ffd9bf' stop-opacity='.9'/><stop offset='1' stop-color='#ffd9bf' stop-opacity='0'/></radialGradient>
      </defs>
      <circle cx='397' cy='260' r='250' fill='url(#glow)'/>
      <rect x='367' y='20' width='60' height='390' rx='30' fill='#fff' stroke='#0f3d47' stroke-width='4'/>
      <circle cx='397' cy='440' r='56' fill='#fff' stroke='#0f3d47' stroke-width='4'/>
      <rect x='381' y='110' width='32' height='340' rx='16' fill='url(#hg)'/>
      <circle cx='397' cy='440' r='42' fill='url(#hg)'/>
      <g stroke='#0f3d47' stroke-width='3'>
        <path d='M340 70h18M340 110h18M340 150h18M340 190h18M340 230h18M340 270h18M340 310h18M340 350h18'/>
        <path d='M436 70h18M436 110h18M436 150h18M436 190h18M436 230h18M436 270h18M436 310h18M436 350h18'/>
      </g>
      <g fill='none' stroke='#e2582a' stroke-width='4' stroke-linecap='round' opacity='.7'>
        <path d='M150 90q14 -16 0 -32t0 -32'/><path d='M190 100q14 -16 0 -32t0 -32'/>
        <path d='M610 90q14 -16 0 -32t0 -32'/><path d='M650 100q14 -16 0 -32t0 -32'/>
      </g>
      <g font-family='Plus Jakarta Sans, Segoe UI, Arial' fill='#17323a'>
        <circle cx='62' cy='150' r='20' fill='#0f3d47'/><text x='62' y='157' text-anchor='middle' font-size='20' font-weight='800' fill='#fff'>1</text>
        <text x='94' y='145' font-size='18' font-weight='800'>Suhu tempat kerja</text><text x='94' y='166' font-size='13'>Diukur alat WBGT meter</text>
        <path d='M285 150H381' stroke='#0f3d47' stroke-width='2'/><circle cx='381' cy='150' r='4' fill='#0f3d47'/>

        <circle cx='546' cy='270' r='20' fill='#0f3d47'/><text x='546' y='277' text-anchor='middle' font-size='20' font-weight='800' fill='#fff'>2</text>
        <text x='578' y='265' font-size='18' font-weight='800'>Kulit lengan</text><text x='578' y='286' font-size='13'>Tewameter, tanpa rasa sakit</text>
        <path d='M526 270H427' stroke='#0f3d47' stroke-width='2'/><circle cx='427' cy='270' r='4' fill='#0f3d47'/>

        <circle cx='62' cy='400' r='20' fill='#0f3d47'/><text x='62' y='407' text-anchor='middle' font-size='20' font-weight='800' fill='#fff'>3</text>
        <text x='94' y='395' font-size='18' font-weight='800'>Darah</text><text x='94' y='416' font-size='13'>Sampel sekali, setelah shift</text>
        <path d='M275 410H315L345 440' fill='none' stroke='#0f3d47' stroke-width='2'/><circle cx='345' cy='440' r='4' fill='#0f3d47'/>
      </g>
    </svg>"""
    return f"""<html><head><meta charset='utf-8'><style>{css}</style></head><body>
    <img class='logo' src='../assets/logo-fkui.png'>
    <div class='top'><div class='kick'>AJAKAN PENELITIAN · INSTALASI GIZI RSCM</div>
    <h1>Dapur <em>panas</em>.<br>Bagaimana kulit dan tubuh Anda?</h1></div>
    {hero}
    <div class='band'>
      <div class='col'><h3>SYARAT IKUT</h3><ul>{li(CRIT)}</ul></div>
      <div class='col no'><h3>TIDAK BISA IKUT JIKA</h3><ul>{li(EXCL)}</ul></div>
    </div>
    <div class='safe'>{''.join(f'<span>{s}</span>' for s in SAFE)}</div>
    <div class='foot'><div><small>Hubungi peneliti</small><b>{KONTAK_NAMA} · PPDS Kedokteran Okupasi FKUI</b></div><div class='wa'>WA {KONTAK_WA}</div></div>
    </body></html>"""


# ---------------------------------------------------------------- B: irisan kulit
def concept_b():
    css = BASE_CSS + """
    body{background:#eef2fb;color:#14213d}
    .top{position:absolute;left:130px;right:40px;top:34px}
    .top .kick{font-size:13px;font-weight:700;letter-spacing:.14em;color:#ef5b5b}
    .top h1{font-size:40px;line-height:1.08;font-weight:800;margin-top:8px;color:#14213d}
    .top h1 em{font-style:normal;color:#ef5b5b}
    .hero{position:absolute;left:0;top:200px}
    .cards{position:absolute;left:40px;right:40px;top:730px;display:grid;grid-template-columns:1fr 1fr;gap:18px}
    .card{background:#fff;border-radius:18px;padding:20px 22px;box-shadow:0 6px 20px rgba(20,33,61,.08)}
    .card h3{font-size:13px;letter-spacing:.14em;font-weight:800;margin-bottom:10px;color:#3d5afe}
    .card.no h3{color:#ef5b5b}
    .card li{font-size:13.5px;line-height:1.35;margin-bottom:6px;padding-left:16px;position:relative}
    .card li:before{content:'';position:absolute;left:0;top:7px;width:7px;height:7px;border-radius:50%;background:#3d5afe}
    .card.no li:before{background:#ef5b5b}
    .safe{position:absolute;left:40px;right:40px;top:984px;display:flex;gap:10px;justify-content:center}
    .safe span{font-size:13px;font-weight:700;color:#fff;background:#14213d;border-radius:20px;padding:7px 16px}
    .foot{position:absolute;left:40px;right:40px;bottom:24px;height:62px;border-radius:31px;background:#fff;border:2px solid #14213d;display:flex;align-items:center;justify-content:space-between;padding:0 30px}
    .foot b{font-size:14.5px}.foot small{display:block;font-size:12px;color:#5b6b8c}
    .foot .wa{background:#ef5b5b;color:#fff;font-size:20px;font-weight:800;padding:8px 22px;border-radius:24px}
    """
    hero = """
    <svg class='hero' width='794' height='520' viewBox='0 0 794 520'>
      <defs>
        <linearGradient id='epi' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffd7c2'/><stop offset='1' stop-color='#f7b79c'/></linearGradient>
        <linearGradient id='der' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#f59fa0'/><stop offset='1' stop-color='#e97f85'/></linearGradient>
        <linearGradient id='sub' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#ffe29a'/><stop offset='1' stop-color='#f6cd6a'/></linearGradient>
        <linearGradient id='top' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#ffe3d3'/><stop offset='1' stop-color='#ffc9ac'/></linearGradient>
        <linearGradient id='ves' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#e5384a'/><stop offset='1' stop-color='#a8182f'/></linearGradient>
      </defs>
      <!-- block: top face -->
      <polygon points='150,230 520,230 640,180 270,180' fill='url(#top)'/>
      <!-- front faces -->
      <rect x='150' y='230' width='370' height='30' fill='url(#epi)'/>
      <rect x='150' y='260' width='370' height='90' fill='url(#der)'/>
      <rect x='150' y='350' width='370' height='70' fill='url(#sub)'/>
      <!-- side faces -->
      <polygon points='520,230 640,180 640,370 520,420' fill='#e9a08a' opacity='.75'/>
      <!-- vessel -->
      <rect x='190' y='292' width='290' height='26' rx='13' fill='url(#ves)'/>
      <ellipse cx='480' cy='305' rx='9' ry='13' fill='#7a1020'/>
      <g fill='#fff' opacity='.9'><circle cx='240' cy='305' r='5'/><circle cx='310' cy='304' r='5'/><circle cx='390' cy='306' r='5'/></g>
      <!-- sweat drops on surface -->
      <g fill='#9fd6ff' stroke='#5aa9e6' stroke-width='1.5'>
        <path d='M330 215c-6 9-10 14-10 19a10 10 0 0020 0c0-5-4-10-10-19z'/>
        <path d='M450 205c-5 8-8 12-8 16a8 8 0 0016 0c0-4-3-8-8-16z'/>
      </g>
      <!-- probe -->
      <rect x='376' y='96' width='64' height='60' rx='10' fill='#14213d'/>
      <rect x='392' y='156' width='32' height='32' rx='4' fill='#3d5afe'/>
      <circle cx='408' cy='126' r='9' fill='#7be0a6'/>
      <g fill='none' stroke='#ef5b5b' stroke-width='5' stroke-linecap='round' opacity='.8'>
        <path d='M330 50q12 -14 0 -28M370 60q12 -14 0 -28M410 50q12 -14 0 -28M450 60q12 -14 0 -28M490 50q12 -14 0 -28'/>
      </g>
      <g font-family='Plus Jakarta Sans, Segoe UI, Arial' fill='#14213d'>
        <circle cx='62' cy='60' r='20' fill='#ef5b5b'/><text x='62' y='67' text-anchor='middle' font-size='20' font-weight='800' fill='#fff'>1</text>
        <text x='94' y='55' font-size='18' font-weight='800'>Panas dapur</text><text x='94' y='76' font-size='13'>Diukur WBGT meter</text>
        <path d='M215 62H300' stroke='#14213d' stroke-width='2'/><circle cx='305' cy='62' r='4' fill='#14213d'/>

        <circle cx='600' cy='330' r='20' fill='#3d5afe'/><text x='600' y='337' text-anchor='middle' font-size='20' font-weight='800' fill='#fff'>2</text>
        <text x='632' y='325' font-size='18' font-weight='800'>Kulit</text><text x='632' y='346' font-size='13'>Tewameter di lengan</text>
        <path d='M580 330H545L505 245' fill='none' stroke='#14213d' stroke-width='2'/><circle cx='505' cy='245' r='4' fill='#14213d'/>

        <circle cx='62' cy='470' r='20' fill='#14213d'/><text x='62' y='477' text-anchor='middle' font-size='20' font-weight='800' fill='#fff'>3</text>
        <text x='94' y='465' font-size='18' font-weight='800'>Darah</text><text x='94' y='486' font-size='13'>Sampel sekali, setelah shift</text>
        <path d='M275 470H330V318' fill='none' stroke='#14213d' stroke-width='2'/><circle cx='330' cy='318' r='4' fill='#14213d'/>
      </g>
    </svg>"""
    return f"""<html><head><meta charset='utf-8'><style>{css}</style></head><body>
    <img class='logo' src='../assets/logo-fkui.png'>
    <div class='top'><div class='kick'>BERGABUNGLAH DALAM PENELITIAN KAMI</div>
    <h1>Seberapa jauh <em>panas dapur</em> memengaruhi kulit dan tubuh Anda?</h1></div>
    {hero}
    <div class='cards'>
      <div class='card'><h3>SYARAT IKUT</h3><ul>{li(CRIT)}</ul></div>
      <div class='card no'><h3>TIDAK BISA IKUT JIKA</h3><ul>{li(EXCL)}</ul></div>
    </div>
    <div class='safe'>{''.join(f'<span>{s}</span>' for s in SAFE)}</div>
    <div class='foot'><div><small>Peneliti · PPDS Kedokteran Okupasi FKUI</small><b>{KONTAK_NAMA}</b></div><div class='wa'>WA {KONTAK_WA}</div></div>
    </body></html>"""


# ---------------------------------------------------------------- C: angka 3
def concept_c():
    css = BASE_CSS + """
    body{background:#0e1b3d;color:#fff}
    .circle{position:absolute;left:40px;top:170px;width:380px;height:380px;border-radius:50%;background:#fad000}
    .top{position:absolute;left:130px;right:50px;top:36px;color:#fff}
    .top .kick{font-size:13px;font-weight:800;letter-spacing:.14em;color:#fad000}
    .top h1{font-size:36px;line-height:1.08;font-weight:800;margin-top:8px}
    .big{position:absolute;left:40px;top:170px;width:380px;height:380px;display:flex;align-items:center;justify-content:center;font-size:300px;line-height:1;font-weight:800;color:#0e1b3d;padding-bottom:14px}
    .big2{position:absolute;left:450px;top:215px;width:300px}
    .big2 .l1{font-size:38px;font-weight:800;line-height:1.05}
    .big2 .l2{font-size:17px;margin-top:8px;color:#c8d3f0;line-height:1.35}
    .steps{position:absolute;left:40px;right:40px;top:580px;display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
    .step{background:#16295a;border-radius:18px;padding:18px;text-align:center}
    .step svg{width:54px;height:54px}
    .step b{display:block;font-size:17px;margin-top:8px;color:#fad000}
    .step span{font-size:12.5px;color:#c8d3f0;line-height:1.35;display:block;margin-top:4px}
    .crit{position:absolute;left:40px;right:40px;top:785px;display:flex;gap:34px}
    .crit h3{font-size:13px;letter-spacing:.14em;font-weight:800;color:#fad000;margin-bottom:10px}
    .crit .no h3{color:#ff8a7a}
    .crit li{font-size:13.5px;line-height:1.35;margin-bottom:6px;padding-left:16px;position:relative;color:#e7ecfa}
    .crit li:before{content:'';position:absolute;left:0;top:7px;width:7px;height:7px;border-radius:50%;background:#fad000}
    .crit .no li:before{background:#ff8a7a}
    .crit>div{flex:1}
    .safe{position:absolute;left:40px;top:976px;display:flex;gap:10px}
    .safe span{font-size:13px;font-weight:700;color:#0e1b3d;background:#fad000;border-radius:20px;padding:6px 14px}
    .foot{position:absolute;left:40px;right:40px;bottom:24px;height:62px;border-radius:31px;border:2px solid #fad000;display:flex;align-items:center;justify-content:space-between;padding:0 30px}
    .foot b{font-size:14.5px}.foot small{display:block;font-size:12px;color:#c8d3f0}
    .foot .wa{font-size:22px;font-weight:800;color:#fad000}
    """
    ic_t = "<svg viewBox='0 0 54 54'><rect x='22' y='4' width='10' height='32' rx='5' fill='none' stroke='#fad000' stroke-width='3'/><circle cx='27' cy='42' r='9' fill='#fad000'/><rect x='25' y='14' width='4' height='26' fill='#fad000'/></svg>"
    ic_s = "<svg viewBox='0 0 54 54'><path d='M4 20q8-10 16 0t16 0t14 0' fill='none' stroke='#fad000' stroke-width='4' stroke-linecap='round'/><path d='M4 32q8-10 16 0t16 0t14 0' fill='none' stroke='#fad000' stroke-width='4' stroke-linecap='round'/><path d='M4 44q8-10 16 0t16 0t14 0' fill='none' stroke='#fad000' stroke-width='4' stroke-linecap='round'/></svg>"
    ic_d = "<svg viewBox='0 0 54 54'><path d='M27 4C19 18 13 25 13 33a14 14 0 0028 0c0-8-6-15-14-29z' fill='#fad000'/></svg>"
    return f"""<html><head><meta charset='utf-8'><style>{css}</style></head><body>
    <div class='circle'></div>
    <img class='logo' src='../assets/logo-fkui.png'>
    <div class='top'><div class='kick'>PENELITIAN · INSTALASI GIZI RSCM</div>
    <h1>Dapur panas dan kesehatan kulit pekerja</h1></div>
    <div class='big'>3</div>
    <div class='big2'><div class='l1'>pemeriksaan sederhana</div><div class='l2'>Ajakan untuk pekerja Instalasi Gizi RSCM ikut penelitian yang mempelajari hubungan panas tempat kerja dengan kulit dan tubuh.</div></div>
    <div class='steps'>
      <div class='step'>{ic_t}<b>Suhu kerja</b><span>Panas area kerja diukur dengan WBGT meter</span></div>
      <div class='step'>{ic_s}<b>Kulit lengan</b><span>Tewameter menempel sebentar, tanpa rasa sakit</span></div>
      <div class='step'>{ic_d}<b>Darah</b><span>Sampel sekali, setelah shift</span></div>
    </div>
    <div class='crit'>
      <div><h3>SYARAT IKUT</h3><ul>{li(CRIT)}</ul></div>
      <div class='no'><h3>TIDAK BISA IKUT JIKA</h3><ul>{li(EXCL)}</ul></div>
    </div>
    <div class='safe'>{''.join(f'<span>{s}</span>' for s in SAFE)}</div>
    <div class='foot'><div><small>Peneliti · PPDS Kedokteran Okupasi FKUI</small><b>{KONTAK_NAMA}</b></div><div class='wa'>WA {KONTAK_WA}</div></div>
    </body></html>"""


EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def render(html_path: pathlib.Path, png_path: pathlib.Path, scale=2):
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--force-device-scale-factor={scale}", "--window-size=794,1123",
                    "--virtual-time-budget=6000",
                    f"--screenshot={png_path}", html_path.as_uri()],
                   check=True, capture_output=True)

if __name__ == "__main__":
    for name, fn in [("A_termometer", concept_a), ("B_irisan_kulit", concept_b), ("C_angka_tiga", concept_c)]:
        h = OUT / f"{name}.html"
        h.write_text(fn(), encoding="utf-8")
        render(h, OUT / f"{name}.png")
        print(name, (OUT / f"{name}.png").stat().st_size // 1024, "KB")
