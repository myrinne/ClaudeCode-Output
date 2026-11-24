"""Sections built from NotebookLM answers q06-q11 (+ PubMed / web checks)."""
from content_late_c import REG_REWRITE, REG_ADD, ASMA_KERJA, KUESIONER, KECACATAN  # noqa: F401

PREDIKSI = [
    ("h2", "5.8 Nilai Prediksi untuk Pekerja Indonesia dan Cara Menghitung NNT dari Data Mentah"),
    ("new", "Sumber: Konsensus Spirometri PERDOKI 2019 (Tabel 1), presentasi Spirometri 2 (Marsen, Des 2024, slide "
            "98–99), PPT Ujian Spirometri Tambahan Adit (slide 220–226), video Spirometri part 2 dan dr. Aziz Sp.Ok, "
            "GLI 2012 Multi-Ethnic Reference Values, Spirometry in Occupational Health 2020 (ACOEM)."),
    ("b", "Nilai prediksi resmi PERDOKI untuk pekerja Indonesia: **Pneumobile Project Indonesia**, dihitung dari "
          "jenis kelamin, usia, tinggi badan (dan etnis). Diakses lewat kalkulator daring pulmo.id/pneumobile atau "
          "dari perangkat lunak spirometer yang sudah memuat persamaan tersebut."),
    ("b", "Koefisien regresi Pneumobile (angka pengali tinggi badan dan umur) **tidak tercantum** di sumber "
          "notebook mana pun. Di ujian, nilai prediksi biasanya sudah diberikan di lembar hasil; tugas Anda "
          "menurunkan NNT dan membandingkan."),
    ("p", "**Rumus NNT (PERDOKI):** NNT = nilai prediksi − 1,64 × SD populasi referensi (batas persentil ke-5). "
          "Konstanta praktis:"),
    ("table", [
        ["Parameter", "NNT laki-laki", "NNT perempuan"],
        ["KVP (FVC)", "Prediksi − 673 mL", "Prediksi − 499 mL"],
        ["VEP1 (FEV1)", "Prediksi − 642 mL", "Prediksi − 447 mL"],
        ["VEP1/KVP", "Prediksi − 10%", "Prediksi − 9%"],
    ]),
    ("p", "**Langkah hitung dari data mentah:**"),
    ("n", "Samakan satuan (semua mL atau semua L)."),
    ("n", "Ambil nilai PREDIKSI dari mesin/kalkulator (bukan nilai terukur pasien) lalu kurangi konstanta sesuai "
          "jenis kelamin untuk mendapat NNT KVP, NNT VEP1, NNT rasio. Bila rasio prediksi tidak tertulis, hitung: "
          "prediksi VEP1 / prediksi KVP × 100%."),
    ("n", "Hitung rasio aktual = VEP1 terukur / KVP terukur × 100%."),
    ("n", "Langkah 1: rasio aktual < NNT rasio → obstruksi. Langkah 2: KVP terukur < NNT KVP → restriksi."),
    ("n", "Simpulkan: normal / obstruksi / restriksi / obstruksi dan restriksi (tanpa gradasi)."),
    ("p", "**Contoh 1 (slide Marsen 2024), laki-laki:** prediksi KVP 3.734 mL, prediksi VEP1 3.102 mL → prediksi "
          "rasio = 3.102 / 3.734 × 100% = 83,1%. Terukur KVP 3.900 mL, VEP1 2.700 mL → rasio aktual = 2.700 / 3.900 "
          "× 100% = 69,2%. NNT KVP = 3.734 − 673 = 3.061 mL; NNT VEP1 = 3.102 − 642 = 2.460 mL; NNT rasio = 83,1 − 10 "
          "= 73,1%. Rasio 69,2% < 73,1% → obstruksi; KVP 3.900 > 3.061 → tidak restriksi. **Kesimpulan: gangguan "
          "obstruksi.**"),
    ("p", "**Contoh 2 (PPT Adit), laki-laki 43 tahun, TB 172 cm, tambang batubara:** prediksi KVP 3.813 mL, "
          "prediksi rasio 81%. NNT KVP = 3.813 − 673 = 3.140 mL; NNT rasio = 81 − 10 = 71%. KVP terukur 3.100 mL "
          "(81% prediksi) < 3.140 → restriksi. Versi paru menyebutnya normal (KVP ≥80%), versi okupasi menyebutnya "
          "restriksi: contoh klasik perbedaan sensitivitas."),
    ("p", "**GLI 2012:** lima kategori etnis (Kaukasia, Afrika-Amerika, Asia Timur Laut, Asia Tenggara, "
          "lainnya/campuran). Untuk Indonesia pilih **Asia Tenggara**. Populasi Asia Tenggara memiliki volume lebih "
          "kecil dibanding Kaukasia dengan tinggi dan usia sama (FEV1 sekitar −9,7% laki-laki, −13,0% perempuan; FVC "
          "sekitar −12,3% laki-laki, −15,7% perempuan)."),
    ("p", "**Bila alat hanya punya nilai Kaukasia (NHANES III):** ACOEM 2020/OSHA memakai faktor koreksi **0,88** "
          "untuk FVC dan FEV1 pekerja keturunan Asia; rasio FEV1/FVC tidak dikoreksi."),
    ("pearl", "Kesalahan tersering di ujian: mengurangkan 673 mL dari KVP TERUKUR, bukan dari KVP PREDIKSI, atau "
              "mencampur liter dan mililiter."),
]

