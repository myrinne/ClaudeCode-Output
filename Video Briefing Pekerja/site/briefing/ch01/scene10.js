'use strict';
/* Adegan 10: kerahasiaan. Set 'kertas'. Tanpa tokoh yang tampil (narator saja).
   Shot 1 (0-5.5): label nama dicoret, lembar data "Kode 017", lemari terkunci.
   Shot 2 (5.5-13.7): grafik batang gabungan, "tidak bisa ditelusuri", atasan dengan tanda larangan, izin tertulis.
   Shot 3 (13.7-17.5): tabung darah, "hanya untuk pemeriksaan ini".
   Memakai pembantu s8T, s8Card, s8Head, S8_CHECK, S8_BAN dari scene8.js. Waktu kata = detik klip adegan + PRE10. */
const PRE10 = 0.8;

const S10_TAG = `<g filter="url(#paper)"><rect x="-150" y="-52" width="300" height="104" rx="14" fill="#fffdf4"/><rect x="-150" y="-52" width="300" height="30" rx="14" fill="#3d7f8f"/><rect x="-150" y="-36" width="300" height="14" fill="#3d7f8f"/><rect x="-118" y="22" width="236" height="14" rx="7" fill="#d8d3c4"/></g>`;
const S10_SHEET = `<g filter="url(#paper)"><rect x="-250" y="-290" width="500" height="580" rx="16" fill="#fffdf4"/><rect x="-250" y="-290" width="500" height="92" rx="16" fill="#3d7f8f"/><rect x="-250" y="-250" width="500" height="52" fill="#3d7f8f"/>
  <rect x="-210" y="-120" width="300" height="22" rx="11" fill="#d8d3c4"/><rect x="-210" y="-70" width="380" height="22" rx="11" fill="#d8d3c4"/><rect x="-210" y="-20" width="240" height="22" rx="11" fill="#d8d3c4"/><rect x="-210" y="30" width="340" height="22" rx="11" fill="#d8d3c4"/><rect x="-210" y="80" width="280" height="22" rx="11" fill="#d8d3c4"/></g>`;
const S10_CABINET = `<g filter="url(#paper)"><rect x="-110" y="-190" width="220" height="380" rx="12" fill="#8a96a0"/><rect x="-96" y="-176" width="94" height="170" rx="6" fill="#a4afb8"/><rect x="2" y="-176" width="94" height="170" rx="6" fill="#a4afb8"/><rect x="-96" y="6" width="94" height="170" rx="6" fill="#a4afb8"/><rect x="2" y="6" width="94" height="170" rx="6" fill="#a4afb8"/><rect x="-18" y="-120" width="10" height="46" rx="4" fill="#6d7a84"/><rect x="8" y="-120" width="10" height="46" rx="4" fill="#6d7a84"/></g>`;
const S10_LOCK = `<g filter="url(#paper)"><path d="M-26,-6 v-30 a26,26 0 0 1 52,0 v30" fill="none" stroke="#c9a23c" stroke-width="12"/><rect x="-44" y="-8" width="88" height="70" rx="14" fill="#e0b83f"/><circle cx="0" cy="22" r="9" fill="#7a5d12"/><rect x="-4" y="26" width="8" height="22" rx="3" fill="#7a5d12"/></g>`;
const S10_BOSS = `<g filter="url(#paper)"><rect x="-46" y="-8" width="92" height="120" rx="28" fill="#4a5a78"/><path d="M-16,-8 L0,40 L16,-8 Z" fill="#fafafa"/><path d="M-6,0 L6,0 L9,52 L0,66 L-9,52 Z" fill="#c8322f"/><circle cx="0" cy="-48" r="34" fill="#e8be98"/><path d="M-34,-52 a34,32 0 0 1 68,0 q-34,-18 -68,0 Z" fill="#2a1f1a"/></g>`;
const S10_PERMIT = `<g filter="url(#paper)"><rect x="-80" y="-100" width="160" height="200" rx="10" fill="#fffdf4"/><path d="M-52,-62 h104 M-52,-36 h104 M-52,-10 h70" stroke="#c9c3b3" stroke-width="8" stroke-linecap="round"/><path d="M-52,56 q18,-34 30,0 t30,0 t30,-6" stroke="#3d7f8f" stroke-width="7" fill="none" stroke-linecap="round"/><rect x="56" y="-4" width="16" height="84" rx="7" fill="#e8833a" transform="rotate(32 64 40)"/></g>`;
const S10_MAGNIFIER = `<g filter="url(#paper)"><circle cx="-14" cy="-14" r="48" fill="#e8f3f6" stroke="#7b8c94" stroke-width="14"/><rect x="26" y="26" width="18" height="70" rx="8" fill="#7b8c94" transform="rotate(-45 35 61)"/></g>`;
const S10_PERSON = `<g filter="url(#paper)"><rect x="-40" y="-6" width="80" height="100" rx="30" fill="#9aa5ad"/><circle cx="0" cy="-42" r="32" fill="#b5bec5"/></g>`;
const S10_TUBE = `<g filter="url(#paper)"><rect x="-34" y="-120" width="68" height="200" rx="30" fill="#e8f3f6"/><rect x="-34" y="-20" width="68" height="100" rx="30" fill="#c8322f"/><rect x="-34" y="-20" width="68" height="40" fill="#c8322f"/><rect x="-42" y="-132" width="84" height="26" rx="10" fill="#e8833a"/></g>`;

