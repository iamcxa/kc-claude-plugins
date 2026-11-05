import importlib.util, json, sys
from pathlib import Path
pkg = Path(sys.argv[1])
sys.path.insert(0, str(pkg/"scripts"))
import test_pr_watch as tw
import test_delivery_gate as tg
out = {}
def scenario(name):
    f=tw.TasksTests("test_a_pr_a_worker_opened_is_recorded_with_two_commands_and_then_watched")
    f.setUp()
    try:
        f.readme("roborev")
        if name == "open":
            f.task("some-task")
            code, lines=f.tasks({"pr list":[{"number":7,"state":"OPEN"}],"pr view 7":tw.view(checks="PENDING")})
        elif name == "merged":
            f.task("some-task",pr="o/r#7")
            f.report("some-task")
            code, lines=f.tasks({"pr view 7":tw.view("MERGED")})
        elif name == "archive":
            f.readme("learn")
            f.archive("some-task")
            from unittest import mock
            _,patch=f.notice_run({"notices":[]})
            with patch:
                code,lines=f.tasks({})
        elif name == "seed":
            f.ideation_readme()
            f.backlog("fine")
            f.gates(("fine","backlog","needs-preparation"))
            code,lines=f.tasks({})
        assert code == 0, (name,lines)
        return "\n".join(lines).replace(str(f.root), "<scratch>")
    finally:
        f.doCleanups()
for name in ("open","merged","archive","seed"):
    out[name]=scenario(name)
f=tg.BoundApprovalTests("test_unquoted_or_prefix_only_approval_asks_separately") if hasattr(tg,"BoundApprovalTests") else None
out["ask"]=tg.run_check().out
from tempfile import TemporaryDirectory
import subprocess
with TemporaryDirectory() as td:
    d=Path(td)
    import test_design_surfaces as ts
    for stage,seed in (("backlog",True),("ideation",False),("implementation",False),("validation",False)):
        path=d/"task.md"
        path.write_text(ts.GATED.replace("status: ideation",f"status: {stage}"))
        done=subprocess.run([sys.executable,"-B",str(pkg/"scripts/design_surfaces.py"),"check",*(["--seed"] if seed else []),str(path)],capture_output=True,text=True)
        assert done.returncode == 0, done.stdout+done.stderr
        out[stage]=done.stdout
import test_design_surfaces as ts
scope=ts.ScopeCheckTests("test_an_unchanged_scope_is_clean_and_prints_the_presentable_line")
scope.setUp()
try:
    code, said=scope.run_main()
    assert code == 0
    out["ideation"]=said
finally:
    scope.doCleanups()
code,said=tg.QuestionTests().ask("Deliver it.")
assert code == 0, said
out["question"]=said
print(json.dumps(out,ensure_ascii=False))
