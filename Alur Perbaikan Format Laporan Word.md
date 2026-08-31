# Alur Kerja: Merapikan Format Laporan Word (Heading, Sitasi Vancouver, Tabel/Gambar)

Dibuat dari pengalaman merapikan `Laporan K3RS_Vidya_Cecilia.docx` (Agustus 2026). Dipakai untuk laporan akademik/board-exam berformat Word yang: heading-nya belum pakai style Word yang benar, penomoran tabel/gambar berantakan, sitasi tersebar dalam beberapa gaya (Vancouver + Harvard campur), dan format font/paragraf tidak seragam.

Cara pakai alur ini: minta Claude Code baca file ini lalu terapkan pada dokumen baru, sebutkan path file-nya. Semua skrip di bawah pakai `python-docx` — jangan edit XML docx secara manual.

## 0. Sebelum mulai

- **Selalu kerja di file salinan** (`_RAPI.docx` atau sejenisnya), jangan timpa file asli, sampai kamu (Vidya) konfirmasi hasilnya oke.
- Simpan backup bertahap tiap kali akan melakukan perubahan besar (`<nama>_backup-sebelum-revisiN.docx`), supaya bisa mundur kalau ada yang salah.
- Nama file skrip Python **jangan** memakai nama modul bawaan Python (mis. `inspect.py`) — itu akan menabrak `import inspect` yang dipakai library seperti lxml/python-docx secara internal dan menghasilkan error `circular import` yang membingungkan. Pakai nama seperti `docx_inspect.py`.
- Kalau mengirim print ke terminal Windows, gunakan `io.open(path, "w", encoding="utf-8")` untuk file output — jangan print langsung karakter Unicode (¹, é, ×, dst.) ke `stdout` di console Windows yang default `cp1252`, karena akan `UnicodeEncodeError`. Selalu tulis hasil analisis ke file `.txt` lalu baca file itu dengan tool Read.

## 1. Baca & audit dokumen dulu — jangan langsung edit

Tulis satu skrip audit (`python-docx`) yang mengekstrak dan menulis ke file teks:

1. Jumlah paragraf, tabel, gambar (inline_shapes), section.
2. Daftar heading yang TERLIHAT seperti heading (regex `BAB`, pola `\d+(\.\d+){0,3}`, baris huruf besar pendek) — lalu **cek manual satu per satu**, karena banyak false positive: nomor formulir ("1. Nama:"), daftar isi kuesioner ("2. Jenis Kelamin"), enumerasi dalam kalimat ("(1) ...; (2) ..."). Style Word saat ini (`p.style.name`) membantu membedakan heading asli dari teks biasa yang kebetulan diawali angka.
3. Semua baris yang mengandung kata "Tabel"/"Gambar" — pisahkan mana **caption asli** (baris pendek, itu saja isinya) vs **referensi silang** dalam kalimat ("...disajikan pada Tabel 4.2...") vs **referensi ke dokumen/tabel EKSTERNAL** (mis. "Tabel 4.1 Pedoman Manajemen Risiko RSCM" — ini bukan tabel di laporan sendiri, jangan disentuh).
4. Semua sitasi: cari pola `(Nama, Tahun)` (Harvard/APA) DAN superscript run (`run.font.superscript`) DAN — ini gampang kelewat — **glyph superscript Unicode** (¹²³⁴⁵⁶⁷⁸⁹⁰, U+00B9/U+00B2/U+00B3/U+2074–2079/U+2070) yang kadang dipakai sebagai "superscript palsu" alih-alih format Word asli. Cek juga superscript yang BUKAN sitasi (satuan m², m³, simbol ° suhu, trademark ™) — jangan ikut diubah.
5. Style default (`docDefaults` di `styles.xml`) untuk font & ukuran — jangan asumsikan font body itu Calibri/Arial hanya karena themeFont bilang begitu; cek `w:rFonts` di `w:docDefaults` langsung.
6. Paragraph format yang dipakai (`line_spacing`, `space_before/after`, `first_line_indent`, alignment) — kelompokkan per kombinasi, lihat mana yang paling sering dipakai (itu kemungkinan "standar" yang dimaksud penulis).
7. `w:outlineLvl` yang menempel LANGSUNG di paragraf (bukan dari style) — ini bisa bikin paragraf non-heading muncul di Daftar Isi walau style-nya "Normal". Sering ada di sisa format formulir/RCA yang di-paste dari dokumen lain.
8. Page break (`w:br type="page"` dan `paragraph_format.page_break_before`) beserta konteks (paragraf apa sebelum/sesudahnya) — supaya nanti bisa dibedakan break di pergantian bab vs break nyasar di tengah sub-bab.

