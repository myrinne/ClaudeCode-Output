import re, json, difflib
import parse

GROUPS = """
543,479,586; 480,587; 544,485,591; 486,592; 484,590; 163,251; 224,454; 526,629; 506,609; 637,529;
104,20,76; 75,103; 162,525; 483,589; 478,585; 186,177;
511,547; 194,404,219,464; 306,235; 466,160,365; 16,69,102; 300,231; 66,99,222; 114,305,15,250; 26,38;
259,301,185; 68,101; 262,353; 138,248;
127,240,325,434,70; 436,18,129,201; 17,71; 469,528,190,636; 167,370; 169,327,460; 165,252; 362,383,549,626; 168,627;
492,597; 125,246,267; 336,293,452; 292,349; 519,621,517; 9,65; 131,481; 278,369; 12,64; 14,67,100; 176,253;
295,347; 11,63; 110,550; 491,596;
268*,411,461,241; 256,279,330; 21,191; 237,113; 0,72; 298,361; 619,516;
493,598; 500,546,601; 489,545,593,215,463; 80,27; 135,28; 594,216;
137*,238,323,432; 23,189; 86,132,326,449; 283,350; 35,87,139; 303,427,443; 25,39,88; 265,355; 7,53; 346,402;
495,599; 272,366; 299,220;
48,93; 276,123,247;
472,579; 473,580; 474,581; 475,582; 551,120; 41,311; 324,239; 307,431; 446,534,632,218; 364,394; 174,397,459;
280,331,242; 205,462; 263,354,389; 277,329; 206,456; 470,578; 502,606; 612,510;
522,624; 521,623; 523,625; 232,379,309; 508,611; 505,608; 210,409; 342,458; 520,622; 555,642; 322,258;
29,32; 567,576; 46,91;
145,249; 318,45,90; 319,62,98,448,199,183; 3,57,95; 315,182,447,527,630; 455,198,203; 535,631,204; 260,49,335;
270,172,233,408; 530,628; 635,531,212; 121,236; 42,435,197; 97,60; 58,426; 588,482,55,111; 136,228,302;
304,51,229; 8,54,94; 289,61,230; 308,96; 503,607; 433,184; 44,89,328; 424,320
"""
ORDER = ['2016','2016-Remed','±2020','2020','2021 (Des)','2021 (recall)','Awal 2022','2022','Remed Agt 2022','Des 2022',
         '2023','Juli 2023','Feb 2024','Okt 2024','Okt 2024-Remed','Okt 2025','Feb 2026','UKOM 22 (2026)']
LABEL = {'2021 (recall)':'2021 (recall peserta)','±2020':'±2020 (catatan peserta)'}

def tok(s): return set(re.sub(r'[^a-z0-9 ]',' ',s.lower()).split())
def same_ans(a,b):
    a0,b0=a.lower().strip(' .'),b.lower().strip(' .')
    if a0[:5]==b0[:5] or a0 in b0 or b0 in a0: return True
    if a0.startswith(('true','false')) or b0.startswith(('true','false')): return True
    ini = lambda s: ''.join(w[0] for w in re.findall(r'[a-z]+', s))
    if re.sub(r'[^a-z]','',a0) in ini(b0) or re.sub(r'[^a-z]','',b0) in ini(a0): return True
    A,B=tok(a),tok(b)
    if not A or not B: return True
    return len(A&B)/min(len(A),len(B)) >= 0.5

def merge():
    it = parse.parse()
    raw = [[x.strip() for x in g.split(',')] for g in re.split(r'[;\n]', GROUPS) if g.strip()]
    groups = [[int(x.rstrip('*')) for x in g] for g in raw]
    forced = {int(x.rstrip('*')) for g in raw for x in g if x.endswith('*')}
    used = set()
    for g in groups:
        for i in g:
            assert i not in used, f"dup index {i}"
            used.add(i)
    out = []
    for g in groups + [[i] for i in range(len(it)) if i not in used]:
        mem = [it[i] for i in g]
        fr = [it[i] for i in g if i in forced]
        clean = lambda q: not re.search(r'\[recall|\(versi|\(opsi|\(redaksi', q, re.I)
        rep = fr[0] if fr else max(mem, key=lambda x: (len(x['O']), bool(x['A']), clean(x['Q']), x['Q'].startswith('(Kasus'), len(x['Q'])))
        m = json.loads(json.dumps(rep))
        exams = []
        for x in mem:
            for e in x['exams']:
                if e not in exams: exams.append(e)
        m['exams'] = sorted(exams, key=lambda e: ORDER.index(e))
        if not m['A']:
            for x in mem:
                if x['A']: m['A'] = x['A']; break
        D, N, S = list(m['D']), list(m['N']), list(m['S'])
        for x in mem:
            if x is rep: continue
            for d in x['D']:
                if d not in D: D.append(d)
            for n in x['N']:
                if n not in N: N.append(n)
            first = re.sub(r'[^a-z]','',x['A'].lower().split()[0]) if x['A'] else ''
            if x['A'] and m['A'] and not same_ans(x['A'], m['A']) and not any(first and first in d.lower() for d in D):
                D.append(f"Jawaban versi {', '.join(LABEL.get(e,e) for e in x['exams'])}: {x['A']}")
        fmts = {}
        for x in mem:
            f = 'pilihan ganda' if x['type']=='mcq' else ('isian' if x['type'] in ('short','essay') else None)
            if f:
                for e in x['exams']: fmts.setdefault(f, []).append(e)
        if len(fmts) > 1 and m['type'] in ('mcq','short','essay'):
            N.append('Format berbeda antar ujian: ' + '; '.join(f"{k} ({', '.join(LABEL.get(e,e) for e in sorted(set(v), key=ORDER.index))})" for k,v in fmts.items()))
        m['D'], m['N'], m['S'] = D, N, S
        m['members'] = g
        out.append(m)
    return out

if __name__ == '__main__':
    out = merge()
    import collections
    print(len(out), collections.Counter(x['type'] for x in out))
    print(sum(1 for x in out if len(x['exams'])>1), 'items appear in >1 exam')
