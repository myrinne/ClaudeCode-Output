"""3D (gas dan korosif) and 3E (debu dan serat) sections. Every list is filtered by which md files exist,
so the document can be rebuilt at any stage."""
import os
from docx.shared import Pt, Cm
import mdconv as M
from extras import para, bullets, callout

GAS = [
    ("3D.1 Sianida (HCN, NaCN/KCN)", "d01_Sianida"),
    ("3D.2 Hidrogen sulfida (H2S)", "d02_H2S"),
    ("3D.3 Karbon monoksida (CO)", "d03_CO"),
    ("3D.4 Karbon dioksida (CO2)", "d04_CO2"),
    ("3D.5 Amonia (NH3, NH4OH)", "d05_Amonia"),
    ("3D.6 Klorin (Cl2)", "d06_Klorin"),
    ("3D.7 Fosgen (COCl2)", "d07_Fosgen"),
    ("3D.8 Nitrogen dioksida / NOx", "d08_NOx"),
    ("3D.9 Sulfur dioksida (SO2)", "d09_SO2"),
    ("3D.10 Iodin", "d10_Iodin"),
    ("3D.11 Nitrit dan nitrat", "d11_NitritNitrat"),
    ("3D.12 Korosif kuat: H2SO4, HCl, HNO3, NaOH", "d12_KorosifKuat"),
    ("3D.13 Asam fluorida (HF)", "d13_HF"),
    ("3D.14 Asam asetat", "d14_AsamAsetat"),
    ("3D.15 Fenol", "d15_Fenol"),
]
DUST = [
    ("3E.1 Silika kristalin (silikosis, silikotuberkulosis)", "e01_Silika"),
    ("3E.2 Asbes (asbestosis, plak pleura, mesotelioma; Kriteria Helsinki)", "e02_Asbes"),
    ("3E.3 Debu batubara (CWP, PMF)", "e03_Batubara"),
    ("3E.4 Debu kayu (karsinoma sinonasal)", "e04_Kayu"),
    ("3E.5 Debu kapas (bisinosis)", "e05_Kapas"),
]


def _present(items, folder):
    return [(t, f) for t, f in items if os.path.exists(os.path.join(folder, f + ".md"))]


def _sections(doc, items, read, find_img, add_img, folder, imgdir, prefix):
    for title, f in _present(items, folder):
        doc.add_page_break()
        doc.add_heading(title, level=2)
        M.render(doc, read(folder, f), h_off=1)
        num = int(title.split(" ", 1)[0].split(".")[1])
        ip = find_img(imgdir, "%s.%02d_" % (prefix, num))
        if ip:
            add_img(doc, ip, title.split(" ", 1)[1])


