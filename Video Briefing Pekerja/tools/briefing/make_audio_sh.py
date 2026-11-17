"""Write tools/briefing/audio.sh from content/briefing/ch01/scenes.json (run after make_narration.py)."""
import json

sc = json.load(open('content/briefing/ch01/scenes.json'))
joins = ' '.join(f"{k}={','.join(v)}" for k, v in sc.items())
sh = f'''#!/bin/sh
# Rerun after any narration change. Run from "Video Briefing Pekerja/".
SKILL=../.claude/skills/papermorph; BOOK=briefing; A="site/$BOOK/ch01/audio/id"; N="content/$BOOK/ch01/narration.id.json"
uv run --with edge-tts python $SKILL/scripts/tts.py "$N" "$A"
python $SKILL/scripts/level.py "$A"/s[0-9]*.mp3
python $SKILL/scripts/mouths.py "$N" "$A"
python $SKILL/scripts/join.py "$A" {joins} --words "$N"
uv run --with numpy python $SKILL/scripts/sfx.py "site/$BOOK/ch01/audio/sfx" chime room
'''
open('tools/briefing/audio.sh', 'w', newline='\n').write(sh)