UAO = [
    ("h2", "6.5 Obstruksi Saluran Napas Atas/Sentral dan Galeri Bentuk Kurva"),
    ("new", "Sumber: Guideline for Office Spirometry in Adults 2012 (bagian 7.5 dan 8.1, Gambar 10), Y. Sim 2017, "
            "ATS/ERS 2019 (FIVC, BEV pada UAO), NIOSH 2004; indeks numerik dan pola tambahan diverifikasi dari "
            "ERS/ATS 2022 (hlm. 18 Gambar 9, hlm. 20 Tabel 6)."),
    ("p", "Lesi di laring, trakea, atau bronkus utama menghasilkan bentuk flow-volume loop yang khas, tergantung "
          "apakah lesinya kaku (fixed) atau lentur (variable), dan apakah terletak di luar atau di dalam rongga "
          "toraks."),
    ("table", [
        ["Pola", "Mekanisme", "Loop ekspirasi", "Loop inspirasi", "Contoh penyebab"],
        ["Fixed (tetap)", "Lesi kaku, tidak dipengaruhi tekanan transmural", "Datar (plateau), PEF terpotong",
         "Datar", "Stenosis trakea pasca-intubasi/trakeostomi, stenosis sikatrikal setelah inhalasi korosif akut "
                  "(klorin, amonia pekat, uap asam), tumor trakea, struma/massa mediastinum yang menekan"],
        ["Variabel ekstratoraks", "Saat inspirasi tekanan intralumen sub-atmosferik → lumen menyempit; saat "
                                  "ekspirasi melebar", "Relatif normal", "Datar",
         "Disfungsi pita suara/inducible laryngeal obstruction (peniru asma kerja, bisa dipicu iritan), paralisis "
         "pita suara, edema laring"],
        ["Variabel intratoraks", "Saat ekspirasi paksa tekanan pleura positif menekan trakea; saat inspirasi "
                                 "trakea melebar", "Datar", "Relatif normal",
         "Trakeomalasia, tumor/polip trakea distal"],
    ]),
    ("b", "Pada tahap awal, obstruksi saluran napas atas/sentral bisa belum menurunkan FEV1 dan/atau FVC, tetapi PEF "
          "sudah turun jauh; obstruksi yang makin berat akhirnya ikut menurunkan FEV1 dan FEV1/FVC (ERS/ATS 2022). "
          "Pasien UAO sering tidak mampu menaikkan aliran dengan cepat sehingga "
          "BEV bisa melewati batas; ATS/ERS 2019 mengizinkan operator meng-override penilaian BEV pada pasien ini."),
    ("b", "**FIVC wajib** bila mencari UAO: tanpa loop inspirasi, pola fixed dan variabel ekstratoraks bisa "
          "terlewat karena loop ekspirasi tampak normal. Alat ekspirasi-saja tidak bisa mendeteksinya."),
    ("b", "**Indeks numerik (ERS/ATS 2022).** Rasio **FEV1 (mL) / PEF (L/menit) >8** pada dewasa mengarah ke "
          "obstruksi saluran napas atas/sentral (Empey index) dan menjadi alasan merekam flow-volume loop inspirasi "
          "dan ekspirasi; usaha awal yang buruk juga bisa menaikkan rasio ini."),
    ("table", [
        ["Indeks (ERS/ATS 2022 Tabel 6)", "Ekstratoraks fixed", "Ekstratoraks variabel", "Intratoraks"],
        ["PEF", "Turun", "Normal atau turun", "Turun"],
        ["FIF50%", "Turun", "Turun", "Normal atau turun"],
        ["FIF50% / FEF50%", "~1", "<1", ">1"],
    ]),
    ("p", "(Dalam bentuk kebalikan yang sering dipakai buku lain, FEF50/FIF50: fixed ~1, variabel ekstratoraks >1, "
          "intratoraks <1.)"),
    ("b", "**Pola tambahan (ERS/ATS 2022):** sumbatan bronkus utama unilateral (jarang) → aliran inspirasi lebih "
          "tinggi di awal lalu menurun, dan aliran ekspirasi turun lalu mendatar di tengah loop (kurva bifasik); "
          "**pola sawtooth** (osilasi aliran inspirasi atau ekspirasi) menandakan ketidakstabilan mekanis dinding "
          "saluran napas. Plateau harus REPEATABLE pada usaha yang acceptable."),
    ("flag", "Tidak adanya pola klasik TIDAK menyingkirkan obstruksi saluran napas sentral. Bila curiga, rujuk untuk "
             "endoskopi atau pencitraan saluran napas (ERS/ATS 2022)."),
    ("b", "Kurva **dua puncak** akibat usaha berubah-ubah (meniup, mengendur, meniup lagi) adalah artefak, bukan "
          "pola penyakit: tidak acceptable karena syarat PERDOKI satu puncak tajam."),
    ("pearl", "Temuan plateau pada flow-volume loop → curigai stenosis saluran napas besar dan rujuk untuk "
              "bronkoskopi dan CT (Y. Sim 2017). Pada pekerja dengan riwayat inhalasi korosif atau intubasi lama "
              "pasca-kecelakaan kerja, ini bisa menjadi PAK/akibat kecelakaan kerja."),
]

