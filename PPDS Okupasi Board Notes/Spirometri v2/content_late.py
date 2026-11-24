"""Corrections, cross-reference replacements, and sections that depend on later NotebookLM answers."""
from content_late_b import (REG_REWRITE, REG_ADD, PREDIKSI, ASMA_KERJA, KUESIONER,  # noqa: F401
                            KECACATAN, UAO, SRC82, CHANGELOG)

KONTRA_KARDIO = (
    "Kardiovaskular (ATS/ERS 2019 Tabel 2): infark miokard akut dalam 1 minggu; hipotensi sistemik atau hipertensi "
    "berat; aritmia atrial/ventrikular bermakna; gagal jantung tak terkompensasi; hipertensi pulmonal tak "
    "terkontrol; kor pulmonal akut; emboli paru tidak stabil; riwayat sinkop terkait ekspirasi paksa/batuk. "
    "Catatan v2: ATS/ERS 2019 TIDAK memberi batas angka untuk \"hipertensi berat\". Angka sistolik >200 atau "
    "diastolik >140 mmHg berasal dari Y. Sim 2017; bila ditanya angka, sebut sumbernya. Angina tidak stabil tetap "
    "layak dianggap kontraindikasi secara klinis walau tidak tercantum di tabel 2019.")

POSISI = (
    "Posisi: ATS/ERS 2019 menganjurkan DUDUK tegak (bahu sedikit ke belakang, dagu sedikit terangkat) di kursi "
    "berlengan tanpa roda demi keselamatan bila sinkop; telapak kaki rata di lantai. Berdiri memberi hasil serupa "
    "dengan duduk pada dewasa, orang obesitas, dan anak; bila berdiri, siapkan kursi di belakang pasien. Posisi "
    "selain duduk harus dicatat di laporan, dan posisi yang sama dipakai pada pemeriksaan ulang (longitudinal).")

LANGKAH2 = (
    "Langkah 2 — Cek FEV1/FVC: bila FEV1/FVC < LLN → obstruksi (ERS/ATS 2022: FEV1 tidak harus < LLN; penyebut "
    "yang dianjurkan FVC, bukan VC seperti anjuran 2005). Bila FEV1/FVC ≥ LLN tetapi FEV1 dan/atau FVC < LLN → PRISm / "
    "pola non-spesifik (perlu TLC untuk membedakan dari restriksi sejati).")

H74 = "7.4 Grading Severity Skema Klasik (Versi Paru Materi Ujian dan ATS/ERS 2005)"

P74 = (
    "Materi ujian board (presentasi Marsen 2024, PPT Ujian Spirometri Tambahan Adit) memakai skema \"versi paru\" "
    "dengan parameter berbeda untuk tiap pola: derajat OBSTRUKSI ditentukan dari angka RASIO AKTUAL VEP1/KVP (bukan "
    "%prediksi), derajat RESTRIKSI dari %PREDIKSI KVP. Konsensus PERDOKI 2019 (versi okupasi, NNT) TIDAK memiliki "
    "gradasi: hasilnya dikotomis normal/abnormal. Pada pola campuran, laporkan kedua derajat terpisah (contoh "
    "presentasi Marsen: rasio 68,07% dan KVP 71,0% prediksi → gangguan obstruksi ringan dan restriksi ringan).")

# first-cell header text in the two original 7.4 tables -> corrected header
T74_HEADER = [
    ("VEP1/KVP (% prediksi)", "Rasio aktual VEP1/KVP (%)"),
    ("KVP (% prediksi)", "KVP (% prediksi)"),
]

T2005 = [
    ("p", "**Skema ATS/ERS 2005 (Pellegrino), 5 tingkat, berbasis %prediksi FEV1 untuk semua pola** (Guideline for "
          "Office Spirometry in Adults 2012 Tabel 7; Y. Sim 2017):"),
    ("table", [
        ["Derajat", "FEV1 % prediksi"],
        ["Ringan (mild)", ">70%"],
        ["Sedang (moderate)", "60–69%"],
        ["Sedang-berat (moderately severe)", "50–59%"],
        ["Berat (severe)", "35–49%"],
        ["Sangat berat (very severe)", "<35%"],
    ]),
    ("table", [
        ["Aspek", "ATS/ERS 2005", "PERDOKI 2019 (versi okupasi)", "Versi paru (materi ujian)"],
        ["Obstruksi bila", "FEV1/VC < LLN", "VEP1/KVP < NNT", "VEP1/KVP < 75%"],
        ["Restriksi bila", "TLC < LLN (spirometri: dugaan bila FVC < LLN)", "KVP < NNT", "KVP < 80% prediksi"],
        ["Gradasi", "5 tingkat, %prediksi FEV1", "Tidak ada", "Obstruksi: rasio 75–60 / 60–30 / <30; "
                                                              "restriksi: %pred KVP 80–60 / 60–30 / <30"],
    ]),
]

