#!/usr/bin/env python3
"""Check that a candidate's changed files map to declared obligations.

Reads the real `git diff` between two revisions, then requires the worker's
Evidence block to carry one `SURFACE:` line per non-excluded changed file,
naming an AC declared in the Brief, a falsifier, a safety boundary, or a
lifecycle obligation. This is the implementation-exit enforcement point for
the kernel's minimal-necessity obligation: a check is evidence only once it
has been seen to fail (see AC-1's DEV-66 fixture).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


class CheckError(RuntimeError):
    pass


DEFAULT_EXCLUDE_PATTERNS = (
    re.compile(r"(^|/)tests/"),
    re.compile(r"(^|/)fixtures/"),
    re.compile(r"(^|/)test_[^/]+$"),
    re.compile(r"(^|/)[^/]+_test\.py$"),
)

AC_HEADING_RE = re.compile(r"\*\*AC-(\d+)\s*\*\*")
AC_TARGET_RE = re.compile(r"^AC-(\d+)$")


def read_text(path: Path, *, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CheckError(f"cannot read {label} {path}: {exc}") from exc


def git_changed_files(base: str, candidate: str, *, repo: Path) -> list[str]:
    for sha in (base, candidate):
        verify = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", f"{sha}^{{commit}}"],
            capture_output=True,
            text=True,
        )
        if verify.returncode != 0:
            raise CheckError(f"unreachable revision: {sha}")
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-status", "--diff-filter=ACMR", base, candidate],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CheckError(f"git diff failed: {result.stderr.strip()}")
    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        # Renames carry old\tnew; the last column is always the current path.
        files.append(line.split("\t")[-1])
    return sorted(files)


def is_excluded(path: str, extra_patterns: list[re.Pattern[str]]) -> bool:
    return any(p.search(path) for p in (*DEFAULT_EXCLUDE_PATTERNS, *extra_patterns))


def parse_brief_acs(text: str) -> set[str]:
    return {f"AC-{number}" for number in AC_HEADING_RE.findall(text)}


def parse_mapping(text: str, *, line_prefix: str | None) -> dict[str, str]:
    if line_prefix:
        pattern = re.compile(
            rf"^{re.escape(line_prefix)}:\s*(?P<path>\S+)\s*->\s*(?P<target>.+?)\s*$",
            re.MULTILINE,
        )
    else:
        pattern = re.compile(r"^(?P<path>\S+)\s*->\s*(?P<target>.+?)\s*$", re.MULTILINE)
    return {m.group("path"): m.group("target").strip() for m in pattern.finditer(text)}


def validate_target(path: str, target: str, declared_acs: set[str]) -> str | None:
    if AC_TARGET_RE.match(target) and target not in declared_acs:
        return f"unknown AC: {path} -> {target}"
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_sha")
    parser.add_argument("candidate_sha")
    parser.add_argument("evidence_file", type=Path)
    parser.add_argument("--brief", type=Path, required=True, help="Brief file declaring AC-N headings")
    parser.add_argument("--profile", choices=("poc", "pilot", "production"), default="pilot")
    parser.add_argument("--retained", action="append", default=[], help="POC-only: retained-surface paths to check")
    parser.add_argument("--exclude", action="append", default=[], help="extra regex excluded from the checked set")
    parser.add_argument(
        "--shape-mapping",
        type=Path,
        default=None,
        help="production-only: file of `path -> obligation` lines from the shape contract",
    )
    parser.add_argument("--repo", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = (args.repo or Path.cwd()).resolve()

    changed = git_changed_files(args.base_sha, args.candidate_sha, repo=repo)
    evidence_text = read_text(args.evidence_file, label="evidence file")
    brief_text = read_text(args.brief, label="brief")
    declared_acs = parse_brief_acs(brief_text)
    surface_map = parse_mapping(evidence_text, line_prefix="SURFACE")

    if args.profile == "poc":
        retained = set(args.retained)
        checked = [path for path in changed if path in retained]
    else:
        extra_excludes = [re.compile(pattern) for pattern in args.exclude]
        checked = [path for path in changed if not is_excluded(path, extra_excludes)]

    violations: list[str] = []
    for path in checked:
        if path not in surface_map:
            violations.append(f"missing SURFACE line: {path}")
            continue
        problem = validate_target(path, surface_map[path], declared_acs)
        if problem:
            violations.append(problem)

    if args.profile == "production" and args.shape_mapping is not None:
        shape_text = read_text(args.shape_mapping, label="shape mapping")
        shape_map = parse_mapping(shape_text, line_prefix=None)
        for path in checked:
            declared = shape_map.get(path)
            if declared is not None and surface_map.get(path) != declared:
                violations.append(
                    f"shape-mapping mismatch: {path} (shape contract wants {declared}, "
                    f"evidence has {surface_map.get(path)!r})"
                )

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