**Susun semua temuan jadi daftar poin ke Vidya dulu**, sebelum eksekusi — terutama untuk keputusan yang tidak bisa ditebak sendiri (format penomoran BAB romawi vs angka, posisi Daftar Pustaka gabungan, dsb.). Pakai `AskUserQuestion` untuk 2-3 keputusan kunci itu.

## 2. Heading & penomoran ulang (Fase inti)

- Jangan pakai regex otomatis untuk menandai heading di seluruh dokumen — **buat mapping eksplisit** `{index_paragraf: (level, teks_baru_atau_None)}` dari hasil audit manual di atas. Regex-only berisiko ikut mengubah teks form/enumerasi yang cuma mirip heading.
- BAB + judul bab biasanya 2 baris terpisah (mis. "BAB I" lalu "PENDAHULUAN") — style-kan KEDUANYA jadi `Heading 1`, jangan digabung jadi satu paragraf (aman & lazim dipakai di laporan institusi Indonesia; Daftar Isi akan menampilkan 2 baris per bab, itu wajar).
- Kalau ada bab yang penomoran sub-babnya salah start dari 1 lagi (mis. "BAB 4" isinya "1.1.1, 1.1.2, ..." padahal seharusnya "4.1, 4.2, ..."), **jangan cuma ganti prefix teks** — hitung ulang levelnya berdasar kedalaman titik (`1.1.2.1` = 4 segmen → setelah prefix salah "1.1." dibuang & diganti "4." jadi `4.2.1` = 3 segmen = level 3 yang benar). Ini juga otomatis menutup celah nomor yang hilang (mis. "...11" lompat ke "...13" karena "...12" memang tidak pernah ada) karena penomoran baru dihitung ulang dari urutan kemunculan, bukan disalin dari angka lama.
- Terapkan style `Heading 1/2/3` VIA `paragraph.style = doc.styles['Heading N']`, lalu override langsung font/ukuran/bold/warna di level run (jangan andalkan definisi bawaan style Heading Word, karena sering pakai warna tema biru/tidak konsisten).
- Sub-heading yang berupa label tebal tanpa nomor (mis. "Problem Statement", "RCA", label field formulir) **jangan** dijadikan Heading — biarkan bold biasa, supaya tidak numpuk di Daftar Isi.

## 3. Penomoran ulang Tabel & Gambar

- Skema paling aman: **nomor urut per BAB saja** (Tabel 4.1, 4.2, 4.3, ...), bukan mengikuti nomor sub-bab — ini yang bikin nomor lama sering dobel (dua tabel beda di sub-bab yang sama kebagian nomor sama).
- Bangun mapping `{index: caption_baru_lengkap}` dari hasil audit, replace teks paragraf caption itu SATU-SATU (bukan regex global), dan sertakan juga mapping untuk **kalimat referensi silang** ("disajikan pada Tabel ...") di paragraf lain yang menyebut nomor lama itu.
- **Verifikasi tidak ada duplikat** setelah selesai: scan ulang semua caption, pastikan tiap `(Tabel|Gambar, nomor)` cuma muncul sekali sebagai caption asli.

## 4. Sitasi → Vancouver terpadu

Ini bagian paling rawan salah. Prinsip:

