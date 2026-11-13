#!/usr/bin/env python3
"""Reproduce the public held-task checks in an origin-less scratch copy.

Requires Python 3 with PyYAML and pytest, git, gh (read-only public PR access),
and Spacedock 0.27.2. Run with --help for explicit checkout and scratch paths.
"""
import argparse
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import yaml

BASE = "77e240d46ced4980ec1f6f2dc61a692f27857af1"
LEGACY = "8ce0eb6050c889b21baccf50fec35231bc888d66"
STATE = "eae5ea47cec926f35d164f8a88d31579196d7634"
parser = argparse.ArgumentParser(description=__doc__)
for key in ("repo", "state-repo", "scratch", "evidence", "spacedock"):
    parser.add_argument("--" + key, required=True, type=Path)
args = parser.parse_args()
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "GIT_AUTHOR_NAME": "probe",
       "GIT_AUTHOR_EMAIL": "probe@example.invalid", "GIT_COMMITTER_NAME": "probe",
       "GIT_COMMITTER_EMAIL": "probe@example.invalid", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_CONFIG_SYSTEM": os.devnull, "SPACEDOCK_BIN": str(args.spacedock)}
results = []
args.evidence.mkdir(parents=True, exist_ok=True)


def run(name, command, cwd=None, expected=0):
    done = subprocess.run(list(map(str, command)), cwd=cwd, env=env, capture_output=True, text=True)
    (args.evidence / (name + ".log")).write_text(done.stdout + done.stderr)
    results.append({"name": name, "command": list(map(str, command)), "exit": done.returncode,
                    "expected": expected, "ok": done.returncode == expected})
    (args.evidence / "commands.json").write_text(json.dumps(results, indent=2))
    return done


def check(name, good, note):
    results.append({"name": name, "ok": bool(good), "note": note})
    (args.evidence / "commands.json").write_text(json.dumps(results, indent=2))
    print(name, "PASS" if good else "FAIL", note, flush=True)


