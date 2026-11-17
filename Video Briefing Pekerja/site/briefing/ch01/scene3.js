'use strict';
// Adegan 3: Kenapa dapur dan panas. Dapur (ibu berkeringat, kompor) -> insert lengan -> insert tubuh + darah -> dokter menunjuk papan.
const PRE3 = 0.8;
function scene3(p, D) {
  const cam = paperCam(p, 'dapur'), S = 'scene3', W = t => PRE3 + t;   // t = detik pada klip adegan (words.txt)
  const stage = cam.stage;
  const FONT = 'Arial Black, Arial, sans-serif', GRN = '#3f9d6b', RED = '#c8322f', INK = '#2b2b2b';
  const T = (s, x, y, size, fill = INK, anchor = 'middle') => `<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="${FONT}" font-weight="900" font-size="${size}" fill="${fill}">${s}</text>`;
  const blink = (q, per, off) => ((q + off) % per) < 2 / FPS;
  const wavy = (x, y0, y1, amp, ph, n = 14) => { let d = ''; for (let i = 0; i <= n; i++) { const u = i / n, y = y0 + (y1 - y0) * u, xx = x + amp * Math.sin(u * 9 + ph) * (.4 + u * .6); d += (i ? 'L' : 'M') + xx.toFixed(1) + ',' + y.toFixed(1); } return d; };
  const ladle = '<g filter="url(#paper)"><rect x="-4" y="-16" width="8" height="78" rx="4" fill="#8b949a"/><ellipse cy="66" rx="19" ry="13" fill="#b9c2c7"/></g>';

  // ---- dapur: panci di kompor, api besar, gelombang panas, ibu berkeringat ----
  const pot = prop(stage, `<g filter="url(#paper)"><path d="M-60,-62 h120 v66 q0,14 -14,14 h-92 q-14,0 -14,-14 Z" fill="#9aa4ab"/><rect x="-68" y="-72" width="136" height="16" rx="7" fill="#c9d1d6"/></g>`, { transform: 'translate(490 436)' });
  const flames = [230, 360].map(x => prop(stage, `<g filter="url(#paper)"><path d="M0,-58 C24,-30 30,-6 18,10 C10,20 -10,20 -18,10 C-30,-8 -12,-26 0,-58 Z" fill="#f08a2c"/><path d="M0,-24 C12,-10 14,0 6,8 C0,12 -8,10 -10,2 C-10,-6 -4,-12 0,-24 Z" fill="#ffd36b"/></g>`));
  const flame3 = prop(stage, `<g filter="url(#paper)"><path d="M0,-58 C24,-30 30,-6 18,10 C10,20 -10,20 -18,10 C-30,-8 -12,-26 0,-58 Z" fill="#f08a2c"/><path d="M0,-24 C12,-10 14,0 6,8 C0,12 -8,10 -10,2 C-10,-6 -4,-12 0,-24 Z" fill="#ffd36b"/></g>`);
  const waves = mk('g', { fill: 'none', 'stroke-linecap': 'round', 'stroke-width': 10 }, stage);
  const wv = [[250, '#f08a2c'], [350, '#e8613a'], [450, '#f08a2c']].map(([x, c]) => mk('path', { stroke: c, opacity: .75 }, waves));
  const steam = smoke(stage, 490, 360, 4, 3.0);
  const drops = Array.from({ length: 3 }, () => prop(stage, `<g filter="url(#paper)"><path d="M0,-18 C12,-2 14,8 0,14 C-14,8 -12,-2 0,-18 Z" fill="#7ec0e0"/></g>`));
  const ibu = ibuPuppet(stage, { holds: { ladle } });
  const dok = dokterPuppet(stage);
  // papan "Kesehatan pekerja" + perisai
  const board = mk('g', {}, stage);
  prop(board, `<g filter="url(#paper)"><rect x="-150" y="-100" width="300" height="200" rx="16" fill="#fffaf0"/><rect x="-150" y="-100" width="300" height="38" rx="14" fill="${GRN}"/></g><g filter="url(#paper)"><rect x="-6" y="100" width="12" height="150" fill="#8a6a46"/></g>`);
  board.insertAdjacentHTML('beforeend', T('Kesehatan', 0, 2, 44) + T('pekerja', 0, 54, 48));
  const shield = prop(stage, `<g filter="url(#paper)"><path d="M0,-52 L44,-34 V6 C44,36 22,52 0,62 C-22,52 -44,36 -44,6 V-34 Z" fill="${GRN}"/></g><g filter="url(#paper)"><path d="M-18,4 l13,14 l24,-30" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></g>`);

  // ---- insert: lengan, tubuh, darah (lapisan layar di atas kamera) ----
  const ins = mk('g', {}, p);
  mk('rect', { width: 1600, height: 900, fill: '#f6efdc' }, ins);
  prop(ins, `<g filter="url(#paper)"><path d="M-100,120 Q400,80 800,130 T1700,110 V-40 H-100 Z" fill="#ecdfc0"/></g>`);
  const ARM = 'M-330,-84 C-200,-100 0,-74 130,-64 L130,64 C0,84 -200,104 -330,92 Z';
  const arm = prop(ins, `<g filter="url(#paper)"><path d="${ARM}" fill="#e8be98"/><ellipse cx="190" cy="0" rx="92" ry="84" fill="#e8be98"/>${[-62, -22, 18, 58].map((y, i) => `<rect x="230" y="${y - 17}" width="${150 - 8 * (i === 0 || i === 3)}" height="36" rx="18" fill="#e8be98"/>`).join('')}<rect x="150" y="-128" width="40" height="110" rx="20" fill="#e8be98" transform="rotate(-24 170 -80)"/><path d="M-250,-40 q80,-8 160,6" fill="none" stroke="#d9a77c" stroke-width="6" stroke-linecap="round"/></g>`);
  const armHi = mk('path', { d: ARM, fill: 'none', stroke: GRN, 'stroke-width': 12, 'stroke-linejoin': 'round' }, arm);
  const hot = mk('g', { fill: 'none', 'stroke-linecap': 'round', 'stroke-width': 14 }, ins);
  const hp = [0, 1, 2, 3].map(i => mk('path', { stroke: i % 2 ? '#e8613a' : '#f08a2c' }, hot));
  const hotFlame = prop(ins, `<g filter="url(#paper)"><path d="M0,-70 C32,-36 40,-8 24,14 C14,28 -14,28 -24,14 C-40,-10 -16,-32 0,-70 Z" fill="#f08a2c"/><path d="M0,-30 C16,-12 18,2 8,12 C0,16 -10,14 -12,4 C-12,-8 -6,-14 0,-30 Z" fill="#ffd36b"/></g>`);
  const body = prop(ins, `<g filter="url(#paper)"><circle cx="0" cy="-150" r="62" fill="#e8be98"/><path d="M-100,-70 Q-100,-96 -60,-96 H60 Q100,-96 100,-70 V90 H-100 Z" fill="#8fcf9f"/><rect x="-100" y="90" width="82" height="170" rx="20" fill="#34584a"/><rect x="-146" y="-90" width="48" height="170" rx="24" fill="#8fcf9f"/><circle cx="-122" cy="92" r="27" fill="#e8be98"/><rect x="98" y="-90" width="48" height="170" rx="24" fill="#8fcf9f"/><circle cx="122" cy="92" r="27" fill="#e8be98"/><rect x="18" y="90" width="82" height="170" rx="20" fill="#34584a"/></g>`);
  const bodyHi = mk('path', { d: 'M-100,-70 Q-100,-96 -60,-96 H60 Q100,-96 100,-70 V90 H-100 Z', fill: 'none', stroke: GRN, 'stroke-width': 10 }, body);
  const vial = prop(ins, `<g filter="url(#paper)"><rect x="-44" y="-120" width="88" height="250" rx="22" fill="#e6f3f8" stroke="#bcd9e5" stroke-width="5"/><rect x="-50" y="-132" width="100" height="26" rx="10" fill="#c8322f"/><path d="M-38,40 H38 V108 Q38,122 24,122 H-24 Q-38,122 -38,108 Z" fill="#c8322f"/></g>`);
  const dropB = prop(ins, `<g filter="url(#paper)"><path d="M0,-34 C22,-6 26,14 0,28 C-26,14 -22,-6 0,-34 Z" fill="${RED}"/><ellipse cx="-7" cy="6" rx="5" ry="9" fill="#e8736f"/></g>`);
  const arrow = prop(ins, `<g filter="url(#paper)"><path d="M-60,0 H40 M10,-34 L50,0 L10,34" fill="none" stroke="${GRN}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></g>`);
  const lab = prop(ins, `<g filter="url(#paper)"><rect x="-500" y="-50" width="1000" height="100" rx="24" fill="#fffaf0"/></g>`);
  const t1 = mk('g', {}, lab), t2 = mk('g', {}, lab), t3 = mk('g', {}, lab);
  t1.innerHTML = T('Panas dapur', -460, 22, 56, RED, 'start'); t2.innerHTML = T('→ kulit', -55, 22, 56, INK, 'start'); t3.innerHTML = T('→ tubuh', 185, 22, 56, GRN, 'start');
  const ph = { wide: [0, W(4.38)], arm: [W(4.38), W(10.32)], body: [W(10.32), W(13.2)] };
  cam.cut({ x: 600, y: 540, z: 1.2 }, 0);
  cam.cut({ x: 900, y: 520, z: 1.1 }, W(13.2));
  const tHot = W(.93), tKompor = W(1.79), tPanasI = W(5.85), tKulit = W(6.8), tTubuh = W(9.97), tDarah = W(11.75);
  const tBoard = W(16.3), tShield = W(19.23), tPoint = W(15.9);
  const pop = (g, q, t0, x, y, s = 1, d = .3) => { if (q < t0) { vis(g, false); return; } const u = span(q, t0, t0 + d); vis(g, true); tf(g, `translate(${x} ${y}) scale(${(s * (.7 + .3 * u + .08 * Math.sin(u * Math.PI))).toFixed(3)})`); g.setAttribute('opacity', Math.min(1, u * 1.8).toFixed(2)); };
  stopClock(D, (q, f) => {
    const inWide = q < ph.arm[0] || q >= ph.body[1], inArm = between(q, ...ph.arm), inBody = between(q, ...ph.body);
    vis(cam.root, inWide); vis(ins, !inWide);
    cam.apply(q, f);
    // ---------- dapur ----------
    steam(q);
    const fl = k => 1 + .14 * Math.sin(q * 11 + k) + .08 * Math.sin(q * 17 + 2 * k);
    pop(flames[0], q, tKompor, 230, 446, 1.5 * fl(0)); pop(flames[1], q, tKompor + .15, 360, 446, 1.5 * fl(2)); vis(flame3, false);
    vis(waves, q >= tHot);
    wv.forEach((e, i) => { e.setAttribute('d', wavy(250 + i * 130 + (i === 2 ? 40 : 0), 400, 150 + i * 20, 22, q * 4 - i * 1.3)); e.setAttribute('opacity', (.35 + .4 * span(q, tHot, tHot + .8)).toFixed(2)); });
    drops.forEach((d, i) => { const t = q - W(.93) - i * .45, u = ((t % 1.35) + 1.35) % 1.35 / 1.35;
      vis(d, q >= tHot + .3 && inWide); tf(d, `translate(${(i === 1 ? 760 : i === 0 ? 590 : 780) + 6 * i} ${(430 + (i % 2) * 14 + 150 * u).toFixed(1)}) scale(${(.9 - .3 * u).toFixed(2)})`); d.setAttribute('opacity', (1 - u * u).toFixed(2)); });
    const stir = Math.sin(q * 4.4);
    ibu.pose({ x: 690, y: 800, s: 1.05, look: -.5, eyeX: -.6, eyeY: -.1, brow: q > tHot ? .6 : 0, bob: 1.8 * Math.sin(q * 2.1), holdL: 'ladle', armL: 66 + 8 * stir, armR: 14 + 5 * Math.sin(q * 3), mouth: q > tHot ? 'wobble' : 'X', shut: blink(q, 4.1, 1.1), lean: -1.5 + stir }, f);
    // dokter muncul setelah kembali ke dapur
    const dokOn = q >= ph.body[1];
    vis(dok.g, dokOn);
    const talk = lips(q, S, PRE3, 's03b'), pointing = q >= tPoint;
    dok.pose({ x: 1130, y: 800, s: 1.03, look: pointing ? .4 : -.2, eyeX: pointing ? .7 : -.4, bob: 1.6 * Math.sin(q * 2.2 + 1), mouth: talk, shut: blink(q, 3.5, .6), headR: 2 * Math.sin(q * 1.2),
      armR: pointing ? 96 + 4 * Math.sin(q * 2) : 10, reachR: pointing ? 1.15 : 1, armL: 10 + (talk !== 'X' ? 6 * Math.sin(q * 5) : 0) }, f);
    pop(board, q, tBoard, 1440, 330, 1);
    pop(shield, q, tShield, 1235, 300, 1.0, .35);
    vis(shield, q >= tShield);
    // ---------- insert ----------
    const lbl = inArm || inBody;
    vis(lab, lbl); tf(lab, 'translate(800 810)');
    vis(t1, q >= tPanasI); vis(t2, q >= tKulit); vis(t3, q >= tTubuh);
    vis(arm, inArm); vis(hot, inArm && q >= tPanasI); vis(hotFlame, inArm && q >= tPanasI);
    const pulse = 1 + .012 * Math.sin(q * 3);
    tf(arm, `translate(700 500) scale(${pulse.toFixed(3)})`);
    armHi.setAttribute('opacity', q >= tKulit ? (.55 + .45 * Math.sin((q - tKulit) * 7)).toFixed(2) : 0);
    hp.forEach((e, i) => { e.setAttribute('d', wavy(250 + i * 150, 130 + 12 * Math.sin(q * 3 + i), 410, 18, q * 5 - i)); e.setAttribute('opacity', q >= tPanasI ? (span(q, tPanasI, tPanasI + .5) * .9).toFixed(2) : 0); });
    tf(hotFlame, `translate(180 150) scale(${(1.3 * fl(5)).toFixed(3)})`);
    vis(body, inBody); tf(body, `translate(500 400) scale(1)`);
    bodyHi.setAttribute('opacity', q >= tTubuh ? (.6 + .4 * Math.sin((q - tTubuh) * 7)).toFixed(2) : 0);
    pop(arrow, q, tDarah - .1, 880, 400, 1); vis(arrow, inBody && q >= tDarah - .1);
    pop(vial, q, tDarah - .1, 1150, 400, 1); vis(vial, inBody && q >= tDarah - .1);
    const fall = span(q, tDarah, tDarah + .9);
    vis(dropB, inBody && q >= tDarah); tf(dropB, `translate(1150 ${(150 + 230 * fall).toFixed(1)}) scale(${(1.1 - .1 * fall).toFixed(2)})`);
  });
}
