# MCU Analisa

Analisa hasil MCU per perusahaan untuk HR / manajer (hat **MCU Data Analyst**, aturan lengkap di vault `Identity/hats/mcu-data-analyst.md`).

Prinsip: semua angka adalah rumus Excel, file vendor tidak pernah diubah, dan ada hitungan ulang terpisah yang harus menunjukkan beda = 0.

> Repo ini PUBLIC. Folder ini hanya berisi skrip. Excel pekerja dan hasil analisa tetap di OneDrive (`Documents\Project\<bulan>`).

## Protokol untuk setiap perusahaan baru

Patokan: PT. PPS dan PT. WKP (MCU Nov 2026). Setiap analisa MCU perusahaan dijalankan persis lewat skrip di folder ini, tidak dibuat manual.

1. **Langkah 1** `mcu_reader.py --cek` → kirim MAP yang masih CEK/TIDAK ADA untuk dikonfirmasi (terutama Departemen vs Bagian, mana kolom grup).
2. **Tanya: perlu pembersihan data?** Kalau tidak, nilai dan cutoff vendor dipakai apa adanya.
3. **Langkah 2** `mcu_summary.py --grup ... --cek` → `Jumlah BEDA` harus 0. Potongan Kesimpulan yang tidak cocok: saya tafsirkan dulu dan usulkan pemetaan, bukan hanya didaftar.
4. **Langkah 3** `mcu_ppt.py --template "...\Untitled design.pptx"` (atau `Untitled design (1).pptx`) `--aset "...\Aset edukasi"` → 0 masalah, lalu render dan periksa visual setiap slide.
5. **Langkah 4** `mcu_excel_ringkas.py` lalu `--cek-excel` (Excel tersembunyi) sebelum dikirim.

Hasil wajib (3 file): `Analisa\<nama> - Analisa.xlsx`, `<file vendor> - dengan Ringkasan.xlsx`, `Analisa\<nama> - Laporan MCU.pptx`.

