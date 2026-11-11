"""Prints the heard time of every word of a beat (from the voice cache), to place page actions: words.py dua"""
import json, sys
c = json.load(open('content/spirometri/ch03/narration.id.timings.json', encoding='utf-8'))
b = c[sys.argv[1]]
print('marks', b['marks'], 'dur', b['dur'])
print(' '.join(f"{t:.1f}:{w}" for t, w in b['words']))