SRC82 = [
    ("src", "Asal angka di tabel atas: ketiga kriteria (≥8% antar dua pemeriksaan tahun ke tahun; >90 mL/tahun pada "
            "evaluasi >3 tahun; nilai < LNL pada tahun yang sama) tertulis di Konsensus PERDOKI 2019 (bab penilaian "
            "antar waktu, slide 22–23); cukup SALAH SATU terpenuhi. Angka 90 mL/tahun ≈ tiga kali laju penuaan normal "
            "(±30 mL/tahun). Metode %prediksi (≥15% eksesif) berasal dari NIOSH/ACOEM. Saat menjawab, sebut kriteria "
            "mana yang Anda pakai."),
    ("new", "ERS/ATS 2022 menambahkan dua alat longitudinal: (1) **conditional change score** untuk anak (menilai "
            "apakah perubahan sesuai lintasan pertumbuhan), dan (2) **FEV1Q** untuk dewasa = FEV1 (L) / 0,5 L "
            "(laki-laki) atau / 0,4 L (perempuan), yaitu persentil ke-1 FEV1 pada orang dewasa dengan penyakit paru. "
            "FEV1Q menunjukkan berapa kali lipat cadangan fungsi di atas batas yang berkaitan dengan kelangsungan "
            "hidup, dan perubahannya bebas bias persamaan prediksi usia lanjut."),
]

