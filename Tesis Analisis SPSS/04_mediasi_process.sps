* Encoding: UTF-8.
* =====================================================================.
* 04 MEDIASI - macro Hayes v5.1 Model 4, Tabel 4.6 dan 4.7.
* PENTING: jangan menulis nama macro di baris komentar, SPSS tetap menjalankannya.
* Bootstrap bawaan = percentile. Opsi bc=1 = bias-corrected, bukan BCa (BCa ada di 05).
* Homoskedastisitas: baca Breusch-Pagan baris Robust pada Model 3; p < 0,05 pakai HC3 di 07.
* =====================================================================.
DATASET ACTIVATE model.

* ----- Model 1: tanpa penyesuaian (sekaligus bivariat jalur a dan c) -----.
TITLE 'Model 1 Unadjusted'.
PROCESS y=h2o2/x=wbgt/m=tewl/model=4/total=1/stand=1/boot=5000/seed=20261130/conf=95.

* ----- Model 2: usia, JK, IMT, rokok, PM2.5 -----.
TITLE 'Model 2'.
PROCESS y=h2o2/x=wbgt/m=tewl/cov=usia jk imt merokok pm25/model=4/total=1/stand=1/boot=5000/seed=20261130/conf=95.

* ----- Model 3 UTAMA: Model 2 + beban kerja (kkal/jam, kontinu) -----.
TITLE 'Model 3 Utama'.
PROCESS y=h2o2/x=wbgt/m=tewl/cov=usia jk imt merokok pm25 bk_kkal/model=4/total=1/stand=1/diagnose=1/boot=5000/seed=20261130/conf=95.