def build_3d(doc, read, find_img, add_img, folder, imgdir):
    doc.add_page_break()
    doc.add_heading("3D. GAS DAN KOROSIF: TEMPLATE PER ZAT", level=1)
    para(doc, "Penomoran mengikuti urutan terbaru dari Vidya: **3D = gas dan korosif** (outline lama: 3E gas, 3F korosif) dan **3E = debu dan serat** (outline lama: 3D). Struktur sama dengan 3A sampai 3C: tabel 13 poin, pearl dan jebakan ujian (poin 14), dan satu infografik per zat. Untuk **iritan dan korosif**, poin 3 diganti **mekanisme cedera dan toksikokinetik** (nekrosis likuefaksi vs koagulatif, kelarutan air, lokasi deposisi) dan tatalaksana menekankan dekontaminasi, irigasi, dan larangan emesis/netralisasi. Sumber: notebook NotebookLM \"Toxicology - Gases and Corrosives\"; untuk **amonia dan klorin** notebook tidak punya sumber sendiri, sehingga ditambahkan ATSDR Toxicological Profile for Ammonia (tp126), Medical Management Guidelines Ammonia, dan ATSDR Toxicological Profile for Chlorine (tp172). Arsin dibahas di 3A.3 (arsen) dan fosfin di 3C.6.", size=10)
    M.add_table(doc, [
        ["Subkategori", "Zat pada catatan ini"],
        ["Asfiksian kimia", "Sianida (HCN, NaCN), H2S, karbon monoksida"],
        ["Asfiksian sederhana", "Karbon dioksida"],
        ["Iritan paru", "Amonia, klorin, fosgen, NO2/NOx, SO2"],
        ["Lain", "Iodin, nitrit/nitrat"],
        ["Korosif kuat", "H2SO4, HCl, HNO3, NaOH; asam fluorida (HF)"],
        ["Korosif lemah", "Amonia/NH4OH (3D.5), asam asetat, fenol"],
    ], font=9, widths=[4.5, 12.3])
    callout(doc,
            "**Jebakan lintas gas dan korosif.** (1) **Penolong tanpa SCBA adalah korban berikutnya** (H2S, CO2, sianida, klorin, amonia). (2) **Bau bukan alat deteksi:** H2S dan amonia melumpuhkan penciuman (olfactory fatigue), sianida tidak tercium pada 20 sampai 40% orang, CO tidak berbau. "
            "(3) **SpO2 normal pada sianida dan CO (palsu).** (4) **Gas berat (H2S, klorin, CO2) mengendap di bawah:** uji atmosfer berlapis dan evakuasi ke tempat tinggi. (5) **Iritan: foto toraks awal normal, edema paru tertunda 12 sampai 48 jam:** observasi 24 sampai 48 jam. "
            "(6) **Korosif: irigasi air banyak, jangan netralisasi, jangan induksi muntah.**",
            fill="FDE9D9")
    _sections(doc, GAS, read, find_img, add_img, folder, imgdir, "3D")


def build_3e(doc, read, find_img, add_img, folder, imgdir):
    doc.add_page_break()
    doc.add_heading("3E. DEBU DAN SERAT: TEMPLATE PER AGEN", level=1)
    para(doc, "Struktur sama dengan zat lain, disesuaikan untuk debu dan serat: poin 3 = **deposisi dan klirens partikel/serat**, poin 5 = **diagnosis dan pemantauan** (radiologi ILO, HRCT, faal paru, patologi), poin 10 = BEI/IPB (umumnya tidak ada), poin 11 = tatalaksana (tidak ada terapi kuratif), dan poin 12 = **kelaikan kerja, surveilans, dan pengendalian** (hierarki kontrol). Kolom antidotum pada quick table diganti **diagnosis dan pengendalian**. Sumber: notebook NotebookLM \"Toxicology - Dust and Fiber\" (32 sumber). Klasifikasi ILO (outline: sesi #8), berilium, dan hard metal dibahas di bagian lain (3A.8, 3A.9) dan catatan ILO terpisah.", size=10)
    callout(doc,
            "**Jebakan lintas debu.** (1) **Spirometri dan foto toraks normal tidak menyingkirkan pneumokoniosis awal;** DLCO dan HRCT lebih sensitif. (2) **Penyakit berlanjut setelah pajanan berhenti.** (3) **Tidak ada BEI/IPB untuk debu/serat.** "
            "(4) **Latensi puluhan tahun vs batas klaim JKK 3 tahun setelah hubungan kerja berakhir (Perpres 7/2019 Pasal 2 ayat 2).** (5) **Silika zona atas, opasitas bulat (p, q, r); asbes zona bawah, opasitas ireguler (s, t, u).**",
            fill="FDE9D9")
    _sections(doc, DUST, read, find_img, add_img, folder, imgdir, "3E")


