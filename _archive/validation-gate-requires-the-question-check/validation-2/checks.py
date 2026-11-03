import subprocess,json
from pathlib import Path
root=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check/.context/validation-767-cycle2-detached'); pkg=Path('/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'); state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'); out=Path('/tmp/validation-767-cycle2')
base='820a3f0ef7db1e802f99c13d1608b4c849f400cf'; head='6b680cf89125d75f062ecf198e37b13239cd16ea'
commands={
'adr-lint':['python3',str(pkg/'scripts/adr_lint.py'),'docs/adr','--since',base,'--require','0051'],
'number-guards':['python3',str(pkg/'scripts/number_guards.py'),'check','--repo',str(root),'--workflow-dir',str(state.parent),'--task',str(state/'validation-gate-requires-the-question-check.md'),'--base',base,'--head',head],
'comment-ratio':['python3',str(pkg/'scripts/comment_ratio.py'),base,head,'--workflow-dir',str(state.parent)],
'doc-impact':['python3',str(pkg/'scripts/doc_impact.py'),base,head],
'design-surfaces':['python3',str(pkg/'scripts/design_surfaces.py'),'check',str(state/'validation-gate-requires-the-question-check.md')],
'dispatch-installed':['python3',str(pkg/'scripts/dispatch_records.py'),str(state/'validation-gate-requires-the-question-check')],
'dispatch-candidate':['python3','-B',str(root/'kc-dev-flow-2/scripts/dispatch_records.py'),str(state/'validation-gate-requires-the-question-check')],
'diff-check':['git','-C',str(root),'diff','--check',base,head],
'stacked-reference-diff':['git','-C',str(root),'diff','--exit-code',base,head,'--','kc-dev-flow-2/references/sd/','kc-dev-flow-2/scripts/lint-skills.py'],
'literal-main-diff':['git','-C',str(root),'diff','--exit-code','origin/main',head,'--','kc-dev-flow-2/references/sd/'],
}
results=[]
for label,command in commands.items():
    p=subprocess.run(command,cwd=root,text=True,capture_output=True)
    (out/(label+'.log')).write_text(p.stdout+p.stderr)
    results.append(dict(label=label,command=command,exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
    print(label, 'exit='+str(p.returncode),flush=True)
(out/'checks.json').write_text(json.dumps(results,indent=2))
