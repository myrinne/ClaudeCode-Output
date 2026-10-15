import re,glob,os,difflib,json
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')
def parse():
    items=[]
    for f in sorted(glob.glob(os.path.join(D,'*.txt'))):
        txt=open(f,encoding='utf-8').read()
        for blk in re.split(r'(?m)^(?=### )',txt):
            if not blk.strip(): continue
            lines=blk.strip().split('\n')
            h=[x.strip() for x in lines[0][4:].split('|')]
            it=dict(type=h[0],topic=h[1],exams=[e.strip() for e in h[2].split(',')],Q='',O=[],A='',S=[],D=[],N=[],file=os.path.basename(f))
            last=None
            for ln in lines[1:]:
                m=re.match(r'^([QOASDN]): ?(.*)$',ln)
                if m:
                    k,v=m.groups(); last=k
                    if k in 'QA': it[k]=(it[k]+' '+v).strip()
                    else: it[k].append(v)
                elif ln.strip() and last:
                    if last in 'QA': it[last]+=' '+ln.strip()
                    else: it[last][-1]+=' '+ln.strip()
            items.append(it)
    return items
STOP=set('the a an of to in is are which following what and or for be by with that this as on at from it its his her he she was were can will'.split())
def norm(s):
    s=s.lower(); s=re.sub(r'\[recall\]|\(kasus[^)]*\)|\(opsi[^)]*\)|\(redaksi[^)]*\)','',s)
    s=re.sub(r'[^a-z0-9 ]',' ',s); return ' '.join(w for w in s.split() if w not in STOP)
def sim(a,b):
    na,nb=norm(a),norm(b)
    r=difflib.SequenceMatcher(None,na,nb).ratio()
    A,B=set(na.split()),set(nb.split())
    j=len(A&B)/max(1,len(A|B))
    return max(r,j)
if __name__=='__main__':
    items=parse(); print(len(items))
    fam=lambda t:{'stem':'stem','osce':'osce','oral':'osce','case':'osce','mcq':'mcq','short':'short','essay':'short'}[t]
    pairs=[]
    for i in range(len(items)):
        for j in range(i+1,len(items)):
            a,b=items[i],items[j]
            if fam(a['type'])!=fam(b['type']): continue
            s=sim(a['Q'],b['Q'])
            if s>=0.55: pairs.append((round(s,2),i,j))
    json.dump(pairs,open('pairs.json','w'))
    for s,i,j in sorted(pairs,reverse=True):
        a,b=items[i],items[j]
        if a['exams']==b['exams']: tag='SAME-EXAM'
        else: tag=''
        print(f"{s} {i}/{j} {tag}\n  [{','.join(a['exams'])}] {a['Q'][:110]}\n   ->{a['A'][:50]}\n  [{','.join(b['exams'])}] {b['Q'][:110]}\n   ->{b['A'][:50]}")
