"""
TRIM QUEUE — potong queue.json supaya cuma menyisakan 1 entri pasien
terakhir (dijalankan setelah fase1_baca.py, sebelum fase3a_generate_teks.py).

Cara pakai:
    python trim_queue.py
"""

import json

with open("queue.json", encoding="utf-8") as f:
    data = json.load(f)

last = data[-1]

with open("queue.json", "w", encoding="utf-8") as f:
    json.dump([last], f, ensure_ascii=False, indent=2)

print("Sisa 1 entri:", last["identitas"]["nama_raw"])
