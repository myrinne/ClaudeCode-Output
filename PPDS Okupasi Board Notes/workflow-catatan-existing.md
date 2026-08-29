# Workflow: Reorganisasi Catatan Board yang Sudah Ada

Berlaku ketika **sudah ada catatan lama** (file `.docx`) untuk suatu topik di `PPDS Okupasi\Materi Board`
(topik: Audiometri, Kecacatan, Spirometri, ILO, JSA+Ergonomi, AMA) dan ingin disusun ulang mengikuti
outline baru.

> Untuk kasus **belum ada catatan sama sekali** untuk suatu topik, lihat `workflow-catatan-baru.md`
> (menyusul, alur kerja terpisah).

## Langkah-langkah

1. **Tentukan topik.** Kalau belum disebutkan, tanya dulu topik mana yang mau dikerjakan. Kerjakan
   satu topik pada satu waktu — jangan semua topik sekaligus.

2. **Ekstrak catatan lama.** Gunakan `python-docx` untuk membaca `.docx` lama secara penuh
   (semua paragraf berikut nama style-nya, dan semua tabel). Tools baca file biasa (mis. `Read`)
   tidak bisa membuka `.docx` langsung.
   - Kalau muncul `PackageNotFoundError` atau `PermissionError`: file sedang terbuka di Word
     (terkunci OneDrive). Minta ditutup dulu, lalu coba lagi.

3. **Petakan ke outline baru.** Cocokkan tiap paragraf/tabel dari catatan lama ke section yang sesuai
   di outline baru yang diberikan pengguna. Identifikasi section outline yang **tidak** punya konten
   yang cocok — ini gap sungguhan yang perlu diisi.

4. **Isi gap lewat NotebookLM.** Untuk tiap gap, cek notebook topik terkait di notebook.google.com
   (mis. notebook "Spirometri").
   - Tanyakan **satu pertanyaan per waktu** — jangan digabung jadi satu prompt berisi beberapa
     pertanyaan sekaligus.
   - CLI `notebooklm` biasanya tidak terpasang di mesin ini (PATH-nya menunjuk ke profil user
     `LENOVO` yang tidak ada). Pakai Chrome browser automation sebagai gantinya:
     navigasi ke notebooklm.google.com (redirect ke notebook.google.com) → buka notebook topik dari
     grid → klik kotak chat → ketik pertanyaan → tunggu status "Responding..." hilang → ambil jawaban
     dengan `read_page` memakai `max_chars` besar (mis. 260000) karena default 50000 sering
     memotong jawaban panjang. `get_page_text` tidak reliable di situs ini (pernah mengembalikan
     DOM emoji-picker basi, bukan isi chat).

5. **Tulis hasil ke file baru.** Buat file **baru** `<TopikNama>_v2.docx` di folder yang sama dengan
   file asli — **jangan menimpa** file aslinya. Gunakan `python-docx`. Pertahankan tabel asli,
   callout clinical-pearl/red-flag, dan bank kasus OSCE, tapi ditempatkan sesuai posisi baru di
   outline.
   - Kalau dua section outline yang berbeda ternyata butuh tabel/rumus yang sama, cross-reference
     saja (rujuk ke section lain), jangan duplikasi tabelnya.

6. **Tandai konten sisipan dengan jelas.**
   - Konten yang benar-benar ditemukan dari sumber NotebookLM → beri tag
     `[BARU — NotebookLM: <nama dokumen sumber>]`.
   - Konten yang NotebookLM sendiri akui **tidak ada** di sumbernya (general-knowledge fill-in,
     misalnya framework "7 Langkah Diagnosis PAK") → beri kotak **CATATAN SUMBER** yang eksplisit,
     memberi tahu pengguna untuk memverifikasi kata-katanya ke mentor sebelum dihafal mentah-mentah.

## Catatan tambahan

- Preferensi pengguna: satu topik per sesi kerja, satu pertanyaan NotebookLM per waktu — kedua hal
  ini sudah dikonfirmasi, jangan dibundel demi "efisiensi".
- File hasil selalu `_v2`, tidak pernah menimpa file lama — file lama tetap jadi arsip/pembanding.
