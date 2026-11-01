# Status Okupasi Builder

Mengisi ulang **Berkas/Status Okupasi** (format PPDS Sp.Ok FKUI) dengan memakai docx yang sudah
pernah dibuat sebagai **basis**. Format asli (logo, font, numbering, tabel, checkbox, body map)
tetap utuh. Skrip hanya mengganti isi.

> Repo ini **publik**. Jangan commit file isi pasien (`*.json`) maupun docx hasil.
> Simpan keduanya di folder pasien di OneDrive.

## Alur kerja per pasien

1. **Kumpulkan data**: transkrip wawancara (`.txt`) + beberapa kunjungan HIS (`.mhtml`) cukup.
2. **Pilih basis**: status lama dengan stase yang sama. Untuk stase psikiatri dipakai
   `References/Contoh status okupasi/Status Okupasi Vidya_Depresi_Researcher.docx`
   (sudah memuat status mental, NBJSQ, Aksis I–V, AMA BPRS/GAF/PIRS, rekomendasi 3 pihak).
3. **Tulis `isi_status_okupasi_<inisial>.json`** di folder pasien (Claude bisa menyusunnya dari
   wawancara + HIS). Lihat skema di bawah.
4. **Jalankan**:
   ```
   python status_okupasi_builder.py "<folder pasien>/isi_status_okupasi_XX.json"
   ```
5. **Lengkapi manual di Word**: gambar BRIEF survey, arsiran body map, skor NBJSQ/BRIEF/BPRS/PIRS
   bila belum ada (ditandai `[...]`), tanda tangan.

Untuk melihat anchor dan nomor tabel basis lain: `python status_okupasi_builder.py basis.docx --map`

## Skema JSON

| Kunci | Fungsi |
|---|---|
| `base_docx`, `output_docx` | Path basis dan nama file hasil (relatif ke folder JSON). |
| `subs` | `[lama, baru]` atau `[lama, baru, true]` (semua kemunculan). Ganti potongan teks walau terpecah di beberapa run. Dipakai untuk identitas, tanggal, nilai TTV. |
| `identity_checks` | Pilihan checkbox tabel identitas (nomor opsi, mulai 1): `jenis_kelamin, agama, status_kawin, pendidikan, kedudukan, alasan_datang, diobati_sebelumnya, sistem_bayar, alergi_obat`. |
| `checks` | Checkbox di paragraf: `{"para": "a. Nadi", "values": [true, false]}`. |
| `paras` | Ganti satu paragraf utuh: `{"startswith": "Diri sendiri :", "text": "...", "occ": 0}`. |
| `sections` | Ganti semua paragraf di antara dua judul: `{"from": "...", "to": "...", "lines": [...]}`. `to: null` artinya sampai akhir dokumen. Gambar di section itu ikut terhapus. |
| `tables` | `by_label` (isi kolom kanan menurut label kolom kiri, misal tabel 7 langkah), `rows` (ganti baris data; `null` = gabung dengan sel di atas), `cells` (`[baris, kolom, teks]`), `bold_row` (Kategori Kesehatan). |

### Penanda baris di `lines` / isi sel

Secara default, baris ke-k memakai gaya paragraf asli ke-k di section itu.

- `• ` pakai paragraf bernomor/bullet asli berikutnya
- `~ ` pakai paragraf tanpa nomor asli berikutnya
- `@N ` pakai paragraf asli ke-N (0-based), misal `@0` judul tebal, `@1` isi bullet
- `!b ` tebal
- `\n` di isi sel = paragraf baru; `\t` = tab

### Nomor tabel pada basis psikiatri (Depresi_Researcher)

0 RM/HP · 1 identitas · 2 RPP · 3 riwayat pekerjaan · 4 bahaya potensial (2 baris header) ·
5 tujuh langkah diagnosis okupasi · 6 kategori kesehatan · 7 prognosis · 8 permasalahan ·
9 METs · 10 prognosis (laik kerja) · 11 persetujuan pembimbing
