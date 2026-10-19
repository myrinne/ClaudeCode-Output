# Dikte MCU CPPDS

Rekam percakapan anamnesis → transkrip lokal (Whisper, audio tidak keluar dari laptop) → Claude menyusun
bagian dokter di template Pemkes CPPDS FKUI → hasil ditambahkan ke `hasil/<tanggal>.md` dan **anamnesis
langsung ada di clipboard**, tinggal Ctrl+V ke rekam medis.

## Cara pakai

1. Klik dua kali **`Jalankan Dikte MCU.bat`**. Tunggu status "Siap" (±10 dtk).
2. (Opsional) ketik nama / No RM peserta di kotak identitas.
3. Tekan **F9** (dari jendela mana pun, termasuk browser RM) atau tombol ⏺ → mulai rekam.
4. Anamnesis seperti biasa. Temuan PF **abnormal saja** cukup diucapkan: *"catat, serumen kanan menutup"*,
   *"tonsil T2 hiperemis"*. Yang normal tidak perlu disebut (RM sudah otomatis normal).
5. Tekan **F9** lagi → stop. Peserta berikutnya boleh langsung direkam; proses jalan di latar belakang.
6. ±20–60 dtk kemudian status hijau "✅ … sudah di clipboard" → baca sekilas di jendela → **Ctrl+V** di RM.
   - "Salin PF abnormal" untuk temuan PF; saran ICD-10 tampil di jendela (ketik kodenya di kolom diagnosis RM).
   - Baris berisi **`[?]`** = tidak ditanyakan / tidak terdengar → lengkapi sendiri.
   - Clipboard selalu berisi peserta yang **terakhir selesai diproses**; lihat nama/nomor di status.
7. Semua peserta hari itu terkumpul di `hasil/<tanggal>.md` (tombol "Buka file hari ini"), lengkap dengan transkrip.

## Catatan penting

- **Butuh internet** untuk langkah Claude. Jika gagal, transkrip mentah tetap ditulis ke .md dan masuk clipboard.
- Saran ICD dan isi anamnesis = **draf**; tanggung jawab klinis tetap pada dokter. Cek bagian "⚠ Perlu dicek".
- Beri tahu peserta bahwa percakapan direkam untuk membantu pencatatan.
- Audio disimpan sementara di `~/.cache/mcu-dikte-work/audio` (di luar OneDrive) dan dihapus per potongan setelah
  ditranskripsi. `hasil/` berisi data pasien dan **di-gitignore** (tidak pernah di-push ke GitHub).
- Selama aplikasi terbuka, **F9 dipakai aplikasi ini** di semua jendela.
- Ruangan bising / tanpa suara bisa memunculkan teks halusinasi pendek (mis. "pi, pi, pi"); Claude menandainya di "Perlu dicek".
- Mengubah format/aturan/daftar ICD: edit `instruksi_ringkas.md`, lalu buka ulang aplikasi.
- Model Claude: default `sonnet` (Haiku diuji tidak lebih cepat dan melewatkan nama). Ganti via env `DIKTE_CLAUDE_MODEL`.

## Uji coba sebelum hari H (±2 menit)

Buka aplikasi → F9 → bacakan anamnesis contoh dengan suara normal ±1 menit (termasuk "catat, serumen kanan menutup")
→ F9 → pastikan hasil muncul dan Ctrl+V di Notepad berisi 12 baris anamnesis. Hapus entri uji di `hasil/<tanggal>.md`.

## Teknis

- Rekam: ffmpeg dshow (mikrofon pertama yang terdeteksi), 16 kHz mono, dipotong per 30 dtk (`-f segment`).
- ASR: faster-whisper `large-v3-turbo` int8, 8 thread CPU, bahasa `id`, VAD. Potongan ditranskripsi **selagi rekaman
  berjalan**; segmen yang terpotong di batas potongan dibawa ke potongan berikutnya. Setelah stop hanya potongan
  terakhir yang tersisa. Model di `~/.cache/mcu-dikte-models/large-v3-turbo` (cadangan: `small`).
- Claude: `claude -p` mode stream-json. Satu sesi "hangat" selalu disiapkan di latar belakang dan dipakai untuk
  **satu peserta saja** lalu ditutup → konteks antarpeserta tidak tercampur dan start-up CLI (±15 dtk) tidak ditunggu.
- Python: venv WhisperX plugin /watch (`~/.cache/watch/whisperx-venv`). WAV dibaca dengan modul `wave`
  karena PyAV di venv itu tidak cocok dengan versi faster-whisper.
- Hasil uji 2026-10-19 (audio fiktif 76 dtk): stop → hasil 17 dtk; 12 baris anamnesis, PF abnormal, dan ICD
  (H61.2, K02.1, H52.1) benar.
