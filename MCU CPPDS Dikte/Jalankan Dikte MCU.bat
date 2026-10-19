@echo off
rem Memakai venv WhisperX dari plugin /watch (sudah berisi faster-whisper). Model: %USERPROFILE%\.cache\mcu-dikte-models
start "" "%USERPROFILE%\.cache\watch\whisperx-venv\Scripts\pythonw.exe" "%~dp0dikte_mcu.py"
