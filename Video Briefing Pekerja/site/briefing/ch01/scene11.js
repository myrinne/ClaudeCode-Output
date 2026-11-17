'use strict';
/* Adegan 11: hak memilih dan penutup. Set 'dapur'.
   Dokter Vidya (tengah, bibir mengikuti suara) dan dua pekerja (bapak kiri, ibu kanan) berdiri berdampingan.
   0-7.7: "Boleh berhenti kapan saja / tanpa alasan", "Tidak ikut pun / tidak memengaruhi pekerjaan".
   8-14.6: "Ringkasan", "Lembar penjelasan", "Tanyakan apa saja". 14.8-: kartu kontak besar; 22.33 "Terima kasih" dan lambaian.
   Memakai pembantu s8T, s8Card, S8_CHECK dari scene8.js. Waktu kata = detik klip adegan + PRE11. */
const PRE11 = 0.8;

const S11_DOC = `<g filter="url(#paper)"><rect x="-44" y="-56" width="88" height="112" rx="9" fill="#fffdf4"/><path d="M-26,-30 h52 M-26,-12 h52 M-26,6 h52 M-26,24 h30" stroke="#9aa5ad" stroke-width="7" stroke-linecap="round"/></g>`;
const S11_PHONE = `<g filter="url(#paper)"><rect x="-26" y="-52" width="52" height="104" rx="12" fill="#2f3b45"/><rect x="-20" y="-44" width="40" height="76" rx="6" fill="#8fd3e8"/><circle cx="0" cy="42" r="4" fill="#8fd3e8"/><circle cx="0" cy="-6" r="13" fill="#3f9d6b"/></g>`;

function scene11(p, D) {
  const W = t => PRE11 + t, cam = paperCam(p, 'dapur'), items = [];
  const add = (svg, t0, x, y, s = 1, r = 0, t1 = 1e9) => { const g = prop(cam.stage, svg); vis(g, false); items.push({ g, t0: W(t0), t1: W(t1), x, y, s, r, k: items.length + 10 }); return g; };
  // ----- teks layar (di atas kepala; tokoh tetap di bawah) -----
  add(s8Card(960, 190, '#fffdf4') + s8T('Boleh berhenti kapan saja', 0, -6, 62), 1.49, 800, 180, 1, 0, 4.0);
  add(s8T('tanpa alasan', 0, 0, 52, '#3f7d56'), 2.62, 800, 232, 1, 0, 4.0);
  add(s8Card(960, 190, '#fffdf4') + s8T('Tidak ikut pun', 0, -6, 62), 4.24, 800, 180, 1, 0, 7.9);
  add(s8T('tidak memengaruhi pekerjaan', 0, 0, 52, '#3f7d56'), 5.35, 800, 232, 1, 0, 7.9);
  add(s8Card(560, 110, '#ddeef2') + s8T('Ringkasan', 0, 20, 60), 8.92, 800, 180, 1, 0, 10.9);
  add(s8Card(560, 130, '#fff1d6') + `<g transform="translate(-205,0) scale(.7)">${S11_DOC}</g>` + s8T('Lembar penjelasan', 40, 16, 42), 11.13, 420, 190, 1, -2, 14.6);
  add(s8Card(560, 130, '#e3f1e8') + s8T('Tanyakan apa saja', 0, 16, 50), 12.43, 1180, 190, 1, 2, 14.6);
  // kartu kontak
  add(s8Card(980, 270, '#fffdf4') + `<g filter="url(#paper)"><rect x="-490" y="-135" width="22" height="270" rx="11" fill="#3f9d6b"/></g>` + s8T('dr. Vidya Cecilia', 40, -34, 66), 14.79, 800, 220, 1, 0);
  add(`<g transform="scale(1.2)">${S11_PHONE}</g>`, 16.73, 395, 275, 1, -6);
  add(s8T('0812-2441-8906', 40, 0, 100, '#2b6a49'), 17.06, 800, 280, 1, 0);
  add(`<g filter="url(#paper)"><rect x="-240" y="-52" width="480" height="104" rx="52" fill="#3f9d6b"/></g>` + s8T('Terima kasih', 0, 22, 66, '#fff'), 22.33, 800, 410);

  const dok = dokterPuppet(cam.stage), bpk = bapakPuppet(cam.stage), ibu = ibuPuppet(cam.stage);
  cam.to({ z: 1.03 }, 0, W(14.3));
  cam.to({ z: 1.07, y: 470 }, W(14.3), 1.6);

  // sfx (tools/briefing/add_sfx.py)
  sfx('scene11', 0, 'room', 0.25, { loop: true });
  stopClock(D, (q, f) => {
    cam.apply(q, f);
    const j = k => .7 * jit(f >> 1, k);
    for (const it of items) {
      if (q < it.t0 || q >= it.t1) { vis(it.g, false); continue; }
      const k = span(q, it.t0, it.t0 + .22), sc = it.s * (.55 + .45 * k + .08 * Math.sin(k * Math.PI));
      vis(it.g, true); it.g.setAttribute('opacity', k.toFixed(2));
      tf(it.g, `translate(${(it.x + j(it.k)).toFixed(1)},${(it.y + j(it.k + 50)).toFixed(1)}) rotate(${it.r}) scale(${sc.toFixed(3)})`);
    }
    // lambaian pada "Terima kasih"
    const wave = span(q, W(22.33), W(22.7)), sw = Math.sin((q - W(22.33)) * 9);
    const sp = lips(q, 'scene11', PRE11, 's11a', 's11b'), talking = sp !== 'X', done = q > W(23.7);
    dok.pose({ x: 800, y: 800, s: 1, look: .04 * Math.sin(q * .7), mouth: done ? 'smile' : sp, shut: blinking(q, [W(1.2), W(6.4), W(11.9), W(18.5), W(21.2)]),
      bob: 2.5 * Math.sin(q * 2.1), headR: talking ? 2 * Math.sin(q * 2.6) : 0,
      armL: 6 + (talking ? 4 * Math.sin(q * 3.1) : 0), armR: 12 + (talking ? 10 * Math.sin(q * 2.3 + 1) : 0) + wave * (125 + 20 * sw) }, f);
    bpk.pose({ x: 470, y: 800, s: 1, look: .5 + .06 * Math.sin(q * .9), eyeX: .6, mouth: 'smile', shut: blinking(q, [W(3.0), W(9.0), W(15.4), W(20.0)]),
      bob: 2.5 * Math.sin(q * 2.0 + 1), headR: 3 * Math.sin(q * .8), armL: 6 + wave * (130 + 20 * sw), armR: 6 }, f);
    ibu.pose({ x: 1130, y: 800, s: 1, look: -.5 + .06 * Math.sin(q * .8), eyeX: -.6, mouth: 'smile', shut: blinking(q, [W(5.0), W(12.2), W(17.8), W(21.7)]),
      bob: 2.5 * Math.sin(q * 2.2 + 2), headR: 3 * Math.sin(q * .9 + 1), armL: 6, armR: 6 + wave * (92 - 20 * sw) }, f);
  });
}
