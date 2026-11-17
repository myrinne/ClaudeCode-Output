'use strict';
/* Adegan 5: siapa yang bisa ikut. Tiga shot (kertas): syarat (usia, masa kerja), denah dapur dua warna, kartu kondisi.
   Waktu kata: lihat content/briefing/ch01/narration.id.words.txt (waktu klip adegan; jam beat = PRE5 + waktu). */
const PRE5 = 0.8;
function scene5(p, D) {
  const cam = paperCam(p, 'kertas'), S = cam.stage, W = t => PRE5 + t;
  const INK = '#2b2b2b', FONT = "'Segoe UI','Helvetica Neue',Arial,sans-serif";
  const paper = (w, h, fill = '#fffaf0', rx = 26) => pf(`<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="${rx}" fill="${fill}"/>`);
  // item: a group at (x, y) with baked paper parts (each shown from its own time) and live text lines
  const item = (parent, x, y, parts, texts = [], rot = 0) => {
    const g = mk('g', {}, parent);
    const ps = parts.map(pt => ({ g: prop(g, pt.svg), at: pt.at }));
    const ts = texts.map(t => { const e = mk('text', { x: t.x, y: t.y, 'text-anchor': t.a || 'middle', 'font-size': t.size || 44, 'font-weight': 800, 'font-family': FONT, fill: t.fill || INK }, g); e.textContent = t.s; return { e, at: t.at }; });
    return { g, x, y, ps, ts, rot, at: Math.min(...parts.map(pt => pt.at ?? 1e9), ...texts.map(t => t.at ?? 1e9)) };
  };
  // show it from t0 (clip time) with a small pop; parts and texts with their own `at` come later
  const show = (it, q, t0, k = 1, sway = 0) => {
    const u = q - W(t0); vis(it.g, u >= 0);
    if (u < 0) return;
    const sc = k * (.6 + .4 * span(q, W(t0), W(t0) + .3) + .07 * Math.sin(Math.PI * Math.min(1, u / .4)));
    tf(it.g, `translate(${it.x} ${it.y}) rotate(${(sway * Math.sin(q * 1.3 + it.x * .01)).toFixed(2)}) scale(${sc.toFixed(3)})`);
    for (const pt of it.ps) if (pt.at != null) vis(pt.g, q >= W(pt.at));
    for (const t of it.ts) if (t.at != null) vis(t.e, q >= W(t.at));
  };
  const blink = (q, off, per = 3.6) => ((q + off) % per) < 2 / FPS;

  /* ---------- icons (centred on 0,0, about +-90) ---------- */
  const heart = () => pf(`<path d="M0,72 C-110,0 -70,-72 -32,-62 C-12,-57 0,-42 0,-32 C0,-42 12,-57 32,-62 C70,-72 110,0 0,72 Z" fill="#d9534f"/>`)
    + pf(`<path d="M-62,6 H-26 L-10,-26 L10,38 L26,6 H62" fill="none" stroke="#fff" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>`);
  const brain = () => pf(`<path d="M-72,0 C-88,-52 -42,-88 -6,-72 C26,-92 82,-62 72,-10 C92,22 62,68 26,56 C6,82 -42,78 -46,52 C-82,52 -92,20 -72,0 Z" fill="#e8a0ad"/>`)
    + pf(`<path d="M0,-72 C-10,-30 10,-10 0,60 M-52,-20 q26,10 42,-5 M10,22 q26,-5 46,10 M-46,26 q20,-10 36,5" stroke="#c9707f" stroke-width="6" fill="none" stroke-linecap="round"/><circle cx="38" cy="-24" r="20" fill="#c8322f"/>`);
  const sugar = () => pf(`<path d="M-24,-78 C-24,-78 -72,-14 -72,14 A48,48 0 0 0 24,14 C24,-14 -24,-78 -24,-78 Z" fill="#c8322f"/>`)
    + pf(`<rect x="10" y="14" width="62" height="62" rx="8" fill="#fff" transform="rotate(10 40 45)"/><rect x="34" y="-34" width="48" height="48" rx="7" fill="#f6f6f2" transform="rotate(-12 58 -10)"/>`);
  const arm = (tat) => pf(`<rect x="-100" y="-38" width="190" height="76" rx="38" fill="#e8be98"/><ellipse cx="82" cy="0" rx="30" ry="34" fill="#e8be98"/>`)
    + pf(`<circle cx="-62" cy="-10" r="7" fill="#c8483f"/><circle cx="-44" cy="12" r="6" fill="#c8483f"/><circle cx="-70" cy="14" r="5" fill="#c8483f"/><circle cx="-50" cy="-14" r="5" fill="#c8483f"/>`)
    + (tat ? pf(`<path d="M-16,0 q12,-26 26,0 t26,0 M0,-26 l7,14 l-14,0 Z" stroke="#3c5aa6" stroke-width="8" fill="#3c5aa6" stroke-linecap="round" stroke-linejoin="round"/>`) : '');
  const kidney = () => pf(`<path d="M-30,-72 C-82,-62 -88,22 -46,62 C-14,88 26,62 6,26 C-6,6 6,-14 32,-26 C68,-42 42,-82 -30,-72 Z" fill="#b5524a"/><path d="M-6,-4 q16,0 24,-16" stroke="#e8a09a" stroke-width="7" fill="none" stroke-linecap="round"/>`);
  const shield = () => pf(`<path d="M0,-78 L62,-52 V6 C62,46 26,72 0,84 C-26,72 -62,46 -62,6 V-52 Z" fill="#5b82c9"/>`)
    + pf(`<path d="M-24,2 a28,28 0 1,1 14,24" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M-36,16 l-4,-24 l24,10 Z" fill="#fff"/>`);
  const germ = () => pf(`<g fill="#6aa84f">${Array.from({ length: 10 }, (_, i) => { const a = i * Math.PI / 5; return `<path d="M0,0 L${(Math.cos(a) * 66).toFixed(1)},${(Math.sin(a) * 66).toFixed(1)}" stroke="#6aa84f" stroke-width="9" stroke-linecap="round"/><circle cx="${(Math.cos(a) * 68).toFixed(1)}" cy="${(Math.sin(a) * 68).toFixed(1)}" r="9"/>`; }).join('')}<circle r="46"/></g>`)
    + pf(`<circle cx="-14" cy="-8" r="7" fill="#fff"/><circle cx="14" cy="-8" r="7" fill="#fff"/><path d="M-14,16 q14,12 28,0" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/>`);
  const pillDrop = () => pf(`<g transform="rotate(-35)"><rect x="-70" y="-28" width="140" height="56" rx="28" fill="#fff"/><path d="M-70,0 a28,28 0 0 1 28,-28 H0 V28 H-42 a28,28 0 0 1 -28,-28 Z" fill="#e6a23c"/></g>`)
    + pf(`<path d="M52,10 C52,10 30,40 30,54 a22,22 0 0 0 44,0 C74,40 52,10 52,10 Z" fill="#4aa3d6"/><path d="M-60,40 C-60,40 -78,64 -78,74 a18,18 0 0 0 36,0 C-42,64 -60,40 -60,40 Z" fill="#4aa3d6"/>`);
  const cig = () => pf(`<g transform="rotate(-28)"><rect x="-80" y="-14" width="116" height="28" rx="5" fill="#f7f3ea"/><rect x="36" y="-14" width="44" height="28" rx="5" fill="#d98a3a"/><rect x="-92" y="-14" width="16" height="28" rx="4" fill="#c8322f"/></g>`)
    + pf(`<path d="M-76,-28 C-100,-60 -60,-72 -82,-100" stroke="#b9bfc4" stroke-width="9" fill="none" stroke-linecap="round"/>`);
  const person = c => pf(`<circle cx="0" cy="-26" r="26" fill="${c}"/><path d="M-46,52 C-46,6 46,6 46,52 Z" fill="${c}"/>`);
  const calendar = () => pf(`<rect x="-52" y="-46" width="104" height="96" rx="12" fill="#fff"/><rect x="-52" y="-46" width="104" height="30" rx="12" fill="#3f9d6b"/><rect x="-52" y="-30" width="104" height="14" fill="#3f9d6b"/><rect x="-30" y="-58" width="10" height="22" rx="4" fill="#2b6d4b"/><rect x="20" y="-58" width="10" height="22" rx="4" fill="#2b6d4b"/><path d="M-32,4 h18 M-9,4 h18 M14,4 h18 M-32,28 h18 M-9,28 h18" stroke="#9bb8a8" stroke-width="9" stroke-linecap="round"/>`);
  const sheet = () => pf(`<rect x="-40" y="-52" width="80" height="104" rx="8" fill="#fff"/><path d="M-24,-26 h48 M-24,-6 h48 M-24,14 h48 M-24,34 h30" stroke="#9aa9aa" stroke-width="7" stroke-linecap="round"/>`);

  /* ---------- shot 1: syarat (0 - 9.5) ---------- */
  const g1 = mk('g', {}, S);
  const card1 = item(g1, 1150, 300, [{ svg: paper(660, 230) }, { svg: `<g transform="translate(-270 0) scale(.9)">${person('#3f9d6b')}</g>` }],
    [{ s: '18', x: -158, y: 36, size: 112, at: 3.11 }, { s: '–', x: -62, y: 36, size: 112, at: 3.76, fill: '#3f9d6b' }, { s: '55', x: 42, y: 36, size: 112, at: 4.1 }, { s: 'tahun', x: 120, y: 36, a: 'start', size: 60, at: 4.86 }]);
  const card2 = item(g1, 1150, 590, [{ svg: paper(660, 270) }, { svg: `<g transform="translate(-270 -14) scale(.9)">${calendar()}</g>` }],
    [{ s: '≥', x: -150, y: 24, size: 112, at: 7.6, fill: '#3f9d6b' }, { s: '3', x: -60, y: 24, size: 112, at: 8.08 }, { s: 'bulan', x: 0, y: 24, a: 'start', size: 80, at: 8.4 },
     { s: 'bekerja di posisi sekarang', x: 20, y: 96, size: 42, at: 6.11, fill: '#5a5a5a' }]);
  const pill = item(g1, 440, 262, [{ svg: paper(620, 82, '#3f9d6b', 41) }], [{ s: 'Pekerja Instalasi Gizi', x: 0, y: 16, size: 44, fill: '#fff' }]);

  /* ---------- shot 2: denah dapur dua warna (9.5 - 15.9) ---------- */
  const g2 = mk('g', {}, S);
  const X0 = 240, X1 = 800, X2 = 1360, Y0 = 170, Y1 = 720;
  const plan = prop(g2, pf(`<rect x="${X0 - 18}" y="${Y0 - 18}" width="${X2 - X0 + 36}" height="${Y1 - Y0 + 36}" rx="26" fill="#8c7a5b"/><rect x="${X0}" y="${Y0}" width="${X2 - X0}" height="${Y1 - Y0}" rx="12" fill="#ece5d3"/>`)
    + pf(`<path d="M${X1},${Y0} V${Y1}" stroke="#8c7a5b" stroke-width="10" stroke-dasharray="40 22"/>`));
  const zoneO = prop(g2, pf(`<rect x="${X0}" y="${Y0}" width="${X1 - X0}" height="${Y1 - Y0}" rx="12" fill="#f4a259"/>`));
  const zoneG = prop(g2, pf(`<rect x="${X1}" y="${Y0}" width="${X2 - X1}" height="${Y1 - Y0}" rx="12" fill="#8fd19e"/>`));
  // inside the orange zone: stove with pots, serving counter with trays
  prop(g2, pf(`<rect x="290" y="330" width="250" height="90" rx="10" fill="#6c757b"/>${[0, 1, 2].map(i => `<ellipse cx="${335 + i * 80}" cy="372" rx="28" ry="12" fill="#2d3336"/><path d="M${321 + i * 80},366 q14,-38 28,0 q-14,-12 -28,0 Z" fill="#ffd36b"/>`).join('')}`)
    + pf(`<path d="M300,300 h60 v36 h-60 Z M390,296 h70 v40 h-70 Z" fill="#c9d1d6"/><rect x="580" y="330" width="190" height="80" rx="10" fill="#b9c2c7"/>${[0, 1, 2].map(i => `<rect x="${592 + i * 60}" y="318" width="50" height="22" rx="5" fill="#d9e1e5"/>`).join('')}`));
  // inside the green zone: cutting board with greens, crates, desk with a clipboard
  prop(g2, pf(`<rect x="840" y="330" width="170" height="86" rx="10" fill="#d9b680"/><path d="M870,376 q18,-34 36,0 q-18,10 -36,0 Z" fill="#4f9a3a"/><circle cx="940" cy="372" r="22" fill="#e8782e"/><circle cx="980" cy="378" r="16" fill="#e8782e"/>`)
    + pf(`<rect x="1050" y="338" width="100" height="78" rx="8" fill="#a98250"/><rect x="1064" y="352" width="72" height="12" fill="#c9a374"/>`)
    + pf(`<rect x="1190" y="338" width="130" height="78" rx="8" fill="#c9a374"/><rect x="1230" y="304" width="52" height="64" rx="6" fill="#fff"/><path d="M1240,322 h32 M1240,338 h32 M1240,354 h20" stroke="#9aa9aa" stroke-width="5"/>`));
  const lblO = item(g2, 520, 236, [{ svg: '' }], [{ s: 'Memasak &', x: 0, y: -4, size: 48, fill: '#7a3b05' }, { s: 'penyajian', x: 0, y: 46, size: 48, fill: '#7a3b05' }]);
  const lblG = item(g2, 1080, 236, [{ svg: '' }], [{ s: 'Persiapan bahan', x: 0, y: -4, size: 48, fill: '#1f5a36' }, { s: '& administrasi', x: 0, y: 46, size: 48, fill: '#1f5a36' }]);
  const note = item(g2, 800, 800, [{ svg: paper(760, 84, '#fffaf0', 42) }, { svg: `<g transform="translate(-320 0) scale(.55)">${sheet()}</g>` }],
    [{ s: 'hanya untuk pencatatan', x: 40, y: 16, size: 46 }]);
  const bp = bapakPuppet(S), ip = ibuPuppet(S);

  /* ---------- shot 3: kartu kondisi (15.9 - end) ---------- */
  const g3 = mk('g', {}, S);
  const cardW = 340, cardH = 340, cy = 330;
  const mkCond = (i, ic, lines, t0, extra = [], tr = 'translate(0 -58)') => item(g3, 230 + i * 380, cy, [{ svg: paper(cardW, cardH) }, { svg: `<g transform="${tr}">${ic}</g>` }, ...extra.map(e => ({ ...e, svg: `<g transform="${tr}">${e.svg}</g>` }))],
    lines.map((s, k) => ({ s, x: 0, y: (lines.length === 1 ? 128 : lines.length === 2 ? 106 : 66) + k * (lines.length === 3 ? 42 : 44), size: 40 })));
  const c1 = mkCond(0, heart(), ['Sakit jantung'], 17.87);
  const c2 = mkCond(1, brain(), ['Stroke'], 19.18);
  const c3 = mkCond(2, sugar(), ['Kencing manis'], 19.91);
  const c4 = mkCond(3, arm(false), ['Kelainan kulit', 'atau tato', 'lengan bawah'], 21.39, [{ svg: arm(true), at: 22.31 }], 'translate(0 -92) scale(.85)');
  const conds = [[c1, 17.87], [c2, 19.18], [c3, 19.91], [c4, 21.39]];
  const badge = (c, t0) => item(g3, c.x + 140, cy - 140, [{ svg: pf('<circle r="38" fill="#e0a02f"/>') }], [{ s: '?', x: 0, y: 17, size: 52, fill: '#fff' }]);
  const badges = conds.map(([c], i) => badge(c)), badgeAt = [27.77, 28.0, 28.29, 28.5];
  const banner1 = item(g3, 800, 84, [{ svg: paper(520, 84, '#e0a02f', 42) }], [{ s: 'Beberapa kondisi', x: 0, y: 17, size: 48, fill: '#fff' }]);
  const banner2 = item(g3, 800, 84, [{ svg: paper(660, 84, '#e0a02f', 42) }, { svg: '<rect x="-266" y="-22" width="12" height="44" rx="4" fill="#fff"/><rect x="-242" y="-22" width="12" height="44" rx="4" fill="#fff"/>' }],
    [{ s: 'Belum bisa ikut', x: 30, y: 17, size: 52, fill: '#fff' }]);
  const chipQ = item(g3, 800, 588, [{ svg: paper(820, 84, '#fffaf0', 42) }, { svg: `<g transform="translate(-352 0) scale(.5)">${calendar()}</g>` }], [{ s: 'Ditanya di hari pemeriksaan', x: 40, y: 16, size: 46 }]);
  const chipL = item(g3, 800, 588, [{ svg: paper(1040, 84, '#fffaf0', 42) }, { svg: `<g transform="translate(-470 0) scale(.55)">${sheet()}</g>` }], [{ s: 'Daftar lengkap: lembar penjelasan', x: 40, y: 16, size: 46 }]);
  const extraDefs = [[kidney(), ['Ginjal']], [shield(), ['Autoimun']], [germ(), ['Infeksi']], [pillDrop(), ['Obat pelancar', 'kencing']], [cig(), ['Rokok', '>20 batang']]];
  const extraAt = [31.54, 31.74, 31.94, 32.14, 32.34];
  const extras = extraDefs.map(([ic, lines], i) => item(g3, 51 + 145 + i * 302, 752, [{ svg: paper(290, 220) }, { svg: `<g transform="translate(0 -30) scale(.58)">${ic}</g>` }],
    lines.map((s, k) => ({ s, x: 0, y: (lines.length === 1 ? 82 : 64) + k * 42, size: 38 }))));

  const ph = { b: 1.7, i: 0.4 };
  // slow camera drift in each shot so none is a slide; a cut at each shot change
  cam.to({ z: 1.04, x: 815, y: 445 }, 0, W(9.4));
  cam.cut({ x: 800, y: 450, z: 1 }, W(9.45)).to({ z: 1.05, x: 790, y: 440 }, W(9.5), 6.2);
  cam.cut({ x: 800, y: 450, z: 1 }, W(15.9)).to({ z: 1.03, x: 800, y: 460 }, W(15.95), 18);
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    const s1 = q < W(9.45), s2 = q >= W(9.45) && q < W(15.9), s3 = q >= W(15.9);
    vis(g1, s1); vis(g2, s2); vis(g3, s3);
    // --- shot 1
    if (s1) {
      show(pill, q, 1.75); show(card1, q, 3.11, 1, .8); show(card2, q, 5.87, 1, .8);
    }
    // --- shot 2
    if (s2) {
      vis(zoneO, q >= W(10.7)); zoneO.setAttribute('opacity', span(q, W(10.7), W(11.1)).toFixed(2));
      vis(zoneG, q >= W(11.74)); zoneG.setAttribute('opacity', span(q, W(11.74), W(12.1)).toFixed(2));
      show(lblO, q, 12.1, 1, 0); show(lblG, q, 12.35, 1, 0); show(note, q, 13.82, 1, .6);
    }
    // --- shot 3
    if (s3) {
      show(banner1, q, 15.98, 1, 0); vis(banner1.g, q >= W(15.98) && q < W(23.83)); show(banner2, q, 23.83, 1, 0);
      conds.forEach(([c, t0]) => show(c, q, t0, 1, .8));
      badges.forEach((b, i) => show(b, q, badgeAt[i], 1, 0));
      show(chipQ, q, 28.82, 1, 0); vis(chipQ.g, q >= W(28.82) && q < W(31.05));
      show(chipL, q, 31.05, 1, 0);
      extras.forEach((e, i) => show(e, q, extraAt[i], 1, .8));
    }
    // --- the two workers: beside the cards in shot 1, in their zones in shot 2, away in shot 3
    const T = q * 2.1;
    if (s1) {
      bp.pose({ x: 290, y: 840, s: 1, look: .4, eyeX: .6, bob: Math.sin(T) * 2.2, shut: blink(q, ph.b), armR: q > W(1.75) && q < W(3) ? 10 : 0 }, f);
      ip.pose({ x: 560, y: 840, s: 1, look: .5, eyeX: .6, bob: Math.sin(T + 1.4) * 2.2, shut: blink(q, ph.i), mouth: 'smile' }, f);
    } else if (s2) {
      const u = span(q, W(9.45), W(10.2)), pointO = q > W(10.7) && q < W(11.7), pointG = q >= W(11.74) && q < W(12.9);
      bp.pose({ x: 620, y: 700, s: .62, look: -.2, eyeX: .3, bob: Math.sin(T) * 1.6, shut: blink(q, ph.b), armL: pointO ? 25 : 0 }, f);
      ip.pose({ x: 1010, y: 700, s: .62, look: .2, eyeX: -.3, bob: Math.sin(T + 1.4) * 1.6, shut: blink(q, ph.i), armR: pointG ? 25 : 0 }, f);
    } else { bp.pose({ x: -400, y: 840 }, f); ip.pose({ x: -400, y: 840 }, f); }
    vis(bp.g, !s3); vis(ip.g, !s3);
  });
}
