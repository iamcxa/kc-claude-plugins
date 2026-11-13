from pathlib import Path
import shutil, subprocess
x=Path(__file__).parent; ev=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-form-counts-ideation-rounds-and-times-each-round/evidence/implementation-1')
p=x/'role-mutants';shutil.copytree(Path.cwd()/'kc-dev-flow-2/scripts',p,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
f=p/'role_triggers.py';original=f.read_text()
for name,old,new,budget in [('no-grammar','if rounds:','if False:','2 ideation, 1 implementation and 2 validation cycles'),('no-default','if default:','if False:','1 implementation and 2 validation cycles')]:
    f.write_text(original.replace(old,new,1))
    r=subprocess.run(['python3','-B',str(x/'run_check.py'),'replay-mutant-'+name,'bash',str(ev/'replay.sh'),str(p),str(x),'merge-ask-holds-missing-clauses',budget,'3'])
    assert r.returncode==0,(name,r.returncode)
f.write_text(original)
print('Both code mutations wrongly allow the third replayed dispatch (exit 0, candidate exits 1)')
