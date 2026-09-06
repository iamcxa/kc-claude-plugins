#!/usr/bin/env python3
"""Behavior and packaging contract for kc-dev-flow."""

from __future__ import annotations

import ast
import importlib.util
import hashlib
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "kc-dev-flow"
LOCAL_MODS = ROOT / "docs/dev/_mods"
# --ablation-check skips the mechanism sub-suites run() shells out to, so an
# assertion that relies on one of them guards nothing in that mode.
require_ablation_only = sys.argv[1:] == ["--ablation-check"]
if sys.argv[1:] not in ([], ["--ablation-check"]):
    raise SystemExit("usage: kc-dev-flow-contract-test.py [--ablation-check]")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"kc-dev-flow contract: {message}")


def require_production_route(text: str, label: str, full: str) -> None:
    rows = [line for line in text.splitlines() if line.startswith(f"| {label} |") and (full in line or "eligible recovery" in line)]
    require(len(rows) == 1, f"{label} Production route row is missing or ambiguous")
    require(full in rows[0], f"{label} route omits the full Production default")
    require("eligible recovery" in rows[0], f"{label} route omits eligible recovery")


def run(command: list[str], label: str) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    require(
        result.returncode == 0,
        f"{label} failed:\n{result.stdout}{result.stderr}",
    )


def read(relative: str) -> str:
    path = ROOT / relative
    require(path.is_file(), f"missing {relative}")
    return path.read_text(encoding="utf-8")


def skill_name(relative: str) -> str:
    text = read(relative)
    match = re.match(r"---\nname: ([a-z0-9-]+)\ndescription: .+?\n---\n", text, re.DOTALL)
    require(match is not None, f"invalid skill frontmatter: {relative}")
    return match.group(1)


profile_files = {
    "poc-exploration": ("base.md", "build.md", "prove.md"),
    "pilot-product-slice": (
        "base.md",
        "shape.md",
        "build.md",
        "verify-deliver.md",
    ),
    "production": ("base.md", "shape.md", "build.md", "verify.md"),
}
profile_observation_limits = {
    "poc-exploration": ("medium", "high", 600, 0),
    "pilot-product-slice": ("medium", "medium", 900, 1),
    "production": ("medium", "medium", 1200, 1),
}

required = [
    "kc-dev-flow/.claude-plugin/plugin.json",
    "kc-dev-flow/.codex-plugin/plugin.json",
    "kc-dev-flow/plugin.json",
    "kc-dev-flow/plugin.yaml",
    "kc-dev-flow/__init__.py",
    "kc-dev-flow/MIGRATION.md",
    "kc-dev-flow/RATIONALE.md",
    "kc-dev-flow/contract-manifest.json",
    "kc-dev-flow/references/kernel.md",
    "kc-dev-flow/references/reverse-recovery-audit.md",
    "kc-dev-flow/references/journey-slicing.md",
    "kc-dev-flow/references/retained-document-policy.md",
    "kc-dev-flow/references/project-context-maintenance.md",
    "kc-dev-flow/references/delivery-branch-base.md",
    "kc-dev-flow/references/pr-delivery.md",
    "kc-dev-flow/references/roborev-implementation-exit.md",
    "kc-dev-flow/scripts/profile-contract-loader.py",
    "kc-dev-flow/scripts/profile-contract-loader.test.py",
    "kc-dev-flow/scripts/engage-reconcile.py",
    "kc-dev-flow/scripts/engage-reconcile.test.py",
    "kc-dev-flow/scripts/linear-admission.py",
    "kc-dev-flow/scripts/poc-close-guard.py",
    "kc-dev-flow/scripts/poc-close-guard.test.py",
    "kc-dev-flow/scripts/profile-spacedock-route.test.py",
    "kc-dev-flow/scripts/pr-review-handoff.py",
    "kc-dev-flow/scripts/pr-review-handoff.test.py",
    "kc-dev-flow/scripts/surface-map-check.py",
    "kc-dev-flow/skills/adopt-dev-flow/SKILL.md",
    "kc-dev-flow/skills/choose-work-profile/SKILL.md",
    "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
    "kc-dev-flow/skills/chief-engineer/SKILL.md",
    "kc-dev-flow/skills/chief-engineer/agents/openai.yaml",
    "kc-dev-flow/skills/science-officer/SKILL.md",
    "kc-dev-flow/skills/science-officer/agents/openai.yaml",
    "kc-dev-flow/skills/science-officer-em/SKILL.md",
    "kc-dev-flow/skills/science-officer-em/agents/openai.yaml",
    "scripts/kc-dev-flow-minimal-stack-ablation.test.py",
    "scripts/kc-dev-flow-multi-profile-gate.py",
    "scripts/kc-dev-flow-published-tag-smoke.py",
    "scripts/kc-dev-flow-published-tag-smoke.test.py",
    "scripts/roborev-implementation-exit-contract.test.py",
    "scripts/pr-merge-portable-delivery.test.py",
    "docs/plan-flow/plan-lint.py",
    "docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json",
    "scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json",
    "scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json",
]
for relative in required:
    require((ROOT / relative).is_file(), f"missing {relative}")
for retired in [
    "kc-dev-flow/references/work-control-profile.md",
    "docs/dev/_mods/work-control-profile.md",
    # The adopter-to-source improvement transport. Retired for never having run:
    # it needed a human to carry a handoff file between repositories, and no such
    # artifact ever existed in any adopter. Guarded because a file can come back
    # quietly and nothing else would notice.
    "kc-dev-flow/references/improvement-harvesting.md",
    "kc-dev-flow/scripts/improvement-intake.py",
    "kc-dev-flow/scripts/improvement-intake.test.py",
    "kc-dev-flow/skills/promote-dev-flow/SKILL.md",
    "kc-dev-flow/skills/setup-github-project-projection",
    "kc-dev-flow/scripts/project-spacedock-state.test.py",
    "docs/dev/_mods/engage-reconcile.py",
    "scripts/kc-dev-flow/engage-reconcile.py",
    "scripts/kc-dev-flow/linear-admission.py",
    # This blind-evaluation adapter had no caller outside its own test. Keep the
    # retired experiment from silently returning as release or runtime surface.
    "scripts/kc-dev-flow-loader-eval.py",
    "scripts/kc-dev-flow-loader-eval.test.py",
    "scripts/fixtures/kc-dev-flow-loader-eval/q08.json",
]:
    require(not (ROOT / retired).exists(), f"retired control still shipped: {retired}")

script_roles = {
    "runtime": {
        "kc-dev-flow/scripts/profile-contract-loader.py",
        "kc-dev-flow/scripts/engage-reconcile.py",
        "kc-dev-flow/scripts/linear-admission.py",
        "kc-dev-flow/scripts/poc-close-guard.py",
        "kc-dev-flow/scripts/pr-review-handoff.py",
        "kc-dev-flow/scripts/surface-map-check.py",
    },
    "package-test": {
        "kc-dev-flow/scripts/profile-contract-loader.test.py",
        "kc-dev-flow/scripts/engage-reconcile.test.py",
        "kc-dev-flow/scripts/poc-close-guard.test.py",
        "kc-dev-flow/scripts/pr-review-handoff.test.py",
        "kc-dev-flow/scripts/profile-spacedock-route.test.py",
    },
    "release-proof": {
        "scripts/kc-dev-flow-contract-test.py",
        "scripts/kc-dev-flow-minimal-stack-ablation.test.py",
        "scripts/kc-dev-flow-multi-profile-gate.py",
        "scripts/kc-dev-flow-published-tag-smoke.py",
        "scripts/kc-dev-flow-published-tag-smoke.test.py",
    },
}
classified_scripts = set().union(*script_roles.values())
require(
    sum(len(paths) for paths in script_roles.values()) == len(classified_scripts),
    "kc-dev-flow script roles overlap",
)
observed_scripts = {
    path.relative_to(ROOT).as_posix()
    for root in (PLUGIN / "scripts", ROOT / "scripts/kc-dev-flow")
    for path in root.glob("*.py")
} | {
    path.relative_to(ROOT).as_posix()
    for path in (ROOT / "scripts").glob("kc-dev-flow*.py")
}
require(
    observed_scripts == classified_scripts,
    "kc-dev-flow scripts must have exactly one runtime, test, adapter, or release-proof role: "
    f"unclassified={sorted(observed_scripts - classified_scripts)} "
    f"missing={sorted(classified_scripts - observed_scripts)}",
)

documentation_references = [
    {
        "path": "../../retained-document-policy.md",
        "trigger": "retained_document_change",
        "receipt": None,
    },
    {
        "path": "../../project-context-maintenance.md",
        "trigger": "project_context_claim_may_change",
        "receipt": "project_context",
    },
]
roborev_reference = [
    {
        "path": "../../roborev-implementation-exit.md",
        "trigger": "implementation_exit_observation_declared",
        "receipt": None,
    },
]
delivery_references = [
    {
        "path": "../../delivery-branch-base.md",
        "trigger": "delivery_artifact_review",
        "receipt": None,
    },
    {
        "path": "../../pr-delivery.md",
        "trigger": "pr_delivery_selected",
        "receipt": None,
    },
]
conditional_stage_references = {
    ("poc-exploration", "build.md"): roborev_reference
    + delivery_references
    + [
        {
            "path": "../../reverse-recovery-audit.md",
            "trigger": "brownfield_capability_change",
            "receipt": "reverse_recovery",
        }
    ]
    + documentation_references,
    ("poc-exploration", "prove.md"): delivery_references + documentation_references,
    ("pilot-product-slice", "shape.md"): [
        {
            "path": "../../reverse-recovery-audit.md",
            "trigger": "brownfield_capability_change",
            "receipt": "reverse_recovery",
        },
        {
            "path": "../../journey-slicing.md",
            "trigger": "multi_slice_required",
            "receipt": "journey_slices",
        },
    ]
    + documentation_references,
    ("pilot-product-slice", "build.md"): roborev_reference
    + delivery_references
    + documentation_references,
    ("pilot-product-slice", "verify-deliver.md"): delivery_references
    + documentation_references,
    ("production", "shape.md"): [
        {
            "path": "../../reverse-recovery-audit.md",
            "trigger": "brownfield_capability_change",
            "receipt": "reverse_recovery",
        },
        {
            "path": "../../journey-slicing.md",
            "trigger": "multi_slice_required",
            "receipt": "journey_slices",
        },
    ]
    + documentation_references,
    ("production", "build.md"): roborev_reference
    + delivery_references
    + documentation_references,
    ("production", "verify.md"): delivery_references + documentation_references,
}
for profile, names in profile_files.items():
    for name in names:
        require(
            (PLUGIN / "references/profiles" / profile / name).is_file(),
            f"missing profile contract: {profile}/{name}",
        )
        if name != "base.md":
            stage_path = PLUGIN / "references/profiles" / profile / name
            stage_contract = stage_path.read_text(encoding="utf-8")
            require(
                "Working perspective:" in stage_contract and "\nRole:" not in stage_contract,
                f"stage perspective is not a lightweight cue: {profile}/{name}",
            )
            json_blocks = [
                json.loads(block)
                for block in re.findall(r"```json\s*\n(.*?)```", stage_contract, re.DOTALL)
            ]
            conditional = [
                block
                for block in json_blocks
                if block.get("schema") == "kc-dev-flow-conditional-references/v1"
            ]
            expected_references = conditional_stage_references.get((profile, name), [])
            require(
                len(conditional) == (1 if expected_references else 0)
                and (not conditional or conditional[0].get("references") == expected_references),
                f"wrong conditional references: {profile}/{name} {conditional}",
            )
            for reference in expected_references:
                resolved = (stage_path.parent / reference["path"]).resolve()
                require(
                    resolved.is_relative_to(PLUGIN / "references")
                    and resolved.is_file(),
                    f"unresolved conditional reference: {profile}/{name} {reference}",
                )
            require(
                "work-control-profile" not in stage_contract,
                f"retired work control leaked into stage: {profile}/{name}",
            )
            if name == "build.md":
                typed = [
                    item
                    for item in json_blocks
                    if item.get("schema") == "kc-dev-flow-observation/v1"
                ]
                require(len(typed) == 1, f"wrong observation count: {profile}")
                observation = typed[0]
                require(
                    (
                        observation.get("reasoning"),
                        observation.get("minimum_severity"),
                        observation.get("live_batch_timeout_seconds"),
                        observation.get("repair_confirmation_cap"),
                    )
                    == profile_observation_limits[profile]
                    and observation.get("capability") == "review_convergence"
                    and observation.get("mode") == "observe"
                    and observation.get("provider") == "roborev"
                    and observation.get("trigger") == "implementation_exit"
                    and observation.get("panel") == "none"
                    and observation.get("request_cap") == 1,
                    f"wrong proportional observation: {profile} {observation}",
                )

for relative in [
    "kc-dev-flow/scripts/profile-contract-loader.py",
    "kc-dev-flow/scripts/profile-contract-loader.test.py",
    "kc-dev-flow/scripts/engage-reconcile.py",
    "kc-dev-flow/scripts/engage-reconcile.test.py",
    "kc-dev-flow/scripts/poc-close-guard.py",
    "kc-dev-flow/scripts/poc-close-guard.test.py",
    "kc-dev-flow/scripts/profile-spacedock-route.test.py",
    "kc-dev-flow/scripts/pr-review-handoff.py",
    "kc-dev-flow/scripts/surface-map-check.py",
    "scripts/kc-dev-flow-published-tag-smoke.py",
]:
    require((ROOT / relative).stat().st_mode & 0o111, f"not executable: {relative}")

