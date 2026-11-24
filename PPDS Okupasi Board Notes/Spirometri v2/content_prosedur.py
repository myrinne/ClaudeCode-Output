"""New sections 4.7 (SOP operator), 4.8 (SVC & IC), 4.10 (grading A-F / usable)."""

SOP = [
    ("h2", "4.7 Prosedur Pengambilan Spirometri Langkah demi Langkah (SOP Operator)"),
    ("new", "Sumber: ATS/ERS 2019 (Tabel 6 dan teks prosedur), NIOSH Spirometry Training Guide 2004, "
            "Konsensus Spirometri PERDOKI 2019, Guideline for Office Spirometry in Adults (South Africa 2012), "
            "Spirometry in Occupational Health 2020 (Townsend/ACOEM), presentasi Spirometri 2 (Marsen, Des 2024)."),
    ("p", "Bagian ini menjawab pertanyaan penguji \"bagaimana Anda memeriksanya?\". Urutannya mengikuti "
          "ATS/ERS 2019 Tabel 6 (cuci tangan → siapkan pasien → instruksi & demonstrasi → manuver → cek "
          "kualitas), dilengkapi detail operasional dari NIOSH 2004 dan Konsensus PERDOKI 2019."),
    ("h3", "A. Sebelum pasien masuk: alat dan ruangan"),
    ("n", "**Nyalakan dan panaskan alat** sesuai petunjuk pabrik; pastikan sensor bersih dan kering."),
    ("n", "**Atur titik nol aliran (zero-flow)** dengan sensor tertutup dan dipegang diam, sebelum kalibrasi dan "
          "sebelum setiap pasien. Bila ada aliran saat zeroing, ulangi. Zero-flow yang salah membuat FEV1 dan FVC "
          "tidak acceptable dan tidak usable (ATS/ERS 2019)."),
    ("n", "**Verifikasi kalibrasi harian** dengan syringe 3,00 L (akurasi syringe ±0,015 L): minimal 3 kali "
          "dorongan dengan kecepatan berbeda sehingga aliran 0,5–12 L/s (waktu injeksi 0,5–6 detik: cepat <1 "
          "detik, sedang 2–3 detik, lambat ±6 detik). Batas: ±3% (2,91–3,09 L) untuk inspirasi dan ekspirasi. "
          "Bila memakai filter in-line saat pemeriksaan, filter juga dipakai saat verifikasi. Alat harus dalam "
          "mode kalibrasi agar tidak dikoreksi BTPS (kalau terkoreksi, 3 L terbaca sekitar 3,30 L)."),
    ("n", "**Uji kebocoran** (spirometer volume): tekanan konstan ≥3 cmH₂O selama 1 menit; batas ≤10 mL/menit "
          "(ATS 1994), ≤20 mL/menit (NIOSH 2004), ≤30 mL/menit (ACOEM 2020). Syringe sendiri diuji bocor tiap bulan."),
    ("n", "**Catat suhu ruang (akurasi ±1°C), tekanan barometer, dan jam pemeriksaan.** Bila suhu ruang "
          "berubah >3°C dalam <30 menit, koreksi BTPS kontinu mungkin diperlukan. Simpan log kalibrasi."),
    ("n", "**Ruangan**: tenang, terpisah dari ruang tunggu, tersedia air minum dan tisu. Kursi berlengan, tanpa "
          "roda, tinggi bisa diatur agar telapak kaki rata di lantai."),
    ("h3", "B. Persiapan dan wawancara pasien"),
    ("n", "**Cuci tangan** (atau hand sanitizer) sebelum kontak; berikan juga hand sanitizer kepada pasien."),
    ("n", "**Konfirmasi identitas**: nama, tanggal lahir (umur dihitung sampai 1 desimal), jenis kelamin "
          "biologis (penentu nilai prediksi, bukan identitas gender), etnis (kategori GLI untuk Indonesia: Asia "
          "Tenggara)."),
    ("n", "**Ukur tinggi badan tanpa sepatu**: kaki rapat, berdiri setegak mungkin, mata lurus ke depan, punggung "
          "menempel dinding/stadiometer; catat dalam cm (1 desimal). Berat badan dengan pakaian dalam ruangan, "
          "tanpa sepatu, dibulatkan 0,5 kg; hitung IMT."),
    ("n", "**Bila pasien tidak bisa berdiri tegak** (kifoskoliosis berat, amputasi, kursi roda): perkirakan tinggi "
          "dari **rentang lengan (arm span)** atau **panjang ulna** (ulna diukur dengan kaliper; lebih disukai pada "
          "anak). Catat metode yang dipakai di laporan karena estimasi ini dipengaruhi jenis kelamin, usia, dan etnis "
          "(ATS/ERS 2019)."),
    ("n", "**Skrining kontraindikasi relatif** (ATS/ERS 2019 Tabel 2): IMA <1 minggu, hipotensi sistemik atau "
          "hipertensi berat, aritmia atrial/ventrikular bermakna, gagal jantung tak terkompensasi, hipertensi pulmonal "
          "tak terkontrol, kor pulmonal akut, emboli paru tidak stabil, riwayat sinkop saat ekspirasi paksa/batuk; "
          "aneurisma serebral, operasi otak <4 minggu, konkusi dengan gejala menetap, operasi mata <1 minggu; operasi "
          "sinus/telinga tengah atau infeksinya <1 minggu; pneumotoraks, operasi toraks atau abdomen <4 minggu, "
          "kehamilan akhir; infeksi menular aktif atau dicurigai (termasuk TB), hemoptisis, sekret banyak, lesi atau "
          "perdarahan mulut. Kontraindikasi relatif tidak otomatis melarang; dokter pengirim menimbang manfaat dan "
          "risiko."),
    ("n", "**Tanyakan dan catat** (ATS/ERS 2019 Tabel 5): merokok/vape/shisha dalam 1 jam, alkohol/zat intoksikan "
          "dalam 8 jam, olahraga berat dalam 1 jam, pakaian yang membatasi dada. Catat jenis, dosis, dan jam "
          "terakhir obat yang memengaruhi fungsi paru. Penahanan bronkodilator bila tujuan diagnostik: SABA 4–6 "
          "jam, SAMA 12 jam, LABA 24 jam, ultra-LABA (indakaterol, vilanterol, olodaterol) 36 jam, LAMA 36–48 jam. "
          "Kortikosteroid inhalasi dan antileukotrien tidak perlu ditahan. Catat juga gejala yang tampak (batuk, "
          "mengi, sesak, sianosis)."),
    ("n", "**Longgarkan pakaian ketat.** Gigi palsu yang pas biarkan terpasang; yang longgar dilepas."),
    ("h3", "C. Instruksi dan demonstrasi (wajib diperagakan operator)"),
    ("b", "Jelaskan tujuan: mengukur seberapa banyak dan seberapa cepat udara bisa dikeluarkan dari paru."),
    ("b", "Peragakan: posisi mouthpiece dan nose clip; postur tegak dengan dagu sedikit terangkat; tarik napas "
          "cepat sampai benar-benar penuh; tiup sekuat tenaga sampai benar-benar kosong; tarik napas lagi sekuat "
          "tenaga sampai penuh."),
    ("b", "Sampaikan bahwa inspirasi maksimal terasa tidak biasa dan sedikit tidak nyaman. Pastikan pasien paham "
          "dan bersedia mengikuti instruksi."),
    ("h3", "D. Manuver FVC (alat sirkuit tertutup, mengukur inspirasi dan ekspirasi)"),
    ("n", "Pasien duduk tegak (bahu sedikit ke belakang, dagu sedikit terangkat). Pasang **nose clip** (atau tutup "
          "hidung manual), masukkan mouthpiece di atas lidah dan di antara gigi, **bibir merapat** tanpa celah."),
    ("n", "Bernapas biasa (tidal) beberapa kali."),
    ("n", "**Inspirasi cepat dan lengkap sampai TLC; jeda di TLC ≤2 detik.** Jeda 4–6 detik atau inspirasi lambat "
          "menurunkan PEF dan FEV1. Tanda inspirasi sudah maksimal: alis terangkat, mata membelalak, kadang kepala "
          "bergetar. Pasien yang tampak nyaman kemungkinan belum penuh."),
    ("n", "**\"BLAST!\"** Tanpa ragu, embuskan sekuat dan secepat mungkin. Target: BEV <5% FVC atau <100 mL (mana "
          "yang lebih besar), waktu naik ke PEF (10–90%) ≤150 ms."),
    ("n", "**Lanjutkan ekspirasi sampai benar-benar kosong** sambil tetap tegak, sampai alat memberi tanda: plateau "
          "<25 mL dalam 1 detik (bunyi bip tunggal) atau FET 15 detik (bip ganda). Tidak ada lagi syarat durasi "
          "minimal 6 detik (dihapus pada 2019)."),
    ("n", "**Inspirasi kembali secepat dan sedalam mungkin** dengan mouthpiece tetap di mulut (FIVC). Bila FIVC − "
          "FVC >100 mL atau >5% FVC (mana yang lebih besar), pasien tidak memulai dari TLC dan manuver tidak "
          "acceptable. FIVC wajib bila sedang mencari obstruksi saluran napas atas."),
    ("n", "**Istirahat ≥1 menit** antar-manuver (Konsensus PERDOKI 2019), sampai pasien dan operator sepakat siap."),
    ("n", "**Ulangi**: target 3 FEV1 acceptable dan 3 FVC acceptable (boleh dari manuver yang berbeda), lalu cek "
          "repeatability (selisih 2 FVC terbesar dan 2 FEV1 terbesar ≤150 mL). Lanjutkan sampai kriteria tercapai, "
          "maksimal umumnya 8 manuver pada dewasa."),
    ("p", "**Alat ekspirasi saja (sirkuit terbuka, umum di skrining massal industri):** pasien menarik napas "
          "maksimal dari udara ruangan, lalu dalam ≤2 detik memasukkan mouthpiece, merapatkan bibir, dan langsung "
          "meniup maksimal. Mulut dibiarkan terbuka sampai mouthpiece terpasang untuk mengurangi kehilangan udara. "
          "Mouthpiece dilepas di akhir ekspirasi. Alat jenis ini tidak bisa mengukur FIVC, sehingga obstruksi saluran "
          "napas atas variabel ekstratoraks tidak terdeteksi."),
    ("table", [
        ["Aspek", "Sirkuit tertutup", "Ekspirasi saja (terbuka)"],
        ["Mouthpiece dipasang", "Sejak napas tidal, sebelum inspirasi maksimal", "Setelah inspirasi maksimal dari udara ruangan"],
        ["Kurva", "Flow-volume loop lengkap (ekspirasi + inspirasi)", "Hanya sisi ekspirasi"],
        ["FIVC", "Terukur; memvalidasi start dari TLC", "Tidak terukur"],
        ["Penggunaan tipikal", "Laboratorium klinis/diagnostik", "Skrining massal di tempat kerja"],
    ]),
    ("h3", "E. Kalimat coaching yang dianjurkan"),
    ("p", "ATS/ERS 2019 meminta coaching yang bersemangat sepanjang manuver, dengan bahasa tubuh. Contoh kalimat "
          "dalam bahasa Indonesia (padanan frasa ATS):"),
    ("table", [
        ["Fase", "Kalimat operator", "Padanan ATS/ERS 2019"],
        ["Inspirasi", "\"Tarik napas sedalam-dalamnya… terus… terus… penuh!\"", "\"Inspire as deeply as possible\"; \"more, more, more\""],
        ["Awal ekspirasi", "\"TIUP! Ledakkan sekuat tenaga!\"", "\"Blast\" (bukan sekadar \"blow\")"],
        ["Sisa ekspirasi", "\"Terus… terus… dorong… habiskan… jangan berhenti!\"", "\"Keep going\""],
        ["Akhir", "\"Sekarang tarik napas lagi sebanyak-banyaknya!\"", "Inspirasi maksimal setelah EOFE (FIVC)"],
    ]),
    ("h3", "F. Kapan pemeriksaan dihentikan"),
    ("b", "Pasien merasa **nyeri** saat manuver, atau muncul tanda sinkop (pusing, pandangan gelap): hentikan "
          "manuver segera (ATS/ERS 2019)."),
    ("b", "**FEV1 dari manuver acceptable turun di bawah 80% nilai awal** sesi (penurunan progresif tiap manuver, "
          "kemungkinan bronkospasme akibat manuver): hentikan demi keselamatan pasien (ATS/ERS 2019)."),
    ("b", "Setelah **5 kali percobaan** belum ada spirogram yang memenuhi syarat: berhenti sebentar dan pastikan "
          "pasien masih sanggup (Konsensus PERDOKI 2019). Bila kelelahan atau sesak, jadwalkan ulang."),
    ("b", "Sudah **8 manuver** pada dewasa: hentikan walaupun repeatability belum tercapai; kualitas dilaporkan "
          "dengan grade ATS/ERS 2019 (A = ≥3 acceptable dengan selisih ≤150 mL; C = selisih ≤200 mL; D = ≤250 mL; "
          "E = >250 mL atau hanya 1 acceptable; U = hanya usable; F = tidak ada yang acceptable maupun usable)."),
    ("b", "Target tercapai: ≥3 manuver acceptable dan repeatable."),
    ("h3", "G. Dokumentasi dan komentar operator"),
    ("b", "Identitas, TB/BB (dan metode estimasi tinggi bila arm span/ulna), posisi pemeriksaan bila bukan duduk, "
          "suhu, tekanan barometer, kelembaban, tanggal dan jam, nama operator, nama dokter penginterpretasi."),
    ("b", "Obat yang dipakai dan jam terakhir, kepatuhan penahanan obat, gejala saat pemeriksaan, penyimpangan dari "
          "persiapan (mis. merokok 30 menit sebelumnya)."),
    ("b", "Semua manuver acceptable dan usable disimpan (bukan hanya yang terbaik). Grade kualitas FEV1 dan FVC "
          "dilaporkan terpisah."),
    ("b", "Komentar standar, contoh: \"Batuk pada detik ke-3, FEV1 valid\"; \"Tidak mencapai plateau, FET 6 detik, "
          "FVC kemungkinan underestimate\"; \"Usaha maksimal tercapai\"."),
    ("b", "Beri tahu pasien bahwa grade A–F menilai konsistensi tiupan, **bukan** kesehatan parunya."),
    ("pearl", "Di OSCE, sebelum membaca angka, sebutkan dulu bahwa Anda menilai kualitas kurva (acceptable, "
              "repeatable, grade). Penguji menilai urutan berpikir ini."),
]

