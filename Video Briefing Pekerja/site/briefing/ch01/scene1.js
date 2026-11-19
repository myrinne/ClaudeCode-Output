'use strict';
// Adegan 1: Salam. Dapur pagi; dokter masuk dan melambai, lalu dua-shot dengan bapak; judul turun.
const PRE1 = 0.8;
// waktu kata (detik pada klip s01a, words.txt) dikurangi ~0,22 s; jam beat = PRE1 + waktu
const T1 = { nama: 2.52 - 0.22, ajak: 7.46 - 0.22, periksa: 9.32 - 0.22 };
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
  cam.cut({ x: 730, y: 600, z: 1.32 }, PRE1 + T1.nama);
  cam.to({ x: 780, y: 560, z: 1.2 }, PRE1 + T1.ajak, 1.0);
  const tIn = PRE1 + T1.periksa;   // 'pemeriksaan'
  const blink = (q, per, off) => ((q + off) % per) < 2 / FPS;
  // sfx (tools/briefing/add_sfx.py)
  sfx('scene1', 0, 'room', 0.25, { loop: true });
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    steam(q);
    // bapak mengaduk, ibu memorsikan
    const stir = Math.sin(q * 5.2), port = Math.sin(q * 3.1);
    bapak.pose({ x: 520, y: 800, s: 1.02, look: q > 1.4 ? .8 : .2 + .2 * Math.sin(q), eyeX: q > 1.4 ? .8 : .3, bob: 1.6 * Math.sin(q * 2.2), armR: 52 + 10 * stir, reachR: 1, hold: 'ladle', armL: 8,
      mouth: q > 1.6 ? 'smile' : 'X', shut: blink(q, 3.7, .4), lean: 1.2 * stir }, f);
    ibu.pose({ x: 930, y: 800, s: 1.02, look: q > 1.4 ? .6 : -.2, eyeX: q > 1.4 ? .7 : -.3, bob: 1.6 * Math.sin(q * 2 + 1), armL: 50 + 12 * port, armR: 24 + 8 * port, hold: null, holdL: 'ladle',
      mouth: q > 1.8 ? 'smile' : 'X', shut: blink(q, 4.3, 1.9), lean: -1 * port }, f);
    // dokter berjalan masuk dari kanan, melambai
    const walkT = span(q, 0.0, 1.4), x = 1700 + (1180 - 1700) * walkT, walking = q < 1.4, w = spWalk(q);
    const wave = between(q, 1.4, 3.2) ? 130 + 22 * Math.sin((q - 1.4) * 9) : 0;
    const talk = lips(q, S, PRE1, 's01a');
    const act = q > PRE1 + T1.nama && q < PRE1 + T1.nama + 3.4 ? 1 : 0;   // sedikit gerak tangan saat menyebut nama
    dok.pose({ x, y: 800, s: 1.04, look: q < 1.4 ? -.5 : -.35 + .1 * Math.sin(q * .8), eyeX: -.5, ...(walking ? { legL: w.legL, legR: w.legR, bob: w.bob } : { bob: 1.6 * Math.sin(q * 2.1 + 2) }),
      armR: wave || (walking ? w.armR : 6 + (act ? 8 * Math.sin((q - PRE1 - T1.nama) * 2.4) : 0)), armL: walking ? w.armL : 8, mouth: talk, shut: blink(q, 3.4, .9), headR: q > 1.4 ? 3 * Math.sin(q * 1.3) : 0 }, f);
    // judul turun dari atas pada kata 'pemeriksaan', menetap pada y 150
    const u = span(q, tIn, tIn + .6), bounce = u >= 1 ? 4 * Math.exp(-(q - tIn - .6) * 6) * Math.sin((q - tIn - .6) * 18) : 0;
    vis(title, q >= tIn);
    tf(title, `translate(800 ${(-130 + (150 + 130) * u + bounce).toFixed(1)})`);
  });
}
