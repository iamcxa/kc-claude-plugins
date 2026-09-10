import sys, subprocess, tempfile, json, re
from pathlib import Path
repo=Path(sys.argv[1]); sd=sys.argv[2]; outputs=[]
ns={"__file__":str(repo/'kc-dev-flow/scripts/poc-close-guard.test.py')}
exec((repo/'kc-dev-flow/scripts/poc-close-guard.test.py').read_text().split('with tempfile.TemporaryDirectory(prefix="poc-close-guard-")')[0],ns)
root=Path(tempfile.mkdtemp(prefix='poc-order-test-')); guard=ns['load_guard']()
def run(label,*args,input=None):
 p=subprocess.run(list(args),cwd=root,text=True,capture_output=True,input=input)
 outputs.append(dict(label=label,argv=list(args),rc=p.returncode,stdout=p.stdout,stderr=p.stderr));return p
readme="""---
commissioned-by: spacedock@0.27.2
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
trunk: main
stages:
  states:
    - name: implementation
      initial: true
    - name: validation
      gate: true
      feedback-to: implementation
    - name: done
      terminal: true
---
# Synthetic local order probe; no real Captain decision
"""
(root/'README.md').write_text(readme)
for a in [('init','-qb','main'),('config','user.name','Synthetic probe'),('config','user.email','probe@example.invalid')]: run('git-init','git',*a)
text=ns['direct_item_text']('change').replace('id: poc123exact\n','').replace('captain_wait_seconds: 0','captain_wait_seconds: pending').replace('terminal_cleanup_seconds: 2','terminal_cleanup_seconds: pending').replace('cleanup_status: complete','cleanup_status: pending')
text+='\n## Stage Report: implementation\n\n- DONE: Synthetic observation.\n  Disposable local proof only.\n'
run('new',sd,'new','probe','--workflow-dir',str(root),input=text)
item=root/'probe.md'
run('commit','git','add','README.md','probe.md');run('commit','git','commit','-qm','synthetic fixture')
def native(label,*args): return run(label,sd,*args,'--workflow-dir',str(root))
for phase in ['review','prepare']:
 args=['--question','Synthetic only?','--artifact',str(item),'--summary','Synthetic pending outcome'] if phase=='prepare' else []
 run('original-'+phase,sys.executable,str(repo/'kc-dev-flow/scripts/poc-close-guard.py'),'--spacedock-bin',sd,'--workflow-dir',str(root),'--work-item',str(item),phase,*args)
native('native-transition','status','--set','probe','status=validation');native('durable','state','commit','probe')
native('native-prepare','gate','prepare','probe','--question','Synthetic only?','--artifact',str(item),'--summary','Synthetic pending outcome')
native('unapproved-consume','gate','consume','probe')
before_approval=item.read_text(); item.write_text(before_approval.replace('captain_wait_seconds: pending','captain_wait_seconds: 99'))
run('commit-stale-before-approval','git','add','probe.md');run('commit-stale-before-approval','git','commit','-qm','synthetic artifact drift')
native('stale-approval','gate','record','probe','--decision','approve','--actor','person:captain','--reason','SYNTHETIC stale test')
item.write_text(before_approval);run('restore-artifact','git','add','probe.md');run('restore-artifact','git','commit','-qm','restore synthetic artifact')
native('synthetic-approve','gate','record','probe','--decision','approve','--actor','person:captain','--reason','SYNTHETIC TEST ONLY, not Kent approval')
native('approved-consume','gate','consume','probe')
briefing=next(root.rglob('index.json')); bound=briefing.read_text(); briefing.write_text(bound.replace('Synthetic only?', 'TAMPERED question'))
native('tampered-briefing-consume','gate','consume','probe')
briefing.write_text(bound)
original=item.read_text(); item.write_text(original.replace('captain_wait_seconds: pending','captain_wait_seconds: 12'))
run('commit-post-approval-measurement','git','add','probe.md');run('commit-post-approval-measurement','git','commit','-qm','synthetic post approval measurement')
native('changed-measurement-consume','gate','consume','probe')
item.write_text(original)
run('restore-pending','git','add','probe.md');run('restore-pending','git','commit','-qm','restore approved pending artifact')
native('merge-finalize','merge','guard','probe','--verdict','passed','--json')
resolved=native('resolve-archived','status','--resolve','probe','--json')
try: archived=Path(json.loads(resolved.stdout)['path'])
except Exception: archived=next(root.rglob('probe.md'))
if archived.exists():
 archived.write_text(archived.read_text().replace('captain_wait_seconds: pending','captain_wait_seconds: 12').replace('terminal_cleanup_seconds: pending','terminal_cleanup_seconds: 3').replace('cleanup_status: pending','cleanup_status: complete'))
 native('commit-final-measurements','state','commit','probe')
 run('existing-owner-path-scoped-archive-commit','git','add',str(archived));run('existing-owner-path-scoped-archive-commit','git','commit','-qm','synthetic final close observations','--',str(archived))
 native('publish-final-measurements','state','commit','probe')
 native('repeat-consume','gate','consume','probe')
 outputs.append({'label':'final-content','path':str(archived),'text':archived.read_text()})
source=repo/'docs/dev/.spacedock-state/first-cloud-dev-flow-improvement-run/index.md'
snapshot=root/'real-task-snapshot.md';body=source.read_text(); start=body.index('## POC close measurement');end=body.index('\n## ',start+3); body=body[:end]+'\n```yaml\npoc_close_measurement:\n  captain_wait_seconds: pending\n  terminal_cleanup_seconds: pending\n  cleanup_status: pending\n```\n'+body[end:];snapshot.write_text(body)
try: guard.validate(snapshot,'review')
except Exception as e: outputs.append({'label':'original-preserved-snapshot','error':str(e)})
result={'synthetic_only':True,'repo':str(repo),'root':str(root),'results':outputs};Path(sys.argv[3]).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
