#!/usr/bin/env python3
"""Pick a batch's UAT-ready CLI-e2e shape from its plan and close receipts.

Usage: e2e-gate.py <plan-receipt.json> <close-receipt.json>

Reads only kc-plan-receipt/v1's `dispatch_order`, `milestones`, and
`issues[*].milestone`, and kc-ship-close-receipt/v1's `issues[*].candidate`
(both receipts may be minimal fixtures carrying just those fields; this
script does not validate the full schema -- that is
docs/plan-flow/schema/validate-receipt.py's job). A batch names one journey:
milestone name and stacked head both come from the last `dispatch_order`
issue that carries one, since an accepted-without-PR layer names neither.

Shape:
  milestone named, docs/ship-flow/flows/<slug>.yaml exists -> run
    scripts/ship-flow/e2e-cli.sh at the stacked head, exit its exit code.
  milestone named, no flow file                            -> print
    "e2e: not applicable" with the reason, exit 0.
  no milestone named                                        -> exit 1;
    the batch is not UAT-ready.

Exit codes: 0 CLI e2e passed, or not-applicable recorded; 1 CLI e2e failed,
a named milestone's flow file has no candidate to run at, or no milestone is
named; 2 usage or receipt-parsing error.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLOWS_DIR = ROOT / "docs/ship-flow/flows"
E2E_CLI = ROOT / "scripts/ship-flow/e2e-cli.sh"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def milestone_name(plan_receipt: dict) -> str | None:
    milestones = {m["id"]: m["name"] for m in plan_receipt.get("milestones", [])}
    issues = plan_receipt["issues"]
    name = None
    for key in plan_receipt["dispatch_order"]:
        milestone_id = issues.get(key, {}).get("milestone")
        if milestone_id is not None:
            name = milestones.get(milestone_id, name)
    return name


def stacked_head(plan_receipt: dict, close_receipt: dict) -> str | None:
    issues = close_receipt["issues"]
    head = None
    for key in plan_receipt["dispatch_order"]:
        candidate = issues.get(key, {}).get("candidate")
        if candidate:
            head = candidate
    return head


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: e2e-gate.py <plan-receipt.json> <close-receipt.json>", file=sys.stderr)
        sys.exit(2)
    try:
        plan_receipt = load(sys.argv[1])
        close_receipt = load(sys.argv[2])
        name = milestone_name(plan_receipt)
        head = stacked_head(plan_receipt, close_receipt)
    except (OSError, json.JSONDecodeError, KeyError) as error:
        print(f"e2e-gate: cannot read receipts: {error}", file=sys.stderr)
        sys.exit(2)

    if name is None:
        print("e2e-gate: no milestone journey named for this batch; batch is not UAT-ready", file=sys.stderr)
        sys.exit(1)

    flow_path = FLOWS_DIR / f"{slugify(name)}.yaml"
    if not flow_path.is_file():
        print(f"e2e: not applicable (reason: milestone '{name}' has no flow file at {flow_path.relative_to(ROOT)})")
        sys.exit(0)

    if head is None:
        print(f"e2e-gate: milestone '{name}' has a flow file but no dispatch_order issue carries a candidate", file=sys.stderr)
        sys.exit(1)

    with tempfile.NamedTemporaryFile(prefix="e2e-cli-", suffix=".log", delete=False, mode="w", encoding="utf-8") as log_file:
        result = subprocess.run(
            [str(E2E_CLI), head, str(flow_path)],
            stdout=log_file, stderr=subprocess.STDOUT,
        )
        log_path = log_file.name
    print(f"CLI e2e: milestone '{name}' at {head}, log at {log_path}, exit {result.returncode}")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
