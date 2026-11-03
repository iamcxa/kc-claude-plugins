import json, subprocess, pathlib
root=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check/.context/validation-767-cycle2-detached"); out=pathlib.Path("/tmp/validation-767-cycle2")
task=root/'.context/live-state/validation-gate-requires-the-question-check.md'
workflow=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/..")
results=[]
for label,code,text in [('live-missing','kc-dev-flow-2/scripts/delivery_gate.py','live-missing.txt'),('live-present','kc-dev-flow-2/scripts/delivery_gate.py','live-present.txt'),('live-no-count-rule','.context/live-no-count-rule/delivery_gate.py','live-missing.txt')]:
    command=['python3','-B',str(root/code),'check',str(task),'--pr','iamcxa/kc-claude-plugins#767','--text-file',str(out/text),'--workflow-dir',str(workflow)]
    before=sorted(x.name for x in task.with_suffix('') .joinpath('merge').glob('ask-*.json'))
    p=subprocess.run(command,cwd=root,text=True,capture_output=True,timeout=120)
    after=sorted(x.name for x in task.with_suffix('') .joinpath('merge').glob('ask-*.json'))
    (out/(label+'.log')).write_text(p.stdout+p.stderr)
    results.append(dict(label=label,command=command,exit=p.returncode,stdout=p.stdout,stderr=p.stderr,records_before=before,records_after=after))
    print(label,p.returncode,flush=True)
(out/'live-results.json').write_text(json.dumps(results,indent=2))
problem='summary needs one top-level External rounds: N line (nonnegative integer)'
assert results[0]['exit']==1 and problem in results[0]['stdout']
assert all(problem not in r['stdout'] for r in results[1:])
assert not any('cannot read' in r['stdout'] for r in results),results


assert results[0]['records_before']==results[0]['records_after']==[]
assert len(results[1]['records_after'])==1 and len(results[2]['records_after'])==2
