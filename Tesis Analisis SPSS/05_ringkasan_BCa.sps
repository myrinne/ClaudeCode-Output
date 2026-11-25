* Encoding: UTF-8.
* =====================================================================.
* 05 RINGKASAN - Tabel 4.6 (satu blok per model), change-in-estimate (4.9), dan IK BCa.
* OLS + bootstrap kasus 5.000 kali, dihitung di MATRIX tanpa macro Hayes.
* Koefisien harus SAMA dengan keluaran 04; batas bootstrap sedikit berbeda (sampel ulang berbeda).
* BCa: z0 = koreksi bias; percepatan dari jackknife (Efron).
* =====================================================================.
DEFINE !MED (nama=!TOKENS(1) /y=!TOKENS(1) /x=!TOKENS(1) /m=!TOKENS(1) /cov=!CMDEND)
MATRIX.
GET D /FILE=* /VARIABLES=!y !x !m !cov /MISSING=OMIT.
COMPUTE n=NROW(D).
COMPUTE p=NCOL(D).
COMPUTE bt=5000.
COMPUTE satu=MAKE(n,1,1).
COMPUTE Y=D(:,1).
COMPUTE M=D(:,3).
DO IF (p > 3).
+  COMPUTE C=D(:,4:p).
+  COMPUTE XA={satu,D(:,2),C}.
+  COMPUTE XB={satu,D(:,2),M,C}.
ELSE.
+  COMPUTE XA={satu,D(:,2)}.
+  COMPUTE XB={satu,D(:,2),M}.
END IF.
COMPUTE ka=NCOL(XA).
COMPUTE kb=NCOL(XB).
* --- estimasi titik ---.
COMPUTE IA=INV(T(XA)*XA).
COMPUTE IB=INV(T(XB)*XB).
COMPUTE ba=IA*T(XA)*M.
COMPUTE bc=IA*T(XA)*Y.
COMPUTE bb=IB*T(XB)*Y.
COMPUTE sa=SQRT(CSSQ(M-XA*ba)/(n-ka)*IA(2,2)).
COMPUTE sc=SQRT(CSSQ(Y-XA*bc)/(n-ka)*IA(2,2)).
COMPUTE s2=CSSQ(Y-XB*bb)/(n-kb).
COMPUTE scp=SQRT(s2*IB(2,2)).
COMPUTE sb=SQRT(s2*IB(3,3)).
COMPUTE est={ba(2);bb(3);bb(2);bc(2)}.
COMPUTE se={sa;sb;scp;sc}.
COMPUTE df={n-ka;n-kb;n-kb;n-ka}.
* t kritis 0,975 dengan bagi dua (MATRIX tidak menyediakan fungsi inversnya).
COMPUTE tk=MAKE(4,1,0).
LOOP j=1 TO 4.
+  COMPUTE lo=1.
+  COMPUTE hi=20.
+  LOOP it=1 TO 60.
+    COMPUTE mid=(lo+hi)/2.
+    DO IF (TCDF(mid,df(j)) < .975).
+      COMPUTE lo=mid.
+    ELSE.
+      COMPUTE hi=mid.
+    END IF.
+  END LOOP.
+  COMPUTE tk(j)=mid.
END LOOP.
COMPUTE pv=MAKE(4,1,0).
LOOP j=1 TO 4.
+  COMPUTE pv(j)=2*(1-TCDF(ABS(est(j)/se(j)),df(j))).
END LOOP.
COMPUTE ab=ba(2)*bb(3).
* --- bootstrap ---.
COMPUTE bs=MAKE(bt,1,0).
LOOP i=1 TO bt.
+  COMPUTE idx=TRUNC(UNIFORM(n,1)*n)+1.
+  COMPUTE wt=MAKE(n,1,0).
+  LOOP j=1 TO n.
+    COMPUTE wt(idx(j))=wt(idx(j))+1.
+  END LOOP.
+  COMPUTE TA=T(XA &* (wt*MAKE(1,ka,1))).
+  COMPUTE TB=T(XB &* (wt*MAKE(1,kb,1))).
+  COMPUTE q1=INV(TA*XA)*TA*M.
+  COMPUTE q2=INV(TB*XB)*TB*Y.
+  COMPUTE bs(i)=q1(2)*q2(3).
END LOOP.
COMPUTE srt=bs.
COMPUTE srt(GRADE(bs))=bs.
COMPUTE bse=SQRT(CSSQ(bs-CSUM(bs)/bt)/(bt-1)).
* --- jackknife ---.
COMPUTE jk=MAKE(n,1,0).
LOOP i=1 TO n.
+  COMPUTE wt=MAKE(n,1,1).
+  COMPUTE wt(i)=0.
+  COMPUTE TA=T(XA &* (wt*MAKE(1,ka,1))).
+  COMPUTE TB=T(XB &* (wt*MAKE(1,kb,1))).
+  COMPUTE q1=INV(TA*XA)*TA*M.
+  COMPUTE q2=INV(TB*XB)*TB*Y.
+  COMPUTE jk(i)=q1(2)*q2(3).
END LOOP.
COMPUTE dj=CSUM(jk)/n-jk.
COMPUTE acc=CSUM(dj&**3)/(6*(CSSQ(dj)**1.5)).
COMPUTE pr=CSUM(bs < ab)/bt.
* z0 = probit(pr) dengan bagi dua.
COMPUTE lo=-8.
COMPUTE hi=8.
LOOP it=1 TO 80.
+  COMPUTE z0=(lo+hi)/2.
+  DO IF (CDFNORM(z0) < pr).
+    COMPUTE lo=z0.
+  ELSE.
+    COMPUTE hi=z0.
+  END IF.
END LOOP.
COMPUTE z=1.959964.
COMPUTE pl={.025,CDFNORM(2*z0-z),CDFNORM(z0+(z0-z)/(1-acc*(z0-z)))}.
COMPUTE pu={.975,CDFNORM(2*z0+z),CDFNORM(z0+(z0+z)/(1-acc*(z0+z)))}.
COMPUTE ci=MAKE(3,2,0).
LOOP j=1 TO 3.
+  COMPUTE ci(j,1)=srt(RMAX({1,TRUNC(pl(j)*bt)})).
+  COMPUTE ci(j,2)=srt(RMIN({bt,TRUNC(pu(j)*bt)+1})).
END LOOP.
COMPUTE sdx=SQRT(CSSQ(D(:,2)-CSUM(D(:,2))/n)/(n-1)).
COMPUTE sdy=SQRT(CSSQ(Y-CSUM(Y)/n)/(n-1)).
* --- cetak ---.
PRINT n /TITLE=!QUOTE(!CONCAT('===== ',!nama,' : n =')) /FORMAT=F8.0.
PRINT {est,se,est-tk&*se,est+tk&*se,est&/se,df,pv} /TITLE='Jalur (B tidak terstandar, IK95%)' /RNAMES={'a';'b';'c_aksen';'c_total'}
  /CNAMES={'B','SE','LLCI','ULCI','t','df','p'} /FORMAT=F11.4.