if not require_ablation_only:
    run(
        [sys.executable, "kc-dev-flow/scripts/profile-contract-loader.test.py"],
        "profile loader",
    )
    run(
        [sys.executable, "kc-dev-flow/scripts/engage-reconcile.test.py"],
        "engage reconcile",
    )
    run(
        [sys.executable, "kc-dev-flow/scripts/poc-close-guard.test.py"],
        "POC close guard",
    )
    run(
        [sys.executable, "kc-dev-flow/scripts/profile-spacedock-route.test.py"],
        "profile Spacedock route",
    )
    run(
        [sys.executable, "kc-dev-flow/scripts/pr-review-handoff.test.py"],
        "PR review handoff",
    )
    run(
        [sys.executable, "scripts/kc-dev-flow-published-tag-smoke.test.py"],
        "published-tag smoke behavior",
    )
    run(
        [sys.executable, "scripts/roborev-implementation-exit-contract.test.py"],
        "RoboRev contract",
    )
    run(
        [sys.executable, "scripts/pr-merge-portable-delivery.test.py"],
        "portable PR delivery",
    )
loader_path = PLUGIN / "scripts/profile-contract-loader.py"
spec = importlib.util.spec_from_file_location("profile_contract_loader", loader_path)
require(spec is not None and spec.loader is not None, "cannot import profile loader")
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)

expected_routes = {
    "poc-exploration": {
        "implementation": ("build", "validation"),
        "validation": ("prove", "done"),
    },
    "pilot-product-slice": {
        "ideation": ("shape", "implementation"),
        "implementation": ("build", "validation"),
        "validation": ("verify-deliver", "done"),
    },
    "production": {
        "ideation": ("shape", "implementation"),
        "implementation": ("build", "validation"),
        "validation": ("verify", "done"),
    },
}
require(loader.ROUTES == expected_routes, "profile route topology drifted")


def write_profile_work_item(
    root: Path,
    profile: str,
    workflow_stage: str,
    logical_route: list[str],
    *,
    schema: str = "kc-dev-flow-work-profile/v3",
) -> Path:
    path = root / f"{profile}-{workflow_stage}.md"
    receipt = [
        "---",
        f"status: {workflow_stage}",
        "sprint: kc-dev-flow/S2",
        "sprint-readiness: ready",
        "---",
        "",
        "## Work profile receipt",
        "",
        "```yaml",
        "work_profile:",
        f"  schema: {schema}",
        f"  selected: {profile}",
        f"  recommended: {profile}",
        f"  route: [{', '.join(logical_route)}]",
        "  basis: contract fixture",
    ]
    if profile == "poc-exploration" and schema.endswith("/v3"):
        receipt.extend(
            [
                "  poc_decision: Choose whether to fund the delivery slice",
                "  poc_falsifier: The integrated probe loses the accepted state",
                "  poc_budget: One local run and one review",
                "  poc_stop_when: Stop after the first integrated result",
            ]
        )
    elif profile in ("pilot-product-slice", "production"):
        receipt.append("  semantics_unchanged: false")
    receipt.extend(["```", ""])
    path.write_text(
        "\n".join(receipt),
        encoding="utf-8",
    )
    return path

installed_package = loader.load_installed_package()
manifest = json.loads((PLUGIN / "contract-manifest.json").read_text(encoding="utf-8"))
expected_manifest_resources = {
    "references/kernel.md",
    "references/reverse-recovery-audit.md",
    "references/journey-slicing.md",
    "references/retained-document-policy.md",
    "references/project-context-maintenance.md",
    "references/delivery-branch-base.md",
    "references/pr-delivery.md",
    "references/roborev-implementation-exit.md",
    "scripts/profile-contract-loader.py",
    "scripts/poc-close-guard.py",
    "scripts/engage-reconcile.py",
    "scripts/linear-admission.py",
    "skills/adopt-dev-flow/SKILL.md",
    "skills/continue-dev-flow/SKILL.md",
} | {
    f"references/profiles/{profile}/{name}"
    for profile, names in profile_files.items()
    for name in names
}
require(
    manifest.get("schema") == "kc-dev-flow-contract-manifest/v1"
    and manifest.get("contract_interface") == "kc-dev-flow-profile-contract/v3"
    and set(manifest.get("resources", [])) == expected_manifest_resources
    and len(str(installed_package["contract_digest"])) == 64,
    "installed manifest does not bind the exact canonical runtime surface",
)
# `release` was a Production-only runtime state until it stranded a Pilot item
# outside its declared route. Nothing else reads adoption prose, so the retired
# state is guarded here rather than trusted to a reviewer.
for relative in [
    "kc-dev-flow/skills/adopt-dev-flow/SKILL.md",
    "kc-dev-flow/MIGRATION.md",
    "kc-dev-flow/README.md",
    "kc-dev-flow/references/kernel.md",
    "kc-dev-flow/references/retained-document-policy.md",
    "kc-dev-flow/references/project-context-maintenance.md",
]:
    normalized = " ".join(read(relative).split())
    for retired in ["adds `release`", "explicit `release` stage", "`release` / `done`"]:
        require(
            retired not in normalized,
            f"{relative} still instructs the retired `release` state: {retired}",
        )

# The ablation only runs at the release gate, so a mutant whose anchor text was
# edited out of its target fails there, after every check a PR ran was green,
# and the cases after it never run. Four such anchors have gone stale this way.
# The guard itself cannot run in --ablation-check: a mutant removes anchor text
# on purpose, so it would fire inside every mutated copy and fail them for the
# wrong reason. Full mode is what marketplace-parity runs on every PR.
if not require_ablation_only:
    ablation_source = read("scripts/kc-dev-flow-minimal-stack-ablation.test.py")
    ablation_constants = {
        name: value.value
        for node in ast.parse(ablation_source).body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Call)
        and getattr(node.value.func, "id", "") == "Path"
        and node.value.args
        and isinstance(value := node.value.args[0], ast.Constant)
        for name in [node.targets[0].id]
    }


    def ablation_literal(node: ast.expr) -> str | None:
        """Resolve a mutant argument that is a literal or `str(MODULE_CONSTANT)`."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if (
            isinstance(node, ast.Call)
            and getattr(node.func, "id", "") == "str"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Name)
        ):
            return ablation_constants.get(node.args[0].id)
        return None


    unresolved = []
    checked = 0
    for call in ast.walk(ast.parse(ablation_source)):
        if not (isinstance(call, ast.Call) and getattr(call.func, "id", "") == "run_manual_contract_mutant"):
            continue
        name, target, before = (ablation_literal(argument) for argument in call.args[:3])
        if target is None or before is None:
            unresolved.append((call.lineno, name, "arguments are not statically resolvable"))
            continue
        checked += 1
        found = read(target).count(before)
        if found != 1:
            unresolved.append((call.lineno, name, f"anchor appears {found}x in {target}"))
    require(
        checked and not unresolved,
        "ablation mutation anchors no longer bind their target: "
        + "; ".join(f"line {line} {name}: {reason}" for line, name, reason in unresolved),
    )


release_gate = read(".github/workflows/kc-dev-flow-release-gate.yml")
require(
    "./scripts/kc-dev-flow-multi-profile-gate.py" in release_gate
    and "./scripts/kc-dev-flow-minimal-stack-ablation.test.py" in release_gate,
    "the release gate workflow no longer runs the baseline and without-it checks",
)
# A job-level `if:` makes a required check report "pending / expected" forever
# and blocks unrelated PRs; the release scoping belongs inside the job.
require(
    not re.search(r"^    if:", release_gate, re.MULTILINE),
    "the release gate job is skipped by a job-level if:, which a required check cannot survive",
)
for phrase in [
    "persist-credentials: false",
    "HEAD_REPO: ${{ github.event.pull_request.head.repo.full_name }}",
    'HEAD_REF" != "release-please--branches--main',
    "SPACEDOCK_SHA256:",
    "sha256sum -c -",
    'changed_files="$(git diff --name-only',
]:
    require(phrase in release_gate, f"the release gate lost a trust-boundary guard: {phrase}")
require(
    "git diff --name-only \"origin/$BASE_REF\"...HEAD |" not in release_gate,
    "the release gate can misclassify a git diff SIGPIPE/error as an unrelated release",
)

gate_path = ROOT / "scripts/kc-dev-flow-multi-profile-gate.py"
gate_spec = importlib.util.spec_from_file_location("kc_dev_flow_release_gate", gate_path)
require(gate_spec is not None and gate_spec.loader is not None, "cannot import release gate")
gate = importlib.util.module_from_spec(gate_spec)
gate_spec.loader.exec_module(gate)
require(
    hasattr(gate, "STATIC_INSTRUCTION_CEILING_BYTES")
    and gate.STATIC_INSTRUCTION_CEILING_BYTES == 40_000,
    "release gate does not enforce the absolute 40000-byte static instruction ceiling",
)
require(
    hasattr(gate, "mandatory_static_components"),
    "release gate does not expose its mandatory static input accounting",
)
static_components = gate.mandatory_static_components(ROOT)
expected_static_components = {
    "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
    "docs/dev/README.md#frontmatter+Local Profile",
}
require(
    set(static_components) == expected_static_components,
    "release gate static input account omits continue-dev-flow or Local Profile",
)
require(
    static_components["kc-dev-flow/skills/continue-dev-flow/SKILL.md"]
    == (PLUGIN / "skills/continue-dev-flow/SKILL.md").stat().st_size,
    "release gate does not count the exact continue-dev-flow bytes",
)
require(
    static_components["docs/dev/README.md#frontmatter+Local Profile"]
    == gate.workflow_context_bytes(ROOT / "docs/dev/README.md"),
    "release gate does not count the bounded workflow frontmatter and Local Profile bytes",
)
with tempfile.TemporaryDirectory(prefix="kc-dev-flow-workflow-context-") as temporary:
    fenced_workflow = Path(temporary) / "README.md"
    fenced_text = """---
state: fixture
---

# Fixture

<!-- kc-dev-flow-static-local-profile:start -->
## Local Profile

Count this.

