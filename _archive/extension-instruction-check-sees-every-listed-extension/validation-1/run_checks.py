import os,sys,json,re,subprocess,pathlib
root=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-extension-instruction-check-sees-every-listed-extension/.context/validation-pr787")
ev=pathlib.Path("/tmp/pr787-validation")
pkg=pathlib.Path("/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0")
wf=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state").parent
task=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/extension-instruction-check-sees-every-listed-extension.md")
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",SPACEDOCK_BIN="/Users/kent/.local/bin/spacedock",SD_PLUGIN_ROOT="/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3")
commands=[]
for line in (root/".github/workflows/kc-dev-flow-2-tests.yml").read_text().splitlines():
 if "run: " not in line or "python3 " not in line: continue
 command=line.split("python3 ",1)[1]
 path=command.split()[0]
 if "test" not in pathlib.Path(path).name: continue
 args=["python3","-B",path]
 if pathlib.Path(path).name=="test_sd_dispatch.py": args+=["--sd-plugin-root","/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3"]
 commands.append((path,args))
for name,args in [
 ("lint",["python3","-B","kc-dev-flow-2/scripts/lint-skills.py"]),
 ("parity",["bash","scripts/version-parity-check.sh"]),
 ("adr-lint",["python3","-B",str(pkg/"scripts/adr_lint.py"),"docs/adr","--since","d37c6dc653e0f45d6ca630c2faa6121c0863a57e"]),
 ("comment-ratio",["python3","-B",str(pkg/"scripts/comment_ratio.py"),"d37c6dc653e0f45d6ca630c2faa6121c0863a57e","272721000cce947c8f2dcdd3a40c22cdf11dee09","--workflow-dir",str(wf)]),
 ("doc-impact",["python3","-B",str(pkg/"scripts/doc_impact.py"),"d37c6dc653e0f45d6ca630c2faa6121c0863a57e","272721000cce947c8f2dcdd3a40c22cdf11dee09"]),
 ("design-surfaces",["python3","-B",str(pkg/"scripts/design_surfaces.py"),"check",str(task)]),
 ("number-guards",["python3","-B",str(pkg/"scripts/number_guards.py"),"check","--workflow-dir",str(wf),"--task",str(task)]),
 ("dispatch-records",["python3","-B",str(pkg/"scripts/dispatch_records.py"),str(task.with_suffix(""))]),
 ("native-dispatch",["python3","-B","kc-dev-flow-2/scripts/test_dispatch_records.py","ContextNoticeTests.test_workflow_strict_preflight_holds_then_repaired_context_reaches_real_builder_fixture"])
]: commands.append((name,args))
results=[]
for name,args in commands:
 log=ev/(pathlib.Path(name).stem+".log")
 try:
  with log.open("w") as f: done=subprocess.run(args,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
  code=done.returncode
 except subprocess.TimeoutExpired: code=124
 text=log.read_text()
 results.append(dict(name=name,status="passed" if code==0 else "failed",exit=code,command=args,log=str(log),message=text[-1200:]))
 (ev/"checks.json").write_text(json.dumps(results,indent=2))
 print(name,code,flush=True)
sys.exit(any(x["exit"] for x in results))

