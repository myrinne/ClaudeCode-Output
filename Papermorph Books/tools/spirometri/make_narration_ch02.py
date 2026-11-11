"""Builds content/spirometri/ch02/narration.id.json from the beat text below (abbreviations spelled for the voice in
SPOKEN; the page rewrites them for the captions with SAY). Run from the Papermorph Books folder:
    uv run --no-project python tools/spirometri/make_narration_ch02.py
"""
import json, re
from pathlib import Path

SPOKEN = {
    "KVP": "ka ve pe", "VEP1": "ve e pe satu", "TLC": "te el ce", "FRC": "ef er ce", "TV": "te ve", "IC": "i ce",
    "VC": "ve ce", "RV": "er ve", "SVC": "es ve ce", "EPP": "e pe pe", "PEF": "pe e ef", "AGD": "a ge de",
    "DLCO": "de el ce o", "ATS": "a te es", "ERS": "e er es",
}

BEATS = {
    "intro": "Bab dua. Kenapa kurva berbentuk begitu. [[sub]]Jawabannya ada di dalam saluran napas.",
    "ukur": "Pertama, apa yang diukur. "
            "[[a]]Spirometri mengukur ventilasi: volume udara masuk dan keluar paru, terhadap waktu. "
            "[[b]]Bukan oksigenasi, itu urusan {AGD} dan pulse oksimetri. "
            "[[c]]Bukan difusi, itu urusan {DLCO}. "
            "[[d]]Volume residu juga tidak terlihat: udara yang tinggal setelah ekspirasi maksimal. "
            "[[e]]Maka kapasitas paru total dan kapasitas residu fungsional tidak bisa dihitung. "
            "[[f]]Perlu pletismografi, dilusi gas, washout, atau pencitraan.",
    "volume": "Satu spirogram, banyak volume. "
              "[[tv]]Napas biasa: volume tidal, {TV}. Sekitar 500 mL pada laki-laki, 400 mL pada perempuan. "
              "[[ic]]Tarik napas sedalam mungkin dari akhir napas biasa: kapasitas inspirasi, {IC}. "
              "[[vc]]Hembuskan sampai habis dari paru penuh: kapasitas vital, {VC}. "
              "[[rv]]Tetap ada udara yang tidak keluar: volume residu, {RV}. "
              "[[tlc]]Kapasitas paru total, {TLC}: kapasitas vital ditambah volume residu. "
              "[[frc]]Kapasitas residu fungsional, {FRC}: sisa udara setelah napas biasa. "
              "[[x]]Tiga yang terakhir tidak terlihat spirometer.",
    "manuver": "Manuver paksa, tiga fase. "
               "[[f1]]Satu: tarik napas sedalam mungkin. "
               "[[f2]]Dua: hembuskan sekeras dan secepat mungkin. "
               "[[f3]]Tiga: teruskan sampai habis. "
               "[[k]]Dari kurva volume terhadap waktu ini dibaca {KVP}, seluruh volume yang dihembuskan. "
               "[[v]]Dan {VEP1}, volume pada detik pertama. "
               "[[fv]]Digambar sebagai aliran terhadap volume, kurva yang sama. Aliran adalah kemiringan kurva volume. "
               "[[pk]]Aliran naik cepat ke puncak, {PEF}. "
               "[[tail]]Lalu turun sampai habis.",
    "epp": "Kenapa kurva aliran-volume berbentuk begitu? Jawabannya {EPP}, equal pressure point, dari Mead, 1967. "
           "[[a]]Pada ekspirasi paksa, dua tekanan mendorong udara keluar. "
           "[[b]]Tekanan pleura dari otot kita. "
           "[[c]]Dan recoil elastis paru. Jumlahnya adalah tekanan pendorong di alveolus. "
           "[[d]]Tekanan pleura juga menekan dinding saluran napas dari luar. "
           "[[e]]Di dalam saluran napas, tekanan turun menuju mulut, karena resistensi. "
           "[[f]]Di satu titik, tekanan di dalam sama dengan di luar. Itulah {EPP}. "
           "[[g]]Ke arah mulut, tekanan luar lebih besar, dan saluran napas tertekan. "
           "[[h]]Pada paru sehat, tekanan turun bertahap, jadi {EPP} ada di saluran napas kartilaginosa.",
    "usaha": "[[a]]Bagaimana bila usaha ditambah? "
             "[[b]]Tekanan pleura naik. "
             "[[c]]Tekanan luar naik, dan tekanan dalam naik sama banyak. "
             "[[d]]{EPP} tidak bergeser. Dorongan dari alveolus ke {EPP} tetap recoil elastis saja. "
             "[[e]]Jadi aliran tidak bertambah. Tekanan tambahan hanya menekan saluran napas lebih keras. "
             "[[f]]Pada kurva, bagian awal, dekat {PEF}, bergantung usaha. "
             "[[g]]Bagian tengah sampai akhir tidak: ditentukan recoil dan resistensi. "
             "[[h]]Karena itu {ATS} dan {ERS} menekankan usaha maksimal di awal manuver.",
    "q1": "Cek cepat. Klik {EPP}.",
    "obstruksi": "[[a]]Obstruksi: resistensi saluran napas naik, seperti pada asma atau bronkitis. "
                 "[[b]]Tekanan turun jauh lebih curam. "
                 "[[c]]Tekanan dalam menyamai tekanan luar lebih dini: {EPP} bergeser ke arah alveolus. "
                 "[[d]]Kini di bronkiolus berdinding tipis. "
                 "[[e]]Bagian hilirnya tertekan dan kolaps. "
                 "[[f]]Itu depresi khas pada kurva: cekung, bukan turun lurus. "
                 "[[g]]Kolaps lebih awal berarti lebih banyak volume tersisa di paru.",
    "emfisema": "[[a]]Ada jalan lain ke pola yang sama. Pada emfisema, jaringan elastis paru rusak. "
                "[[b]]Recoil turun, jadi tekanan pendorong lebih kecil. "
                "[[c]]Tekanan dalam cepat sampai ke tekanan luar. {EPP} bergeser ke arah alveolus. "
                "[[d]]Asma dan bronkitis: resistensi naik. "
                "[[e]]Emfisema: recoil turun. Mekanisme beda, pola sama: obstruksi.",
    "q2": "Cek cepat. Klik pasien yang emfisema.",
    "kolaps": "[[a]]Satu akibat lagi. Kapasitas vital lambat, {SVC}, diukur tanpa paksaan. "
              "[[b]]Pada obstruksi berat, ekspirasi paksa memicu kolaps dinamis lebih awal. "
              "[[c]]Akibatnya {KVP} lebih kecil dari {SVC}. "
              "[[d]]Jadi membandingkannya bukan aturan administratif, tetapi cerminan mekanika paru.",
    "wrap": "Ringkasnya. "
            "[[w1]]Spirometri mengukur ventilasi, bukan volume residu dan {TLC}. "
            "[[w2]]Di {EPP}, tekanan dalam sama dengan tekanan luar. "
            "[[w3]]Awal kurva bergantung usaha, akhirnya tidak. "
            "[[w4]]Pada obstruksi, {EPP} bergeser ke arah alveolus dan kurva cekung. Emfisema: recoil turun. Asma dan bronkitis: resistensi naik. "
            "[[end]]Sekarang latihan.",
    "final1": "Latihan bab. Jawab tiap soal.",
    "finish": "Bab dua selesai.",
}

def spoken(s):
    return re.sub(r"\{(\w+)\}", lambda m: SPOKEN[m.group(1)], s)

root = Path(__file__).resolve().parents[2]
out = root / "content/spirometri/ch02/narration.id.json"
out.parent.mkdir(parents=True, exist_ok=True)
style = json.loads((root / "books/spirometri/style.json").read_text(encoding="utf-8"))
doc = {"voice": style["voice"]["voice"], "rate": style["voice"]["rate"], "beats": {k: spoken(v) for k, v in BEATS.items()}}
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", out, sum(len(v.split()) for v in doc["beats"].values()), "words")
