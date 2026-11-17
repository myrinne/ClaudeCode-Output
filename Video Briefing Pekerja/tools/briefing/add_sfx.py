"""Insert sound effects into the scene files (idempotent). Run from 'Video Briefing Pekerja/'.
Times are beat-clock seconds (clip time + PRE 0.8 where the agent reported clip times)."""
import re

BEDS = {1: .25, 3: .25, 7: .22, 9: .22, 11: .25}   # room tone under dapur / ruang scenes
CHIMES = {
    2: [4.73, 11.65, 17.26, 21.89],      # the four benefit cards
    4: [6.68],                           # "1 kali" tick
    6: [3.46, 12.96, 19.2, 23.95],       # the four preparation cards
    7: [12.77, 14.86, 17.95, 23.1],      # the four steps
    8: [23.22],                          # sum = 8 turns green
    9: [14.95],                          # "Tanpa biaya"
    10: [4.72],                          # "Kode 017" stamp
}
MARK = '// sfx (tools/briefing/add_sfx.py)'
for n in range(1, 12):
    p = f'site/briefing/ch01/scene{n}.js'
    s = open(p, encoding='utf-8').read()
    if MARK in s:
        continue
    lines = [MARK]
    if n in BEDS:
        lines.append(f"sfx('scene{n}', 0, 'room', {BEDS[n]}, {{ loop: true }});")
    for t in CHIMES.get(n, []):
        lines.append(f"sfx('scene{n}', {t}, 'chime', .5);")
    if len(lines) == 1:
        continue
    k = s.find('stopClock(D')
    if k < 0:
        print('no stopClock in', p)
        continue
    k = s.rfind('\n', 0, k) + 1
    indent = re.match(r'\s*', s[k:]).group(0)
    s = s[:k] + ''.join(indent + l + '\n' for l in lines) + s[k:]
    open(p, 'w', encoding='utf-8').write(s)
    print('sfx added to', p, len(lines) - 1)
