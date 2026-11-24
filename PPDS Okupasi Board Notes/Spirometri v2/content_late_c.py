"""Regulations (1.3), questionnaires (8.7), impairment (11.5). Asthma section lives in content_asma."""
from content_asma import ASMA_KERJA  # noqa: F401
from content_reg import REG_REWRITE, REG_ADD  # noqa: F401

KUESIONER = [
    ("h2", "8.7 Kuesioner Gejala Respirasi Standar untuk Surveilans"),
    ("new", "Sumber notebook: Konsensus PERDOKI 2019 dan presentasi Marsen 2024 (form lembar kerja anamnesis), "
            "NIOSH 2004 (Appendix D-1 dan E), Spirometry in Occupational Health 2020 (ACOEM), PPT 06_Chemical Hazard "
            "and RPP. Isi instrumen (ATS-DLD-78, mMRC, Schilling) tidak ada di notebook; diisi dari literatur standar."),
    ("b", "Spirometri surveilans selalu dipasangkan dengan **kuesioner terstruktur**: riwayat merokok (pack-years), "
          "gejala respirasi saat ini (batuk, dahak, mengi, sesak), penyakit paru terdahulu, riwayat pekerjaan dan "
          "pajanan. ACOEM 2020 menganjurkan menelaah kuesioner pra-kerja dan kuesioner berkala bersamaan dengan "
          "evaluasi longitudinal spirometri."),
    ("b", "**ATS-DLD-78** (American Thoracic Society – Division of Lung Diseases): kuesioner epidemiologi baku "
          "untuk batuk kronik, dahak, mengi, sesak, dikaitkan dengan riwayat kerja dan rokok."),
    ("b", "**Skala sesak mMRC/BMRC (0–4)**: 0 sesak hanya saat aktivitas berat; 1 saat jalan cepat di jalan datar "
          "atau mendaki sedikit; 2 berjalan lebih lambat dari sebaya atau harus berhenti di jalan datar dengan "
          "kecepatan sendiri; 3 berhenti setelah ±100 m atau beberapa menit; 4 terlalu sesak untuk keluar rumah "
          "atau sesak saat berpakaian. (Skala ATS 0–4 yang dipakai Permenakertrans 25/2008 untuk derajat sesak "
          "memiliki struktur yang sama.)"),
    ("b", "**Kuesioner bisinosis (klasifikasi Schilling)**, wajib di standar cotton dust OSHA: grade 0 tanpa "
          "keluhan; grade ½ dada berat atau batuk kadang-kadang pada hari pertama kerja; grade 1 dada berat dan/atau "
          "sesak SETIAP hari pertama minggu kerja (Senin); grade 2 dada berat pada hari pertama dan hari kerja lain; "
          "grade 3 gejala grade 2 disertai penurunan fungsi paru menetap (obstruksi kronik)."),
    ("b", "**Kuesioner evaluasi medis respirator OSHA** (29 CFR 1910.134 Appendix C) dipakai sebelum fit test dan "
          "pemakaian respirator."),
    ("pearl", "Pada surveilans sensitizer (mis. isosianat), kuesioner gejala lebih sering menangkap kasus asma kerja "
              "dibanding spirometri tunggal; frekuensi pengulangan lazim tiap 6–12 bulan, paling intensif di 2–3 "
              "tahun pertama pajanan."),
]

