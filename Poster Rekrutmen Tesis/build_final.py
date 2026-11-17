"""Poster final A (termometer) dan B (irisan kulit) memakai ilustrasi ChatGPT di assets/.
Jalankan dari folder ini: python -X utf8 build_final.py"""
import pathlib
from build_konsep import BASE_CSS, CRIT, EXCL, SAFE, KONTAK_NAMA, KONTAK_WA, li, render

HERE = pathlib.Path(__file__).parent
OUT = HERE / "final"
OUT.mkdir(exist_ok=True)

FF = "font-family='Plus Jakarta Sans, Segoe UI, Arial'"


def callout_svg(items, color, text_color, line_color):
    """items: (n, cx, cy, title, sub, tx, [path points], dot)"""
    g = [f"<svg style='position:absolute;left:0;top:0' width='794' height='1123' viewBox='0 0 794 1123' {FF}>"]
    for n, cx, cy, title, sub, path, dot in items:
        g.append(f"<path d='{path}' fill='none' stroke='{line_color}' stroke-width='2'/>")
        g.append(f"<circle cx='{dot[0]}' cy='{dot[1]}' r='4.5' fill='{line_color}'/>")
        g.append(f"<circle cx='{cx}' cy='{cy}' r='20' fill='{color}'/>")
        g.append(f"<text x='{cx}' y='{cy+7}' text-anchor='middle' font-size='20' font-weight='800' fill='#fff'>{n}</text>")
        g.append(f"<text x='{cx+32}' y='{cy-5}' font-size='18' font-weight='800' fill='{text_color}'>{title}</text>")
        g.append(f"<text x='{cx+32}' y='{cy+16}' font-size='13' fill='{text_color}'>{sub}</text>")
    g.append("</svg>")
    return "".join(g)


