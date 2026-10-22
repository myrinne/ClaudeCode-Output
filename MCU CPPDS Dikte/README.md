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
   - Baris yang **kosong** setelah titik dua = tidak ditanyakan / tidak terdengar → isi sendiri bila perlu.
   - Clipboard selalu berisi peserta yang **terakhir selesai diproses**; lihat nama/nomor di status.
7. Semua peserta hari itu terkumpul di `hasil/<tanggal>.md` (tombol "Buka file hari ini"), lengkap dengan transkrip.

## Isi otomatis SIM DoctorTool (sejak 2026-10-22, uji coba)

1. Klik dua kali **`Buka Chrome SIM.bat`** → login SIM di jendela itu (Chrome khusus, port 9223). Pakai jendela ini untuk SIM.
2. Buka aplikasi Dikte seperti biasa.
3. Ketik **sebagian nama** peserta di kotak nama → **Enter**. Rekaman langsung mulai, dan aplikasi membuka pasien di SIM
   (daftar Hari ini → Periksa → cek Pemeriksaan Awal; Keluhan Utama ICPC kosong diisi -30 → tab Pemkes Maba).
   Bila ada >1 nama cocok, pilih di jendela kecil.
4. Anamnesis + PF → **F9** (stop). Setelah hasil dikte keluar, aplikasi mengisi Subjektif (3 kotak), Objektif
   (centang 5 regio, temuan menggantikan `dbn`), Asesmen (Baru, Umum, Bonam, Z02.0, ICD sekunder + E66.9 bila IMT ≥ 25),
   Perencanaan (Rontgen Paru, Pemeriksaan EKG, Darah EDTA, Darah tanpa anti koagulan, Urine), lalu kembali ke Subjektif.
5. Baris SIM di aplikasi menjadi kuning "TERISI" → **cek semua sub-tab → klik Simpan sendiri**. Aplikasi tidak pernah menekan Simpan.
6. Peserta berikutnya baru dibuka di SIM setelah Simpan terdeteksi. Rekamannya tetap langsung jalan.
   Tombol **"Lanjut tanpa Simpan"** muncul bila Anda ingin meninggalkan pasien tanpa menyimpan.

Langkah yang gagal (mis. kode ICD tidak ada di SIM) dilaporkan di baris SIM dan di `hasil/<tanggal>.md`: isi manual.
Bila Chrome SIM tidak terbuka, aplikasi tetap bekerja seperti biasa (clipboard).

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

## Suara peserta kurang terdengar

Evaluasi 43 peserta 2026-10-21: pertanyaan dokter hampir selalu tertangkap, **jawaban peserta** sering hilang/kacau,
dan saat pemeriksaan fisik muncul teks berulang ("Sip! Sip!", "Terima kasih"). Pada simulasi dengan file audio,
jawaban yang 22 dB lebih pelan tetap tertangkap, jadi penyebab utamanya ada **sebelum** audio sampai ke aplikasi:

1. **Matikan efek mikrofon Windows** (paling penting). Laptop ini memakai *Windows Studio Effects – Voice Clarity*
   yang sengaja menonjolkan satu pembicara di depan layar dan meredam suara lain (= peserta).
   - Settings → System → Sound → *Microphone Array on SoundWire Device* → **Audio enhancements: Off**.
   - Win+A (Quick Settings) → **Studio effects** → matikan **Voice focus** (bila ada).
   - Di halaman mikrofon yang sama: **Input volume 100**.
2. **Posisi:** laptop di antara dokter dan peserta, bukan menghadap dokter saja. Lebih baik lagi: mikrofon USB
   *omnidirectional* (mikrofon rapat) di meja, di tengah.
3. **Ulangi jawaban singkat** dengan suara Anda: *"oke, alergi amoksisilin ya"*. Suara dokter paling jelas terekam.

Di aplikasi (sejak 2026-10-22): suara pelan dinaikkan otomatis (`dynaudnorm`), deteksi suara lebih peka,
teks sebelumnya tidak lagi dipakai sebagai petunjuk (pemicu pengulangan), dan frasa berulang ≥3x dibuang.

## Uji coba sebelum hari H (±2 menit)

Buka aplikasi → F9 → bacakan anamnesis contoh dengan suara normal ±1 menit (termasuk "catat, serumen kanan menutup")
→ F9 → pastikan hasil muncul dan Ctrl+V di Notepad berisi anamnesis sesuai format template. Hapus entri uji di `hasil/<tanggal>.md`.

## Teknis

- Rekam: ffmpeg dshow (mikrofon pertama yang terdeteksi), 16 kHz mono, dipotong per 30 dtk (`-f segment`).
- ASR: faster-whisper `large-v3-turbo` int8, 8 thread CPU, bahasa `id`, VAD. Potongan ditranskripsi **selagi rekaman
  berjalan**; segmen yang terpotong di batas potongan dibawa ke potongan berikutnya. Setelah stop hanya potongan
  terakhir yang tersisa. Model di `~/.cache/mcu-dikte-models/large-v3-turbo` (cadangan: `small`).
- Claude: `claude -p` mode stream-json. Satu sesi "hangat" selalu disiapkan di latar belakang dan dipakai untuk
  **satu peserta saja** lalu ditutup → konteks antarpeserta tidak tercampur dan start-up CLI (±15 dtk) tidak ditunggu.
- Python: venv WhisperX plugin /watch (`~/.cache/watch/whisperx-venv`). WAV dibaca dengan modul `wave`
  karena PyAV di venv itu tidak cocok dengan versi faster-whisper.
- Hasil uji 2026-10-19 (audio fiktif 76 dtk): stop → hasil 17 dtk; anamnesis, PF abnormal, dan ICD
  (H61.2, K02.1, H52.1) benar.
