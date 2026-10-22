# Protokol: Dikte → isi otomatis SIM DoctorTool (Pemkes Maba)

Status: **v0.2 (2026-10-22)**. Pertanyaan v0.1 sudah dijawab dokter (bagian 9). Belum dibangun; berikutnya tahap 1.

Tujuan: dokter cukup mengetik nama peserta di aplikasi Dikte MCU. Setelah itu aplikasi membuka pasien di
`sim.doctortool.id`, merekam anamnesis, lalu mengisi Subjektif, Objektif, Asesmen, dan Perencanaan.
**Tombol Simpan tetap ditekan dokter sendiri.** Aplikasi berhenti di halaman pasien, tidak pindah halaman,
dan mengingatkan dokter bila Simpan belum ditekan.

---

## 1. Arsitektur

| Komponen | Tugas | Teknologi |
|---|---|---|
| Aplikasi Dikte MCU (yang sudah ada) | Kotak nama, rekam F9, Whisper lokal, Claude | Tkinter + faster-whisper + `claude -p` |
| **Modul baru `isi_sim.py`** | Membuka pasien dan mengisi form di website | Playwright yang terhubung ke Chrome lewat CDP, sama dengan pipeline MCU RSCM |
| Chrome "debug" | Jendela SIM tempat dokter login sendiri | `chrome.exe --remote-debugging-port=9223 --user-data-dir=C:\chrome-sim` |

- Pembagian kerja: Claude hanya mengubah transkrip menjadi **data terstruktur (JSON)**. Semua klik dan isian dikerjakan
  skrip Python yang tetap, tidak dikerjakan AI, sehingga hasilnya cepat dan bisa diprediksi.
- Login dan captcha dikerjakan dokter sendiri. Skrip tidak pernah menyimpan password.
- Port 9223 dipakai supaya tidak bentrok dengan Chrome EHR RSCM yang memakai 9222.

## 2. Alur per peserta

```
[Dokter] ketik nama di aplikasi → Enter
  │
  ├─(A) REKAM mulai otomatis (sama seperti F9)
  │
  └─(B) BUKA PASIEN (paralel, ±3–5 dtk)
        1. Halaman Praktik → tab "Hari ini" → cari baris yang Namanya MENGANDUNG teks ketikan
           (boleh sebagian, tidak peka huruf besar/kecil; mis. "juniarto")
           - 0 hasil  → status merah "Nama tidak ditemukan"; rekaman tetap jalan
           - >1 hasil → aplikasi menampilkan pilihan (nama, umur/JK, No. antrean); dokter memilih
        2. Klik Aksi "Periksa" (ikon ke-2)
        3. Verifikasi header "Pasien Aktif: <NAMA>" = nama yang dipilih   ← KUNCI PENGAMAN
        4. Tab Pemeriksaan Awal: cek Tujuan = "PEMERIKSAAN KESEHATAN" dan
           Keluhan Utama (ICPC) = "-30 - Pemeriksaan Kesehatan"
           - Bila beda/kosong → PERINGATAN saja (tidak diubah otomatis)
        5. Klik tab "Pemkes Maba" → sub-tab Subjektif
  │
[Dokter] anamnesis + PF, ucapkan temuan abnormal → F9 (stop)
  │
  ├─ Whisper → Claude → JSON (±20–30 dtk, seperti sekarang)
  │
  └─(C) ISI FORM — hanya bila header masih pasien yang sama
        Subjektif → Objektif → Asesmen → Perencanaan (bagian 3)
        Satu tombol Simpan menyimpan keempat sub-tab, jadi pindah sub-tab sebelum Simpan aman.
        Lalu kembali ke sub-tab Subjektif agar dokter bisa membaca dari atas
  │
[Aplikasi] status kuning "Terisi: <NAMA>. Periksa lalu klik SIMPAN"
[Dokter]   cek → klik Simpan
[Aplikasi] mendeteksi Simpan berhasil → status hijau
```

## 3. Isian per tab

### 3a. Subjektif (kotak ke-2, ke-3, ke-4)
Kotak pertama ("Pasien 31 th, TB ... datang dg keluhan ...") **tidak disentuh** karena terisi otomatis oleh sistem.

