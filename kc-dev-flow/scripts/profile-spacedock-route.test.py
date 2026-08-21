#!/usr/bin/env python3
"""Live Spacedock smoke for non-Production profile route skips."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"profile Spacedock route test: {message}")


configured = os.environ.get("SPACEDOCK_BIN")
located = configured or shutil.which("spacedock")
if located is None:
    print("profile Spacedock route test: SKIP (spacedock unavailable)")
    raise SystemExit(0)

spacedock = Path(located).resolve()
require(spacedock.is_file(), f"spacedock executable does not exist: {spacedock}")

with tempfile.TemporaryDirectory(prefix="kc-dev-flow-spacedock-route-") as temporary:
    workflow = Path(temporary)
    (workflow / "README.md").write_text(
        """---
stages:
  states:
    - name: backlog
      initial: true
    - name: ideation
    - name: implementation
    - name: validation
    - name: release
    - name: done
      terminal: true
---

# Profile route fixture
""",
        encoding="utf-8",
    )

    for slug, profile in (
        ("poc-route", "poc-exploration"),
        ("pilot-route", "pilot-product-slice"),
    ):
        entity = workflow / f"{slug}.md"
        entity.write_text(
            f"""---
status: validation
---

# {slug}

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: {profile}
```
""",
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                str(spacedock),
                "status",
                "--workflow-dir",
                str(workflow),
                "--set",
                slug,
                "status=done",
                "verdict=passed",
                "completed",
                "--json",
            ],
            text=True,
            capture_output=True,
        )
        require(
            result.returncode == 0,
            f"{profile} validation -> done failed:\n{result.stdout}{result.stderr}",
        )
        updated = entity.read_text(encoding="utf-8")
        # This write may store `PASSED`: the observed Spacedock canonicalises the
        # CLI's `verdict=passed` to its schema case. The smoke checks that the
        # entity terminalized, not how the value was serialized, so compare
        # case-insensitively.
        require(
            "status: done" in updated
            and "verdict: passed" in updated.lower()
            and "completed:" in updated,
            f"{profile} did not terminalize directly:\n{updated}",
        )

print("profile Spacedock route test: PASS")
