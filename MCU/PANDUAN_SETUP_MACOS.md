# PANDUAN SETUP — Pengisian MCU Otomatis di MacBook (Claude Code)

Panduan ini untuk teman Anda yang punya Claude Pro tapi belum pernah pakai
Claude Code, di MacBook. Ikuti urut dari atas.

---

## BAGIAN A — Install Claude Code

1. Buka aplikasi **Terminal** (cari lewat Spotlight: tekan `Cmd+Space`,
   ketik "Terminal", Enter).

2. Cek apakah Node.js sudah terpasang, ketik:
   ```
   node -v
   ```
   - Kalau muncul nomor versi (mis. `v20.11.0`), lanjut ke langkah 3.
   - Kalau muncul "command not found", install Node.js dulu dari
     https://nodejs.org (pilih versi LTS, download installer `.pkg`,
     buka, ikuti instruksinya sampai selesai). Setelah itu tutup Terminal,
     buka lagi, ulangi `node -v` untuk pastikan berhasil.

3. Install Claude Code:
   ```
   npm install -g @anthropic-ai/claude-code
   ```
   Tunggu sampai selesai (biasanya 1-2 menit).

4. Jalankan Claude Code pertama kali:
   ```
   claude
   ```
   Ini akan minta login — ikuti instruksi di layar (biasanya buka browser,
   login pakai akun Claude Pro miliknya sendiri, bukan akun Anda).

5. Kalau berhasil login, akan muncul prompt Claude Code siap dipakai.
   Ketik `/exit` atau tekan `Ctrl+C` dua kali untuk keluar dulu — nanti
   dibuka lagi setelah folder kerja siap (Bagian C).

---

## BAGIAN B — Install Python & Playwright

1. Cek Python, di Terminal ketik:
   ```
   python3 --version
   ```
   Kalau belum ada, install lewat https://python.org (download installer
   macOS, jalankan seperti biasa) — atau kalau sudah pernah install
   Homebrew, bisa `brew install python3`.

2. Install Playwright:
   ```
   pip3 install playwright
   playwright install chromium
   ```
   Baris kedua akan download browser Chromium khusus untuk Playwright
   (beda dari Chrome biasa) — proses ini bisa makan waktu beberapa menit,
   biarkan sampai selesai.

---

## BAGIAN C — Salin file kerja (supaya tidak mulai dari nol)

Teman Anda **tidak perlu** membuat ulang script — cukup salin file-file
ini dari folder `MCU` Anda:

**WAJIB disalin** (script & dokumentasi, aman untuk dibagikan — tidak
berisi data pasien):
```
fase0_buka_pasien.py
fase1_baca.py
fase3a_generate_teks.py
fase3b_tulis_ehr.py
input_dict.py
konverter_queue.py
protocol_engine.py
PETA_FIELD_EHR.md
Protokol_Interpretasi_MCU_Draft.md
CATATAN_ALUR_KERJA.md
```

**JANGAN disalin** (berisi data pasien dari sesi Anda sendiri):
```
queue.json
draft_fase3.json
__pycache__/
```
Kalau file `queue.json`/`draft_fase3.json` tidak ada, tidak masalah —
akan otomatis dibuat ulang saat script pertama kali jalan.

**Cara paling gampang:** kirim ke teman Anda lewat WhatsApp/Google
Drive/AirDrop cuma 10 file yang "WAJIB disalin" di atas (bukan seluruh
folder), lalu di MacBook-nya:

1. Buat folder baru khusus, mis. buka Finder → Documents → klik kanan →
   New Folder → beri nama `MCU`.
2. Pindahkan 10 file yang dikirim tadi ke folder `MCU` itu.

---

## BAGIAN D — Setup Chrome untuk browser automation

Beda dari Windows, di Mac perintahnya:

1. Tutup semua jendela Chrome yang terbuka.
2. Di Terminal, ketik (sesuaikan kalau Chrome ter-install di lokasi lain):
   ```
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-mcu"
   ```
3. Di jendela Chrome yang baru terbuka, **login sendiri** pakai akun EHR
   RSCM milik teman Anda ke `http://ehr.rscm.co.id/ehr/index.php`.
4. Biarkan Chrome ini tetap terbuka selama kerja.

---

## BAGIAN E — Mulai kerja dengan Claude Code

1. Buka Terminal baru (yang ini terpisah dari Terminal yang menjalankan
   Chrome di Bagian D — biarkan Chrome tetap jalan di Terminal lamanya).
2. Masuk ke folder kerja:
   ```
   cd ~/Documents/MCU
   ```
   (sesuaikan path kalau folder disimpan di tempat lain)
3. Jalankan Claude Code:
   ```
   claude
   ```
4. Setelah Claude Code terbuka, langsung minta seperti ini (ketik di
   prompt Claude Code):
   > "Saya mau pakai script MCU yang sudah ada di folder ini untuk
   > mengisi MCU pegawai. Chrome debug sudah saya buka & login di port
   > 9222. Baca dulu CATATAN_ALUR_KERJA.md untuk paham alurnya."
5. Setelah itu, alurnya sama seperti yang sudah dipakai di sesi ini:
   **cukup kasih NRM pasien**, Claude akan jalankan
   `fase0_buka_pasien.py` → `fase1_baca.py` → bersihkan `queue.json` →
   `fase3a_generate_teks.py` (review draft) → `fase3b_tulis_ehr.py
   --tulis --ya` (tulis ke EHR).

---

## Hal penting yang perlu diketahui teman Anda

- **Login EHR pakai akun dia sendiri** — jangan pernah pakai akun/password
  orang lain untuk ini.
- **Field auto-save begitu ditulis** — tidak ada undo di sisi RSCM. Fase
  3b selalu tampilkan preview "ISI SEKARANG vs AKAN DIISI" sebelum
  benar-benar menulis — baca dulu sebelum konfirmasi.
- Beberapa ambang klinis di `input_dict.py`/`protocol_engine.py` sudah
  dikonfirmasi bersama dr. Vidya untuk kasus-kasus yang muncul di sesi
  ini — kalau teman Anda menemukan kasus baru yang aturannya belum ada
  atau terasa salah, sebaiknya didiskusikan dulu sebelum dipakai ke
  pasien sungguhan (sama seperti proses yang dilakukan di sesi awal).
- Field radiologi (578) tidak punya kotak isian terpisah — kesimpulannya
  otomatis masuk ke bagian "Rontgen thorax :" di dalam field Kesimpulan
  gabungan (581). Ini sudah dikonfirmasi lewat pengecekan struktur HTML
  form RSCM, jadi seharusnya sama di semua browser/komputer — tapi kalau
  ternyata beda, kasih tahu Claude untuk dicek ulang strukturnya.

---

*Dibuat berdasarkan setup yang sudah berjalan di Windows (dr. Vidya) —
langkah Bagian D disesuaikan untuk macOS, bagian lain sama persis.*
