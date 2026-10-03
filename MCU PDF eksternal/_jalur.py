"""
Menyambungkan pipeline PDF eksternal ke pipeline MCU lama (protocol_engine,
konverter_queue, fase0/1/3a/3b) TANPA menyalin file -- supaya setiap
perbaikan protokol di folder lama otomatis ikut berlaku di sini.

Nama folder lama pernah berganti ("MCU" -> "MCU automatisation" ->
"MCU automation"), jadi dicari berurutan.
"""

import sys
from pathlib import Path

FOLDER_INI = Path(__file__).resolve().parent
_KANDIDAT_FOLDER_LAMA = ("MCU automation", "MCU automatisation", "MCU")

FOLDER_LAMA = None
for _nama in _KANDIDAT_FOLDER_LAMA:
    _p = FOLDER_INI.parent / _nama
    if (_p / "protocol_engine.py").exists():
        FOLDER_LAMA = _p
        break

if FOLDER_LAMA is None:
    raise ImportError(
        "Folder pipeline MCU lama (berisi protocol_engine.py) tidak ditemukan. "
        f"Dicari: {', '.join(_KANDIDAT_FOLDER_LAMA)} di {FOLDER_INI.parent}"
    )

if str(FOLDER_LAMA) not in sys.path:
    sys.path.insert(0, str(FOLDER_LAMA))
