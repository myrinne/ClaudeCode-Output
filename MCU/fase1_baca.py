"""
FASE 1 — PEMBACA DATA MCU (READ-ONLY)
=====================================

Script ini HANYA MEMBACA data dari EHR RSCM. Satu-satunya interaksi
yang bukan-membaca adalah KLIK TAB "Kesimpulan" untuk menampilkan ringkasan
(berpindah tab tampilan — BUKAN submit, BUKAN menyimpan, BUKAN mengubah data).
Tidak ada perintah mengisi, menyimpan, atau approve di file ini.

Cara kerja:
1. Anda buka Chrome sendiri (perintah di bawah), lalu LOGIN SENDIRI ke EHR
2. Script menempel ke browser itu — tidak pernah tahu password Anda
3. Script membaca angka-angka dari form yang sedang terbuka
4. Hasil disimpan ke queue.json untuk diproses Fase 2

===========================================================================
LANGKAH PERSIAPAN (sekali saja)
===========================================================================

1. Install Playwright:
       pip install playwright
       playwright install chromium

2. Tutup SEMUA jendela Chrome yang sedang terbuka

3. Buka Chrome dengan mode debug. Di Command Prompt Windows, ketik:

   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\chrome-mcu"

   (Kalau Chrome ada di Program Files (x86), sesuaikan path-nya)

4. Di Chrome yang baru terbuka itu, LOGIN SENDIRI ke http://ehr.rscm.co.id/ehr/index.php

5. Buka satu pasien sampai ke halaman Formulir Medical Check Up

6. Baru jalankan script ini:
       python fase1_baca.py

===========================================================================
"""

import sys
import json
import asyncio
from datetime import datetime

from protocol_engine import (_baris_temuan_radiologi, KATA_KUNCI_TANPA_SARAN_GENERIK,
                              KATA_KUNCI_TULANG, KATA_KUNCI_INFEKSI_PARU)
from konverter_queue import ekstrak_kesimpulan_radiologi

sys.stdout.reconfigure(encoding="utf-8")

try:
    from playwright.async_api import async_playwright
except ImportError:
    raise SystemExit(
        "Playwright belum terpasang.\n"
        "Jalankan dulu:\n"
        "    pip install playwright\n"
        "    playwright install chromium"
    )


# ---------------------------------------------------------------------------
# PETA FIELD — hasil pemetaan dari HTML form RSCM
# ---------------------------------------------------------------------------
# Format ID: FNDx########## (Finding ID)
# CATATAN PENTING: beberapa field punya 2 textarea dengan id sama —
# yang pertama readonly (contoh), yang kedua editable. Kita baca yang readonly
# untuk melihat isi existing, tapi Fase 3 nanti menulis ke yang editable.

FIELD_TANDA_VITAL = {
    "td_sistolik":      "FNDx0000000929",
    "td_diastolik":     "FNDx0000000930",
    "kesimpulan_td":    "FNDx0000000965",
    "nadi":             "FNDx0000000448",
    "suhu":             "FNDx0000000449",
    "pernafasan":       "FNDx0000000450",
    "tinggi_badan":     "FNDx0000000117",
    "berat_badan":      "FNDx0000000388",
    "bmi":              "FNDx0000000451",
    "kesimpulan_bmi":   "FNDx0000000966",
    "lingkar_perut":    "FNDx0000000687",
    "kesimpulan_lp":    "FNDx0000000967",
}

FIELD_KESIMPULAN = {
    "ringkasan_anamnesis_srq":  "FNDx0000000873",
    "ringkasan_jasmani":        "FNDx0000000576",
    "ringkasan_laboratorium":   "FNDx0000000577",
    "ringkasan_radiologi":      "FNDx0000000578",
    "hasil_ekg":                "FNDx0000000580",
    "hasil_audiometri":         "FNDx0000000874",
    "hasil_spirometri":         "FNDx0000000875",
    "catatan_kelaikan":         "FNDx0000000964",
    "kesimpulan":               "FNDx0000000581",
    "saran":                    "FNDx0000000926",
}

