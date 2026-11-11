import concurrent.futures, hashlib, json, os, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]); out=Path('/tmp/budget-worth-repair');out.mkdir(parents=True,exist_ok=True)
package=Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1')
workflow=root.parent.parent/'docs/dev2'; task=workflow/'.spacedock-state/budget-overrun-holds-and-findings-meet-non-goals.md'
base='e8664a72b0f904e5dda3c391d52ab3abaca876b4'
checks=[('lint-at-commit',['python3','-B',str(root/'kc-dev-flow-2/scripts/lint-skills.py')]),
        ('adr-at-commit',['python3','-B',str(package/'scripts/adr_lint.py'),'docs/adr','--since',base,'--require','0077']),
        ('number-guards',['python3','-B',str(package/'scripts/number_guards.py'),'check','--repo',str(root),'--workflow-dir',str(workflow),'--base',base,'--head','HEAD','--task',str(task)]),
        ('comment-ratio',['python3','-B',str(package/'scripts/comment_ratio.py'),base,'HEAD','--repo',str(root),'--workflow-dir',str(workflow)])]
def run(item):
    name,command=item
    with (out/(name+'.log')).open('w') as stream:
        result=subprocess.run(command,cwd=root,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    return dict(name=name,command=command,exit=result.returncode,status='passed' if result.returncode==0 else 'failed')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(run,checks))
(out/'required-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
identity=json.loads((out/'final/test-identity.json').read_text())
patch=subprocess.check_output(['git','-C',str(root),'diff','--binary',base,'HEAD'])
assert hashlib.sha256(patch).hexdigest()==identity['patch_sha256'],'committed bytes differ from tested patch'
identity.update(candidate=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),committed_patch_matches_tested=True)
(out/'identity-at-commit.json').write_text(json.dumps(identity,indent=2)+'\n')
for row in rows:print(row['name'],row['exit'])
sys.exit(any(row['exit'] for row in rows))
