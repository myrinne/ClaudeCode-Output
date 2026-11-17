/* cast_briefing.js — tokoh video briefing, di atas spKid (cast.js). Dimuat SESUDAH cast.js.
   dokterPuppet(parent)  : dr. Vidya, perempuan, rambut panjang, snelli putih, TANPA hijab (aturan poster/ilustrasi).
   bapakPuppet(parent, o): pekerja dapur laki-laki, topi koki, seragam hijau.
   ibuPuppet(parent, o)  : pekerja dapur perempuan, hijab, seragam hijau.
   Semua mengikuti kontrak kidPuppet (pose x,y,s,look,mouth,brow,armL/armR,reach,hold, dst; lihat header cast.js).
   Palet: dapur oranye-krem, ruang biru-hijau, aksen manfaat hijau '#3f9d6b', larangan merah '#c8322f'. */
'use strict';
const GREEN_UNI = { coat: '#4f9a6a', stripe: '#f4f1ea', pants: '#34584a' };

SHAPES.dokter = { ...SHAPES.kid, cheeks: [48, -222], slide: 26,
  hair: ['#2a1f1a', 'M-92,-250 C-100,-332 -58,-342 0,-342 C58,-342 100,-332 92,-250 L98,-120 Q80,-104 60,-124 L74,-262 Q0,-300 -74,-262 L-60,-124 Q-80,-104 -98,-120 Z'] };
SHAPES.bapak = { ...SHAPES.kid, slide: 28,
  hair: ['#1d1a1a', 'M-90,-258 C-94,-312 -56,-326 0,-326 C56,-326 94,-312 90,-258 L72,-278 Q0,-292 -72,-278 Z'],
  hat: '<path d="M-72,-312 C-100,-372 -40,-408 0,-392 C40,-408 100,-372 72,-312 Z" fill="#fbfbf7"/><rect x="-76" y="-322" width="152" height="20" rx="7" fill="#e9e6dc"/>' };
SHAPES.ibu = { ...SHAPES.kid, cheeks: [50, -222], slide: 18,
  hair: ['#2f7d6b', 'M0,0'],
  hat: '<path fill-rule="evenodd" fill="#2f7d6b" d="M-108,-250 C-114,-346 -60,-356 0,-356 C60,-356 114,-346 108,-250 L112,-160 Q0,-132 -112,-160 Z M-80,-248 a80,82 0 1,0 160,0 a80,82 0 1,0 -160,0 Z"/>' };

const dokterPuppet = (p, o = {}) => spKid(p, 'dokter', { skin: '#f0cfae', coat: '#fafafa', stripe: '#5aa6c9', pants: '#3b4a6b', cuff: '#e4edf1', ...o });
const bapakPuppet = (p, o = {}) => spKid(p, 'bapak', { skin: '#d9a77c', ...GREEN_UNI, ...o });
const ibuPuppet = (p, o = {}) => spKid(p, 'ibu', { skin: '#e8be98', ...GREEN_UNI, coat: '#5aa77a', ...o });
