#!/usr/bin/env python3
"""Behavior contract for poc-close-guard.py."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
GUARD_PATH = HERE / "poc-close-guard.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"POC close guard test: {message}")


def load_guard():
    spec = importlib.util.spec_from_file_location("poc_close_guard", GUARD_PATH)
    require(spec is not None and spec.loader is not None, "cannot load close guard")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def work_item_text(
    direction: str = "stop",
    *,
    outcome: str | None = None,
) -> str:
    if outcome is None:
        outcome = f"""## POC outcome

```yaml
poc_outcome:
  direction: {direction}
  evidence: artifact.json at revision abc123
  strongest_limit: One provider was not evaluated
  reversal_fact: A real run loses the accepted state
  cleanup: complete
```
"""
    return f"""---
id: poc123exact
status: validation
sprint: test/S1
sprint-readiness: ready
---

# POC fixture

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: fixture
  poc_decision: Choose whether to fund the delivery slice
  poc_falsifier: The integrated probe loses the accepted state
  poc_budget: One local run and one review
  poc_stop_when: Stop after the first integrated result
```

{outcome}
"""


def direct_item_text(
    direction: str = "proceed", ready_at: str = "2026-08-30T00:15:00Z", elapsed: int = 900, interventions: int = 0
) -> str:
    outcome = f"""## POC outcome
```yaml
poc_outcome:
  direction: {direction}
  admitted_at: 2026-08-30T00:00:00Z
  decision_ready_at: {ready_at}
  decision_ready_elapsed_seconds: {elapsed}
  captain_interventions_before_decision_ready: {interventions}
  evidence: exact read-only probe at revision abc123
  strongest_limit: One provider was not evaluated
  reversal_fact: A real run loses the accepted state
  cleanup_status_at_decision: complete
```

## POC close measurement
```yaml
poc_close_measurement:
  captain_wait_seconds: 0
  terminal_cleanup_seconds: 2
  cleanup_status: complete
