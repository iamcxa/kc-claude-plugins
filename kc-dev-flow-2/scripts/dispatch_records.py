#!/usr/bin/env python3
"""Check a task's dispatch records: each needs a Dispatched line with a full SHA, a Model line,
non-empty Checklist and Scope notes sections, a `Package root:` line with an absolute path inside Scope notes, a scope-notes
line naming `main` as the completion recipient, and a checklist that is not only pointer lines (a record name plus only
words from POINTER_WORDS, as in "Same checklist as implementation-2."); a pointer worded outside that set, such as
"Reuse the checklist of implementation-2.", passes.
When the workflow README lists an extension whose EXTENSION.md has an `Instruction FO adds to the scope notes`
bullet, the first record of its `Joins:` stage (`implementation-1.md`) also needs that bullet's script paths with
`<package>` replaced by the record's own `Package root:` value, or a line `<name> not run: <reason>`.

Usage: dispatch_records.py [--readme FILE] <task folder or task .md file>
       dispatch_records.py --names <record file>...
       dispatch_records.py --newest <state checkout> <task slug>
Exit 1 naming each record that lacks a part, or when the task has no dispatch records. The README is FILE, else the
nearest README.md above the task folder with an `entity-type:` line; with neither, the run prints
`extensions not checked: no workflow README above <folder>` and its exit code is unchanged. A missing FILE exits 2.
--names prints `<file>:<line>: bare package script name <NAME>` for each package script (a .py file
directly under <package>/scripts/ or <package>/extensions/<name>/) written with no directory part in the
Checklist or Scope notes section (the whole file when it has neither heading), and exits 1 when any is found.
--newest runs that scan on the file added by the latest commit that adds a file under <slug>/dispatch/, read as it
is on disk: exit 0 when it is clean or the task has no record, 1 when a name is found, 2 when git cannot read the state.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from number_guards import Misconfigured, frontmatter  # noqa: E402

PACKAGE = Path(__file__).resolve().parent.parent

PARTS = {
    "a 'Dispatched:' line with a full 40-character SHA": re.compile(r"^Dispatched:.*\b[0-9a-f]{40}\b", re.M),
    "a 'Model:' line": re.compile(r"^Model:[ \t]*\S", re.M),
    "a non-empty '## Checklist' section": re.compile(r"^## Checklist[ \t]*\n(?:[ \t]*\n)*(?!## )\S", re.M),
    "a non-empty '## Scope notes' section": re.compile(r"^## Scope notes[ \t]*\n(?:[ \t]*\n)*(?!## )\S", re.M),
    "a 'Package root:' line with an absolute path in its scope notes":
        re.compile(r"^## Scope notes\b(?:(?!^## )[\s\S])*?^Package root:[ \t]*/\S", re.M),
    "a scope-notes line naming main as the completion recipient":
        re.compile(r"^## Scope notes\b(?:(?!^## )[\s\S])*?\bcompletion(?: message)? to [`']?main(?![\w-])", re.M | re.I),
}

SCRIPT_TOKEN = re.compile(r"(?<![\w./~-])([\w-]+\.py)(?!\w)")
SCANNED = re.compile(r"^## (?:Checklist|Scope notes)[ \t]*$")


INSTRUCTION = re.compile(r"^- \*\*Instruction FO adds to the scope notes:\*\*(.*?)(?=^- \*\*|\Z)", re.M | re.S)
JOINS = re.compile(r"^- \*\*Joins:\*\*[ \t]*(\w+)", re.M)
PACKAGE_PATH = re.compile(r"<package>/(extensions/[\w-]+/[\w.-]+\.py)")
ROOT = re.compile(r"^Package root:[ \t]*(/\S+)", re.M)


POINTER_WORDS = {"same", "identical", "unchanged", "checklist", "items", "as", "in", "to", "of", "from", "the", "see", "and", "for"}


def is_pointer(line, others):
    stems = "|".join(re.escape(name) for name in others)
    rest, hits = re.subn(rf"(?<![\w-])(?:[\w./~-]*/)?(?:{stems})(?:\.md)?(?![\w-])", " ", line) if others else (line, 0)
    return bool(hits) and all(word in POINTER_WORDS for word in re.findall(r"[a-z]+", rest.lower()))


def only_points_at_records(text, others):
    match = re.search(r"^## Checklist[ \t]*\n((?:(?!^## )[\s\S])*)", text, re.M)
    lines = [line for line in match.group(1).splitlines() if line.strip()] if match else []
    return bool(lines) and all(is_pointer(line, others) for line in lines)


def declared_instructions(package, listed):
    found = []
    for name in listed:
        file = Path(package, "extensions", name, "EXTENSION.md")
        text = file.read_text() if file.is_file() else ""
        bullet, stage = INSTRUCTION.search(text), JOINS.search(text)
        paths = PACKAGE_PATH.findall(bullet.group(1)) if bullet else []
        if stage and paths:
            found.append((name, stage.group(1), paths))
    return found


def find_readme(folder):
    for parent in Path(folder).resolve().parents:
        candidate = parent / "README.md"
        if candidate.is_file() and "entity-type" in frontmatter(candidate):
            return candidate
    return None


def instruction_error(record, name, paths):
    text, root = record.read_text(), ROOT.search(record.read_text())
    if not root or re.search(rf"^.*\b{re.escape(name)} not run:[ \t]*\S", text, re.M):
        return None
    base = root.group(1).rstrip("/")
    missing = [p for p in paths if not re.search(rf"(?<![\w.~-]){re.escape(base + '/' + p)}(?=[.,`)\x22\x27]{{0,3}}(?:\s|$))", text)]
    if not missing:
        return None
    if any(f"<package>/{p}" in text for p in missing):
        return f"{record.name}: {name} worker instruction has an unsubstituted <package>; write {base}/{missing[0]}"
    return (f"{record.name}: {name} worker instruction is absent; copy the 'Instruction FO adds to the scope notes' "
            f"bullet of {base}/extensions/{name}/EXTENSION.md into the scope notes, or add a line '{name} not run: <reason>'")


def extension_errors(folder, readme, package):
    listed = re.findall(r"[\w-]+", frontmatter(readme).get("extensions", ""))
    errors = []
    for name, stage, paths in declared_instructions(package, listed):
        for record in [Path(folder, "dispatch", f"{stage}-1.md")]:
            error = instruction_error(record, name, paths) if record.is_file() else None
            if error:
                errors.append(error)
    return errors


def package_scripts(package):
    return {p.name for pattern in ("scripts/*.py", "extensions/*/*.py") for p in package.glob(pattern)}


def bare_names(text, names):
    lines = text.splitlines()
    if not any(SCANNED.match(line) for line in lines):
        scanned = range(len(lines))
    else:
        scanned, inside = [], False
        for number, line in enumerate(lines):
            if line.startswith("## "):
                inside = bool(SCANNED.match(line))
            elif inside:
                scanned.append(number)
    return [(number + 1, name) for number in scanned
            for name in dict.fromkeys(SCRIPT_TOKEN.findall(lines[number])) if name in names]


def check_names(files, package):
    names = package_scripts(package)
    found = False
    for file in files:
        for number, name in bare_names(Path(file).read_text(), names):
            print(f"{file}:{number}: bare package script name {name}")
            found = True
    return 1 if found else 0


def check_newest(state, slug, package):
    done = subprocess.run(["git", "-C", str(state), "log", "--diff-filter=A", "--no-renames", "--relative",
                           "--name-only", "--format=", "-n", "1", "--", f"{slug}/dispatch/"],
                          capture_output=True, text=True)
    if done.returncode:
        print(f"git cannot read the dispatch records: {' '.join(done.stderr.split())}")
        return 2
    added = sorted(line for line in done.stdout.splitlines() if line.endswith(".md"))
    record = Path(state, added[-1]) if added else None
    return check_names([record], package) if record and record.is_file() else 0


def main(argv=None, package=PACKAGE):
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["--names"] and len(args) > 1:
        return check_names(args[1:], package)
    if args[:1] == ["--newest"] and len(args) == 3:
        return check_newest(args[1], args[2], package)
    readme = None
    if "--readme" in args:
        at = args.index("--readme")
        given, args = args[at + 1:at + 2], args[:at] + args[at + 2:]
        if not given:
            print(__doc__.strip())
            return 2
        readme = Path(given[0])
        if not readme.is_file():
            print(f"--readme {readme}: no such file")
            return 2
    if len(args) != 1 or args[0] in ("--names", "--newest"):
        print(__doc__.strip())
        return 2
    task = Path(args[0])
    folder = task.with_suffix("") if task.suffix == ".md" else task
    records = sorted((folder / "dispatch").glob("*.md"))
    if not records:
        print(f"{folder}: no dispatch records under dispatch/")
        return 1
    errors = [f"{path.name}: needs {part}" for path in records
              for part, pattern in PARTS.items() if not pattern.search(path.read_text())]
    readme = readme or find_readme(folder)
    if readme:
        errors += extension_errors(folder, readme, package)
    names = [path.stem for path in records]
    for path in records:
        if only_points_at_records(path.read_text(), [name for name in names if name != path.stem]):
            errors.append(f"{path.name}: needs a checklist of its own, not only a reference to another dispatch record")
    for error in errors:
        print(error)
    if not readme:
        print(f"extensions not checked: no workflow README above {folder}")
    if not errors:
        print(f"{len(records)} dispatch record(s) complete")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
