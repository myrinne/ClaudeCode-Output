"""
COBA MANUAL — jalankan file ini untuk mencoba protokol dengan data yang Anda ketik sendiri.

Cara pakai di Claude Code / terminal:
    python coba_manual.py

Program akan tanya jawab, lalu keluarkan draft teks untuk 4 kolom di web RSCM:
- Ringkasan Pemeriksaan Jasmani
- Ringkasan Pemeriksaan Laboratorium (+ Radiologi + EKG)
- Catatan Tambahan Kategori Kesehatan/Kelaikan Kerja
- Saran
"""

import sys

from protocol_engine import DataPegawai, proses_pegawai

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def tanya(prompt, tipe=str, wajib=True, default=None):
    while True:
        jawaban = input(f"{prompt}: ").strip()
        if not jawaban:
            if not wajib:
                return default
            if default is not None:
                return default
            print("  (wajib diisi, atau ketik 'skip' kalau memang tidak ada data)")
            continue
        if jawaban.lower() == "skip":
            return None
        try:
            if tipe == bool:
                return jawaban.lower() in ("y", "ya", "yes", "true", "1")
            return tipe(jawaban)
        except ValueError:
            print(f"  Format salah, coba lagi (perlu {tipe.__name__})")


def cetak_hasil(hasil, nama):
    print("\n" + "=" * 70)
    print(f"HASIL UNTUK: {nama}")
    print("=" * 70)

    if hasil.flag == "merah":
        print("\n🔴 FLAG MERAH — JANGAN AUTO-APPROVE")
        for a in hasil.flag_alasan:
            print(f"   - {a}")
    elif hasil.flag == "kuning":
        print("\n🟡 FLAG KUNING — baca dulu sebelum approve")
        for a in hasil.flag_alasan:
            print(f"   - {a}")
    else:
        print("\n🟢 FLAG HIJAU")

    print("\n--- KOLOM 1: Ringkasan Pemeriksaan Jasmani ---")
    for line in hasil.kesimpulan_jasmani:
        print(line)

    print("\n--- KOLOM 2: Ringkasan Pemeriksaan Laboratorium ---")
    print("Laboratorium :")
    for line in hasil.kesimpulan_lab:
        print(line)
    print(f"\nRontgen thorax : {hasil.kesimpulan_radiologi}")
    print(f"EKG : {hasil.kesimpulan_ekg}")

    print("\n--- KOLOM 3: Catatan Tambahan Kategori Kesehatan/Kelaikan Kerja ---")
    print(hasil.catatan_tambahan or "(tidak ada catatan tambahan)")

    print("\n--- KOLOM 4: Saran ---")
    if hasil.saran:
        for s in hasil.saran:
            print(f"- {s}")
    else:
        print("(tidak ada saran khusus)")

    print("\n--- KELAIKAN KERJA ---")
    print(f">>> {hasil.kelaikan} <<<")
    print("=" * 70 + "\n")


def main():
    print("=== INPUT DATA PEGAWAI (ketik 'skip' untuk field yang tidak ada datanya) ===\n")

    nama = tanya("Nama pegawai", str)
    usia = tanya("Usia (tahun)", int)
    jk = tanya("Jenis kelamin (L/P)", str)
    hamil = tanya("Hamil? (y/n)", bool, wajib=False, default=False)

    print("\n-- Tanda Vital --")
    sistolik = tanya("TD Sistolik (mmHg)", int, wajib=False)
    diastolik = tanya("TD Diastolik (mmHg)", int, wajib=False)
    imt = tanya("IMT (kg/m2)", float, wajib=False)
    lp = tanya("Lingkar perut (cm)", float, wajib=False)

    print("\n-- Laboratorium (enter kosong = skip / normal) --")
    hb = tanya("Status Hb (normal/anemia_ringan/anemia_sedang/anemia_berat)", str, wajib=False)
    leukosit = tanya("Status leukosit (normal/leukositosis/leukopenia)", str, wajib=False)
    trombosit = tanya("Status trombosit (normal/trombositosis)", str, wajib=False)
    led_rasio = tanya("LED = berapa x nilai rujukan atas? (mis 1.0 normal, 2.5 = 2.5x)", float, wajib=False)
    sgot_sgpt = tanya("SGOT/SGPT (normal/naik)", str, wajib=False)
    ggt = tanya("Gamma GT (normal/naik)", str, wajib=False)
    hbsag = tanya("HBsAg positif? (y/n, skip kalau tidak diperiksa)", bool, wajib=False)
    anti_hbs_diperiksa = tanya("Anti-HBs diperiksa? (y/n)", bool, wajib=False, default=False)
    anti_hbs_positif = None
    if anti_hbs_diperiksa:
        anti_hbs_positif = tanya("Anti-HBs positif (ada kekebalan)? (y/n)", bool)
    kreatinin = tanya("Status kreatinin (normal/naik_egfr_turun_ureum_normal/naik_egfr_turun_ureum_naik)", str, wajib=False)
    riwayat_ggk = tanya("Riwayat GGK sebelumnya? (y/n)", bool, wajib=False, default=False)
    kolesterol = tanya("Status kolesterol (normal/batas_tinggi/tinggi/dislipidemia)", str, wajib=False)
    trigliserida = tanya("Status trigliserida (normal/tinggi)", str, wajib=False)
    gdp = tanya("Status GDP (normal/naik/suspek_dm)", str, wajib=False)
    asam_urat = tanya("Status asam urat (normal/hiperurisemia)", str, wajib=False)
    urinalisa = tanya("Urinalisa (normal/leukosituria_bakteriuria/proteinuria_ringan/albuminuria/kristal)", str, wajib=False)

    print("\n-- Radiologi --")
    rontgen_dilakukan = tanya("Rontgen dilakukan? (y/n)", bool, wajib=False, default=True)
    rontgen_status = None
    if rontgen_dilakukan:
        rontgen_status = tanya("Status rontgen (normal/abnormal_deskripsi)", str, wajib=False, default="normal")

    print("\n-- EKG --")
    ekg_dilakukan = tanya("EKG dilakukan? (y/n)", bool, wajib=False, default=(usia >= 35))
    ekg_status = None
    if ekg_dilakukan:
        ekg_status = tanya("Status EKG (normal/abnormal_deskripsi)", str, wajib=False, default="normal")

    d = DataPegawai(
        nama=nama, usia=usia, jenis_kelamin=jk, hamil=hamil,
        td_sistolik=sistolik, td_diastolik=diastolik, imt=imt, lingkar_perut=lp,
        hb_status=hb, leukosit_status=leukosit, trombosit_status=trombosit,
        led_rasio_dari_rujukan_atas=led_rasio,
        sgot_sgpt_status=sgot_sgpt, ggt_status=ggt,
        hbsag_positif=hbsag, anti_hbs_diperiksa=anti_hbs_diperiksa, anti_hbs_positif=anti_hbs_positif,
        kreatinin_status=kreatinin, riwayat_ggk=riwayat_ggk,
        kolesterol_status=kolesterol, trigliserida_status=trigliserida,
        gdp_status=gdp, asam_urat_status=asam_urat,
        urinalisa_status_list=([urinalisa] if urinalisa else []),
        rontgen_dilakukan=rontgen_dilakukan, rontgen_status=rontgen_status,
        ekg_dilakukan=ekg_dilakukan, ekg_status=ekg_status,
    )

    hasil = proses_pegawai(d)
    cetak_hasil(hasil, nama)


if __name__ == "__main__":
    main()