# Field "Kelainan yang bermakna" di tab "Formulir EKG" — INI sumber asli
# hasil EKG dari dokter penganalisa EKG, BUKAN field 580 (yang cuma
# ringkasan kita sendiri, bisa ketinggalan/kosong walau EKG sudah selesai
# dianalisa). Ditemukan lewat kasus dr. Reyhan Eddy Yunus: field 580 masih
# bilang "Belum dilakukan" padahal field 955 sudah berisi
# "OMI Anteroseptal Iskemik Anterior".
FIELD_EKG_ASLI = "FNDx0000000955"
# Field "Keterangan lainnya" — TERPISAH dari 955 ("Kelainan yang bermakna"),
# dokter penganalisa EKG kadang isi salah satu atau dua-duanya (dikonfirmasi
# dr. Vidya, 2026-08-04, kasus Yusli Revika NRM 448-96-86: "Sinus Bradikardi"
# ada di 953, field 955 kosong -- sebelumnya cuma 955 yang dibaca, jadi
# "Sinus Bradikardi" hilang total dari draft). Digabung "953, lalu 955" kalau
# dua-duanya ada isi -- lihat interpretasi_ekg_existing() di konverter_queue.py.
FIELD_EKG_KETERANGAN_LAIN = "FNDx0000000953"
# Radio button "Kesan" EKG (Normal/Abnormal) TEPAT SEBELUM field 955 di
# form — ini penentu klasifikasi OTORITATIF (jangan menebak Normal/Abnormal
# dari isi teks field 955, mis. "Sinus Bradikardi" itu teksnya spesifik
# tapi kesannya tetap Normal — dikonfirmasi Anda).
FIELD_EKG_KESAN = "FNDx0000000954"


# ---------------------------------------------------------------------------
# FUNGSI BACA — semuanya read-only
# ---------------------------------------------------------------------------

async def baca_field(page, field_id):
    """
    Baca nilai satu field. Menangani kasus 2-textarea (readonly + editable).
    Mengembalikan dict berisi kedua nilai bila ada.
    """
    try:
        elements = await page.query_selector_all(f'#{field_id}')
        if not elements:
            return None

        hasil = {"readonly": None, "editable": None}
        for el in elements:
            is_readonly = await el.get_attribute("readonly")
            nilai = await el.input_value()
            if is_readonly is not None:
                hasil["readonly"] = nilai
            else:
                hasil["editable"] = nilai

        # Kalau cuma satu elemen dan bukan readonly
        if len(elements) == 1 and hasil["editable"] is None and hasil["readonly"] is None:
            hasil["editable"] = await elements[0].input_value()

        return hasil
    except Exception as e:
        return {"error": str(e)}


async def baca_identitas(page):
    """Baca nama, ID pegawai, tanggal lahir, usia dari header form"""
    identitas = {}
    try:
        body_text = await page.inner_text('body')
        import re

        # Nama pasien: baris pertama yang tidak kosong setelah heading form.
        # (Selector CSS generik seperti 'b' tidak reliable di halaman ini —
        # nama pasien murni teks polos, bukan elemen ber-class khusus.)
        idx = body_text.find("FORMULIR MEDICAL CHECK UP")
        if idx != -1:
            sisa = body_text[idx + len("FORMULIR MEDICAL CHECK UP"):]
            for baris in sisa.split("\n"):
                bersih = baris.strip().strip("\xa0").strip()
                if bersih:
                    identitas["nama_raw"] = bersih
                    break

        # Baris identitas: [NIP 18 digit ATAU ID pegawai non-standar mis. "NPS147533"] ♥ P ♥ 20 Nov 1992 ♥ 33Y 8M 1D
        # PENTING: jangan batasi ID cuma \d{18} — pegawai kategori tertentu
        # (mis. "Pekerja Radiasi") punya ID berformat huruf+angka. Kalau ID
        # tak dikenali regex, SELURUH match gagal dan usia ikut tak terbaca
        # (bisa diam-diam default ke 0 -> salah tentukan wajib-EKG).
        m = re.search(r'([A-Za-z0-9]{6,20})\s*[^\w]*\s*([LP])\s*[^\w]*\s*(\d{1,2}\s+\w+\s+\d{4})\s*[^\w]*\s*(\d+)Y', body_text)
        if m:
            identitas["nip"] = m.group(1)
            identitas["jenis_kelamin"] = m.group(2)
            identitas["tgl_lahir"] = m.group(3)
            identitas["usia"] = int(m.group(4))
    except Exception as e:
        identitas["error_identitas"] = str(e)
    return identitas


