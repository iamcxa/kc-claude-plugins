import contextlib, importlib.util, io, json, re, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]); out=Path('/tmp/budget-implementation'); scripts=root/'kc-dev-flow-2/scripts';sys.path.insert(0,str(scripts))
import design_surfaces as candidate
basefile=out/'base_design_surfaces.py'
basefile.write_bytes(subprocess.check_output(['git','-C',str(root),'show','e8664a72b0f904e5dda3c391d52ab3abaca876b4:kc-dev-flow-2/scripts/design_surfaces.py']))
spec=importlib.util.spec_from_file_location('base_design',basefile);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
rows=[]
for corpus in (out/'corpus-md').iterdir():
    for path in sorted(corpus.rglob('*.md')):
        rel=path.relative_to(corpus).as_posix()
        if not re.fullmatch(r'(?:_archive/)?(?:[^/]+\.md|[^/]+/index\.md)',rel):continue
        text=path.read_text()
        if not text.startswith('---\n'):continue
        for seed in (False,True):
            before=base.check_task(path,seed=seed);after=candidate.check_task(path,seed=seed)
            added=[e for e in after if e not in before];removed=[e for e in before if e not in after]
            assert not removed,(rel,removed)
            assert all('Worth questions' in e or 'Budget must start' in e for e in added),(rel,added)
            rows.append(dict(corpus=corpus.name,task=rel,mode='seed' if seed else 'design',base_exit=int(bool(before)),candidate_exit=int(bool(after)),added=added))
summary={name:{mode:dict(tasks=sum(r['corpus']==name and r['mode']==mode for r in rows),new_refusals=sum(r['corpus']==name and r['mode']==mode and not r['base_exit'] and r['candidate_exit'] for r in rows),changed_messages=sum(r['corpus']==name and r['mode']==mode and bool(r['added']) for r in rows)) for mode in ('seed','design')} for name in ('dev2','qnow','relay','web')}
(out/'corpus-check.json').write_text(json.dumps(dict(summary=summary,rows=rows),indent=2)+'\n')
print(json.dumps(summary,indent=2))
