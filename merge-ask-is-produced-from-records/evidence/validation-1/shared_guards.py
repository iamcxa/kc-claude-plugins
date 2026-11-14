from pathlib import Path
import contextlib, hashlib, io, json, os, re, sys
from unittest import mock

WT = Path(os.environ["PRODUCT_WORKTREE"])
OUT = Path(__file__).parent
sys.path.insert(0, str(WT / "kc-dev-flow-2/scripts"))
import test_delivery_gate as tests
gate = tests.gate
case = tests.RecordRouteParityTests()
original = gate.question
rows = []

def run_case(name, broken, mutant):
    def question(args):
        task, q = Path(args.task), Path(args.text_file)
        path = Path(args.facts_record) if args.facts_record else None
        summary = Path(args.summary_file) if args.summary_file else None
        data = json.loads(path.read_text()) if path else None
        if broken:
            target = q if path else summary
            text = target.read_text()
            if name == "reviewer declaration":
                target.write_text(text.replace(tests.DECLARATION, ""))
            elif name == "prod trigger":
                target.write_text(text.replace(tests.DECLARATION, "Second reviewer: not triggered.\n"))
                task.write_text(task.read_text().replace("profile: pilot", 'profile: "prod"'))
            elif name == "merge head":
                q.write_text(q.read_text().replace(tests.HEAD40, "not-a-sha"))
            elif name == "current configuration":
                readme = task.parent / "README.md"
                readme.write_text(readme.read_text().replace("second-reviewer: copilot", "second-reviewer: invalid"))
            elif name == "Captain steps":
                p = gate.task_folder(task) / "captain-steps/1.md"
                p.write_text(p.read_text().replace("Candidate:", "Unbound candidate:"))
                if path:
                    data["captain_steps"] = gate.observed_steps(task, tests.HEAD40)
            elif name == "merge hold clause":
                q.write_text(q.read_text().replace("unless he says he merges or holds", "after approval"))
            elif name == "worktree removal":
                q.write_text(q.read_text().replace("and removing its clean, pushed worktree", "and keeping its worktree"))
            elif name == "merge-result disclosure":
                if path:
                    data["merge_result"] = "not run"
                else:
                    p = next((gate.task_folder(task) / "merge").glob("ask-*.json"))
                    d = json.loads(p.read_text()); d["merge_result"] = "not run"; p.write_text(json.dumps(d))
            if path:
                data["question_sha256"] = hashlib.sha256(q.read_bytes()).hexdigest()
                path.write_text(json.dumps(data))
        with contextlib.ExitStack() as stack:
            if mutant:
                if name in {"reviewer declaration", "prod trigger"}:
                    stack.enter_context(mock.patch.object(gate, "reviewer_problems", return_value=([], [])))
                elif name == "merge head":
                    stack.enter_context(mock.patch.object(gate, "merge_head_matches", return_value=True))
                elif name == "current configuration":
                    stack.enter_context(mock.patch.object(gate, "reviewer_config", return_value=("copilot", {"codex", "copilot"})))
                elif name == "Captain steps":
                    stack.enter_context(mock.patch.object(gate, "captain_step_problems", return_value=[]))
                elif name == "merge hold clause":
                    stack.enter_context(mock.patch.object(gate, "grant_without_hold_out", return_value=False))
                elif name == "worktree removal":
                    stack.enter_context(mock.patch.object(gate, "WORKTREE_REMOVAL", re.compile("")))
                elif name == "merge-result disclosure":
                    stack.enter_context(mock.patch.object(gate, "MERGE_NOT_RUN", re.compile("")))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = original(args)
            logs.append(dict(route="record" if path else "legacy", exit=code, output=out.getvalue()))
            return code
    logs = []
    with mock.patch.object(gate, "question", question):
        pair = case.paired()
    return dict(check={r: pair[r]["check"] for r in pair}, question={r: pair[r]["question"] for r in pair}, logs=logs)

for name in ("reviewer declaration", "prod trigger", "merge head", "current configuration",
             "Captain steps", "merge hold clause", "worktree removal", "merge-result disclosure"):
    controls = run_case(name, False, False)
    negative = run_case(name, True, False)
    mutation = run_case(name, True, True)
    assert set(controls["check"].values()) == {0}, (name, controls)
    assert set(controls["question"].values()) == {0}, (name, controls)
    assert all(v != 0 for v in negative["question"].values()), (name, negative)
    assert set(mutation["question"].values()) == {0}, (name, mutation)
    rows.append(dict(name=name, status="passed", controls=controls, negative=negative, mutation=mutation,
                     scope="Only the shared question guard is disabled after a passing producer; facts digests are refreshed to isolate that guard. No product bytes changed."))
    (OUT / "shared-guard-mutations.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(name, "caught by both input routes", flush=True)
