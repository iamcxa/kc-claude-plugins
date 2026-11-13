import os, subprocess, pathlib, json
wt=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-ready-pr-gets-a-codex-code-review-without-fo-noticing")
scratch=pathlib.Path("/tmp/dev2/kc-claude-plugins-3042bb224e995ded/ready-pr-gets-a-codex-code-review-without-fo-noticing/validation-1")
e=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/ready-pr-gets-a-codex-code-review-without-fo-noticing/evidence/validation-1")
candidate=scratch/'candidate'
package=pathlib.Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0')
task=e.parent.parent
workflow=task.parent.parent
base='6a1eaf837bd6087cd0b8b665dc19beaed3c44dff'
head='1c8a29faf402ef6d7018c298f59bad58d38cfb1d'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(scratch))
results=[]
def run(name,args,cwd=candidate,expected=0):
 p=subprocess.run([str(a) for a in args],cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (e/(name+'.log')).write_text(p.stdout)
 results.append(dict(name=name,command=[str(a) for a in args],cwd=str(cwd),exit=p.returncode,expected=expected))
 print(name,p.returncode,p.stdout[-500:].strip())
 return p
sentence='when FO marks a PR ready, it comments `@codex review` on the PR once.'
run('ac5',['rg','-n','-F','--',sentence,'kc-dev-flow-2/extensions/codex/EXTENSION.md'])
f=candidate/'kc-dev-flow-2/extensions/codex/EXTENSION.md'
mutant=scratch/'without-sentence.md'
mutant.write_text(''.join(l for l in f.read_text().splitlines(keepends=True) if sentence not in l))
run('falsifier',['rg','-n','-F','--',sentence,mutant],expected=1)
run('lint',['python3','-B','kc-dev-flow-2/scripts/lint-skills.py'])
run('codex-tests',['python3','-B','kc-dev-flow-2/extensions/codex/test_codex_review.py'])
run('adr-lint',['python3','-B',package/'scripts/adr_lint.py','docs/adr','--since',base],wt)
run('comment-ratio',['python3','-B',package/'scripts/comment_ratio.py',base,head,'--workflow-dir',workflow],wt)
run('doc-impact',['python3','-B',package/'scripts/doc_impact.py',base,head],wt)
run('design-check',['python3','-B',package/'scripts/design_surfaces.py','check',str(task)+'.md'],wt)
run('dispatch-records',['python3','-B',package/'scripts/dispatch_records.py',task],wt)
(e/'results.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['exit']==r['expected'] for r in results)

