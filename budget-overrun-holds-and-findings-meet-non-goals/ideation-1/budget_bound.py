import re,sys,json,pathlib,collections
NUM={'one':1,'a':1,'an':1,'two':2,'three':3,'four':4,'five':5,'six':6,'single':1}
UNIT=r'(?:cycles?|rounds?|pass(?:es)?|dispatch(?:es)?)'
STAGES=('ideation','implementation','validation')
def parse(line):
    """Return {stage: bound} from a Budget line, or None when it states no cycle count."""
    l=line.lower()
    m=re.search(rf'\b(\d+|one|two|three|four|five|six|a|single)\s+{UNIT}\s+per\s+stage',l)
    if m:
        n=int(m.group(1)) if m.group(1).isdigit() else NUM[m.group(1)]
        return {s:n for s in STAGES}
    out={}
    for m in re.finditer(rf'\b(\d+|one|two|three|four|five|six|single)\s+(?:short\s+|small\s+)?(ideation|implementation|validation)(?:\s+{UNIT})?',l):
        n=int(m.group(1)) if m.group(1).isdigit() else NUM[m.group(1)]
        out[m.group(2)]=n
    return out or None
if __name__=='__main__':
    for r in sys.argv[1:]:
        root=pathlib.Path(r); held=[]; parsed=0; total=0; unparsed=collections.Counter()
        for base in [root, root/'_archive']:
            if not base.exists(): continue
            for d in sorted(base.iterdir()):
                dd=d/'dispatch'
                if not (d.is_dir() and dd.is_dir()): continue
                tf=base/(d.name+'.md')
                if not tf.exists(): tf=d/'index.md'
                if not tf.exists(): continue
                t=tf.read_text(errors='replace'); L=t.split('\n'); b=None
                for i,l in enumerate(L):
                    if re.match(r'^## Budget\s*$',l): b=next((x.strip() for x in L[i+1:i+6] if x.strip()),''); break
                    mm=re.match(r'^(?:- )?Budget:\s*(.*)',l)
                    if mm: b=mm.group(1); break
                if b is None: continue
                c=collections.Counter()
                for f in dd.iterdir():
                    m=re.match(r'^(ideation|implementation|validation)-(\d+)\.md$',f.name)
                    if m: c[m.group(1)]=max(c[m.group(1)],int(m.group(2)))
                if not sum(c.values()): continue
                total+=1; p=parse(b)
                if p is None: unparsed[b[:50]]+=1; continue
                parsed+=1
                over=[(s,c[s],p[s]) for s in STAGES if s in p and c[s]>p[s]]
                if over: held.append((d.name,over,b[:60]))
        print(f'== {root.name}: tasks with dispatch records and a Budget line {total}; cycle bound parsed {parsed}; would hold at first overrun {len(held)}')
        for h in held: print('   ',h)
        print('   unparsed sample:',unparsed.most_common(4))
