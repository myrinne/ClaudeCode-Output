# CLAUDE.md — Automation External PDF (MCU)

Folder ini mengisi Kesimpulan MCU di EHR RSCM dari PDF hasil pemeriksaan RS/lab luar. Baca `README.md`.

## Aturan wajib (dari pemilik protokol)

1. **SATU NRM per permintaan.** Kalau pengguna memberi lebih dari satu NRM sekaligus, proses HANYA
   yang pertama dan minta yang lain dikirim satu per satu SETELAH NRM ini di-approve. Jangan pernah
   membuat loop, batch, script tambahan, atau menjalankan beberapa NRM berurutan dalam satu permintaan.
2. **Jangan pernah menyentuh Approve Dokter** (`FNDx0000000641`) dengan cara apa pun.
3. **Jangan mengubah `pengaturan.py`** (`SATU_NRM_SAMPAI_APPROVE` harus tetap True), jangan menghapus
   `nrm_terakhir_ditulis.json`, dan jangan mengakali penolakan "NRM sebelumnya belum di-approve" —
   minta pengguna approve dulu di EHR.
4. Jangan mengubah file di `engine/` (protokol klinis). Kalau ada temuan yang belum ada aturannya,
   laporkan ke pengguna, jangan menebak.

## Alur per NRM

Prasyarat: Chrome debug port 9222 terbuka & sudah login EHR (README bagian Persiapan).

1. `python ambil_pdf.py <NRM> <link_drive> [<link_drive_2> ...]` (semua link untuk NRM yang SAMA).
2. Baca SETIAP halaman di `pdf_masuk/<NRM>/`: `berkasN_halM.txt` kalau ada teksnya, `berkasN_halM.png`
   untuk halaman scan/EKG (tetap lihat png kalau teksnya janggal). Tulis `ekstrak/<NRM>.json` persis
   format `contoh_ekstrak.json`:
   - Nama tes, hasil, satuan, rujukan ditulis **persis seperti di PDF** (pemetaan ke nama RSCM urusan
     `kamus_lab.py`; kalau nama tes tidak dikenal, tambahkan aliasnya ke `kamus_lab.py`, jangan
     mengganti nama di ekstrak).
   - `dibaca_dari`: `"teks"` kalau dari .txt, `"gambar"` kalau dari .png.
   - `tanggal` = tanggal pemeriksaan (YYYY-MM-DD) per item; `berkas`/`halaman` sesuai sumber.
   - `tanda_vital`, `radiologi`, `ekg` → `{}` / `null` kalau tidak ada di PDF. Radiologi: salin
     kesimpulan radiolog persis. EKG: `kesan` Normal/Abnormal + deskripsi dari pembaca EKG.
   - Hal penting lain (surat keterangan, catatan lab spt "fraksi Hb varian") → `lain`.
3. `python proses_pdf.py <NRM> --tulis` (sekali saja; kalau gagal, laporkan — jangan diulang otomatis).
4. Laporkan ke pengguna: identitas cocok/tidak, field yang ditulis, kesimpulan/saran/kelaikan,
   nilai yang dibaca dari scan (minta dicocokkan), dan semua catatan PERLU_CEK_MANUAL.
   Ingatkan: baca di EHR lalu approve manual sebelum mengirim NRM berikutnya.

Data pasien (`pdf_masuk/`, `ekstrak/`, `draft/`, `notes_*.md`) tidak boleh dikirim ke layanan luar mana pun.