async def ambil_judul_panel(tbl):
    """Cari judul panel (mis. 'URIN LENGKAP', 'HEMATOLOGI RUTIN') dari
    div._divtanggal yang jadi sibling tabel ini. Struktur HTML EHR:
    <div style="width:95%">
      <div class="_divtanggal"><span>KODE : tanggal :</span> JUDUL PANEL</div>
      <div style="padding-left:20px;"><table class="labtbl">...</table></div>
    </div>
    Return None kalau judul tidak ditemukan (dianggap bukan panel urinalisa)."""
    try:
        return await tbl.evaluate('''(table) => {
            const wrapper = table.parentElement && table.parentElement.parentElement;
            if (!wrapper) return null;
            const dt = wrapper.querySelector(':scope > div._divtanggal');
            if (!dt) return null;
            const teks = dt.textContent.trim();
            const idx = teks.lastIndexOf(':');
            return idx >= 0 ? teks.slice(idx + 1).trim() : teks;
        }''')
    except Exception:
        return None


async def baca_tabel_lab(page):
    """
    Baca tabel hasil laboratorium dari section RINGKASAN PEMERIKSAAN LABORATORIUM
    (field FNDx0000000577, container #ipx_FNDx0000000577).

    PENTING: hasil lab TIDAK ada dalam satu tabel besar, melainkan terpecah
    per panel pemeriksaan sebagai <table class="labtbl"> (satu panel = satu
    kelompok, mis. "KIMIA KLINIK", "HEMATOLOGI RUTIN"), masing-masing dengan
    baris header sendiri (Nama Test | Flag | Hasil | Satuan | Nilai Rujukan |
    Catatan) diikuti baris data, lalu ditutup baris "Responsible Name".

    Sebelumnya kita pakai selector generik 'table tr' yang menyapu SEMUA
    ratusan tabel di frame (menu navigasi, jadwal vaksin, pemeriksaan fisik,
    dst) — itu sumber data "menggumpal". Sekarang kita batasi ke container
    lab saja, lalu baca tiap panel lewat baris headernya sendiri (kolom bisa
    beda urutan/jumlah antar panel).

    PANEL URIN LENGKAP DIPISAH ke dict `lab_urin` TERSENDIRI (return kedua),
    BUKAN digabung ke dict `lab` umum. Alasan (ditemukan dr. Vidya, kasus
    Dwiria Maharani Purba, NRM 455-93-96): panel HEMATOLOGI RUTIN dan panel
    URIN LENGKAP SAMA-SAMA punya baris bernama persis "Eritrosit" (RBC darah
    vs sedimen eritrosit urin) -- kalau digabung dalam satu dict datar
    berkunci nama tes, salah satu SALING MENIMPA yang lain. Ini bikin
    klasifikasi_urinalisa() salah kira urinalisa ADA padahal pasien itu
    urinalisa-nya belum dikerjakan sama sekali (cuma kebetulan py panel CBC
    juga punya baris "Eritrosit"). Dengan dipisah per judul panel, urinalisa
    HANYA dianggap ada kalau panel "URIN LENGKAP"-nya sendiri betul-betul ada.
    """
    lab = {}
    lab_urin = {}
    try:
        container = await page.query_selector('#ipx_FNDx0000000577')
        if container is None:
            container = page  # fallback: container tak ditemukan, coba seluruh frame

        panel_tables = await container.query_selector_all('table.labtbl')
        for tbl in panel_tables:
            rows = await tbl.query_selector_all('tr')
            if not rows:
                continue

            header_cells = await rows[0].query_selector_all('td, th')
            header = [(await c.inner_text()).strip().lower() for c in header_cells]
            kolom = {nama: i for i, nama in enumerate(header)}
            if "nama test" not in kolom:
                continue  # bukan panel hasil lab

            judul_panel = await ambil_judul_panel(tbl)
            tujuan = lab_urin if (judul_panel and "urin" in judul_panel.lower()) else lab

            def ambil(nilai, kunci):
                idx = kolom.get(kunci)
                return nilai[idx] if idx is not None and idx < len(nilai) else ""

            for row in rows[1:]:
                cells = await row.query_selector_all('td, th')
                if len(cells) < 2:
                    continue
                nilai = [(await c.inner_text()).strip() for c in cells]
                if nilai[0].lower() == "responsible name":
                    continue
                nama = ambil(nilai, "nama test")
                if not nama:
                    continue
                tujuan[nama] = {
                    "hasil": ambil(nilai, "hasil"),
                    "flag": ambil(nilai, "flag"),
                    "satuan": ambil(nilai, "satuan"),
                    "rujukan": ambil(nilai, "nilai rujukan"),
                    "catatan": ambil(nilai, "catatan"),
                }
    except Exception as e:
        lab["_error"] = str(e)
    return lab, lab_urin