```markdown
```~
## Mixed fence closer is not a heading
```

<!--
## HTML comment heading
-->

Count this too.

<!-- kc-dev-flow-static-local-profile:end -->

## State prerequisite

Do not count this.
"""
    fenced_workflow.write_text(fenced_text, encoding="utf-8")
    expected_context = (
        fenced_text[: fenced_text.index("\n---\n", 4) + len("\n---\n")]
        + fenced_text[
            fenced_text.index("## Local Profile")
            : fenced_text.index(gate.LOCAL_PROFILE_END) + len(gate.LOCAL_PROFILE_END)
        ]
    )
    require(
        gate.workflow_context_bytes(fenced_workflow) == len(expected_context.encode("utf-8")),
        "release gate does not count the exact marked Local Profile bytes",
    )
    fenced_workflow.write_bytes(fenced_text.replace("\n", "\r\n").encode("utf-8"))
    try:
        gate.workflow_context_bytes(fenced_workflow)
    except gate.GateError as error:
        require("LF-only newlines" in str(error), "CRLF workflow failed for the wrong reason")
    else:
        require(False, "release gate accepts CRLF that makes static byte accounting undercount")
require(
    "reference tree" not in gate_path.read_text(encoding="utf-8"),
    "release gate still uses a gameable percentage of the reference tree",
)
_routes, measured_components, measured_static_inputs = gate.assert_proportional_load(
    loader, PLUGIN / "references"
)
require(
    measured_components == static_components,
    "release gate reported a different static prefix from its component account",
)
with tempfile.TemporaryDirectory(prefix="kc-dev-flow-static-load-") as temporary:
    for profile, route in expected_routes.items():
        logical_route = [logical for logical, _next_stage in route.values()]
        for workflow_stage, (logical_stage, _next_stage) in route.items():
            item = write_profile_work_item(
                Path(temporary), profile, workflow_stage, logical_route
            )
            selected = loader.load_contracts(PLUGIN / "references", item)
            canonical = dict(selected)
            canonical["work_item"] = "<work-item>"
            rendered = loader.render_text(canonical)
            expected_header = {
                key: canonical[key]
                for key in (
                    "schema",
                    "work_item",
                    "work_item_sha256",
                    "receipt_schema",
                    "profile",
                    "workflow_stage",
                    "logical_stage",
                    "next_workflow_stage",
                    "declared_receipts",
                )
            }
            for key in (
                "skip_to_workflow_stage",
                "review_risks",
                "implementation_exit_observation_declared",
                "poc_artifact",
                "poc_safety_boundary",
                "poc_decision_ready_minutes",
                "poc_decision_ready_reason",
                "poc_proof_path",
                "development_brief_sha256",
            ):
                if key in canonical:
                    expected_header[key] = canonical[key]
            try:
                actual_header = json.loads(rendered.splitlines()[0])
            except (IndexError, json.JSONDecodeError):
                actual_header = None
            require(
                actual_header == expected_header,
                f"default loader output header differs: {profile}/{workflow_stage}",
            )
            expected_chunks = [json.dumps(expected_header, sort_keys=True)]
            expected_static_bytes = sum(static_components.values()) + len(
                rendered.encode("utf-8")
            )
            require(
                measured_static_inputs[f"{profile}/{workflow_stage}"]
                == expected_static_bytes,
                f"release gate does not count {profile}/{workflow_stage} default output",
            )
            for relative in (
                "kernel.md",
                f"profiles/{profile}/base.md",
                f"profiles/{profile}/{logical_stage}.md",
            ):
                raw = (PLUGIN / "references" / relative).read_bytes()
                expected_payload = (
                    f"<contract path={json.dumps(relative)} "
                    f"sha256={json.dumps(hashlib.sha256(raw).hexdigest())}>\n"
                    f"{raw.decode('utf-8')}</contract>"
                )
                expected_chunks.append(f"\n{expected_payload}")
                require(
                    expected_payload in rendered,
                    f"default loader output omits selected payload: {relative}",
                )
            require(
                rendered == "\n".join(expected_chunks) + "\n",
                f"default loader output order or framing differs: {profile}/{workflow_stage}",
            )

kernel = read("kc-dev-flow/references/kernel.md")
normalized_kernel = " ".join(kernel.split())
for phrase in [
    "A work item is complete only when both conditions hold for the same exact candidate",
    "**Goal sufficiency**",
    "**Minimal necessity**",
    "without the retained implementation",
    "the accepted goal, a named falsifier, a safety boundary, or a required lifecycle obligation",
    "CI, review, and delivery authorization do not substitute for either condition",
    "Before terminalization, the First Officer confirms both conditions",
    "existing evidence produced across the selected route",
    "Goal sufficiency binds to the exact candidate",
    "minimal necessity names the candidate change removed by its without-it observation",
]:
    require(phrase in normalized_kernel, f"kernel omits completion invariant: {phrase}")
require(
    "state owner refuses terminalization" not in normalized_kernel,
    "kernel overclaims an automatic completion refusal instead of assigning the First Officer duty",
)
for phrase in [
    "compare added files, dependencies, abstractions, tests, and comments",
    "A comment that earns its place still passes a necessity test",
    "cut restatement of adjacent code or prose translation of a signature",
    "This is not a size target; do not delete for deletion's sake",
    "choose one explanatory home; the others state the invariant and point to that home",
    "reports both the blocks it cut and the candidates it kept, with the reason for each",
    "LOC and file counts are diagnostic signals, never pass/fail gates",
    "create no receipt or commentary",
    "A removal is graded by Minimal necessity like a retention; without it, unmapped.",
]:
    require(phrase in normalized_kernel, f"kernel omits subtraction rule: {phrase}")

audit = read("kc-dev-flow/references/reverse-recovery-audit.md")
normalized_audit = " ".join(audit.split())
for phrase in [
    "it maps to `kernel.md`'s minimal-necessity reasons — the accepted goal, a "
    "named falsifier, a safety boundary, or a required lifecycle obligation",
    "`NO_OBSERVED_CONSUMER` | None of the REQUIRED reasons was found inside "
    "declared boundaries",
    "a safety-boundary surface with no observed consumer classifies `REQUIRED`, "
    "the same tier `kernel.md`'s execution-tier mapping reaches",
    "This audit's `disproof_hook` runs at the search tier: it can conclude only "
    "that two searches inside the named boundary found no consumer, never that "
    "none exists",
    "`kernel.md`'s without-it observation runs the same primitive at the "
    "execution tier and can conclude a surface is unnecessary",
]:
    require(phrase in normalized_audit, f"audit omits unified need vocabulary: {phrase}")
chooser_contract = read("kc-dev-flow/skills/choose-work-profile/SKILL.md")
require_production_route(
    chooser_contract,
    "`Production` (`production`)",
    "`shape -> build -> verify`",
)
for phrase in [
    "one planning authority per item",
    "one execution-record authority",
    "planning item owns discussion, the accepted goal, priority, and human-facing status",
    "planning window owns time",
    "planning outcome owns the accepted result",
    "admitted execution set and its accepted goal and non-goals are snapshots, not planning authorities",
    "local execution grouping does not prove a Planning Receipt",
    "runtime owns execution and evidence",
    "execution-to-planning-provider projector",
    "No reconcile result writes either side automatically",
    "Captain admits the delta",
]:
    require(phrase in normalized_kernel, f"kernel omits provider-neutral planning boundary: {phrase}")
normalized_continuation_policy = " ".join(
    read("kc-dev-flow/skills/continue-dev-flow/SKILL.md").split()
)
for phrase in [
    "exact work item's `source`",
    "shares the exact window and outcome read from the engaged item",
    "stdout parses as one JSON object with `status: clean`",
    "Exit `1` reports the classified delta",
    "Exit `2` reports `planning reconcile unavailable`",
    "added, removed, changed, or moved item",
    "Captain must admit the delta",
]:
    require(
        phrase in normalized_continuation_policy,
        f"continuation omits provider engage behavior: {phrase}",
    )
for phrase in [
    "Development Brief is required",
    "Planning Receipt is optional",
    "complete or absent",
    "partial Planning Receipt",
    "Captain-approved committed work item",
    "does not invoke the planning reader or comparator",
    "compare the accepted goal and complete non-goal list exactly",
    "structured planning delta",
    "affected acceptance evidence",
    "recommended `change` or `stop`",
    "Runtime adapters own task and execution-context cardinality",
]:
    require(phrase in normalized_kernel, f"kernel omits brief boundary: {phrase}")
for forbidden in [
    "one planning item to one SD task and one isolated execution context",
    "refusing a second task or execution context for the same admitted source",
    "The fresh executor receives",
    "each task records the tuple",
    "The SD entity set",
    "committed SD entity set",
    "SD-to-planning-provider projector",
]:
    require(forbidden not in normalized_kernel, f"kernel owns runtime topology: {forbidden}")
for phrase in [
    "An item leaves `backlog` only after its required brief is admitted",
    "Development Brief",
    "Exploration Brief",
    "local execution grouping does not prove a Planning Receipt",
]:
    require(phrase in normalized_kernel, f"kernel backlog exit bar is missing: {phrase}")
require(
    "brief admission" in " ".join(read("kc-dev-flow/skills/choose-work-profile/SKILL.md").split()),
    "choose-work-profile no longer checks the brief admission bar",
)
# `public compatibility` promoted on publication, which every change to this
# package satisfies, so the trigger fired on all of them and sorted none. The
# replacement asks whether a consumer must run a migration. Guarded in all four
# places that state a promotion boundary, because a reader who finds the old
# wording in any one of them gets the old rule.
for relative in [
    "kc-dev-flow/references/kernel.md",
    "kc-dev-flow/README.md",
    "kc-dev-flow/skills/choose-work-profile/SKILL.md",
    "kc-dev-flow/references/profiles/pilot-product-slice/base.md",
]:
    normalized = " ".join(read(relative).split())
    require(
        "public compatibility" not in normalized,
        f"{relative} still promotes on publication rather than on a consumer migration",
    )
    require(
        "compatibility break that makes a consumer act" in normalized,
        f"{relative} omits the consumer-migration promotion trigger",
    )
# The kernel names the trigger; the skill that makes the call owns the test for
# it. Kernel bytes are paid at every stage of every route, and this explanation
# is only read when a profile is being chosen.
normalized_choose = " ".join(read("kc-dev-flow/skills/choose-work-profile/SKILL.md").split())
require(
    "asks whether a consumer must do something, not whether the change is published"
    in normalized_choose
    and "it has to run a migration" in normalized_choose,
    "choose-work-profile no longer states the consumer-migration test",
)
for relative, phrases in {
    "kc-dev-flow/README.md": [
        "Load development constraints in proportion to work risk",
        "POC — bounded exploration or technical proof",
    ],
    "kc-dev-flow/skills/choose-work-profile/SKILL.md": [
        "Could credible negative evidence cancel or materially change the next commitment",
        "kc-dev-flow-work-profile/v3",
    ],
    "kc-dev-flow/skills/continue-dev-flow/SKILL.md": [
        "do not dispatch a validation worker",
        "return the POC outcome to planning",
        "does not create downstream delivery work",
        "planning decides whether a new Development Brief exists",
    ],
    "kc-dev-flow/references/profiles/poc-exploration/base.md": [
        "Decision-ready time above the recorded limit",
        "any Captain intervention before decision-ready",
        "ends product proof",
        "Continue only to record a complete `change` outcome",
    ],
}.items():
    normalized = " ".join(read(relative).split())
    for phrase in phrases:
        require(phrase in normalized, f"{relative} omits the v4 POC contract: {phrase}")
architecture = " ".join(read("ARCHITECTURE.md").split())
require(
    "Direct no-code or disposable POCs emit no observation" in architecture
    and "without a validation worker" in architecture,
    "project context still claims unconditional POC review or validation",
)
poc_guard_source = read("kc-dev-flow/scripts/poc-close-guard.py")
require(
    'commands.add_parser("create")' not in poc_guard_source,
    "POC guard still creates downstream work",
)
normalized_continue = " ".join(
    read("kc-dev-flow/skills/continue-dev-flow/SKILL.md").split()
)
require(
    "poc_handoff" not in normalized_continue,
    "continuation still owns downstream POC handoff",
)
for phrase in [
    "one ephemeral `delivery` binding",
    "exact `branchName` and `Fixes TEAM-N`",
    "`branch: null` and `Closes owner/repo#N`",
    "stop before branch push or PR creation",
]:
    require(
        phrase in normalized_continue,
        f"continuation omits provider delivery linkage: {phrase}",
    )
normalized_pr_delivery = " ".join(
    read("kc-dev-flow/references/pr-delivery.md").split()
)
for phrase in [
    "delivery.branch",
    "delivery.close_line",
    "same exact reconciled `source`",
    "legacy `issue` field only for a standalone item",
]:
    require(
        phrase in normalized_pr_delivery,
        f"PR delivery omits provider linkage: {phrase}",
    )
obsolete_adopter_copies = {
    LOCAL_MODS / "kernel.md",
    LOCAL_MODS / "profile-contract-loader.py",
    LOCAL_MODS / "poc-close-guard.py",
    ROOT / "scripts/kc-dev-flow/engage-reconcile.py",
} | {
    LOCAL_MODS / reference
    for reference in (
        "reverse-recovery-audit.md",
        "journey-slicing.md",
        "retained-document-policy.md",
        "project-context-maintenance.md",
        "delivery-branch-base.md",
        "pr-delivery.md",
        "roborev-implementation-exit.md",
    )
} | {
    LOCAL_MODS / "profiles" / profile / name
    for profile, names in profile_files.items()
    for name in names
}
require(
    not [path for path in obsolete_adopter_copies if path.exists()],
    "canonical runtime copies remain in the adopter",
)
for reference, trigger in [
    ("retained-document-policy.md", "retained_document_change"),
    ("project-context-maintenance.md", "project_context_claim_may_change"),
]:
    policy = re.sub(
        r"\s+",
        " ",
        (PLUGIN / "references" / reference).read_text(encoding="utf-8"),
    )
    require(
        "as a typed conditional reference" in policy
        and trigger in policy
        and "do not load the file when that trigger is false" in policy,
        f"conditional reference has stale adoption instructions: {reference}",
    )
with tempfile.TemporaryDirectory(prefix="kc-dev-flow-work-items-") as temporary:
    work_items = Path(temporary)
    for contracts_root in [PLUGIN / "references"]:
        for profile, stages in expected_routes.items():
            logical_route = [logical for logical, _next in stages.values()]
            for workflow_stage, (logical_stage, next_stage) in stages.items():
                work_item = write_profile_work_item(
                    work_items, profile, workflow_stage, logical_route
                )
                contract = loader.load_contracts(contracts_root, work_item)
                paths = [entry["path"] for entry in contract["loaded"]]
                require(
                    paths
                    == [
                        "kernel.md",
                        f"profiles/{profile}/base.md",
                        f"profiles/{profile}/{logical_stage}.md",
                    ]
                    and contract["next_workflow_stage"] == next_stage
                    and contract["work_item"] == work_item.resolve().as_posix(),
                    f"wrong selected load set: {contracts_root} {profile} {workflow_stage}",
                )
                require(
                    contract["schema"] == "kc-dev-flow-profile-contract/v2"
                    and contract["receipt_schema"] == "kc-dev-flow-work-profile/v3",
                    f"work-item binding schema drifted: {contract}",
                )
                require(
                    all(
                        f"profiles/{other}/" not in "\n".join(paths)
                        for other in expected_routes
                        if other != profile
                    ),
                    f"unselected profile path leaked: {profile} {workflow_stage}",
                )

        for profile, workflow_stage in (
            ("pilot-product-slice", "ideation"),
            ("production", "ideation"),
        ):
            logical_route = [
                logical for logical, _next in expected_routes[profile].values()
            ]
            work_item = write_profile_work_item(
                work_items,
                profile,
                workflow_stage,
                logical_route,
                schema="kc-dev-flow-work-profile/v2",
            )
            contract = loader.load_contracts(contracts_root, work_item)
            require(
                contract["receipt_schema"] == "kc-dev-flow-work-profile/v2",
                f"compatible v2 receipt was not retained: {contracts_root} {profile}",
            )

skills = {
    "adopt-dev-flow": "kc-dev-flow/skills/adopt-dev-flow/SKILL.md",
    "choose-work-profile": "kc-dev-flow/skills/choose-work-profile/SKILL.md",
    "continue-dev-flow": "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
    "chief-engineer": "kc-dev-flow/skills/chief-engineer/SKILL.md",
    "science-officer": "kc-dev-flow/skills/science-officer/SKILL.md",
    "science-officer-em": "kc-dev-flow/skills/science-officer-em/SKILL.md",
}
for expected, relative in skills.items():
    require(skill_name(relative) == expected, f"skill name drifted: {relative}")

