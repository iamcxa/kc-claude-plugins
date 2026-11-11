import sys,re,pathlib,json,collections
sys.path.insert(0,'/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts')
import role_triggers as rt
root=pathlib.Path(sys.argv[1]); only=sys.argv[2] if len(sys.argv)>2 else None
H2=re.compile(r'^## ')
res=[]
for base in [root, root/'_archive']:
    if not base.exists() or (only=='archive' and base==root): continue
    for p in sorted(base.iterdir()):
        f=p/'index.md' if p.is_dir() else p
        if not (f.suffix=='.md' and f.exists()): continue
        t=f.read_text(errors='replace')
        if not t.startswith('---') or 'variant: kc-dev-flow-2' not in t.split('\n---',1)[0]: continue
        name=p.name if p.is_dir() else p.stem
        dd=(base/name/'dispatch')
        impl_d=max([int(m.group(1)) for x in (dd.iterdir() if dd.is_dir() else []) for m in [re.match(r'^implementation-(\d+)\.md$',x.name)] if m] or [0])
        impl_r=0; vals=[]; cur=None
        for l in rt.outside_fences(t):
            if H2.match(l):
                cur=None
                if rt.IMPLEMENTATION_REPORT.match(l): impl_r+=1
                if rt.VALIDATION_REPORT.match(l): vals.append(0); cur='v'
            elif cur=='v' and re.match(r'^[ \t]*[-*][ \t]+\*{0,2}F[0-9]+\*{0,2}[ \t]*[:(—–-]?[ \t]*Material\b',l): vals[-1]+=1
        res.append(dict(task=name,impl=max(impl_d,impl_r),impl_d=impl_d,valmat=sum(1 for v in vals if v),matf=sum(vals),val=len(vals)))
n=len(res); c=lambda f:sum(1 for r in res if f(r))
print(root.parent.name if root.name=='.spacedock-state' else root.name, only or 'all', 'dev2 tasks',n,'| impl>=1',c(lambda r:r['impl']>=1))
print('  hold@2nd impl',c(lambda r:r['impl']>=2),'| hold@3rd',c(lambda r:r['impl']>=3),'| hold@4th',c(lambda r:r['impl']>=4),'| CE 4 repair passes (impl>=5)',c(lambda r:r['impl']>=5))
print('  any Material validation',c(lambda r:r['valmat']>=1),'(findings',sum(r['matf'] for r in res),') | step-back 2 Material validations',c(lambda r:r['valmat']>=2))
json.dump(res,open('/tmp/r2-'+(root.name if root.name!='.spacedock-state' else 'kcp')+'-'+(only or 'all')+'.json','w'))