P75 = (
    "Skema 2005 lima tingkat berbasis %prediksi FEV1 (ringan >70%, sedang 60–69%, sedang-berat 50–59%, berat "
    "35–49%, sangat berat <35%) sudah digantikan skema z-score tiga tingkat ERS/ATS 2022 (ringan −1,65 s.d. −2,5; "
    "sedang −2,51 s.d. −4,0; berat < −4,1). Kuasai keduanya untuk ujian.")

REVERS = (
    "Interpretasi: respons bronkodilator positif MENDUKUNG asma tetapi tidak memastikannya (ATS/ERS 2019 memakai "
    "istilah \"bronchodilator responsiveness\" justru karena \"reversibilitas\" disalahartikan sebagai hilangnya "
    "obstruksi). PPOK juga bisa menunjukkan respons sebagian, dan asma bisa tidak responsif saat diperiksa. Bila "
    "pasca-BD VEP1/KVP kembali normal → mendukung asma; bila pasca-BD rasio tetap rendah → obstruksi persisten "
    "(PPOK, asma kronik dengan remodeling). Diagnosis tetap butuh klinis, PEF serial, atau uji provokasi.")

P73 = (
    "Standar internasional saat ini merekomendasikan keluarga persamaan Global Lung Function Initiative (GLI-2012) "
    "sebagai referensi multi-etnis global, dengan kategori etnis: Kaukasia, Afrika-Amerika, Asia Timur Laut, Asia "
    "Tenggara, dan lainnya/campuran. Untuk pekerja Indonesia, kategori GLI yang paling mendekati adalah Asia "
    "Tenggara. Isu Indonesia: memakai nilai prediksi Kaukasia tanpa penyesuaian mendistorsi interpretasi pekerja "
    "lokal; Konsensus PERDOKI 2019 memakai nilai prediksi Pneumobile Project Indonesia dengan NNT (dikotomis, tanpa "
    "gradasi), berbeda dari LLN persentil ke-5 GLI.")

LAFAZ_NOTE = ("fix", "Teks Konsensus PERDOKI 2019 sendiri berbunyi \"3 hasil yang dapat diterima dan dua di antaranya "
              "reprodusibel (perbedaan KVP tidak melebihi 150 mL)\"; ATS/ERS 2019 juga hanya memakai 150 mL (FVC dan "
              "FEV1, usia >6 tahun). Frasa \"atau 5%\" berasal dari draf lafaz/cheat sheet dan standar historis (ATS "
              "1987). Lafazkan \"selisih dua nilai terbesar tidak melebihi 150 mL\"; bila penguji menyinggung 5%, "
              "jelaskan asal historisnya.")

