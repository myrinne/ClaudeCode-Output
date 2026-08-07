"""
FASE 0 — BUKA PASIEN DARI NRM (navigasi otomatis, BUKAN input data)
====================================================================

Cari pasien lewat No. Rekam Medis (NRM), pilih kunjungan MCU Pegawai
TERBARU (Pembayaran = "MCU Pegawai" DAN Unit/Dept = "Medical Check Up" —
bukan Poli Pratama/Poli Spesialis/KENCANA/dst), lalu navigasi browser
langsung ke Formulir Medical Check Up kunjungan itu.

INTERAKSI BROWSER yang dilakukan: mengisi kolom pencarian NRM, klik hasil
pencarian, baca tabel Daftar Kunjungan, lalu navigasi URL. TIDAK PERNAH
mengisi/menyimpan data klinis apa pun — murni navigasi, sama seperti Anda
klik-klik manual.

Kalau kunjungan MCU Pegawai/Medical Check Up TIDAK ditemukan atau lebih
dari satu kandidat "terbaru" yang meragukan (jaraknya berdekatan / tidak
ada yang baru-baru ini), script BERHENTI dan menampilkan semua kunjungan
supaya Anda yang putuskan — tidak menebak.

Cara pakai:
    python fase0_buka_pasien.py <NRM>
    contoh: python fase0_buka_pasien.py 406-66-04
"""

import sys
import re
import asyncio
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

BULAN_ID = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
}


def parse_tanggal_id(teks):
    """'8 Juli 2026 08:37' -> datetime(2026,7,8,8,37). None kalau format tak dikenali."""
    m = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})\s+(\d{1,2}):(\d{2})', teks.strip())
    if not m:
        return None
    hari, bulan_nama, tahun, jam, menit = m.groups()
    bulan = BULAN_ID.get(bulan_nama.lower())
    if not bulan:
        return None
    try:
        return datetime(int(tahun), bulan, int(hari), int(jam), int(menit))
    except ValueError:
        return None


async def sambung(p):
    """Connect ke Chrome CDP, ambil tab pertama (halaman menu utama EHR)."""
    try:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
    except Exception:
        return None, None, "GAGAL menyambung ke Chrome. Pastikan Chrome debug sudah terbuka & login."
    contexts = browser.contexts
    if not contexts or not contexts[0].pages:
        return browser, None, "Tidak ada tab terbuka di Chrome."
    return browser, contexts[0].pages[0], None


async def cari_pasien(page, nrm):
    """Isi kolom pencarian NRM, tekan enter, klik hasil kalau tepat 1.
    Return (mpi_pid, nama, error)."""
    await page.goto("http://ehr.rscm.co.id/ehr/index.php?XP_ehradmissionemployee_menu=0")
    await asyncio.sleep(1.5)

    el = await page.query_selector('#searchpat')
    if el is None:
        # Kotak pencarian belum tampil -- klik "[ Pilih Pasien ]" dulu
        pilih = await page.query_selector('text=Pilih Pasien')
        if pilih:
            await pilih.click()
            await asyncio.sleep(1.5)
        el = await page.query_selector('#searchpat')
    if el is None:
        return None, None, "Kolom pencarian NRM (#searchpat) tidak ditemukan di halaman."

    await el.fill(nrm)
    await el.press("Enter")
    await asyncio.sleep(1.5)

    hasil = await page.query_selector_all('.xsr_sel')
    if len(hasil) == 0:
        return None, None, f"Tidak ada pasien ditemukan untuk NRM '{nrm}'."
    if len(hasil) > 1:
        teks_semua = []
        for h in hasil:
            teks_semua.append((await h.inner_text()).strip().split("\n")[0])
        return None, None, f"Ditemukan {len(hasil)} hasil untuk '{nrm}' (harusnya cuma 1): {teks_semua}"

    nama = (await hasil[0].inner_text()).strip().split("\n")[0]
    await hasil[0].click()
    await asyncio.sleep(1.5)

    m = re.search(r'mpi_pid=(\d+)', page.url)
    if not m:
        return None, None, f"Klik hasil pencarian tidak menghasilkan mpi_pid di URL: {page.url}"
    return m.group(1), nama, None


async def cari_kandidat_kunjungan_mcu(page):
    """Baca tabel Daftar Kunjungan, filter Pembayaran='MCU Pegawai' AND
    Unit/Dept='Medical Check Up', urutkan terbaru dulu.
    Return (daftar_kandidat_terurut, semua_baris_untuk_debug, error).
    TIDAK langsung memutuskan satu -- caller yang coba render tiap kandidat
    (beberapa kunjungan berlabel sama ternyata cuma sub-visit vaksin, bukan
    MCU lengkap -- lihat kasus Mia Harisandi)."""
    baris = await page.evaluate('''() => {
        const trs = document.querySelectorAll('tr');
        const out = [];
        for (const tr of trs) {
            const tds = tr.querySelectorAll('td');
            if (tds.length < 6) continue;
            const a = tds[0].querySelector('a');
            if (!a) continue;
            const href = a.getAttribute('href') || '';
            const m = href.match(/adm_id=(\\d+)/);
            if (!m) continue;
            out.push({
                tanggal: a.textContent.trim(),
                adm_id: m[1],
                pembayaran: tds[2].textContent.trim(),
                unit_dept: tds[3].textContent.trim(),
            });
        }
        return out;
    }''')

    if not baris:
        return [], baris, "Tidak ada baris 'Daftar Kunjungan' ditemukan sama sekali."

    kandidat = [b for b in baris
                if b["pembayaran"] == "MCU Pegawai" and b["unit_dept"] == "Medical Check Up"]

    if not kandidat:
        return [], baris, (
            "Tidak ada kunjungan dengan Pembayaran='MCU Pegawai' DAN "
            "Unit/Dept='Medical Check Up'. Cek manual daftar kunjungan di bawah."
        )

    for k in kandidat:
        k["_dt"] = parse_tanggal_id(k["tanggal"])
    kandidat_valid = [k for k in kandidat if k["_dt"] is not None]
    if not kandidat_valid:
        return [], baris, "Kandidat ditemukan tapi tanggalnya gagal di-parse — cek manual."

    kandidat_valid.sort(key=lambda k: k["_dt"], reverse=True)

    umur_hari = (datetime.now() - kandidat_valid[0]["_dt"]).days
    if umur_hari > 90:
        return [], baris, (
            f"Kunjungan MCU Pegawai/Medical Check Up TERBARU untuk pasien ini adalah "
            f"{kandidat_valid[0]['tanggal']} ({umur_hari} hari lalu) -- terlalu lama, "
            f"kemungkinan belum ada kunjungan MCU baru. TIDAK dipilih otomatis, cek manual."
        )

    return kandidat_valid, baris, None


