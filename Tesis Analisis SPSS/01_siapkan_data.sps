* Encoding: UTF-8.
* =====================================================================.
* 01 SIAPKAN DATA - impor, label, cek mutu, variabel turunan.
* Dipanggil dari 00_JALANKAN.sps (FILE HANDLE berkasdata diatur di sana).
* =====================================================================.

GET DATA /TYPE=XLSX /FILE='berkasdata' /SHEET=INDEX 1 /CELLRANGE=FULL /READNAMES=ON
  /DATATYPEMIN PERCENTAGE=95.0 /HIDDEN IGNORE=YES.
DATASET NAME tesis WINDOW=FRONT.

* Sel kosong hasil Paste Values dari Excel dapat terbaca sebagai teks: paksa numerik.
ALTER TYPE kode (A10).
ALTER TYPE hari TO selang (F8.2).

* Hanya subjek yang ikut pemeriksaan (baris kode yang tidak terpakai dibuang).
SELECT IF (RTRIM(kode) NE '' AND ikut = 1).
EXECUTE.

VARIABLE LABELS
  kode 'Kode subjek' /hari 'Hari pengambilan' /shift 'Shift' /ikut 'Ikut pemeriksaan' /analisis 'Dianalisis'
  /area 'Area kerja' /usia 'Usia (tahun)' /jk 'Jenis kelamin' /imt 'IMT (kg/m2)' /masakrj 'Masa kerja (tahun)'
  /brinkman 'Indeks Brinkman' /rokok 'Kategori merokok' /rokok_ak 'Perokok aktif'
  /bk_kkal 'Beban kerja (kkal/jam)' /bk_kat 'Kategori beban kerja'
  /bk_sdg 'Dummy beban kerja sedang' /bk_brt 'Dummy beban kerja berat'
  /wbgt 'WBGT individual (C)' /pm25 'PM2.5 individual (ug/m3, setara-optik)'
  /tewl 'TEWL (g/m2/h)' /h2o2 'H2O2 plasma (mmol/L)'
  /pelembap 'Pelembap lengan 1 minggu' /wetwork 'Kontak air/sabun >=2 jam/hari' /selang 'Akhir shift ke darah (menit)'.
VALUE LABELS
  hari 1 '30 Nov' 2 '2 Des' /shift 1 'Subuh' 2 'Pagi' 3 'Sore'
  /ikut analisis rokok_ak pelembap wetwork bk_sdg bk_brt 0 'Tidak' 1 'Ya'
  /area 1 'Area panas' 0 'Area tidak panas' /jk 1 'Laki-laki' 0 'Perempuan'
  /rokok 0 'Bukan perokok' 1 'Ringan (IB<200)' 2 'Sedang (IB 200-599)' 3 'Berat (IB>=600, eksklusi)'
  /bk_kat 1 'Ringan' 2 'Sedang' 3 'Berat'.
VARIABLE LEVEL usia imt masakrj brinkman bk_kkal wbgt pm25 tewl h2o2 selang (SCALE)
  /hari shift ikut analisis area jk rokok_ak bk_sdg bk_brt pelembap wetwork (NOMINAL) /rokok bk_kat (ORDINAL).
FORMATS hari shift ikut analisis area usia jk rokok rokok_ak bk_kat bk_sdg bk_brt pelembap wetwork selang brinkman (F8.0)
  /imt masakrj bk_kkal pm25 (F8.1) /wbgt tewl h2o2 (F8.2).

* ----- Variabel turunan -----.
* Batas IMT Asia Pasifik; batas berupa < 23 dan < 25 sehingga 22,95 tetap normoweight.
IF (imt < 18.5) imt_kat = 1.
IF (imt >= 18.5 AND imt < 23) imt_kat = 2.
IF (imt >= 23 AND imt < 25) imt_kat = 3.
IF (imt >= 25) imt_kat = 4.
VALUE LABELS imt_kat 1 'Underweight (<18,5)' 2 'Normoweight (18,5-22,9)' 3 'Overweight (23-24,9)' 4 'Obese (>=25)'.
* Kovariat merokok = Indeks Brinkman per 100 (satu prediktor, k tetap 8).
* Bila diputuskan memakai perokok aktif 1/0, ganti baris berikut menjadi COMPUTE merokok = rokok_ak.
COMPUTE merokok = brinkman / 100.
* Transformasi log, hanya dipakai bila asumsi tidak terpenuhi (lihat 03).
IF (tewl > 0) ln_tewl = LN(tewl).
IF (h2o2 > 0) ln_h2o2 = LN(h2o2).
COMPUTE rk_bukan = (rokok = 0).
COMPUTE rk_ring = (rokok = 1).
COMPUTE rk_sdg = (rokok = 2).
COMPUTE bk_ring = (bk_kat = 1).
COMPUTE imt_und = (imt_kat = 1).
COMPUTE imt_nor = (imt_kat = 2).
COMPUTE imt_ovr = (imt_kat = 3).
COMPUTE imt_obs = (imt_kat = 4).
VARIABLE LABELS imt_kat 'Kategori IMT (Asia Pasifik)' /merokok 'Merokok (Brinkman per 100)'
  /ln_tewl 'ln TEWL' /ln_h2o2 'ln H2O2'.
EXECUTE.

* ----- Cek mutu data: harus bersih sebelum lanjut -----.
TITLE '01 Cek mutu data'.
COMPUTE ck_rent = 0.
IF (usia < 18 OR usia > 55) ck_rent = 1.
IF (imt < 14 OR imt > 45) ck_rent = 1.
IF (wbgt < 15 OR wbgt > 40) ck_rent = 1.
IF (pm25 <= 0) ck_rent = 1.
IF (tewl <= 0 OR tewl > 60) ck_rent = 1.
IF (h2o2 <= 0) ck_rent = 1.
IF (selang < 0 OR selang > 180) ck_rent = 1.
* Dianalisis tetapi ada variabel model yang kosong, atau IB >= 600, berarti tidak konsisten.
COMPUTE ck_kons = (analisis = 1 AND NMISS(wbgt,tewl,h2o2,usia,jk,imt,merokok,pm25,bk_kkal,area) > 0).
IF (analisis = 1 AND brinkman >= 600) ck_kons = 1.
SORT CASES BY kode.
MATCH FILES /FILE=* /BY kode /FIRST=brs1 /LAST=brs2.
COMPUTE ck_ganda = (brs1 = 0 OR brs2 = 0).
EXECUTE.
DELETE VARIABLES brs1 brs2.
VARIABLE LABELS ck_rent 'Ada nilai di luar rentang wajar' /ck_kons 'Dianalisis tetapi data tidak lengkap atau IB>=600'
  /ck_ganda 'Kode subjek ganda'.
VALUE LABELS ck_rent ck_kons ck_ganda 0 'Bersih' 1 'PERIKSA'.
FREQUENCIES VARIABLES=analisis ck_rent ck_kons ck_ganda.
TEMPORARY.
SELECT IF (ck_rent = 1 OR ck_kons = 1 OR ck_ganda = 1).
LIST VARIABLES=kode analisis usia imt wbgt pm25 tewl h2o2 selang brinkman.
DESCRIPTIVES VARIABLES=usia imt masakrj brinkman bk_kkal wbgt pm25 tewl h2o2 selang /STATISTICS=MIN MAX MEAN STDDEV.

* Dataset analisis: hanya analisis = 1. Dataset tesis (semua yang ikut) dipakai untuk Tabel 4.1.
DATASET COPY model.
DATASET ACTIVATE model.
SELECT IF (analisis = 1).
EXECUTE.
