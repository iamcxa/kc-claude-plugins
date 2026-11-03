import hashlib, io, json, os, subprocess, sys, tarfile
from pathlib import Path
import proof
root=proof.WT
out=proof.OUT
package=Path('/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0')
workflow=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state').parent
task=workflow/'.spacedock-state/diagnosis-rounds-count-toward-step-back.md'
commands={
 'adr-origin-main':[sys.executable,'-B',package/'scripts/adr_lint.py','docs/adr','--since','origin/main','--require','26'],
 'adr-dispatch-package':[sys.executable,'-B','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py','docs/adr','--since','origin/main','--require','26'],
 'number-guards-origin':[sys.executable,'-B',package/'scripts/number_guards.py','check','--repo',root,'--workflow-dir',workflow,'--base','origin/main','--head','HEAD','--task',task],
 'design':[sys.executable,'-B',package/'scripts/design_surfaces.py','check',task],
 'dispatch-records':[sys.executable,'-B',package/'scripts/dispatch_records.py',task.with_suffix('')],
 'comment-ratio-origin':[sys.executable,'-B',package/'scripts/comment_ratio.py','origin/main','HEAD','--workflow-dir',workflow],
 'doc-impact-origin':[sys.executable,'-B',package/'scripts/doc_impact.py','origin/main','HEAD','--repo',root,'--json'],
 'diff-check':['git','diff','--check','origin/main...HEAD'],
}
rows=[]
for name,args in commands.items():
 result=proof.run(*args)
 (out/(name+'.log')).write_text(result.stdout+result.stderr)
 rows.append({'name':name,'status':'passed' if result.returncode==0 else 'failed','command':list(map(str,args)),'exit':result.returncode,'message':result.stdout.strip()})
(out/'supplemental.json').write_text(json.dumps(rows,indent=2))
assert all(row['exit']==0 for row in rows), rows
print('Current origin/main structural checks: all exit 0.')
paths=proof.git(root,'diff','--name-only','origin/main...HEAD').splitlines()
identity={'candidate':proof.git(root,'rev-parse','HEAD').strip(),'origin_main':proof.git(root,'rev-parse','origin/main').strip(),'merge_base':proof.git(root,'merge-base','HEAD','origin/main').strip(),'state':proof.git(task.parent,'rev-parse','HEAD').strip(),'files':{path:hashlib.sha256((root/path).read_bytes()).hexdigest() for path in paths}}
(out/'identity.json').write_text(json.dumps(identity,indent=2))
proof.BASE=identity['origin_main']
proof.OUT=out/'origin-main'
proof.OUT.mkdir(exist_ok=True)
proof.OLD=root.parent/'.validation-origin-main/kc-dev-flow-2'
proof.OLD.parent.mkdir(exist_ok=True)
raw=subprocess.run(['git','-C',str(root),'archive',proof.BASE,'kc-dev-flow-2'],capture_output=True,check=True).stdout
with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
 tf.extractall(proof.OLD.parent,filter='data')
proof.replay()
proof.words()
