"""Builds content/spirometri/ch04/narration.id.json from the beat text below (abbreviations spelled for the voice in
SPOKEN; the page rewrites them, and the spoken numbers, for the captions with SAY). Run from the Papermorph Books folder:
    uv run --no-project python tools/spirometri/make_narration_ch04.py
"""
import json, re
from pathlib import Path

SPOKEN = {
    "KVP": "ka ve pe", "VEP1": "ve e pe satu", "LLN": "el el en", "SD": "es de", "ATS": "a te es", "ERS": "e er es",
    "BD": "be de", "BD1": "be de satu", "BD2": "be de dua", "SABA": "es a be a", "SAMA": "es a em a", "LABA": "el a be a",
    "LAMA": "el a em a", "Z": "zet skor", "OSCE": "oski",
}

BEATS = {
    "intro": "Bab empat. Grading dan uji bronkodilator. [[sub]]Pilih penggaris yang tepat: penggaris berbeda bisa memberi jawaban berlawanan.",
    "batas": "[[a]]Rasio {VEP1} per {KVP} turun sekitar sepuluh persen dari usia dua puluh ke tujuh puluh. "
             "[[b]]Batas bawah normal, {LLN}, ikut turun: sekitar tujuh puluh empat persen, lalu enam puluh empat. "
             "[[c]]Batas tetap tujuh puluh tidak ikut turun. "
             "[[d]]Usia dua puluh, rasio tujuh puluh dua persen: batas tetap bilang normal, {LLN} bilang obstruksi. Negatif palsu. "
             "[[e]]Usia tujuh puluh, rasio enam puluh delapan: batas tetap bilang obstruksi, {LLN} bilang normal. Positif palsu.",
    "zscore": "[[a]]{Z}: jarak hasil dari nilai prediksi, dalam satuan {SD}. "
              "[[b]]Terukur dikurangi prediksi, dibagi {SD}. "
              "[[c]]Batas bawah normal adalah persentil lima: {Z} minus satu koma enam empat lima. "
              "[[d]]Contoh ilustratif: prediksi tiga koma lima nol liter, {SD} nol koma lima nol. "
              "[[e]]Batas bawah sekitar dua koma enam delapan liter. "
              "[[f]]Di bawah itu, di bawah {LLN}.",
    "zgrade": "[[a]]Derajat menurut {Z}, {ERS} {ATS} dua ribu dua puluh dua: tiga tingkat. "
              "[[b]]Ringan sampai minus dua koma lima. Sedang sampai minus empat. Berat di bawahnya. "
              "[[c]]Contoh ilustratif: terukur dua koma enam nol liter, minus satu koma delapan nol. Ringan. "
              "[[d]]Dua koma dua nol: minus dua koma enam nol. Sedang. "
              "[[e]]Satu koma empat nol: minus empat koma dua nol. Berat.",
    "q1": "Cek cepat. Klik pasien yang derajatnya sedang.",
    "klasik": "[[a]]Skema klasik memakai persen prediksi, persis seperti tertulis di catatan. "
              "[[b]]Obstruksi: tujuh puluh lima sampai enam puluh, ringan. Sampai tiga puluh, sedang. Di bawahnya, berat. "
              "[[c]]Restriksi: delapan puluh sampai enam puluh, ringan. Sampai tiga puluh, sedang. Di bawahnya, berat. "
              "[[d]]Kuasai kedua skema untuk {OSCE}.",
    "vep1": "[[a]]Kenapa {VEP1} untuk kedua pola? "
            "[[b]]Paling kuat berhubungan dengan sesak, kapasitas aktivitas, kualitas hidup, rawat inap, dan kematian. "
            "[[c]]Untuk medikolegal, pakai {VEP1} pasca {BD}, "
            "[[d]]supaya komponen reversibel tidak ikut dihitung.",
    "protokol": "[[a]]Protokol uji bronkodilator. Pertama, tahan obat. "
                "[[b]]{SABA}, empat sampai enam jam. {SAMA}, dua belas. {LABA}, dua puluh empat. {LAMA}, tiga puluh enam sampai empat puluh delapan. "
                "[[c]]Lalu spirometri pra {BD}. "
                "[[d]]Salbutamol empat ratus mikrogram lewat spacer: empat semprotan, jeda tiga puluh detik. "
                "[[e]]Tunggu sepuluh sampai lima belas menit. Dengan ipratropium, tiga puluh menit. "
                "[[f]]Terakhir, spirometri pasca {BD}.",
    "q2": "Cek cepat. Klik batang penahanan obat untuk {LABA}.",
    "rev1": "[[a]]Contoh ilustratif, pasien {BD1}. {VEP1} sebelum obat dua koma nol nol liter, sesudah dua koma tiga nol, prediksi tiga koma lima nol. "
            "[[b]]Naik nol koma tiga nol liter. "
            "[[c]]Kriteria dua ribu lima, dibanding nilai sebelum obat: dua belas persen dan dua ratus mililiter. Lima belas persen, tiga ratus mililiter: positif. "
            "[[d]]Kriteria dua ribu dua puluh dua, dibanding prediksi: sepuluh persen atau lebih. Delapan koma enam persen: negatif. "
            "[[e]]Satu pasien, dua penggaris, hasil berlawanan.",
    "rev2": "[[a]]{BD2}: sebelum satu koma nol nol, sesudah satu koma satu delapan, prediksi satu koma enam nol. "
            "[[b]]Dua ribu lima: delapan belas persen, tetapi seratus delapan puluh mililiter, kurang dari dua ratus. Negatif. "
            "[[c]]Dua ribu dua puluh dua: nol koma satu delapan dibagi satu koma enam nol, sebelas koma tiga persen. Positif. "
            "[[d]]Kebalikan {BD1}. "
            "[[e]]Jawab dengan kriteria dua ribu dua puluh dua; sebut dua ribu lima bila ditanya.",
    "wrap": "Ringkasnya. "
            "[[w1]]Batas tetap tujuh puluh menipu: {LLN} turun menurut usia. "
            "[[w2]]{Z}: terukur dikurangi prediksi, dibagi {SD}. Batas bawahnya minus satu koma enam empat lima. "
            "[[w3]]Derajat: {Z} dan skema klasik. Kuasai keduanya. "
            "[[w4]]Uji bronkodilator: kriteria dua ribu dua puluh dua membandingkan dengan prediksi. "
            "[[end]]Sekarang latihan.",
    "final1": "Latihan bab. Hitung dan nilai setiap kasus.",
    "finish": "Bab empat selesai.",
}

def spoken(s):
    return re.sub(r"\{(\w+)\}", lambda m: SPOKEN[m.group(1)], s)

root = Path(__file__).resolve().parents[2]
out = root / "content/spirometri/ch04/narration.id.json"
out.parent.mkdir(parents=True, exist_ok=True)
style = json.loads((root / "books/spirometri/style.json").read_text(encoding="utf-8"))
doc = {"voice": style["voice"]["voice"], "rate": style["voice"]["rate"], "beats": {k: spoken(v) for k, v in BEATS.items()}}
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", out, sum(len(v.split()) for v in doc["beats"].values()), "words")
