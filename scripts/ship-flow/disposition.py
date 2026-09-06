#!/usr/bin/env python3
"""Disposition kc-pr-review findings by the plan-approval `defaults.findings_outside_brief` rule.

Usage: disposition.py <findings.json>

Reads the findings the First Officer's own session wrote to disk after
running the `kc-pr-review` skill on a PR (schema
`kc-dev-flow-pr-review-findings/v1`: `{"schema": ..., "pr": <int>,
"findings": [{"category": <str>, ...}, ...]}`). A missing file, an
unreadable/invalid file, or a `findings` list with zero entries are all
"reviewer-absent": `kc-plan-approval/v1`'s `empty_reviewer` default
(`fallback_to_fo_diff_read`) exists precisely because empty reviewer output
must never read as "no findings" -- the two are indistinguishable from this
script's input alone, and only the FO's own diff read can tell them apart.

Blocking categories match `kc-plan-approval/v1`'s `findings_outside_brief`
enum (`docs/plan-flow/schema/kc-plan-approval.v1.schema.json`): security,
data-loss, and compatibility findings block; every other category is listed
for the UAT document.

Exit codes: 0 disposition computed and printed as JSON on stdout (block,
listed, or reviewer-absent); 2 usage error.
"""
from __future__ import annotations

import json
import sys

SCHEMA = "kc-dev-flow-ship-flow-disposition/v1"
BLOCKING_CATEGORIES = ("security", "data-loss", "compatibility")
FALLBACK_MARKER = "fallback_to_fo_diff_read"


def load_findings(path: str) -> list[dict] | None:
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(document, dict):
        return None
    findings = document.get("findings")
    if not isinstance(findings, list):
        return None
    return findings


def disposition(findings: list[dict] | None) -> dict:
    if not findings:
        return {"schema": SCHEMA, "disposition": "reviewer-absent", "marker": FALLBACK_MARKER, "findings_count": 0}
    blocking = sorted({
        finding.get("category")
        for finding in findings
        if isinstance(finding, dict) and finding.get("category") in BLOCKING_CATEGORIES
    })
    if blocking:
        return {"schema": SCHEMA, "disposition": "block", "blocking_categories": blocking, "findings_count": len(findings)}
    return {"schema": SCHEMA, "disposition": "listed", "findings_count": len(findings)}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: disposition.py <findings.json>", file=sys.stderr)
        return 2
    result = disposition(load_findings(argv[1]))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
