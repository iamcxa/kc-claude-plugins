from pathlib import Path
import importlib.util,json,subprocess,sys,tempfile,collections,shutil
wt=Path('/tmp/merge-guard-validation-b82f20de/export'); state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state');poc=state/'merge-guard-stops-unasked-merges/poc'
script=Path('/tmp/merge-guard-validation-b82f20de/evidence/merge-guard-head-mutant.py');spec=importlib.util.spec_from_file_location('guard',script);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
prs={p['number']:p for file in ('pr672.json','merged-14d.json') for data in [json.loads((poc/file).read_text())] for p in (data if isinstance(data,list) else [data])}
results={}; overlay=Path(tempfile.mkdtemp(prefix='merge-recount-'))
for stage in ('replay','recount'):
 refused=[]
 if stage=='recount':
  for p in prs.values():
   ref=p['headRefName']; kind='release' if ref.startswith('release-please') else 'sync' if ref.startswith('chore/dev2-sync-') else 'learning' if ref.startswith('learning/') else 'other'
   if kind=='other':continue
   question=json.loads((state/'_archive/special-role-calls-fire-when-needed/review/validation/briefing-1/index.json').read_text())['question'] if p['number']==672 else f"Merge {kind} #{p['number']} at {p['headRefOid'][:8]}?"
   q=overlay/'question.txt';q.write_text(question)
   r=subprocess.run([sys.executable,'-B',str(script),'record',str(overlay),'--pr',f"iamcxa/kc-claude-plugins#{p['number']}",'--head',p['headRefOid'],'--question-file',str(q),'--answer','synthetic recount approval'],capture_output=True,text=True)
   if r.returncode:refused.append({'pr':p['number'],'reason':r.stdout.strip()})
 roots=[state]+([overlay] if stage=='recount' else [])
 verdicts={str(n):g.verdict(f"gh pr merge {n} --repo iamcxa/kc-claude-plugins --squash --match-head-commit {p['headRefOid']}",wt,roots)[0] for n,p in prs.items()}
 counts=dict(collections.Counter(verdicts.values()));print(stage,counts,'refused',refused)
 results[stage]={'counts':counts,'verdicts':verdicts,'refused':refused}
 assert verdicts['672']==('pass' if stage=='recount' else 'stop')
 original=set()
 for line in (poc/(stage+'-output.txt')).read_text().splitlines():
  words=line.split()
  if len(words)>2 and words[0].isdigit() and words[-1]=='stop':original.add(words[0])
 current={n for n,v in verdicts.items() if v=='stop'}
 print('differences from ideation:',{'now_pass':sorted(original-current),'now_stop':sorted(current-original)})
 results[stage]['differences']={'now_pass':sorted(original-current),'now_stop':sorted(current-original)}
for n in set(results['replay']['differences']['now_pass']):
 p=prs[int(n)]
 for root in [state]:
  for record in g.newest_records([root]):
   if record.get('pr')==f'iamcxa/kc-claude-plugins#{n}' and record.get('head')==p['headRefOid']:
    print('newly carrying record',n,record)
Path('/tmp/merge-guard-validation-b82f20de/evidence/merge-guard-head-mutant-replay.json').write_text(json.dumps(results,indent=2))
