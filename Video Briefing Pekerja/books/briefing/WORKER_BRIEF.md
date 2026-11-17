# Brief untuk agen adegan (video briefing "Cek Kulit dan Panas di Dapur Gizi")

Kamu menulis HANYA file `site/briefing/ch01/sceneN.js` untuk adegan yang diberikan. Jangan ubah file lain (lib/, index.html, sets.js, audio, narasi). Kalau menemukan bug di kit, laporkan, jangan perbaiki sendiri.

Semua path relatif terhadap `Video Briefing Pekerja/`. `SKILL=../.claude/skills/papermorph`. Baca dulu: `$SKILL/references/picture-books/stories.md` (bagian Scenes, shots, cuts), `puppets.md`, dan contoh `site/briefing/lib/*.js` (`cast.js` header, `shared.js`, `paper.js`).

## Cerita dan tujuan
Video 6 menit untuk pekerja Instalasi Gizi RSCM (pendidikan SD sampai S1), dipasang sebelum mereka memutuskan ikut pemeriksaan kulit dan panas. Naskah: `naskah_briefing_v1.md`; storyboard: `books/briefing/storyboard.md` (baca baris adegan milikmu). Prinsip: manfaat untuk pekerja dulu, ramah, jelas, tidak menakut-nakuti, tidak menyebut kata "penelitian". Narator = suara dr. Vidya (perempuan, id-ID). Tidak ada tokoh yang berbicara selain narator. Teks di layar besar, pendek, huruf tebal sans (font-size ≥ 56 px untuk judul angka, ≥ 38 px untuk label), kontras tinggi; angka kunci selalu tampil.

## Kit
- Set: `paperCam(p, 'dapur' | 'ruang' | 'kertas')`. Layout 1600×900; lantai ±y 700; puppet berdiri di `y: 800`.
- Tokoh: `dokterPuppet(cam.stage)` (dr. Vidya, perempuan, TANPA hijab), `bapakPuppet`, `ibuPuppet` (di `lib/cast_briefing.js`; semua kontrak `kidPuppet`). Warna seragam bisa diganti lewat opsi (`coat`, `pants`). Skala normal 0.95–1.1.
- Ikon dan benda: gambar sendiri dengan SVG di dalam scene (`mk('g'/'rect'/'path'...)`, `pf(...)` kertas ber-filter, lihat `paper.js`/`cast.js` untuk `prop()`, `mk`, `tf`, `vis`). Gaya: bentuk kertas datar, tanpa garis tepi hitam, warna matte; palet: dapur krem-oranye, ruang biru-hijau, manfaat hijau `#3f9d6b`, larangan merah `#c8322f`, teks `#2b2b2b`.
- Waktu: setiap adegan = satu beat dengan satu klip gabungan (`scene<N>`). `TIMINGS['scene<N>'].parts[id]` = detik klip `s<NN><x>` dalam audio adegan; `.words` per kata (lihat `audio/id/timings.js`, `shots.js`); helper `clipAt(scene, PRE, clip, t)`, `cueAt`, `lips(q, scene, PRE, 's01a', ...)`, `blinking(q, [..])`, `tween`, `between`, `span`.
- Setiap `sceneN.js` mendefinisikan `const PREn = 0.8;` (detik gambar sebelum suara mulai) dan `function sceneN(p, D) {...}` yang dipanggil `scene<N>(panel(0), D)`. Pakai `stopClock(D, (q, f) => {...})`; semuanya fungsi murni dari `q`.
- Setiap ikon/kartu yang disebut narasi muncul pada saat katanya diucapkan (cari waktu kata di `TIMINGS[...].words`), bukan lebih awal; tetap di layar sampai adegan berakhir atau digantikan kartu berikutnya.
- Lip-sync hanya untuk dokter yang tampil di layar saat bicara (adegan 1, 3, 4, 10, 11); `lips(...)` dengan klip yang sedang berbicara. Adegan lain: narasi tanpa mulut yang bergerak.
- Semua tokoh hidup: berkedip bergantian, napas/gerak kecil, tidak membeku. Tidak ada wajah atau tubuh menembus objek. Tidak ada hijab pada dokter.
- Kamera: potong (`cam.cut`) untuk ganti shot, `cam.to` untuk gerak pelan. 8–14 shot per 30 detik hanya bila isi menuntut; di sini informasi dulu, jangan berlebihan: jelas lebih penting daripada ramai.
- Gunakan hanya fakta dari naskah (angka, jam, urutan). Jangan menambah klaim.

## Cara melihat hasil kerjamu
Server preview sudah berjalan di http://localhost:8765 (jika belum: `python $SKILL/scripts/serve.py 8765 site` dari folder ini). Halaman: `http://localhost:8765/briefing/ch01/?beat=N` (N dari 0; adegan 1 = beat 0).
- Frame penuh: `uv run --with playwright --with pillow python $SKILL/scripts/shot.py ch01 --out books/briefing/review/sN --url http://localhost:8765/briefing/ sceneN:T ...` (T detik pada jam beat; jalankan `--help`).
- Strip gerak: `strip.py ch01 OUT sceneN/0.5 --url http://localhost:8765/briefing/`.
- `check.py` dan `lint.py` pada ch01 untuk error konsol.
Jalankan screenshot sendiri dan LIHAT gambarnya (Read pada PNG) sebelum melapor: teks terpotong? ikon tumpang tindih? puppet keluar frame? kata diucapkan sebelum ikonnya muncul?

## Laporan balik (singkat)
Daftar shot dengan waktunya, hal yang belum beres, bug kit yang kamu temukan. Jangan commit; saya yang commit.
