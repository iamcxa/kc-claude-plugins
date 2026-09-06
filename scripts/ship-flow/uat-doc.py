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
record does not already say (no Captain judgment is synthesized). Every string
pulled from a receipt or an Evidence block is single-line-normalized before it
is rendered, and never trusted as markdown source. Prints markdown to stdout.

Exit 0 on success. Exit 2 on: bad argv; a missing plan-receipt.json; or
receipt/close-receipt JSON that fails to parse or is missing a field this
script reads (json.JSONDecodeError, KeyError, TypeError).
"""
import glob
import json
import os
import re
import sys

EVIDENCE_FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*):\s?(.*)$")
REF_SAFE_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
UNSAFE_MARKER = "<unsafe value refused>"


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


def single_line(value):
    """Collapse any embedded newline/CR run in value into one space."""
    if value is None:
        return None
    return re.sub(r"\s*[\r\n]+\s*", " ", str(value)).strip()


def sanitize_text(value):
    """Single-line-normalize free text and neutralize markdown link/heading syntax."""
    if value is None:
        return None
    value = single_line(value)
    for ch in "\\`[]()":
        value = value.replace(ch, "\\" + ch)
    return value


def render_ref(value, truncate=None):
    """Render value inside a backtick span, or a visible refusal marker."""
    if not value:
        return None
    value = single_line(value)
    if not REF_SAFE_RE.match(value):
        return UNSAFE_MARKER
    return value[:truncate] if truncate else value


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


def find_worker_evidence_files(batch_dir, issue):
    """Files for exactly this issue id: 'worker-evidence-<issue>.md' or
    'worker-evidence-<issue>-<anything>.md', never a longer issue id that
    happens to share this one as a prefix (DEV-9 must not match DEV-90)."""
    pattern = os.path.join(batch_dir, "evidence", f"worker-evidence-{issue}*.md")
    boundary = re.compile(r"^worker-evidence-" + re.escape(issue) + r"(?:[.-]|$)")
    return sorted(p for p in glob.glob(pattern) if boundary.match(os.path.basename(p)))


def has_worker_evidence(batch_dir, issue):
    return bool(find_worker_evidence_files(batch_dir, issue))


def load_worker_evidence(batch_dir, issue):
    matches = find_worker_evidence_files(batch_dir, issue)
    if not matches:
        return None
    with open(matches[0], encoding="utf-8") as f:
        return parse_evidence_block(f.read())


def load_defaults_decisions(batch_dir):
    """'- ' and '* ' top-level bullets under the decisions heading; a non-bullet,
    non-blank line continues the previous bullet (a wrapped line)."""
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

    decisions = []
    current = None
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if current is not None:
                decisions.append(current)
            current = stripped[2:].strip()
        elif stripped and current is not None:
            current += " " + stripped
    if current is not None:
        decisions.append(current)
    return decisions


def base_label(base_sha, issues_by_candidate):
    if not base_sha:
        return "(not recorded)"
    if base_sha in issues_by_candidate:
        return f"({issues_by_candidate[base_sha]})"
    return "(main)"


def render_candidate_field(candidate):
    if not candidate:
        return "candidate: not recorded"
    return f"candidate `{render_ref(candidate, 12)}`"


def render_base_field(base_sha, issues_by_candidate):
    if not base_sha:
        return "base: not recorded"
    safe = single_line(base_sha)
    if not REF_SAFE_RE.match(safe):
        return f"base `{UNSAFE_MARKER}`"
    return f"base `{safe[:12]}` {base_label(safe, issues_by_candidate)}"


def render_branch_field(branch):
    if not branch:
        return "branch: not recorded"
    return f"branch `{render_ref(branch)}`"


def pr_url(pr_field):
    # "owner/repo#123" -> "https://github.com/owner/repo/pull/123"
    m = re.match(r"^([^#]+)#(\d+)$", pr_field or "")
    if not m:
        return sanitize_text(pr_field)
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

    lines = [f"# UAT: {sanitize_text(receipt['project']['name'])}", ""]

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
            reason = f" ({sanitize_text(disposition[0])})" if disposition else ""
            dispositions.append(f"{i} is accepted without a PR{reason}")
        accepted_no_pr_note = " " + "; ".join(dispositions) + "."
    lines.append(
        "Each accepted layer is one Draft PR at one pinned candidate on top of the "
        "previous layer's candidate." + accepted_no_pr_note + " All Linear state untouched by the FO."
    )
    lines.append("")

    unaccounted = [
        i for i in dispatch_order
        if i not in close_issues and not has_worker_evidence(batch_dir, i)
    ]

    for idx, issue_id in enumerate(dispatch_order, 1):
        issue = issues[issue_id]
        worker = load_worker_evidence(batch_dir, issue_id) or {}
        close_issue = close_issues.get(issue_id, {})

        lines.append(f"## Layer {idx}: {issue_id} — {sanitize_text(issue['title'])}")
        lines.append("")

        candidate = close_issue.get("candidate") or worker.get("CANDIDATE_SHA")
        base_sha = worker.get("BASE_SHA")
        branch = close_issue.get("candidate") and worker.get("BRANCH") or issue.get("branch")
        pr = close_issue.get("pr")

        if pr:
            lines.append(
                f"- PR: {pr_url(pr)} · {render_candidate_field(candidate)} · "
                f"{render_base_field(base_sha, candidate_to_issue)} · {render_branch_field(branch)}"
            )
        elif candidate:
            lines.append(
                f"- Outcome: **{sanitize_text(close_issue.get('outcome', 'no PR'))}**. "
                f"{render_candidate_field(candidate)} · "
                f"{render_base_field(base_sha, candidate_to_issue)} · {render_branch_field(branch)}"
            )

        without_it_observed = worker.get("WITHOUT_IT_OBSERVED")
        tests = worker.get("TESTS", "")
        contract_status = "PASS" if tests.rstrip().endswith("exit 0") else ("unrecorded" if not tests else "FAIL")
        if without_it_observed:
            lines.append(
                f"- Without-it (worker self-report): {sanitize_text(without_it_observed)} · "
                f"contract test (worker self-report) {contract_status}"
            )

        self_check = worker.get("SELF_CHECK")
        if self_check:
            lines.append(f"- FO accept station: {sanitize_text(self_check)}")

        for residual in close_issue.get("residuals", []):
            lines.append(f"- Residual: {sanitize_text(residual)}")

        without_it_command = worker.get("WITHOUT_IT_COMMAND")
        without_it_variant = worker.get("WITHOUT_IT_REMOVED_VARIANT")
        if without_it_command and without_it_variant:
            lines.append(
                f"- How to verify: run `{sanitize_text(without_it_command)}` (expect the retained exit above); "
                f"apply `{sanitize_text(without_it_variant)}`; run it again (expect the removed exit above)."
            )
        lines.append("")

    lines.append("## Unaccounted")
    lines.append("")
    if unaccounted:
        for i in unaccounted:
            lines.append(f"- {i}: no Evidence file and no close-receipt entry.")
    else:
        lines.append("- none.")
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
    elif unaccounted:
        lines.append(f"- none dispositioned as stuck; see Unaccounted above for {', '.join(unaccounted)}.")
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
            lines.append(f"- Residual ({i}): {sanitize_text(residual)}")
    if not pr_issues and not no_pr_issues:
        lines.append("- Nothing recorded in the close receipt yet.")
    lines.append("")

    defaults = load_defaults_decisions(batch_dir)
    if defaults is not None:
        lines.append("## Decisions made under `defaults`")
        lines.append("")
        for d in defaults:
            lines.append(f"- {sanitize_text(d)}")
        lines.append("")
        lines.append(f"({len(defaults)} defaults decisions listed above.)")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    batch_dir = argv[1]
    try:
        doc = build_doc(batch_dir)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"uat-doc: malformed or incomplete receipt data in {batch_dir}: {exc!r}", file=sys.stderr)
        return 2
    sys.stdout.write(doc)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
