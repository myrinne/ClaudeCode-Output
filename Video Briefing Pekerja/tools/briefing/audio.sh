#!/bin/sh
# Rerun after any narration change. Run from "Video Briefing Pekerja/".
SKILL=../.claude/skills/papermorph; BOOK=briefing; A="site/$BOOK/ch01/audio/id"; N="content/$BOOK/ch01/narration.id.json"
uv run --with edge-tts python $SKILL/scripts/tts.py "$N" "$A"
python $SKILL/scripts/level.py "$A"/s[0-9]*.mp3
python $SKILL/scripts/mouths.py "$N" "$A"
python $SKILL/scripts/join.py "$A" scene1=s01a scene2=s02a,s02b scene3=s03a,s03b,s03c,s03d scene4=s04a,s04b scene5=s05a,s05b scene6=s06a,s06b,s06c,s06d scene7=s07a,s07b,s07c scene8=s08a,s08b,s08c scene9=s09a scene10=s10a,s10b scene11=s11a,s11b --words "$N"
