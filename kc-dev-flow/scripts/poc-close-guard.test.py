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

print("POC close guard test: PASS")
