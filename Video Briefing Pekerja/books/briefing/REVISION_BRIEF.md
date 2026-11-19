# Brief revisi video utama (naskah v3, suara 1,15x)

Kamu merevisi HANYA file `site/briefing/ch01/sceneN.js` milikmu. Jangan ubah lib/, index.html, audio, narasi, atau file adegan lain. Jangan commit. Baca dulu `books/briefing/WORKER_BRIEF.md` (API, cara melihat hasil; aturan umum masih berlaku) lalu ini.

## Keadaan sekarang
- Naskah final: `naskah_briefing_v3.md`. Klip dan waktu kata: `content/briefing/ch01/narration.id.words.txt` (waktu kata per klip dalam adegan; jam beat = PREn + waktu), `site/briefing/ch01/audio/id/timings.js` (parts/cues). Audio baru, lebih cepat (laju +24%): SEMUA waktu kemunculan ikon/teks yang ditulis sebagai angka di file adegan sekarang salah. Kamu harus menulis ulang waktunya dari `narration.id.words.txt`, kata demi kata.
- Cara paling aman: ganti angka literal dengan konstanta yang kamu turunkan dari words.txt di bagian atas file (satu tabel waktu per adegan), supaya mudah diubah lagi.
- Adegan 2 dan 3 sudah ditukar: sekarang `scene2.js` = "Kenapa dapur dan panas" (klip s02a,s02b), `scene3.js` = "Apa yang Bapak dan Ibu dapat" (klip s03a,s03b,s03c). Isinya sudah diganti nama (PRE2/PRE3, id adegan, id klip). Waktunya saja yang perlu ditulis ulang.
- Gambar lengan bawah baru: `FOREARM()` di `site/briefing/lib/forearm.js` (sudah dipasang di scene5, 6, 7, 9). Adegan 2 (insert lengan di atas kamera) memakai gambar lengan sendiri (`ARM` path + ellipse): ganti agar memakai `FOREARM()` bila memungkinkan (lengan terbaca sebagai lengan bawah dengan telapak tangan), sorotan hijau mengikuti bentuknya.
- Layar kosong dan baca-ulang: lihat hasil dengan `shot.py`/`strip.py` atau skrip playwright sendiri (server preview http://localhost:8765/briefing/ch01/?beat=N, N dari 0). Satu job browser pada satu waktu (memori terbatas).

## Perubahan isi per adegan (di luar waktu)
- **Adegan 1**: teks narasi berubah (salam "Selamat pagi Bapak Ibu."; kalimat "Video ini menjelaskan semuanya" dihapus). Judul "Cek Kulit dan Panas di Dapur Gizi" muncul pada kata "pemeriksaan" (cari kata itu di words.txt).
- **Adegan 2** (dapur panas): sama seperti dulu (adegan 3 lama), hanya waktu dan tukar nomor.
- **Adegan 3** (manfaat): sama seperti dulu (adegan 2 lama), hanya waktu.
- **Adegan 4**: tetap; waktu saja.
- **Adegan 5**: HAPUS shot denah dua warna dan chip "hanya untuk pencatatan" dan chip "Ditanya di hari pemeriksaan". Isi sekarang: (1) pekerja + kartu usia 18-55 tahun dan masa kerja >= 3 bulan; (2) kartu kondisi yang belum bisa ikut: sakit jantung, stroke, kencing manis, kelainan kulit lengan, tato di lengan (pada kata yang diucapkan); lalu chip "Daftar lengkap: lembar penjelasan" pada kalimat terakhir; lima ikon tambahan tanpa diucapkan boleh tetap muncul setelahnya.
- **Adegan 6**: urutan empat kartu sekarang: 1) 24 jam losion/pelembap/minyak/tabir surya (lengan + krim); 2) 24 jam suplemen (pil, vit C, vit E, glutation, pengencer dahak); 3) 3 jam rokok + darah; 4) 2 jam basahi (keran + lengan + tetes). Susun ulang konten kartu 2, 3, 4 sesuai urutan baru dan tempatnya di kiri-kanan. Bagian "Katakan terus terang" / "Tidak ada sanksi" tetap di akhir.
- **Adegan 7**: judul kartu waktu ada "empat langkah yang akan dilakukan" (kata-kata "Lalu ada empat langkah yang akan dilakukan" di narasi). Tampilkan judul layar "4 langkah yang akan dilakukan" pada saat itu. Kartu 3 (kulit lengan bawah) memakai `FOREARM()` dengan alat kecil (probe TEWL) menempel di kulit lengan bawah (gambar alat kecil: silinder abu-abu kecil bertangkai, di atas lengan, dekat pergelangan). Tidak ada perubahan lain.
- **Adegan 8** (kuesioner): narasi baru: "Pengisian kuesioner singkat, namun yang perlu diperhatikan adalah jam kerja di tiap area dan jenis kegiatan. Jumlahnya harus sama dengan lama kerja Bapak dan Ibu sehari." lalu contoh 5+2+1=8 lalu "Tidak ada jawaban benar atau salah." HAPUS kartu "Boleh dilewati", panah lompat, dan balon "?" pada akhir. Teks layar awal "KUESIONER" tetap.
- **Adegan 9**: tetap; lengan sekarang `FOREARM({ sleeve: true })`, periksa memar dan plester tidak menumpuk aneh di gambar baru.
- **Adegan 10**: ganti teks layar "Tidak bisa ditelusuri" menjadi "Tidak akan ditelusuri"; narasi: "tidak akan ditelusuri ke perorangan".
- **Adegan 11**: narasi baru: "Bapak dan Ibu boleh berhenti kapan saja tanpa alasan. Namun, partisipasi Bapak dan Ibu sangat diharapkan." / "Video ini ringkasan. Silakan baca lembar penjelasan dan tanyakan kepada saya. Terima kasih." Ganti teks layar awal ("tidak ikut pun / tidak memengaruhi pekerjaan" HAPUS) menjadi "Boleh berhenti kapan saja / tanpa alasan" lalu "Namun, partisipasi Bapak dan Ibu sangat diharapkan". Kartu kontak (nama "dr. Vidya Cecilia" dan nomor 0812-2441-8906) tampil di layar mulai pada kalimat "tanyakan kepada saya" dan tetap sampai akhir, TANPA diucapkan (narasi tidak menyebut nama/nomor). Kartu "Terima kasih" dan lambaian pada "Terima kasih".

## Aturan
- Tiap ikon/teks muncul tepat pada kata yang menyebutnya (waktu kata dikurangi ~0,22 s), bukan lebih awal; jangan ada yang muncul setelah kata lewat. Tulis ulang `sfx('sceneN', t, 'chime', .5)` dengan waktu baru (waktu beat = PREn + waktu kata) atau hapus yang tidak relevan.
- Tidak ada teks dengan outline hitam. Tidak ada yang membaca nama/nomor HP.
- Setelah selesai: lihat frame penting (Read PNG), pastikan tidak ada teks terpotong/tumpang tindih, lalu lapor ringkas: shot per adegan dengan waktunya, masalah tersisa.
