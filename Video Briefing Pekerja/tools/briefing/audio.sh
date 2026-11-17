#!/bin/sh
# Rerun after any narration change. Run from "Video Briefing Pekerja/".  SKILL path relative to this folder.
SKILL=../.claude/skills/papermorph; BOOK=briefing; A="site/$BOOK/ch01/audio/id"; N="content/$BOOK/ch01/narration.id.json"
python tools/$BOOK/make_narration.py
uv run --with edge-tts python $SKILL/scripts/tts.py "$N" "$A"
python $SKILL/scripts/level.py "$A"/*.mp3
python $SKILL/scripts/mouths.py "$N" "$A"
python $SKILL/scripts/join.py "$A" scene1=s01a scene2=s02a,s02b,s02c,s02d,s02e,s02f scene3=s03a,s03b scene4=s04a scene5=s05a,s05b,s05c scene6=s06a,s06b,s06c,s06d,s06e,s06f scene7=s07a,s07b,s07c scene8=s08a,s08b,s08c,s08d scene9=s09a scene10=s10a scene11=s11a,s11b --words "$N"
uv run --with numpy python $SKILL/scripts/sfx.py "site/$BOOK/ch01/audio/sfx" chime room