async def baca_radiologi(page):
    """
    Baca report radiologi dari section RINGKASAN PEMERIKSAAN RADIOLOGI.

    PENTING: membedakan tiga kondisi yang berbeda maknanya —
      - section_tidak_termuat : section belum di-expand / tidak ada di DOM
                                (BUKAN berarti rontgen belum dilakukan!)
      - belum_dilakukan       : rontgen memang belum dikerjakan
      - normal / ada_temuan   : rontgen sudah ada hasilnya

    Kalau ketiganya dikembalikan sebagai {} yang sama, protokol bisa salah
    menyimpulkan "belum dilakukan" padahal datanya cuma belum termuat.
    """
    radio = {"kesan": "section_tidak_termuat"}
    try:
        # Cek dulu apakah field radiologi ada di DOM
        el_radio = await page.query_selector('#FNDx0000000578')
        body = await page.inner_text('body')

        ada_section = "RINGKASAN PEMERIKSAAN RADIOLOGI" in body
        radio["section_ada_di_dom"] = bool(el_radio) or ada_section

        if not radio["section_ada_di_dom"]:
            radio["kesan"] = "section_tidak_termuat"
            radio["catatan"] = (
                "Section radiologi tidak ditemukan di halaman. Ini BUKAN berarti "
                "rontgen belum dilakukan — kemungkinan section belum di-expand. "
                "Buka section radiologi di layar lalu jalankan ulang."
            )
            return radio

        # Ambil isi field radiologi bila ada
        if el_radio:
            isi = await el_radio.input_value()
            radio["isi_field"] = isi

        idx = body.find("RINGKASAN PEMERIKSAAN RADIOLOGI")
        if idx == -1:
            potongan = ""
        else:
            # Batasi sampai heading section BERIKUTNYA, jangan potong 2000
            # karakter tetap — laporan radiologi biasanya lebih pendek dari
            # itu, sehingga potongan lama kebablasan sampai membawa isi
            # section EKG/Catatan Tambahan/checkbox "Approve Dokter" ikut
            # tercampur (tidak aman ditulis ke field radiologi nanti).
            batas_akhir = idx + 2000
            for penanda in ("HASIL PEMERIKSAAN EKG", "HASIL PEMERIKSAAN AUDIOMETRI",
                             "HASIL PEMERIKSAAN SPIROMETRI", "CATATAN TAMBAHAN"):
                pos = body.find(penanda, idx + len("RINGKASAN PEMERIKSAAN RADIOLOGI"))
                if pos != -1:
                    batas_akhir = min(batas_akhir, pos)
            potongan = body[idx:batas_akhir].rstrip()
        radio["raw_text"] = potongan

        gabungan = (potongan + " " + radio.get("isi_field", "")).lower()

        # PENTING: heading "RINGKASAN PEMERIKSAAN RADIOLOGI" SENDIRI selalu
        # ikut ke dalam 'potongan' (karena kita mulai memotong dari situ).
        # Kalau cuma heading tanpa isi laporan (kasus Rani Istiarti: tabel
        # laporan radiologi genuinely kosong, belum ada report PACS masuk),
        # 'gabungan' TETAP tidak kosong secara string — jadi pengecekan
        # "not gabungan.strip()" lama TIDAK PERNAH kena. Buang heading dulu
        # sebelum cek kosong, supaya kasus ini benar terklasifikasi
        # "kosong_perlu_cek_manual", BUKAN "ada_temuan_perlu_review".
        konten_tanpa_heading = gabungan.replace("ringkasan pemeriksaan radiologi", "").strip()

        # Dulu cuma cek frasa persis "tidak tampak kelainan radiologis" --
        # gagal kena laporan perbandingan (mis. "Tidak tampak kelainan pada
        # pemeriksaan radiografi toraks, dibandingkan dengan ... 31 Juli
        # 2025") yang kata-katanya sedikit beda, sehingga jatuh ke
        # "ada_temuan_perlu_review" dan salah memicu saran Respirologi
        # generik walau filmnya normal (kasus Ismiati, NRM 328-40-35,
        # 2026-07-28). Dipersingkat jadi "tidak tampak kelainan" saja --
        # konsisten dengan KATA_KUNCI_BUKAN_TEMUAN di protocol_engine.py.
        #
        # TAPI cuma cek substring "tidak tampak kelainan" ADA di teks itu
        # sendiri tidak cukup -- gagal kena kasus kesimpulan yang PUNYA baris
        # "tidak tampak kelainan pada jantung dan paru" DAN baris temuan lain
        # yang tidak terkait jantung/paru (mis. "Sinus kostofrenikus kanan
        # tumpul DD/ penebalan pleura"), sehingga baris temuan itu ikut
        # diam-diam dianggap "normal" tanpa PERLU_CEK_MANUAL sama sekali
        # (dikonfirmasi dr. Vidya, 2026-08-04, kasus Melati Indah Putri
        # Hermadi NRM 304-06-33). Sekarang: isolasi ke kesimpulan ([Conclusion]
        # saja, bukan Deskripsi lengkap) lalu cek baris temuannya -- kalau ADA
        # baris yang bukan "tidak tampak kelainan"/lateralisasi DAN bukan
        # kategori yang sudah dikenal aman (fibrosis/kalsifikasi/kardiomegali/
        # elongasi aorta/struma/tulang-vertebra, KATA_KUNCI_TANPA_SARAN_GENERIK
        # + KATA_KUNCI_TULANG), tetap flag "ada_temuan_perlu_review" WALAU ada
        # frasa "tidak tampak kelainan" di baris lain. Elongasi/kalsifikasi
        # aorta SENDIRIAN (dan struma/tulang, yang sudah dapat penanganan
        # otomatis sendiri) TETAP tidak memicu flag manual -- dikonfirmasi
        # dr. Vidya, supaya tidak menambah beban review untuk temuan yang
        # sudah dikenal tidak perlu rujukan.
        kesimpulan_terisolasi = ekstrak_kesimpulan_radiologi(potongan)
        baris_temuan = _baris_temuan_radiologi(kesimpulan_terisolasi)
        kata_kunci_sudah_dikenal = KATA_KUNCI_TANPA_SARAN_GENERIK + KATA_KUNCI_TULANG
        # Baris yang JUGA menyebut kata kunci infeksi paru (TBC/pneumonia)
        # TIDAK BOLEH dianggap "sudah dikenal" walau kebetulan ikut menyebut
        # fibrosis/kalsifikasi/tulang dst dalam kalimat yang sama --
        # sebelumnya kata "fibrosis" saja cukup membungkam kecurigaan TB/
        # pneumonia sepenuhnya, tanpa flag PERLU_CEK_MANUAL sama sekali
        # (dikonfirmasi dr. Vidya, 2026-08-04, kasus Ikhsanudin NRM
        # 387-63-73: "Opasitas dan fibrosis ... DD/ TB Paru, pneumonia.").
        ada_temuan_belum_dikenal = any(
            any(k in b.lower() for k in KATA_KUNCI_INFEKSI_PARU)
            or not any(k in b.lower() for k in kata_kunci_sudah_dikenal)
            for b in baris_temuan
        )
        if "tidak tampak kelainan" in gabungan and not ada_temuan_belum_dikenal:
            radio["kesan"] = "normal"
        elif "tidak tampak kelainan" in gabungan and ada_temuan_belum_dikenal:
            radio["kesan"] = "ada_temuan_perlu_review"
        elif "belum dilakukan" in gabungan or "tidak dilakukan" in gabungan:
            radio["kesan"] = "belum_dilakukan"
        elif not konten_tanpa_heading:
            radio["kesan"] = "kosong_perlu_cek_manual"
            radio["catatan"] = "Section ada tapi isinya kosong — cek manual di layar."
        else:
            radio["kesan"] = "ada_temuan_perlu_review"

    except Exception as e:
        radio["kesan"] = "error"
        radio["error"] = str(e)
    return radio


