# PANDUAN SETUP — Pengisian MCU Otomatis di Windows (Claude Code)

Panduan ini untuk orang yang punya Claude Pro tapi belum pernah pakai
Claude Code, di komputer/laptop Windows. Ikuti urut dari atas.

---

## BAGIAN A — Install Claude Code

1. Buka **PowerShell** (klik Start, ketik "PowerShell", Enter).

2. Cek apakah Node.js sudah terpasang, ketik:
   ```powershell
   node -v
   ```
   - Kalau muncul nomor versi (mis. `v24.17.0`), lanjut ke langkah 3.
   - Kalau muncul error "not recognized", install Node.js dulu dari
     https://nodejs.org (pilih versi LTS, download installer `.msi`,
     buka, ikuti instruksinya sampai selesai — biarkan opsi default apa
     adanya). Setelah itu tutup PowerShell, buka lagi, ulangi `node -v`
     untuk pastikan berhasil.

3. Install Claude Code:
   ```powershell
   npm install -g @anthropic-ai/claude-code
   ```
   Tunggu sampai selesai (biasanya 1-2 menit).

4. Jalankan Claude Code pertama kali:
   ```powershell
   claude
   ```
   Ini akan minta login — ikuti instruksi di layar (biasanya buka browser,
   login pakai akun Claude Pro miliknya sendiri, bukan akun orang lain).

5. Kalau berhasil login, akan muncul prompt Claude Code siap dipakai.
   Ketik `/exit` atau tekan `Ctrl+C` dua kali untuk keluar dulu — nanti
   dibuka lagi setelah folder kerja siap (Bagian C).

---

## BAGIAN B — Install Python & Playwright

1. Cek Python, di PowerShell ketik:
   ```powershell
   python --version
   ```
   - Kalau muncul pesan soal Microsoft Store ("Python was not found; run
     without arguments to install from the Microsoft Store...") — itu
     BUKAN Python asli, cuma shortcut kosong bawaan Windows. **Jangan**
     pakai jalur Microsoft Store, karena sering bikin masalah PATH.
     Install Python asli dari https://python.org/downloads (download
     installer Windows, jalankan, **centang "Add python.exe to PATH"**
     di layar pertama installer sebelum klik Install — ini langkah yang
     paling sering kelewat).
   - Tutup PowerShell, buka lagi, ulangi `python --version` untuk
     pastikan sudah muncul nomor versi (mis. `Python 3.14.6`).

2. Install Playwright:
   ```powershell
   pip install playwright
   playwright install chromium
   ```
   Baris kedua akan download browser Chromium khusus untuk Playwright
   (beda dari Chrome biasa) — proses ini bisa makan waktu beberapa menit,
   biarkan sampai selesai.

---

## BAGIAN C — Salin file kerja (supaya tidak mulai dari nol)

Tidak perlu membuat ulang script — cukup salin file-file ini dari folder
`MCU` yang sudah ada:

**WAJIB disalin** (script & dokumentasi, aman untuk dibagikan — tidak
berisi data pasien):
```
fase0_buka_pasien.py
fase1_baca.py
fase3a_generate_teks.py
fase3b_tulis_ehr.py
fase_batch.py
input_dict.py
konverter_queue.py
protocol_engine.py
PETA_FIELD_EHR.md
Protokol_Interpretasi_MCU_Draft.md
CATATAN_ALUR_KERJA.md
```

**JANGAN disalin** (berisi data pasien dari sesi sebelumnya):
```
queue.json
draft_fase3.json
notes.md / notes_*.md
__pycache__/
```
Kalau file-file itu tidak ada, tidak masalah — akan otomatis dibuat ulang
saat script pertama kali jalan.

**Cara paling gampang:** kirim lewat email/USB/OneDrive cuma file yang
"WAJIB disalin" di atas (bukan seluruh folder), lalu di komputer tujuan:

1. Buat folder baru khusus, mis. buka File Explorer → Documents → klik
   kanan → New → Folder → beri nama `MCU`.
2. Pindahkan file-file yang dikirim tadi ke folder `MCU` itu.

---

## BAGIAN D — Setup Chrome untuk browser automation

1. Tutup semua jendela Chrome yang terbuka.
2. Di PowerShell, ketik (sesuaikan path kalau Chrome ter-install di lokasi
   lain):
   ```powershell
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-mcu"
   ```
