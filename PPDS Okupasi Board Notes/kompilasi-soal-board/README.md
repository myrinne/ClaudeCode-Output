# Kompilasi soal ujian board Sp.Ok

Sumber data untuk `../Kompilasi Soal Ujian Board Sp.Ok 2016-2026.docx`.

- `data/*.txt`: satu file per ujian. Format per soal:
  `### <mcq|short|essay|case|stem|osce|oral> | <TOPIK> | <label ujian[, label lain]>`,
  lalu baris `Q:` (soal), `O:` (opsi), `A:` (kunci sumber), `S:` (sub-soal), `D:` (kunci diperdebatkan), `N:` (catatan / [Perlu dicek]).
- `merge.py`: daftar `GROUPS` (indeks soal yang sama digabung jadi satu; `*` = versi yang ditampilkan).
  Indeks berasal dari urutan `parse.parse()`. Tambahkan soal ujian baru di file data baru (nama urut paling belakang) supaya indeks lama tidak bergeser.
- `build.py`: membuat docx.

```
python build.py "../Kompilasi Soal Ujian Board Sp.Ok 2016-2026.docx"
```
