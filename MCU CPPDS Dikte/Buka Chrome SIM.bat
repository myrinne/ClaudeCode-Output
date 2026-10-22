@echo off
rem Chrome khusus untuk SIM DoctorTool (port debug 9223, profil terpisah). Login sendiri di jendela ini.
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir=C:\chrome-sim https://sim.doctortool.id/Praktik/DoctorPractice
