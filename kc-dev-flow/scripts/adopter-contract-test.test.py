#!/usr/bin/env python3
"""Process-level contract test for adopter-contract-test.py. Drives the checker
as a subprocess against a checked-in conforming fixture adopter and three
separately mutated copies of it, asserting exit code and that the failure
message names the specific row, block, or body that diverged -- a fixture-only
unit test would not catch a checker that reads the wrong file or crashes
before reaching its own checks."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKER = ROOT / "adopter-contract-test.py"
CONFORMING = ROOT / "fixtures" / "adopter-contract-test" / "conforming"
PACKAGE_ROOT = ROOT.parent


def run_checker(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--repo", str(repo), "--package-root", str(PACKAGE_ROOT)],
        text=True,
        capture_output=True,
    )


def make_mutant(tmp_path: Path, name: str, mutate) -> Path:
    mutant = tmp_path / name
    shutil.copytree(CONFORMING, mutant)
    mutate(mutant)
    return mutant


failures: list[str] = []

import tempfile

with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)

    # Conforming fixture: exit 0.
    result = run_checker(CONFORMING)
    if result.returncode != 0:
        failures.append(
            f"conforming fixture: expected exit 0, got {result.returncode} "
            f"(stdout={result.stdout!r} stderr={result.stderr!r})"
        )

    # Mutation 1: a marked Local Profile row is edited (schema value corrupted).
    def mutate_row(mutant: Path) -> None:
        readme = mutant / "docs" / "dev" / "README.md"
        text = readme.read_text(encoding="utf-8")
        text = text.replace("kc-dev-flow-local-profile/v1", "kc-dev-flow-local-profile/v2")
        readme.write_text(text, encoding="utf-8")

    row_mutant = make_mutant(tmp_path, "mutant-row", mutate_row)
    row_result = run_checker(row_mutant)
    if row_result.returncode == 0:
        failures.append("row mutation: expected non-zero exit, got 0")
    elif "LOCAL_PROFILE" not in row_result.stderr:
        failures.append(f"row mutation: exit {row_result.returncode} but stderr did not name the row: {row_result.stderr!r}")

    # Mutation 2: the _mods/pr-merge.md extension block diverges from
    # references/pr-merge-extension.md.
    def mutate_block(mutant: Path) -> None:
        mod = mutant / "docs" / "dev" / "_mods" / "pr-merge.md"
        text = mod.read_text(encoding="utf-8")
        marker = "<!-- kc-dev-flow runtime extension:start -->\n"
        start = text.index(marker) + len(marker)
        text = text[:start] + "MUTATED EXTENSION LINE\n" + text[start:]
        mod.write_text(text, encoding="utf-8")

    block_mutant = make_mutant(tmp_path, "mutant-block", mutate_block)
    block_result = run_checker(block_mutant)
    if block_result.returncode == 0:
        failures.append("block mutation: expected non-zero exit, got 0")
    elif "PR_MERGE_BLOCK" not in block_result.stderr:
        failures.append(f"block mutation: exit {block_result.returncode} but stderr did not name the block: {block_result.stderr!r}")

    # Mutation 3: the released body (before the extension marker) diverges from
    # its per-mod-version pin.
    def mutate_body(mutant: Path) -> None:
        mod = mutant / "docs" / "dev" / "_mods" / "pr-merge.md"
        text = mod.read_text(encoding="utf-8")
        marker = "<!-- kc-dev-flow runtime extension:start -->\n"
        head, _, tail = text.partition(marker)
        head = head.replace("# PR Merge", "# PR Merge (mutated)", 1)
        mod.write_text(head + marker + tail, encoding="utf-8")

    body_mutant = make_mutant(tmp_path, "mutant-body", mutate_body)
    body_result = run_checker(body_mutant)
    if body_result.returncode == 0:
        failures.append("body mutation: expected non-zero exit, got 0")
    elif "PR_MERGE_BODY" not in body_result.stderr:
        failures.append(f"body mutation: exit {body_result.returncode} but stderr did not name the body: {body_result.stderr!r}")

    # Mutation 4 (leftover copy): drop a byte-identical canonical resource copy
    # under the adopter's docs/dev tree.
    def mutate_leftover(mutant: Path) -> None:
        canonical = PACKAGE_ROOT / "references" / "kernel.md"
        target = mutant / "docs" / "dev" / "kernel.md"
        target.write_bytes(canonical.read_bytes())

    leftover_mutant = make_mutant(tmp_path, "mutant-leftover", mutate_leftover)
    leftover_result = run_checker(leftover_mutant)
    if leftover_result.returncode == 0:
        failures.append("leftover-copy mutation: expected non-zero exit, got 0")
    elif "LEFTOVER_COPY" not in leftover_result.stderr:
        failures.append(
            f"leftover-copy mutation: exit {leftover_result.returncode} but stderr did not name the leftover: {leftover_result.stderr!r}"
        )

if failures:
    raise SystemExit("adopter-contract-test:FAIL\n" + "\n".join(failures))
print("adopter-contract-test:PASS (1 conforming fixture + 4 mutation cases)")
