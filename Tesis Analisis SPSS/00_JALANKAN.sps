* Encoding: UTF-8.
* =====================================================================.
* TESIS WBGT - TEWL - H2O2. Buka berkas ini, lalu Run > All.
* Yang diganti saat data asli masuk HANYA baris berkasdata.
* =====================================================================.
SET DECIMAL=DOT /TNUMBERS=BOTH /TVARS=BOTH /PRINTBACK=OFF /MPRINT=OFF.

FILE HANDLE folder /NAME='C:\Users\vidya\OneDrive\Documents\PPDS Okupasi\Usulan Thesis\Gizi\Analisis SPSS'.
FILE HANDLE berkasdata /NAME='C:\Users\vidya\OneDrive\Documents\PPDS Okupasi\Usulan Thesis\Gizi\Analisis SPSS\Data\SIMULASI_A_mediasi.xlsx'.

* Macro Hayes v5.1 (cukup sekali per sesi SPSS).
INSERT FILE='folder\process51.sps' SYNTAX=INTERACTIVE ERROR=CONTINUE CD=NO.

INSERT FILE='folder\01_siapkan_data.sps' SYNTAX=INTERACTIVE ERROR=CONTINUE CD=NO ENCODING='UTF8'.
INSERT FILE='folder\02_deskriptif.sps' SYNTAX=INTERACTIVE ERROR=CONTINUE CD=NO ENCODING='UTF8'.
INSERT FILE='folder\03_asumsi.sps' SYNTAX=INTERACTIVE ERROR=CONTINUE CD=NO ENCODING='UTF8'.
INSERT FILE='folder\04_mediasi_process.sps' SYNTAX=INTERACTIVE ERROR=CONTINUE CD=NO ENCODING='UTF8'.
INSERT FILE='folder\05_ringkasan_BCa.sps' SYNTAX=INTERACTIVE ERROR=CONTINUE CD=NO ENCODING='UTF8'.
INSERT FILE='folder\06_sekunder.sps' SYNTAX=INTERACTIVE ERROR=CONTINUE CD=NO ENCODING='UTF8'.