async def render_form_klinis(page, mpi_pid, adm_id):
    """Navigasi ke admission tertentu & coba render form klinis penuh.
    Return True kalau tab 'Tanda Vital' berhasil muncul (form klinis
    lengkap, bukan cuma sub-visit vaksin/lainnya)."""
    url_form = f"http://ehr.rscm.co.id/ehr/index.php?XP_formmedicalpegawai_menu=0&patient_id={mpi_pid}&admission_id={adm_id}"
    await page.goto(url_form)
    await asyncio.sleep(1.5)

    body = await page.inner_text('body')
    if "FORMULIR MEDICAL CHECK UP" not in body:
        return False, url_form

    tab_pegawai = await page.query_selector('span.xlnk:has-text("Medical Check Up Pegawai")')
    if tab_pegawai:
        await tab_pegawai.click()

    # Render bisa butuh lebih dari beberapa detik tergantung riwayat kunjungan
    # pasien (kasus Dian Kurniawati: render baru selesai di detik ke-8+).
    # Polling terlalu pendek bisa salah menyimpulkan "bukan MCU lengkap" dan
    # fallback ke kunjungan yang jauh lebih lama — jangan buru-buru menyerah.
    for _ in range(20):
        await asyncio.sleep(1)
        ada = await page.evaluate('''() => {
            const spans = document.querySelectorAll('span.xlnk');
            return Array.from(spans).some(s => s.textContent.trim() === 'Tanda Vital');
        }''')
        if ada:
            return True, url_form
    return False, url_form


async def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python fase0_buka_pasien.py <NRM>")
        print("Contoh    : python fase0_buka_pasien.py 406-66-04")
        return
    nrm = sys.argv[1]

    print("=" * 70)
    print(f"FASE 0 — BUKA PASIEN DARI NRM: {nrm}")
    print("=" * 70)

    async with async_playwright() as p:
        browser, page, error = await sambung(p)
        if error:
            print(error)
            return

        print("\nMencari pasien...")
        mpi_pid, nama, error = await cari_pasien(page, nrm)
        if error:
            print(f"🔴 {error}")
            return
        print(f"✓ Ditemukan: {nama} (patient_id={mpi_pid})")

        print("\nMencari kunjungan MCU Pegawai/Medical Check Up terbaru...")
        kandidat, semua_baris, error = await cari_kandidat_kunjungan_mcu(page)
        if error:
            print(f"\n🟡 {error}")
            print("\nSemua kunjungan yang ada:")
            for b in semua_baris[:15]:
                print(f"  {b['tanggal']:22s} | {b['pembayaran']:20s} | {b['unit_dept']}")
            print("\nTIDAK menavigasi ke form apa pun. Beri tahu saya admission_id yang benar,")
            print("atau buka manual di browser lalu jalankan fase1_baca.py seperti biasa.")
            return

        # Coba kandidat dari yang PALING BARU. Kalau satu ternyata cuma
        # sub-visit (mis. vaksin) dan bukan MCU lengkap (tab 'Tanda Vital'
        # tidak muncul), coba kandidat berikutnya yang lebih lama — jangan
        # langsung menyerah (lihat kasus Mia Harisandi: kunjungan terbaru
        # ternyata cuma "Vaksin Campak", MCU sebenarnya di kunjungan sebelumnya).
        berhasil = False
        for i, k in enumerate(kandidat[:5]):
            ok, url_form = await render_form_klinis(page, mpi_pid, k["adm_id"])
            if ok:
                if i > 0:
                    print(f"🟡 Kunjungan terbaru ({kandidat[0]['tanggal']}) bukan MCU lengkap — dilewati.")
                print(f"✓ Kunjungan terpilih: {k['tanggal']} (admission_id={k['adm_id']})")
                print(f"\n✓ Berhasil membuka Formulir MCU (form klinis sudah ter-render): {url_form}")
                print("Siap dilanjutkan dengan: python fase1_baca.py")
                berhasil = True
                break
            else:
                print(f"  ({k['tanggal']} tidak me-render form klinis penuh, coba kandidat berikutnya...)")

        if not berhasil:
            print("\n🔴 TIDAK ADA kandidat kunjungan (dari 5 terbaru) yang berhasil me-render form")
            print("   klinis penuh. Semua kunjungan yang cocok kategori:")
            for k in kandidat[:5]:
                print(f"  {k['tanggal']:22s} | admission_id={k['adm_id']}")
            print("Beri tahu saya admission_id yang benar, atau buka manual di browser.")


if __name__ == "__main__":
    asyncio.run(main())
