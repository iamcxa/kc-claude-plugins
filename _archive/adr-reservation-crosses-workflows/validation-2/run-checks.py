import os, json, subprocess, time
from pathlib import Path
OUT=Path('/tmp/adr-reservation-validation-801-r2')
ROOT=OUT/'candidate'
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-adr-reservation-crosses-workflows')
FLOW=WT.parents[1]/'docs/dev2'
STATE=FLOW/'.spacedock-state'
PKG=Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0')
BASE='ba055b8a7a55a787ac989c4cef52d07dd75661ad'
HEAD='ef3ed3e05534e2a997acbdfb055a880fde1f484a'
GITDIR=subprocess.check_output(['git','-C',str(WT),'rev-parse','--absolute-git-dir'],text=True).strip()
checks=[
('number-tests',['python3','-B','kc-dev-flow-2/scripts/test_number_guards.py'],{}),
('dispatch-tests',['python3','-B','kc-dev-flow-2/scripts/test_dispatch_records.py'],{}),
('lint',['python3','-B','kc-dev-flow-2/scripts/lint-skills.py'],{}),
('adr-lint',['python3','-B',str(PKG/'scripts/adr_lint.py'),'docs/adr','--since',BASE,'--require','0002'],{'GIT_DIR':GITDIR,'GIT_WORK_TREE':str(ROOT),'GIT_OPTIONAL_LOCKS':'0'}),
('installed-number-check',['python3','-B',str(PKG/'scripts/number_guards.py'),'check','--repo',str(WT),'--workflow-dir',str(FLOW),'--task',str(STATE/'adr-reservation-crosses-workflows.md'),'--base',BASE,'--head',HEAD],{}),
('comment-ratio',['python3','-B',str(PKG/'scripts/comment_ratio.py'),BASE,HEAD,'--repo',str(WT),'--workflow-dir',str(FLOW)],{}),
('doc-impact',['python3','-B',str(PKG/'scripts/doc_impact.py'),BASE,HEAD,'--repo',str(WT),'--json'],{}),
('design-surfaces',['python3','-B',str(PKG/'scripts/design_surfaces.py'),'check',str(STATE/'adr-reservation-crosses-workflows.md')],{}),
('dispatch-records',['python3','-B',str(PKG/'scripts/dispatch_records.py'),str(STATE/'adr-reservation-crosses-workflows')],{}),
('diff-check',['git','-C',str(WT),'diff','--check',BASE,HEAD],{}),
('replay-candidate',['bash','--noprofile','--norc',str(OUT/'replay.sh'),str(ROOT/'kc-dev-flow-2/scripts/number_guards.py')],{}),
('replay-base',['bash','--noprofile','--norc',str(OUT/'replay.sh'),str(OUT/'base/kc-dev-flow-2/scripts/number_guards.py')],{}),
]
for ext,script in [('codex','test_codex_review.py'),('roborev','test_roborev_gate.py'),('copilot','test_copilot_review.py'),('journey-map','test_map_footprint.py'),('release-acceptance','test_release_acceptance.py')]:
 checks.append((ext,['python3','-B',str(ROOT/'kc-dev-flow-2/extensions'/ext/script)],{}))
checks.append(('sd-dispatch',['python3','-B','kc-dev-flow-2/scripts/test_sd_dispatch.py','--sd-plugin-root','/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.3'],{}))
results=[]
for name,cmd,extra in checks:
 with (OUT/(name+'.log')).open('w') as f:
  result=subprocess.run(cmd,cwd=ROOT,env={**os.environ,**extra},stdout=f,stderr=subprocess.STDOUT)
 row={'name':name,'command':cmd,'env':extra,'exit':result.returncode,'status':'passed' if result.returncode==0 else 'failed','log':str(OUT/(name+'.log'))}
 results.append(row)
 (OUT/'checks.json').write_text(json.dumps(results,indent=2))
 print(name,result.returncode,flush=True)
