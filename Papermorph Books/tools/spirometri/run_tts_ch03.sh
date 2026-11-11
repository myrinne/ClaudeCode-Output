#!/bin/sh
# Runs tts.py until every beat is voiced; a hung Edge socket is cut after 150 s and the run resumes from its cache.
cd "$(dirname "$0")/../.."
SK="C:/Users/vidya/OneDrive/Documents/ClaudeCode Output/.claude/skills/papermorph"
for i in 1 2 3 4 5 6 7 8; do
  PYTHONIOENCODING=utf-8 timeout 150 uv run --no-project --with edge-tts python "$SK/scripts/tts.py" content/spirometri/ch03/narration.id.json site/spirometri/ch03/audio/id 2>&1 | tail -3 | cut -c1-200
  [ "${PIPESTATUS:-0}" = 0 ] 2>/dev/null
  if PYTHONIOENCODING=utf-8 uv run --no-project python tools/spirometri/tts_done_ch03.py; then echo DONE; exit 0; fi
done
echo GAVEUP
