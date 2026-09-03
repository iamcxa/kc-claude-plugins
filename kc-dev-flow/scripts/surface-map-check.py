#!/usr/bin/env python3
"""Check that a candidate's changed files map to declared obligations.

Reads the real `git diff` between two revisions, then requires the worker's
Evidence block to carry one `SURFACE:` line per checked changed file, naming
an AC declared in the Brief, a falsifier, a safety boundary, a lifecycle
obligation, or (for a deleted file) removal — each backed by a without-it
command and removed variant that actually binds the surface's path, not a
stub. Profile and (for POC) the retained-surface set are read from the work
item's own receipt, not from caller-supplied flags: a caller-declared scope
is exactly the kind of unchecked input this script exists to remove.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from pathlib import Path


class CheckError(RuntimeError):
    pass


HERE = Path(__file__).resolve().parent
LOADER_PATH = HERE / "profile-contract-loader.py"


def load_profile_loader():
    spec = importlib.util.spec_from_file_location("profile_contract_loader", LOADER_PATH)
    if spec is None or spec.loader is None:
        raise CheckError(f"cannot import profile loader at {LOADER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LOADER = load_profile_loader()

EXCLUDE_DIR_RE = re.compile(r"(^|/)(tests?|fixtures?|__tests__)/")
EXCLUDE_SUFFIXES = (".test.py", "_test.py", ".test.ts", ".spec.ts")

AC_HEADING_RE = re.compile(r"\*\*AC-(\d+)\s*\*\*")
AC_TARGET_RE = re.compile(r"^AC-(\d+)$")
LIFECYCLE_TARGET_RE = re.compile(r"^lifecycle:[A-Za-z0-9_-]+$")
LITERAL_TARGETS = {"falsifier", "safety-boundary"}
FORBIDDEN_WITHOUT_IT = {"true", ":", "exit 0"}

SURFACE_LINE_RE = re.compile(
    r"^SURFACE:\s*(?P<path>\S+)\s*->\s*(?P<target>[^|\n]+?)\s*\|"
    r"\s*(?P<without_it>[^|\n]*?)\s*\|\s*(?P<removed>[^|\n]*?)\s*$",
    re.MULTILINE,
)


def read_text(path: Path, *, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CheckError(f"cannot read {label} {path}: {exc}") from exc


def git_changed_files(base: str, candidate: str, *, repo: Path) -> list[tuple[str, str]]:
    for sha in (base, candidate):
        verify = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", f"{sha}^{{commit}}"],
            capture_output=True,
            text=True,
        )
        if verify.returncode != 0:
            raise CheckError(f"unreachable revision: {sha}")
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-status", "--diff-filter=ACMRD", base, candidate],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CheckError(f"git diff failed: {result.stderr.strip()}")
    entries: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        # Renames carry old\tnew; the last column is always the current path.
        entries.append((parts[0][0], parts[-1]))
    return sorted(entries, key=lambda entry: entry[1])


def is_excluded(path: str) -> bool:
    return bool(EXCLUDE_DIR_RE.search(path)) or path.endswith(EXCLUDE_SUFFIXES)


def parse_brief_acs(text: str) -> set[str]:
    return {f"AC-{number}" for number in AC_HEADING_RE.findall(text)}


def parse_mapping(text: str) -> dict[str, str]:
    pattern = re.compile(r"^(?P<path>\S+)\s*->\s*(?P<target>.+?)\s*$", re.MULTILINE)
    return {m.group("path"): m.group("target").strip() for m in pattern.finditer(text)}


def parse_surface_lines(text: str) -> dict[str, tuple[str, str, str]]:
    mapping: dict[str, tuple[str, str, str]] = {}
    for match in SURFACE_LINE_RE.finditer(text):
        mapping[match.group("path")] = (
            match.group("target").strip(),
            match.group("without_it").strip(),
            match.group("removed").strip(),
        )
    return mapping


def extract_retained_surfaces(work_item_text: str) -> list[str]:
    headings = list(re.finditer(r"^## POC outcome\s*$", work_item_text, re.MULTILINE))
    if not headings:
        return []
    start = headings[-1].end()
    next_heading = re.search(r"^##\s+", work_item_text[start:], re.MULTILINE)
    section = work_item_text[start : start + next_heading.start()] if next_heading else work_item_text[start:]
    field = re.search(r"^  retained_surfaces:[ \t]*(.*)$", section, re.MULTILINE)
    if not field:
        return []
    inline = field.group(1).strip()
    if inline.startswith("[") and inline.endswith("]"):
        inline = inline[1:-1]
    if inline:
        return [item.strip().strip("\"'") for item in inline.split(",") if item.strip()]
    items = []
    for line in section[field.end():].splitlines():
        if not line.strip():
            continue
        if re.match(r"^\s{2,}-\s", line):
            items.append(line.split("- ", 1)[1].strip().strip("\"'"))
            continue
        break
    return items


def target_problem(path: str, target: str, declared_acs: set[str], is_deleted: bool) -> str | None:
    if AC_TARGET_RE.match(target):
        if target not in declared_acs:
            return f"unknown AC: {path} -> {target}"
        return None
    if target == "removal":
        return None if is_deleted else f"invalid target: {path} -> {target}"
    if target in LITERAL_TARGETS or LIFECYCLE_TARGET_RE.match(target):
        return None
    return f"invalid target: {path} -> {target}"


def without_it_binds(target: str, without_it: str, removed_variant: str, path: str, changed_files: list[str]) -> bool:
    if target == "removal":
        return without_it.strip() == "-" and removed_variant.strip() == "-"
    if not without_it or not removed_variant:
        return False
    if without_it.strip() in FORBIDDEN_WITHOUT_IT:
        return False
    if not any(candidate in without_it for candidate in changed_files):
        return False
    removed_tokens = removed_variant.strip().split()
    if not removed_tokens or removed_tokens[0] != "git":
        return False
    return path in removed_variant


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_sha")
    parser.add_argument("candidate_sha")
    parser.add_argument("evidence_file", type=Path)
    parser.add_argument("--work-item", type=Path, required=True, help="work item whose receipt selects the profile")
    parser.add_argument("--brief", type=Path, required=True, help="Brief file declaring AC-N headings")
    parser.add_argument(
        "--shape-mapping",
        type=Path,
        default=None,
        help="required for a production profile: `path -> obligation` lines from the shape contract",
    )
    parser.add_argument(
        "--no-exclude",
        action="store_true",
        help="check every changed file, ignoring the fixed test/fixture exclusion pattern",
    )
    parser.add_argument("--repo", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = (args.repo or Path.cwd()).resolve()

    diff_entries = git_changed_files(args.base_sha, args.candidate_sha, repo=repo)
    changed = [path for _, path in diff_entries]
    deleted_paths = {path for status, path in diff_entries if status == "D"}

    evidence_text = read_text(args.evidence_file, label="evidence file")
    brief_text = read_text(args.brief, label="brief")
    declared_acs = parse_brief_acs(brief_text)
    surface_map = parse_surface_lines(evidence_text)

    work_item_path = args.work_item.expanduser().resolve()
    work_item_text = read_text(work_item_path, label="work item")
    try:
        receipt = LOADER.resolve_work_item(work_item_path)
    except LOADER.ContractError as exc:
        raise CheckError(str(exc)) from exc
    profile = receipt["profile"]

    violations: list[str] = []
    excluded: list[str] = []

    if profile == "poc-exploration":
        retained = extract_retained_surfaces(work_item_text)
        if not retained:
            raise CheckError("POC declares no retained surface")
        changed_set = set(changed)
        checked = []
        for path in retained:
            if path not in changed_set:
                violations.append(f"retained surface not in diff: {path}")
            else:
                checked.append(path)
    else:
        checked = []
        for path in changed:
            if not args.no_exclude and is_excluded(path) and path not in surface_map:
                excluded.append(path)
            else:
                checked.append(path)

    shape_map: dict[str, str] | None = None
    if profile == "production":
        if args.shape_mapping is None:
            raise CheckError("--shape-mapping is required for production profile")
        shape_map = parse_mapping(read_text(args.shape_mapping, label="shape mapping"))

    for path in checked:
        entry = surface_map.get(path)
        if entry is None:
            violations.append(f"missing SURFACE line: {path}")
            continue
        target, without_it, removed_variant = entry
        problem = target_problem(path, target, declared_acs, path in deleted_paths)
        if problem:
            violations.append(problem)
        if not without_it_binds(target, without_it, removed_variant, path, changed):
            violations.append(f"without-it pair does not bind {path}")
        if shape_map is not None:
            declared_obligation = shape_map.get(path)
            if declared_obligation is None:
                violations.append(f"unmapped in shape: {path}")
            elif declared_obligation.strip() != target.strip():
                violations.append(
                    f"shape mapping says {declared_obligation.strip()}, evidence says {target.strip()}"
                )

    for path in excluded:
        print(f"excluded: {path}")

    if violations:
        print("surface-map-check: FAIL")
        for violation in violations:
            print(violation)
        return 1

    print(f"surface-map-check: OK ({len(checked)} files checked)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CheckError as exc:
        print(f"surface-map-check: {exc}", file=sys.stderr)
        raise SystemExit(2)
