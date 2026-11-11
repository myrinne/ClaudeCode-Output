'use strict';
// This book's own pieces, loaded right after engine.js. The engine has no Indonesian block in TRANSLATIONS, so the
// interface text (cover, player help, question cards, score card) would fall back to English: it is added here, in
// the book, and the engine copy stays as it is. (The engine reads DECIMAL_SIGN once when it loads, so a decimal
// comma is written by the chapter itself, not by num().)
TRANSLATIONS.id = {
  decimalSign: ',', stageLabel: 'Animasi pelajaran', stageLabelTitled: 'Animasi pelajaran: {title}',
  shortcuts: 'Pintasan papan ketik', lesson: 'Pelajaran', questions: 'Soal',
  helpPlay: 'Putar atau jeda', helpStep: 'Langkah sebelumnya atau berikutnya', helpStepInQuestion: 'Ganti langkah saat soal', helpRestart: 'Mulai dari awal',
  helpCaptions: 'Teks narasi hidup atau mati', helpSpeed: 'Lebih lambat atau lebih cepat', helpFullScreen: 'Layar penuh', helpList: 'Tampilkan daftar ini',
  helpChoose: 'Pilih jawaban atau lingkaran', helpTrueFalse: 'Benar atau salah', helpRows: 'Pindah antar baris',
  helpNumberLine: 'Geser sepanjang garis bilangan', helpEnter: 'Periksa, lalu lanjut',
  helpShowAnswer: 'Tampilkan jawaban', helpLeaveBox: 'Keluar dari kotak jawaban', helpClose: 'Tekan {key} untuk menutup.',
  paused: 'Dijeda. Tekan spasi atau klik untuk melanjutkan.',
  soundFailed: 'Suara tidak dapat diputar. Pelajaran berlanjut dengan teks di layar.',
  startLesson: 'Mulai pelajaran', startFilm: 'Putar', aboutMinutesFilm: 'Sekitar {n} menit, dengan suara.', coverKeys: 'Tekan {space} untuk mulai, {help} untuk pintasan.', spaceKey: 'Spasi',
  chapterNumber: 'Bab {n}', aboutMinutes: 'Sekitar {n} menit, dengan suara dan cek cepat.',
  allChapters: 'Semua bab', playLabel: 'Putar atau jeda (spasi)', backLabel: 'Langkah sebelumnya (panah kiri)', restartLabel: 'Ulangi pelajaran',
  checksInLesson: 'Cek cepat dan latihan ada di pelajaran interaktif.',
  volumeLabel: 'Atur volume', volumeTitle: 'Volume (0 = bisu)', volumeSlider: 'Volume',
  helpLabel: 'Pintasan papan ketik (?)', speedLabel: 'Kecepatan putar (< dan >)', captionsLabel: 'Teks narasi (C)', fullScreenLabel: 'Layar penuh', goToStep: 'Ke langkah {n}: {title}',
  quickCheck: 'Cek cepat', countOf: 'soal {k} dari {n}', check: 'Periksa', showAnswer: 'Lihat jawaban', nextQuestion: 'Soal berikutnya', continue: 'Lanjut',
  correct: 'Benar. ', notQuite: 'Belum tepat. ', answerPrefix: 'Jawaban: ', keysPrefix: 'Tombol: ',
  hintMove: ' pindah, ', hintChoose: ' pilih', hintChooseOrClickGrid: ' pilih, atau klik petak', hintMoveAlongLine: ' geser sepanjang garis, ',
  hintChooseOrClick: ' pilih, atau klik', hintRow: ' baris, ', hintTypeFraction: 'ketik angka seperti 3/4 atau −2 1/4, ', hintTypeNumber: 'ketik angkanya, ',
  hintTypeDecimal: 'ketik angkanya, ', hintNextBox: ' kotak berikutnya, ', hintCheck: ' periksa, ', hintLeaveBox: ' keluar dari kotak',
  hintPickNumber: ' pilih angka, ', hintPickRing: ' pilih lingkarannya',
  rowsRight: '{r} dari {n} benar. Perbaiki baris yang bertanda ✗ lalu periksa lagi.',
  choicesShown: 'pilihan yang benar sudah terpilih.', numbersShown: 'angka yang benar sudah terisi.',
  notPlacedYet: '{x} belum diletakkan.',
  pointLabel: 'Titik {v}', answerBox: 'Jawaban',
  trueLabel: 'Benar', falseLabel: 'Salah',
  chapterComplete: 'Bab {n} selesai', quickChecks: 'Cek cepat', chapterPractice: 'Latihan bab', sources: 'Sumber dalam bab ini', opensSource: '{label}, membuka sumber di tab baru',
  firstTryScore: '{name}: {r} dari {t} benar pada percobaan pertama.', notAttempted: '{name}: belum dicoba.',
  watchAgain: 'Tonton lagi', nextChapter: 'Bab berikutnya',
};

