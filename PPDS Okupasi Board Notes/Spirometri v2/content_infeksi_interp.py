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
    ("h2", "7.10 Pola Spirometri menurut ERS/ATS 2022: Obstruksi, PRISm/Pola Non-spesifik, Restriksi, Campuran, Dysanapsis"),
    ("new", "Sumber: ERS/ATS technical standard on interpretive strategies for routine lung function tests (Stanojevic "
            "dkk., Eur Respir J 2022), Spirometry in Occupational Health 2020 (Townsend/ACOEM), Guideline for Office "
            "Spirometry in Adults 2012, Y. Sim 2017."),
    ("table", [
        ["Pola", "Kriteria", "Catatan dan tindak lanjut"],
        ["Obstruksi", "FEV1/VC < LLN (z < −1,645). VC = nilai terbesar dari FVC, EVC, atau IVC. "
                      "FEV1 tidak harus < LLN.",
         "Kolaps dinamis saat manuver paksa mengecilkan FVC sehingga FEV1/FVC bisa naik palsu. Penyebut VC terbesar "
         "membuat obstruksi tersembunyi lebih mudah terdeteksi."],
        ["PRISm / pola non-spesifik", "FEV1/VC ≥ LLN, tetapi FEV1 dan/atau FVC < LLN. Disebut pola non-spesifik bila "
                                      "TLC terukur normal.",
         "Penyebab: obesitas, penyakit saluran napas kecil dini, kelemahan otot napas ringan, inspirasi/usaha "
         "submaksimal. Lanjutan: ulang dengan kualitas baik, uji bronkodilator, TLC (body plethysmography/dilusi "
         "gas), DLCO, HRCT bila curiga kelainan parenkim akibat kerja."],
        ["Kemungkinan restriksi", "FEV1/VC ≥ LLN dan FVC < LLN pada spirometri saja.",
         "Spirometri tidak bisa menegakkan restriksi. Sebut \"pola restriksi / kemungkinan restriksi\"."],
        ["Restriksi terkonfirmasi", "TLC < LLN.", "Butuh pengukuran volume paru statis."],
        ["Campuran", "FEV1/VC < LLN DAN TLC < LLN.",
         "Bila hanya ada spirometri (rasio < LLN dan FVC < LLN): sebut \"obstruksi dengan FVC rendah, dugaan pola "
         "campuran\" dan rujuk untuk TLC."],
        ["Dysanapsis (varian fisiologis)", "FEV1/FVC < LLN dengan FEV1 ≥100% prediksi (ACOEM 2020).",
         "Pertumbuhan saluran napas tidak sebanding dengan volume paru; sering pada orang sangat bugar (atlet, "
         "pemadam kebakaran, tentara). Pada pekerja terpajan, tetap waspadai obstruksi awal dan ikuti longitudinal."],
    ]),
    ("p", "**Grading keparahan ERS/ATS 2022 (z-score):** ringan −1,65 sampai −2,5; sedang −2,51 sampai −4,0; berat "
          "< −4,1. Parameter utama tetap **z-score FEV1** dan berlaku untuk obstruksi maupun restriksi (\"Using FEV1 "
          "(includes obstruction or restriction)\"); skema yang sama dapat diterapkan pada FVC, TLC, dan DLCO. Skema "
          "lama ATS/ERS 2005 (5 tingkat, %prediksi FEV1): ringan >70%, sedang 60–69%, sedang-berat 50–59%, berat "
          "35–49%, sangat berat <35%."),
    ("p", "**Perubahan dari waktu ke waktu (dewasa):** ERS/ATS 2022 menyebut perubahan FEV1 >15% dalam periode "
          "pendek (±1 tahun) sering dipakai sebagai ambang di luar variabilitas biologis; variabilitas FEV1 tahun ke "
          "tahun pada orang sehat biasanya 6–8% (ini latar belakang angka ≥8% di kriteria PERDOKI). Perubahan harus "
          "ditafsirkan bersama riwayat klinis."),
    ("src", "Kutipan ERS/ATS 2022 di bagian ini diperoleh lewat NotebookLM yang dibatasi pada PDF ERS/ATS 2022 di "
            "notebook Anda; dysanapsis hanya disebut di Tabel 1 dokumen tersebut tanpa definisi naratif, sehingga "
            "definisinya (FEV1/FVC < LLN dengan FEV1 ≥100% prediksi) diambil dari ACOEM 2020."),
    ("p", "**FEF25-75%:** tidak dianjurkan untuk diagnosis rutin atau skrining penyakit saluran napas kecil; "
          "variabilitasnya sangat besar (±20% vs ±3% pada FEV1) dan LLN-nya sekitar 50% prediksi."),
    ("p", "**Rasio tetap 0,70:** tidak dianjurkan untuk mendefinisikan obstruksi. FEV1/FVC turun fisiologis ±10% "
          "antara usia 20–70 tahun; LLN ±0,74 pada usia 20 tahun (underdiagnosis pekerja muda) dan ±0,64 pada usia "
          "70 tahun (overdiagnosis pekerja senior). Rasio 0,70 hanya pas di sekitar usia 40 tahun."),
    ("flag", "Konsensus PERDOKI 2019 untuk ujian board tetap memakai 75%/80% (versi paru) dan NNT (versi okupasi), "
             "bersifat dikotomis tanpa gradasi. Sebutkan konsep 2022 sebagai pengetahuan pembanding, lalu simpulkan "
             "dengan lafaz PERDOKI."),
]
