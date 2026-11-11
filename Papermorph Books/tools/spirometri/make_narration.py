"""Builds content/spirometri/ch01/narration.id.json from the beat text below.

The text uses tokens for the abbreviations, so the way they are spoken (and therefore shown in the captions, which come
from this text) is set in one place: SPOKEN. Run from the Papermorph Books folder:
    uv run --no-project python tools/spirometri/make_narration.py
"""
import json, re
from pathlib import Path

SPOKEN = {
    "KVP": "ka ve pe", "VEP1": "ve e pe satu", "NNT": "en en te", "TLC": "te el ce",
    "ATS": "a te es", "ERS": "e er es", "SD": "es de", "SpOk": "es pe o ka", "OSCE": "oski",
}

BEATS = {
    "intro": "Bab satu. Membaca pola. [[sub]]Aliran dulu, lalu kapasitas.",
    "dua": "Validitas dulu. [[v]]Kurva dibaca bila ada minimal tiga kurva acceptable dan repeatable. "
           "[[dua]]Lalu dua pertanyaan. "
           "[[a]]Pertama, rasio {VEP1} per {KVP}: kecepatan aliran. Turun berarti obstruksi. "
           "[[b]]Kedua, {KVP}: kapasitas paru. Turun berarti restriksi.",
    "matriks": "Dua pertanyaan, empat hasil. "
               "[[ax]]{KVP} di sumbu mendatar, rasio {VEP1} per {KVP} di sumbu tegak. "
               "[[cut]]Tiap sumbu punya satu batas: {NNT}. "
               "[[n]]Kanan atas: fungsi paru normal. [[r]]Kiri atas: gangguan restriksi. [[o]]Kanan bawah: gangguan obstruksi. "
               "[[c]]Kiri bawah: gangguan obstruksi dan restriksi. "
               "[[dot]]Satu pasien adalah satu titik. Letaknya menentukan hasil.",
    "kurva": "[[n]]Kurva normal: aliran naik cepat, lalu turun hampir lurus. "
             "[[o]]Pada obstruksi, {VEP1} turun lebih besar dari {KVP}. Rasio turun, kurva cekung. "
             "[[r]]Pada restriksi, {VEP1} dan {KVP} turun sebanding. Rasio normal atau naik. Kurvanya sempit. "
             "[[c]]Pada campuran, kurvanya cekung dan juga sempit.",
    "q1": "Cek cepat. Klik kurva obstruksi.",
    "batas": "Dari mana batasnya? Dua penggaris. "
             "[[vp]]Versi Paru: batas tetap. Rasio 75%, {KVP} 80% prediksi, acuan PERDOKI 2019. "
             "[[ats]]{ATS} dan {ERS} menganjurkan batas bawah normal, tetapi di {OSCE} ikuti PERDOKI. "
             "[[ok]]Versi Okupasi: {NNT}, berbeda untuk tiap pasien. "
             "[[f]]{NNT} adalah prediksi dikurangi satu koma enam empat kali {SD}. "
             "[[t]]Pengurangnya berbeda untuk pria dan wanita. "
             "[[ex]]Contoh ilustratif: pria, {KVP} prediksi 4500 mL. 4500 dikurangi 673 sama dengan 3827 mL.",
    "kasus": "Satu pasien: pria, {KVP} 3645 mL, 81% prediksi, rasio 82%. Contoh ilustratif. "
             "[[vp]]Penggaris Versi Paru: rasio di atas 75%, {KVP} di atas 80%. Titik di kanan atas: normal. "
             "[[sw]]Ganti penggaris. Titik tidak bergerak, hanya garisnya. "
             "[[nnt]]Batas {KVP} pasien ini 3827 mL, jadi garis bergeser ke kanan, melewati titik. Batas rasio 74%, hampir sama. "
             "[[res]]Titik kini di kiri atas: restriksi. Pasien sama, penggaris beda, hasil beda. "
             "[[kls]]Inilah kasus klasik board.",
    "q2": "Cek cepat. Klik garis yang membuat pasien ini restriksi.",
    "lafaz": "Lafaz di ujian. "
             "[[a]]Pada Versi Paru: rasio {VEP1} per {KVP} sama dengan atau lebih dari 75%, dan {KVP} sama dengan atau lebih dari 80%. Jadi fungsi paru normal. "
             "[[b]]Namun pada Versi Okupasi: rasio {VEP1} per {KVP} sama dengan atau lebih dari {NNT}, tetapi {KVP} kurang dari {NNT}. Jadi gangguan fungsi paru restriksi. "
             "[[c]]Sebagai {SpOk}, saya mengutamakan Versi Okupasi karena lebih sensitif untuk deteksi dini pada pekerja terpajan, "
             "sehingga kesimpulan saya: gangguan fungsi paru restriksi yang memerlukan evaluasi lanjutan dan korelasi dengan riwayat pajanan kerja.",
    "curiga": "Satu catatan. "
              "[[a]]Spirometri saja tidak memastikan restriksi. "
              "[[b]]{KVP} rendah dengan rasio normal hanya mencurigai gangguan restriksi. "
              "[[t]]Memastikannya perlu {TLC}, kapasitas paru total. "
              "[[at]]Air trapping juga menurunkan {KVP}. "
              "[[o]]Spirometri mencurigai, {TLC} memastikan.",
    "strategi": "Bila dua versi berbeda: "
                "[[a]]sebut kedua hasil. "
                "[[b]]Lalu jelaskan mengapa Versi Okupasi menjadi kesimpulan: tujuannya surveilans, sensitif untuk deteksi dini. "
                "[[c]]Bila obstruksi dan restriksi bersamaan, sebut kedua derajat secara terpisah.",
    "wrap": "Ringkasnya. "
            "[[w1]]Validitas dulu, lalu rasio, lalu {KVP}. "
            "[[w2]]Hasilnya empat: normal, restriksi, obstruksi, atau keduanya. "
            "[[w3]]Garis batas menentukan hasil: tetap pada Versi Paru, {NNT} pada Versi Okupasi. "
            "[[w4]]Bila berbeda, sebut keduanya, simpulkan Versi Okupasi. Spirometri mencurigai restriksi, {TLC} memastikan. "
            "[[end]]Sekarang latihan.",
    "final1": "Latihan bab. Tentukan hasil tiap kasus menurut kedua versi.",
    "finish": "Bab satu selesai.",
}

def spoken(s):
    return re.sub(r"\{(\w+)\}", lambda m: SPOKEN[m.group(1)], s)

root = Path(__file__).resolve().parents[2]
out = root / "content/spirometri/ch01/narration.id.json"
style = json.loads((root / "books/spirometri/style.json").read_text(encoding="utf-8"))
doc = {"voice": style["voice"]["voice"], "rate": style["voice"]["rate"], "beats": {k: spoken(v) for k, v in BEATS.items()}}
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", out, sum(len(v.split()) for v in doc["beats"].values()), "words")
