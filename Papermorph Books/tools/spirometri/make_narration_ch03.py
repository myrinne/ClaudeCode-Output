"""Builds content/spirometri/ch03/narration.id.json from the beat text below (abbreviations spelled for the voice in
SPOKEN; the page rewrites them for the captions with SAY). Run from the Papermorph Books folder:
    uv run --no-project python tools/spirometri/make_narration_ch03.py
"""
import json, re
from pathlib import Path

SPOKEN = {
    "KVP": "ka ve pe", "VEP1": "ve e pe satu", "TLC": "te el ce", "BEV": "be e ve", "EOFE": "e o ef e", "FIVC": "ef i ve ce",
    "FET": "ef e te", "ATS": "a te es", "ERS": "e er es",
}

BEATS = {
    "intro": "Bab tiga. Kurva valid atau cacat. [[sub]]Angka spirometri hanya sebaik kurvanya.",
    "sebelum": "Sebelum pasien, alat diperiksa. "
               "[[a]]Uji kebocoran: batasnya berbeda menurut sumber. "
               "[[b]]Lalu syringe tiga liter. Batas tiga persen: dua koma sembilan satu sampai tiga koma nol sembilan liter. "
               "[[c]]Contoh ilustratif: tiga koma nol lima, lolos. "
               "[[d]]Tiga koma satu dua, gagal. "
               "[[e]]Dan nose clip, supaya udara tidak bocor lewat hidung.",
    "lima": "Lima kriteria acceptable, menurut PERDOKI. "
            "[[a]]Awal yang baik, tegak, tanpa hesitation. "
            "[[b]]Inspirasi dan ekspirasi maksimal. "
            "[[c]]Satu puncak. "
            "[[d]]Bebas artefak. "
            "[[e]]Selesai dengan baik: enam detik, atau plateau satu detik. "
            "[[f]]Kurva acceptable memenuhi kelimanya.",
    "awal": "[[a]]Awal dinilai dengan {BEV}, volume hasil ekstrapolasi mundur. "
            "[[b]]Garis singgung di bagian tercuram ditarik ke waktu nol. "
            "[[c]]Batasnya: lima persen {KVP}, atau seratus mililiter, yang lebih besar. "
            "[[d]]Contoh ilustratif: {KVP} empat liter. Lima persen adalah dua ratus mililiter, jadi batasnya dua ratus. "
            "[[e]]Pasien ragu, kurva landai dulu. {BEV} seratus delapan puluh: lolos. "
            "[[f]]Dua ratus empat puluh: gagal. "
            "[[g]]{KVP} dan {VEP1} terukur terlalu rendah.",
    "akhir": "[[a]]Akhir ekspirasi. "
             "[[b]]PERDOKI: enam detik, atau plateau satu detik. "
             "[[c]]{ATS} dan {ERS} menghapus aturan enam detik: plateau di bawah dua puluh lima mililiter selama satu detik, atau {FET} lima belas detik. "
             "[[d]]Dua sumber, dua rumusan. "
             "[[e]]Pasien berhenti terlalu cepat: kurva masih menanjak saat terpotong. "
             "[[f]]{KVP} terukur terlalu rendah.",
    "fivc": "[[a]]{FIVC}: volume inspirasi paksa sesudah ekspirasi. "
            "[[b]]Menurut catatan, {FIVC} dikurangi {KVP} lebih dari seratus mililiter, atau lebih dari lima persen: tidak acceptable. "
            "[[c]]Lingkarannya tidak menutup. Pasien tidak mulai dari {TLC} penuh.",
    "batuk": "Artefak kelompok pertama: menurunkan nilai. "
             "[[a]]Batuk di detik pertama: takik tajam. "
             "[[b]]{VEP1} tidak acceptable. {KVP} masih bisa, bila batuk setelah detik pertama. "
             "[[c]]Penutupan glotis: aliran turun mendadak. "
             "[[d]]Keduanya tidak acceptable.",
    "bocor": "[[a]]Kebocoran: kurva volume-waktu mendatar terlalu dini, pada volume rendah. "
             "[[b]]Bandingkan dengan manuver lain. "
             "[[c]]Usaha submaksimal: puncak rendah dan tumpul. "
             "[[d]]Catatan menyebutnya cekung, kata yang sama dengan obstruksi. "
             "[[e]]Bedanya: cekung obstruksi mulai setelah puncak. Pada submaksimal puncaknya sendiri rendah dan tumpul, dan berubah antar manuver.",
    "q1": "Cek cepat. Klik bagian kurva yang cacat.",
    "rasio": "Kelompok kedua: memalsukan rasio. "
             "[[a]]Zero-flow error. "
             "[[b]]Under-recording: {KVP} terekam jauh lebih kecil daripada {VEP1}. "
             "[[c]]Rasio naik palsu. Obstruksi sejati tersembunyi. "
             "[[d]]Over-recording: {KVP} naik semu, kurva tak pernah datar. "
             "[[e]]Rasio turun palsu. Obstruksi palsu. "
             "[[f]]Ekor aliran-volume memanjang ke kanan. "
             "[[g]]Arahnya berlawanan.",
    "hidung": "[[a]]Extra breath via nose, arahnya sama dengan over-recording. "
              "[[b]]Pasien menghirup tambahan lewat hidung di akhir embusan, lalu mengembuskannya lagi. "
              "[[c]]Ekor ganda. "
              "[[d]]{KVP} naik palsu, rasio turun palsu. "
              "[[e]]Nose clip wajib.",
    "q2": "Cek cepat. Klik kurva yang mencurigakan sebagai obstruksi palsu.",
    "ulang": "[[a]]Repeatability: minimal tiga manuver acceptable, paling banyak delapan. "
             "[[b]]Jeda satu menit atau lebih. "
             "[[c]]Dua terbesar berselisih paling banyak seratus lima puluh mililiter. "
             "[[d]]Contoh ilustratif, {KVP}: selisih seratus mililiter, lolos. "
             "[[e]]{VEP1}: dua ratus mililiter, tidak lolos. "
             "[[f]]Yang tertinggi boleh berasal dari kurva berbeda.",
    "variabel": "[[a]]Terakhir, usaha tidak konsisten. "
                "[[b]]Tumpuk tiga kurva. Bentuk sama, puncak sedikit beda: konsisten. "
                "[[c]]Bentuk berbeda-beda: data tidak reproducible. "
                "[[d]]Tidak boleh ditarik kesimpulan.",
    "wrap": "Ringkasnya. "
            "[[w1]]Verifikasi alat dulu: syringe tiga liter, batas tiga persen. "
            "[[w2]]Kurva acceptable memenuhi lima kriteria PERDOKI. "
            "[[w3]]Artefak: sebagian menurunkan nilai, sebagian memalsukan rasio, ke arah berlawanan. "
            "[[w4]]Ulangi minimal tiga kali, dua terbesar berselisih paling banyak seratus lima puluh mililiter, bentuk konsisten. "
            "[[end]]Sekarang latihan.",
    "final1": "Latihan bab. Nilai setiap kurva.",
    "finish": "Bab tiga selesai.",
}

def spoken(s):
    return re.sub(r"\{(\w+)\}", lambda m: SPOKEN[m.group(1)], s)

root = Path(__file__).resolve().parents[2]
out = root / "content/spirometri/ch03/narration.id.json"
out.parent.mkdir(parents=True, exist_ok=True)
style = json.loads((root / "books/spirometri/style.json").read_text(encoding="utf-8"))
doc = {"voice": style["voice"]["voice"], "rate": style["voice"]["rate"], "beats": {k: spoken(v) for k, v in BEATS.items()}}
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", out, sum(len(v.split()) for v in doc["beats"].values()), "words")
