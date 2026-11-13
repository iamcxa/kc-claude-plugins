from pathlib import Path
import subprocess, tarfile, io, json, hashlib
wt=Path.cwd(); x=Path(__file__).parent; ev=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-form-counts-ideation-rounds-and-times-each-round/evidence/implementation-1')
state=ev.parents[2]
base=subprocess.check_output(['git','-C',str(wt),'rev-parse','origin/main'],text=True).strip()
data=subprocess.check_output(['git','-C',str(wt),'archive',base,'kc-dev-flow-2/scripts'])
with tarfile.open(fileobj=io.BytesIO(data)) as arc: arc.extractall(x/'base',filter='data')
if not (x/'state').exists(): subprocess.run(['git','clone','--quiet','--shared',str(state),str(x/'state')],check=True)
if not (x/'replay').exists(): subprocess.run(['git','clone','--quiet','--shared',str(x/'state'),str(x/'replay')],check=True)
provenance={'base':base,'state':subprocess.check_output(['git','-C',str(x/'state'),'rev-parse','HEAD'],text=True).strip(),'probe':'de91166f055129f6a589594c25d70be68124551d','spacedock':subprocess.check_output(['/Users/kent/.local/bin/spacedock','--version'],text=True).strip(),'python':subprocess.check_output(['python3','--version'],text=True).strip(),'test_substitution':'FO explicitly requires unittest form in place of design pytest convenience commands (2026-11-13). No pytest installed; attempted install failed DNS before FO direction.'}
(ev/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps(provenance))