CHANGELOG = [
    ("h1", "LAMPIRAN — CATATAN REVISI v2 (24 November 2026)"),
    ("p", "Versi ini dibuat dari Catatan_Spirometri.docx (file asli tidak diubah). Isi baru ditandai 🆕 BARU v2 "
          "beserta sumbernya; koreksi ditandai ✏️ DIKOREKSI v2 atau ditulis ulang langsung di tempatnya."),
    ("table", [
        ["Jenis", "Lokasi", "Perubahan"],
        ["Tambah", "4.7", "Prosedur pengambilan langkah demi langkah (SOP operator), coaching, kapan berhenti, "
                          "sirkuit tertutup vs terbuka, dokumentasi"],
        ["Tambah", "4.8", "Prosedur SVC dan IC, urutan SVC sebelum FVC, FEV1/VC (2005) vs FEV1/FVC (2022)"],
        ["Tambah", "4.9", "Pengendalian infeksi dan higiene"],
        ["Tambah", "4.10", "Grading kualitas A–F dan konsep usable (ATS/ERS 2019)"],
        ["Tambah", "4.5.3", "Galeri artefak kurva volume-time (gambar skematis)"],
        ["Tambah", "5.8", "Nilai prediksi Pneumobile/GLI dan langkah hitung NNT dari data mentah"],
        ["Tambah", "6.5", "Obstruksi saluran napas atas + galeri bentuk kurva flow-volume"],
        ["Tambah", "6.6", "Alur diagnosis asma akibat kerja (PEF serial, OASYS, uji provokasi)"],
        ["Tambah", "7.4", "Tabel ATS/ERS 2005 lima tingkat dan tabel perbandingan tiga skema"],
        ["Tambah", "7.10", "Pola ERS/ATS 2022: obstruksi, PRISm/non-spesifik, restriksi, campuran, dysanapsis"],
        ["Tambah", "8.2", "Asal angka kriteria longitudinal, FEV1Q dan conditional change score"],
        ["Tambah", "8.7", "Kuesioner gejala respirasi standar untuk surveilans"],
        ["Tambah", "11.5", "Penilaian kecacatan/impairment fungsi paru"],
        ["Tambah", "13.11", "Kunci jawaban Bank Kasus 1–8"],
        ["Koreksi", "1.3", "Regulasi: Permenkes 56/2016 diganti Permenkes 11/2022; deskripsi Permenakertrans "
                           "25/2008; tambahan regulasi terkait"],
        ["Koreksi", "2.1", "KVP bukan \"volume statik\"; FVC diukur dengan manuver paksa (dinamis)"],
        ["Koreksi", "4.1", "Daftar kontraindikasi disamakan dengan ATS/ERS 2019 (tanpa angka hipertensi); angka "
                           ">200/140 dari Y. Sim 2017"],
        ["Koreksi", "6.3", "ATS/ERS menganjurkan VC terbesar sebagai penyebut = anjuran 2005; ERS/ATS 2022 kembali "
                           "ke FEV1/FVC"],
        ["Koreksi", "4.4", "Posisi: duduk dianjurkan ATS/ERS 2019; berdiri setara, bukan \"lebih disukai\""],
        ["Koreksi", "5.7", "Label sumber kriteria cross-shift"],
        ["Koreksi", "7.1", "Langkah 2 mengikuti ERS/ATS 2022 (obstruksi tidak mensyaratkan FEV1 < LLN; PRISm)"],
        ["Koreksi", "7.3", "Rujukan ke \"Bagian 1.4\" yang tidak ada diganti isi langsung (GLI, Asia Tenggara)"],
        ["Koreksi", "7.4", "Judul dan header tabel: obstruksi memakai rasio AKTUAL VEP1/KVP, restriksi %prediksi KVP"],
        ["Koreksi", "7.5", "Nilai tabel z-score disamakan dengan ERS/ATS 2022 (−1,65/−2,5; −2,51/−4,0; < −4,1); "
                           "kalimat tabel 2005 kini memuat angkanya langsung"],
        ["Koreksi", "7.7", "\"Reversibel = asma\" diperhalus: respons bronkodilator mendukung, tidak memastikan"],
        ["Koreksi", "13.2", "Catatan bahwa teks Konsensus PERDOKI dan ATS/ERS 2019 hanya 150 mL; \"atau 5%\" dari "
                            "draf lafaz"],
        ["Verifikasi", "6.5, 7.10, 8.2", "Seluruh klaim ERS/ATS 2022 dicek ulang langsung dari PDF milik Anda: "
                                         "Empey >8 (bukan >10), FIF50/FEF50 Tabel 6, severity z-score untuk semua "
                                         "parameter, ambang okupasi 15%, definisi dysanapsis; klaim NotebookLM "
                                         "\"variabilitas tahunan 6–8%\" tidak ada di dokumen dan dihapus"],
        ["Koreksi", "Seluruh dokumen", "17 rujukan silang (\"lihat Bagian X\") diganti isi langsung agar tiap "
                                       "bagian bisa dibaca sendiri"],
    ]),
    ("src", "Yang masih perlu Anda verifikasi: (1) koefisien persamaan Pneumobile tidak ada di sumber; (2) batas "
            "waktu klaim JKK untuk PAK setelah hubungan kerja berakhir (PP 44/2015) di kunci Kasus 8; (3) status "
            "pencabutan PP 88/2019 oleh PP 28/2024."),
]
