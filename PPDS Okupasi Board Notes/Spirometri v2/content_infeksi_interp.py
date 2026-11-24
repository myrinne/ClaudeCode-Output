"""4.9 infection control; 7.10 ERS/ATS 2022 patterns (PRISm, non-specific, dysanapsis)."""

INFEKSI = [
    ("h2", "4.9 Pengendalian Infeksi dan Higiene"),
    ("new", "Sumber: ATS/ERS 2019 (Hygiene and Infection Control), Guideline for Office Spirometry in Adults 2012 "
            "(South Africa), NIOSH Spirometry Training Guide 2004, presentasi Spirometri 2 (Marsen, Des 2024)."),
    ("p", "**Jalur penularan:** kontak langsung (mouthpiece, nose clip, spirometer genggam, sandaran kursi, katup "
          "dan selang proksimal; bisa termasuk hepatitis dan HIV bila ada luka mulut, gusi berdarah, atau "
          "hemoptisis) dan tidak langsung (droplet dan aerosol yang ditiupkan ke alat dan terlontar ke udara "
          "ruangan saat batuk di antara manuver: TB, influenza, patogen respirasi lain)."),
    ("table", [
        ["Komponen", "Ketentuan"],
        ["Tangan operator", "Cuci tangan/hand sanitizer sebelum kontak dengan tiap pasien dan segera setelah memegang "
                            "mouthpiece, selang, katup, atau bagian dalam alat. Sarung tangan tidak menggantikan cuci "
                            "tangan; ganti tiap pasien; wajib bila memegang alat terkontaminasi atau ada luka di tangan."],
        ["Tangan pasien", "Beri hand sanitizer saat masuk ruang pemeriksaan."],
        ["Filter in-line sekali pakai", "Standar praktik saat ini; mouthpiece biasanya menyatu dengan filter. Bila "
                                        "filter dipakai saat tes, filter juga dipakai saat verifikasi kalibrasi. "
                                        "Spirofilter yang dapat dipakai ulang diganti bila rusak (Marsen 2024), tetapi "
                                        "ATS/ERS 2019 mengutamakan filter sekali pakai."],
        ["Mouthpiece dan nose clip", "Satu pasien, satu mouthpiece baru. Nose clip sekali pakai dianjurkan; yang "
                                     "dipakai ulang harus didisinfeksi tingkat tinggi setiap kali. Pasien bisa diminta "
                                     "membuang sendiri mouthpiece bekas. Semua bahan sekali pakai dibuang di akhir sesi."],
        ["Alat", "Permukaan keras dilap alkohol isopropil. Bagian dengan embun ekspirasi didisinfeksi/disterilkan "
                 "sebelum dipakai lagi. Sensor yang baru dicuci harus kering dan bersuhu ruang sebelum kalibrasi. "
                 "Membongkar/mencuci sensor menuntut kalibrasi ulang. Ikuti petunjuk pabrik untuk bahan dan "
                 "konsentrasi disinfektan."],
        ["Sirkuit tertutup", "Wajib filter in-line per pasien; tanpa filter, seluruh sirkuit dibongkar dan "
                             "didisinfeksi. Spirometer volume sirkuit tertutup dibilas udara ruangan ≥5 kali volume "
                             "penuh antar-pasien (NIOSH 2004)."],
        ["Sirkuit terbuka (ekspirasi saja)", "Risiko kontaminasi silang paling kecil karena pasien tidak menghirup "
                                             "dari alat; pilihan untuk skrining massal di tempat kerja."],
        ["Ruangan", "Pertukaran udara memadai; bila sering menangani TB, pertimbangkan filtrasi HEPA atau "
                    "ultraviolet germicidal irradiation (NIOSH 2004)."],
    ]),
    ("p", "**Pasien dengan TB (terduga/terkonfirmasi), hemoptisis, lesi mulut, atau infeksi menular lain** (pada "
          "dasarnya kontraindikasi relatif, tunda sampai tidak menular). Bila pemeriksaan tetap perlu:"),
    ("n", "Jadwalkan **paling akhir** di hari itu agar alat bisa dibongkar dan didisinfeksi."),
    ("n", "Atau gunakan **alat khusus** yang hanya dipakai untuk pasien infeksius."),
    ("n", "Atau periksa di **kamar pasien sendiri** dengan ventilasi memadai dan perlindungan pernapasan yang tepat "
          "untuk operator."),
    ("n", "Filter in-line wajib; komponen yang terpajan darah/sekret didekontaminasi dengan disinfektan untuk "
          "patogen darah."),
    ("p", "Pekerja dengan infeksi saluran napas akut (flu, selesma) ditunda pemeriksaannya (NIOSH 2004); salah satu "
          "materi PPT menyebut penundaan minimal 3 hari setelah infeksi akut yang mengganggu usaha napas maksimal."),
    ("src", "Protokol khusus bernama \"COVID-19\" (swab pra-tes, N95/PAPR untuk teknisi, waktu jeda pengosongan "
            "ruangan) tidak ada di sumber notebook. Bila ditanya, jawab dengan prinsip di atas (filter, ventilasi, "
            "penjadwalan, APD pernapasan operator, sirkuit terbuka), lalu sebutkan bahwa rekomendasi era pandemi "
            "dibangun dari prinsip yang sama."),
]

