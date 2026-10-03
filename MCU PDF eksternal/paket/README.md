# Automation External PDF — MCU dari PDF RS/Lab Luar

Untuk mengisi Kesimpulan MCU pegawai di EHR RSCM ketika hasil pemeriksaannya **bukan dari RSCM**,
melainkan PDF dari RS/lab lain (Prodia, Pramita, RS YARSI, RSPI Sulianti Saroso, dll) yang dibagikan
lewat link Google Drive.

Paket ini **mandiri**: tidak mengubah dan tidak bergantung pada folder automation MCU lama Anda.
Protokol interpretasinya (folder `engine/`) adalah salinan protokol dr. Vidya per 3 Oktober 2026.

## ⚠️ Aturan pemakaian

1. **Satu NRM per proses.** Script hanya menerima satu NRM sekali jalan.
2. **NRM berikutnya baru bisa ditulis setelah NRM sebelumnya di-approve dokter.** Script mengecek
   langsung ke EHR. Kalau belum di-approve → ditolak.
3. **Script tidak pernah menyentuh Approve Dokter.** Baca hasilnya di EHR, cocokkan dengan PDF,
   baru approve sendiri.

## Persiapan (sekali)

1. Install **Python 3.11+** dan **Claude Code**.
2. Di folder ini jalankan:
   ```
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Setiap mulai kerja, tutup semua Chrome, lalu buka Chrome mode debug:
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-mcu"
   ```
   Login sendiri ke `http://ehr.rscm.co.id/ehr/index.php` di jendela Chrome itu dan biarkan terbuka.

## Cara pakai (per pasien)

Buka Claude Code di folder ini, lalu ketik **satu** NRM + link Drive-nya, misalnya:

```
proses NNN-NN-NN https://drive.google.com/file/d/xxxx/view
```

Claude akan:
1. `python ambil_pdf.py <NRM> <link>` — unduh PDF, pecah per halaman (teks + gambar).
2. Membaca semua halaman (termasuk scan) dan mengisi `ekstrak/<NRM>.json`.
3. `python proses_pdf.py <NRM> --tulis` — buka pasien di EHR, cek identitas, gabung data, tulis
   field Kesimpulan.
4. Melaporkan ringkasan + hal yang perlu Anda cek.

Lalu **Anda**: buka pasien di EHR, baca semua field, cocokkan dengan PDF (terutama nilai yang
ditandai ⚠️SCAN-cek), **approve manual**. Baru kirim NRM berikutnya.

Menjalankan tanpa Claude juga bisa: langkah 2 berarti Anda mengisi `ekstrak/<NRM>.json` sendiri
sesuai `contoh_ekstrak.json`.

Mode lain `proses_pdf.py`:
- tanpa flag → preview saja, tidak menulis apa pun
- `--tanpa-ehr` → uji offline tanpa Chrome

## Aturan interpretasi

| Hal | Aturan |
|---|---|
| Identitas | Nama boleh beda gelar/sapaan; **tanggal lahir wajib sama** (juga NIP kalau ada di PDF). Beda → berhenti. |
| Rujukan tes tergantung alat (SGOT/SGPT, GGT, kreatinin, ureum, asam urat, bilirubin, Hb, leukosit, trombosit, LED, eritrosit, sedimen urin) | Pakai **rujukan lab pengirim** (tercetak di PDF) |
| Ambang diagnostik (GDP 100/126, GD2PP 140, HbA1c 5.7/6.5, kolesterol 200/240, TG 150, eGFR 60) | Pakai **angka protokol**, rujukan lab diabaikan |
| Data ada di EHR dan PDF | **EHR yang dipakai** |
| Data belum lengkap (tanda vital, EKG usia ≥35, rontgen) | Saran "Mohon segera lengkapi …", kelaikan **tetap diberikan**: "Laik kerja dengan catatan … dan melengkapi pemeriksaan X" |
| Tes di luar protokol (LDL/HDL, Vit D, dll) | Tidak masuk ringkasan; yang bisa memengaruhi kelaikan (hs-CRP, tumor marker, D-dimer, NAPZA) dicatat kalau abnormal |
| Beberapa PDF beda tanggal | Hasil terbaru dipakai; tes yang cuma ada di PDF lama tetap dipakai + dicatat |
| GDP naik + HbA1c DM | Satu temuan: "Suspek DM tipe 2" |

## Pengaman

- Angka dari halaman PDF berteks dicek otomatis: harus benar-benar ada di halaman itu. Kalau tidak cocok → tidak ditulis.
- Nama tes/satuan yang tidak dikenal `kamus_lab.py` → tidak ditebak, dilaporkan PERLU_CEK_MANUAL.
- NIP halaman EHR dicek ulang tepat sebelum menulis; record yang sudah di-approve (terkunci) tidak disentuh.
- Field "Ringkasan Laboratorium" biasanya tidak bisa diisi untuk pasien tanpa order lab RSCM (EHR tidak menyediakan kotak isian) — hasil lab tetap tertulis di field **Kesimpulan**.

Semua proses dicatat di `notes_pdf_<tanggal>.md`. Folder `pdf_masuk/`, `ekstrak/`, `draft/` dan file
notes berisi **data pasien** — jangan dibagikan atau diunggah ke mana pun.
