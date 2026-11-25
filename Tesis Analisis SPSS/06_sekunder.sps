* Encoding: UTF-8.
* =====================================================================.
* 06 SEKUNDER EKSPLORATIF - Tabel 4.8 dan 4.9 (hypothesis-generating).
* =====================================================================.
DATASET ACTIVATE model.

* ----- Tabel 4.8 beda antar-area -----.
* Normal pada kedua area: t-test (Levene p < 0,05 baca baris equal variances not assumed). Selain itu Mann-Whitney.
TITLE 'Tabel 4.8 Beda antar-area'.
EXAMINE VARIABLES=wbgt pm25 tewl h2o2 BY area /PLOT=NPPLOT /STATISTICS=DESCRIPTIVES /NOTOTAL.
MEANS TABLES=wbgt pm25 tewl h2o2 BY area /CELLS=COUNT MEAN STDDEV MEDIAN MIN MAX.
T-TEST GROUPS=area(1 0) /VARIABLES=wbgt pm25 tewl h2o2 /ES DISPLAY(TRUE) /CRITERIA=CI(.95).
NPAR TESTS /M-W=wbgt pm25 tewl h2o2 BY area(0 1).

* ----- Tabel 4.9 interaksi WBGT x PM2.5 terhadap H2O2 -----.
* z-score dihitung pada subjek yang dianalisis. TEWL tidak dimasukkan (bukan model mediasi).
TITLE 'Tabel 4.9 Interaksi'.
DESCRIPTIVES VARIABLES=wbgt(z_wbgt) pm25(z_pm25) /SAVE /STATISTICS=MEAN STDDEV.
COMPUTE z_int = z_wbgt * z_pm25.
EXECUTE.
REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA CHANGE COLLIN TOL
  /DEPENDENT h2o2
  /METHOD=ENTER z_wbgt z_pm25 usia jk imt merokok bk_kkal
  /METHOD=ENTER z_int.