codex_manifest = json.loads(read("kc-dev-flow/.codex-plugin/plugin.json"))
hermes_manifest = json.loads(read("kc-dev-flow/plugin.json"))
require(
    hermes_manifest
    == {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": "kc-dev-flow",
        "version": codex_manifest["version"],
        "description": codex_manifest["description"],
        "author": codex_manifest["author"],
        "homepage": "https://github.com/iamcxa/kc-claude-plugins/tree/main/kc-dev-flow",
        "repository": "https://github.com/iamcxa/kc-claude-plugins",
        "license": "MIT",
        "keywords": [
            "development-workflow",
            "sprint",
            "delivery",
            "evidence",
            "hermes-agent",
        ],
    },
    "Hermes portable manifest drifted",
)
require(
    {
        path.parent.name
        for path in (PLUGIN / "skills").glob("*/SKILL.md")
    }
    == {
        "adopt-dev-flow",
        "chief-engineer",
        "choose-work-profile",
        "continue-dev-flow",
        "science-officer",
        "science-officer-em",
    },
    "Hermes portable package does not expose the complete direct skills set",
)
starter_prompts = codex_manifest["interface"]["defaultPrompt"]
require(
    any("$chief-engineer" in prompt for prompt in starter_prompts),
    "Codex starter prompts omit Chief Engineer",
)
require(
    any("$science-officer" in prompt for prompt in starter_prompts),
    "Codex starter prompts omit Science Officer",
)
require(
    all("$science-officer-em" not in prompt for prompt in starter_prompts),
    "Codex starter prompts still activate the legacy adapter",
)

chooser = read(skills["choose-work-profile"])
continue_skill = read(skills["continue-dev-flow"])
chief = read(skills["chief-engineer"])
science = read(skills["science-officer"])
legacy = read(skills["science-officer-em"])
adopter = read(skills["adopt-dev-flow"])
migration = read("kc-dev-flow/MIGRATION.md")
production_verify = read("kc-dev-flow/references/profiles/production/verify.md")
rationale = read("kc-dev-flow/RATIONALE.md")
normalized_adopter = " ".join(adopter.split())
normalized_rationale = " ".join(rationale.split())
normalized_chooser = " ".join(chooser.split())
normalized_continue = " ".join(continue_skill.split())
normalized_chief = " ".join(chief.split())
normalized_science = " ".join(science.split())
normalized_migration = " ".join(migration.split())
normalized_production_verify = " ".join(production_verify.split())

for marker in (gate.LOCAL_PROFILE_START, gate.LOCAL_PROFILE_END):
    require(marker in normalized_adopter, f"adopter omits static Local Profile marker: {marker}")
migration_3x = migration.split("## Migrating from 3.x to 4.x", 1)[1].split(
    "## Migrating from 2.x", 1
)[0]
migration_2x = migration.split("## Migrating from 2.x", 1)[1]
normalized_migration_3x = " ".join(migration_3x.split())
for label, section in (("3.x migration", migration_3x), ("2.x migration", migration_2x)):
    for marker in (gate.LOCAL_PROFILE_START, gate.LOCAL_PROFILE_END):
        require(marker in section, f"{label} omits static Local Profile marker: {marker}")

for phrase in [
    "structured Ask UI",
]:
    require(phrase in normalized_chooser, f"chooser is missing: {phrase}")
require_production_route(chooser, "`Production` (`production`)", "`shape -> build -> verify`")
require(
    "shape -> build -> verify -> release" not in normalized_chooser,
    "chooser still documents the removed release route element",
)
require("before a work item enters its first working stage" in normalized_chooser, "profile selection is still ideation-bound")
for phrase in [
    "repository that supports Planning Receipts",
    "standalone adopter binds the Captain-approved committed brief",
    "A Planning Receipt is complete or absent",
    "Local `sprint` and `sprint-readiness` remain runtime grouping and readiness mechanics",
    "Linear uses installed sibling `linear-admission.py`",
    "other providers keep a repository-local adapter",
    "installed engage comparator",
    "every currently Ready snapshot source",
    "For a provider-backed adopter, run one clean, one delta, and one invalid-input comparator invocation",
    "A standalone adopter has no comparator to exercise",
    "For a complete Planning Receipt, the engage reconcile is read-only",
    "do not persist an installation path",
    "exact source, window, and outcome",
    "do not all share",
    "Captain admits every delta",
    "parsed `status: clean` result",
    "starts directly with `## The problem`",
    "omits both an `## Agent execution contract` section",
    "Provider-backed work uses its reader",
    "standalone uses neither",
    "preserve repository-local free text in a repository-owned field",
    "remove the canonical `source` field",
    "Do not reinterpret provenance as provider identity",
    "A missing delivery authority is a refit requirement",
    "do not invent direct Git delivery",
    "adds no repository-owned reader, adapter, script, test, or check for a capability a declared resource already supplies",
    "commit it only when the Captain names a consumer that reads it",
    "a repository-local Linear planning reader",
    "needs `LINEAR_API_KEY` in the invoking process environment, which is provider credential rather than host binding",
    "a state authority at `<workflow-dir>/.spacedock-state` that is its own committed git root",
    "It reads no other environment variable to decide whether to run",
    "Work with no planning provider at all records no Planning Receipt, invokes no reader, and needs no credential",
    "raise that layout as a refit requirement against the package and keep the repository-local adapter",
    "The Issue and the committed work item carry the accepted goal under the same heading, and `linear-admission.py` reads no other name for it",
]:
    require(phrase in normalized_adopter, f"adopter omits scheduling binding: {phrase}")
adopt_steps = [int(value) for value in re.findall(r"^(\d+)\.", adopter, re.MULTILINE)]
require(
    adopt_steps == list(range(1, 11)),
    f"adopter steps must be unique and sequential: {adopt_steps}",
)
for forbidden in [
    "one planning item to one SD task and one isolated execution context",
    "refuse a second matching task or context",
    "Feed the executor only",
]:
    require(forbidden not in normalized_adopter, f"adopter owns runtime topology: {forbidden}")
for phrase in [
    "Migrating from 3.x to 4.x",
    "drain every entity at `status: release`",
    "sprint-readiness=ready",
    "do not mark the unscheduled queue ready as a bulk migration",
    "parsed `status: clean` result",
    "inventory every existing `source` field",
    "move it to a repository-owned provenance field",
    "remove the canonical `source` field before either v4 admission validation or continuation",
    "do not reinterpret it as provider identity",
    "retires its repository-local planning reader",
    "no longer requires `CONDUCTOR_WORKSPACE_ID`",
    "work with no planning provider records no Planning Receipt and needs neither",
]:
    require(phrase in normalized_migration, f"v4 migration omits: {phrase}")
for phrase in [
    "classify its Planning Receipt before recording scheduling fields",
    "For provider-backed work, resolve the accepted planning window and outcome from `source`",
    "For standalone work, leave `source`, `planning-window`, and `planning-outcome` absent",
    "Both paths assign a non-empty local `sprint` execution group",
    "Run the reader and comparator only for provider-backed work",
    "Standalone work skips both and continues from the Captain-approved committed brief",
]:
    require(
        phrase in normalized_migration_3x,
        f"3.x migration omits standalone planning branch: {phrase}",
    )
for stale in [
    "Before continuing any item already at its first working stage, resolve its accepted planning window and outcome from `source`",
    "then run one read-only engage reconcile against the provider's current Ready set",
]:
    require(
        stale not in normalized_migration_3x,
        f"3.x migration still makes provider planning universal: {stale}",
    )
require(
    "review disposition" in normalized_production_verify
    and "model identity" in normalized_production_verify,
    "Production verification omits risk-selected review disposition",
)

for phrase in [
    "kc-dev-flow-static-local-profile",
    "start/end marker pair",
    "Read only its frontmatter and marked block",
    "never infer boundaries from headings",
    "from this activated skill",
    "--work-item <exact-committed-work-item>",
    "simultaneous items may load different routes",
    "emits shared core, selected base, and selected stage only",
    "kc-dev-flow:chief-engineer",
    "kc-dev-flow:science-officer",
    "kc-dev-flow-conditional-references/v1",
    "A link is not activation",
]:
    require(phrase in normalized_continue, f"continuation is missing: {phrase}")
continuation_authority_order = [
    "Read the exact committed work item and selected brief.",
    "Classify its optional Planning Receipt before provider access.",
    "Then read current execution state from its declared authority.",
]
continuation_authority_positions = []
for phrase in continuation_authority_order:
    require(phrase in normalized_continue, f"continuation authority resolution omits: {phrase}")
    continuation_authority_positions.append(normalized_continue.index(phrase))
require(
    continuation_authority_positions == sorted(continuation_authority_positions)
    and len(set(continuation_authority_positions)) == len(continuation_authority_positions),
    "continuation must resolve the brief and optional receipt before execution state",
)
for phrase in [
    "all Planning Receipt fields are absent",
    "all Planning Receipt fields are present",
    "report `planning receipt incomplete`",
    "run provider reconcile only for the provider-backed branch",
    "Invoke the installed loader's sibling read-only engage comparator only in the provider-backed branch.",
    "Captain-approved committed brief",
    "If `source` is not a resolvable planning link, report `planning source unavailable`",
    "stop before reading execution state",
    "Do not promote the admission snapshot into planning authority",
    "The Captain must admit the delta before an authorized actor commits a replacement snapshot.",
    "Do not cancel a running worker.",
    "No difference writes the provider or execution snapshot automatically.",
    "every currently Ready snapshot source",
    "Refuse a truncated provider result",
    "stdout parses as one JSON object with `status: clean`",
    "compare the accepted goal and complete non-goal list exactly",
    "do not replace the snapshot or candidate",
    "affected acceptance evidence",
    "recommended `change` or `stop`",
]:
    require(phrase in normalized_continue, f"continuation planning disambiguation omits: {phrase}")
for phrase in [
    "retained_document_change",
    "project_context_claim_may_change",
    "A Markdown work record alone satisfies neither trigger",
    "`receipt: null` creates no receipt",
]:
    require(phrase in normalized_continue, f"continuation omits doc trigger: {phrase}")
require_production_route(continue_skill, "Production", "`backlog -> ideation -> implementation -> validation -> done`")
require(
    "-> release ->" not in continue_skill,
    "continuation route table still documents the removed release stage",
)
require("fresh-context EM verdict" not in continue_skill, "continuation still mandates EM")
for retired in ["`engineering-judgment.md`", "`work-control-profile.md`"]:
    require(retired in adopter, f"adopter omits retired-mod disposition: {retired}")
for phrase in [
    "older explicit Captain choice outside the v1 schema",
    "extra local terminal state only through an explicit mapping",
    "Keep `retained-document-policy.md`",
    "`receipt: null` adds no receipt",
]:
    require(phrase in normalized_adopter, f"adopter omits migration rule: {phrase}")
for phrase in [
    "breaking upgrade",
    "one coordinated cutover",
    "leave completed and archived items unchanged",
    "finding-only terminal",
    "Preserve `retained-document-policy.md`",
    "New choices use `kc-dev-flow-work-profile/v3`",
    "Pilot or Production v1 receipt may migrate mechanically to v3",
    "a POC v1 receipt requires the Captain to record the v3 decision fields",
]:
    require(phrase in migration, f"migration guide omits: {phrase}")
for phrase in [
    "The first version of KC Dev Flow",
    "carrying the whole workshop",
    "kc-dev-flow-work-profile/v3",
    "A Planning Receipt is optional and complete or absent",
    "Without a Planning Receipt, the Captain-approved committed work item",
    "Runtime adapters decide task, worktree, and worker cardinality",
    "returns `poc_outcome` to planning",
    "directional evidence",
    "What would prove this wrong",
    "Load the work, not the ceremony",
    "The First Officer supplies the source, window, and outcome read from the exact work item",
    "The First Officer continues only on one parsed `status: clean` result",
]:
    require(phrase in normalized_rationale, f"rationale omits: {phrase}")
for forbidden in [
    "committed Spacedock entity set is the snapshot",
    "bind each task to its planning selection",
    "not yet admitted to SD move",
    "`sprint` remains an SD execution grouping",
]:
    require(forbidden not in normalized_rationale, f"rationale restores runtime coupling: {forbidden}")
require(
    "net repository lines" not in normalized_rationale,
    "rationale retains a mutable PR diff snapshot",
)

for phrase in [
    "next smallest integrated step",
    "recommendation: proceed | adjust | escalate",
    "no gate or state authority",
]:
    require(phrase in normalized_chief, f"Chief Engineer is missing: {phrase}")
for phrase in [
    "contested, high-risk, hard-to-reverse",
    "recommendation: proceed | adjust | hold | escalate",
    "It is not a state mutation or veto",
    "Do not read `science-officer-em`",
]:
    require(phrase in normalized_science, f"Science Officer is missing: {phrase}")
require("Do not treat `EM` as an alias" in legacy, "legacy adapter still owns EM")

for retired in [
    ".github/workflows/spacedock-project-sync.yml",
    ".github/spacedock-project.json",
    ".github/scripts/project-spacedock-state.py",
]:
    require(not (ROOT / retired).exists(), f"self-adoption still installs projector control: {retired}")

roadmap = read("docs/dev/ROADMAP.md")
normalized_roadmap = " ".join(roadmap.split())
kc_dev_flow_roadmap = roadmap.split("## `kc-dev-flow`", 1)[1].split("\n## ", 1)[0]
kc_dev_flow_lines = kc_dev_flow_roadmap.splitlines()
for active_projection_plan in [
    "### Sprint S3 — GitHub projection dogfood",
    "Captain direction: begin immediately alongside the remaining `kc-dev-flow/S2`",
    "Projection exit: a disposable proof establishes",
    "Status-update exit: the sibling derives facts and metrics",
    "remaining S3 projection work",
]:
    require(
        active_projection_plan not in roadmap,
        f"Roadmap retains the active S3 projection plan: {active_projection_plan}",
    )
