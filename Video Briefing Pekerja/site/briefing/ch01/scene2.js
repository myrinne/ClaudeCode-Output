'use strict';
// Adegan 2: Apa yang Bapak dan Ibu dapat. Empat kartu manfaat berurutan, lalu konsumsi + pelembap dan "biaya ditanggung".
const PRE2 = 0.8;
function scene2(p, D) {
  const cam = paperCam(p, 'kertas'), S = 'scene2', W = (t) => PRE2 + t;   // t = detik pada klip adegan (kata di narration.id.words.txt)
  const stage = cam.stage;
  const FONT = 'Arial Black, Arial, sans-serif';
  const T = (s, x, y, size, fill = '#2b2b2b', anchor = 'middle') => `<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="${FONT}" font-weight="900" font-size="${size}" fill="${fill}">${s}</text>`;
  const GRN = '#3f9d6b', RED = '#c8322f', INK = '#2b2b2b';
  // satu benda: grup (x, y, s) yang muncul pada t0 (memantul kecil)
  const thing = (svg, live = '') => { const g = mk('g', {}, stage); const b = prop(g, svg); if (live) g.insertAdjacentHTML('beforeend', live); vis(g, false); return g; };
  const place = (g, q, t0, x, y, s = 1) => {
    if (q < t0) { vis(g, false); return; }
    const u = span(q, t0, t0 + .32); vis(g, true);
    tf(g, `translate(${x} ${y}) scale(${(s * (.72 + .28 * u + .07 * Math.sin(u * Math.PI))).toFixed(3)})`); g.setAttribute('opacity', Math.min(1, u * 1.6).toFixed(2));
  };
  const cardSvg = n => `<g filter="url(#paper)"><rect x="-270" y="-165" width="540" height="330" rx="22" fill="#fffaf0"/><circle cx="-214" cy="-110" r="40" fill="${GRN}"/></g>`;
  const card = (n, title) => thing(cardSvg(n), T(n, -214, -94, 52, '#fff') + T(title, -160, -92, 40, INK, 'start'));
  const C = [[330, 215], [900, 215], [330, 575], [900, 575]];
  const cards = [card(1, 'Hasil sendiri'), card(2, 'Rawat kulit'), card(3, 'Tanda kepanasan'), card(4, 'Saran lanjutan')];
  const tCard = [3.93, 10.85, 16.46, 21.09].map(W);

  // ---- ikon kartu (koordinat lokal kartu; pusat kartu = 0,0) ----
  const sheet = thing(`<g filter="url(#paper)"><rect x="-62" y="-84" width="124" height="160" rx="8" fill="#fff" stroke="#d9cfb4" stroke-width="3"/>
    <rect x="-42" y="-62" width="84" height="10" rx="4" fill="#b9c2c7"/><rect x="-42" y="-40" width="60" height="10" rx="4" fill="#b9c2c7"/>
    <rect x="-42" y="-14" width="14" height="50" fill="${GRN}"/><rect x="-20" y="6" width="14" height="30" fill="#f08a2c"/><rect x="2" y="-4" width="14" height="40" fill="${GRN}"/><rect x="24" y="14" width="14" height="22" fill="#7ec0e0"/></g>`);
  const bubble = thing(`<g filter="url(#paper)"><ellipse rx="44" ry="38" fill="#fff" stroke="${GRN}" stroke-width="5"/><path d="M-18,30 l-12,26 l32,-18 Z" fill="#fff" stroke="${GRN}" stroke-width="5" stroke-linejoin="round"/><ellipse rx="40" ry="34" fill="#fff"/><path d="M-18,32 l-8,16 l22,-12 Z" fill="#fff"/></g>`, T('?', 0, 20, 62, GRN));
  const bapak = bapakPuppet(stage);
  const tube = thing(`<g filter="url(#paper)"><rect x="-26" y="-60" width="52" height="106" rx="12" fill="#7ec0e0"/><rect x="-18" y="-82" width="36" height="26" rx="7" fill="#f4f1ea"/><rect x="-26" y="-14" width="52" height="30" fill="#fff" opacity=".85"/><path d="M-12,48 h24 l-4,14 h-16 Z" fill="#7ec0e0"/></g>`);
  const hand = thing(`<g filter="url(#paper)"><rect x="-34" y="-8" width="68" height="84" rx="26" fill="#e8be98"/><rect x="-34" y="-62" width="14" height="66" rx="7" fill="#e8be98"/><rect x="-16" y="-76" width="14" height="76" rx="7" fill="#e8be98"/><rect x="2" y="-74" width="14" height="74" rx="7" fill="#e8be98"/><rect x="20" y="-60" width="14" height="62" rx="7" fill="#e8be98"/><ellipse cx="-40" cy="26" rx="10" ry="24" fill="#e8be98" transform="rotate(30 -40 26)"/></g><circle cx="-14" cy="-84" r="0"/>`);
  const shirt = col => `<g filter="url(#paper)"><path d="M-50,-44 L-22,-58 Q0,-40 22,-58 L50,-44 L70,-6 L44,6 L36,-10 L36,56 L-36,56 L-36,-10 L-44,6 L-70,-6 Z" fill="${col}"/></g>`;
  const wet = thing(shirt('#6c9fc4') + `<g filter="url(#paper)"><path d="M-14,20 q-10,16 0,24 q10,-8 0,-24 Z M16,6 q-8,12 0,18 q8,-6 0,-18 Z" fill="#cfe9f7"/></g>`);
  const swap = thing(`<g filter="url(#paper)"><path d="M-34,0 h50 M2,-22 l24,22 l-24,22" fill="none" stroke="${GRN}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></g>`);
  const clean = thing(shirt('#8fcf9f') + `<g filter="url(#paper)"><path d="M-6,22 l10,12 l22,-28" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></g>`);
  const therm = thing(`<g filter="url(#paper)"><rect x="-17" y="-96" width="34" height="154" rx="17" fill="#fff" stroke="#d9cfb4" stroke-width="3"/><circle cy="64" r="30" fill="${RED}"/><rect x="-8" y="-50" width="16" height="116" rx="8" fill="${RED}"/></g>`);
  const flame = thing(`<g filter="url(#paper)"><path d="M0,-40 C26,-14 34,10 22,30 C14,42 -14,42 -22,30 C-34,8 -14,-8 0,-40 Z" fill="#f08a2c"/><path d="M0,-6 C12,8 14,20 6,28 C0,32 -8,30 -10,22 C-10,12 -4,4 0,-6 Z" fill="#ffd36b"/></g>`);
  const glass = thing(`<g filter="url(#paper)"><path d="M-40,-60 h80 l-12,118 q-1,10 -12,10 h-32 q-11,0 -12,-10 Z" fill="#e6f3f8" stroke="#bcd9e5" stroke-width="3"/><path d="M-34,-22 h68 l-8,80 h-52 Z" fill="#7ec0e0"/></g>`);
  const clock = thing(`<g filter="url(#paper)"><circle r="54" fill="#fff" stroke="${GRN}" stroke-width="9"/><path d="M0,-34 V0 L22,16" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>`);
  const mail = thing(`<g filter="url(#paper)"><rect x="-76" y="-50" width="152" height="104" rx="10" fill="#fff" stroke="#d9cfb4" stroke-width="3"/><path d="M-72,-44 L0,16 L72,-44" fill="none" stroke="#b9a77c" stroke-width="7" stroke-linejoin="round"/></g><g filter="url(#paper)"><circle cx="60" cy="48" r="24" fill="${GRN}"/><path d="M48,48 l9,9 l16,-18" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>`);
  const clinic = thing(`<g filter="url(#paper)"><rect x="-90" y="-50" width="180" height="120" rx="6" fill="#e9eef0"/><rect x="-100" y="-62" width="200" height="22" rx="6" fill="#7ec0e0"/><rect x="-22" y="20" width="44" height="50" fill="#9a7b58"/><rect x="-74" y="-20" width="36" height="34" fill="#bfe0ee"/><rect x="38" y="-20" width="36" height="34" fill="#bfe0ee"/><rect x="-20" y="-96" width="40" height="40" rx="6" fill="#fff"/><path d="M0,-90 v28 M-14,-76 h28" stroke="${RED}" stroke-width="10"/></g>`);
  // ---- bonus: konsumsi, pelembap, biaya ditanggung (kanan atas) ----
  const food = thing(`<g filter="url(#paper)"><rect x="-56" y="-30" width="112" height="70" rx="12" fill="#f08a2c"/><rect x="-56" y="-40" width="112" height="24" rx="10" fill="#d9731a"/><circle cx="-18" cy="10" r="14" fill="#ffd36b"/><circle cx="18" cy="14" r="12" fill="#8fcf9f"/></g>`, T('Konsumsi', 80, 16, 38, INK, 'start'));
  const cream = thing(`<g filter="url(#paper)"><rect x="-54" y="-26" width="108" height="52" rx="14" fill="#7ec0e0"/><rect x="-74" y="-18" width="26" height="36" rx="7" fill="#f4f1ea"/></g>`, T('Pelembap', 80, 14, 38, INK, 'start'));
  const free = thing(`<g filter="url(#paper)"><rect x="-196" y="-34" width="392" height="68" rx="20" fill="${GRN}"/></g>`, T('Biaya ditanggung', 0, 14, 38, '#fff'));

  const dok = dokterPuppet(stage);
  const blink = (q, per, off) => ((q + off) % per) < 2 / FPS;
  const at = (i, dx, dy) => [C[i][0] + dx, C[i][1] + dy];
  const tT = { sheet: W(5.34), bub: W(7.75), tube: W(12.39), hand: W(12.72), wet: W(13.39), clean: W(14.52),
    therm: W(17.71), flame: W(18.39), glass: W(19.57), clock: W(20.0), mail: W(24.5), clinic: W(26.52), food: W(29.81), cream: W(30.96), free: W(34.7) };
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    cards.forEach((c, i) => place(c, q, tCard[i], C[i][0], C[i][1], 1));
    place(sheet, q, tT.sheet, ...at(0, -140, 28), 1);
    place(bubble, q, tT.bub, ...at(0, 170, -20), 1);
    place(tube, q, tT.tube, ...at(1, -180, 30), 1);
    place(hand, q, tT.hand, ...at(1, -90, 50), .9);
    place(wet, q, tT.wet, ...at(1, 40, 36), .9);
    place(swap, q, tT.clean, ...at(1, 118, 40), .9);
    place(clean, q, tT.clean + .15, ...at(1, 190, 36), .9);
    place(therm, q, tT.therm, ...at(2, -180, 12), .95);
    place(flame, q, tT.flame, ...at(2, -90, 6), .85);
    place(glass, q, tT.glass, ...at(2, 30, 26), .9);
    place(clock, q, tT.clock, ...at(2, 160, 36), .9);
    place(mail, q, tT.mail, ...at(3, -140, 36), .95);
    place(clinic, q, tT.clinic, ...at(3, 120, 30), .9);
    place(food, q, tT.food, 1262, 98, 1);
    place(cream, q, tT.cream, 1262, 218, 1);
    place(free, q, tT.free, 1380, 362, 1);
    // bapak kecil di kartu 1: muncul bersama kertas, membaca
    const bs = .44, bx = C[0][0] + 80, by = C[0][1] + 150;
    vis(bapak.g, q >= tT.sheet);
    bapak.pose({ x: bx, y: by, s: bs * (.8 + .2 * span(q, tT.sheet, tT.sheet + .3)), look: q < tT.bub ? -.9 : .2, eyeX: q < tT.bub ? -.9 : -.2, eyeY: q < tT.bub ? .5 : 0,
      bob: 1.6 * Math.sin(q * 2.2), mouth: q > tT.bub ? 'smile' : 'X', shut: blink(q, 3.9, .5), armR: q < tT.bub ? 40 : 8 + 5 * Math.sin(q * 3), armL: 8 }, f);
    // dokter di sudut: mendengarkan, mengangguk, menunjuk ke klinik pada kata 'sarankan'
    const tPoint = W(26.0), pointing = q >= tPoint && q < W(29.0);
    const base = { x: 1310, y: 800, s: 1.0, bob: 1.6 * Math.sin(q * 2.1 + 2), look: -.7, eyeX: -.7, shut: blink(q, 3.4, .9), mouth: q > W(29.0) ? 'smile' : 'X' };
    const nod = tCard.some(t => between(q, t, t + .5)) ? 5 * Math.sin((q % .5) * 12.6) : 0;
    const pose = { ...base, headR: -2 + nod * .5, headY: nod > 0 ? 4 : 0, armR: 8 };
    if (pointing) Object.assign(pose, dok.aim({ ...pose }, 'L', [1160, 640]), { look: -1, eyeX: -1 });
    else pose.armL = between(q, tCard[0], tCard[0] + 5) || between(q, tCard[1], tCard[1] + 4) || between(q, tCard[2], tCard[2] + 4) ? 48 + 6 * Math.sin(q * 2) : 8;
    dok.pose(pose, f);
  });
}
