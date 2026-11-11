"""Builds content/spirometri/ch05/narration.id.json from the beat text below (abbreviations spelled for the voice in
SPOKEN; the page rewrites them, and the spoken numbers, for the captions with SAY). Run from the Papermorph Books folder:
    uv run --no-project python tools/spirometri/make_narration_ch05.py
"""
import json, re
from pathlib import Path

SPOKEN = {
    "KVP": "ka ve pe", "VEP1": "ve e pe satu", "LNL": "el en el", "LLN": "el el en", "APE": "a pe e",
    "NIOSH": "en ai o es ha", "OSHA": "o es ha a", "SHIFT": "syift", "XSHIFT": "kros syift",
}

BEATS = {
    "intro": "Bab lima. Surveilans. [[sub]]Sekali potret tidak cukup. Yang dibaca adalah arahnya.",
    "hwe": "[[a]]Pekerja baru sering mulai dari {VEP1} supernormal, di atas seratus persen prediksi. "
           "[[b]]Tiap tahun, hasilnya masih di atas batas bawah normal. Normal, normal, normal. "
           "[[c]]Padahal garisnya turun, dan banyak fungsi sudah hilang. "
           "[[d]]Maka bandingkan pekerja dengan baseline dirinya sendiri.",
    "kapan": "[[a]]Prakerja: inilah baseline. "
             "[[b]]Berkala: tahunan, enam bulanan bila pajanan tinggi. "
             "[[c]]Sebelum dan sesudah satu {SHIFT}. "
             "[[d]]Khusus: setelah pindah area, cuti panjang, atau insiden inhalasi. "
             "[[e]]Akhir: saat pensiun.",
    "turun": "[[a]]Penurunan fisiologis, per tahun. "
             "[[b]]Laki-laki: {VEP1} sekitar tiga puluh mililiter, {KVP} dua puluh lima. "
             "[[c]]Perempuan: dua puluh lima untuk keduanya. "
             "[[d]]Pada laki-laki bukan perokok, turun jauh melebihi ini dalam waktu singkat: curigai pajanan.",
    "persen": "[[a]]Cara pertama: persen prediksi. Penurunan sama dengan persen prediksi baseline dikurangi persen prediksi sekarang. "
              "[[b]]Kasus dari catatan. Baseline: tiga koma tiga nol dibagi tiga koma enam lima, sembilan puluh koma empat persen. "
              "[[c]]Sekarang: dua koma lima lima dibagi tiga koma lima lima, tujuh puluh satu koma delapan persen. "
              "[[d]]Selisihnya delapan belas koma enam persen. "
              "[[e]]Di bawah sepuluh: variabilitas biologis. Sepuluh sampai lima belas: waspada. "
              "[[f]]Lima belas atau lebih: abnormal, kriteria {NIOSH}.",
    "kriteria": "[[a]]Tabel catatan: tiga kriteria. "
                "[[b]]Satu: penurunan {VEP1} atau {KVP} antara dua pemeriksaan, delapan persen atau lebih. "
                "[[c]]Dua: laju lebih dari sembilan puluh mililiter per tahun, selama lebih dari tiga tahun. "
                "[[d]]Tiga: hasil di bawah {LNL} pada tahun yang sama. "
                "[[e]]Ambang persen prediksi lima belas, tabel ini delapan. Sebut yang dipakai.",
    "q1": "Cek cepat. Klik pengukuran yang memenuhi kriteria delapan persen.",
    "lnl": "[[a]]Cara kedua: {LNL}, dibangun dari baseline. "
           "[[b]]Kasus dari catatan. Baseline: tiga koma dua empat liter. "
           "[[c]]Kali nol koma delapan lima: dua koma tujuh lima empat. "
           "[[d]]Kurangi efek usia: tiga koma tiga satu dikurangi tiga koma satu lima, nol koma satu enam. "
           "[[e]]{LNL}: dua koma lima sembilan empat liter.",
    "lnl2": "[[a]]Sekarang nilai aktual. Catatan membulatkan batas menjadi dua koma enam nol. "
            "[[b]]Aktual: dua koma lima delapan liter. "
            "[[c]]Di bawah batas: penurunan signifikan, perlu evaluasi. "
            "[[d]]Dibulatkan atau tidak, tetap di bawah.",
    "baseline": "[[a]]Jebakan: tahun baseline. "
                "[[b]]Bila lupa menggulir ke atas, data tahun kedua terbaca sebagai baseline. "
                "[[c]]Periksa tahun paling awal dulu.",
    "shift": "[[a]]{XSHIFT}: spirometri sebelum dan sesudah satu {SHIFT}, paparan paling sedikit enam jam. "
             "[[b]]Persen penurunan: sebelum dikurangi sesudah, dibagi sebelum, kali seratus persen. "
             "[[c]]Kasus dari catatan. Dua ribu delapan ratus turun jadi dua ribu tiga ratus delapan puluh mililiter: lima belas koma nol persen. "
             "[[d]]{OSHA}, debu kapas: lima persen atau lebih. Materi tambahan: lebih dari sepuluh persen. "
             "[[e]]{APE} empat ratus dua puluh jadi tiga ratus dua puluh: dua puluh tiga koma delapan persen. Ambang materi tambahan: lebih dari dua puluh. "
             "[[f]]Sebut sumber ambangnya.",
    "suhu": "[[a]]Positif palsu lain: suhu ruangan. "
            "[[b]]Pagi lebih dingin dari siang, dan koreksi suhu bisa memberi penurunan semu. "
            "[[c]]Sekitar empat persen. "
            "[[d]]Ruang pemeriksaan harus bersuhu konstan.",
    "q2": "Cek cepat. Klik ukuran yang persen penurunannya lebih besar.",
    "wrap": "Ringkasnya. "
            "[[w1]]Bandingkan dengan baseline sendiri. "
            "[[w2]]Persen prediksi: lima belas persen atau lebih abnormal. "
            "[[w3]]{LNL}: nol koma delapan lima kali baseline, dikurangi efek usia. "
            "[[w4]]{XSHIFT}: sebut sumber ambang. "
            "[[end]]Sekarang latihan.",
    "final1": "Latihan bab. Hitung dan nilai setiap kasus.",
    "finish": "Bab lima selesai.",
}

def spoken(s):
    return re.sub(r"\{(\w+)\}", lambda m: SPOKEN[m.group(1)], s)

root = Path(__file__).resolve().parents[2]
out = root / "content/spirometri/ch05/narration.id.json"
out.parent.mkdir(parents=True, exist_ok=True)
style = json.loads((root / "books/spirometri/style.json").read_text(encoding="utf-8"))
doc = {"voice": style["voice"]["voice"], "rate": style["voice"]["rate"], "beats": {k: spoken(v) for k, v in BEATS.items()}}
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", out, sum(len(v.split()) for v in doc["beats"].values()), "words")
