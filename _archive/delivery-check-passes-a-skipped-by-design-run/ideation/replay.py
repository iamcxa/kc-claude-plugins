import json, sys, importlib.util
from pathlib import Path
d = Path(sys.argv[1]); fx = Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("t", d / "test_delivery_gate.py"); t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
f = json.load(open(fx)); req = f["required"]
head = f["head"]; roll, wr = f["statusCheckRollup"], f["workflow_runs"]
def go(label, rollup, runlist, required):
    if hasattr(t.gate, "required_checks"):
        t.gate.required_checks = lambda repo, number: required
    r = t.run_check(head=head, records={"validation-1.md": t.record(head)}, facts=dict(statusCheckRollup=rollup, mergeable="MERGEABLE", baseRefName="main", changedFiles=1),
                    runs=dict(total_count=len(runlist), workflow_runs=runlist))
    print(f"== {label}: exit {r.code}, printed words {len(r.out.split())}")
    for l in r.out.splitlines():
        if l != t.CLAIM_SOURCE and not l.startswith(("point:", "class:", "record")): print("   ", l)
pg = lambda **k: [dict(c, **k) if c.get("name") == "pr-test / pg-tests" else c for c in roll]
pc = lambda **k: [dict(w, **k) if w["name"] == "PR Checking" else w for w in wr]
go("#1338 as read", roll, wr, req)
go("pg-tests FAILURE", pg(conclusion="FAILURE"), pc(conclusion="failure"), req)
go("pg-tests pending", pg(status="IN_PROGRESS", conclusion=None), pc(status="in_progress", conclusion=None), req)
noci = [dict(c, conclusion="SKIPPED") if c.get("workflowName") == "PR Checking" else c for c in roll if c.get("__typename") == "CheckRun"]
go("PR Checking skipped whole (unexpected), required ci-gate only skipped", noci, pc(conclusion="skipped"), [r for r in req if r["bucket"] == "skipping"])
go("same, repo reports no required checks (relay/web)", noci, pc(conclusion="skipped"), [])
go("Release Gate run failed", roll, [dict(w, conclusion="failure") if w["name"] == "Release Gate" else w for w in wr], req)
