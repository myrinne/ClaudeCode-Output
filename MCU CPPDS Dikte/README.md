# Dikte MCU CPPDS

Rekam percakapan anamnesis → transkrip lokal (Whisper, audio tidak keluar dari laptop) → Claude menyusun
bagian dokter di template Pemkes CPPDS FKUI → hasil ditambahkan ke `hasil/<tanggal>.md` dan **anamnesis
langsung ada di clipboard**, tinggal Ctrl+V ke rekam medis.

## Cara pakai

1. Klik dua kali **`Jalankan Dikte MCU.bat`**. Tunggu status "Siap" (±30 dtk, model Whisper dimuat).
2. (Opsional) ketik nama / No RM peserta di kotak identitas.
3. Tekan **F9** (bisa dari jendela mana pun, termasuk browser RM) atau tombol ⏺ → mulai rekam.
4. Anamnesis seperti biasa. Temuan PF abnormal bisa didikte: *"catat: serumen kanan menutup"*.
5. Tekan **F9** lagi → stop. Proses jalan di latar belakang; Anda bisa langsung rekam peserta berikutnya.
6. Setelah ±10–40 dtk status hijau "✅ … sudah di clipboard" → baca sekilas di jendela → **Ctrl+V** di RM.
   - "Salin PF abnormal" untuk temuan PF; saran ICD-10 tampil di jendela (ketik kodenya di kolom diagnosis RM).
   - Baris berisi **`[?]`** = tidak ditanyakan / tidak terdengar → lengkapi sendiri.
7. Semua peserta hari itu terkumpul di `hasil/<tanggal>.md` (tombol "Buka file hari ini"), lengkap dengan transkrip.

## Catatan penting

- **Butuh internet** untuk langkah Claude. Jika gagal, transkrip mentah tetap ditulis ke .md dan masuk clipboard.
- Saran ICD dan isi anamnesis = **draf**; tanggung jawab klinis tetap pada dokter. Cek bagian "⚠ Perlu dicek".
- Beri tahu peserta bahwa percakapan direkam untuk membantu pencatatan. Audio dihapus otomatis setelah ditranskripsi.
- `hasil/` berisi data pasien dan **di-gitignore** (tidak pernah di-push ke GitHub).
- Mengubah format/aturan/daftar ICD: edit `instruksi_ringkas.md` (berlaku di peserta berikutnya setelah aplikasi dibuka ulang).
- Model Claude: default `sonnet` (Haiku diuji lebih lambat dan melewatkan nama). Ganti via env `DIKTE_CLAUDE_MODEL`.

## Teknis

- Rekam: ffmpeg dshow (mikrofon pertama yang terdeteksi), 16 kHz mono.
- ASR: faster-whisper `large-v3-turbo` int8 CPU (cadangan `small`), bahasa `id`, VAD aktif.
- Claude: `claude -p` mode stream-json. Satu sesi "hangat" selalu disiapkan di latar belakang dan dipakai untuk
  **satu peserta saja** lalu ditutup, sehingga konteks antarpeserta tidak tercampur dan start-up CLI (±15 dtk) tidak ditunggu.
- Python: venv `~/.cache/mcu-dikte-venv` (cadangan: venv WhisperX plugin /watch).
