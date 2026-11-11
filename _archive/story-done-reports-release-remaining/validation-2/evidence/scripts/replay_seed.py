import os
from pathlib import Path
import importlib.util,io,contextlib,json,sys,subprocess
OUT=Path(os.environ.get('EVIDENCE_ROOT','/tmp/opencode-story-done'))
CAND=Path(os.environ.get('DEV2_WT','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining-dev2'))/'kc-dev-flow-2/scripts'
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
cand=load(CAND/'design_surfaces.py','candidate_design');base=load(OUT/'base/kc-dev-flow-2/scripts/design_surfaces.py','base_design')
results={}
for name in ['relay','qnow','local']:
 wf=OUT/'replays'/name/'docs/dev2';state=wf/'.spacedock-state'
 paths=sorted(p for p in state.rglob('*.md') if (p.parent==state or p.parent==state/'_archive' or (p.name=='index.md' and p.parent.parent in (state,state/'_archive'))) and p.name!='README.md' and p.read_text().startswith('---\n') and any(x.startswith('status:') for x in (cand.decision_ledger.split_task(p.read_text())[0] or [])))
 refused=[];changed=[];consistent=[]
 for path in paths:
  errors=cand.check_task(path,seed=True)
  if any("needs a 'Story:' line" in x for x in errors):refused.append(str(path.relative_to(state)))
  for seed in [True,False]:
   old=base.check_task(path,seed=seed);new=cand.check_task(path,seed=seed)
   if old!=new:changed.append({'path':str(path.relative_to(state)),'seed':seed,'added':[e for e in new if e not in old],'removed':[e for e in old if e not in new]})
  if 'Story:' in path.read_text() and path.name in ['entry-without-name-field.md','own-comments-follow-account.md']:
   consistent.append({'path':str(path.relative_to(state)),'errors':[e for e in cand.check_task(path) if "'Story:'" in e]})
 result={'tasks':len(paths),'story_refusals':len(refused),'refused':refused,'changed':changed,'recorded_consistency':consistent}
 if name!='local':
  cp=subprocess.run(['spacedock','status','--workflow-dir',str(wf),'--next','--json'],capture_output=True,text=True);(OUT/(name+'-next.json')).write_text(cp.stdout)
  assert cp.returncode==0,cp.stderr
  ready=json.loads(cp.stdout)['ready_gates'];by_slug={p.stem if p.name!='index.md' else p.parent.name:p for p in paths}
  names=[r['slug'] for r in ready if r.get('current')=='backlog' and r.get('readiness')=='needs-preparation' and r['slug'] in by_slug and cand.FO_HEADING.search(by_slug[r['slug']].read_text()) and any("needs a 'Story:' line" in e for e in cand.check_task(by_slug[r['slug']],seed=True))]
  result['idle_names']=names;result['idle_count']=len(names)
 results[name]=result
(OUT/'seed-replay.json').write_text(json.dumps(results,indent=2)+'\n')
for n,r in results.items():print(n,r['tasks'],r['story_refusals'],r.get('idle_count'),len(r['changed']))
assert [results[n]['story_refusals'] for n in results]==[135,163,0]
assert [results[n]['idle_count'] for n in ['relay','qnow']]==[31,11]
assert all(not r['removed'] and all("'Story:'" in x for x in r['added']) for rs in results.values() for r in rs['changed'])
assert all(not item['errors'] for item in results['relay']['recorded_consistency'])
