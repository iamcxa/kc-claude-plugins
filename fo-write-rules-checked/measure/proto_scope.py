#!/usr/bin/env python3
"""Prototype of the R3 check, run over every task file of a state checkout. Writes nothing.

Usage: python3 -I -B proto_scope.py <package scripts dir> <state checkout> [task.md ...]
For each task with a closed backlog approval: read the backlog briefing's artifact uri (git-root://state/<sha>/<path>), take the
task file at that sha with `git show`, and report each `## Scope` line added or removed since, except lines that open with
"Non-goals", "Budget", "Stop condition" or "Follow-up:" (the README task template and Review-finding disposition), unless an `### Amendment N - <date>` dated on or after the approval exists. Prints held / not judged / clean counts.
"""
import json, re, subprocess, sys
from pathlib import Path
pkg, state = sys.argv[1], Path(sys.argv[2])
sys.path.insert(0, pkg)
import decision_ledger as dl

NONGOAL = re.compile(r"\s*(?:[-*]\s*)?(?:Non-goals?\b|Budget\b|Stop condition\b|Follow-up:)", re.I)
AMD = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2})", re.M)


def scope(text):
    m = re.search(r"^## Scope\b[^\n]*\n(.*?)(?=^## |\Z)", text or "", re.M | re.S)
    return (m.group(1) if m else "").splitlines()


def judge(task):
    text = task.read_text()
    fm, body = dl.split_task(text)
    if fm is None:
        return "not judged", "no frontmatter"
    closed = [e for e in dl.gate_entries(fm) if e["stage"] == "backlog" and e["kind"] == "resolution" and e.get("decision") == "approve"]
    if not closed:
        return "not judged", "no closed backlog approval"
    gate = closed[-1]
    index = task.parent / gate["room"] / "index.json"
    try:
        uri = json.loads(index.read_text())["artifacts"][0]["uri"]
    except (OSError, ValueError, KeyError, IndexError):
        return "not judged", "briefing unreadable"
    m = re.fullmatch(r"git-root://state/([0-9a-f]{40})/(.+)", uri)
    if not m:
        return "not judged", "artifact uri has no sha"
    done = subprocess.run(["git", "-C", str(task.parent), "show", f"{m[1]}:{m[2]}"], capture_output=True)
    if done.returncode:
        return "not judged", "baseline not readable by git"
    old, new = scope(done.stdout.decode("utf-8", "replace")), scope(text)
    add = [l for l in new if l not in old and l.strip() and not NONGOAL.match(l)]
    rem = [l for l in old if l not in new and l.strip() and not NONGOAL.match(l)]
    if not add and not rem:
        return "clean", ""
    day = (gate.get("at") or "")[:10]
    if any(d >= day for _, d in AMD.findall(body)):
        return "amended", f"+{len(add)} -{len(rem)}"
    return "HOLD", f"+{len(add)} -{len(rem)}: {(add or rem)[0][:90]}"


tasks = [Path(a) for a in sys.argv[3:]] or sorted(p for p in list(state.glob("*.md")) + list((state / "_archive").glob("*.md")) if p.name != "README.md")
tally = {}
for t in tasks:
    verdict, why = judge(t)
    tally.setdefault(verdict, []).append(t.stem)
    if verdict in ("HOLD", "amended"):
        print(f"{verdict:8s} {t.stem[:46]:46s} {why}")
print({k: len(v) for k, v in tally.items()})
print("not judged:", {w for w in ()} or sorted({j for j in [judge(t)[1] for t in tasks if judge(t)[0] == 'not judged']}))
