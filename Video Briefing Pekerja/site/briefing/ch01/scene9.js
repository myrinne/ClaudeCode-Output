'use strict';
/* Adegan 9: rasa tidak nyaman dan penanganannya. Set 'ruang'.
   Shot 1 (0-9.5): tiga kartu insert: nyeri ringan + plester, memar kecil yang mengecil, jarum sekali pakai + petugas terlatih.
   Shot 2 (9.5-16): potong ke dokter Vidya memegang telepon; teks "Ada keluhan? / Hubungi saya / Tanpa biaya"; bibirnya mengikuti suara.
   Memakai pembantu s8T, s8Card, s8Head, S8_CHECK dari scene8.js (file ini milik paket yang sama, dimuat lebih dulu).
   Waktu kata: detik klip adegan (narration.id.words.txt) ditambah PRE9. */
const PRE9 = 0.8;

const S9_ARM = `<g filter="url(#paper)"><rect x="-130" y="-34" width="200" height="68" rx="32" fill="#e8be98"/><rect x="50" y="-42" width="80" height="84" rx="16" fill="#4f9a6a"/><path d="M-110,-6 q24,-10 48,0" stroke="#d1a07a" stroke-width="4" fill="none" stroke-linecap="round"/></g>`;
const S9_PLASTER = `<g filter="url(#paper)"><rect x="-34" y="-15" width="68" height="30" rx="14" fill="#f0d3a8" transform="rotate(-14)"/><circle cx="-6" cy="-2" r="2.6" fill="#d3b184"/><circle cx="6" cy="-4" r="2.6" fill="#d3b184"/><circle cx="0" cy="3" r="2.6" fill="#d3b184"/></g>`;
const S9_SPARK = `<g filter="url(#paper)"><path d="M0,-34 L8,-10 L32,-14 L14,4 L26,28 L0,14 L-26,28 L-14,4 L-32,-14 L-8,-10 Z" fill="#f5c542"/></g>`;
const S9_SYRINGE = `<g filter="url(#paper)"><rect x="-84" y="-34" width="168" height="68" rx="20" fill="#f4f7f8"/><rect x="-70" y="-14" width="104" height="28" rx="9" fill="#cfe3ea"/><rect x="-96" y="-30" width="16" height="60" rx="6" fill="#9fb4bd"/><rect x="34" y="-7" width="54" height="14" rx="5" fill="#9fb4bd"/><path d="M88,0 L140,0" stroke="#7b8c94" stroke-width="6" stroke-linecap="round"/></g>`;
const S9_PETUGAS = `<g filter="url(#paper)"><rect x="-34" y="-24" width="68" height="84" rx="22" fill="#fafafa"/>${s8Head(0, -48)}<path d="M-19,-64 h38 v-10 q-19,-16 -38,0 Z" fill="#fafafa"/></g><path d="M0,-6 v30 M-15,9 h30" stroke="#c8322f" stroke-width="9" stroke-linecap="round"/>`;
const S9_PHONE = `<g filter="url(#paper)"><rect x="-30" y="-88" width="60" height="104" rx="12" fill="#2f3b45"/><rect x="-24" y="-80" width="48" height="76" rx="6" fill="#8fd3e8"/><circle cx="0" cy="6" r="4" fill="#8fd3e8"/><circle cx="0" cy="-42" r="13" fill="#3f9d6b"/><path d="M-6,-48 q-1,12 12,9 l2,-4 l-5,-3 l-2,2 q-3,-1 -3,-4 l2,-2 l-3,-5 Z" fill="#fff"/></g>`;

