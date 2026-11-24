"""6.6 Alur diagnosis asma akibat kerja (NotebookLM q09 + PubMed)."""

ASMA_KERJA = [
    ("h2", "6.6 Alur Diagnosis Asma Akibat Kerja: Cross-shift, Bronkodilator, PEF Serial, Uji Provokasi"),
    ("new", "Sumber notebook: NIOSH 2004 (Appendix C), Spirometry in Occupational Health 2020 (ACOEM, Tabel 7), "
            "Konsensus PERDOKI 2019, PPT Ujian Spirometri Tambahan Adit, video Spirometri part 2. Karena notebook "
            "tidak memuat protokol PEF serial, OASYS, dan ambang uji provokasi, bagian itu dilengkapi dari PubMed: "
            "review \"Update on the Management of Occupational Asthma and Work-Exacerbated "
            "Asthma\" (Allergy Asthma Immunol Res 2019; doi:10.4168/aair.2019.11.2.188), Moore dkk. Chest 2009 "
            "(doi:10.1378/chest.08-0778), Moore dkk. Occup Med 2009 (doi:10.1093/occmed/kqp081) dan 2012 "
            "(doi:10.1093/occmed/kqs097), ERS technical standard on bronchial challenge testing 2017 "
            "(doi:10.1183/13993003.01526-2016)."),
    ("table", [
        ["Entitas", "Mekanisme", "Pajanan", "Masa laten", "Prinsip tata laksana kerja"],
        ["Asma akibat kerja tipe sensitizer (occupational asthma)", "Imunologis (sensitisasi) terhadap agen spesifik",
         "Berulang; >300 sensitizer (isosianat, debu kayu keras, tepung, enzim, lateks, akrilat)",
         "Ada (minggu–tahun; isosianat paling sering 2–3 tahun pertama)",
         "Hentikan pajanan SEPENUHNYA (substitusi atau pindah kerja); respirator saja tidak cukup"],
        ["Asma akibat iritan / RADS", "Cedera epitel toksik, non-imunologis",
         "Satu kali pajanan sangat tinggi (klorin, amonia, asap kebakaran)", "Tidak ada (gejala <24 jam)",
         "Cegah kebocoran/insiden berulang; pajanan iritan rendah dikurangi, tidak harus nol"],
        ["Asma yang diperberat pekerjaan (work-exacerbated)", "Asma yang sudah ada dicetuskan faktor kerja",
         "Iritan, udara dingin, beban fisik, alergen umum", "Asma sudah ada sebelum bekerja",
         "Optimalkan terapi, kurangi pemicu, akomodasi kerja"],
    ]),
    ("p", "**Alur pemeriksaan (sebaiknya saat pekerja MASIH bekerja dan terpajan):**"),
    ("n", "**Anamnesis kerja**: gejala memburuk saat kerja dan membaik saat libur/cuti; gejala bisa muncul beberapa jam "
          "setelah shift (reaksi lambat); hubungan dengan perubahan bahan/proses; SDS bahan. Tidak adanya sensitizer "
          "yang dikenal TIDAK menyingkirkan asma kerja."),
    ("n", "**Konfirmasi asma**: spirometri dan uji bronkodilator (2022: kenaikan >10% dari nilai prediksi untuk FEV1 "
          "atau FVC; 2005: ≥12% dan ≥200 mL dari baseline)."),
    ("n", "**Cross-shift spirometri/APE**: Konsensus PERDOKI 2019 VEP1 turun >10% atau APE turun >20%; OSHA "
          "cotton dust ≥5% (atau >150 mL bila FEV1 <3 L) sebagai \"reactor\". Satu hari negatif tidak menyingkirkan."),
    ("n", "**PEF serial di tempat kerja vs saat libur** (langkah objektif pertama yang dianjurkan pedoman; ACOEM 2020 "
          "Tabel 7: \"consider peak flow recordings at and away from work\"). Pekerja meniup peak flow meter beberapa "
          "kali sehari (catat terbaik dari 3 tiupan tiap waktu) pada hari kerja dan hari libur, catat jam kerja dan "
          "obat. Data yang cukup untuk skor ABC: PEF tiap 2 jam (±8 kali/hari) selama ≥8 hari kerja dan ≥3 hari "
          "libur; bila hanya ≤4 kali/hari, perlu ≥15 hari kerja agar spesifisitas >90%."),
    ("n", "**Analisis OASYS** (program komputer Oasys-2): skor Oasys-2 ≥2,51 dipakai sebagai batas asma akibat kerja. "
          "Skor ABC (area between curves: selisih PEF rerata hari kerja dan hari libur per jam sejak bangun) ≥15 "
          "L/menit/jam: spesifisitas 100%, sensitivitas ±72%. Variasi diurnal saja kurang spesifik."),
    ("n", "**Uji provokasi bronkus non-spesifik** (metakolin/histamin): positif bila dosis/konsentrasi yang "
          "menurunkan FEV1 20% rendah. Standar ERS 2017 kini melaporkan **PD20** (dosis kumulatif yang diberikan) "
          "menggantikan PC20, dengan napas tidal (bukan inspirasi maksimal). Penelitian lama memakai PC20 histamin "
          "≤16 mg/mL (sensitivitas 87%, spesifisitas 36% terhadap SIC). Metakolin yang dilakukan saat masih bekerja: "
          "sensitivitas 95%, nilai prediksi negatif 98%, artinya hasil NEGATIF saat masih terpajan membuat asma kerja "
          "sangat tidak mungkin. Saat jauh dari pajanan, hiperresponsif bisa membaik sampai normal. Perbandingan PC20 "
          "saat bekerja vs libur (perubahan bermakna) mendukung asma kerja."),
    ("n", "**Specific inhalation challenge (SIC)** = standar emas: hanya di pusat khusus, dengan tantangan kontrol "
          "dan pajanan bertahap terhadap agen tersangka. Positif bila FEV1 turun **≥15% dari baseline** selama "
          "pemantauan ≥6 jam. Dipakai bila pemeriksaan lain tidak bisa atau diagnosis masih ragu."),
    ("n", "**Pemeriksaan tambahan**: IgE spesifik/skin prick (praktis untuk agen berat molekul tinggi: tepung, "
          "hewan, enzim; IgE isosianat sangat spesifik tetapi sensitivitas ±44%), eosinofil sputum induksi (naik "
          "setelah pajanan; menambah sensitivitas sampai ±94% bersama FeNO dan uji hiperresponsif)."),
    ("pearl", "Jangan suruh pekerja cuti panjang sebelum diperiksa: diagnosis jauh lebih sulit setelah lama bebas "
              "pajanan. Prognosis terbaik bila diagnosis dan penghentian pajanan dilakukan dini, saat asma masih "
              "ringan (rerata hanya ±32% sembuh simtomatik setelah ±31 bulan dihentikan pajanannya)."),
    ("flag", "Disfungsi pita suara (inducible laryngeal obstruction) bisa meniru asma kerja dan dipicu iritan. "
             "Petunjuknya loop INSPIRASI yang mendatar pada flow-volume loop, sehingga manuver FIVC penting."),
]
