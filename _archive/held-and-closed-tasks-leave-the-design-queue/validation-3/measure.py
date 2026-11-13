#!/usr/bin/env python3
"""Independent recount of candidate output; needs Python 3, PyYAML and Spacedock."""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
import yaml
a=argparse.ArgumentParser()
for k in ('candidate','workflow','scratch','output'): a.add_argument('--'+k,required=True,type=Path)
a=a.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(a.candidate/'kc-dev-flow-2/scripts'))
import pr_watch
from decision_ledger import split_task,gate_entries
def git_init(path):
    subprocess.run(['git','-C',str(path),'init','-q'],check=True,capture_output=True)
def pathof(base,slug):
    flat=base/(slug+'.md')
    return flat if flat.exists() else base/slug/'index.md'
native=pr_watch.held_rows(a.workflow)
assert len(native)==15
stages=[r['name'] for r in yaml.safe_load((a.workflow/'README.md').read_text().split('\n---\n',1)[0].lstrip('-\n'))['stages']['states']]
a.scratch.mkdir(parents=True,exist_ok=True)
# A separate native workflow containing one existing held task.
one=a.scratch/'one'; wf=one/'docs/dev2'; st=wf/'.spacedock-state';st.mkdir(parents=True)
(wf/'README.md').write_bytes((a.workflow/'README.md').read_bytes())
(st/'README.md').write_bytes((a.workflow/'.spacedock-state/README.md').read_bytes())
r=sorted(native,key=lambda r:r['slug'])[0]; original=pathof(a.workflow/'.spacedock-state',r['slug'])
(st/(r['slug']+'.md')).write_bytes(original.read_bytes())
git_init(one);git_init(st)
single=pr_watch.held_rows(wf)
assert len(single)==1
large=[dict(slug=f'synthetic-{i:03d}-{stage}',status=stage) for stage in stages for i in range(25)]
results=[]
for label,rows,source in [('one',single,st),('current',native,a.workflow/'.spacedock-state'),('larger',large,None)]:
    found={}; copies=a.scratch/label/'copies'; copies.mkdir(parents=True)
    for row in rows:
        slug=row['slug']; target=copies/(slug+'.md')
        if source:
            text=pathof(source,slug).read_text()
            fm,body=split_task(text)
            reasons=[g['reason'] for g in gate_entries(fm) if g.get('decision')=='hold']
            # Remove only an existing projection section from our scratch input.
            body=re.sub(r'^## Held\n.*?(?=^## |\Z)','',body,flags=re.M|re.S)
            front=text.split('\n---\n',1)[0]
            projected=front+'\n---\n'+body+'\n## Held\nReopen when: '+reasons[-1].splitlines()[0]+'\n'
            target.write_text(projected)
            assert target.read_text().split('\n---\n',1)[0]==front
        else:
            target.write_text('---\nstatus: '+row['status']+'\n---\n## Held\nClosed: synthetic finished\n## Captain amendments\nCaptain: synthetic finished\n')
        found[slug]=target
    lines=pr_watch.held_lines(rows,found)
    assert len(lines)==1
    fact=lines[0]+'\n'; path=a.output/(label+'-fact.txt');path.write_text(fact)
    wc=subprocess.check_output(['wc','-w',str(path)],text=True).strip()
    words=int(wc.split()[0]); assert words==len(fact.split())
    assert all(fact.count(r['slug'])==1 for r in rows)
    limit=len(rows)+20
    assert words<=limit
    over=a.output/(label+'-over-bound.txt'); over.write_text(fact+' extra'*(limit+1-words))
    counter=int(subprocess.check_output(['wc','-w',str(over)],text=True).split()[0])
    rejected=counter>limit
    assert rejected and counter==limit+1
    result=dict(case=label,held=len(rows),stages=len({r['status'] for r in rows}),words=words,maximum=limit,
                fixed_words=words-len(rows)-len({r['status'] for r in rows}),wc_output=wc,
                exactly_once=True,over_bound_words=counter,over_bound_rejected=rejected,synthetic=source is None)
    results.append(result);print(f"{label.upper()} held={len(rows)} words={words} maximum={limit} PASS; over-bound {counter} REJECTED",flush=True)
assert results[-1]['stages']==len(stages)==5
(a.output/'measurements.json').write_text(json.dumps(results,indent=2)+'\n')

