"""
Pembantu ekstrak/<NRM>.json untuk template RSKD Duren Sawit (paket CPNS: hasil pengujian,
hasil MCU vital+PF, rekap lab darah rutin 8 parameter, rontgen, SK jiwa; biasanya TANPA
urinalisa). Nilai tetap dibaca dari gambar oleh Claude; rujukan ditulis apa adanya.
"""
import json
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
V = "RSKD Duren Sawit"
SAT = {"Hematokrit": "%", "MCV": "fl", "Hemoglobin": "g/dl", "MCHC": "g/dl", "Eritrosit": "juta /uL",
       "MCH": "pg", "Trombosit": "Ribu/uL", "Leukosit": "Ribu/uL"}
RUJ = {"P": {"Hematokrit": "35 - 47", "Hemoglobin": "11,7 - 15,5", "Eritrosit": "3,8 - 5,2", "Leukosit": "3,6 - 11"},
       "L": {"Hematokrit": "40 - 52", "Hemoglobin": "13,2 - 17,3", "Eritrosit": "4,4 - 5,9", "Leukosit": "3,8 - 10,6"}}
RUJ_UMUM = {"MCV": "80 - 100", "MCHC": "32 - 36", "MCH": "26 - 34", "Trombosit": "150 - 440"}


def tulis(nrm, *, nama, tgl_lahir, jk, nip, tanggal, vital, darah, hal_lab, hal_rad=None,
          rad_kesimpulan=None, rad_deskripsi="", flag=None, lain=None, urin=None):
    flag = flag or {}
    ruj = {**RUJ_UMUM, **RUJ[jk]}
    lab = [dict(nama=k, hasil=v, satuan=SAT.get(k, ""), rujukan=ruj.get(k, ""), flag_vendor=flag.get(k, ""),
                vendor=V, tanggal=tanggal, berkas="berkas1", halaman=hal_lab, dibaca_dari="gambar")
           for k, v in darah.items()]
    d = dict(nrm=nrm, sumber=[dict(berkas="berkas1", vendor=V, tanggal=tanggal,
                                   isi="paket CPNS RSKD Duren Sawit; scan")],
             identitas_pdf=dict(nama=nama, tgl_lahir=tgl_lahir, jenis_kelamin=jk, nip=nip),
             tanda_vital=vital, lab=lab, urin=urin or [],
             radiologi=(dict(ada=True, vendor=V, tanggal=tanggal, berkas="berkas1", halaman=hal_rad,
                             deskripsi=rad_deskripsi, kesimpulan=rad_kesimpulan) if rad_kesimpulan else None),
             ekg=None, lain=lain or [])
    p = FOLDER / "ekstrak" / f"{nrm}.json"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
