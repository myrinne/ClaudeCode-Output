/* pengingat.js: the reminder film's own pieces, loaded after shorts.js and the puppet kit (cast.js, cast_briefing.js).
   Paper icons as SVG strings (pf() = the kit's paper-filtered group), centred on 0,0, and the helpers that place them. */
'use strict';
const INK = '#2b2b2b', GREEN = '#3f9d6b';

const IC = {
  arm: () => FOREARM(),
  cream: () => pf(`<path d="M-70,-8 q20,-22 44,-4 q22,16 46,-2 q24,-14 44,6 q-6,26 -36,22 q-30,12 -52,-2 q-24,6 -46,-20 Z" fill="#fffdf6" opacity=".92"/>`),
  faucet: () => pf(`<rect x="-14" y="-64" width="28" height="30" rx="6" fill="#7f8c95"/><path d="M-60,-34 H34 a22,22 0 0 1 22,22 V8 H34 V-12 H-60 Z" fill="#a6b3bb"/><rect x="26" y="4" width="36" height="14" rx="5" fill="#7f8c95"/>`),
  drops: () => pf([0, 1, 2].map(i => `<path d="M${44 + (i - 1) * 3},${34 + i * 34} c0,0 -14,16 -14,24 a14,14 0 0 0 28,0 c0,-8 -14,-24 -14,-24 Z" fill="#4aa3d6"/>`).join('')),
  cig: () => pf(`<g transform="rotate(-28)"><rect x="-80" y="-14" width="116" height="28" rx="5" fill="#f7f3ea"/><rect x="36" y="-14" width="44" height="28" rx="5" fill="#d98a3a"/><rect x="-92" y="-14" width="16" height="28" rx="4" fill="#c8322f"/></g>`)
    + pf(`<path d="M-76,-28 C-100,-60 -60,-72 -82,-100" stroke="#b9bfc4" stroke-width="9" fill="none" stroke-linecap="round"/>`),
  blood: () => pf(`<path d="M0,-44 C0,-44 -36,2 -36,22 A36,36 0 0 0 36,22 C36,2 0,-44 0,-44 Z" fill="${RED}"/>`) + pf(`<path d="M-14,16 q0,14 12,18" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity=".8"/>`),
  clock: () => pf(`<circle r="40" fill="#fff"/><circle r="40" fill="none" stroke="#e0a02f" stroke-width="9"/>`) + pf(`<path d="M0,0 V-24 M0,0 L17,10" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>`),
  losion: () => pf(`<rect x="-20" y="-6" width="40" height="42" rx="9" fill="#7ec0e0"/><rect x="-8" y="-24" width="16" height="18" rx="4" fill="#4a7f99"/><rect x="-8" y="-30" width="30" height="9" rx="4" fill="#4a7f99"/>`),
  pelembap: () => pf(`<rect x="-30" y="-6" width="60" height="34" rx="9" fill="#f2a6c0"/><rect x="-33" y="-20" width="66" height="16" rx="6" fill="#fff"/>`),
  minyak: () => pf(`<rect x="-18" y="-10" width="36" height="46" rx="10" fill="#e8b923"/><rect x="-8" y="-28" width="16" height="20" rx="4" fill="#9a7a10"/><path d="M0,2 c0,0 -9,10 -9,15 a9,9 0 0 0 18,0 c0,-5 -9,-15 -9,-15 Z" fill="#fff4c4"/>`),
  tabir: () => pf(`<circle r="20" fill="#f08a2c"/>${Array.from({ length: 8 }, (_, i) => { const a = i * Math.PI / 4; return `<path d="M${(Math.cos(a) * 28).toFixed(1)},${(Math.sin(a) * 28).toFixed(1)} L${(Math.cos(a) * 38).toFixed(1)},${(Math.sin(a) * 38).toFixed(1)}" stroke="#f08a2c" stroke-width="7" stroke-linecap="round"/>`; }).join('')}`),
  vitC: () => pf(`<circle r="30" fill="#f08a2c"/>`) + `<text y="14" text-anchor="middle" font-size="40" font-weight="800" font-family="Arial,sans-serif" fill="#fff">C</text>`,
  vitE: () => pf(`<circle r="30" fill="#e8c030"/>`) + `<text y="14" text-anchor="middle" font-size="40" font-weight="800" font-family="Arial,sans-serif" fill="#fff">E</text>`,
  gluta: () => pf(`<g transform="rotate(-35)"><rect x="-34" y="-15" width="68" height="30" rx="15" fill="#fff"/><path d="M-34,0 a15,15 0 0 1 15,-15 H0 V15 H-19 a15,15 0 0 1 -15,-15 Z" fill="#9b6bc2"/></g>`),
  syrup: () => pf(`<rect x="-18" y="-14" width="36" height="50" rx="9" fill="#5aa77a"/><rect x="-10" y="-30" width="20" height="18" rx="4" fill="#2f6f4c"/><rect x="-12" y="2" width="24" height="18" rx="4" fill="#f4f1ea"/>`),
  pill: () => pf(`<g transform="rotate(-35)"><rect x="-56" y="-22" width="112" height="44" rx="22" fill="#fff"/><path d="M-56,0 a22,22 0 0 1 22,-22 H0 V22 H-34 a22,22 0 0 1 -22,-22 Z" fill="#9b6bc2"/></g>`)
    + pf(`<circle cx="46" cy="40" r="22" fill="#f08a2c"/><circle cx="-26" cy="50" r="18" fill="#e8c030"/>`),
  check: () => `<g filter="url(#paper)"><circle r="46" fill="${GREEN}"/></g><path d="M-22,2 L-6,19 L24,-16" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
  thumb: () => pf(`<g transform="scale(1.5)"><rect x="-10" y="-54" width="20" height="46" rx="10" fill="#f2efe6"/></g>`),
  no: r => pf(`<circle r="${r}" fill="none" stroke="${RED}" stroke-width="${Math.max(16, r / 6)}"/><path d="M${-r * .7},${-r * .7} L${r * .7},${r * .7}" stroke="${RED}" stroke-width="${Math.max(16, r / 6)}" stroke-linecap="round"/>`),
};

// a paper icon at (x, y), scale sc, popping in at t0 (there from the first frame when t0 <= .01)
function icon(g, svg, x, y, sc, t0, { from = .55, r = 0 } = {}) {
  const e = G(g, { x, y, s: sc * from, r, o: 0 });
  e.innerHTML = typeof svg === 'function' ? svg() : svg;
  if (t0 <= .01) put(e, { s: sc, o: 1 }); else tw(e, { s: sc, o: 1 }, t0, .26, out);
  return e;
}
// the step badge, top left
function badge(g, n, t0 = .05) {
  const e = G(g, { x: 120, y: 225, s: .6, o: 0 });
  mk('circle', { r: 68, fill: GREEN }, e);
  T(e, String(n), { x: 0, y: 32, size: 96, fill: '#fff', font: SANS, weight: 600, anchor: 'middle' });
  tw(e, { s: 1, o: 1 }, t0, .22, out);
}
// the big "24 JAM" with a chime when it lands
function bigHours(g, m, num) {
  word(g, num, CX, 620, m('num'), { size: 420, fill: RED, maxW: 760 });
  word(g, 'JAM', CX, 792, m('num', .45), { size: 150, fill: DARK });
  sfx(BEAT_ID, m('num'), 'chime', .6);
}
