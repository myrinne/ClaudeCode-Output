# MCU Analisa

Analisa hasil MCU per perusahaan untuk HR / manajer (hat **MCU Data Analyst**, aturan lengkap di vault `Identity/hats/mcu-data-analyst.md`).

Prinsip: semua angka adalah rumus Excel, file vendor tidak pernah diubah, dan ada hitungan ulang terpisah yang harus menunjukkan beda = 0.

> Repo ini PUBLIC. Folder ini hanya berisi skrip. Excel pekerja dan hasil analisa tetap di OneDrive (`Documents\Project\<bulan>`).

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

## Langkah berikutnya (belum dibuat)
- Pembersihan data dan cutoff tambahan: hanya bila Anda bilang datanya perlu dibersihkan
