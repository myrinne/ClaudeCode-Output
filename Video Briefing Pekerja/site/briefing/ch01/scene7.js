'use strict';
/* Adegan 7: hari pemeriksaan. Shot 1: ruang sejuk, bapak dan ibu duduk istirahat 15-30 menit. Shot 2: garis waktu empat langkah
   (kuesioner, timbang + tinggi badan, kulit lengan bawah, darah) dan kartu terpisah "panas dan udara dapur diukur di hari lain".
   Waktu kata: narration.id.words.txt (jam beat = PRE7 + waktu). */
const PRE7 = 0.8;
// waktu kata (klip adegan) dikurangi 0,22 s; sumber: narration.id.words.txt
const wd7 = t => +(t - .22).toFixed(2);
const T7 = {
  end: wd7(.64), rest: wd7(2.75), n15: wd7(3.27), dash: wd7(3.79), n30: wd7(4.04), menit: wd7(4.34), ruangan: wd7(4.94),
  cut: 6.1, empat: wd7(6.98), sekitar: wd7(8.97),
  s1: wd7(11.39), s1b: wd7(11.73), s2: wd7(13.21), s2b: wd7(14.32),
  s3: wd7(16.54), s3b: wd7(17.05), s3alat: wd7(17.68), s3sakit: wd7(18.6),
  s4: wd7(21.26), s4ml: wd7(22.05), s4sdk: wd7(24.59), s4sekali: wd7(25.34),
  other: wd7(26.9), otherb: wd7(28.57), cal: wd7(29.11)
};
function scene7(p, D) {
  const cam = paperCam(p, 'ruang'), S = cam.stage, W = t => PRE7 + t;
  cam.show('bench', false);   // the set's bench is a tall stool for standing figures; a low bench is drawn below
  const INK = '#2b2b2b', RED = '#c8322f', GREEN = '#3f9d6b', FONT = "'Segoe UI','Helvetica Neue',Arial,sans-serif";
  const paper = (w, h, fill = '#fffaf0', rx = 28) => pf(`<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="${rx}" fill="${fill}"/>`);
  const item = (parent, x, y, parts, texts = []) => {
    const g = mk('g', {}, parent);
    const ps = parts.map(pt => { const h = mk('g', pt.tr ? { transform: pt.tr } : {}, g); prop(h, pt.svg); return { el: h, at: pt.at }; });
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
  const clock = () => pf(`<circle r="40" fill="#fff"/><circle r="40" fill="none" stroke="#e0a02f" stroke-width="9"/>`) + pf(`<path d="M0,0 V-24 M0,0 L17,10" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>`);
  const flake = () => pf(`<g stroke="#4aa3d6" stroke-width="9" stroke-linecap="round" fill="none">${[0, 60, 120].map(a => `<path d="M0,-40 V40" transform="rotate(${a})"/>`).join('')}${[0, 60, 120, 180, 240, 300].map(a => `<path d="M0,-26 l-9,-10 M0,-26 l9,-10" transform="rotate(${a})"/>`).join('')}</g>`);
  const clip = () => pf(`<rect x="-52" y="-66" width="104" height="132" rx="12" fill="#fff"/><rect x="-26" y="-76" width="52" height="22" rx="8" fill="#7f8c95"/>`)
    + pf(`<path d="M-30,-26 h60 M-30,-4 h60 M-30,18 h36" stroke="#9aa9aa" stroke-width="8" stroke-linecap="round"/><path d="M12,36 l12,14 l24,-28" stroke="${GREEN}" stroke-width="11" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`);
  const scale = () => pf(`<rect x="-62" y="-4" width="124" height="52" rx="14" fill="#7ec0e0"/><rect x="-36" y="6" width="72" height="30" rx="9" fill="#fff"/>`) + pf(`<path d="M-22,22 a22,22 0 0 1 44,0" stroke="${RED}" stroke-width="6" fill="none"/><path d="M0,22 L10,10" stroke="${INK}" stroke-width="5" stroke-linecap="round"/>`);
  const ruler = () => pf(`<rect x="-14" y="-70" width="28" height="140" rx="7" fill="#e0a02f"/>`) + pf(`<path d="M-14,-50 h14 M-14,-30 h20 M-14,-10 h14 M-14,10 h20 M-14,30 h14 M-14,50 h20" stroke="#7a5a10" stroke-width="4"/>`);
  const arm = () => FOREARM();
  const tewl = () => pf(`<rect x="-9" y="-80" width="18" height="64" rx="8" fill="#a9b4bb"/><rect x="-14" y="-88" width="28" height="14" rx="7" fill="#7f8c95"/>`) + pf(`<rect x="-24" y="-22" width="48" height="26" rx="9" fill="#6f7c85"/><rect x="-24" y="-8" width="48" height="8" rx="4" fill="#4aa3d6"/>`);
  const probe = () => pf(`<rect x="-22" y="-70" width="44" height="60" rx="14" fill="#8a97a0"/><ellipse cx="0" cy="-10" rx="26" ry="10" fill="#5f6b73"/>`) + pf(`<circle cx="0" cy="-44" r="9" fill="#4aa3d6"/>`);
  const tube = () => pf(`<rect x="-22" y="-60" width="44" height="120" rx="20" fill="#eef6fa"/><rect x="-22" y="-60" width="44" height="20" rx="8" fill="#4aa3d6"/>`) + pf(`<path d="M-22,0 H22 V40 a22,22 0 0 1 -44,0 Z" fill="${RED}"/>`);
  const teaspoon = () => pf(`<ellipse cx="0" cy="-44" rx="30" ry="36" fill="#d5dbe0"/><rect x="-7" y="-12" width="14" height="92" rx="7" fill="#d5dbe0"/>`) + pf(`<ellipse cx="0" cy="-44" rx="22" ry="27" fill="${RED}"/>`);
  const thermo = () => pf(`<rect x="-12" y="-62" width="24" height="96" rx="12" fill="#fff"/><circle cy="40" r="24" fill="${RED}"/><rect x="-6" y="-26" width="12" height="62" fill="${RED}"/>`) + pf(`<path d="M16,-40 h14 M16,-22 h14 M16,-4 h14" stroke="#7a7a7a" stroke-width="4"/>`);
  const calendar = () => pf(`<rect x="-44" y="-40" width="88" height="82" rx="10" fill="#fff"/><rect x="-44" y="-40" width="88" height="26" rx="10" fill="${GREEN}"/><rect x="-44" y="-26" width="88" height="12" fill="${GREEN}"/><path d="M-28,2 h16 M-8,2 h16 M12,2 h16 M-28,22 h16 M-8,22 h16" stroke="#9bb8a8" stroke-width="8" stroke-linecap="round"/>`);
  const smile = () => pf(`<circle r="26" fill="#f6c34a"/>`) + pf(`<circle cx="-9" cy="-6" r="3.6" fill="${INK}"/><circle cx="9" cy="-6" r="3.6" fill="${INK}"/><path d="M-12,6 q12,12 24,0" stroke="${INK}" stroke-width="4" fill="none" stroke-linecap="round"/>`);

  /* ---------- shot 1: the cool room ---------- */
  const g1 = mk('g', {}, S);
  prop(g1, pf(`<rect x="730" y="758" width="560" height="34" rx="9" fill="#9a7b58"/><rect x="762" y="792" width="28" height="48" rx="4" fill="#7d6044"/><rect x="1230" y="792" width="28" height="48" rx="4" fill="#7d6044"/>`));
  const bapak = bapakPuppet(g1), ibu = ibuPuppet(g1);
  // cold air from the air conditioner (x 120-640, y 90-210 in the set), streaks drifting to the right and down
  const air = Array.from({ length: 6 }, (_, i) => ({ g: prop(mk('g', {}, g1), pf(`<path d="M0,0 q22,-14 44,0 t44,0 t44,0" stroke="#9fd2ea" stroke-width="10" fill="none" stroke-linecap="round"/>`)), x0: 200 + i * 70 }));
  const chipEnd = item(g1, 800, 100, [{ svg: paper(640, 84, '#fffaf0', 42) }, { svg: `<g transform="translate(-270 0) scale(.62)">${clock()}</g>` }], [{ s: 'Jam kerja selesai', x: 40, y: 17, size: 48 }]);
  const chipRest = item(g1, 800, 100, [{ svg: paper(760, 92, GREEN, 46) }],
    [{ s: 'Istirahat', x: -372, y: 21, a: 'start', size: 60, at: T7.rest, fill: '#fff' }, { s: '15', x: -88, y: 21, a: 'start', size: 60, at: T7.n15, fill: '#fff' }, { s: '–', x: -6, y: 21, a: 'start', size: 60, at: T7.dash, fill: '#fff' },
     { s: '30', x: 44, y: 21, a: 'start', size: 60, at: T7.n30, fill: '#fff' }, { s: 'menit', x: 134, y: 21, a: 'start', size: 60, at: T7.menit, fill: '#fff' }]);
  const chipCool = item(g1, 800, 880, [{ svg: paper(560, 84, '#fffaf0', 42) }, { svg: `<g transform="translate(-220 0) scale(.62)">${flake()}</g>` }], [{ s: 'Ruangan sejuk', x: 30, y: 17, size: 50 }]);

  /* ---------- shot 2: the four steps ---------- */
  const g2 = mk('g', {}, S);
  mk('rect', { x: -100, y: -60, width: 1800, height: 762, fill: '#e3efec' }, g2);   // a plain panel over the wall: the steps read on a quiet ground
  const TX = [230, 610, 990, 1370], CY = 452, CH = 470;
  // the line and its four stations from "empat" (7.99), stretched between the circle centres
  const seg = [0, 1, 2].map(i => ({ g: prop(mk('g', {}, g2), pf(`<rect x="${TX[i]}" y="143" width="${TX[i + 1] - TX[i]}" height="14" rx="7" fill="${GREEN}"/>`)), at: T7.empat + .14 + i * .2 }));
  const dots = TX.map((x, i) => item(g2, x, 150, [{ svg: pf(`<circle r="38" fill="${GREEN}"/>`) }], [{ s: String(i + 1), x: 0, y: 19, size: 54, fill: '#fff' }]));
  const dotAt = [0, 1, 2, 3].map(i => T7.empat + i * .2);
  const title4 = item(g2, 800, 62, [{ svg: paper(900, 78, GREEN, 39) }], [{ s: '4 langkah yang akan dilakukan', x: 0, y: 17, size: 48, fill: '#fff' }]);
  const chip30 = item(g2, 800, 62, [{ svg: paper(540, 78, '#fffaf0', 39) }, { svg: `<g transform="translate(-220 0) scale(.55)">${clock()}</g>` }], [{ s: 'Sekitar 30 menit', x: 30, y: 16, size: 46 }]);
  const stepCard = (i, parts, texts) => item(g2, TX[i], CY, [{ svg: paper(340, CH) }, ...parts], texts);
  const pill = (i, y, w, fill) => ({ svg: `<g transform="translate(0 ${y})">${paper(w, 58, fill, 29)}</g>` });
  const st1 = stepCard(0, [{ svg: `<g transform="translate(0 -78) scale(1.35)">${clip()}</g>`, at: T7.s1 }],
    [{ s: 'Isi', x: 0, y: 92, size: 46, at: T7.s1 }, { s: 'kuesioner', x: 0, y: 140, size: 46, at: T7.s1b }]);
  const st2 = stepCard(1, [{ svg: `<g transform="translate(-48 -74) scale(1.2)">${scale()}</g>`, at: T7.s2 }, { svg: `<g transform="translate(84 -78) scale(1.2)">${ruler()}</g>`, at: T7.s2b }],
    [{ s: 'Timbang &', x: 0, y: 92, size: 46, at: T7.s2 }, { s: 'tinggi badan', x: 0, y: 140, size: 46, at: T7.s2b }]);
  const st3 = stepCard(2, [{ svg: `<g transform="translate(0 -92) scale(.85)">${arm()}</g>`, at: T7.s3 }, { svg: `<g transform="translate(0 -92) scale(.85) translate(10 -4)">${tewl()}</g>`, at: T7.s3alat },
      pill(2, 176, 300, '#d6efdf'), { svg: `<g transform="translate(-122 176) scale(.5)">${smile()}</g>`, at: T7.s3sakit }],
    [{ s: 'Kulit lengan', x: 0, y: 62, size: 46, at: T7.s3 }, { s: 'bawah', x: 0, y: 110, size: 46, at: T7.s3b }, { s: 'Tidak sakit', x: 30, y: 190, size: 40, at: T7.s3sakit, fill: '#1f5a36' }]);
  const st4 = stepCard(3, [{ svg: `<g transform="translate(-66 -88)">${tube()}</g>`, at: T7.s4 }, { svg: `<g transform="translate(58 -78) scale(.9)">${teaspoon()}</g>`, at: T7.s4sdk },
      { svg: `<g transform="translate(0 168)">${paper(280, 58, '#fbe3e0', 29)}</g>`, at: T7.s4sdk }, { svg: `<g transform="translate(122 -194)">${pf(`<circle r="34" fill="${GREEN}"/>`)}</g>`, at: T7.s4sekali }],
    [{ s: 'Darah', x: 0, y: 58, size: 46, at: T7.s4 }, { s: '3–5 mL', x: 0, y: 118, size: 62, at: T7.s4ml, fill: RED }, { s: '± 1 sendok teh', x: 0, y: 183, size: 38, at: T7.s4sdk, fill: '#7a1f1c' },
     { s: '1×', x: 122, y: -179, size: 40, at: T7.s4sekali, fill: '#fff' }]);
  const holder = () => pf(`<rect x="-170" y="-235" width="340" height="470" rx="28" fill="#cfe0dc" opacity=".85"/>`) + `<rect x="-156" y="-221" width="312" height="442" rx="22" fill="none" stroke="#9fb9b3" stroke-width="7" stroke-dasharray="26 16"/>`;
  const place = TX.map((x, i) => item(g2, x, CY, [{ svg: holder() }]));
  const steps = [[st1, T7.s1], [st2, T7.s2], [st3, T7.s3], [st4, T7.s4]];
  const other = item(g2, 800, 800, [{ svg: pf(`<rect x="-640" y="-78" width="1280" height="156" rx="30" fill="#fffaf0"/>`) + `<rect x="-628" y="-66" width="1256" height="132" rx="22" fill="none" stroke="#4aa3d6" stroke-width="6" stroke-dasharray="22 14"/>` },
      { svg: `<g transform="translate(-560 0) scale(.9)">${thermo()}</g>`, at: T7.other }, { svg: `<g transform="translate(560 0) scale(.95)">${calendar()}</g>`, at: T7.cal }],
    [{ s: 'Panas dan udara dapur', x: 0, y: -4, size: 46, at: T7.other }, { s: 'diukur di hari lain', x: 0, y: 52, size: 46, at: T7.otherb, fill: '#1c5f86' }]);

  // continuity: shot 1 holds both seated; a cut to the timeline at 7.0 (before "Lalu ada empat langkah")
  cam.to({ z: 1.06, x: 830, y: 460 }, 0, W(T7.cut - .1));
  cam.cut({ x: 800, y: 450, z: 1 }, W(T7.cut)).to({ z: 1.03, x: 800, y: 455 }, W(T7.cut + .05), 25);

  const ph = { b: 1.1, i: 2.6 };
  // sfx (tools/briefing/add_sfx.py)
  sfx('scene7', 0, 'room', 0.22, { loop: true });
  sfx('scene7', W(T7.s1), 'chime', .5);
  sfx('scene7', W(T7.s2), 'chime', .5);
  sfx('scene7', W(T7.s3), 'chime', .5);
  sfx('scene7', W(T7.s4), 'chime', .5);
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    const s1 = q < W(T7.cut); vis(g1, s1); vis(g2, !s1);
    const T = q * 2.1;
    if (s1) {
      show(chipEnd, q, T7.end, 1, 0); vis(chipEnd.g, q >= W(T7.end) && q < W(T7.rest));
      show(chipRest, q, T7.rest, 1, 0); show(chipCool, q, T7.ruangan, 1, 0);
      // the air: only after "ruangan" (5.64)
      air.forEach((a, i) => {
        const on = q >= W(T7.ruangan), u = (((q - W(T7.ruangan)) * .45 + i / 6) % 1 + 1) % 1;
        vis(a.g, on); if (!on) return;
        tf(a.g, `translate(${(a.x0 + 150 * u + 12 * Math.sin(u * 7 + i)).toFixed(1)} ${(232 + 330 * u).toFixed(1)}) rotate(${(24 * u + 10).toFixed(1)})`);
        a.g.setAttribute('opacity', (Math.sin(Math.PI * u) * .85).toFixed(2));
      });
      // seated, listening to the clock: heads turn a little, they breathe; a sigh of relief at "istirahat"
      const sigh = between(q, W(T7.rest), W(T7.rest + .77)) ? Math.sin(Math.PI * (q - W(T7.rest)) / .77) : 0;
      bapak.pose({ x: 900, y: 800, s: 1, sit: 34, look: .25 * Math.sin(q * .7), eyeX: .3 * Math.sin(q * .7), bob: Math.sin(T) * 2 + sigh * 3, shut: blink(q, ph.b), headR: 2 * Math.sin(q * .6),
        mouth: between(q, W(T7.rest), W(T7.cut - .1)) ? 'smile' : 'X', armL: 4, armR: -4 }, f);
      ibu.pose({ x: 1140, y: 800, s: 1, sit: 34, look: -.3 + .2 * Math.sin(q * .8 + 1), eyeX: -.4, bob: Math.sin(T + 1.4) * 2 + sigh * 3, shut: blink(q, ph.i), headR: -2 * Math.sin(q * .5 + 2),
        mouth: between(q, W(T7.rest), W(T7.cut - .1)) ? 'smile' : 'X', armL: 4, armR: -4 }, f);
    } else {
      dots.forEach((d, i) => show(d, q, dotAt[i], 1, 0));
      seg.forEach(sg => vis(sg.g, q >= W(sg.at)));
      show(title4, q, T7.empat, 1, 0); vis(title4.g, q >= W(T7.empat) && q < W(T7.sekitar)); show(chip30, q, T7.sekitar, 1, 0);
      place.forEach((pl, i) => { show(pl, q, T7.empat + .2 + i * .12, 1, 0); vis(pl.g, q >= W(T7.empat + .2 + i * .12) && q < W(steps[i][1])); });
      steps.forEach(([st, t0]) => show(st, q, t0, 1, .5));
      show(other, q, T7.other, 1, 0);
    }
  });
}
