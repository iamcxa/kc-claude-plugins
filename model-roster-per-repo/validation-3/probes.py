import importlib.util,json,subprocess,sys,os,time
from pathlib import Path
root=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo/.validation3-candidate')
out=Path('/tmp/model-roster-validation3')
if len(sys.argv)>1:
 sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
 spec=importlib.util.spec_from_file_location('sd',root/'kc-dev-flow-2/scripts/test_sd_dispatch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.exercise_model_roster(out/('fixture-'+sys.argv[1]),Path(sys.argv[2]));sys.exit(0)
source=(root/'kc-dev-flow-2/scripts/model_roster.py').read_text()
old=subprocess.check_output(['git','-C',str(root),'show','a8536dc52:kc-dev-flow-2/scripts/model_roster.py'],text=True)
variants={
 'fixed':source,
 'revert-absent-author':source.replace('if len(lines) == 1 and lines[0] != "absent; source README default":','if len(lines) == 1:').replace('elif not lines or lines == ["absent; source README default"]:','elif not lines:'),
 'revert-absent-return':source.replace('result = {"source": "readme-default", "role": stage, "tuple": None,','return {"source": "readme-default", "role": stage, "tuple": None,'),
 'invent-validator-family':source.replace('if result["tuple"] and authors and all','if authors and all'),
 'prior-head':old}
probe=root/'.validation3-probes';probe.mkdir(exist_ok=True)
results=[]
for name,body in variants.items():
 path=probe/(name+'.py');path.write_text(body)
 t=time.monotonic();p=subprocess.run([sys.executable,'-B',__file__,name,str(path)],text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=100)
 (out/(name+'.log')).write_text(p.stdout+p.stderr)
 results.append(dict(variant=name,exit=p.returncode,seconds=round(time.monotonic()-t,3),tail=(p.stdout+p.stderr)[-1800:]))
 assert p.returncode==(0 if name=='fixed' else 1),(name,p.returncode,p.stderr)
(out/'mutations.json').write_text(json.dumps(results,indent=2)+'\n')
for p in probe.iterdir():p.unlink()
probe.rmdir()
print(json.dumps(results,indent=2))
