from pathlib import Path
import subprocess, os
x=Path(__file__).parent; ev=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-form-counts-ideation-rounds-and-times-each-round/evidence/implementation-1/repair-1')
pkg=Path.cwd()/'kc-dev-flow-2/scripts'
cases=[('2 ideation, 1 implementation and 2 validation cycles',2,0),('2 ideation, 1 implementation and 2 validation cycles',3,1),('3 ideation, 1 implementation and 2 validation cycles',3,0),('1 implementation and 2 validation cycles',2,0),('1 implementation and 2 validation cycles',3,1),('two ideation, one implementation and two validation cycles, in one package PR.',3,1)]
for i,(budget,n,expected) in enumerate(cases,1):
    run=subprocess.run(['python3','-B',str(x/'run_check.py'),f'replay-{i}','bash',str(ev/'replay.sh'),str(pkg),str(x),'merge-ask-holds-missing-clauses',budget,str(n)])
    assert run.returncode==expected,(i,run.returncode,expected)
print('All six replay exits match 0/1/0/0/1/1')