require(
    "### Sprint S3 — RETIRED for new admissions" in kc_dev_flow_lines,
    "Roadmap omits the exact retired kc-dev-flow/S3 heading",
)
issue_297_url = "https://github.com/iamcxa/kc-claude-plugins/issues/297"
s6_heading = "### Sprint S6 — provider-neutral planning"
require(s6_heading in kc_dev_flow_lines, "Roadmap omits the exact kc-dev-flow/S6 heading")
require(
    roadmap.count(issue_297_url) == 1,
    f"Roadmap must link Issue #297 exactly once, found {roadmap.count(issue_297_url)}",
)
s6_body = re.split(
    r"\n#{2,3} ", kc_dev_flow_roadmap.split(s6_heading, 1)[1], maxsplit=1
)[0].strip()
require(
    s6_body == f"- [Issue #297]({issue_297_url})",
    "kc-dev-flow/S6 must contain only the Issue #297 link",
)
require(
    "`spacedock-project-status-updates` remains at `implementation`" not in roadmap,
    "Roadmap copies mutable Spacedock execution state into retired S3",
)
require(
    "A RETIRED heading remains registered only for existing execution records and forbids new admissions by Captain authority."
    in roadmap,
    "Roadmap omits the RETIRED-heading authority boundary",
)

workflow = read("docs/dev/README.md")
normalized_workflow = " ".join(workflow.split())
ship_readme = read("docs/ship-flow/README.md")
normalized_ship_readme = " ".join(ship_readme.split())
for phrase in [
    "Linear is this repository's planning provider for new provider-backed admissions, not an iteration authority.",
    "`source` links the accepted Linear Issue.",
    "At every provider-backed engage, compare the current Project/Cycle active set with the committed SD snapshot.",
    "Existing admitted work keeps its recorded provider and reader",
    "GitHub Project #4 remains historical and receives no new admissions.",
    "A standalone Captain-approved brief leaves `source`, `planning-window`, and `planning-outcome` empty",
    "A difference requires Captain admission and never writes either side automatically.",
    "| Planning reader and admission guard | Installed sibling `linear-admission.py`",
    "| Planning comparator | Installed sibling `engage-reconcile.py` supplied by the activated `kc-dev-flow` skill; no stored installation path |",
    "reconcile exact Project/Cycle active Issues",
]:
    require(phrase in normalized_workflow, f"self-adoption omits Linear cutover boundary: {phrase}")
require(
    "GitHub Issues plus Project #4 is this repository's default planning provider"
    not in normalized_workflow,
    "self-adoption restored GitHub Project as the default for new admissions",
)
for phrase in [
    "For a complete Planning Receipt, copy the planning item's accepted outcome and non-goals into the work item as an admission snapshot",
    "it is not a second accepted-goal authority",
    "For standalone work, the Captain-approved committed Development Brief already holds that authority.",
    "Record task-specific acceptance evidence as execution evidence.",
]:
    require(phrase in normalized_workflow, f"self-adoption misstates brief authority: {phrase}")
manual_issue_body = workflow.split("```markdown\n", 1)[1].split("```", 1)[0]
normalized_manual_issue_body = " ".join(manual_issue_body.split())
manual_issue_headings = [
    "## The problem", "## Accepted outcome", "## Non-goals",
    "## Acceptance criteria", "## Route-back conditions",
]
require(all(manual_issue_body.count(heading) == 1 for heading in manual_issue_headings), "manual admission Issue headings are missing or duplicated")
heading_positions = [manual_issue_body.index(heading) for heading in manual_issue_headings]
require(heading_positions == sorted(heading_positions), "manual admission Issue headings are out of order")
require(
    manual_issue_body.startswith("## The problem\n"),
    "manual admission Issue body does not start directly with The problem",
)
require(
    "## Human-readable release brief" not in manual_issue_body,
    "manual admission Issue body restored the redundant release-brief wrapper",
)
require(
    "- **AC-1** <observable condition>" in manual_issue_body
    and "## Acceptance evidence" not in manual_issue_body,
    "manual admission Issue body is not canonical AC-N criteria",
)
require(
    " ".join(adopter.split("```markdown\n", 1)[1].split("```", 1)[0].split())
    == normalized_manual_issue_body,
    "adopter Issue template drifted from the workflow README template",
)
for phrase in [
    "The accepted outcome or non-goals changed",
    "structured planning delta",
]:
    require(phrase in normalized_manual_issue_body, f"manual admission Issue body omits: {phrase}")
for forbidden in [
    "## Agent execution contract",
    "one Issue to one committed Spacedock task and one isolated worktree",
]:
    require(forbidden not in manual_issue_body, f"manual admission Issue body owns runtime topology: {forbidden}")
for phrase in [
    "Roadmap headings are legacy or local SD execution-group identifiers, not planning windows or outcomes.",
    "It does not store task state, acceptance criteria, evidence, or provider-specific cycle metadata.",
]:
    require(phrase in normalized_roadmap, f"Roadmap is not thin enough for provider-neutral planning: {phrase}")
require(
    "sprint-readiness: defer" in workflow
    and "--where sprint-readiness=ready" in normalized_workflow,
    "self-adoption template/query no longer default closed and select only ready items",
)
frontmatter = workflow.split("---", 2)[1]
expected_stage_order = ["backlog", "ideation", "implementation", "validation", "done"]
actual_stage_order = re.findall(r"    - name: ([a-z-]+)", frontmatter)
require(actual_stage_order == expected_stage_order, f"workflow stage graph drifted: {actual_stage_order}")

# The literal above pins this repository's graph; these two derive the reason it
# is that shape. #276's incident was a state — `release` — that sat between a
# profile's last working state and the terminal one: Spacedock computed the
# gate's target from graph order, so a Pilot approval targeted a stage outside
# its route and the item had no way to reach `done`. A profile-only state is
# therefore safe before a route's first state and fatal after its last.
terminal_state = actual_stage_order[-1]
for profile, stages in expected_routes.items():
    route_states = [state for state in actual_stage_order if state in stages]
    require(
        route_states == [state for state in stages],
        f"{profile} route states are missing from or out of order in the workflow graph: "
        f"{route_states} vs {list(stages)}",
    )
    last = actual_stage_order.index(route_states[-1])
    require(
        actual_stage_order[last + 1] == terminal_state,
        f"{profile} would strand: the graph puts "
        f"{actual_stage_order[last + 1]!r} between its last working state "
        f"{route_states[-1]!r} and {terminal_state!r}",
    )
for phrase in [
    "POC | `backlog -> implementation -> validation -> done`",
    "Pilot | `backlog -> ideation -> implementation -> validation -> done`",
    "profile-contract-loader.py",
    "Profiles are per item",
    "| Installed contract interface | `kc-dev-flow-local-profile/v1` |",
    "| Local mods | `docs/dev/_mods/pr-merge.md` |",
    "No agent is a general gatekeeper",
    "delivery event mod, not a profile contract",
    "canonical runtime resources",
    "`pr_delivery_selected` stays false and `pr-delivery.md` is not loaded here",
    "Work-item records and unrelated Markdown changes activate neither",
]:
    require(phrase in workflow, f"self-adoption is missing: {phrase}")
require_production_route(workflow, "Production", "`backlog -> ideation -> implementation -> validation -> done`")

package_readme = read("kc-dev-flow/README.md")
normalized_package_readme = " ".join(package_readme.split())
root_readme = read("README.md")
require_production_route(package_readme, "Production", "`shape -> build -> verify`")
require(
    "shape -> build -> verify -> release" not in normalized_package_readme
    and 'R5["Release' not in package_readme,
    "package README still documents the removed release route element",
)
# Match against the normalized text: a claim that survives only because of where
# the line happens to wrap is not a claim the README is actually holding.
require(
    "run POC, Pilot, and Production items concurrently" in normalized_package_readme,
    "package README omits item-local concurrent profiles",
)
require(
    "cognitive cue, not another agent, review, or gate" in normalized_package_readme,
    "package README overstates stage-role authority",
)
require(
    "stable entity slug rather than a host filesystem path"
    in normalized_package_readme,
    "package README omits portable stage-pin identity",
)
for phrase in [
    "candidate receipt is valid only for its exact tracked package snapshot",
    "discard the receipt and rerun candidate mode on the final release PR head",
    "local install sync waits for that check to pass",
]:
    require(
        phrase in normalized_package_readme,
        f"package README omits the release-proof boundary: {phrase}",
    )
require("](./MIGRATION.md)" in package_readme, "package README omits migration guide")
require("[design rationale](./RATIONALE.md)" in package_readme, "package README omits rationale")
require(
    "checks ephemeral normalized admission and current Ready sets against the caller-supplied expected source, window, and outcome"
    in normalized_package_readme,
    "package README overclaims comparator provenance binding",
)
require(
    "binds the exact engaged source" not in normalized_package_readme,
    "package README still overclaims comparator provenance binding",
)
require(
    "[profile-native migration guide](./kc-dev-flow/MIGRATION.md)" in root_readme,
    "root README omits migration guide",
)
architecture = " ".join(read("ARCHITECTURE.md").split())
for phrase in [
    "one canonical `AC-N` Development Brief",
    "default loading leaves already-admitted headings unchanged",
    "success-only dispatch-envelope emission without creating execution state",
]:
    require(phrase in architecture, f"architecture omits admission boundary: {phrase}")
validation_runbook = read("docs/dev/runbooks/validation-evidence.md")
normalized_validation_runbook = " ".join(validation_runbook.split())
for stale in ["selected policy mods", "Write all six lines", "the EM selects"]:
    require(stale not in validation_runbook, f"validation runbook retains stale ceremony: {stale}")
for phrase in [
    "POC never loads it",
    "smallest evidence set that can fail",
    "Science Officer remains risk-triggered and advisory",
]:
    require(
        phrase in normalized_validation_runbook,
        f"validation runbook omits: {phrase}",
    )
for name in ["chief-engineer", "science-officer", "science-officer-em"]:
    require(name in package_readme, f"package README omits {name}")
    require(name in root_readme, f"root README omits {name}")

linear_admission = PLUGIN / "scripts/linear-admission.py"
linear_source = linear_admission.read_text(encoding="utf-8")
for mechanism in [
    '"--validate-admission"',
    '"GIT_NO_REPLACE_OBJECTS": "1"',
    '"state or work-item revision changed during admission"',
    '"status") != "clean"',
    '"branchName"',
    '"delivery": delivery',
    '"kc-dev-flow-dispatch-envelope/v1"',
    '"committed snapshot Non-goals must be a \'- \' bullet list"',
]:
    require(mechanism in linear_source, f"Linear admission omits retained mechanism: {mechanism}")


