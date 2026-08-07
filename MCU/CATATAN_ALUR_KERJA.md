# CATATAN ALUR KERJA — Pengisian MCU Otomatis

Ringkasan cara pakai sistem ini dari nol (buka Chrome) sampai satu pasien
selesai ditulis ke EHR. Ditulis setelah sesi debugging panjang — lihat
bagian "Riwayat perbaikan penting" di bawah kalau ada error yang mirip
dengan yang pernah terjadi sebelumnya.

---

## 1. Persiapan (sekali di awal sesi kerja)

1. Tutup semua Chrome yang sedang terbuka.
2. Buka Command Prompt / PowerShell, jalankan:
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-mcu"
   ```
3. Di jendela Chrome yang baru terbuka itu, **login sendiri** ke
   `http://ehr.rscm.co.id/ehr/index.php`.
4. Biarkan Chrome itu tetap terbuka selama sesi kerja — semua script di
   folder ini menyambung ke situ lewat port 9222, bukan membuka Chrome baru.

Kalau Claude Code lapor "GAGAL menyambung ke Chrome", cek: apakah Chrome
debug-nya masih terbuka? Apakah portnya benar 9222?

---

## 2. Alur kerja per pasien (apa yang perlu Anda ketik)

**Cukup ketik NRM pasien** (format "406-66-04"), tidak perlu apa-apa lagi.
Ini berlaku sama persis baik untuk pasien baru maupun untuk update pasien
yang datanya sudah pernah ditulis sebelumnya (mis. EKG yang tadinya
"Belum dilakukan" sudah Anda isi hasil aslinya) — sistem selalu baca ulang
SEMUA data dari layar dan hitung ulang semuanya, supaya Kesimpulan gabungan
dan kelaikan kerja tetap sinkron dengan temuan terbaru.

Di baliknya, Claude menjalankan 4 langkah ini berurutan:

1. `python fase0_buka_pasien.py <NRM>` — cari pasien by NRM, pilih
   kunjungan MCU Pegawai/Medical Check Up TERBARU, navigasi browser ke
   Formulir MCU-nya. Kalau ragu (kunjungan terbaru ternyata bukan MCU
   lengkap, atau semua kandidat gagal), berhenti dan tampilkan daftar
   kunjungan untuk dicek manual — tidak menebak.
2. `python fase1_baca.py` — baca SEMUA data dari layar (tanda vital, lab,
   radiologi, field kesimpulan yang sudah ada) ke `queue.json`. Murni
   baca, tidak mengubah apa pun di EHR.
3. Bersihkan `queue.json` supaya cuma menyisakan 1 entri pasien terakhir
   (kalau dijalankan berkali-kali, entri lama numpuk).
4. `python fase3a_generate_teks.py` — hitung interpretasi klinis & susun
   draft teks utk 8 field EHR, ditampilkan ke layar untuk direview
   sekilas (flag hijau/kuning/merah).
5. `python fase3b_tulis_ehr.py --tulis --ya` — tulis ke 8 field EHR:
   Ringkasan Jasmani, Ringkasan Lab, Hasil EKG, Hasil Audiometri, Hasil
   Spirometri, Catatan Tambahan/Kelaikan, Kesimpulan gabungan, Saran.
   Field **Approve Dokter TIDAK PERNAH disentuh** oleh script ini.

Field ini **auto-save begitu kehilangan fokus** — tidak ada draft/undo di
sisi RSCM. Karena itu Fase 3b selalu menampilkan dulu perbandingan
"ISI SEKARANG" vs "AKAN DIISI" per field sebelum menulis.

---

## 2b. Mode Batch (banyak NRM sekaligus, ditambahkan setelah sesi ini)

Untuk efisiensi, ada alur alternatif `fase_batch.py` yang memproses BEBERAPA
NRM sekaligus dalam satu sesi, TANPA review per-pasien di tengah jalan —
Anda cukup review satu `notes.md` di akhir. Ini menggantikan langkah 1-5 di
atas untuk kasus batch (alur manual satu-pasien di atas tetap ada untuk
debugging/kasus khusus).

```
python fase_batch.py --ya 406-66-04 123-45-67 ...   # tulis + approve sungguhan
python fase_batch.py 406-66-04 123-45-67 ...        # preview saja, tidak menulis apa pun
```

**Kebijakan approve otomatis (dikonfirmasi Anda):**
- Flag 🔴 merah (data belum lengkap / lab rusak) → 8 field klinis tetap
  ditulis, **Approve Dokter TIDAK disentuh** — tetap perlu approve manual.
