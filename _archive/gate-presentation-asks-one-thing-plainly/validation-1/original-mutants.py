import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
wt, output = map(Path, sys.argv[1:])
scripts = wt / "kc-dev-flow-2/scripts"
output.mkdir(parents=True, exist_ok=True)
helper = (scripts / "decision_ledger.py").read_text()
start, end = helper.index("def quotes_bound_question("), helper.index("\ndef ledger(")
whole = helper[start:end]
def helper_variant(body):
    return "def quotes_bound_question(row):\n" + body + "\n\n"
cases = [
 ("reminder-on-entry", "design_surfaces.py", '    notes = []\n', '    from delivery_gate import ASK_FORM\n    print(ASK_FORM)\n    notes = []\n', "test_design_surfaces.py", "AskFormTests"),
 ("reminder-status-guard-removed", "design_surfaces.py", 'if status and status.group(1) in ("backlog", "ideation"):', 'if True:', "test_design_surfaces.py", "AskFormTests"),
 ("reminder-dropped", "design_surfaces.py", '            print(ASK_FORM)\n', '            pass\n', "test_design_surfaces.py", "AskFormTests"),
 ("question-reminder-on-entry", "delivery_gate.py", 'def question(args):\n', 'def question(args):\n    emit(ASK_FORM)\n', "test_delivery_gate.py", "BoundApprovalTests"),
 ("question-reminder-dropped", "delivery_gate.py", 'emit("gate text complete", ASK_FORM)', 'emit("gate text complete")', "test_delivery_gate.py", "BoundApprovalTests"),
 ("prefix-only", "decision_ledger.py", whole, helper_variant('    return bool(row.get("question") and row["question"][:10] in (row.get("reason") or ""))'), "test_delivery_gate.py", "BoundApprovalTests"),
 ("any-quote", "decision_ledger.py", whole, helper_variant('    return "「" in (row.get("reason") or "")'), "test_decision_ledger.py", "BoundQuestionTests"),
 ("oldest-approval", "delivery_gate.py", 'max(captain, key=lambda r: r["at"] or "")', 'min(captain, key=lambda r: r["at"] or "")', "test_delivery_gate.py", "BoundApprovalTests"),
 ("exact-whitespace", "decision_ledger.py", whole, helper_variant('    return bool(row.get("question") and "answering 「" + row["question"] + "」" in (row.get("reason") or ""))'), "test_delivery_gate.py", "BoundApprovalTests"),
 ("agent-resolution-judged", "delivery_gate.py", ' and r["by"] == "person:captain"', '', "test_delivery_gate.py", "BoundApprovalTests"),
 ("nested-brackets-regex", "decision_ledger.py", whole, helper_variant('    match = re.search(r"answering 「(.*?)」", row.get("reason") or "")\n    return bool(match and "".join(match[1].split()) == "".join((row.get("question") or "").split()))'), "test_decision_ledger.py", "BoundQuestionTests"),
 ("reminder-leaks-to-idle", "pr_watch.py", 'def seeds(', 'def seeds(', "test_pr_watch.py", "test_a_backlog_task_the_seed_check_refuses_is_named_in_one_line_and_an_accepted_one_is_not"),
]
rows = []
with tempfile.TemporaryDirectory(prefix="gate-falsifiers-") as td:
    copy = Path(td, "kc-dev-flow-2/scripts")
    shutil.copytree(scripts, copy, ignore=shutil.ignore_patterns("__pycache__"))
    def run(pattern, name):
        for cache in copy.rglob("__pycache__"):
            shutil.rmtree(cache)
        done = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(copy), "-p", pattern, "-k", name],
                              capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE":"1"}, cwd=td)
        return done
    for pattern, name in sorted(set((c[4], c[5]) for c in cases)):
        done = run(pattern, name)
        assert done.returncode == 0, done.stdout + done.stderr
    for name, filename, old, new, pattern, selection in cases:
        path = copy / filename
        original = path.read_text()
        if name == "reminder-leaks-to-idle":
            match = re.search(r"(?m)^def seeds\([^\n]+\):\n", original)
            assert match
            old = match[0]
            new = old + '    from delivery_gate import ASK_FORM\n    print(ASK_FORM)\n'
        assert original.count(old) == 1, (name, original.count(old))
        path.write_text(original.replace(old, new))
        done = run(pattern, selection)
        path.write_text(original)
        log = output / (name + ".log")
        log.write_text(done.stdout + done.stderr)
        caught = done.returncode == 1 and "FAIL:" in done.stderr and "ERROR:" not in done.stderr
        rows.append({"name":name, "caught":caught, "exit":done.returncode, "log":str(log)})
        assert caught, (name, done.stdout, done.stderr)
(output / "mutations.json").write_text(json.dumps(rows, indent=2))
print(json.dumps({"mutations":len(rows), "caught":sum(r["caught"] for r in rows)}))
