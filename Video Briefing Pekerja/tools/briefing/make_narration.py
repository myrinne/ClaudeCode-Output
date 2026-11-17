"""Build content/briefing/ch01/narration.id.json and scenes.json from naskah_briefing_v2.md.
Run from 'Video Briefing Pekerja/': python tools/briefing/make_narration.py"""
import re, json

t = open('naskah_briefing_v2.md', encoding='utf-8').read()
parts = re.split(r'\n## Adegan (\d+)\. ', t)[1:]
beats, scenes = {}, {}
for i in range(0, len(parts), 2):
    n = int(parts[i])
    lines = [l[2:].strip() for l in parts[i + 1].splitlines() if l.startswith('> ')]
    # Edge TTS cuts the end of long clips: split lines over 35 words at the sentence break nearest the middle
    flat = []
    for l in lines:
        if len(l.split()) > 35:
            sents = re.split(r'(?<=[.!?;])\s+', l)
            best = min(range(1, len(sents)), key=lambda i: abs(len(' '.join(sents[:i]).split()) - len(' '.join(sents[i:]).split()))) if len(sents) > 1 else None
            if best:
                flat += [' '.join(sents[:best]), ' '.join(sents[best:])]
                continue
        flat.append(l)
    ids = []
    for k, l in enumerate(flat):
        bid = f's{n:02d}{"abcdefghij"[k]}'
        beats[bid] = l
        ids.append(bid)
    scenes[f'scene{n}'] = ids
nar = {"engine": "edge", "voice": "id-ID-GadisNeural", "rate": "+8%", "beats": beats}
json.dump(nar, open('content/briefing/ch01/narration.id.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(scenes, open('content/briefing/ch01/scenes.json', 'w'), indent=1)
print({k: len(v) for k, v in scenes.items()}, sum(len(b.split()) for b in beats.values()), 'words')
