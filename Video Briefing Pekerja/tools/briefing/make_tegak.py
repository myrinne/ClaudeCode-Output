"""Build content/pengingat/ch01/narration.id.json from naskah_pengingat_v3.md (one beat per '## Bn.' section).
Run from 'Video Briefing Pekerja/': python tools/briefing/make_tegak.py"""
import re, json, os

t = open('naskah_pengingat_v3.md', encoding='utf-8').read()
parts = re.split(r'\n## B(\d+)\. ', t)[1:]
beats = {}
for i in range(0, len(parts), 2):
    n = int(parts[i])
    lines = [l[2:].strip() for l in parts[i + 1].splitlines() if l.startswith('> ')]
    beats[f'b{n}'] = ' '.join(lines)
os.makedirs('content/pengingat/ch01', exist_ok=True)
json.dump({"engine": "edge", "voice": "id-ID-GadisNeural", "rate": "+8%", "beats": beats},
          open('content/pengingat/ch01/narration.id.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(re.sub(r'\[\[\w+\]\]', '', v).split()) for k, v in beats.items()})
