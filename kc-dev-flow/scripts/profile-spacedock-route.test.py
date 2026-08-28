#!/usr/bin/env python3
"""Live Spacedock proof for the guarded POC terminal paths."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
GUARD = HERE / "poc-close-guard.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"profile Spacedock route test: {message}")


def run(command: list[str], cwd: Path, *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, input=input_text, text=True, capture_output=True
    )


configured = os.environ.get("SPACEDOCK_BIN")
located = configured or shutil.which("spacedock")
if located is None:
    print("profile Spacedock route test: SKIP (spacedock unavailable)")
    raise SystemExit(0)
spacedock = Path(located).resolve()
require(spacedock.is_file(), f"spacedock executable does not exist: {spacedock}")


def git(workflow: Path, *args: str) -> None:
    result = run(["git", *args], workflow)
    require(result.returncode == 0, f"git {' '.join(args)} failed: {result.stderr}")


def commit_all(workflow: Path, message: str) -> None:
    git(workflow, "add", "--all")
    result = run(["git", "diff", "--cached", "--quiet"], workflow)
    if result.returncode != 0:
        git(workflow, "commit", "-qm", message)


def poc_body(slug: str, direction: str) -> str:
    return f"""---
+title: {slug}
+status: validation
+sprint: fixture/S1
+sprint-readiness: ready
+---
+
+# {slug}
+
+## Work profile receipt
+
+```yaml
+work_profile:
+  schema: kc-dev-flow-work-profile/v3
+  selected: poc-exploration
+  recommended: poc-exploration
+  route: [build, prove]
+  basis: live fixture
+  poc_decision: Choose whether to fund the delivery slice
+  poc_falsifier: The integrated probe loses the accepted state
+  poc_budget: One local run and one review
+  poc_stop_when: Stop after the first integrated result
+```
+
+## POC outcome
+
+```yaml
+poc_outcome:
+  direction: {direction}
+  evidence: review.md at the fixture revision
+  strongest_limit: One provider was not evaluated
+  reversal_fact: A real run loses the accepted state
+  cleanup: complete
+```
+""".replace("\n+", "\n")


def guard(workflow: Path, item: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run(
        [
            sys.executable,
            str(GUARD),
            "--spacedock-bin",
            str(spacedock),
            "--workflow-dir",
            str(workflow),
            "--work-item",
            str(item),
            *args,
        ],
        workflow,
    )


def create_poc(workflow: Path, slug: str, direction: str) -> Path:
    created = run(
        [str(spacedock), "new", slug, "--workflow-dir", str(workflow)],
        workflow,
        input_text=poc_body(slug, direction),
    )
    require(created.returncode == 0, f"new {slug} failed: {created.stderr}")
    commit_all(workflow, f"add {slug}")
    return workflow / f"{slug}.md"


def approve(workflow: Path, item: Path) -> None:
    prepared = guard(
        workflow,
        item,
        "prepare",
        "--question",
        "Is the POC conclusion supported?",
        "--artifact",
        "review.md",
        "--summary",
        "live POC fixture",
    )
    require(prepared.returncode == 0, f"guard prepare failed: {prepared.stderr}")
    recorded = run(
        [
            str(spacedock),
            "gate",
            "record",
            item.stem,
            "--workflow-dir",
            str(workflow),
            "--decision",
            "approve",
            "--actor",
            "person:captain",
        ],
        workflow,
    )
    require(recorded.returncode == 0, f"gate record failed: {recorded.stderr}")


def finish(workflow: Path, item: Path) -> None:
    commit_all(workflow, f"record {item.stem} outcome")
    consumed = guard(workflow, item, "consume")
    require(consumed.returncode == 0, f"guard consume failed: {consumed.stderr}")
    finalized = run(
        [
            str(spacedock),
            "merge",
            "guard",
            item.stem,
            "--workflow-dir",
            str(workflow),
            "--verdict",
            "passed",
        ],
        workflow,
    )
    require(finalized.returncode == 0, f"merge guard failed: {finalized.stderr}")
    require(
        (workflow / "_archive" / item.name).is_file(),
        f"{item.stem} did not reach the archive",
    )


with tempfile.TemporaryDirectory(prefix="kc-dev-flow-poc-close-live-") as temporary:
    workflow = Path(temporary)
    (workflow / "README.md").write_text(
        """---
+commissioned-by: spacedock@0.27.0
+entity-type: task
+entity-label: task
+entity-label-plural: tasks
+id-style: sd-b32
+trunk: main
+stages:
+  states:
+    - name: backlog
+      initial: true
+      gate: true
+    - name: ideation
+      gate: true
+    - name: implementation
+    - name: validation
+      feedback-to: implementation
+      gate: true
+    - name: done
+      terminal: true
+---
+
+# POC close fixture
+""".replace("\n+", "\n"),
        encoding="utf-8",
    )
    git(workflow, "init", "-q", "-b", "main", ".")
    git(workflow, "config", "user.name", "POC fixture")
    git(workflow, "config", "user.email", "poc@example.invalid")
    (workflow / "review.md").write_text("supported fixture conclusion\n", encoding="utf-8")
    commit_all(workflow, "seed workflow")

    for direction in ("stop", "change", "proceed"):
        item = create_poc(workflow, f"{direction}-poc", direction)
        approve(workflow, item)
        finish(workflow, item)

    retired_poc = create_poc(workflow, "retired-create-poc", "proceed")
    approve(workflow, retired_poc)
    refused_create = guard(
        workflow,
        retired_poc,
        "create",
    )
    require(
        refused_create.returncode != 0 and "invalid choice" in refused_create.stderr,
        "retired downstream creation command still exists",
    )
    require(retired_poc.is_file(), "refused creation moved the POC out of validation")
    finish(workflow, retired_poc)

print("profile Spacedock route test: PASS")