class LinearFixture(http.server.BaseHTTPRequestHandler):
    def log_message(self, _format: str, *args: object) -> None:
        return

    def do_POST(self) -> None:
        fixture = self.server
        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length))
        query, variables = request["query"], request["variables"]
        fixture.queries.append(query)
        if fixture.scenario == "unauthorized":
            self.send_error(401)
            return
        if fixture.scenario == "timeout":
            time.sleep(0.2)
        if fixture.scenario in {"state-race", "work-item-race"} and not fixture.raced:
            fixture.raced = True
            if fixture.scenario == "state-race":
                (fixture.state / "race.md").write_text("race\n", encoding="utf-8")
                subprocess.run(["git", "-C", str(fixture.state), "add", "race.md"], check=True)
                subprocess.run(
                    ["git", "-C", str(fixture.state), "-c", "user.name=fixture",
                     "-c", "user.email=fixture@example.test", "commit", "-m", "race"],
                    check=True, capture_output=True,
                )
            else:
                fixture.work_item.write_text(
                    fixture.work_item.read_text(encoding="utf-8") + "changed\n",
                    encoding="utf-8",
                )
        content = fixture.project_content
        cycle_id = fixture.cycle_id
        goal, non_goal = fixture.goal, fixture.non_goal
        goal_heading = (
            "## Goal"
            if fixture.scenario == "legacy-goal-heading"
            else "## Accepted outcome"
        )
        if fixture.scenario == "project-drift":
            content += " changed"
        if fixture.scenario == "cycle-drift":
            cycle_id = "22222222-2222-4222-8222-222222222222"
        if fixture.scenario == "goal-drift":
            goal += " changed"
        if fixture.scenario == "non-goal-drift":
            non_goal += " changed"
        state_type = "completed" if fixture.scenario == "removed" else "started"

        def issue(identifier: str = "DEV-12") -> dict[str, object]:
            issue_state = "completed" if identifier == "DEV-11" else state_type
            reported_identifier = (
                "DEV-99"
                if fixture.scenario == "mismatched-identifier" and "AdmissionIssue" in query
                else identifier
            )
            branch_name = (
                "feature/not-the-engaged-issue"
                if fixture.scenario == "invalid-branch"
                else f"feature/{reported_identifier.lower()}-fixture"
            )
            item = {
                "id": identifier.lower(), "identifier": reported_identifier,
                "url": f"https://linear.app/{fixture.workspace}/issue/{identifier}/fixture",
                "description": f"{goal_heading}\n\n{goal}\n\n## Non-goals\n\n* {non_goal}\n",
                "state": {"type": issue_state},
                "project": {"id": fixture.project_id, "name": fixture.project_name, "content": content},
                "cycle": {"id": cycle_id, "startsAt": fixture.starts, "endsAt": fixture.ends},
            }
            if "branchName" in query:
                item["branchName"] = branch_name
            return item

        if "AdmissionIssue" in query:
            data = {
                "viewer": {"organization": {"id": "org", "urlKey": (
                    "wrong" if fixture.scenario == "wrong-org" else fixture.workspace
                )}},
                "issue": issue(str(variables["id"])),
            }
        elif "AdmissionProject" in query:
            data = {"project": {"id": fixture.project_id, "name": fixture.project_name, "content": content}}
        else:
            nodes = [] if fixture.scenario == "removed" else [issue("DEV-13"), issue()]
            if fixture.scenario == "added":
                nodes.append(issue("DEV-14"))
            page = {"hasNextPage": fixture.scenario == "truncated", "endCursor": None}
            data = {"issues": {"nodes": nodes, "pageInfo": page}}
        encoded = json.dumps({"data": data}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        try:
            self.wfile.write(encoded)
        except BrokenPipeError:
            pass


with tempfile.TemporaryDirectory(prefix="linear-admission-contract-") as temporary:
    fixture_root = Path(temporary)
    workflow = fixture_root / "docs/dev"
    state = workflow / ".spacedock-state"
    state.mkdir(parents=True)
    project_id = "11111111-1111-4111-8111-111111111111"
    cycle_id = "33333333-3333-4333-8333-333333333333"
    project_name, project_content = "Project One", "One accepted package."
    starts, ends = "2026-08-27T16:00:00.000Z", "2026-09-10T16:00:00.000Z"
    goal, non_goal = "Emit one exact envelope.", "No provider writes."
    workspace_slug = "qnow"
    source = f"https://linear.app/{workspace_slug}/issue/DEV-12/fixture"
    project_digest = hashlib.sha256(f"{project_name}\n{project_content}".encode()).hexdigest()
    window = f"Linear Cycle {cycle_id} {starts}/{ends}"
    outcome = f"Linear Project {project_id} {project_name} sha256:{project_digest}"
    work_item = state / "dev-12.md"
    work_item.write_text(
        f"""---
status: implementation
source: {source}
planning-window: "{window}"
planning-outcome: "{outcome}"
sprint: dev-12
sprint-readiness: ready
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: fixture
  semantics_unchanged: false
```

## The problem

Manual provider input is not repeatable.

## Accepted outcome

{goal}

## Non-goals

- {non_goal}

## Acceptance criteria

- **AC-1** A current read emits one exact envelope.

## Route-back conditions

Stop on any planning drift.
""",
        encoding="utf-8",
    )
    (state / "dev-13.md").write_text(
        work_item.read_text(encoding="utf-8").replace("DEV-12", "DEV-13"),
        encoding="utf-8",
    )
    # Archived and finished in Linear too: only an active snapshot item that
    # Linear has closed counts as a removed planning item.
    (state / "_archive").mkdir()
    (state / "_archive/dev-11.md").write_text(
        work_item.read_text(encoding="utf-8")
        .replace("DEV-12", "DEV-11")
        .replace("status: implementation", "status: done", 1),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", str(state)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(state), "add", "dev-12.md", "dev-13.md", "_archive/dev-11.md"], check=True)
    subprocess.run(
        ["git", "-C", str(state), "-c", "user.name=fixture",
         "-c", "user.email=fixture@example.test", "commit", "-m", "fixture"],
        check=True, capture_output=True,
    )
    revision = subprocess.check_output(["git", "-C", str(state), "rev-parse", "HEAD"], text=True).strip()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), LinearFixture)
    server.scenario, server.queries, server.raced = "clean", [], False
    server.state, server.work_item = state, work_item
    server.workspace = workspace_slug
    server.project_id, server.project_name, server.project_content = project_id, project_name, project_content
    server.cycle_id, server.starts, server.ends = cycle_id, starts, ends
    server.goal, server.non_goal = goal, non_goal
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def admit(
        scenario: str,
        *,
        key: str | None = "test-key",
        timeout: str = "5",
        reader: Path = linear_admission,
        workflow_dir: Path = workflow,
    ) -> subprocess.CompletedProcess[str]:
        server.scenario, server.raced = scenario, False
        env = os.environ.copy()
        if key is None:
            env.pop("LINEAR_API_KEY", None)
        else:
            env["LINEAR_API_KEY"] = key
        return subprocess.run(
            [sys.executable, str(reader), "--workflow-dir", str(workflow_dir),
             "--work-item", str(work_item),
             "--profile-loader", str(PLUGIN / "scripts/profile-contract-loader.py"),
             "--local-profile", str(ROOT / "docs/dev/README.md"),
             "--linear-workspace", workspace_slug, "--state-revision", revision,
             "--timeout", timeout, "--graphql-url", f"http://127.0.0.1:{server.server_port}/graphql"],
            cwd=ROOT, env=env, text=True, capture_output=True,
        )

    before = (revision, work_item.read_bytes())
    requests_before = len(server.queries)
    refused = admit("missing-key", key=None)
    require(
        refused.returncode == 2
        and not refused.stdout
        and "LINEAR_API_KEY is unavailable" in refused.stderr,
        f"missing-key was not refused for the credential: {refused.stderr}",
    )
    require(len(server.queries) == requests_before, "a missing credential reached Linear")
    started_at = time.monotonic()
    clean = admit("clean")
    journey_ms = round((time.monotonic() - started_at) * 1000)
    require(clean.returncode == 0, f"clean Linear admission failed: {clean.stderr}")
    envelope = json.loads(clean.stdout)
    require(
        set(envelope) == {
            "schema", "linear_organization", "delivery", "work_item_sha256",
            "state_revision", "snapshot_sha256", "live_read_sha256", "reconcile",
            "development_brief_sha256", "plugin_version", "contract_digest",
            "local_profile_interface", "profile_contract_hashes", "command_elapsed_ms",
        },
        f"dispatch envelope key set drifted: {sorted(envelope)}",
    )
    require(
        envelope["schema"] == "kc-dev-flow-dispatch-envelope/v1"
        and envelope.get("delivery") == {
            "branch": "feature/dev-12-fixture",
            "close_line": "Fixes DEV-12",
        }
        and envelope["reconcile"] == {"added": [], "changed": [], "moved": [], "removed": [], "status": "clean"}
        and envelope["snapshot_sha256"] == envelope["live_read_sha256"]
        and envelope["plugin_version"] == installed_package["version"]
        and envelope["contract_digest"] == installed_package["contract_digest"]
        and envelope["local_profile_interface"] == "kc-dev-flow-local-profile/v1"
        and envelope["command_elapsed_ms"] <= journey_ms <= 60000,
        f"full-boundary admission receipt is invalid: {envelope} / {journey_ms}",
    )
    legacy_heading = admit("legacy-goal-heading")
    require(
        legacy_heading.returncode == 2
        and not legacy_heading.stdout
        and "needs one Accepted outcome section" in legacy_heading.stderr,
        f"the retired Goal heading was still admitted: {legacy_heading.stderr}",
    )
    inline_workflow = fixture_root / "inline"
    inline_workflow.mkdir()
    inline = admit("clean", workflow_dir=inline_workflow)
    require(
        inline.returncode == 2
        and not inline.stdout
        and "state authority is not <workflow-dir>/.spacedock-state" in inline.stderr,
        f"inline state layout was not named in the refusal: {inline.stderr}",
    )
    with tempfile.TemporaryDirectory(prefix="linear-delivery-mutants-") as temporary:
        mutant_root = Path(temporary)
        branch_mutant = mutant_root / "branch-read-removed.py"
        branch_source, branch_count = re.subn(
            r" url branchName description", " url description", linear_source, count=1
        )
        require(branch_count == 1, "Linear branch-read mutant anchor changed")
        branch_mutant.write_text(branch_source, encoding="utf-8")
        refused = admit("clean", reader=branch_mutant)
        require(
            refused.returncode == 2 and not refused.stdout,
            "linear-delivery-branch-read-removed mutant survived",
        )

        goal_heading_mutant = mutant_root / "retired-goal-heading-restored.py"
        goal_heading_source, goal_heading_count = re.subn(
            r'"accepted-goal": section\(description, "Accepted outcome"\),',
            '"accepted-goal": section(description, "Goal"),',
            linear_source,
            count=1,
        )
        require(goal_heading_count == 1, "Linear goal-heading mutant anchor changed")
        goal_heading_mutant.write_text(goal_heading_source, encoding="utf-8")
        survived = admit("legacy-goal-heading", reader=goal_heading_mutant)
        require(
            survived.returncode == 0,
            f"retired-goal-heading-restored mutant still refused: {survived.stderr}",
        )

        state_mutant = mutant_root / "state-authority-message-removed.py"
        state_source, state_count = re.subn(
            r'^        if not state\.is_dir\(\):\n'
            r'            raise AdmissionError\("state authority is not <workflow-dir>/\.spacedock-state"\)\n',
            "",
            linear_source,
            count=1,
            flags=re.MULTILINE,
        )
        require(state_count == 1, "Linear state-authority mutant anchor changed")
        state_mutant.write_text(state_source, encoding="utf-8")
        survived = admit("clean", reader=state_mutant, workflow_dir=inline_workflow)
        require(
            survived.returncode == 2
            and "state authority is not <workflow-dir>/.spacedock-state" not in survived.stderr,
            f"state-authority-message-removed mutant kept the message: {survived.stderr}",
        )

        envelope_mutant = mutant_root / "delivery-envelope-removed.py"
        envelope_source, envelope_count = re.subn(
            r'^            "delivery": delivery,\n',
            "",
            linear_source,
            count=1,
            flags=re.MULTILINE,
        )
        require(envelope_count == 1, "Linear delivery-envelope mutant anchor changed")
        envelope_mutant.write_text(envelope_source, encoding="utf-8")
        survived = admit("clean", reader=envelope_mutant)
        survived_envelope = json.loads(survived.stdout) if survived.returncode == 0 else {}
        require(
            survived.returncode != 0 or survived_envelope.get("delivery") != envelope["delivery"],
            "linear-delivery-envelope-removed mutant survived",
        )
    for scenario, classification in (
        ("project-drift", "moved"), ("cycle-drift", "moved"),
        ("goal-drift", "changed"), ("non-goal-drift", "changed"),
        ("added", "added"), ("removed", "removed"),
    ):
        refused = admit(scenario)
        require(
            refused.returncode == 2 and not refused.stdout and f'"{classification}"' in refused.stderr,
            f"{scenario} did not stop with {classification}: {refused.stderr}",
        )
    for scenario in (
        "wrong-org", "unauthorized", "truncated", "invalid-branch",
        "mismatched-identifier",
    ):
        refused = admit(scenario)
        require(refused.returncode == 2 and not refused.stdout, f"{scenario} emitted an envelope")
    timed_out = admit("timeout", timeout="0.05")
    require(timed_out.returncode == 2 and not timed_out.stdout, "timeout emitted an envelope")
    require(before == (revision, work_item.read_bytes()), "Linear outcomes changed state or work-item bytes")
    require(all("mutation" not in query.casefold() for query in server.queries), "Linear reader sent a mutation")
    require(
        any("AdmissionIssue" in query and "branchName" in query for query in server.queries),
        "Linear reader did not request branchName",
    )
    raced = admit("work-item-race")
    require(raced.returncode == 2 and not raced.stdout, "changing work-item bytes emitted an envelope")
    subprocess.run(
        ["git", "-C", str(state), "restore", "--source", revision, "--", "dev-12.md"],
        check=True,
    )
    raced = admit("state-race")
    require(raced.returncode == 2 and not raced.stdout, "changing state revision emitted an envelope")
    server.shutdown()
    server.server_close()

for phrase in [
    "A dispatch message to a cloud build worker carries no bootstrap or download line",
    "the Conductor WAF blocks a dispatch message containing a `curl | tar` bootstrap line",
    "it travels on a committed carrier",
    "the worker fetches and reads with `git show <branch>:<path>`",
]:
    require(phrase in normalized_ship_readme, f"Ship-flow runtime omits a dispatch-carrier rule: {phrase}")
for phrase in [
    "CLI e2e evidence is a timestamped stdout log written by",
    "exits non-zero on the first step whose command's exit code does not match its declared `expect`",
]:
    require(phrase in normalized_ship_readme, f"Ship-flow runtime omits the CLI e2e evidence rule: {phrase}")
for phrase in [
    "`CANDIDATE_SHA`, `BRANCH`, `BASE_SHA`, `WITHOUT_IT_COMMAND`, and `WITHOUT_IT_REMOVED_VARIANT`",
    "`WITHOUT_IT_COMMAND` is one self-contained shell line: it references no file outside the candidate "
    "tree, it exits 0 on the candidate and non-zero once `WITHOUT_IT_REMOVED_VARIANT` is applied, and the "
    "First Officer runs it verbatim, unchanged, in a worktree with no secrets.",
]:
    require(phrase in normalized_ship_readme, f"Ship-flow runtime omits the WITHOUT_IT_COMMAND one-line rule: {phrase}")
for phrase in [
    "The First Officer reads a worker's transcript through `conductor sql` against "
    "`session_transcripts_view`, not `conductor session message --after`",
    "that CLI truncates its JSON response at 64 KB, which cuts off a long Evidence block, and "
    "its `--after` cursor rejects a sent message's id, which breaks polling from the FO's own last message.",
    "`scripts/ship-flow/worker-transcript.sh <session-id>` prints the session's last fenced "
    "`## Evidence` block, or exits 1 with `no evidence block` when the transcript has none.",
]:
    require(phrase in normalized_ship_readme, f"Ship-flow runtime omits the conductor-sql transcript-read rule: {phrase}")
