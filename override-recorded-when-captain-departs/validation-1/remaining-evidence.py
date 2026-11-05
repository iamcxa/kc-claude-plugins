import json, subprocess, sys
from pathlib import Path
O=Path(__file__).resolve().parent
W=Path(sys.argv[1]).resolve()
S=W/'kc-dev-flow-2/scripts/decision_ledger.py'
B='d37c6dc653e0f45d6ca630c2faa6121c0863a57e'
commands=[]
def run(args,expected=0):
 r=subprocess.run([str(a) for a in args],capture_output=True,text=True)
 commands.append(dict(argv=[str(a) for a in args],exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
 (O/'remaining-commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2))
 assert r.returncode==expected,(args,r.stdout,r.stderr)
 return r
checker=O/'compatibility-check.py'
checker.write_text('''import json,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parent
rows=lambda s: [json.loads(r) for r in subprocess.check_output([sys.executable,'-B',str(s),str(p/'state-snapshot')],text=True).splitlines()]
a=rows(p/'base-decision-ledger.py'); b=rows(sys.argv[1])
b=[{k:v for k,v in r.items() if k!='followed'} for r in b]
print('compatible' if a==b else 'changed existing ledger keys or values')
sys.exit(0 if a==b else 1)
''')
run([sys.executable,'-B',checker,S])
mutant=O/'rename-key-decision-ledger.py'
source=S.read_text()
assert source.count('"task": path.stem')==1
mutant.write_text(source.replace('"task": path.stem','"renamed_task": path.stem'))
run([sys.executable,'-B',checker,mutant],1)
guard=O/'scope-check.py'
guard.write_text('''import subprocess,sys
paths=subprocess.check_output(['git','-C',sys.argv[1],'diff','--name-only',sys.argv[2]],text=True).splitlines()
forbidden={'kc-dev-flow-2/scripts/'+n for n in ['delivery_gate.py','design_surfaces.py','role_triggers.py']}
forbidden.add('kc-dev-flow-2/skills/observer/SKILL.md')
found=sorted(forbidden.intersection(paths))
print('forbidden scope: '+', '.join(found) if found else 'scope unchanged')
sys.exit(1 if found else 0)
''')
run([sys.executable,'-B',guard,W,B])
probe=O/'scope-mutation'; probe.mkdir()
target=probe/'kc-dev-flow-2/scripts/delivery_gate.py'; target.parent.mkdir(parents=True)
target.write_text((W/'kc-dev-flow-2/scripts/delivery_gate.py').read_text())
git=['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null']
run([*git,'init','--initial-branch=main',probe]);run([*git,'-C',probe,'add','.']);run([*git,'-C',probe,'commit','-m','test: scope control'])
target.write_text(target.read_text()+'\n# Intentional scope mutation.\n')
run([sys.executable,'-B',guard,probe,'HEAD'],1)
words={}
for stage in ('ideation','implementation','validation'):
 values=[]
 outputs=[]
 for kind in ('base','candidate'):
  folder=O/('stage-'+kind);folder.mkdir(exist_ok=True)
  text=run(['git','-C',W,'show',B+':kc-dev-flow-2/references/sd/workflow.md']).stdout if kind=='base' else (W/'kc-dev-flow-2/references/sd/workflow.md').read_text()
  (folder/'README.md').write_text(text)
  r=run(['/Users/kent/.local/bin/spacedock','dispatch','show-stage-def','--workflow-dir',folder,'--stage',stage])
  (folder/(stage+'.md')).write_text(r.stdout)
  values.append(len(r.stdout.split()));outputs.append(r.stdout)
 assert outputs[0]==outputs[1]
 words[stage]=dict(base=values[0],candidate=values[1],byte_identical=True)
(O/'stage-word-counts.json').write_text(json.dumps(words,indent=2))
print('PASS: actual key-renaming and scope mutations fail their acceptance guards; every worker stage is byte-identical.')
