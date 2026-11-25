"""Data SIMULASI (bukan data penelitian) untuk latihan sintaks SPSS tesis.
Kolom identik dengan sheet 6_Ekspor_SPSS. Pakai: python buat_simulasi.py FOLDER_TUJUAN
A = ada mediasi (b=1.35), VIF <5 ; B = jalur b nol (b=0) ; C = seperti A tetapi PM2.5 melekat pada WBGT (VIF 5-10).
Simpan ulang di Excel sebelum dibuka SPSS: SPSS 32 tidak membaca xlsx langsung dari openpyxl."""
import sys, pathlib
import numpy as np, openpyxl

COLS = ("kode hari shift ikut analisis area usia jk imt masakrj brinkman rokok rokok_ak bk_kkal bk_kat "
        "bk_sdg bk_brt wbgt pm25 tewl h2o2 pelembap wetwork selang").split()
N, SEED = 68, 20261130
PAR = dict(a=0.90, cp=0.60)                       # parameter populasi (tidak terstandar)
W_Z = np.array([31.5, 30.5, 29.5, 28.5, 26.5, 25.5, 24.0, 23.5])   # WBGT zona E1..E8 (ilustratif)
P_AB = np.array([150, 40, 95, 35, 80, 40, 30, 35.])                # PM2.5 zona skenario A dan B (ilustratif)
P_C = np.array([180, 60, 120, 45, 40, 30, 25, 20.])                # PM2.5 zona skenario C: searah dengan WBGT


def buat(b, P_Z, out):
    g = np.random.default_rng(SEED)
    rows = []
    for i in range(N):
        area = int(i % 2 == 0)
        shift = int(g.choice([1, 2, 3], p=[.25, .5, .25]) if area else g.choice([1, 2], p=[.3, .7]))
        alpha = np.r_[np.full(4, 1.2), np.full(4, .12)] if area else np.r_[np.full(4, .08), np.full(4, 1.5)]
        p = g.dirichlet(alpha)
        wbgt = round(float(p @ W_Z + (0, -.6, .3, .4)[shift] + g.normal(0, .25)), 2)
        pm = round(float(p @ P_Z * np.exp(g.normal(0, .12))), 1)
        usia = int(np.clip(g.normal(36, 8.5), 19, 55))
        jk = int(g.random() < (.60 if area else .45))
        imt = round(float(np.clip(g.normal(24.8, 3.6), 17.5, 36)), 1)
        masa = round(float(min(g.gamma(1.6, 5) + .3, max(usia - 18, .5))), 1)
        aktif = int(g.random() < (.50 if jk else .04))
        ib = int(g.choice([4, 6, 8, 10, 12, 16]) * g.integers(2, max(3, min(usia - 17, 25)))) if aktif else 0
        ib = min(ib, 560)
        bk = round(float(np.clip(g.normal(285 if area else 222, 48), 130, 430)), 1)
        tewl = (9.5 + PAR["a"] * (wbgt - 26.5) + .006 * (pm - 60) - .05 * (usia - 36) + .3 * jk
                + .05 * (imt - 25) + .001 * ib + .003 * (bk - 250) + g.normal(0, 1.9))
        tewl = round(float(max(tewl, 3)), 2)
        h = (38 + PAR["cp"] * (wbgt - 26.5) + b * (tewl - 10) + .02 * (pm - 60) + .10 * (usia - 36) - 1.2 * jk
             + .30 * (imt - 25) + .006 * ib + .01 * (bk - 250) + g.normal(0, 5.2))
        h = round(float(max(h, 8)), 2)
        pel, wet = int(g.random() < .30), int(g.random() < (.50 if area else .42))
        sel = int(np.clip(g.normal(45, 8), 28, 68))
        rows.append(dict(kode=f"H1-{i+1:02d}" if i < 44 else f"H2-{i-43:02d}", hari=1 if i < 44 else 2, shift=shift,
                         ikut=1, analisis=1, area=area, usia=usia, jk=jk, imt=imt, masakrj=masa, brinkman=ib,
                         rokok=0 if ib == 0 else 1 if ib < 200 else 2, rokok_ak=aktif, bk_kkal=bk, wbgt=wbgt, pm25=pm,
                         tewl=tewl, h2o2=h, pelembap=pel, wetwork=wet, selang=sel))
    for k in (11, 46):                              # hemolisis: H2O2 kosong
        rows[k].update(h2o2=None, analisis=0)
    rows[29].update(tewl=None, analisis=0)          # TEWL tidak layak
    rows[54].update(jk=1, rokok_ak=1, brinkman=720, rokok=3, analisis=0)   # IB >=600
    for r in rows:
        r["bk_kat"] = 1 if r["bk_kkal"] <= 200 else 2 if r["bk_kkal"] <= 350 else 3
        r["bk_sdg"], r["bk_brt"] = int(r["bk_kat"] == 2), int(r["bk_kat"] == 3)
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "data"; ws.append(COLS)
    for r in rows:
        ws.append([r[c] for c in COLS])
    wb.save(out)
    return rows


if __name__ == "__main__":
    d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True, exist_ok=True)
    buat(1.35, P_AB, d / "SIMULASI_A_mediasi.xlsx")
    buat(0.0, P_AB, d / "SIMULASI_B_tanpa_mediasi.xlsx")
    buat(1.35, P_C, d / "SIMULASI_C_VIF_tinggi.xlsx")
