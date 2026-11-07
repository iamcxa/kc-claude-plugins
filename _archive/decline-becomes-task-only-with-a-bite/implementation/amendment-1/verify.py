#!/usr/bin/env python3
"""Verify the Captain-amended repeat-only replay from recorded fresh runs."""
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parent
state = root.parents[2]
worktree = Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-decline-becomes-task-only-with-a-bite")
candidate = "ae7750375bc19e482f829edc9a041d95fb280693"
task = (state / "decline-becomes-task-only-with-a-bite.md").read_text()
moves = json.loads((root / "criteria-move.json").read_text())
criteria = task.split("## Acceptance criteria\n", 1)[1].split("## Decisions for the Captain\n", 1)[0]
amendment = task.split("### Amendment 1", 1)[1].split("## Stage Report", 1)[0]
assert "**AC-4**" not in criteria and "**AC-7**" in criteria
assert "Superseded text:\n" + moves["original_block"] in amendment
assert moves["replacement_block"] in criteria
record = (root / "record-e.md").read_text()
for name, old in [("candidate", "candidate-1.prompt.md"), ("base", "base.prompt.md"),
                  ("mutation", "missing-bite-1.prompt.md")]:
    expected = (root.parent / old).read_text()
    for before, after in [("four records below", "five records below"),
                          ("four requested lines", "five requested lines"),
                          ("four decline records from four tasks", "five decline records from five tasks"),
                          ("For each record A to D", "For each record A to E")]:
        expected = expected.replace(before, after)
    assert (root / f"{name}.prompt.md").read_text() == expected.rstrip() + "\n" + record
rows = []
runs = json.loads((root / "sonnet-runs.json").read_text())
assert len({x["agentId"] for x in runs}) == 4
for run in runs:
    assert run["provider"] == "claude" and run["model"] == "sonnet" and run["archived"]
    data = json.loads((root / run["activity_file"]).read_text())["structuredContent"]
    assert data["updateCount"] == 2, "A no-tools run must contain only prompt and final reply"
    activity = data["content"]
    found = re.findall(r"^([A-E]) \| (violation|ok) \| (.+)$", activity, re.M)
    assert len(found) == 5, run
    verdicts = {letter: verdict for letter, verdict, quote in found}
    quotes = {letter: quote for letter, verdict, quote in found}
    expected = dict(A="ok", B="ok", C="ok", D="violation",
                    E="violation" if run["name"].startswith("candidate") else "ok")
    assert verdicts == expected, (run["name"], verdicts)
    if run["name"].startswith("candidate"):
        assert "a repeat in a later round or task" in quotes["E"]
    rows.append({**run, "verdicts": verdicts, "E_reading": quotes["E"], "status": "passed"})
(root / "results.json").write_text(json.dumps(rows, indent=2) + "\n")
pr = json.loads((root / "pr-800.json").read_text())
assert pr["headRefOid"] == candidate and pr["state"] == "OPEN"
assert subprocess.check_output(["git", "-C", str(worktree), "rev-parse", "HEAD"], text=True).strip() == candidate
assert not subprocess.check_output(["git", "-C", str(worktree), "status", "--porcelain"], text=True)
tests = [
    {"name": "AC-4 moved verbatim into amendment 1; AC-7 replaces it", "status": "passed"},
    {"name": "Candidate/base/mutation prompts retain A-D and append identical synthetic E", "status": "passed"},
    {"name": "Two fresh no-tools Sonnet candidate runs require E task, quoting repeat clause", "status": "passed"},
    {"name": "Two fresh no-tools Sonnet mutation runs read E ok; A-D retained beside E", "status": "passed"},
    {"name": "Product tree clean and PR 800 still at unchanged candidate", "status": "passed"},
]
(root / "tests.json").write_text(json.dumps(tests, indent=2) + "\n")
print("Amendment 1 verified: candidate E violation twice, mutation E ok twice; A-D retained; product unchanged.")
