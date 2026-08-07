# PETA FIELD EHR RSCM — Formulir Medical Check Up

Hasil pemetaan dari HTML asli. Simpan file ini — kalau nanti ada perubahan
sistem, kita bandingkan dengan ini untuk tahu apa yang berubah.

## Format ID
Semua field pakai format `FNDx##########` (Finding ID).
Label ditampilkan di `<div id="com_[ID]_h" class="concept-title">`.

## ⚠️ Catatan penting: dua textarea per field

Beberapa field punya **DUA textarea dengan ID yang sama**:
1. Textarea pertama — `readonly` — ini **kolom 1** (contoh untuk dicopas)
2. Textarea kedua — bisa diedit — ini **kolom 2** (tempat Anda isi)

Field yang punya struktur ini: `RINGKASAN PEMERIKSAAN JASMANI`, `KESIMPULAN`, `SARAN`.

Artinya saat Fase 3 nanti, selector harus menargetkan textarea **kedua** —
`page.query_selector_all('#FNDx0000000581')[1]`, bukan `[0]`.
Kalau salah, kita akan menimpa kolom contoh, bukan mengisi kolom jawaban.

---

## TANDA VITAL

| Field | ID |
|---|---|
| Tekanan Darah Sistolik | FNDx0000000929 |
| Tekanan Darah Diastolik | FNDx0000000930 |
| Kesimpulan Tekanan Darah | FNDx0000000965 |
| Nadi | FNDx0000000448 |
| Suhu | FNDx0000000449 |
| Pernafasan | FNDx0000000450 |
| Tinggi Badan | FNDx0000000117 |
| Berat Badan | FNDx0000000388 |
| BMI | FNDx0000000451 |
| Kesimpulan BMI | FNDx0000000966 |
| Lingkar Perut | FNDx0000000687 |
| Kesimpulan Lingkar Perut | FNDx0000000967 |

## FIELD TARGET PENGISIAN (yang akan diisi di Fase 3)

| Field | ID | Dua textarea? |
|---|---|---|
| RINGKASAN ANAMNESIS, SRQ | FNDx0000000873 | — |
| RINGKASAN PEMERIKSAAN JASMANI | FNDx0000000576 | ✅ Ya |
| RINGKASAN PEMERIKSAAN LABORATORIUM | FNDx0000000577 | Tidak |
| RINGKASAN PEMERIKSAAN RADIOLOGI | FNDx0000000578 | — |
| HASIL PEMERIKSAAN EKG | FNDx0000000580 | — |
| HASIL PEMERIKSAAN AUDIOMETRI | FNDx0000000874 | — |
| HASIL PEMERIKSAAN SPIROMETRI | FNDx0000000875 | — |
| CATATAN TAMBAHAN KATEGORI KESEHATAN/KELAIKAN KERJA | FNDx0000000964 | Tidak |
| KESIMPULAN | FNDx0000000581 | ✅ Ya |
| SARAN | FNDx0000000926 | ✅ Ya |
| **Approve Dokter** | **FNDx0000000641** | **JANGAN DISENTUH SCRIPT** |

## Mekanisme submit

Setiap field punya `onchange="submit_panelfinding(order_id, form_id, this, event)"`.

Artinya: **setiap kali isi field berubah dan kehilangan fokus, data langsung
terkirim ke server.** Tidak menunggu tombol Kirim.

Ini konsekuensinya penting untuk Fase 3: mengisi field = langsung tersimpan.
Tidak ada "draft" yang bisa dibatalkan. Karena itu Fase 3 harus diuji sangat
hati-hati, idealnya pada satu pasien uji dulu.

## Order ID

Terlihat di HTML sebagai parameter pertama `submit_panelfinding`:
contoh `00230003532836`. Ini berbeda tiap kunjungan pasien.

## Field lain (pemeriksaan fisik detail)

Ada ~95 field berlabel total, termasuk pemeriksaan kulit, kepala, mata,
telinga, mulut, leher, paru, jantung, abdomen, payudara, genitourinaria,
punggung, refleks, dan keseimbangan. Daftar lengkap ada di `fase1_baca.py`
bila sewaktu-waktu diperlukan.