SVC = [
    ("h2", "4.8 Prosedur Slow Vital Capacity (SVC) dan Inspiratory Capacity (IC)"),
    ("new", "Sumber: ATS/ERS 2019 (VC and Inspiratory Capacity Maneuver), NIOSH 2004, Guideline for Office "
            "Spirometry in Adults 2012, Y. Sim 2017."),
    ("b", "**VC (SVC)** = perubahan volume antara TLC dan RV dengan napas santai, tidak dipaksa (kecuali di ujung "
          "inspirasi dan ekspirasi). Dua cara: **EVC** (ekspirasi lambat TLC → RV) atau **IVC** (inspirasi lambat RV "
          "→ TLC)."),
    ("b", "**IC** = volume dari akhir ekspirasi tidal (FRC) sampai inspirasi maksimal (TLC). IC adalah perkiraan "
          "tidak langsung derajat hiperinflasi saat istirahat."),
    ("p", "**Langkah:**"),
    ("n", "Pasien duduk tegak, rileks, nose clip terpasang, bibir rapat di mouthpiece (alat sirkuit tertutup)."),
    ("n", "Napas tidal sampai volume akhir ekspirasi **stabil**: minimal 3 napas tidal dengan volume akhir ekspirasi "
          "dalam rentang 15% volume tidal. Bila belum stabil setelah 10 napas, VC boleh dilanjutkan tetapi **IC "
          "tidak dilaporkan**."),
    ("n", "Opsi EVC: tarik napas sampai penuh (TLC) tanpa ragu, lalu embuskan perlahan dan rata sampai benar-benar "
          "kosong (RV). Opsi IVC: embuskan perlahan sampai kosong (RV), lalu tarik napas sampai penuh (TLC), lalu "
          "kembali napas biasa."),
    ("n", "Aliran relatif konstan dan santai. Orang sehat mencapai ujung volume dalam 5–6 detik; pada obstruksi "
          "lebih lama, tetapi ekspirasi dihentikan pada 15 detik. Jangan terlalu lambat (VC jadi underestimate)."),
    ("n", "Alat memberi bip ganda saat plateau (<25 mL dalam 1 detik terakhir) atau 15 detik."),
    ("p", "**Kriteria kualitas:** tidak bocor di mulut/hidung, mouthpiece tidak tersumbat, TLC dan RV benar-benar "
          "tercapai. Minimal **3 manuver VC acceptable**, maksimal praktis 8. Repeatability (usia >6 tahun): selisih "
          "VC terbesar dan kedua terbesar **≤150 mL atau ≤10% VC, ambil yang LEBIH KECIL** (berbeda dengan FVC yang "
          "memakai batas tetap 150 mL). Laporkan **VC terbesar**; untuk **IC laporkan rata-rata** manuver acceptable."),
    ("p", "**Urutan: SVC dilakukan SEBELUM FVC** (ATS/ERS 2019), karena (1) manuver paksa melelahkan otot napas, "
          "dan (2) efek riwayat volume: setelah inspirasi dan ekspirasi paksa berulang, pasien obstruksi berat bisa "
          "kembali ke FRC/RV yang tinggi palsu akibat gas trapping atau stress relaxation."),
    ("p", "**Kapan SVC diindikasikan:**"),
    ("b", "Curiga obstruksi (FEV1/FVC rendah atau borderline): ekspirasi paksa menyebabkan kolaps dinamis saluran "
          "napas kecil sehingga FVC < SVC (pada obstruksi berat selisihnya bisa sampai ±1 L, NIOSH 2004)."),
    ("b", "FVC rendah dengan kesan pola campuran: SVC yang jauh lebih besar dari FVC menunjukkan restriksi semu "
          "(pseudo-restriksi akibat air trapping)."),
    ("b", "Menilai hiperinflasi lewat IC, termasuk respons bronkodilator dan efek latihan."),
    ("p", "**Rasio FEV1/VC:** penyebut terbaik untuk mendeteksi obstruksi adalah **VC terbesar** dari FVC, EVC, atau "
          "IVC. Bila FVC mengecil akibat air trapping, FEV1/FVC naik palsu dan obstruksi bisa terlewat; FEV1/VC "
          "lebih sensitif."),
    ("flag", "Konsensus PERDOKI 2019 untuk surveilans rutin tetap memakai KVP, VEP1, dan rasio VEP1/KVP terhadap NNT. "
             "Tidak ada NNT untuk SVC atau IC di sumber Indonesia. Di ujian: sebut FEV1/VC sebagai konsep fisiologis "
             "ATS/ERS, lalu tetap simpulkan dengan kriteria PERDOKI."),
]

