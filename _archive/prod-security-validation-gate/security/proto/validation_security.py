#!/usr/bin/env python3
"""Check a prod task's validation security review: a saved report bound to the candidate head, one disposition per finding.

Usage: validation_security.py check <task file>      (delivery_gate.py check calls the same function)

Lines the validation worker writes in the task file:
  Security review (validation): security/validation-<N>.yaml at <40-hex head>
  Security finding (validation <N>) <n>: Material: <text> | declined: <reason> | Needs decision: <text>
Exit 0 when the task is not prod or the review holds; 1 with one line per problem.
"""
import re
import sys
from pathlib import Path

from design_surfaces import FM_PROFILE, report_severities, report_shape

REVIEW = re.compile(r"^Security review \(validation\):[ \t]*(\S.*)$", re.M)
REVIEW_AT = re.compile(r"^(security/validation-(\d+)\.yaml) at ([0-9a-f]{40})$")
FINDING = re.compile(r"^Security finding \(validation (\d+)\) (\d+):[ \t]*(\S.*)$", re.M)


def check_task(task, candidates):
    task = Path(task)
    text = task.read_text()
    front = re.match(r"---\n(.*?)\n---", text, re.S)
    profile = FM_PROFILE.search(front.group(1)) if front else None
    if not profile or profile.group(1) != "prod":
        return [], None
    name = task.name
    reviews = REVIEW.findall(text)
    if not reviews:
        return [f"{name}: a prod task needs a 'Security review (validation):' line naming the saved report and the head it ran on"], None
    bound = None
    for value in reviews:
        m = REVIEW_AT.match(value.strip())
        if m and m.group(3) in candidates:
            bound = m
    if not bound:
        last = reviews[-1].strip()
        if last.lower().startswith("not run"):
            return [f"{name}: validation security review not run ({last}); a missing reviewer holds the ask"], None
        return [f"{name}: no 'Security review (validation):' line has the form 'security/validation-<N>.yaml at <40-hex head>' with a head the latest validation record dispatched (found: {last})"], None
    path, number = bound.group(1), bound.group(2)
    folder = task.parent if task.name == "index.md" else task.parent / task.stem
    report = folder / path
    if not report.is_file():
        return [f"{name}: '{path}' is not a file in the task folder"], None
    body = report.read_text()
    problems = [f"{name}: '{path}' {p}" for p in report_shape(body)]
    if problems:
        return problems, None
    severities, bad = report_severities(body)
    if bad:
        return [f"{name}: '{path}' {p}" for p in bad], None
    lines = {int(n): v.strip() for r, n, v in FINDING.findall(text) if r == number}
    errors, tally = [], {"declined": 0, "decision": 0}
    for n, severity in enumerate(severities, 1):
        entry = lines.get(n, "")
        if re.match(r"Material:\s*\S", entry):
            errors.append(f"{name}: finding {n} of {path} is Material and open at this head; repair and revalidate a new candidate")
        elif re.match(r"declined:\s*\S", entry) and severity in ("MEDIUM", "LOW"):
            tally["declined"] += 1
        elif re.match(r"Needs decision:\s*\S", entry):
            tally["decision"] += 1
        else:
            errors.append(f"{name}: finding {n} of {path} has no 'Security finding (validation {number}) {n}:' line of 'Material: <text>', 'declined: <reason>' (MEDIUM or LOW only) or 'Needs decision: <text>'")
    for n in sorted(set(lines) - set(range(1, len(severities) + 1))):
        errors.append(f"{name}: 'Security finding (validation {number}) {n}:' has no finding in '{path}' ({len(severities)} listed)")
    return errors, f"validation security review {path}: {len(severities)} findings, {tally['declined']} declined, {tally['decision']} decisions"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] != "check":
        print(__doc__)
        return 2
    from delivery_gate import dispatched_candidates
    task = Path(argv[1])
    candidates, _ = dispatched_candidates(task)
    errors, note = check_task(task, candidates)
    print(*errors, sep="\n") if errors else print(note or "not a prod task; no validation security review required")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
