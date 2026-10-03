"""Pembantu ringkas menulis ekstrak/<NRM>.json untuk vendor apa pun (nilai dibaca Claude dari gambar).
lab/urin: list tuple (nama, hasil, satuan, rujukan, flag_vendor, halaman)."""
import json
from pathlib import Path

FOLDER = Path(__file__).resolve().parent


def tulis(nrm, *, vendor, tanggal, nama, tgl_lahir, jk, nip=None, vital=None, lab=(), urin=(),
          rad=None, ekg=None, lain=(), isi=""):
    def baris(t):
        n, h, s, r, f, hal = (list(t) + [""] * 6)[:6]
        return dict(nama=n, hasil=h, satuan=s, rujukan=r, flag_vendor=f, vendor=vendor, tanggal=tanggal,
                    berkas="berkas1", halaman=hal or 1, dibaca_dari="gambar")
    radiologi = None
    if rad:
        radiologi = dict(ada=True, vendor=vendor, tanggal=tanggal, berkas="berkas1", halaman=rad.get("halaman", 1),
                         deskripsi=rad.get("deskripsi", ""), kesimpulan=rad["kesimpulan"])
    d = dict(nrm=nrm, sumber=[dict(berkas="berkas1", vendor=vendor, tanggal=tanggal, isi=isi or "scan")],
             identitas_pdf=dict(nama=nama, tgl_lahir=tgl_lahir, jenis_kelamin=jk, nip=nip),
             tanda_vital=vital or {}, lab=[baris(t) for t in lab], urin=[baris(t) for t in urin],
             radiologi=radiologi, ekg=ekg, lain=list(lain))
    p = FOLDER / "ekstrak" / f"{nrm}.json"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
