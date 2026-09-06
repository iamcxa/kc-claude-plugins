#!/usr/bin/env python3
"""Behavior contract for kc-ship-flow/scripts/ship-debrief.py."""

from __future__ import annotations

import importlib.util
import json as json_mod
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "ship-debrief.py"
FIXTURES = HERE / "fixtures" / "debrief-writer"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ship-debrief test: {message}")


def load_module():
    spec = importlib.util.spec_from_file_location("ship_debrief", MODULE_PATH)
    require(spec is not None and spec.loader is not None, "cannot load ship-debrief.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ship_debrief = load_module()


def run(batch: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), str(batch)], capture_output=True, text=True
    )


# --- finding #3: a missing README.md exits 2, never a silent [] ----------
missing_readme = run(FIXTURES / "batch-missing-readme-probe")
require(missing_readme.returncode == 2, f"missing README must exit 2, got {missing_readme.returncode}")
require("README.md" in missing_readme.stderr, f"missing-README refusal must name README.md: {missing_readme.stderr!r}")

# --- finding #3: a missing `minutes` key exits 2 naming the issue, never -
# --- a silent default of {} ------------------------------------------------
missing_minutes = run(FIXTURES / "batch-missing-minutes-probe")
require(missing_minutes.returncode == 2, f"missing minutes must exit 2, got {missing_minutes.returncode}")
require("DEV-306" in missing_minutes.stderr, f"missing-minutes refusal must name DEV-306: {missing_minutes.stderr!r}")

# --- finding #5: the overturn rule -- a later bullet marks the earlier ----
# --- decision it names by timestamp with retract/overturn/correction; a --
# --- shared timestamp cannot mark any of its candidates; a bullet's own --
# --- timestamp never marks itself ------------------------------------------
overturn = run(FIXTURES / "batch-overturn-probe")
require(overturn.returncode == 0, f"overturn-probe must exit 0, got {overturn.returncode}: {overturn.stderr}")
overturn_doc = json_mod.loads(overturn.stdout)
flags = [d["overturned"] for d in overturn_doc["defaults_decisions"]]
require(
    flags == [True, False, False, True, False, False, False, False],
    f"overturn flags mismatch: {flags}",
)

# --- direct unit check of the timestamp-collision rule, isolated from ----
# --- README parsing ---------------------------------------------------------
require(
    ship_debrief.mark_overturned(
        [
            "2026-01-01T00:00:00Z — A",
            "2026-01-01T00:05:00Z — correction of 2026-01-01T00:00:00Z: A retracted",
        ]
    )
    == [True, False],
    "a single unambiguous timestamp reference must mark the earlier decision, not the note",
)
require(
    ship_debrief.mark_overturned(
        [
            "2026-01-01T00:00:00Z — A",
            "2026-01-01T00:00:00Z — B (same timestamp as A)",
            "2026-01-01T00:10:00Z — overturn 2026-01-01T00:00:00Z",
        ]
    )
    == [False, False, False],
    "a timestamp shared by two earlier decisions must mark neither",
)

# --- finding #9: malformed JSON exits 2 with a one-line reason, never a --
# --- raw traceback -----------------------------------------------------------
import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    receipt_dir = Path(tmp) / "receipt"
    receipt_dir.mkdir()
    (receipt_dir / "close-receipt.json").write_text("{not valid json", encoding="utf-8")
    malformed = run(Path(tmp))
    require(malformed.returncode == 2, f"malformed close receipt must exit 2, got {malformed.returncode}")
    require("Traceback" not in malformed.stderr, f"malformed JSON leaked a traceback: {malformed.stderr!r}")

print("ship-debrief test: all checks passed")
