@echo off
rem Pakai venv khusus bila sudah ada faster-whisper; jika tidak, venv WhisperX dari plugin /watch.
set "PY=%USERPROFILE%\.cache\mcu-dikte-venv\Scripts\pythonw.exe"
"%USERPROFILE%\.cache\mcu-dikte-venv\Scripts\python.exe" -c "import faster_whisper" 2>nul || set "PY=%USERPROFILE%\.cache\watch\whisperx-venv\Scripts\pythonw.exe"
start "" "%PY%" "%~dp0dikte_mcu.py"