QT_3D = {
    "d01_Sianida": ["**Sianida**", "Kolaps, koma, kejang, laktat > 8, SpO2 normal, vena merah cerah", "Sianida darah > 1 mg/L; laktat ≥ 8 mmol/L; tiosianat urin (B, Ns)", "**Hidroksokobalamin 5 g IV;** alternatif nitrit 300 mg + tiosulfat 12,5 g; asap kebakaran: tanpa nitrit"],
    "d02_H2S": ["**H2S**", "Knockdown, paralisis olfaktori > 100 sampai 150 ppm, gas eye, edema paru", "Tiosulfat urin (riset); tidak ada BEI; sulfHb bukan penanda", "O2 100%, penolong SCBA; nitrit sangat dini (kontroversial); tiosulfat tidak berguna; HBO"],
    "d03_CO": ["**Karbon monoksida**", "Sakit kepala, sinkop, koma; DNS 2 sampai 40 hari; kulit merah ceri hanya post-mortem", "COHb 3,5% (IPB, akhir shift); CO napas 20 ppm; SpO2 dan PaO2 normal palsu", "O2 100% NRB sampai COHb < 3%; **HBO** bila sinkop, neuro, iskemia, COHb > 25%, hamil > 15 sampai 20%"],
    "d04_CO2": ["**Karbon dioksida**", "Hiperpnea, sakit kepala, kejang, knockdown > 25%; toksikan sistemik > 10%", "PaCO2 > 60 dan pH < 7,2 (AGD); tidak ada IPB", "SCBA, O2 + ventilasi mekanis (washout); hindari bikarbonat agresif; tanpa HBO"],
    "d05_Amonia": ["**Amonia**", "Luka bakar mata/saluran napas, edema laring menit, edema paru 12 sampai 48 jam; RADS", "Tidak ada biomarker/IPB; AGD, spirometri, laringoskopi, slit-lamp", "Irigasi masif (mata sampai pH netral); O2 lembab; **intubasi dini; JANGAN netralisasi asam**"],
    "d06_Klorin": ["**Klorin**", "Batuk, bronkospasme, nyeri dada; edema paru puncak 12 sampai 24 jam; RADS", "Tidak ada biomarker/IPB; spirometri, AGD, foto serial", "O2 lembab, salbutamol, nebulisasi bikarbonat (bukti terbatas), steroid dini, intubasi dini, observasi 24 sampai 48 jam"],
    "d07_Fosgen": ["**Fosgen**", "Iritasi ringan lalu laten 6 sampai 24 jam, edema paru; bronkiolitis obliterans", "Tidak ada biomarker/IPB", "Istirahat total, observasi 24 sampai 48 jam, O2, steroid; hindari tekanan positif berlebih"],
    "d08_NOx": ["**NO2 / NOx**", "Laten 3 sampai 30 jam lalu edema paru; bronkiolitis obliterans 2 sampai 6 minggu (silo filler)", "Tidak ada biomarker/IPB; Met-Hb pada NOx tinggi", "O2, steroid, observasi; kelaikan dan ventilasi silo"],
    "d09_SO2": ["**SO2**", "Bronkospasme, asma tereksaserbasi, RADS", "Tidak ada biomarker/IPB", "Bronkodilator, O2, irigasi mata"],
    "d10_Iodin": ["**Iodin**", "Iritasi mata, saluran napas; hipertiroid/hipotiroid", "Iodium urin; fungsi tiroid", "Irigasi, suportif; tiosulfat topikal"],
    "d11_NitritNitrat": ["**Nitrit / nitrat**", "Methemoglobinemia, sianosis cokelat, hipotensi", "Met-Hb (co-oksimetri)", "**Biru metilen 1 sampai 2 mg/kg;** O2"],
    "d12_KorosifKuat": ["**Korosif kuat (asam/basa)**", "Luka bakar kimia kulit/mata/saluran cerna; asam: koagulatif; basa: likuefaksi", "Tidak ada biomarker; pH irigasi, endoskopi", "Irigasi air banyak; tanpa netralisasi, tanpa emesis"],
    "d13_HF": ["**Asam fluorida**", "Nyeri hebat tidak sebanding, hipokalsemia, hipomagnesemia, aritmia", "Ca, Mg, EKG; fluorida", "**Kalsium glukonat** topikal/intradermal/intra-arteri/IV; koreksi Mg"],
    "d14_AsamAsetat": ["**Asam asetat**", "Luka bakar kimia (konsentrat), iritasi", "Tidak ada biomarker", "Irigasi, suportif"],
    "d15_Fenol": ["**Fenol**", "Luka bakar putih, absorpsi kulit sistemik: SSP, aritmia, gagal ginjal", "Fenol total urin", "Dekontaminasi PEG 300/400 atau air banyak; suportif"],
}
QT_3E = {
    "e01_Silika": ["**Silika**", "Sesak, batuk; nodul zona atas; PMF; TB, kanker, autoimun", "Tidak ada BEI; foto ILO (p, q, r), HRCT, DLCO, IGRA", "Hentikan pajanan; LTBI/OAT 8 sampai 9 bulan; WLL (akut); transplantasi; pengendalian basah/LEV/respirator"],
    "e02_Asbes": ["**Asbes**", "Asbestosis basal, plak pleura, BAPE, mesotelioma, kanker paru", "Tidak ada BEI; ILO (s, t, u), HRCT prone, DLCO, AB/serat paru (Helsinki)", "Hentikan pajanan; stop rokok; onkologi (platinum + pemetreksed, nivolumab + ipilimumab); abatement HEPA"],
    "e03_Batubara": ["**Debu batubara**", "CWP simpleks, PMF, Caplan, bronkitis, emfisema", "Tidak ada BEI; foto ILO, spirometri", "Hentikan pajanan; suportif; kontrol debu"],
    "e04_Kayu": ["**Debu kayu**", "Rinitis, asma, karsinoma sinonasal (adenokarsinoma)", "Tidak ada BEI; nasoendoskopi", "Hentikan pajanan; onkologi; LEV"],
    "e05_Kapas": ["**Debu kapas**", "Bisinosis: dada sesak hari Senin", "Tidak ada BEI; FEV1 pra/pasca shift", "Hentikan pajanan; bronkodilator; kontrol debu"],
}


