"""Pengisi SIM DoctorTool (sim.doctortool.id, tab Pemkes Maba) untuk aplikasi Dikte MCU.

Berjalan sebagai proses terpisah dengan Python sistem (punya Playwright) dan menyambung ke Chrome debug
(port 9223) tempat dokter sudah login. Perintah masuk lewat stdin, satu JSON per baris; jawaban keluar
lewat stdout, satu JSON per baris. Protokol lengkap: PROTOKOL_ISI_SIM.md.

  {"cmd": "buka", "nama": "juni"}          -> terbuka | pilih | gagal
  {"cmd": "pilih", "no": "Z-0-148-A"}      -> terbuka | gagal
  {"cmd": "isi", "nama": "<header>", "data": {...}} -> terisi | gagal
  {"cmd": "status"}                        -> status (apakah Simpan sudah diklik)
  {"cmd": "lepas"}                         -> boleh meninggalkan pasien tanpa Simpan

TIDAK PERNAH mengklik Simpan, Batal Berkunjung, Tutup Sementara, atau tombol antrean selain Periksa.

Uji baca-saja dari terminal:  python isi_sim.py --cek
"""
import datetime as dt
import json
import re
import sys
import time

from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9223"
URL_PRAKTIK = "https://sim.doctortool.id/Praktik/DoctorPractice"
OBES_IMT = 25.0  # WHO Asia-Pacific; overweight tidak dikode (E66.3 tidak ada di SIM)
REGIO = ["Kepala", "Leher", "Thorax", "Abdomen", "Ekstremitas"]
LAB = ["Rontgen Paru", "Pemeriksaan EKG", "Darah EDTA", "Darah tanpa anti koagulan", "Urine"]

# Elemen ditandai dengan atribut data-dikte lalu dipakai lewat locator. Id elemen situs (GUID) berubah tiap muat.
JS_HELPERS = r"""
window.__dk = window.__dk || {
  vis: e => !!(e && (e.offsetWidth || e.offsetHeight || e.getClientRects().length)),
  label: e => {
    if (e.id) { const l = document.querySelector(`label[for="${CSS.escape(e.id)}"]`); if (l) return l.innerText.trim(); }
    const l = e.closest('label'); return l ? l.innerText.trim() : '';
  },
  // teks judul terdekat di atas elemen (naik maksimal 8 induk, cek saudara sebelumnya)
  head: e => {
    let n = e;
    for (let i = 0; i < 8; i++) {
      n = n.parentElement; if (!n) break;
      for (let s = n.previousElementSibling; s; s = s.previousElementSibling) {
        if (s.tagName === 'TEXTAREA' || s.querySelector('textarea')) continue;
        const t = (s.innerText || '').trim();
        if (t && t.length < 70) return t;
      }
    }
    return '';
  },
  mark: (el, id) => { if (!el) return false; el.setAttribute('data-dikte', id); return true; },
};
"""