// The book's meanings (style.json look.meaning). The board, ink, NNT magenta, normal and gangguan colours come from
// book.css through COL; these are the ones COL does not have.
const K = {
  rasio: '#1f6fc5',      // rasio VEP1/KVP
  kvp: '#c8641e',        // KVP
  ok: '#3f8a1d',         // normal
  bad: '#d9473a',        // gangguan
  paru: '#6a6a6e',       // cut-off Versi Paru
  nnt: '#b83280',        // NNT
  ink: '#1d1d1f', dim: '#6a6a6e', faint: '#c4bfae', board: '#fbfaf5',
};

// The engine builds its shell (cover, player bar, help panel) when it loads, before the Indonesian block above exists,
// so that text was written in English. Replace it here: every text node and label that equals an English string
// of the interface becomes its Indonesian one (strings with variables are rebuilt where they are used).
(function () {
  const run = () => {
    const en = TRANSLATIONS.en, id = TRANSLATIONS.id, map = new Map();
    for (const k in id) if (typeof en[k] === 'string' && typeof id[k] === 'string' && !/\{/.test(en[k])) map.set(en[k].trim(), id[k].trim());
    const root = document.getElementById('frame') || document.body;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) { const t = n.nodeValue.trim(), to = map.get(t); if (to) n.nodeValue = n.nodeValue.replace(t, to); }
    for (const e of root.querySelectorAll('[aria-label],[title]')) for (const a of ['aria-label', 'title']) { const to = map.get((e.getAttribute(a) || '').trim()); if (to) e.setAttribute(a, to); }
    const meta = document.getElementById('coverMeta');
    if (meta) { const small = meta.parentNode; [...small.childNodes].forEach(n => { if (n !== meta) n.remove(); }); small.insertAdjacentHTML('beforeend', ' ' + translate('coverKeys', { space: `<kbd>${translate('spaceKey')}</kbd>`, help: '<kbd>?</kbd>' })); }
    const close = document.querySelector('.help-close');
    if (close) close.innerHTML = translate('helpClose', { key: '<kbd>Esc</kbd>' });
  };
  if (document.getElementById('bCC')) run(); else document.addEventListener('DOMContentLoaded', run);
})();

// Typed answers with a decimal comma. The engine reads the decimal sign once, when it loads (before the Indonesian
// block above exists), so its answer boxes read "2,68" as nothing. blanksId wraps blanks(): before a row is judged the
// comma of a typed number becomes a point (the boxes keep what was typed), and Show answer writes the comma back.
// The authored answers (box: '2.68') and test() work on points, the text shown to the reader on commas.
const blanksId = rows => (body, api) => {
  const inner = blanks(rows)(body, api), boxes = () => [...body.querySelectorAll('input.box')];
  const asPoint = v => v.trim().replace(/^([−–-]?)\s*(\d+),(\d+)$/, '$1$2.$3');
  return {
    ...inner,
    check() { const saved = boxes().map(b => b.value); boxes().forEach(b => { b.value = asPoint(b.value); }); inner.check(); boxes().forEach((b, i) => { b.value = saved[i]; }); },
    reveal() { const r = inner.reveal(); boxes().forEach(b => { b.value = b.value.replace('.', ','); }); return r; },
  };
};
