import json, re, sys
from pathlib import Path
try:
    t = Path('site/spirometri/ch04/audio/id/timings.js').read_text(encoding='utf-8')
    d = json.loads(t[len('window.TIMINGS = '):].rstrip().rstrip(';'))
    n = json.loads(Path('content/spirometri/ch04/narration.id.json').read_text(encoding='utf-8'))
    cache = json.loads(Path('content/spirometri/ch04/narration.id.timings.json').read_text(encoding='utf-8'))
except Exception: sys.exit(1)
clean = lambda s: re.sub(r'\[\[\w+\]\]', '', s)
ok = all(b in d and [c[1] for c in d[b]['cues']] and ' '.join(c[1] for c in d[b]['cues']).split() == clean(v).split() for b, v in n['beats'].items())
sys.exit(0 if ok else 1)
