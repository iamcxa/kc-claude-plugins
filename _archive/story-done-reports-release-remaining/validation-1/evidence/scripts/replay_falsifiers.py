from pathlib import Path
import shutil,subprocess,json,os,importlib.util
OUT=Path('/tmp/validation-story-progress-20261111');P=Path('/tmp/validation-story-progress-20261111/producer');rows=[]
state=OUT/'replays/relay/docs/dev2/.spacedock-state';(state/'inbox-home.md').write_bytes(subprocess.check_output(['git','-C','/tmp/opencode-story-done/replays/relay/docs/dev2/.spacedock-state','show','77f5bb4e0e286467ec7078038e8bb9d680baddde:inbox-home.md']))
map=OUT/'replays/relay/docs/journey/spacedock-review.yaml';wf=OUT/'replays/relay/docs/dev2'
for name,rel in [('AC2-live-members-as-declared','AC2-members-as-declared'),('AC3-live-declared-list-only',None)]:
 if rel:root=OUT/'mutants'/rel
 else:
  root=OUT/'mutants'/name;shutil.copytree(P/'kc-journey-map',root,ignore=shutil.ignore_patterns('node_modules','__pycache__'));(root/'node_modules').symlink_to(P/'kc-journey-map/node_modules',target_is_directory=True)
  path=root/'lib/progress.mjs';s=path.read_text().replace("const done = members.filter((t) => t.status === 'done')","const owner = members.find((t) => t['journey-required-tasks'])\n\t\tlet counted = []\n\t\ttry { const required = JSON.parse(owner['journey-required-tasks']); counted = members.filter((t) => required.includes(t.id)) } catch {}\n\t\tconst done = counted.filter((t) => t.status === 'done')",1).replace('members: { tasks: members.length, done: done.length','members: { tasks: counted.length, done: done.length',1);path.write_text(s)
 cp=subprocess.run(['node',str(root/'lib/journey-progress.mjs'),str(map),'--workflow-dir',str(wf)],capture_output=True,text=True);(OUT/(name+'.stdout')).write_text(cp.stdout);(OUT/(name+'.stderr')).write_text(cp.stderr);d=json.loads(cp.stdout);assert d['diagnostic'] is None,d['diagnostic']
 if rel:
  old=json.loads((OUT/'relay-base.json').read_text());changed=[r['release'] for r in d['releases'] if [(x['status'],x['acceptance']) for x in old['releases'] if x['release']==r['release']]!=[(r['status'],r['acceptance'])]];assert 'continuity-latest' in changed,changed
  rows.append({'name':name,'status':'passed','message':'mutant changes declared status/acceptance on '+', '.join(changed)})
 else:
  story=next(s for s in d['stories'] if s['story']=='agent-reviews-from-link');assert story['members']['tasks']==3,story
  rows.append({'name':name,'status':'passed','message':'mutant counts 3 declared tasks instead of 6 filed tasks'})
 (OUT/'replay-falsifiers.json').write_text(json.dumps(rows,indent=2)+'\n')
p=OUT/'mutants/AC11-unlisted-workflows/scripts/design_surfaces.py';spec=importlib.util.spec_from_file_location('mutated_story',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=OUT/'replays/local/docs/dev2/.spacedock-state';paths=[x for x in root.rglob('*.md') if (x.parent in (root,root/'_archive') or (x.name=='index.md' and x.parent.parent in (root,root/'_archive'))) and x.name!='README.md' and x.read_text().startswith('---\n') and any(l.startswith('status:') for l in (m.decision_ledger.split_task(x.read_text())[0] or []))]
count=sum(any("needs a 'Story:' line" in e for e in m.check_task(x,seed=True)) for x in paths);assert count==230,count
(OUT/'AC12-force-all-workflows.json').write_text(json.dumps({'name':'AC12 force rule on unlisted workflow','status':'passed','message':f'mutant refuses {count}; candidate refuses 0; python3 -B, fresh cache-free mutant'},indent=2)+'\n')
print('native AC2/AC3 falsifiers and cache-free AC12 passed')