```
"""
    return work_item_text(direction, outcome=outcome).replace(
        "status: validation", "status: implementation\nstarted: 2026-08-30T00:00:00Z"
    ).replace(
        "  poc_stop_when: Stop after the first integrated result",
        "  poc_stop_when: Stop after the first integrated result\n  poc_artifact: no-code\n  poc_safety_boundary: none",
    )


def write_item(root: Path, text: str, name: str = "poc-item") -> Path:
    path = root / f"{name}.md"
    path.write_text(text, encoding="utf-8")
    return path


def require_refusal(guard, root: Path, text: str, phase: str, expected: str) -> None:
    item = write_item(root, text, f"refusal-{len(list(root.glob('*.md')))}")
    try:
        guard.validate(item, phase)
    except guard.CloseError as error:
        require(expected in str(error), f"wrong refusal for {expected!r}: {error}")
        return
    raise SystemExit(f"POC close guard accepted invalid input: {expected}")


def write_fake_spacedock(root: Path) -> tuple[Path, Path]:
    log = root / "spacedock.jsonl"
    fake = root / "spacedock"
    fake.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

log = Path(os.environ["FAKE_SPACEDOCK_LOG"])
with log.open("a", encoding="utf-8") as stream:
    stream.write(json.dumps({"argv": sys.argv[1:], "stdin": sys.stdin.read()}) + "\\n")
if sys.argv[1:3] == ["state", "commit"] and (log.parent / "fail-state-commit").exists():
    print("state durability failed", file=sys.stderr)
    raise SystemExit(7)
if "--resolve" in sys.argv:
    item = Path(os.environ["FAKE_SPACEDOCK_ITEM"])
    print(json.dumps({"slug": item.stem, "path": str(item)}))
else:
    print("delegated")
""",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return fake, log


def run_guard(
    fake: Path,
    log: Path,
    workflow: Path,
    item: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(
        {
            "FAKE_SPACEDOCK_LOG": str(log),
            "FAKE_SPACEDOCK_ITEM": str(item),
        }
    )
    return subprocess.run(
        [
            sys.executable,
            str(GUARD_PATH),
            "--spacedock-bin",
            str(fake),
            "--workflow-dir",
            str(workflow),
            "--work-item",
            str(item),
            *arguments,
        ],
        text=True,
        capture_output=True,
        env=environment,
    )


def native_regressions(root: Path, spacedock: Path) -> None:
    workflow = root / "native"
    workflow.mkdir()

    def native(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(args), cwd=workflow, input=input_text, text=True, capture_output=True,
        )

    def checked(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        result = native(*args, input_text=input_text)
        require(result.returncode == 0, f"native command failed: {args}: {result.stderr}")
        return result

    (workflow / "README.md").write_text("""---
commissioned-by: spacedock@0.27.2
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
trunk: main
stages:
  states:
    - name: backlog
      initial: true
      gate: true
    - name: implementation
    - name: validation
      gate: true
      feedback-to: implementation
    - name: done
      terminal: true
---
# POC close fixture
""", encoding="utf-8")
    checked("git", "init", "-qb", "main")
    checked("git", "config", "user.name", "POC fixture")
    checked("git", "config", "user.email", "poc@example.invalid")
    reports = """
## Exploration Brief

Determine whether one bounded observation supports more work.

## Stage Report: implementation

- FAILED: Establish isolation.
  Isolation is unproven.

### Summary

The first dispatch obligation demanded a positive result.

## Stage Report: implementation (cycle 2)

- DONE: Determine isolation.
  One actual run established that isolation is unproven.

### Summary

Stopped with change under the approved validity stop.
"""
    checked(
        str(spacedock), "new", "direct-poc", "--workflow-dir", str(workflow),
        input_text=direct_item_text("change").replace("id: poc123exact\n", "") + reports,
    )
    item = workflow / "direct-poc.md"
    checked("git", "add", "README.md", item.name)
    checked("git", "commit", "-qm", "seed direct POC")
    (workflow / "sibling.txt").write_text("unrelated staged work\n", encoding="utf-8")
    checked("git", "add", "sibling.txt")

    def close(*args: str, target: Path = item) -> subprocess.CompletedProcess[str]:
        return native(
            sys.executable, str(GUARD_PATH), "--spacedock-bin", str(spacedock),
            "--workflow-dir", str(workflow), "--work-item", str(target), *args,
        )

    prepared = close("prepare", "--question", "Supported?", "--artifact", str(item), "--summary", "direct fixture")
    require(prepared.returncode == 0, f"direct prepare did not durably bind the changed task: {prepared.stderr}")
    committed = checked("git", "show", f"HEAD:{item.name}").stdout
    require("status: validation" in committed, "direct transition was not committed before prepare")
    require(native("git", "cat-file", "-e", "HEAD:sibling.txt").returncode != 0, "direct close committed sibling work")
    require(checked("git", "diff", "--cached", "--name-only").stdout.strip() == "sibling.txt", "direct close changed the sibling index")

    clean_item = item.read_text(encoding="utf-8")
    head_before_retry = checked("git", "rev-parse", "HEAD").stdout
    item.write_text(clean_item + "\nUncommitted validation-stage observation.\n", encoding="utf-8")
    dirty_retry = close("prepare", "--question", "Supported?", "--artifact", str(item), "--summary", "direct fixture")
    require(dirty_retry.returncode != 0, "already-validation prepare accepted a dirty task artifact")
    require(checked("git", "rev-parse", "HEAD").stdout == head_before_retry, "already-validation prepare committed pre-existing task edits")
    require("Uncommitted validation-stage observation." in item.read_text(encoding="utf-8"), "already-validation prepare discarded pre-existing task edits")
    item.write_text(clean_item, encoding="utf-8")

    # The generic defaults still reproduce the incident; the POC entry point
    # must select the existing proof stage without changing Spacedock.
    default = native(str(spacedock), "status", "--workflow-dir", str(workflow), "--read", str(item), "--checklist", "--json")
    require(default.returncode != 0 and 'stage "validation"' in default.stderr, "fixture no longer reproduces current-stage default")
    absent_ac = native(str(spacedock), "status", "--workflow-dir", str(workflow), "--read", str(item), "--stage", "implementation", "--ac-scan", "--json")
    require(absent_ac.returncode != 0 and "no ## Acceptance criteria section" in absent_ac.stderr, "fixture unexpectedly declares ACs")
    before_review = item.read_bytes()
    reviewed = close("review")
    require(reviewed.returncode == 0, f"direct review failed: {reviewed.stderr}")
    review = json.loads(reviewed.stdout)
    require(
        review["proof_stage"] == "implementation" and review["direction"] == "change"
        and len(review["checklist"]) == 1 and review["checklist"][0]["text"] == "Determine isolation."
        and review["acceptance_criteria"] == {"declared": False, "acs": []},
        f"direct review did not select the latest exact-stage negative outcome: {review}",
    )
    require(item.read_bytes() == before_review, "review mutated the work item")
    original = item.read_text(encoding="utf-8")

    for label, text, diagnostic in [
        ("missing report", original.replace("Stage Report: implementation", "Stage Report: implementation-other"), "no ## Stage Report"),
        ("empty latest report", original.replace("- DONE: Determine isolation.\n  One actual run established that isolation is unproven.\n", ""), "no checklist obligations"),
        ("failed latest report", original.replace("- DONE: Determine isolation.", "- FAILED: Determine isolation."), "unfinished or unevidenced"),
        ("no evidence", original.replace("  One actual run established that isolation is unproven.\n", ""), "unfinished or unevidenced"),
        ("blank-only evidence", original.replace("  One actual run established that isolation is unproven.\n", "  \n\n"), "unfinished or unevidenced"),
        ("empty AC section", original + "\n## Acceptance criteria\n", "no recognized criteria"),
        ("malformed AC section", original + "\n## Acceptance criteria\n\nThe result should work.\n", "no recognized criteria"),
        ("uncovered AC", original + "\n## Acceptance criteria\n\n**AC-1** The observation is attributable.\n", "missing evidence"),
        ("undeclared citation", original.replace("  One actual run", "  AC-1: One actual run"), "section is absent"),
    ]:
        item.write_text(text, encoding="utf-8")
        refused = close("review")
        require(refused.returncode != 0 and diagnostic in refused.stderr, f"{label} was silently accepted: {refused.stdout} {refused.stderr}")

    covered = original.replace("  One actual run", "  AC-1: One actual run") + "\n## Acceptance criteria\n\n**AC-1** The observation is attributable.\n"
    item.write_text(covered, encoding="utf-8")
    covered_result = close("review")
    require(covered_result.returncode == 0 and json.loads(covered_result.stdout)["acceptance_criteria"]["declared"], f"covered declared AC was refused: {covered_result.stderr}")
    item.write_text(covered.replace("  AC-1: One", "  AC-1 and AC-2: One"), encoding="utf-8")
    unknown = close("review")
    require(unknown.returncode != 0 and "unknown acceptance criteria: AC-2" in unknown.stderr, "unknown criterion was silently accepted")
    item.write_text(original, encoding="utf-8")

    fresh = workflow / "fresh.md"
    fresh.write_text(work_item_text() + reports + "\n## Stage Report: validation\n\n- DONE: Fresh proof was exercised.\n  The independent validation observation supports stop.\n\n### Summary\n\nReady for the Captain decision.\n", encoding="utf-8")
    fresh_result = close("review", target=fresh)
    require(fresh_result.returncode == 0, fresh_result.stderr)
    fresh_review = json.loads(fresh_result.stdout)
    require(fresh_review["proof_path"] == "fresh" and fresh_review["proof_stage"] == "validation" and fresh_review["checklist"][0]["text"] == "Fresh proof was exercised.", "fresh proof fell back to implementation")
    fresh.write_text(work_item_text() + reports, encoding="utf-8")
    missing_fresh = close("review", target=fresh)
    require(missing_fresh.returncode != 0 and 'stage "validation"' in missing_fresh.stderr, "fresh proof accepted implementation as validation")
    print("POC close guard native regressions: PASS (durable prepare; latest direct/fresh proof; absent/malformed/uncovered ACs)")


with tempfile.TemporaryDirectory(prefix="poc-close-guard-") as temporary:
    root = Path(temporary)
    guard = load_guard()
    direct = write_item(root, direct_item_text(), "direct")
    require(guard.validate(direct, "prepare")[2:] == ("direct", "implementation"), "direct POC was not accepted from implementation")
    require_refusal(guard, root, direct_item_text(elapsed=899), "prepare", "does not match")
    require_refusal(guard, root, direct_item_text(interventions=1), "prepare", "requires direction change")
    require_refusal(guard, root, direct_item_text(ready_at="2026-08-30T00:15:01Z", elapsed=901), "prepare", "requires direction change")
    changed = write_item(root, direct_item_text("change", "2026-08-30T00:15:01Z", 901), "over-budget-change")
    require(guard.validate(changed, "prepare")[1] == "change", "901-second change outcome was refused")

    for field in (
        "direction",
        "evidence",
        "strongest_limit",
        "reversal_fact",
        "cleanup",
    ):
        text = work_item_text().replace(
            next(line for line in work_item_text().splitlines() if line.startswith(f"  {field}:")) + "\n",
            "",
            1,
        )
        require_refusal(guard, root, text, "prepare", f"exactly one {field}")

    require_refusal(
        guard,
        root,
        work_item_text(direction="success"),
        "prepare",
        "direction must be proceed, stop, or change",
    )
    require_refusal(
        guard,
        root,
        work_item_text().replace("  evidence: artifact.json at revision abc123", "  evidence: TBD"),
        "prepare",
        "evidence must be a concrete scalar",
    )

    workflow = root / "workflow"
    workflow.mkdir()
    fake, log = write_fake_spacedock(root)
    stop_item = write_item(root, work_item_text(), "delegated-stop")
    prepared = run_guard(
        fake,
        log,
        workflow,
        stop_item,
        "prepare",
        "--question",
        "Supported?",
        "--artifact",
        "review.md",
        "--summary",
        "POC",
    )
    require(prepared.returncode == 0, prepared.stderr)
    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    require(
        calls[-1]["argv"][:3] == ["gate", "prepare", "poc123exact"],
        f"wrong prepare delegation: {calls[-1]}",
    )

    direct_prepared = run_guard(fake, log, workflow, direct, "prepare", "--question", "Supported?", "--artifact", "review.md", "--summary", "POC")
    require(direct_prepared.returncode == 0, direct_prepared.stderr)
    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    require(calls[-3]["argv"][0] == "status" and calls[-2]["argv"][:3] == ["state", "commit", "direct"] and calls[-1]["argv"][:2] == ["gate", "prepare"], f"direct close did not commit the transition before prepare: {calls[-3:]}")

    (root / "fail-state-commit").touch()
    before = len(calls)
    failed_commit = run_guard(fake, log, workflow, direct, "prepare", "--question", "Supported?", "--artifact", "review.md", "--summary", "POC")
    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    require(failed_commit.returncode == 7 and "state durability failed" in failed_commit.stderr, "state commit failure was hidden")
    require(not any(call["argv"][:2] == ["gate", "prepare"] for call in calls[before:]), "gate prepared despite failed durability")
    (root / "fail-state-commit").unlink()
    retry = write_item(root, direct_item_text().replace("status: implementation", "status: validation"), "retry")
    before = len(calls)
    retried = run_guard(fake, log, workflow, retry, "prepare", "--question", "Supported?", "--artifact", "review.md", "--summary", "POC")
    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    require(retried.returncode == 0 and [call["argv"][:2] for call in calls[before:]] == [["gate", "prepare"]], "already-validation prepare claimed ownership of existing task edits")

    consumed = run_guard(fake, log, workflow, stop_item, "consume")
    require(consumed.returncode == 0, consumed.stderr)
    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    require(
        calls[-1]["argv"][:3] == ["gate", "consume", "poc123exact"],
        f"wrong consume delegation: {calls[-1]}",
    )
    require(
        all(call["argv"][0] != "new" for call in calls),
        f"POC close path created downstream work: {calls}",
    )

    proceed_item = write_item(root, work_item_text(direction="proceed"), "retired-create")
    body = root / "delivery.md"
    body.write_text(
        "---\nsource: poc:poc123exact\nstatus: backlog\n---\n\n# Delivery seed\n",
        encoding="utf-8",
    )
    retired_create = run_guard(
        fake,
        log,
        workflow,
        proceed_item,
        "create",
        "--slug",
        "delivery-seed",
        "--body",
        str(body),
    )
    require(
        retired_create.returncode != 0 and "invalid choice" in retired_create.stderr,
        "POC close guard still accepts downstream creation",
    )

    located = os.environ.get("SPACEDOCK_BIN") or shutil.which("spacedock")
    if located:
        native_regressions(root, Path(located).resolve())
    else:
        print("POC close guard native regressions: SKIP (spacedock unavailable)")

print("POC close guard test: PASS")