def _qt(doc, title, tag, rows_map, items, folder, last_col):
    present = [f for _, f in _present(items, folder)]
    rows = [["Zat", "Gejala kunci", "Biomarker / diagnosis", last_col]] + [rows_map[f] for f in present if f in rows_map]
    doc.add_heading(title, level=1)
    para(doc, "Kolom: zat | gejala kunci | biomarker/diagnosis | %s." % last_col.lower(), size=9.5, italic=True)
    M.add_table(doc, rows, font=8, widths=[2.4, 4.9, 5.3, 4.2])


def quick_table_3d(doc):
    # SHORT3D is resolved by caller path layout (same folder as this module)
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "short3d")
    _qt(doc, "5D. QUICK TABLE AKHIR (3D. GAS DAN KOROSIF)", "3D", QT_3D, GAS, folder, "Antidotum / terapi")


def quick_table_3e(doc):
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "short3e")
    _qt(doc, "5E. QUICK TABLE AKHIR (3E. DEBU DAN SERAT)", "3E", QT_3E, DUST, folder, "Diagnosis dan pengendalian")


OSCE_3D = [
    "**Sianida:** \"Hidroksokobalamin 5 g IV dalam 15 menit adalah lini pertama, terutama pada asap kebakaran karena nitrit memperburuk hipoksia bila ada CO; SpO2 normal dan laktat di atas 8 dengan SvO2 tinggi adalah kunci.\"",
    "**H2S:** \"Bau telur busuk hilang pada lebih dari 100 sampai 150 ppm karena paralisis olfaktori; penolong wajib SCBA, beri O2 100%, nitrit hanya sangat dini dan kontroversial, dan tiosulfat tidak berguna.\"",
    "**CO:** \"SpO2 dan PaO2 normal tidak menyingkirkan CO; berikan O2 100% sampai COHb di bawah 3% dan HBO bila sinkop, defisit neurologis, iskemia miokard, COHb di atas 25%, atau hamil dengan COHb di atas 15 sampai 20%.\"",
    "**CO2:** \"CO2 di atas 10% adalah toksikan sistemik walau O2 normal; gunakan detektor NDIR dan uji atmosfer tiga tingkat, tangani dengan ventilasi mekanis, bukan HBO.\"",
    "**Amonia:** \"Edema laring dalam menit dan edema paru tertunda; irigasi mata sampai pH netral, intubasi dini, dan jangan menetralkan dengan asam.\"",
    "**Klorin:** \"Daya larut sedang merusak saluran napas atas dan bawah; observasi 24 sampai 48 jam, evakuasi ke tempat tinggi tegak lurus angin, dan pencampuran pemutih dengan asam melepas Cl2.\"",
]
OSCE_3E = [
    "**Silika:** \"DLCO dan HRCT mendeteksi silikosis awal saat spirometri dan foto masih normal; tidak ada BEI, skrining TB dengan IGRA, dan pekerja ditarik dari pajanan.\"",
    "**Asbes:** \"Plak pleura adalah penanda pajanan, bukan asbestosis; Helsinki 10^6 serat amfibol per gram menghasilkan 33 sampai 45% negatif palsu sehingga usulan 600 badan asbes atau 300.000 serat dipertimbangkan, dan batas klaim JKK 3 tahun tidak sesuai latensi.\"",
]


