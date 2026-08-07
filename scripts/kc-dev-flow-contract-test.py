#!/usr/bin/env python3
"""Fail-closed package contract for the portable kc-dev-flow product."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "kc-dev-flow"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"kc-dev-flow contract: {message}")


def load_json(path: Path) -> object:
    require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


required_files = [
    PLUGIN / ".claude-plugin/plugin.json",
    PLUGIN / ".codex-plugin/plugin.json",
    PLUGIN / "skills/adopt-dev-flow/SKILL.md",
    PLUGIN / "skills/continue-dev-flow/SKILL.md",
    PLUGIN / "references/kernel.md",
    PLUGIN / "references/project-context-maintenance.md",
    PLUGIN / "references/reverse-recovery-audit.md",
    PLUGIN / "references/work-control-profile.md",
    PLUGIN / "scripts/absolutes-check.py",
    PLUGIN / "references/absolutes.registry",
]
for required_file in required_files:
    require(required_file.is_file(), f"missing {required_file.relative_to(ROOT)}")

require(
    (PLUGIN / "scripts/absolutes-check.py").stat().st_mode & 0o111,
    "scripts/absolutes-check.py is not executable",
)

for legacy in [
    PLUGIN / "assets/kernel-binding.template.yaml",
    PLUGIN / "scripts/verify-binding.py",
    ROOT / "scripts/verify-binding.test.sh",
    ROOT / "docs/dev/kernel-binding.yaml",
    ROOT / "docs/dev/_mods/STATUS.md",
]:
    require(not legacy.exists(), f"legacy distribution artifact remains: {legacy.relative_to(ROOT)}")

claude_manifest = load_json(required_files[0])
codex_manifest = load_json(required_files[1])
marketplace = load_json(ROOT / ".claude-plugin/marketplace.json")
release_manifest = load_json(ROOT / ".release-please-manifest.json")
release_config = load_json(ROOT / "release-please-config.json")

require(claude_manifest["name"] == "kc-dev-flow", "wrong Claude plugin name")
require(codex_manifest["name"] == "kc-dev-flow", "wrong Codex plugin name")
require(codex_manifest.get("skills") == "./skills/", "Codex skills path is missing")

entries = [p for p in marketplace["plugins"] if p["name"] == "kc-dev-flow"]
require(len(entries) == 1, "marketplace must contain exactly one entry")
versions = {
    claude_manifest["version"],
    codex_manifest["version"],
    entries[0]["version"],
    release_manifest["kc-dev-flow"],
}
require(len(versions) == 1, f"version parity failed: {sorted(versions)}")
version = next(iter(versions))
require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is not None, "version is not semver")

package = release_config["packages"].get("kc-dev-flow")
require(package is not None, "release-please package is missing")
extra_paths = {item["path"] for item in package["extra-files"]}
require(
    extra_paths
    == {
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        "/.claude-plugin/marketplace.json",
    },
    f"release propagation paths are incomplete: {sorted(extra_paths)}",
)

adopt_skill = required_files[2].read_text(encoding="utf-8")
for phrase in [
    "adopt, audit, or upgrade",
    "Do not replace an existing tracker",
    "Do not create, schedule, advance, or merge",
    "one narrow improvement proposal",
    "Claude Code and Codex",
    "Local Profile",
    "byte-for-byte",
    "_mods/",
]:
    require(phrase in adopt_skill, f"adopt skill is missing boundary: {phrase}")

continue_skill = required_files[3].read_text(encoding="utf-8")
for phrase in [
    "next committed work item",
    "continue without a captain pause",
    "Do not invent or schedule work",
    "fresh validation",
    "Claude Code and Codex",
    "repository-local",
    "reusable kernel",
    "_mods/kernel.md",
    "Policy mods",
    "_improvements/state.yaml",
    "no unseen debrief",
    "Inside the same transaction",
]:
    require(phrase in continue_skill, f"continue skill is missing boundary: {phrase}")

runtime_docs = {
    "adopt skill": adopt_skill,
    "continue skill": continue_skill,
    "package README": (PLUGIN / "README.md").read_text(encoding="utf-8"),
    "workflow README": (ROOT / "docs/dev/README.md").read_text(encoding="utf-8"),
}
for label, content in runtime_docs.items():
    for legacy_reference in [
        "verify-binding.py",
        "kernel-binding.yaml",
        "kernel-binding.template.yaml",
    ]:
        require(
            legacy_reference not in content,
            f"{label} still instructs the legacy distribution path: {legacy_reference}",
        )

workflow = (ROOT / "docs/dev/README.md").read_text(encoding="utf-8")
for phrase in [
    "## Local Profile",
    "| Project context |",
    "| Work items |",
    "| Iteration |",
    "| Execution state |",
    "| Delivery |",
    "| Gate verdicts |",
    "| Scope and irreversibility |",
    "| Observation |",
    "No binding YAML",
]:
    require(phrase in workflow, f"self-adoption is missing Local Profile boundary: {phrase}")

stage_headings = [
    "### `backlog`",
    "### `ideation`",
    "### `implementation`",
    "### `validation`",
    "### `done`",
]
for heading in stage_headings:
    start = workflow.find(heading)
    require(start >= 0, f"self-adoption is missing stage: {heading}")
    end = workflow.find("### `", start + len(heading))
    if end < 0:
        end = len(workflow)
    require(
        "Policy mods:" in workflow[start:end],
        f"self-adoption stage is missing Policy mods: {heading}",
    )

kernel = required_files[4].read_text(encoding="utf-8")
for phrase in [
    "Project context authority",
    "Work-item authority",
    "Iteration authority",
    "Delivery authority",
    "Observation is not authority",
    "backlog → ideation → implementation → validation → done",
    "smallest sufficient route",
    "before routing product work",
    "repository-local",
    "reusable kernel",
    "_improvements/state.yaml",
    "newer than the recorded cursor",
    "compare-and-swap",
]:
    require(phrase in kernel, f"kernel is missing invariant: {phrase}")

route_discipline = kernel.find("## Route discipline")
require(route_discipline >= 0, "kernel is missing Route discipline")
require(
    kernel.find("## Sprint continuity and autonomy")
    < route_discipline
    < kernel.find("## Outcome discipline"),
    "Route discipline is not between Sprint continuity and Outcome discipline",
)
for phrase in [
    "approved outcome contract is its destination",
    "last accepted route",
    "observable lifecycle invariant",
    "plan-local pre/post mapping",
    "Work Control Profile",
    "reviewer's recorded `PASS`",
    "resolves only the ambiguity it names",
    "authority that owns the changed field or decision",
]:
    require(phrase in kernel, f"Route discipline is missing invariant: {phrase}")

# The kernel requires an absolute to name its enforcement point or be rewritten
# as a bounded claim, and that rule had none of its own. Four hand-audits of one
# file each found a different subset, so the registry replaces re-reading: every
# block carrying an absolute is judged once, and an unjudged or edited one fails
# here rather than in a fifth read-through.
absolutes = subprocess.run(
    [sys.executable, str(PLUGIN / "scripts/absolutes-check.py"), str(PLUGIN / "references/absolutes.registry")]
    + [str(p) for p in sorted((PLUGIN / "references").glob("*.md"))],
    capture_output=True,
    text=True,
)
require(absolutes.returncode == 0, absolutes.stdout.strip() or "absolutes-check failed")

for reference_name in ["kernel.md", "reverse-recovery-audit.md", "work-control-profile.md"]:
    canonical = (PLUGIN / "references" / reference_name).read_bytes()
    self_adoption = (ROOT / "docs/dev/_mods" / reference_name).read_bytes()
    require(canonical == self_adoption, f"self-adoption drifted: {reference_name}")

print("kc-dev-flow contract: PASS")
