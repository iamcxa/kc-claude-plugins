import json, os, subprocess
from pathlib import Path

root = Path(os.environ['CAPTAIN_STEPS_WORKTREE'])
out = Path(__file__).parent
package = Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0')
workflow = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2')
task = workflow / '.spacedock-state/fo-tries-what-it-asks-the-captain.md'
base = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'origin/main'], text=True).strip()
head = '4f08f008f9b117876ffe4b569210278e240d203d'
checks = {
 'lint': ['python3','-B','kc-dev-flow-2/scripts/lint-skills.py'],
 'adr-lint': ['python3','-B',str(package/'scripts/adr_lint.py'),'docs/adr','--since',base,'--require','0054'],
 'number-guards': ['python3','-B',str(package/'scripts/number_guards.py'),'check','--repo',str(root),'--workflow-dir',str(workflow),'--task',str(task),'--base',base,'--head',head],
 'comment-ratio': ['python3','-B',str(package/'scripts/comment_ratio.py'),base,head,'--repo',str(root),'--workflow-dir',str(workflow)],
 'design': ['python3','-B',str(package/'scripts/design_surfaces.py'),'check',str(task)],
 'dispatch': ['python3','-B',str(package/'scripts/dispatch_records.py'),str(task.with_suffix(''))],
 'doc-impact': ['python3','-B',str(package/'scripts/doc_impact.py'),base,head],
 'diff-check': ['git','-C',str(root),'diff','--check',base,head],
}
results=[]
for name, command in checks.items():
 result=subprocess.run(command,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (out/(name+'.log')).write_text(result.stdout)
 results.append({'name':name,'command':command,'exit':result.returncode,'log':name+'.log'})
 print(name,result.returncode,flush=True)
(out/'checks.json').write_text(json.dumps(results,indent=2)+'\n')