def penutup_3d(doc):
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "short3d")
    have = {f for _, f in _present(GAS, folder)}
    doc.add_heading("6.8 Lafaz OSCE: satu kalimat per zat (3D)", level=2)
    for t, f in zip(OSCE_3D, ["d01_Sianida", "d02_H2S", "d03_CO", "d04_CO2", "d05_Amonia", "d06_Klorin"]):
        if f in have:
            bullets(doc, [t])
    doc.add_heading("6.9 Vignette MCQ (3D)", level=2)
    para(doc, "Skenario fiktif untuk latihan.", size=9.5, italic=True)
    V = [
        ("Vignette 12 (Sianida)",
         "Pemadam kebakaran 35 tahun keluar dari gedung terbakar dengan koma, TDS 70, SpO2 99%, laktat 11 mmol/L, COHb 12%. Antidot yang paling tepat?",
         ["A. Natrium nitrit 300 mg IV", "B. Hidroksokobalamin 5 g IV dengan O2 100%", "C. Biru metilen", "D. Atropin", "E. Tiosulfat saja"],
         "B. Asap kebakaran (HCN + CO): hidroksokobalamin; nitrit membentuk MetHb dan memperburuk hipoksia bersama COHb."),
        ("Vignette 13 (H2S)",
         "Pekerja IPAL kolaps di dalam manhole; rekannya langsung turun menolong. Respons pertama yang benar sebelum menolong?",
         ["A. Masuk cepat tanpa alat", "B. Bunyikan alarm, kenakan SCBA bertekanan positif, siapkan lifeline/ventilasi", "C. Gunakan masker N95", "D. Tutup hidung dan masuk", "E. Tunggu bau hilang"],
         "B. 25 sampai 40% kematian H2S adalah penolong tanpa SCBA; bau hilang justru tanda paralisis olfaktori."),
        ("Vignette 14 (Klorin)",
         "Petugas kebersihan 30 tahun mencampur pemutih dan pembersih kloset di kamar mandi tertutup, batuk dan mengi. Foto toraks normal, SpO2 95% setelah salbutamol. Tindakan paling tepat?",
         ["A. Pulang tanpa observasi", "B. Observasi 24 sampai 48 jam karena edema paru dapat tertunda 12 sampai 24 jam", "C. Cairan IV agresif", "D. Netralisasi dengan asam", "E. Antibiotik profilaksis"],
         "B. Edema paru klorin memuncak 12 sampai 24 jam; foto awal sering normal; hindari kelebihan cairan."),
    ]
    for title, stem, opts, ans in V:
        para(doc, "**" + title + "**", after=2)
        para(doc, stem, after=2)
        for o in opts:
            para(doc, o, after=0).paragraph_format.left_indent = Cm(0.8)
        para(doc, "**Jawaban:** " + ans, size=9.5, after=8)


