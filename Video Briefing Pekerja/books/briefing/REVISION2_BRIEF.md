# Brief revisi 2 (video utama): adegan 2, 3, 7

Baca juga `books/briefing/REVISION_BRIEF.md` dan `WORKER_BRIEF.md` (API, cara melihat hasil, aturan umum; masih berlaku). Kamu hanya mengubah file adegan milikmu di `site/briefing/ch01/`. Jangan commit.

Naskah final: `naskah_briefing_v3.md`. Waktu kata per klip: `content/briefing/ch01/narration.id.words.txt` (jam beat = PREn + waktu; kemunculan = waktu kata - 0,22 s). Audio adegan 2, 3, dan 7 sudah disintesis ulang, jadi waktu di file adegan mu mungkin bergeser: tulis ulang dari words.txt yang baru.

## Adegan 2 (`scene2.js`, dapur panas)
Narasi bertambah: "...dan apakah itu berkaitan dengan keadaan **stres oksidatif** tubuh yang bisa dilihat dari darah." Tampilkan label layar "Stres oksidatif" (kartu kecil, ikon tetes darah) pada kata "stres oksidatif" di bagian insert tubuh/darah. Waktu setelah kalimat itu bergeser: tulis ulang semua waktu dari words.txt.

## Adegan 3 (`scene3.js`, manfaat)
Kartu 1 sekarang: "tahu hasil pemeriksaan sendiri, termasuk berat badan, kulit, dan **stres oksidatif dari darah**". Ganti label tetes darah di kartu 1 agar menyebut stres oksidatif (ikon tetes darah muncul pada kata "stres oksidatif"; boleh tambahkan label kecil "Stres oksidatif"). Karena kalimat memanjang, SEMUA waktu setelahnya bergeser: tulis ulang dari words.txt (kartu 2-4, konsumsi, pelembap, biaya, shot penutup dengan empat area berlabel).

## Adegan 7 (`scene7.js`, hari pemeriksaan)
Narasi baru: "Setelah jam kerja selesai, Bapak dan Ibu istirahat 15 sampai 30 menit di ruangan sejuk. Selama menunggu, isi kuesioner, lalu ditimbang dan diukur tinggi badan." / "Setelah itu dilanjutkan dengan pemeriksaan kulit lengan bawah dengan alat kecil, tidak sakit. Terakhir, darah dari lengan 3 sampai 5 mililiter, kira-kira satu sendok teh, hanya sekali. Panas dan udara di dapur kami ukur sebelumnya, dan tidak mengganggu pekerjaan Bapak dan Ibu."
- Frasa "empat langkah" TIDAK diucapkan lagi, tetapi banner layar "4 langkah yang akan dilakukan" tetap ada di gambar (tampil bersama kartu langkah; waktu munculnya: pada kata "selama menunggu"; ganti chip "Sekitar 30 menit" dengan banner itu atau hapus chip 30 menit bila tidak ada kata yang cocok).
- Kelompokkan kartu: kartu 1-2 (kuesioner, timbang+tinggi badan) diberi chip kecil "Selama menunggu"; kartu 3-4 (kulit lengan bawah, darah) chip "Dilanjutkan dengan pemeriksaan". Kartu 1 muncul pada "isi kuesioner", kartu 2 pada "ditimbang", chip kedua + kartu 3 pada "kulit lengan bawah", kartu 4 pada "darah".
- Kartu terpisah di akhir: "Panas dan udara dapur diukur sebelumnya" (ganti teks lama "di hari lain"), dan tambahan "Tidak mengganggu pekerjaan" pada kata "tidak mengganggu".
- Pastikan layar tidak terlalu penuh: chip kecil, tidak menimpa kartu.

## Aturan
Tidak ada teks beroutline hitam. Nama dan nomor HP tidak dibaca. Server preview: http://localhost:8765/briefing/ch01/?beat=N (adegan 2 = beat 1, adegan 3 = beat 2, adegan 7 = beat 6). Satu job browser pada satu waktu (memori terbatas). Lihat frame (Read PNG) sebelum lapor. Laporan singkat: shot dengan waktunya, masalah tersisa.
