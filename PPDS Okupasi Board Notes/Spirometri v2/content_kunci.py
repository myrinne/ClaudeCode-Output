"""13.11 Kunci jawaban Bank Kasus OSCE (8 skenario). Self-contained per case."""

KUNCI = [
    ("h2", "13.11 Kunci Jawaban Bank Kasus OSCE (Kasus 1–8)"),
    ("new", "Disusun di v2 dari data kasus masing-masing. Hitungan memakai rumus yang dipakai di catatan ini "
            "(%penurunan, LNL, reversibilitas 2005 dan 2022, NNT). Coba kerjakan sendiri dulu dengan timer 10 menit "
            "sebelum membaca kunci."),
    ("h3", "Kunci Kasus 1 — Penambang Batubara Sangatta"),
    ("b", "Kualitas: data kurva tidak diberikan; di ujian tetap lafazkan acceptable (5 kriteria) dan reproducible "
          "(selisih 2 KVP dan 2 VEP1 terbesar ≤150 mL)."),
    ("b", "**Versi Paru:** VEP1/KVP 80% ≥75% → tidak ada obstruksi; KVP 81% prediksi ≥80% → tidak ada restriksi. "
          "Kesimpulan versi paru: **fungsi paru normal**."),
    ("b", "**Versi Okupasi:** VEP1/KVP 80% ≥ NNT 71% → tidak ada obstruksi; KVP 3.100 mL < NNT 3.140 mL → **ada "
          "restriksi**. Kesimpulan versi okupasi: **gangguan fungsi paru restriksi**."),
    ("b", "**Kesimpulan akhir:** sebut kedua hasil, lalu pilih versi okupasi karena tujuan surveilans pekerja "
          "terpajan menuntut sensitivitas tinggi. Sebut sebagai **pola restriksi** (perlu konfirmasi TLC)."),
    ("b", "Temuan tambahan yang harus disebut: IMT = 51 / (1,72)² = **17,2 kg/m² (berat badan kurang)**. Massa "
          "otot napas yang rendah dapat ikut menurunkan KVP, jadi masuk faktor individu (langkah 5)."),
    ("b", "**Rekomendasi perorangan:** foto toraks dengan klasifikasi ILO (curiga pneumokoniosis batubara/CWP); "
          "spirometri ulang dengan kualitas optimal; rujuk Sp.P untuk TLC dan DLCO; evaluasi gizi; penilaian laik "
          "kerja sesuai hasil ILO."),
    ("b", "**Rekomendasi komunitas:** pengukuran debu respirabel batubara dibanding NAB Permenaker 5/2018; "
          "pengendalian teknis (penyiraman, ventilasi, kabin tertutup); evaluasi program perlindungan pernapasan "
          "(fit test); surveilans spirometri dan ILO untuk pekerja se-area."),
    ("h3", "Kunci Kasus 2 — Perbandingan Antar Waktu Penambang Batubara"),
    ("b", "**%Penurunan VEP1** = (2.400 − 2.200) / 2.400 × 100% = 200 / 2.400 × 100% = **8,3%**."),
    ("b", "**%Penurunan KVP** = (3.100 − 3.000) / 3.100 × 100% = 100 / 3.100 × 100% = **3,2%**."),
    ("b", "Laju penurunan VEP1 = 200 mL / 3 tahun = **67 mL/tahun** (belum >90 mL/tahun). Penurunan fisiologis "
          "akibat usia laki-laki ±30 mL/tahun × 3 = 90 mL, jadi kelebihan penurunan ±110 mL."),
    ("b", "**Interpretasi dengan kriteria jangka panjang PERDOKI** (penurunan VEP1 atau KVP antar dua pemeriksaan ≥8%): "
          "VEP1 turun 8,3% → **signifikan**; KVP 3,2% → tidak signifikan. Dengan kriteria NIOSH/ACOEM (≥15%) belum "
          "eksesif. Sebut kriteria yang dipakai."),
    ("b", "**Langkah selanjutnya:** pastikan kedua tes berkualitas baik (alat, operator, suhu ruang, nilai prediksi "
          "sama); ulangi spirometri; anamnesis gejala dan rokok; foto toraks ILO; hitung LNL bila data ≥3 tahun "
          "tersedia lengkap dengan nilai prediksi; evaluasi pajanan dan APD; percepat interval surveilans (6 bulan)."),
    ("h3", "Kunci Kasus 3 — Welder Galangan Surabaya"),
    ("b", "**Versi Paru:** VEP1/KVP 57,1% <75% → **obstruksi**; KVP 81% ≥80% → tidak ada restriksi. Derajat dengan "
          "skema rasio VEP1/KVP (75–60% ringan, 60–30% sedang, <30% berat): 57,1% → **obstruksi sedang**. "
          "(Pembanding ATS/ERS 2005 dengan %prediksi VEP1 57,6% → sedang-berat, 50–59%.)"),
    ("b", "**Versi Okupasi:** VEP1/KVP 57,1% < NNT 71% → obstruksi; KVP 2.310 ≥ NNT 2.170 → tidak ada restriksi. "
          "Kesimpulan: **gangguan obstruksi**."),
    ("b", "**Riwayat rokok:** 1 bungkus/hari dari usia 18 sampai 51 = 33 tahun × 1 = **33 pack-years**."),
    ("b", "**Diagnosis banding:** PPOK akibat rokok murni vs PPOK dengan kontribusi pajanan kerja (welding fume: "
          "partikel logam, NOx, ozon; 22 tahun) vs asma (perlu uji bronkodilator). Pajanan kerja dan rokok bisa "
          "bersifat aditif; pajanan kerja bisa ditetapkan sebagai faktor kontributor bermakna walau ada rokok."),
    ("b", "**Rujukan dan investigasi:** uji bronkodilator; rujuk Sp.P (DLCO, HRCT bila perlu); foto toraks (siderosis "
          "pada welder biasanya tidak bermakna secara fungsi); riwayat pekerjaan rinci (ruang tertutup, ventilasi "
          "lokal, jenis elektroda: stainless → kromium/nikel); berhenti merokok."),
    ("b", "**Komunitas:** LEV (local exhaust ventilation) pada stasiun las, terutama ruang tertutup kapal; "
          "pengukuran fume; respirator yang sesuai dan fit test; surveilans spirometri rekan kerja."),
    ("h3", "Kunci Kasus 4 — Sandblaster Batam Pre-Post Shift"),
    ("b", "**%Penurunan VEP1** = (3.500 − 3.480) / 3.500 × 100% = 20 / 3.500 × 100% = **0,6%**."),
    ("b", "**%Penurunan APE** = (480 − 470) / 480 × 100% = 10 / 480 × 100% = **2,1%**."),
    ("b", "**Kriteria jangka pendek:** VEP1 turun >10% atau APE >20% (materi PERDOKI); OSHA cotton dust ≥5%. "
          "Keduanya jauh di bawah ambang → **tidak signifikan**."),
    ("b", "**Apakah pajanan aman?** Tidak bisa disimpulkan. Hazard utama sandblasting adalah **silika kristalin "
          "respirabel** yang efeknya kronik (silikosis, PPOK, kanker paru, peningkatan risiko TB), bukan "
          "bronkokonstriksi akut. Pre-post shift yang negatif tidak menyingkirkan efek kronik."),
    ("b", "**Tindak lanjut:** spirometri longitudinal (bandingkan dengan baseline, LNL); foto toraks ILO berkala; "
          "skrining TB; pengukuran debu silika respirabel; substitusi abrasif non-silika (eliminasi/substitusi "
          "adalah kontrol tertinggi); blasting cabinet atau ventilasi; respirator supplied-air untuk abrasive "
          "blasting; RPP lengkap."),
    ("h3", "Kunci Kasus 5 — Pekerja Tekstil Cotton Dust Senin Pagi"),
    ("b", "**%Penurunan VEP1** = (2.800 − 2.380) / 2.800 × 100% = 420 / 2.800 × 100% = **15%**."),
    ("b", "**%Penurunan APE** = (420 − 320) / 420 × 100% = 100 / 420 × 100% = **23,8%**."),
    ("b", "Keduanya melewati ambang (VEP1 >10%, APE >20%; juga ≥5% menurut OSHA cotton dust) → **signifikan, efek "
          "akut pajanan**."),
    ("b", "**Diagnosis tentatif:** **bisinosis** (byssinosis): dada terasa berat/sesak pada hari pertama kembali "
          "bekerja setelah libur (Monday chest tightness) pada pekerja bagian carding pabrik kapas, disertai "
          "penurunan VEP1 sepanjang shift."),
    ("b", "**Mengapa Senin pagi?** Gejala dan penurunan fungsi paling nyata pada hari pertama setelah bebas pajanan "
          "(akhir pekan). Dengan pajanan harian berikutnya terjadi toleransi sementara sehingga gejala berkurang di "
          "hari-hari berikutnya; pemeriksaan Senin memaksimalkan peluang menangkap respons akut. Pada tahap lanjut "
          "gejala menetap setiap hari dan bisa terjadi obstruksi kronik."),
    ("b", "**Rekomendasi perorangan:** konfirmasi dengan PEF serial; uji bronkodilator; rujuk Sp.P; pertimbangkan "
          "pindah dari area carding bila penurunan menetap atau ada obstruksi kronik; penilaian laik kerja dengan "
          "pembatasan pajanan."),
    ("b", "**Rekomendasi komunitas:** pengukuran debu kapas; ventilasi lokal di mesin carding/blowing; pembasahan "
          "atau pencucian kapas; respirator partikulat dengan fit test; pre-post shift spirometri untuk pekerja "
          "se-bagian (surveilans gaya standar cotton dust)."),
    ("h3", "Kunci Kasus 6 — Hitung LNL Pekerja Smelter Nikel Morowali"),
    ("b", "**Rumus:** LNL = (0,85 × VEP1 baseline) − (prediksi VEP1 saat baseline − prediksi VEP1 saat ini)."),
    ("b", "**Substitusi:** variabilitas = 0,85 × 3.200 = 2.720 mL; aging effect = 3.400 − 3.250 = 150 mL; "
          "LNL = 2.720 − 150 = **2.570 mL**."),
    ("b", "**Hasil:** VEP1 terbaru 2.500 mL < LNL 2.570 mL → **penurunan longitudinal signifikan**."),
    ("b", "**%Penurunan VEP1 2020–2025** = (3.200 − 2.500) / 3.200 × 100% = 700 / 3.200 × 100% = **21,9%** "
          "(≥8%, signifikan). Laju = 700 / 5 = **140 mL/tahun** (>90 mL/tahun). Metode %prediksi: 3.200/3.400 = "
          "94,1% → 2.500/3.250 = 76,9%; selisih **17,2 poin** (≥15%, eksesif menurut NIOSH/ACOEM). Semua metode "
          "konsisten."),
    ("b", "**Arti untuk pekerja:** penurunan jauh melebihi penuaan; telusuri pajanan smelter (SO₂, debu/fume "
          "nikel termasuk nikel sulfat yang bisa menyebabkan asma kerja, panas), gejala yang berhubungan dengan "
          "kerja, rokok. Langkah: verifikasi kualitas tes, uji bronkodilator, PEF serial bila curiga asma, rujuk "
          "Sp.P, evaluasi APD dan pengendalian pajanan, interval surveilans dipersingkat, pertimbangkan pembatasan "
          "atau pemindahan sementara."),
    ("h3", "Kunci Kasus 7 — Asma Okupasi pada Pengecatan Industri (Isosianat)"),
    ("b", "**Pre-BD versi paru:** VEP1/KVP 66,7% <75% → obstruksi; KVP 95% ≥80% → tidak ada restriksi. Derajat "
          "skema rasio: 66,7% → **obstruksi ringan** (75–60%). Pembanding ATS/ERS 2005: VEP1 72% prediksi → ringan "
          "(>70%)."),
    ("b", "**Reversibilitas 2005:** ΔVEP1 = 3.200 − 2.800 = 400 mL; %Δ = 400 / 2.800 × 100% = **14,3%** → ≥12% "
          "dan ≥200 mL → **positif**."),
    ("b", "**Reversibilitas 2022 (% prediksi):** prediksi VEP1 = 2.800 / 0,72 = 3.889 mL; %Δ = 400 / 3.889 × 100% "
          "= **10,3%** → >10% → **positif**. KVP: prediksi = 4.200 / 0,95 = 4.421 mL; Δ 100 mL = 2,3% (tidak "
          "bermakna). Pasca-BD: VEP1/KVP = 3.200 / 4.300 = 74,4%; VEP1 = 82% prediksi."),
    ("b", "**Diagnosis kerja:** **asma akibat kerja (tipe sensitizer, dengan masa laten) akibat toluene "
          "diisocyanate**: obstruksi reversibel, gejala memburuk di tempat kerja dan membaik di akhir pekan. "
          "Konfirmasi dengan PEF serial periode kerja vs libur dan, bila tersedia, uji provokasi spesifik."),
    ("b", "**Rekomendasi khusus isosianat:** **hentikan pajanan sepenuhnya** (pindah tugas permanen dari area "
          "isosianat). Pada asma sensitizer, pajanan sangat kecil pun bisa mencetuskan serangan, sehingga respirator "
          "saja tidak cukup. Tata laksana asma oleh Sp.P. Komunitas: substitusi dengan cat bebas isosianat, spray"
          "booth dengan ventilasi, respirator supplied-air untuk penyemprotan, surveilans gejala dan spirometri "
          "rekan kerja, edukasi. Laporkan sebagai dugaan PAK."),
    ("h3", "Kunci Kasus 8 — Pekerja Asbes-Semen dengan Asbestosis Lanjut"),
    ("b", "**Versi Paru:** VEP1/KVP 83% ≥75% → tidak ada obstruksi; KVP 64% <80% → **restriksi**. Derajat skema "
          "KVP %prediksi (80–60% ringan): 64% → **restriksi ringan**. (Pembanding ATS/ERS 2005: VEP1 66% → sedang, "
          "60–69%.)"),
    ("b", "**Versi Okupasi:** VEP1/KVP 83% ≥ NNT 71% → tidak ada obstruksi; KVP 2.400 < NNT 3.077 → **restriksi**."),
    ("b", "**Diagnosis terintegrasi:** pola restriksi + small irregular opacities s/t profusi 1/1 di lobus bawah "
          "bilateral + plak pleura berkalsifikasi bilateral + riwayat 30 tahun pabrik asbes-semen tanpa rokok → "
          "**asbestosis dengan penyakit pleura akibat asbes**. Konfirmasi: TLC (restriksi sejati), DLCO (biasanya "
          "turun), HRCT."),
    ("b", "**Hak klaim JKK:** PAK dapat timbul bertahun-tahun setelah pajanan berakhir. Pekerja yang hubungan "
          "kerjanya sudah berakhir tetap dapat mengajukan manfaat JKK untuk PAK bila penyakit didiagnosis dalam "
          "jangka waktu yang ditetapkan PP 44/2015 (seingat saya paling lama 3 tahun sejak hubungan kerja berakhir; "
          "verifikasi pasalnya). Pada kasus ini pensiun 3 tahun lalu, sehingga **batas waktu menjadi poin kritis**: "
          "segera tegakkan diagnosis PAK dengan 7 langkah dan proses pelaporan."),
    ("b", "**Surveilans seumur hidup eks-pekerja asbes:** gejala dan spirometri/DLCO berkala, foto toraks ILO "
          "berkala, kewaspadaan mesotelioma dan kanker paru (laten 20–40 tahun), berhenti merokok tetap ditekankan "
          "karena rokok dan asbes bersinergi terhadap kanker paru, vaksinasi influenza dan pneumokokus, serta "
          "pelacakan rekan kerja seangkatan."),
]
