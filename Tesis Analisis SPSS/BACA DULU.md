# Sintaks SPSS tesis WBGT–TEWL–H₂O₂

SPSS 32 + PROCESS v5.1. Data `SIMULASI_*.xlsx` adalah **data buatan**, bukan data penelitian. Jangan mengutip angkanya di naskah.

## Cara menjalankan
1. Buka `00_JALANKAN.sps` di SPSS → Run → All.
2. Pemuatan PROCESS dan tiga model PROCESS adalah bagian paling lama; tunggu sampai selesai.
3. Simpan keluaran: File → Save As `.spv` (Lampiran keluaran SPSS).

Data asli: salin `6_Ekspor_SPSS` (baris judul + semua baris) → workbook baru → Paste Special › Values → simpan `.xlsx` dari Excel → ganti baris `berkasdata` di `00_JALANKAN.sps`. Sel kosong dan kode tak terpakai sudah ditangani (diuji). Simpan selalu dari Excel; xlsx yang langsung dibuat skrip Python tidak terbaca SPSS.

## Isi dan padanan Bab 4
| Berkas | Isi | Tabel naskah |
|---|---|---|
| 01_siapkan_data | impor, label, cek rentang / kelengkapan / kode ganda | 4.1 (n) |
| 02_deskriptif | atrisi, karakteristik + SMD, normalitas, korelasi | 4.1, 4.3, 4.4, 4.5 |
| 03_asumsi | VIF, residual, linearitas, Cook | 4.6, 4.7 |
| 04_mediasi_process | PROCESS Model 1, 2, 3; Breusch-Pagan (Robust) di Model 3 | 4.6 (mediasi), 4.7 |
| 07_cadangan | tidak otomatis: dummy, HC3, log, tanpa PM2.5, pelembap/wet work | lampiran |
| 05_ringkasan_BCa | a, b, c′, c + IK; a×b percentile, BC, BCa | Tabel 4.6, sub-bab 4.9 |
| 06_sekunder | beda area, interaksi | 4.8, 4.9 |

Tabel 4.2 (zona × shift) tetap dari Excel `3_Matriks_Zona`.

## Cara membaca keluaran
| Angka | Letak |
|---|---|
| Jalur a | PROCESS, `OUTCOME VARIABLE: tewl`, baris wbgt |
| Jalur b, c′ | PROCESS, `OUTCOME VARIABLE: h2o2`, baris tewl dan wbgt |
| Jalur c | `TOTAL EFFECT MODEL`, baris wbgt |
| a×b | `Indirect effect(s) of X on Y`, BootLLCI–BootULCI |
| a×b terstandar penuh | `Completely standardized indirect effect(s)` |
| VIF untuk aturan 3.7.4 | 03, persamaan TEWL (tanpa mediator). VIF di persamaan H₂O₂ lebih tinggi karena memuat TEWL |

Rumus: proporsi termediasi = a×b / c × 100%; change-in-estimate = (B Model 1 − B Model 3) / B Model 3 × 100%.

## Skenario simulasi (68 ikut, 64 dianalisis: 2 hemolisis, 1 TEWL tidak layak, 1 IB ≥600)
| Skenario | Dirancang untuk melatih |
|---|---|
| A_mediasi | jalur dermal bermakna, VIF <5; H2 tidak bermakna tetapi H4 bermakna di Model 3 |
| B_tanpa_mediasi | jalur b = 0, naskah versi "tidak ada mediasi" |
| C_VIF_tinggi | PM2.5 searah WBGT, VIF 5–10 (aturan 3.7.4 butir 2) |

Parameter populasi: a = 0,90; b = 1,35 (A, C) atau 0 (B); c′ = 0,60. Nilai zona, TEWL, H₂O₂ bersifat ilustratif. Benih 20261130.

## Pilihan yang dipakai sintaks (ubah bila diputuskan lain)
- Beban kerja = `bk_kkal` kontinu. Versi dua dummy (teks Bab 3.7.3) ada di 07 (a); **gagal di simulasi** karena hanya 2 subjek Berat (bootstrap singular).
- Merokok = Indeks Brinkman per 100, satu prediktor. Alternatif perokok aktif 1/0: satu baris di 01.
- Bootstrap utama PROCESS = percentile. `bc=1` = bias-corrected tanpa percepatan. **PROCESS tidak menyediakan BCa**; BCa ada di 05.
