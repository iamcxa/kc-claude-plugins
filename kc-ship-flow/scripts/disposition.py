#!/usr/bin/env python3
"""Disposition kc-pr-review findings by the plan-approval `defaults.findings_outside_brief` rule.

Usage: disposition.py <findings.json>
       disposition.py <bundle-dir>

Reads the findings the First Officer's own session wrote to disk after
running the `kc-pr-review` skill on a PR (schema
`kc-dev-flow-pr-review-findings/v1`: `{"schema": ..., "pr": <int>,
"findings": [{"category": <str>, ...}, ...]}`). A missing file, an
unreadable/invalid file, or a `findings` list with zero entries are all
"reviewer-absent": `kc-plan-approval/v1`'s `empty_reviewer` default
(`fallback_to_fo_diff_read`) exists precisely because empty reviewer output
must never read as "no findings" -- the two are indistinguishable from this
script's input alone, and only the FO's own diff read can tell them apart.

A non-empty `findings` list whose entries are not all dicts with a string
`category` is refused outright (exit 2, not a disposition) -- a malformed
writer output must not silently read as a normal `listed` finding.

`category` is normalized (stripped, casefolded) before comparison, so a
differently-cased category (`Security`) still matches. Blocking categories
match `kc-plan-approval/v1`'s `findings_outside_brief` enum
(`docs/plan-flow/schema/kc-plan-approval.v1.schema.json`): security,
data-loss, and compatibility findings block. A fixed set of other categories
this station has actually seen from kc-pr-review (correctness, docs, style,
test-coverage) are listed for the UAT document. Any category outside both
sets is unrecognized and blocks -- fail closed like the reviewer-absent path,
rather than let an unreviewed category class through as merely `listed`.

When the sole argument is a directory, it is a self-describing review-input
bundle: `<dir>/findings.json` (same schema as the single-file form),
`<dir>/changed-files.txt` (one changed path per line; this script does not
otherwise learn the diff, so the bundle carries it explicitly), and, only
required when a changed path is a dependency manifest or lockfile
(package.json, package-lock.json, pnpm-lock.yaml, yarn.lock,
requirements*.txt, pyproject.toml, poetry.lock, go.mod, go.sum, Cargo.toml,
Cargo.lock), `<dir>/review/findings-<pr>-supply.json` (the
`tob-supply-chain-checker` lane's output, `<pr>` taken from `findings.json`'s
`pr` field). A dependency-manifest path with the supply-chain file absent
refuses (exit 2, `supply-chain findings required`) before any disposition is
computed; a diff without such a path, or a present supply-chain file, is
unaffected and proceeds to the normal disposition below. The single-file
form never checks this -- it carries no changed-file list to gate on.

Exit codes: 0 disposition computed and printed as JSON on stdout (block,
listed, or reviewer-absent); 2 usage error, a findings list with a
non-dict entry or an entry whose `category` is not a string, or (bundle form
only) a dependency-manifest diff missing its supply-chain findings file.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCHEMA = "kc-dev-flow-ship-flow-disposition/v1"
BLOCKING_CATEGORIES = frozenset({"security", "data-loss", "compatibility"})
NON_BLOCKING_CATEGORIES = frozenset({"correctness", "docs", "style", "test-coverage"})
KNOWN_CATEGORIES = BLOCKING_CATEGORIES | NON_BLOCKING_CATEGORIES
FALLBACK_MARKER = "fallback_to_fo_diff_read"
UNRECOGNIZED_REASON = "unrecognized-category"

DEPENDENCY_FILENAMES = frozenset({
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "pyproject.toml", "poetry.lock", "go.mod", "go.sum", "Cargo.toml", "Cargo.lock",
})
REQUIREMENTS_RE = re.compile(r"^requirements.*\.txt$")
SUPPLY_CHAIN_REFUSAL = "supply-chain findings required"


class MalformedFindings(ValueError):
    """A non-empty `findings` list has an entry that is not a dict with a string `category`."""


def normalize_category(raw: str) -> str:
    return raw.strip().casefold()


def is_dependency_path(changed_path: str) -> bool:
    name = changed_path.rsplit("/", 1)[-1]
    return name in DEPENDENCY_FILENAMES or bool(REQUIREMENTS_RE.match(name))


def load_document(path: str) -> dict | None:
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return document if isinstance(document, dict) else None


def findings_from_document(document: dict | None, source: str) -> list[dict] | None:
    if document is None:
        return None
    findings = document.get("findings")
    if not isinstance(findings, list):
        return None
    if findings and not all(
        isinstance(finding, dict) and isinstance(finding.get("category"), str)
        for finding in findings
    ):
        raise MalformedFindings(source)
    return findings


def load_findings(path: str) -> list[dict] | None:
    return findings_from_document(load_document(path), path)


def read_changed_files(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def disposition(findings: list[dict] | None) -> dict:
    if not findings:
        return {"schema": SCHEMA, "disposition": "reviewer-absent", "marker": FALLBACK_MARKER, "findings_count": 0}

    normalized = [normalize_category(finding["category"]) for finding in findings]
    unrecognized = sorted({
        finding["category"]
        for finding, category in zip(findings, normalized)
        if category not in KNOWN_CATEGORIES
    })
    if unrecognized:
        return {
            "schema": SCHEMA,
            "disposition": "block",
            "reason": UNRECOGNIZED_REASON,
            "unrecognized_categories": unrecognized,
            "findings_count": len(findings),
        }

    blocking = sorted({category for category in normalized if category in BLOCKING_CATEGORIES})
    if blocking:
        return {"schema": SCHEMA, "disposition": "block", "blocking_categories": blocking, "findings_count": len(findings)}
    return {"schema": SCHEMA, "disposition": "listed", "findings_count": len(findings)}


def main_bundle(target: Path) -> int:
    document = load_document(str(target / "findings.json"))
    try:
        findings = findings_from_document(document, str(target / "findings.json"))
    except MalformedFindings:
        print(
            f"disposition.py: refusing malformed findings (non-dict or non-string category entry): "
            f"{target / 'findings.json'}",
            file=sys.stderr,
        )
        return 2

    changed_files_path = target / "changed-files.txt"
    changed_files = read_changed_files(changed_files_path) if changed_files_path.is_file() else []
    if any(is_dependency_path(changed) for changed in changed_files):
        pr = document.get("pr") if document else None
        supply_findings_path = target / "review" / f"findings-{pr}-supply.json"
        if not supply_findings_path.is_file():
            print(SUPPLY_CHAIN_REFUSAL, file=sys.stderr)
            return 2

    result = disposition(findings)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: disposition.py <findings.json>|<bundle-dir>", file=sys.stderr)
        return 2
    target = Path(argv[1])
    if target.is_dir():
        return main_bundle(target)
    try:
        findings = load_findings(argv[1])
    except MalformedFindings:
        print(
            f"disposition.py: refusing malformed findings (non-dict or non-string category entry): {argv[1]}",
            file=sys.stderr,
        )
        return 2
    result = disposition(findings)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