async def _frame_punya_tab(fr):
    """Cek apakah frame ini memuat tab Kesimpulan / form MCU."""
    try:
        tab = await fr.query_selector('span.xlnk:has-text("Kesimpulan")')
        if tab:
            return True
        # cek juga keberadaan fungsi find_pnltab di frame ini
        ada = await fr.evaluate("typeof find_pnltab === 'function'")
        return bool(ada)
    except Exception:
        return False


async def buka_tab_kesimpulan(page):
    """
    Klik tab 'Kesimpulan' agar ringkasan lab/radiologi/EKG ter-render penuh.
    Tanpa ini, data menggumpal jadi satu blok teks yang tak terbaca.

    PENTING: form MCU RSCM berada di dalam IFRAME. Tab Kesimpulan + fungsi
    find_pnltab ada di frame itu, BUKAN di halaman utama. Karena itu kita
    telusuri SEMUA frame, temukan yang memuat tab, lalu klik di frame tsb.
    Ini BUKAN submit; hanya berpindah tab tampilan.

    Return: frame yang berisi form (dipakai untuk membaca data), atau page
    kalau ternyata form ada di halaman utama.
    """
    # Kumpulkan semua frame (halaman utama + semua iframe, termasuk nested)
    semua_frame = list(page.frames)

    frame_form = None
    for fr in semua_frame:
        if await _frame_punya_tab(fr):
            frame_form = fr
            break

    if frame_form is None:
        print("  (peringatan: tab Kesimpulan tidak ditemukan di frame mana pun)")
        print("  -> kemungkinan struktur halaman berbeda; kirim screenshot ke Claude")
        return page  # fallback: baca dari halaman utama apa adanya

    # Klik tab Kesimpulan DI DALAM frame yang benar
    try:
        tab = await frame_form.query_selector('span.xlnk:has-text("Kesimpulan")')
        if tab:
            await tab.click()
        else:
            # fallback: panggil fungsi JS langsung di frame itu
            await frame_form.evaluate("if (typeof find_pnltab === 'function') find_pnltab(24, 25);")
        await asyncio.sleep(2.5)  # tunggu render
        print("  Tab Kesimpulan dibuka di dalam iframe form.")
    except Exception as e:
        print(f"  (peringatan: gagal klik tab Kesimpulan: {e})")

    return frame_form


