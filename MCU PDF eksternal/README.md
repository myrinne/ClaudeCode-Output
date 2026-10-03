# MCU dari PDF Eksternal

Review MCU pegawai RSCM yang hasil pemeriksaannya **bukan** dari RSCM, tapi PDF dari
RS/lab lain (Prodia, Pramita, RS YARSI, RSPI Sulianti Saroso, dst), lalu tulis
8 field Kesimpulan di EHR RSCM.

Pipeline lama (`../MCU automation/`) **tidak diubah**. Folder ini meng-*import*
`protocol_engine.py`, `konverter_queue.py`, `fase0/1/3a/3b` dari sana (lihat
`_jalur.py`), jadi setiap perbaikan protokol di sana otomatis berlaku di sini.

## Alur per pasien

Prasyarat sama dgn pipeline lama: Chrome debug port 9222 sudah terbuka & login EHR
(lihat `../MCU automation/CATATAN_ALUR_KERJA.md` bagian 1).

1. **Ambil PDF** — `python ambil_pdf.py <NRM> <link_drive> [<link_drive_2> ...]`
   Unduh ke `pdf_masuk/<NRM>/`, simpan teks + gambar per halaman.
2. **Baca PDF → `ekstrak/<NRM>.json`** — dilakukan Claude di sesi (bukan API):
   halaman teks dibaca dari `.txt`, halaman scan/EKG dari `.png`. Format di bawah.
3. **Tulis langsung** — `python proses_pdf.py <NRM> --tulis` setiap kali selesai membaca 1 NRM,
   TANPA menunggu konfirmasi per pasien (dikonfirmasi dr. Vidya, 2026-10-03: dia membaca sendiri
   sebelum approve). **Approve Dokter tidak pernah disentuh** — approve manual.
   Opsional: `--tanpa-ehr` (uji offline tanpa Chrome) atau tanpa flag (preview, tidak menulis).

Semua run (kecuali `--tanpa-ehr`) dicatat di `notes_pdf_<tanggal>.md` + `draft/<NRM>.json`.

## Aturan (dikonfirmasi dr. Vidya, 2026-10-03)

| Hal | Aturan |
|---|---|
| Identitas | Nama longgar (gelar/sapaan diabaikan, toleran typo); **tgl lahir wajib sama** (NIP juga kalau ada di PDF). Beda → run berhenti. |
| Cutoff tes "mesin" | SGOT/SGPT, GGT, kreatinin, ureum, asam urat, bilirubin, Hb, leukosit, trombosit, LED, eritrosit, sedimen urin → **rujukan vendor**. |
| Cutoff "pedoman" | GDP 70–99/126, GD2PP 140, HbA1c 5.7/6.5, kolesterol 200/240, TG 150, eGFR 60 → **angka protokol**, rujukan vendor diabaikan. |
| EHR vs PDF | Kalau dua-duanya ada, **EHR menang**. PDF mengisi yang kosong saja. |
| Data belum lengkap | Tetap "Mohon segera lengkapi …" di saran, **tapi kelaikan tetap diberikan**: "Laik kerja dengan catatan … dan melengkapi pemeriksaan X". |
| Tes di luar protokol | LDL/HDL, Vit D, dst tidak masuk ringkasan. Yang bisa mengubah kelaikan (hs-CRP, tumor marker, D-dimer, NAPZA) → catatan di notes kalau abnormal. |
| >1 PDF beda tanggal | Hasil terbaru dipakai, yang lama jadi "riwayat" di tabel. Tes yang cuma ada di PDF lama → dipakai + catatan PERLU_CEK_MANUAL. |
| GDP naik + HbA1c DM | (di protocol_engine.py, berlaku utk kedua pipeline) Satu temuan saja: **"Suspek DM tipe 2"** (baris & saran GDP dibuang, GDP tidak dihitung sbg temuan terpisah utk kelaikan). GDP+GD2PP naik tetap ditangani protokol lama ("Suspek DM 2"). |
| Saran GD2PP | (di protocol_engine.py) Kalau HbA1c sudah diperiksa, saran "Cek GD2PP ... GDP terganggu" dibuang (temuan GDP tetap). |
| Approve | Manual dulu sampai alur ini terbukti andal. Kalau sudah di-approve, field terkunci -> script tidak menulis. |

