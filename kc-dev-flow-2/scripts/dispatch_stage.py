#!/usr/bin/env python3
"""Save and check a stage dispatch record before building its Spacedock envelope."""

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

from design_surfaces import task_folder

SCRIPTS = Path(__file__).resolve().parent


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def record_text(args, number, dispatched, checklist, notes):
    annotation = "workflow checkout" + (f", {args.note}" if args.note else "")
    header = [f"# {args.stage}-{number}", f"Dispatched: {dispatched} ({annotation})", f"Model: {args.model}"]
    if args.roster:
        header.append(f"Roster: {args.roster}")
    header += [f"Candidate: {sha}" for sha in args.candidate]
    if args.symptom:
        header.append(f"Symptom: {args.symptom}")
    return "\n".join(header) + "\n\n## Checklist\n" + checklist + "\n## Scope notes\n" + notes


def select_record(args, folder, dispatched, checklist, notes):
    state = Path(git(args.entity_path.parent, "rev-parse", "--show-toplevel"))
    directory = folder / "dispatch"
    relative = directory.relative_to(state).as_posix()
    pattern = re.compile(rf"{re.escape(args.stage)}-([1-9][0-9]*)\.md")
    committed = git(state, "ls-tree", "-r", "--name-only", "HEAD", "--", relative).splitlines()
    numbers = [int(match[1]) for path in committed
               if (match := pattern.fullmatch(Path(path).name)) and Path(path).parent.as_posix() == relative]
    newest = max(numbers, default=0)
    if newest:
        path = directory / f"{args.stage}-{newest}.md"
        rel = path.relative_to(state).as_posix()
        expected = record_text(args, newest, dispatched, checklist, notes)
        added = git(state, "log", "-1", "--diff-filter=A", "--format=%H", "--", rel)
        if (added == git(state, "rev-parse", "HEAD") and path.is_file()
                and path.read_bytes() == expected.encode("utf-8")):
            return path, False
    path = directory / f"{args.stage}-{newest + 1}.md"
    if git(state, "ls-files", "--", path.relative_to(state).as_posix()):
        raise FileExistsError(f"record already exists in index: {path}")
    directory.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(record_text(args, newest + 1, dispatched, checklist, notes).encode("utf-8"))
    return path, True


def remove_uncommitted(path, wrote):
    if wrote:
        state = Path(git(path.parent, "rev-parse", "--show-toplevel"))
        relative = path.relative_to(state).as_posix()
        committed = subprocess.run(["git", "-C", str(state), "cat-file", "-e", f"HEAD:{relative}"], capture_output=True)
        if committed.returncode:
            subprocess.run(["git", "-C", str(state), "update-index", "--force-remove", "--", relative], check=True)
            path.unlink(missing_ok=True)


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("workflow-dir", "entity-path", "checklist-file", "scope-notes-file"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--model", required=True)
    for name in ("roster", "symptom", "note"):
        parser.add_argument(f"--{name}")
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--spacedock", default=os.environ.get("SPACEDOCK_BIN") or "spacedock")
    parser.add_argument("--host", choices=("claude", "codex", "pi"))
    parser.add_argument("--feedback-context-file", type=Path)
    parser.add_argument("--feedback-reflow", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--advance", action="store_true")
    mode.add_argument("--bare-mode", action="store_true")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", args.stage):
        parser.error("--stage must be a stage name")
    if any(not re.fullmatch(r"[0-9a-fA-F]{40}", sha) for sha in args.candidate):
        parser.error("--candidate must be a full 40-hex SHA")
    try:
        for name in ("workflow_dir", "entity_path", "checklist_file", "scope_notes_file", "feedback_context_file"):
            value = getattr(args, name)
            if value is not None:
                setattr(args, name, value.resolve(strict=True))
        checklist = args.checklist_file.read_text()
        notes = args.scope_notes_file.read_text()
        dispatched = git(args.workflow_dir, "rev-parse", "HEAD")
    except (OSError, UnicodeError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    return args, dispatched, checklist, notes


def main(argv=None):
    args, dispatched, checklist, notes = parse_args(argv)
    try:
        path, wrote = select_record(args, task_folder(args.entity_path), dispatched, checklist, notes)
    except FileExistsError as error:
        print(f"dispatch_stage: dispatch not built; refusing existing record: {error}", file=sys.stderr)
        return 1
    checks = [subprocess.run([sys.executable, "-B", str(SCRIPTS / "dispatch_records.py"), *map(str, flags)],
                             capture_output=True, text=True)
              for flags in ((task_folder(args.entity_path),), ("--names", "--strict", path))]
    if any(check.returncode for check in checks):
        remove_uncommitted(path, wrote)
        print("dispatch_stage: dispatch not built; repair the dispatch record:", file=sys.stderr)
        for check in checks:
            if check.returncode:
                sys.stderr.write(check.stdout + check.stderr)
        return 1
    # see docs/adr/0070-stage-worker-dispatches-are-built-by-a-package-script-that-writes-their-record.md
    command = [args.spacedock, "dispatch", "build", "--advance" if args.advance else "--stamp"]
    for name in ("workflow_dir", "entity_path", "stage", "checklist_file", "scope_notes_file", "host", "feedback_context_file"):
        value = getattr(args, name)
        if value is not None:
            command += ["--" + name.replace("_", "-"), str(value)]
    command += ["--" + name.replace("_", "-") for name in ("feedback_reflow", "bare_mode") if getattr(args, name)]
    try:
        build = subprocess.run(command, capture_output=True, text=True)
    except OSError as error:
        remove_uncommitted(path, wrote)
        print(f"dispatch_stage: {error}", file=sys.stderr)
        return 1
    sys.stderr.write(build.stderr)
    if build.returncode:
        remove_uncommitted(path, wrote)
        return build.returncode
    if args.advance:
        slug = args.entity_path.parent.name if args.entity_path.name == "index.md" else args.entity_path.stem
        commit = subprocess.run([args.spacedock, "state", "commit", slug, "--workflow-dir", str(args.workflow_dir)],
                                capture_output=True, text=True)
        sys.stderr.write(commit.stderr)
        if commit.returncode:
            sys.stderr.write(commit.stdout)
            return 1
    sys.stdout.write(build.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
