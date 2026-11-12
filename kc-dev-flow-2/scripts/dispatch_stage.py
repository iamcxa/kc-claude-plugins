#!/usr/bin/env python3
"""Save and check a stage or special-role record before returning its dispatch prompt."""

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

from design_surfaces import task_folder
from number_guards import Misconfigured, frontmatter
from role_triggers import budget_text, rank
from scratch import notes_for, root_for

SCRIPTS = Path(__file__).resolve().parent


def git(root, *args):
    return subprocess.run(["git", "--literal-pathspecs", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def resolve_scope(args):
    value = frontmatter(args.workflow_dir / "README.md").get("state", "")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"{str(args.workflow_dir / 'README.md')!r}: unsupported state path")
    container = args.workflow_dir if value in ("", "$inline") else args.workflow_dir / relative
    if container.resolve(strict=True) != container:
        raise ValueError(f"{str(container)!r}: symlinked state directory")
    state = Path(git(container, "rev-parse", "--show-toplevel")).resolve(strict=True)
    if not container.is_relative_to(state) or (value not in ("", "$inline") and state != container):
        raise ValueError(f"{str(container)!r}: unsupported state repository layout")
    entity = args.entity_path
    folder = task_folder(entity)
    if (args.entity_input != entity or entity.suffix != ".md"
            or (entity.parent.parent if entity.name == "index.md" else entity.parent) != container):
        raise ValueError(f"{str(args.entity_input)!r}: unsupported or symlinked task layout")
    for directory in (folder, folder / "dispatch"):
        if os.path.lexists(directory) and (directory.is_symlink() or not directory.is_dir()):
            raise ValueError(f"{str(directory)!r}: unsupported task directory type")
    scope = [folder] if entity.name == "index.md" else [entity, folder]
    return state, folder, [path.relative_to(state).as_posix() for path in scope]


def check_task_scope(state, scope):
    def read(*flags):
        try:
            return subprocess.run(["git", "--literal-pathspecs", "-C", str(state), *flags],
                                  check=True, capture_output=True,
                                  env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}).stdout
        except subprocess.CalledProcessError as error:
            raise ValueError(f"{str(state / scope[0])!r}: cannot inspect task scope ({flags[0]})") from error

    def refuse(name, condition):
        raise ValueError(f"{str(state / os.fsdecode(name))!r}: {condition}")

    head = {}
    for entry in read("ls-tree", "-r", "-z", "HEAD", "--", *scope).split(b"\0"):
        if entry:
            metadata, name = entry.split(b"\t", 1)
            mode, kind, oid = metadata.split()
            if kind != b"blob" or mode not in (b"100644", b"100755"):
                refuse(name, "unsupported HEAD type")
            head[name] = (mode, oid)
    index = {}
    for entry in read("ls-files", "--stage", "-z", "--", *scope).split(b"\0"):
        if entry:
            metadata, name = entry.split(b"\t", 1)
            mode, oid, stage = metadata.split()
            if stage != b"0":
                refuse(name, "unresolved index conflict")
            index[name] = (mode, oid)
    for entry in read("ls-files", "-v", "-z", "--", *scope).split(b"\0"):
        if entry and (entry[:1].islower() or entry[:1] == b"S"):
            refuse(entry[2:], "unsupported assume-unchanged or skip-worktree index flag")
    for name in sorted(head.keys() | index.keys()):
        if head.get(name) != index.get(name):
            refuse(name, "staged content, existence or mode differs from HEAD")
    algorithm = read("rev-parse", "--show-object-format").strip().decode("ascii")
    for name, (mode, oid) in index.items():
        path = state / os.fsdecode(name)
        try:
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or path.resolve(strict=True) != path:
                refuse(name, "unsupported worktree type or path escape")
            data = path.read_bytes()
        except OSError as error:
            refuse(name, f"unstaged missing or unreadable worktree file ({error.strerror})")
        actual_mode = b"100755" if info.st_mode & stat.S_IXUSR else b"100644"
        actual_oid = hashlib.new(algorithm, b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest().encode()
        if (actual_mode, actual_oid) != (mode, oid):
            refuse(name, "unstaged content or mode differs from index")
    for name in read("ls-files", "--others", "--exclude-standard", "-z", "--", *scope).split(b"\0"):
        if name:
            refuse(name, "untracked non-ignored task file")


def record_text(args, number, dispatched, checklist, notes):
    notes = notes_for(args.workflow_dir, task_folder(args.entity_path),
                      f"{args.stage}-{number}", notes, SCRIPTS.parent)
    annotation = "workflow checkout" + (f", {args.note}" if args.note else "")
    header = [f"# {args.stage}-{number}", f"Dispatched: {dispatched} ({annotation})", f"Model: {args.model}"]
    # see docs/adr/0077-a-task-budget-counts-cycles-and-past-it-the-question-returns-to-the-captain.md
    if not args.role:
        header.append(f"Budget: {budget_text(args.entity_path.read_text()) or 'not recorded'}")
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
    committed = git(state, "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", relative).split("\0")
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
    text = record_text(args, newest + 1, dispatched, checklist, notes)
    directory.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(text.encode("utf-8"))
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
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--stage")
    target.add_argument("--role", choices=("chief-engineer", "engineering-reviewer"))
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
    if args.role:
        if (args.advance or args.bare_mode or args.feedback_reflow or args.candidate
                or any(getattr(args, name) is not None for name in
                       ("host", "symptom", "feedback_context_file"))):
            parser.error("--role cannot use --advance, --bare-mode, --host, --candidate, --symptom, "
                         "--feedback-context-file or --feedback-reflow")
        args.stage = args.role
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", args.stage):
        parser.error("--stage must be a stage name")
    if any(not re.fullmatch(r"[0-9a-fA-F]{40}", sha) for sha in args.candidate):
        parser.error("--candidate must be a full 40-hex SHA")
    try:
        args.entity_input = Path(os.path.abspath(args.entity_path))
        for name in ("workflow_dir", "entity_path", "checklist_file", "scope_notes_file", "feedback_context_file"):
            value = getattr(args, name)
            if value is not None:
                setattr(args, name, value.resolve(strict=True))
        checklist = args.checklist_file.read_bytes().decode("utf-8")
        notes = args.scope_notes_file.read_bytes().decode("utf-8")
        dispatched = git(args.workflow_dir, "rev-parse", "HEAD")
    except (OSError, UnicodeError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    return args, dispatched, checklist, notes


def main(argv=None):
    args, dispatched, checklist, notes = parse_args(argv)
    try:
        state, folder, scope = resolve_scope(args)
        check_task_scope(state, scope)
        path, wrote = select_record(args, folder, dispatched, checklist, notes)
    except (OSError, ValueError, Misconfigured, subprocess.CalledProcessError) as error:
        print(f"dispatch_stage: dispatch not built; {error}. "
              "Have the owner preserve and reconcile staged/worktree versions, then intentionally commit them; "
              "do not blindly state commit divergent data.", file=sys.stderr)
        return 1
    if args.role and rank(args.model) < rank("opus"):
        remove_uncommitted(path, wrote)
        print("dispatch_stage: dispatch not built; --role needs the opus model floor or above (astra qualifies)",
              file=sys.stderr)
        return 1
    if args.stage in ("implementation", "validation"):
        roles = subprocess.run([sys.executable, "-B", str(SCRIPTS / "role_triggers.py"),
                                str(folder.parent), folder.name, "--pending", str(path)], capture_output=True, text=True)
        if roles.returncode:
            remove_uncommitted(path, wrote)
            print(f"dispatch_stage: dispatch not built; {folder.name} budget or special-role check held:", file=sys.stderr)
            sys.stderr.write(roles.stdout + roles.stderr)
            return 1
        sys.stderr.write("".join(line for line in roles.stdout.splitlines(keepends=True) if line.startswith("budget:")))
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
    for line in dict.fromkeys(line for check in checks for line in check.stderr.splitlines(keepends=True)):
        sys.stderr.write(line)
    # see docs/adr/0070-stage-worker-dispatches-are-built-by-a-package-script-that-writes-their-record.md
    # see docs/adr/0074-special-role-calls-are-built-by-the-stage-dispatch-script.md
    if args.role:
        slug = args.entity_path.parent.name if args.entity_path.name == "index.md" else args.entity_path.stem
        try:
            commit = subprocess.run([args.spacedock, "state", "commit", slug, "--workflow-dir", str(args.workflow_dir)],
                                    capture_output=True, text=True)
        except OSError as error:
            print(f"dispatch_stage: {error}", file=sys.stderr)
            return 1
        sys.stderr.write(commit.stderr)
        if commit.returncode:
            sys.stderr.write(commit.stdout)
            return 1
        sys.stdout.buffer.write(path.read_bytes())
        return 0
    command = [args.spacedock, "dispatch", "build", "--advance" if args.advance else "--stamp"]
    scratch = root_for(args.workflow_dir, folder.name, path.stem)
    scratch.mkdir(parents=True, exist_ok=True)
    scoped = scratch / "scope-notes.md"
    scoped.write_bytes(notes_for(args.workflow_dir, folder, path.stem, notes, SCRIPTS.parent).encode("utf-8"))
    for name in ("workflow_dir", "entity_path", "stage", "checklist_file", "scope_notes_file", "host", "feedback_context_file"):
        value = scoped if name == "scope_notes_file" else getattr(args, name)
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
