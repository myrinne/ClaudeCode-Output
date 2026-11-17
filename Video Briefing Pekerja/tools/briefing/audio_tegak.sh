#!/bin/sh
# Portrait reminder audio. Run from "Video Briefing Pekerja/" after make_tegak.py.
SKILL=../.claude/skills/papermorph; A="site/pengingat/ch01/audio/id"; N="content/pengingat/ch01/narration.id.json"
uv run --with edge-tts python $SKILL/scripts/tts.py "$N" "$A"
python $SKILL/scripts/level.py "$A"/b[0-9]*.mp3
python $SKILL/scripts/mouths.py "$N" "$A"
python $SKILL/scripts/sfx.py site/pengingat/ch01/audio/sfx whoosh bang tick chime room