def out(**kw):
    sys.stdout.write(json.dumps(kw, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def split_anamnesis(text):
    """Teks anamnesis dari Claude -> isi 3 kotak Subjektif SIM."""
    lines = [l.rstrip() for l in (text or "").splitlines()]
    boxes = {"subjektif": [], "rpd": [], "psl": []}
    cur = "subjektif"
    for l in lines:
        low = l.lower()
        if low.startswith("riwayat penyakit dahulu"):
            cur = "rpd"
        elif low.startswith("riwayat personal sosial"):
            cur = "psl"
            extra = l.split(":", 1)[1].strip() if ":" in l else ""
            if extra:  # hal sosial lain yang disebut ditaruh di judul oleh Claude
                boxes["psl"].append("Lain-lain : " + extra)
            continue
        elif low.startswith("riwayat olahraga") and cur != "psl":
            cur = "psl"
        if l.strip():
            boxes[cur].append(l)
    return {k: "\n".join(v) for k, v in boxes.items()}


class Sim:
    def __init__(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.connect_over_cdp(CDP)
        self.page = None
        self.kandidat = []
        self.nama_aktif = None  # nama di header "Pasien Aktif" pasien yang sedang dibuka
        self.terisi_pada = None
        self.boleh_lepas = True
        self.galat = []  # pesan dialog "Gagal" situs yang ditutup otomatis
        self.disimpan = False  # Simpan sudah diklik untuk pasien yang kita isi
        self.izin_tinggal = False  # dokter menekan "Lanjut tanpa Simpan"
        self._id = 0

    # ---- dasar ----
    def pg(self):
        pages = [p for c in self.browser.contexts for p in c.pages if "doctortool" in p.url]
        if not pages:
            raise RuntimeError("Tab SIM DoctorTool tidak ditemukan di Chrome debug (port 9223). Login dulu.")
        if self.page not in pages:
            self.page = pages[-1]
            self.page.on("dialog", lambda d: d.accept() if self.izin_tinggal else d.dismiss())
        return self.page

    def js(self, body, arg=None):
        p = self.pg()
        p.evaluate(JS_HELPERS)
        return p.evaluate(body, arg)

    def new_id(self):
        self._id += 1
        return f"d{self._id}"

    def loc(self, kind, text, last=False):
        """Tandai elemen terlihat lalu kembalikan locator-nya. kind: checkbox|radio|textarea|picker|input."""
        i = self.new_id()
        ok = self.js(r"""([kind, text, last, id]) => {
          const d = window.__dk, t = text.toLowerCase();
          let c = [];
          if (kind === 'checkbox' || kind === 'radio')
            c = [...document.querySelectorAll(`input[type=${kind}]`)].filter(e => d.label(e).toLowerCase() === t);
          else if (kind === 'textarea')
            c = [...document.querySelectorAll('textarea')].filter(e => d.vis(e) && d.head(e).toLowerCase() === t);
          else if (kind === 'picker')  // dropdownlist/combobox dikenali dari judul baris
            c = [...document.querySelectorAll('.k-dropdownlist,.k-combobox')].filter(e => d.vis(e) && d.head(e).toLowerCase().startsWith(t));
          else if (kind === 'placeholder')
            c = [...document.querySelectorAll('input')].filter(e => d.vis(e) && (e.placeholder || '').toLowerCase() === t);
          else if (kind === 'input')
            c = [...document.querySelectorAll('input')].filter(e => d.vis(e) && d.head(e).toLowerCase().startsWith(t));
          c = c.filter(e => kind === 'checkbox' || kind === 'radio' ? d.vis(e) || d.vis(e.closest('label') || e.parentElement) : true);
          return d.mark(last ? c[c.length - 1] : c[0], id);
        }""", [kind, text, last, i])
        if not ok:
            raise RuntimeError(f"{kind} '{text}' tidak ditemukan")
        return self.pg().locator(f'[data-dikte="{i}"]')

    def tutup_galat(self):
        """Dialog "Gagal" bawaan situs (mis. galat ReportViewer saat pindah tab) menutupi halaman: tekan OK."""
        p = self.pg()
        for _ in range(3):
            d = p.locator(".k-dialog-wrapper", has_text="Gagal").locator("visible=true")
            if d.count() == 0:
                return
            baris = [b for b in d.first.inner_text().splitlines() if b.strip()]
            self.galat.append(baris[1][:120] if len(baris) > 1 else "dialog Gagal")
            d.first.get_by_role("button", name="OK").click()
            p.wait_for_timeout(800)

    def tunggu_teks(self, teks, timeout=15000):
        self.pg().get_by_text(teks).locator("visible=true").first.wait_for(timeout=timeout)

    # teks yang pasti tampil setelah tab/sub-tab selesai dirender
    PENANDA = {"Pemeriksaan Awal": "Tinggi Badan", "Pemkes Maba": "Subjektif", "Subjektif": "Riwayat Penyakit Dahulu dan Pengobatan",
               "Objektif": "Ekstremitas", "Asesmen": "Prognosis", "Perencanaan": "Darah EDTA"}

    def tab(self, nama):
        self.tutup_galat()
        self.pg().locator("li.k-menu-item", has_text=nama).locator("visible=true").first.click()
        self.tunggu_teks(self.PENANDA[nama])
        self.pg().wait_for_timeout(1500)
        self.tutup_galat()

    def subtab(self, nama):
        self.tutup_galat()
        self.pg().get_by_text(nama, exact=True).locator("visible=true").first.click()
        self.tunggu_teks(self.PENANDA[nama])
        self.pg().wait_for_timeout(1200)
        self.tutup_galat()

    def header(self):
        t = self.js("() => { const m = document.body.innerText.match(/Pasien Aktif\\s*:\\s*([^;\\n]+)/); return m ? m[1].trim() : null; }")
        return t

    def pasang_pemantau_simpan(self):
        self.js(r"""() => { if (window.__dikteSimpanPasang) return;
          window.__dikteSimpanPasang = true;
          document.addEventListener('click', ev => {
            const b = ev.target.closest('button');
            if (b && b.innerText.trim() === 'Simpan') window.__dikteSimpan = Date.now();
          }, true); }""")

    def simpan_diklik(self):
        if not self.terisi_pada:
            return False
        # Simpan yang berhasil membawa SIM kembali ke halaman utama Praktik; penanda klik ikut hilang saat itu
        if "DoctorPracticeEntry" not in self.pg().url:
            return True
        t = self.js("() => window.__dikteSimpan || 0")
        return bool(t and t / 1000 >= self.terisi_pada)

    # ---- perintah ----
    def buka(self, nama):
        p = self.pg()
        if "DoctorPracticeEntry" in p.url and not self.izin_tinggal:
            # jangan tinggalkan halaman pasien yang mungkin berisi isian (manual atau dari kita) yang belum disimpan
            hdr = self.header()
            if not (hdr and self.nama_aktif and norm(hdr) == norm(self.nama_aktif) and self.disimpan):
                return out(ev="gagal", perlu_lepas=True,
                           pesan=f"halaman pasien {hdr or '?'} masih terbuka; klik Simpan/tutup di SIM, atau 'Lanjut tanpa Simpan'")
        self.izin_tinggal = False
        p.goto(URL_PRAKTIK)
        p.wait_for_selector(".k-grid", timeout=20000)
        p.wait_for_timeout(2500)  # grid diisi Blazor setelah halaman tampil
        rows = self.js(r"""() => { const g = document.querySelector('.k-grid');
          const h = [...g.querySelectorAll('thead th')].map(t => t.innerText.trim());
          const iN = h.findIndex(x => x.startsWith('Nama')), iNo = h.findIndex(x => x.startsWith('No'));
          return [...g.querySelectorAll('tbody tr')].filter(r => r.querySelector('.btn-dt-periksa')).map(r => {
            const td = r.querySelectorAll('td');
            return {no: td[iNo].innerText.trim(), nama: td[iN].innerText.trim(),
                    status: (td[h.findIndex(x => x.startsWith('Status'))] || {innerText: ''}).innerText.trim()};
          }); }""")
        cocok = [r for r in rows if norm(nama) in norm(r["nama"])]
        if not cocok:
            return out(ev="gagal", pesan=f"'{nama}' tidak ada di daftar Hari ini ({len(rows)} pasien)")
        if len(cocok) > 1:
            self.kandidat = cocok
            return out(ev="pilih", kandidat=cocok)
        return self.pilih(cocok[0]["no"], rows=cocok)

    def pilih(self, no, rows=None):
        rows = rows or self.kandidat
        r = next((x for x in rows if x["no"] == no), None)
        if not r:
            return out(ev="gagal", pesan=f"antrean {no} tidak ada")
        p = self.pg()
        tr = p.locator(".k-grid").first.locator("tbody tr", has_text=no)
        tr.locator(".btn-dt-periksa").click()
        p.wait_for_url("**/DoctorPracticeEntry**", timeout=20000)
        p.wait_for_selector("text=Pasien Aktif", timeout=20000)
        p.wait_for_timeout(2500)
        hdr = self.header() or ""
        nama_grid = re.sub(r"\s*\(.*$", "", r["nama"]).strip()
        if norm(nama_grid) not in norm(hdr) and norm(hdr) not in norm(nama_grid):
            return out(ev="gagal", pesan=f"header '{hdr}' tidak cocok dengan '{nama_grid}'; tidak diisi")
        self.nama_aktif, self.terisi_pada, self.boleh_lepas, self.disimpan = hdr, None, True, False
        self.pasang_pemantau_simpan()
        info = self.cek_awal()
        self.tab("Pemkes Maba")
        self.subtab("Subjektif")
        out(ev="terbuka", nama=hdr, no=no, **info)

    def cek_awal(self):
        """Tab Pemeriksaan Awal: Tujuan, Keluhan Utama (ICPC) diisi -30 bila kosong, TB/BB untuk IMT."""
        info = {"peringatan": [], "imt": None}
        try:
            self.tab("Pemeriksaan Awal")
            tujuan = self.loc("picker", "Tujuan").inner_text().strip()
            if "pemeriksaan kesehatan" not in tujuan.lower():
                info["peringatan"].append(f"Tujuan = '{tujuan or 'kosong'}' (bukan Pemeriksaan Kesehatan)")
            icpc = self.loc("input", "Keluhan Utama")
            if not icpc.input_value().strip():
                self.pilih_combobox(icpc, "Pemeriksaan Kesehatan", lambda t: t.strip().startswith("-30"))
                info["peringatan"].append("Keluhan Utama ICPC kosong → diisi -30 Pemeriksaan Kesehatan")
            elif "-30" not in icpc.input_value():
                info["peringatan"].append(f"Keluhan Utama = '{icpc.input_value()}'")
            tb = float(self.loc("input", "Tinggi Badan").input_value().replace(",", "."))
            bb = float(self.loc("input", "Berat Badan").input_value().replace(",", "."))
            if tb > 0 and bb > 0:
                info["imt"] = round(bb / (tb / 100) ** 2, 1)
        except Exception as e:
            info["peringatan"].append(f"cek Pemeriksaan Awal: {e}")
        return info

    def pilih_combobox(self, inp, ketik, cocok):
        """Ketik di combobox Telerik lalu pilih item pertama yang lolos fungsi cocok(teks)."""
        p = self.pg()
        inp.click()
        inp.fill("")
        inp.press_sequentially(ketik, delay=60)
        items = p.locator(".k-animation-container li.k-list-item, .k-popup li.k-list-item").locator("visible=true")
        t0 = time.time()
        while time.time() - t0 < 10:
            for i in range(items.count()):
                txt = items.nth(i).inner_text()
                if cocok(txt):
                    items.nth(i).click()
                    p.wait_for_timeout(800)
                    return txt.strip()
            p.wait_for_timeout(400)
        inp.press("Escape")
        inp.fill("")
        raise RuntimeError(f"'{ketik}' tidak ada di pilihan")

    def isi_teks(self, loc, teks):
        loc.fill(teks)
        loc.evaluate("e => e.blur()")
        self.pg().wait_for_timeout(300)
        if loc.input_value() != teks:
            raise RuntimeError("isi tidak menempel")

    def isi(self, nama, data):
        lap, gagal = [], []

        def langkah(nama_langkah, fn):
            try:
                hasil = fn()
                lap.append(f"{nama_langkah} ✓" + (f" ({hasil})" if isinstance(hasil, str) and hasil else ""))
            except Exception as e:
                gagal.append(f"{nama_langkah}: {str(e).splitlines()[0][:120]}")

        hdr = self.header()
        if not hdr or norm(hdr) != norm(nama):
            return out(ev="gagal", pesan=f"pasien di layar '{hdr}' ≠ '{nama}'; TIDAK diisi")
        self.tab("Pemkes Maba")
        kotak = split_anamnesis(data.get("anamnesis", ""))

        self.subtab("Subjektif")
        langkah("Subjektif", lambda: self.isi_teks(self.loc("textarea", "Subjektif", last=True), kotak["subjektif"]))
        langkah("RPD & pengobatan", lambda: self.isi_teks(self.loc("textarea", "Riwayat Penyakit Dahulu dan Pengobatan"), kotak["rpd"]))
        langkah("Personal sosial", lambda: self.isi_teks(self.loc("textarea", "Riwayat Personal Sosial dan Lingkungan"), kotak["psl"]))

        self.subtab("Objektif")
        pf = {k.lower(): (v or "").strip() for k, v in (data.get("pf_regio") or {}).items()}
        for r in REGIO:
            def regio(r=r):
                cb = self.loc("checkbox", r)
                if not cb.is_checked():
                    cb.check()
                    self.pg().wait_for_timeout(700)
                temuan = pf.get(r.lower())
                if temuan:
                    self.isi_teks(self.loc("textarea", r), temuan)
                    return temuan
            langkah(f"PF {r}", regio)

        self.subtab("Asesmen")
        langkah("Kasus Baru", lambda: self.loc("radio", "Baru").check())
        langkah("Masalah Umum", lambda: self.loc("radio", "Umum").check())

        def prognosis():
            self.loc("picker", "Prognosis").click()
            self.pg().locator("li.k-list-item", has_text="Bonam").locator("visible=true").first.click()
            self.pg().wait_for_timeout(600)
        langkah("Prognosis Bonam", prognosis)

        def dx_kerja():
            inp = self.loc("placeholder", "Pencarian Diagnosis Kerja (ICD10)")
            if inp.input_value().upper().startswith("Z02.0"):
                return "sudah ada"
            return self.pilih_combobox(inp, "Z02.0", lambda t: t.strip().upper().startswith("Z02.0 "))
        langkah("Dx kerja Z02.0", dx_kerja)

        icd = [i["kode"].strip().upper() for i in data.get("icd") or [] if i.get("kode")]
        imt = data.get("imt")
        if imt and imt >= OBES_IMT and "E66.9" not in icd:
            icd.append("E66.9")
            lap.append(f"IMT {imt} → E66.9 ditambahkan")
        def dx_sekunder(k):
            # pengisian ulang (rekaman lanjutan peserta yang sama) tidak boleh menggandakan kode
            if self.js("k => document.body.innerText.toUpperCase().includes(k + ' - ')", k):
                return "sudah ada"
            return self.pilih_combobox(self.loc("placeholder", "Pencarian Diagnosis Sekunder (ICD10)"), k,
                                       lambda t: t.strip().upper().startswith(k + " "))
        for kode in icd:
            if not kode.startswith("Z02"):
                langkah(f"Dx sekunder {kode}", lambda k=kode: dx_sekunder(k))

        self.subtab("Perencanaan")
        for nm in LAB:
            def lab(nm=nm):
                cb = self.loc("checkbox", nm)
                if not cb.is_checked():
                    cb.check()
                    self.pg().wait_for_timeout(600)
                if not cb.is_checked():
                    raise RuntimeError("tidak tercentang")
            langkah(nm, lab)

        # kembali ke awal + cek isian Subjektif masih ada setelah pindah sub-tab
        self.subtab("Subjektif")
        for coba in range(3):
            try:
                if self.loc("textarea", "Subjektif", last=True).input_value() != kotak["subjektif"]:
                    gagal.append("isian Subjektif HILANG setelah pindah sub-tab")
                break
            except Exception as e:
                if coba == 2:
                    gagal.append(f"cek ulang Subjektif: {e}")
                self.pg().wait_for_timeout(1500)
        self.terisi_pada = time.time()
        self.boleh_lepas = False
        self.pasang_pemantau_simpan()
        out(ev="terisi", nama=hdr, laporan=lap, gagal=gagal, galat_situs=self.galat[-3:])

    def status(self):
        disimpan = False
        try:
            disimpan = self.simpan_diklik()
        except Exception:
            pass
        if disimpan:
            self.boleh_lepas = self.disimpan = True
        out(ev="status", nama=self.nama_aktif, terisi=bool(self.terisi_pada), disimpan=disimpan)

    def cek(self):
        """Baca-saja: pastikan semua target ada di halaman pasien yang sedang terbuka."""
        hasil = {"header": self.header()}
        if not hasil["header"]:
            return print("Buka dulu satu pasien (halaman Periksa).")
        hasil["awal"] = self.cek_awal_baca()
        self.tab("Pemkes Maba")
        for sub, targets in [
            ("Subjektif", [("textarea", "Subjektif"), ("textarea", "Riwayat Penyakit Dahulu dan Pengobatan"),
                           ("textarea", "Riwayat Personal Sosial dan Lingkungan")]),
            ("Objektif", [("checkbox", r) for r in REGIO]),
            ("Asesmen", [("radio", "Baru"), ("radio", "Umum"), ("picker", "Prognosis"),
                         ("placeholder", "Pencarian Diagnosis Kerja (ICD10)"),
                         ("placeholder", "Pencarian Diagnosis Sekunder (ICD10)")]),
            ("Perencanaan", [("checkbox", n) for n in LAB]),
        ]:
            self.subtab(sub)
            for kind, text in targets:
                try:
                    self.loc(kind, text)
                    hasil[f"{sub}/{text}"] = "ada"
                except Exception as e:
                    hasil[f"{sub}/{text}"] = f"TIDAK: {e}"
        self.subtab("Subjektif")
        print(json.dumps(hasil, ensure_ascii=False, indent=1))

    def cek_awal_baca(self):
        self.tab("Pemeriksaan Awal")
        r = {}
        for kind, t in [("picker", "Tujuan"), ("input", "Keluhan Utama"), ("input", "Tinggi Badan"), ("input", "Berat Badan")]:
            try:
                l = self.loc(kind, t)
                r[t] = l.inner_text().strip() if kind == "picker" else (l.input_value() or "(kosong)")
            except Exception as e:
                r[t] = f"TIDAK: {e}"
        return r


def serve():
    try:
        sim = Sim()
        sim.pg()
        out(ev="siap")
    except Exception as e:
        return out(ev="mati", pesan=str(e).splitlines()[0][:200])
    for line in sys.stdin:
        try:
            m = json.loads(line)
            c = m.get("cmd")
            if c == "buka":
                sim.buka(m["nama"])
            elif c == "pilih":
                sim.pilih(m["no"])
            elif c == "isi":
                sim.isi(m["nama"], m["data"])
            elif c == "status":
                sim.status()
            elif c == "lepas":
                sim.boleh_lepas = sim.izin_tinggal = True
                out(ev="dilepas")
        except Exception as e:
            out(ev="gagal", pesan=f"{c}: {str(e).splitlines()[0][:200]}")


if __name__ == "__main__":
    # pipa stdin/stdout di Windows default cp1252: tanda ✓/⚠ dan nama beraksen membuat laporan gagal terkirim
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    if "--cek" in sys.argv:
        Sim().cek()
    else:
        serve()