GRADING = [
    ("h2", "4.10 Grading Kualitas Sesi A–F dan Konsep \"Usable\" (ATS/ERS 2019)"),
    ("new", "Sumber: ATS/ERS 2019, Tabel 7 dan Tabel 10 (dibaca langsung dari teks penuh di PubMed Central, "
            "PMC6794117)."),
    ("p", "ATS/ERS 2019 membedakan dua tingkat: **acceptable** (memenuhi semua kriteria) dan **usable** (tidak "
          "memenuhi semua kriteria, tetapi nilainya masih bermakna secara klinis, mis. pasien hanya mampu sebatas "
          "itu). FEV1 dan FVC dinilai **terpisah**."),
    ("table", [
        ["Kriteria", "FEV1 acceptable", "FVC acceptable", "FEV1 usable", "FVC usable"],
        ["BEV ≤5% FVC atau ≤100 mL (mana lebih besar)", "Ya", "Ya", "Ya", "Ya"],
        ["Tidak ada bukti zero-flow salah", "Ya", "Ya", "Ya", "Ya"],
        ["Tidak batuk di detik pertama", "Ya", "Tidak", "Ya", "Tidak"],
        ["Tidak ada penutupan glotis di detik pertama", "Ya", "Ya", "Ya", "Ya"],
        ["Tidak ada penutupan glotis setelah 1 detik", "Tidak", "Ya", "Tidak", "Tidak"],
        ["Satu indikator EOFE tercapai*", "Tidak", "Ya", "Tidak", "Tidak"],
        ["Tidak ada sumbatan mouthpiece/alat", "Ya", "Ya", "Tidak", "Tidak"],
        ["Tidak ada kebocoran", "Ya", "Ya", "Tidak", "Tidak"],
        ["FIVC − FVC ≤100 mL atau ≤5% FVC (mana lebih besar)", "Ya", "Ya", "Tidak", "Tidak"],
    ]),
    ("p", "*Indikator EOFE (cukup salah satu): (1) plateau <25 mL dalam 1 detik terakhir; (2) FET ≥15 detik; "
          "(3) pasien tidak mampu ekspirasi cukup lama untuk plateau (mis. restriksi, recoil tinggi), tetapi FVC-nya "
          "sama atau lebih besar dari FVC terbesar sebelumnya dalam batas repeatability."),
    ("p", "**Grading sesi** (diterapkan pada set manuver pra-bronkodilator dan pasca-bronkodilator secara terpisah; "
          "repeatability dihitung dari selisih 2 nilai terbesar):"),
    ("table", [
        ["Grade", "Jumlah pengukuran", "Repeatability usia >6 th", "Repeatability usia ≤6 th"],
        ["A", "≥3 acceptable", "≤150 mL", "≤100 mL*"],
        ["B", "2 acceptable", "≤150 mL", "≤100 mL*"],
        ["C", "≥2 acceptable", "≤200 mL", "≤150 mL*"],
        ["D", "≥2 acceptable", "≤250 mL", "≤200 mL*"],
        ["E", "≥2 acceptable ATAU 1 acceptable", ">250 mL atau tidak berlaku", ">200 mL"],
        ["U", "0 acceptable DAN ≥1 usable", "Tidak berlaku", "Tidak berlaku"],
        ["F", "0 acceptable dan 0 usable", "Tidak berlaku", "Tidak berlaku"],
    ]),
    ("p", "*atau 10% nilai tertinggi, mana yang lebih besar (khusus usia ≤6 tahun)."),
    ("b", "Nilai yang dilaporkan: FVC terbesar dan FEV1 terbesar dari semua nilai acceptable (atau usable bila tidak "
          "ada yang acceptable); rasionya dihitung dari keduanya walaupun berasal dari manuver berbeda."),
    ("b", "Batuk di detik pertama: FEV1 manuver itu tidak acceptable dan tidak usable, tetapi FVC-nya masih bisa "
          "acceptable."),
    ("b", "Penutupan glotis atau berhenti dini setelah detik pertama: FVC tidak acceptable, FEV1 masih bisa "
          "acceptable."),
    ("b", "Grade di bawah A tidak berarti hasil dibuang: interpretasi tetap dilakukan dengan kehati-hatian klinis "
          "yang lebih besar, dan grade disebutkan dalam laporan."),
    ("pearl", "Ini menjawab dilema OSCE \"kurva tidak sempurna\": sebutkan grade-nya (mis. \"FEV1 grade A, FVC grade "
              "C karena selisih 2 FVC terbesar 180 mL\"), lalu tetap interpretasikan dengan catatan. Ini lebih tepat "
              "daripada menolak membaca."),
]
