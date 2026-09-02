#!/usr/bin/env python3
"""Compatibility entrypoint until the packaged Linear admission is released."""

from __future__ import annotations

import runpy
from pathlib import Path


PACKAGE_ENTRYPOINT = (
    Path(__file__).resolve().parents[2]
    / "kc-dev-flow"
    / "scripts"
    / "linear-admission.py"
)


if __name__ == "__main__":
    runpy.run_path(str(PACKAGE_ENTRYPOINT), run_name="__main__")