Batas eGFR protokol = 60 (KDIGO, dikonfirmasi 2026-10-03); kalau vendor tidak mencetak eGFR,
dihitung CKD-EPI 2021 dari kreatinin. Hasil dari PDF lama boleh dipakai kalau tes itu tidak ada
di PDF terbaru (dikonfirmasi 2026-10-03) -- tetap dicatat di notes.

## Pengaman

- Setiap angka yang dibaca dari halaman **teks** dicek ulang otomatis harus benar-benar ada di
  teks halaman itu (`periksa_ekstrak`). Tidak cocok → flag merah, tidak bisa `--tulis`.
- Angka dari halaman **scan** ditandai `⚠️SCAN-cek` di tabel verifikasi — cocokkan dengan PDF.
- Nama tes / satuan yang tidak ada di `kamus_lab.py` → tidak ditebak, dilaporkan PERLU_CEK_MANUAL.
  Tambah aliasnya ke kamus lalu jalankan ulang.
- NIP halaman EHR dicek ulang tepat sebelum menulis.

## Format `ekstrak/<NRM>.json`

```json
{
  "nrm": "385-45-12",
  "sumber": [{"berkas": "berkas1", "vendor": "Prodia", "tanggal": "2026-09-21", "isi": "lab + urin"}],
  "identitas_pdf": {"nama": "…apa adanya di PDF…", "tgl_lahir": "YYYY-MM-DD", "jenis_kelamin": "L|P", "nip": null},
  "tanda_vital": {"td_sistolik": 120, "td_diastolik": 80, "tinggi_badan": 170, "berat_badan": 70,
                  "bmi": 24.2, "lingkar_perut": 85, "nadi": 80},
  "lab": [{"nama": "…nama vendor apa adanya…", "hasil": "14.6", "satuan": "g/dL", "rujukan": "13.2 - 17.3",
           "flag_vendor": "*", "vendor": "Prodia", "tanggal": "YYYY-MM-DD",
           "berkas": "berkas1", "halaman": 1, "dibaca_dari": "teks|gambar"}],
  "urin": [{"nama": "…", "hasil": "0 - 1", "satuan": "/LPB", "rujukan": "<= 5", "…": "sama spt lab"}],
  "radiologi": {"ada": true, "vendor": "…", "tanggal": "…", "deskripsi": "…", "kesimpulan": "…persis PDF…"},
  "ekg": {"ada": true, "kesan": "Normal|Abnormal", "deskripsi": "mis. Sinus rhythm"},
  "lain": ["temuan/surat lain yang perlu dr. Vidya tahu"]
}
```

- `tanda_vital` / `radiologi` / `ekg` → `{}` / `null` kalau tidak ada di PDF.
- Anti-HBs: `hasil` teks + `nilai_angka` kalau ada konsentrasi.
- Tulis nama tes & hasil **persis** seperti di PDF — pemetaan ke nama RSCM urusan `kamus_lab.py`.

## File

| File | Fungsi |
|---|---|
| `ambil_pdf.py` | Unduh dari Drive, pecah per halaman (teks + png) |
| `kamus_lab.py` | Alias nama tes vendor → RSCM, konversi satuan, kategori mesin/pedoman/info |
| `pdf_ke_queue.py` | Ekstrak → format `queue.json`, gabung dgn EHR, cek identitas |
| `generate_pdf.py` | Draft 8 field (fase3a lama + aturan kelaikan data belum lengkap) |
| `proses_pdf.py` | Orkestrasi: EHR, cek ulang ekstrak, tabel verifikasi, notes, tulis (tanpa approve) |
