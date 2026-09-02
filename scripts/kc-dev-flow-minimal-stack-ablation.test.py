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
RECONCILE = Path("kc-dev-flow/scripts/engage-reconcile.py")
RECONCILE_TEST = Path("kc-dev-flow/scripts/engage-reconcile.test.py")
CONTRACT_TEST = Path("scripts/kc-dev-flow-contract-test.py")
LINEAR_ADMISSION = Path("kc-dev-flow/scripts/linear-admission.py")


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
    (destination / "docs/dev").mkdir(parents=True)
    shutil.copy2(ROOT / "docs/dev/README.md", destination / "docs/dev/README.md")


def copy_repository_fixture(destination: Path) -> None:
    tracked = {
        encoded
        for encoded in subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT
        ).split(b"\0")
        if encoded
    }
    # The runner and a newly packaged runtime must be provable before their
    # first commit too.
    tracked.add(os.fsencode(Path(__file__).resolve().relative_to(ROOT)))
    tracked.add(os.fsencode(LINEAR_ADMISSION))
    for encoded in tracked:
        relative = Path(os.fsdecode(encoded))
        source = ROOT / relative
        # The candidate may delete a tracked path; its fixture must not resurrect it.
        if not source.exists() and not source.is_symlink():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, target)
    subprocess.run(["git", "init"], cwd=destination, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=destination, check=True)
    subprocess.run(
        ["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.test",
         "commit", "-m", "seed fixture"],
        cwd=destination, check=True, capture_output=True,
    )


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
    contracts = fixture / "kc-dev-flow/references"
    totals = route_totals(contracts)
    poc_total = totals["poc-exploration"]
    for profile in ("pilot-product-slice", "production"):
        if totals[profile] <= poc_total:
            path = contracts / "profiles" / profile / "build.md"
            with path.open("ab") as contract:
                contract.write(b"X" * (poc_total - totals[profile] + 1))


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


def exceed_static_input_ceiling(fixture: Path) -> None:
    contracts = fixture / "kc-dev-flow/references"
    ceiling = load_gate(fixture / GATE).STATIC_INSTRUCTION_CEILING_BYTES
    path = contracts / "profiles/poc-exploration/build.md"
    with path.open("ab") as contract:
        contract.write(b"X" * ceiling)


def hide_oversized_local_profile_behind_fenced_heading(fixture: Path) -> None:
    workflow = fixture / "docs/dev/README.md"
    ceiling = load_gate(fixture / GATE).STATIC_INSTRUCTION_CEILING_BYTES
    replace_once(
        workflow,
        "\n<!-- kc-dev-flow-static-local-profile:end -->\n",
        "\n```markdown\n## Example heading\n```\n\n"
        + ("X" * ceiling)
        + "\n\n<!-- kc-dev-flow-static-local-profile:end -->\n",
    )


def hide_oversized_local_profile_behind_mixed_fence_closer(fixture: Path) -> None:
    workflow = fixture / "docs/dev/README.md"
    ceiling = load_gate(fixture / GATE).STATIC_INSTRUCTION_CEILING_BYTES
    replace_once(
        workflow,
        "\n<!-- kc-dev-flow-static-local-profile:end -->\n",
        "\n```markdown\n```~\n## Example heading\n"
        + ("X" * ceiling)
        + "\n```\n\n<!-- kc-dev-flow-static-local-profile:end -->\n",
    )


def hide_oversized_local_profile_behind_html_comment(fixture: Path) -> None:
    workflow = fixture / "docs/dev/README.md"
    ceiling = load_gate(fixture / GATE).STATIC_INSTRUCTION_CEILING_BYTES
    replace_once(
        workflow,
        "\n<!-- kc-dev-flow-static-local-profile:end -->\n",
        "\n<!--\n## Example heading\n-->\n"
        + ("X" * ceiling)
        + "\n\n<!-- kc-dev-flow-static-local-profile:end -->\n",
    )


