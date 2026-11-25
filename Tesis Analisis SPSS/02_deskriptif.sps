* Encoding: UTF-8.
* =====================================================================.
* 02 DESKRIPTIF - Tabel 4.1, 4.3, 4.4, 4.5.
* =====================================================================.

* Macro SMD = |m1-m0| / akar((v1+v0)/2). Kontinu v = varians; dikotomi 0/1 v = p(1-p).
* Rumus sama dengan sheet 7_Tabel1_SMD, jadi hasilnya dapat dicocokkan.
DEFINE !SMD (grup=!TOKENS(1) /var=!CMDEND)
MATRIX.
GET X /FILE=* /VARIABLES=!var /NAMES=VN /MISSING=ACCEPT /SYSMIS=-99999.
GET G /FILE=* /VARIABLES=!grup /MISSING=ACCEPT /SYSMIS=-99999.
COMPUTE hasil=MAKE(NCOL(X),7,0).
LOOP j=1 TO NCOL(X).
+  COMPUTE ok1=(X(:,j) <> -99999) &* (G = 1).
+  COMPUTE ok0=(X(:,j) <> -99999) &* (G = 0).
+  COMPUTE n1=CSUM(ok1).
+  COMPUTE n0=CSUM(ok0).
+  DO IF (n1 > 1 AND n0 > 1).
+    COMPUTE m1=CSUM(X(:,j) &* ok1)/n1.
+    COMPUTE m0=CSUM(X(:,j) &* ok0)/n0.
+    COMPUTE v1=CSUM(((X(:,j)-m1)&**2) &* ok1)/(n1-1).
+    COMPUTE v0=CSUM(((X(:,j)-m0)&**2) &* ok0)/(n0-1).
+    COMPUTE biner=CSUM((X(:,j)=0) &* (ok1+ok0)) + CSUM((X(:,j)=1) &* (ok1+ok0)).
+    DO IF (biner = n1+n0).
+      COMPUTE v1=m1*(1-m1).
+      COMPUTE v0=m0*(1-m0).
+    END IF.
+    COMPUTE s=0.
+    DO IF (v1+v0 > 0).
+      COMPUTE s=ABS(m1-m0)/SQRT((v1+v0)/2).
+    END IF.
+    COMPUTE hasil(j,:)={n1,m1,SQRT(v1),n0,m0,SQRT(v0),s}.
+  END IF.
END LOOP.
PRINT hasil /TITLE='SMD grup 1 vs grup 0 (variabel biner: rerata = proporsi). SMD <= 0.25 = seimbang'
  /CNAMES={'n_1','rerata_1','SD_1','n_0','rerata_0','SD_0','SMD'} /RNAMES=VN /FORMAT=F10.3.
END MATRIX.
!ENDDEFINE.

* ----- Tabel 4.1 atrisi: dianalisis (1) vs tidak dianalisis (0), di antara yang ikut -----.
TITLE 'Tabel 4.1 Atrisi'.
DATASET ACTIVATE tesis.
FREQUENCIES VARIABLES=analisis.
MEANS TABLES=usia imt masakrj BY analisis /CELLS=COUNT MEAN STDDEV MEDIAN MIN MAX.
CROSSTABS /TABLES=jk area BY analisis /CELLS=COUNT COLUMN.
!SMD grup=analisis var=usia imt masakrj jk area.

* ----- Tabel 4.3 karakteristik per area (hanya yang dianalisis) -----.
TITLE 'Tabel 4.3 Karakteristik dan keseimbangan'.
DATASET ACTIVATE model.
MEANS TABLES=usia imt masakrj brinkman bk_kkal selang BY area /CELLS=COUNT MEAN STDDEV MEDIAN MIN MAX.
CROSSTABS /TABLES=imt_kat rokok bk_kat jk pelembap wetwork shift BY area /CELLS=COUNT COLUMN.
EXAMINE VARIABLES=usia imt masakrj brinkman BY area /PLOT=NPPLOT /STATISTICS=NONE /NOTOTAL.
!SMD grup=area var=usia imt imt_und imt_nor imt_ovr imt_obs masakrj rk_bukan rk_ring rk_sdg brinkman
  bk_kkal bk_ring bk_sdg bk_brt jk pelembap wetwork.

* ----- Tabel 4.4 pajanan, mediator, luaran + normalitas -----.
* n > 50: baca kolom Kolmogorov-Smirnov (koreksi Lilliefors). n <= 50: baca Shapiro-Wilk.
* Nilai sig 0.200 berarti p >= 0.200 (batas bawah yang dilaporkan SPSS).
TITLE 'Tabel 4.4 Pajanan, mediator, luaran'.
FREQUENCIES VARIABLES=wbgt pm25 tewl h2o2 selang /FORMAT=NOTABLE /STATISTICS=MEAN STDDEV MEDIAN MINIMUM MAXIMUM SKEWNESS.
EXAMINE VARIABLES=wbgt pm25 tewl h2o2 /PLOT=NPPLOT HISTOGRAM /COMPARE GROUPS /STATISTICS=DESCRIPTIVES /CINTERVAL 95.

* ----- Tabel 4.5 korelasi (deskriptif) -----.
* Pearson bila kedua variabel normal, selain itu Spearman.
TITLE 'Tabel 4.5 Korelasi'.
CORRELATIONS /VARIABLES=wbgt pm25 tewl h2o2 usia imt /PRINT=TWOTAIL NOSIG /MISSING=LISTWISE.
NONPAR CORR /VARIABLES=wbgt pm25 tewl h2o2 usia imt /PRINT=SPEARMAN TWOTAIL NOSIG /MISSING=LISTWISE.
