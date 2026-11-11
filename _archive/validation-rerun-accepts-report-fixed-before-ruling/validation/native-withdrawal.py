import os,pathlib,subprocess,json,sys
r=pathlib.Path(sys.argv[1]); root=r/'native-withdrawal'; root.mkdir(); wf=root/'docs/dev2'; wf.mkdir(parents=True)
source=r/'candidate/kc-dev-flow-2/references/sd/workflow.md'
(wf/'README.md').write_text(source.read_text().replace('state: .spacedock-state\n',''))
entity=wf/'probe.md'; entity.write_text('---\ntitle: Synthetic withdrawal probe\nvariant: kc-dev-flow-2\nprofile: pilot\nstatus: ideation\n---\n\n## Scope\n\nSynthetic local test only, no human authority.\n\n## Stage Report: ideation\n\n- DONE: synthetic\n  Fixture only.\n\n### Summary\n\nSynthetic local probe.\n')
env=dict(os.environ,GIT_AUTHOR_NAME='Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid',GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_SYSTEM=os.devnull)
results=[]
def run(args):
 p=subprocess.run(args,cwd=root,env=env,capture_output=True,text=True); results.append(dict(command=args,exit=p.returncode,stdout=p.stdout,stderr=p.stderr)); print(json.dumps(results[-1]),flush=True); return p
run(['git','init','-b','main']);run(['git','add','--','docs/dev2']);run(['git','commit','-m','synthetic local gate fixture'])
bin='/Users/kent/.local/bin/spacedock'
p=run([bin,'gate','prepare','probe','--question','Synthetic question only?','--artifact',str(entity),'--summary','Synthetic proof, no human decision.','--workflow-dir',str(wf)])
assert p.returncode==0
p=run([bin,'gate','record','probe','--decision','hold','--actor','person:captain','--reason','SYNTHETIC test only; no actual Captain decision.','--workflow-dir',str(wf)])
assert p.returncode==0
p=run([bin,'gate','withdraw','probe','--reason','SYNTHETIC test only.','--workflow-dir',str(wf)])
(r/'evidence/native-withdrawal.json').write_text(json.dumps(results,indent=2)+'\n')
(r/'evidence/native-withdrawal-entity.md').write_text(entity.read_text())

assert p.returncode == 1 and "frozen closed" in p.stderr, results[-1]
print("PASS: native Spacedock refuses withdrawal of an already-resolved attempt")
