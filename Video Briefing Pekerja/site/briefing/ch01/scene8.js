'use strict';
/* Adegan 8: cara mengisi kuesioner. Set 'kertas'. Tanpa tokoh; narator saja.
   Bentuk: s8a (0-11) formulir + aturan, s8b (11-22.2) hitung 8 = 5+2+1, s8c (22.2-25.4) tidak ada benar/salah.
   Waktu kata (detik klip adegan, ditambah PRE8) dari content/briefing/ch01/narration.id.words.txt; waktu muncul = kata - 0.22. */
const PRE8 = 0.8;
const T8 = {
  form: 0.0, shift: 2.5,                      // formulir jatuh; geser ke kiri sebelum "jam kerja"
  area: 4.27, jenis: 5.0,                      // "area", "jenis"
  rule: 6.66, eq: 7.47, lama: 8.01, clock: 8.26,   // "Jumlahnya", "sama", "lama", "kerja"
  C1: 11.0, C2: 22.2,                          // potongan antar shot
  kerja: 11.59, jam8: 11.92,                   // "kerja", "8"
  n5: 12.88, memasak: 13.39, n2: 14.15, pemorsian: 14.56, n1: 15.41, persiapan: 16.06,
  eqCard: 17.44, eqDone: 18.06,                // "Jumlahnya" .. "delapan"
  approx: 19.39,                               // "Perkiraan"
  tidak: 22.3, benar: 23.24, salah: 23.97, ban: 24.3
};

const S8_FONT = "'Segoe UI','Helvetica Neue',Arial,sans-serif";
const s8T = (s, x, y, size, fill = '#2b2b2b', anchor = 'middle') =>
  `<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="${S8_FONT}" font-weight="800" font-size="${size}" fill="${fill}">${s}</text>`;
// Kartu besar tanpa filter kertas (membaking bitmap besar terlalu berat): bayangan dan tepi digambar langsung.
const s8Rect = (x, y, w, h, rx, fill) => `<rect x="${x + 3}" y="${y + 5}" width="${w}" height="${h}" rx="${rx}" fill="#2a1608" opacity=".24"/><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}"/>`;
const s8Card = (w, h, fill = '#fffdf4', rx = 22) => s8Rect(-w / 2, -h / 2, w, h, rx, fill);

