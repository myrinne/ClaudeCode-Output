# -*- coding: utf-8 -*-
"""Vignette OSCE + lafaz untuk Bagian 1 (1.1 sampai 1.12). Skenario fiktif untuk latihan."""

V = {
    "1.1": dict(
        skenario="Manajer K3 pabrik kimia bertanya kepada Anda sebagai dokter okupasi. Studi toksisitas tikus pada zat X menguji tiga dosis: 0,1; 1; dan 10 mg/kg/hari. Efek merugikan baru bermakna pada 1 mg/kg/hari. Ia juga heran mengapa benzena dikatakan \"tidak punya dosis aman\", sedangkan merkuri anorganik punya nilai ambang.",
        qa=[
            ("Tentukan NOAEL dan LOAEL, lalu hitung RfD bila faktor ketidakpastian antarspesies 10 dan antarmanusia 10.",
             "NOAEL adalah dosis tertinggi tanpa peningkatan efek merugikan yang bermakna, yaitu 0,1 mg/kg/hari. LOAEL adalah dosis terendah yang mulai menimbulkan efek, yaitu 1 mg/kg/hari. RfD = NOAEL dibagi hasil kali UF dan MF, jadi 0,1 / (10 × 10) = 0,001 mg/kg/hari."),
            ("Apa kelemahan NOAEL dan pendekatan apa yang menggantikannya?",
             "NOAEL harus salah satu dosis yang diuji, mengabaikan bentuk kurva, dan studi kecil berdaya rendah justru menghasilkan NOAEL lebih tinggi sehingga kurang protektif. Penggantinya benchmark dose: seluruh kurva dimodelkan pada benchmark response 1 sampai 10%, lalu batas bawah kepercayaan 95% (BMDL) dipakai sebagai titik awal perhitungan."),
            ("Mengapa benzena diperlakukan tanpa ambang, sedangkan merkuri anorganik berambang?",
             "Benzena adalah karsinogen genotoksik. Satu metabolit reaktif yang mengikat DNA dapat memicu mutasi permanen, sehingga diasumsikan tidak ada dosis bebas risiko (linear non-threshold). Risikonya dinyatakan sebagai ECR dan pajanan ditekan serendah mungkin (ALARA). Merkuri anorganik bekerja lewat pengikatan gugus tiol dan tubuh punya cadangan faal serta perbaikan seluler, sehingga ada ambang dan risikonya dinilai dengan RQ ≤ 1."),
        ]),
    "1.2": dict(
        skenario="Lembar data keselamatan (SDS) sebuah bahan pembersih industri mencantumkan: LD50 oral tikus 250 mg/kg, LD50 dermal 1.500 mg/kg, dan LC50 inhalasi uap 4 jam 1,5 mg/L. Petugas K3 bertanya klasifikasinya dan apakah angka LD50 cukup dipakai sebagai dasar NAB.",
        qa=[
            ("Tentukan kategori toksisitas akut GHS untuk masing-masing rute.",
             "Oral 250 mg/kg berada pada lebih dari 50 sampai 300, jadi Kategori 3. Dermal 1.500 mg/kg berada pada lebih dari 1.000 sampai 2.000, jadi Kategori 4. Inhalasi uap 1,5 mg/L berada pada lebih dari 0,5 sampai 2,0, jadi Kategori 2."),
            ("Sebutkan elemen komunikasi bahaya untuk rute yang paling berbahaya.",
             "Rute paling berbahaya adalah inhalasi uap Kategori 2. Piktogramnya tengkorak dan tulang bersilang, kata sinyal DANGER, pernyataan bahaya H330 \"Fatal if inhaled\". Untuk oral Kategori 3 dipakai H301, dan dermal Kategori 4 memakai tanda seru, WARNING, H312."),
            ("Mengapa LD50 tidak boleh dijadikan dasar NAB?",
             "LD50 hanya mengukur kematian, tidak menilai efek non-letal, kronik, mutagenik, maupun karsinogenik. Reprodusibilitas antarlaboratorium buruk, ekstrapolasi dari hewan inbred ke pekerja outbred lemah, dan nilai median mengabaikan slope kurva. Kadar yang membunuh 50% bukan batas aman. NAB diturunkan dari NOAEL, LOAEL, atau BMDL dengan faktor ketidakpastian."),
        ]),
    "1.3": dict(
        skenario="Hasil pemantauan personal pekerja pelarut: TWA 8 jam zat X adalah 16 ppm (TLV-TWA 20 ppm; zat X tidak punya STEL). Terdapat empat ekskursi 15 menit sebesar 50 ppm, dengan jeda lebih dari 1 jam. Zat X juga bernotasi Skin dan manajer menyimpulkan \"udara di bawah NAB, jadi aman\".",
        qa=[
            ("Apakah pajanan puncak tersebut memenuhi syarat?",
             "Untuk zat tanpa STEL berlaku aturan 3 kali 5: ekskursi boleh sampai 3 × TWA, yaitu 60 ppm, selama 15 menit, maksimal 4 kali sehari, dengan jeda 1 jam, dan tidak boleh melebihi 5 × TWA, yaitu 100 ppm. Ekskursi 50 ppm sebanyak 4 kali dengan jeda cukup dan TWA 16 ppm masih di bawah 20 ppm, jadi memenuhi syarat."),
            ("Tanggapi kesimpulan manajer mengenai notasi Skin.",
             "Kesimpulan itu belum tepat. Notasi Skin berarti rute kulit, mukosa, dan mata berkontribusi bermakna pada dosis total, sehingga pemantauan udara saja tidak cukup. Diperlukan sarung tangan yang sesuai dan biomonitoring untuk menilai dosis internal."),
            ("Jelaskan status hukum TLV ACGIH dibandingkan NAB Permenaker 5/2018.",
             "TLV ACGIH adalah rekomendasi profesional berbasis kesehatan dan tidak mengikat. NAB dalam Permenaker 5/2018 adalah hukum positif yang wajib dipatuhi, dengan sanksi. Jebakannya, ACGIH diperbarui tiap tahun sedangkan Permenaker statis sampai direvisi, sehingga angka Permenaker sering lebih tua dan keduanya perlu disebutkan."),
        ]),
    "1.4": dict(
        skenario="Perusahaan tambang menerapkan roster 12 jam per hari, 4 hari kerja lalu 3 hari libur (48 jam per minggu). Zat kimia di area kerja punya NAB 8 jam sebesar 100 ppm dan bersifat toksikan kumulatif kronis.",
        qa=[
            ("Hitung NAB yang disesuaikan dengan model Brief dan Scala.",
             "RFd = (8/12) × ((24 − 12)/16) = 0,67 × 0,75 = 0,50. RFw = (40/48) × ((168 − 48)/128) = 0,83 × 0,9375 = 0,78. Dipakai faktor reduksi terkecil, yaitu 0,50, sehingga NAB yang disesuaikan = 100 × 0,50 = 50 ppm."),
            ("Hitung dengan pendekatan OSHA untuk zat kategori 3, lalu bandingkan.",
             "Kategori 3 adalah toksikan kumulatif, jadi dipakai penyesuaian mingguan: RFw = 40/48 = 0,83, sehingga NAB yang disesuaikan = 100 × 0,83 = 83,3 ppm. OSHA lebih longgar karena tidak memberi penalti pada berkurangnya jam pemulihan. Brief dan Scala paling konservatif dan menjadi pilihan bila farmakokinetik zat belum diketahui."),
            ("Batas pajanan apa yang tidak disesuaikan pada shift panjang?",
             "Hanya TWA yang disesuaikan. STEL atau PSD dan Ceiling atau KTD tidak pernah disesuaikan, karena melindungi dari efek akut dan iritasi seketika. BEI juga tidak dikoreksi secara numerik karena sudah mencerminkan kadar internal."),
        ]),
    "1.5": dict(
        skenario="Di ruang pengecatan terukur aseton 300 bds (NAB 750), MEK 120 bds (NAB 200), dan butil asetat sekunder 100 bds (NAB 200). Ketiganya menekan sistem saraf pusat dan mengiritasi saluran napas atas. Pekerja mengeluh pusing. Manajer berkata, \"semuanya di bawah NAB masing-masing\".",
        qa=[
            ("Hitung indeks campuran dan simpulkan.",
             "Karena organ target dan efeknya sama, efek dianggap aditif. Rumusnya Σ(Ci/Ti) ≤ 1. Substitusi: 300/750 + 120/200 + 100/200 = 0,40 + 0,60 + 0,50 = 1,50. Nilai lebih dari 1, jadi NAB campuran terlampaui walaupun tiap zat di bawah NAB-nya."),
            ("Apa tindak lanjut Anda?",
             "Pengendalian teknik dan administratif sampai indeks ≤ 1, misalnya ventilasi pembuangan lokal, lalu pemantauan ulang. Basis waktu harus konsisten: pajanan 8 jam dibandingkan TWA, 15 menit dibandingkan STEL atau PSD, sesaat dibandingkan Ceiling atau KTD."),
            ("Kapan rumus unity tidak berlaku?",
             "Bila organ target berbeda, misalnya Pb dan H2SO4, tiap zat dinilai sendiri. Pada sinergisme, seperti CCl4 dengan etanol atau toluena dengan bising di atas 85 dBA, rumus unity meremehkan risiko. Pada potensiasi, seperti isopropanol dengan CCl4, rumus gagal karena zat yang tidak toksik dihitung nol. Karsinogen A1 sampai A3 tidak cukup dengan unity dan ditekan serendah mungkin."),
        ]),
    "1.6": dict(
        skenario="Pekerja pabrik cat terpajan benzena di bawah 1 ppm. Laboratorium menawarkan tiga pemeriksaan urin: fenol, t,t-asam mukonat (t,t-MA), dan S-fenilmerkapturat (S-PMA). Hasil β2-mikroglobulin urin seorang pekerja Cd lain juga meningkat dan atasannya menganggap itu pasti keracunan kadmium.",
        qa=[
            ("Pilih biomarker benzena yang paling tepat dan jelaskan alasannya.",
             "Saya memilih S-PMA karena paling spesifik, bahkan pada pajanan rendah mendekati latar belakang asap rokok. Fenol urin sudah dihapus karena sensitivitas dan spesifisitasnya buruk pada pajanan di bawah 1 ppm. t,t-MA kurang spesifik karena asam sorbat dari pengawet makanan dan dihambat ko-pajanan toluena."),
            ("Sebutkan tiga jenis biomarker dengan contoh timbal.",
             "Biomarker eksposur: Pb darah, dan tulang dengan K-XRF untuk beban kumulatif. Biomarker efek: penurunan ALAD serta kenaikan ALA dan ZPP. Biomarker kerentanan: polimorfisme ALAD, di mana ALAD2 mengikat Pb lebih kuat sehingga Pb darah lebih tinggi."),
            ("Tanggapi anggapan bahwa β2-mikroglobulin tinggi pasti keracunan kadmium.",
             "β2-mikroglobulin adalah biomarker efek yang sangat sensitif tetapi tidak spesifik. Hipertensi, diabetes, obat nefrotoksik, dan merokok dapat memengaruhinya. Interpretasinya harus bersama U-Cd, pH urin, dan riwayat pajanan."),
        ]),
    "1.7": dict(
        skenario="Seorang pekerja benzena mendapat hasil S-PMA urin akhir shift 30 µg/g kreatinin (BEI 25 µg/g kreatinin). Atasannya berkata, \"berarti dia sudah leukemia, langsung pecat saja\".",
        qa=[
            ("Apa arti hasil tersebut?",
             "Hasil di atas BEI berarti benzena terserap dan terdetoksifikasi. Itu bukan diagnosis leukemia atau anemia aplastik dan bukan garis kaku aman atau berbahaya. Hasil ini adalah alarm untuk menyelidiki lingkungan, APD, dan ventilasi serta mengulang sampel. Tindakan administratif berat tidak diambil dari satu hasil."),
            ("Kapan sampel diambil untuk Cr urin dan Pb darah?",
             "Cr urin: akhir shift setelah 4 sampai 5 hari kerja berturut-turut, atau sampel berpasangan pra dan pasca shift untuk melihat kenaikan selama shift. Pb darah: discretionary atau not critical karena waktu paruhnya sangat panjang, dan kenaikan tajam pada serial tetap bermakna meski di bawah BEI."),
            ("Apakah BEI merupakan standar hukum di Indonesia? Apa arti notasi B?",
             "BEI dari ACGIH adalah nilai panduan profesional, bukan standar hukum. Di Indonesia angkanya mengikat setelah diadopsi sebagai IPB dalam Permenaker 5/2018. Notasi B (background) berarti determinan juga ada pada orang yang tidak terpajan okupasional, misalnya S-PMA benzena, sehingga latar belakang populasi harus diperhitungkan."),
        ]),
    "1.8": dict(
        skenario="Tiga sampel urin sewaktu. Pekerja A: analit 6 µg/L, kreatinin 1,2 g/L. Pekerja B: kreatinin 0,2 g/L. Pekerja C (perempuan dengan malnutrisi, kreatinin tidak andal): analit 8 µg/L, berat jenis 1,016.",
        qa=[
            ("Hitung kadar pekerja A dalam µg/g kreatinin dan nilai apakah sampel layak.",
             "µg/g kreatinin = analit (µg/L) dibagi kreatinin (g/L) = 6 / 1,2 = 5 µg/g kreatinin. Kreatinin 1,2 g/L berada dalam rentang layak 0,3 sampai 3,0 g/L."),
            ("Bagaimana sampel pekerja B diperlakukan?",
             "Kreatinin 0,2 g/L di bawah 0,3, jadi urin terlalu encer dan tidak boleh diinterpretasi. Sampel dibuang, pekerja diedukasi hidrasi seimbang, lalu sampel diambil ulang. Bila berulang di luar rentang, dievaluasi secara medis, misalnya fungsi ginjal dan diabetes."),
            ("Koreksi kadar pekerja C dan sebutkan zat yang tidak perlu koreksi kreatinin.",
             "Koreksi berat jenis: C koreksi = C ukur × (SG ref − 1,000) / (SG sampel − 1,000) = 8 × (0,024 / 0,016) = 12 µg/L, dengan SG referensi 1,024. Zat yang tidak dikoreksi: yang diekskresi lewat difusi pasif tubulus, dan yang BEI-nya berbasis volume, seperti aseton urin 25 mg/L, metanol 15 mg/L, dan MEK 2 mg/L. Pada gagal ginjal berat kreatinin juga tidak andal."),
        ]),
    "1.9": dict(
        skenario="Pekerja pencuci komponen yang memakai karbon tetraklorida (CCl4) dan rutin minum alkohol datang dengan ikterus, nyeri perut kanan atas, ALT dan AST sangat tinggi, serta INR memanjang. Pemeriksaan menunjukkan nekrosis sentrilobular.",
        qa=[
            ("Jelaskan mengapa riwayat alkohol memperberat toksisitas CCl4.",
             "Etanol menginduksi CYP2E1. CYP2E1 mengubah CCl4 lewat dehalogenasi reduktif menjadi radikal triklorometil dan peroksi-triklorometil, yang memicu peroksidasi lipid dan nekrosis sentrilobular di zona 3 hati. Induksi enzim membuat bioaktivasi lebih besar, jadi alkohol memperberat toksisitas."),
            ("Bedakan fase I dan fase II biotransformasi dengan contoh.",
             "Fase I adalah fungsionalisasi, menambah atau membuka gugus -OH, -NH2, -SH, atau -COOH, misalnya oksidasi CYP450, reduksi, dan hidrolisis. Fase II adalah konjugasi dengan molekul endogen polar: glukuronidasi (UGT, kapasitas terbesar), sulfasi (mudah jenuh), glutation (GST, jalur asam merkapturat), asetilasi (NAT), dan metilasi. Tujuannya mengubah zat lipofilik menjadi hidrofilik, tetapi dapat juga menghasilkan metabolit reaktif."),
            ("Jelaskan bioaktivasi metanol dan terapinya.",
             "Metanol dimetabolisme ADH menjadi formaldehida lalu ALDH menjadi format. Format menghambat sitokrom c oksidase, menimbulkan asidosis metabolik anion gap tinggi, osmolar gap, dan kebutaan. Terapinya etanol atau fomepizol untuk menghambat ADH, serta hemodialisis."),
        ]),
    "1.10": dict(
        skenario="Pekerja pengecoran logam memiliki U-Cd meningkat dengan paparan sudah dihentikan 5 tahun lalu. Pada pekerja lain, trikloroetilen (waktu paruh sekitar 24 jam) dipantau dan mengikuti pola kenaikan Senin sampai Jumat. Pekerja ketiga terpajan uap toluena sangat tinggi dan kadar darahnya naik mendadak.",
        qa=[
            ("Mengapa U-Cd masih tinggi walaupun pajanan sudah berhenti?",
             "T1/2 = 0,693 × Vd / Cl. Kadmium punya volume distribusi sangat besar karena terikat jaringan, terutama ginjal, sehingga T1/2 puluhan tahun, 10 sampai 30 tahun, meski klirens normal. Karena itu U-Cd mencerminkan beban ginjal, sampling bersifat not critical, dan kenaikan tajam pada serial tetap bermakna."),
            ("Berapa lama zat dengan T1/2 24 jam mencapai steady state dan apa implikasinya pada sampling?",
             "Fraksi steady state = 1 − (1/2)^n. Setelah 5 T1/2 tercapai 96,9%, sekitar 97%, dianggap steady state. Untuk T1/2 24 jam berarti sekitar 5 hari, sehingga zat menumpuk Senin sampai Jumat dan sampel diambil pada akhir shift akhir minggu kerja (end of workweek)."),
            ("Mengapa kadar toluena naik mendadak pada pajanan sangat tinggi?",
             "Eliminasi mengikuti Michaelis-Menten: v = Vmax·C / (Km + C). Pada C jauh lebih kecil dari Km kinetika orde-1. Pada pajanan sangat tinggi enzim jenuh dan kinetika menjadi orde-0 dengan laju konstan Vmax, sehingga toksikan utuh menumpuk mendadak dan T1/2 memanjang."),
        ]),
    "1.11": dict(
        skenario="Unit okupasi memantau tiga kelompok pekerja: (a) electroplating krom dengan MDA dan 8-OHdG meningkat, (b) pengaspalan dengan pajanan PAH, (c) petani penyemprot organofosfat dengan salivasi, miosis, dan fasikulasi.",
        qa=[
            ("Jelaskan mekanisme stres oksidatif pada kelompok (a).",
             "Stres oksidatif adalah ketidakseimbangan antara produksi ROS dan kapasitas antioksidan. O2•− menjadi H2O2 oleh SOD, lalu reaksi Fenton menghasilkan radikal hidroksil. GSH adalah pertahanan utama dan toksik bila terkuras lebih dari 70 sampai 80%. Radikal memicu peroksidasi lipid dengan produk MDA, dan kerusakan DNA terlihat sebagai 8-OHdG."),
            ("Bagaimana kelompok (b) menimbulkan kanker?",
             "Benzo(a)piren dibioaktivasi CYP450 menjadi metabolit elektrofil. Elektrofil keras mengikat nukleofil keras, yaitu N2 guanin, membentuk aduk DNA, lalu timbul mutasi seperti TP53 dan K-ras. Klinisnya kanker paru."),
            ("Jelaskan mekanisme kelompok (c) dan beda organofosfat dengan karbamat.",
             "Okson organofosfat memfosforilasi Ser-203 asetilkolinesterase sehingga asetilkolin menumpuk dan menimbulkan krisis kolinergik muskarinik, nikotinik, dan sentral. Terjadi aging, yaitu lepasnya satu gugus alkil, sehingga enzim terkunci permanen dan tidak dapat direaktivasi oksim. Karbamat melakukan karbamilasi yang reversibel dalam hitungan jam."),
        ]),
    "1.12": dict(
        skenario="Pabrik memakai benzena dalam sistem tertutup total. Direktur bertanya, \"benzena itu IARC Grup 1, jadi pekerja kami pasti kena kanker?\" Ia juga membaca bahwa zat lain berada pada IARC Grup 3 dan menganggapnya aman.",
        qa=[
            ("Jelaskan perbedaan hazard dan risk pada pertanyaan direktur.",
             "IARC menilai bahaya, yaitu kemampuan bawaan zat menimbulkan kanker, secara kualitatif. Risiko adalah probabilitas pada dosis dan skenario nyata, yaitu bahaya × pajanan, dan dinilai oleh EPA, OSHA, atau ARKL. Benzena dalam sistem tertutup total tetap berbahaya Grup 1, tetapi risikonya mendekati nol."),
            ("Sebutkan klasifikasi benzena di IARC, GHS, dan ACGIH beserta targetnya.",
             "Benzena IARC Grup 1, GHS Kategori 1A dengan piktogram Health Hazard, kata sinyal DANGER, dan H350, serta ACGIH A1. Target kankernya AML dan MDS."),
            ("Apa arti IARC Grup 2B dan Grup 3?",
             "Grup 2B mungkin karsinogenik: bukti manusia terbatas dan bukti hewan kurang dari cukup, atau bukti manusia tidak memadai dengan bukti hewan cukup. Grup 3 tidak dapat diklasifikasikan karena data tidak memadai, dan itu bukan berarti aman."),
        ]),
}
