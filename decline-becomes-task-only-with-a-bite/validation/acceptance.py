#!/usr/bin/env python3
"""Validation rerun of implementation acceptance, using exact archive exports only."""
import argparse
import ast
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

BASE = "ba055b8a7a55a787ac989c4cef52d07dd75661ad"
STATE_REV = "79af09021bcfdb30267aabbc4f2dc150ac05a6dd"
ADR = "docs/adr/0064-a-round-three-declined-finding-becomes-a-backlog-task-only-with-a-bite.md"
OLD_ADR = "docs/adr/0010-a-round-three-declined-finding-becomes-its-own-backlog-task.md"
WORKFLOW = "kc-dev-flow-2/references/sd/workflow.md"
NAMED = [WORKFLOW, "kc-dev-flow-2/scripts/test_sd_dispatch.py", OLD_ADR, ADR]
p = argparse.ArgumentParser()
p.add_argument("worktree", type=Path)
p.add_argument("state", type=Path)
p.add_argument("package", type=Path)
p.add_argument("sd_plugin", type=Path)
a = p.parse_args()
context = json.loads((Path(__file__).parent / "context.json").read_text())
repo = Path(context["worktree"])
out = Path(__file__).resolve().parent
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
results = []

def check(name, fn):
    try:
        detail = fn()
        results.append(dict(name=name, status="passed", message=str(detail or "")))
    except Exception as exc:
        results.append(dict(name=name, status="failed", message=str(exc)))
        raise
    finally:
        (out / "tests.json").write_text(json.dumps(results, indent=2) + "\n")

def command(name, args, cwd=None, expected=0):
    r = subprocess.run([str(x) for x in args], cwd=cwd or a.worktree, env=(dict(env, GIT_DIR=context["git_dir"], GIT_WORK_TREE=str(a.worktree), GIT_OPTIONAL_LOCKS="0")
                            if name in ("adr-lint", "number-guards") else env),
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / (name + ".log")).write_text(r.stdout)
    assert r.returncode == expected, (name, r.returncode, r.stdout[-2000:])
    return r.stdout

def git_show(rev, path):
    return subprocess.check_output(["git", "-C", str(a.state), "show", f"{rev}:{path}"], text=True)

def load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def clear_caches(root):
    for path in root.rglob("__pycache__"):
        shutil.rmtree(path)

