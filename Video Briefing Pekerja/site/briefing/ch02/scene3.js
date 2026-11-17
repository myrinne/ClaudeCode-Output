'use strict';
/* Pengingat H-1, adegan 3: "Ada pertanyaan? Hubungi dokter Vidya Cecilia di 0812-2441-8906. Sampai besok!"
   Set 'dapur'. Dokter tengah, bapak dan ibu melambai di akhir. Waktu kata: narration.id.words.txt (ch02). */
const PRE3 = 0.8;
const S3_PHONE = `<g filter="url(#paper)"><rect x="-26" y="-52" width="52" height="104" rx="12" fill="#2f3b45"/><rect x="-20" y="-44" width="40" height="76" rx="6" fill="#8fd3e8"/><circle cx="0" cy="42" r="4" fill="#8fd3e8"/><circle cx="0" cy="-6" r="13" fill="#3f9d6b"/></g>`;

function scene3(p, D) {
  const W = t => PRE3 + t, cam = paperCam(p, 'dapur'), items = [];
  const add = (svg, t0, x, y, s = 1, r = 0, t1 = 1e9) => { const g = prop(cam.stage, svg); vis(g, false); items.push({ g, t0: W(t0), t1: W(t1), x, y, s, r, k: items.length + 10 }); return g; };
  add(s8Card(720, 130, '#fffdf4') + s8T('Ada pertanyaan?', 0, 20, 70), 0.22, 800, 170, 1, 0, 2.15);
  add(s8Card(980, 280, '#fffdf4') + `<g filter="url(#paper)"><rect x="-490" y="-140" width="22" height="280" rx="11" fill="#3f9d6b"/></g>` + s8T('dr. Vidya Cecilia', 40, -36, 68), 2.22, 800, 195, 1, 0);
  add(`<g transform="scale(1.25)">${S3_PHONE}</g>`, 3.94, 395, 255, 1, -6);
  add(s8T('0812-2441-8906', 40, 0, 100, '#2b6a49'), 4.12, 800, 260, 1, 0);
  add(`<g filter="url(#paper)"><rect x="-290" y="-54" width="580" height="108" rx="54" fill="#3f9d6b"/></g>` + s8T('Sampai besok!', 0, 23, 68, '#fff'), 9.49, 800, 392);

  const dok = dokterPuppet(cam.stage), bpk = bapakPuppet(cam.stage), ibu = ibuPuppet(cam.stage);
  cam.cut({ x: 800, y: 450, z: 1 }, 0);
  cam.to({ z: 1.05, y: 470 }, 0, W(10.5));

  sfx('scene3', 0, 'room', 0.25, { loop: true });
  sfx('scene3', W(2.22), 'chime', .5);
  sfx('scene3', W(9.49), 'chime', .5);
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    const j = k => .7 * jit(f >> 1, k);
    for (const it of items) {
      if (q < it.t0 || q >= it.t1) { vis(it.g, false); continue; }
      const k = span(q, it.t0, it.t0 + .22), sc = it.s * (.55 + .45 * k + .08 * Math.sin(k * Math.PI));
      vis(it.g, true); it.g.setAttribute('opacity', k.toFixed(2));
      tf(it.g, `translate(${(it.x + j(it.k)).toFixed(1)},${(it.y + j(it.k + 50)).toFixed(1)}) rotate(${it.r}) scale(${sc.toFixed(3)})`);
    }
    const wave = span(q, W(9.49), W(9.85)), sw = Math.sin((q - W(9.49)) * 9);
    const sp = lips(q, 'scene3', PRE3, 'r03a'), talking = sp !== 'X', done = q > W(10.7);
    dok.pose({ x: 800, y: 800, s: 1, look: .04 * Math.sin(q * .7), mouth: done ? 'smile' : sp, shut: blinking(q, [W(1.2), W(5.4), W(8.6)]),
      bob: 2.5 * Math.sin(q * 2.1), headR: talking ? 2 * Math.sin(q * 2.6) : 0,
      armL: 6 + (talking ? 4 * Math.sin(q * 3.1) : 0), armR: 12 + (talking ? 10 * Math.sin(q * 2.3 + 1) : 0) + wave * (125 + 20 * sw) }, f);
    bpk.pose({ x: 470, y: 800, s: 1, look: .5 + .06 * Math.sin(q * .9), eyeX: .6, mouth: 'smile', shut: blinking(q, [W(3.0), W(7.0)]),
      bob: 2.5 * Math.sin(q * 2.0 + 1), headR: 3 * Math.sin(q * .8), armL: 6 + wave * (130 + 20 * sw), armR: 6 }, f);
    ibu.pose({ x: 1130, y: 800, s: 1, look: -.5 + .06 * Math.sin(q * .8), eyeX: -.6, mouth: 'smile', shut: blinking(q, [W(5.0), W(8.2)]),
      bob: 2.5 * Math.sin(q * 2.2 + 2), headR: 3 * Math.sin(q * .9 + 1), armL: 6, armR: 6 + wave * (92 - 20 * sw) }, f);
  });
}
