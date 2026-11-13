import json,os,shlex,subprocess,sys
from pathlib import Path
root=Path(__file__).parent
wt=Path('<worktree>')
task=Path('<task>')
pkg=Path('<package>')
env={**os.environ,"TMPDIR":str(root/"tmp"),"PYTHONDONTWRITEBYTECODE":"1","SPACEDOCK_BIN":"<home>/.local/bin/spacedock"}
commands={
"regression":(["python3","-B","-m","unittest","discover","-s",str(root/"regression/kc-dev-flow-2/scripts"),"-p","test_design_surfaces.py","-k","test_each_declared_id_gets_a_proof_check"],1),
"design-suite":(["python3","-B","-m","unittest","discover","-s","kc-dev-flow-2/scripts","-p","test_design_surfaces.py"],0),
"records-suite":(["python3","-B","-m","unittest","discover","-s","kc-dev-flow-2/scripts","-p","test_dispatch_records.py"],0),
"laws-suite":(["python3","-B","-m","unittest","discover","-s","kc-dev-flow-2/scripts","-p","test_laws_check.py"],0),
"cases":(["python3","-B",str(root/"cases.py"),str(wt/"kc-dev-flow-2/scripts/design_surfaces.py"),str(task/"evidence/ideation-1/fixtures/run1.md"),str(task/"evidence/ideation-1/fixtures/run2.md"),str(root/"cases")],0),
"mutations":(["python3","-B",str(root/"mutations.py"),str(wt),str(root)],0),
"dispatch-stage":(["python3","-B","kc-dev-flow-2/scripts/test_dispatch_stage.py"],0),
"sd-dispatch":(["python3","-B","kc-dev-flow-2/scripts/test_sd_dispatch.py","--sd-plugin-root","<home>/.codex/plugins/cache/spacedock/spacedock/0.28.0"],0),
"lint-skills":(["python3","-B","kc-dev-flow-2/scripts/lint-skills.py"],0),
"adr-lint":(["python3","-B",str(pkg/"scripts/adr_lint.py"),"docs/adr","--since","6a1eaf837bd6087cd0b8b665dc19beaed3c44dff"],0),
"number-guards":(["python3","-B",str(pkg/"scripts/number_guards.py"),"check","--workflow-dir",str(task.parent.parent),"--task",str(task)+".md"],0),
"comment-ratio":(["python3","-B",str(pkg/"scripts/comment_ratio.py"),"6a1eaf837bd6087cd0b8b665dc19beaed3c44dff","HEAD","--workflow-dir",str(task.parent.parent)],0),
"doc-impact":(["python3","-B",str(pkg/"scripts/doc_impact.py"),"6a1eaf837bd6087cd0b8b665dc19beaed3c44dff","HEAD"],0),
"installed-design-check":(["python3","-B",str(pkg/"scripts/design_surfaces.py"),"check",str(task)+".md"],0),
"candidate-design-check":(["python3","-B","kc-dev-flow-2/scripts/design_surfaces.py","check",str(task)+".md"],0)
}
for name in sys.argv[1:]:
    args,want=commands[name]
    log=root/"checks"/(name+".log")
    with log.open("w") as output:
        done=subprocess.run(args,cwd=wt,env=env,stdout=output,stderr=subprocess.STDOUT)
    record=dict(name=name,command="TMPDIR="+shlex.quote(str(root/"tmp"))+" PYTHONDONTWRITEBYTECODE=1 SPACEDOCK_BIN=<home>/.local/bin/spacedock "+shlex.join(args),cwd=str(wt),exit=done.returncode,expected_exit=want,output="checks/"+log.name)
    (root/"checks"/(name+".json")).write_text(json.dumps(record,indent=2))
    print(name,done.returncode,"expected",want,flush=True)
    if done.returncode!=want:
        print(log.read_text()[-5000:],flush=True)
        sys.exit(1)