def replace_local_profile_with_frontmatter_comment(fixture: Path) -> None:
    workflow = fixture / "docs/dev/README.md"
    text = workflow.read_text(encoding="utf-8")
    start = text.index("<!-- kc-dev-flow-static-local-profile:start -->")
    end_marker = "<!-- kc-dev-flow-static-local-profile:end -->"
    end = text.index(end_marker) + len(end_marker)
    text = text[:start] + text[end:]
    workflow.write_text(
        text.replace("---\n", "---\n## Local Profile\n", 1),
        encoding="utf-8",
    )


def convert_workflow_to_crlf(fixture: Path) -> None:
    workflow = fixture / "docs/dev/README.md"
    raw = workflow.read_bytes()
    if b"\r" in raw:
        raise AblationError("baseline workflow already contains CR bytes")
    workflow.write_bytes(raw.replace(b"\n", b"\r\n"))


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
    replace_once(
        fixture / GATE,
        "STATIC_INSTRUCTION_CEILING_BYTES = 40_000",
        "STATIC_INSTRUCTION_CEILING_BYTES = 1_000_000",
    )
    delta = totals["pilot-product-slice"] - totals["poc-exploration"]
    addition = delta // 2 + 1
    for name in ("build.md", "prove.md"):
        path = contracts / "profiles/poc-exploration" / name
        with path.open("ab") as contract:
            contract.write(b"X" * addition)


