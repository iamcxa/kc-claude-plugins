#!/usr/bin/env python3
"""Build the declared public, origin-less base replay and Held-only projection.

Arguments: product checkout, state checkout, scratch root, evidence directory.
Requires git, Python 3.11, PyYAML, and the unchanged candidate's Python scripts.
"""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import yaml

repo, source_state, scratch, evidence = map(Path, sys.argv[1:])
env = {**os.environ, "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
       "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid",
       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}


def archive(source, revision, target, paths=()):
    target.mkdir(parents=True)
    data = subprocess.check_output(["git", "-C", str(source), "archive", revision, *paths])
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(target, filter="data")


def init(path, branch):
    for args in (("init", "-q", "-b", branch), ("add", "-A"), ("commit", "-qm", "public snapshot")):
        subprocess.run(["git", "-C", str(path), *args], env=env, check=True, capture_output=True)


legacy = scratch / "legacy"
archive(repo, "8ce0eb6050c889b21baccf50fec35231bc888d66", legacy,
        ("docs/dev2/README.md", "docs/dev2/_mods", "kc-dev-flow-2/scripts", "kc-dev-flow-2/extensions"))
init(legacy, "main")
state = legacy / "docs/dev2/.spacedock-state"
archive(source_state, "eae5ea47cec926f35d164f8a88d31579196d7634", state)
init(state, "spacedock-state/dev2")
assert not subprocess.check_output(["git", "-C", str(state), "remote"], text=True).strip()
assert not subprocess.check_output(["git", "-C", str(legacy), "remote"], text=True).strip()

projection = scratch / "projection"
projection.mkdir()
query = json.loads((evidence / "held-query.json").read_text())
found, unchanged = {}, True
for row in query:
    slug = row["slug"]
    path = source_state / (slug + ".md")
    if not path.exists():
        path = source_state / slug / "index.md"
    text = path.read_text()
    front = text[4:].split("\n---\n", 1)[0]
    meta = yaml.safe_load(front)
    reasons = [a["resolution"]["reason"] for record in meta["gates"]["records"] for a in record["attempts"]
               if a.get("resolution", {}).get("decision") == "hold"]
    target = projection / (slug + ".md")
    target.write_text(text + "\n## Held\nReopen when: " + reasons[-1].splitlines()[0] + "\n")
    unchanged &= target.read_text()[4:].split("\n---\n", 1)[0] == front
    found[slug] = target

sys.path.insert(0, str(repo / "kc-dev-flow-2/scripts"))
import pr_watch
lines = pr_watch.held_lines(query, found)
assert unchanged and len(lines) == 1 and lines[0].startswith("fact: held by the Captain, not waiting:")
(evidence / "projection-held-lines.txt").write_text("\n".join(lines) + "\n")
(evidence / "projection.json").write_text(json.dumps({"held_tasks": len(query), "valid_held_sections": sum(pr_watch.held_quote(p) for p in found.values()),
    "frontmatter_unchanged": unchanged, "projection_only": True, "actual_state_not_modified": True}, indent=2))
print(json.dumps({"legacy": str(legacy), "state_revision": "eae5ea47cec926f35d164f8a88d31579196d7634",
                  "legacy_revision": "8ce0eb6050c889b21baccf50fec35231bc888d66", "projected_held_tasks": len(query)}, indent=2))
