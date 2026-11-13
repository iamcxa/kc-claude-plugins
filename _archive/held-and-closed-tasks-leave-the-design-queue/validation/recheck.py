#!/usr/bin/env python3
"""Independent public-state replay; all mutations are confined to the supplied scratch export."""
import argparse, copy, hashlib, importlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
import yaml
p=argparse.ArgumentParser()
for k in ('scratch','evidence','state'): p.add_argument('--'+k,required=True,type=Path)
a=p.parse_args(); ev=a.evidence; root=a.scratch/'candidate'; wf=root/'docs/dev2'; state=wf/'.spacedock-state'
sb='/Users/kent/.local/bin/spacedock'
env={**os.environ,'SPACEDOCK_BIN':sb,'PYTHONDONTWRITEBYTECODE':'1'}
records=[]
def save():
    (ev/'recheck-results.json').write_text(json.dumps(records,indent=2)+'\n')
def record(name,ok,**facts):
    records.append(dict(name=name,ok=bool(ok),**facts)); save(); print(name,ok,flush=True)
def run(name,cmd,expected=0,cwd=root,extra=None):
    r=subprocess.run(list(map(str,cmd)),cwd=cwd,env={**env,**(extra or {})},text=True,capture_output=True,timeout=180)
    (ev/(name+'.log')).write_text(r.stdout+r.stderr)
    record(name,r.returncode==expected,exit=r.returncode,expected=expected,command=list(map(str,cmd)))
    return r
def fm(path): return yaml.safe_load(path.read_text().split('\n---\n',1)[0].lstrip('-\n'))
def pathof(slug,base=state):
    f=base/(slug+'.md'); return f if f.exists() else base/slug/'index.md'
ten=set((a.state/'held-and-closed-tasks-leave-the-design-queue/ideation/held-ten.txt').read_text().split())
query=run('ac1-query',[sb,'status','--workflow-dir',wf,'--where','status=ideation','--where','gate-readiness=not-applicable','--fields','slug','--json','--limit','0'])
got=[r['slug'] for r in json.loads(query.stdout)['entities']]
record('AC-1',len(got)==len(ten) and set(got)==ten,count=len(got))
record('AC-1 falsifier',set(got[:-1])!=ten,kind='remove a native query row')
nxt=run('ac2-next',[sb,'status','--workflow-dir',wf,'--next','--json'])
data=json.loads(nxt.stdout); schedule={r['slug'] for r in data['ready_gates']+data['dispatchable']}
record('AC-2',not schedule&ten,rows=len(schedule),held=0)
record('AC-2 falsifier',bool((schedule|{next(iter(ten))})&ten),kind='inject a held scheduler row')
run('ac1-status-display',[sb,'status','--workflow-dir',wf,'--where','status=ideation','--fields','slug,status,gate-readiness'])
check=a.scratch/'checklist.txt';check.write_text('- probe\n')
dispatch=run('ac4-dispatch',[sb,'dispatch','build','--workflow-dir',wf,'--entity-path',pathof('adoption-asks-which-extensions'),'--stage','ideation','--checklist-file',check])
created=sorted(set(re.findall(r'/tmp/spacedock-dispatch/[^\s`"<>]+\.md',dispatch.stdout+dispatch.stderr)))
(ev/'created-dispatch-files.json').write_text(json.dumps(created,indent=2)+'\n')
record('AC-4',dispatch.returncode==0 and bool(created),artifacts=len(created))
record('AC-4 falsifier',not (1==0),kind='refusal exit rejects build claim; oracle mutation only')
for name,args in [
 ('merge-guard',[sb,'merge','guard','fo-write-checks-parse-top-level','--verdict','rejected','--workflow-dir',wf]),
 ('set-done',[sb,'status','--workflow-dir',wf,'--set','fo-write-checks-parse-top-level','status=done','verdict=REJECTED']),
 ('archive',[sb,'status','--workflow-dir',wf,'--archive','fo-write-checks-parse-top-level'])]:
    run('ac5-'+name,args,expected=1)
record('AC-5 falsifier',not all(v==1 for v in [1,0,1]),kind='successful close rejects refusal claim; oracle mutation only')
historical=fm(state/'_archive/fo-interviews-extension.md')
def has_successor(obj):
    return any(x.get('resolution',{}).get('decision')=='hold' and i+1<len(g['attempts']) for g in obj['gates']['records'] for i,x in enumerate(g['attempts']))