INTERP2022 = [
    ("h2", "7.10 Pola Spirometri menurut ERS/ATS 2022: Obstruksi, Pola Non-spesifik/PRISm, Restriksi, Campuran, Dysanapsis"),
    ("new", "Diverifikasi langsung dari PDF ERS/ATS technical standard on interpretive strategies for routine lung "
            "function tests (Stanojevic dkk., Eur Respir J 2022;60:2101499) milik Anda: Tabel 1 (hlm. 3), hlm. 11–14 "
            "(BDR, perubahan waktu, severity), Gambar 8 dan Tabel 5 (hlm. 17–18), hlm. 19–20."),
    ("p", "**Algoritma ERS/ATS 2022 (Gambar 8):** (1) FEV1/FVC > persentil ke-5? Tidak → (2) FVC > persentil ke-5? "
          "Ya = obstruksi; Tidak = kemungkinan gangguan campuran → ukur volume paru. Bila rasio normal: FVC normal = "
          "spirometri normal; FVC rendah = kemungkinan restriksi ATAU pola non-spesifik → ukur volume paru (TLC)."),
    ("table", [
        ["Pola (Tabel 5)", "FEV1", "FVC", "FEV1/FVC", "Keterangan"],
        ["Obstruktif", "Normal/↓", "Normal", "↓", "FEV1/FVC (atau VC) < LLN; FEV1 tidak harus < LLN"],
        ["Restriktif", "↓", "↓", "Normal/↑", "Konfirmasi dengan TLC rendah (restriksi simpel vs kompleks)"],
        ["Non-spesifik", "↓", "↓", "Normal", "TLC normal; uji tambahan (BDR, Raw) bisa membantu. Bila TLC tidak "
                                             "tersedia, pada perokok/mantan perokok disebut PRISm"],
        ["Kelemahan otot", "↓", "↓", "Normal", "Tidak ada PEF yang tajam"],
        ["Usaha submaksimal", "↓", "↓", "Normal", "Tidak ada PEF yang tajam"],
        ["Campuran", "↓", "↓", "↓", "Perlu volume paru untuk konfirmasi"],
        ["Dysanapsis", "Normal", "Normal/↑", "↓", "Bisa varian normal"],
    ], [3.0, 1.7, 1.7, 1.7, 7.1]),
    ("b", "**Penyebut rasio:** ERS/ATS 2022 menganjurkan **FEV1/FVC**. FEV1/VC (VC terbesar dari SVC dan FVC) "
          "dianjurkan pada 2005; lebih sensitif tetapi kurang spesifik, VC sulit distandarkan (alat, riwayat volume), "
          "dan tidak ada persamaan referensi kuat untuk FEV1/VC, sehingga pemakaiannya menambah ketidakpastian "
          "diagnosis, terutama pada lansia. Pada orang sehat FVC tidak berbeda bermakna dari VC."),
    ("b", "**Pola non-spesifik:** FVC dan/atau FEV1 rendah, rasio normal, TLC normal. Bisa mencerminkan usaha kurang, "
          "restriksi dini (FVC turun sebelum RV), atau obstruksi dini/air trapping (kolaps saluran napas kecil "
          "menurunkan FVC sebelum rasio turun). Pada pemantauan 3 tahun, ±2/3 tetap non-spesifik dan ±1/3 menjadi "
          "penyakit obstruktif atau restriktif yang jelas. Bila usaha maksimal: ulang setelah bronkodilator; atau "
          "bandingkan dengan SVC (SVC > FVC lebih dari 100 mL berarti ada kolaps saluran napas saat ekspirasi paksa). "
          "PRISm berhubungan dengan munculnya pola restriktif maupun obstruktif yang lebih khas di kemudian hari."),
    ("b", "**Restriksi:** spirometri hanya bisa MENDUGA; konfirmasi TLC < persentil ke-5. Campuran: FEV1/FVC < LLN "
          "dan TLC < LLN."),
    ("b", "**Dysanapsis:** FEV1/FVC rendah dengan FEV1 dalam batas normal (FVC normal atau di atas prediksi; sering "
          "pada laki-laki, usia muda, bertubuh tinggi). Dulu dianggap varian fisiologis normal, tetapi data baru "
          "menunjukkan pola ini mungkin berkaitan dengan kecenderungan penyakit obstruktif; tafsirkan sesuai "
          "probabilitas pra-tes dan bila perlu BDR, DLCO, kekuatan otot, atau uji latih. (ACOEM 2020 memakai "
          "batasan FEV1 ≥100% prediksi.)"),
    ("p", "**Grading keparahan ERS/ATS 2022 (z-score), untuk SEMUA parameter:** normal > −1,645; ringan −1,65 s.d. "
          "−2,5; sedang −2,51 s.d. −4; berat < −4,1. Dasarnya: hazard ratio mortalitas pada z-score FEV1, FVC, dan "
          "DLCO; z −1,65 s.d. −2,5 risikonya hampir sama sehingga digabung menjadi \"ringan\". Derajat gangguan fungsi "
          "paru tidak sama dengan derajat penyakit (dipengaruhi juga gejala, anemia, kelemahan otot, dll.). Skema "
          "2005 (\"Using FEV1, includes obstruction or restriction\"): ringan >70%, sedang 60–69%, sedang-berat "
          "50–59%, berat 35–49%, sangat berat <35% prediksi."),
    ("p", "**Respons bronkodilator 2022:** (post − pre) / nilai prediksi GLI × 100%; >10% untuk FEV1 atau FVC = "
          "bermakna. Contoh dokumen: laki-laki 50 tahun, TB 170 cm, FEV1 2,0 → 2,4 L, prediksi 3,32 L → 12,1% → "
          "bermakna. Ini BUKAN sama dengan perubahan 10% dari nilai pre-BD. PEF dan FEF25-75 tidak dipakai untuk "
          "menilai respons karena sangat bervariasi."),
    ("p", "**Perubahan dari waktu ke waktu (dewasa):** pada bukan perokok >25 tahun FEV1 turun ±30 mL/tahun. Dulu "
          "dipakai perubahan absolut (mis. 100 mL) atau relatif (mis. 10% dari baseline). **Di kedokteran okupasi, "
          "dengan pemeriksaan tahunan atau lebih jarang, ambang 15% diusulkan** sebagai perubahan di luar variabilitas "
          "biologis. Penurunan yang terlihat dari banyak pengukuran lebih meyakinkan daripada dua pengukuran saja. "
          "Alternatif: **FEV1Q** = FEV1 (L) / 0,5 L (laki-laki) atau / 0,4 L (perempuan); normalnya 1 unit hilang "
          "±tiap 18 tahun (±10 tahun pada perokok dan lansia), jadi dalam setahun FEV1Q seharusnya stabil; contoh: "
          "perempuan 70 tahun FEV1 0,9 L → FEV1Q 2,25 (makin dekat 1, makin tinggi risiko kematian). Anak: "
          "conditional change score, normal bila dalam ±1,96."),
    ("p", "**FEF25-75%:** sangat bervariasi, sulit direproduksi, tidak spesifik untuk penyakit saluran napas kecil, "
          "dan tidak menambah keputusan klinis di luar FEV1, FVC, dan FEV1/FVC."),
    ("p", "**Rasio tetap 0,70 dan 80% prediksi:** tidak dianjurkan; batas normal = LLN persentil ke-5 (dan ULN "
          "persentil ke-95). FEV1/FVC turun fisiologis ±10% antara usia 20–70 tahun; LLN ±0,74 pada usia 20 tahun "
          "dan ±0,64 pada usia 70 tahun (ACOEM 2020)."),
    ("flag", "Konsensus PERDOKI 2019 untuk ujian board tetap memakai 75%/80% (versi paru) dan NNT (versi okupasi), "
             "dikotomis tanpa gradasi. Sebutkan konsep 2022 sebagai pengetahuan pembanding, lalu simpulkan dengan "
             "lafaz PERDOKI."),
]

