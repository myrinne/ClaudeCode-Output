'use strict';
/* Pengingat H-1, adegan 1: "Besok Bapak dan Ibu ada pemeriksaan kulit dan panas di Instalasi Gizi. Ingat empat hal ya."
   Set 'dapur'. Dokter (tengah, bibir mengikuti suara), bapak kiri, ibu kanan. Kartu teks pada kata-katanya.
   Waktu kata: narration.id.words.txt (ch02), jam beat = PRE1 + waktu. Memakai s8T/s8Card dari ../ch01/scene8.js. */
const PRE1 = 0.8;

function scene1(p, D) {
  const W = t => PRE1 + t, cam = paperCam(p, 'dapur'), items = [];
  const add = (svg, t0, x, y, s = 1, r = 0, t1 = 1e9) => { const g = prop(cam.stage, svg); vis(g, false); items.push({ g, t0: W(t0), t1: W(t1), x, y, s, r, k: items.length + 10 }); return g; };
  add(s8Card(560, 170, '#fff1d6') + s8T('BESOK', 0, 26, 110, '#c8322f'), 0.22, 800, 190, 1, 0, 1.8);
  add(s8Card(1000, 150, '#fffdf4') + s8T('Pemeriksaan kulit dan panas', 0, 20, 62), 1.88, 800, 190, 1, 0, 3.6);
  add(s8Card(1000, 150, '#fffdf4') + s8T('di Instalasi Gizi', 0, 20, 66), 3.67, 800, 190, 1, 0, 5.55);
  add(s8Card(780, 190, '#3f9d6b') + s8T('Ingat 4 hal', 0, 26, 94, '#fff'), 5.63, 800, 195, 1, 0);

  const dok = dokterPuppet(cam.stage), bpk = bapakPuppet(cam.stage), ibu = ibuPuppet(cam.stage);
  cam.cut({ x: 800, y: 450, z: 1 }, 0);
  cam.to({ z: 1.06, y: 470 }, 0, W(7.6));

  // sfx
  sfx('scene1', 0, 'room', 0.25, { loop: true });
  sfx('scene1', W(0.22), 'chime', .5);
  sfx('scene1', W(5.99), 'chime', .5);
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    const j = k => .7 * jit(f >> 1, k);
    for (const it of items) {
      if (q < it.t0 || q >= it.t1) { vis(it.g, false); continue; }
      const k = span(q, it.t0, it.t0 + .22), sc = it.s * (.55 + .45 * k + .08 * Math.sin(k * Math.PI));
      vis(it.g, true); it.g.setAttribute('opacity', k.toFixed(2));
      tf(it.g, `translate(${(it.x + j(it.k)).toFixed(1)},${(it.y + j(it.k + 50)).toFixed(1)}) rotate(${it.r}) scale(${sc.toFixed(3)})`);
    }
    // dokter melambai pada "Besok", lalu bicara dan mengangkat empat jari kecil pada "empat"
    const wave = between(q, W(0.2), W(1.7)) ? 125 + 20 * Math.sin((q - W(0.2)) * 9) : 0;
    const sp = lips(q, 'scene1', PRE1, 'r01a'), talking = sp !== 'X';
    dok.pose({ x: 800, y: 800, s: 1, look: .04 * Math.sin(q * .7), mouth: sp, shut: blinking(q, [W(1.0), W(4.6), W(7.0)]),
      bob: 2.5 * Math.sin(q * 2.1), headR: talking ? 2 * Math.sin(q * 2.6) : 0,
      armL: 6 + (talking ? 4 * Math.sin(q * 3.1) : 0), armR: 12 + (talking ? 8 * Math.sin(q * 2.3 + 1) : 0) + wave }, f);
    bpk.pose({ x: 470, y: 800, s: 1, look: .5 + .06 * Math.sin(q * .9), eyeX: .6, mouth: 'smile', shut: blinking(q, [W(2.0), W(5.4)]),
      bob: 2.5 * Math.sin(q * 2.0 + 1), headR: 3 * Math.sin(q * .8), armL: 6, armR: 6 }, f);
    ibu.pose({ x: 1130, y: 800, s: 1, look: -.5 + .06 * Math.sin(q * .8), eyeX: -.6, mouth: 'smile', shut: blinking(q, [W(3.2), W(6.8)]),
      bob: 2.5 * Math.sin(q * 2.2 + 2), headR: 3 * Math.sin(q * .9 + 1), armL: 6, armR: 6 }, f);
  });
}
