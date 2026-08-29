# Workflow: Membuat Catatan Board dari Nol (Belum Ada Catatan)

Berlaku ketika **belum ada catatan lama sama sekali** untuk suatu topik di `PPDS Okupasi\Materi Board`.

> Untuk kasus **sudah ada catatan lama** yang tinggal disusun ulang, lihat `workflow-catatan-existing.md`.

## Langkah-langkah

1. **Minta outline ke pengguna.** Tanyakan outline catatan untuk 1 topik — kerjakan satu topik
   pada satu waktu, sama seperti alur "catatan existing".

2. **Isi tiap poin outline lewat NotebookLM, satu per satu.**
   - Untuk tiap poin outline, buka notebook topik terkait di notebook.google.com dan tanyakan
     **satu pertanyaan per waktu** (jangan digabung).
   - Nilai jawaban yang didapat: kalau menurut Claude jawabannya sudah cukup memadai/lengkap,
     lanjut ke poin berikutnya.
   - Kalau jawabannya terlalu dangkal/kurang lengkap, **catat dan laporkan ke pengguna** — jangan
     diam-diam dianggap cukup.
   - CLI `notebooklm` biasanya tidak terpasang di mesin ini (PATH menunjuk ke profil `LENOVO` yang
     tidak ada). Pakai Chrome browser automation: navigasi ke notebooklm.google.com (redirect ke
     notebook.google.com) → buka notebook topik dari grid → klik kotak chat → ketik pertanyaan →
     tunggu status "Responding..." hilang → ambil jawaban dengan `read_page` memakai `max_chars`
     besar (mis. 260000), karena default 50000 sering memotong jawaban panjang. `get_page_text`
     tidak reliable di situs ini.

3. **Hasilkan file Word baru di folder ini.** Susun jawaban-jawaban tersebut menjadi catatan utuh
   mengikuti urutan outline, simpan sebagai `.docx` baru (via `python-docx`) di folder
   `PPDS Okupasi Board Notes` ini.

## Catatan tambahan

- Preferensi pengguna yang sudah dikonfirmasi (sama seperti alur catatan existing): satu topik per
  sesi kerja, satu pertanyaan NotebookLM per waktu.
- Poin yang jawabannya dangkal harus dilaporkan ke pengguna, bukan dilewati begitu saja.
