* Encoding: UTF-8.
* =====================================================================.
* 03 ASUMSI - VIF (4.6) dan asumsi regresi (4.7). Dibaca SEBELUM 04.
* =====================================================================.
DATASET ACTIVATE model.

* ----- VIF dan residual, Model 3 (utama) -----.
* Aturan 3.7.4: VIF WBGT dan PM2.5 < 5 pertahankan; 5-10 pertajam pembobotan zona; >= 10 fokus WBGT.
* Persamaan M (TEWL).
TITLE '03 Persamaan TEWL Model 3'.
REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA COLLIN TOL
  /DEPENDENT tewl
  /METHOD=ENTER wbgt usia jk imt merokok pm25 bk_kkal
  /PARTIALPLOT ALL
  /SCATTERPLOT=(*ZRESID ,*ZPRED)
  /RESIDUALS HISTOGRAM(ZRESID) NORMPROB(ZRESID)
  /CASEWISE PLOT(SRESID) OUTLIERS(3)
  /SAVE RESID(res_m) COOK(cook_m).
* Persamaan Y langsung (H2O2, memuat TEWL).
TITLE '03 Persamaan H2O2 Model 3'.
REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA COLLIN TOL
  /DEPENDENT h2o2
  /METHOD=ENTER wbgt tewl usia jk imt merokok pm25 bk_kkal
  /PARTIALPLOT ALL
  /SCATTERPLOT=(*ZRESID ,*ZPRED)
  /RESIDUALS HISTOGRAM(ZRESID) NORMPROB(ZRESID)
  /CASEWISE PLOT(SRESID) OUTLIERS(3)
  /SAVE RESID(res_y) COOK(cook_y).
* Persamaan Y total (jalur c).
TITLE '03 Persamaan efek total Model 3'.
REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA COLLIN TOL
  /DEPENDENT h2o2
  /METHOD=ENTER wbgt usia jk imt merokok pm25 bk_kkal
  /SCATTERPLOT=(*ZRESID ,*ZPRED)
  /RESIDUALS NORMPROB(ZRESID)
  /SAVE RESID(res_t).

* ----- Normalitas residual -----.
TITLE '03 Normalitas residual'.
EXAMINE VARIABLES=res_m res_y res_t /PLOT=NPPLOT /STATISTICS=DESCRIPTIVES.

* Homoskedastisitas: Breusch-Pagan (baris Robust) ada di keluaran Model 3 berkas 04.
* Satu uji saja; uji MBP bawaan UNIANOVA memakai nilai prediksi (df 1) dan dapat berbeda kesimpulan.

* ----- Linearitas -----.
TITLE '03 Linearitas'.
GRAPH /SCATTERPLOT(BIVAR)=wbgt WITH tewl.
GRAPH /SCATTERPLOT(BIVAR)=wbgt WITH h2o2.
GRAPH /SCATTERPLOT(BIVAR)=tewl WITH h2o2.

* Subjek dengan Cook > 4/n: periksa ulang entri datanya, jangan dibuang otomatis.
TITLE '03 Subjek berpengaruh'.
AGGREGATE /OUTFILE=* MODE=ADDVARIABLES /n_mod=N.
TEMPORARY.
SELECT IF (cook_m > 4/n_mod OR cook_y > 4/n_mod).
LIST VARIABLES=kode wbgt tewl h2o2 res_m res_y cook_m cook_y.
