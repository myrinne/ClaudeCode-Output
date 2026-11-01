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
5. **Lengkapi manual di Word**: arsiran body map, skor NBJSQ bila belum ada (ditandai `[...]`),
   tanda tangan. Gambar BRIEF dibuat otomatis (lihat `brief`).

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
| `brief` | Isi otomatis formulir **BRIEF™ Survey v3.0** (PDF isian) per aktivitas, render ke PNG (`<output>_BRIEF_N.png`), lalu sisipkan dengan baris `IMG:brief:N`. Lihat di bawah. |
| `clear_ink` | Default `true`: hapus coretan ink di basis (arsiran body map pasien contoh). |
| `tables` | `by_label` (isi kolom kanan menurut label kolom kiri, misal tabel 7 langkah), `rows` (ganti baris data; `null` = gabung dengan sel di atas), `cells` (`[baris, kolom, teks]`), `bold_row` (Kategori Kesehatan). |

### BRIEF survey otomatis

```json
"brief": {
  "template": ".../PDF BRIEF Form 3.0_2 (1).pdf", "width_cm": 16, "dpi": 150,
  "activities": [
    {"title": "Memasak pesanan", "job": "Pedagang makanan", "station": "Memasak pesanan",
     "site": "Rumah", "date": "09/09/2024",
     "parts": {"RHW": "PFR", "Neck": "PD", "Back": "PD"},
     "postures": ["HWExtended", "NeckFlex", "BackFlex"],
     "stressors": {"V": ["LeftHand", "RightHand", "Whole Body"]}}
  ]
}
```

- Bagian tubuh: `LHW RHW LE RE LS RS Neck Back Legs`. Kode: `P` posture, `F` force, `D` duration, `R` frequency.
  Duration/Frequency hanya boleh bila Posture/Force dicentang (aturan form).
- Skor dan Risk Rating dihitung otomatis (3–4 = H, 2 = M, 0–1 = L); kotak hijau dipindah ke rating terpilih.
  Pastikan teks HASIL BRIEF SURVEY sama dengan skor ini (log builder mencetak skor tiap aktivitas).
- Ikon postur: `HWFlexed HWExtended HWUlnar HWRadial ElbowRotate ElbowExtend ShoulderBehind ShoulderRaised
  ShoulderShrug NeckFlex NeckSide NeckExtend NeckTwist BackFlex BackSide BackExtend BackTwist BackUnsupp
  LegsSquat LegsKneel LegsUnsupp`.
- Stressor Step 4: `V L S I G` → huruf ditulis di bagian tubuh (`Head`, `LeftHand`, `RightShoulder`, `Whole Body`, ...).
- Di section `III. BRIEF`: `"lines": ["Judul aktivitas 1", "IMG:brief:1", "Judul aktivitas 2", "IMG:brief:2"]`.
  Judul otomatis *keep with next* agar tidak terpisah dari gambarnya.

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
