#!/usr/bin/env python3
"""Refuse candidates that change an applied migration or take a number another task holds, and reserve numbers per task.

check   exit 0 clean, 1 findings, 2 misconfiguration. Rules: R1 a migration present at the merge-base is
        modified or deleted; R2 the same against every 'Applied at: <env> <sha>' commit; R3 an added migration
        number is not above the base tip's highest; R4 an added migration or ADR number is not in the task's
        'Migration:' / 'ADR:' lines; R5 an added ADR number exists on the base tip; R6 a task whose frontmatter says
        'profile: poc' differs from the merge-base anywhere under the migrations directory.
reserve prints 'Migration: NNNN' or 'ADR: NNNN' (one above the base tip and every other task file, never
        filling a gap); a task that already holds a line gets it back. One number per kind per task.
Limits: only files named NNNN_name.sql count as migrations, so meta/_journal.json and snapshots are not checked (R6 does check them);
a deploy nobody recorded as 'Applied at:' is not detected; run 'git -C <repo> fetch' first, the base tip is what is local.
Task lines are read from the task's '## Number guards' section.
"""
import argparse
import posixpath
import re
import subprocess
import sys
from pathlib import Path

MIGRATION = re.compile(r"^(\d+)_.+\.sql$")
ADR = re.compile(r"^(\d{4})-.+\.md$")
KINDS = {"migration": ("Migration", MIGRATION), "adr": ("ADR", ADR)}


class Misconfigured(Exception):
    pass


def git(repo, *args):
    done = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if done.returncode:
        raise Misconfigured(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def resolve(repo, ref, what="ref"):
    done = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                          capture_output=True, text=True)
    if done.returncode:
        raise Misconfigured(f"cannot resolve {what} '{ref}' in {repo}")
    return done.stdout.strip()


def frontmatter(readme):
    if not readme.is_file():
        raise Misconfigured(f"no workflow README at {readme}")
    lines = readme.read_text().split("\n")
    found = {}
    for line in lines[1:] if lines[0] == "---" else []:
        if line == "---":
            break
        match = re.match(r"^([\w-]+):[ \t]*(.*?)[ \t]*$", line)
        if match:
            found[match.group(1)] = match.group(2).strip("'\"")
    return found