def run_static_accounting_mutant(name: str, anchor: str) -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        replace_once(fixture / GATE, anchor, "")
        reject(
            name,
            execute(
                [sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"],
                fixture,
            ),
            "release gate static input account omits continue-dev-flow or Local Profile",
        )


def run_rendered_payload_omission_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        for relative in (LOADER,):
            replace_once(
                fixture / relative,
                '    for item in contract["loaded"]:\n        chunks.append(\n',
                '    for item in contract["loaded"]:\n'
                '        if item["path"] == "kernel.md" or item["path"].endswith("/base.md"):\n'
                "            continue\n"
                "        chunks.append(\n",
            )
        reject(
            "rendered-kernel-and-base-omitted",
            execute(
                [sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"],
                fixture,
            ),
            "default loader output omits selected payload: kernel.md",
        )


def run_production_payload_omission_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        for relative in (LOADER,):
            replace_once(
                fixture / relative,
                '    for item in contract["loaded"]:\n        chunks.append(\n',
                '    for item in contract["loaded"]:\n'
                '        if item["path"].startswith("profiles/production/"):\n'
                "            continue\n"
                "        chunks.append(\n",
            )
        reject(
            "rendered-production-payloads-omitted",
            execute(
                [sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"],
                fixture,
            ),
            "default loader output omits selected payload: profiles/production/base.md",
        )


def run_routing_header_omission_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        for relative in (LOADER,):
            replace_once(
                fixture / relative,
                '            "next_workflow_stage",\n',
                "",
            )
        reject(
            "rendered-routing-header-omitted",
            execute(
                [sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"],
                fixture,
            ),
            "default loader output header differs: poc-exploration/implementation",
        )


def run_rendered_payload_order_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        for relative in (LOADER,):
            replace_once(
                fixture / relative,
                '    for item in contract["loaded"]:\n',
                '    for item in reversed(contract["loaded"]):\n',
            )
        reject(
            "rendered-payload-order-reversed",
            execute(
                [sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"],
                fixture,
            ),
            "default loader output order or framing differs: poc-exploration/implementation",
        )


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


def run_poc_entry_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        shutil.copytree(ROOT / "kc-dev-flow", fixture / "kc-dev-flow")
        replace_once(
            fixture / LOADER,
            'POC_FIELDS = ("poc_decision", "poc_falsifier", "poc_budget", "poc_stop_when")\n',
            'POC_FIELDS = ("poc_falsifier", "poc_budget", "poc_stop_when")\n',
        )
        reject(
            "poc-entry-fields-disabled",
            execute([sys.executable, str(fixture / LOADER_TEST)], fixture),
            "v3 POC accepted a missing poc_decision",
        )


def run_reconcile_exit_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        shutil.copytree(ROOT / "kc-dev-flow", fixture / "kc-dev-flow")
        replace_once(
            fixture / RECONCILE,
            '    return 1 if result["status"] == "delta" else 0\n',
            "    return 0\n",
        )
        reject(
            "reconcile-delta-exit-disabled",
            execute([sys.executable, str(fixture / RECONCILE_TEST)], fixture),
            "membership delta returned 0",
        )


def run_reconcile_wiring_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        continuation = fixture / "kc-dev-flow/skills/continue-dev-flow/SKILL.md"
        replace_once(
            continuation,
            "7. Invoke the installed loader's sibling read-only engage comparator only in\n"
            "   the provider-backed branch. The activated skill supplies both package paths\n",
            "7. Continue without invoking the engage comparator.\n",
        )
        reject(
            "reconcile-wiring-removed",
            execute([sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"], fixture),
            "continuation planning disambiguation omits: Invoke the installed loader's sibling read-only engage comparator only in the provider-backed branch.",
        )


def run_reconcile_clean_output_wiring_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        continuation = fixture / "kc-dev-flow/skills/continue-dev-flow/SKILL.md"
        replace_once(
            continuation,
            "   Exit `0` continues only when stdout parses as one JSON object with\n"
            "   `status: clean` and empty `added`, `removed`, `changed`, and `moved` arrays.\n",
            "   Exit `0` continues without validating stdout.\n",
        )
        reject(
            "reconcile-clean-output-wiring-removed",
            execute([sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"], fixture),
            "continuation omits provider engage behavior: stdout parses as one JSON object with `status: clean`",
        )


def run_manual_contract_mutant(
    name: str, relative: str, before: str, after: str, evidence: str
) -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        replace_once(fixture / relative, before, after)
        reject(
            name,
            execute([sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"], fixture),
            evidence,
        )


def run_loader_admission_mutant(
    name: str, before: str, after: str, evidence: str
) -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        shutil.copytree(ROOT / "kc-dev-flow", fixture / "kc-dev-flow")
        replace_once(fixture / LOADER, before, after)
        reject(
            name,
            execute([sys.executable, str(fixture / LOADER_TEST)], fixture),
            evidence,
        )


def run_loader_multi_mutant(
    name: str, mutations: list[tuple[str, str]], evidence: str
) -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        shutil.copytree(ROOT / "kc-dev-flow", fixture / "kc-dev-flow")
        for before, after in mutations:
            replace_once(fixture / LOADER, before, after)
        reject(
            name,
            execute([sys.executable, str(fixture / LOADER_TEST)], fixture),
            evidence,
        )


def run_kernel_contract_mutant(
    name: str, before: str, after: str, evidence: str
) -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        for relative in ("kc-dev-flow/references/kernel.md",):
            replace_once(fixture / relative, before, after)
        reject(
            name,
            execute([sys.executable, str(fixture / CONTRACT_TEST), "--ablation-check"], fixture),
            evidence,
        )


def run_missing_close_guard_mutant() -> None:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-ablation-") as temporary:
        fixture = Path(temporary)
        copy_repository_fixture(fixture)
        (fixture / "kc-dev-flow/scripts/poc-close-guard.py").unlink()
        reject(
            "poc-close-guard-removed",
            execute([sys.executable, str(fixture / CONTRACT_TEST)], fixture),
            "missing kc-dev-flow/scripts/poc-close-guard.py",
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
            execute([sys.executable, str(contract_test), "--ablation-check"], fixture),
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
        "oversized-static-input",
        exceed_static_input_ceiling,
        "over the absolute 40000-byte static instruction ceiling",
    )
    run_gate_mutant(
        "fenced-heading-local-profile-bypass",
        hide_oversized_local_profile_behind_fenced_heading,
        "over the absolute 40000-byte static instruction ceiling",
    )
    run_gate_mutant(
        "mixed-fence-closer-local-profile-bypass",
        hide_oversized_local_profile_behind_mixed_fence_closer,
        "over the absolute 40000-byte static instruction ceiling",
    )
    run_gate_mutant(
        "html-comment-local-profile-bypass",
        hide_oversized_local_profile_behind_html_comment,
        "over the absolute 40000-byte static instruction ceiling",
    )
    run_gate_mutant(
        "frontmatter-comment-local-profile-substitute",
        replace_local_profile_with_frontmatter_comment,
        "workflow must contain one static Local Profile start marker",
    )
    run_gate_mutant(
        "crlf-static-input-undercount",
        convert_workflow_to_crlf,
        "workflow must use LF-only newlines",
    )
    run_static_accounting_mutant(
        "continuation-input-accounting-removed",
        '        "kc-dev-flow/skills/continue-dev-flow/SKILL.md": continuation.stat().st_size,\n',
    )
    run_static_accounting_mutant(
        "local-profile-input-accounting-removed",
        '        "docs/dev/README.md#frontmatter+Local Profile": workflow_context_bytes(workflow),\n',
    )
    run_rendered_payload_omission_mutant()
    run_production_payload_omission_mutant()
    run_routing_header_omission_mutant()
    run_rendered_payload_order_mutant()
    run_manual_contract_mutant(
        "installed-skill-anchor-removed",
        "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
        "Resolve `../../scripts/profile-contract-loader.py` from this activated skill.\n",
        "Resolve a profile loader from the current host.\n",
        "continuation is missing: from this activated skill",
    )
    run_manual_contract_mutant(
        "manifest-inventory-removed",
        "kc-dev-flow/contract-manifest.json",
        '    "references/kernel.md",\n',
        "",
        "installed manifest does not bind the exact canonical runtime surface",
    )
    run_manual_contract_mutant(
        "local-interface-binding-removed",
        "docs/dev/README.md",
        "| Installed contract interface | `kc-dev-flow-local-profile/v1` |\n",
        "",
        "self-adoption is missing: | Installed contract interface | `kc-dev-flow-local-profile/v1` |",
    )
    run_loader_admission_mutant(
        "installed-digest-disabled",
        "        digest.update(raw)\n",
        "        digest.update(b\"\")\n",
        "compatible next-stage upgrade did not bind the new package",
    )
    run_loader_admission_mutant(
        "active-stage-equality-disabled",
        "        if any(previous.get(key) != value for key, value in exact.items()):\n",
        "        if False:\n",
        "active stage accepted changed installed version or bytes",
    )
    run_loader_multi_mutant(
        "local-interface-compatibility-disabled",
        [
            (
                '    if rows["Installed contract interface"].strip("`") != expected:\n',
                '    if False and rows["Installed contract interface"].strip("`") != expected:\n',
            ),
            (
                '            previous.get("local_profile_interface") != interface\n',
                '            False and previous.get("local_profile_interface") != interface\n',
            ),
        ],
        "incompatible boundary did not fail closed",
    )
    run_loader_admission_mutant(
        "preservation-check-disabled",
        '    contract["local_profile"] = local_profile\n',
        '    local_profile_path.write_text(local_profile_path.read_text(encoding="utf-8") + "MUTATION\\n", encoding="utf-8")\n'
        '    contract["local_profile"] = local_profile\n',
        "installed loading changed README policy, local-mod bytes/mode, or unrelated state",
    )
    run_manual_contract_mutant(
        "marked-local-profile-read-contract-removed",
        "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
        "   marked block; never infer boundaries from headings or open the full README.\n",
        "   infer its boundary from headings in the full workflow README.\n",
        "continuation is missing: Read only its frontmatter and marked block",
    )
    run_manual_contract_mutant(
        "adopter-local-profile-marker-removed",
        "kc-dev-flow/skills/adopt-dev-flow/SKILL.md",
        "<!-- kc-dev-flow-static-local-profile:start -->",
        "<!-- local-profile-start-removed -->",
        "adopter omits static Local Profile marker: <!-- kc-dev-flow-static-local-profile:start -->",
    )
    run_manual_contract_mutant(
        "migration-3x-local-profile-marker-removed",
        "kc-dev-flow/MIGRATION.md",
        "   `<!-- kc-dev-flow-static-local-profile:start -->` and one end marker\n",
        "   `<!-- local-profile-start-removed -->` and one end marker\n",
        "3.x migration omits static Local Profile marker: <!-- kc-dev-flow-static-local-profile:start -->",
    )
    run_manual_contract_mutant(
        "migration-2x-local-profile-marker-removed",
        "kc-dev-flow/MIGRATION.md",
        "   exactly one start marker `<!-- kc-dev-flow-static-local-profile:start -->`\n",
        "   exactly one start marker `<!-- local-profile-start-removed -->`\n",
        "2.x migration omits static Local Profile marker: <!-- kc-dev-flow-static-local-profile:start -->",
    )
    run_manual_contract_mutant(
        "migration-3x-standalone-fields-removed",
        "kc-dev-flow/MIGRATION.md",
        "   `planning-outcome` values. For standalone work, leave `source`,\n"
        "   `planning-window`, and `planning-outcome` absent and use the Captain-approved\n"
        "   committed brief as planning authority. Both paths assign a non-empty local\n",
        "   `planning-outcome` values. Record provider planning fields for every item.\n"
        "   Both paths assign a non-empty local\n",
        "3.x migration omits standalone planning branch: For standalone work, leave `source`, `planning-window`, and `planning-outcome` absent",
    )
    run_manual_contract_mutant(
        "migration-3x-standalone-reconcile-removed",
        "kc-dev-flow/MIGRATION.md",
        "   adapter and the installed comparator with that exact source, window, and\n"
        "   outcome. Standalone work skips\n"
        "   both and continues from the Captain-approved committed brief. For the\n",
        "   adapter and the installed comparator with that exact source, window, and\n"
        "   outcome. All work runs the\n"
        "   comparator before continuing. For the\n",
        "3.x migration omits standalone planning branch: Standalone work skips both and continues from the Captain-approved committed brief",
    )
    run_gate_mutant(
        "poc-no-longer-lightest",
        make_poc_not_lightest,
        "poc-exploration no longer loads less than pilot-product-slice",
    )
    run_scheduling_mutant()
    run_poc_entry_mutant()
    run_reconcile_exit_mutant()
    run_reconcile_wiring_mutant()
    run_reconcile_clean_output_wiring_mutant()
    run_loader_admission_mutant(
        "canonical-admission-heading-removed",
        '    "Acceptance criteria",\n',
        '    "Acceptance evidence",\n',
        "Development Brief must contain exactly one Acceptance evidence",
    )
    run_loader_admission_mutant(
        "dual-section-refusal-removed",
        '    if re.search(r"^## Acceptance evidence\\s*$", text, re.MULTILINE):\n',
        '    if False and re.search(r"^## Acceptance evidence\\s*$", text, re.MULTILINE):\n',
        "admission accepted dual-section-admission",
    )
    run_loader_admission_mutant(
        "ac-order-check-removed",
        "        or [int(match.group(1)) for match in criteria if match] != list(\n",
        "        or False and [int(match.group(1)) for match in criteria if match] != list(\n",
        "admission accepted non-ascending-ac",
    )
    run_loader_admission_mutant(
        "default-loader-revalidation-restored",
        '        if validate_admission\n        else None\n',
        '        if True\n        else None\n',
        "new admission cannot contain Acceptance evidence with canonical criteria",
    )
    run_loader_admission_mutant(
        "partial-planning-receipt-accepted",
        "    if any(present) and not all(present):\n",
        "    if False:\n",
        "Planning Receipt presence mask 1 had wrong admission result",
    )
    run_loader_admission_mutant(
        "omitted-planning-receipt-rejected",
        "        if len(matches) > 1:\n",
        "        if len(matches) != 1:\n",
        "standalone admission with an omitted Planning Receipt was rejected",
    )
    run_manual_contract_mutant(
        "linear-reader-removed",
        str(LINEAR_ADMISSION),
        "        request = urllib.request.Request(\n",
        '        raise AdmissionError("reader removed")\n        request = urllib.request.Request(\n',
        "clean Linear admission failed",
    )
    run_manual_contract_mutant(
        "workspace-auth-guard-removed",
        str(LINEAR_ADMISSION),
        "        if not key or not workspace_id:\n",
        "        if False:\n",
        "missing-workspace emitted an envelope",
    )
    run_manual_contract_mutant(
        "linear-workspace-binding-removed",
        str(LINEAR_ADMISSION),
        '        if not isinstance(organization, dict) or organization.get("urlKey") != args.linear_workspace:\n',
        "        if False:\n",
        "wrong-org emitted an envelope",
    )
    run_manual_contract_mutant(
        "admission-loader-invocation-removed",
        str(LINEAR_ADMISSION),
        '             "--validate-admission"],\n',
        '             "--invalid-admission-mode"],\n',
        'Linear admission omits retained mechanism: "--validate-admission"',
    )
    run_manual_contract_mutant(
        "state-binding-final-check-removed",
        str(LINEAR_ADMISSION),
        "        if final_head != args.state_revision or final_status or work_item.read_bytes() != committed:\n",
        "        if False:\n",
        "changing work-item bytes emitted an envelope",
    )
    run_manual_contract_mutant(
        "comparator-payload-stop-removed",
        str(LINEAR_ADMISSION),
        '        if compared.returncode != 0 or reconciliation.get("status") != "clean" or not empty:\n',
        "        if False:\n",
        'Linear admission omits retained mechanism: "status") != "clean"',
    )
    run_manual_contract_mutant(
        "success-only-envelope-stop-removed",
        str(LINEAR_ADMISSION),
        '        print(f"linear admission: {exc}", file=sys.stderr)\n',
        '        print(f"linear admission: {exc}")\n',
        "missing-key emitted an envelope",
    )
    run_kernel_contract_mutant(
        "required-development-brief-removed",
        "A Development Brief is required",
        "A Development Brief is optional",
        "kernel omits brief boundary: Development Brief is required",
    )
    run_kernel_contract_mutant(
        "standalone-path-removed",
        "A Planning Receipt is optional",
        "A Planning Receipt is required",
        "kernel omits brief boundary: Planning Receipt is optional",
    )
    run_manual_contract_mutant(
        "partial-receipt-accepted",
        "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
        "report `planning receipt incomplete`",
        "continue with the available planning fields",
        "continuation planning disambiguation omits: report `planning receipt incomplete`",
    )
    run_kernel_contract_mutant(
        "runtime-topology-restored",
        "Runtime adapters own task and execution-context\ncardinality.",
        "Runtime adapters own task and execution-context\ncardinality. one planning item to one SD task and one isolated execution context.",
        "kernel owns runtime topology: one planning item to one SD task and one isolated execution context",
    )
    run_kernel_contract_mutant(
        "runtime-vocabulary-restored",
        "Runtime adapters own task and execution-context\ncardinality.",
        "Runtime adapters own task and execution-context\ncardinality. At admission, each task records the tuple.",
        "kernel owns runtime topology: each task records the tuple",
    )
    run_manual_contract_mutant(
        "execution-scope-replacement-restored",
        "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
        "do not replace the snapshot or\n   candidate",
        "replace the snapshot and continue the\n   candidate",
        "continuation planning disambiguation omits: do not replace the snapshot or candidate",
    )
    run_manual_contract_mutant(
        "release-brief-wrapper-restored",
        "docs/dev/README.md",
        "```markdown\n## The problem\n",
        "```markdown\n## Human-readable release brief\n\n## The problem\n",
        "manual admission Issue body does not start directly with The problem",
    )
    run_manual_contract_mutant(
        "manual-issue-required-fields-removed",
        "docs/dev/README.md",
        "```markdown\n## The problem\n\n## Accepted outcome\n\n## Non-goals\n\n## Acceptance criteria\n\n- **AC-1** <observable condition>\n\n## Route-back conditions\n",
        "```markdown\n## The problem\n",
        "manual admission Issue headings are missing or duplicated",
    )
    run_manual_contract_mutant(
        "poc-route-back-removed",
        "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
        "return the POC outcome to planning",
        "continue directly into delivery",
        "kc-dev-flow/skills/continue-dev-flow/SKILL.md omits the v4 POC contract: return the POC outcome to planning",
    )
    run_missing_close_guard_mutant()
    run_release_state_mutant()
    print("kc-dev-flow minimal-stack ablation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AblationError, subprocess.TimeoutExpired) as error:
        print(f"kc-dev-flow minimal-stack ablation: FAIL\n{error}", file=sys.stderr)
        raise SystemExit(1)
