'use strict';
/* Adegan 11: hak memilih dan penutup. Set 'dapur'.
   Dokter Vidya (tengah, bibir mengikuti suara) dan dua pekerja (bapak kiri, ibu kanan) berdiri berdampingan.
   0-8: "Boleh berhenti kapan saja / tanpa alasan", "Namun, partisipasi ... sangat diharapkan".
   9-12: "Ringkasan", "Lembar penjelasan". 12.49-: kartu kontak (tanpa diucapkan); 14.49-18.4 kartu "Hasil akhir untuk semua peserta"; 18.42 "Terima kasih" dan lambaian.
   Memakai pembantu s8T, s8Card, S8_CHECK dari scene8.js. Waktu kata = detik klip adegan + PRE11. */
const PRE11 = 0.8;

const S11_DOC = `<g filter="url(#paper)"><rect x="-44" y="-56" width="88" height="112" rx="9" fill="#fffdf4"/><path d="M-26,-30 h52 M-26,-12 h52 M-26,6 h52 M-26,24 h30" stroke="#9aa5ad" stroke-width="7" stroke-linecap="round"/></g>`;
const S11_PHONE = `<g filter="url(#paper)"><rect x="-26" y="-52" width="52" height="104" rx="12" fill="#2f3b45"/><rect x="-20" y="-44" width="40" height="76" rx="6" fill="#8fd3e8"/><circle cx="0" cy="42" r="4" fill="#8fd3e8"/><circle cx="0" cy="-6" r="13" fill="#3f9d6b"/></g>`;

function scene11(p, D) {
  const W = t => PRE11 + t, cam = paperCam(p, 'dapur'), items = [];
  const add = (svg, t0, x, y, s = 1, r = 0, t1 = 1e9) => { const g = prop(cam.stage, svg); vis(g, false); items.push({ g, t0: W(t0), t1: W(t1), x, y, s, r, k: items.length + 10 }); return g; };
  // ----- teks layar (di atas kepala; tokoh tetap di bawah). Waktu = kata - 0.22 -----
  add(s8Card(960, 190, '#fffdf4') + s8T('Boleh berhenti kapan saja', 0, -6, 62), 0.85, 800, 180, 1, 0, 3.9);
  add(s8T('tanpa alasan', 0, 0, 52, '#3f7d56'), 2.22, 800, 232, 1, 0, 3.9);
  add(s8Card(1100, 190, '#fffdf4') + s8T('Namun, partisipasi Bapak dan Ibu', 0, -6, 52), 3.84, 800, 180, 1, 0, 8.3);
  add(s8T('sangat diharapkan', 0, 0, 58, '#3f7d56'), 6.16, 800, 236, 1, 0, 8.3);
  add(s8Card(560, 110, '#ddeef2') + s8T('Ringkasan', 0, 20, 60), 9.19, 800, 180, 1, 0, 10.9);
  add(s8Card(560, 130, '#fff1d6') + `<g transform="translate(-205,0) scale(.7)">${S11_DOC}</g>` + s8T('Lembar penjelasan', 40, 16, 42), 11.37, 800, 190, 1, -2, 12.4);
  // kartu kontak: dari "tanyakan kepada saya" sampai akhir, tidak diucapkan
  add(s8Card(980, 240, '#fffdf4') + `<g filter="url(#paper)"><rect x="-490" y="-120" width="22" height="240" rx="11" fill="#3f9d6b"/></g>` + s8T('Tanyakan kepada', 40, -66, 38, '#3f7d56') + s8T('dr. Vidya Cecilia', 40, -12, 58), 12.49, 800, 175, 1, 0);
  add(`<g transform="scale(1.1)">${S11_PHONE}</g>`, 12.8, 395, 245, 1, -6);
  add(s8T('0812-2441-8906', 40, 0, 88, '#2b6a49'), 12.8, 800, 240, 1, 0);
  // kartu hasil akhir: "Hasil akhirnya ... semua peserta" (di bawah kartu kontak)
  add(s8Card(900, 130, '#ddeef2') + `<g transform="translate(-380,0) scale(.62)">${S11_DOC}</g>` + s8T('Hasil akhir untuk', 50, -22, 44, '#3f7d56') + s8T('semua peserta', 50, 28, 56), 14.49, 800, 380, 1, 1.5, 18.4);
  add(`<g filter="url(#paper)"><rect x="-240" y="-52" width="480" height="104" rx="52" fill="#3f9d6b"/></g>` + s8T('Terima kasih', 0, 22, 66, '#fff'), 18.42, 800, 380);

  const dok = dokterPuppet(cam.stage), bpk = bapakPuppet(cam.stage), ibu = ibuPuppet(cam.stage);
  cam.to({ z: 1.03 }, 0, W(18.2));
  cam.to({ z: 1.06, y: 460 }, W(18.2), 1.6);

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
    const wave = span(q, W(18.42), W(18.79)), sw = Math.sin((q - W(18.42)) * 9);
    const sp = lips(q, 'scene11', PRE11, 's11a', 's11b'), talking = sp !== 'X', done = q > W(19.7);
    dok.pose({ x: 800, y: 800, s: 1, look: .04 * Math.sin(q * .7), mouth: done ? 'smile' : sp, shut: blinking(q, [W(1.2), W(5.4), W(9.9), W(13.0), W(16.0), W(19.2)]),
      bob: 2.5 * Math.sin(q * 2.1), headR: talking ? 2 * Math.sin(q * 2.6) : 0,
      armL: 6 + (talking ? 4 * Math.sin(q * 3.1) : 0), armR: 12 + (talking ? 10 * Math.sin(q * 2.3 + 1) : 0) + wave * (125 + 20 * sw) }, f);
    bpk.pose({ x: 470, y: 800, s: 1, look: .5 + .06 * Math.sin(q * .9), eyeX: .6, mouth: 'smile', shut: blinking(q, [W(3.0), W(7.5), W(11.5), W(14.0), W(17.5)]),
      bob: 2.5 * Math.sin(q * 2.0 + 1), headR: 3 * Math.sin(q * .8), armL: 6 + wave * (130 + 20 * sw), armR: 6 }, f);
    ibu.pose({ x: 1130, y: 800, s: 1, look: -.5 + .06 * Math.sin(q * .8), eyeX: -.6, mouth: 'smile', shut: blinking(q, [W(5.0), W(9.5), W(12.2), W(15.0), W(18.0)]),
      bob: 2.5 * Math.sin(q * 2.2 + 2), headR: 3 * Math.sin(q * .9 + 1), armL: 6, armR: 6 + wave * (92 - 20 * sw) }, f);
  });
}
