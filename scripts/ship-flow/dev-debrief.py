#!/usr/bin/env python3
"""Draft the ship-flow dev debrief from a batch's durable records, addressed to dev-flow.
usage: dev-debrief.py <batch-dir>

Reads, all optional except receipt/close-receipt(.DRAFT).json:
  <batch-dir>/receipt/close-receipt.json (or .DRAFT.json)   per-issue rounds, residuals
  <batch-dir>/evidence/worker-evidence-<ISSUE>*.md            each issue's own Evidence block

Prints a kc-ship-close-receipt/v1 `dev_debrief` object (JSON) to stdout: per
Issue, its rounds, its without-it refusal shape, and its review residuals as
code_refusals. It is a draft for the First Officer to edit, not a finished
debrief -- `candidate_correction` is always a placeholder the writer cannot
fill in from the record. Exit 0 on success, 2 on usage or a missing close
receipt.
"""
import glob
import json
import os
import re
import sys

EVIDENCE_FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*):\s?(.*)$")


def parse_evidence_block(text):
    m = re.search(r"^## Evidence\s*$", text, re.MULTILINE)
    if not m:
        return {}
    fields = {}
    for line in text[m.end():].splitlines():
        fm = EVIDENCE_FIELD_RE.match(line)
        if fm:
            fields.setdefault(fm.group(1), fm.group(2))
    return fields


def load_worker_evidence(batch_dir, issue):
    matches = sorted(glob.glob(os.path.join(batch_dir, "evidence", f"worker-evidence-{issue}*.md")))
    if not matches:
        return {}
    with open(matches[0], encoding="utf-8") as f:
        return parse_evidence_block(f.read())


def find_first(*paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None


def build(batch_dir):
    close_path = find_first(
        os.path.join(batch_dir, "receipt", "close-receipt.json"),
        os.path.join(batch_dir, "receipt", "close-receipt.DRAFT.json"),
    )
    if not close_path:
        print(f"dev-debrief: missing {batch_dir}/receipt/close-receipt(.DRAFT).json", file=sys.stderr)
        sys.exit(2)
    with open(close_path, encoding="utf-8") as f:
        close = json.load(f)

    per_issue = {}
    for issue_id, entry in close["issues"].items():
        worker = load_worker_evidence(batch_dir, issue_id)
        evidence_refusals = []
        observed = worker.get("WITHOUT_IT_OBSERVED")
        if observed:
            evidence_refusals.append(observed)
        per_issue[issue_id] = {
            "rounds": entry.get("rounds", 0),
            "evidence_refusals": evidence_refusals,
            "code_refusals": list(entry.get("residuals", [])),
        }

    return {
        "per_issue": per_issue,
        "candidate_correction": "TBD (FO): one candidate correction to the build contract from this batch's Evidence.",
    }


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    print(json.dumps(build(argv[1]), indent=1, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