PRINT {ab,bse,ci(1,1),ci(1,2);ab,bse,ci(2,1),ci(2,2);ab,bse,ci(3,1),ci(3,2)}
  /TITLE='Efek tidak langsung a x b, bootstrap 5000' /RNAMES={'persent';'BC';'BCa'}
  /CNAMES={'ab','BootSE','BootLLCI','BootULCI'} /FORMAT=F11.4.
PRINT {ab*sdx/sdy,100*ab/bc(2),z0,acc} /TITLE='ab terstandar penuh; proporsi termediasi % (hanya bila searah dan c tidak mendekati 0); z0; percepatan'
  /CNAMES={'ab_cs','PM_%','z0','acc'} /FORMAT=F11.4.
END MATRIX.
!ENDDEFINE.

DATASET ACTIVATE model.
SET SEED=20261130.
SET MXLOOPS=100000.
TITLE '05 Ringkasan Tabel 4.6'.
!MED nama=Model_1 y=h2o2 x=wbgt m=tewl cov=.
!MED nama=Model_2 y=h2o2 x=wbgt m=tewl cov=usia jk imt merokok pm25.
!MED nama=Model_3 y=h2o2 x=wbgt m=tewl cov=usia jk imt merokok pm25 bk_kkal.

* Change-in-estimate 4.9: (B Model 1 - B Model 3) / B Model 3 x 100%, dihitung dari a dan c_total di atas.
