#!/usr/bin/env python3
"""Public-corpus evidence. Usage: python3 -B verify.py CODE STATE PACKAGE SCRATCH."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
import tempfile

code, state, package, scratch = map(Path, sys.argv[1:])
evidence = Path(__file__).resolve().parent
scripts = code / "kc-dev-flow-2/scripts"
helper = scripts / "task_timeline.py"
scratch.mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(scratch)
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(scratch)}
summary = []


def run(name, args, expected=0, cwd=code):
    result = subprocess.run(list(map(str, args)), cwd=cwd, env=env, capture_output=True, text=True)
    (evidence / f"{name}.log").write_text(result.stdout + result.stderr)
    summary.append({"name": name, "command": list(map(str, args)), "exit": result.returncode,
                    "expected": expected, "matched": result.returncode == expected})
    (evidence / "commands.json").write_text(json.dumps(summary, indent=2))
    assert result.returncode == expected, (name, result.returncode, result.stderr)
    return result.stdout


sys.path.insert(0, str(scripts))
import task_timeline as tt
import test_task_timeline as tests


class Results(unittest.TextTestResult):
    rows = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.rows.append({"name": test.id(), "status": "passed"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.rows.append({"name": test.id(), "status": "failed", "message": self._exc_info_to_string(err, test)})

    addError = addFailure


with (evidence / "tests.log").open("w") as stream:
    result = unittest.TextTestRunner(stream=stream, resultclass=Results, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(tests))
(evidence / "tests.json").write_text(json.dumps(result.rows, indent=2))
assert result.wasSuccessful()

finished = "worth-questions-asked-only-before-the-design-gate"
out = run("ac1-finished", [sys.executable, "-B", helper, state, finished, "--json"])
actual = json.loads(out)
expected = {"ideation": ("2026-11-11T14:24:19Z", "2026-11-11T14:46:03Z"),
            "implementation": ("2026-11-11T14:46:03Z", "2026-11-11T15:01:44Z"),
            "validation": ("2026-11-11T15:01:44Z", "2026-11-11T15:44:32Z")}
assert all((row["start"], row["end"]) == expected[row["stage"]]
           for row in actual["stages"] if row["stage"] in expected)
assert actual["done"] == expected["validation"][1]
run("ac1-human", [sys.executable, "-B", helper, state, finished])
run("ac1-hand-log", ["git", "-C", state, "log", "--reverse", "--format=%aI %s", "--",
                    f"{finished}.md", finished, f"_archive/{finished}.md", f"_archive/{finished}"])
run("ac2-compare-spent", [sys.executable, "-B", evidence.parent / "poc/compare_spent.py", helper, package, state])
run("ac3-ask-smoke", ["bash", evidence.parent / "poc/ask_smoke.sh", helper])
run("ac4-sweep", [sys.executable, "-B", helper, state, "--all"])
untimed = []
slugs = {p.stem for p in (state / "_archive").glob("*.md")} | {p.parent.name for p in (state / "_archive").glob("*/index.md")}
for slug in sorted(slugs):
    path = tt.find_task(state, slug)
    row = tt.timeline(state, slug)
    if not row["stages"]:
        assert not re.search(r"^started:", path.read_text(), re.M)
        assert not (tt.folder(path) / "dispatch").exists()
        untimed.append(slug)
(evidence / "ac4-untimed.json").write_text(json.dumps({"count": len(untimed), "not_dispatched": untimed}, indent=2))
run("ac5-running", [sys.executable, "-B", helper, state, evidence.parent.name, "--json"])
assert any(r["end"] is None and r["elapsed_min"] > 0 for r in tt.timeline(state, evidence.parent.name)["stages"])

mutant = scratch / "mutant"
mutant.mkdir(exist_ok=True)
for source in scripts.glob("*.py"):
    shutil.copy2(source, mutant / source.name)
source = helper.read_text()
mutations = [
    ("ac1-no-archive", 'if archived and archived["slug"] == slug and done is None:', "if False:",
     "test_finished_boundaries_use_author_dates_even_after_rebase"),
    ("ac1-committer-time", "%aI", "%cI", "test_finished_boundaries_use_author_dates_even_after_rebase"),
    ("ac2-count-files", 'n = max(len(starts.get(stage, [])), max(records.get(stage, {}), default=0))',
     'n = len(records.get(stage, {}))', "test_repeat_without_entering_uses_highest_record_number_and_excludes_messages"),
    ("ac3-ignore-asks", 'asks_file = folder(task) / "asks.jsonl"', 'asks_file = folder(task) / "none.jsonl"',
     "test_ask_cli_appends_utc_questions_and_rejects_empty_without_write"),
    ("ac4-unreadable-history", 'date, subject = head.split("\\x1f", 1)',
     'raise ValueError("mutation: unreadable history")', "test_folder_form_archived_task_is_in_sweep"),
    ("ac5-zero-running-time", 'row["elapsed"] += mins(start, end or now) or 0',
     'row["elapsed"] += mins(start, end) or 0', "test_running_stage_minutes_reach_now"),
    ("gate-only-before", 'before, after = 0.0, round(row["elapsed"] - wait, 1)',
     'before, after = before, after', "test_gate_only_stage_has_no_before_gate_minutes"),
    ("ask-wrong-stage", 'row["asks_outside_gate"] += 1', 'row["asks_outside_gate"] += 0',
     "test_asks_are_attributed_to_running_segment_with_boundary_on_next_stage"),
    ("sweep-ignore-folders", ' | {p.parent.name for p in archive.glob("*/index.md")}', '',
     "test_folder_form_archived_task_is_in_sweep"),
]
mutations.append(("repeated-stage-last-gate-only", '        after = 0.0\n        for (start, st), end in zip(segments, ends):\n            if st != stage:\n                continue\n            end = end or now\n            last = max((a["closed"] for a in attempts if a["closed"] and start <= a["closed"] <= end), default=None)\n            after += mins(last, end) or 0.0\n        after = round(after, 1)', '        last = max((a["closed"] for a in attempts if a["closed"]), default=None)\n        end = row["end"] or now\n        after = mins(last, end) if last and last < end else 0.0', "test_repeated_stage_preserves_each_cycles_after_gate_time"))
for name, old, new, test in mutations:
    assert old in source, name
    for cache in mutant.rglob("__pycache__"):
        shutil.rmtree(cache)
    (mutant / helper.name).write_text(source.replace(old, new))
    run(f"mutation-{name}", [sys.executable, "-B", "-m", "unittest",
                             f"test_task_timeline.TimelineTests.{test}"], expected=1, cwd=mutant)

run("lint-skills", [sys.executable, "-B", scripts / "lint-skills.py"])
run("lint-tests", [sys.executable, "-B", scripts / "test_lint_skills.py"])
run("ledger-tests", [sys.executable, "-B", scripts / "test_decision_ledger.py"])
run("role-tests", [sys.executable, "-B", scripts / "test_role_triggers.py"])
run("design-surfaces", [sys.executable, "-B", package / "scripts/design_surfaces.py", "check", state / f"{evidence.parent.name}.md"])
(evidence / "summary.json").write_text(json.dumps({"fixture_tests": result.testsRun,
    "mutations_caught": len(mutations), "commands": len(summary), "all_expected": all(r["matched"] for r in summary)}, indent=2))
print("verification evidence saved")