1. **Kumpulkan semua identitas sumber unik** dulu (dari Daftar Pustaka yang tersebar + sitasi in-text), baru tentukan nomor — jangan menomori sambil jalan tanpa peta lengkap.
2. **Dedupe berdasarkan identitas sumber, bukan teks sitasi** — "(Kemenkes RI, 2016)" dan "(Kementerian Kesehatan Republik Indonesia, 2016)" kemungkinan besar regulasi yang SAMA, cek judul lengkapnya di teks/daftar pustaka sebelum memutuskan.
3. Nomor final ditentukan oleh **urutan kemunculan pertama di seluruh dokumen** (bukan per bab). Kalau bab yang isinya diedit ulang nanti dan urutannya berubah (lihat §7), SEMUA nomor sesudahnya bisa ikut bergeser — bukan cuma bab yang diedit.
4. Sitasi sekunder gaya "(A et al., dalam B et al., tahun)" → kutip sumber yang **benar-benar dibaca** (B), bukan A — ganti seluruh frasa jadi satu nomor superscript milik B.
5. Sumber yang disebut NAMANYA di kalimat tapi TANPA kurung "(...)" (umum untuk regulasi: "...sesuai UU No 17/2023 tentang Kesehatan, ...") tetap butuh superscript kalau dokumen itu memang sudah membiasakan pola begitu di bagian lain — sisipkan nomor tepat setelah nama instrumen, sebelum tanda baca berikutnya.
6. **Referensi tanpa sitasi in-text di manapun → hapus** dari Daftar Pustaka (jangan biarkan nyangkut).
7. Kalau ada sumber yang jelas-jelas dikutip tapi TIDAK ada di daftar pustaka manapun (studi/reference yang hilang), dan itu memang dokumen nyata yang sangat dikenal (mis. manual NIOSH, guideline WHO) — boleh dilengkapi dari pengetahuan umum, TAPI **selalu beri tahu Vidya secara eksplisit** referensi mana yang begitu, supaya bisa diverifikasi. Jangan pernah mengarang detail bibliografi yang tidak yakin kebenarannya.
8. **Cara ganti teks jadi superscript**: cari-dan-replace per paragraf (bukan seluruh dokumen sekaligus) dengan fungsi yang: (a) menghapus teks "(Nama, Tahun)" beserta satu spasi sebelumnya, (b) menyisipkan run baru berisi angka dengan `run.font.superscript = True`, (c) menyalin properti font (nama/ukuran/bold/warna) dari run asli supaya tidak berubah tampilan. Untuk satu paragraf dengan BEBERAPA sitasi, kumpulkan semua posisi dulu, urutkan berdasar posisi kemunculan di teks (bukan urutan di daftar rencana), baru bangun ulang paragraf sekali jalan.
9. **Format nomor gabungan**: `[4,5,6]` → `4-6` (≥3 berurutan pakai strip), `[1,3,4,5,9]` → `1,3-5,9` (kombinasi pakai koma) — kalau memang itu gaya yang diminta.
10. **Aturan tanda baca** (dikonfirmasi Vidya 2026-08-31): superscript diletakkan **setelah** titik/koma kalimat, langsung tanpa spasi, baru spasi sebelum kata berikutnya — `...dijelaskan.⁸ Kalimat berikutnya`, BUKAN `...dijelaskan⁸. Kalimat berikutnya`. Ini beda dari konvensi internasional yang lebih umum (superscript sebelum tanda baca) — pastikan ikuti versi Vidya untuk laporan Indonesia.
11. Kalau dokumen sudah punya heading "DAFTAR PUSTAKA" di satu tempat, taruh Daftar Pustaka final gabungan di **akhir dokumen** (setelah bab terakhir) kecuali diminta lain — hapus semua daftar pustaka parsial yang tersebar per-bab/per-subbab.

## 5. Font & warna

- Cek dulu font default sesungguhnya (`w:rFonts` di `docDefaults`) sebelum mengasumsikan dokumen belum Times New Roman — kadang sudah benar di level template, tinggal bersihkan pengecualian (font aneh yang ke-set eksplisit di beberapa run, biasanya sisa copy-paste).
- Set eksplisit di level run: `run.font.name`, `run.font.size = Pt(12)`, `run.font.color.rgb = RGBColor(0,0,0)` — jangan andalkan warna hitam "default" karena style Heading bawaan Word kadang override ke warna tema.
- **Kalau dokumen akan diedit lagi nanti oleh Vidya setelah dirapikan** (nambah teks baru dsb.), ingatkan bahwa teks baru itu TIDAK otomatis ikut aturan font/warna yang baru saja diterapkan — perlu re-run bagian "set warna hitam & font" itu lagi mencakup seluruh dokumen (idempotent, aman dijalankan berkali-kali).
- Style paste-an aneh dari AI chat (misal style bernama `font-claude-response-body` atau sejenisnya) → konversi ke `Normal`.
- Emoji/simbol (GHS hazard pictograms dsb.) — biarkan font aslinya (Segoe UI Emoji dkk.), jangan dipaksa Times New Roman (glyph-nya tidak akan tampil), cukup samakan ukurannya saja.

## 6. Paragraf, Daftar Isi, Daftar Tabel/Gambar, Page Break

