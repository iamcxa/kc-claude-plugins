import importlib.util,json,pathlib,subprocess,sys,os
root=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo/.validation-2')
out=pathlib.Path('/tmp/roster-validation2-a8536dc5/mutations-rerun');out.mkdir()
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
source=(root/'kc-dev-flow-2/scripts/model_roster.py').read_text()
mutations={
 'cwd-instead-of-root':('root = root.resolve()', 'root = Path.cwd().resolve()'),
 'fabricated-absence':('return {"source": "readme-default", "role": stage, "tuple": None,','return {"source": "repository", "role": stage, "tuple": {"provider":"codex"},'),
 'swap-stage':('role = "implementation" if stage == "repair" else stage','role = "implementation" if stage in ("repair", "ideation") else stage'),
 'drop-effort':('if stage == "validation":\n        authors', 'result["tuple"].pop("effort")\n    if stage == "validation":\n        authors'),
 'hide-family':('"same-family: openai" if authors and all(a["tuple"] for a in authors)','"unverified" if authors and all(a["tuple"] for a in authors)'),
 'write-on-resolve':('root = root.resolve()', 'root = root.resolve()\n    (root / "unexpected-write").write_text("mutation")'),
 'hard-refuse-family':('result["authors"] = authors', 'result["authors"] = authors\n        if authors and all(a["tuple"] for a in authors): raise Invalid("family refused")'),
}
results=[]
for name,(old,new) in mutations.items():
 assert source.count(old)==1,(name,source.count(old))
 directory=out/name; directory.mkdir(); resolver=directory/'model_roster.py';resolver.write_text(source.replace(old,new))
 program='import importlib.util,pathlib; s=importlib.util.spec_from_file_location("suite",'+repr(str(root/'kc-dev-flow-2/scripts/test_sd_dispatch.py'))+');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.exercise_model_roster(pathlib.Path('+repr(str(directory/'fixture'))+'),pathlib.Path('+repr(str(resolver))+'))'
 r=subprocess.run([sys.executable,'-B','-c',program],cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(root/'kc-dev-flow-2/scripts')),capture_output=True,text=True)
 (directory/'result.log').write_text(r.stdout+r.stderr)
 result=dict(name=name,exit=r.returncode,caught=r.returncode==1 and 'AssertionError' in r.stderr,assertion=r.stderr.splitlines()[-1]);results.append(result);print(json.dumps(result),flush=True)
sp=importlib.util.spec_from_file_location('suite',root/'kc-dev-flow-2/scripts/test_sd_dispatch.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
for key in ['roster-question-prerequisites','roster-adoption-prerequisites']:
 gaps={k:v for k,v in m.fix_gaps(m.at_0_10_1(m.pinned_texts(),key)).items() if any(v)}
 result=dict(name=key,caught=key in gaps,gaps=gaps);results.append(result);print(json.dumps(result),flush=True)
pathlib.Path('/tmp/roster-validation2-a8536dc5/mutations.json').write_text(json.dumps(results,indent=2))
assert all(x['caught'] for x in results)