for phrase in [
    "the production entry issues at most one `conductor workspace create` call after a committed intent",
    "It is not exactly-once and it covers workspace creation only",
    "in no case does the new holder create a workspace for an intent it did not commit",
]:
    require(phrase in normalized_ship_readme, f"Ship-flow runtime omits the intent-commit rule: {phrase}")

for phrase in [
    "Dispatch a higher layer only after the lower layer is fully verified. (DEV-67)",
]:
    require(phrase in normalized_ship_readme, f"Ship-flow runtime omits dispatch-layer-verification DEV-67: {phrase}")

for phrase in [
    "A worker's without-it command runs in an isolated environment (temporary HOME, no agent, no network). (DEV-67)",
]:
    require(phrase in normalized_ship_readme, f"Ship-flow runtime omits without-it-isolation DEV-67: {phrase}")

for phrase in [
    "Security, data-loss, and compatibility findings outside the Brief block the candidate while general improvements are scoped out. (DEV-67)",
]:
    require(phrase in normalized_ship_readme, f"Ship-flow runtime omits finding-classification DEV-67: {phrase}")

pilot_build = read("kc-dev-flow/references/profiles/pilot-product-slice/build.md")
production_build = read("kc-dev-flow/references/profiles/production/build.md")
poc_build = read("kc-dev-flow/references/profiles/poc-exploration/build.md")
normalized_pilot_build = " ".join(pilot_build.split())
normalized_production_build = " ".join(production_build.split())
normalized_poc_build = " ".join(poc_build.split())
require(
    "run `kc-dev-flow/scripts/surface-map-check.py` against the candidate diff and "
    "the Evidence block, checking every non-test changed file"
    in normalized_pilot_build,
    "Pilot build omits the surface-map-check.py naming sentence",
)
require(
    "run `kc-dev-flow/scripts/surface-map-check.py` against the candidate diff and "
    "the Evidence block, checking every changed file against the shape contract's "
    "changed-file-to-obligation mapping"
    in normalized_production_build,
    "Production build omits the surface-map-check.py naming sentence",
)
require(
    "kc-dev-flow/scripts/surface-map-check.py` applies only to the surfaces this "
    "stage's `poc_outcome` marks retained"
    in normalized_poc_build,
    "POC build omits the surface-map-check.py retained-only scope sentence",
)

surface_map_check = ROOT / "kc-dev-flow/scripts/surface-map-check.py"
run([sys.executable, "-m", "py_compile", str(surface_map_check)], "surface-map-check compile")

if not require_ablation_only:
    run([sys.executable, "scripts/ship-flow/uat-doc.test.py"], "ship-flow UAT doc")
    run(["bash", "scripts/ship-flow/notify.test.sh"], "ship-flow notify")
    run([sys.executable, "scripts/ship-flow/dev-debrief.test.py"], "ship-flow dev debrief")
    run([sys.executable, "scripts/ship-flow/ship-debrief.test.py"], "ship-flow ship debrief")
    run([sys.executable, "docs/plan-flow/schema/close-receipt.test.py"], "plan-flow close-receipt validation")

surface_map_fixtures = ROOT / "kc-dev-flow/scripts/fixtures/surface-map"
surface_map_work_item = surface_map_fixtures / "dev-66-work-item-fixture.md"
surface_map_round0_evidence = surface_map_fixtures / "dev-66-round0-evidence.md"
surface_map_free_text_evidence = surface_map_fixtures / "free-text-target-evidence.md"
surface_map_poc_not_in_diff_work_item = surface_map_fixtures / "poc-work-item-not-in-diff.md"
surface_map_without_it_true_evidence = surface_map_fixtures / "without-it-true-true-evidence.md"
surface_map_deletion_only_evidence = surface_map_fixtures / "deletion-only-evidence.md"
surface_map_production_work_item = surface_map_fixtures / "production-work-item-fixture.md"
surface_map_shape_mapping = surface_map_fixtures / "shape-mapping-fixture.txt"
surface_map_shape_mismatch_evidence = surface_map_fixtures / "shape-mapping-mismatch-evidence.md"
surface_map_full_coverage_evidence = surface_map_fixtures / "full-coverage-evidence.md"
for fixture in (
    surface_map_work_item,
    surface_map_round0_evidence,
    surface_map_free_text_evidence,
    surface_map_poc_not_in_diff_work_item,
    surface_map_without_it_true_evidence,
    surface_map_deletion_only_evidence,
    surface_map_production_work_item,
    surface_map_shape_mapping,
    surface_map_shape_mismatch_evidence,
    surface_map_full_coverage_evidence,
):
    require(fixture.is_file(), f"missing surface-map fixture: {fixture}")