# (paragraph start, old substring, new substring)
XREF = [
    ("Kedua artefak di atas penting dibedakan",
     "sehingga bisa jadi jebakan gambar kurva di OSCE (lihat Bagian 13.8).",
     "sehingga sering dipakai sebagai jebakan gambar kurva di OSCE: over-recording dan extra breath tampak seperti "
     "obstruksi, sedangkan under-recording justru menyembunyikan obstruksi."),
    ("Interpretasi: gunakan LLN persentil ke-5",
     " (lihat Bagian 7.2).",
     ". Contoh: LLN rasio FEV1/FVC ±74% pada usia 20 tahun tetapi ±64% pada usia 70 tahun, sehingga cut-off tetap "
     "70% menyebabkan underdiagnosis pada pekerja muda dan overdiagnosis pada pekerja senior."),
    ("Kriteria signifikansi dan contoh substitusi lengkap",
     "Kriteria signifikansi dan contoh substitusi lengkap: lihat Bagian 8.2.",
     "Kriteria (NIOSH/ACOEM): <10% = variabilitas biologis; 10–15% = waspada; ≥15% = abnormal/eksesif. Contoh: "
     "baseline 3,30/3,65 = 90,4% prediksi, sekarang 2,55/3,55 = 71,8% prediksi → penurunan 18,6 poin → eksesif."),
    ("Detail protokol & bias suhu ambien",
     "Detail protokol & bias suhu ambien: lihat Bagian 8.5.",
     "Protokol: pre-shift sebelum mulai kerja, post-shift setelah ≥6 jam terpajan, dengan alat, operator, posisi, "
     "dan suhu ruang yang sama. Bias suhu: ruangan pagi yang lebih dingin dapat memalsukan penurunan FEV1 sampai "
     "±4% bila koreksi BTPS tidak tepat, jadi suhu ruang harus dijaga konstan."),
    ("Klasifikasi pola gangguan ventilasi ditentukan",
     "— lihat matriks lengkap dan cutoff numerik di Bagian 7.8–7.9)",
     "; versi paru: obstruksi bila VEP1/KVP <75%, restriksi bila KVP <80% prediksi; versi okupasi: obstruksi bila "
     "VEP1/KVP < NNT, restriksi bila KVP < NNT; keduanya terganggu = obstruksi dan restriksi; keduanya normal = "
     "fungsi paru normal)"),
    ("Rumus %ΔFEV1 (2005 vs 2022)",
     "Rumus %ΔFEV1 (2005 vs 2022): lihat Bagian 5.4.",
     "Rumus 2005: %ΔFEV1 = (Post-BD − Pre-BD) / Pre-BD × 100%, positif bila ≥12% DAN ≥200 mL. Rumus 2022: "
     "%Δ = (Post-BD − Pre-BD) / nilai prediksi × 100%, positif bila >10% untuk FEV1 atau FVC, tanpa syarat volume."),
    ("Versi Okupasi menggunakan NNT",
     "Rumus NNT: lihat Bagian 5.3.",
     "Rumus NNT = nilai prediksi − 1,64 × SD populasi referensi; praktisnya (PERDOKI): pria KVP prediksi − 673 mL, "
     "VEP1 prediksi − 642 mL, VEP1/KVP prediksi − 10%; wanita KVP − 499 mL, VEP1 − 447 mL, VEP1/KVP − 9%."),
    ("Rumus & contoh substitusi lengkap",
     "Rumus & contoh substitusi lengkap: lihat Bagian 5.6.",
     "Rumus: LNL = (0,85 × nilai baseline) − (prediksi saat baseline − prediksi saat ini). Contoh: baseline FEV1 "
     "3,24 L → 0,85 × 3,24 = 2,754 L; aging effect 3,31 − 3,15 = 0,16 L; LNL = 2,594 ≈ 2,60 L; FEV1 sekarang 2,58 L "
     "< LNL → penurunan signifikan."),
    ("Perhatikan dua kriteria cross-shift",
     "(OSHA Cotton Dust vs materi tambahan, lihat Tabel di Bagian 5.7)",
     "(OSHA Cotton Dust: FEV1 turun ≥5%; Konsensus PERDOKI 2019: VEP1 turun >10% atau APE turun >20%)"),
    ("⚠️ CATATAN SUMBER: Seluruh isi Bagian 9 ini", "Seluruh isi Bagian 9 ini", "Seluruh isi bagian ini"),
    ("Tentukan Peranan Faktor Lain di Luar Pekerjaan",
     "(lihat diagnosis banding non-okupasional di Bagian 9)",
     "(diagnosis banding non-okupasional: pola obstruktif → asma atopik, PPOK akibat rokok, bronkiektasis, "
     "obstruksi saluran napas besar/tumor/benda asing; pola restriktif → IPF/ILD idiopatik, pneumonia, efusi "
     "pleura, kardiomegali/tumor mediastinum, deformitas dinding dada, obesitas/asites/kehamilan, penyakit "
     "neuromuskular)"),
    ("Respirator adalah alat untuk melindungi",
     "(Dasar hukum lengkap: lihat Bagian 12.1.)",
     "(Dasar hukum: OSHA 29 CFR 1910.134 — program perlindungan pernapasan tertulis dengan fit testing, dikelola "
     "Program Administrator yang kompeten.)"),
    ("Eks-pekerja yang sudah pensiun",
     ", lihat vignette Kasus 8 di Bagian 13.10)",
     ")"),
    ("Durasi 1 jam (vs OSCE",
     "Tulis diagnosis 7 langkah okupasi (Bagian 10)",
     "Tulis diagnosis 7 langkah okupasi (diagnosis klinis → pajanan di tempat kerja → hubungan pajanan-penyakit → "
     "besar pajanan → faktor individu → faktor di luar pekerjaan → diagnosis PAK/bukan PAK)"),
    ("4. Interpretasi Pola & Derajat",
     "(Tabel Bagian 7.4)",
     "(skema versi paru: rasio VEP1/KVP 75–60% ringan, 60–30% sedang, <30% berat)"),
    ("Pertanyaan: (a) Interpretasi spirometri (Versi Paru DAN Versi Okupasi). (b) Apa diagnosis terintegrasi",
     " (lihat Bagian 12.5)", ""),
]
