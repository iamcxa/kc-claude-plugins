#!/usr/bin/env python3
"""Behavior contract for poc-close-guard.py."""

from __future__ import annotations

import importlib.util
import json
import os
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
    handoff: str | None = None,
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
    if handoff is None:
        handoff = """## POC handoff

```yaml
poc_handoff:
  disposition: not_applicable
  to:
  reason:
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
{handoff}
"""


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
if sys.argv[1:2] == ["status"]:
    print(json.dumps({"command": "status", "entities": json.loads(os.environ.get("FAKE_ENTITIES", "[]"))}))
    raise SystemExit(0)
if sys.argv[1:2] == ["new"]:
    raise SystemExit(int(os.environ.get("FAKE_NEW_EXIT", "0")))
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
    entities: list[dict[str, object]] | None = None,
    new_exit: int = 0,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(
        {
            "FAKE_SPACEDOCK_LOG": str(log),
            "FAKE_ENTITIES": json.dumps(entities or []),
            "FAKE_NEW_EXIT": str(new_exit),
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


with tempfile.TemporaryDirectory(prefix="poc-close-guard-") as temporary:
    root = Path(temporary)
    guard = load_guard()

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

    proceed_not_applicable = work_item_text(direction="proceed")
    require_refusal(
        guard,
        root,
        proceed_not_applicable,
        "consume",
        "proceed requires created, deferred, or declined",
    )
    stop_created = work_item_text().replace(
        "  disposition: not_applicable\n  to:\n  reason:",
        "  disposition: created\n  to: downstream123\n  reason:",
    )
    require_refusal(
        guard,
        root,
        stop_created,
        "consume",
        "stop requires not_applicable",
    )
    proceed_deferred_without_reason = work_item_text(direction="proceed").replace(
        "  disposition: not_applicable", "  disposition: deferred"
    )
    require_refusal(
        guard,
        root,
        proceed_deferred_without_reason,
        "consume",
        "deferred requires a concrete reason",
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

    consumed = run_guard(fake, log, workflow, stop_item, "consume")
    require(consumed.returncode == 0, consumed.stderr)
    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    require(
        calls[-1]["argv"][:3] == ["gate", "consume", "poc123exact"],
        f"wrong consume delegation: {calls[-1]}",
    )

    proceed_item = write_item(root, work_item_text(direction="proceed"), "failed-create")
    body = root / "delivery.md"
    body.write_text(
        "---\nsource: poc:poc123exact\nstatus: backlog\n---\n\n# Delivery seed\n",
        encoding="utf-8",
    )
    failed_create = run_guard(
        fake,
        log,
        workflow,
        proceed_item,
        "create",
        "--slug",
        "delivery-seed",
        "--body",
        str(body),
        new_exit=42,
    )
    require(failed_create.returncode == 42, f"new failure was not preserved: {failed_create}")
    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    require(
        calls[-1]["argv"][0] == "new"
        and all(call["argv"][:2] != ["gate", "consume"] for call in calls[-2:]),
        "failed creation consumed the POC gate",
    )

print("POC close guard test: PASS")
