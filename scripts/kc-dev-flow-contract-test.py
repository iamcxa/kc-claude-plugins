#!/usr/bin/env python3
"""Fail-closed package contract for the portable kc-dev-flow product."""

from __future__ import annotations

import json
import re
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
    PLUGIN / "references/reverse-recovery-audit.md",
    PLUGIN / "references/work-control-profile.md",
    PLUGIN / "assets/kernel-binding.template.yaml",
    PLUGIN / "scripts/verify-binding.py",
]
for required_file in required_files:
    require(required_file.is_file(), f"missing {required_file.relative_to(ROOT)}")

# The binding checker is the package's only executable part, and the binding
# template plus the adopt skill both instruct adopters to run it from the
# installed package. Packaging is whole-directory, so it ships by default —
# which means nothing would notice if it stopped. Require both that it is
# present and that it is runnable.
verifier = PLUGIN / "scripts/verify-binding.py"
require(verifier.stat().st_mode & 0o111, "scripts/verify-binding.py is not executable")
for caller in (PLUGIN / "assets/kernel-binding.template.yaml", PLUGIN / "skills/adopt-dev-flow/SKILL.md"):
    require(
        "scripts/verify-binding.py" in caller.read_text(encoding="utf-8"),
        f"{caller.relative_to(ROOT)} no longer names the checker adopters are told to run",
    )

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
    "upstream_contribution",
    "Do not merge the upstream pull request",
]:
    require(phrase in continue_skill, f"continue skill is missing boundary: {phrase}")

kernel = required_files[4].read_text(encoding="utf-8")
for phrase in [
    "Project context authority",
    "Work-item authority",
    "Iteration authority",
    "Delivery authority",
    "Observation is not authority",
    "backlog → ideation → implementation → validation → done",
    "smallest sufficient route",
    "At each sprint boundary",
    "repository-local",
    "reusable kernel",
    "`propose_only`",
    "`pull_request`",
]:
    require(phrase in kernel, f"kernel is missing invariant: {phrase}")

binding = required_files[7].read_text(encoding="utf-8")
for field in [
    "kernel_source:",
    "kernel_version:",
    "project_context:",
    "work_items:",
    "iteration:",
    "execution_state:",
    "delivery:",
    "observation:",
    "upstream_contribution:",
    "adopted_controls:",
]:
    require(field in binding, f"local binding is missing {field}")

for reference_name in ["reverse-recovery-audit.md", "work-control-profile.md"]:
    canonical = (PLUGIN / "references" / reference_name).read_bytes()
    self_adoption = (ROOT / "docs/dev/_mods" / reference_name).read_bytes()
    require(canonical == self_adoption, f"self-adoption drifted: {reference_name}")

print("kc-dev-flow contract: PASS")
