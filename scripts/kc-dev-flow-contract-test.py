#!/usr/bin/env python3
"""Behavior and packaging contract for kc-dev-flow."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "kc-dev-flow"
ADOPTED = ROOT / "docs/dev/_mods"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"kc-dev-flow contract: {message}")


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
    "production": ("thorough", "medium", 1200, 1),
}

required = [
    "kc-dev-flow/.claude-plugin/plugin.json",
    "kc-dev-flow/.codex-plugin/plugin.json",
    "kc-dev-flow/plugin.json",
    "kc-dev-flow/plugin.yaml",
    "kc-dev-flow/__init__.py",
    "kc-dev-flow/MIGRATION.md",
    "kc-dev-flow/RATIONALE.md",
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
    "kc-dev-flow/scripts/profile-spacedock-route.test.py",
    "kc-dev-flow/skills/adopt-dev-flow/SKILL.md",
    "kc-dev-flow/skills/choose-work-profile/SKILL.md",
    "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
    "kc-dev-flow/skills/chief-engineer/SKILL.md",
    "kc-dev-flow/skills/chief-engineer/agents/openai.yaml",
    "kc-dev-flow/skills/science-officer/SKILL.md",
    "kc-dev-flow/skills/science-officer/agents/openai.yaml",
    "kc-dev-flow/skills/science-officer-em/SKILL.md",
    "kc-dev-flow/skills/science-officer-em/agents/openai.yaml",
    "kc-dev-flow/scripts/project-spacedock-state.test.py",
    "scripts/kc-dev-flow-loader-eval.test.py",
    "scripts/kc-dev-flow-multi-profile-gate.py",
    "scripts/kc-dev-flow-published-tag-smoke.py",
    "scripts/kc-dev-flow-published-tag-smoke.test.py",
    "scripts/roborev-implementation-exit-contract.test.py",
    "scripts/pr-merge-portable-delivery.test.py",
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
]:
    require(not (ROOT / retired).exists(), f"retired control still shipped: {retired}")

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
    "kc-dev-flow/scripts/profile-spacedock-route.test.py",
    "scripts/kc-dev-flow-loader-eval.test.py",
    "scripts/kc-dev-flow-published-tag-smoke.py",
]:
    require((ROOT / relative).stat().st_mode & 0o111, f"not executable: {relative}")

run(
    [sys.executable, "kc-dev-flow/scripts/profile-contract-loader.test.py"],
    "profile loader",
)
run(
    [sys.executable, "kc-dev-flow/scripts/profile-spacedock-route.test.py"],
    "profile Spacedock route",
)
run([sys.executable, "scripts/kc-dev-flow-loader-eval.test.py"], "loader eval")
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
run(
    [sys.executable, "kc-dev-flow/scripts/project-spacedock-state.test.py"],
    "Spacedock projection",
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
    root: Path, profile: str, workflow_stage: str, logical_route: list[str]
) -> Path:
    path = root / f"{profile}-{workflow_stage}.md"
    path.write_text(
        "\n".join(
            [
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
                "  schema: kc-dev-flow-work-profile/v2",
                f"  selected: {profile}",
                f"  recommended: {profile}",
                f"  route: [{', '.join(logical_route)}]",
                "  basis: contract fixture",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path

require(
    (PLUGIN / "references/kernel.md").read_bytes()
    == (ADOPTED / "kernel.md").read_bytes(),
    "self-adopted shared core differs from package source",
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

release_gate = read(".github/workflows/kc-dev-flow-release-gate.yml")
require(
    "./scripts/kc-dev-flow-multi-profile-gate.py" in release_gate,
    "the release gate workflow no longer runs the multi-profile route gate",
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

kernel = read("kc-dev-flow/references/kernel.md")
for phrase in [
    "compare added files, dependencies, abstractions, tests, and comments",
    "LOC and file counts are diagnostic signals, never pass/fail gates",
    "create no receipt or commentary",
]:
    require(phrase in " ".join(kernel.split()), f"kernel omits subtraction rule: {phrase}")
require(
    "| `production` | `shape -> build -> verify` |" in kernel,
    "kernel route table omits the current Production route",
)
normalized_kernel = " ".join(kernel.split())
for phrase in [
    "An item leaves `backlog` only when its committed body states all three",
    "**What it is**",
    "**Why it is worth doing**",
    "**When it is scheduled**",
    "`sprint-readiness: ready`",
    "--where sprint=X --where sprint-readiness=ready",
]:
    require(phrase in normalized_kernel, f"kernel backlog exit bar is missing: {phrase}")
require(
    "when it is scheduled" in " ".join(read("kc-dev-flow/skills/choose-work-profile/SKILL.md").split()),
    "choose-work-profile no longer checks the scheduling part of the exit bar",
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
require(
    (PLUGIN / "scripts/profile-contract-loader.py").read_bytes()
    == (ADOPTED / "profile-contract-loader.py").read_bytes(),
    "self-adopted profile loader differs from package source",
)
for reference in [
    "reverse-recovery-audit.md",
    "journey-slicing.md",
    "retained-document-policy.md",
    "project-context-maintenance.md",
    "delivery-branch-base.md",
    "pr-delivery.md",
    "roborev-implementation-exit.md",
]:
    require(
        (PLUGIN / "references" / reference).read_bytes()
        == (ADOPTED / reference).read_bytes(),
        f"self-adopted conditional reference differs: {reference}",
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
for profile, names in profile_files.items():
    for name in names:
        require(
            (PLUGIN / "references/profiles" / profile / name).read_bytes()
            == (ADOPTED / "profiles" / profile / name).read_bytes(),
            f"self-adopted profile contract differs: {profile}/{name}",
        )

with tempfile.TemporaryDirectory(prefix="kc-dev-flow-work-items-") as temporary:
    work_items = Path(temporary)
    for contracts_root in [PLUGIN / "references", ADOPTED]:
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
                    and contract["receipt_schema"] == "kc-dev-flow-work-profile/v2",
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
        "setup-github-project-projection",
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
rationale = read("kc-dev-flow/RATIONALE.md")
normalized_adopter = " ".join(adopter.split())
normalized_rationale = " ".join(rationale.split())
normalized_chooser = " ".join(chooser.split())
normalized_continue = " ".join(continue_skill.split())
normalized_chief = " ".join(chief.split())
normalized_science = " ".join(science.split())
normalized_migration = " ".join(migration.split())

for phrase in [
    "kc-dev-flow-work-profile/v2",
    "build -> prove",
    "shape -> build -> verify-deliver",
    "`shape -> build -> verify` | The scope accepts a production boundary",
    "structured Ask UI",
    "do not ask the Captain to repeat the decision",
]:
    require(phrase in normalized_chooser, f"chooser is missing: {phrase}")
require(
    "shape -> build -> verify -> release" not in normalized_chooser,
    "chooser still documents the removed release route element",
)
require("before a work item enters its first working stage" in normalized_chooser, "profile selection is still ideation-bound")
for phrase in [
    "Default the entity template to `sprint-readiness: defer`",
    "do not mark the unscheduled backlog ready during adoption",
]:
    require(phrase in normalized_adopter, f"adopter omits scheduling binding: {phrase}")
for phrase in [
    "Migrating from 3.x to 4.x",
    "drain every entity at `status: release`",
    "sprint-readiness=ready",
    "do not mark the unscheduled queue ready as a bulk migration",
]:
    require(phrase in normalized_migration, f"v4 migration omits: {phrase}")

for phrase in [
    "read that bounded section plus the frontmatter",
    "repository-local profile loader",
    "--work-item <exact-committed-work-item>",
    "simultaneous items may load different routes",
    "Do not separately read the full kernel, another profile, another stage",
    "kc-dev-flow:chief-engineer",
    "kc-dev-flow:science-officer",
    "kc-dev-flow-conditional-references/v1",
    "A link is not activation",
]:
    require(phrase in normalized_continue, f"continuation is missing: {phrase}")
for phrase in [
    "retained_document_change",
    "project_context_claim_may_change",
    "A Markdown work record alone satisfies neither trigger",
    "`receipt: null` creates no receipt",
]:
    require(phrase in normalized_continue, f"continuation omits doc trigger: {phrase}")
require(
    "Production | `backlog -> ideation -> implementation -> validation -> done`"
    in continue_skill,
    "continuation route table omits the current Production route",
)
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
    "Preserve the surviving `retained-document-policy.md`",
    "`receipt: null` adds no receipt",
]:
    require(phrase in normalized_adopter, f"adopter omits migration rule: {phrase}")
for phrase in [
    "breaking upgrade",
    "one coordinated cutover",
    "leave completed and archived items unchanged",
    "finding-only terminal",
    "Preserve `retained-document-policy.md`",
]:
    require(phrase in migration, f"migration guide omits: {phrase}")
for phrase in [
    "The first version of KC Dev Flow",
    "carrying the whole workshop",
    "kc-dev-flow-work-profile/v2",
    "directional evidence",
    "What would prove this wrong",
    "Load the work, not the ceremony",
]:
    require(phrase in normalized_rationale, f"rationale omits: {phrase}")
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

workflow = read("docs/dev/README.md")
require(
    "sprint-readiness: defer" in workflow
    and "--where sprint-readiness=ready" in workflow,
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
    "Production | `backlog -> ideation -> implementation -> validation -> done`",
    "profile-contract-loader.py",
    "Profiles are per item",
    "No agent is a general gatekeeper",
    "delivery event mod, not a profile contract",
    "seven conditional references",
    "`pr_delivery_selected` stays false and `pr-delivery.md` is not loaded here",
    "Work-item records and unrelated Markdown changes activate neither",
]:
    require(phrase in workflow, f"self-adoption is missing: {phrase}")

package_readme = read("kc-dev-flow/README.md")
normalized_package_readme = " ".join(package_readme.split())
root_readme = read("README.md")
require(
    "| Production | `shape -> build -> verify` |" in package_readme,
    "package README route table omits the current Production route",
)
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
require("](./MIGRATION.md)" in package_readme, "package README omits migration guide")
require("[design rationale](./RATIONALE.md)" in package_readme, "package README omits rationale")
require(
    "[profile-native migration guide](./kc-dev-flow/MIGRATION.md)" in root_readme,
    "root README omits migration guide",
)
# One sentence covers conditionality for the whole set, so a reference added
# later cannot be described as always-loaded by omitting an adjective. The
# per-file checks then confirm each one is still listed with a trigger.
for phrase in [
    "Everything else under `references/` is conditional",
    "a reference link is not activation, and vendoring one adds no ordinary-stage work",
    "`reverse-recovery-audit.md`",
    "`journey-slicing.md`",
    "`retained-document-policy.md`",
    "`project-context-maintenance.md`",
    "it loads even when a provider mod owns the ceremony",
    "already owns the forge-PR ceremony",
]:
    require(
        phrase in normalized_package_readme,
        f"package README omits mod boundary: {phrase}",
    )

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

run([sys.executable, "-m", "py_compile", str(loader_path)], "loader compile")

print("kc-dev-flow contract: PASS")
