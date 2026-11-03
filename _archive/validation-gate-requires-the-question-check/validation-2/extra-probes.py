import json, subprocess, tempfile, shutil
from pathlib import Path
root=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check/.context/validation-767-cycle2-detached')
pkg=Path('/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0')
out=Path('/tmp/validation-767-cycle2')
results=[]
def run(label,cmd,cwd=root):
    p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
    (out/(label+'.log')).write_text(p.stdout+p.stderr)
    results.append(dict(label=label,command=[str(x) for x in cmd],exit=p.returncode,output=p.stdout+p.stderr))
    print(label, 'exit='+str(p.returncode), p.stdout.strip(), flush=True)
    return p
with tempfile.TemporaryDirectory(prefix='additional-probes-',dir=root/'.context') as d:
    d=Path(d)
    shutil.copytree(root/'kc-dev-flow-2',d/'kc-dev-flow-2')
    p=d/'kc-dev-flow-2/references/sd/workflow.md'
    p.write_text(p.read_text()+'\nvalidationprobe\n')
    r=run('AC6-added-workflow-word',['python3','-B',root/'kc-dev-flow-2/scripts/lint-skills.py','--root',d/'kc-dev-flow-2'])
    assert r.returncode==1 and 'exceeds the budget' in r.stdout
    shutil.copytree(root/'docs/adr',d/'docs/adr')
    target=d/'docs/adr/0051-the-merge-ask-check-requires-the-round-count.md'
    original=target.read_text()
    for label,before,after,expected in [('AC7-remove-Words','**Words:**','Words:',1),('AC7-remove-Asked','**Asked:**','Asked:',0),('AC7-remove-Recommended','**Recommended:**','Recommended:',1)]:
        target.write_text(original.replace(before,after))
        r=run(label,['python3',pkg/'scripts/adr_lint.py',d/'docs/adr','--root',d,'--require','0051'])
        assert r.returncode==expected, r.stdout+r.stderr
    target.write_text(original)
    code=d/'kc-dev-flow-2/scripts/delivery_gate.py'
    s=code.read_text()
    code.write_text(s.replace('    # see docs/adr/0051-the-merge-ask-check-requires-the-round-count.md\n',''))
    r=run('AC7-remove-code-pointer',['python3',pkg/'scripts/adr_lint.py',d/'docs/adr','--root',d,'--require','0051'])
    assert r.returncode==1 and 'has no pointer' in r.stdout
(out/'extra-probes.json').write_text(json.dumps(results,indent=2))