| Kotak | Isi (contoh) |
|---|---|
| Subjektif (ke-2) | `Keluhan saat ini : Tidak ada keluhan`<br>`Riwayat Penyakit Sekarang : -` |
| Riwayat Penyakit Dahulu dan Pengobatan | 7 baris, urutan tetap: `Riwayat Penyakit Dahulu` (DM, hipertensi, jantung, asma disangkal) / Pengobatan / Rawat inap di RS / Operasi / Penggunaan kacamata / Penyakit Keluarga / **Alergi (paling bawah)** |
| Riwayat Personal Sosial dan Lingkungan | Riwayat Olahraga / Riwayat Merokok/Alkohol / Program studi. Isi bawaan sistem (mis. "Prodi ... dan Riwayat Personal Sosial dan Lingkungan") **ikut diganti** |

- Isi kotak **diganti seluruhnya** dengan teks hasil dikte.
- Baris yang tidak ditanyakan dibiarkan kosong setelah titik dua, sama dengan aturan sekarang.
- Panel kanan (Daftar Alergi, Riwayat Penyakit Keluarga, APGAR, SCREEM) **tidak diisi** pada versi 1.

### 3b. Objektif
- Centang **Kepala, Leher, Thorax, Abdomen, Ekstremitas**.
- `dbn` muncul otomatis saat dicentang. Skrip hanya mengganti kotak regio yang punya temuan abnormal
  (mis. Ekstremitas: `varices ekstremitas kanan grade 1`).
- Pemetaan temuan ke regio dikerjakan Claude: mata/telinga/gigi/tonsil masuk Kepala; tiroid/KGB masuk Leher; dst.
- Genitalia, Lain-lain, dan Catatan Pemeriksaan Awal tidak disentuh.

### 3c. Asesmen
| Field | Nilai |
|---|---|
| Kasus | Baru |
| Masalah | Umum |
| Prognosis | Bonam (Baik) |
| Diagnosis Kerja (ICD10) | ketik `Z02.0` lalu pilih "Z02.0 - Examination for admission to educational institution" |
| Diagnosis Sekunder (ICD10) | (1) temuan dari dikte (kode saran Claude) + (2) **status gizi dari IMT** (lihat di bawah). Tiap kode: ketik kode lalu pilih baris yang **kodenya persis sama**; bila tidak ada yang sama → dilewati dan dilaporkan |
| ICPC-2, Banding, Status Fungsional, Aspek Personal | tidak diisi |

**Status gizi (IMT)** dihitung skrip, bukan Claude. Angka diambil dari teks bawaan kotak Subjektif pertama ("... IMT 22.76 ...");
bila tidak ada, dihitung dari TB/BB di Pemeriksaan Awal. Batas WHO Asia-Pacific, sama dengan pipeline MCU RSCM:

| IMT | Diagnosis sekunder |
|---|---|
| 23,0–24,9 | E66.3 Overweight |
| ≥ 25,0 | E66.9 Obesity, unspecified |
| < 23,0 | (tidak ditambah) |

Catatan: E66.3 ada di ICD-10-CM, tetapi belum tentu ada di daftar ICD-10 WHO yang dipakai SIM. Dicek saat tahap 1;
bila tidak ada, aplikasi melapor "overweight: kode tidak tersedia, isi manual".

### 3d. Perencanaan
- Centang **Darah EDTA, Darah tanpa anti koagulan, Urine**. Tanggal terisi otomatis hari ini, seperti di screenshot.
- Checkbox lain (Rontgen Paru, EKG, dll.) **tidak diubah**.

## 4. Pengaman

1. **Cocokkan pasien dua kali**: setelah klik Periksa, dan tepat sebelum mengisi. Bila nama di header berbeda,
   tidak ada yang diisi dan hasil hanya masuk clipboard dan .md, seperti sekarang.
2. Tidak pernah menekan **Simpan**, Hapus/Batal (ikon merah), Surat, Resep, atau tombol lain di luar daftar di atas.
3. Tidak pindah halaman setelah selesai mengisi.
4. Bila dokter mengetik nama peserta berikutnya padahal peserta sebelumnya belum disimpan:
   - **Rekaman peserta baru langsung mulai**, sehingga tidak ada waktu yang hilang.
   - Halaman **tidak dipindah**, dan muncul peringatan "<NAMA LAMA> belum disimpan".
   - Pasien baru dibuka setelah dokter menekan Simpan, atau setelah dokter menekan "Lanjut tanpa simpan".
5. Setiap langkah dicatat di `hasil/<tanggal>.md`, misalnya "Subjektif ✓, Objektif ✓, ICD H52.1 ✓, Z02.0 ✓".
   Jadi bila ada yang gagal, jelas bagian mana yang harus diisi manual.
