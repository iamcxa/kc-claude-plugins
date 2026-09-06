#!/usr/bin/env python3
"""Build the ship-flow UAT document from a batch's durable records.
usage: uat-doc.py <batch-dir>

Reads, all optional except plan-receipt.json:
  <batch-dir>/receipt/plan-receipt.json               dispatch order, issue titles, project name
  <batch-dir>/receipt/plan-approval.json               go/max_workspaces/concurrency/repair_rounds
  <batch-dir>/receipt/close-receipt.json (or .DRAFT.json)  per-issue outcome, pr, candidate, residuals
  <batch-dir>/evidence/worker-evidence-<ISSUE>*.md     each issue's own Evidence block
  <batch-dir>/README.md                                "## Decisions made under `defaults`" bullets

It lists what the batch record already states; it does not decide anything the
record does not already say (no Captain judgment is synthesized). Prints
markdown to stdout. Exit 0 on success, 2 on usage or a missing plan-receipt.
"""
import glob
import json
import os
import re
import sys

EVIDENCE_FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*):\s?(.*)$")


def load_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_first(*paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None


def parse_evidence_block(text):
    """First '## Evidence' fenced block's top-level 'KEY: value' fields."""
    m = re.search(r"^## Evidence\s*$", text, re.MULTILINE)
    if not m:
        return {}
    body = text[m.end():]
    fields = {}
    for line in body.splitlines():
        fm = EVIDENCE_FIELD_RE.match(line)
        if fm:
            fields.setdefault(fm.group(1), fm.group(2))
    return fields


def load_worker_evidence(batch_dir, issue):
    pattern = os.path.join(batch_dir, "evidence", f"worker-evidence-{issue}*.md")
    matches = sorted(glob.glob(pattern))
    if not matches:
        return None
    with open(matches[0], encoding="utf-8") as f:
        return parse_evidence_block(f.read())


def load_defaults_decisions(batch_dir):
    readme = os.path.join(batch_dir, "README.md")
    if not os.path.isfile(readme):
        return None
    with open(readme, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^## Decisions made under `defaults`.*?$", text, re.MULTILINE)
    if not m:
        return None
    rest = text[m.end():]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)
    section = rest[:next_heading.start()] if next_heading else rest
    return [line[2:].strip() for line in section.splitlines() if line.startswith("- ")]


def short(sha, n=12):
    return sha[:n] if sha else sha


def base_label(base_sha, issues_by_candidate):
    if base_sha and base_sha in issues_by_candidate:
        return f"({issues_by_candidate[base_sha]})"
    return "(main)"


def pr_url(pr_field):
    # "owner/repo#123" -> "https://github.com/owner/repo/pull/123"
    m = re.match(r"^([^#]+)#(\d+)$", pr_field or "")
    if not m:
        return pr_field
    return f"https://github.com/{m.group(1)}/pull/{m.group(2)}"


def build_doc(batch_dir):
    receipt_path = find_first(
        os.path.join(batch_dir, "receipt", "plan-receipt.json"),
    )
    if not receipt_path:
        print(f"uat-doc: missing {batch_dir}/receipt/plan-receipt.json", file=sys.stderr)
        sys.exit(2)
    receipt = load_json(receipt_path)

    approval = load_json(os.path.join(batch_dir, "receipt", "plan-approval.json"))
    close = load_json(
        find_first(
            os.path.join(batch_dir, "receipt", "close-receipt.json"),
            os.path.join(batch_dir, "receipt", "close-receipt.DRAFT.json"),
        )
        or ""
    )

    dispatch_order = receipt["dispatch_order"]
    issues = receipt["issues"]
    close_issues = (close or {}).get("issues", {})
    batch_name = os.path.basename(os.path.normpath(batch_dir))

    candidate_to_issue = {
        v["candidate"]: k for k, v in close_issues.items() if v.get("candidate")
    }

    lines = [f"# UAT: {receipt['project']['name']}", ""]

    approval_bit = ""
    if approval:
        approval_bit = (
            f" · approval {approval['decision']}/{approval['max_workspaces']}"
            f"/{approval['concurrency']}/{approval['repair_rounds']}"
        )
    lines.append(
        f"Plan receipt `{receipt['receipt_sha256'][:16]}`{approval_bit} · "
        f"dispatch order {' -> '.join(dispatch_order)} · batch `{batch_name}`"
    )
    lines.append("")

    no_pr_issues = [i for i in dispatch_order if close_issues.get(i, {}).get("outcome") == "accepted_no_pr"]
    accepted_no_pr_note = ""
    if no_pr_issues:
        dispositions = []
        for i in no_pr_issues:
            disposition = close_issues[i].get("residuals", [])
            reason = f" ({disposition[0]})" if disposition else ""
            dispositions.append(f"{i} is accepted without a PR{reason}")
        accepted_no_pr_note = " " + "; ".join(dispositions) + "."
    lines.append(
        "Each accepted layer is one Draft PR at one pinned candidate on top of the "
        "previous layer's candidate." + accepted_no_pr_note + " All Linear state untouched by the FO."
    )
    lines.append("")

    for idx, issue_id in enumerate(dispatch_order, 1):
        issue = issues[issue_id]
        worker = load_worker_evidence(batch_dir, issue_id) or {}
        close_issue = close_issues.get(issue_id, {})

        lines.append(f"## Layer {idx}: {issue_id} — {issue['title']}")
        lines.append("")

        candidate = close_issue.get("candidate") or worker.get("CANDIDATE_SHA")
        base_sha = worker.get("BASE_SHA")
        branch = close_issue.get("candidate") and worker.get("BRANCH") or worker.get("BRANCH")
        pr = close_issue.get("pr")

        if pr:
            lines.append(
                f"- PR: {pr_url(pr)} · candidate `{short(candidate)}` · "
                f"base `{short(base_sha)}` {base_label(base_sha, candidate_to_issue)} · "
                f"branch `{branch}`"
            )
        elif candidate:
            lines.append(
                f"- Outcome: **{close_issue.get('outcome', 'no PR')}**. Candidate `{short(candidate)}` · "
                f"base `{short(base_sha)}` {base_label(base_sha, candidate_to_issue)} · branch `{branch}`"
            )

        without_it_observed = worker.get("WITHOUT_IT_OBSERVED")
        tests = worker.get("TESTS", "")
        contract_status = "PASS" if tests.rstrip().endswith("exit 0") else ("unrecorded" if not tests else "FAIL")
        if without_it_observed:
            lines.append(
                f"- Without-it (worker one-liner, FO ran verbatim): {without_it_observed} · "
                f"contract test {contract_status}"
            )

        for residual in close_issue.get("residuals", []):
            lines.append(f"- Residual: {residual}")

        without_it_command = worker.get("WITHOUT_IT_COMMAND")
        without_it_variant = worker.get("WITHOUT_IT_REMOVED_VARIANT")
        if without_it_command and without_it_variant:
            lines.append(
                f"- How to verify: run `{without_it_command}` (expect the retained exit above); "
                f"apply `{without_it_variant}`; run it again (expect the removed exit above)."
            )
        lines.append("")

    lines.append("## Not handed off")
    lines.append("")
    stuck = [
        i for i in dispatch_order
        if close_issues.get(i, {}).get("outcome") in ("failed", "carried", "drift")
    ]
    if stuck:
        for i in stuck:
            lines.append(f"- {i}: {close_issues[i]['outcome']}")
    elif no_pr_issues:
        lines.append(f"- none stuck; {', '.join(no_pr_issues)} dispositioned above.")
    else:
        lines.append("- none stuck.")
    lines.append("")

    lines.append("## For the Captain")
    lines.append("")
    pr_issues = [i for i in dispatch_order if close_issues.get(i, {}).get("pr")]
    if pr_issues:
        prs = ", ".join(f"{pr_url(close_issues[i]['pr'])} ({i})" for i in pr_issues)
        lines.append(f"- Delivery units to approve: {prs}.")
    for i in no_pr_issues:
        lines.append(f"- {i}: outcome accepted_no_pr; accept the disposition or ask for a distinct deliverable.")
    for i in dispatch_order:
        for residual in close_issues.get(i, {}).get("residuals", []):
            lines.append(f"- Residual ({i}): {residual}")
    if not pr_issues and not no_pr_issues:
        lines.append("- Nothing recorded in the close receipt yet.")
    lines.append("")

    defaults = load_defaults_decisions(batch_dir)
    if defaults is not None:
        lines.append("## Decisions made under `defaults`")
        lines.append("")
        for d in defaults:
            lines.append(f"- {d}")
        lines.append("")
        lines.append(f"({len(defaults)} defaults decisions listed above.)")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    batch_dir = argv[1]
    sys.stdout.write(build_doc(batch_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
