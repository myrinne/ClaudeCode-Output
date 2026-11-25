* Encoding: UTF-8.
* 07 CADANGAN - TIDAK dijalankan otomatis. Blok (select) satu perintah lalu Run Selection.
* Jalankan 00_JALANKAN lebih dulu.
DATASET ACTIVATE model.

* (a) TEWL H2O2 dengan dua dummy beban kerja. Gagal bila kategori Berat kosong atau sangat sedikit (bootstrap singular).
PROCESS y=h2o2/x=wbgt/m=tewl/cov=usia jk imt merokok pm25 bk_sdg bk_brt/model=4/total=1/stand=1/boot=5000/seed=20261130/conf=95.

* (b) Heteroskedastisitas: HC3.
PROCESS y=h2o2/x=wbgt/m=tewl/cov=usia jk imt merokok pm25 bk_kkal/model=4/total=1/hc=3/boot=5000/seed=20261130/conf=95.

* (c) Log H2O2.
PROCESS y=ln_h2o2/x=wbgt/m=tewl/cov=usia jk imt merokok pm25 bk_kkal/model=4/total=1/boot=5000/seed=20261130/conf=95.

* (d) Log TEWL.
PROCESS y=h2o2/x=wbgt/m=ln_tewl/cov=usia jk imt merokok pm25 bk_kkal/model=4/total=1/boot=5000/seed=20261130/conf=95.

* (e) VIF >= 10: tanpa PM2.5 (3.7.4 butir 3).
PROCESS y=h2o2/x=wbgt/m=tewl/cov=usia jk imt merokok bk_kkal/model=4/total=1/stand=1/boot=5000/seed=20261130/conf=95.

* (f) SMD pelembap atau wetwork > 0,25: model lampiran.
PROCESS y=h2o2/x=wbgt/m=tewl/cov=usia jk imt merokok pm25 bk_kkal pelembap wetwork/model=4/total=1/boot=5000/seed=20261130/conf=95.
