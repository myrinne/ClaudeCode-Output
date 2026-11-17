'use strict';
// Adegan 4: Bukan pengobatan. Dokter dekat di kiri; di kanan ikon obat dan suntikan dicoret, "1 kali", pilihan ya/tidak + perisai pekerjaan.
const PRE4 = 0.8;
function scene4(p, D) {
  const cam = paperCam(p, 'kertas'), S = 'scene4', W = t => PRE4 + t;   // t = detik pada klip adegan (words.txt)
  const FONT = 'Arial Black, Arial, sans-serif', GRN = '#3f9d6b', RED = '#c8322f', INK = '#2b2b2b';
  const T = (s, x, y, size, fill = INK, anchor = 'middle') => `<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="${FONT}" font-weight="900" font-size="${size}" fill="${fill}">${s}</text>`;
  const blink = (q, per, off) => ((q + off) % per) < 2 / FPS;
  const dok = dokterPuppet(cam.stage);
  cam.cut({ x: 640, y: 610, z: 1.3 }, 0);
  cam.to({ x: 600, y: 600, z: 1.38 }, W(9.4), 6);   // dorong pelan sampai akhir
  // ikon di lapisan layar (kanan); tiap benda = grup kertas + teks hidup
  const ov = mk('g', {}, p);
  const thing = (svg, live = '') => { const g = mk('g', {}, ov); prop(g, svg); if (live) g.insertAdjacentHTML('beforeend', live); vis(g, false); return g; };
  const place = (g, q, t0, x, y, s = 1) => { if (q < t0) { vis(g, false); return; } const u = span(q, t0, t0 + .32); vis(g, true);
    tf(g, `translate(${x} ${y}) scale(${(s * (.72 + .28 * u + .07 * Math.sin(u * Math.PI))).toFixed(3)})`); g.setAttribute('opacity', Math.min(1, u * 1.6).toFixed(2)); };
  const cardBg = (w, h, col = '#fffaf0') => `<g filter="url(#paper)"><rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="22" fill="${col}"/></g>`;
  const banner = thing(`<g filter="url(#paper)"><rect x="-370" y="-46" width="740" height="92" rx="24" fill="${RED}"/></g>`, T('Bukan pengobatan', 0, 24, 58, '#fff'));
  const pill = thing(cardBg(330, 260) + `<g filter="url(#paper)"><g transform="rotate(-35)"><rect x="-86" y="-34" width="172" height="68" rx="34" fill="#f4f1ea"/><path d="M0,-34 H52 a34,34 0 0 1 0,68 H0 Z" fill="${RED}" opacity=".9"/><path d="M-52,-22 h30" stroke="#d9d3c2" stroke-width="6" stroke-linecap="round"/></g></g>`, T('Obat', 0, 112, 44));
  const syr = thing(cardBg(330, 260) + `<g filter="url(#paper)"><g transform="rotate(-35)"><rect x="-80" y="-22" width="130" height="44" rx="10" fill="#e6f3f8" stroke="#bcd9e5" stroke-width="5"/><rect x="-60" y="-12" width="70" height="24" fill="#7ec0e0"/><rect x="-102" y="-26" width="22" height="52" rx="6" fill="#8b949a"/><rect x="-130" y="-5" width="30" height="10" fill="#8b949a"/><path d="M50,0 H106" stroke="#8b949a" stroke-width="7" stroke-linecap="round"/></g></g>`, T('Suntikan', 0, 112, 44));
  const mkX = () => `<path class="xs" d="M-60,-60 L60,60 M60,-60 L-60,60" fill="none" stroke="${RED}" stroke-width="24" stroke-linecap="round" opacity=".92" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`;
  [pill, syr].forEach(g => g.insertAdjacentHTML('beforeend', `<g transform="translate(0 -10)">${mkX()}</g>`));
  const xs = [pill, syr].map(g => g.querySelector('.xs'));
  const once = thing(cardBg(720, 150), T('1 kali', -225, 28, 80, INK, 'start') + `<g transform="translate(-290 0)"><circle r="46" fill="${GRN}"/><path d="M-22,2 l16,18 l30,-38" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/></g>`);
  const clock = thing(`<g filter="url(#paper)"><circle r="48" fill="#fff" stroke="${GRN}" stroke-width="9"/><path d="M0,-30 V0 L20,14" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>`, T('setelah', 64, 4, 36, INK, 'start') + T('jam kerja', 64, 42, 36, INK, 'start'));
  const yes = thing(`<g filter="url(#paper)"><rect x="-100" y="-54" width="200" height="108" rx="26" fill="${GRN}"/></g>`, T('Ya', 0, 26, 68, '#fff'));
  const no = thing(`<g filter="url(#paper)"><rect x="-100" y="-54" width="200" height="108" rx="26" fill="#8b949a"/></g>`, T('Tidak', 0, 24, 58, '#fff'));
  const bag = thing(`<g filter="url(#paper)"><rect x="-62" y="-36" width="124" height="90" rx="14" fill="#9a7b58"/><path d="M-26,-36 v-16 q0,-10 10,-10 h32 q10,0 10,10 v16" fill="none" stroke="#7d6044" stroke-width="10"/><rect x="-62" y="2" width="124" height="10" fill="#7d6044"/><rect x="-12" y="-4" width="24" height="24" rx="5" fill="#d9a05b"/></g>`);
  const shield = thing(`<g filter="url(#paper)"><path d="M0,-56 L48,-36 V6 C48,38 24,56 0,66 C-24,56 -48,38 -48,6 V-36 Z" fill="${GRN}" stroke="#fff" stroke-width="7"/></g><g filter="url(#paper)"><path d="M-18,6 l14,15 l26,-32" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></g>`);
  const tTidak = W(1.19), tObat = W(1.93), tTind = W(3.23), tSatu = W(5.88), tJam = W(7.52), tYa = W(9.64), tNo = W(10.31), tBag = W(14.04);
  // sfx (tools/briefing/add_sfx.py)
  sfx('scene4', 6.68, 'chime', .5);
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    place(banner, q, tTidak, 1190, 118, 1);
    place(pill, q, tObat, 1000, 330, 1); place(syr, q, tTind, 1380, 330, 1);
    xs[0].setAttribute('stroke-dashoffset', (1 - span(q, tObat + .35, tObat + .75)).toFixed(3));
    xs[1].setAttribute('stroke-dashoffset', (1 - span(q, tTind + .35, tTind + .75)).toFixed(3));
    place(once, q, tSatu, 1190, 570, 1);
    place(clock, q, tJam, 1300, 570, .9);
    place(yes, q, tYa, 930, 770, 1); place(no, q, tNo, 1170, 770, 1);
    place(bag, q, tBag, 1440, 790, .95);
    place(shield, q, tBag + .4, 1400, 735, .8);
    // dokter: bicara dengan gerak kecil; menggeleng saat "tidak", tangan terbuka saat "pilihan"
    const talk = lips(q, S, PRE4, 's04a', 's04b');
    const shake = between(q, tTidak, tTidak + 1.4) ? 5 * Math.sin((q - tTidak) * 10) : 0;
    const one = between(q, tSatu - .1, tSatu + 1.6), open = between(q, W(10.6), W(14.8));
    dok.pose({ x: 420, y: 800, s: 1.02, look: .35, eyeX: .5, bob: 1.6 * Math.sin(q * 2.1), headR: shake || 2 * Math.sin(q * 1.1), mouth: talk, shut: blink(q, 3.6, 1.2),
      armR: one ? 100 + 6 * Math.sin(q * 3) : open ? 52 + 6 * Math.sin(q * 2.2) : 10, armL: open ? 50 + 6 * Math.sin(q * 2.2 + 1) : 10 + (talk !== 'X' ? 5 * Math.sin(q * 4) : 0) }, f);
  });
}