with tempfile.TemporaryDirectory(prefix="decline-bite-validation-", dir="/tmp") as tmp:
    tmp = Path(tmp)
    base, candidate = tmp / "base", tmp / "candidate"
    base.mkdir()
    archive = subprocess.check_output(["git", "-C", str(repo), "archive", BASE,
                                       "kc-dev-flow-2", "scripts", "docs/adr"])
    with tarfile.open(fileobj=io.BytesIO(archive)) as archive_file:
        archive_file.extractall(base, filter="data")
    candidate.mkdir()
    archive = subprocess.check_output(["git", "-C", str(repo), "archive", context["head"],
                                       "kc-dev-flow-2", "scripts", "docs/adr"])
    with tarfile.open(fileobj=io.BytesIO(archive)) as archive_file:
        archive_file.extractall(candidate, filter="data")
    clear_caches(candidate)
    check("AC-1 repository skill lint and unchanged budget",
          lambda: command("lint", ["python3", "-B", a.worktree / "kc-dev-flow-2/scripts/lint-skills.py"]))
    def budget():
        old = (base / WORKFLOW).read_text()
        new = (candidate / WORKFLOW).read_text()
        old_sentence = re.search(r"FO declines it.*?Scope\.", old, re.S).group()
        new_sentence = re.search(r"FO declines it.*?Scope\.", new, re.S).group()
        assert len(old.split()) == len(new.split()) == 5939
        assert len(old_sentence.split()) == len(new_sentence.split()) == 53
        assert (base / "kc-dev-flow-2/scripts/lint-skills.py").read_bytes() == (a.worktree / "kc-dev-flow-2/scripts/lint-skills.py").read_bytes()
        return "workflow 5939 -> 5939; step 5 sentence 53 -> 53; no budget-script change"
    check("AC-1 reading count", budget)
    helper = a.state / "decline-becomes-task-only-with-a-bite/ideation"
    def pins():
        text = command("pins-candidate", ["python3", "-B", helper / "pins.py", candidate / "kc-dev-flow-2"])
        assert "ROUND_RULE missing: []" in text
        assert "follow-up-reason gaps: ([], [])" in text
        assert "proposed pins missing: []" in text and "proposed swap matches: 1" in text
        text = command("pins-base", ["python3", "-B", helper / "pins.py", base / "kc-dev-flow-2"])
        line = next(l for l in text.splitlines() if l.startswith("proposed pins missing:"))
        assert len(ast.literal_eval(line.split(":", 1)[1].strip())) == 3
        assert "proposed swap matches: 0" in text
        return "candidate no gaps, swap 1; base three new pins absent, swap 0"
    check("AC-2 candidate and base wording pins", pins)
    module_path = candidate / "kc-dev-flow-2/scripts/test_sd_dispatch.py"
    dispatch = load("candidate_dispatch", module_path)
    # Execute the actual enforcement assertion from exercise(), not a copied assertion.
    tree = ast.parse(module_path.read_text())
    exercise = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "exercise")
    nodes = next(n.body for n in exercise.body if isinstance(n, ast.Try))
    index = next(i for i, n in enumerate(nodes) if isinstance(n, ast.Assert)
                 and isinstance(n.msg, ast.Constant) and n.msg.value == "round rule missing from workflow.md")
    pin_code = compile(ast.fix_missing_locations(ast.Module(body=nodes[index-1:index+1], type_ignores=[])),
                       str(module_path), "exec")
    def rejected_pin(name, changed):
        path = tmp / (name + ".md")
        path.write_text(changed)
        clear_caches(candidate)
        try:
            exec(pin_code, dict(TEMPLATE=path, ROUND_RULE=dispatch.ROUND_RULE))
        except AssertionError as exc:
            assert str(exc) == "round rule missing from workflow.md"
            (out / (name + ".log")).write_text(str(exc) + "\n")
            return str(exc)
        raise AssertionError("mutated wording passed the real ROUND_RULE assertion")
    check("AC-1 falsifier restore old step 5",
          lambda: rejected_pin("restore-old", (base / WORKFLOW).read_text()))
    check("AC-2 falsifier remove observed-failure clause",
          lambda: rejected_pin("remove-clause", (candidate / WORKFLOW).read_text().replace(
              "Only an observed failure naming who it hurts", "", 1)))
    def replays():
        gate = load("candidate_gate", candidate / "kc-dev-flow-2/scripts/delivery_gate.py")
        assert (base / "kc-dev-flow-2/scripts/delivery_gate.py").read_bytes() == (a.worktree / "kc-dev-flow-2/scripts/delivery_gate.py").read_bytes()
        rows = []
        fixture = None
        for slug, count in [("fo-tries-what-it-asks-the-captain", 3),
                            ("model-roster-question-needs-both-families", 2),
                            ("rewritten-criteria-checked-against-captain-words", 3)]:
            path = f"_archive/{slug}/review/validation/briefing-1/index.json"
            raw = git_show(STATE_REV, path)
            assert raw == git_show("HEAD", path), "helper's HEAD fixture drifted"
            d = json.loads(raw)
            sha, path = re.match(r"git-root://state/([0-9a-f]{40})/(.+)$", d["artifacts"][0]["uri"]).groups()
            text = d["question"] + "\n" + "\n".join(x.get("summary", "") for x in d["artifacts"])
            task = git_show(sha, path)
            problems, _ = gate.text_problems(task, text)
            declines = [x for x in problems if "declin" in x.lower()]
            assert len(gate.declined_items(text)) == count and not declines, (slug, declines)
            rows.append(dict(task=slug, bound=sha, declined=count, problems=declines))
            fixture = task, text
        (out / "gate-replays.json").write_text(json.dumps(rows, indent=2) + "\n")
        command("replay-gate", ["python3", "-B", helper / "replay_gate.py", a.state,
                              candidate / "kc-dev-flow-2/scripts"])
        task, text = fixture
        item = gate.declined_items(text)[0]
        # Change only the reason's delimiters on one real archived decline.
        unbracketed = item.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        assert item in text and item != unbracketed
        mutated = text.replace(item, unbracketed, 1)
        problems, _ = gate.text_problems(task, mutated)
        (out / "remove-bracket.log").write_text("\n".join(problems) + "\n")
        assert any("declined item has no reason" in x for x in problems), problems
        return "3/2/3 declined items pass; removed reason delimiters are rejected"
    check("AC-3 archived declines and bracket falsifier", replays)
    def ruling():
        old, new = (candidate / OLD_ADR).read_text(), (candidate / ADR).read_text()
        assert "## Status\n\nSuperseded by 0064\n" in old
        assert "## Status\n\nAccepted\n" in new
        source = (a.state / "decline-becomes-task-only-with-a-bite.md").read_text().replace("''", "'")
        flatten = lambda s: "".join(s.split())
        for question in re.findall(r"\*\*Asked:\*\* (.+)", new):
            assert flatten(question) in flatten(source), question
        assert "「核准（建議）」" in new and "「可以，但是該怎樣紀錄合理的followup」" in new
        mutated = old.replace("Superseded by 0064", "Accepted", 1)
        assert "## Status\n\nAccepted\n" in mutated and "## Status\n\nAccepted\n" in new
        (out / "old-adr-accepted.log").write_text(
            "Mutation: 0010 Status restored to Accepted.\nAccepted opposite step-5 rulings: 0010 and 0064.\n")
        return "0064 accepted; 0010 superseded; bound questions verbatim; mutation leaves both accepted"
    check("AC-6 ruling, quotes and supersession falsifier", ruling)
    check("Required ADR lint", lambda: command("adr-lint", ["python3", "-B",
          a.package / "scripts/adr_lint.py", "docs/adr", "--since", BASE, "--require", "0010", "0064"]))
    check("Required number guards", lambda: command("number-guards", ["python3", "-B",
          a.package / "scripts/number_guards.py", "check", "--workflow-dir",
          a.state.parent, "--task", a.state / "decline-becomes-task-only-with-a-bite.md"]))
    check("Required design-surface check", lambda: command("design-surfaces", ["python3", "-B",
          a.package / "scripts/design_surfaces.py", "check",
          a.state / "decline-becomes-task-only-with-a-bite.md"]))
    check("AC-2 native dispatch suite after lint workaround", lambda: command("dispatch", ["python3", "-B",
          a.worktree / "kc-dev-flow-2/scripts/test_sd_dispatch.py", "--sd-plugin-root", a.sd_plugin]))
print(f"{len(results)} deterministic acceptance groups passed; fresh Sonnet evidence is recorded separately.")