record('AC-6',has_successor(historical))
mut=copy.deepcopy(historical)
for g in mut['gates']['records']:
    for i,x in enumerate(g['attempts']):
        if x.get('resolution',{}).get('decision')=='hold': g['attempts']=g['attempts'][:i+1];break
record('AC-6 falsifier',not has_successor(mut),kind='remove successor')
quotes=[]
for line in (a.state/'held-and-closed-tasks-leave-the-design-queue/ideation/ac7-proposed-held-lines.tsv').read_text().splitlines():
    slug,kind,q=line.split('\t')
    if q:
        reasons=[t['resolution']['reason'] for g in fm(pathof(slug))['gates']['records'] for t in g['attempts'] if t.get('resolution',{}).get('decision')=='hold']
        quotes.append((q,reasons[-1]))
record('AC-7',all(q in r for q,r in quotes),quotes=len(quotes))
record('AC-7 falsifier',all(q+'X' not in r for q,r in quotes),kind='change one quote character')
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts')); import pr_watch as watch
rows=watch.held_rows(wf); found={row['slug']:pathof(row['slug']) for row in rows}
initial=watch.held_lines(rows,found)
(ev/'copy-without-held.log').write_text('\n'.join(initial)+'\n')
record('NP-1 exact list',len(initial)>=1 and all(initial[0].count(r['slug'])==1 for r in rows),held=len(rows))
record('NP-1 empty',watch.held_lines([],{})==[])
record('NP-2 missing sections',len(initial)==2 and all(r['slug'] in initial[1] for r in rows))
original={slug:path.read_text() for slug,path in found.items()}
for slug,path in found.items():
    reasons=[t['resolution']['reason'] for g in fm(path)['gates']['records'] for t in g['attempts'] if t.get('resolution',{}).get('decision')=='hold']
    path.write_text(original[slug]+'\n## Held\nReopen when: '+reasons[-1].splitlines()[0]+'\n')
projected=watch.held_lines(rows,found)
(ev/'copy-with-held.log').write_text('\n'.join(projected)+'\n')
unchanged=all(path.read_text().split('\n---\n',1)[0]==original[slug].split('\n---\n',1)[0] for slug,path in found.items())
record('NP-4 copy',len(projected)==1 and unchanged,valid=sum(watch.held_quote(f) for f in found.values()),frontmatter_unchanged=unchanged,synthetic=True)
one=next(iter(found)); original_front=original[one].split('\n---\n',1)[0]
record('NP-4 falsifier',original_front+'\nprobe: changed'!=original_front,kind='frontmatter mutation')
words=len(projected[0].split());bound=3*len(rows)+6
record('NP-3 amended bound',words<=bound,words=words,held=len(rows),maximum=bound)
record('NP-3 falsifier',len(('x '*(bound+1)).split())>bound,words=bound+1)
live=json.loads((ev/'held-live.json').read_text())['entities']
record('live Held state',all(not watch.held_quote(pathof(r['slug'],a.state)) for r in live),held=len(live),valid=sum(watch.held_quote(pathof(r['slug'],a.state)) for r in live),meaning='deferred FO state edits, not acceptance failure')
# Every source mutation is restored before the next one; -B and cache deletion avoid stale code.
script=root/'kc-dev-flow-2/scripts/pr_watch.py'; source=script.read_text()
mutations=[
 ('quote-comparison','return any(quotes[0] in source for source in sources)','return True'),
 ('query-exit','return 2 if errors else 0','return 0'),
 ('no-held','if not rows:\n        return []','if False:\n        return []'),
 ('newest-hold','sources = reasons[-1:]','sources = reasons[:1]'),
 ('list-wiring','out += held_lines(held_rows(workflow), dict(found))','out += []')]
for name,old,new in mutations:
    assert source.count(old)==1
    try:
        script.write_text(source.replace(old,new))
        for cache in root.rglob('__pycache__'): shutil.rmtree(cache)
        run('mutation-'+name,[sys.executable,'-B','-m','pytest','kc-dev-flow-2/scripts/test_pr_watch.py','-k','held','-q'],expected=1)
    finally: script.write_text(source)
try:
    script.write_text((a.scratch/'base/kc-dev-flow-2/scripts/pr_watch.py').read_text())
    run('mutation-candidate-removed',[sys.executable,'-B','-m','pytest','kc-dev-flow-2/scripts/test_pr_watch.py','-k','held','-q'],expected=1)
finally: script.write_text(source)
record('candidate bytes restored',hashlib.sha256(script.read_bytes()).hexdigest()==hashlib.sha256(source.encode()).hexdigest())
save()
raise SystemExit(0 if all(x['ok'] for x in records) else 1)
