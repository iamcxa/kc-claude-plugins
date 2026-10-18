#!/usr/bin/env python3
"""Count the can't-tell rows of the six batch-2 observer reports by FO rule.

Run from the state checkout: python3 -B chat-only-evidence-observer-blind/measure/tally.py
A row names several rules, so each row adds one to every rule it names (rule-report pairs).
"""
import re
import sys
from pathlib import Path

TASKS = ["workflow-budget-ratchet", "prod-security-validation-gate", "worker-loads-declared-package",
         "special-role-triggers", "ui-design-review-in-ideation", "merge-gatekeeper"]
RULES = {
    "A acceptance script presented in full": r"every step in full|presents every step|minimal acceptance script",
    "B goal sufficiency and minimal necessity": r"sufficien",
    "C answers a question the Captain asks at a gate": r"question the Captain asks|asking FO to restate",
    "D package_version / workflow_checkout run": r"package_version|workflow_checkout",
    "E design_surfaces check run": r"design_surfaces",
    "F delivery_gate check run": r"delivery_gate",
    "G dispatch_records --names run": r"--names",
    "H marks the PR ready": r"marks the PR ready",
    "I ruling landed as ADR (judgment)": r"landed as an ADR",
    "J Reviewer: line": r"Reviewer:",
    "K follow-up message is a dispatch": r"follow-up message",
    "L approving accepts the stated order": r"stated order",
    "M Codex/Copilot round handling": r"Codex round 2",
    "N Spacedock Feedback Cycles heading": r"Feedback Cycles",
    "O Captain amendment (grant after chat options)": r"Grant: the Captain answered",
    "P scope change needs the Captain": r"Scope, value, threshold",
    "Q four-field assessment of a finding": r"four-field assessment",
}


def rows(task):
    path = Path("_archive") / task / "observer.md"
    return [line for line in path.read_text().splitlines() if line.lower().startswith("can't tell")]


def main():
    total, pairs, unmatched = 0, {}, []
    for task in TASKS:
        found = rows(task)
        total += len(found)
        print(f"{task}: {len(found)} can't-tell rows")
        for row in found:
            hit = [name for name, rx in RULES.items() if re.search(rx, row, re.I)]
            if not hit:
                unmatched.append((task, row[:100]))
            for name in hit:
                pairs.setdefault(name, set()).add(task)
    print(f"rows: {total}")
    for name in RULES:
        print(f"{len(pairs.get(name, ())):2d} reports  {name}")
    print(f"rule-report pairs: {sum(len(v) for v in pairs.values())}")
    for item in unmatched:
        print("UNMATCHED", item)
    return 1 if unmatched else 0


if __name__ == "__main__":
    sys.exit(main())