6. Semua langkah yang gagal tetap menyisakan hasil dikte di clipboard dan .md. Aplikasi tidak pernah lebih buruk dari sekarang.
7. Data pasien tetap lokal. Yang dikirim ke Claude hanya transkrip, sama seperti sekarang.

## 5. Format JSON dari Claude (pengganti output teks sekarang)

```json
{
  "subjektif": "Keluhan saat ini : Tidak ada keluhan\nRiwayat Penyakit Sekarang : -",
  "rpd_pengobatan": "Riwayat Penyakit Dahulu : (DM, hipertensi, jantung, asma disangkal)\n...\nRiwayat Alergi : tidak ada",
  "psl": "Riwayat Olahraga : ...\nRiwayat Merokok/Alkohol : ...\nProgram studi : ...",
  "pf": {"kepala": "", "leher": "", "thorax": "", "abdomen": "", "ekstremitas": "varices ekstremitas kanan grade 1"},
  "icd_sekunder": [{"kode": "H52.1", "nama": "Myopia"}],
  "perlu_dicek": ["..."]
}
```
Isian `pf` yang kosong ditulis `dbn` oleh skrip.

## 6. Tahap pembangunan

| Tahap | Isi | Butuh dokter? |
|---|---|---|
| 0 | Protokol ini disetujui dan pertanyaan bagian 9 dijawab | Ya |
| 1 | **Inspeksi DOM baca-saja**: dokter login di Chrome debug, membuka 1 pasien; skrip hanya membaca struktur form (selector), tanpa mengetik atau mengklik isian | Ya, ±10 menit |
| 2 | Buat `isi_sim.py`. **Tidak ada pasien dummy**, jadi uji pertama pada peserta sungguhan sambil diawasi: skrip mengisi, dokter memeriksa setiap sub-tab sebelum Simpan. Bila isian salah: perbaiki manual, atau muat ulang halaman (isian yang belum disimpan hilang) lalu isi manual | Ya |
| 3 | Integrasi ke aplikasi Dikte: kotak nama → buka pasien → rekam → isi | Tidak |
| 4 | Uji nyata 2–3 peserta pertama sambil diawasi; mode cadangan = clipboard seperti sekarang | Ya |

## 7. Estimasi waktu per peserta

| Langkah | Sekarang | Dengan protokol |
|---|---|---|
| Cari nama + klik Periksa + buka Pemkes Maba | manual ±20–30 dtk | otomatis, berjalan selama anamnesis |
| Tempel anamnesis 3 kotak | manual (Ctrl+V + rapikan) | otomatis |
| Centang PF + tulis temuan | manual | otomatis |
| Asesmen + cari ICD | manual ±30–60 dtk | otomatis (dokter hanya mengecek) |
| Centang 3 perencanaan | manual | otomatis |
| Cek + Simpan | manual | manual |

## 8. Risiko yang diketahui

- Website bisa berubah tampilan, sehingga selector tidak lagi cocok. Akibatnya langkah itu gagal dan dilaporkan, tetapi tidak salah isi.
- Dropdown ICD memakai pencarian ke server. Bila lambat, skrip menunggu sampai 10 dtk, lalu melewati dan melaporkan.
- Chrome harus dibuka lewat pintasan khusus (port debug). Bila dokter membuka SIM di Chrome biasa, otomatisasi tidak bisa jalan.
- Penanda "Peringatan: Pasien belum dilakukan penilaian kesehatan" berasal dari tab Penilaian Kesehatan dan **di luar** protokol ini.

## 9. Pertanyaan untuk dokter (perlu dijawab sebelum tahap 1)

Dijawab dokter 2026-10-22:

| # | Pertanyaan | Jawaban |
|---|---|---|
| 1 | Urutan kotak RPD | RPD di atas, Alergi paling bawah; label "Riwayat Penyakit Dahulu" |
| 2 | Isi bawaan kotak PSL | Diganti sesuai input |
| 3 | `dbn` di Objektif | Muncul otomatis saat dicentang |
| 4 | Tombol Simpan | Satu Simpan untuk Subjektif s/d Perencanaan |
| 5 | Pasien dummy | Tidak ada |
| 6 | Nama sebagian | Boleh |
| 7 | (tambahan dokter) | Diagnosis sekunder juga memperhatikan obesitas/overweight |