def poster_a():
    css = BASE_CSS + """
    body{background:#faf3ea;color:#17323a}
    .top{position:absolute;left:130px;right:40px;top:34px}
    .top .kick{font-size:13px;font-weight:700;letter-spacing:.14em;color:#e2582a}
    .top h1{font-size:44px;line-height:1.05;font-weight:800;margin-top:8px;color:#0f3d47}
    .top h1 em{font-style:normal;color:#e2582a}
    .hero{position:absolute;left:223px;top:200px;width:347px}
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
    items = [
        (1, 62, 380, "Suhu tempat kerja", "Diukur alat WBGT meter", "M275 372H372", (377, 369)),
        (2, 546, 450, "Kulit lengan", "Tewameter, tanpa rasa sakit", "M526 450H440", (438, 444)),
        (3, 62, 560, "Darah", "Sampel sekali, setelah shift", "M278 570H300L333 592", (333, 592)),
    ]
    # path lines: use explicit coordinates tied to hero (top=200, scale .3385)
    items[0] = (1, 62, 380, "Suhu tempat kerja", "Diukur alat WBGT meter", "M285 375H372", (377, 369))
    return f"""<html><head><meta charset='utf-8'><style>{css}</style></head><body>
    <img class='logo' src='../assets/logo-fkui.png'>
    <div class='top'><div class='kick'>AJAKAN PENELITIAN · INSTALASI GIZI RSCM</div>
    <h1>Dapur <em>panas</em>.<br>Bagaimana kulit dan tubuh Anda?</h1></div>
    <img class='hero' src='../assets/hero-A-termometer.png'>
    {callout_svg(items, '#0f3d47', '#17323a', '#0f3d47')}
    <div class='band'>
      <div class='col'><h3>SYARAT IKUT</h3><ul>{li(CRIT)}</ul></div>
      <div class='col no'><h3>TIDAK BISA IKUT JIKA</h3><ul>{li(EXCL)}</ul></div>
    </div>
    <div class='safe'>{''.join(f'<span>{s}</span>' for s in SAFE)}</div>
    <div class='foot'><div><small>Hubungi peneliti</small><b>{KONTAK_NAMA} · PPDS Kedokteran Okupasi FKUI</b></div><div class='wa'>WA {KONTAK_WA}</div></div>
    </body></html>"""


def poster_b():
    css = BASE_CSS + """
    body{background:#e9f2fd;color:#14213d}
    .top{position:absolute;left:130px;right:40px;top:34px}
    .top .kick{font-size:13px;font-weight:700;letter-spacing:.14em;color:#ef5b5b}
    .top h1{font-size:40px;line-height:1.08;font-weight:800;margin-top:8px;color:#14213d}
    .top h1 em{font-style:normal;color:#ef5b5b}
    .hero{position:absolute;left:47px;top:215px;width:700px}
    .cards{position:absolute;left:40px;right:40px;top:722px;display:grid;grid-template-columns:1fr 1fr;gap:18px}
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
    items = [
        (1, 62, 305, "Panas dapur", "Diukur WBGT meter", "M268 308H306", (310, 312)),
        (2, 596, 480, "Kulit", "Tewameter di lengan", "M576 480H555L505 447", (505, 447)),
        (3, 62, 655, "Darah", "Sampel sekali, setelah shift", "M272 655H287V545", (287, 542)),
    ]
    return f"""<html><head><meta charset='utf-8'><style>{css}</style></head><body>
    <img class='logo' src='../assets/logo-fkui.png'>
    <div class='top'><div class='kick'>BERGABUNGLAH DALAM PENELITIAN KAMI</div>
    <h1>Seberapa jauh <em>panas dapur</em> memengaruhi kulit dan tubuh Anda?</h1></div>
    <img class='hero' src='../assets/hero-B-kulit.png'>
    {callout_svg(items, '#ef5b5b', '#14213d', '#14213d')}
    <div class='cards'>
      <div class='card'><h3>SYARAT IKUT</h3><ul>{li(CRIT)}</ul></div>
      <div class='card no'><h3>TIDAK BISA IKUT JIKA</h3><ul>{li(EXCL)}</ul></div>
    </div>
    <div class='safe'>{''.join(f'<span>{s}</span>' for s in SAFE)}</div>
    <div class='foot'><div><small>Peneliti · PPDS Kedokteran Okupasi FKUI</small><b>{KONTAK_NAMA}</b></div><div class='wa'>WA {KONTAK_WA}</div></div>
    </body></html>"""



SAFE_V2 = ["Sukarela", "Tanpa biaya", "Data dirahasiakan", "Boleh berhenti kapan saja"]

ICON = {
    "clock": "<svg viewBox='0 0 40 40'><circle cx='20' cy='20' r='15' fill='none' stroke='#fff' stroke-width='3'/><path d='M20 10v10l7 4' fill='none' stroke='#ffb3b3' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "place": "<svg viewBox='0 0 40 40'><path d='M20 36s12-10.5 12-19a12 12 0 00-24 0c0 8.5 12 19 12 19z' fill='none' stroke='#fff' stroke-width='3'/><circle cx='20' cy='17' r='4.5' fill='#ffb3b3'/></svg>",
    "data": "<svg viewBox='0 0 40 40'><rect x='7' y='5' width='26' height='30' rx='4' fill='none' stroke='#fff' stroke-width='3'/><path d='M13 25v-5M20 25V14M27 25v-8' stroke='#ffb3b3' stroke-width='3.5' stroke-linecap='round'/></svg>",
    "safe": "<svg viewBox='0 0 40 40'><path d='M20 4l13 5v10c0 8-5.5 13.5-13 17C12.5 32.500 7 27 7 19V9z' fill='none' stroke='#fff' stroke-width='3' stroke-linejoin='round'/><path d='M13.500 20l5 5 8-9' fill='none' stroke='#ffb3b3' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'/></svg>",
}

BENEFITS = [
    ("clock", "30 menit", "perkiraan per orang"),
    ("place", "Di tempat kerja", "tidak perlu datang ke tempat lain"),
    ("data", "Data pengukuran", "diberikan kembali kepada Anda"),
    ("safe", "Dapur lebih aman", "hasil disampaikan ke Instalasi Gizi"),
]


def poster_b_v2():
    css = BASE_CSS + """
    body{background:#e9f2fd;color:#14213d}
    .top{position:absolute;left:130px;right:40px;top:34px}
    .top .kick{font-size:13px;font-weight:700;letter-spacing:.14em;color:#ef5b5b}
    .top h1{font-size:40px;line-height:1.08;font-weight:800;margin-top:8px;color:#14213d}
    .top h1 em{font-style:normal;color:#ef5b5b}
    .sub{position:absolute;left:130px;right:40px;top:194px;font-size:15px;font-weight:600;color:#3d5afe}
    .hero{position:absolute;left:60px;top:218px;width:600px}
    .ben{position:absolute;left:40px;right:40px;top:684px;display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
    .tile{background:#14213d;color:#fff;border-radius:16px;padding:12px 12px;display:flex;gap:9px;align-items:center;height:94px}
    .tile svg{width:34px;height:34px;flex:none}
    .tile b{display:block;font-size:13.5px;line-height:1.15}
    .tile span{display:block;font-size:11.5px;line-height:1.25;margin-top:3px;color:#c9d6f2}
    .cards{position:absolute;left:40px;right:40px;top:800px;display:grid;grid-template-columns:1fr 1fr;gap:16px}
    .card{background:#fff;border-radius:18px;padding:15px 20px;box-shadow:0 6px 20px rgba(20,33,61,.08)}
    .card h3{font-size:12.5px;letter-spacing:.14em;font-weight:800;margin-bottom:8px;color:#3d5afe}
    .card.no h3{color:#ef5b5b}
    .card li{font-size:12.8px;line-height:1.3;margin-bottom:4px;padding-left:15px;position:relative}
    .card li:before{content:'';position:absolute;left:0;top:6px;width:6px;height:6px;border-radius:50%;background:#3d5afe}
    .card.no li:before{background:#ef5b5b}
    .safe{position:absolute;left:40px;right:40px;top:997px;display:flex;gap:9px;justify-content:center}
    .safe span{font-size:12.5px;font-weight:700;color:#fff;background:#ef5b5b;border-radius:20px;padding:6px 14px}
    .foot{position:absolute;left:40px;right:40px;bottom:22px;height:60px;border-radius:30px;background:#fff;border:2px solid #14213d;display:flex;align-items:center;justify-content:space-between;padding:0 30px}
    .foot b{font-size:14.5px}.foot small{display:block;font-size:12px;color:#5b6b8c}
    .foot .wa{background:#ef5b5b;color:#fff;font-size:20px;font-weight:800;padding:7px 22px;border-radius:24px}
    """
    items = [
        (1, 62, 300, "Panas dapur", "Diukur WBGT meter", "M268 305H283", (287, 308)),
        (2, 575, 470, "Kulit", "Tewameter di lengan", "M555 470H540L503 437", (503, 437)),
        (3, 62, 642, "Darah", "Sampel sekali, setelah shift", "M272 645H300V492", (300, 489)),
    ]
    tiles = "".join(
        f"<div class='tile'>{ICON[i]}<div><b>{t}</b><span>{sub}</span></div></div>" for i, t, sub in BENEFITS
    )
    return f"""<html><head><meta charset='utf-8'><style>{css}</style></head><body>
    <img class='logo' src='../assets/logo-fkui.png'>
    <div class='top'><div class='kick'>BERGABUNGLAH DALAM PENELITIAN KAMI</div>
    <h1>Seberapa jauh <em>panas dapur</em> memengaruhi kulit dan tubuh Anda?</h1></div>
    <div class='sub'>Anda yang paling tahu panasnya dapur. Bantu kami membuktikannya.</div>
    <img class='hero' src='../assets/hero-B-kulit.png'>
    {callout_svg(items, '#ef5b5b', '#14213d', '#14213d')}
    <div class='ben'>{tiles}</div>
    <div class='cards'>
      <div class='card'><h3>SYARAT IKUT</h3><ul>{li(CRIT)}</ul></div>
      <div class='card no'><h3>TIDAK BISA IKUT JIKA</h3><ul>{li(EXCL)}</ul></div>
    </div>
    <div class='safe'>{''.join(f'<span>{s}</span>' for s in SAFE_V2)}</div>
    <div class='foot'><div><small>Peneliti · PPDS Kedokteran Okupasi FKUI</small><b>{KONTAK_NAMA}</b></div><div class='wa'>WA {KONTAK_WA}</div></div>
    </body></html>"""


if __name__ == "__main__":
    for name, fn in [("Poster_A_Termometer", poster_a), ("Poster_B_Irisan_Kulit", poster_b), ("Poster_B_Irisan_Kulit_v2", poster_b_v2)]:
        h = OUT / f"{name}.html"
        h.write_text(fn(), encoding="utf-8")
        render(h, OUT / f"{name}.png", scale=2)
        print(name, (OUT / f"{name}.png").stat().st_size // 1024, "KB")
