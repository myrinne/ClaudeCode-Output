'use strict';
/* Adegan 6: empat persiapan. Empat kartu besar (24 jam losion, 24 jam suplemen, 3 jam rokok, 2 jam basahi), tiap bagian muncul pada katanya;
   di akhir ibu mengacungkan jempol pada "katakan terus terang". Waktu kata: narration.id.words.txt (jam beat = PRE6 + waktu). */
const PRE6 = 0.8;
// waktu kata (klip adegan) dikurangi 0,22 s; sumber: narration.id.words.txt
const wd6 = t => +(t - .22).toFixed(2);
const T6 = {
  empat: wd6(.57),
  a_satu: wd6(2.35), a_24: wd6(3.36), a_jam: wd6(4.08), a_jangan: wd6(5.14), a_oleskan: wd6(5.46), a_losion: wd6(5.89), a_pelembap: wd6(6.68), a_minyak: wd6(7.4), a_tabir: wd6(8.28),
  b_dua: wd6(11.08), b_24: wd6(11.94), b_jam: wd6(12.64), b_jangan: wd6(13.7), b_suplemen: wd6(14.32), b_C: wd6(15.15), b_E: wd6(16.19), b_gluta: wd6(16.78), b_syrup: wd6(18.29),
  c_tiga: wd6(20.22), c_3: wd6(21.01), c_jam: wd6(21.32), c_sebelum: wd6(21.55), c_darah: wd6(21.88), c_diambil: wd6(22.11), c_jangan: wd6(22.87), c_merokok: wd6(23.26),
  d_empat: wd6(24.34), d_2: wd6(25.17), d_jam: wd6(25.42), d_jangan: wd6(26.48), d_cuci: wd6(26.81), d_basahi: wd6(27.45), d_lengan: wd6(27.89),
  katakan: wd6(31.44), sanksi: wd6(33.31)
};
function scene6(p, D) {
  const cam = paperCam(p, 'kertas'), S = cam.stage, W = t => PRE6 + t;
  const INK = '#2b2b2b', RED = '#c8322f', GREEN = '#3f9d6b', FONT = "'Segoe UI','Helvetica Neue',Arial,sans-serif";
  const paper = (w, h, fill = '#fffaf0', rx = 28) => pf(`<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="${rx}" fill="${fill}"/>`);
  const item = (parent, x, y, parts, texts = []) => {
    const g = mk('g', {}, parent);
    const ps = parts.map(pt => ({ g: prop(mk('g', pt.tr ? { transform: pt.tr } : {}, g), pt.svg), at: pt.at, el: g.lastChild }));
    const ts = texts.map(t => { const e = mk('text', { x: t.x, y: t.y, 'text-anchor': t.a || 'middle', 'font-size': t.size || 44, 'font-weight': 800, 'font-family': FONT, fill: t.fill || INK }, g); e.textContent = t.s; return { e, at: t.at }; });
    return { g, x, y, ps, ts };
  };
  const show = (it, q, t0, k = 1, sway = 0) => {
    const u = q - W(t0); vis(it.g, u >= 0);
    if (u < 0) return;
    const sc = k * (.6 + .4 * span(q, W(t0), W(t0) + .3) + .07 * Math.sin(Math.PI * Math.min(1, u / .4)));
    tf(it.g, `translate(${it.x} ${it.y}) rotate(${(sway * Math.sin(q * 1.3 + it.x * .01)).toFixed(2)}) scale(${sc.toFixed(3)})`);
    for (const pt of it.ps) if (pt.at != null) vis(pt.el, q >= W(pt.at));
    for (const t of it.ts) if (t.at != null) vis(t.e, q >= W(t.at));
  };
  const blink = (q, off, per = 3.6) => ((q + off) % per) < 2 / FPS;

  /* ---------- icons ---------- */
  const arm = () => FOREARM();
  const cream = () => pf(`<path d="M-70,-8 q20,-22 44,-4 q22,16 46,-2 q24,-14 44,6 q-6,26 -36,22 q-30,12 -52,-2 q-24,6 -46,-20 Z" fill="#fffdf6" opacity=".92"/>`);
  const faucet = () => pf(`<rect x="-14" y="-64" width="28" height="30" rx="6" fill="#7f8c95"/><path d="M-60,-34 H34 a22,22 0 0 1 22,22 V8 H34 V-12 H-60 Z" fill="#a6b3bb"/><rect x="26" y="4" width="36" height="14" rx="5" fill="#7f8c95"/>`);
  const drops = () => pf([0, 1, 2].map(i => `<path d="M${44 + (i - 1) * 3},${34 + i * 34} c0,0 -14,16 -14,24 a14,14 0 0 0 28,0 c0,-8 -14,-24 -14,-24 Z" fill="#4aa3d6"/>`).join(''));
  const cig = () => pf(`<g transform="rotate(-28)"><rect x="-80" y="-14" width="116" height="28" rx="5" fill="#f7f3ea"/><rect x="36" y="-14" width="44" height="28" rx="5" fill="#d98a3a"/><rect x="-92" y="-14" width="16" height="28" rx="4" fill="#c8322f"/></g>`)
    + pf(`<path d="M-76,-28 C-100,-60 -60,-72 -82,-100" stroke="#b9bfc4" stroke-width="9" fill="none" stroke-linecap="round"/>`);
  const bloodDrop = () => pf(`<path d="M0,-44 C0,-44 -36,2 -36,22 A36,36 0 0 0 36,22 C36,2 0,-44 0,-44 Z" fill="${RED}"/>`) + pf(`<path d="M-14,16 q0,14 12,18" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity=".8"/>`);
  const clock = () => pf(`<circle r="40" fill="#fff"/><circle r="40" fill="none" stroke="#e0a02f" stroke-width="9"/>`) + pf(`<path d="M0,0 V-24 M0,0 L17,10" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>`);
  const bottleRack = () => pf(`<rect x="-34" y="-30" width="68" height="74" rx="10" fill="#e8f4fa"/><rect x="-24" y="-52" width="48" height="24" rx="6" fill="#4aa3d6"/><rect x="-26" y="-8" width="52" height="28" rx="6" fill="#fff"/>`);
  // small product icons (about 64 px), centred on 0,0
  const mini = {
    losion: () => pf(`<rect x="-20" y="-6" width="40" height="42" rx="9" fill="#7ec0e0"/><rect x="-8" y="-24" width="16" height="18" rx="4" fill="#4a7f99"/><rect x="-8" y="-30" width="30" height="9" rx="4" fill="#4a7f99"/>`),
    pelembap: () => pf(`<rect x="-30" y="-6" width="60" height="34" rx="9" fill="#f2a6c0"/><rect x="-33" y="-20" width="66" height="16" rx="6" fill="#fff"/>`),
    minyak: () => pf(`<rect x="-18" y="-10" width="36" height="46" rx="10" fill="#e8b923"/><rect x="-8" y="-28" width="16" height="20" rx="4" fill="#9a7a10"/><path d="M0,2 c0,0 -9,10 -9,15 a9,9 0 0 0 18,0 c0,-5 -9,-15 -9,-15 Z" fill="#fff4c4"/>`),
    tabir: () => pf(`<circle r="20" fill="#f08a2c"/>${Array.from({ length: 8 }, (_, i) => { const a = i * Math.PI / 4; return `<path d="M${(Math.cos(a) * 28).toFixed(1)},${(Math.sin(a) * 28).toFixed(1)} L${(Math.cos(a) * 38).toFixed(1)},${(Math.sin(a) * 38).toFixed(1)}" stroke="#f08a2c" stroke-width="7" stroke-linecap="round"/>`; }).join('')}`),
    vitC: () => pf(`<circle r="30" fill="#f08a2c"/>`) + `<text y="14" text-anchor="middle" font-size="40" font-weight="800" font-family="Arial,sans-serif" fill="#fff">C</text>`,
    vitE: () => pf(`<circle r="30" fill="#e8c030"/>`) + `<text y="14" text-anchor="middle" font-size="40" font-weight="800" font-family="Arial,sans-serif" fill="#fff">E</text>`,
    gluta: () => pf(`<g transform="rotate(-35)"><rect x="-34" y="-15" width="68" height="30" rx="15" fill="#fff"/><path d="M-34,0 a15,15 0 0 1 15,-15 H0 V15 H-19 a15,15 0 0 1 -15,-15 Z" fill="#9b6bc2"/></g>`),
    syrup: () => pf(`<rect x="-18" y="-14" width="36" height="50" rx="9" fill="#5aa77a"/><rect x="-10" y="-30" width="20" height="18" rx="4" fill="#2f6f4c"/><rect x="-12" y="2" width="24" height="18" rx="4" fill="#f4f1ea"/>`),
    pill: () => pf(`<g transform="rotate(-35)"><rect x="-56" y="-22" width="112" height="44" rx="22" fill="#fff"/><path d="M-56,0 a22,22 0 0 1 22,-22 H0 V22 H-34 a22,22 0 0 1 -22,-22 Z" fill="#9b6bc2"/></g>`)
      + pf(`<circle cx="46" cy="40" r="22" fill="#f08a2c"/><circle cx="-26" cy="50" r="18" fill="#e8c030"/>`)
  };
  const noSign = r => pf(`<circle r="${r}" fill="none" stroke="${RED}" stroke-width="16"/><path d="M${-r * .7},${-r * .7} L${r * .7},${r * .7}" stroke="${RED}" stroke-width="16" stroke-linecap="round"/>`);
  const holder = () => pf(`<rect x="-175" y="-230" width="350" height="460" rx="28" fill="#ece3cc" opacity=".8"/>`)
    + `<rect x="-160" y="-215" width="320" height="430" rx="22" fill="none" stroke="#b9a98a" stroke-width="7" stroke-dasharray="26 16"/>`;

  /* ---------- tiles ---------- */
  const TX = [230, 610, 990, 1370], TY = 330;
  const tile = (i, big, label, parts, rowParts, t0, tNum, tNumJam, tNo, extraTexts = []) => {
    const num = big;
    return item(S, TX[i], TY, [{ svg: paper(350, 460) }, ...parts, { svg: `<g transform="translate(0 -55)">${noSign(78)}</g>`, at: tNo }, ...rowParts],
      [{ s: num, x: 6, y: -152, a: 'end', size: 88, at: tNum, fill: RED }, { s: 'jam', x: 18, y: -152, a: 'start', size: 58, at: tNumJam },
       { s: label[0], x: 0, y: 140, size: 40, at: tNo }, { s: label[1], x: 0, y: 186, size: 40, at: tNo }, ...extraTexts]);
  };
  const place = [0, 1, 2, 3].map(i => item(S, TX[i], TY, [{ svg: holder() }]));
  const T1 = tile(0, '24', ['Jangan dioles', 'lengan bawah'],
    [{ svg: `<g transform="translate(0 -55) scale(.75)">${arm()}</g>`, at: T6.a_jangan }, { svg: `<g transform="translate(0 -55) scale(.75)">${cream()}</g>`, at: T6.a_oleskan }],
    [[-117, 'losion', T6.a_losion], [-39, 'pelembap', T6.a_pelembap], [39, 'minyak', T6.a_minyak], [117, 'tabir', T6.a_tabir]].map(([x, k, at]) => ({ svg: `<g transform="translate(${x} 58) scale(.95)">${mini[k]()}</g>`, at })),
    T6.a_satu, T6.a_24, T6.a_jam, T6.a_jangan);
  const T2 = tile(1, '24', ['Jangan minum', 'suplemen & obat'],
    [{ svg: `<g transform="translate(0 -55) scale(.85)">${mini.pill()}</g>`, at: T6.b_suplemen }],
    [[-117, 'vitC', T6.b_C], [-39, 'vitE', T6.b_E], [39, 'gluta', T6.b_gluta], [117, 'syrup', T6.b_syrup]].map(([x, k, at]) => ({ svg: `<g transform="translate(${x} 58) scale(.95)">${mini[k]()}</g>`, at })),
    T6.b_dua, T6.b_24, T6.b_jam, T6.b_jangan);
  const T3 = tile(2, '3', ['', ''],
    [{ svg: `<g transform="translate(-30 -55) scale(.95)">${cig()}</g>`, at: T6.c_merokok }, { svg: `<g transform="translate(96 -46) scale(.62)">${bloodDrop()}</g>`, at: T6.c_darah }],
    [{ svg: `<g transform="translate(0 58) scale(.62)">${clock()}</g>`, at: T6.c_jam }],
    T6.c_tiga, T6.c_3, T6.c_jam, T6.c_jangan, [{ s: 'Jangan merokok', x: 0, y: 136, size: 40, at: T6.c_merokok }, { s: 'sebelum darah', x: 0, y: 178, size: 38, at: T6.c_sebelum }, { s: 'diambil', x: 0, y: 220, size: 38, at: T6.c_diambil }]);
  const T4 = tile(3, '2', ['Jangan dibasahi', 'lengan bawah'],
    [{ svg: `<g transform="translate(-6 -96) scale(.6)">${faucet()}</g>`, at: T6.d_cuci }, { svg: `<g transform="translate(-6 -100) scale(.6)">${drops()}</g>`, at: T6.d_basahi }, { svg: `<g transform="translate(0 -8) scale(.62)">${arm()}</g>`, at: T6.d_lengan }],
    [{ svg: `<g transform="translate(0 70) scale(.8)">${clock()}</g>`, at: T6.d_jam }],
    T6.d_empat, T6.d_2, T6.d_jam, T6.d_jangan);
  const tiles = [[T1, T6.a_satu], [T2, T6.b_dua], [T3, T6.c_tiga], [T4, T6.d_empat]];

  const chipT = item(S, 800, 628, [{ svg: paper(640, 92, GREEN, 46) }], [{ s: 'Katakan terus terang', x: 0, y: 17, size: 52, fill: '#fff' }]);
  const chipS = item(S, 800, 628, [{ svg: paper(640, 92, '#fffaf0', 46) }, { svg: `<circle cx="-270" cy="0" r="30" fill="${GREEN}"/><path d="M-284,0 l10,11 l20,-24" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>` }], [{ s: 'Tidak ada sanksi', x: 30, y: 17, size: 52, fill: '#1f5a36' }]);

  const thumb = pf(`<g transform="scale(1.5)"><rect x="-10" y="-54" width="20" height="46" rx="10" fill="#f2efe6"/></g>`);
  const ibu = ibuPuppet(S, { holds: { up: thumb } }), bapak = bapakPuppet(S);
  const ph = { b: 0.9, i: 2.3 };

  // the camera drifts in and, once the four cards are said (33.4), pushes slowly down toward the two workers and the words
  cam.to({ z: 1.04, x: 805, y: 450 }, 0, W(T6.katakan - .3));
  cam.to({ z: 1.03, x: 800, y: 500 }, W(T6.katakan - .2), 5);

  // sfx (tools/briefing/add_sfx.py)
  sfx('scene6', W(T6.a_24), 'chime', .5);
  sfx('scene6', W(T6.b_24), 'chime', .5);
  sfx('scene6', W(T6.c_3), 'chime', .5);
  sfx('scene6', W(T6.d_2), 'chime', .5);
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    // four dashed places from "empat" (0.61); each is taken by its card
    place.forEach((pl, i) => { show(pl, q, T6.empat + i * .1, 1, 0); vis(pl.g, q >= W(T6.empat + i * .1) && q < W(tiles[i][1])); });
    tiles.forEach(([t, t0]) => show(t, q, t0, 1, .6));
    show(chipT, q, T6.katakan, 1, 0); vis(chipT.g, q >= W(T6.katakan) && q < W(T6.sanksi)); show(chipS, q, T6.sanksi, 1, 0);
    const T = q * 2.1;
    const up = span(q, W(T6.katakan), W(T6.katakan + .42));
    ibu.pose({ x: 330, y: 850, s: .8, look: .3, eyeX: .5, bob: Math.sin(T) * 2, shut: blink(q, ph.i), mouth: up > .5 ? 'smile' : 'X',
      armR: 100 * up, reachR: 1 + .4 * up, hold: up > .05 ? 'up' : null, headR: 3 * Math.sin(T * .6) }, f);
    bapak.pose({ x: 1270, y: 850, s: .8, look: -.3, eyeX: -.5, bob: Math.sin(T + 1.4) * 2, shut: blink(q, ph.b), headR: q > W(T6.sanksi) ? 4 * Math.sin((q - W(T6.sanksi)) * 5) * .5 - 2 : 0,
      mouth: q > W(T6.sanksi) ? 'smile' : 'X' }, f);
  });
}