- Paragraf isi (`style='Normal'`, bukan heading, bukan sampul): seragamkan `line_spacing` ke nilai yang paling umum dipakai di dokumen (biasanya 1.5). Jangan sentuh indentasi/spacing before-after list & formulir — risiko merusak tata letak lebih besar dari manfaatnya.
- **Daftar Isi otomatis**: sisipkan field TOC (`{ TOC \o "1-3" \h \z \u }`) via manipulasi XML langsung (`w:fldChar` begin/instrText/separate/end) setelah heading "DAFTAR ISI" — python-docx tidak punya API bawaan untuk field, harus bikin elemen OOXML manual.
- **Daftar Tabel & Daftar Gambar**: JANGAN pakai Heading style untuk caption supaya bisa masuk field TOC — itu akan bikin semua caption ikut nongol di Daftar Isi juga. Sebagai gantinya: buat **custom paragraph style** (mis. `DaftarTabelEntry`, `DaftarGambarEntry`, base on `Normal`), terapkan ke semua paragraf caption, lalu bikin field TOC terpisah pakai switch `\t "NamaStyle,1"` (bukan `\o`). Field TOC berbasis `\t` tetap dapat nomor halaman otomatis dari Word walau caption-nya teks biasa (bukan field SEQ) — asal style-nya dikenali saat "Update Field".
- **Selalu cek `w:outlineLvl` liar** (lihat §1.7) sebelum menganggap "kenapa teks non-heading ini ikut muncul di Daftar Isi" adalah soal style — kemungkinan besar itu properti outline langsung yang nempel dari format lama, bukan soal style Heading. Hapus elemen `<w:outlineLvl>` itu dari `pPr` paragraf yang bukan heading.
- **Page break**: hanya boleh ada di pergantian BAB (dan bagian depan: Halaman Pengesahan/Daftar Isi/Daftar Tabel/Daftar Gambar/Refleksi Diri/Daftar Pustaka). Cek tiap `w:br type="page"`, lihat paragraf SESUDAHNYA (lewati paragraf kosong) — kalau bukan judul BAB/section-level itu, hapus elemen `<w:br>`-nya (bukan paragrafnya, cukup elemen break-nya) supaya teks menyambung. Cek juga `paragraph_format.page_break_before` yang nyasar di tengah sub-bab.

## 7. Kalau dokumen diedit lagi setelah dirapikan

Ini yang paling sering kejadian: Vidya menulis ulang satu bab (nambah paragraf + sitasi baru + daftar pustaka sendiri di bawah bab itu) SETELAH proses di atas selesai. Langkah:

1. Baca ulang bab yang diedit, cari sitasi baru (gaya apa pun — Harvard, Vancouver, superscript Unicode).
2. Untuk tiap sitasi baru, cek dulu apakah itu **sumber yang SAMA** dengan yang sudah ada di Daftar Pustaka gabungan (bandingkan judul/regulasi lengkapnya, bukan cuma nama-tahun) — kalau sama, pakai nomor yang sudah ada, JANGAN bikin entri baru.
3. Karena penomoran Vancouver berbasis urutan kemunculan, kalau bab yang diedit itu urutannya lebih awal dari bab lain yang sudah bernomor, **nomor-nomor lama yang sudah ada pun bisa harus digeser** — hitung ulang urutan kemunculan LENGKAP dari awal dokumen, bukan cuma menambah nomor baru di ujung.
4. Hapus daftar pustaka lokal/sisipan yang baru ditambahkan manual di bab itu (biasanya muncul sebagai heading tak-formal seperti "Referensi bab X") setelah kontennya masuk ke Daftar Pustaka gabungan.
5. Jalankan lagi cek warna font hitam (§5) untuk teks baru itu.
6. **Selalu verifikasi ulang dengan reload file dari disk** setelah tiap fase simpan — jangan percaya begitu saja pada log skrip yang bilang "berhasil". Baca ulang paragraf yang barusan diubah dari file yang baru disimpan.

## 8. Jebakan teknis yang pernah kejadian (baca supaya tidak terulang)

- **Salah nama file output saat menyambung banyak skrip bertahap**: kalau develop skrip secara iteratif (`d.save(SRC + ".tmp_stageX.docx")` untuk tes tiap tahap), gampang lupa ganti baris save terakhir ke `d.save(SRC)` saat semua tahap sudah digabung jadi satu skrip. Akibatnya perubahan terasa "hilang" padahal skrip jalan tanpa error. **Selalu `grep -n "d.save"` di skrip sebelum run**, pastikan cuma ada satu `d.save(SRC)` di akhir (atau path yang memang dimaksud).
- Setelah `d.save(SRC)`, **buka ulang file itu di proses yang sama** (`docx.Document(SRC)` lagi) dan print beberapa baris kunci untuk memverifikasi isinya benar-benar tersimpan seperti yang dimaksud — jangan cuma percaya nilai variabel di memori sebelum save.
- Kalau mencari index paragraf lewat potongan teks (`fragment in paragraph.text`), hati-hati match ke **field TOC yang sudah pernah di-update di Word** (isinya jadi duplikat teks heading + nomor halaman) yang letaknya lebih awal di dokumen daripada versi "asli"-nya — cari dengan fragmen yang cukup unik dari isi paragraf (kalimat isi, bukan judul heading), atau batasi pencarian mulai dari index tertentu (`start=...`).
- Objek `Paragraph` dari python-docx tetap valid dipakai (`.text`, `.runs`, `._element`) walau paragraf LAIN di daftar yang sama sudah dihapus duluan — tidak perlu `d.paragraphs` ulang tiap kali menghapus satu paragraf, asal jangan hapus objek yang sedang dipegang itu sendiri.
