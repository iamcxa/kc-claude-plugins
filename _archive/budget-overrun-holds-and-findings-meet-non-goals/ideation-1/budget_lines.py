import sys,re,pathlib,collections
root=pathlib.Path(sys.argv[1])
units=collections.Counter(); rows=[]
for p in sorted(root.rglob('*.md')):
    if '/review/' in str(p) or '/dispatch/' in str(p): continue
    t=p.read_text(errors='replace').split('\n')
    if not t or t[0]!='---': continue
    b=None
    for i,l in enumerate(t):
        if re.match(r'^## Budget\s*$',l):
            for m in t[i+1:i+6]:
                if m.strip() and not m.startswith('## '): b=m.strip(); break
            break
        m=re.match(r'^(?:- )?Budget:\s*(.*)',l)
        if m and '<approved' not in l: b=m.group(1); break
    if b is None: continue
    low=b.lower()
    u=[k for k,pat in [('pr',r'\bprs?\b|pull request'),('cycle',r'cycle|round|pass'),('day/hour',r'\bday|\bhour|working'),('run',r'\bruns?\b'),('task',r'\btasks?\b'),('lines/files',r'\blines?\b|\bfiles?\b'),('money/tokens',r'\$|usd|token|cost|sms')] if re.search(pat,low)]
    for k in u or ['other']: units[k]+=1
    rows.append((str(p.relative_to(root)),','.join(u) or 'other',b[:110]))
print(len(rows),'tasks with a budget'); print(dict(units))
for r in rows: print(' | '.join(r))
