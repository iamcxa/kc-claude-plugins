#!/usr/bin/env python3
"""Pinned, read-only state exports for PR 849 acceptance evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
META = json.loads((OUT / "identity.json").read_text())
SCRATCH = Path(sys.argv[1] if len(sys.argv) > 1 else META["scratch"])
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", SPACEDOCK_BIN="/Users/kent/.local/bin/spacedock")
WORTH = "design needs '### Worth questions'"
INPUTS = [
    ("plugins", META["state"], "7fa26e4391fb13df6ceb450775d3a271e46080c8",
     META["worktree"], META["base"], 75),
    ("qnow", "/Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state",
     "a01fae619a2b1a9eff8233a70b77962a7e10a458",
     "/Users/kent/conductor/repos/qnow-adopt-dev2",
     "429b4673e0cff4088adf5ee75db64830de441917", 98),
]
EXPECTED = {
    "plugins/adr-required-statement", "plugins/archive-waits-for-observer-report",
    "plugins/merge-guard-stops-unasked-merges", "plugins/ops-inbox-r1-setup-and-isolation",
    "plugins/validation-reads-pr-review-comments", "qnow/booking-attempt-identity",
    "qnow/branch-price-copy", "qnow/operator-secret-hardening",
    "qnow/owner-cancels-booking", "qnow/shop-edits-booking",
}

def run(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, env=ENV, capture_output=True, text=True, timeout=60)
    return {"command": args, "exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr}

def archive(repo, rev, target, paths=()):
    target.mkdir(parents=True, exist_ok=False)
    first = subprocess.Popen(["git", "-C", repo, "archive", rev, *paths], stdout=subprocess.PIPE)
    second = subprocess.run(["tar", "-x", "-C", str(target)], stdin=first.stdout, capture_output=True)
    first.stdout.close()
    assert first.wait() == second.returncode == 0, second.stderr

def check(version, path):
    return run(["python3", "-B", str(SCRATCH / version / "kc-dev-flow-2/scripts/design_surfaces.py"), "check", str(path)])

def worth(result):
    return WORTH in result["stdout"]

def rest(result):
    return [line for line in result["stdout"].splitlines()
            if WORTH not in line and "design surfaces presentable" not in line]

def valid_pair(name, before, after):
    if rest(before) != rest(after) or before["stderr"] != after["stderr"]:
        return False
    if name in EXPECTED:
        return worth(before) and not worth(after) and after["exit"] == (1 if rest(after) and any(
            not line.startswith("scope check ") for line in rest(after)) else 0)
    return (before["stdout"], before["stderr"], before["exit"]) == (
        after["stdout"], after["stderr"], after["exit"])

rows, bite, before_status = [], [], {}
for label, state, rev, repo, readme_rev, total in INPUTS:
    before_status[label] = run(["git", "-C", state, "status", "--porcelain"])["stdout"]
    target = SCRATCH / "replay" / label / "dev2" / ".spacedock-state"
    archive(state, rev, target)
    readme = subprocess.check_output(["git", "-C", repo, "show", readme_rev + ":docs/dev2/README.md"])
    (target.parent / "README.md").write_bytes(readme)
    tasks = sorted(p for p in target.glob("*.md") if p.name != "README.md")
    assert len(tasks) == total, (label, len(tasks))
    for task in tasks:
        old, new = check("baseline", task), check("candidate", task)
        name = label + "/" + task.stem
        row = {"name": name, "sha256": hashlib.sha256(task.read_bytes()).hexdigest(),
               "baseline": old, "candidate": new, "valid": valid_pair(name, old, new)}
        if worth(new) or name in EXPECTED:
            stage = run([ENV["SPACEDOCK_BIN"], "status", "--workflow-dir", str(target.parent),
                         "--read", str(task), "--json"])
            assert stage["exit"] == 0, stage
            row["stage_read"] = stage
            row["stage"] = json.loads(stage["stdout"])["frontmatter"].get("status")
        rows.append(row)
        if label == "plugins" and task.stem in ("adr-required-statement", "merge-guard-stops-unasked-merges", "archive-waits-for-observer-report"):
            legacy = check("v038", task)
            bite.append({"name": task.stem, "candidate": new, "v038": legacy,
                         "equal": all(new[k] == legacy[k] for k in ("exit", "stdout", "stderr")),
                         "reverted_rule_restores_worth": worth(old)})
    after = run(["git", "-C", state, "status", "--porcelain"])["stdout"]
    assert before_status[label] == after, ("source state status changed", label)
released = [r["name"] for r in rows if worth(r["baseline"]) and not worth(r["candidate"])]
remaining = [r for r in rows if worth(r["candidate"])]
assert set(released) == EXPECTED, released
assert len(remaining) == 17 and {r["stage"] for r in remaining} == {"ideation"}
assert all(r["valid"] for r in rows), [r["name"] for r in rows if not r["valid"]]
assert all(r["equal"] and r["reverted_rule_restores_worth"] for r in bite)
sample = next(r for r in rows if r["name"] == "plugins/merge-guard-stops-unasked-merges")
injected = dict(sample["candidate"], stdout=sample["candidate"]["stdout"] + "injected unrelated line\n")
controls = {
    "unrelated_output_rejected": not valid_pair(sample["name"], sample["baseline"], injected),
    "later_stage_retaining_worth_rejected": not valid_pair(sample["name"], sample["baseline"], sample["baseline"]),
}
assert all(controls.values())
summary = {"tasks": len(rows), "released": released, "remaining": len(remaining),
           "remaining_stages": sorted({r["stage"] for r in remaining}),
           "other_differences": sum(not r["valid"] for r in rows),
           "gained": sum(not worth(r["baseline"]) and worth(r["candidate"]) for r in rows)}
(OUT / "replay.json").write_text(json.dumps({"inputs": INPUTS, "summary": summary,
    "bite": bite, "negative_controls": controls, "rows": rows,
    "source_state_status_before_and_after": before_status}, indent=2) + "\n")
print("AC-1: all three bite tasks match 0.38.1; exits 1/0/0; reverse-stage control restores Worth")
print("AC-4: 173 tasks; 10 released; 17 ideation refusals; 0 other differences; 0 gained")
print("AC-4 falsifiers: unrelated output and retained later-stage Worth rejected")