- Flag 🟢 hijau DAN 🟡 kuning (termasuk trombositosis) → 8 field ditulis DAN
  **Approve Dokter otomatis di-set "Ya" + tombol Kirim panel diklik**.
  Catatan manual (mis. trombositosis) tetap ditulis lengkap di `notes.md`
  supaya Anda tetap bisa baca setelahnya.

**Approve Dokter (`FNDx0000000641`)** dipastikan lewat inspeksi DOM langsung
(bukan tebakan): radio button Ya/Tidak di panel Kesimpulan yang sama dengan
8 field lain (`frmfinding_PNL_x000000457`), auto-save lewat
`submit_panelfinding` begitu diklik — sama seperti field lain. Panel itu
juga punya satu tombol "Kirim" umum yang diklik sesudahnya. Tab
"[ dr. X ] Dokter Approval MCU" yang sempat terlihat di daftar tab BUKAN
tab approval terpisah — itu cuma label peran staf di bawah "Tenaga Medis".

**Satu file notes per hari** (dikonfirmasi Anda, 2026-07-25, supaya tidak
menumpuk panjang ke bawah): nama file otomatis `notes_YYYY-MM-DD.md`
mengikuti tanggal batch dijalankan (mis. `notes_2026-07-25.md`). Di-append
(bukan overwrite) tiap kali batch dijalankan PADA HARI YANG SAMA, dengan
header `# Batch <tanggal jam>` per run, lalu per pasien: temuan
(kesimpulan), saran, kelaikan/catatan tambahan, dan status akhir (✅
approved+terkirim / 🔴 ditahan data belum lengkap / ⚠️ gagal). Kegagalan 1
pasien (NRM tidak ketemu, kunjungan ambigu, NIP tidak cocok, field
terkunci, dll) TIDAK menghentikan batch — dicatat di notes file hari itu,
lanjut ke NRM berikutnya.

Diuji end-to-end pada 2026-07-24 (NRM 437-71-89, Fadilatul Qoyyimah,
flag hijau) — 8 field + approve+kirim berhasil terverifikasi.

---

## 3. Pengaman yang sudah dibangun

- **Verifikasi NIP**: sebelum menulis, dicocokkan NIP di draft vs NIP di
  halaman EHR yang sedang terbuka. Kalau tidak cocok, batal — tidak pernah
  menulis ke pasien yang salah.
- **Data belum lengkap (TD/BMI/Lingkar Perut kosong semua, atau EKG belum
  dilakukan usia ≥35, atau Rontgen belum dilakukan)** → flag 🔴 merah,
  teks otomatis jujur bilang "belum dapat diberikan status kelaikan kerja
  sampai dilakukan pemeriksaan dengan lengkap" + saran "mohon segera
  lengkapi X". Ini **aman ditulis** — teksnya sudah benar mencerminkan
  keadaan, bukan tebakan.
- **Data lab rusak/menggumpal** (section Laboratorium belum ter-render
  penuh saat Fase 1) → flag 🔴 merah, **hard block**, tidak boleh ditulis
  sampai Fase 1 diulang dengan benar.
