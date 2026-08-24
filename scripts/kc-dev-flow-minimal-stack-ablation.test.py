#!/usr/bin/env python3
"""Prove the kc-dev-flow minimal profile stack fails without each guard."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = Path("scripts/kc-dev-flow-multi-profile-gate.py")
LOADER = Path("kc-dev-flow/scripts/profile-contract-loader.py")
LOADER_TEST = Path("kc-dev-flow/scripts/profile-contract-loader.test.py")
CONTRACT_TEST = Path("scripts/kc-dev-flow-contract-test.py")


class AblationError(RuntimeError):
    """A required mutant survived or the test fixture was invalid."""


def replace_once(path: Path, before: str, after: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(before)
    if count != 1:
        raise AblationError(f"expected one mutation anchor in {path}, found {count}")
    path.write_text(text.replace(before, after, 1), encoding="utf-8")


def copy_gate_fixture(destination: Path) -> None:
    (destination / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / GATE, destination / GATE)
    shutil.copytree(ROOT / "kc-dev-flow", destination / "kc-dev-flow")


def copy_repository_fixture(destination: Path) -> None:
    tracked = {
        encoded
        for encoded in subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT
        ).split(b"\0")
        if encoded
    }
    # The runner must be able to prove itself before its first commit too.
    tracked.add(os.fsencode(Path(__file__).resolve().relative_to(ROOT)))
    for encoded in tracked:
        relative = Path(os.fsdecode(encoded))
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, target)


def execute(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=os.environ.copy(),
        text=True,
        capture_output=True,
        timeout=180,
    )


def reject(name: str, completed: subprocess.CompletedProcess[str], evidence: str) -> None:
    output = completed.stdout + completed.stderr
    if completed.returncode == 0:
        raise AblationError(f"{name} mutant survived")
    if evidence not in output:
        raise AblationError(
            f"{name} failed for the wrong reason; expected {evidence!r}:\n{output}"
        )
    print(f"{name}: REJECTED")


def run_gate_mutant(name: str, mutate, evidence: str) -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_gate_fixture(fixture)
        gate = fixture / GATE
        mutate(fixture)
        reject(name, execute([sys.executable, str(gate), "--json"], fixture), evidence)


def missing_pilot(fixture: Path) -> None:
    replace_once(
        fixture / GATE,
        "        for profile in sorted(states):\n",
        "        for profile in sorted(states):\n"
        "            if profile == \"pilot-product-slice\":\n"
        "                continue\n",
    )


def permit_poc_ideation(fixture: Path) -> None:
    replace_once(
        fixture / LOADER,
        '    "poc-exploration": {\n'
        '        "implementation": ("build", "validation"),\n',
        '    "poc-exploration": {\n'
        '        "ideation": ("build", "implementation"),\n'
        '        "implementation": ("build", "validation"),\n',
    )


def broaden_readiness_query(fixture: Path) -> None:
    replace_once(
        fixture / GATE,
        '            "--where", "sprint-readiness=ready",\n',
        '            "--where", "sprint-readiness!=defer",\n',
    )


def skip_pilot_terminalization(fixture: Path) -> None:
    replace_once(
        fixture / GATE,
        "        for path in items.values():\n"
        "            terminalize(spacedock, workflow, path.stem)\n"
        "        remaining = run(\n",
        "        for path in items.values():\n"
        "            if path != items[\"pilot-product-slice\"]:\n"
        "                terminalize(spacedock, workflow, path.stem)\n"
        "        remaining = run(\n",
    )


def exceed_stage_ceiling(fixture: Path) -> None:
    contracts = fixture / "kc-dev-flow/references"
    tree_bytes = sum(path.stat().st_size for path in contracts.rglob("*.md"))
    path = contracts / "profiles/poc-exploration/build.md"
    with path.open("ab") as contract:
        contract.write(b"X" * tree_bytes)


def route_totals(contracts: Path) -> dict[str, int]:
    loader_path = contracts.parent / "scripts/profile-contract-loader.py"
    spec = importlib.util.spec_from_file_location("ablation_loader", loader_path)
    if spec is None or spec.loader is None:
        raise AblationError(f"cannot import {loader_path}")
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    kernel = (contracts / "kernel.md").stat().st_size
    totals: dict[str, int] = {}
    for profile, route in loader.ROUTES.items():
        base = (contracts / "profiles" / profile / "base.md").stat().st_size
        totals[profile] = sum(
            kernel + base + (contracts / "profiles" / profile / f"{logical}.md").stat().st_size
            for logical, _next in route.values()
        )
    return totals


def load_gate(path: Path):
    spec = importlib.util.spec_from_file_location("ablation_gate", path)
    if spec is None or spec.loader is None:
        raise AblationError(f"cannot import {path}")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    return gate


def make_poc_not_lightest(fixture: Path) -> None:
    contracts = fixture / "kc-dev-flow/references"
    totals = route_totals(contracts)
    gate = load_gate(fixture / GATE)
    delta = totals["pilot-product-slice"] - totals["poc-exploration"]
    addition = delta // 2 + 1
    tree_after = (
        sum(path.stat().st_size for path in contracts.rglob("*.md")) + 2 * addition
    )
    kernel = (contracts / "kernel.md").stat().st_size
    base = (contracts / "profiles/poc-exploration/base.md").stat().st_size
    for name in ("build.md", "prove.md"):
        path = contracts / "profiles/poc-exploration" / name
        if (
            kernel + base + path.stat().st_size + addition
            > tree_after * gate.STAGE_LOAD_CEILING
        ):
            raise AblationError(
                "cannot isolate the POC-lightest mutant without crossing the stage ceiling"
            )
        with path.open("ab") as contract:
            contract.write(b"X" * addition)


def run_scheduling_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        shutil.copytree(ROOT / "kc-dev-flow", fixture / "kc-dev-flow")
        replace_once(
            fixture / LOADER,
            "    if workflow_stage == first_workflow_stage:\n",
            "    if False and workflow_stage == first_workflow_stage:\n",
        )
        reject(
            "first-stage-scheduling-guard-disabled",
            execute([sys.executable, str(fixture / LOADER_TEST)], fixture),
            "first working stage accepted an item with no scheduled sprint",
        )


def run_release_state_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        workflow = fixture / "docs/dev/README.md"
        replace_once(
            workflow,
            "    - name: done\n      terminal: true\n",
            "    - name: release\n      gate: true\n"
            "    - name: done\n      terminal: true\n",
        )
        contract_test = fixture / CONTRACT_TEST
        replace_once(
            contract_test,
            'expected_stage_order = ["backlog", "ideation", "implementation", "validation", "done"]\n',
            'expected_stage_order = ["backlog", "ideation", "implementation", "validation", "release", "done"]\n',
        )
        reject(
            "release-state-restored",
            execute([sys.executable, str(contract_test)], fixture),
            "would strand",
        )


def main() -> int:
    baseline = execute([sys.executable, str(ROOT / GATE), "--json"], ROOT)
    if baseline.returncode != 0:
        raise AblationError(f"baseline gate failed:\n{baseline.stdout}{baseline.stderr}")
    json.loads(baseline.stdout)
    print("baseline: PASS")

    run_gate_mutant(
        "missing-pilot-item",
        missing_pilot,
        "fixture did not create one live item for every declared profile",
    )
    run_gate_mutant(
        "poc-owns-pilot-state",
        permit_poc_ideation,
        "loaded a contract at off-route state ideation",
    )
    run_gate_mutant(
        "broad-readiness-query",
        broaden_readiness_query,
        "blank readiness entered the drivable set",
    )
    run_gate_mutant(
        "pilot-terminalization-skipped",
        skip_pilot_terminalization,
        "pilot-item is still active after its route completed",
    )
    run_gate_mutant(
        "oversized-stage-load",
        exceed_stage_ceiling,
        f"over the {load_gate(ROOT / GATE).STAGE_LOAD_CEILING:.0%} share",
    )
    run_gate_mutant(
        "poc-no-longer-lightest",
        make_poc_not_lightest,
        "poc-exploration no longer loads less than pilot-product-slice",
    )
    run_scheduling_mutant()
    run_release_state_mutant()
    print("kc-dev-flow minimal-stack ablation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AblationError, subprocess.TimeoutExpired) as error:
        print(f"kc-dev-flow minimal-stack ablation: FAIL\n{error}", file=sys.stderr)
        raise SystemExit(1)