async def baca_ekg_asli(frame_form):
    """
    Baca field 'Kelainan yang bermakna' (FNDx0000000955) DAN radio "Kesan"
    Normal/Abnormal (FNDx0000000954) di tab 'Formulir EKG' — ini hasil EKG
    ASLI dari dokter penganalisa EKG, BUKAN field 580 (yang cuma ringkasan
    kita sendiri dan bisa ketinggalan/masih 'Belum dilakukan' walau EKG
    sudah selesai dianalisa). Lihat catatan di FIELD_EKG_ASLI.

    kesan diambil dari radio 954 (OTORITATIF), BUKAN ditebak dari teks 955
    — teks 955 bisa spesifik (mis. "Sinus Bradikardi") walau kesannya
    tetap Normal.

    Juga baca field 953 ("Keterangan lainnya") -- field TERPISAH dari 955,
    dokter penganalisa EKG kadang isi salah satu saja (dikonfirmasi dr.
    Vidya, 2026-08-04, kasus Yusli Revika NRM 448-96-86).

    Return dict {"kelainan_bermakna": str|None, "keterangan_lain": str|None,
                 "kesan": "Normal"|"Abnormal"|None, "tab_ditemukan": bool}.
    """
    hasil = {"kelainan_bermakna": None, "keterangan_lain": None, "kesan": None, "tab_ditemukan": False}
    try:
        tab = await frame_form.query_selector('span.xlnk:has-text("Formulir EKG")')
        if tab is None:
            return hasil
        hasil["tab_ditemukan"] = True
        await tab.click()
        await asyncio.sleep(2.5)

        el = await frame_form.query_selector(f'#{FIELD_EKG_ASLI}')
        if el:
            nilai = await el.input_value()
            hasil["kelainan_bermakna"] = nilai.strip() if nilai else ""

        el2 = await frame_form.query_selector(f'#{FIELD_EKG_KETERANGAN_LAIN}')
        if el2:
            nilai2 = await el2.input_value()
            hasil["keterangan_lain"] = nilai2.strip() if nilai2 else ""

        for opsi in ("Normal", "Abnormal"):
            radio = await frame_form.query_selector(f'#{FIELD_EKG_KESAN}{opsi}')
            if radio and await radio.is_checked():
                hasil["kesan"] = opsi
                break
    except Exception as e:
        hasil["error"] = str(e)
    return hasil