- **Field yang sudah di-approve dokter** → kadang EHR mengunci field-nya
  sementara (disabled), Fase 3b/fase_batch akan gagal (Playwright: "element
  is not enabled") bukan diam-diam menembus kuncian itu. **Diselidiki
  2026-07-24** (kasus Fadilatul Qoyyimah, NRM 437-71-89): kuncian ini
  ternyata SEMENTARA, bukan permanen — kemungkinan cuma UI lock selagi AJAX
  "Kirim" submit sebelumnya masih diproses. **Kalau menemui error ini pada
  pasien yang sudah di-approve**: jalankan ulang `fase0_buka_pasien.py`
  <NRM> dari awal (navigasi penuh, BUKAN `page.reload()` mentah — itu
  merusak proses render tab Kesimpulan) lalu coba tulis ulang sekali lagi
  sebelum menyimpulkan perlu edit manual. Ini berhasil memperbaiki record
  Fadilatul di percobaan kedua.
- **Trombositosis** selalu flag 🟡 kuning — perlu Anda baca catatan klinis
  sebelum approve (sesuai instruksi Anda dari awal).

---

## 4. Deskripsi file

| File | Fungsi |
|---|---|
| `fase0_buka_pasien.py` | Cari pasien by NRM, navigasi ke Formulir MCU |
| `fase1_baca.py` | Baca semua data dari layar EHR (read-only) ke `queue.json` |
| `input_dict.py` | Ubah angka lab mentah → status klinis (baca rujukan EHR langsung, bukan angka hardcode) |
| `konverter_queue.py` | Jembatan `queue.json` → `protocol_engine.py` |
| `protocol_engine.py` | Mesin interpretasi klinis murni (kalkulator teks, tidak menyentuh browser) |
| `fase3a_generate_teks.py` | Susun draft teks 8 field EHR dari hasil `protocol_engine.py` |
| `fase3b_tulis_ehr.py` | Tulis draft ke EHR (mode `--tulis --ya` = tulis sungguhan; tanpa argumen = preview saja) |
| `Protokol_Interpretasi_MCU_Draft.md` | Dasar aturan klinis (kategori, ambang, logika kelaikan) — dikonfirmasi Anda |
| `PETA_FIELD_EHR.md` | Pemetaan ID field HTML form RSCM |

---

## 5. Aturan klinis penting yang sudah dikonfirmasi (ringkasan cepat)

- **Kesimpulan (581)** = gabungan semua bagian (Jasmani + Lab/Urinalisa +
  EKG + Rontgen thorax), dipisah baris kosong.
- **Catatan Tambahan (964)** = status laik/tidak saja. Kalau "dengan
  catatan": disambung alasan — "memerlukan konsultasi dengan dokter..."
  KALAU ada saran yang sebut "dokter"; kalau tidak ada yang sebut dokter
  sama sekali → "melakukan tatalaksana terhadap hasil MCU".
- **Vaksin Hepatitis B** direkomendasikan → catatan tambahan otomatis
  tambah "+ diberikan vaksinasi Hepatitis B" di akhir.
- **Anti-HBs tidak diperiksa sendirian** (tanpa temuan lain) → TIDAK lagi
  memaksa "dengan catatan" (direvisi setelah kasus Reza Zada Maulana).
- **Saran ke "Poli Pegawai/Klinik Pratama/Dokter Umum"** — semua teks
  destinasi ini distandarkan sama persis, supaya kalau >1 temuan
  mengarah ke situ, otomatis digabung satu baris dipisah koma.
- **Pasien yang jabatannya sendiri dokter** ("dr." di nama) → rujukan ke
  Dokter Umum Poli Pratama diganti "Memerlukan tatalaksana terhadap X"
  (tidak masuk akal menyuruh dokter konsultasi ke dokter umum untuk
  temuannya sendiri).
- **SGOT/SGPT**: naik >5 poin dari rujukan = "Peningkatan enzim fungsi
  hati" (saran: Konsultasi Poli Pegawai). Naik ≥2x lipat rujukan =
  "Suspek gangguan fungsi hati" (saran: Sp.PD-KGEH).
- **Leukositosis**: kenaikan <1000 sel (< 1.0 di satuan 10^3/uL) diabaikan
  (variasi wajar). Kalau lebih, saran "Cek ulang dan bila perlu
  konsultasi ke Dokter Umum Poli Pegawai".
- **Kolesterol Total tinggi**: kalau HDL & LDL JUGA diperiksa →
  "Dislipidemia". Kalau cuma Kolesterol Total sendirian → "Hiperkolesterolemia".
- **Urinalisa**: albumin+darah bersamaan & keduanya cuma "Trace" → saran
  ringan "Cek ulang urinalisa, bila perlu konsultasi ke Dokter Umum
  Klinik Pratama" (bukan "Konsultasi dokter" biasa).

---

## 6. Kasus khusus / catatan tambahan

- **ID pegawai non-18-digit** (mis. "NPS147533", "ORP0024" untuk pegawai
  kategori tertentu seperti Pekerja Radiasi) — sudah ditangani, regex
  identitas menerima format huruf+angka, bukan cuma NIP 18 digit.
- **Kunjungan "MCU Pegawai/Medical Check Up" ganda** (mis. kunjungan
  vaksin terdaftar di kategori yang sama) — Fase 0 otomatis coba kandidat
  berikutnya kalau yang terbaru gagal render form klinis penuh.
- **Render form klinis bisa lambat** (pernah sampai >8 detik) — Fase 0
  menunggu sampai 20 detik sebelum menyerah, supaya tidak salah pilih
  kunjungan yang jauh lebih lama sebagai fallback.
- **Radiologi kosong** (laporan PACS belum masuk ke EHR) — otomatis
  terdeteksi, tidak disalahartikan sebagai "ada temuan". Kelaikan jadi
  merah "data belum lengkap", bukan menebak isi laporan.

---

*Catatan ini dibuat oleh Claude berdasarkan sesi kerja bersama dr. Vidya,
mencakup seluruh proses debug dari pembacaan data mentah sampai penulisan
ke EHR untuk banyak pasien.*
