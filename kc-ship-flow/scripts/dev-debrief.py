#!/usr/bin/env python3
"""Draft the ship-flow dev debrief from a batch's durable records, addressed to dev-flow.
usage: dev-debrief.py <batch-dir>

Reads, all required once an issue names them:
  <batch-dir>/receipt/close-receipt.json (or .DRAFT.json)   per-issue rounds
  <batch-dir>/evidence/worker-evidence-<ISSUE>*.md            each issue's own Evidence block (WITHOUT_IT_OBSERVED)
  <batch-dir>/README.md                                       "## Decisions made under `defaults`" bullets naming a REFUSE
  <batch-dir>/review/disposition-<PR>*.json                   a blocking review disposition, if the issue has a PR

Prints a kc-ship-close-receipt/v1 `dev_debrief` object (JSON) to stdout: per
Issue, its rounds, its without-it refusal shape, and its code refusals
sourced from the record (never a copy of `issues[*].residuals`). It is a
draft for the First Officer to edit, not a finished debrief --
`candidate_correction` is always a placeholder the writer cannot fill in
from the record.

Exit 0 on success. Exit 2 on: bad argv; a missing close receipt; a missing
rounds field; a missing worker-evidence file; an evidence-file selection
nothing here can resolve (see select_evidence_file); or a close receipt
that parses as JSON but is malformed or missing a field this script reads
(json.JSONDecodeError, KeyError, TypeError) -- never silently defaulted to
0 or {}.
"""
import glob
import importlib.util
import json
import os
import re
import sys

EVIDENCE_FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*):\s?(.*)$")
ROUND_SUFFIX_RE = re.compile(r"-r(\d+)(?:[.\-]|$)")


def _load_uat_doc():
    """Reuse uat-doc.py's boundary-safe evidence glob and defaults-decision
    bullet parser rather than re-implementing them (both were review findings
    on this same PR: a DEV-9/DEV-90 prefix collision and a dropped `*`
    bullet / wrapped-line bug)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uat-doc.py")
    spec = importlib.util.spec_from_file_location("kc_ship_flow_uat_doc", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


uat_doc = _load_uat_doc()


class AmbiguousEvidence(Exception):
    def __init__(self, candidates):
        self.candidates = candidates
        super().__init__(", ".join(candidates))


def select_evidence_file(matches):
    """Prefer the file whose name carries "accepted"; among what remains,
    prefer the highest `-rN-` round suffix. Raise AmbiguousEvidence if more
    than one candidate survives both tie-breaks (including: any candidate
    has no round suffix to rank by)."""
    if len(matches) == 1:
        return matches[0]
    accepted = [m for m in matches if "accepted" in os.path.basename(m).lower()]
    pool = accepted if accepted else matches
    if len(pool) == 1:
        return pool[0]
    ranked = []
    for m in pool:
        rm = ROUND_SUFFIX_RE.search(os.path.basename(m))
        ranked.append((int(rm.group(1)) if rm else None, m))
    if any(n is None for n, _ in ranked):
        raise AmbiguousEvidence(pool)
    top_round = max(n for n, _ in ranked)
    top = [m for n, m in ranked if n == top_round]
    if len(top) != 1:
        raise AmbiguousEvidence(pool)
    return top[0]


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
    matches = uat_doc.find_worker_evidence_files(batch_dir, issue)
    if not matches:
        print(f"dev-debrief: missing worker-evidence file for {issue} (worker-evidence-{issue}*.md)", file=sys.stderr)
        sys.exit(2)
    try:
        chosen = select_evidence_file(matches)
    except AmbiguousEvidence as exc:
        print(
            f"dev-debrief: {issue} evidence-file selection is ambiguous "
            f"(no single file preferred by 'accepted' or a distinct highest round): {exc.candidates}",
            file=sys.stderr,
        )
        sys.exit(2)
    with open(chosen, encoding="utf-8") as f:
        return parse_evidence_block(f.read())


def find_first(*paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None


def issue_refuse_re(issue_id):
    """Match this issue's own id immediately followed by REFUSE (the
    authoring convention: "DEV-91 REFUSE: ..."), not merely co-occurring
    with REFUSE anywhere in the bullet -- a bullet refusing DEV-91 routinely
    also names DEV-90 as the reason, and that must not attribute the
    refusal to DEV-90 too."""
    return re.compile(r"(?<![A-Z0-9-])" + re.escape(issue_id) + r"(?![A-Z0-9-])\s*REFUSE\b", re.IGNORECASE)


def readme_refuse_bullets(batch_dir, issue_id):
    """Defaults-decision bullets whose own leading reference is this issue's REFUSE."""
    decisions = uat_doc.load_defaults_decisions(batch_dir) or []
    pattern = issue_refuse_re(issue_id)
    return [d for d in decisions if pattern.search(d)]


def review_disposition_refusals(batch_dir, pr):
    """A blocking (non-'accept') review/disposition-<PR>*.json for this
    issue's own PR."""
    if not pr:
        return []
    m = re.search(r"#(\d+)$", pr)
    if not m:
        return []
    review_dir = os.path.join(batch_dir, "review")
    if not os.path.isdir(review_dir):
        return []
    out = []
    for path in sorted(glob.glob(os.path.join(review_dir, f"disposition-{m.group(1)}*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        disposition = data.get("disposition")
        if disposition and disposition != "accept":
            blocking = ", ".join(data.get("blocking_categories", []))
            out.append(
                f"{os.path.basename(path)}: disposition={disposition} "
                f"findings={data.get('findings_count')} blocking=[{blocking}]"
            )
    return out


def find_code_refusals(batch_dir, issue_id, pr):
    refusals = readme_refuse_bullets(batch_dir, issue_id) + review_disposition_refusals(batch_dir, pr)
    return refusals if refusals else ["source: not recorded"]


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
        if "rounds" not in entry:
            print(f"dev-debrief: {issue_id} missing rounds in {close_path}", file=sys.stderr)
            sys.exit(2)
        worker = load_worker_evidence(batch_dir, issue_id)
        evidence_refusals = []
        observed = worker.get("WITHOUT_IT_OBSERVED")
        if observed:
            evidence_refusals.append(observed)
        per_issue[issue_id] = {
            "rounds": entry["rounds"],
            "evidence_refusals": evidence_refusals,
            "code_refusals": find_code_refusals(batch_dir, issue_id, entry.get("pr")),
        }

    return {
        "per_issue": per_issue,
        "candidate_correction": "TBD (FO): one candidate correction to the build contract from this batch's Evidence.",
    }


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    batch_dir = argv[1]
    try:
        debrief = build(batch_dir)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"dev-debrief: malformed or incomplete batch record in {batch_dir}: {exc!r}", file=sys.stderr)
        return 2
    print(json.dumps(debrief, indent=1, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