KECACATAN = [
    ("h2", "11.5 Penilaian Kecacatan (Impairment) Fungsi Paru"),
    ("new", "Sumber: catatan Kecacatan (AMA + Permenaker) Gabungan milik Anda (AMA Guides 6th Bab 5 dan "
            "Permenakertrans 25/2008 Bidang 7 Paru), Konsensus PERDOKI 2019 (pilar ke-4 tujuan spirometri), "
            "Guideline for Office Spirometry in Adults 2012, Y. Sim 2017, Spirometry in Occupational Health 2020."),
    ("p", "**Prinsip umum:** nilai setelah kondisi menetap (MMI) dengan terapi optimal; gunakan nilai "
          "**pasca-bronkodilator**; singkirkan faktor ekstrapulmoner (obesitas/kelemahan otot menurunkan FVC, "
          "anemia menurunkan DLco). Bila sesak tidak sebanding dengan spirometri yang normal: periksa DLco dan uji "
          "latih kardiopulmonal (CPET)."),
    ("h3", "A. AMA Guides edisi 6 — Bab 5 Paru"),
    ("p", "Key factor = hasil uji objektif; cukup salah satu dari empat parameter memenuhi kelas (kecuali kelas 0, "
          "yang menuntut semua normal termasuk FEV1/FVC > LLN). Rentang WPI per kelas: 1 = 2–10%, 2 = 11–23%, "
          "3 = 24–40%, 4 = 45–65%."),
    ("table", [
        ["Kelas", "FVC (%prediksi)", "FEV1 (%prediksi)", "DLco (%prediksi)", "VO₂max"],
        ["0", "≥80%", "≥80%", "≥75%", ">25 mL/kg/menit (>7,1 METs)"],
        ["1", "70–79%", "65–79%", "65–74%", "22–25"],
        ["2", "60–69%", "55–64%", "55–64%", "18–21"],
        ["3", "50–59%", "45–54%", "45–54%", "15–17"],
        ["4", "<50%", "<45%", "<45%", "<15 (<4,3 METs)"],
    ]),
    ("p", "Contoh: asbestosis dengan FVC 55% → kelas 3 (default grade C). Riwayat dan pemeriksaan fisik sama-sama "
          "kelas 4 → grade naik ke E → 40% WPI (kelas tetap ditentukan hanya oleh key factor)."),
    ("h3", "B. Permenakertrans No. PER.25/MEN/XII/2008 — Bidang 7 Paru"),
    ("table", [
        ["Derajat", "Restriksi (KVP %prediksi)", "Obstruksi (VEP1/KVP% atau %prediksi)"],
        ["Normal", ">80%", ">75%"],
        ["Ringan", "60–79%", "60–74%"],
        ["Sedang", "30–59%", "30–59%"],
        ["Berat", "<30%", "<30%"],
    ]),
    ("table", [
        ["Derajat sesak (skala ATS)", "VEP1", "% cacat fungsi paru"],
        ["0", ">2,5 L", "—"],
        ["1 Ringan", "1,6–2,5 L", "25%"],
        ["2 Sedang", "1,1–1,5 L", "50%"],
        ["3 Berat", "0,5–1 L", "75%"],
        ["4 Sangat berat", "<0,1 L (tertulis demikian di regulasi; kemungkinan maksudnya <0,5 L)", "100%"],
    ]),
    ("b", "Penilaian setelah terapi maksimal (bronkodilator) **3 bulan** dengan hasil menetap."),
    ("b", "Paru = organ dalam: cacat fungsi 100% setara cacat total tetap = **70% upah**. Persentase upah = % cacat "
          "fungsi paru × 70%. Rupiah santunan (PP 44/2015) = persentase upah × 80 × upah sebulan."),
    ("b", "Contoh: pneumokoniosis batubara, VEP1 di rentang 1,6–2,5 L → 25% cacat fungsi → 25% × 70% = 17,5% upah → "
          "17,5% × 80 × upah sebulan. Di Formulir 3B PAK butir 9 dokter menulis \"cacat fungsi pada paru sebesar "
          "25% (dua puluh lima persen)\"; konversi rupiah dihitung BPJS Ketenagakerjaan."),
    ("b", "Contoh berat: asma kerja isosianat, VEP1 0,8 L → 75% cacat fungsi → 52,5% upah → upah Rp 8.000.000 × "
          "0,525 × 80 = **Rp 336.000.000**. Kelaikan: tidak laik di area isosianat; butir 10 Formulir 3B: \"Ringan "
          "dengan kondisi tertentu: tanpa pajanan isosianat\"."),
    ("h3", "C. Pembanding lain di sumber notebook"),
    ("b", "ATS 1991 (NIOSH 2004 Appendix M-1): ringan FEV1 70–99% prediksi; sedang 50–69%; berat ≤50%."),
    ("b", "Guideline SA 2012: untuk keperluan medikolegal, ATS/ERS menyarankan satu penilaian berbasis FEV1 "
          "pasca-bronkodilator."),
    ("b", "Y. Sim 2017 (kriteria disabilitas paru Korea 2015): kelas 1 FEV1 atau DLco ≤25% prediksi (atau PaO₂ "
          "istirahat ≤55 mmHg); kelas 2 >25–30%; kelas 3 >30–40%."),
    ("b", "ACOEM 2020 sengaja tidak menetapkan gradasi kecacatan karena pedoman yang ada saling berbeda; AMA "
          "Guides edisi 6 memakai nilai referensi NHANES III."),
]