async def baca_halaman_aktif(page):
    """Baca SEMUA data dari halaman form MCU yang sedang terbuka"""
    data = {
        "waktu_baca": datetime.now().isoformat(),
        "url": page.url,
    }

    print("  Membuka tab Kesimpulan agar ringkasan ter-render penuh...")
    frame_form = await buka_tab_kesimpulan(page)
    data["tab_kesimpulan_terbuka"] = frame_form is not page

    # Identitas bisa di iframe atau di header luar — coba frame dulu, lalu page
    ident = await baca_identitas(frame_form)
    if not ident or not ident.get("nama_raw"):
        ident_luar = await baca_identitas(page)
        if ident_luar and ident_luar.get("nama_raw"):
            ident = ident_luar
    data["identitas"] = ident

    print("  Membaca tanda vital...")
    tv = {}
    for nama, fid in FIELD_TANDA_VITAL.items():
        nilai = await baca_field(frame_form, fid)
        if nilai:
            tv[nama] = nilai
    data["tanda_vital"] = tv

    print("  Membaca field kesimpulan (isi existing)...")
    kes = {}
    for nama, fid in FIELD_KESIMPULAN.items():
        nilai = await baca_field(frame_form, fid)
        if nilai:
            kes[nama] = nilai
    data["kesimpulan_existing"] = kes

    print("  Membaca tabel laboratorium...")
    data["laboratorium"], data["urinalisa_raw"] = await baca_tabel_lab(frame_form)

    print("  Membaca radiologi...")
    data["radiologi"] = await baca_radiologi(frame_form)

    # EKG cuma wajib utk usia >=35 — utk yang lebih muda EKG pasti "Tidak
    # dilakukan", jadi skip buka tab Formulir EKG sama sekali (percepat
    # proses, dikonfirmasi Anda). usia 0 (gagal parse identitas) dianggap
    # BUKAN muda -- tetap baca EKG demi aman (lihat pengaman usia=999 di
    # konverter_queue.py utk kasus identitas gagal terbaca total).
    usia = ident.get("usia") if ident else None
    if usia is not None and usia < 35:
        print(f"  Usia {usia} (<35) — EKG tidak wajib, lewati baca tab Formulir EKG.")
        data["ekg_asli"] = {"kelainan_bermakna": None, "kesan": None, "tab_ditemukan": False,
                             "dilewati_usia_muda": True}
    else:
        print("  Membuka tab Formulir EKG untuk baca hasil EKG asli...")
        data["ekg_asli"] = await baca_ekg_asli(frame_form)

    return data


# ---------------------------------------------------------------------------
# KONEKSI — dipakai bareng oleh Fase 1 dan Fase 3b (biar konsisten)
# ---------------------------------------------------------------------------