function scene9(p, D) {
  const W = t => PRE9 + t, cam = paperCam(p, 'ruang', {}, { after: 'bench' }), items = [];
  const add = (svg, t0, x, y, s = 1, r = 0, t1 = 1e9) => { const g = prop(cam.stage, svg); vis(g, false); items.push({ g, t0: W(t0), t1: W(t1), x, y, s, r, k: items.length + 10 }); return g; };
  const CUT = 9.5;   // shot 1 -> shot 2
  // ----- shot 1: tiga kartu -----
  const tile = (x, fill, t) => add(s8Card(440, 440, fill), t, x, 460, 1, 0, CUT);
  tile(300, '#eaf3f5', 0.22); tile(800, '#eaf3f5', 3.19); tile(1300, '#eaf3f5', 5.75);
  // kartu 1: darah diambil, nyeri ringan, plester kecil
  add(`<g transform="scale(1.3)">${S9_ARM}</g>`, 0.22, 300, 400, 1, 0, CUT);
  add(`<g filter="url(#paper)"><path d="M0,-30 C20,-2 26,10 0,28 C-26,10 -20,-2 0,-30 Z" fill="#c8322f"/></g>`, 0.96, 255, 400, 1.1, 0, CUT);
  add(S9_SPARK, 1.77, 392, 330, .9, 12, CUT);
  add(`<g transform="scale(1.3)">${S9_PLASTER}</g>`, 2.06, 330, 410, 1.1, 0, CUT);
  add(s8T('Nyeri ringan', 0, 0, 46), 2.06, 300, 590, 1, 0, CUT);
  // kartu 2: memar kecil yang mengecil sendiri
  add(`<g transform="scale(1.3)">${S9_ARM}</g>`, 3.19, 800, 400, 1, 0, CUT);
  const bruise = add(`<ellipse class="bz" rx="26" ry="20" fill="#8b6fa8" opacity=".85"/><ellipse class="bz2" cx="-6" cy="-4" rx="14" ry="10" fill="#6f5590" opacity=".6"/>`, 3.19, 790, 408, 1, 0, CUT);
  add(s8T('Memar kecil', 0, 0, 46), 3.19, 800, 590, 1, 0, CUT);
  add(s8T('hilang sendiri', 0, 0, 40, '#3f7d56'), 3.99, 800, 640, 1, 0, CUT);
  add(`<g transform="scale(.6)">${S8_CHECK}</g>`, 4.38, 960, 640, 1, 0, CUT);
  // kartu 3: jarum sekali pakai, petugas terlatih
  add(`<g transform="translate(-22,0) scale(.95)">${S9_SYRINGE}</g>`, 5.75, 1215, 400, 1, -8, CUT);
  add(s8T('Sekali pakai', 0, 0, 46), 6.36, 1300, 590, 1, 0, CUT);
  add(`<g filter="url(#paper)"><circle r="34" fill="#e8833a"/></g>` + s8T('1×', 0, 14, 38, '#fff'), 6.36, 1445, 320, 1, 0, CUT);
  add(`<g transform="scale(.95)">${S9_PETUGAS}</g>`, 7.88, 1435, 410, 1, 0, CUT);
  add(s8T('Petugas terlatih', 0, 0, 40), 7.88, 1300, 640, 1, 0, CUT);
  // ----- shot 2: dokter dan telepon -----
  const dok = dokterPuppet(cam.stage, { holds: { phone: S9_PHONE } });
  add(s8Card(540, 110, '#fffdf4') + s8T('Ada keluhan?', 0, 18, 56), 10.6, 430, 250, 1, 0);
  add(s8Card(540, 130, '#e3f1e8') + `<g transform="translate(-205,0) scale(.55)">${S9_PHONE}</g>` + s8T('Hubungi saya', 30, 20, 56), 11.47, 430, 392, 1, 0);
  add(s8Card(540, 150, '#3f9d6b') + s8T('Tanpa biaya', 0, 20, 70, '#fff'), 14.15, 430, 535, 1, 0);
  add(`<g transform="scale(.7)">${S8_CHECK}</g>`, 15.0, 760, 535, 1, 0);

  cam.cut({ x: 800, y: 450, z: 1 }, 0); cam.to({ z: 1.03 }, 0, W(CUT));
  cam.cut({ x: 800, y: 450, z: 1 }, W(CUT)); cam.to({ z: 1.04 }, W(CUT), 7);
  const bz = bruise.querySelector('.bz'), bz2 = bruise.querySelector('.bz2');

  // sfx (tools/briefing/add_sfx.py)
  sfx('scene9', 0, 'room', 0.22, { loop: true });
  sfx('scene9', 14.95, 'chime', .5);
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    const j = k => .7 * jit(f >> 1, k);
    for (const it of items) {
      if (q < it.t0 || q >= it.t1) { vis(it.g, false); continue; }
      const k = span(q, it.t0, it.t0 + .22), sc = it.s * (.55 + .45 * k + .08 * Math.sin(k * Math.PI));
      vis(it.g, true); it.g.setAttribute('opacity', k.toFixed(2));
      tf(it.g, `translate(${(it.x + j(it.k)).toFixed(1)},${(it.y + j(it.k + 50)).toFixed(1)}) rotate(${it.r}) scale(${sc.toFixed(3)})`);
    }
    // memar: tumbuh sedikit pada "memar kecil", lalu mengecil dan hilang dari "hilang" sampai "sendiri"
    const grow = span(q, W(3.19), W(3.6)), fade = 1 - span(q, W(3.99), W(5.6)), m = grow * fade;
    bz.setAttribute('rx', (26 * m).toFixed(1)); bz.setAttribute('ry', (20 * m).toFixed(1));
    bz2.setAttribute('rx', (14 * m).toFixed(1)); bz2.setAttribute('ry', (10 * m).toFixed(1));
    // dokter: hanya di shot 2
    const on = q >= W(CUT);
    vis(dok.g, on);
    if (on) {
      const sp = lips(q, 'scene9', PRE9, 's09a'), talking = sp !== 'X';
      const o = { x: 1010, y: 800, s: 1.2, look: -.35 + .05 * Math.sin(q), mouth: sp, shut: blinking(q, [W(10.0), W(12.6), W(14.9)]),
        bob: 3 * Math.sin(q * 2.2), headR: talking ? 2 * Math.sin(q * 3) : 0, armL: 8, hold: 'phone', brow: 0, armFrontR: true };
      // telepon diangkat di samping badan, di luar helai rambut, lengan di depan kepala supaya terlihat
      dok.pose({ ...o, ...dok.aim(o, 'R', [1175, 600 + 4 * Math.sin(q * 2)]) }, f);
    }
  });
}
