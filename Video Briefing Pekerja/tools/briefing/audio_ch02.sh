#!/bin/sh
# Reminder video audio. Run from "Video Briefing Pekerja/".
SKILL=../.claude/skills/papermorph; A="site/briefing/ch02/audio/id"; N="content/briefing/ch02/narration.id.json"
uv run --with edge-tts python $SKILL/scripts/tts.py "$N" "$A"
python $SKILL/scripts/level.py "$A"/r[0-9]*.mp3
python $SKILL/scripts/mouths.py "$N" "$A"
python $SKILL/scripts/join.py "$A" scene1=r01a scene2=r02a,r02b,r02c,r02d,r02e scene3=r03a --words "$N"
