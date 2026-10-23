#!/usr/bin/env python3
"""Check a docs/adr directory against the dev2 ADR format; exit 1 on any violation."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

NAME = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
SECTIONS = ["Status", "Context", "Decision", "Consequences"]
STATUS = re.compile(r"^(Proposed|Accepted|Deprecated|Superseded by (\d{4}))$")
LEGACY = re.compile(r"^Status: Legacy\b", re.M)
SKIP = {"README.md", "index.md", "template.md"}
PROTECTS = re.compile(r"^\*\*Protects:\*\*\s*(.*)$")
ENTRY = re.compile(r"^- `([^`]+)`")


def sections(text):
    found, current = {}, None
    for line in text.split("\n"):
        if line.startswith("## "):
            current = line[3:].strip()
            found.setdefault("_order", []).append(current)
            found[current] = []
        elif current:
            found[current].append(line)
    return found


def protected_paths(decision_lines, name):
    lines = [l.strip() for l in decision_lines]
    at = next((i for i, l in enumerate(lines) if PROTECTS.match(l)), None)
    if at is None:
        return [], []
    rest = PROTECTS.match(lines[at]).group(1).strip()
    entries = []
    for line in lines[at + 1:]:
        if not line.startswith("- "):
            break
        entries.append(line)
    if not entries:
        return [], [] if rest.lower().startswith("none") else [
            f"{name}: Protects must be 'none' or a list of '- `path` — where in the file' lines"]
    paths, errors = [], []
    for line in entries:
        match = ENTRY.match(line)
        path = match.group(1) if match else ""
        if not path or path.startswith("/") or ".." in Path(path).parts:
            errors.append(f"{name}: Protects entry must start with a backticked path from the repo root: {line!r}")
        else:
            paths.append(path)
    return paths, errors


def check_pointers(files, root, adr_dir):
    records, listed, superseded = [], {}, {}
    for number, path in sorted(files.items()):
        found = sections(path.read_text())
        status = STATUS.match(next((l.strip() for l in found.get("Status", []) if l.strip()), ""))
        if not status:
            continue
        if status.group(2):
            superseded[number] = int(status.group(2))
        for listed_path in protected_paths(found.get("Decision", []), path.name)[0]:
            listed.setdefault(listed_path, []).append(number)
            records.append((path, listed_path, status.group(0) == "Accepted"))
    if not listed:
        return []
    try:
        where = adr_dir.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return [f"{adr_dir} is not inside the repository root {root}; pass --root"]
    errors = []
    cites = re.compile(re.escape(where) + r"/(\d{4})(?!\d)")

    def cited_by(site):
        return {int(c) for c in cites.findall(site.read_text(errors="replace"))}

    for path, listed_path, accepted in records:
        if accepted:
            site = root / listed_path
            if not site.is_file():
                errors.append(f"{path.name}: protects {listed_path}, which does not exist")
            elif int(path.name[:4]) not in cited_by(site):
                errors.append(f"{path.name}: {listed_path} has no pointer; add a comment line 'see {where}/{path.name}'")
    for listed_path in sorted(listed):
        site = root / listed_path
        if site.is_file():
            for cited in sorted(cited_by(site) & set(superseded)):
                errors.append(f"{listed_path}: points at ADR {cited:04d}, Superseded by {superseded[cited]:04d}; "
                              f"point it at {superseded[cited]:04d} or the record in force")
    return errors


def repo_root(adr_dir, given):
    if given:
        return Path(given)
    top = subprocess.run(["git", "-C", str(adr_dir), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return Path(top.stdout.strip()) if top.returncode == 0 and top.stdout.strip() else Path(".")


def check_file(path, numbers):
    errors, text = [], path.read_text()
    number = int(NAME.match(path.name).group(1))
    head = "\n".join(text.split("\n")[:30])
    if LEGACY.search(head):
        return errors, True
    first = next((l for l in text.split("\n") if l.strip()), "")
    title = re.match(r"^# (\d+)\. \S", first)
    if not title or int(title.group(1)) != number:
        errors.append(f"{path.name}: first line must be '# {number}. <title>'")
    preamble = text.split("\n## ", 1)[0]
    if not re.search(r"^Date: \d{4}-\d{2}-\d{2}$", preamble, re.M):
        errors.append(f"{path.name}: needs a 'Date: YYYY-MM-DD' line before the first section")
    found = sections(text)
    if found.get("_order") != SECTIONS:
        errors.append(f"{path.name}: sections must be exactly {', '.join(SECTIONS)} in that order")
    for name in SECTIONS:
        if not "".join(found.get(name, [])).strip():
            errors.append(f"{path.name}: section '{name}' is empty")
    status = next((l.strip() for l in found.get("Status", []) if l.strip()), "")
    matched = STATUS.match(status)
    if not matched:
        errors.append(f"{path.name}: status '{status}' is not Proposed, Accepted, Deprecated or 'Superseded by NNNN'")
    elif matched.group(2) and int(matched.group(2)) not in numbers:
        errors.append(f"{path.name}: superseded by {matched.group(2)}, which does not exist")
    decision = "\n".join(found.get("Decision", []))
    for label in ("**Words:**", "**Options considered:**"):
        if label not in decision:
            errors.append(f"{path.name}: Decision needs a '{label}' line")
    errors += protected_paths(found.get("Decision", []), path.name)[1]
    return errors, False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adr_dir")
    parser.add_argument("--require", nargs="*", default=[], help="ADR numbers this change must add or update")
    parser.add_argument("--root", help="repository root that listed Protects paths are relative to (default: the git toplevel)")
    parser.add_argument("--since", help="base commit; every record added or changed since it is required")
    args = parser.parse_args(argv)
    root = Path(args.adr_dir)
    required = list(args.require)
    if args.since:
        diff = subprocess.run(["git", "-C", str(root), "diff", "--name-only", "--relative", "--diff-filter=AMR",
                               args.since, "--", "."], capture_output=True, text=True)
        if diff.returncode:
            print(f"--since {args.since}: {diff.stderr.strip() or 'git diff failed'}")
            return 2
        untracked = subprocess.run(["git", "-C", str(root), "ls-files", "--others", "--exclude-standard", "--", "."],
                                   capture_output=True, text=True).stdout
        required += [m.group(1) for m in map(NAME.match, (diff.stdout + untracked).split()) if m]
    errors, files = [], {}
    for path in sorted(root.glob("*.md")):
        if path.name in SKIP:
            continue
        match = NAME.match(path.name)
        if not match:
            errors.append(f"{path.name}: file name must be NNNN-short-title.md")
            continue
        number = int(match.group(1))
        if number in files:
            errors.append(f"{path.name}: number {number} is also used by {files[number].name}")
        files[number] = path
    legacy = set()
    for number, path in files.items():
        found, is_legacy = check_file(path, set(files))
        errors += found
        if is_legacy:
            legacy.add(number)
    errors += check_pointers({n: p for n, p in files.items() if n not in legacy}, repo_root(root, args.root), root)
    for number, raw in {int(raw): raw for raw in reversed(required)}.items():
        if number not in files:
            errors.append(f"required ADR {raw} does not exist")
        elif number in legacy and raw in args.require:
            errors.append(f"required ADR {raw} is a legacy record; a new ruling needs its own file")
        elif number in legacy:
            continue
        elif "**Recommended:**" not in "\n".join(sections(files[number].read_text()).get("Decision", [])):
            errors.append(f"required ADR {raw}: Decision needs a '**Recommended:**' line; a record written "
                          "before that line existed takes '**Recommended:** not recorded', never a reconstructed recommendation")
    for error in errors:
        print(error)
    if not errors:
        unchecked = "" if args.since or args.require else "; changed records not checked (no --since or --require)"
        print(f"{len(files)} ADR file(s) checked, {len(legacy)} legacy{unchecked}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
