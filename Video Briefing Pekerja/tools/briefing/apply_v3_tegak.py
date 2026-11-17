"""One-off: apply the v3 changes to site/pengingat/ch01/index.html (new 'waktu' beat, renumbered ids, no text outlines).
Run from 'Video Briefing Pekerja/'. Safe to run once."""
import re

p = 'site/pengingat/ch01/index.html'
s = open(p, encoding='utf-8').read()
assert "['b8'," not in s, 'already applied'

# 1. no black (or light) outlines on any on-screen text
s = s.replace(', stroke: DARK', '').replace(', stroke: LIGHT', '')

# 2. renumber beats b7..b2 -> b8..b3 (highest first) and the lip-sync clip of the contact beat
for n in range(7, 1, -1):
    s = s.replace(f"['b{n}',", f"['b{n + 1}',")
s = s.replace("mouthAt('b7', q - PRE)", "mouthAt('b8', q - PRE)")

# 3. the hook no longer says "Ingat 4 hal": that moves to the new beat
s = s.replace("    word(s, 'Ingat 4 hal', CX, 965, m('four'), { size: 130, fill: GREEN });\n    sfx(BEAT_ID, m('four'), 'chime', .6);\n", '')

# 4. the new beat: when the examination and the blood draw happen
waktu = """  ['b2', 'Kapan pemeriksaan', (m, D) => {
    const s = base();
    word(s, 'Setelah shift', CX, 330, m('shift'), { size: 170, fill: TEAL });
    word(s, 'selesai', CX, 485, m('shift', .55), { size: 170, fill: TEAL });
    icon(s, IC.clock, CX, 690, 3.0, m('shift', .2));
    icon(s, IC.blood, 130, 990, 2.4, m('blood'));
    band(s, ['Darah diambil', '30-60 menit', 'setelah shift'], 920, m('blood'), { size: 62, fill: RED, colour: '#fff' });
    word(s, 'Ingat 4 hal', CX, 1190, m('four'), { size: 130, fill: GREEN });
    sfx(BEAT_ID, m('four'), 'chime', .6);
    sfx(BEAT_ID, m('blood'), 'chime', .5);
    const bpk = bapakPuppet(s), ibu = ibuPuppet(s);
    stopClock(D, (q, f) => {
      bpk.pose({ x: 230, y: 1500, s: .9, look: .4, eyeX: .5, mouth: 'smile', shut: blinking(q, [2.2, 6.4]), ...alive(q, 1), armL: 6, armR: 6 }, f);
      ibu.pose({ x: 670, y: 1500, s: .9, look: -.4, eyeX: -.5, mouth: 'smile', shut: blinking(q, [3.4, 7.2]), ...alive(q, 2), armL: 6, armR: 6 }, f);
    });
  }, { pre: PRE }],

"""
marker = "  ['b3', '1 · 24 jam: losion'"
assert marker in s
s = s.replace(marker, waktu + marker)
open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count("stroke: "))
