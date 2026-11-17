'use strict';
// Adegan 1: Salam. Dapur pagi; dokter masuk dan melambai, lalu dua-shot dengan bapak; judul turun.
const PRE1 = 0.8;
function scene1(p, D) {
  const cam = paperCam(p, 'dapur'), S = 'scene1', W = (clip, t) => clipAt(S, PRE1, clip, t);
  const ladle = '<g filter="url(#paper)"><rect x="-4" y="-16" width="8" height="78" rx="4" fill="#8b949a"/><ellipse cy="66" rx="19" ry="13" fill="#b9c2c7"/></g>';
  const steam = smoke(cam.stage, 360, 392, 4, 3.4);
  const pot = prop(cam.stage, `<g filter="url(#paper)"><rect x="-86" y="90" width="10" height="120" fill="#8b949a"/><rect x="76" y="90" width="10" height="120" fill="#8b949a"/><rect x="-100" y="84" width="200" height="16" rx="6" fill="#c9d1d6"/><path d="M-80,-30 h160 v110 q0,16 -16,16 h-128 q-16,0 -16,-16 Z" fill="#9aa4ab"/><rect x="-88" y="-42" width="176" height="20" rx="9" fill="#c9d1d6"/></g>`, { transform: 'translate(690 590)' });
  const ibu = ibuPuppet(cam.stage, { holds: { ladle } });
  const bapak = bapakPuppet(cam.stage, { holds: { ladle } });
  const dok = dokterPuppet(cam.stage);
  // judul (lapisan layar, tidak ikut kamera)
  const title = mk('g', {}, p);
  const card = prop(title, `<g filter="url(#paper)"><rect x="-560" y="-92" width="1120" height="184" rx="26" fill="#fffaf0"/><rect x="-560" y="62" width="1120" height="30" rx="14" fill="#3f9d6b"/></g>`);
  const tx = (s, y, size, fill) => `<text x="0" y="${y}" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="${size}" fill="${fill}">${s}</text>`;
  title.insertAdjacentHTML('beforeend', tx('Cek Kulit dan Panas', -8, 76, '#2b2b2b') + tx('di Dapur Gizi', 52, 64, '#2f7d54'));
  // dua-shot: kamera dekat saat kalimat kedua, lalu mundur sedikit sebelum judul turun
  cam.cut({ x: 800, y: 450, z: 1 }, 0);
  cam.cut({ x: 730, y: 600, z: 1.32 }, cueAt(S, PRE1, 1));
  cam.to({ x: 780, y: 560, z: 1.2 }, W('s01b', 1.5), 1.0);
  const tIn = clipAt(S, PRE1, 's01b', 11.91 - 9.542);   // 'pemeriksaan'
  const blink = (q, per, off) => ((q + off) % per) < 2 / FPS;
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    steam(q);
    // bapak mengaduk, ibu memorsikan
    const stir = Math.sin(q * 5.2), port = Math.sin(q * 3.1);
    bapak.pose({ x: 520, y: 800, s: 1.02, look: q > 2.2 ? .8 : .2 + .2 * Math.sin(q), eyeX: q > 2.2 ? .8 : .3, bob: 1.6 * Math.sin(q * 2.2), armR: 52 + 10 * stir, reachR: 1, hold: 'ladle', armL: 8,
      mouth: q > 2.6 ? 'smile' : 'X', shut: blink(q, 3.7, .4), lean: 1.2 * stir }, f);
    ibu.pose({ x: 1210, y: 800, s: 1.02, look: q > 2.2 ? -.7 : -.2, eyeX: q > 2.2 ? -.7 : -.3, bob: 1.6 * Math.sin(q * 2 + 1), armL: 50 + 12 * port, armR: 24 + 8 * port, hold: null, holdL: 'ladle',
      mouth: q > 2.8 ? 'smile' : 'X', shut: blink(q, 4.3, 1.9), lean: -1 * port }, f);
    // dokter berjalan masuk dari kanan, melambai
    const walkT = span(q, 0.0, 2.3), x = 1700 + (900 - 1700) * walkT, walking = q < 2.3, w = spWalk(q);
    const wave = between(q, 2.3, 4.6) ? 130 + 22 * Math.sin((q - 2.3) * 9) : 0;
    const talk = lips(q, S, PRE1, 's01a', 's01b');
    const act = q > 5.0 && q < 8.5 ? 1 : 0;   // sedikit gerak tangan saat menyebut nama
    dok.pose({ x, y: 800, s: 1.04, look: q < 2.3 ? -.5 : -.35 + .1 * Math.sin(q * .8), eyeX: -.5, ...(walking ? { legL: w.legL, legR: w.legR, bob: w.bob } : { bob: 1.6 * Math.sin(q * 2.1 + 2) }),
      armR: wave || (walking ? w.armR : 6 + (act ? 8 * Math.sin((q - 5) * 2.4) : 0)), armL: walking ? w.armL : 8, mouth: talk, shut: blink(q, 3.4, .9), headR: q > 2.3 ? 3 * Math.sin(q * 1.3) : 0 }, f);
    // judul turun dari atas pada kata 'pemeriksaan', menetap pada y 150
    const u = span(q, tIn, tIn + .6), bounce = u >= 1 ? 4 * Math.exp(-(q - tIn - .6) * 6) * Math.sin((q - tIn - .6) * 18) : 0;
    vis(title, q >= tIn);
    tf(title, `translate(800 ${(-130 + (150 + 130) * u + bounce).toFixed(1)})`);
  });
}
