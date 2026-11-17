"""Build ch02 (reminder video) narration + scene map from naskah_pengingat_v1.md, and write tools/briefing/audio_ch02.sh.
Run from 'Video Briefing Pekerja/': python tools/briefing/make_ch02.py"""
import re, json

t = open('naskah_pengingat_v1.md', encoding='utf-8').read()
parts = re.split(r'\n## Adegan (\d+)\. ', t)[1:]
beats, scenes = {}, {}
for i in range(0, len(parts), 2):
    n = int(parts[i])
    lines = [l[2:].strip() for l in parts[i + 1].splitlines() if l.startswith('> ')]
    ids = []
    for k, l in enumerate(lines):
        bid = f'r{n:02d}{"abcdefgh"[k]}'
        beats[bid] = l
        ids.append(bid)
    scenes[f'scene{n}'] = ids
json.dump({"engine": "edge", "voice": "id-ID-GadisNeural", "rate": "+8%", "beats": beats},
          open('content/briefing/ch02/narration.id.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(scenes, open('content/briefing/ch02/scenes.json', 'w'), indent=1)
joins = ' '.join(f"{k}={','.join(v)}" for k, v in scenes.items())
open('tools/briefing/audio_ch02.sh', 'w', newline='\n').write(f'''#!/bin/sh
# Reminder video audio. Run from "Video Briefing Pekerja/".
SKILL=../.claude/skills/papermorph; A="site/briefing/ch02/audio/id"; N="content/briefing/ch02/narration.id.json"
uv run --with edge-tts python $SKILL/scripts/tts.py "$N" "$A"
python $SKILL/scripts/level.py "$A"/r[0-9]*.mp3
python $SKILL/scripts/mouths.py "$N" "$A"
python $SKILL/scripts/join.py "$A" {joins} --words "$N"
''')
print({k: len(v) for k, v in scenes.items()}, sum(len(b.split()) for b in beats.values()), 'words')