// ---- ikon (pusat di 0,0, kira-kira 100 x 100) ----
const S8_CLOCK = `<g filter="url(#paper)"><circle r="46" fill="#fffdf4" stroke="#3d7f8f" stroke-width="9"/><path d="M0,0 V-27 M0,0 L19,9" stroke="#2b2b2b" stroke-width="7" stroke-linecap="round" fill="none"/><circle r="5" fill="#2b2b2b"/></g>`;
const S8_POT = `<g filter="url(#paper)"><rect x="-44" y="-10" width="88" height="56" rx="11" fill="#6b7a85"/><rect x="-52" y="-18" width="104" height="14" rx="7" fill="#8c9aa5"/><rect x="-66" y="6" width="16" height="11" rx="5" fill="#8c9aa5"/><rect x="50" y="6" width="16" height="11" rx="5" fill="#8c9aa5"/><rect x="-9" y="-30" width="18" height="13" rx="6" fill="#8c9aa5"/></g><path d="M-18,-40 q-8,-10 0,-20 M14,-40 q-8,-10 0,-20" stroke="#aab6bd" stroke-width="5" fill="none" stroke-linecap="round"/>`;
const S8_TRAY = `<g filter="url(#paper)"><rect x="-54" y="-24" width="108" height="64" rx="9" fill="#c4ccd1"/><rect x="-46" y="-16" width="40" height="48" rx="6" fill="#f0c25a"/><rect x="-2" y="-16" width="46" height="21" rx="6" fill="#7bb369"/><rect x="-2" y="9" width="46" height="23" rx="6" fill="#d9694f"/></g>`;
const S8_PREP = `<g filter="url(#paper)"><rect x="-54" y="6" width="108" height="38" rx="7" fill="#c89b6a"/><path d="M-40,-16 L30,-4 L-40,12 Z" fill="#ee8a2b"/><path d="M-40,-16 L-58,-26 L-50,-6 Z" fill="#5aa05a"/><rect x="26" y="-42" width="14" height="46" rx="5" fill="#9aa5ad" transform="rotate(22 33 -20)"/><rect x="40" y="-4" width="12" height="30" rx="5" fill="#7a5233" transform="rotate(22 46 10)"/></g>`;
const S8_CHECK = `<g filter="url(#paper)"><circle r="46" fill="#3f9d6b"/></g><path d="M-22,2 L-6,19 L24,-16" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
const S8_CROSS = `<g filter="url(#paper)"><circle r="46" fill="#c8322f"/></g><path d="M-19,-19 L19,19 M19,-19 L-19,19" stroke="#fff" stroke-width="12" stroke-linecap="round"/>`;
const S8_BAN = `<g filter="url(#paper)"><path fill-rule="evenodd" fill="#c8322f" d="M0,-122 a122,122 0 1,0 0.1,0 Z M0,-102 a102,102 0 1,1 -0.1,0 Z"/><rect x="-108" y="-9" width="216" height="18" rx="6" fill="#c8322f" transform="rotate(-45)"/></g>`;
// orang sederhana: kepala, badan hijau, celana; pose lewat tambahan
const s8Head = (x, y) => `<circle cx="${x}" cy="${y}" r="19" fill="#e8be98"/><path d="M${x - 19},${y - 4} a19,17 0 0 1 38,0 q-19,-9 -38,0 Z" fill="#2a1f1a"/>`;
const S8_SIT = `<g filter="url(#paper)"><rect x="-36" y="34" width="52" height="9" rx="4" fill="#a8774a"/><rect x="-28" y="43" width="8" height="22" fill="#a8774a"/><rect x="2" y="43" width="8" height="22" fill="#a8774a"/>
  <rect x="-24" y="-30" width="40" height="66" rx="14" fill="#4f9a6a"/><rect x="-6" y="22" width="48" height="15" rx="7" fill="#34584a"/><rect x="30" y="22" width="15" height="46" rx="7" fill="#34584a"/>${s8Head(-4, -50)}<rect x="-8" y="-6" width="38" height="12" rx="6" fill="#4f9a6a"/></g>`;
const S8_WATCH = `<g filter="url(#paper)"><rect x="-22" y="20" width="16" height="50" rx="7" fill="#34584a"/><rect x="2" y="20" width="16" height="50" rx="7" fill="#34584a"/><rect x="-30" y="-30" width="48" height="60" rx="16" fill="#4f9a6a"/>${s8Head(-6, -52)}
  <rect x="14" y="-12" width="14" height="40" rx="7" fill="#4f9a6a" transform="rotate(-30 20 -10)"/><rect x="22" y="-34" width="38" height="50" rx="5" fill="#f4f1ea"/><path d="M29,-22 h24 M29,-12 h24 M29,-2 h16" stroke="#9aa5ad" stroke-width="4"/></g>
  <path d="M-52,-72 q22,-20 44,0 q-22,20 -44,0 Z" fill="#fffdf4" stroke="#2b2b2b" stroke-width="4"/><circle cx="-30" cy="-72" r="7" fill="#2b2b2b"/>`;
const S8_LIFT = `<g filter="url(#paper)"><rect x="-30" y="22" width="16" height="48" rx="7" fill="#34584a"/><rect x="-6" y="22" width="16" height="48" rx="7" fill="#34584a"/><rect x="-40" y="-26" width="52" height="58" rx="16" fill="#4f9a6a" transform="rotate(10 -14 0)"/>${s8Head(-14, -48)}
  <rect x="-8" y="-6" width="52" height="15" rx="7" fill="#4f9a6a"/><rect x="2" y="-4" width="74" height="54" rx="12" fill="#6b7a85"/><rect x="-4" y="-12" width="86" height="14" rx="7" fill="#8c9aa5"/><rect x="-14" y="10" width="14" height="10" rx="5" fill="#8c9aa5"/><rect x="76" y="10" width="14" height="10" rx="5" fill="#8c9aa5"/></g>`;
const S8_PUSH = `<g filter="url(#paper)"><rect x="-58" y="22" width="16" height="48" rx="7" fill="#34584a" transform="rotate(8 -50 22)"/><rect x="-36" y="22" width="16" height="48" rx="7" fill="#34584a" transform="rotate(-14 -28 22)"/><rect x="-62" y="-26" width="52" height="58" rx="16" fill="#4f9a6a" transform="rotate(16 -36 0)"/>${s8Head(-34, -46)}
  <rect x="-30" y="-8" width="56" height="14" rx="7" fill="#4f9a6a" transform="rotate(10 -30 0)"/><rect x="18" y="-2" width="62" height="46" rx="6" fill="#a8774a"/><rect x="24" y="-26" width="22" height="26" rx="3" fill="#d9a35a"/><rect x="50" y="-20" width="24" height="20" rx="3" fill="#e8c27a"/><circle cx="34" cy="56" r="13" fill="#555"/><circle cx="70" cy="56" r="13" fill="#555"/></g>`;

function scene8(p, D) {
  const W = t => PRE8 + t, cam = paperCam(p, 'kertas'), items = [];
  const add = (svg, t0, x, y, s = 1, r = 0, t1 = 1e9, parent = cam.stage) => {
    const g = prop(parent, svg); vis(g, false); items.push({ g, t0: W(t0), t1: W(t1), x, y, s, r, k: items.length + 10 }); return g;
  };
  // ----- formulir besar (satu benda yang pindah tempat antar shot) -----
  const row = (y, w) => `<rect x="-270" y="${y - 12}" width="${w}" height="22" rx="11" fill="#d8d3c4"/><rect x="130" y="${y - 26}" width="140" height="46" rx="9" fill="#fff" stroke="#bdb7a5" stroke-width="4"/>`;
  const boxes = y => [110, 176, 242].map(x => `<rect x="${x}" y="${y - 28}" width="54" height="54" rx="9" fill="#fff" stroke="#bdb7a5" stroke-width="4"/>`).join('');
  const formG = prop(cam.stage, `${s8Rect(-310, -300, 620, 600, 16, '#fffdf4')}<path d="M-310,-216 V-284 a16,16 0 0 1 16,-16 H294 a16,16 0 0 1 16,16 V-216 Z" fill="#3d7f8f"/><g>
    ${row(-165, 330)}${row(-100, 250)}${row(-35, 380)}<rect x="-270" y="205" width="300" height="22" rx="11" fill="#d8d3c4"/><rect x="-270" y="245" width="210" height="22" rx="11" fill="#d8d3c4"/></g>
    ${s8T('KUESIONER', 0, -233, 52, '#fff')}${s8T('Area kerja', -282, 52, 44, '#2b2b2b', 'start')}${s8T('Jenis kegiatan', -282, 142, 44, '#2b2b2b', 'start')}
    <g filter="url(#paper)">${boxes(40)}${boxes(130)}</g>`);
  vis(formG, false);
  const mark = (y) => `<rect x="-304" y="${y}" width="608" height="76" rx="12" fill="#ffd84a" opacity=".8"/>`;
  // sorotan di formulir (shot 1): muncul pada "area" dan "jenis"
  const mA = add(mark(2), T8.area, 0, 0, 1, 0, T8.C1, formG), mB = add(mark(92), T8.jenis, 0, 0, 1, 0, T8.C1, formG);
  formG.insertBefore(mA, formG.children[2]); formG.insertBefore(mB, formG.children[2]);   // di bawah teks
  // ----- shot 1: aturan penting di kanan -----
  const chip = (w, h, fill) => s8Card(w, h, fill, 20);
  add(chip(370, 92, '#fff1d6') + `<g transform="translate(-135,0) scale(.55)">${S8_POT}</g>` + s8T('Area kerja', -50, 16, 44, '#2b2b2b', 'start'), T8.area, 845, 258, 1, 0, T8.C1);
  add(chip(500, 92, '#ddeef2') + `<g transform="translate(-205,0) scale(.5)">${S8_SIT}</g>` + s8T('Jenis kegiatan', 40, 16, 44), T8.jenis, 1295, 258, 1, 0, T8.C1);
  // aturan: Jumlah jam = lama kerja sehari
  add(s8Card(930, 120, '#fffdf4') + `<rect x="-465" y="-60" width="16" height="120" rx="8" fill="#e8833a"/>`, T8.rule, 1100, 560, 1, 0, T8.C1);
  add(s8T('Jumlah jam', 0, 16, 44), T8.rule, 825, 560, 1, 0, T8.C1);
  add(s8T('=', 0, 18, 64, '#3f9d6b'), T8.eq, 1005, 560, 1, 0, T8.C1);
  add(s8T('lama kerja sehari', 0, 16, 44), T8.lama, 1245, 560, 1, 0, T8.C1);
  add(`<g transform="scale(.55)">${S8_CLOCK}</g>`, T8.clock, 1470, 560, 1, 0, T8.C1);
  // ----- shot 2: 8 = 5 + 2 + 1 -----
  add(s8Card(640, 130, '#ddeef2') + `<g transform="translate(-255,0) scale(.85)">${S8_CLOCK}</g>` + s8T('Kerja', -190, 20, 56, '#2b2b2b', 'start'), T8.kerja, 800, 245, 1, 0, T8.C2);
  add(s8T('8 jam', 0, 34, 100, '#2b2b2b', 'start'), T8.jam8, 815, 245, 1, 0, T8.C2);
  const tile = (x, num, ic, fill, tNum, label, tLab) => {
    add(s8Card(380, 300, fill) + `<g transform="translate(0,-85) scale(1.05)">${ic}</g>` + s8T(num + ' jam', 0, 62, 96), tNum, x, 475, 1, 0, T8.C2);
    add(s8T(label, 0, 0, 46, '#2b2b2b'), tLab, x, 614, 1, 0, T8.C2);
  };
  tile(330, 5, S8_POT, '#ffe2c2', T8.n5, 'Memasak', T8.memasak);
  tile(800, 2, S8_TRAY, '#dcefd9', T8.n2, 'Pemorsian', T8.pemorsian);
  tile(1270, 1, S8_PREP, '#fff0b8', T8.n1, 'Persiapan', T8.persiapan);
  add(s8T('+', 0, 30, 96), T8.n2, 565, 470, 1, 0, T8.C2);
  add(s8T('+', 0, 30, 96), T8.n1, 1035, 470, 1, 0, T8.C2);
  add(s8Card(440, 104, '#fffdf4') + s8T('=', -150, 30, 84, '#2b2b2b') + s8T('jam', 35, 32, 54, '#2b2b2b', 'start'), T8.eqCard, 480, 700, 1, 0, T8.C2);
  const rollG = add(`<text x="-30" y="38" text-anchor="middle" font-family="${S8_FONT}" font-weight="900" font-size="104" fill="#2b2b2b">0</text>`, T8.eqCard, 480, 700, 1, 0, T8.C2);
  const rollT = rollG.querySelector('text');
  add(`<g transform="scale(.8)">${S8_CHECK}</g>`, T8.eqDone, 745, 700, 1, 0, T8.C2);
  add(s8Card(430, 112, '#fff1d6') + s8T('≈ Perkiraan saja', 0, -4, 42) + s8T('sudah cukup', 0, 40, 42), T8.approx, 1235, 700, 1, -2, T8.C2);
  // ----- shot 3: tidak ada benar atau salah -----
  add(s8Card(660, 190, '#fffdf4') + s8T('Tidak ada jawaban', 0, -12, 62), T8.tidak, 1190, 295);
  add(s8T('benar atau salah', 0, 0, 62, '#2b2b2b'), T8.benar, 1190, 358);
  add(`<g transform="scale(.9)">${S8_CHECK}</g>`, T8.benar, 1030, 520);
  add(`<g transform="scale(.9)">${S8_CROSS}</g>`, T8.salah, 1170, 520);
  add(S8_BAN, T8.ban, 1100, 520, .96);

  // ----- kamera: tiga shot, gerak pelan -----
  cam.to({ z: 1.035 }, 0, W(T8.C1 - .1));
  cam.cut({ x: 800, y: 450, z: 1 }, W(T8.C1)); cam.to({ z: 1.035 }, W(T8.C1), 11);
  cam.cut({ x: 800, y: 450, z: 1 }, W(T8.C2)); cam.to({ z: 1.035 }, W(T8.C2), 3.2);

  // sfx (tools/briefing/add_sfx.py)
  sfx('scene8', T8.eqDone, 'chime', .5);
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    const j = k => .7 * jit(f >> 1, k);
    // formulir: jatuh dari atas, geser ke kiri, hilang (shot 2), kembali (shot 3)
    let fx, fy, fs, show = true;
    if (q < W(T8.form)) show = false;
    else if (q < W(T8.C1)) {
      const d = span(q, W(T8.form), W(T8.form) + .4), m = span(q, W(T8.shift), W(T8.shift) + .8);
      fx = 800 + (340 - 800) * m; fy = 470 + (1 - d) * -520; fs = .95 + (.8 - .95) * m;
    } else if (q < W(T8.C2)) show = false;
    else { const d = span(q, W(T8.C2), W(T8.C2) + .35); fx = 480; fy = 470 + (1 - d) * -520; fs = .88; }
    vis(formG, show);
    if (show) tf(formG, `translate(${(fx + j(1)).toFixed(1)},${(fy + j(2)).toFixed(1)}) rotate(${(j(3) * .25 - .4).toFixed(2)}) scale(${fs.toFixed(3)})`);
    for (const it of items) {
      if (q < it.t0 || q >= it.t1) { vis(it.g, false); continue; }
      const k = span(q, it.t0, it.t0 + .22), sc = it.s * (.55 + .45 * k + .08 * Math.sin(k * Math.PI));
      vis(it.g, true); it.g.setAttribute('opacity', k.toFixed(2));
      tf(it.g, `translate(${(it.x + j(it.k)).toFixed(1)},${(it.y + j(it.k + 50)).toFixed(1)}) rotate(${it.r}) scale(${sc.toFixed(3)})`);
    }
    // jumlah bergulir 0 -> 8 antara "Jumlahnya" dan "delapan", hijau pada "delapan"
    const n = Math.round(8 * span(q, W(T8.eqCard), W(T8.eqDone)));
    if (rollT._n !== n) rollT.textContent = rollT._n = n;
    const col = q >= W(T8.eqDone) ? '#3f9d6b' : '#2b2b2b';
    if (rollT._c !== col) rollT.setAttribute('fill', rollT._c = col);
  });
}
