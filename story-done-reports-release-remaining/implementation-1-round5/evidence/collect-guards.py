from pathlib import Path
import json
out=Path('/tmp/opencode-story-done-round5')
pkg='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1'
wt='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining-dev2'
wf='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2'
base='fd1caa475f85483cf5c4031a1e58656ff5d3eaff';head='01d23393ebe5bfd63d8bcafc01859c3b146021d2'
checks=[('adr-lint',['python3','-B',pkg+'/scripts/adr_lint.py','docs/adr','--since',base,'--require','0076']),('comment-ratio',['python3','-B',pkg+'/scripts/comment_ratio.py',base,head,'--repo',wt,'--workflow-dir',wf]),('number-guards',['python3','-B',pkg+'/scripts/number_guards.py','check','--repo',wt,'--workflow-dir',wf,'--base',base,'--head',head,'--task',wf+'/.spacedock-state/story-done-reports-release-remaining.md']),('doc-impact',['python3','-B',pkg+'/scripts/doc_impact.py',base,head,'--json'])]
results=[]
for name,command in checks:
 code=int((out/(name+'.exit')).read_text())
 results.append({'name':name,'status':'passed' if code==0 else 'failed','exit':code,'command':command,'cwd':wt,'log':name+('.json' if name=='doc-impact' else '.log')})
(out/'guard-results.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['exit']==0 for r in results)
verdicts={'docs/adr/0041-seed-admission-enforces-required-fields.md':('unaffected','The three required seed bounds and seed-only call are unchanged; the Story helper remains a separate check.'),'docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md':('unaffected','Amendment comparison helpers remain importable without the Story-only dependency; their code and ADR are unchanged.'),'docs/adr/0076-a-journey-workflows-new-seed-records-its-story-or-none.md':('retained','The Story check still runs in seed and default modes; moving the import inside that check does not change the documented rule. ADR bytes equal the original dev2 commit.')}
impact=json.loads((out/'doc-impact.json').read_text())
assert set(r['doc'] for r in impact)==set(verdicts)
(out/'document-verdicts.json').write_text(json.dumps([{'doc':r['doc'],'verdict':verdicts[r['doc']][0],'reason':verdicts[r['doc']][1]} for r in impact],indent=2)+'\n')
print('four guards passed; three affected document verdicts retained')