def penutup_3e(doc):
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "short3e")
    have = {f for _, f in _present(DUST, folder)}
    doc.add_heading("6.10 Lafaz OSCE: satu kalimat per agen (3E)", level=2)
    for t, f in zip(OSCE_3E, ["e01_Silika", "e02_Asbes"]):
        if f in have:
            bullets(doc, [t])
    doc.add_heading("6.11 Vignette MCQ (3E)", level=2)
    para(doc, "Skenario fiktif untuk latihan.", size=9.5, italic=True)
    V = [
        ("Vignette 15 (Silika)",
         "Pemotong meja batu buatan 42 tahun, sesak ringan; spirometri normal, foto toraks normal; DLCO 62% prediksi. Langkah paling tepat?",
         ["A. Singkirkan silikosis karena foto normal", "B. HRCT toraks dan skrining IGRA; tarik dari pajanan bila konfirmasi", "C. Kortikosteroid jangka panjang", "D. BEI silika urin", "E. Lanjut bekerja dengan N95"],
         "B. DLCO dan HRCT lebih sensitif; 53,4% spirometri normal saat diagnosis; tidak ada BEI; skrining TB wajib."),
        ("Vignette 16 (Asbes)",
         "Mantan pekerja galangan kapal 68 tahun, plak pleura kalsifikasi bilateral, faal paru normal, tanpa fibrosis parenkim. Pernyataan yang benar?",
         ["A. Asbestosis", "B. Plak pleura adalah penanda pajanan, bukan asbestosis dan bukan prakanker", "C. Pasti mesotelioma", "D. BEI asbes urin positif", "E. Steroid sistemik"],
         "B. Asbestosis = fibrosis parenkim difus basal; plak pleura tidak menurunkan faal paru; surveilans seumur hidup."),
    ]
    for title, stem, opts, ans in V:
        para(doc, "**" + title + "**", after=2)
        para(doc, stem, after=2)
        for o in opts:
            para(doc, o, after=0).paragraph_format.left_indent = Cm(0.8)
        para(doc, "**Jawaban:** " + ans, size=9.5, after=8)


def quality_extra_3d(doc):
    bullets(doc, [
        "**3D, amonia dan klorin:** notebook tidak punya sumber sendiri; dijawab dengan tambahan ATSDR ToxProfile (tp126, tp172) dan MMG amonia; nomor butir Perpres 7/2019 (I.a, II.b, I.a butir 11) dan nilai evakuasi belum diverifikasi ke lampiran.",
        "**3D, batas pajanan:** NAB Permenaker 5/2018 CO 25 ppm, H2S 1 ppm (PSD 5), CO2 5.000 ppm (PSD 30.000), NH3 25 ppm (PSD 35), Cl2 0,5 ppm (PSD 1), HCN ceiling 4,7 ppm dari NotebookLM; cek ulang Lampiran 3.",
        "**3D, bukti terbatas:** nebulisasi natrium bikarbonat untuk klorin (laporan kasus), natrium nitrit untuk H2S (kontroversial), steroid dini untuk iritan paru.",
        "**3D, nomor butir Perpres 7/2019:** sianida, H2S, CO, CO2 = Lampiran I.a butir 16 menurut NotebookLM; cek ulang.",
    ], size=10)


def quality_extra_3e(doc):
    bullets(doc, [
        "**3E, penomoran:** 3E (debu dan serat) mengikuti urutan terbaru Vidya; outline lama menempatkan debu sebagai 3D.",
        "**3E, batas pajanan:** ACGIH silika respirabel 0,025 mg/m3 dan asbes 0,1 serat/cm3; nilai Permenaker 5/2018 (silika 0,025; tridimit 0,05) dari NotebookLM, cek ulang Lampiran 3.",
        "**3E, Perpres 7/2019:** silikosis dan siliko-TB (Lampiran II.a butir 1 dan 2), kanker asbes (Lampiran III butir 1): nomor butir belum diverifikasi.",
        "**3E, Kepmenaker 03/MEN/1985** (larangan krosidolit) dan status larangan parsial asbes di Indonesia berasal dari NotebookLM; cek ulang.",
    ], size=10)