function scene10(p, D) {
  const W = t => PRE10 + t, cam = paperCam(p, 'kertas'), items = [];
  const add = (svg, t0, x, y, s = 1, r = 0, t1 = 1e9) => { const g = prop(cam.stage, svg); vis(g, false); items.push({ g, t0: W(t0), t1: W(t1), x, y, s, r, k: items.length + 10 }); return g; };
  const C1 = 5.5, C2 = 13.7;   // potongan antar shot
  // ----- shot 1: nama tidak ditulis, hanya kode; lemari terkunci -----
  add(S10_TAG + s8T('Nama', 0, 8, 46), 0.58, 330, 400, 1.15, -3, C1);
  add(`<g transform="scale(.62)">${S8_BAN}</g>`, 1.5, 330, 400, 1, 0, C1);
  add(s8T('Nama Bapak dan Ibu', 0, 0, 40, '#2b2b2b'), 0.22, 330, 520, 1, 0, C1);
  add(`<g transform="scale(.95)">${S10_SHEET}</g>`, 2.42, 900, 450, 1, 0, C1);
  add(s8T('LEMBAR DATA', 0, 0, 46, '#fff'), 2.42, 900, 240, 1, 0, C1);
  add(s8Card(330, 130, '#3f9d6b') + s8T('Kode 017', 0, 28, 76, '#fff'), 3.92, 905, 480, 1, -3, C1);
  add(`<g transform="scale(.95)">${S10_CABINET}</g><g transform="translate(0,20)">${S10_LOCK}</g>`, 4.45, 1385, 470, 1, 0, C1);
  // ----- shot 2: gabungan, tidak ditelusuri, atasan -----
  const bars = [[-120, 90, '#6fb1c4'], [-40, 170, '#3d7f8f'], [40, 130, '#6fb1c4'], [120, 220, '#3d7f8f']];
  add(s8Card(480, 400, '#fffdf4') + `<rect x="-190" y="150" width="380" height="10" rx="5" fill="#c9c3b3"/>`, 5.73, 400, 440, 1, 0, C2);
  const barG = add(bars.map(([x, , c], i) => `<rect class="b${i}" x="${x - 26}" y="150" width="52" height="0" rx="6" fill="${c}"/>`).join(''), 6.82, 400, 440, 1, 0, C2);
  add(s8T('Hasil gabungan', 0, 0, 46), 6.25, 400, 690 - 10, 1, 0, C2);
  add(`<g transform="translate(-60,0) scale(1.25)">${S10_PERSON}</g>`, 9.03, 890, 420, 1, 0, C2);
  add(`<g transform="scale(1.3)">${S10_MAGNIFIER}</g>`, 8.36, 930, 370, 1, 0, C2);
  add(`<g transform="scale(.95)">${S8_BAN}</g>`, 9.5, 880, 420, 1, 0, C2);
  add(s8T('Tidak bisa ditelusuri', 0, 0, 42), 8.36, 885, 640, 1, 0, C2);
  add(`<g transform="scale(1.15)">${S10_BOSS}</g>`, 11.2, 1300, 330, 1, 0, C2);
  add(`<g transform="scale(.62)">${S8_BAN}</g>`, 11.69, 1300, 350, 1, 0, C2);
  add(s8T('ke atasan', 0, 0, 42), 11.2, 1300, 490, 1, 0, C2);
  add(`<g transform="scale(.62)">${S10_PERMIT}</g>`, 12.03, 1210, 625, 1, -4, C2);
  add(s8T('Izin tertulis', 0, 0, 42, '#3f7d56'), 12.03, 1410, 640, 1, 0, C2);
  // ----- shot 3: darah hanya untuk pemeriksaan ini -----
  add(`<g transform="scale(1.4)">${S10_TUBE}</g>`, 14.04, 560, 450, 1, 6);
  add(s8Card(640, 220, '#fffdf4') + s8T('Hanya untuk', 0, -8, 62), 14.43, 1070, 400);
  add(s8T('pemeriksaan ini', 0, 0, 62, '#3f7d56'), 15.63, 1070, 470);
  add(`<g transform="scale(1.1)">${S8_CHECK}</g>`, 16.28, 1070, 600);

  cam.to({ z: 1.035 }, 0, W(C1)); cam.cut({ x: 800, y: 450, z: 1 }, W(C1)); cam.to({ z: 1.035 }, W(C1), 8.2);
  cam.cut({ x: 800, y: 450, z: 1 }, W(C2)); cam.to({ z: 1.04 }, W(C2), 4.5);
  const rects = [0, 1, 2, 3].map(i => barG.querySelector('.b' + i));

  stopClock(D, (q, f) => {
    cam.apply(q, f);
    const j = k => .7 * jit(f >> 1, k);
    for (const it of items) {
      if (q < it.t0 || q >= it.t1) { vis(it.g, false); continue; }
      const k = span(q, it.t0, it.t0 + .22), sc = it.s * (.55 + .45 * k + .08 * Math.sin(k * Math.PI));
      vis(it.g, true); it.g.setAttribute('opacity', k.toFixed(2));
      tf(it.g, `translate(${(it.x + j(it.k)).toFixed(1)},${(it.y + j(it.k + 50)).toFixed(1)}) rotate(${it.r}) scale(${sc.toFixed(3)})`);
    }
    // batang tumbuh pada "gabungan"
    bars.forEach(([, h], i) => { const g = span(q, W(6.82 + .12 * i), W(7.3 + .12 * i)) * h; rects[i].setAttribute('height', g.toFixed(1)); rects[i].setAttribute('y', (150 - g).toFixed(1)); });
  });
}