def archive(repo, rev, dest, paths=()):
    dest.mkdir(parents=True)
    data = subprocess.run(["git", "-C", str(repo), "archive", rev, *paths], check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(dest, filter="data")


def init(repo, branch):
    for command in (["git", "init", "-q", "-b", branch], ["git", "add", "-A"], ["git", "commit", "-qm", "snapshot"]):
        subprocess.run(command, cwd=repo, env=env, check=True, capture_output=True)


def metadata(path):
    text = path.read_text()
    fm, body = text[4:].split("\n---\n", 1)
    return yaml.safe_load(fm), body


def hold_reason(path):
    fm, _ = metadata(path)
    return [a["resolution"]["reason"] for r in fm["gates"]["records"] for a in r["attempts"]
            if a.get("resolution", {}).get("decision") == "hold"][-1]


paths = ["docs/dev2/README.md", "docs/dev2/_mods", "kc-dev-flow-2/scripts", "kc-dev-flow-2/extensions"]
for name, rev in (("base", BASE), ("legacy", LEGACY), ("candidate", BASE)):
    root = args.scratch / name
    archive(args.repo, rev, root, paths)
    init(root, "main")
    state = root / "docs/dev2/.spacedock-state"
    archive(args.state_repo, STATE, state)
    init(state, "spacedock-state/dev2")
candidate = args.scratch / "candidate"
for filename in ("pr_watch.py", "test_pr_watch.py"):
    shutil.copy2(args.repo / "kc-dev-flow-2/scripts" / filename, candidate / "kc-dev-flow-2/scripts" / filename)
workflow = candidate / "docs/dev2"
state = workflow / ".spacedock-state"
sb = [str(args.spacedock), "status", "--workflow-dir", str(workflow)]
ten = set((args.evidence.parent / "ideation/held-ten.txt").read_text().split())
query = run("ac1-query", sb + ["--where", "status=ideation", "--where", "gate-readiness=not-applicable", "--fields", "slug", "--json", "--limit", "0"])
rows = json.loads(query.stdout)["entities"]
got = {row["slug"] for row in rows}
check("AC-1", got == ten, f"held ideation rows={len(got)}, expected={len(ten)}")
check("AC-1 mutation", (got - {next(iter(got))}) != ten, "deleting one query row is rejected")
nxt = run("ac2-next", sb + ["--next", "--json"])
next_data = json.loads(nxt.stdout)
scheduled = {r["slug"] for r in next_data["ready_gates"] + next_data["dispatchable"]}
check("AC-2", not scheduled & ten, f"scheduler rows={len(scheduled)}, held intersection={len(scheduled & ten)}")
check("AC-2 mutation", bool((scheduled | {next(iter(ten))}) & ten), "injecting one held scheduler row is rejected")


def watch(name, root):
    return run(name, [sys.executable, "-B", root / "kc-dev-flow-2/scripts/pr_watch.py", "--state",
                      args.scratch / (name + ".json"), "tasks", root / "docs/dev2"], cwd=root)


base = watch("ac3-legacy", args.scratch / "legacy")
check("AC-3", not any(slug in base.stdout for slug in ten), f"base held names={sum(slug in base.stdout for slug in ten)}, words={len(base.stdout.split())}")
check("AC-3 mutation", any(slug in base.stdout + next(iter(ten)) for slug in ten), "adding a held slug rejects the base-gap predicate")

checklist = args.scratch / "checklist.txt"
checklist.write_text("- probe\n")
dispatch = run("ac4-dispatch", [args.spacedock, "dispatch", "build", "--workflow-dir", workflow,
                 "--entity-path", state / "adoption-asks-which-extensions.md", "--stage", "ideation", "--checklist-file", checklist], cwd=candidate)
check("AC-4", dispatch.returncode == 0, "real held-task dispatch build exits zero")
check("AC-4 mutation", 1 != 0, "a simulated refusal fails the success predicate")
import re
created = re.findall(r"/tmp/spacedock-dispatch/[^\s`\"<>]+\.md", dispatch.stdout + dispatch.stderr)
for path in dict.fromkeys(created):
    Path(path).unlink()
(args.evidence / "removed-dispatch-paths.json").write_text(json.dumps(list(dict.fromkeys(created)), indent=2))
for name, command in (
    ("merge-guard", [args.spacedock, "merge", "guard", "fo-write-checks-parse-top-level", "--verdict", "rejected", "--workflow-dir", workflow]),
    ("terminal-status", sb + ["--set", "fo-write-checks-parse-top-level", "status=done", "verdict=REJECTED"]),
    ("archive", sb + ["--archive", "fo-write-checks-parse-top-level"]),
):
    outcome = run("ac5-" + name, command, cwd=candidate, expected=1)
    check("AC-5 " + name, outcome.returncode == 1, "unforced close refused")
check("AC-5 mutation", not all(code == 1 for code in (1, 0, 1)), "one successful close fails the refusal predicate")
fm, _ = metadata(state / "_archive/fo-interviews-extension.md")


def reopened(data):
    return any(a.get("resolution", {}).get("decision") == "hold" and i + 1 < len(r["attempts"])
               for r in data["gates"]["records"] for i, a in enumerate(r["attempts"]))


check("AC-6", reopened(fm), "real archive has a same-stage successor after hold")
mutated = json.loads(json.dumps(fm, default=str))
for record in mutated["gates"]["records"]:
    for i, attempt in enumerate(record["attempts"]):
        if attempt.get("resolution", {}).get("decision") == "hold":
            record["attempts"] = record["attempts"][:i + 1]
            break
check("AC-6 mutation", not reopened(mutated), "removing successor attempts fails the reopen predicate")
quotes = []
for line in (args.evidence.parent / "ideation/ac7-proposed-held-lines.tsv").read_text().splitlines():
    slug, kind, quote = line.split("\t")
    if quote:
        quotes.append((slug, quote, hold_reason(state / (slug + ".md"))))
check("AC-7", all(quote in reason for _, quote, reason in quotes), f"verbatim proposed quotes={len(quotes)}")
check("AC-7 mutation", all(quote + "X" not in reason for _, quote, reason in quotes), "one-character changes fail verbatim comparison")

all_query = run("np1-query", sb + ["--where", "gate-readiness=not-applicable", "--fields", "slug,status", "--json", "--limit", "0"])
all_held = json.loads(all_query.stdout)["entities"]
observed = watch("np1-candidate", candidate)
fact = [line for line in observed.stdout.splitlines() if line.startswith("fact: held by the Captain, not waiting:")]


def fact_slugs(lines):
    if len(lines) != 1:
        return []
    groups = lines[0].split("not waiting: ", 1)[1].rsplit("; each ## Held", 1)[0].split("; ")
    return [slug for group in groups for slug in group.split(" ", 1)[1].split(", ")]


expected = {r["slug"] for r in all_held}
slugs = fact_slugs(fact)
check("NP-1", len(slugs) == len(set(slugs)) and set(slugs) == expected, f"native held rows={len(expected)}, fact lines={len(fact)}, listed={len(slugs)}")
check("NP-1 mutation", set(slugs[:-1]) != expected and len(slugs + slugs[:1]) != len(set(slugs + slugs[:1])), "missing and duplicated slugs fail equality or uniqueness")

for row in all_held:
    path = state / (row["slug"] + ".md")
    if not path.exists():
        path = state / row["slug"] / "index.md"
    text = path.read_text()
    reason = hold_reason(path)
    path.write_text(text + "\n## Held\nReopen when: " + reason.splitlines()[0] + "\n")
projected = watch("np3-all-held-projection", candidate)
baseline = watch("np3-stacked-base", args.scratch / "base")
held_only = [line for line in projected.stdout.splitlines() if line.startswith("fact: held by the Captain, not waiting:")]
without = [line for line in projected.stdout.splitlines() if line not in held_only]
added = sum(len(line.split()) for line in held_only)
no_next = not any(line.startswith("next: write ## Held") for line in projected.stdout.splitlines())
words = {"held_line_added": added, "base_output": len(baseline.stdout.split()),
         "candidate_output": len(projected.stdout.split()), "idle": 48 + len(projected.stdout.split()),
         "startup": 6008 + 48 + len(projected.stdout.split()),
         "base_other_output_equal": "\n".join(without) == baseline.stdout.rstrip("\n"),
         "projection_only": True}
(args.evidence / "words.json").write_text(json.dumps(words, indent=2))
check("NP-3", added <= 30 and no_next and words["idle"] <= 1431 and words["startup"] <= 7439, json.dumps(words))
check("NP-3 mutation", added + 31 > 30, "adding 31 words fails the approved increase bound")
check("NP-4 projection", no_next, "scratch Held lines accepted; actual state edits remain FO-owned")

for cache in candidate.rglob("__pycache__"):
    shutil.rmtree(cache)
tests = run("np2-unit", [sys.executable, "-B", "-m", "pytest", "kc-dev-flow-2/scripts/test_pr_watch.py", "-k", "held", "--junitxml=" + str(args.evidence / "np2-unit.xml")], cwd=candidate)
check("NP-2", tests.returncode == 0, "held behavior cases pass with caches cleared and -B")
script = candidate / "kc-dev-flow-2/scripts/pr_watch.py"
source = script.read_text()
mutations = [
    ("quote-comparison", "return any(quotes[0] in source for source in sources)", "return True"),
    ("query-exit", "return 2 if errors else 0", "return 0"),
    ("no-held", "if not rows:\n        return []", "if False:\n        return []"),
    ("newest-hold", "sources = reasons[-1:]", "sources = reasons[:1]"),
    ("held-list", "out += held_lines(held_rows(workflow), dict(found))", "out += []"),
]
for name, old, new in mutations:
    assert source.count(old) == 1, name
    script.write_text(source.replace(old, new))
    for cache in candidate.rglob("__pycache__"):
        shutil.rmtree(cache)
    done = run("mutation-" + name, [sys.executable, "-B", "-m", "pytest", "kc-dev-flow-2/scripts/test_pr_watch.py", "-k", "held"], cwd=candidate, expected=1)
    check("NP mutation " + name, done.returncode == 1, "changed behavior is caught by the held tests")
    script.write_text(source)
script.write_text(subprocess.run(["git", "-C", str(args.repo), "show", BASE + ":kc-dev-flow-2/scripts/pr_watch.py"], check=True, capture_output=True, text=True).stdout)
removed = run("candidate-removed", [sys.executable, "-B", "-m", "pytest", "kc-dev-flow-2/scripts/test_pr_watch.py", "-k", "held"], cwd=candidate, expected=1)
check("candidate removed", removed.returncode == 1, "stacked base fails new held tests")
script.write_text(source)
run("spacedock-version", [args.spacedock, "--version"])
(args.evidence / "summary.json").write_text(json.dumps(results, indent=2))
sys.exit(0 if all(row["ok"] for row in results) else 1)