async def sambung_dan_cari_halaman(p):
    """
    Connect ke Chrome CDP (port 9222) dan cari tab yang sedang menampilkan
    Formulir MCU pasien. Return (browser, page_target, pesan_error).
    pesan_error None kalau sukses; page_target None kalau gagal (browser
    tetap dikembalikan bila konek berhasil, supaya caller bisa lihat daftar tab).
    """
    try:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
    except Exception:
        return None, None, (
            "GAGAL menyambung ke Chrome.\n\n"
            "Pastikan Anda sudah:\n"
            "1. Menutup semua Chrome\n"
            "2. Membuka Chrome dengan perintah:\n"
            '   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
            '--remote-debugging-port=9222 --user-data-dir="C:\\chrome-mcu"\n'
            "3. Login ke EHR di Chrome tersebut"
        )

    contexts = browser.contexts
    if not contexts:
        return browser, None, "Tidak ada tab terbuka di Chrome."

    pages = contexts[0].pages
    if not pages:
        return browser, None, "Tidak ada halaman terbuka."

    page_target = None
    for pg in pages:
        try:
            body = await pg.inner_text('body')
            if "FORMULIR MEDICAL CHECK UP" in body or "Tekanan Darah Sistolik" in body:
                page_target = pg
                break
        except Exception:
            continue

    if page_target is None:
        daftar = "\n".join(f"  - {pg.url}" for pg in pages)
        return browser, None, (
            "Tidak menemukan tab yang menampilkan Formulir Medical Check Up.\n"
            f"Tab yang terbuka ({len(pages)}):\n{daftar}\n\n"
            "Buka dulu halaman form MCU pasien, lalu jalankan lagi script ini."
        )

    body = await page_target.inner_text('body')
    if "Username" in body and "Password" in body and "FORMULIR" not in body:
        return browser, None, (
            "Sesi tampaknya sudah timeout — halaman menampilkan login.\n"
            "Silakan login ulang di Chrome, lalu jalankan script ini lagi."
        )

    return browser, page_target, None


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

async def main():
    print("=" * 70)
    print("FASE 1 — PEMBACA DATA MCU (READ-ONLY)")
    print("=" * 70)
    print("\nMenghubungkan ke Chrome yang sudah Anda buka...\n")

    async with async_playwright() as p:
        browser, page_target, error = await sambung_dan_cari_halaman(p)
        if error:
            print(error)
            return

        print(f"Membaca dari: {page_target.url}\n")
        data = await baca_halaman_aktif(page_target)

        # Simpan hasil
        nama_file = "queue.json"
        try:
            with open(nama_file, "r", encoding="utf-8") as f:
                antrian = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            antrian = []

        antrian.append(data)

        with open(nama_file, "w", encoding="utf-8") as f:
            json.dump(antrian, f, indent=2, ensure_ascii=False)

        print(f"\nSelesai. Data tersimpan di {nama_file}")
        print(f"Total pasien dalam antrian: {len(antrian)}")
        print("\nSilakan buka queue.json dan periksa apakah angka-angkanya benar")
        print("dibandingkan dengan yang tampil di layar.")

        # Tampilkan ringkasan singkat untuk verifikasi cepat
        print("\n--- RINGKASAN UNTUK VERIFIKASI CEPAT ---")
        tv = data.get("tanda_vital", {})
        for k in ("td_sistolik", "td_diastolik", "bmi", "lingkar_perut"):
            v = tv.get(k, {})
            nilai = v.get("editable") or v.get("readonly") if isinstance(v, dict) else v
            print(f"{k:20s}: {nilai}")
        jml_lab = len(data.get('laboratorium', {}))
        print(f"{'jumlah item lab':20s}: {jml_lab}")

        # SELF-CHECK: deteksi apakah data lab menggumpal
        lab = data.get("laboratorium", {})
        gumpalan = 0
        for nama_lab, isi in lab.items():
            h = isi.get("hasil", "") if isinstance(isi, dict) else str(isi)
            if len(str(h)) > 60 or any(p in str(h) for p in ["Nama Test", "Order No", "\n\t"]):
                gumpalan += 1
        if gumpalan > 0:
            print("\n" + "!" * 60)
            print(f"PERINGATAN: {gumpalan} item lab terbaca MENGGUMPAL (tidak rapi).")
            print("Data ini TIDAK bisa dipakai untuk kesimpulan otomatis.")
            print("Penyebab: tab/section Kesimpulan belum ter-render penuh.")
            print("SOLUSI: di layar, klik tab 'Kesimpulan' sampai tabel lab")
            print("        tampil rapi, lalu jalankan ulang script ini.")
            print("!" * 60)
        else:
            print("\n✓ Data lab terbaca rapi (tidak menggumpal).")


if __name__ == "__main__":
    asyncio.run(main())