3. Di jendela Chrome yang baru terbuka, **login sendiri** ke
   `http://ehr.rscm.co.id/ehr/index.php`.
4. Biarkan Chrome ini tetap terbuka selama kerja — jangan ditutup, dan
   jangan buka Chrome lain untuk situs EHR yang sama (bisa bentrok sesi
   login).

---

## BAGIAN E — Mulai kerja dengan Claude Code

1. Buka PowerShell baru (yang ini terpisah dari PowerShell yang
   menjalankan Chrome di Bagian D — biarkan Chrome tetap jalan di jendela
   lamanya).
2. Masuk ke folder kerja:
   ```powershell
   cd "$HOME\Documents\MCU"
   ```
   (sesuaikan path kalau folder disimpan di tempat lain)
3. Jalankan Claude Code:
   ```powershell
   claude
   ```
4. Setelah Claude Code terbuka, langsung minta seperti ini (ketik di
   prompt Claude Code):
   > "Saya mau pakai script MCU yang sudah ada di folder ini untuk
   > mengisi MCU pegawai. Chrome debug sudah saya buka & login di port
   > 9222. Baca dulu CATATAN_ALUR_KERJA.md untuk paham alurnya."
5. Setelah itu, alurnya: **cukup kasih NRM pasien**, Claude akan jalankan
   `fase0_buka_pasien.py` → `fase1_baca.py` → bersihkan `queue.json` →
   `fase3a_generate_teks.py` (review draft) → `fase3b_tulis_ehr.py
   --tulis --ya` (tulis ke EHR). Untuk banyak pasien sekaligus, tinggal
   kasih semua NRM sekaligus — Claude pakai `fase_batch.py --ya` dan
   hasilnya bisa direview di `notes_YYYY-MM-DD.md` setelah selesai.

---

## Hal penting yang perlu diketahui

- **Login EHR pakai akun sendiri** — jangan pernah pakai akun/password
  orang lain untuk ini.
- **Field auto-save begitu ditulis** — tidak ada undo di sisi RSCM. Fase
  3b/`fase_batch.py` selalu tampilkan preview sebelum benar-benar
  menulis — baca dulu sebelum konfirmasi (kecuali sudah terbiasa dan
  memilih jalur batch langsung `--ya`, sesuai kebijakan yang sudah
  berjalan).
- **Approve Dokter** tidak pernah disentuh manual oleh script kecuali
  lewat kebijakan auto-approve `fase_batch.py` (flag hijau/kuning) —
  lihat detail di `CATATAN_ALUR_KERJA.md`.
- Beberapa ambang klinis di `input_dict.py`/`protocol_engine.py` sudah
  dikonfirmasi berdasarkan kasus-kasus nyata sebelumnya — kalau ada kasus
  baru yang aturannya belum ada atau terasa salah, sebaiknya didiskusikan
  dulu dengan dr. Vidya sebelum dipakai ke pasien sungguhan.
- Field radiologi (578) tidak punya kotak isian terpisah — kesimpulannya
  otomatis masuk ke bagian "Rontgen thorax :" di dalam field Kesimpulan
  gabungan (581). Ini sudah dikonfirmasi lewat pengecekan struktur HTML
  form RSCM.

---

## Troubleshooting cepat

- **"GAGAL menyambung ke Chrome" saat script jalan** → cek Chrome debug
  di Bagian D masih terbuka, dan portnya benar 9222 (jangan tutup jendela
  itu selama bekerja).
- **`python`/`pip`/`node`/`npm`/`claude` dianggap "not recognized"** →
  biasanya PATH belum ke-refresh. Tutup PowerShell sepenuhnya, buka yang
  baru, coba lagi. Kalau masih gagal, cek ulang instalasi di Bagian A/B
  (khususnya centang "Add python.exe to PATH" saat install Python).
- **`playwright install chromium` gagal/lambat** → pastikan koneksi
  internet stabil, coba ulangi perintahnya — ini cuma download browser,
  aman diulang.

---

*Dibuat berdasarkan setup yang sudah berjalan (dr. Vidya, Windows) —
panduan ini format & langkahnya disamakan dengan `PANDUAN_SETUP_MACOS.md`
supaya konsisten, tapi seluruh perintah dan path disesuaikan untuk
Windows/PowerShell.*
