"""Synthesize the narration of ch01 in 3 parallel tts.py processes, then merge mp3s and timing caches so that the normal
audio.sh run finds every clip cached. Run from 'Video Briefing Pekerja/': python tools/briefing/par_tts.py [N=3]"""
import json, subprocess, sys, shutil, os
from pathlib import Path

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
SKILL = Path('../.claude/skills/papermorph/scripts/tts.py').resolve()
src = Path('content/briefing/ch01/narration.id.json')
nar = json.loads(src.read_text(encoding='utf-8'))
out = Path('site/briefing/ch01/audio/id'); out.mkdir(parents=True, exist_ok=True)

# balance by text length, keeping beat order inside each part
parts = [[] for _ in range(N)]; load = [0] * N
for bid, text in nar['beats'].items():
    k = load.index(min(load)); parts[k].append(bid); load[k] += len(text if isinstance(text, str) else text['text'])

procs, tmp = [], []
for i, ids in enumerate(parts):
    sub = {**nar, 'beats': {b: nar['beats'][b] for b in ids}}
    p = Path(f'content/briefing/ch01/_p{i}.json'); p.write_text(json.dumps(sub, ensure_ascii=False, indent=1), encoding='utf-8')
    o = Path(f'site/briefing/ch01/_p{i}'); o.mkdir(parents=True, exist_ok=True)
    tmp.append((p, o))
    procs.append(subprocess.Popen(['uv', 'run', '--with', 'edge-tts', 'python', str(SKILL), str(p), str(o)]))
codes = [pr.wait() for pr in procs]
print('tts exit codes', codes)

# merge: mp3s into the real audio folder, caches into the real cache
cache_path = src.with_suffix('.timings.json')
cache = json.loads(cache_path.read_text(encoding='utf-8-sig')) if cache_path.exists() else {}
for p, o in tmp:
    for f in o.glob('*.mp3'):
        shutil.copy2(f, out / f.name)
    c = p.with_suffix('.timings.json')
    if c.exists():
        cache.update(json.loads(c.read_text(encoding='utf-8-sig')))
        c.unlink()
    p.unlink()
    shutil.rmtree(o, ignore_errors=True)
cache_path.write_text(json.dumps(cache, indent=1), encoding='utf-8')
print('merged', len(cache), 'cache entries,', len(list(out.glob('s*.mp3'))), 'mp3')
sys.exit(0 if all(c == 0 for c in codes) else 1)
