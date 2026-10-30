#!/usr/bin/env python3
"""Resolve a committed repository stage-worker choice without changing it."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

ROSTER = ".dev2/model-roster.json"
STAGES = ("ideation", "implementation", "validation")
MODELS = ("gpt-6.1-sol", "gpt-6-astra")
EFFORTS = ("low", "medium", "high", "xhigh", "max", "ultra")
FIELDS = {"provider", "model", "effort", "host"}


class Invalid(ValueError):
    pass


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args],
                            env=env, capture_output=True)
    if result.returncode:
        raise Invalid(f"git {args[0]}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def keys(value, expected, field):
    if not isinstance(value, dict) or set(value) != expected:
        raise Invalid(f"{field}: expected keys {', '.join(sorted(expected))}")


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Invalid(f"duplicate key: {key}")
        result[key] = value
    return result


def validate(data):
    keys(data, {"schema_version", "selected_from", "decision", "stages"}, "roster")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise Invalid("schema_version: expected 1")
    for name in ("selected_from", "decision"):
        if not isinstance(data[name], str) or not data[name].strip():
            raise Invalid(f"{name}: expected nonempty provenance string")
    keys(data["stages"], set(STAGES), "stages")
    for stage, row in data["stages"].items():
        keys(row, FIELDS, f"stages.{stage}")
        for field, allowed in (("provider", ("codex",)), ("model", MODELS),
                               ("effort", EFFORTS), ("host", ("paseo",))):
            if row[field] not in allowed:
                raise Invalid(f"stages.{stage}.{field}: expected {', '.join(allowed)}")
    return data


def author(path):
    result = {"record": str(path), "tuple": None}
    try:
        text = path.read_text(encoding="utf-8").split("\n## ", 1)[0]
        lines = re.findall(r"^Roster: (.+)$", text, re.M)
        if len(lines) == 1:
            parts = lines[0].split("; ")
            pairs = [part.split("=", 1) for part in parts]
            if any(len(pair) != 2 for pair in pairs):
                return result
            fields = unique(pairs)
            if fields.get("source") != "repository" or fields.get("role") not in ("implementation", "repair"):
                return result
            row = {key: fields.get(key) for key in FIELDS}
            if (row["provider"] == "codex" and row["host"] == "paseo"
                    and row["model"] in MODELS and row["effort"] in EFFORTS):
                result["tuple"] = row
        elif not lines:
            models = re.findall(r"^Model: (gpt-6\.1-sol|gpt-6-astra) \(Codex via Paseo, thinking (low|medium|high|xhigh|max|ultra)(?:[;,)])", text, re.M)
            if len(models) == 1:
                result["tuple"] = dict(provider="codex", model=models[0][0], effort=models[0][1], host="paseo")
    except (OSError, UnicodeError, Invalid):
        pass
    return result


def resolve(root, stage, records):
    if stage not in (*STAGES, "repair"):
        raise Invalid(f"stage: unsupported {stage!r}")
    if not root.is_absolute():
        raise Invalid("code-root: expected absolute Git worktree root")
    root = root.resolve()
    if Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() != root:
        raise Invalid("code-root: expected exact Git worktree root")
    commit = git(root, "rev-parse", "HEAD").decode().strip()
    path = root / ROSTER
    if path.parent.is_symlink() or path.is_symlink():
        raise Invalid(f"{ROSTER}: symlink is unsupported")
    if path.exists():
        mode = path.stat().st_mode
        if not stat.S_ISREG(mode) or not mode & 0o444:
            raise Invalid(f"{ROSTER}: unreadable regular file")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all", "--", ROSTER):
        raise Invalid(f"{ROSTER}: uncommitted choice; return to repository review")
    entry = git(root, "ls-tree", commit, "--", ROSTER)
    if not entry:
        if path.exists():
            raise Invalid(f"{ROSTER}: present but not committed")
        # see docs/adr/0047-repository-stage-model-rosters-keep-readme-defaults-when-absent.md
        return {"source": "readme-default", "role": stage, "tuple": None,
                "path": ROSTER, "commit": commit, "digest": None}
    if not entry.startswith(b"100644 blob ") and not entry.startswith(b"100755 blob "):
        raise Invalid(f"{ROSTER}: expected regular committed file")
    raw = path.read_bytes()
    if raw != git(root, "show", f"{commit}:{ROSTER}"):
        raise Invalid(f"{ROSTER}: bytes differ from committed choice")
    data = validate(json.loads(raw.decode("utf-8"), object_pairs_hook=unique))
    role = "implementation" if stage == "repair" else stage
    result = {"source": "repository", "role": role, "tuple": data["stages"][role],
              "path": ROSTER, "commit": commit, "digest": "sha256:" + hashlib.sha256(raw).hexdigest()}
    if stage == "validation":
        authors = [author(path) for path in records]
        result["authors"] = authors
        result["family"] = ("same-family: openai" if authors and all(a["tuple"] for a in authors)
                            else "unverified")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("resolve")
    command.add_argument("--code-root", type=Path, required=True)
    command.add_argument("--stage", required=True)
    command.add_argument("--author-record", type=Path, action="append", default=[])
    args = parser.parse_args()
    try:
        result = resolve(args.code_root, args.stage, args.author_record)
    except (Invalid, OSError, UnicodeError, ValueError) as error:
        print(f"model-roster: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
