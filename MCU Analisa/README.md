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
| `GRUP` | Kandidat kolom divisi/bagian dan jumlah pekerja per nilai (apa adanya, huruf besar/kecil dibedakan). Tulis pilihan di sel B3 |
| `KOLOM_VENDOR` | Semua kolom vendor dan dipetakan ke mana; yang abu-abu belum dipakai |
| `SHEET_LAIN` | Sheet lain di file vendor (UNFIT, EKG, dll.) |
| `RAW` | Salinan persis sheet utama vendor (huruf kolom sama dengan file asli) |

**Kalau ada yang salah:** isi kolom `Koreksi` di MAP dengan huruf kolom RAW (mis. `KD`), atau `X` bila memang tidak ada. Simpan, tutup Excel, lalu jalankan ulang. Koreksi tetap dipakai di setiap putaran berikutnya.

**Vendor baru dengan nama header lain:** tambahkan nama itu ke `alias` di `variabel_standar.json`, tanpa mengubah kode.

**`--cek`** menghitung ulang file hasil dengan LibreOffice (tanpa membuka Excel Anda), lalu membandingkan setiap sel rumus dengan hitungan Python. Harus tertulis `beda = 0`.

File vendor yang sedang terbuka di Excel tetap bisa dibaca (lewat salinan sementara). File **hasil** harus ditutup dulu sebelum dijalankan ulang.

## Langkah berikutnya (belum dibuat)
- Pembersihan data dan cutoff: hanya bila Anda bilang datanya perlu dibersihkan
- `SUMMARY` per slide dan `CHECK`, lalu pengisian template PPT
