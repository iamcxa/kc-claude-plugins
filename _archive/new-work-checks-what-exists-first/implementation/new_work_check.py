#!/usr/bin/env python3
"""Disposable source/loading probe; never a model-behavior grader."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True)


def source(repo, ref, path):
    return git(repo, "show", f"{ref}:kc-dev-flow-2/{path}")


def routing(a):
    ideation = source(a.repo, a.ref, "skills/ideation/principles.md")
    implementation = source(a.repo, a.ref, "skills/implementation/principles.md")
    general = "## Before new work\n" in implementation
    linked = "../implementation/principles.md#before-new-work" in ideation
    rows = []
    for stage in ("ideation", "implementation"):
        skill = source(a.repo, a.ref, f"skills/{stage}/SKILL.md")
        for profile in ("poc", "pilot", "prod"):
            active = not (stage == "ideation" and profile == "poc")
            reaches = general and (linked if stage == "ideation" else True)
            rows.append(dict(stage=stage, profile=profile, active=active,
                             general_check_loaded=active and reaches,
                             stage_principles_declared="[stage principles](principles.md)" in skill))
    deep = implementation.split("## Existing-code capability check\n", 1)[1]
    base_deep = source(a.repo, a.base, "skills/implementation/principles.md").split(
        "## Existing-code capability check\n", 1)[1]
    passed = all(not r["active"] or (r["general_check_loaded"] and r["stage_principles_declared"]) for r in rows)
    passed = passed and deep == base_deep
    print(json.dumps(dict(rows=rows, existing_capability_check_unchanged=deep == base_deep,
                          result="pass" if passed else "missing general check",
                          limit="Source loading and applicability only; does not prove worker compliance."), indent=2))
    return 0 if passed else 1


def scope(a):
    changed = git(a.repo, "diff", "--name-only", a.base, a.ref, "--", "kc-dev-flow-2").splitlines()
    expected = ["kc-dev-flow-2/skills/ideation/principles.md", "kc-dev-flow-2/skills/implementation/principles.md"]
    print(json.dumps(dict(changed=changed, expected=expected, no_workflow_or_runtime_change=sorted(changed) == sorted(expected)), indent=2))
    return 0 if sorted(changed) == sorted(expected) else 1


def cost(a):
    paths = ["references/sd/workflow.md", "references/sd/mods/kc-dev-flow-2.md",
             "scripts/pr_watch.py", "scripts/delivery_gate.py", "scripts/observer_check.py"]
    equal = all(source(a.repo, a.base, p) == source(a.repo, a.ref, p) for p in paths)
    workflow = source(a.repo, a.base, paths[0])
    mod = source(a.repo, a.base, paths[1])
    sections = {}
    name = "preamble"
    for line in workflow.splitlines(keepends=True):
        if line.startswith("## "):
            name = line[3:].strip()
        sections[name] = sections.get(name, "") + line
    moments = {
        "startup/resume": ["full workflow", "full mod"],
        "idle/open PR": ["full mod", "Delivery authority", "Review-finding disposition"],
        "idle/merged PR": ["full mod", "Delivery authority"],
        "after archive": ["full mod", "Extensions"],
        "merge ask": ["Delivery authority", "Captain steps", "Review-finding disposition"],
        "stage dispatch": ["Stages", "Dispatch facts"],
    }
    texts = dict(sections, **{"full workflow": workflow, "full mod": mod})
    rows = []
    for moment, parts in moments.items():
        found = [p for p in parts if p in texts]
        words = sum(len(texts[p].split()) for p in found)
        rows.append(dict(moment=moment, passages=found, base_words=words,
                         probe_words=words, delta=0))
    workers = []
    for stage in ("ideation", "implementation"):
        path = f"skills/{stage}/principles.md"
        before = len(source(a.repo, a.base, path).split())
        after = len(source(a.repo, a.ref, path).split())
        workers.append(dict(stage=stage, base_words=before, probe_words=after, delta=after-before))
    print(json.dumps(dict(fo_instruction_sources_byte_equal=equal, rows=rows,
                         worker_principles=workers, workflow_words=len(workflow.split()),
                         limit="Counts enumerate the named passages, not a universal total. Dynamic output volume is input-dependent; unchanged scripts with the same input add zero changed words. Ideation follows the new linked section in implementation principles."), indent=2))
    return 0 if equal else 1


def siblings(a):
    rows = []
    for i, root in enumerate(a.adopter, 1):
        root = Path(root)
        workflow = root / "docs/dev2/README.md"
        readme = workflow.read_text()
        ref = "refs/heads/spacedock-state/dev2"
        files = git(root, "ls-tree", "-r", "--name-only", ref).splitlines()
        task_files = [p for p in files if p.endswith(".md") and "/" not in p]
        archived = [p for p in files if p.startswith("_archive/") and p.endswith(".md") and p.count("/") == 1]
        texts = [git(root, "show", f"{ref}:{p}") for p in task_files + archived]
        rows.append(dict(adopter=i, readmes_read=1, state_files_read=len(texts),
                         current_files=len(task_files), archived_files=len(archived),
                         state_read_from_committed_branch=1,
                         readme_explicit_upstream_check=int(bool(re.search(r"upstream.first|before new work", readme, re.I))),
                         files_mentioning_upstream=sum(bool(re.search(r"upstream.first|check.{0,30}upstream|先查上游", t, re.I)) for t in texts),
                         files_mentioning_adr=sum(bool(re.search(r"\bADR\b", t)) for t in texts)))
    print(json.dumps(dict(rows=rows, limit="Read-only presence counts; not execution or adoption compliance. Private names, titles, rulings and logs are never emitted."), indent=2))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("routing", "scope", "cost", "siblings"))
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--ref", default="HEAD")
    p.add_argument("--base", default="8125e6d516d32abbf79c6772de10cde2c20900a8")
    p.add_argument("--adopter", action="append", default=[])
    a = p.parse_args()
    return globals()[a.mode](a)


if __name__ == "__main__":
    sys.exit(main())