def task_facts(path):
    task = Path(path)
    if not task.is_file():
        raise Misconfigured(f"task file {task} does not exist")
    text = task.read_text(errors="replace")
    section = re.search(r"^## Number guards[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    body = section.group(1) if section else ""
    surfaces = re.search(r"^Surfaces:(.*)$", text, re.M)
    return {
        "migration": {int(n) for n in re.findall(r"^Migration:[ \t]*(\d+)[ \t]*$", body, re.M)},
        "adr": {int(n) for n in re.findall(r"^ADR:[ \t]*(\d+)[ \t]*$", body, re.M)},
        "applied": re.findall(r"^Applied at:[ \t]*(\S+)[ \t]+([0-9a-f]{7,40})[ \t]*$", body, re.M),
        "poc": frontmatter(task).get("profile") == "poc",
        "surfaces": set(re.split(r"[\s,]+", surfaces.group(1).strip())) if surfaces else set(),
    }


def numbered(repo, ref, directory, pattern):
    found = {}
    for path in git(repo, "ls-tree", "--name-only", ref, directory.rstrip("/") + "/").splitlines():
        match = pattern.match(posixpath.basename(path))
        if match:
            found.setdefault(int(match.group(1)), []).append(posixpath.basename(path))
    return found


def added_changed(repo, old, new, directory, pattern):
    """Return (added files, files present at old and modified or deleted at new) among numbered files in directory."""
    added, touched = [], []
    out = git(repo, "diff", "--name-status", "--no-renames", old, new, "--", directory.rstrip("/") + "/")
    for line in out.splitlines():
        status, path = line.split("\t", 1)
        if posixpath.dirname(path) != directory.rstrip("/") or not pattern.match(posixpath.basename(path)):
            continue
        (added if status == "A" else touched).append((status, path))
    return added, touched


def settings(args):
    cfg = frontmatter(Path(args.workflow_dir) / "README.md") if args.workflow_dir else {}
    base = args.base
    if not base and cfg.get("trunk"):
        remote = f"origin/{cfg['trunk']}"
        base = remote if subprocess.run(["git", "-C", args.repo, "rev-parse", "--verify", "--quiet", remote],
                                        capture_output=True).returncode == 0 else cfg["trunk"]
    if not base:
        raise Misconfigured("no base: pass --base, or --workflow-dir whose README declares trunk:")
    return {
        "migrations": args.migrations_path or cfg.get("migrations-path"),
        "adr": args.adr_path or cfg.get("adr-path") or "docs/adr",
        "base": base,
        "state": getattr(args, "state_dir", None) or (cfg.get("state") and str(Path(args.workflow_dir) / cfg["state"])),
    }


def require_migrations(repo, base, directory):
    files = numbered(repo, base, directory, MIGRATION)
    if not files:
        raise Misconfigured(f"no migration file matching NNNN_name.sql under '{directory}' at {base} "
                            "(the path is absent there or holds none)")
    return files


def check(args):
    repo, cfg = args.repo, settings(args)
    facts = task_facts(args.task) if args.task else None
    directory = cfg["migrations"]
    if not directory and facts and "db" in facts["surfaces"]:
        raise Misconfigured("task has Surfaces: db but no migrations-path is declared "
                            "(pass --migrations-path or set migrations-path: in the workflow README)")
    base, head = resolve(repo, cfg["base"], "base"), resolve(repo, args.head, "head")
    merge_base = git(repo, "merge-base", base, head).strip()
    applied = [("cli", ref) for ref in args.applied_ref] + (facts["applied"] if facts else [])
    applied = [(env, ref, resolve(repo, ref, f"applied commit ({env})")) for env, ref in applied]
    out = []

    def fail(rule, path, reason):
        out.append(f"FAIL {rule}: {path}: {reason}")

    if directory:
        base_numbers = require_migrations(repo, base, directory)
        added, touched = added_changed(repo, merge_base, head, directory, MIGRATION)
        for status, path in touched:
            fail("R1", path, f"{status} since the merge-base; a migration on the base branch must not change, "
                 "revert it and add a new migration")
        for env, ref, sha in applied:
            for status, path in added_changed(repo, sha, head, directory, MIGRATION)[1]:
                fail("R2", path, f"{status} since {sha[:12]}, applied at {env}; revert it and add a new migration")
        top = max(base_numbers)
        for _, path in added:
            number = int(MIGRATION.match(posixpath.basename(path)).group(1))
            if number in base_numbers:
                fail("R3", path, f"base already has {number:04d} ({base_numbers[number][0]})")
            elif number < top:
                fail("R3", path, f"number {number:04d} is not above the base maximum {top:04d}")
            if facts is not None and number not in facts["migration"]:
                fail("R4", path, f"number {number:04d} is not in the task's Migration: lines")
        if facts and facts["poc"]:
            for line in git(repo, "diff", "--name-status", "--no-renames", merge_base, head,
                            "--", directory.rstrip("/") + "/").splitlines():
                status, path = line.split("\t", 1)
                fail("R6", path, f"{status} under the migrations directory; a POC task changes none of it")
    else:
        out.append("migration guard skipped: no migrations-path declared")
    adr_base = numbered(repo, base, cfg["adr"], ADR)
    for _, path in added_changed(repo, merge_base, head, cfg["adr"], ADR)[0]:
        number = int(ADR.match(posixpath.basename(path)).group(1))
        if number in adr_base:
            fail("R5", path, f"base already has {number:04d} ({adr_base[number][0]})")
        if facts is not None and number not in facts["adr"]:
            fail("R4", path, f"number {number:04d} is not in the task's ADR: lines")
    if facts is None:
        out.append("R4 skipped: no --task given")
    failed = any(line.startswith("FAIL") for line in out)
    print("\n".join(out + ([] if failed else ["PASS: no findings"])))
    print(f"base {base[:12]} head {head[:12]} merge-base {merge_base[:12]}")
    return 1 if failed else 0


def reserve(args):
    repo, cfg = args.repo, settings(args)
    label, pattern = KINDS[args.kind]
    facts = task_facts(args.task)
    if facts[args.kind]:
        for number in sorted(facts[args.kind]):
            print(f"{label}: {number:04d}")
        return 0
    if not cfg["state"]:
        raise Misconfigured("no state directory: pass --state-dir, or --workflow-dir whose README declares state:")
    if args.kind == "migration":
        if not cfg["migrations"]:
            raise Misconfigured("no migrations-path declared (pass --migrations-path or set it in the workflow README)")
        files = require_migrations(repo, resolve(repo, cfg["base"], "base"), cfg["migrations"])
        width = max(4, *(len(name.split("_")[0]) for names in files.values() for name in names))
    else:
        files = numbered(repo, resolve(repo, cfg["base"], "base"), cfg["adr"], pattern)
        width = 4
    taken = set(files)
    for sibling in sorted(Path(cfg["state"]).glob("*.md")):
        if sibling.resolve() != Path(args.task).resolve():
            taken |= task_facts(sibling)[args.kind]
    print(f"{label}: {max(taken, default=0) + 1:0{width}d}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("check", check), ("reserve", reserve)):
        cmd = sub.add_parser(name)
        cmd.set_defaults(handler=handler)
        cmd.add_argument("--repo", default=".")
        cmd.add_argument("--workflow-dir", help="workflow directory whose README supplies trunk, migrations-path, adr-path, state")
        cmd.add_argument("--base", help="base ref; default origin/<trunk>, else <trunk>")
        cmd.add_argument("--migrations-path")
        cmd.add_argument("--adr-path")
        cmd.add_argument("--task", help="task file holding the '## Number guards' section")
    sub.choices["check"].add_argument("--head", default="HEAD")
    sub.choices["check"].add_argument("--applied-ref", action="append", default=[])
    sub.choices["reserve"].add_argument("--kind", choices=KINDS, required=True)
    sub.choices["reserve"].add_argument("--state-dir")
    args = parser.parse_args(argv)
    if args.command == "reserve" and not args.task:
        parser.error("reserve needs --task")
    try:
        return args.handler(args)
    except Misconfigured as error:
        print(f"number_guards: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
