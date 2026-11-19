"""One-off: point every arm icon at FOREARM() (lib/forearm.js) in ch01, ch02 and the upright book. Run from 'Video Briefing Pekerja/'."""
import re, shutil

old = re.compile(r"pf\(`<rect x=\"-100\" y=\"-38\" width=\"190\" height=\"76\" rx=\"38\" fill=\"#e8be98\"/><ellipse cx=\"82\" cy=\"0\" rx=\"30\" ry=\"34\" fill=\"#e8be98\"/>`\)")
files = ['site/briefing/ch01/scene5.js', 'site/briefing/ch01/scene6.js', 'site/briefing/ch01/scene7.js',
         'site/briefing/ch02/scene2.js', 'site/pengingat/lib/pengingat.js']
for f in files:
    s = open(f, encoding='utf-8').read()
    if f.endswith('scene5.js'):
        s2 = s.replace("const arm = (tat) => " + old.pattern.replace('\\', ''), "const arm = (tat) => FOREARM({ tat })")
        s2 = re.sub(r"const arm = \(tat\) => pf\(`<rect x=\"-100\".*?`\)", "const arm = (tat) => FOREARM({ tat })", s, count=1)
    else:
        s2 = old.sub('FOREARM()', s)
    assert s2 != s, f
    open(f, 'w', encoding='utf-8').write(s2)
    print('arm ->', f)

# scene 9: the arm with a sleeve (hand to the left, sleeve at the right), as before
f = 'site/briefing/ch01/scene9.js'
s = open(f, encoding='utf-8').read()
s2 = re.sub(r"const S9_ARM = `.*?`;", "const S9_ARM = `<g transform=\"scale(-1,1)\">${FOREARM({ sleeve: true })}</g>`;", s, count=1, flags=re.S)
assert s2 != s
open(f, 'w', encoding='utf-8').write(s2); print('arm ->', f)

# load forearm.js after cast_briefing.js / before pengingat.js
for f, anchor in (('site/briefing/ch01/index.html', '<script src="../lib/cast_briefing.js"></script>'),
                  ('site/briefing/ch02/index.html', '<script src="../lib/cast_briefing.js"></script>'),
                  ('site/pengingat/ch01/index.html', '<script src="../lib/cast_briefing.js"></script>')):
    s = open(f, encoding='utf-8').read()
    tag = '<script src="../lib/forearm.js"></script>'
    if tag not in s:
        s = s.replace(anchor, anchor + '\n' + tag, 1)
        open(f, 'w', encoding='utf-8').write(s)
    print('forearm.js loaded in', f)
shutil.copy('site/briefing/lib/forearm.js', 'site/pengingat/lib/forearm.js')