Aturan tetap:
- Cutoff: milik perusahaan dulu; protokol interpretasi hanya bila perusahaan tidak punya; tanpa keduanya default NCEP/ADA/WHO/JNC 7. Interpretasi vendor (Kesimpulan, kelaikan, risiko, Saran) dipakai apa adanya; cutoff hanya untuk parameter yang tidak diinterpretasi vendor (mis. TG/HDL).
- Vendor dengan nama header lain: tambah ke `alias` di `variabel_standar.json`, bukan ubah kode.
- Tampilan deck sudah mengikuti editan tangan pada deck PPS (PR #88): judul "Ringkasan", "TOP 10 PENYAKIT DAN TEMUAN", tanpa baris profil perusahaan, slide kebiasaan label/angka, subjudul kombinasi, ukuran kotak rekomendasi, gambar HRA dari folder aset (`hra_gambar`), slide Overview Program Wellness.
- Label grup memakai nama kolom vendor apa adanya ("Departemen" walaupun isinya jabatan). Bila vendor menulis "Status Akhir" (Baik/Sedang/Kurang), slide dan Ringkasan memakai judul **Status Akhir**, bukan kelaikan/Fit-Unfit. Kolom "Dugaan PAK" selalu dapat slide sendiri (PT. SKP, 2026-11-10).
- Pembersihan kecil (salah ketik grup, tanggal yang diubah Excel) lewat `--bersih VAR:ASLI=BERSIH#alasan` di Langkah 2; tercatat di sheet `DICT_BERSIH` dan ikut dipakai Ringkasan. "-" dibiarkan apa adanya.
- Template: `Untitled design.pptx` (teal) atau `Untitled design (1).pptx` (biru tua-oranye); `mcu_ppt.py` memilih layout otomatis dari template yang diberikan (`mcu_ppt_navy.py` untuk yang biru tua). Isi dan pengecekan sama.
- Teks yang dibaca HRD/vendor (PPT dan sheet Ringkasan) tidak memuat "(interpretasi/keputusan/kolom vendor …)" atau catatan DICT_CUTOFF (`untuk_pembaca()` di `mcu_ppt.py`); file Analisa internal tetap lengkap. Judul grafik: "Jumlah pekerja dengan temuan kelainan gigi / kelainan tajam penglihatan". Kategori bernilai 0 tidak tampil di grafik PPT maupun Excel (Ringkasan: daftar pendamping berumus di kolom GR:GS). Vidya 2026-11-10.
- Selalu cek tanggal campuran: vendor kadang menyimpan sebagian baris sebagai tanggal Excel yang tertukar hari-bulan (SKP: 29 baris 10-07/10-08 = 7/8 Okt).
- Bila deck yang sudah dikirim diedit tangan: buat ulang deck di folder sementara, bandingkan dengan versi editan, masukkan perbedaannya ke `mcu_ppt.py`/`ppt_konten.json` sebagai default. File editan tidak pernah ditimpa; hanya disisipi slide bila diminta.
- Aturan lengkap hat: vault `Identity/hats/mcu-data-analyst.md`; alasan dua Excel: vault `Projects/mcu-analisa-perusahaan.md`.

## Langkah 1: baca kolom + pemetaan (`mcu_reader.py`)

```powershell
cd "MCU Analisa"
uv run --with openpyxl python mcu_reader.py "C:\...\Project\Nov 2026\PT. WKP .xlsx" --cek
```

Hasilnya `Analisa\<nama file> - Analisa.xlsx` di sebelah file vendor:

| Sheet | Isi |
|---|---|
| `MAP` | Variabel standar → kolom vendor. **OK** = nama header cocok persis, **CEK** = mohon dicek, **TIDAK ADA** = vendor tidak punya kolom itu |
| `GRUP` | Kandidat kolom divisi/bagian dan jumlah pekerja per nilai. Kolom di `grup_disamakan` (Bagian, Jabatan) dihitung dengan huruf besar/kecil dan spasi disamakan, dan ejaan aslinya ditampilkan; kolom lain dihitung persis. Tulis pilihan di sel B3 |
| `KOLOM_VENDOR` | Semua kolom vendor dan dipetakan ke mana; yang abu-abu belum dipakai |
| `SHEET_LAIN` | Sheet lain di file vendor (UNFIT, EKG, dll.) |
| `RAW` | Salinan persis sheet utama vendor (huruf kolom sama dengan file asli) |

**Kalau ada yang salah:** isi kolom `Koreksi` di MAP dengan huruf kolom RAW (mis. `KD`), atau `X` bila memang tidak ada. Simpan, tutup Excel, lalu jalankan ulang. Koreksi tetap dipakai di setiap putaran berikutnya.

**Header berulang yang urutannya sudah dikonfirmasi** (mis. audiometri blok 1 = kanan, blok 2 = kiri) diberi `urutan_dikonfirmasi` di `variabel_standar.json`, sehingga statusnya OK.

**Vendor baru dengan nama header lain:** tambahkan nama itu ke `alias` di `variabel_standar.json`, tanpa mengubah kode.

**`--cek`** menghitung ulang file hasil dengan LibreOffice (tanpa membuka Excel Anda), lalu membandingkan setiap sel rumus dengan hitungan Python. Harus tertulis `beda = 0`.

File vendor yang sedang terbuka di Excel tetap bisa dibaca (lewat salinan sementara). File **hasil** harus ditutup dulu sebelum dijalankan ulang.

## Langkah 2: SUMMARY per slide (`mcu_summary.py`)

Jalankan setelah MAP sudah dicek (tidak ada CEK lagi):

```powershell
uv run --with openpyxl python mcu_summary.py "C:\...\Analisa\PT. PPS_New - Analisa.xlsx" --grup bagian --cek
uv run --with openpyxl python mcu_summary.py "C:\...\Analisa\PT. WKP - Analisa.xlsx" --grup departemen:10 --grup bagian:10 --cek
```

`--grup KODE:N` = kolom untuk tabel per divisi (kode dari MAP) dan berapa grup terbesar yang ditampilkan.

Sheet yang ditambahkan ke workbook Analisa (semuanya rumus):

| Sheet | Isi | Bisa diedit? |
|---|---|---|
| `SUMMARY` | Satu blok per slide: S3 demografi, kelaikan & risiko (apa adanya dari vendor), semua temuan, S4 top ten, S5 top 3 per grup, S6 kombinasi 3 kelainan, S8-S15 per topik, interpretasi spirometri/rontgen/EKG/audiometri | Tidak (hasil) |
| `CHECK` | Setiap sel SUMMARY di sebelah hitungan ulang Python. Sel B2 "Jumlah BEDA" harus 0. Juga daftar potongan Kesimpulan yang tidak cocok dengan temuan mana pun | Tidak |
| `DICT_TEMUAN` | Temuan yang dicari di Kesimpulan vendor: kata kunci, pengecualian, ikut Top ten atau tidak | Ya |
| `DICT_NILAI` | Kategori untuk isi teks (jenis kelamin, merokok, alkohol, olahraga, spirometri, rontgen, EKG, audiometri). Kuning = saran otomatis | Ya |
| `DICT_CUTOFF` | Cutoff kombinasi 3 kelainan dan batas umur. Kuning = default | Ya |
| `PEKERJA` | Satu baris per pekerja (nomor baris = RAW): umur, grup, tanda 1/0 per temuan | Tidak |

Edit di sheet DICT, simpan, tutup Excel, lalu jalankan ulang `mcu_summary.py`; editan Anda tetap dipakai.
Temuan baru yang ditambahkan ke `temuan_standar.json` otomatis ikut masuk. `--reset-dict` membuang isi sheet DICT dan memakai ulang default JSON (editan DICT hilang).

Kolom abu-abu "Bantu urutan (abaikan)" hanya dipakai rumus untuk mengurutkan Top Ten dan top 3 per grup tanpa bentrok bila jumlahnya sama; tidak masuk PPT. Daftar "Potongan Kesimpulan yang tidak cocok" di CHECK juga hanya untuk tinjauan, tidak masuk PPT.
**Perhatian:** menjalankan ulang `mcu_reader.py` membuat workbook baru (hanya koreksi MAP yang dipertahankan), jadi edit DICT ikut hilang.

Keputusan vendor (status kelaikan, risiko, Kesimpulan, interpretasi) dipakai apa adanya. Grup dihitung dengan huruf besar/kecil dan spasi disamakan.

## Langkah 3: laporan PPT (`mcu_ppt.py`)

```powershell
uv run --with openpyxl --with python-pptx python mcu_ppt.py "C:\...\Analisa\PT. PPS_New - Analisa.xlsx" --template "C:\...\Professional MCU Template\Untitled design.pptx"
```

Hasilnya `<nama> - Laporan MCU.pptx` di folder Analisa. Desain mengikuti template Canva pilihan Anda; font diganti ke Arial Black (judul) dan Arial (isi) karena font Canva (Neue Montreal, Helios) tidak terpasang di komputer.

- Semua angka diambil dari SUMMARY yang dihitung ulang dengan LibreOffice; skrip menolak jalan bila sheet CHECK masih ada BEDA.
- Catatan pembicara (speaker notes) tiap slide berisi sel SUMMARY sumber angkanya.
- Setelah disimpan, PPT dibuka lagi dan setiap angka/teks serta data chart dicocokkan dengan SUMMARY; juga dicek tidak ada sisa teks template.
- Chart dan tabel adalah chart/tabel PowerPoint asli, bisa diedit.
- Teks edukasi dan rekomendasi ada di `ppt_konten.json` (diambil dari laporan lama Anda); rekomendasi hanya muncul untuk topik yang memang ada temuannya, diurutkan dari persentase temuan tertinggi. Isi `"penyaji"` di file itu untuk nama di sampul.
- Foto orang di template diganti gambar gedung dari template yang sama (dipotong tengah agar tidak gepeng).
- `--aset "<folder>"` (opsional) menambah slide gambar edukasi (infografis, tabel kriteria, QR) setelah slide topik. Folder berisi gambar dan `aset_edukasi.json` yang mengatur judul, urutan, dan keterangan. Gambar tidak disimpan di repo publik; untuk MCU Nov 2026 foldernya `Documents\Project\Nov 2026\Aset edukasi`.

## Langkah 4: file vendor + sheet Ringkasan (`mcu_excel_ringkas.py`)

Untuk dokter/vendor yang memberikan file. Membuat duplikat file vendor (file asli tidak diubah) dan menambah sheet **Ringkasan** tepat di sebelah sheet data vendor, berisi tabel seperti di PPT beserta grafik Excel asli.

```powershell
uv run --with openpyxl --with python-pptx python mcu_excel_ringkas.py "C:\...\Analisa\PT. PPS_New - Analisa.xlsx"
```

Hasil: `PT. PPS_New - dengan Ringkasan.xlsx` di sebelah file vendor.

- Hanya satu sheet yang ditambahkan (Ringkasan); tidak ada sheet tersembunyi. Setiap angka adalah rumus yang menghitung langsung dari sheet data vendor (`SUMPRODUCT`, `MATCH`, `SEARCH`, `AGGREGATE`), dengan kata kunci, kategori, dan cutoff yang sama dengan file Analisa.
- Top ten dan top 3 per grup dipilih dengan rumus dari tabel "Semua temuan" dan tabel bantu di kolom AD ke kanan (di luar area cetak).
- Setelah disimpan, file dihitung ulang dengan LibreOffice dan setiap angka dicocokkan dengan SUMMARY file Analisa.
- Rumus disimpan sebagai rumus array (`{=...}`) dan setiap tes logika diubah ke 0/1 (`--`), karena Excel (berbeda dari LibreOffice) menganggap FALSE lebih besar dari angka dan membaca fungsi di dalam SUMPRODUCT hanya satu baris bila bukan rumus array.
- `--cek-excel` menghitung ulang salinan di Excel tersembunyi (instance terpisah) dan membandingkan semua sel rumus dengan LibreOffice. Pakai ini sebelum file dikirim.

## Langkah berikutnya (belum dibuat)
- Pembersihan data dan cutoff tambahan: hanya bila Anda bilang datanya perlu dibersihkan