with tempfile.TemporaryDirectory(prefix="kc-dev-flow-surface-map-") as surface_map_repo_name:
    surface_map_repo = Path(surface_map_repo_name)
    subprocess.run(["git", "init", str(surface_map_repo)], check=True, capture_output=True)
    git_user = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.test"]

    (surface_map_repo / "docs/dev").mkdir(parents=True)
    (surface_map_repo / "scripts/ship-flow").mkdir(parents=True)
    (surface_map_repo / "docs/dev/README.md").write_text("base\n", encoding="utf-8")
    (surface_map_repo / "scripts/kc-dev-flow-contract-test.py").write_text("# base\n", encoding="utf-8")
    (surface_map_repo / "scripts/ship-flow/legacy-runner.sh").write_text(
        "#!/bin/sh\necho legacy\n", encoding="utf-8"
    )
    subprocess.run(["git", "-C", str(surface_map_repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(surface_map_repo), *git_user, "commit", "-m", "base"],
        check=True, capture_output=True,
    )
    surface_map_base = subprocess.check_output(
        ["git", "-C", str(surface_map_repo), "rev-parse", "HEAD"], text=True
    ).strip()

    (surface_map_repo / "scripts/fixtures/ship-flow").mkdir(parents=True)
    (surface_map_repo / "docs/dev/README.md").write_text("candidate\n", encoding="utf-8")
    (surface_map_repo / "scripts/kc-dev-flow-contract-test.py").write_text("# candidate\n", encoding="utf-8")
    (surface_map_repo / "scripts/ship-flow/e2e-cli.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (surface_map_repo / "scripts/ship-flow/parse-execute-external.py").write_text("# candidate\n", encoding="utf-8")
    (surface_map_repo / "scripts/fixtures/ship-flow/dev-50-cli-flow.yaml").write_text("steps: []\n", encoding="utf-8")
    (surface_map_repo / "scripts/fixtures/ship-flow/dev-50-cli-flow-failing.yaml").write_text(
        "steps: []\n", encoding="utf-8"
    )
    subprocess.run(
        ["git", "-C", str(surface_map_repo), "rm", "-q", "scripts/ship-flow/legacy-runner.sh"],
        check=True, capture_output=True,
    )
    subprocess.run(["git", "-C", str(surface_map_repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(surface_map_repo), *git_user, "commit", "-m", "candidate"],
        check=True, capture_output=True,
    )
    surface_map_candidate = subprocess.check_output(
        ["git", "-C", str(surface_map_repo), "rev-parse", "HEAD"], text=True
    ).strip()

    def run_surface_map_check(
        evidence: Path,
        *,
        work_item: Path = surface_map_work_item,
        shape_mapping: Path | None = None,
        extra_args: list[str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable, str(surface_map_check),
            surface_map_base, surface_map_candidate,
            str(evidence),
            "--work-item", str(work_item),
            "--brief", str(work_item),
            "--repo", str(surface_map_repo),
        ]
        if shape_mapping is not None:
            command += ["--shape-mapping", str(shape_mapping)]
        if extra_args:
            command += extra_args
        return subprocess.run(command, capture_output=True, text=True)

    round0 = run_surface_map_check(surface_map_round0_evidence)
    require(
        round0.returncode == 1 and "parse-execute-external.py" in round0.stdout,
        "surface-map-check did not redden on the DEV-66-shaped round-0 fixture: "
        f"exit={round0.returncode} stdout={round0.stdout!r} stderr={round0.stderr!r}",
    )

    free_text = run_surface_map_check(surface_map_free_text_evidence)
    require(
        free_text.returncode == 1 and "invalid target" in free_text.stdout,
        "surface-map-check did not reject a free-text SURFACE target: "
        f"exit={free_text.returncode} stdout={free_text.stdout!r} stderr={free_text.stderr!r}",
    )

    poc_not_in_diff = run_surface_map_check(
        surface_map_round0_evidence, work_item=surface_map_poc_not_in_diff_work_item
    )
    require(
        poc_not_in_diff.returncode == 1 and "retained surface not in diff" in poc_not_in_diff.stdout,
        "surface-map-check did not reject a POC retained surface absent from the diff: "
        f"exit={poc_not_in_diff.returncode} stdout={poc_not_in_diff.stdout!r} stderr={poc_not_in_diff.stderr!r}",
    )

    without_it_stub = run_surface_map_check(surface_map_without_it_true_evidence)
    require(
        without_it_stub.returncode == 1 and "without-it pair does not bind" in without_it_stub.stdout,
        "surface-map-check accepted a `true | true` without-it stub: "
        f"exit={without_it_stub.returncode} stdout={without_it_stub.stdout!r} stderr={without_it_stub.stderr!r}",
    )

    deletion_only = run_surface_map_check(surface_map_deletion_only_evidence)
    deletion_violations = (
        "invalid target: scripts/ship-flow/legacy-runner.sh",
        "without-it pair does not bind scripts/ship-flow/legacy-runner.sh",
        "missing SURFACE line: scripts/ship-flow/legacy-runner.sh",
    )
    require(
        deletion_only.returncode == 1
        and not any(violation in deletion_only.stdout for violation in deletion_violations),
        "surface-map-check flagged a deleted file declared `removal | - | -`: "
        f"exit={deletion_only.returncode} stdout={deletion_only.stdout!r} stderr={deletion_only.stderr!r}",
    )

    shape_mismatch = run_surface_map_check(
        surface_map_shape_mismatch_evidence,
        work_item=surface_map_production_work_item,
        shape_mapping=surface_map_shape_mapping,
    )
    require(
        shape_mismatch.returncode == 1 and "shape mapping says" in shape_mismatch.stdout,
        "surface-map-check did not reject a shape-mapping/evidence target mismatch: "
        f"exit={shape_mismatch.returncode} stdout={shape_mismatch.stdout!r} stderr={shape_mismatch.stderr!r}",
    )

    full_coverage = run_surface_map_check(surface_map_full_coverage_evidence)
    require(
        full_coverage.returncode == 0,
        "surface-map-check did not accept a fully-covering Evidence block for the DEV-66-shaped diff: "
        f"exit={full_coverage.returncode} stdout={full_coverage.stdout!r} stderr={full_coverage.stderr!r}",
    )

with tempfile.TemporaryDirectory(prefix="kc-dev-flow-intent-lock-") as intent_lock_root_name:
    # DEV-93: a split-root state checkout (`git worktree add`) has `.git` as a FILE, not a
    # directory; a lock path hardcoded as `<state>/.git/...` can never `mkdir` there. This
    # case fails on the pre-fix script (SystemExit-worthy `lock timeout`, exit 6) and only
    # passes once the lock path is resolved through `git rev-parse --git-dir`.
    intent_lock_root = Path(intent_lock_root_name)
    intent_lock_origin = intent_lock_root / "origin.git"
    intent_lock_seed = intent_lock_root / "seed"
    intent_lock_bare = intent_lock_root / "bare-clone"
    intent_lock_state_wt = intent_lock_root / "state-wt"
    git_user = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.test"]
    subprocess.run(["git", "init", "-q", "--bare", str(intent_lock_origin)], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(intent_lock_origin), str(intent_lock_seed)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(intent_lock_seed), *git_user, "checkout", "-q", "-b", "spacedock-state/dev"], check=True, capture_output=True)
    (intent_lock_seed / "_holder.json").write_text(json.dumps({"writer": 1, "holder": "laptop", "at": "x"}), encoding="utf-8")
    subprocess.run(["git", "-C", str(intent_lock_seed), "add", "_holder.json"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(intent_lock_seed), *git_user, "commit", "-q", "-m", "seed holder"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(intent_lock_seed), "push", "-q", "origin", "spacedock-state/dev"], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(intent_lock_origin), str(intent_lock_bare)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(intent_lock_bare), "worktree", "add", "-q", str(intent_lock_state_wt), "spacedock-state/dev"],
        check=True, capture_output=True,
    )
    require((intent_lock_state_wt / ".git").is_file(), "DEV-93 fixture: worktree .git is not a file")

    def run_intent_commit(script: Path, claim: str) -> subprocess.CompletedProcess:
        env = dict(os.environ, SHIP_LOCK_STALE_S="3")
        return subprocess.run(
            [
                str(script), "commit", str(intent_lock_state_wt), "laptop", "1", claim,
                "0123456789abcdef0123456789abcdef",
                "11111111-1111-1111-1111-111111111111",
                "d98f40b5e2080cb884facf1734fc66052eff998",
                hashlib.sha256(claim.encode()).hexdigest(),
            ],
            capture_output=True, text=True, env=env, timeout=60,
        )

    fixed_result = run_intent_commit(ROOT / "scripts/ship-flow/intent.sh", "dev-93-contract-case")
    require(
        fixed_result.returncode == 0,
        "intent.sh commit did not succeed on a worktree-style state checkout (`.git` is a file): "
        f"exit={fixed_result.returncode} stdout={fixed_result.stdout!r} stderr={fixed_result.stderr!r}",
    )
    intent_lock_git_dir_raw = subprocess.run(
        ["git", "-C", str(intent_lock_state_wt), "rev-parse", "--git-dir"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    intent_lock_git_dir = Path(intent_lock_git_dir_raw)
    if not intent_lock_git_dir.is_absolute():
        intent_lock_git_dir = intent_lock_state_wt / intent_lock_git_dir
    require(
        not list(intent_lock_git_dir.glob("ship-lock.d*")),
        "intent.sh left lock residue under the worktree's git dir",
    )

run([sys.executable, "-m", "py_compile", str(loader_path)], "loader compile")
run([sys.executable, "-m", "py_compile", str(linear_admission)], "Linear admission compile")

plan_lint = ROOT / "docs/plan-flow/plan-lint.py"
require(plan_lint.is_file(), f"missing {plan_lint}")
require(plan_lint.stat().st_mode & 0o111, f"not executable: docs/plan-flow/plan-lint.py")

plan_flow_schemas = [
    ROOT / "docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json",
]
for schema in plan_flow_schemas:
    require(schema.is_file(), f"missing {schema}")

plan_flow_fixtures = [
    ROOT / "scripts/fixtures/plan-flow/dev89-runA-reverified.snapshot.json",
    ROOT / "scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json",
]
for fixture in plan_flow_fixtures:
    require(fixture.is_file(), f"missing {fixture}")

lint_correct = (ROOT / "scripts/fixtures/plan-flow/dev89-runA-reverified.snapshot.json").read_text()
lint_cmd = [sys.executable, str(plan_lint), "lint", str(plan_flow_fixtures[0])]
lint_result = subprocess.run(lint_cmd, capture_output=True, text=True, cwd=ROOT)
require(
    "PASS L6" in lint_result.stdout and "PASS L8" in lint_result.stdout and "PASS L10" in lint_result.stdout,
    f"plan-lint output missing expected rules on reverified fixture: {lint_result.stdout}",
)
require(
    "FAIL L9" in lint_result.stdout and "DEV-91" in lint_result.stdout,
    f"plan-lint L9 should fail on DEV-91 by-product: {lint_result.stdout}",
)

with tempfile.TemporaryDirectory(prefix="plan-flow-offline-") as temporary:
    offline_env = os.environ.copy()
    offline_env["https_proxy"] = "http://127.0.0.1:9"
    lint_offline = subprocess.run(
        lint_cmd,
        capture_output=True, text=True, cwd=ROOT, env=offline_env, timeout=5,
    )
    require(
        lint_offline.returncode in (0, 1),
        f"plan-lint failed with network access blocked: {lint_offline.stderr}",
    )
    require(
        "PASS L" in lint_offline.stdout,
        f"plan-lint offline did not emit rules: {lint_offline.stdout}",
    )

e2e_gate = ROOT / "scripts/ship-flow/e2e-gate.py"
e2e_gate_fixtures = ROOT / "scripts/fixtures/ship-flow/e2e-gate"


def run_e2e_gate(
    plan_fixture: str,
    close_fixture: str,
    *,
    offline: bool = False,
    close_receipt_override: dict | None = None,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if offline:
        env["https_proxy"] = "http://127.0.0.1:9"
        env["http_proxy"] = "http://127.0.0.1:9"
    close_path = e2e_gate_fixtures / close_fixture
    override_path: Path | None = None
    if close_receipt_override is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(close_receipt_override, handle)
            override_path = Path(handle.name)
        close_path = override_path
    try:
        return subprocess.run(
            [sys.executable, str(e2e_gate), str(e2e_gate_fixtures / plan_fixture), str(close_path)],
            cwd=ROOT, text=True, capture_output=True, env=env, timeout=30,
        )
    finally:
        if override_path is not None:
            override_path.unlink(missing_ok=True)


# The committed ac2 fixture carries a placeholder candidate (a real SHA
# would go unreachable under a shallow CI checkout); this is the only
# gate scenario that runs e2e-cli.sh, so it needs a commit that both
# resolves and contains the fixtures its flow's own steps reference --
# this checkout's own HEAD always satisfies both.
current_head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True,
).stdout.strip()
ac2_close_receipt = json.loads((e2e_gate_fixtures / "close-receipt.ac2.json").read_text(encoding="utf-8"))
ac2_issue_key = next(iter(ac2_close_receipt["issues"]))
ac2_close_receipt["issues"][ac2_issue_key]["candidate"] = current_head

e2e_gate_ac2 = run_e2e_gate(
    "plan-receipt.ac2.json", "close-receipt.ac2.json", offline=True, close_receipt_override=ac2_close_receipt,
)
require(
    e2e_gate_ac2.returncode == 0 and re.search(r"CLI e2e:.*at [0-9a-f]{40},", e2e_gate_ac2.stdout),
    f"e2e-gate ac2 (run branch) did not exit 0 with a resolved-SHA report line: "
    f"exit {e2e_gate_ac2.returncode}, stdout {e2e_gate_ac2.stdout!r}, stderr {e2e_gate_ac2.stderr!r}",
)

e2e_gate_ac3 = run_e2e_gate("plan-receipt.ac3.json", "close-receipt.ac3.json")
require(
    e2e_gate_ac3.returncode == 0 and "e2e: not applicable" in e2e_gate_ac3.stdout,
    f"e2e-gate ac3 (not-applicable branch) failed: exit {e2e_gate_ac3.returncode}, stdout {e2e_gate_ac3.stdout!r}",
)

e2e_gate_ac4 = run_e2e_gate("plan-receipt.ac4.json", "close-receipt.ac4.json")
require(
    e2e_gate_ac4.returncode == 1,
    f"e2e-gate ac4 (no milestone named) should exit 1: exit {e2e_gate_ac4.returncode}, stderr {e2e_gate_ac4.stderr!r}",
)

e2e_gate_dangling = run_e2e_gate("plan-receipt.dangling-milestone.json", "close-receipt.dangling-milestone.json")
require(
    e2e_gate_dangling.returncode == 2,
    f"e2e-gate dangling milestone id should exit 2: exit {e2e_gate_dangling.returncode}, stderr {e2e_gate_dangling.stderr!r}",
)

e2e_gate_empty_slug = run_e2e_gate("plan-receipt.empty-slug.json", "close-receipt.empty-slug.json")
require(
    e2e_gate_empty_slug.returncode == 2,
    f"e2e-gate punctuation-only milestone name should exit 2 (empty slug): "
    f"exit {e2e_gate_empty_slug.returncode}, stderr {e2e_gate_empty_slug.stderr!r}",
)

e2e_gate_chinese = run_e2e_gate("plan-receipt.chinese-milestone.json", "close-receipt.chinese-milestone.json")
require(
    e2e_gate_chinese.returncode == 0
    and "docs/ship-flow/flows/从派工到一条-slack-消息.yaml" in e2e_gate_chinese.stdout,
    f"e2e-gate Chinese milestone name should derive its Unicode flow path: "
    f"exit {e2e_gate_chinese.returncode}, stdout {e2e_gate_chinese.stdout!r}",
)

# --- ship-flow review station: open-pr.sh BRANCH binding + disposition.py category handling ---
ship_flow_fixtures = ROOT / "scripts/fixtures/ship-flow"
open_pr_script = ROOT / "scripts/ship-flow/open-pr.sh"
disposition_script = ROOT / "scripts/ship-flow/disposition.py"


def run_disposition(fixture: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(disposition_script), str(fixture)], capture_output=True, text=True,
    )


disposition_security_cased = run_disposition(ship_flow_fixtures / "findings-security-cased.json")
require(
    disposition_security_cased.returncode == 0 and '"disposition": "block"' in disposition_security_cased.stdout,
    "disposition.py did not block a case-varied 'Security' category after normalization: "
    f"exit={disposition_security_cased.returncode} stdout={disposition_security_cased.stdout!r}",
)

disposition_unrecognized = run_disposition(ship_flow_fixtures / "findings-unrecognized-category.json")
require(
    disposition_unrecognized.returncode == 0
    and '"disposition": "block"' in disposition_unrecognized.stdout
    and "unrecognized-category" in disposition_unrecognized.stdout,
    "disposition.py did not fail closed (block) on an unrecognized category: "
    f"exit={disposition_unrecognized.returncode} stdout={disposition_unrecognized.stdout!r}",
)

disposition_malformed = run_disposition(ship_flow_fixtures / "findings-malformed-entry.json")
require(
    disposition_malformed.returncode == 2,
    "disposition.py did not refuse a findings list with a non-dict entry: "
    f"exit={disposition_malformed.returncode} stdout={disposition_malformed.stdout!r} stderr={disposition_malformed.stderr!r}",
)

open_pr_fork_branch = subprocess.run(
    ["bash", str(open_pr_script), str(ship_flow_fixtures / "open-pr-evidence-fork-branch.md")],
    cwd=ROOT, capture_output=True, text=True,
)
require(
    open_pr_fork_branch.returncode == 2 and "fork syntax refused" in open_pr_fork_branch.stderr,
    "open-pr.sh did not refuse a BRANCH containing ':' (fork syntax): "
    f"exit={open_pr_fork_branch.returncode} stderr={open_pr_fork_branch.stderr!r}",
)

open_pr_double_block = subprocess.run(
    ["bash", str(open_pr_script), str(ship_flow_fixtures / "open-pr-evidence-double-block.md")],
    cwd=ROOT, capture_output=True, text=True,
)
require(
    open_pr_double_block.returncode == 2 and "'## Evidence' headings" in open_pr_double_block.stderr,
    "open-pr.sh did not refuse an evidence file with more than one '## Evidence' heading: "
    f"exit={open_pr_double_block.returncode} stderr={open_pr_double_block.stderr!r}",
)

with tempfile.TemporaryDirectory(prefix="kc-dev-flow-open-pr-") as open_pr_dir_name:
    open_pr_dir = Path(open_pr_dir_name)
    open_pr_origin = open_pr_dir / "origin.git"
    open_pr_repo = open_pr_dir / "repo"
    git_user = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.test"]
    subprocess.run(["git", "init", "-q", "--bare", str(open_pr_origin)], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(open_pr_origin), str(open_pr_repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(open_pr_repo), *git_user, "commit", "-q", "--allow-empty", "-m", "feat(fixture): seed"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(open_pr_repo), "push", "-q", "origin", "HEAD:refs/heads/main"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(open_pr_repo), *git_user, "checkout", "-q", "-b", "feature/fixture-branch"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(open_pr_repo), "push", "-q", "origin", "feature/fixture-branch"],
        check=True, capture_output=True,
    )
    open_pr_sha = subprocess.check_output(
        ["git", "-C", str(open_pr_repo), "rev-parse", "HEAD"], text=True,
    ).strip()

    def write_open_pr_evidence(name: str, branch: str) -> Path:
        evidence = open_pr_dir / name
        evidence.write_text(
            "## Evidence\n"
            f"CANDIDATE_SHA: {open_pr_sha}\n"
            f"BRANCH: {branch}\n"
            f"BASE_SHA: {open_pr_sha}\n"
            "SELF_CHECK: fixture accept-evidence: ACCEPT\n"
            "WITHOUT_IT_COMMAND: true\n"
            "WITHOUT_IT_REMOVED_VARIANT: true\n",
            encoding="utf-8",
        )
        return evidence

    open_pr_bound_evidence = write_open_pr_evidence("bound-evidence.md", "feature/fixture-branch")
    open_pr_unbound_evidence = write_open_pr_evidence("unbound-evidence.md", "feature/does-not-exist-on-origin")

    fake_gh_dir = open_pr_dir / "fake-gh"
    fake_gh_dir.mkdir()
    fake_gh_sentinel = open_pr_dir / "gh-called"
    fake_gh_path = fake_gh_dir / "gh"
    fake_gh_path.write_text(
        "#!/usr/bin/env bash\n"
        f"touch '{fake_gh_sentinel}'\n"
        "echo 'warning: 999 deprecation notice' >&2\n"
        "echo 'https://github.com/example/example/pull/777'\n",
        encoding="utf-8",
    )
    fake_gh_path.chmod(0o755)

    def run_open_pr(evidence: Path) -> subprocess.CompletedProcess[str]:
        if fake_gh_sentinel.exists():
            fake_gh_sentinel.unlink()
        open_pr_env = dict(os.environ)
        open_pr_env["PATH"] = f"{fake_gh_dir}:{open_pr_env.get('PATH', '')}"
        return subprocess.run(
            ["bash", str(open_pr_script), str(evidence)],
            cwd=open_pr_repo, capture_output=True, text=True, env=open_pr_env,
        )

    open_pr_bound = run_open_pr(open_pr_bound_evidence)
    require(
        open_pr_bound.returncode == 0
        and open_pr_bound.stdout.strip() == "777"
        and fake_gh_sentinel.exists(),
        "open-pr.sh did not open a PR (parsing 777 from stdout only, ignoring stderr's 999) "
        f"for a BRANCH whose remote head matches CANDIDATE_SHA: exit={open_pr_bound.returncode} "
        f"stdout={open_pr_bound.stdout!r} stderr={open_pr_bound.stderr!r}",
    )

    open_pr_unbound = run_open_pr(open_pr_unbound_evidence)
    require(
        open_pr_unbound.returncode == 2 and not fake_gh_sentinel.exists(),
        "open-pr.sh did not refuse a BRANCH absent from origin before calling gh: "
        f"exit={open_pr_unbound.returncode} stderr={open_pr_unbound.stderr!r}",
    )

print("kc-dev-flow contract: PASS")
